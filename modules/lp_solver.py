import pulp
from typing import Dict, Any

def solve_crop_allocation(water_budget: float, fertilizer_budget: float, land_budget: float) -> Dict[str, Any]:
    """
    حل‌کننده ریاضی مسئله برنامه‌ریزی خطی (LP) برای الگوی کشت بهینه (با مکانیزم جریمه انعطاف‌پذیر).
    """
    model = pulp.LpProblem("Smart_Agri_Crop_Allocation", pulp.LpMaximize)

    # متغیرهای اصلی (سطح زیر کشت)
    wheat = pulp.LpVariable('Wheat_Area_ha', lowBound=0, cat='Continuous')
    barley = pulp.LpVariable('Barley_Area_ha', lowBound=0, cat='Continuous')
    corn = pulp.LpVariable('Corn_Area_ha', lowBound=0, cat='Continuous')

    # متغیرهای مازاد برای محاسبه جریمه (Excess variables)
    wheat_excess = pulp.LpVariable('Wheat_Excess_ha', lowBound=0, cat='Continuous')
    barley_excess = pulp.LpVariable('Barley_Excess_ha', lowBound=0, cat='Continuous')
    corn_excess = pulp.LpVariable('Corn_Excess_ha', lowBound=0, cat='Continuous')

    total_planted = wheat + barley + corn

    # ==========================================
    # تابع هدف (سود منهای جریمه‌های تک‌کشتی)
    # سود پایه: گندم 50، جو 40، ذرت 90
    # جریمه مازاد: گندم -20، جو -15، ذرت -40
    # ==========================================
    model += (50 * wheat + 40 * barley + 90 * corn) - (20 * wheat_excess + 15 * barley_excess + 40 * corn_excess), "Total_Profit"

    # ==========================================
    # قیود منابع فیزیکی
    # ==========================================
    model += (4500 * wheat + 4000 * barley + 8500 * corn <= water_budget, "Water_Constraint")
    model += (250 * wheat + 150 * barley + 400 * corn <= fertilizer_budget, "Fertilizer_Constraint")
    model += (total_planted <= land_budget, "Land_Constraint")

    # ==========================================
    # قیود نرم (Soft Constraints) برای شناسایی مازاد
    # اگر محصولی بیش از 40 درصد کل کشت را اشغال کند، مقدار مازاد آن محاسبه شده و جریمه می‌شود
    # ==========================================
    model += wheat - 0.40 * total_planted <= wheat_excess, "Wheat_Penalty_Bound"
    model += barley - 0.40 * total_planted <= barley_excess, "Barley_Penalty_Bound"
    model += corn - 0.40 * total_planted <= corn_excess, "Corn_Penalty_Bound"

    # حل کردن ماتریس
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status_str = pulp.LpStatus[model.status]

    if status_str == 'Optimal':
        results = {
            "status": "Optimal",
            "wheat_ha": round(wheat.varValue, 2),
            "barley_ha": round(barley.varValue, 2),
            "corn_ha": round(corn.varValue, 2),
            "wheat_excess": round(wheat_excess.varValue, 2),
            "barley_excess": round(barley_excess.varValue, 2),
            "corn_excess": round(corn_excess.varValue, 2),
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
