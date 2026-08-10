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

    # تابع هدف: طراحی مهندسی شده برای ایجاد مزیت رقابتی مجزا
    # گندم: بهترین بهره‌وری آب
    # جو: بهترین بهره‌وری کود
    # ذرت: سودآورترین در واحد زمین (اما پرمصرف)
    model += 50 * wheat + 40 * barley + 90 * corn, "Total_Profit"

    # قیود منابع (ظرفیت‌ها)
    model += (3000 * wheat + 4000 * barley + 6500 * corn <= water_budget, "Water_Constraint")
    model += (250 * wheat + 150 * barley + 400 * corn <= fertilizer_budget, "Fertilizer_Constraint")
    model += (wheat + barley + corn <= land_budget, "Land_Constraint")

    # ==========================================
    # قیود تناوب زراعی و مدیریت ریسک (Crop Rotation)
    # برای جلوگیری از تک‌کشتی، هیچ محصولی نباید بیش از ۴۵٪ از کل مساحت کاشته شده را اشغال کند.
    # فرمول: Crop <= 0.45 * (Wheat + Barley + Corn)
    # که به شکل استاندارد زیر ساده می‌شود:
    # ==========================================
    model += (0.55 * wheat - 0.45 * barley - 0.45 * corn <= 0, "Rotation_Wheat")
    model += (-0.45 * wheat + 0.55 * barley - 0.45 * corn <= 0, "Rotation_Barley")
    model += (-0.45 * wheat - 0.45 * barley + 0.55 * corn <= 0, "Rotation_Corn")

    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status_str = pulp.LpStatus[model.status]

    if status_str == 'Optimal':
        results = {
            "status": "Optimal",
            "wheat_ha": round(wheat.varValue, 2),
            "barley_ha": round(barley.varValue, 2),
            "corn_ha": round(corn.varValue, 2),
            "total_profit_million": round(pulp.value(model.objective), 2),
            "water_shadow_price": round(model.constraints["Water_Constraint"].pi, 4),
            "fertilizer_shadow_price": round(model.constraints["Fertilizer_Constraint"].pi, 4),
            "land_shadow_price": round(model.constraints["Land_Constraint"].pi, 4)
        }
    else:
        results = {
            "status": status_str,
            "wheat_ha": 0, "barley_ha": 0, "corn_ha": 0,
            "total_profit_million": 0,
            "water_shadow_price": 0, "fertilizer_shadow_price": 0, "land_shadow_price": 0
        }

    return results
