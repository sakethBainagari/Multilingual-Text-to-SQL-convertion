"""
Test script to verify Ollama connection and available models
"""
import requests

print("=" * 70)
print("OLLAMA CONNECTION TEST")
print("=" * 70)

ollama_url = "http://localhost:11434"

try:
    # Test if Ollama is running
    print("\n1. Testing Ollama connection...")
    response = requests.get(f"{ollama_url}/api/tags", timeout=5)
    
    if response.status_code == 200:
        print("   ✅ Ollama is running and accessible!")
        
        data = response.json()
        models = data.get('models', [])
        
        print(f"\n2. Available Ollama models ({len(models)} found):")
        print("-" * 70)
        
        for model in models:
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_gb = size / (1024**3)  # Convert to GB
            print(f"   ✅ {name:<25} ({size_gb:.1f} GB)")
        
        print("\n" + "=" * 70)
        print("OLLAMA STATUS: READY FOR USE")
        print("=" * 70)
        
    else:
        print(f"   ❌ Ollama returned status code: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("   ❌ Cannot connect to Ollama!")
    print("   Make sure Ollama is running on http://localhost:11434")
    print("\n   To start Ollama, run: ollama serve")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("WEB UI INTEGRATION:")
print("=" * 70)
print("You can now use Ollama models in the web UI at:")
print("http://localhost:5000")
print("\nSteps:")
print("1. Enter your natural language query")
print("2. Click 'Check Similarity & Process'")
print("3. In Step 3, you'll see TWO options:")
print("   - Left: Gemini (Google's AI)")
print("   - Right: Ollama (Your local models)")
print("4. Select an Ollama model from the dropdown")
print("5. Click 'Generate SQL with Ollama'")
print("=" * 70)
