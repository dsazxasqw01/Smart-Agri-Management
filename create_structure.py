import os

# نام پوشه اصلی پروژه
project_name = "Sharif_Agri_Project"

# لیست پوشه‌های داخلی
folders = [
    "modules",
    "assets"
]

# دیکشنری فایل‌ها و محتوای پیش‌فرض آن‌ها
files = {
    "modules/__init__.py": "",
    "modules/lp_solver.py": "# کدهای ماژول برنامه‌ریزی خطی (LP)\n",
    "modules/ga_solver.py": "# کدهای ماژول الگوریتم ژنتیک (GA)\n",
    "modules/llm_chatbot.py": "# کدهای ماژول چت‌بات و هوش مصنوعی\n",
    "assets/mock_data.csv": "id,x,y\n1,10,20\n", # یک فایل دیتای فرضی تستی
    "app.py": "# هسته اصلی رابط کاربری Streamlit\nimport streamlit as st\n",
    "requirements.txt": "streamlit==1.36.0\npulp==2.8.0\nnumpy==1.26.4\npandas==2.2.2\nmatplotlib==3.9.0\ngroq==0.9.0\n",
    ".gitignore": "venv/\n__pycache__/\n.env\n.DS_Store\n",
    "README.md": "# سیستم مدیریت مجتمع کشت و صنعت هوشمند 🌾\nپروژه پایانی درس برنامه‌نویسی پیشرفته - دانشگاه صنعتی شریف.\n"
}

def create_project_structure():
    print(f"🚀 در حال ساخت پروژه: {project_name} ...")
    
    # ساخت پوشه اصلی
    os.makedirs(project_name, exist_ok=True)
    os.chdir(project_name)
    
    # ساخت پوشه‌های فرعی
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"📁 پوشه ساخته شد: {folder}/")
        
    # ساخت فایل‌ها
    for filepath, content in files.items():
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 فایل ساخته شد: {filepath}")
        
    print("\n✅ ساختار ماژولار پروژه با موفقیت ایجاد شد!")
    print("⚠️ نکته: برای فایل assets/logo.png یک عکس دلخواه با فرمت png در آن مسیر قرار دهید.")

if __name__ == "__main__":
    create_project_structure()