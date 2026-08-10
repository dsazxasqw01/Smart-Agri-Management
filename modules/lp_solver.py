import pulp
from typing import Dict, Any

def solve_crop_allocation(water_budget: float, fertilizer_budget: float, land_budget: float) -> Dict[str, Any]:
    """
    حل‌کننده مدل برنامه‌ریزی خطی (LP) جهت تخصیص بهینه منابع.
    در این مدل از تکنیک تقریب خطی تکه‌ای (Piecewise Linear Approximation) جهت اعمال
    تابع جریمه بهره‌وری خاک ناشی از کشت متوالی استفاده شده است.
    """
    model = pulp.LpProblem("Smart_Agri_Crop_Allocation", pulp.LpMaximize)

    # ==========================================
    # پارامترهای مدل‌سازی زراعی
    # شامل سود خالص برآورد شده، نیاز آبی (متر مکعب بر هکتار) و نیاز کودی (کیلوگرم بر هکتار)
    # ==========================================
    crops = {
        "wheat": {"profit": 55, "water": 3500, "fert": 200},
        "barley": {"profit": 40, "water": 4000, "fert": 100},
        "corn": {"profit": 90, "water": 8000, "fert": 400}
    }

    # تنظیمات پارامترهای تابع جریمه پلکانی (حفظ تنوع زراعی)
    num_tiers = 10
    max_penalty = 0.30
    penalty_power = 2.0

    tier_capacity = land_budget / num_tiers
    tier_vars = {c: [] for c in crops}
    
    # تعریف متغیرهای تصمیم در قالب طبقه‌بندی‌های کیفی اراضی
    for c in crops:
        for i in range(num_tiers):
            var = pulp.LpVariable(f'{c}_Tier_{i}', lowBound=0, upBound=tier_capacity, cat='Continuous')
            tier_vars[c].append(var)

    # فرمول‌بندی تابع هدف (بهینه‌سازی سود کل با اعمال ضریب افت کیفیت)
    total_profit = 0
    for c, data in crops.items():
        base_profit = data["profit"]
        for i in range(num_tiers):
            loss_factor = max_penalty * ((i / (num_tiers - 1)) ** penalty_power)
            tier_profit = base_profit * (1.0 - loss_factor)
            total_profit += tier_profit * tier_vars[c][i]
            
    model += total_profit, "Total_Profit"

    # اعمال قیود اصلی سیستم بر اساس ظرفیت منابع
    model += pulp.lpSum(crops[c]["water"] * tier_vars[c][i] for c in crops for i in range(num_tiers)) <= water_budget, "Water_Constraint"
    model += pulp.lpSum(crops[c]["fert"] * tier_vars[c][i] for c in crops for i in range(num_tiers)) <= fertilizer_budget, "Fertilizer_Constraint"
    model += pulp.lpSum(tier_vars[c][i] for c in crops for i in range(num_tiers)) <= land_budget, "Land_Constraint"

    # اجرای الگوریتم حل‌کننده
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status_str = pulp.LpStatus[model.status]

    if status_str == 'Optimal':
        areas = {c: sum(tier_vars[c][i].varValue for i in range(num_tiers)) for c in crops}
        excesses = {c: sum(tier_vars[c][i].varValue for i in range(1, num_tiers)) for c in crops}

        # استخراج متغیرهای دوگان (Shadow Prices) جهت تفسیر مدیریتی و هوش مصنوعی
        results = {
            "status": "Optimal",
            "wheat_ha": round(areas["wheat"], 2),
            "barley_ha": round(areas["barley"], 2),
            "corn_ha": round(areas["corn"], 2),
            "wheat_excess": round(excesses["wheat"], 2),
            "barley_excess": round(excesses["barley"], 2),
            "corn_excess": round(excesses["corn"], 2),
            "total_profit_million": round(pulp.value(model.objective), 2),
            "water_shadow_price": round(model.constraints["Water_Constraint"].pi, 4) if model.constraints["Water_Constraint"].pi else 0.0,
            "fertilizer_shadow_price": round(model.constraints["Fertilizer_Constraint"].pi, 4) if model.constraints["Fertilizer_Constraint"].pi else 0.0,
            "land_shadow_price": round(model.constraints["Land_Constraint"].pi, 4) if model.constraints["Land_Constraint"].pi else 0.0
        }
    else:
        results = {
            "status": status_str,
            "wheat_ha": 0, "barley_ha": 0, "corn_ha": 0,
            "wheat_excess": 0, "barley_excess": 0, "corn_excess": 0,
            "total_profit_million": 0,
            "water_shadow_price": 0.0, "fertilizer_shadow_price": 0.0, "land_shadow_price": 0.0
        }

    return results
