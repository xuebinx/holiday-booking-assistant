from typing import List, Dict, Any
from datetime import date, timedelta
import random

def generate_trip_options(trip_intent: dict) -> List[dict]:
    """
    Generate optimized trip options based on user preferences.
    
    Args:
        trip_intent: Dictionary containing destination, date_range, num_travelers, preferences
        
    Returns:
        List of trip packages with flight, hotel, scoring, and costs
    """
    destination = trip_intent['destination']
    date_range = trip_intent['date_range']
    num_travelers = trip_intent['num_travelers']
    preferences = trip_intent['preferences']
    
    # Generate valid travel windows within the date range
    start_date = date_range[0] if isinstance(date_range[0], date) else date.fromisoformat(date_range[0])
    end_date = date_range[1] if isinstance(date_range[1], date) else date.fromisoformat(date_range[1])
    
    duration_range = preferences.get('duration_range', [3, 5])
    min_duration = duration_range[0]
    max_duration = min(duration_range[1], (end_date - start_date).days)
    
    # Generate all possible travel windows
    travel_windows = []
    current_date = start_date
    while current_date + timedelta(days=min_duration) <= end_date:
        for duration in range(min_duration, max_duration + 1):
            if current_date + timedelta(days=duration) <= end_date:
                travel_windows.append({
                    'start_date': current_date,
                    'end_date': current_date + timedelta(days=duration),
                    'duration': duration
                })
        current_date += timedelta(days=1)
    
    # Generate trip options for each window
    all_options = []
    
    for window in travel_windows[:10]:  # Limit to 10 windows for performance
        # Generate multiple flight options
        flight_options = generate_flight_options(destination, window, preferences)
        
        # Generate multiple hotel options
        hotel_options = generate_hotel_options(destination, window, preferences)
        
        # Combine flight and hotel options
        for flight in flight_options:
            for hotel in hotel_options:
                option = create_trip_package(flight, hotel, window, num_travelers, preferences)
                all_options.append(option)
    
    # Score and sort options
    scored_options = []
    for option in all_options:
        score = calculate_score(option, preferences)
        option['total_score'] = score
        scored_options.append(option)
    
    # Return top 3 highest scoring options
    scored_options.sort(key=lambda x: x['total_score'], reverse=True)
    return scored_options[:3]

def generate_flight_options(destination: str, window: dict, preferences: dict) -> List[dict]:
    """Generate mock flight options."""
    airlines = ['British Airways', 'EasyJet', 'Ryanair', 'Virgin Atlantic', 'Lufthansa']
    flights = []
    
    for i in range(3):  # Generate 3 flight options
        # Determine departure time based on preferences
        if preferences.get('prefer_evening_flights', False):
            depart_hour = random.choice([18, 19, 20, 21])  # Evening flights
        else:
            depart_hour = random.choice([8, 9, 10, 11, 14, 15, 16])  # Day flights
        
        depart_time = f"{depart_hour:02d}:{random.randint(0, 59):02d}"
        arrive_hour = (depart_hour + random.randint(1, 3)) % 24
        arrive_time = f"{arrive_hour:02d}:{random.randint(0, 59):02d}"
        
        # Base cost varies by destination and airline
        base_cost = random.randint(80, 300)
        if destination.lower() in ['london', 'paris', 'rome']:
            base_cost += random.randint(50, 100)
        
        flight = {
            'airline': random.choice(airlines),
            'depart_time': depart_time,
            'arrive_time': arrive_time,
            'cost': base_cost
        }
        flights.append(flight)
    
    return flights

def generate_hotel_options(destination: str, window: dict, preferences: dict) -> List[dict]:
    """Generate mock hotel options."""
    hotel_chains = ['Hilton', 'Marriott', 'Holiday Inn', 'Premier Inn', 'Travelodge']
    hotels = []
    
    for i in range(3):  # Generate 3 hotel options
        # Determine if family-friendly based on preferences
        is_family_friendly = preferences.get('family_friendly_hotel', False)
        
        # Base cost varies by destination and family-friendliness
        base_cost = random.randint(60, 150)
        if is_family_friendly:
            base_cost += random.randint(20, 40)
        if destination.lower() in ['london', 'paris', 'rome']:
            base_cost += random.randint(30, 60)
        
        # Distance from POI (Points of Interest)
        distance_from_poi = random.uniform(0.5, 5.0)
        
        hotel = {
            'name': f"{random.choice(hotel_chains)} {destination}",
            'cost': base_cost,
            'distance_from_poi_km': round(distance_from_poi, 1),
            'family_friendly': is_family_friendly
        }
        hotels.append(hotel)
    
    return hotels

def create_trip_package(flight: dict, hotel: dict, window: dict, num_travelers: int, preferences: dict) -> dict:
    """Create a complete trip package."""
    duration = window['duration']
    
    # Calculate total costs
    flight_total = flight['cost'] * num_travelers
    hotel_total = hotel['cost'] * duration * num_travelers
    total_cost = flight_total + hotel_total
    
    return {
        'flight': flight,
        'hotel': hotel,
        'total_cost': total_cost,
        'duration': duration,
        'start_date': window['start_date'],
        'end_date': window['end_date'],
        'num_travelers': num_travelers
    }

def calculate_score(option: dict, preferences: dict) -> float:
    """Calculate a score for the trip option based on preferences."""
    score = 0.0
    
    # Determine scoring weights based on user priorities
    cost_weight = 0.4
    flight_weight = 0.3
    hotel_weight = 0.25
    duration_weight = 0.05
    
    # Adjust weights based on user priorities
    if preferences.get('prioritize_cost', False):
        cost_weight = 0.6
        flight_weight = 0.2
        hotel_weight = 0.15
        duration_weight = 0.05
    elif preferences.get('prioritize_flight_time', False):
        cost_weight = 0.25
        flight_weight = 0.5
        hotel_weight = 0.2
        duration_weight = 0.05
    elif preferences.get('prioritize_hotel_quality', False):
        cost_weight = 0.25
        flight_weight = 0.2
        hotel_weight = 0.5
        duration_weight = 0.05
    
    # Cost scoring (lower is better)
    max_expected_cost = 2000  # Assume £2000 is max expected cost
    cost_score = max(0, 100 - (option['total_cost'] / max_expected_cost) * 100)
    score += cost_score * cost_weight
    
    # Flight time scoring
    flight = option['flight']
    depart_hour = int(flight['depart_time'].split(':')[0])
    
    flight_score = 0
    if preferences.get('prefer_evening_flights', False):
        if 18 <= depart_hour <= 22:  # Evening flights
            flight_score = 100
        elif 6 <= depart_hour <= 12:  # Morning flights
            flight_score = 50
        else:  # Afternoon flights
            flight_score = 30
    else:
        if 8 <= depart_hour <= 16:  # Day flights
            flight_score = 100
        else:
            flight_score = 50
    
    score += flight_score * flight_weight
    
    # Hotel quality scoring (closer to POI is better)
    hotel = option['hotel']
    distance = hotel['distance_from_poi_km']
    
    hotel_score = 0
    if distance <= 1.0:
        hotel_score = 100
    elif distance <= 2.0:
        hotel_score = 80
    elif distance <= 3.0:
        hotel_score = 60
    else:
        hotel_score = 40
    
    # Family-friendly hotel bonus
    if preferences.get('family_friendly_hotel', False) and hotel.get('family_friendly', False):
        hotel_score += 20
    
    score += hotel_score * hotel_weight
    
    # Duration scoring (prefer longer stays)
    duration = option['duration']
    duration_score = 0
    if duration >= 5:
        duration_score = 100
    elif duration >= 4:
        duration_score = 80
    elif duration >= 3:
        duration_score = 60
    else:
        duration_score = 40
    
    score += duration_score * duration_weight
    
    return round(score, 1) 