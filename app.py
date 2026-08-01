import streamlit as st
import matplotlib.pyplot as plt
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

    col_lp_settings, col_lp_results = st.columns([1, 2])

    with col_lp_settings:
        st.subheader("تنظیمات پارامترها")
        st.info("پارامترهای موجودی منابع را برای شبیه‌سازی تغییر دهید.")

        water_limit = st.slider("💧 حق‌آبه کل در دسترس (متر مکعب):", min_value=10000, max_value=300000, value=100000, step=5000)
        fert_limit = st.slider("🧪 موجودی انبار کود (کیلوگرم):", min_value=1000, max_value=50000, value=5000, step=500)

        if st.button("اجرای مدل بهینه‌سازی کشت 🚀", use_container_width=True, type="primary"):
            with st.spinner("در حال حل ماتریس‌های برنامه‌ریزی خطی..."):
                st.session_state.lp_results = solve_crop_allocation(water_budget=water_limit, fertilizer_budget=fert_limit)

    with col_lp_results:
        if st.session_state.lp_results:
            res = st.session_state.lp_results

            if res["status"] == "Optimal":
                st.success("✅ جواب بهینه سراسری (Global Optimal) یافت شد.")

                m1, m2, m3 = st.columns(3)
                m1.metric(label="💰 سود خالص برآوردی", value=f"{res['total_profit_million']} میلیون تومان")
                m2.metric(label="💧 ارزش سایه‌ای آب", value=f"{res['water_shadow_price']}", delta="ارزش 1 واحد آب اضافه")
                m3.metric(label="🧪 ارزش سایه‌ای کود", value=f"{res['fertilizer_shadow_price']}", delta="ارزش 1 واحد کود اضافه")

                st.subheader("📊 سهم اختصاص یافته به هر محصول")

                labels = ['گندم (Wheat)', 'جو (Barley)', 'ذرت (Corn)']
                sizes = [res['wheat_ha'], res['barley_ha'], res['corn_ha']]
                colors = ['#f1c40f', '#e67e22', '#2ecc71']

                actual_labels = [l for i, l in enumerate(labels) if sizes[i] > 0]
                actual_sizes = [s for s in sizes if s > 0]
                actual_colors = [c for i, c in enumerate(colors) if sizes[i] > 0]

                if actual_sizes:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.pie(actual_sizes, labels=actual_labels, colors=actual_colors, autopct='%1.1f%%',
                           startangle=140, explode=[0.05]*len(actual_sizes), shadow=True)
                    ax.axis('equal')
                    st.pyplot(fig)

                    df = pd.DataFrame({"محصول": actual_labels, "مساحت پیشنهادی (هکتار)": actual_sizes})
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("منابع وارد شده به قدری کم است که امکان کشت هیچ محصولی وجود ندارد!")
            else:
                st.error("❌ مدل جواب موجهی ندارد (Infeasible). لطفاً منابع را افزایش دهید.")
        else:
            st.caption("برای مشاهده نتایج، لطفاً دکمه اجرای مدل را از منوی سمت راست فشار دهید.")

# ==========================================
# 🔵 تب دوم: الگوریتم ژنتیک (Genetic Algorithm)
# ==========================================
with tab_ga:
    st.header("زمان‌بندی و مسیریابی ماشین‌آلات سنگین (کمباین)")

    col_ga_settings, col_ga_results = st.columns([1, 2])

    with col_ga_settings:
        st.subheader("تنظیمات ژنتیک (Hyperparameters)")
        num_farms = st.number_input("تعداد مزارع (Nodes):", min_value=5, max_value=100, value=20)
        generations = st.number_input("تعداد نسل‌ها (Generations):", min_value=50, max_value=1000, value=200)
        pop_size = st.selectbox("اندازه جمعیت (Population Size):", [50, 100, 150, 200], index=1)
        mutation_rate = st.slider("نرخ جهش (Mutation Rate):", 0.01, 0.50, 0.15, step=0.01)

        if st.button("اجرای الگوریتم تکاملی 🧬", use_container_width=True, type="primary"):
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

            st.success(f"✅ جستجو پایان یافت. توقف در نسل: {res_ga['stopped_at_generation']}")
            st.metric("کوتاه‌ترین مسافت یافت شده", f"{res_ga['best_distance']} کیلومتر")

            chart_tab1, chart_tab2 = st.tabs(["🗺️ نقشه مسیریابی کمباین", "📉 نمودار همگرایی الگوریتم"])

            with chart_tab1:
                coords = np.array(res_ga["coords"])
                path = res_ga["best_path"]
                path_closed = path + [path[0]]
                path_coords = coords[path_closed]

                fig_map, ax_map = plt.subplots(figsize=(8, 5))
                ax_map.plot(path_coords[:, 0], path_coords[:, 1], color='#2980b9', linestyle='-', linewidth=2, zorder=1)
                ax_map.scatter(coords[:, 0], coords[:, 1], color='#e74c3c', s=100, zorder=2, label='مزارع')
                ax_map.scatter(coords[path[0], 0], coords[path[0], 1], color='#27ae60', s=200, marker='*', zorder=3, label='گاراژ مرکزی (مبدأ)')

                for i, (x, y) in enumerate(coords):
                    ax_map.annotate(str(i), (x+1, y+1), fontsize=9)

                ax_map.set_title("Optimal Harvester Route Network", pad=15)
                ax_map.grid(True, linestyle='--', alpha=0.6)
                ax_map.legend()
                st.pyplot(fig_map)

                st.write("**ترتیب ویزیت مزارع:**")
                st.code(" ➔ ".join(map(str, path_closed)))

            with chart_tab2:
                st.write("این نمودار نشان می‌دهد الگوریتم در چه نسلی به جواب بهینه رسیده و متوقف شده است.")
                fig_hist, ax_hist = plt.subplots(figsize=(8, 4))
                ax_hist.plot(res_ga["history"], color='#8e44ad', linewidth=2)
                ax_hist.set_xlabel("نسل‌ها (Generations)")
                ax_hist.set_ylabel("مسافت کل (Distance)")
                ax_hist.set_title("Genetic Algorithm Convergence History")
                ax_hist.grid(True, linestyle='--', alpha=0.6)
                st.pyplot(fig_hist)
        else:
            st.caption("برای مشاهده نقشه مسیریابی، الگوریتم ژنتیک را اجرا کنید.")

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