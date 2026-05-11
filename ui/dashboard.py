import streamlit as st
import numpy as np
from services.db import users_col, records_col, documents_col
from models.medora_oop import HealthRecord, MedicalDocument
from datetime import datetime
from models.medora_oop import gen_id
from models.medora_oop import MedicalDocument
#transformers
from services.chat_engine import get_medora_response
import plotly.graph_objects as go
#for chatbot
#from services.chat_engine import chatbot
from services.calorie_predictor import predict_calories
from services.lifestyle_predictor import predict_lifestyle
from services.stress_predictor import predict_stress
from services.heart_predictor import predict_heart_disease
from services.genetic_test_predictor import predict_genetic_test
import streamlit.components.v1 as components
import random
from datetime import datetime
from services.db import doctors_col, messages_col, prescriptions_col
from bson.objectid import ObjectId

def show_dashboard(user):
    role = user.get("role", "patient")

    if role == "doctor":
        show_doctor_dashboard(user)
    else:
        st.markdown("""
            <style>
            .welcome-banner {
                padding: 20px;
                border-radius: 12px;
                background: rgba(0,0,0,0.6); /* semi-transparent overlay */
                color: #fff;
                margin-bottom: 20px;
                animation: fadeIn 0.8s ease-in-out;
            }
            .section-box {
                margin-top: 20px;
                padding: 20px;
                border-radius: 10px;
                background: rgba(255,255,255,0.1); /* translucent card */
                border-left: 6px solid #ffcc00;
                color: #fff;
                animation: fadeIn 0.6s ease-in-out;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="welcome-banner">
                <h2>📊 Medora Dashboard</h2>
                <p>Welcome, <strong>{user['name']}</strong> ({user['role'].title()})</p>
            </div>
        """, unsafe_allow_html=True)

        records = list(records_col.find({"patient_id": user["user_id"]}))
        st.markdown('<div class="section-box"><h4>🩺 Health Records</h4>', unsafe_allow_html=True)
        if records:
            for r in records:
                st.markdown(f"""
                    <div style="
                        background: #e8f6f3;
                        border-radius: 12px;
                        padding: 18px;
                        margin-bottom: 15px;
                        margin-top: 15px;
                        border-left: 6px solid #2ecc71;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                        animation: fadeIn 0.6s ease-in-out;
                    ">
                        <p style="margin:6px 0; color:#333;">
                            ⏰ <strong>Timestamp:</strong> {str(r['timestamp'])}<br>
                            💓 <strong>Blood Pressure:</strong> {r['blood_pressure']}<br>
                            ❤️ <strong>Heart Rate:</strong> {r['heart_rate']} bpm<br>
                            ⚖️ <strong>Weight:</strong> {r['weight_kg']} kg<br>
                            📏 <strong>Height:</strong> {r['height_m']} m
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p>No health records found.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        def calculate_scores(records):
            if not records:   
                return {
                    "BMI Score": 0,
                    "Heart Health": 0,
                    "Fitness": 0,
                    "Wellness": 0
                }

            bmi_scores = []
            heart_scores = []

            for r in records:
                bmi = r["weight_kg"] / (r["height_m"] ** 2)
                bmi_score = max(0, 100 - abs(bmi - 22) * 5)
                heart_score = max(0, 100 - abs(r["heart_rate"] - 72) * 2)
                bmi_scores.append(bmi_score)
                heart_scores.append(heart_score)

            avg_bmi = sum(bmi_scores) / len(bmi_scores)
            avg_heart = sum(heart_scores) / len(heart_scores)
            fitness_score = (avg_bmi + avg_heart) / 2
            wellness_score = (avg_bmi + avg_heart + fitness_score) / 3

            return {
                "BMI Score": round(avg_bmi),
                "Heart Health": round(avg_heart),
                "Fitness": round(fitness_score),
                "Wellness": round(wellness_score)
            }


        def render_ring(label, value, color):
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value,
                title={'text': f"<b>{label}</b>", 'font': {'size': 18}},
                number={'font': {'size': 28}},
                gauge= {
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#fff"},
                    'bar': {'color': color},
                    'bgcolor': "rgba(255,255,255,0.1)",
                    'borderwidth': 2,
                    'bordercolor': "#fff",
                    'steps': [
                        {'range': [0, 50], 'color': '#f8d7da'},
                        {'range': [50, 80], 'color': '#fff3cd'},
                        {'range': [80, 100], 'color': '#d4edda'}
                    ],
                }
            ))
            fig.update_layout(
                margin=dict(t=20, b=0, l=0, r=0),
                height=300,
                paper_bgcolor="rgba(0,0,0,0)",  
                plot_bgcolor="rgba(0,0,0,0)"
            )

            return fig

        scores = calculate_scores(records)
        colors = {
            "BMI Score": "#6a11cb",
            "Heart Health": "#2ecc71",
            "Fitness": "#f39c12",
            "Wellness": "#e74c3c"
        }

        st.markdown('<div class="section-box"><h4>🌟 Health Insights</h4>', unsafe_allow_html=True)

        cols = st.columns(2)
        labels = list(scores.keys())
        for i in range(2):
            with cols[i]:
                fig = render_ring(labels[i], scores[labels[i]], colors[labels[i]])
                st.plotly_chart(fig, use_container_width=True)

        cols = st.columns(2)
        for i in range(2, 4):
            with cols[i - 2]:
                fig = render_ring(labels[i], scores[labels[i]], colors[labels[i]])
                st.plotly_chart(fig, use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

        documents = list(documents_col.find({"patient_id": user["user_id"]}))
        st.markdown('<div class="section-box"><h4>📁 Medical Documents</h4>', unsafe_allow_html=True)
        if documents:
            for d in documents:
                st.markdown(f"""
                    <div style="
                        background: #e8f6f3;
                        border-radius: 12px;
                        padding: 18px;
                        margin-bottom: 15px;
                        margin-top: 15px;
                        border-left: 6px solid #2ecc71;
                        animation: fadeIn 0.6s ease-in-out;
                    ">
                        <h4 style="margin:0; color:#2c3e50;">📄 {d['title']}</h4>
                        <p style="margin:6px 0; color:#555;">
                            🏥 <strong>Source:</strong> {d['source']}<br>
                            🗂️ <strong>Type:</strong> {d['file_type']}<br>
                            ⏰ <strong>Uploaded:</strong> {str(d['timestamp'])}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<p>No documents uploaded.</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.sidebar:
            st.markdown("""
                <style>
                [data-testid="stSidebar"] {
                    background: rgba(0,0,0,0.6);
                    color: #fff;
                }
                </style>
            """, unsafe_allow_html=True)

            st.header("⚙️ Actions")
            st.markdown("Use the tools below to explore Medora's features:")
            
            with st.expander("🚪 Logout"):
                st.write("Log out of your Medora account and return to the login screen.")
                if st.button("Confirm Logout"):
                    st.session_state.user = None
                    st.session_state.logged_in = False   
                    st.session_state.page = "auth"
                    st.rerun()

            with st.expander("➕ Add Health Record"):
                st.write("Record your latest health metrics like weight, height, blood pressure, and heart rate.")
                if st.button("Open Health Record Form"):
                    st.session_state.page = "add_record"
                    st.rerun()

            with st.expander("💬 Chat with AI Assistant"):
                st.write("Ask Medora anything medical or health-related. Get instant AI-powered answers.")
                if st.button("Start Chat", key="chat_button"):
                    st.session_state.page = "chat"
                    show_chat_screen(user)
                    st.rerun()

            with st.expander("🤗 Relieve Loneliness"):
                st.write("Talk to Medora’s companion chat for emotional support and friendly conversation.")
                if st.button("Open Companion Chat", key="loneliness_button"):
                    st.session_state.page = "companion"
                    st.rerun()

            with st.expander("🧮 Calorie Recommendation"):
                st.write("Get personalized calorie recommendations based on your body type and activity level.")
                if st.button("Open Calorie Predictor"):
                    st.session_state.page = "calorie_predictor"
                    st.rerun()

            with st.expander("🧠 Lifestyle Assessment"):
                st.write("Analyze your lifestyle habits and receive tailored health improvement suggestions.")
                if st.button("Open Lifestyle Predictor"):
                    st.session_state.page = "lifestyle_predictor"
                    st.rerun()

            with st.expander("🧠🧠 Stress Assessment"):
                st.write("Evaluate your stress level based on sleep, blood pressure, and emotional state.")
                if st.button("Open Stress Predictor"):
                    st.session_state.page = "stress_predictor"
                    st.rerun()

            with st.expander("❤️ Heart Risk Assessment"):
                st.write("Assess your risk of heart disease using clinical indicators and lifestyle factors.")
                if st.button("Open Heart Predictor"):
                    st.session_state.page = "heart_predictor"
                    st.rerun()

            with st.expander("🧬 Genetic Test Predictor"):
                st.write("Predict your need for genetic testing based on family history and environmental risks.")
                if st.button("Open Genetic Test Predictor"):
                    st.session_state.page = "genetic_test_predictor"
                    st.rerun()

            with st.expander("📁 Add Medical Health Record"):
                st.write("Upload medical documents like prescriptions, lab reports, or diagnostic files.")
                if st.button("Open Medical Record Upload"):
                    st.session_state.page = "add_medrecord"
                    st.rerun()

            with st.expander("📞 Contact Doctor"):
                st.write("Send a message to your doctor for advice, follow-up, or medication requests.")
                if st.button("Open Contact Form"):
                    st.session_state.page = "contact_doctor"
                    st.rerun()

def show_admin_dashboard():
    st.header("👨‍💼 Admin Dashboard")

    patients = list(users_col.find({"role": "patient"}))
    doctors = list(users_col.find({"role": "doctor"}))

    st.subheader("🧑‍🤝‍🧑 Patients")
    if patients:
        patient_data = []
        for p in patients:
            name = p.get("name", "Unknown")
            last_active = p.get("last_active", "N/A")
            patient_data.append({"ID": str(p["_id"]), "Name": name, "Last Active": last_active})
        st.table(patient_data)
    else:
        st.info("No patients found.")

    st.subheader("👨‍⚕️ Doctors")
    if doctors:
        doctor_data = []
        for d in doctors:
            name = d.get("name", "Unknown")
            last_active = d.get("last_active", "N/A")
            doctor_data.append({"ID": str(d["_id"]), "Name": name, "Last Active": last_active})
        st.table(doctor_data)
    else:
        st.info("No doctors found.")

    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
                color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)

        st.header("⚙️ Actions")

        with st.expander("🚪 Logout"):
            st.write("Log out of your admin panel and return to the login screen.")
            if st.button("Confirm Logout"):
                st.session_state.user = None
                st.session_state.logged_in = False
                st.session_state.page = "auth"
                st.rerun()
        st.markdown("""
            <style>
            /* Sidebar background */
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
            }

            /* Sidebar headers and labels */
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p {
                color: #ffffff !important;
            }

            /* Inputs inside sidebar */
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea,
            [data-testid="stSidebar"] select {
                background-color: #ffffff !important;
                color: #000000 !important;
                border-radius: 6px;
                padding: 6px;
            }

            /* Buttons inside sidebar */
            [data-testid="stSidebar"] button {
                background-color: #0084ff !important;
                color: #ffffff !important;
                border-radius: 6px;
                padding: 6px 12px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        with st.expander("❌ Remove Patient"):
            patient_id = st.text_input("Enter Patient ObjectId to remove")

            if st.button("Find Patient"):
                try:
                    patient_oid = ObjectId(patient_id)
                    patient_doc = users_col.find_one({"_id": patient_oid, "role": "patient"})
                    if patient_doc:
                        st.session_state.found_patient = patient_doc  
                        st.success(f"Found patient: {patient_doc.get('name','Unknown')}")
                    else:
                        st.error("Patient not found.")
                except Exception:
                    st.error("Invalid ObjectId format.")

            if "found_patient" in st.session_state:
                patient_doc = st.session_state.found_patient
                st.markdown("### 🔑 Admin Verification")
                admin_user = st.text_input("Admin Username", key="remove_patient_user")
                admin_pass = st.text_input("Admin Password", type="password", key="remove_patient_pass")

                if st.button("Confirm Remove Patient"):
                    if admin_user == "admin" and admin_pass == "admin123":
                        result = users_col.delete_one({"_id": patient_doc["_id"], "role": "patient"})
                        if result.deleted_count > 0:
                            st.success(f"Patient {patient_doc.get('name')} removed successfully.")
                            del st.session_state.found_patient 
                            st.rerun()
                        else:
                            st.error("Patient not found.")
                    else:
                        st.error("Invalid admin credentials.")

        with st.expander("❌ Remove Doctor"):
            doctor_id = st.text_input("Enter Doctor ObjectId to remove")

            if st.button("Find Doctor"):
                try:
                    doctor_oid = ObjectId(doctor_id)
                    doctor_doc = users_col.find_one({"_id": doctor_oid, "role": "doctor"})
                    if doctor_doc:
                        st.session_state.found_doctor = doctor_doc  
                        st.success(f"Found doctor: {doctor_doc.get('name','Unknown')}")
                    else:
                        st.error("Doctor not found.")
                except Exception:
                    st.error("Invalid ObjectId format.")

            if "found_doctor" in st.session_state:
                doctor_doc = st.session_state.found_doctor
                st.markdown("### 🔑 Admin Verification")
                admin_user = st.text_input("Admin Username", key="remove_doctor_user")
                admin_pass = st.text_input("Admin Password", type="password", key="remove_doctor_pass")

                if st.button("Confirm Remove Doctor"):
                    if admin_user == "admin" and admin_pass == "admin123":
                        result = users_col.delete_one({"_id": doctor_doc["_id"], "role": "doctor"})
                        if result.deleted_count > 0:
                            st.success(f"Doctor {doctor_doc.get('name')} removed successfully.")
                            del st.session_state.found_doctor   
                            st.rerun()
                        else:
                            st.error("Doctor not found.")
                    else:
                        st.error("Invalid admin credentials.")

def show_doctor_dashboard(user):
    st.header(f"👨‍⚕️ Welcome Dr. {user.get('name','Unknown')}")

    st.subheader("📜 Your Past Prescriptions")
    past_prescriptions = list(prescriptions_col.find({"doctor_id": user["_id"]}))

    if past_prescriptions:
        for i, p in enumerate(past_prescriptions, start=1):
            patient_doc = users_col.find_one({"_id": p["patient_id"]})
            patient_name = patient_doc.get("name", "Unknown") if patient_doc else "Unknown"

            st.markdown(f"""
            <div style="
                border: 2px solid #0084ff;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                background-color: #f9f9f9;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
            ">
                <h4 style="color:#0084ff;">Prescription #{i}</h4>
                <p><b>Patient:</b> {patient_name}</p>
                <p><b>Medication:</b> {p['medication']}</p>
                <p><b>Dosage:</b> {p['dosage']}</p>
                <p><b>Instructions:</b> {p['instructions']}</p>
                <p><b>Date:</b> {p['date']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No prescriptions created yet.")
    
    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
                color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)

        st.header("⚙️ Doctor Actions")

        with st.expander("📩 Respond to Patients"):
            st.write("Here you will see patient messages (future feature).")
            if st.button("Open Patient Inbox"):
                st.session_state.page = "doctor_inbox"
                st.rerun()
        with st.expander("🚪 Back to Login/Signup"):
            st.write("Here you can go back to start.")
            if st.button("Logout"):
                st.session_state.user = None
                st.session_state.logged_in = False   
                st.session_state.page = "auth"
                st.rerun()
        st.markdown("""
            <style>
            /* Sidebar background */
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
            }

            /* Sidebar headers and labels */
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p {
                color: #ffffff !important;
            }

            /* Inputs inside sidebar */
            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea,
            [data-testid="stSidebar"] select {
                background-color: #ffffff !important;
                color: #000000 !important;
                border-radius: 6px;
                padding: 6px;
            }

            /* Buttons inside sidebar */
            [data-testid="stSidebar"] button {
                background-color: #0084ff !important;
                color: #ffffff !important;
                border-radius: 6px;
                padding: 6px 12px;
            }
            </style>
        """, unsafe_allow_html=True)
        with st.expander("💊 Create Medication"):
            contacted_patients = list(messages_col.aggregate([
                {"$match": {"receiver": user["_id"]}},
                {"$group": {"_id": "$sender"}}
            ]))

            patient_options = []
            for p in contacted_patients:
                patient_doc = users_col.find_one({"_id": p["_id"], "role": "patient"})
                if patient_doc:
                    patient_options.append((patient_doc["_id"], patient_doc.get("name", "Unknown")))

            if patient_options:
                patient_choice = st.selectbox(
                    "Select Patient",
                    options=patient_options,
                    format_func=lambda x: x[1]  
                )

                med_name = st.text_input("Medication Name")
                dosage = st.text_input("Dosage")
                instructions = st.text_area("Instructions")

                if st.button("Prescribe"):
                    prescription = {
                        "doctor_id": user["_id"],
                        "patient_id": patient_choice[0],
                        "medication": med_name,
                        "dosage": dosage,
                        "instructions": instructions,
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    prescriptions_col.insert_one(prescription)
                    st.success(f"Prescription for {patient_choice[1]} saved successfully!")

            else:
                st.info("No patients have contacted you yet.")

def show_contact_doctor(user):
    st.header("📞 Contact a Doctor")

    doctors = list(users_col.find({"role": "doctor"})) 
    if not doctors:
        st.info("No doctors available.")
        return

    for doc in doctors:
        rating = random.randint(3, 5)
        if st.button(f"👨‍⚕️ {doc.get('name','Doctor')} ⭐ {rating}/5"):
            st.session_state.selected_doctor = doc["_id"] 
            st.session_state.page = "patient_chat"
            st.rerun()

def show_patient_chat(user):
    doctor_id = st.session_state.get("selected_doctor")
    doctor = users_col.find_one({"_id": doctor_id, "role": "doctor"})
    if not doctor:
        st.error("Doctor not found.")
        return

    st.markdown(f"<div class='chat-header'>💬 Chat with Dr. {doctor.get('name','Unknown')}</div>", unsafe_allow_html=True)

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    messages_col.update_many(
        {"receiver": user["_id"], "status": {"$ne": "seen"}},
        {"$set": {"status": "seen"}}
    )

    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

    msgs = list(messages_col.find({
        "$or": [
            {"sender": user["_id"], "receiver": doctor["_id"]},
            {"sender": doctor["_id"], "receiver": user["_id"]}
        ]
    }).sort("timestamp", 1))

    for msg in msgs:
        ts = msg["timestamp"].strftime("%H:%M")
        status = msg.get("status", "sent")
        status_label = "✓ Sent" if status == "sent" else "✓✓ Delivered" if status == "delivered" else "✓✓ Seen"

        if msg["sender"] == user["_id"]:
            components.html(f"""
                <div style='display: flex; align-items: flex-end; gap: 8px; margin-bottom: 10px;'>
                    <div style='width: 32px; height: 32px; border-radius: 50%; background: #ccc; display: flex; align-items: center; justify-content: center;'>👤</div>
                    <div>
                        <div style='background: #fff; color: #111; padding: 10px 14px; border-radius: 18px 18px 18px 4px; max-width: 400px; font-size: 15px; line-height: 1.4; display: inline-block; word-break: break-word;'>{msg['content']}</div>
                        <div style='font-size: 11px; color: #666; margin-top: 4px; text-align: right;'>{ts} • {status_label}</div>
                    </div>
                </div>
            """, height=80)

        else:
            components.html(f"""
                <div style='display: flex; align-items: flex-end; gap: 8px; justify-content: flex-end; margin-bottom: 10px;'>
                    <div>
                        <div style='background: #0084ff; color: #fff; padding: 10px 14px; border-radius: 18px 18px 4px 18px; max-width: 400px; font-size: 15px; line-height: 1.4; display: inline-block; word-break: break-word;'>{msg['content']}</div>
                        <div style='font-size: 11px; color: #ccc; margin-top: 4px; text-align: right;'>{ts} • {status_label}</div>
                    </div>
                    <div style='width: 32px; height: 32px; border-radius: 50%; background: #ccc; display: flex; align-items: center; justify-content: center;'>👨‍⚕️</div>
                </div>
            """, height=80)

    components.html("<div id='scroll-anchor'></div><script>document.getElementById('scroll-anchor').scrollIntoView({behavior: 'smooth'});</script>", height=0)

    st.markdown("</div>", unsafe_allow_html=True)

    emoji = st.selectbox("😊 Emoji", ["", "😀", "😢", "❤️", "👍", "👨‍⚕️", "💊", "🤒", "🧠", "🫀"], index=0)
    user_input = st.chat_input("Type your message...")

    if user_input:
        final_message = f"{user_input} {emoji}".strip()
        messages_col.insert_one({
            "sender": user["_id"],
            "receiver": doctor["_id"],
            "content": final_message,
            "timestamp": datetime.now(),
            "status": "sent"
        })
        st.rerun()

def show_doctor_inbox(user):
    st.header("📩 Patient Messages")

    pipeline = [
        {"$match": {"receiver": user["_id"]}},   
        {"$group": {"_id": "$sender", "count": {"$sum": 1}}}
    ]
    patients = list(messages_col.aggregate(pipeline))

    for p in patients:
        patient_id = p["_id"]
        count = p["count"]

        patient_doc = users_col.find_one({"_id": patient_id, "role": "patient"})
        patient_name = patient_doc.get("name", "Unknown Patient") if patient_doc else str(patient_id)

        if st.button(f"👤 {patient_name} ({count} messages)"):
            st.session_state.selected_patient = patient_id
            st.session_state.page = "doctor_chat"
            st.rerun()

def show_doctor_chat(user):
    patient_id = st.session_state.get("selected_patient")
    patient = users_col.find_one({"_id": patient_id, "role": "patient"})
    if not patient:
        st.error("Patient not found.")
        return

    st.markdown(f"<div class='chat-header'>💬 Chat with {patient.get('name','Unknown Patient')}</div>", unsafe_allow_html=True)

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    messages_col.update_many(
        {"receiver": user["_id"], "status": {"$ne": "seen"}},
        {"$set": {"status": "seen"}}
    )

    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)

    msgs = list(messages_col.find({
        "$or": [
            {"sender": patient["_id"], "receiver": user["_id"]},
            {"sender": user["_id"], "receiver": patient["_id"]}
        ]
    }).sort("timestamp", 1))

    for msg in msgs:
        ts = msg["timestamp"].strftime("%H:%M")
        status = msg.get("status", "sent")
        status_label = "✓ Sent" if status == "sent" else "✓✓ Delivered" if status == "delivered" else "✓✓ Seen"

        if msg["sender"] == patient["_id"]:
            components.html(f"""
                <div style='display: flex; align-items: flex-end; gap: 8px; margin-bottom: 10px;'>
                    <div style='width: 32px; height: 32px; border-radius: 50%; background: #ccc; display: flex; align-items: center; justify-content: center;'>👤</div>
                    <div>
                        <div style='background: #fff; color: #111; padding: 10px 14px; border-radius: 18px 18px 18px 4px; max-width: 400px; font-size: 15px; line-height: 1.4; display: inline-block; word-break: break-word;'>{msg['content']}</div>
                        <div style='font-size: 11px; color: #666; margin-top: 4px; text-align: right;'>{ts} • {status_label}</div>
                    </div>
                </div>
            """, height=80)

        else:
            components.html(f"""
                <div style='display: flex; align-items: flex-end; gap: 8px; justify-content: flex-end; margin-bottom: 10px;'>
                    <div>
                        <div style='background: #0084ff; color: #fff; padding: 10px 14px; border-radius: 18px 18px 4px 18px; max-width: 400px; font-size: 15px; line-height: 1.4; display: inline-block; word-break: break-word;'>{msg['content']}</div>
                        <div style='font-size: 11px; color: #ccc; margin-top: 4px; text-align: right;'>{ts} • {status_label}</div>
                    </div>
                    <div style='width: 32px; height: 32px; border-radius: 50%; background: #ccc; display: flex; align-items: center; justify-content: center;'>👨‍⚕️</div>
                </div>
            """, height=80)

    components.html("<div id='scroll-anchor'></div><script>document.getElementById('scroll-anchor').scrollIntoView({behavior: 'smooth'});</script>", height=0)

    st.markdown("</div>", unsafe_allow_html=True)

    emoji = st.selectbox("😊 Emoji", ["", "😀", "😢", "❤️", "👍", "👨‍⚕️", "💊", "🤒", "🧠", "🫀"], index=0)
    reply = st.chat_input("Type your response...")
    if reply:
        final_message = f"{reply} {emoji}".strip()
        messages_col.insert_one({
            "sender": user["_id"],
            "receiver": patient["_id"],
            "content": final_message,
            "timestamp": datetime.now(),
            "status": "sent"
        })
        st.rerun()

def show_calorie_predictor():
    st.markdown("""
        <style>
        .welcome-banner {
            padding: 20px;
            border-radius: 12px;
            background: rgba(0,0,0,0.6); /* semi-transparent overlay */
            color: #fff;
            margin-bottom: 20px;
            animation: fadeIn 0.8s ease-in-out;
        }
        .section-box {
            margin-top: 20px;
            padding: 20px;
            border-radius: 10px;
            background: rgba(255,255,255,0.1); /* translucent card */
            border-left: 6px solid #ffcc00;
            color: #fff;
            animation: fadeIn 0.6s ease-in-out;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🧮 Calorie Recommendation")

    with st.form("calorie_form"):
        weight_choice = st.selectbox("Weight category", [1, 2, 3, 4], format_func=lambda x: ["Underweight (<50kg)", "Normal (50–75kg)", "Overweight (75–90kg)", "Obese (>90kg)"][x-1])
        height_choice = st.selectbox("Height category", [1, 2, 3], format_func=lambda x: ["Short (<1.60m)", "Medium (1.60–1.75m)", "Tall (>1.75m)"][x-1])
        activity_choice = st.selectbox("Activity level", [1, 2, 3, 4, 5], format_func=lambda x: ["Sedentary", "Light", "Moderate", "Very", "Super"][x-1])
        gender = st.radio("Gender", ["M", "F"])
        age = st.number_input("Age in years", min_value=10, max_value=100, step=1)

        submitted = st.form_submit_button("🔍 Get Recommendation")

    if submitted:
        result = predict_calories(weight_choice, height_choice, activity_choice, gender, age)

        st.markdown(f"""
            <div class="calorie-box">
                <h4>📊 Your Personalized Calorie Plan</h4>
                <p><strong>BMI:</strong> {result['BMI']} — {result['bmi_status']}</p>
                <p><strong>Maintenance Calories:</strong> {result['maintenance']} kcal</p>
                <p><strong>To Lose Weight:</strong> {result['loss']} kcal</p>
                <p><strong>To Gain Weight:</strong> {result['gain']} kcal</p>
            </div>
        """, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
                color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)
        st.header("⚙️ Actions")
        st.markdown("Use the tools below to explore Medora's features:")
        
        with st.expander("🚪 Logout"):
            st.write("Log out of your Medora account and return to the login screen.")
            if st.button("Confirm Logout"):
                st.session_state.user = None
                st.session_state.logged_in = False   
                st.session_state.page = "auth"
                st.rerun()

        with st.expander("➕ Add Health Record"):
            st.write("Record your latest health metrics like weight, height, blood pressure, and heart rate.")
            if st.button("Open Health Record Form"):
                st.session_state.page = "add_record"
                st.rerun()

        with st.expander("💬 Chat with AI Assistant"):
            st.write("Ask Medora anything medical or health-related. Get instant AI-powered answers.")
            if st.button("Start Chat", key="chat_button"):
                st.session_state.page = "chat"
                show_chat_screen(user)
                st.rerun()

        with st.expander("🤗 Relieve Loneliness"):
            st.write("Talk to Medora’s companion chat for emotional support and friendly conversation.")
            if st.button("Open Companion Chat", key="loneliness_button"):
                st.session_state.page = "companion"
                st.rerun()

        with st.expander("🧮 Calorie Recommendation"):
            st.write("Get personalized calorie recommendations based on your body type and activity level.")
            if st.button("Open Calorie Predictor"):
                st.session_state.page = "calorie_predictor"
                st.rerun()

        with st.expander("🧠 Lifestyle Assessment"):
            st.write("Analyze your lifestyle habits and receive tailored health improvement suggestions.")
            if st.button("Open Lifestyle Predictor"):
                st.session_state.page = "lifestyle_predictor"
                st.rerun()

        with st.expander("🧠🧠 Stress Assessment"):
            st.write("Evaluate your stress level based on sleep, blood pressure, and emotional state.")
            if st.button("Open Stress Predictor"):
                st.session_state.page = "stress_predictor"
                st.rerun()

        with st.expander("❤️ Heart Risk Assessment"):
            st.write("Assess your risk of heart disease using clinical indicators and lifestyle factors.")
            if st.button("Open Heart Predictor"):
                st.session_state.page = "heart_predictor"
                st.rerun()

        with st.expander("🧬 Genetic Test Predictor"):
            st.write("Predict your need for genetic testing based on family history and environmental risks.")
            if st.button("Open Genetic Test Predictor"):
                st.session_state.page = "genetic_test_predictor"
                st.rerun()

        with st.expander("📁 Add Medical Health Record"):
            st.write("Upload medical documents like prescriptions, lab reports, or diagnostic files.")
            if st.button("Open Medical Record Upload"):
                st.session_state.page = "add_medrecord"
                st.rerun()

        with st.expander("📞 Contact Doctor"):
            st.write("Send a message to your doctor for advice, follow-up, or medication requests.")
            if st.button("Open Contact Form"):
                st.session_state.page = "contact_doctor"
                st.rerun()

def show_genetic_test_predictor():
    st.markdown("""
        <style>
        .prediction-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f9ff;
            border-left: 6px solid #1f77b4;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🧬 Genetic Test Recommendation")

    with st.form("genetic_test_form"):
        age = st.number_input("Age", min_value=1, max_value=120)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        parental_history = st.radio("Parental History of Disease", ["Yes", "No"])
        sibling_history = st.radio("Sibling History of Disease", ["Yes", "No"])
        num_relatives = st.number_input("Number of Relatives with Disease", min_value=0, max_value=10)
        known_mutation = st.radio("Known Genetic Mutation in Family", ["Yes", "No"])
        early_onset = st.radio("Early Onset Cases in Family", ["Yes", "No"])
        env_risk = st.selectbox("Environmental Risk Exposure", ["Low", "Moderate", "High"])

        submitted = st.form_submit_button("🔍 Predict Genetic Test Need")

    if submitted:
        user_input = {
            'Age': age,
            'Gender': gender,
            'Parental History': parental_history,
            'Sibling History': sibling_history,
            'Number of Relatives with Disease': num_relatives,
            'Known Genetic Mutation': known_mutation,
            'Early Onset Cases in Family': early_onset,
            'Environmental Risk Exposure': env_risk
        }
        result = predict_genetic_test(user_input)

        st.markdown(f"""
            <div class="prediction-box">
                <h4>📊 Prediction Result</h4>
                <p><strong>{result}</strong></p>
            </div>
        """, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
                color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)

        st.header("⚙️ Actions")
        st.markdown("Use the tools below to explore Medora's features:")
        
        with st.expander("🚪 Logout"):
            st.write("Log out of your Medora account and return to the login screen.")
            if st.button("Confirm Logout"):
                st.session_state.user = None
                st.session_state.logged_in = False   
                st.session_state.page = "auth"
                st.rerun()

        with st.expander("➕ Add Health Record"):
            st.write("Record your latest health metrics like weight, height, blood pressure, and heart rate.")
            if st.button("Open Health Record Form"):
                st.session_state.page = "add_record"
                st.rerun()

        with st.expander("💬 Chat with AI Assistant"):
            st.write("Ask Medora anything medical or health-related. Get instant AI-powered answers.")
            if st.button("Start Chat", key="chat_button"):
                st.session_state.page = "chat"
                show_chat_screen(user)
                st.rerun()

        with st.expander("🤗 Relieve Loneliness"):
            st.write("Talk to Medora’s companion chat for emotional support and friendly conversation.")
            if st.button("Open Companion Chat", key="loneliness_button"):
                st.session_state.page = "companion"
                st.rerun()

        with st.expander("🧮 Calorie Recommendation"):
            st.write("Get personalized calorie recommendations based on your body type and activity level.")
            if st.button("Open Calorie Predictor"):
                st.session_state.page = "calorie_predictor"
                st.rerun()

        with st.expander("🧠 Lifestyle Assessment"):
            st.write("Analyze your lifestyle habits and receive tailored health improvement suggestions.")
            if st.button("Open Lifestyle Predictor"):
                st.session_state.page = "lifestyle_predictor"
                st.rerun()

        with st.expander("🧠🧠 Stress Assessment"):
            st.write("Evaluate your stress level based on sleep, blood pressure, and emotional state.")
            if st.button("Open Stress Predictor"):
                st.session_state.page = "stress_predictor"
                st.rerun()

        with st.expander("❤️ Heart Risk Assessment"):
            st.write("Assess your risk of heart disease using clinical indicators and lifestyle factors.")
            if st.button("Open Heart Predictor"):
                st.session_state.page = "heart_predictor"
                st.rerun()

        with st.expander("🧬 Genetic Test Predictor"):
            st.write("Predict your need for genetic testing based on family history and environmental risks.")
            if st.button("Open Genetic Test Predictor"):
                st.session_state.page = "genetic_test_predictor"
                st.rerun()

        with st.expander("📁 Add Medical Health Record"):
            st.write("Upload medical documents like prescriptions, lab reports, or diagnostic files.")
            if st.button("Open Medical Record Upload"):
                st.session_state.page = "add_medrecord"
                st.rerun()

        with st.expander("📞 Contact Doctor"):
            st.write("Send a message to your doctor for advice, follow-up, or medication requests.")
            if st.button("Open Contact Form"):
                st.session_state.page = "contact_doctor"
                st.rerun()
        

def show_heart_predictor():
    st.markdown("""
        <style>
        .heart-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #fff0f5;
            border-left: 6px solid #e63946;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("❤️ Heart Disease Risk Assessment")

    with st.form("heart_form"):
        age = st.number_input("Age", min_value=1, max_value=120, step=1)
        sex = st.radio("Sex", ["M", "F"])
        chest_pain = st.selectbox("Chest Pain Type", ["ATA", "NAP", "ASY", "TA"])
        resting_bp = st.number_input("Resting Blood Pressure", min_value=80, max_value=200)
        cholesterol = st.number_input("Cholesterol", min_value=100, max_value=600)
        fasting_bs = st.radio("Fasting Blood Sugar", [0, 1])
        resting_ecg = st.selectbox("Resting ECG", ["Normal", "ST", "LVH"])
        max_hr = st.number_input("Max Heart Rate", min_value=60, max_value=220)
        exercise_angina = st.radio("Exercise-Induced Angina", ["Y", "N"])
        oldpeak = st.number_input("Oldpeak (ST depression)", min_value=0.0, max_value=6.0, step=0.1)
        st_slope = st.selectbox("ST Slope", ["Up", "Flat", "Down"])

        submitted = st.form_submit_button("🔍 Predict Heart Risk")

    if submitted:
        user_input = {
            'Age': age,
            'Sex': sex,
            'ChestPainType': chest_pain,
            'RestingBP': resting_bp,
            'Cholesterol': cholesterol,
            'FastingBS': fasting_bs,
            'RestingECG': resting_ecg,
            'MaxHR': max_hr,
            'ExerciseAngina': exercise_angina,
            'Oldpeak': oldpeak,
            'ST_Slope': st_slope
        }
        result = predict_heart_disease(user_input)

        st.markdown(f"""
            <div class="heart-box">
                <h4>📊 Prediction Result</h4>
                <p><strong>Risk Level:</strong> {result}</p>
            </div>
        """, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
                color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)

        st.header("⚙️ Actions")
        st.markdown("Use the tools below to explore Medora's features:")
        
        with st.expander("🚪 Logout"):
            st.write("Log out of your Medora account and return to the login screen.")
            if st.button("Confirm Logout"):
                st.session_state.user = None
                st.session_state.logged_in = False   
                st.session_state.page = "auth"
                st.rerun()

        with st.expander("➕ Add Health Record"):
            st.write("Record your latest health metrics like weight, height, blood pressure, and heart rate.")
            if st.button("Open Health Record Form"):
                st.session_state.page = "add_record"
                st.rerun()

        with st.expander("💬 Chat with AI Assistant"):
            st.write("Ask Medora anything medical or health-related. Get instant AI-powered answers.")
            if st.button("Start Chat", key="chat_button"):
                st.session_state.page = "chat"
                show_chat_screen(user)
                st.rerun()

        with st.expander("🤗 Relieve Loneliness"):
            st.write("Talk to Medora’s companion chat for emotional support and friendly conversation.")
            if st.button("Open Companion Chat", key="loneliness_button"):
                st.session_state.page = "companion"
                st.rerun()

        with st.expander("🧮 Calorie Recommendation"):
            st.write("Get personalized calorie recommendations based on your body type and activity level.")
            if st.button("Open Calorie Predictor"):
                st.session_state.page = "calorie_predictor"
                st.rerun()

        with st.expander("🧠 Lifestyle Assessment"):
            st.write("Analyze your lifestyle habits and receive tailored health improvement suggestions.")
            if st.button("Open Lifestyle Predictor"):
                st.session_state.page = "lifestyle_predictor"
                st.rerun()

        with st.expander("🧠🧠 Stress Assessment"):
            st.write("Evaluate your stress level based on sleep, blood pressure, and emotional state.")
            if st.button("Open Stress Predictor"):
                st.session_state.page = "stress_predictor"
                st.rerun()

        with st.expander("❤️ Heart Risk Assessment"):
            st.write("Assess your risk of heart disease using clinical indicators and lifestyle factors.")
            if st.button("Open Heart Predictor"):
                st.session_state.page = "heart_predictor"
                st.rerun()

        with st.expander("🧬 Genetic Test Predictor"):
            st.write("Predict your need for genetic testing based on family history and environmental risks.")
            if st.button("Open Genetic Test Predictor"):
                st.session_state.page = "genetic_test_predictor"
                st.rerun()

        with st.expander("📁 Add Medical Health Record"):
            st.write("Upload medical documents like prescriptions, lab reports, or diagnostic files.")
            if st.button("Open Medical Record Upload"):
                st.session_state.page = "add_medrecord"
                st.rerun()

        with st.expander("📞 Contact Doctor"):
            st.write("Send a message to your doctor for advice, follow-up, or medication requests.")
            if st.button("Open Contact Form"):
                st.session_state.page = "contact_doctor"
                st.rerun()


def show_lifestyle_predictor():
    st.markdown("""
        <style>
        .lifestyle-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #f0fff4;
            border-left: 6px solid #2ecc71;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        .lifestyle-box ul {
            padding-left: 20px;
            margin-top: 10px;
        }
        .lifestyle-box li {
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🧠 Lifestyle Assessment")

    with st.form("lifestyle_form"):
        age = st.number_input("Age", min_value=18, max_value=100, step=1)
        gender = st.radio("Gender", ["M", "F"])
        weight = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0)
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, step=0.01)
        activity_level = st.slider("Activity level (1=Sedentary, 5=Very Active)", 1, 5)
        sleep_hours = st.slider("Average sleep hours per day", 3.0, 10.0, step=0.5)
        diet_score = st.slider("Diet score (1=Poor, 4=Excellent)", 1, 4)

        submitted = st.form_submit_button("🔍 Analyze Lifestyle")

    if submitted:
        result = predict_lifestyle(age, gender, weight, height, activity_level, sleep_hours, diet_score)

        recommendations_html = ""
        if result["recommendations"]:
            recommendations_html += "<ul>"
            for rec in result["recommendations"]:
                recommendations_html += f"<li>{rec}</li>"
            recommendations_html += "</ul>"
        else:
            recommendations_html = "<p>✅ No major issues detected. Maintain your current lifestyle.</p>"

        st.markdown(f"""
            <div class="lifestyle-box">
                <h4>📋 Personalized Recommendations</h4>
                {recommendations_html}
                <p style='margin-top:10px; font-size: 0.9em; color: #555;'>Prediction Probabilities: {np.round(result['probabilities'], 2)}</p>
            </div>
        """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
                color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)

        st.header("⚙️ Actions")
        st.markdown("Use the tools below to explore Medora's features:")
        
        with st.expander("🚪 Logout"):
            st.write("Log out of your Medora account and return to the login screen.")
            if st.button("Confirm Logout"):
                st.session_state.user = None
                st.session_state.logged_in = False   
                st.session_state.page = "auth"
                st.rerun()

        with st.expander("➕ Add Health Record"):
            st.write("Record your latest health metrics like weight, height, blood pressure, and heart rate.")
            if st.button("Open Health Record Form"):
                st.session_state.page = "add_record"
                st.rerun()

        with st.expander("💬 Chat with AI Assistant"):
            st.write("Ask Medora anything medical or health-related. Get instant AI-powered answers.")
            if st.button("Start Chat", key="chat_button"):
                st.session_state.page = "chat"
                show_chat_screen(user)
                st.rerun()

        with st.expander("🤗 Relieve Loneliness"):
            st.write("Talk to Medora’s companion chat for emotional support and friendly conversation.")
            if st.button("Open Companion Chat", key="loneliness_button"):
                st.session_state.page = "companion"
                st.rerun()

        with st.expander("🧮 Calorie Recommendation"):
            st.write("Get personalized calorie recommendations based on your body type and activity level.")
            if st.button("Open Calorie Predictor"):
                st.session_state.page = "calorie_predictor"
                st.rerun()

        with st.expander("🧠 Lifestyle Assessment"):
            st.write("Analyze your lifestyle habits and receive tailored health improvement suggestions.")
            if st.button("Open Lifestyle Predictor"):
                st.session_state.page = "lifestyle_predictor"
                st.rerun()

        with st.expander("🧠🧠 Stress Assessment"):
            st.write("Evaluate your stress level based on sleep, blood pressure, and emotional state.")
            if st.button("Open Stress Predictor"):
                st.session_state.page = "stress_predictor"
                st.rerun()

        with st.expander("❤️ Heart Risk Assessment"):
            st.write("Assess your risk of heart disease using clinical indicators and lifestyle factors.")
            if st.button("Open Heart Predictor"):
                st.session_state.page = "heart_predictor"
                st.rerun()

        with st.expander("🧬 Genetic Test Predictor"):
            st.write("Predict your need for genetic testing based on family history and environmental risks.")
            if st.button("Open Genetic Test Predictor"):
                st.session_state.page = "genetic_test_predictor"
                st.rerun()

        with st.expander("📁 Add Medical Health Record"):
            st.write("Upload medical documents like prescriptions, lab reports, or diagnostic files.")
            if st.button("Open Medical Record Upload"):
                st.session_state.page = "add_medrecord"
                st.rerun()

        with st.expander("📞 Contact Doctor"):
            st.write("Send a message to your doctor for advice, follow-up, or medication requests.")
            if st.button("Open Contact Form"):
                st.session_state.page = "contact_doctor"
                st.rerun()

def show_stress_predictor():
    st.markdown("""
        <style>
        .stress-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #f5faff;
            border-left: 6px solid #3498db;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("🧠🧠 Stress Level Assessment")

    with st.form("stress_form"):
        self_esteem = st.selectbox("Self-esteem level", ["low", "mild", "severe"])
        blood_pressure = st.radio("Blood pressure", ["low", "normal", "high"])
        sleep_quality = st.selectbox("Sleep quality", ["poor", "fair", "average", "good", "excellent"])
        bullying = st.selectbox("Frustration level", ["none", "mild", "moderate", "severe", "extreme"])

        submitted = st.form_submit_button("🔍 Predict Stress Level")

    if submitted:
        result = predict_stress(self_esteem, blood_pressure, sleep_quality, bullying)

        st.markdown(f"""
            <div class="stress-box">
                <h4>📊 Stress Prediction</h4>
                <p><strong>Stress Level:</strong> {result['level']}</p>
                <p>{result['message']}</p>
            </div>
        """, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown("""
            <style>
            [data-testid="stSidebar"] {
                background: rgba(0,0,0,0.6);
                color: #fff;
            }
            </style>
        """, unsafe_allow_html=True)

        st.header("⚙️ Actions")
        st.markdown("Use the tools below to explore Medora's features:")
        
        with st.expander("🚪 Logout"):
            st.write("Log out of your Medora account and return to the login screen.")
            if st.button("Confirm Logout"):
                st.session_state.user = None
                st.session_state.logged_in = False   
                st.session_state.page = "auth"
                st.rerun()

        with st.expander("➕ Add Health Record"):
            st.write("Record your latest health metrics like weight, height, blood pressure, and heart rate.")
            if st.button("Open Health Record Form"):
                st.session_state.page = "add_record"
                st.rerun()

        with st.expander("💬 Chat with AI Assistant"):
            st.write("Ask Medora anything medical or health-related. Get instant AI-powered answers.")
            if st.button("Start Chat", key="chat_button"):
                st.session_state.page = "chat"
                show_chat_screen(user)
                st.rerun()

        with st.expander("🤗 Relieve Loneliness"):
            st.write("Talk to Medora’s companion chat for emotional support and friendly conversation.")
            if st.button("Open Companion Chat", key="loneliness_button"):
                st.session_state.page = "companion"
                st.rerun()

        with st.expander("🧮 Calorie Recommendation"):
            st.write("Get personalized calorie recommendations based on your body type and activity level.")
            if st.button("Open Calorie Predictor"):
                st.session_state.page = "calorie_predictor"
                st.rerun()

        with st.expander("🧠 Lifestyle Assessment"):
            st.write("Analyze your lifestyle habits and receive tailored health improvement suggestions.")
            if st.button("Open Lifestyle Predictor"):
                st.session_state.page = "lifestyle_predictor"
                st.rerun()

        with st.expander("🧠🧠 Stress Assessment"):
            st.write("Evaluate your stress level based on sleep, blood pressure, and emotional state.")
            if st.button("Open Stress Predictor"):
                st.session_state.page = "stress_predictor"
                st.rerun()

        with st.expander("❤️ Heart Risk Assessment"):
            st.write("Assess your risk of heart disease using clinical indicators and lifestyle factors.")
            if st.button("Open Heart Predictor"):
                st.session_state.page = "heart_predictor"
                st.rerun()

        with st.expander("🧬 Genetic Test Predictor"):
            st.write("Predict your need for genetic testing based on family history and environmental risks.")
            if st.button("Open Genetic Test Predictor"):
                st.session_state.page = "genetic_test_predictor"
                st.rerun()

        with st.expander("📁 Add Medical Health Record"):
            st.write("Upload medical documents like prescriptions, lab reports, or diagnostic files.")
            if st.button("Open Medical Record Upload"):
                st.session_state.page = "add_medrecord"
                st.rerun()

        with st.expander("📞 Contact Doctor"):
            st.write("Send a message to your doctor for advice, follow-up, or medication requests.")
            if st.button("Open Contact Form"):
                st.session_state.page = "contact_doctor"
                st.rerun()

def show_add_record_form(user):
    st.markdown("""
        <style>
        .record-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f7ff;
            border-left: 6px solid #1e90ff;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='padding: 20px; background: linear-gradient(90deg, #1e90ff, #00bfff); color: white; border-radius: 10px; margin-bottom: 20px;'>
            <h2>📝 Add Health Record</h2>
            <p>Fill in your latest health metrics below</p>
        </div>
    """, unsafe_allow_html=True)

    form = st.form("add_record_form")
    weight = form.number_input("Weight (kg)", min_value=0.0)
    height = form.number_input("Height (m)", min_value=0.0)
    bp = form.text_input("Blood Pressure")
    hr = form.number_input("Heart Rate (bpm)", min_value=0)
    submitted = form.form_submit_button("💾 Save Record")

    if submitted:
        record = HealthRecord(gen_id("r_"), datetime.now(), weight, height, bp, hr)
        records_col.insert_one({
            "record_id": record.record_id,
            "patient_id": user["user_id"],
            "timestamp": str(record.timestamp),
            "weight_kg": weight,
            "height_m": height,
            "blood_pressure": bp,
            "heart_rate": hr
        })

        st.markdown(f"""
            <div class="record-box">
                <h4>✅ Record Saved Successfully</h4>
                <p><strong>Record ID:</strong> {record.record_id}</p>
                <p><strong>Timestamp:</strong> {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Weight:</strong> {weight} kg</p>
                <p><strong>Height:</strong> {height} m</p>
                <p><strong>Blood Pressure:</strong> {bp}</p>
                <p><strong>Heart Rate:</strong> {hr} bpm</p>
            </div>
        """, unsafe_allow_html=True)
    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

def show_chat_screen(user):
    #Transformers
    st.title("💬 Chat with AI Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Ask Medora anything medical...")
    if user_input:
        st.chat_message("user").write(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        response = get_medora_response(user_input, st.session_state.chat_history)
        st.chat_message("assistant").write(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    elif st.button("🚪 Back to Dashboard", key="companion_logout"):
        st.session_state.page = "dashboard"
        st.rerun()

    #DataSet
    # st.subheader("💬 Chat with AI Assistant")

    # if "chat_history" not in st.session_state:
    #     st.session_state.chat_history = []

    # for msg in st.session_state.chat_history:
    #     st.chat_message(msg["role"]).write(msg["content"])

    # user_input = st.chat_input("Ask Medora a medical question...")
    # if user_input:
    #     st.chat_message("user").write(user_input)
    #     response = chatbot.get_response(user_input) or "I'm not sure how to help with that."
    #     st.chat_message("assistant").write(response)
    #     st.session_state.chat_history.append({"role": "user", "content": user_input})
    #     st.session_state.chat_history.append({"role": "assistant", "content": response})
def show_add_medical_record(user):
    st.markdown("""
        <style>
        .doc-box {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
            background-color: #fffaf0;
            border-left: 6px solid #ffb347;
            animation: fadeIn 0.8s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='padding: 20px; background: linear-gradient(90deg, #ffb347, #ffcc80); color: black; border-radius: 10px; margin-bottom: 20px;'>
            <h2>📁 Add Medical Record</h2>
            <p>Upload a medical document (image or PDF) with a title and source.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("medical_doc_form"):
        title = st.text_input("Document Title")
        source = st.text_input("Source or Description")
        file = st.file_uploader("Upload Image or PDF", type=["png", "jpg", "jpeg", "pdf"])
        submitted = st.form_submit_button("💾 Save Document")

    if submitted:
        if not file:
            st.warning("Please upload a file.")
            return

        file_bytes = file.read()
        file_type = file.type or "application/octet-stream"

        document = MedicalDocument(
            doc_id=gen_id("d_"),
            title=title,
            source=source,
            file_type=file_type,
            file_data=file_bytes,
            timestamp=datetime.now()
        )

        documents_col.insert_one({
            "doc_id": document.doc_id,
            "patient_id": str(user["user_id"]),
            "timestamp": document.timestamp,
            "title": document.title,
            "source": document.source,
            "file_data": file_bytes,
            "file_type": file_type
        })

        st.markdown(f"""
            <div class="doc-box">
                <h4>✅ Document Saved</h4>
                <p><strong>Title:</strong> {title}</p>
                <p><strong>Source:</strong> {source}</p>
                <p><strong>Timestamp:</strong> {document.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Type:</strong> {file_type}</p>
            </div>
        """, unsafe_allow_html=True)

    if st.button("⬅️ Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()