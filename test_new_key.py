#!/usr/bin/env python3
"""
Test script for new OpenAI API key
"""

import asyncio
import aiohttp
import json

async def test_new_api_key(api_key):
    """Test a new OpenAI API key"""
    
    print("🔍 Testing New OpenAI API Key")
    print("=" * 50)
    
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
                json=test_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ SUCCESS! New API key is working!")
                    print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Main function to get and test new API key"""
    
    print("🔑 New OpenAI API Key Test")
    print("=" * 50)
    print("Please enter your NEW OpenAI API key:")
    print("(It should start with 'sk-' and be about 51 characters long)")
    print("(NOT the project key that starts with 'sk-proj-')")
    
    api_key = input("\nNew API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
    
    if api_key.startswith('sk-proj-'):
        print("⚠️  Warning: This looks like a project key. You need a regular API key.")
    
    print(f"\n{'='*50}")
    is_valid = asyncio.run(test_new_api_key(api_key))
    
    if is_valid:
        print(f"\n🎉 SUCCESS: Your new API key is working!")
        print(f"\n📝 Next steps:")
        print(f"1. Set the environment variable:")
        print(f"   export OPENAI_API_KEY='{api_key}'")
        print(f"2. Restart your server:")
        print(f"   cd server && pkill -f uvicorn && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &")
        print(f"3. Test the travel AI:")
        print(f"   curl -X POST 'http://localhost:8000/api/search-with-ai' -H 'Content-Type: application/json' -d '{{\"origin\": \"LHR\", \"destination\": \"CDG\", \"departure_date\": \"2024-09-10\", \"use_ai\": true}}'")
    else:
        print(f"\n❌ FAILED: New API key validation failed")
        print(f"Please check your OpenAI account and API key.")

if __name__ == "__main__":
    main() 