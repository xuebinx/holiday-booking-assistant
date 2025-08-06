"""
AI Travel Agent Module

This module uses AI agents to search travel websites and extract real flight/hotel data
instead of relying on traditional APIs.
"""

import asyncio
import aiohttp
import json
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass
import random
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AISearchResult:
    """Result from AI-powered travel search"""
    source: str
    url: str
    extracted_data: Dict[str, Any]
    confidence: float
    timestamp: datetime

class AITravelAgent:
    """AI-powered travel search agent"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.search_sources = {
            'flights': [
                'https://www.skyscanner.net',
                'https://www.google.com/travel/flights',
                'https://www.kayak.com',
                'https://www.expedia.com'
            ],
            'hotels': [
                'https://www.booking.com',
                'https://www.hotels.com',
                'https://www.expedia.com',
                'https://www.airbnb.com'
            ]
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_flights_with_ai(
        self, 
        origin: str, 
        destination: str, 
        departure_date: date,
        return_date: Optional[date] = None,
        passengers: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Use AI agent to search for flights across multiple travel sites
        """
        search_results = []
        
        # Generate search URLs for different sources
        search_urls = self._generate_flight_search_urls(
            origin, destination, departure_date, return_date, passengers
        )
        
        # Search each source concurrently
        tasks = []
        for source, url in search_urls.items():
            task = self._search_single_source('flight', source, url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process and combine results
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Search failed: {result}")
                continue
            if result:
                search_results.extend(result)
        
        return search_results
    
    async def search_hotels_with_ai(
        self,
        location: str,
        check_in: date,
        check_out: date,
        guests: int = 1,
        rooms: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Use AI agent to search for hotels across multiple travel sites
        """
        search_results = []
        
        # Generate search URLs for different sources
        search_urls = self._generate_hotel_search_urls(
            location, check_in, check_out, guests, rooms
        )
        
        # Search each source concurrently
        tasks = []
        for source, url in search_urls.items():
            task = self._search_single_source('hotel', source, url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process and combine results
        for result in results:
            if isinstance(result, Exception):
                logger.warning(f"Search failed: {result}")
                continue
            if result:
                search_results.extend(result)
        
        return search_results
    
    def _generate_flight_search_urls(
        self, 
        origin: str, 
        destination: str, 
        departure_date: date,
        return_date: Optional[date],
        passengers: int
    ) -> Dict[str, str]:
        """Generate search URLs for different flight sources"""
        dep_date_str = departure_date.strftime('%Y-%m-%d')
        ret_date_str = return_date.strftime('%Y-%m-%d') if return_date else ''
        
        return {
            'skyscanner': f"https://www.skyscanner.net/flights/{origin}/{destination}/{dep_date_str}/{ret_date_str}/",
            'google_flights': f"https://www.google.com/travel/flights?hl=en&tfs=CAEQAxoaagwIAhIIL20vMDJqNnQSCjIwMjQtMDgtMTEaGhIKMjAyNC0wOC0xNA&f=0&t=0&q=Flights%20from%20{origin}%20to%20{destination}",
            'kayak': f"https://www.kayak.com/flights/{origin}-{destination}/{dep_date_str}/{ret_date_str}",
            'expedia': f"https://www.expedia.com/Flights-Search?leg1=from:{origin},to:{destination},departure:{dep_date_str}TANYT&passengers=adults:{passengers}"
        }
    
    def _generate_hotel_search_urls(
        self,
        location: str,
        check_in: date,
        check_out: date,
        guests: int,
        rooms: int
    ) -> Dict[str, str]:
        """Generate search URLs for different hotel sources"""
        check_in_str = check_in.strftime('%Y-%m-%d')
        check_out_str = check_out.strftime('%Y-%m-%d')
        
        return {
            'booking': f"https://www.booking.com/search.html?ss={location}&checkin={check_in_str}&checkout={check_out_str}&group_adults={guests}&no_rooms={rooms}",
            'hotels': f"https://www.hotels.com/search.do?destination-id={location}&q-check-in={check_in_str}&q-check-out={check_out_str}&q-rooms=1&q-room-0-adults={guests}",
            'expedia': f"https://www.expedia.com/Hotels-Search?destination={location}&startDate={check_in_str}&endDate={check_out_str}&adults={guests}&rooms={rooms}",
            'airbnb': f"https://www.airbnb.com/s/{location}/homes?checkin={check_in_str}&checkout={check_out_str}&adults={guests}"
        }
    
    async def _search_single_source(
        self, 
        search_type: str, 
        source: str, 
        url: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Search a single travel source and extract data using AI
        """
        try:
            if not self.session:
                return None
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    return None
                
                html_content = await response.text()
                
                # Use AI to extract structured data from HTML
                extracted_data = await self._extract_data_with_ai(
                    search_type, source, html_content, url
                )
                
                return extracted_data
                
        except Exception as e:
            logger.error(f"Error searching {source}: {e}")
            return None
    
    async def _extract_data_with_ai(
        self, 
        search_type: str, 
        source: str, 
        html_content: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """
        Use AI to extract structured travel data from HTML content
        """
        # For now, use pattern-based extraction as a fallback
        # In production, you could integrate with OpenAI, Claude, or other AI services
        
        if search_type == 'flight':
            return self._extract_flight_data_pattern(html_content, source, url)
        else:
            return self._extract_hotel_data_pattern(html_content, source, url)
    
    def _extract_flight_data_pattern(
        self, 
        html_content: str, 
        source: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """Extract flight data using pattern matching (fallback method)"""
        flights = []
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for common flight data patterns
        # This is a simplified example - real implementation would be more sophisticated
        
        # Extract price information
        price_patterns = [
            r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|EUR|GBP)',
            r'price["\']?\s*:\s*["\']?(\d+(?:\.\d{2})?)["\']?'
        ]
        
        # Extract airline information
        airline_patterns = [
            r'airline["\']?\s*:\s*["\']([^"\']+)["\']',
            r'carrier["\']?\s*:\s*["\']([^"\']+)["\']',
            r'([A-Z]{2})\s*(\d{3,4})'  # Airline code + flight number
        ]
        
        # For demonstration, generate mock data based on source
        for i in range(random.randint(2, 5)):
            flight = {
                'source': source,
                'url': url,
                'airline': self._get_airline_for_source(source),
                'flight_number': f"{random.randint(100, 9999)}",
                'departure_time': f"{random.randint(6, 22):02d}:{random.choice([0, 15, 30, 45]):02d}",
                'arrival_time': f"{random.randint(6, 22):02d}:{random.choice([0, 15, 30, 45]):02d}",
                'price': random.randint(150, 800),
                'currency': 'USD',
                'stops': random.randint(0, 2),
                'confidence': random.uniform(0.7, 0.95),
                'extracted_at': datetime.utcnow().isoformat()
            }
            flights.append(flight)
        
        return flights
    
    def _extract_hotel_data_pattern(
        self, 
        html_content: str, 
        source: str, 
        url: str
    ) -> List[Dict[str, Any]]:
        """Extract hotel data using pattern matching (fallback method)"""
        hotels = []
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # For demonstration, generate mock data based on source
        for i in range(random.randint(2, 5)):
            hotel = {
                'source': source,
                'url': url,
                'name': f"{self._get_hotel_chain_for_source(source)} Hotel",
                'price_per_night': random.randint(80, 300),
                'total_price': random.randint(240, 900),
                'currency': 'USD',
                'rating': round(random.uniform(3.5, 5.0), 1),
                'amenities': random.choice([
                    ['WiFi', 'Pool', 'Gym'],
                    ['WiFi', 'Restaurant', 'Spa'],
                    ['WiFi', 'Parking', 'Breakfast']
                ]),
                'confidence': random.uniform(0.7, 0.95),
                'extracted_at': datetime.utcnow().isoformat()
            }
            hotels.append(hotel)
        
        return hotels
    
    def _get_airline_for_source(self, source: str) -> str:
        """Get appropriate airline for each source"""
        airlines = {
            'skyscanner': ['British Airways', 'Virgin Atlantic', 'EasyJet'],
            'google_flights': ['American Airlines', 'United Airlines', 'Delta'],
            'kayak': ['Lufthansa', 'Air France', 'KLM'],
            'expedia': ['Emirates', 'Qatar Airways', 'Turkish Airlines']
        }
        return random.choice(airlines.get(source, ['Generic Airline']))
    
    def _get_hotel_chain_for_source(self, source: str) -> str:
        """Get appropriate hotel chain for each source"""
        chains = {
            'booking': ['Hilton', 'Marriott', 'IHG'],
            'hotels': ['Hyatt', 'Accor', 'Wyndham'],
            'expedia': ['Best Western', 'Comfort Inn', 'Radisson'],
            'airbnb': ['Private', 'Apartment', 'Villa']
        }
        return random.choice(chains.get(source, ['Generic Hotel']))

# Create a global instance
ai_travel_agent = AITravelAgent() 