from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body, HTTPException, status, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import motor.motor_asyncio
import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from .trip_optimizer import generate_trip_options

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

def verify_firebase_token(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    id_token = auth_header.split(" ", 1)[1]
    try:
        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase ID token")

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:3002",
    "http://localhost:8000",
    "http://192.168.0.166:3002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Async MongoDB (motor) config ---
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = mongo_client["holiday_booking"]
trip_requests_collection = db["trip_requests"]

# Firestore 预留配置
# import google.cloud.firestore_async
# firestore_client = google.cloud.firestore_async.AsyncClient()

# --- Request/Response Schemas ---
class TripPreferences(BaseModel):
    prefer_evening_flights: bool = False
    family_friendly_hotel: bool = False
    duration_range: List[int] = Field(default=[3, 5])  # e.g. [3, 5] for 3-5 days
    num_kids: int = Field(default=0)
    other: Dict[str, Any] = Field(default_factory=dict)

class PlanTripRequest(BaseModel):
    destination: str
    date_range: List[date]  # [start, end]
    num_travelers: int
    preferences: TripPreferences

class FlightDetails(BaseModel):
    airline: str
    depart_time: str
    arrive_time: str
    cost: float

class HotelDetails(BaseModel):
    name: str
    cost: float
    distance_from_poi_km: float

class TripPackage(BaseModel):
    flight: FlightDetails
    hotel: HotelDetails
    total_score: float
    total_cost: float
    duration: int
    start_date: date
    end_date: date

class PlanTripResponse(BaseModel):
    packages: List[TripPackage]
    user_input: dict
    generated_at: datetime

# --- Trip Request DB Model ---
class TripRequestDB(BaseModel):
    destination: str
    date_range: List[date]
    num_travelers: int
    preferences: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    generated_packages: List[Dict[str, Any]] = Field(default_factory=list)
    generated_at: Optional[datetime] = None

# --- Endpoint ---
@app.post("/api/plan-trip", response_model=PlanTripResponse)
async def plan_trip(request: Request, payload: PlanTripRequest = Body(...)):
    # Verify Firebase ID token (temporarily disabled for testing)
    # verify_firebase_token(request)
    
    # Parse and prepare trip intent
    trip_intent = {
        'destination': payload.destination,
        'date_range': payload.date_range,
        'num_travelers': payload.num_travelers,
        'preferences': {
            'prefer_evening_flights': payload.preferences.prefer_evening_flights,
            'family_friendly_hotel': payload.preferences.family_friendly_hotel,
            'duration_range': payload.preferences.duration_range,
            'num_kids': payload.preferences.num_kids,
            **payload.preferences.other
        }
    }
    
    # Generate optimized trip options
    optimized_options = generate_trip_options(trip_intent)
    
    # Convert to TripPackage format
    packages = []
    for option in optimized_options:
        trip_package = TripPackage(
            flight=FlightDetails(
                airline=option['flight']['airline'],
                depart_time=option['flight']['depart_time'],
                arrive_time=option['flight']['arrive_time'],
                cost=option['flight']['cost']
            ),
            hotel=HotelDetails(
                name=option['hotel']['name'],
                cost=option['hotel']['cost'],
                distance_from_poi_km=option['hotel']['distance_from_poi_km']
            ),
            total_score=option['total_score'],
            total_cost=option['total_cost'],
            duration=option['duration'],
            start_date=option['start_date'],
            end_date=option['end_date']
        )
        packages.append(trip_package)
    
    # Prepare data for MongoDB
    generated_at = datetime.utcnow()
    
    # Store request and results in MongoDB
    trip_db = TripRequestDB(
        destination=payload.destination,
        date_range=payload.date_range,
        num_travelers=payload.num_travelers,
        preferences=trip_intent['preferences'],
        generated_packages=[pkg.dict() for pkg in packages],
        generated_at=generated_at
    )
    
    # Convert date/datetime fields to ISO strings for MongoDB
    def trip_db_to_mongo(trip_db: TripRequestDB):
        doc = trip_db.dict()
        doc["date_range"] = [d.isoformat() for d in doc["date_range"]]
        if isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat()
        if isinstance(doc["generated_at"], datetime):
            doc["generated_at"] = doc["generated_at"].isoformat()
        # Convert package dates
        for pkg in doc["generated_packages"]:
            if "start_date" in pkg:
                pkg["start_date"] = pkg["start_date"].isoformat()
            if "end_date" in pkg:
                pkg["end_date"] = pkg["end_date"].isoformat()
        return doc
    
    await trip_requests_collection.insert_one(trip_db_to_mongo(trip_db))
    
    return PlanTripResponse(
        packages=packages,
        user_input=trip_intent,
        generated_at=generated_at
    )

@app.get("/")
def read_root():
    return {"message": "Holiday Booking Assistant API is running."}
