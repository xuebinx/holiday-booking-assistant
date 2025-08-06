#!/usr/bin/env python3
"""
Debug script to check AI configuration and test AI functionality
"""

import os
import asyncio
import aiohttp
import json

async def debug_ai_configuration():
    """Debug AI configuration and test functionality"""
    
    print("🔍 AI Configuration Debug")
    print("=" * 50)
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    print(f"OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    if openai_key:
        print(f"  Key starts with: {openai_key[:10]}...")
    
    print(f"Anthropic API Key: {'✅ Set' if anthropic_key else '❌ Not set'}")
    if anthropic_key:
        print(f"  Key starts with: {anthropic_key[:10]}...")
    
    if not openai_key and not anthropic_key:
        print("\n❌ No AI API keys found!")
        print("To enable AI, set one of these environment variables:")
        print("  export OPENAI_API_KEY='your-openai-key'")
        print("  export ANTHROPIC_API_KEY='your-anthropic-key'")
        return False
    
    print(f"\n✅ AI keys found! Testing AI functionality...")
    
    # Test AI functionality
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
                    
                    print(f"\n✅ AI search successful!")
                    print(f"📊 Found {len(flights)} flights")
                    
                    # Analyze AI usage
                    ai_models = set(f.get('ai_model', 'unknown') for f in flights)
                    extraction_methods = set(f.get('extraction_method', 'unknown') for f in flights)
                    avg_confidence = sum(f['confidence'] for f in flights) / len(flights) if flights else 0
                    
                    print(f"\n🤖 AI Analysis:")
                    print(f"  - AI models used: {', '.join(ai_models)}")
                    print(f"  - Extraction methods: {', '.join(extraction_methods)}")
                    print(f"  - Average confidence: {avg_confidence:.2f}")
                    
                    # Check if AI was actually used
                    if 'openai' in ai_models or 'anthropic' in ai_models:
                        print(f"\n🎉 SUCCESS: AI is working!")
                        print(f"   Real AI extraction is being used.")
                    elif 'pattern_matching' in ai_models:
                        print(f"\n⚠️  WARNING: AI keys set but still using pattern matching")
                        print(f"   This might indicate an issue with the AI service.")
                    else:
                        print(f"\n❓ UNKNOWN: Unexpected AI model: {ai_models}")
                    
                    return True
                    
                else:
                    print(f"\n❌ AI search failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"\n❌ AI test failed: {e}")
        return False

async def test_without_ai():
    """Test without AI for comparison"""
    
    print(f"\n🔍 Testing without AI (for comparison)")
    print("=" * 50)
    
    test_data = {
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
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    flights = result.get("flights", [])
                    
                    print(f"✅ Pattern matching search successful!")
                    print(f"📊 Found {len(flights)} flights")
                    
                    ai_models = set(f.get('ai_model', 'unknown') for f in flights)
                    extraction_methods = set(f.get('extraction_method', 'unknown') for f in flights)
                    avg_confidence = sum(f['confidence'] for f in flights) / len(flights) if flights else 0
                    
                    print(f"\n📊 Pattern Matching Analysis:")
                    print(f"  - AI models used: {', '.join(ai_models)}")
                    print(f"  - Extraction methods: {', '.join(extraction_methods)}")
                    print(f"  - Average confidence: {avg_confidence:.2f}")
                    
                    return True
                    
                else:
                    print(f"❌ Pattern matching search failed: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ Pattern matching test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AI Travel Agent Debug Tool")
    print("=" * 60)
    
    # Test AI configuration
    ai_working = asyncio.run(debug_ai_configuration())
    
    # Test without AI for comparison
    pattern_working = asyncio.run(test_without_ai())
    
    print(f"\n{'='*60}")
    print("📋 Summary:")
    print(f"  - AI Configuration: {'✅ Working' if ai_working else '❌ Not Working'}")
    print(f"  - Pattern Matching: {'✅ Working' if pattern_working else '❌ Not Working'}")
    
    if ai_working and pattern_working:
        print(f"\n🎉 Both AI and pattern matching are working!")
        print(f"   You can now test with both methods.")
    elif pattern_working:
        print(f"\n⚠️  Only pattern matching is working.")
        print(f"   Set up AI API keys to enable AI extraction.")
    else:
        print(f"\n❌ Neither method is working.")
        print(f"   Check your server configuration.")
    
    print(f"{'='*60}") 