import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ No GEMINI_API_KEY found in .env file")
    exit(1)

print(f"🔑 API Key loaded: {api_key[:10]}...")

genai.configure(api_key=api_key)

# List available models
try:
    print("🔍 Fetching available models...")
    models = genai.list_models()
    
    print("\n📋 Available Gemini models:")
    for model in models:
        if 'gemini' in model.name.lower():
            print(f"  ✅ {model.name}")
            print(f"     Display name: {model.display_name}")
            print(f"     Supported methods: {model.supported_generation_methods}")
            print()
    
    # Test with the first available model
    print("🧪 Testing with first available model...")
    for model in models:
        if 'gemini' in model.name.lower() and 'generateContent' in model.supported_generation_methods:
            try:
                test_model = genai.GenerativeModel(model.name)
                response = test_model.generate_content("Say hello")
                print(f"✅ SUCCESS with {model.name}: {response.text}")
                break
            except Exception as e:
                print(f"❌ Failed with {model.name}: {e}")
    
except Exception as e:
    print(f"❌ Error listing models: {e}")
    print("This might indicate an API key issue or API access problem")