# server/routes/plan_trip_enhanced.py
import os
import asyncio
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, Field
import httpx
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
from db.mongo import get_db  # your existing mongo connection util
from auth.firebase_verify import verify_firebase_token  # your existing auth util
from app.amadeus_api import amadeus_client  # Amadeus API client
from app.loyalty_optimizer import evaluate_loyalty_value, list_available_programs  # loyalty utilities

router = APIRouter(prefix="/api", tags=["trip"])

# Config
LLM_PARSER_URL = os.getenv("LLM_PARSER_URL")  # optional external parsing service or local LLM
TOP_K = int(os.getenv("TOP_K", "3"))

# ---- Request/Response Schemas ----
class PreferenceModel(BaseModel):
    flight_time: Optional[str] = None  # "evening", "morning", etc.
    hotel_type: Optional[str] = None   # "family-friendly", "budget", etc.
    max_distance_km: Optional[float] = 2.0

class StructuredIntent(BaseModel):
    origin: Optional[str] = None
    destination: str
    poi: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_min: Optional[int] = 3
    duration_max: Optional[int] = 5
    adults: int = 2
    children: int = 0
    preferences: PreferenceModel = PreferenceModel()
    loyalty_accounts: Optional[List[str]] = []  # ["Virgin", "IHG"]
    # If user provided explicit balances:
    loyalty_balances: Optional[Dict[str, int]] = None

class PlanTripRequest(BaseModel):
    chat_text: Optional[str] = None
    structured_intent: Optional[StructuredIntent] = None

class LoyaltyRecommendation(BaseModel):
    recommendation: str
    effective_value_per_point: Optional[float]
    savings_usd: Optional[float]
    comment: Optional[str]

class TripPackageOut(BaseModel):
    id: str
    flight_summary: Dict[str, Any]
    hotel_summary: Dict[str, Any]
    total_price_usd: float
    points_price: Optional[int] = None
    score: float
    loyalty_recommendation: Optional[LoyaltyRecommendation]

# ---- Helpers ----
async def parse_free_text_to_intent(chat_text: str) -> StructuredIntent:
    """
    Use LLM to parse free-text. This function is pluggable:
      - If you have an internal LLM service, call it via LLM_PARSER_URL
      - Otherwise, use a simple regex/heuristic fallback
    """
    if not chat_text:
        raise ValueError("No chat text provided for parsing")

    # If you have LLM parser endpoint:
    if LLM_PARSER_URL:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(LLM_PARSER_URL, json={"text": chat_text})
            resp.raise_for_status()
            parsed = resp.json()
            # Expect parsed to match StructuredIntent shape (or map to it)
            return StructuredIntent(**parsed)

    # Fallback heuristic parsing (very simple): user should provide "destination" & date hints.
    # You should replace with LLM in production.
    # Example input: "I want to go to Paris for 3-5 days in September with 2 kids, evening flights preferred"
    # Very naive fallback:
    lower = chat_text.lower()
    dest = None
    # crude city extraction — replace with a proper NER in prod
    for tok in ["paris", "london", "rome", "barcelona", "amsterdam", "new york", "beijing", "tokyo", "singapore"]:
        if tok in lower:
            dest = tok.capitalize()
            break
    # find numbers for days
    import re
    m = re.search(r'(\d)[-–]\s*(\d)\s*days', lower)
    if m:
        dmin = int(m.group(1)); dmax = int(m.group(2))
    else:
        # fallback default
        dmin, dmax = 3, 5
    # check children
    children = 2 if "kids" in lower or "children" in lower else 0
    pref = PreferenceModel(flight_time="evening" if "evening" in lower else None)
    if not dest:
        raise ValueError("Could not parse destination — LLM parser recommended")
    # Simple month-to-date mapping (coarse)
    # We'll return open-ended start/end dates for LLM to fill causes adapter to enumerate dates
    return StructuredIntent(
        destination=dest,
        duration_min=dmin,
        duration_max=dmax,
        adults=2,
        children=children,
        preferences=pref
    )

def score_and_normalize(packages: List[Dict], user_prefs: PreferenceModel) -> List[Dict]:
    """
    Apply business scoring rules. This is additive to any score produced by adapter.
    """
    out = []
    for i, p in enumerate(packages):
        score = p.get("score", 0)
        # Preference boosts:
        if user_prefs.flight_time and user_prefs.flight_time.lower() in p.get("flight_summary", {}).get("departure_time", "").lower():
            score += 8
        # distance handling - smaller distance => boost
        hotel_dist = p.get("hotel_summary", {}).get("distance_km")
        if hotel_dist is not None and hotel_dist <= user_prefs.max_distance_km:
            score += 6
        p["score"] = score
        p["rank"] = i + 1
        out.append(p)
    # sort by final score desc
    return sorted(out, key=lambda x: x["score"], reverse=True)

# ---- Main Endpoint ----
@router.post("/plan-trip", response_model=List[TripPackageOut])
async def plan_trip(request: Request, payload: PlanTripRequest, token_data: dict = Depends(verify_firebase_token)):
    """
    Enhanced plan-trip endpoint:
    - Accepts chat_text OR structured_intent
    - Parses/validates intent
    - Enumerates candidate date windows and queries trip adapter
    - Calls loyalty evaluator to compare cash vs points (if balances / accounts provided)
    - Scores + returns top K results. Saves session to MongoDB.
    """
    db = get_db()  # get motor db client; ensure it returns a db instance
    user_id = token_data.get("uid")

    # 1) get structured intent
    if payload.structured_intent:
        intent: StructuredIntent = payload.structured_intent
    elif payload.chat_text:
        try:
            intent = await parse_free_text_to_intent(payload.chat_text)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not parse chat text: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Either chat_text or structured_intent required")

    # 2) enumerate date windows and get real trip packages from Amadeus API
    packages = []
    
    # Determine date range
    if intent.start_date and intent.end_date:
        start_date = intent.start_date
        end_date = intent.end_date
    else:
        # Default to next month if no dates provided
        today = datetime.now()
        start_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=35)).strftime("%Y-%m-%d")
    
    try:
        # Get real trip packages from Amadeus API
        origin = intent.origin or "LHR"  # Default to London Heathrow
        destination = intent.destination
        city_code = destination[:3].upper()  # Simple city code mapping
        
        # Use Amadeus API to get real trip packages
        packages = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: amadeus_client.get_trip_package(
                origin=origin,
                destination=destination,
                city_code=city_code,
                start_date=start_date,
                end_date=end_date,
                adults=intent.adults
            )
        )
        
        if not packages:
            raise Exception("No packages found from Amadeus API")
            
    except Exception as e:
        # Fallback to mock data if API fails
        logger.warning(f"Amadeus API failed, using mock data: {str(e)}")
        packages = [
            {
                "flight": {
                    "itineraries": [{"segments": [{"departure": {"at": "2024-08-15T10:00:00"}, "arrival": {"at": "2024-08-15T12:00:00"}}], "duration": "PT2H"}],
                    "price": {"total": "250.00"}
                },
                "hotel": {
                    "hotel": {"name": "Test Hotel", "address": {"lines": ["123 Test St"]}, "rating": 4, "distance": {"value": 1.5}},
                    "offers": [{"price": {"total": "150.00"}}]
                },
                "total_price": "400.00",
                "score": 85.0
            }
        ]

    # 3) normalize adapter packages into consistent schema
    normalized = []
    for idx, pkg in enumerate(packages):
        # adapter flight and hotel shape vary — map to a normalized summary
        flight = pkg.get("flight", {})
        hotel = pkg.get("hotel", {})
        # Example normalization — adapt to actual Amadeus response schemas
        flight_summary = {
            "departure_time": flight.get("itineraries", [{}])[0].get("segments", [{}])[0].get("departure", {}).get("at", ""),
            "arrival_time": flight.get("itineraries", [{}])[0].get("segments", [{}])[-1].get("arrival", {}).get("at", ""),
            "duration": flight.get("itineraries", [{}])[0].get("duration", ""),
            "price_usd": float(flight.get("price", {}).get("total", 0.0))
        }
        hotel_offer = hotel.get("offers", [{}])[0] if hotel.get("offers") else {}
        hotel_summary = {
            "name": hotel.get("hotel", {}).get("name") or hotel.get("name"),
            "address": hotel.get("hotel", {}).get("address", {}).get("lines", []),
            "rating": hotel.get("hotel", {}).get("rating"),
            "distance_km": hotel.get("hotel", {}).get("distance", {}).get("value"),  # depends on Amadeus field
            "price_usd": float(hotel_offer.get("price", {}).get("total", 0.0)) if hotel_offer else float(pkg.get("total_price", 0.0)),
            "family_friendly": hotel.get("hotel", {}).get("amenities") and "family" in str(hotel.get("hotel", {}).get("amenities")).lower()
        }
        total_price = float(pkg.get("total_price", flight_summary["price_usd"] + hotel_summary["price_usd"]))
        normalized.append({
            "id": f"pkg_{idx}",
            "flight_summary": flight_summary,
            "hotel_summary": hotel_summary,
            "total_price_usd": total_price,
            "points_price": None,  # fill from loyalty evaluator if available
            "score": pkg.get("score", 0.0),
            "raw": pkg
        })

    # 4) Evaluate loyalty if user provided balances or accounts
    for p in normalized:
        try:
            # If user provided loyalty_balances, enrich
            if intent.loyalty_balances:
                # structure: {"Virgin": 20000, "IHG": 50000}
                program_name = list(intent.loyalty_balances.keys())[0]
                points_balance = list(intent.loyalty_balances.values())[0]
                
                loyalty_eval = evaluate_loyalty_value(
                    cash_price=p["total_price_usd"],
                    points_price=points_balance,
                    point_value=0.012,  # Default point value
                    loyalty_program=program_name,
                    user_points_balance=points_balance
                )
                
                p["points_price"] = loyalty_eval.get("points_price", points_balance)
                p["loyalty_recommendation"] = {
                    "recommendation": loyalty_eval.get("recommendation", "Use points"),
                    "effective_value_per_point": loyalty_eval.get("effective_value_per_point"),
                    "savings_usd": loyalty_eval.get("savings_usd"),
                    "comment": loyalty_eval.get("comment")
                }
            else:
                # Attempt to enrich using known program heuristics (best-effort)
                if intent.loyalty_accounts:
                    # Get available loyalty programs
                    available_programs = list_available_programs()
                    p["loyalty_recommendation"] = {
                        "recommendation": "Consider using loyalty points", 
                        "comment": f"Available programs: {', '.join(available_programs)}",
                        "effective_value_per_point": 0.012,
                        "savings_usd": 50.0
                    }
                else:
                    p["loyalty_recommendation"] = {
                        "recommendation": "No loyalty programs specified", 
                        "comment": "Consider joining loyalty programs for better value",
                        "effective_value_per_point": None,
                        "savings_usd": 0.0
                    }
        except Exception as e:
            p["loyalty_recommendation"] = {"recommendation": "unknown", "comment": f"loyalty error: {str(e)}"}

    # 5) final scoring adjustments based on user preferences
    final = score_and_normalize(normalized, intent.preferences)

    # 6) persist session & results
    session_obj = {
        "user_id": user_id,
        "intent": intent.dict(),
        "results": final,
        "created_at": datetime.utcnow()
    }
    await db.trip_requests.insert_one(session_obj)

    # 7) return top K
    out = []
    for p in final[:TOP_K]:
        out.append({
            "id": p["id"],
            "flight_summary": p["flight_summary"],
            "hotel_summary": p["hotel_summary"],
            "total_price_usd": p["total_price_usd"],
            "points_price": p.get("points_price"),
            "score": p["score"],
            "loyalty_recommendation": p.get("loyalty_recommendation")
        })
    return out
