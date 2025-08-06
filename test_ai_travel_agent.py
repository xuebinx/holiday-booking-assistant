#!/usr/bin/env python3
"""
Test script for AI Travel Agent
"""

import asyncio
import aiohttp
import json
from datetime import date, timedelta

async def test_ai_travel_agent():
    """Test the AI travel agent with different scenarios"""
    
    base_url = "http://localhost:8000"
    
    # Test scenarios
    test_cases = [
        {
            "name": "London to Paris (Short trip)",
            "data": {
                "origin": "LHR",
                "destination": "CDG", 
                "departure_date": "2024-09-10",
                "return_date": "2024-09-13",
                "passengers": 2,
                "guests": 2,
                "use_ai": False
            }
        },
        {
            "name": "London to New York (Long trip)",
            "data": {
                "origin": "LHR",
                "destination": "JFK",
                "departure_date": "2024-10-15", 
                "return_date": "2024-10-22",
                "passengers": 1,
                "guests": 1,
                "use_ai": False
            }
        },
        {
            "name": "London to Tokyo (International)",
            "data": {
                "origin": "LHR",
                "destination": "NRT",
                "departure_date": "2024-11-01",
                "return_date": "2024-11-08", 
                "passengers": 3,
                "guests": 3,
                "use_ai": False
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_case in test_cases:
            print(f"\n{'='*60}")
            print(f"Testing: {test_case['name']}")
            print(f"{'='*60}")
            
            try:
                async with session.post(
                    f"{base_url}/api/search-with-ai",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Analyze results
                        flights = result.get("flights", [])
                        hotels = result.get("hotels", [])
                        metadata = result.get("search_metadata", {})
                        
                        print(f"✅ Search successful!")
                        print(f"📊 Results:")
                        print(f"   - Flights found: {len(flights)}")
                        print(f"   - Hotels found: {len(hotels)}")
                        print(f"   - Search method: {metadata.get('use_ai', False)}")
                        
                        # Show flight details
                        if flights:
                            print(f"\n✈️  Flight Options:")
                            for i, flight in enumerate(flights[:3], 1):  # Show first 3
                                print(f"   {i}. {flight['airline']} - ${flight['price']} "
                                      f"({flight['departure_time']} → {flight['arrival_time']}) "
                                      f"[{flight['source']}]")
                        
                        # Show hotel details  
                        if hotels:
                            print(f"\n🏨 Hotel Options:")
                            for i, hotel in enumerate(hotels[:3], 1):  # Show first 3
                                print(f"   {i}. {hotel['name']} - ${hotel['price_per_night']}/night "
                                      f"({hotel['rating']}★) [{hotel['source']}]")
                        
                        # Show extraction quality
                        if flights:
                            avg_confidence = sum(f['confidence'] for f in flights) / len(flights)
                            extraction_methods = set(f.get('extraction_method', 'unknown') for f in flights)
                            print(f"\n🔍 Extraction Quality:")
                            print(f"   - Average confidence: {avg_confidence:.2f}")
                            print(f"   - Extraction methods: {', '.join(extraction_methods)}")
                        
                    else:
                        print(f"❌ Search failed: {response.status}")
                        error_text = await response.text()
                        print(f"Error: {error_text}")
                        
            except Exception as e:
                print(f"❌ Request failed: {e}")
            
            # Wait between requests
            await asyncio.sleep(1)

async def test_with_real_ai():
    """Test with AI enabled (requires API keys)"""
    print(f"\n{'='*60}")
    print("Testing with AI enabled (requires API keys)")
    print(f"{'='*60}")
    
    # Check if API keys are available
    import os
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not openai_key and not anthropic_key:
        print("❌ No AI API keys found!")
        print("To test with AI, set one of these environment variables:")
        print("   export OPENAI_API_KEY='your-openai-key'")
        print("   export ANTHROPIC_API_KEY='your-anthropic-key'")
        return
    
    print(f"✅ AI keys found: OpenAI={bool(openai_key)}, Anthropic={bool(anthropic_key)}")
    
    # Test with AI enabled
    test_data = {
        "origin": "LHR",
        "destination": "CDG",
        "departure_date": "2024-09-10",
        "return_date": "2024-09-13", 
        "passengers": 1,
        "guests": 1,
        "use_ai": True
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                "http://localhost:8000/api/search-with-ai",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    flights = result.get("flights", [])
                    
                    print(f"✅ AI search successful!")
                    print(f"📊 Found {len(flights)} flights")
                    
                    # Check if AI was actually used
                    ai_models = set(f.get('ai_model', 'unknown') for f in flights)
                    print(f"🤖 AI models used: {', '.join(ai_models)}")
                    
                    if flights:
                        avg_confidence = sum(f['confidence'] for f in flights) / len(flights)
                        print(f"🔍 Average confidence: {avg_confidence:.2f}")
                        
                else:
                    print(f"❌ AI search failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ AI test failed: {e}")

if __name__ == "__main__":
    print("🚀 AI Travel Agent Test Suite")
    print("=" * 60)
    
    # Run basic tests
    asyncio.run(test_ai_travel_agent())
    
    # Run AI tests
    asyncio.run(test_with_real_ai())
    
    print(f"\n{'='*60}")
    print("✅ Test suite completed!")
    print(f"{'='*60}") 