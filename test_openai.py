#!/usr/bin/env python3
"""
Simple OpenAI API test script
"""

import os
import asyncio
import aiohttp
import json

async def test_openai_api():
    """Test OpenAI API connectivity"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    print("🔍 OpenAI API Test")
    print("=" * 40)
    
    if not api_key:
        print("❌ No OpenAI API key found!")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test OpenAI API directly
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    test_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Hello! Just testing the API connection."}
        ],
        "max_tokens": 10
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=test_data
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ OpenAI API is working!")
                    print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ OpenAI API failed: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

async def test_travel_ai():
    """Test our travel AI endpoint"""
    
    print(f"\n🔍 Travel AI Endpoint Test")
    print("=" * 40)
    
    test_data = {
        "origin": "LHR",
        "destination": "CDG",
        "departure_date": "2024-09-10",
        "return_date": "2024-09-13",
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
                    
                    print(f"✅ Travel AI search successful!")
                    print(f"📊 Found {len(flights)} flights")
                    
                    # Check AI usage
                    ai_models = set(f.get('ai_model', 'unknown') for f in flights)
                    extraction_methods = set(f.get('extraction_method', 'unknown') for f in flights)
                    avg_confidence = sum(f.get('confidence', 0) for f in flights) / len(flights) if flights else 0
                    
                    print(f"\n🤖 AI Analysis:")
                    print(f"  - AI models: {', '.join(ai_models)}")
                    print(f"  - Extraction methods: {', '.join(extraction_methods)}")
                    print(f"  - Average confidence: {avg_confidence:.2f}")
                    
                    if 'openai' in ai_models:
                        print(f"\n🎉 SUCCESS: OpenAI is being used!")
                        return True
                    else:
                        print(f"\n⚠️  Still using pattern matching")
                        return False
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Travel AI failed: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Travel AI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OpenAI API & Travel AI Test Suite")
    print("=" * 60)
    
    # Test OpenAI API
    openai_working = asyncio.run(test_openai_api())
    
    # Test Travel AI
    travel_working = asyncio.run(test_travel_ai())
    
    print(f"\n{'='*60}")
    print("📋 Summary:")
    print(f"  - OpenAI API: {'✅ Working' if openai_working else '❌ Not Working'}")
    print(f"  - Travel AI: {'✅ Working' if travel_working else '❌ Not Working'}")
    
    if openai_working and travel_working:
        print(f"\n🎉 Everything is working perfectly!")
    elif openai_working:
        print(f"\n⚠️  OpenAI API works but Travel AI needs fixing")
    else:
        print(f"\n❌ OpenAI API key issue - check your key")
    
    print(f"{'='*60}") 