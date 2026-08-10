import pulp
from typing import Dict, Any

def solve_crop_allocation(
    water_budget: float, 
    fertilizer_budget: float, 
    land_budget: float, 
    num_tiers: int = 10, 
    max_penalty: float = 0.5, 
    penalty_power: float = 2.0
) -> Dict[str, Any]:
    """
    حل‌کننده برنامه‌ریزی خطی با ایجاد پویای تقریب خطی تکه‌ای (Dynamic Piecewise Linear).
    بدون هیچ عدد ثابتی، افت عملکرد خاک به صورت یک تابع نرم (پیش‌فرض: درجه 2) محاسبه می‌شود.
    """
    model = pulp.LpProblem("Smart_Agri_Crop_Allocation", pulp.LpMaximize)

    # داده‌های پایه محصولات
    crops = {
        "wheat": {"profit": 50, "water": 4500, "fert": 250},
        "barley": {"profit": 40, "water": 4000, "fert": 150},
        "corn": {"profit": 90, "water": 8500, "fert": 400}
    }

    # محاسبه ظرفیت هر پله بر اساس زمین کل (جلوگیری از باگ فریب الگوریتم)
    tier_capacity = land_budget / num_tiers
    
    # دیکشنری برای نگهداری متغیرهای هر پله از هر محصول
    tier_vars = {c: [] for c in crops}
    
    # ==========================================
    # ایجاد متغیرها به صورت کاملاً پویا و الگوریتمیک
    # ==========================================
    for c in crops:
        for i in range(num_tiers):
            # هر پله دارای حد بالا معادل tier_capacity است
            var = pulp.LpVariable(f'{c}_Tier_{i}', lowBound=0, upBound=tier_capacity, cat='Continuous')
            tier_vars[c].append(var)

    # ==========================================
    # ساخت تابع هدف با شیب سود کاهنده (Diminishing Returns)
    # ==========================================
    total_profit = 0
    for c, data in crops.items():
        base_profit = data["profit"]
        for i in range(num_tiers):
            # تابع افت عملکرد: در پله صفر افت 0 است، در پله آخر افت برابر max_penalty است.
            # استفاده از توان 2 (penalty_power) باعث می‌شود نمودار جریمه در ابتدا نرم و در انتها تند باشد.
            loss_factor = max_penalty * ((i / (num_tiers - 1)) ** penalty_power)
            tier_profit = base_profit * (1.0 - loss_factor)
            total_profit += tier_profit * tier_vars[c][i]
            
    model += total_profit, "Total_Profit"

    # ==========================================
    # قیود منابع (با تجمیع جبری تمامی پله‌ها)
    # ==========================================
    model += pulp.lpSum(crops[c]["water"] * tier_vars[c][i] for c in crops for i in range(num_tiers)) <= water_budget, "Water_Constraint"
    model += pulp.lpSum(crops[c]["fert"] * tier_vars[c][i] for c in crops for i in range(num_tiers)) <= fertilizer_budget, "Fertilizer_Constraint"
    model += pulp.lpSum(tier_vars[c][i] for c in crops for i in range(num_tiers)) <= land_budget, "Land_Constraint"

    # اجرای حل‌کننده
    model.solve(pulp.PULP_CBC_CMD(msg=False))
    status_str = pulp.LpStatus[model.status]

    if status_str == 'Optimal':
        # تجمیع مساحت کل هر محصول از روی پله‌های آن
        areas = {c: sum(tier_vars[c][i].varValue for i in range(num_tiers)) for c in crops}
        
        # محاسبه مساحتی که وارد فاز افت عملکرد شده است (پله‌های ۱ به بعد)
        excesses = {c: sum(tier_vars[c][i].varValue for i in range(1, num_tiers)) for c in crops}

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
