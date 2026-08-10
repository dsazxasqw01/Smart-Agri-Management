import pulp
from typing import Dict, Any

def solve_crop_allocation(water_budget: float, fertilizer_budget: float, land_budget: float) -> Dict[str, Any]:
    """
    حل‌کننده ریاضی مسئله برنامه‌ریزی خطی (LP) برای الگوی کشت بهینه.
    """
    model = pulp.LpProblem("Smart_Agri_Crop_Allocation", pulp.LpMaximize)

    wheat = pulp.LpVariable('Wheat_Area_ha', lowBound=0, cat='Continuous')
    barley = pulp.LpVariable('Barley_Area_ha', lowBound=0, cat='Continuous')
    corn = pulp.LpVariable('Corn_Area_ha', lowBound=0, cat='Continuous')

    # ==========================================
    # تابع هدف (سود به میلیون تومان در هکتار)
    # طراحی مهندسی شده ضرایب:
    # گندم: بهترین بهره‌وری آب | جو: بهترین بهره‌وری کود | ذرت: سودآورترین در واحد زمین
    # ==========================================
    model += 50 * wheat + 40 * barley + 90 * corn, "Total_Profit"

    # ==========================================
    # قیود منابع (ظرفیت‌ها و موجودی)
    # ==========================================
    model += (4500 * wheat + 4000 * barley + 8500 * corn <= water_budget, "Water_Constraint")
    model += (250 * wheat + 150 * barley + 400 * corn <= fertilizer_budget, "Fertilizer_Constraint")
    model += (wheat + barley + corn <= land_budget, "Land_Constraint")

    # ==========================================
    # قیود تناوب زراعی و مدیریت ریسک (Crop Rotation)
    # هیچ محصولی نباید بیش از ۵۰٪ از کل مساحت تخصیص‌یافته را اشغال کند.
    # Wheat <= 0.50 * (Wheat + Barley + Corn) => 0.50*Wheat - 0.50*Barley - 0.50*Corn <= 0
    # ==========================================
    model += (0.50 * wheat - 0.50 * barley - 0.50 * corn <= 0, "Rotation_Wheat")
    model += (-0.50 * wheat + 0.50 * barley - 0.50 * corn <= 0, "Rotation_Barley")
    model += (-0.50 * wheat - 0.50 * barley + 0.50 * corn <= 0, "Rotation_Corn")

    # حل کردن ماتریس
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status_str = pulp.LpStatus[model.status]

    if status_str == 'Optimal':
        results = {
            "status": "Optimal",
            "wheat_ha": round(wheat.varValue, 2),
            "barley_ha": round(barley.varValue, 2),
            "corn_ha": round(corn.varValue, 2),
            "total_profit_million": round(pulp.value(model.objective), 2),
            "water_shadow_price": round(model.constraints["Water_Constraint"].pi, 4) if model.constraints["Water_Constraint"].pi else 0.0,
            "fertilizer_shadow_price": round(model.constraints["Fertilizer_Constraint"].pi, 4) if model.constraints["Fertilizer_Constraint"].pi else 0.0,
            "land_shadow_price": round(model.constraints["Land_Constraint"].pi, 4) if model.constraints["Land_Constraint"].pi else 0.0
        }
    else:
        results = {
            "status": status_str,
            "wheat_ha": 0, "barley_ha": 0, "corn_ha": 0,
            "total_profit_million": 0,
            "water_shadow_price": 0.0, "fertilizer_shadow_price": 0.0, "land_shadow_price": 0.0
        }

    return results
