import json
from modules.lp_solver import solve_crop_allocation

def run_scenarios():
    # افزایش سناریوها به ۱۰ مورد و خلاصه کردن توضیحات برای خوانایی بهتر در فایل متنی
    scenarios = [
        {"name": "۱. فراوانی", "water": 2000000, "fert": 100000, "land": 100},
        {"name": "۲. بحران آب", "water": 120000, "fert": 100000, "land": 100},
        {"name": "۳. کمبود کود", "water": 2000000, "fert": 8000, "land": 100},
        {"name": "۴. متوازن", "water": 350000, "fert": 25000, "land": 80},
        {"name": "۵. خشکسالی", "water": 20000, "fert": 1000, "land": 50},
        {"name": "۶. گندم‌خیز", "water": 500000, "fert": 50000, "land": 100},
        {"name": "۷. جوخیز", "water": 1000000, "fert": 12000, "land": 100},
        {"name": "۸. زمین مازاد", "water": 200000, "fert": 50000, "land": 500},
        {"name": "۹. بحران ۲گانه", "water": 80000, "fert": 5000, "land": 100},
        {"name": "۱۰. منابع باز", "water": 5000000, "fert": 200000, "land": 500}
    ]

    report = "==== 🧪 گزارش خلاصه تست سناریوهای LP (مدل جریمه مازاد) ====\n\n"

    for s in scenarios:
        res = solve_crop_allocation(s["water"], s["fert"], s["land"])
        
        # قالب‌بندی خلاصه‌تر و جدولی‌تر
        report += f"🔹 {s['name']:<15} | 🏞️ {s['land']:<3} | 💧 {s['water']:<7} | 🧪 {s['fert']:<6}  =>  "
        
        if res['status'] == 'Optimal':
            # شناسایی محصولاتی که از حد مجاز ۴۰ درصد عبور کرده و جریمه شده‌اند
            excesses = [n for n, v in zip(["گندم", "جو", "ذرت"], [res['wheat_excess'], res['barley_excess'], res['corn_excess']]) if v > 0]
            penalty_str = f"⚠️ جریمه: {','.join(excesses)}" if excesses else "✅ تنوع حفظ شد"
            
            report += f"💰 سود: {res['total_profit_million']:<6} م.ت | 🌾 گ:{res['wheat_ha']:<5} ج:{res['barley_ha']:<5} ذ:{res['corn_ha']:<5} | {penalty_str}\n"
        else:
            report += f"❌ وضعیت ناموجه: {res['status']}\n"

    # ذخیره گزارش در فایل
    output_file = "test_lp_results.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ {len(scenarios)} تست با موفقیت اجرا شد! نتایج در فایل '{output_file}' ذخیره گردید.")

if __name__ == "__main__":
    run_scenarios()
