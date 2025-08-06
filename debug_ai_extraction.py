#!/usr/bin/env python3
"""
Debug script to test AI extraction and identify issues
"""

import asyncio
import aiohttp
import json
import time

async def test_ai_extraction():
    """Test AI extraction and compare with pattern matching"""
    
    print("🔍 AI Extraction Debug Test")
    print("=" * 50)
    
    # Test 1: Pattern matching (should work)
    print("\n🧪 Test 1: Pattern Matching (use_ai=false)")
    print("-" * 40)
    
    pattern_data = {
        "origin": "LHR",
        "destination": "CDG",
        "departure_date": "2024-09-10",
        "return_date": "2024-09-13",
        "passengers": 1,
        "guests": 1,
        "use_ai": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/search-with-ai",
                json=pattern_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    flights = result.get("flights", [])
                    hotels = result.get("hotels", [])
                    
                    print(f"✅ Pattern matching: {len(flights)} flights, {len(hotels)} hotels")
                    
                    if flights:
                        flight = flights[0]
                        print(f"   Sample flight: {flight.get('airline')} - ${flight.get('price')}")
                        print(f"   AI model: {flight.get('ai_model')}")
                        print(f"   Extraction method: {flight.get('extraction_method')}")
                    
                    return len(flights) > 0
                else:
                    print(f"❌ Pattern matching failed: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Pattern matching exception: {e}")
        return False

async def test_ai_extraction_detailed():
    """Test AI extraction with detailed error checking"""
    
    print("\n🧪 Test 2: AI Extraction (use_ai=true)")
    print("-" * 40)
    
    ai_data = {
        "origin": "LHR",
        "destination": "CDG",
        "departure_date": "2024-09-10",
        "return_date": "2024-09-13",
        "passengers": 1,
        "guests": 1,
        "use_ai": True
    }
    
    try:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/search-with-ai",
                json=ai_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)  # Longer timeout for AI
            ) as response:
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"⏱️  Request took {duration:.2f} seconds")
                
                if response.status == 200:
                    result = await response.json()
                    flights = result.get("flights", [])
                    hotels = result.get("hotels", [])
                    
                    print(f"📊 AI Results: {len(flights)} flights, {len(hotels)} hotels")
                    
                    if flights:
                        flight = flights[0]
                        print(f"   Sample flight: {flight.get('airline')} - ${flight.get('price')}")
                        print(f"   AI model: {flight.get('ai_model')}")
                        print(f"   Extraction method: {flight.get('extraction_method')}")
                        print(f"   Confidence: {flight.get('confidence', 'N/A')}")
                        
                        if flight.get('ai_model') == 'openai':
                            print("   🎉 SUCCESS: OpenAI is being used!")
                            return True
                        else:
                            print("   ⚠️  Still using pattern matching")
                            return False
                    else:
                        print("   ❌ No flights returned")
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ AI extraction failed: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ AI extraction timed out (60 seconds)")
        return False
    except Exception as e:
        print(f"❌ AI extraction exception: {e}")
        return False

async def test_single_source():
    """Test a single source to isolate the issue"""
    
    print("\n🧪 Test 3: Single Source Test")
    print("-" * 40)
    
    # Test with just one source to see if it's a timeout issue
    single_data = {
        "origin": "LHR",
        "destination": "CDG",
        "departure_date": "2024-09-10",
        "passengers": 1,
        "guests": 1,
        "use_ai": True
    }
    
    try:
        start_time = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/search-with-ai",
                json=single_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=120)  # Even longer timeout
            ) as response:
                
                end_time = time.time()
                duration = end_time - start_time
                
                print(f"⏱️  Single source request took {duration:.2f} seconds")
                
                if response.status == 200:
                    result = await response.json()
                    flights = result.get("flights", [])
                    
                    print(f"📊 Single source results: {len(flights)} flights")
                    
                    if flights:
                        for i, flight in enumerate(flights[:3]):  # Show first 3
                            print(f"   Flight {i+1}: {flight.get('airline')} - ${flight.get('price')} - {flight.get('ai_model')}")
                    
                    return len(flights) > 0
                else:
                    error_text = await response.text()
                    print(f"❌ Single source failed: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Single source exception: {e}")
        return False

async def main():
    """Main debug function"""
    
    print("🚀 AI Extraction Debug Suite")
    print("=" * 60)
    
    # Test pattern matching
    pattern_working = await test_ai_extraction()
    
    # Test AI extraction
    ai_working = await test_ai_extraction_detailed()
    
    # Test single source if AI failed
    if not ai_working:
        single_working = await test_single_source()
    else:
        single_working = True
    
    print(f"\n{'='*60}")
    print("📋 Debug Summary:")
    print(f"  - Pattern matching: {'✅ Working' if pattern_working else '❌ Failed'}")
    print(f"  - AI extraction: {'✅ Working' if ai_working else '❌ Failed'}")
    print(f"  - Single source: {'✅ Working' if single_working else '❌ Failed'}")
    
    if ai_working:
        print(f"\n🎉 SUCCESS: AI extraction is working!")
    elif pattern_working and not ai_working:
        print(f"\n⚠️  Pattern matching works but AI extraction fails")
        print(f"   This suggests an issue with AI processing or timeouts")
    else:
        print(f"\n❌ Both methods are failing")
        print(f"   Check server configuration and network connectivity")
    
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main()) 