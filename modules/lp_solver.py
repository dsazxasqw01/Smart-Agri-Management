import pulp
from typing import Dict, Any

def solve_crop_allocation(water_budget: float, fertilizer_budget: float) -> Dict[str, Any]:
    """
    حل‌کننده ریاضی مسئله برنامه‌ریزی خطی (LP) برای الگوی کشت بهینه.

    :param water_budget: سقف حق‌آبه در دسترس مجتمع (به متر مکعب)
    :param fertilizer_budget: سقف موجودی انبار کود (به کیلوگرم)
    :return: دیکشنری شامل وضعیت حل، متغیرهای تصمیم، سود بهینه و ارزش‌های سایه‌ای
    """

    # 1. تعریف شیء مدل: چون هدف بیشینه‌سازی سود است از LpMaximize استفاده می‌کنیم
    model = pulp.LpProblem("Smart_Agri_Crop_Allocation", pulp.LpMaximize)

    # 2. تعریف متغیرهای تصمیم (پیوسته و بزرگتر مساوی صفر)
    # Continuous یعنی مساحت می‌تواند عدد اعشاری باشد (مثلا 2.5 هکتار)
    wheat = pulp.LpVariable('Wheat_Area_ha', lowBound=0, cat='Continuous')
    barley = pulp.LpVariable('Barley_Area_ha', lowBound=0, cat='Continuous')
    corn = pulp.LpVariable('Corn_Area_ha', lowBound=0, cat='Continuous')

    # 3. تعریف تابع هدف (اضافه کردن به مدل با عملگر +=)
    # سود هر هکتار (میلیون تومان): گندم=45، جو=35، ذرت=65
    model += 45 * wheat + 35 * barley + 65 * corn, "Total_Profit"

    # 4. تعریف قیود مسئله (Constraints)
    # بسیار مهم: برای گرفتن Shadow Price در PuLP، حتماً باید به قیود "نام" (String) بدهیم.

    # قید نیاز آبی (متر مکعب بر هکتار): گندم=4500، جو=3500، ذرت=7500
    model += (4500 * wheat + 3500 * barley + 7500 * corn <= water_budget, "Water_Constraint")

    # قید نیاز کودی (کیلوگرم بر هکتار): گندم=250، جو=150، ذرت=400
    model += (250 * wheat + 150 * barley + 400 * corn <= fertilizer_budget, "Fertilizer_Constraint")

    # 5. حل مدل با حل‌کننده پیش‌فرض PuLP (بدون نمایش پیام‌های اضافه در کنسول)
    model.solve(pulp.PULP_CBC_CMD(msg=False))

    # 6. بررسی وضعیت و استخراج نتایج
    status_str = pulp.LpStatus[model.status]

    if status_str == 'Optimal':
        # استخراج ارزش‌های سایه‌ای (Shadow Prices/Dual Values) با استفاده از ویژگی .pi
        water_shadow = model.constraints["Water_Constraint"].pi
        fert_shadow = model.constraints["Fertilizer_Constraint"].pi

        results = {
            "status": "Optimal",
            "wheat_ha": round(wheat.varValue, 2),
            "barley_ha": round(barley.varValue, 2),
            "corn_ha": round(corn.varValue, 2),
            "total_profit_million": round(pulp.value(model.objective), 2),
            # ارزش سایه‌ای نشان می‌دهد افزایش یک واحد از منبع، چقدر به تابع هدف می‌افزاید
            "water_shadow_price": round(water_shadow, 4),
            "fertilizer_shadow_price": round(fert_shadow, 4)
        }
    else:
        # اگر منابع به قدری کم باشد که مسئله موجه نباشد
        results = {
            "status": status_str,
            "wheat_ha": 0, "barley_ha": 0, "corn_ha": 0,
            "total_profit_million": 0,
            "water_shadow_price": 0, "fertilizer_shadow_price": 0
        }

    return results

if __name__ == "__main__":
    test_results = solve_crop_allocation(water_budget=100000, fertilizer_budget=5000)
    print(test_results)