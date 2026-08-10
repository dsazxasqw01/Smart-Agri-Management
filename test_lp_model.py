import json
from modules.lp_solver import solve_crop_allocation

def run_scenarios():
    # 8 سناریوی متنوع برای تست عملکرد جریمه‌ها و ارزش‌های سایه‌ای
    scenarios = [
        {
            "name": "۱. فراوانی منابع (تست جریمه تک‌کشتی - فقط زمین محدود است)",
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
        },
        {
            "name": "۶. تمایل به کشت گندم (آب متوسط، کود عالی)",
            "water": 500000, "fert": 50000, "land": 100
        },
        {
            "name": "۷. تمایل به کشت جو (آب عالی، کود محدود)",
            "water": 1000000, "fert": 12000, "land": 100
        },
        {
            "name": "۸. زمین بسیار وسیع، منابع کم (تست رها کردن زمین)",
            "water": 200000, "fert": 50000, "land": 500
        }
    ]

    report = "==== 🧪 گزارش تست و تحلیل مدل برنامه‌ریزی خطی (ورژن جریمه مازاد) ====\n\n"

    for s in scenarios:
        res = solve_crop_allocation(s["water"], s["fert"], s["land"])
        
        report += f"🔹 سناریو: {s['name']}\n"
        report += f"📥 ورودی‌ها: مساحت={s['land']} | آب={s['water']} | کود={s['fert']}\n"
        report += f"📊 وضعیت حل: {res['status']}\n"
        
        if res['status'] == 'Optimal':
            report += f"💰 سود خالص برآوردی: {res['total_profit_million']} میلیون تومان\n"
            report += f"🌾 تخصیص زمین -> گندم: {res['wheat_ha']} | جو: {res['barley_ha']} | ذرت: {res['corn_ha']} (هکتار)\n"
            
            # نمایش مازادهایی که جریمه خورده‌اند
            excesses = []
            if res['wheat_excess'] > 0: excesses.append(f"گندم ({res['wheat_excess']} هکتار)")
            if res['barley_excess'] > 0: excesses.append(f"جو ({res['barley_excess']} هکتار)")
            if res['corn_excess'] > 0: excesses.append(f"ذرت ({res['corn_excess']} هکتار)")
            
            if excesses:
                report += f"⚠️ محصولات جریمه شده (عبور از حد ۴۰٪): {', '.join(excesses)}\n"
            else:
                report += "✅ تنوع عالی (هیچ محصولی جریمه تک‌کشتی نخورد)\n"
                
            report += f"💡 ارزش سایه‌ای -> آب: {res['water_shadow_price']} | کود: {res['fertilizer_shadow_price']} | زمین: {res['land_shadow_price']}\n"
        
        report += "-" * 65 + "\n"

    # ذخیره گزارش در فایل
    output_file = "test_lp_results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ تست‌ها با موفقیت اجرا شد! نتایج در فایل '{output_file}' ذخیره گردید.")

if __name__ == "__main__":
    run_scenarios()
