import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_ai_analysis(user_message: str, system_prompt: str) -> str:
    """
    ارسال پیام کاربر به همراه کانتکست به مدل Gemini.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return '⚠️ **خطای سیستم:** کلید `GEMINI_API_KEY` یافت نشد. لطفاً آن را در فایل .env وارد کنید.'

    try:
        genai.configure(api_key=api_key, transport='rest')
        
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_prompt
        )
        
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f'❌ **خطا در ارتباط با سرور هوش مصنوعی:**\n{str(e)}'