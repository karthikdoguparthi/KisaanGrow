# KisaanGrow Streamlit App — Modern UI + Language Toggle (English/Hindi)

import streamlit as st
import pandas as pd
import gspread
import json
import openai
import time
from google.oauth2.service_account import Credentials
from datetime import datetime
import random


# ===================== SESSION TIMEOUT =====================
INACTIVITY_LIMIT = 300  # seconds (5 minutes)

if 'last_activity' not in st.session_state:
    st.session_state.last_activity = time.time()

# Reset timer on every interaction
st.session_state.last_activity = time.time()

# Auto‑logout check
if 'user' in st.session_state and time.time() - st.session_state.last_activity > INACTIVITY_LIMIT:
    for k in ['user','mobile','name','emp','corp_name','page']:
        st.session_state.pop(k, None)
    st.warning("Session expired due to inactivity. Please login again.")
    st.rerun()


st.set_page_config(page_title="KisaanGrow", page_icon="🌾", layout="wide", initial_sidebar_state="expanded")

# =========================================================
# LANGUAGE SYSTEM
# =========================================================
LANGUAGES = {"en": "English", "hi": "हिन्दी"}

if "lang" not in st.session_state:
    st.session_state.lang = "en"

# Set ai_lang to match lang if not already set
if "ai_lang" not in st.session_state:
    st.session_state.ai_lang = st.session_state.lang

lang = st.session_state.lang

# TRANSLATION DICTIONARY
TEXT = {
    "title": {"en": "Welcome to KisaanGrow", "hi": "किसानग्रो में आपका स्वागत है"},
    "subtitle": {"en": "Smart slot booking. AI guidance. Simple payments.", "hi": "स्मार्ट स्लॉट बुकिंग, AI सलाह और आसान भुगतान."},
    "home_line1": {
        "en": "KisaanGrow helps farmers book sugarcane delivery slots easily and avoid long waiting hours.",
        "hi": "किसानग्रो किसानों को गन्ने की डिलीवरी स्लॉट आसानी से बुक करने और लंबे इंतज़ार से बचने में मदद करता है।"
    },
    "home_line2": {
        "en": "Get instant AI guidance and track your payments in one place.",
        "hi": "तुरंत AI सलाह प्राप्त करें और अपने भुगतान एक ही जगह ट्रैक करें।"
    },

    # Login Cards
    "farmer_login": {"en": "Farmer Login", "hi": "किसान लॉगिन"},
    "corporate_login": {"en": "Corporate Login", "hi": "कॉपोरेट लॉगिन"},
    "mobile": {"en": "Mobile Number", "hi": "मोबाइल नंबर"},
    "password": {"en": "Password", "hi": "पासवर्ड"},
    "login_btn": {"en": "Login", "hi": "लॉगिन करें"},
    "login_success": {"en": "Login successful", "hi": "लॉगिन सफल"},
    "login_error": {"en": "Invalid credentials", "hi": "गलत जानकारी"},

    # Farmer Dashboard
    "farmer_dashboard": {"en": "Farmer Dashboard", "hi": "किसान डैशबोर्ड"},
    "book_slot": {"en": "Book a Slot", "hi": "स्लॉट बुक करें"},
    "quantity": {"en": "Sugarcane quantity (tonnes)", "hi": "गन्ने की मात्रा (टन में)"},
    "choose_date": {"en": "Choose slot date", "hi": "स्लॉट की तारीख चुनें"},
    "choose_time": {"en": "Select time slot", "hi": "समय का स्लॉट चुनें"},
    "book_btn": {"en": "Book Slot", "hi": "स्लॉट बुक करें"},
    "slot_booked": {"en": "Slot booked!", "hi": "स्लॉट बुक हो गया!"},
    "ai_tip": {"en": "AI Advice", "hi": "AI सलाह"},

    # Corporate Dashboard
    "corp_dashboard": {"en": "Corporate Dashboard", "hi": "कॉपोरेट डैशबोर्ड"},
    "all_bookings": {"en": "All Bookings", "hi": "सभी बुकिंग"},
    "no_slots": {"en": "No farmer bookings yet.", "hi": "अभी कोई किसान बुकिंग नहीं है."},

    "farmer_reg": {"en": "Farmer Registration", "hi": "किसान पंजीकरण"},
    "corp_reg": {"en": "Corporate Registration", "hi": "कॉपोरेट पंजीकरण"},
    "full_name": {"en": "Full Name", "hi": "पूरा नाम"},
    "aadhar": {"en": "Aadhar Number", "hi": "आधार नंबर"},
    "village": {"en": "Village (optional)", "hi": "गाँव (ऐच्छिक)"},
    "create_pwd": {"en": "Create Password", "hi": "पासवर्ड बनाएँ"},
    "confirm_pwd": {"en": "Confirm Password", "hi": "पासवर्ड की पुष्टि करें"},
    "reg_farmer_btn": {"en": "Register Farmer", "hi": "किसान पंजीकृत करें"},
    "reg_success_farmer": {"en": "Farmer registered successfully!", "hi": "किसान सफलतापूर्वक पंजीकृत हो गया!"},
    "emp_id": {"en": "Employee ID", "hi": "कर्मचारी आईडी"},
    "role": {"en": "Role", "hi": "भूमिका"},
    "reg_corp_btn": {"en": "Register Corporate User", "hi": "कॉपोरेट उपयोगकर्ता पंजीकृत करें"},
    "reg_success_corp": {"en": "Corporate user registered successfully!", "hi": "कॉपोरेट उपयोगकर्ता सफलतापूर्वक पंजीकृत हुआ!"},
    "slot_id": {"en": "Enter Slot ID to update payment", "hi": "भुगतान अपडेट करने के लिए स्लॉट आईडी दर्ज करें"},
    "payment_status": {"en": "Payment status", "hi": "भुगतान स्थिति"},
    "update_payment_btn": {"en": "Update Payment", "hi": "भुगतान अपडेट करें"},
    "payment_updated": {"en": "Payment status updated", "hi": "भुगतान स्थिति अपडेट हो गई"},
    "payment_failed": {"en": "Slot ID not found", "hi": "स्लॉट आईडी नहीं मिली"}
}

# Translation helper
T = lambda key: TEXT[key][st.session_state.lang]

# =========================================================
# MODERN THEME COLORS
# =========================================================
PRIMARY = "#2E7D32"
ACCENT = "#A5D6A7"
CARD_BG = "#FFFFFF"
CARD_SHADOW = "0 4px 12px rgba(0,0,0,0.1)"

# =========================================================
# LOTTIE
# =========================================================


# =========================================================
# GOOGLE SHEETS
# =========================================================
@st.cache_resource
def get_gsheet_client():
    data = json.loads(st.secrets['GCP_SERVICE_ACCOUNT'])
    scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_info(data, scopes=scopes)
    return gspread.authorize(creds)

@st.cache_data(ttl=20)
def read_sheet(name):
    sh = get_gsheet_client().open_by_key(st.secrets['SHEET_ID'])
    try:
        ws = sh.worksheet(name)
        return pd.DataFrame(ws.get_all_records())
    except:
        return pd.DataFrame()

def write_row(sheet, row_dict):
    sh = get_gsheet_client().open_by_key(st.secrets['SHEET_ID'])
    try:
        ws = sh.worksheet(sheet)
    except:
        ws = sh.add_worksheet(sheet, rows=500, cols=20)
        ws.append_row(list(row_dict.keys()))
    headers = sh.worksheet(sheet).row_values(1)
    sh.worksheet(sheet).append_row([row_dict.get(h, '') for h in headers])

# =========================================================
# AI ADVICE — LANG AWARE
# =========================================================
from openai import OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ai_advice(qty, days):
    if not st.secrets.get("OPENAI_API_KEY"):
        return T("ai_tip")

    if st.session_state.ai_lang == "hi":
        prompt = f"किसान के लिए {qty} टन गन्ने और {days} दिनों के आधार पर एक छोटी, सरल और उपयोगी सलाह दें।"
    else:
        prompt = f"Give short, simple and useful advice for a farmer based on {qty} tonnes of sugarcane and {days} days."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI Error: {e}"

# =========================================================
# CARD COMPONENT
# =========================================================

def card(title, content, icon="", color=PRIMARY):
    # Black background for AI Advice and Payment Status cards
    if icon in ["🤖", "💰"]:
        bg = "#000000"
    else:
        bg = CARD_BG

    st.markdown(
        f"""
        <div style="background:{bg}; padding:20px; border-radius:12px;
        box-shadow:{CARD_SHADOW}; border-left:6px solid {color};
        color:#000000 !important;">
            <h3 style="margin:0; color:{color};">{icon} {title}</h3>
            <p style="margin-top:10px; font-size:16px; color:#000000 !important;">{content}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================================================
# PAGE: HOME
# =========================================================

def page_home():
    st.markdown(f"<h1 style='color:{PRIMARY}; text-align:center;'>{T('title')} 🌾</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; font-size:18px;'>{T('subtitle')}</p>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center; font-size:16px; margin-top:10px;'>{T('home_line1')}</p>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='text-align:center; font-size:16px; margin-top:5px;'>{T('home_line2')}</p>",
        unsafe_allow_html=True
    )

    st.markdown("---")
    left, right = st.columns(2)

    with left:
        card(T("farmer_login"), "", "👨‍🌾")
        with st.form('farmer_login'):
            m = st.text_input(T("mobile"))
            p = st.text_input(T("password"), type='password')
            if st.form_submit_button(T("login_btn")):
                df = read_sheet('Farmers')
                match = df[(df['Mobile'].astype(str)==m) & (df['Password']==p)]
                if not match.empty:
                    st.session_state.user='farmer'
                    st.session_state.mobile=m
                    st.session_state.name=match.iloc[0]['Name']
                    st.success(T("login_success"))
                    st.balloons()
                    st.session_state.page = "Farmer Dashboard"
                    st.rerun()
                else:
                    st.error(T("login_error"))
        if st.button("New Farmer? Create Account", key="new_farmer_btn"):
            st.session_state.page = "Farmer Registration"
            st.rerun()

    with right:
        card(T("corporate_login"), "", "🏢", color="#1565C0")
        with st.form('corp_login'):
            e = st.text_input("Employee ID")
            pw = st.text_input(T("password"), type='password')
            if st.form_submit_button(T("login_btn")):
                df = read_sheet('Corporates')
                match = df[(df['Corp_ID'].astype(str)==e) & (df['Password']==pw)]
                if not match.empty:
                    st.session_state.user='corp'
                    st.session_state.emp=e
                    st.session_state.corp_name=match.iloc[0]['Name']
                    st.success(T("login_success"))
                    st.session_state.page = "Corporate Dashboard"
                    st.rerun()
                else:
                    st.error(T("login_error"))

# =========================================================
# PAGE: FARMER DASHBOARD
# =========================================================

def page_farmer_dashboard():
    st.markdown(f"<h2 style='color:{PRIMARY};'>📊 {T('farmer_dashboard')}</h2>", unsafe_allow_html=True)
    if st.button("🏠 Home", key="farmer_home_btn"):
        st.session_state.page = "Home"
        st.rerun()

    if 'name' in st.session_state:
        st.write(f"Welcome, {st.session_state.name}!")

    if st.button("Logout", key="farmer_logout"):
        for k in ['user','mobile','name','page']:
            st.session_state.pop(k, None)
        st.rerun()

    # --- Slot Booking ---
    card(T("book_slot"), "")

    qty = st.number_input(T("quantity"), min_value=0.0)
    date = st.date_input(T("choose_date"))
    times = [f"{h}:00 - {h+2}:00" for h in range(0,24,2)]
    t = st.selectbox(T("choose_time"), times)

    if st.button(T("book_btn"), use_container_width=True):
        write_row('Slots',{
            'Date':date.strftime('%Y-%m-%d'),
            'Time':t,
            'Quantity':qty,
            'Farmer_Mobile':st.session_state.mobile,
            'Farmer_Name':st.session_state.name,
            'Payment_Status':'pending'
        })
        st.success(T("slot_booked"))
        st.balloons()

    # --- AI Language Toggle ---
    st.markdown("#### AI Language")
    colAI1, colAI2 = st.columns(2)
    with colAI1:
        if st.button("English (AI)", key="ai_lang_en_btn"):
            st.session_state.ai_lang = "en"
    with colAI2:
        if st.button("हिन्दी (AI)", key="ai_lang_hi_btn"):
            st.session_state.ai_lang = "hi"

    st.markdown(f"<h3 style='text-align:center;'>🤖 {T('ai_tip')}</h3>", unsafe_allow_html=True)
    days = (date - datetime.today().date()).days
    card(T("ai_tip"), ai_advice(qty, days), "🤖", color="#9C27B0")

    st.markdown("---")
    st.markdown("### 📋 Your Booked Slots")

    df_slots = read_sheet('Slots')
    my_slots = df_slots[df_slots['Farmer_Mobile'].astype(str) == str(st.session_state.mobile)]

    if my_slots.empty:
        st.info(T('no_slots'))
    else:
        filter_date = st.date_input("Filter by Date (optional)")
        if filter_date:
            my_slots = my_slots[my_slots['Date'] == filter_date.strftime('%Y-%m-%d')]

        # Show only specific columns
        my_slots = my_slots[['Time', 'Quantity', 'Payment_Status']]
        st.dataframe(my_slots, use_container_width=True)

        st.markdown("### 💰 Check Payment Status")
        slot_list = df_slots.loc[my_slots.index, 'Date'] + " | " + my_slots['Time'] + " | ID:" + my_slots.index.astype(str)
        selected = st.selectbox("Select Slot", slot_list)

        if selected:
            try:
                idx = int(selected.split('ID:')[-1].strip())
                slot_row = my_slots.loc[idx]
                pay = slot_row['Payment_Status'] if 'Payment_Status' in slot_row else 'unknown'
                card("Payment Status", f"Current status: <b>{pay}</b>", "💰", color="#4CAF50")
            except Exception:
                st.warning("Unable to read slot details.")
        else:
            st.info("No slot selected.")

# =========================================================
# PAGE: CORPORATE DASHBOARD
# =========================================================

def page_corp_dashboard():
    st.markdown(f"<h2 style='color:{PRIMARY};'>🧾 {T('corp_dashboard')}</h2>", unsafe_allow_html=True)
    if st.button("🏠 Home", key="corp_home_btn"):
        st.session_state.page = "Home"
        st.rerun()

    if 'corp_name' in st.session_state:
        st.write(f"Welcome, {st.session_state.corp_name}!")
    if st.button("Logout", key="corp_logout"):
        for k in ['user','emp','corp_name','page']:
            st.session_state.pop(k, None)
        st.rerun()

    # --- KPI Section ---
    df = read_sheet('Slots')
    total_tonnes = df['Quantity'].sum() if not df.empty else 0
    unique_farmers = df['Farmer_Mobile'].nunique() if not df.empty else 0

    st.markdown("### 📊 Today's KPIs")

    # Banner summary with today's date
    today_str = datetime.today().strftime("%Y-%m-%d")
    st.markdown(
        f"""
        <div style='background:#000000; padding:18px; border-radius:10px; margin-bottom:20px; color:white;'>
            <h4>Today's Date: <b>{today_str}</b></h4>
            <h4>Today's Incoming Sugarcane: <b>{total_tonnes}</b> tonnes</h4>
            <h4>Total Farmers Registered Today: <b>{unique_farmers}</b></h4>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Gauge Charts
    import plotly.graph_objects as go
    colG1, colG2 = st.columns(2)

    with colG1:
        fig1 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_tonnes,
            title={'text': "Total Sugarcane (tonnes)"},
            gauge={'axis': {'range': [0, max(10, total_tonnes + 5)]}}
        ))
        st.plotly_chart(fig1, use_container_width=True)

    with colG2:
        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=unique_farmers,
            title={'text': "Unique Farmers Booked"},
            gauge={'axis': {'range': [0, max(5, unique_farmers + 1)]}}
        ))
        st.plotly_chart(fig2, use_container_width=True)

    if df.empty:
        card(T("no_slots"), "", "📭", color="#B71C1C")
    else:
        card(T("all_bookings"), "")
        st.dataframe(df, use_container_width=True)
        st.markdown("### 💰 Update Payment Status")
        if not df.empty:
            st.markdown("### 🔍 Filter Slots")

            colF1, colF2, colF3 = st.columns(3)
            with colF1:
                filter_farmer = st.selectbox("Farmer", ["All"] + sorted(df['Farmer_Name'].unique().tolist()))
            with colF2:
                filter_time = st.selectbox("Slot", ["All"] + sorted(df['Time'].unique().tolist()))
            with colF3:
                filter_status = st.selectbox("Payment Status", ["All", "paid", "pending"])

            df_filtered = df.copy()
            if filter_farmer != "All":
                df_filtered = df_filtered[df_filtered['Farmer_Name'] == filter_farmer]
            if filter_status != "All":
                df_filtered = df_filtered[df_filtered['Payment_Status'] == filter_status]
            if filter_time != "All":
                df_filtered = df_filtered[df_filtered['Time'] == filter_time]

            slot_options = df_filtered.apply(lambda row: f"{row['Farmer_Name']} | {row['Time']} | Qty: {row['Quantity']} | Status: {row['Payment_Status']} | ID:{row.name}", axis=1)

            selected_slot = st.selectbox("Select Slot to Update", slot_options)

            if selected_slot:
                try:
                    chosen_id = int(selected_slot.split("ID:")[-1].strip())

                    # Map pandas index to Google Sheets row (row 1 = header)
                    sheet_row = chosen_id + 2

                    new_status = st.selectbox(T('payment_status'), ['paid', 'pending'], key="status_update")

                    if st.button(T('update_payment_btn'), key="corp_status_btn"):
                        sh = get_gsheet_client().open_by_key(st.secrets['SHEET_ID'])
                        ws = sh.worksheet('Slots')

                        col_index = df.columns.get_loc('Payment_Status') + 1
                        ws.update_cell(sheet_row, col_index, new_status)

                        st.success(T('payment_updated'))
                except Exception as e:
                    st.error(f"Update failed: {e}")

# =========================================================
# PAGE: FARMER REGISTRATION
# =========================================================

def page_farmer_registration():
    st.markdown(f"<h2>👨‍🌾 {T('farmer_reg')}</h2>", unsafe_allow_html=True)
    if st.button("🏠 Home", key="farmer_reg_home_btn"):
        st.session_state.page = "Home"
        st.rerun()
    with st.form('farmer_reg'):
        name = st.text_input(T('full_name'))
        mobile = st.text_input(T('mobile'))
        aadhar = st.text_input(T('aadhar'))
        village = st.text_input(T('village'))
        pwd = st.text_input(T('create_pwd'), type='password')
        pwd2 = st.text_input(T('confirm_pwd'), type='password')
        submit = st.form_submit_button(T('reg_farmer_btn'))
        if submit:
            import re
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', pwd):
                st.error('Password must be 8+ chars with upper, lower and a number.')
            elif pwd != pwd2:
                st.error('Passwords do not match.')
            else:
                write_row('Farmers', {
                    'Name': name,
                    'Mobile': mobile,
                    'Aadhar': aadhar,
                    'Village': village,
                    'Password': pwd
                })
                st.success(T('reg_success_farmer'))

# =========================================================
# PAGE: CORPORATE REGISTRATION
# =========================================================

def page_corporate_registration():
    st.markdown(f"<h2>🏢 {T('corp_reg')}</h2>", unsafe_allow_html=True)
    if st.button("🏠 Home", key="corp_reg_home_btn"):
        st.session_state.page = "Home"
        st.rerun()
    with st.form('corp_reg'):
        name = st.text_input(T('full_name'))
        emp_id = st.text_input(T('emp_id'))
        role = st.text_input(T('role'))
        pwd = st.text_input(T('create_pwd'), type='password')
        pwd2 = st.text_input(T('confirm_pwd'), type='password')
        submit = st.form_submit_button(T('reg_corp_btn'))
        if submit:
            import re
            if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$', pwd):
                st.error('Password must be 8+ chars with upper, lower and a number.')
            elif pwd != pwd2:
                st.error('Passwords do not match.')
            else:
                write_row('Corporates', {
                    'Name': name,
                    'Corp_ID': emp_id,
                    'Role': role,
                    'Password': pwd
                })
                st.success(T('reg_success_corp'))

# =========================================================
# ROUTING + LANGUAGE TOGGLE
# =========================================================


# Language toggle without resetting progress
st.sidebar.markdown("### Language")
colA, colB = st.sidebar.columns(2)
with colA:
    if st.button("English", key="lang_en_btn"):
        st.session_state.lang = "en"
with colB:
    if st.button("हिन्दी", key="lang_hi_btn"):
        st.session_state.lang = "hi"

# Smooth UI transitions
st.markdown(
    """
    <style>
    * {
        transition: all 0.25s ease-in-out;
    }
    div[data-testid="stSidebar"] * {
        transition: all 0.25s ease-in-out;
    }
    button, select, input, textarea {
        transition: background-color 0.25s ease, color 0.25s ease, border 0.25s ease;
    }
    </style>
    """,
    unsafe_allow_html=True
)

page = st.session_state.get("page", st.sidebar.selectbox("Go to",[
    "Home",
    "Farmer Registration",
    "Corporate Registration",
    "Farmer Dashboard",
    "Corporate Dashboard"
]))

if page == "Home": page_home()
elif page == "Farmer Registration": page_farmer_registration()
elif page == "Corporate Registration": page_corporate_registration()
elif page == "Farmer Dashboard": page_farmer_dashboard()
elif page == "Corporate Dashboard": page_corp_dashboard()

st.sidebar.markdown("---")
st.sidebar.write("KisaanGrow © Bilingual Version")