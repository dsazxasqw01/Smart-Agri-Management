import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import math
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# وارد کردن ماژول‌های توسعه داده شده
from modules.lp_solver import solve_crop_allocation
from modules.ga_solver import solve_harvester_routing
from modules.llm_chatbot import get_ai_analysis

st.set_page_config(
    page_title="سیستم کشت و صنعت هوشمند | دانشگاه شریف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 💅 استایل‌های سفارشی
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700;900&display=swap');

* {
    font-family: 'Vazirmatn', sans-serif !important;
}

h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stSelectbox label, .stSlider label, .stNumberInput label {
    direction: rtl;
    text-align: right;
}

div[data-baseweb="tab-list"] {
    display: flex;
    flex-direction: row-reverse;
    gap: 15px;
    margin-bottom: 25px;
    padding-bottom: 5px;
}
button[data-baseweb="tab"] {
    background-color: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    padding: 12px 30px !important;
    transition: all 0.3s ease !important;
}
button[data-baseweb="tab"]:hover {
    background-color: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.3) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4) !important;
}
button[data-baseweb="tab"] p {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
}
button[data-baseweb="tab"][aria-selected="true"] p {
    color: white !important;
}
div[data-baseweb="tab-highlight"] {
    display: none !important;
}
[data-testid="stChatMessage"] {
    direction: rtl;
    text-align: right;
}
.stButton>button {
    background: linear-gradient(135deg, #FF416C 0%, #FF4B2B 100%);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 24px;
    box-shadow: 0 4px 15px rgba(255, 75, 43, 0.3);
    font-weight: 700;
    transition: all 0.3s ease;
    width: 100%;
}
.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(255, 75, 43, 0.4);
}
.custom-metric-card {
    background-color: rgba(30, 30, 30, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    padding: 20px 15px;
    text-align: right;
    direction: rtl;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    transition: transform 0.2s;
    margin-bottom: 1rem;
}
.custom-metric-card:hover {
    transform: scale(1.02);
    background-color: rgba(40, 40, 40, 0.6);
}
.cm-title {
    color: #a0aec0;
    font-size: 1rem;
    margin-bottom: 8px;
    font-weight: 400;
}
.cm-value {
    color: #ffffff;
    font-size: 2.2rem;
    font-weight: 900;
    margin-bottom: 8px;
    line-height: 1.2;
}
.cm-delta {
    background-color: rgba(16, 185, 129, 0.15);
    color: #10b981;
    font-size: 0.9rem;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-block;
    font-weight: 500;
}
@keyframes pulse-right {
    0% { transform: translateX(0); }
    50% { transform: translateX(15px); }
    100% { transform: translateX(0); }
}
.empty-icon {
    display: inline-block;
    font-size: 55px;
    margin-bottom: 15px;
    animation: pulse-right 1.5s infinite;
}
</style>
""", unsafe_allow_html=True)

def render_custom_metric(title, value, delta=None):
    delta_html = f"<div class='cm-delta'>{delta}</div>" if delta else ""
    html = f"""
    <div class="custom-metric-card">
        <div class="cm-title">{title}</div>
        <div class="cm-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_empty_state(message):
    html = f"""
    <div style="background: rgba(255, 255, 255, 0.02); border: 2px dashed rgba(255, 255, 255, 0.15); 
                border-radius: 20px; padding: 60px 20px; text-align: center; direction: rtl; margin-top: 30px;
                box-shadow: inset 0 0 20px rgba(0,0,0,0.2);">
        <div class="empty-icon">👉</div>
        <div style="font-size: 1.3rem; color: #cbd5e1; font-weight: 500; line-height: 1.8;">{message}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

if "lp_results" not in st.session_state:
    st.session_state.lp_results = None
if "ga_results" not in st.session_state:
    st.session_state.ga_results = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

st.title("🌾 سیستم هوشمند مدیریت مجتمع کشت و صنعت")
st.markdown("""
**پروژه پایانی درس برنامه‌نویسی پیشرفته - دانشگاه صنعتی شریف**  
این داشبورد با استفاده از معماری ۴ ماژوله، مدل‌های برنامه‌ریزی خطی (LP) برای الگوی کشت و الگوریتم ژنتیک (GA) برای زمان‌بندی ماشین‌آلات را با یک دستیار هوش مصنوعی یکپارچه کرده است.
""")
st.divider()

tab_lp, tab_ga, tab_ai = st.tabs([
    "🧮 ماژول ۱: بهینه‌سازی الگوی کشت (LP)",
    "🚜 ماژول ۲: مسیریابی ماشین‌آلات (GA)",
    "🤖 ماژول ۳: دستیار تحلیلی هوشمند (LLM)"
])

# ==========================================
# 🟢 تب اول: برنامه‌ریزی خطی (Linear Programming)
# ==========================================
with tab_lp:
    st.header("تخصیص بهینه منابع آب و کود به مزارع")
    col_lp_results, col_lp_settings = st.columns([2.5, 1])

    with col_lp_settings:
        st.subheader("تنظیمات پارامترها")
        
        # اسلایدر زمین
        land_limit = st.slider("🏞️ مساحت کل زمین (هکتار):", min_value=50, max_value=500, value=100, step=10)
        
        # اسلایدر آب و تحلیل لحظه‌ای درجه‌بندی (Water Grading)
        water_limit = st.slider("💧 حق‌آبه کل (متر مکعب):", min_value=100000, max_value=4000000, value=700000, step=50000)
        water_per_ha = water_limit / land_limit
        if water_per_ha < 4000:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#ff4b4b; font-size:0.85em;'>🔴 وضعیت: بحران آبی (بخشی از زمین بایر می‌ماند)</span></div>", unsafe_allow_html=True)
        elif water_per_ha < 6000:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#feca57; font-size:0.85em;'>🟡 وضعیت: محدودیت آبی (تمایل مدل به جو/گندم)</span></div>", unsafe_allow_html=True)
        elif water_per_ha < 8000:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#1dd1a1; font-size:0.85em;'>🟢 وضعیت: متوازن (ترکیب بهینه ۳ محصول)</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#54a0ff; font-size:0.85em;'>🔵 وضعیت: مازاد آب (تمایل مدل به ذرت)</span></div>", unsafe_allow_html=True)

        # اسلایدر کود و تحلیل لحظه‌ای درجه‌بندی (Fertilizer Grading)
        fert_limit = st.slider("🧪 موجودی کود (کیلوگرم):", min_value=5000, max_value=200000, value=28000, step=2000)
        fert_per_ha = fert_limit / land_limit
        if fert_per_ha < 150:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#ff4b4b; font-size:0.85em;'>🔴 وضعیت: بحران کودی (بخشی از زمین بایر می‌ماند)</span></div>", unsafe_allow_html=True)
        elif fert_per_ha < 220:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#feca57; font-size:0.85em;'>🟡 وضعیت: محدودیت کودی (تمایل مدل به جو)</span></div>", unsafe_allow_html=True)
        elif fert_per_ha < 320:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#1dd1a1; font-size:0.85em;'>🟢 وضعیت: متوازن (ترکیب بهینه ۳ محصول)</span></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='margin-top:-15px; margin-bottom:15px;'><span style='color:#54a0ff; font-size:0.85em;'>🔵 وضعیت: مازاد کود (بدون محدودیت کودی)</span></div>", unsafe_allow_html=True)

        if st.button("اجرای مدل بهینه‌سازی کشت 🚀", use_container_width=True):
            with st.spinner("در حال حل ماتریس‌های برنامه‌ریزی خطی..."):
                st.session_state.lp_results = solve_crop_allocation(water_budget=water_limit, fertilizer_budget=fert_limit, land_budget=land_limit)

    with col_lp_results:
        if st.session_state.lp_results:
            res = st.session_state.lp_results
            if res["status"] == "Optimal":
                st.success("✅ جواب بهینه یافت شد (محاسبه شده با الگوریتم تقریب خطی پویا جهت تنوع زراعی).")
                
                m1, m2 = st.columns(2)
                m3, m4 = st.columns(2)
                
                with m1:
                    formatted_profit = f"{res['total_profit_million']:,.0f} <span style='font-size:1rem; font-weight:400;'>م.تومان</span>"
                    render_custom_metric("💰 سود خالص برآوردی", formatted_profit)
                with m2:
                    render_custom_metric("🏞️ ارزش سایه‌ای زمین", f"{abs(res['land_shadow_price']):.2f}", "سود ۱ هکتار زمین اضافه")
                with m3:
                    render_custom_metric("🧪 ارزش سایه‌ای کود", f"{abs(res['fertilizer_shadow_price']):.2f}", "سود ۱ واحد کود اضافه")
                with m4:
                    render_custom_metric("💧 ارزش سایه‌ای آب", f"{abs(res['water_shadow_price']):.2f}", "سود ۱ واحد آب اضافه")

                st.subheader("📊 سهم اختصاص یافته به هر محصول")
                labels = ['گندم (Wheat)', 'جو (Barley)', 'ذرت (Corn)']
                sizes = [res['wheat_ha'], res['barley_ha'], res['corn_ha']]
                
                actual_labels = [l for i, l in enumerate(labels) if sizes[i] > 0]
                actual_sizes = [s for s in sizes if s > 0]

                if actual_sizes:
                    df_pie = pd.DataFrame({"محصول": actual_labels, "مساحت پیشنهادی (هکتار)": actual_sizes})
                    fig = px.pie(
                        df_pie, values="مساحت پیشنهادی (هکتار)", names="محصول", color="محصول",
                        color_discrete_map={'گندم (Wheat)': '#f1c40f', 'جو (Barley)': '#e67e22', 'ذرت (Corn)': '#2ecc71'},
                        hole=0.4
                    )
                    fig.update_layout(
                        margin=dict(t=20, b=20, l=20, r=20), font=dict(family="Vazirmatn", size=14),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("منابع وارد شده به قدری کم است که امکان کشت هیچ محصولی وجود ندارد!")
            else:
                st.error("❌ مدل جواب موجهی ندارد (Infeasible). لطفاً منابع را افزایش دهید.")
        else:
            render_empty_state("جهت مشاهده نتایج تخصیص زمین، لطفاً مقادیر را تنظیم کرده و روی دکمه «اجرای مدل» کلیک کنید.")

# ==========================================
# 🔵 تب دوم: الگوریتم ژنتیک (Genetic Algorithm)
# ==========================================
with tab_ga:
    st.header("زمان‌بندی و مسیریابی ناوگان ماشین‌آلات (mTSP)")
    col_ga_results, col_ga_settings = st.columns([2.5, 1])

    with col_ga_settings:
        st.subheader("تنظیمات ژنتیک")
        num_farms = st.number_input("تعداد مزارع (Nodes):", min_value=5, max_value=100, value=20)
        num_vehicles = st.slider("🚜 تعداد کمباین‌ها (ناوگان):", min_value=1, max_value=10, value=3)
        generations = st.number_input("تعداد نسل‌ها:", min_value=50, max_value=1000, value=200)
        pop_size = st.selectbox("اندازه جمعیت:", [50, 100, 150, 200], index=1)
        mutation_rate = st.slider("نرخ جهش:", 0.01, 0.50, 0.15, step=0.01)

        if st.button("اجرای الگوریتم تکاملی 🧬", use_container_width=True):
            with st.spinner("در حال تکامل نسل‌ها برای اعزام ناوگان..."):
                st.session_state.ga_results = solve_harvester_routing(
                    num_farms=num_farms, num_vehicles=num_vehicles, generations=generations,
                    pop_size=pop_size, mutation_rate=mutation_rate
                )

    with col_ga_results:
        if st.session_state.ga_results:
            res_ga = st.session_state.ga_results

            render_custom_metric(
                "⏳ کوتاه‌ترین زمان‌بندی کل (Makespan)", 
                f"{res_ga['best_distance']} <span style='font-size:1.2rem; font-weight:400;'>واحد</span>", 
                f"بهینه شده در نسل: {res_ga['stopped_at_generation']}"
            )

            chart_tab1, chart_tab2 = st.tabs(["🗺️ نقشه مسیریابی ناوگان", "📉 نمودار همگرایی الگوریتم"])

            with chart_tab1:
                coords = np.array(res_ga["coords"])
                path = res_ga["best_path"]
                n_vehicles = res_ga["num_vehicles"]
                
                # تقسیم مسیرها بین کمباین‌ها
                chunk_size = math.ceil(len(path) / n_vehicles)
                routes = [path[i:i + chunk_size] for i in range(0, len(path), chunk_size)]

                fig_map = go.Figure()
                
                # رسم مزارع
                fig_map.add_trace(go.Scatter(
                    x=coords[1:, 0], y=coords[1:, 1], mode='markers+text',
                    text=[str(i) for i in range(1, len(coords))], textposition="top center",
                    marker=dict(size=12, color='#e74c3c', line=dict(width=1, color='white')), name='مزارع'
                ))
                
                # رسم گاراژ
                fig_map.add_trace(go.Scatter(
                    x=[coords[0, 0]], y=[coords[0, 1]], mode='markers',
                    marker=dict(size=22, color='#27ae60', symbol='star', line=dict(width=2, color='white')), name='گاراژ مرکزی'
                ))
                
                # رسم مسیر هر کمباین با رنگ مجزا
                colors = ['#2980b9', '#8e44ad', '#f39c12', '#16a085', '#c0392b', '#d35400', '#34495e']
                for idx, route in enumerate(routes):
                    if not route: continue
                    full_route = [0] + route + [0] # رفت از گاراژ و برگشت به گاراژ
                    route_coords = coords[full_route]
                    
                    fig_map.add_trace(go.Scatter(
                        x=route_coords[:, 0], y=route_coords[:, 1], mode='lines',
                        line=dict(width=3, color=colors[idx % len(colors)]), name=f'کمباین {idx+1}'
                    ))
                
                fig_map.update_layout(
                    title="شبکه بهینه اعزام ناوگان کمباین‌ها (mTSP)", font=dict(family="Vazirmatn"),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig_map, use_container_width=True)

            with chart_tab2:
                fig_hist = px.line(
                    x=list(range(len(res_ga["history"]))), y=res_ga["history"],
                    labels={'x': 'نسل‌ها (Generations)', 'y': 'زمان/مسافت ماکزیمم'}
                )
                fig_hist.update_traces(line_color='#8e44ad', line_width=3)
                fig_hist.update_layout(
                    title="روند همگرایی الگوریتم ژنتیک ناوگان", font=dict(family="Vazirmatn"),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig_hist, use_container_width=True)
        else:
            render_empty_state("جهت مشاهده نقشه اعزام ناوگان، لطفاً روی دکمه «اجرای الگوریتم تکاملی» کلیک کنید.")

# ==========================================
# 🤖 تب سوم: دستیار هوشمند (LLM / Dynamic RAG)
# ==========================================
with tab_ai:
    st.header("💬 دستیار مدیریتی هوشمند (مبتنی بر Gemini)")
    st.markdown("من نتایج تخصیص زمین و مسیریابی را خوانده‌ام. سوالات مدیریتی یا تحلیل حساسیت خود را بپرسید!")

    system_context = """
    شما یک مهندس صنایع و مشاور ارشد تصمیم‌گیری در یک 'مجتمع کشت و صنعت هوشمند' هستید.
    وظیفه شما پاسخگویی دقیق، علمی و مدیریتی به زبان فارسی به مدیر عامل مجتمع است.
    قوانین:
    - فقط بر اساس داده‌های زیر تحلیل کن و عددسازی نکن.
    - اگر داده‌ها صفر است، بگو منابع برای کشت کافی نبوده است.
    - از مفاهیم 'ارزش سایه‌ای' برای ارائه پیشنهاد خرید منابع بیشتر استفاده کن.
    """

    if st.session_state.lp_results and st.session_state.lp_results["status"] == "Optimal":
        lp = st.session_state.lp_results
        system_context += f"""
        [نتایج مدل برنامه‌ریزی خطی (LP)]:
        - سود کل پیش‌بینی شده: {lp['total_profit_million']} میلیون تومان
        - مساحت کل گندم: {lp['wheat_ha']} هکتار (مساحت مشمول افت عملکرد تدریجی: {lp['wheat_excess']} هکتار)
        - مساحت کل جو: {lp['barley_ha']} هکتار (مساحت مشمول افت عملکرد تدریجی: {lp['barley_excess']} هکتار)
        - مساحت کل ذرت: {lp['corn_ha']} هکتار (مساحت مشمول افت عملکرد تدریجی: {lp['corn_excess']} هکتار)
        - ارزش سایه‌ای زمین: {lp['land_shadow_price']}
        - ارزش سایه‌ای آب: {lp['water_shadow_price']}
        - ارزش سایه‌ای کود: {lp['fertilizer_shadow_price']}
        """
    
    if st.session_state.ga_results:
        ga = st.session_state.ga_results
        system_context += f"""
        [نتایج مدل الگوریتم ژنتیک (GA) برای ناوگان]:
        - تعداد کمباین‌های اعزام شده: {ga['num_vehicles']}
        - بهترین زمان‌بندی کل (Makespan): {ga['best_distance']} واحد
        """

    if len(st.session_state.chat_messages) == 0:
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": "سلام! من دستیار هوشمند شما هستم. نتایج مدل‌های بهینه‌سازی (LP و GA ناوگان) را در حافظه دارم. چه کمکی از من ساخته است؟"
        })

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_prompt := st.chat_input("سوال خود را اینجا تایپ کنید..."):
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("در حال تحلیل داده‌های بهینه‌سازی..."):
                ai_response = get_ai_analysis(user_prompt, system_context)
                st.markdown(ai_response)

        st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
