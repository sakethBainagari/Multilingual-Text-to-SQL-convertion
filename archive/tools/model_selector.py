#!/usr/bin/env python3
"""
Model Selection Tool for Advanced NL-to-SQL System
Allows easy switching between Ollama models and online models
"""

import os
import requests
import json
from typing import List, Dict

class ModelSelector:
    """Tool to select and configure models for the NL-to-SQL system"""
    
    def __init__(self):
        self.env_file = ".env"
        self.ollama_base_url = "http://localhost:11434"
        
    def get_ollama_models(self) -> List[Dict]:
        """Get list of available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                return response.json().get('models', [])
            return []
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            return []
    
    def update_env_file(self, use_ollama: bool, ollama_model: str = None):
        """Update .env file with model configuration"""
        env_lines = []
        
        # Read current .env file
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                env_lines = f.readlines()
        
        # Update configuration
        updated_lines = []
        found_use_ollama = False
        found_ollama_model = False
        
        for line in env_lines:
            if line.startswith('USE_OLLAMA='):
                updated_lines.append(f'USE_OLLAMA={"true" if use_ollama else "false"}\n')
                found_use_ollama = True
            elif line.startswith('OLLAMA_MODEL=') and ollama_model:
                updated_lines.append(f'OLLAMA_MODEL={ollama_model}\n')
                found_ollama_model = True
            else:
                updated_lines.append(line)
        
        # Add missing configuration
        if not found_use_ollama:
            updated_lines.append(f'USE_OLLAMA={"true" if use_ollama else "false"}\n')
        if not found_ollama_model and ollama_model:
            updated_lines.append(f'OLLAMA_MODEL={ollama_model}\n')
        
        # Write updated .env file
        with open(self.env_file, 'w') as f:
            f.writelines(updated_lines)
        
        print(f"✅ Updated {self.env_file}")
    
    def show_current_config(self):
        """Show current model configuration"""
        print("\n📊 Current Configuration:")
        print("-" * 30)
        
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.startswith(('USE_OLLAMA=', 'OLLAMA_MODEL=', 'GEMINI_API_KEY=', 'OLLAMA_BASE_URL=')):
                        key, value = line.strip().split('=', 1)
                        if key == 'GEMINI_API_KEY' and value != 'your_gemini_api_key_here':
                            print(f"   {key}: {'*' * 20}")
                        else:
                            print(f"   {key}: {value}")
        else:
            print("   No .env file found")
    
    def main_menu(self):
        """Show main selection menu"""
        print("🤖 Advanced NL-to-SQL Model Selector")
        print("=" * 40)
        
        self.show_current_config()
        
        print("\nAvailable Options:")
        print("1. 🔄 Use Ollama (Offline Models)")
        print("2. 🌐 Use Gemini AI (Online)")
        print("3. 📊 Show Model Status")
        print("4. ❌ Exit")
        
        while True:
            try:
                choice = input("\nEnter your choice (1-4): ").strip()
                
                if choice == '1':
                    self.select_ollama_model()
                elif choice == '2':
                    self.select_gemini()
                elif choice == '3':
                    self.show_model_status()
                elif choice == '4':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-4.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
    
    def select_ollama_model(self):
        """Select Ollama model"""
        print("\n🔄 Configuring Ollama (Offline) Models")
        print("-" * 35)
        
        models = self.get_ollama_models()
        
        if not models:
            print("❌ No Ollama models found. Make sure Ollama is running and models are installed.")
            print("   Install models with: ollama pull mistral")
            return
        
        print("\n📋 Available Ollama Models:")
        for i, model in enumerate(models, 1):
            name = model.get('name', 'Unknown')
            size = model.get('size', 0)
            size_mb = size / (1024 * 1024) if size else 0
            modified = model.get('modified_at', '')
            
            print(f"{i}. {name}")
            print(f"   Size: {size_mb:.1f} MB")
            if modified:
                print(f"   Modified: {modified[:10]}")
        
        while True:
            try:
                choice = input(f"\nSelect model (1-{len(models)}) or 'back': ").strip()
                
                if choice.lower() == 'back':
                    return
                
                model_idx = int(choice) - 1
                if 0 <= model_idx < len(models):
                    selected_model = models[model_idx]['name']
                    
                    # Test the model
                    print(f"\n⏳ Testing model '{selected_model}'...")
                    if self.test_ollama_model(selected_model):
                        self.update_env_file(use_ollama=True, ollama_model=selected_model)
                        print(f"✅ Successfully configured Ollama model: {selected_model}")
                        print("🔄 Restart the main application to use the new model")
                        return
                    else:
                        print(f"❌ Failed to test model '{selected_model}'")
                else:
                    print("❌ Invalid selection")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                return
    
    def test_ollama_model(self, model_name: str) -> bool:
        """Test if Ollama model works"""
        try:
            payload = {
                "model": model_name,
                "prompt": "Test prompt: What is 2+2?",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Model test failed: {e}")
            return False
    
    def select_gemini(self):
        """Configure Gemini AI"""
        print("\n🌐 Configuring Gemini AI (Online)")
        print("-" * 30)
        
        # Check if API key exists
        api_key = None
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        
        if api_key and api_key != 'your_gemini_api_key_here':
            print("✅ Gemini API key found")
            confirm = input("Use Gemini AI? (y/n): ").lower().startswith('y')
            
            if confirm:
                self.update_env_file(use_ollama=False)
                print("✅ Configured to use Gemini AI (online)")
                print("🔄 Restart the main application to use Gemini")
        else:
            print("❌ No Gemini API key found")
            print("📋 To use Gemini AI:")
            print("1. Get API key from: https://makersuite.google.com/app/apikey")
            print("2. Edit .env file and add: GEMINI_API_KEY=your_key_here")
    
    def show_model_status(self):
        """Show detailed model status"""
        print("\n📊 Detailed Model Status")
        print("-" * 25)
        
        # Check Ollama
        print("\n🔄 Ollama (Offline):")
        models = self.get_ollama_models()
        if models:
            print(f"   ✅ Connected ({len(models)} models available)")
            for model in models[:3]:  # Show first 3
                name = model.get('name', 'Unknown')
                size = model.get('size', 0) / (1024 * 1024)
                print(f"   - {name} ({size:.1f} MB)")
            if len(models) > 3:
                print(f"   ... and {len(models) - 3} more")
        else:
            print("   ❌ Not available (check if Ollama is running)")
        
        # Check Gemini
        print("\n🌐 Gemini AI (Online):")
        api_key = None
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        
        if api_key and api_key != 'your_gemini_api_key_here':
            print("   ✅ API key configured")
        else:
            print("   ❌ No API key found")

def main():
    selector = ModelSelector()
    selector.main_menu()

if __name__ == "__main__":
    main()