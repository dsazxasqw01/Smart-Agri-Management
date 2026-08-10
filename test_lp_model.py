import json
from modules.lp_solver import solve_crop_allocation

def run_scenarios():
    # سناریوهای مختلف برای تست استرس مدل و بررسی رفتار آن در محدودیت‌های مختلف
    scenarios = [
        {
            "name": "۱. فراوانی منابع (فقط زمین محدود است)",
            "water": 2000000, "fert": 100000, "land": 100
        },
        {
            "name": "۲. کم‌آبی شدید (بحران آب)",
            "water": 120000, "fert": 100000, "land": 100
        },
        {
            "name": "۳. کمبود شدید کود شیمیایی",
            "water": 2000000, "fert": 8000, "land": 100
        },
        {
            "name": "۴. منابع متوازن اما محدود",
            "water": 350000, "fert": 25000, "land": 80
        },
        {
            "name": "۵. خشکسالی و کمبود سراسری",
            "water": 20000, "fert": 1000, "land": 50
        }
    ]

    report = "==== 🧪 گزارش تست و تحلیل مدل برنامه‌ریزی خطی (الگوی کشت) ====\n\n"

    for s in scenarios:
        res = solve_crop_allocation(s["water"], s["fert"], s["land"])
        
        report += f"🔹 سناریو: {s['name']}\n"
        report += f"📥 ورودی‌ها: مساحت={s['land']} هکتار | آب={s['water']} مترمکعب | کود={s['fert']} کیلوگرم\n"
        report += f"📊 وضعیت حل: {res['status']}\n"
        
        if res['status'] == 'Optimal':
            report += f"💰 سود خالص برآوردی: {res['total_profit_million']} میلیون تومان\n"
            report += f"🌾 تخصیص زمین -> گندم: {res['wheat_ha']} | جو: {res['barley_ha']} | ذرت: {res['corn_ha']} (هکتار)\n"
            report += f"💡 ارزش سایه‌ای -> آب: {res['water_shadow_price']} | کود: {res['fertilizer_shadow_price']} | زمین: {res['land_shadow_price']}\n"
        
        report += "-" * 60 + "\n"

    # ذخیره گزارش در یک فایل متنی
    output_file = "test_lp_results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ تست‌ها با موفقیت اجرا شد! نتایج در فایل '{output_file}' ذخیره گردید.")
    print("اکنون می‌توانید محتوای این فایل را کپی کرده و به هوش مصنوعی (AI) بدهید تا منطق تخصیص‌ها را تحلیل کند.")

if __name__ == "__main__":
    run_scenarios()
