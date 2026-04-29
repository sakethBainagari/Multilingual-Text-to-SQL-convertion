import os
import sys

from dotenv import load_dotenv

# Load .env file
load_dotenv()

try:
    import google.generativeai as genai
except Exception as e:
    print("Required package 'google-generativeai' not installed. Run: pip install google-generativeai")
    sys.exit(2)


def mask_key(k: str) -> str:
    if not k:
        return '<none>'
    return k[:6] + '...' + k[-3:]


def main():
    # Prefer GEMINI_API_KEYS (comma-separated) then GEMINI_API_KEY
    keys_env = os.getenv('GEMINI_API_KEYS', '')
    keys = [k.strip() for k in keys_env.split(',') if k.strip()]
    single = os.getenv('GEMINI_API_KEY')
    if single and not keys:
        keys = [single]

    if not keys:
        print('No Gemini API key found in environment. Set GEMINI_API_KEYS or GEMINI_API_KEY in .env')
        sys.exit(1)

    print(f"Loaded {len(keys)} key(s) from environment. Testing first key: {mask_key(keys[0])}")

    for idx, key in enumerate(keys, start=1):
        print(f"\n=== Testing key #{idx}: {mask_key(key)} ===")
        try:
            genai.configure(api_key=key)
            # Try multiple models - some may have different quota limits
            models_to_try = [
                'models/gemini-2.5-flash',
                'models/gemini-2.5-pro',
                'models/gemini-2.0-flash',
                'models/gemini-2.0-flash-lite',
            ]
            m = None
            for model_name in models_to_try:
                try:
                    m = genai.GenerativeModel(model_name)
                    print(f'Model handle created: {model_name}')
                    break
                except Exception as me:
                    print(f'Could not create {model_name}: {me}')
            
            if m is None:
                print('Could not initialize any model handle with this key')
                continue

            # Try generation with each model until one works
            prompt = 'Return the single token: OK'
            for model_name in models_to_try:
                try:
                    test_model = genai.GenerativeModel(model_name)
                    print(f'Testing generation with {model_name}...')
                    response = test_model.generate_content(prompt)
                    txt = getattr(response, 'text', str(response))
                    print(f'Generation OK with {model_name}, sample:', repr(txt[:200]))
                    print('Key appears valid.')
                    return 0
                except Exception as gen_e:
                    print(f'Generation failed with {model_name}:', gen_e)
                    continue
            print('All models failed for this key')
        except Exception as e:
            print('Configuration failed or key rejected:', e)

    print('\nNo valid Gemini key found among provided keys.')
    return 2


if __name__ == '__main__':
    sys.exit(main())
