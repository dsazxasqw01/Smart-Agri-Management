import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_ai_analysis(user_message: str, system_prompt: str) -> str:
    """
    ماژول ارتباط با مدل زبانی بزرگ (LLM) جهت پردازش درخواست‌های کاربر و ارائه تحلیل حساسیت.
    با استفاده از سرویس ابری Google Gemini API پیاده‌سازی شده است.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return '⚠️ **خطای سیستم:** کلید `GEMINI_API_KEY` یافت نشد. لطفاً پیکربندی سرور را بررسی کنید.'

    try:
        genai.configure(api_key=api_key, transport='rest')
        
        model = genai.GenerativeModel(
            model_name='gemini-3.6-flash',
            system_instruction=system_prompt
        )
        
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f'❌ **خطا در برقراری ارتباط با سرویس هوش مصنوعی:**\n{str(e)}'
