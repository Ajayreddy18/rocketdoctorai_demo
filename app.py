# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import random
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Rocket Doctor AI Demo", layout="wide")
st.title(" Rocket Doctor AI Demo: Remote Patient Monitoring")

patients = [
    {
        "id": 1,
        "name": "John Doe",
        "age": 67,
        "location": "Rural",
        "symptoms": ["cough", "fever", "fatigue"],
        "vitals": {"heart_rate": 70, "SpO2": 98, "temperature": 38.0, "blood_pressure": "130/80"},
        "ai": ""
    },
    {
        "id": 2,
        "name": "Mary Smith",
        "age": 45,
        "location": "Urban",
        "symptoms": ["headache", "dizziness", "nausea"],
        "vitals": {"heart_rate": 90, "SpO2": 95, "temperature": 37.5, "blood_pressure": "120/75"},
        "ai": ""
    },
    {
        "id": 3,
        "name": "Ali Khan",
        "age": 30,
        "location": "Remote",
        "symptoms": ["chest pain", "shortness of breath"],
        "vitals": {"heart_rate": 80, "SpO2": 92, "temperature": 37.8, "blood_pressure": "135/85"},
        "ai": ""
    }
]


if "history" not in st.session_state:
    st.session_state.history = {p["id"]: [] for p in patients}


def ai_triage(symptoms, vitals):
    hr = vitals["heart_rate"]
    spo2 = vitals["SpO2"]
    temp = vitals["temperature"]

    if "chest pain" in symptoms or hr > 100 or spo2 < 90 or temp > 39:
        return "ER alert; urgent intervention needed"
    elif "cough" in symptoms or temp >= 38:
        return "Virtual consult today; monitor at home"
    else:
        return "Home care; follow-up in 24h"


def update_vitals(patients_list):
    for p in patients_list:
        p["vitals"]["heart_rate"] = random.randint(60, 110)
        p["vitals"]["SpO2"] = random.randint(88, 100)
        p["vitals"]["temperature"] = round(random.uniform(36.0, 39.0), 1)
        systolic = random.randint(100, 140)
        diastolic = random.randint(60, 90)
        p["vitals"]["blood_pressure"] = f"{systolic}/{diastolic}"


st.sidebar.header("Add New Patient")
with st.sidebar.form("new_patient_form"):
    new_name = st.text_input("Name")
    new_age = st.number_input("Age", min_value=0, max_value=120, value=30)
    new_location = st.selectbox("Location", ["Urban", "Rural", "Remote"])
    new_symptoms = st.text_area("Symptoms (comma-separated)").split(",")

    
    new_hr = st.number_input("Heart Rate (bpm)", min_value=30, max_value=200, value=75)
    new_spo2 = st.number_input("SpO₂ (%)", min_value=50, max_value=100, value=97)
    new_temp = st.number_input("Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0)
    new_bp = st.text_input("Blood Pressure (e.g., 120/80)", value="120/80")

    submitted = st.form_submit_button("Add Patient")
    if submitted:
        new_id = max(p["id"] for p in patients) + 1
        new_patient = {
            "id": new_id,
            "name": new_name,
            "age": new_age,
            "location": new_location,
            "symptoms": [s.strip() for s in new_symptoms],
            "vitals": {
                "heart_rate": new_hr,
                "SpO2": new_spo2,
                "temperature": new_temp,
                "blood_pressure": new_bp
            },
            "ai": ""
        }
        new_patient["ai"] = ai_triage(new_patient["symptoms"], new_patient["vitals"])
        patients.append(new_patient)
        st.session_state.history[new_id] = [{
            "vitals": new_patient["vitals"].copy(),
            "ai": new_patient["ai"],
            "time": pd.Timestamp.now()
        }]
        st.success(f"Patient {new_name} added successfully!")


st.sidebar.header("Simulate Random Patients")
num_sim = st.sidebar.number_input("Number of patients to simulate", min_value=1, max_value=50, value=5)
if st.sidebar.button("Generate Patients"):
    for i in range(num_sim):
        sim_id = max([p["id"] for p in patients]) + 1
        sim_patient = {
            "id": sim_id,
            "name": f"Patient {sim_id}",
            "age": random.randint(18, 90),
            "location": random.choice(["Urban", "Rural", "Remote"]),
            "symptoms": random.choice([["cough"], ["fever"], ["fatigue"], ["headache"], ["chest pain"]]),
            "vitals": {
                "heart_rate": random.randint(60, 110),
                "SpO2": random.randint(88, 100),
                "temperature": round(random.uniform(36.0, 39.0), 1),
                "blood_pressure": f"{random.randint(100,140)}/{random.randint(60,90)}"
            },
            "ai": ""
        }
        sim_patient["ai"] = ai_triage(sim_patient["symptoms"], sim_patient["vitals"])
        patients.append(sim_patient)
        st.session_state.history[sim_id] = [{
            "vitals": sim_patient["vitals"].copy(),
            "ai": sim_patient["ai"],
            "time": pd.Timestamp.now()
        }]
    st.success(f"{num_sim} patients simulated!")


refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 5)
st_autorefresh(interval=refresh_rate * 1000, key="refresh")


update_vitals(patients)
for p in patients:
    p["ai"] = ai_triage(p["symptoms"], p["vitals"])
    st.session_state.history[p["id"]].append({
        "vitals": p["vitals"].copy(),
        "ai": p["ai"],
        "time": pd.Timestamp.now()
    })


df = pd.DataFrame([
    {
        "ID": p["id"],
        "Name": p["name"],
        "Age": p["age"],
        "Location": p["location"],
        "Symptoms": ", ".join(p["symptoms"]),
        "HR": p["vitals"]["heart_rate"],
        "SpO₂": p["vitals"]["SpO2"],
        "Temp": p["vitals"]["temperature"],
        "BP": p["vitals"]["blood_pressure"],
        "AI Recommendation": p["ai"],
        "ER Alert": "Yes" if "ER alert" in p["ai"] else "No",
        "Referral": "Lab / Specialist" if "Virtual consult" in p["ai"] else ""
    }
    for p in patients
])

def color_rec(val):
    if "ER alert" in val:
        return 'background-color: red; color: white; font-weight: bold'
    elif "Virtual consult" in val:
        return 'background-color: yellow; font-weight: bold'
    else:
        return 'background-color: lightgreen; font-weight: bold'

st.dataframe(df.style.applymap(color_rec, subset=["AI Recommendation"]))


patient_id = st.selectbox(
    "Select Patient to View Trends",
    [p["id"] for p in patients],
    key="patient_trend_select"
)
history = st.session_state.history[patient_id]
if history:
    hist_df = pd.DataFrame([{
        "Time": h["time"],
        "HR": h["vitals"]["heart_rate"],
        "SpO₂": h["vitals"]["SpO2"],
        "Temp": h["vitals"]["temperature"]
    } for h in history])
    st.line_chart(hist_df.set_index("Time"))


er_count = sum(1 for p in patients if "ER alert" in p["ai"])
st.metric("Current ER Alerts", er_count)


st.subheader(" Key Features Demo")
st.markdown("""
- **Expanding access to timely care**: Patients from Rural/Remote locations demonstrate access.
- **Supporting continuity through referrals, labs, and follow-ups**: Virtual consults generate referral alerts.
- **Reducing unnecessary ER visits**: Only critical vitals trigger ER alert.
- **Enabling collaboration between digital and on-the-ground care teams**: Location + AI recommendation per patient.
""")