#!/usr/bin/env python3
"""
Test script to debug AI response parsing
"""

import asyncio
import aiohttp
import json
import re
import os

async def test_ai_response():
    """Test what the AI is actually returning"""
    
    print("🔍 AI Response Debug Test")
    print("=" * 50)
    
    # Test with a simple request to see AI response
    test_data = {
        "origin": "LHR",
        "destination": "CDG",
        "departure_date": "2024-09-10",
        "passengers": 1,
        "guests": 1,
        "use_ai": True
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/search-with-ai",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    flights = result.get("flights", [])
                    hotels = result.get("hotels", [])
                    
                    print(f"📊 Results: {len(flights)} flights, {len(hotels)} hotels")
                    
                    if flights:
                        print(f"\n✅ Flights found:")
                        for i, flight in enumerate(flights[:3]):
                            print(f"   Flight {i+1}: {flight.get('airline')} - ${flight.get('price')} - {flight.get('ai_model')}")
                    else:
                        print(f"\n❌ No flights returned")
                    
                    if hotels:
                        print(f"\n✅ Hotels found:")
                        for i, hotel in enumerate(hotels[:3]):
                            print(f"   Hotel {i+1}: {hotel.get('name')} - ${hotel.get('price_per_night')} - {hotel.get('ai_model')}")
                    else:
                        print(f"\n❌ No hotels returned")
                    
                    return len(flights) > 0 or len(hotels) > 0
                else:
                    error_text = await response.text()
                    print(f"❌ Request failed: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_json_parsing():
    """Test the JSON parsing logic"""
    
    print(f"\n🧪 JSON Parsing Test")
    print("-" * 40)
    
    # Test cases for the regex pattern
    test_cases = [
        # Valid JSON array
        'Here is the flight data: [{"airline": "British Airways", "price": 500}]',
        
        # Invalid JSON
        'Here is the flight data: British Airways $500',
        
        # Empty response
        'No flights found',
        
        # Malformed JSON
        'Here is the data: [{"airline": "BA", "price": 500,}]',  # Trailing comma
        
        # No brackets
        '{"airline": "BA", "price": 500}'
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case[:50]}...")
        
        # Use the same regex as in the code
        json_match = re.search(r'\[.*\]', test_case, re.DOTALL)
        
        if json_match:
            try:
                data = json.loads(json_match.group())
                print(f"   ✅ JSON found and parsed: {len(data)} items")
                print(f"   Data: {data}")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON found but invalid: {e}")
        else:
            print(f"   ❌ No JSON array found")

async def test_direct_openai():
    """Test OpenAI API directly"""
    
    print(f"\n🧪 Direct OpenAI Test")
    print("-" * 40)
    
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test prompt
    test_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": "You are a travel data extraction expert. Extract structured travel information from the provided content."
            },
            {
                "role": "user",
                "content": "Extract flight information from this text: 'British Airways flight BA123 from London to Paris, departing at 10:30 AM, price $500. Virgin Atlantic flight VS456 from London to Paris, departing at 2:15 PM, price $450.' Return the data as a JSON array."
            }
        ],
        "max_tokens": 500,
        "temperature": 0.1
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=test_data,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    ai_response = result['choices'][0]['message']['content']
                    
                    print(f"✅ OpenAI API response:")
                    print(f"Response: {ai_response}")
                    
                    # Test the parsing
                    json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
                    if json_match:
                        try:
                            data = json.loads(json_match.group())
                            print(f"✅ Parsed JSON: {data}")
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON parsing failed: {e}")
                    else:
                        print(f"❌ No JSON array found in response")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ OpenAI API failed: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

async def main():
    """Main debug function"""
    
    print("🚀 AI Response Debug Suite")
    print("=" * 60)
    
    # Test AI response
    ai_working = await test_ai_response()
    
    # Test JSON parsing logic
    test_json_parsing()
    
    # Test direct OpenAI (if API key works)
    direct_working = await test_direct_openai()
    
    print(f"\n{'='*60}")
    print("📋 Debug Summary:")
    print(f"  - AI response: {'✅ Working' if ai_working else '❌ Failed'}")
    print(f"  - Direct OpenAI: {'✅ Working' if direct_working else '❌ Failed'}")
    
    if ai_working:
        print(f"\n🎉 SUCCESS: AI extraction is working!")
    else:
        print(f"\n⚠️  AI extraction is failing")
        print(f"   Check the JSON parsing logic and AI response format")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main()) 