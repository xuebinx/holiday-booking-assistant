#!/usr/bin/env python3
"""
Simple OpenAI API key verification script
"""

import os
import asyncio
import aiohttp
import json

async def verify_openai_key(api_key):
    """Verify if an OpenAI API key is valid"""
    
    print(f"🔍 Verifying OpenAI API key...")
    print(f"Key starts with: {api_key[:10]}...")
    print(f"Key length: {len(api_key)} characters")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple test request
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
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ API key is valid!")
                    print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ API key validation failed: {response.status}")
                    print(f"Error: {error_text}")
                    
                    # Parse error details
                    try:
                        error_json = json.loads(error_text)
                        error_type = error_json.get('error', {}).get('type', 'unknown')
                        error_message = error_json.get('error', {}).get('message', 'No message')
                        
                        print(f"\n🔍 Error Analysis:")
                        print(f"  - Error type: {error_type}")
                        print(f"  - Error message: {error_message}")
                        
                        if error_type == 'invalid_api_key':
                            print(f"  - Solution: Check your API key format and validity")
                        elif error_type == 'insufficient_quota':
                            print(f"  - Solution: Add billing to your OpenAI account")
                        elif error_type == 'billing_not_active':
                            print(f"  - Solution: Activate billing in your OpenAI account")
                        else:
                            print(f"  - Solution: Check your OpenAI account status")
                            
                    except:
                        print(f"  - Could not parse error details")
                    
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out - check your internet connection")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def get_api_key():
    """Get API key from user input"""
    print("🔑 OpenAI API Key Verification")
    print("=" * 50)
    
    # Try to get from environment first
    env_key = os.getenv('OPENAI_API_KEY')
    if env_key:
        print(f"Found API key in environment: {env_key[:10]}...")
        use_env = input("Use this key? (y/n): ").lower().strip()
        if use_env == 'y':
            return env_key
    
    # Get from user input
    print("\nPlease enter your OpenAI API key:")
    print("(It should start with 'sk-' and be about 51 characters long)")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return None
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
    
    if len(api_key) < 40:
        print("⚠️  Warning: API key seems too short")
    
    return api_key

async def main():
    """Main verification function"""
    
    api_key = get_api_key()
    if not api_key:
        print("❌ No API key to verify")
        return
    
    print(f"\n{'='*50}")
    is_valid = await verify_openai_key(api_key)
    
    print(f"\n{'='*50}")
    if is_valid:
        print("🎉 SUCCESS: Your OpenAI API key is working!")
        print("You can now use it with the travel AI system.")
        
        # Test with travel AI
        print(f"\n🧪 Testing with travel AI system...")
        await test_travel_ai_with_key(api_key)
    else:
        print("❌ FAILED: API key validation failed")
        print("Please check your OpenAI account and API key.")

async def test_travel_ai_with_key(api_key):
    """Test the travel AI system with the verified key"""
    
    # Set the key temporarily
    os.environ['OPENAI_API_KEY'] = api_key
    
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
                    
                    print(f"✅ Travel AI test successful!")
                    print(f"📊 Found {len(flights)} flights")
                    
                    # Check AI usage
                    ai_models = set(f.get('ai_model', 'unknown') for f in flights)
                    extraction_methods = set(f.get('extraction_method', 'unknown') for f in flights)
                    
                    print(f"\n🤖 AI Analysis:")
                    print(f"  - AI models: {', '.join(ai_models)}")
                    print(f"  - Extraction methods: {', '.join(extraction_methods)}")
                    
                    if 'openai' in ai_models:
                        print(f"\n🎉 SUCCESS: OpenAI is being used in travel AI!")
                    else:
                        print(f"\n⚠️  Still using pattern matching - check server logs")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ Travel AI test failed: {response.status}")
                    print(f"Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Travel AI test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 