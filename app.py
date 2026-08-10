import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی برای دسترسی به کلیدهای API
load_dotenv()

# وارد کردن ماژول‌های توسعه داده شده
from modules.lp_solver import solve_crop_allocation
from modules.ga_solver import solve_harvester_routing
from modules.llm_chatbot import get_ai_analysis

# ⚙️ تنظیمات پیکربندی صفحه (Page Config)
st.set_page_config(
    page_title="سیستم کشت و صنعت هوشمند | دانشگاه شریف",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 💅 استایل‌های سفارشی (CSS) برای رابط کاربری پیشرفته
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700;900&display=swap');

* {
    font-family: 'Vazirmatn', sans-serif !important;
}

/* راست‌چین کردن متون بدون تخریب ساختار فلکس‌باکس Streamlit */
h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stSelectbox label, .stSlider label, .stNumberInput label {
    direction: rtl;
    text-align: right;
}

/* 🎨 استایل و بزرگ‌نمایی تب‌ها (ماژول‌ها) و تغییر جهت به راست‌چین */
div[data-baseweb="tab-list"] {
    display: flex;
    flex-direction: row-reverse; /* قرارگیری ماژول ۱ در سمت راست */
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
/* مخفی کردن خط زیرین پیش‌فرض استریم‌لیت */
div[data-baseweb="tab-highlight"] {
    display: none !important;
}

/* راست‌چین کردن پیام‌های چت‌بات */
[data-testid="stChatMessage"] {
    direction: rtl;
    text-align: right;
}

/* استایل دهی به دکمه‌های اصلی */
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
    color: white;
}

/* ویجت اختصاصی برای متریک‌ها */
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

/* انیمیشن اشاره برای حالت خالی (Empty State) */
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

# توابع کمکی برای رسم کادرهای سفارشی در محیط رابط کاربری
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

# 💾 مدیریت حافظه موقت (Session State Initialization)
if "lp_results" not in st.session_state:
    st.session_state.lp_results = None
if "ga_results" not in st.session_state:
    st.session_state.ga_results = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# 🎨 هدر و عنوان اصلی داشبورد
st.title("🌾 سیستم هوشمند مدیریت مجتمع کشت و صنعت")
st.markdown("""
**پروژه پایانی درس برنامه‌نویسی پیشرفته - دانشگاه صنعتی شریف**  
این داشبورد با استفاده از معماری ۴ ماژوله، مدل‌های برنامه‌ریزی خطی (LP) برای الگوی کشت و الگوریتم ژنتیک (GA) برای زمان‌بندی ماشین‌آلات را با یک دستیار هوش مصنوعی یکپارچه کرده است.
""")
st.divider()

# ایجاد سه تب مجزا
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

    # ترفند طلایی برای RTL: ستون نتایج (چپ) را اول می‌نویسیم و ستون تنظیمات (راست) را دوم
    col_lp_results, col_lp_settings = st.columns([2.5, 1])

    with col_lp_settings:
        st.subheader("تنظیمات پارامترها")
        st.info("پارامترهای موجودی منابع را برای شبیه‌سازی تغییر دهید.")

        water_limit = st.slider("💧 حق‌آبه کل در دسترس (متر مکعب):", min_value=10000, max_value=300000, value=100000, step=5000)
        fert_limit = st.slider("🧪 موجودی انبار کود (کیلوگرم):", min_value=1000, max_value=50000, value=5000, step=500)

        if st.button("اجرای مدل بهینه‌سازی کشت 🚀", use_container_width=True):
            with st.spinner("در حال حل ماتریس‌های برنامه‌ریزی خطی..."):
                st.session_state.lp_results = solve_crop_allocation(water_budget=water_limit, fertilizer_budget=fert_limit)

    with col_lp_results:
        if st.session_state.lp_results:
            res = st.session_state.lp_results

            if res["status"] == "Optimal":
                st.success("✅ جواب بهینه سراسری (Global Optimal) یافت شد.")

                # نمایش متریک‌ها به صورت راست‌چین واقعی با HTML سفارشی
                m_water, m_fert, m_profit = st.columns(3)
                
                with m_profit:
                    # استفاده از فرمت‌بندی , برای جداکردن هزارگان اعداد سود
                    formatted_profit = f"{res['total_profit_million']:,.0f} <span style='font-size:1.2rem; font-weight:400;'>میلیون تومان</span>"
                    render_custom_metric("💰 سود خالص برآوردی", formatted_profit)
                
                with m_fert:
                    # رفع مشکل -0.0 با قدر مطلق و فرمت دو رقم اعشار
                    fert_val = abs(res['fertilizer_shadow_price'])
                    render_custom_metric("🧪 ارزش سایه‌ای کود", f"{fert_val:.2f}", "↑ ارزش ۱ واحد کود اضافه")
                
                with m_water:
                    water_val = abs(res['water_shadow_price'])
                    render_custom_metric("💧 ارزش سایه‌ای آب", f"{water_val:.2f}", "↑ ارزش ۱ واحد آب اضافه")

                st.subheader("📊 سهم اختصاص یافته به هر محصول")

                labels = ['گندم (Wheat)', 'جو (Barley)', 'ذرت (Corn)']
                sizes = [res['wheat_ha'], res['barley_ha'], res['corn_ha']]
                
                actual_labels = [l for i, l in enumerate(labels) if sizes[i] > 0]
                actual_sizes = [s for s in sizes if s > 0]

                if actual_sizes:
                    df_pie = pd.DataFrame({"محصول": actual_labels, "مساحت پیشنهادی (هکتار)": actual_sizes})
                    
                    # نمودار دایره ای مدرن با پلاتلی
                    fig = px.pie(
                        df_pie, 
                        values="مساحت پیشنهادی (هکتار)", 
                        names="محصول",
                        color="محصول",
                        color_discrete_map={
                            'گندم (Wheat)': '#f1c40f', 
                            'جو (Barley)': '#e67e22', 
                            'ذرت (Corn)': '#2ecc71'
                        },
                        hole=0.4
                    )
                    fig.update_layout(
                        margin=dict(t=20, b=20, l=20, r=20),
                        font=dict(family="Vazirmatn", size=14),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.warning("منابع وارد شده به قدری کم است که امکان کشت هیچ محصولی وجود ندارد!")
            else:
                st.error("❌ مدل جواب موجهی ندارد (Infeasible). لطفاً منابع را افزایش دهید.")
        else:
            render_empty_state("جهت مشاهده نتایج تخصیص زمین، لطفاً مقادیر را در منوی سمت راست تنظیم کرده و روی دکمه «اجرای مدل» کلیک کنید.")

# ==========================================
# 🔵 تب دوم: الگوریتم ژنتیک (Genetic Algorithm)
# ==========================================
with tab_ga:
    st.header("زمان‌بندی و مسیریابی ماشین‌آلات سنگین (کمباین)")

    # چیدمان ستون‌ها برای حالت راست‌چین
    col_ga_results, col_ga_settings = st.columns([2.5, 1])

    with col_ga_settings:
        st.subheader("تنظیمات ژنتیک")
        num_farms = st.number_input("تعداد مزارع (Nodes):", min_value=5, max_value=100, value=20)
        generations = st.number_input("تعداد نسل‌ها:", min_value=50, max_value=1000, value=200)
        pop_size = st.selectbox("اندازه جمعیت:", [50, 100, 150, 200], index=1)
        mutation_rate = st.slider("نرخ جهش (Mutation):", 0.01, 0.50, 0.15, step=0.01)

        if st.button("اجرای الگوریتم تکاملی 🧬", use_container_width=True):
            with st.spinner("در حال تکامل نسل‌ها و جستجوی فضای حالت..."):
                st.session_state.ga_results = solve_harvester_routing(
                    num_farms=num_farms,
                    generations=generations,
                    pop_size=pop_size,
                    mutation_rate=mutation_rate
                )

    with col_ga_results:
        if st.session_state.ga_results:
            res_ga = st.session_state.ga_results

            render_custom_metric(
                "🏆 کوتاه‌ترین مسافت کشف شده", 
                f"{res_ga['best_distance']} <span style='font-size:1.2rem; font-weight:400;'>کیلومتر</span>", 
                f"توقف در نسل: {res_ga['stopped_at_generation']}"
            )

            chart_tab1, chart_tab2 = st.tabs(["🗺️ نقشه مسیریابی کمباین", "📉 نمودار همگرایی الگوریتم"])

            with chart_tab1:
                coords = np.array(res_ga["coords"])
                path = res_ga["best_path"]
                path_closed = path + [path[0]]
                path_coords = coords[path_closed]

                fig_map = go.Figure()
                
                # رسم مزارع
                fig_map.add_trace(go.Scatter(
                    x=coords[:, 0], y=coords[:, 1], 
                    mode='markers+text',
                    text=[str(i) for i in range(len(coords))],
                    textposition="top center",
                    marker=dict(size=12, color='#e74c3c', line=dict(width=1, color='white')),
                    name='مزارع'
                ))
                
                # رسم مسیر
                fig_map.add_trace(go.Scatter(
                    x=path_coords[:, 0], y=path_coords[:, 1], 
                    mode='lines',
                    line=dict(width=2, color='#2980b9'),
                    name='مسیر حرکت'
                ))
                
                # گاراژ
                fig_map.add_trace(go.Scatter(
                    x=[coords[path[0], 0]], y=[coords[path[0], 1]], 
                    mode='markers',
                    marker=dict(size=20, color='#27ae60', symbol='star', line=dict(width=1, color='white')),
                    name='گاراژ مرکزی (مبدأ)'
                ))
                
                fig_map.update_layout(
                    title="شبکه بهینه مسیریابی ماشین‌آلات",
                    font=dict(family="Vazirmatn"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                )
                
                st.plotly_chart(fig_map, use_container_width=True)

                st.write("**ترتیب ویزیت مزارع:**")
                st.code(" ➔ ".join(map(str, path_closed)))

            with chart_tab2:
                st.write("این نمودار نشان می‌دهد الگوریتم در چه نسلی به جواب بهینه رسیده و متوقف شده است.")
                
                fig_hist = px.line(
                    x=list(range(len(res_ga["history"]))), 
                    y=res_ga["history"],
                    labels={'x': 'نسل‌ها (Generations)', 'y': 'مسافت کل (کیلومتر)'}
                )
                fig_hist.update_traces(line_color='#8e44ad', line_width=3)
                fig_hist.update_layout(
                    title="روند همگرایی الگوریتم ژنتیک",
                    font=dict(family="Vazirmatn"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)')
                )
                st.plotly_chart(fig_hist, use_container_width=True)
        else:
            render_empty_state("جهت مشاهده نقشه مسیریابی، لطفاً روی دکمه «اجرای الگوریتم تکاملی» در منوی سمت راست کلیک کنید.")

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

    وضعیت فعلی سیستم در داشبورد:
    """

    if st.session_state.lp_results and st.session_state.lp_results["status"] == "Optimal":
        lp = st.session_state.lp_results
        system_context += f"""
        [نتایج مدل برنامه‌ریزی خطی (LP)]:
        - سود کل پیش‌بینی شده: {lp['total_profit_million']} میلیون تومان
        - مساحت گندم: {lp['wheat_ha']} هکتار
        - مساحت جو: {lp['barley_ha']} هکتار
        - مساحت ذرت: {lp['corn_ha']} هکتار
        - ارزش سایه‌ای آب (سود هر 1 واحد آب اضافه): {lp['water_shadow_price']}
        - ارزش سایه‌ای کود (سود هر 1 واحد کود اضافه): {lp['fertilizer_shadow_price']}
        """
    else:
        system_context += "\n[نتایج LP]: هنوز مدلی اجرا نشده یا مدل موجه نبوده است."

    if st.session_state.ga_results:
        ga = st.session_state.ga_results
        system_context += f"""
        [نتایج مدل الگوریتم ژنتیک (GA) برای زمان‌بندی کمباین]:
        - بهترین مسافت کشف شده برای ویزیت مزارع: {ga['best_distance']} کیلومتر
        - الگوریتم در نسل {ga['stopped_at_generation']} متوقف شده است.
        """
    else:
        system_context += "\n[نتایج GA]: هنوز مدلی برای مسیریابی اجرا نشده است."

    # نمایش پیام‌های خوشامدگویی یا پیام‌های گذشته
    if len(st.session_state.chat_messages) == 0:
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": "سلام! من دستیار هوشمند شما هستم. نتایج مدل‌های بهینه‌سازی (LP و GA) را در حافظه دارم. چه کمکی از من ساخته است؟ \n*(مثال: تحلیل حساسیت آب رو بگو، یا چرا ذرت بیشتر از جو کشت شده؟)*"
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
