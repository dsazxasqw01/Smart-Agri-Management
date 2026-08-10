import pulp
from typing import Dict, Any

def solve_crop_allocation(water_budget: float, fertilizer_budget: float, land_budget: float) -> Dict[str, Any]:
    """
    حل‌کننده ریاضی مسئله برنامه‌ریزی خطی (LP) برای الگوی کشت بهینه
    با استفاده از تکنیک پیشرفته Piecewise Linear Approximation برای ایجاد جریمه پیوسته و نرم.
    """
    model = pulp.LpProblem("Smart_Agri_Crop_Allocation", pulp.LpMaximize)

    # ==========================================
    # تعریف متغیرها در ۴ پله (Tier) برای هر محصول
    # این کار یک منحنی غیرخطی و نرم را شبیه‌سازی می‌کند
    # ==========================================
    w = [pulp.LpVariable(f'Wheat_T{i}', lowBound=0, cat='Continuous') for i in range(1, 5)]
    b = [pulp.LpVariable(f'Barley_T{i}', lowBound=0, cat='Continuous') for i in range(1, 5)]
    c = [pulp.LpVariable(f'Corn_T{i}', lowBound=0, cat='Continuous') for i in range(1, 5)]

    total_wheat = pulp.lpSum(w)
    total_barley = pulp.lpSum(b)
    total_corn = pulp.lpSum(c)
    total_planted = total_wheat + total_barley + total_corn

    # ==========================================
    # تابع هدف: سود حاشیه‌ای نزولی (Diminishing Marginal Returns)
    # سود پایه: گندم 50، جو 40، ذرت 90
    # پله ۱ (تا ۳۰٪): سود کامل
    # پله ۲ (۳۰ تا ۵۰٪): ۱۰٪ افت سود
    # پله ۳ (۵۰ تا ۷۰٪): ۲۵٪ افت سود
    # پله ۴ (۷۰ تا ۱۰۰٪): ۵۰٪ افت سود
    # ==========================================
    profit_w = 50 * w[0] + 45.0 * w[1] + 37.5 * w[2] + 25.0 * w[3]
    profit_b = 40 * b[0] + 36.0 * b[1] + 30.0 * b[2] + 20.0 * b[3]
    profit_c = 90 * c[0] + 81.0 * c[1] + 67.5 * c[2] + 45.0 * c[3]

    model += profit_w + profit_b + profit_c, "Total_Profit"

    # ==========================================
    # قیود منابع فیزیکی
    # ==========================================
    model += 4500 * total_wheat + 4000 * total_barley + 8500 * total_corn <= water_budget, "Water_Constraint"
    model += 250 * total_wheat + 150 * total_barley + 400 * total_corn <= fertilizer_budget, "Fertilizer_Constraint"
    model += total_planted <= land_budget, "Land_Constraint"

    # ==========================================
    # قیود پله‌ها (Piecewise Bounds) مرتبط با کل سطح زیر کشت
    # ==========================================
    model += w[0] <= 0.30 * total_planted, "W_Tier1_Limit"
    model += w[1] <= 0.20 * total_planted, "W_Tier2_Limit"
    model += w[2] <= 0.20 * total_planted, "W_Tier3_Limit"
    # پله 4 نیازی به محدودیت ندارد چون مازاد بر 70 درصد است

    model += b[0] <= 0.30 * total_planted, "B_Tier1_Limit"
    model += b[1] <= 0.20 * total_planted, "B_Tier2_Limit"
    model += b[2] <= 0.20 * total_planted, "B_Tier3_Limit"

    model += c[0] <= 0.30 * total_planted, "C_Tier1_Limit"
    model += c[1] <= 0.20 * total_planted, "C_Tier2_Limit"
    model += c[2] <= 0.20 * total_planted, "C_Tier3_Limit"

    # حل کردن ماتریس
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status_str = pulp.LpStatus[model.status]

    if status_str == 'Optimal':
        # محاسبه مساحتی که وارد پله‌های دوم به بعد شده‌اند (مشمول افت عملکرد)
        w_excess = sum(w[i].varValue for i in range(1, 4))
        b_excess = sum(b[i].varValue for i in range(1, 4))
        c_excess = sum(c[i].varValue for i in range(1, 4))

        results = {
            "status": "Optimal",
            "wheat_ha": round(pulp.value(total_wheat), 2),
            "barley_ha": round(pulp.value(total_barley), 2),
            "corn_ha": round(pulp.value(total_corn), 2),
            "wheat_excess": round(w_excess, 2),
            "barley_excess": round(b_excess, 2),
            "corn_excess": round(c_excess, 2),
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
