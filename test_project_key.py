#!/usr/bin/env python3
"""
Test script for OpenAI project key with different models
"""

import asyncio
import aiohttp
import json
import os

async def test_project_key():
    """Test the project key with different models"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return False
    
    print("🔍 Testing OpenAI Project Key")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test different models
    models_to_test = [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    ]
    
    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")
        
        test_data = {
            "model": model,
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
                        print(f"✅ SUCCESS with {model}!")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed with {model}: {response.status}")
                        
                        try:
                            error_json = json.loads(error_text)
                            error_message = error_json.get('error', {}).get('message', 'No message')
                            print(f"   Error: {error_message[:100]}...")
                        except:
                            print(f"   Error: {error_text[:100]}...")
                            
        except Exception as e:
            print(f"❌ Exception with {model}: {e}")
    
    return False

async def test_models_list():
    """Test if we can list available models"""
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No OpenAI API key found in environment")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        return False
    
    print(f"\n🔍 Testing Models List")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.openai.com/v1/models",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    models = result.get('data', [])
                    print(f"✅ SUCCESS! Found {len(models)} models:")
                    
                    for model in models[:5]:  # Show first 5
                        model_id = model.get('id', 'unknown')
                        print(f"   - {model_id}")
                    
                    if len(models) > 5:
                        print(f"   ... and {len(models) - 5} more")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to list models: {response.status}")
                    print(f"Error: {error_text}")
                    return False
                    
    except Exception as e:
        print(f"❌ Exception listing models: {e}")
        return False

if __name__ == "__main__":
    print("🚀 OpenAI Project Key Test Suite")
    print("=" * 60)
    
    # Test different models
    models_working = asyncio.run(test_project_key())
    
    # Test models list
    list_working = asyncio.run(test_models_list())
    
    print(f"\n{'='*60}")
    print("📋 Summary:")
    print(f"  - Models working: {'✅ Yes' if models_working else '❌ No'}")
    print(f"  - Can list models: {'✅ Yes' if list_working else '❌ No'}")
    
    if models_working:
        print(f"\n🎉 SUCCESS: Your project key works with some models!")
        print(f"   You can use it with the travel AI system.")
    else:
        print(f"\n❌ FAILED: Project key doesn't work with any tested models")
        print(f"   Recommendation: Create a new API key with proper permissions")
    
    print(f"{'='*60}") 