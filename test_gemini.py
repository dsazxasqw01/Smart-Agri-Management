import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# 1. UNCOMMENT THESE LINES and set to your VPN port (10808 for v2ray, 7890 for clash)
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10808'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10808'

def run_gemini_test():
    print("🔄 Checking API key and connecting to Google Gemini servers...")
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # 2. THIS IS THE MAGIC FIX: Add transport='rest'
    genai.configure(api_key=api_key, transport='rest')
    
    model = genai.GenerativeModel("gemini-3-flash-preview")
    prompt = "Hello! Please reply in English with exactly one short sentence confirming you are connected."
    
    try:
        response = model.generate_content(prompt)
        print("✅ CONNECTION SUCCESSFUL! AI Response:")
        print(response.text.strip())
    except Exception as e:
        print(f"❌ CONNECTION FAILED: {str(e)}")

if __name__ == "__main__":
    run_gemini_test()