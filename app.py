import streamlit as st
import pandas as pd
from datetime import date, timedelta
from streamlit_calendar import calendar
import os
import fitz
import re
import hashlib

# =========================================================
# CONFIG (MUST BE FIRST)
# =========================================================
st.set_page_config(page_title="Health Tracker", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');

/* ── GLOBAL RESET ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── PAGE BACKGROUND ── */
.stApp {
    background: linear-gradient(135deg, #fff0f5 0%, #fce4ec 40%, #f8f0ff 100%);
    min-height: 100vh;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fff0f5 0%, #fce4ec 100%) !important;
    border-right: 1px solid #f8bbd0;
}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    color: #5c2d4a !important;
}

/* ── MAIN CONTENT PADDING ── */
.main .block-container {
    padding: 1.5rem 2.5rem 3rem 2.5rem;
    max-width: 860px;
}

/* ── WELCOME BANNER ── */
.welcome-banner {
    background: linear-gradient(135deg, #f8bbd0, #e1bee7);
    border-radius: 20px;
    padding: 18px 24px;
    text-align: center;
    font-size: 16px;
    color: #4a1942;
    margin-bottom: 24px;
    box-shadow: 0 4px 20px rgba(233,30,99,0.12);
}

/* ── HEADER ── */
.app-title {
    font-family: 'Playfair Display', serif;
    font-size: 3rem;
    font-weight: 700;
    color: #c2185b;
    line-height: 1.1;
    margin: 0 0 4px 0;
}
.app-caption {
    color: #ad6c87;
    font-size: 14px;
    font-weight: 400;
    margin-bottom: 28px;
    letter-spacing: 0.5px;
}

/* ── SECTION HEADERS ── */
.section-header {
    font-family: 'DM Sans', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: #3d1a2e;
    margin: 32px 0 16px 0;
}

/* ── SUMMARY CARD ── */
.summary-card {
    background: white;
    border-radius: 20px;
    padding: 22px 26px;
    border: 1px solid #f8bbd0;
    box-shadow: 0 4px 24px rgba(233,30,99,0.08);
    font-size: 15px;
    line-height: 2.1;
    color: #3d1a2e;
    margin-bottom: 8px;
}
.summary-card b { color: #c2185b; }

/* ── ACTIVITY CARDS (2-col grid) ── */
.activity-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-bottom: 24px;
}
.activity-card {
    background: white;
    border-radius: 18px;
    padding: 18px 20px;
    box-shadow: 0 2px 16px rgba(233,30,99,0.07);
    border: 1px solid #fce4ec;
}
.activity-card .time {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 4px;
}
.activity-card .label {
    font-size: 13px;
    color: #888;
    font-weight: 400;
}
.time-pink   { color: #e91e63; }
.time-orange { color: #ff9800; }
.time-purple { color: #7c4dff; }
.time-rose   { color: #e91e63; }

/* ── SUGGESTION CARDS ── */
.suggestions-row {
    display: flex;
    gap: 12px;
    margin-top: 8px;
}
.suggestion-card {
    flex: 1;
    background: white;
    border-radius: 18px;
    padding: 20px 14px;
    text-align: center;
    box-shadow: 0 2px 16px rgba(233,30,99,0.07);
    border: 1px solid #fce4ec;
}
.suggestion-card .icon {
    font-size: 2rem;
    margin-bottom: 10px;
}
.suggestion-card .title {
    font-weight: 700;
    font-size: 14px;
    color: #3d1a2e;
    margin-bottom: 6px;
}
.suggestion-card .desc {
    font-size: 12px;
    color: #888;
    line-height: 1.4;
}

/* ── NAV BAR ── */
.nav-container {
    background: white;
    border-radius: 50px;
    padding: 6px 8px;
    display: flex;
    gap: 4px;
    box-shadow: 0 4px 20px rgba(233,30,99,0.10);
    border: 1px solid #f8bbd0;
    margin-bottom: 32px;
}
div[data-testid="stHorizontalBlock"] {
    background: white;
    border-radius: 50px !important;
    padding: 6px 10px !important;
    box-shadow: 0 4px 20px rgba(233,30,99,0.10) !important;
    border: 1px solid #f8bbd0 !important;
    gap: 4px !important;
    margin-bottom: 28px !important;
}
div[data-testid="stHorizontalBlock"] button {
    background: transparent !important;
    color: #ad6c87 !important;
    border: none !important;
    border-radius: 40px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    width: 100% !important;
    padding: 10px 0 !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    background: #fce4ec !important;
    color: #c2185b !important;
}
div[data-testid="stHorizontalBlock"] button:focus,
div[data-testid="stHorizontalBlock"] button:active {
    background: linear-gradient(135deg, #f48fb1, #ce93d8) !important;
    color: white !important;
}

/* ── ALL OTHER BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #f48fb1, #ce93d8) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.55em 1.6em !important;
    box-shadow: 0 4px 14px rgba(233,30,99,0.22) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #e91e63, #9c27b0) !important;
    box-shadow: 0 6px 20px rgba(233,30,99,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── SLEEP CIRCLE ── */
.sleep-circle {
    text-align: center;
    background: linear-gradient(135deg, #fce4ec, #f3e5f5);
    padding: 28px;
    border-radius: 50%;
    width: 140px;
    height: 140px;
    margin: 12px auto 20px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 700;
    border: 3px solid #f8bbd0;
    color: #c2185b;
    box-shadow: 0 8px 24px rgba(233,30,99,0.15);
}

/* ── INPUTS & SLIDERS ── */
.stSlider [data-baseweb="slider"] {
    padding: 0 4px;
}
.stNumberInput input, .stTextInput input {
    border-radius: 12px !important;
    border-color: #f8bbd0 !important;
    background: white !important;
}
.stNumberInput input:focus, .stTextInput input:focus {
    border-color: #e91e63 !important;
    box-shadow: 0 0 0 2px rgba(233,30,99,0.15) !important;
}

/* ── RADIO BUTTONS ── */
.stRadio > div {
    gap: 12px !important;
}
.stRadio label {
    background: white;
    border: 1.5px solid #f8bbd0;
    border-radius: 50px;
    padding: 6px 18px;
    font-weight: 500;
    color: #5c2d4a;
    cursor: pointer;
    transition: all 0.2s;
}
.stRadio label:hover {
    border-color: #e91e63;
    background: #fce4ec;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: white;
    border-radius: 16px;
    padding: 16px 20px;
    border: 1px solid #f8bbd0;
    box-shadow: 0 2px 12px rgba(233,30,99,0.07);
}
[data-testid="stMetricLabel"] { color: #ad6c87 !important; font-size: 13px !important; }
[data-testid="stMetricValue"] { color: #c2185b !important; font-weight: 700 !important; }

/* ── ALERTS ── */
.stSuccess, .stInfo, .stWarning {
    border-radius: 14px !important;
    border: none !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: white !important;
    border-radius: 14px !important;
    border: 1px solid #f8bbd0 !important;
}

/* ── DIVIDER ── */
hr { border-color: #f8bbd0 !important; }

/* ── SIDEBAR PROFILE NAME ── */
.profile-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #c2185b;
    margin: 4px 0 12px 0;
}

/* ── LINE CHART ── */
[data-testid="stVegaLiteChart"] {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(233,30,99,0.07);
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def hash_password(p):
    return hashlib.sha256(p.encode()).hexdigest()

def extract_value(text, keyword):
    match = re.search(keyword + r".{0,20}(\d+\.?\d*)", text)
    return float(match.group(1)) if match else None

def compare(value, low, name):
    if value is None:
        st.info(f"{name}: Not detected")
    elif value < low:
        st.warning(f"{name} is below normal range 🔻")
    else:
        st.success(f"{name} is within healthy range ✅")


# =========================================================
# AUTH
# =========================================================
USERS_FILE = "users.csv"
if os.path.exists(USERS_FILE):
    users = pd.read_csv(USERS_FILE)
else:
    users = pd.DataFrame(columns=["username", "password"])
 
for key, val in [("logged_in", False), ("user", None), ("moods", ["Happy","Calm","Okay","Sad","Stressed"])]:
    if key not in st.session_state:
        st.session_state[key] = val
 
if not st.session_state.logged_in:
    st.sidebar.markdown("### Welcome 💕")
    mode = st.sidebar.radio("Mode", ["Login", "Sign Up"], label_visibility="collapsed", horizontal=True)
 
    with st.sidebar.form(key="auth_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_label = "Create Account 💕" if mode == "Sign Up" else "Login →"
        submitted = st.form_submit_button(submit_label, use_container_width=True)
 
    if submitted:
        if mode == "Sign Up":
            if username in users["username"].values:
                st.sidebar.error("User already exists")
            else:
                users = pd.concat([users, pd.DataFrame([{"username": username, "password": hash_password(password)}])])
                users.to_csv(USERS_FILE, index=False)
                st.sidebar.success("Account created 💕")
        else:
            user_row = users[users["username"] == username]
            if len(user_row) > 0 and user_row.iloc[0]["password"] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.sidebar.error("Wrong credentials")
 
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:center;height:60vh;flex-direction:column;gap:16px;">
        <div style="font-size:4rem;">💖</div>
        <div style="font-family:'Playfair Display',serif;font-size:2rem;color:#c2185b;font-weight:700;">Health Tracker</div>
        <div style="color:#ad6c87;font-size:15px;">Please log in to continue</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
 
# Session state defaults
for key, val in [("page", "Dashboard"), ("confirm_delete", False)]:
    if key not in st.session_state:
        st.session_state[key] = val
 
 
# =========================================================
# SIDEBAR — PROFILE
# =========================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### 👤 Profile")
st.sidebar.markdown(f'<div class="profile-name">{st.session_state.user}</div>', unsafe_allow_html=True)


st.sidebar.markdown("---")
age    = st.sidebar.number_input("Age", 10, 100, 24)
height = st.sidebar.number_input("Height (cm)", 100, 220, 160)
weight = st.sidebar.number_input("Weight (kg)", 30.0, 200.0, 60.0)
bmi    = weight / ((height / 100) ** 2)
st.sidebar.markdown(f"**BMI:** {bmi:.1f}")

with st.sidebar.expander("📊 Normal Ranges"):
    st.markdown("**Vitamin D:** 20–50  \n**Iron:** 50–150  \n**B12:** 300–900")


st.sidebar.markdown("---")
st.sidebar.markdown(f'<div style="font-size:12px;color:#ad6c87;text-align:center;margin-bottom:8px;">Logged in as <b>{st.session_state.user}</b></div>', unsafe_allow_html=True)
if st.sidebar.button("👋 Log out"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()
 
# =========================================================
# USER DATA
# =========================================================
FILE = f"data_{st.session_state.user}.csv"
if os.path.exists(FILE):
    df = pd.read_csv(FILE)
else:
    df = pd.DataFrame()
for col in ["mood","energy","sleep","iron","vitamin_d","b12"]:
    if col not in df.columns:
        df[col] = []


# =========================================================
# WELCOME BANNER
# =========================================================
st.markdown(f"""
<div class="welcome-banner">
    Welcome back, <b>{st.session_state.user}</b> 👋<br>
    <span style="font-size:14px;opacity:0.85;">Track your health, cycle, mood &amp; vitamins</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">Health Tracker</div>', unsafe_allow_html=True)
st.markdown('<div class="app-caption">Cycle · Vitamins · Mood · Insights</div>', unsafe_allow_html=True)


# =========================================================
# NAV BAR
# =========================================================
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🏠 Home"):
        st.session_state.page = "Dashboard"; st.rerun()
with c2:
    if st.button("🌸 Cycle"):
        st.session_state.page = "Cycle"; st.rerun()
with c3:
    if st.button("📈 Trends"):
        st.session_state.page = "Trends"; st.rerun()
with c4:
    if st.button("💡 Insights"):
        st.session_state.page = "Insights"; st.rerun()


# =========================================================
# DASHBOARD
# =========================================================
if st.session_state.page == "Dashboard":

    st.markdown('<div class="section-header">Dashboard</div>', unsafe_allow_html=True)

    # ── TODAY'S ACTIVITY CARDS ──
    st.markdown("#### 📋 Today's Activity Log")

    if len(df) > 0:
        last = df.iloc[-1]
        sleep_val  = last.get("sleep", 0)
        energy_val = last.get("energy", 0)
        mood_val   = last.get("mood", 3)
        vit_d_val  = last.get("vitamin_d", 0)
        iron_val   = last.get("iron", 0)
        b12_val    = last.get("b12", 0)

        mood_text = "😄 Great" if mood_val >= 4 else ("😐 Okay" if mood_val == 3 else ("😔 Low" if mood_val == 2 else "😩 Stressed"))
        sleep_status = "Good 🟢" if sleep_val >= 7 else "Low 🟡"
        vit_status   = "OK 🟢" if (vit_d_val >= 20 and iron_val >= 50 and b12_val >= 300) else "Low 🟡"

        st.markdown(f"""
        <div class="activity-grid">
            <div class="activity-card">
                <div style="font-size:1.6rem;margin-bottom:8px;">😴</div>
                <div class="time time-pink">{sleep_val}h sleep</div>
                <div class="label">{sleep_status}</div>
            </div>
            <div class="activity-card">
                <div style="font-size:1.6rem;margin-bottom:8px;">⚡</div>
                <div class="time time-orange">Energy {energy_val}/5</div>
                <div class="label">Today's level</div>
            </div>
            <div class="activity-card">
                <div style="font-size:1.6rem;margin-bottom:8px;">🧠</div>
                <div class="time time-purple">{mood_text}</div>
                <div class="label">Current mood</div>
            </div>
            <div class="activity-card">
                <div style="font-size:1.6rem;margin-bottom:8px;">💊</div>
                <div class="time time-rose">Vitamins</div>
                <div class="label">{vit_status}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="activity-grid">
            <div class="activity-card" style="opacity:0.5;">
                <div style="font-size:1.6rem;margin-bottom:8px;">😴</div>
                <div class="time time-pink">—</div>
                <div class="label">Sleep</div>
            </div>
            <div class="activity-card" style="opacity:0.5;">
                <div style="font-size:1.6rem;margin-bottom:8px;">⚡</div>
                <div class="time time-orange">—</div>
                <div class="label">Energy</div>
            </div>
            <div class="activity-card" style="opacity:0.5;">
                <div style="font-size:1.6rem;margin-bottom:8px;">🧠</div>
                <div class="time time-purple">—</div>
                <div class="label">Mood</div>
            </div>
            <div class="activity-card" style="opacity:0.5;">
                <div style="font-size:1.6rem;margin-bottom:8px;">💊</div>
                <div class="time time-rose">—</div>
                <div class="label">Vitamins</div>
            </div>
        </div>
        <p style="color:#ad6c87;font-size:14px;text-align:center;">No data yet — start your first check-in below 💕</p>
        """, unsafe_allow_html=True)

    # ── SUGGESTIONS ──
    st.markdown("#### 💝 Today's Suggestions")
    st.markdown("""
    <div class="suggestions-row">
        <div class="suggestion-card">
            <div class="icon">🧘</div>
            <div class="title">Mindful Moment</div>
            <div class="desc">Take a breath, slow down</div>
        </div>
        <div class="suggestion-card">
            <div class="icon">🌸</div>
            <div class="title">Cycle Check</div>
            <div class="desc">Log your cycle data today</div>
        </div>
        <div class="suggestion-card">
            <div class="icon">📊</div>
            <div class="title">View Trends</div>
            <div class="desc">See your weekly health summary</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── DAILY CHECK-IN ──
    st.markdown('<div class="section-header">Daily Check-In 💕</div>', unsafe_allow_html=True)

    mood = st.radio("How are you feeling today?", st.session_state.moods, horizontal=True)

    new_mood = st.text_input("Add a new mood (optional)")
    if st.button("Add Mood"):
        if new_mood and new_mood not in st.session_state.moods:
            st.session_state.moods.append(new_mood)
            st.success("Mood added 💕")
            st.rerun()
        elif new_mood:
            st.warning("Mood already exists")

    st.markdown("##### 😴 Sleep")
    sleep = st.slider("Hours of sleep", 0.0, 12.0, 7.0, 0.5, label_visibility="collapsed")
    st.markdown(f'<div class="sleep-circle">{sleep}h</div>', unsafe_allow_html=True)

    st.markdown("##### ⚡ Energy")
    st.write("Rate your energy from 1 to 5")
    energy = st.slider("Energy level (1–5)", 1, 5, 3, label_visibility="collapsed")

    st.markdown("##### 💊 Vitamins")
    tab_iron, tab_vitd, tab_b12 = st.tabs(["🩸 Iron", "☀️ Vitamin D", "🧬 B12"])
 
    with tab_iron:
        st.markdown("**Normal range: 50–150**")
        iron = st.number_input("Iron level (µg/dL)", min_value=0.0, step=1.0, key="iron_input")
        if iron > 0:
            if iron < 50:
                st.warning("Below normal range 🔻")
            elif iron <= 150:
                st.success("Within healthy range ✅")
            else:
                st.warning("Above normal range ⬆️")
 
    with tab_vitd:
        st.markdown("**Normal range: 20–50**")
        vitamin_d = st.number_input("Vitamin D level (ng/mL)", min_value=0.0, step=1.0, key="vitd_input")
        if vitamin_d > 0:
            if vitamin_d < 20:
                st.warning("Below normal range 🔻")
            elif vitamin_d <= 50:
                st.success("Within healthy range ✅")
            else:
                st.warning("Above normal range ⬆️")
 
    with tab_b12:
        st.markdown("**Normal range: 300–900**")
        b12 = st.number_input("B12 level (pg/mL)", min_value=0.0, step=1.0, key="b12_input")
        if b12 > 0:
            if b12 < 300:
                st.warning("Below normal range 🔻")
            elif b12 <= 900:
                st.success("Within healthy range ✅")
            else:
                st.warning("Above normal range ⬆️")
 

    if st.button("💾 Save Health Data"):
        mood_map = {"Happy":5,"Calm":4,"Okay":3,"Sad":2,"Stressed":1}
        mapped_mood = mood_map.get(mood, 3)
        new_entry = pd.DataFrame([{
            "date": date.today(), "mood": mapped_mood,
            "sleep": sleep, "energy": energy,
            "iron": iron, "vitamin_d": vitamin_d, "b12": b12
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(FILE, index=False)
        st.success("Saved 💕")


# =========================================================
# CYCLE
# =========================================================
elif st.session_state.page == "Cycle":

    st.markdown('<div class="section-header">🌸 Cycle Tracker</div>', unsafe_allow_html=True)

    CYCLE_PERIODS_FILE = f"cycle_periods_{st.session_state.user}.csv"

    # Load saved periods
    if os.path.exists(CYCLE_PERIODS_FILE):
        periods_df = pd.read_csv(CYCLE_PERIODS_FILE)
        periods_df["start"] = pd.to_datetime(periods_df["start"]).dt.date
        periods_df["end"]   = pd.to_datetime(periods_df["end"]).dt.date
    else:
        periods_df = pd.DataFrame(columns=["start", "end"])

    col1, col2 = st.columns(2)
    period_start = col1.date_input("Period Start")
    period_end   = col2.date_input("Period End")

    if period_end < period_start:
        st.error("End date must be after start date")
        st.stop()

    if st.button("💾 Save Period"):
        new_period = pd.DataFrame([{"start": period_start, "end": period_end}])
        periods_df = pd.concat([periods_df, new_period], ignore_index=True)
        periods_df.to_csv(CYCLE_PERIODS_FILE, index=False)
        st.success("Period saved 💕")
        st.rerun()

    # Build calendar events from ALL saved periods
    events = []
    for _, row in periods_df.iterrows():
        s = row["start"]
        events.append({"title": "🔴 Period", "start": str(s), "end": str(row["end"]), "color": "#e91e63"})
        events.append({"title": "🟣 Fertile Window",
                        "start": str(s + timedelta(days=10)),
                        "end":   str(s + timedelta(days=15)),
                        "color": "#ce93d8"})

    st.markdown("#### 📅 Cycle Calendar")
    calendar(events=events, options={
        "initialView": "dayGridMonth",
        "headerToolbar": {"left":"prev,next today","center":"title","right":"dayGridMonth,timeGridWeek"}
    })

    # Show saved periods table
    if len(periods_df) > 0:
        st.markdown("#### 📋 Saved Periods")
        st.dataframe(periods_df.rename(columns={"start":"Start","end":"End"}), use_container_width=True, hide_index=True)
        if st.button("🗑️ Delete Last Period"):
            periods_df = periods_df.iloc[:-1]
            periods_df.to_csv(CYCLE_PERIODS_FILE, index=False)
            st.rerun()

    # ── DAILY CYCLE LOG ──
    st.markdown("#### 📝 Daily Cycle Log")
    log_date   = st.date_input("Date", key="cycle_log_date")
    cycle_mood = st.selectbox("Mood", ["Great","Good","Okay","Bad","Terrible"])
    flow       = st.selectbox("Flow", ["None","Spotting","Light","Medium","Heavy"])
    notes      = st.text_input("Notes")

    if st.button("💾 Save Daily Entry"):
        cycle_file = f"cycle_{st.session_state.user}.csv"
        new_entry  = pd.DataFrame([{"date":log_date,"mood":cycle_mood,"flow":flow,"notes":notes}])
        if os.path.exists(cycle_file):
            old = pd.concat([pd.read_csv(cycle_file), new_entry], ignore_index=True)
        else:
            old = new_entry
        old.to_csv(cycle_file, index=False)
        st.success("Saved 💕")

    # ── PHASE INFO ──
    # Use most recently saved period if available, else fall back to widget value
    if len(periods_df) > 0:
        last_saved_start = periods_df.iloc[-1]["start"]
    else:
        last_saved_start = period_start

    today     = date.today()
    cycle_day = (today - last_saved_start).days + 1

    if cycle_day <= 5:
        phase = "🩸 Menstrual Phase"
        tips  = ["Rest more 💤","Eat iron-rich foods 🥗","Warm tea helps cramps ☕"]
    elif cycle_day <= 13:
        phase = "🌱 Follicular Phase"
        tips  = ["High energy phase ⚡","Great time to work out 🏃‍♀️","Focus improves 🎯"]
    elif cycle_day <= 16:
        phase = "🌟 Ovulation Phase"
        tips  = ["Social energy high 🤝","Hydrate well 💧","Confidence boost 💪"]
    else:
        phase = "🌙 Luteal Phase"
        tips  = ["Mood swings possible 🌊","Reduce stress 🧘","Sleep more 😴"]

    st.markdown(f"""
    <div class="summary-card" style="margin-top:20px;">
        <div style="font-size:1.1rem;font-weight:700;color:#c2185b;margin-bottom:10px;">{phase}</div>
        {''.join(f'<div style="margin:4px 0;">• {t}</div>' for t in tips)}
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# TRENDS
# =========================================================
elif st.session_state.page == "Trends":

    st.markdown('<div class="section-header">📈 Trends</div>', unsafe_allow_html=True)
    st.markdown("Keep track of your progress 💕")

    if len(df) > 0:
        # Ensure date column is parsed and set as index for x-axis labeling
        df_plot = df.copy()
        if "date" in df_plot.columns:
            df_plot["date"] = pd.to_datetime(df_plot["date"])
            df_plot = df_plot.set_index("date")

        # ── SLEEP ──
        st.markdown("##### 😴 Sleep Over Time")
        avg_sleep = df_plot["sleep"].mean()
        min_sleep = df_plot["sleep"].min()
        max_sleep = df_plot["sleep"].max()
        trend_sleep = "improving 📈" if df_plot["sleep"].iloc[-1] > avg_sleep else "below average 📉"
        st.markdown(f"""
        <div class="summary-card">
            <b>Summary:</b> Your average sleep is <b>{avg_sleep:.1f}h</b> per night
            (min <b>{min_sleep:.1f}h</b>, max <b>{max_sleep:.1f}h</b>).
            Your most recent night is {trend_sleep}.
            {"✅ You're hitting the recommended 7–9h!" if avg_sleep >= 7 else "⚠️ Try to aim for at least 7 hours consistently."}
        </div>
        """, unsafe_allow_html=True)
        st.line_chart(df_plot["sleep"], use_container_width=True)

        # ── VITAMINS ──
        st.markdown("##### 💊 Vitamins Over Time")
        vit_cols = [c for c in ["vitamin_d", "iron", "b12"] if c in df_plot.columns]
        if vit_cols:
            avg_vd  = df_plot["vitamin_d"].mean() if "vitamin_d" in df_plot.columns else 0
            avg_fe  = df_plot["iron"].mean()       if "iron"      in df_plot.columns else 0
            avg_b12 = df_plot["b12"].mean()        if "b12"       in df_plot.columns else 0
            vit_notes = []
            if avg_vd  < 20:  vit_notes.append("Vitamin D is low ☀️")
            if avg_fe  < 50:  vit_notes.append("Iron is low 🩸")
            if avg_b12 < 300: vit_notes.append("B12 is low 🧬")
            summary_text = " · ".join(vit_notes) if vit_notes else "All vitamins look on track ✅"
            st.markdown(f"""
            <div class="summary-card">
                <b>Summary:</b> Avg Vitamin D <b>{avg_vd:.0f}</b> ng/mL ·
                Avg Iron <b>{avg_fe:.0f}</b> µg/dL ·
                Avg B12 <b>{avg_b12:.0f}</b> pg/mL.<br>
                {summary_text}
            </div>
            """, unsafe_allow_html=True)
            st.line_chart(df_plot[vit_cols], use_container_width=True)

        # ── ENERGY ──
        st.markdown("##### ⚡ Energy Over Time")
        avg_energy = df_plot["energy"].mean()
        min_energy = df_plot["energy"].min()
        max_energy = df_plot["energy"].max()
        energy_trend = "rising ⚡" if df_plot["energy"].iloc[-1] > avg_energy else "dipping 💤"
        st.markdown(f"""
        <div class="summary-card">
            <b>Summary:</b> Your average energy is <b>{avg_energy:.1f}/5</b>
            (min <b>{min_energy}</b>, max <b>{max_energy}</b>).
            Your latest entry is {energy_trend}.
            {"✅ Great energy levels!" if avg_energy >= 3.5 else "⚠️ Low energy — check sleep and iron levels."}
        </div>
        """, unsafe_allow_html=True)
        st.line_chart(df_plot["energy"], use_container_width=True)

    else:
        st.info("No trend data yet. Start logging daily! 💕")

# =========================================================
# INSIGHTS
# =========================================================
elif st.session_state.page == "Insights":

    st.markdown('<div class="section-header">💡 Insights & Recommendations</div>', unsafe_allow_html=True)

    if len(df) > 0:
        recommendations = []
        if df["energy"].mean() < 2.5:
            recommendations.append("⚡ Your energy is low. Try more sleep and short walks.")
        if df["sleep"].mean() < 6:
            recommendations.append("😴 Sleep is below 6h. Aim for a consistent sleep schedule.")
        if df["vitamin_d"].mean() < 20:
            recommendations.append("☀️ Vitamin D is low. Get more sunlight or ask your doctor about supplements.")
        if df["iron"].mean() < 50:
            recommendations.append("🥗 Iron is low. Spinach, red meat, or lentils are good sources of iron. Ask your doctor about taking supplements.")
        if df["b12"].mean() < 300:
            recommendations.append("🥚 B12 is low. Eating eggs and dairy and ask your doctor about taking supplements.")

        if recommendations:
            for r in recommendations:
                st.warning(r)
        else:
            st.success("You're doing great! Keep your current habits 🌟")
    else:
        st.info("No data yet — check in daily to see your insights! 💕")

    st.markdown("---")
    st.markdown("##### 🌸 Daily Wellness Tip")
    tips = [
        "Drink water first thing in the morning 💧",
        "Take a 10–15 min walk daily 🚶‍♀️",
        "Avoid screens before bed 📵",
        "Eat balanced meals 🥗",
        "Stretch for 5 minutes daily 🧘"
    ]
    st.markdown(f"""
    <div class="summary-card" style="text-align:center;font-size:16px;font-weight:500;">
        {tips[hash(str(date.today())) % len(tips)]}
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# DATA CONTROL
# =========================================================
st.markdown("---")
st.markdown("##### 🗄️ Data Control")

if st.button("🗑️ Delete All Data"):
    st.session_state.confirm_delete = True

if st.session_state.confirm_delete:
    st.warning("Are you sure? This cannot be undone ⚠️")
    col1, col2 = st.columns(2)
    if col1.button("Yes, delete"):
        if os.path.exists(FILE):
            os.remove(FILE)
        df = pd.DataFrame()
        st.session_state.confirm_delete = False
        st.success("All data deleted")
    if col2.button("Cancel"):
        st.session_state.confirm_delete = False


# =========================================================
# CSV UPLOAD
# =========================================================
with st.expander("📁 Upload CSV"):
    file = st.file_uploader("Upload file")
    if file:
        st.dataframe(pd.read_csv(file))


# =========================================================
# PDF ANALYZER
# =========================================================
with st.expander("📄 Upload Lab Report PDF"):
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
    if pdf_file:
        doc  = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = "".join(page.get_text().lower() for page in doc)
        st.success("PDF loaded ✅")

        vit_d = extract_value(text, "vitamin d")
        iron  = extract_value(text, "iron")
        b12   = extract_value(text, "b12")

        col1, col2, col3 = st.columns(3)
        col1.metric("Vitamin D", vit_d)
        col2.metric("Iron", iron)
        col3.metric("B12", b12)

        st.markdown("##### 🔍 Analysis")
        compare(vit_d, 20, "Vitamin D")
        compare(iron,  50, "Iron")
        compare(b12,  300, "B12")