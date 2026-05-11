import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime
from models.medora_oop import gen_id, Patient, Doctor, HealthRecord, MedicalDocument
from services.db import patients_col, doctors_col, records_col, documents_col
from services.db import users_col, messages_col, prescriptions_col
from ui.dashboard import (
    show_dashboard, show_chat_screen, show_calorie_predictor, show_admin_dashboard,
    show_lifestyle_predictor, show_stress_predictor, show_heart_predictor,
    show_genetic_test_predictor, show_add_record_form, show_add_medical_record,
    show_contact_doctor, show_patient_chat, show_doctor_inbox, show_doctor_chat
)
from ui.companion import show_companion_chat

st.set_page_config(page_title="Medora Login", layout="centered")
st.markdown("""
    <style>
    /* Expander header container */
    [data-testid="stExpander"] > details > summary {
        background: linear-gradient(135deg, rgb(34,193,195) 0%, rgb(253,187,45) 100%) !important;
        color: black !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 10px;
        list-style: none;
    }

    /* Expander arrow icon */
    [data-testid="stExpander"] svg {
        stroke: black !important;
    }

    /* Expander content */
    [data-testid="stExpander"] .streamlit-expanderContent {
        background: rgba(255,255,255,0.1) !important;
        color: white !important;
        border-radius: 8px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, rgb(34,193,195) 0%, rgb(253,187,45) 100%);
        color: white;
    }
    .stApp {
        background: linear-gradient(135deg, rgb(34,193,195) 0%, rgb(253,187,45) 100%);
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Target Streamlit buttons */
    div.stButton > button {
        color: black !important;   /* text color */
        background-color: #f0f0f0; /* optional: light background for contrast */
        border-radius: 8px;
        border: 1px solid #ccc;
    }
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Fix message text wrapping */
    .chat-wrapper{
        white-space: pre-wrap;
        word-break: break-word;
        display: block;
        font-size: 15px;
        line-height: 1.4;
    }

    .bubble-text {
        display: inline-block;
        white-space: pre-wrap;
        word-break: break-word;
        overflow-wrap: break-word;
        font-size: 15px;
        line-height: 1.4;
    }

    /* Patient bubble */
    .patient-msg {
        display: flex;
        align-items: flex-end;
        gap: 8px;
    }
    .patient-bubble {
        background: #fff;
        color: #111;
        padding: 10px 14px;
        border-radius: 18px 18px 18px 4px;
        max-width: 65%;
        font-size: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }

    /* Doctor bubble */
    .doctor-msg {
        display: flex;
        align-items: flex-end;
        gap: 8px;
        justify-content: flex-end;
    }
    .doctor-bubble {
        background: #0084ff;
        color: #fff;
        padding: 10px 14px;
        border-radius: 18px 18px 4px 18px;
        max-width: 65%;
        font-size: 15px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.25);
    }

    /* Avatars */
    .avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #ccc;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        font-weight: bold;
    }
    /* Remove top margin/padding */
    section.main > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    /* Timestamp */
    .timestamp {
        font-size: 11px;
        color: #666;
        margin-top: 4px;
        text-align: right;
    }

    .chat-header {
        font-size: 20px;
        font-weight: bold;
        color: #333;
        text-align: center;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "auth"  
if "selected_doctor" not in st.session_state:
    st.session_state.selected_doctor = None
if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None

st.title("🩺 Medora Health Assistant")

if st.session_state.page == "auth":
    if not st.session_state.logged_in:
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Signup", "👨‍💼 Admin"])

        with tab1:
            st.subheader("Login to Medora")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                user = users_col.find_one({"email": email, "password": password})
                if user:
                    users_col.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
                    )
                    st.session_state.user = user
                    st.session_state.page = "dashboard"
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with tab2:
            st.subheader("Create a Medora Account")
            name = st.text_input("Full Name", key="signup_name")
            email_new = st.text_input("Email Address", key="signup_email")
            password_new = st.text_input("Password", type="password", key="signup_password")
            role_new = st.selectbox("Role", ["patient", "doctor"])
            if st.button("Signup"):
                if users_col.find_one({"email": email_new}):
                    st.error("Email already registered")
                else:
                    user_id = gen_id("p_" if role_new == "patient" else "d_")
                    user_data = {
                        "user_id": user_id,
                        "name": name,
                        "email": email_new,
                        "password": password_new,
                        "role": role_new,
                        "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    users_col.insert_one(user_data)
                    st.success("Account created! Please login.")

        with tab3:
            st.subheader("Admin Login")
            admin_user = st.text_input("Admin Username", key="admin_username")
            admin_pass = st.text_input("Admin Password", type="password", key="admin_password")
            if st.button("Login as Admin"):
                if admin_user == "admin" and admin_pass == "admin123": 
                    st.session_state.page = "admin_dashboard"
                    st.session_state.logged_in = True
                    st.success("Welcome Admin!")
                    st.rerun()
                else:
                    st.error("Invalid admin credentials")

elif st.session_state.page == "dashboard" and st.session_state.user:
    show_dashboard(st.session_state.user)
elif st.session_state.page == "chat" and st.session_state.user:
    show_chat_screen(st.session_state.user)
elif st.session_state.page == "companion":
    show_chat_screen(st.session_state.user)
elif st.session_state.page == "calorie_predictor":
    show_calorie_predictor() 
elif st.session_state.page == "lifestyle_predictor":
    show_lifestyle_predictor()  
elif st.session_state.page == "stress_predictor":
    show_stress_predictor() 
elif st.session_state.page == "heart_predictor":
    show_heart_predictor()
elif st.session_state.page == "genetic_test_predictor":
    show_genetic_test_predictor()
elif st.session_state.page == "add_record":
    show_add_record_form(st.session_state.user)
elif st.session_state.page == "add_medrecord":
    show_add_medical_record(st.session_state.user)
elif st.session_state.page == "contact_doctor":
    show_contact_doctor(st.session_state.user)
elif st.session_state.page == "patient_chat":
    show_patient_chat(st.session_state.user)
elif st.session_state.page == "doctor_inbox":
    show_doctor_inbox(st.session_state.user)
elif st.session_state.page == "doctor_chat":
    show_doctor_chat(st.session_state.user)
elif st.session_state.page == "admin_dashboard":
    show_admin_dashboard()
