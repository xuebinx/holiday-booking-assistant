from typing import List, Dict, Any
from datetime import date, timedelta
import random
from .loyalty_optimizer import evaluate_loyalty_value, LOYALTY_PROGRAMS

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

def generate_loyalty_analysis(total_cost: float, hotel_cost: float) -> dict:
    """Generate loyalty program analysis for the trip."""
    # Mock user loyalty balances (in real app, this would come from user profile)
    user_balances = {
        'ihg': 25000,
        'marriott': 15000,
        'hilton': 30000,
        'american_airlines': 45000
    }
    
    # Analyze hotel loyalty options
    hotel_loyalty_options = []
    
    # IHG analysis
    ihg_points_needed = int(hotel_cost * 10)  # Rough conversion: £1 = 10 points
    if ihg_points_needed <= user_balances['ihg']:
        ihg_analysis = evaluate_loyalty_value(
            cash_price=hotel_cost,
            points_price=ihg_points_needed,
            point_value=0.012,  # IHG average point value
            loyalty_program='ihg',
            user_points_balance=user_balances['ihg']
        )
        hotel_loyalty_options.append({
            'program': 'IHG Rewards',
            'program_code': 'ihg',
            'points_needed': ihg_points_needed,
            'points_available': user_balances['ihg'],
            'recommendation': ihg_analysis['recommendation'],
            'savings': ihg_analysis.get('savings', 0),
            'effective_value': ihg_analysis['effective_value_per_point']
        })
    
    # Marriott analysis
    marriott_points_needed = int(hotel_cost * 8)  # Rough conversion: £1 = 8 points
    if marriott_points_needed <= user_balances['marriott']:
        marriott_analysis = evaluate_loyalty_value(
            cash_price=hotel_cost,
            points_price=marriott_points_needed,
            point_value=0.015,  # Marriott average point value
            loyalty_program='marriott',
            user_points_balance=user_balances['marriott']
        )
        hotel_loyalty_options.append({
            'program': 'Marriott Bonvoy',
            'program_code': 'marriott',
            'points_needed': marriott_points_needed,
            'points_available': user_balances['marriott'],
            'recommendation': marriott_analysis['recommendation'],
            'savings': marriott_analysis.get('savings', 0),
            'effective_value': marriott_analysis['effective_value_per_point']
        })
    
    # Find best recommendation
    best_option = None
    if hotel_loyalty_options:
        best_option = max(hotel_loyalty_options, key=lambda x: x['savings'])
    
    return {
        'cash_price': total_cost,
        'hotel_loyalty_options': hotel_loyalty_options,
        'best_recommendation': best_option,
        'user_balances': user_balances
    }

def generate_flight_booking_url(base_url: str, search_path: str, start_date: date, end_date: date, destination: str) -> str:
    """Generate dynamic flight booking URL with search parameters."""
    # Format dates for URL parameters
    departure_date = start_date.strftime('%Y-%m-%d')
    return_date = end_date.strftime('%Y-%m-%d')
    
    # Common origin airports (default to LHR for London)
    origin_airports = {
        'london': 'LHR',
        'paris': 'CDG', 
        'new york': 'JFK',
        'tokyo': 'NRT',
        'sydney': 'SYD',
        'dubai': 'DXB',
        'singapore': 'SIN'
    }
    
    # Get origin airport code
    origin = origin_airports.get(destination.lower(), 'LHR')
    
    # Use real booking aggregator URLs that actually work
    if 'britishairways' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'easyjet' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'ryanair' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'virginatlantic' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'lufthansa' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'emirates' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'qatarairways' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'aa.com' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'delta.com' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    elif 'united.com' in base_url:
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"
    else:
        # Fallback to Skyscanner
        return f"https://www.skyscanner.net/flights/{origin}/{destination.upper()}/{departure_date}/{return_date}/"

def generate_hotel_booking_url(base_url: str, search_path: str, start_date: date, end_date: date, destination: str) -> str:
    """Generate dynamic hotel booking URL with search parameters."""
    # Format dates for URL parameters
    check_in = start_date.strftime('%Y-%m-%d')
    check_out = end_date.strftime('%Y-%m-%d')
    
    # Use real booking aggregator URLs that actually work
    # Booking.com format: https://www.booking.com/search.html?ss=destination&checkin=date&checkout=date
    return f"https://www.booking.com/search.html?ss={destination}&checkin={check_in}&checkout={check_out}"

def generate_flight_options(destination: str, window: dict, preferences: dict) -> List[dict]:
    """Generate mock flight options."""
    airlines = [
        {'name': 'British Airways', 'base_url': 'https://www.britishairways.com', 'search_path': '/en-gb/flights'},
        {'name': 'EasyJet', 'base_url': 'https://www.easyjet.com', 'search_path': '/en/flights'},
        {'name': 'Ryanair', 'base_url': 'https://www.ryanair.com', 'search_path': '/en/cheap-flights'},
        {'name': 'Virgin Atlantic', 'base_url': 'https://www.virginatlantic.com', 'search_path': '/en/flights'},
        {'name': 'Lufthansa', 'base_url': 'https://www.lufthansa.com', 'search_path': '/en/flights'},
        {'name': 'Emirates', 'base_url': 'https://www.emirates.com', 'search_path': '/english/flights'},
        {'name': 'Qatar Airways', 'base_url': 'https://www.qatarairways.com', 'search_path': '/en/flights'},
        {'name': 'American Airlines', 'base_url': 'https://www.aa.com', 'search_path': '/flights'},
        {'name': 'Delta Air Lines', 'base_url': 'https://www.delta.com', 'search_path': '/flights'},
        {'name': 'United Airlines', 'base_url': 'https://www.united.com', 'search_path': '/flights'}
    ]
    flights = []
    
    # Get dates for URL parameters
    start_date = window['start_date']
    end_date = window['end_date']
    
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
        
        airline = random.choice(airlines)
        
        # Generate dynamic booking URL with search parameters
        booking_url = generate_flight_booking_url(
            airline['base_url'], 
            airline['search_path'],
            start_date, 
            end_date, 
            destination
        )
        
        flight = {
            'airline': airline['name'],
            'depart_time': depart_time,
            'arrive_time': arrive_time,
            'cost': base_cost,
            'booking_url': booking_url
        }
        flights.append(flight)
    
    return flights

def generate_hotel_options(destination: str, window: dict, preferences: dict) -> List[dict]:
    """Generate mock hotel options."""
    hotel_chains = [
        {'name': 'Hilton', 'base_url': 'https://www.hilton.com', 'search_path': '/search'},
        {'name': 'Marriott', 'base_url': 'https://www.marriott.com', 'search_path': '/search'},
        {'name': 'Holiday Inn', 'base_url': 'https://www.ihg.com', 'search_path': '/holidayinn/search'},
        {'name': 'Premier Inn', 'base_url': 'https://www.premierinn.com', 'search_path': '/search'},
        {'name': 'Travelodge', 'base_url': 'https://www.travelodge.co.uk', 'search_path': '/search'},
        {'name': 'InterContinental', 'base_url': 'https://www.ihg.com', 'search_path': '/intercontinental/search'},
        {'name': 'Hyatt', 'base_url': 'https://www.hyatt.com', 'search_path': '/search'},
        {'name': 'Radisson', 'base_url': 'https://www.radissonhotels.com', 'search_path': '/search'},
        {'name': 'Best Western', 'base_url': 'https://www.bestwestern.com', 'search_path': '/search'},
        {'name': 'Comfort Inn', 'base_url': 'https://www.choicehotels.com', 'search_path': '/comfort/search'}
    ]
    hotels = []
    
    # Get dates for URL parameters
    start_date = window['start_date']
    end_date = window['end_date']
    
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
        
        hotel_chain = random.choice(hotel_chains)
        
        # Generate dynamic booking URL with search parameters
        booking_url = generate_hotel_booking_url(
            hotel_chain['base_url'],
            hotel_chain['search_path'],
            start_date,
            end_date,
            destination
        )
        
        hotel = {
            'name': f"{hotel_chain['name']} {destination}",
            'cost': base_cost,
            'distance_from_poi_km': round(distance_from_poi, 1),
            'family_friendly': is_family_friendly,
            'booking_url': booking_url
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
    
    # Generate loyalty analysis
    loyalty_analysis = generate_loyalty_analysis(total_cost, hotel_total)
    
    return {
        'flight': flight,
        'hotel': hotel,
        'total_cost': total_cost,
        'duration': duration,
        'start_date': window['start_date'],
        'end_date': window['end_date'],
        'num_travelers': num_travelers,
        'loyalty_analysis': loyalty_analysis
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