"""
GutAngle — GutBelt Companion Web App
Streamlit web application for posture + EGG monitoring.

Run:
    streamlit run gutangle_app.py

Deploy:
    Use Streamlit Cloud or similar with requirements.txt
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
import random
import math
from collections import deque
import threading

# App state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'bt_connected' not in st.session_state:
    st.session_state.bt_connected = False
if 'battery' not in st.session_state:
    st.session_state.battery = 78
if 'signal' not in st.session_state:
    st.session_state.signal = -65
if 'posture_score' not in st.session_state:
    st.session_state.posture_score = 85
if 'egg_amplitude' not in st.session_state:
    st.session_state.egg_amplitude = 0.5
if 'egg_data' not in st.session_state:
    st.session_state.egg_data = deque([0.0] * 200, maxlen=200)
if 'posture_data' not in st.session_state:
    st.session_state.posture_data = deque([0.0] * 200, maxlen=200)
if 'session_time' not in st.session_state:
    st.session_state.session_time = 0
if 'simulating' not in st.session_state:
    st.session_state.simulating = False

def generate_history():
    data = {}
    now = time.time()
    for i in range(30):
        day = time.strftime("%Y-%m-%d", time.localtime(now - i * 86400))
        data[day] = {
            "posture_avg": random.randint(55, 95),
            "egg_avg": round(random.uniform(0.3, 0.9), 2),
            "sessions": random.randint(1, 5),
        }
    return data

history_data = generate_history()

def data_simulator():
    t = 0
    while st.session_state.simulating:
        t += 0.1
        egg = (0.5 * math.sin(2 * math.pi * 0.05 * t) +
               0.2 * math.sin(2 * math.pi * 0.15 * t) +
               random.gauss(0, 0.04))
        posture = max(0.0, min(1.0,
            0.7 + 0.3 * math.sin(2 * math.pi * 0.005 * t) + random.gauss(0, 0.025)))
        st.session_state.egg_amplitude = egg
        st.session_state.posture_score = int(posture * 100)
        st.session_state.egg_data.append(egg)
        st.session_state.posture_data.append(posture * 100)
        time.sleep(0.1)

def start_simulation():
    if not st.session_state.simulating:
        st.session_state.simulating = True
        thread = threading.Thread(target=data_simulator, daemon=True)
        thread.start()

def stop_simulation():
    st.session_state.simulating = False

def login_page():
    st.title("GutAngle")
    st.subheader("Posture & Gut Health Monitor")
    st.markdown("Welcome back — your gut is waiting.")

    username = st.text_input("Username / Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Please enter username and password.")

def bluetooth_page():
    st.title("Bluetooth Setup")
    st.write("Pair your GutBelt wearable")

    if st.button("Scan for Devices"):
        with st.spinner("Scanning..."):
            time.sleep(2)
            # Mock connection
            st.session_state.bt_connected = True
            st.success("GutBelt found and connected!")
            st.rerun()

    if st.button("Skip for now"):
        st.session_state.bt_connected = False
        st.rerun()

def dashboard_page():
    st.title("Dashboard")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Posture Score", f"{st.session_state.posture_score}%", "Good")
    with col2:
        st.metric("EGG Activity", "Normal", "3.0 cpm")
    with col3:
        minutes, seconds = divmod(st.session_state.session_time, 60)
        st.metric("Session Time", f"{minutes:02d}:{seconds:02d}", "Active")
    with col4:
        st.metric("Alerts", "0", "Today")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("EGG Signals")
        fig, ax = plt.subplots()
        ax.plot(list(st.session_state.egg_data))
        ax.set_title("EGG (mV)")
        st.pyplot(fig)

    with col2:
        st.subheader("Posture")
        fig, ax = plt.subplots()
        ax.plot(list(st.session_state.posture_data))
        ax.set_title("Posture Score (%)")
        st.pyplot(fig)

    status_col1, status_col2, status_col3 = st.columns([1,1,2])
    with status_col1:
        posture_status = "Good" if st.session_state.posture_score >= 75 else "Fair" if st.session_state.posture_score >= 50 else "Poor"
        st.write(f"Posture: {posture_status}")
    with status_col2:
        digestion_status = "Normal"
        st.write(f"Digestion: {digestion_status}")
    with status_col3:
        st.write("GutBelt Status: Connected" if st.session_state.bt_connected else "GutBelt Status: Not Connected")

def egg_signals_page():
    st.title("EGG Signals")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(list(st.session_state.egg_data))
    ax.set_title("Electrogastrography (EGG) Signal")
    ax.set_ylabel("Amplitude (mV)")
    st.pyplot(fig)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dominant Freq", "~3.0 cpm")
    with col2:
        st.metric("Amplitude", f"{abs(st.session_state.egg_amplitude):.2f} mV")
    with col3:
        status = "Active" if abs(st.session_state.egg_amplitude) > 0.6 else "Low" if abs(st.session_state.egg_amplitude) < 0.2 else "Normal"
        st.metric("Status", status)

    st.info("EGG measures the stomach's electrical activity. Normal gastric rhythm is 2–4 cpm. Deviations may indicate gastric motility issues or stress-related disruption.")

def posture_page():
    st.title("Posture")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Posture Score")
        fig, ax = plt.subplots()
        ax.pie([st.session_state.posture_score, 100 - st.session_state.posture_score], colors=['green', 'lightgray'], startangle=90)
        ax.text(0, 0, f"{st.session_state.posture_score}%", ha='center', va='center', fontsize=20)
        st.pyplot(fig)
        posture_label = "Good" if st.session_state.posture_score >= 75 else "Fair" if st.session_state.posture_score >= 50 else "Poor"
        st.write(f"**{posture_label}**")

    with col2:
        st.subheader("Posture (Session)")
        fig, ax = plt.subplots()
        ax.plot(list(st.session_state.posture_data))
        ax.set_title("Score (%)")
        st.pyplot(fig)

    st.subheader("Posture Tips")
    tips = [
        "Keep your back straight and shoulders relaxed.",
        "Screen should be at eye level to reduce neck strain.",
        "Take a posture break every 30 minutes.",
        "Keep feet flat on the floor for lumbar support.",
    ]
    for tip in tips:
        st.write(f"• {tip}")

def history_page():
    st.title("History")

    period = st.radio("Period", ["Week", "Month"], horizontal=True)
    days = 7 if period == "Week" else 30

    keys = sorted(history_data.keys())[-days:]

    st.subheader(f"Posture — Last {days} Days")
    posture_vals = [history_data[k]["posture_avg"] for k in keys]
    fig, ax = plt.subplots()
    ax.plot(posture_vals)
    st.pyplot(fig)

    st.subheader(f"EGG Activity — Last {days} Days")
    egg_vals = [history_data[k]["egg_avg"] for k in keys]
    fig, ax = plt.subplots()
    ax.plot(egg_vals)
    st.pyplot(fig)

    st.subheader("Daily Summary")
    summary_data = []
    for k in reversed(keys[-7:]):
        d = history_data[k]
        summary_data.append({
            "Date": k,
            "Posture": f"{d['posture_avg']}%",
            "EGG": str(d["egg_avg"]),
            "Sessions": str(d["sessions"])
        })
    st.table(summary_data)

def settings_page():
    st.title("Settings")

    st.subheader("Theme")
    theme = st.selectbox("Choose theme", ["Dark", "Light"])

    st.subheader("Language")
    language = st.selectbox("Choose language", ["English", "Tamil", "Hindi", "Telugu", "Kannada", "Malayalam", "Bengali", "Marathi", "Odia", "Urdu"])

    st.subheader("Change Password")
    current_pw = st.text_input("Current Password", type="password")
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm Password", type="password")
    if st.button("Save Changes"):
        if new_pw == confirm_pw:
            st.success("Password updated successfully.")
        else:
            st.error("New passwords do not match.")

    st.subheader("Device Info")
    st.write(f"**Device:** GutBelt v1.0")
    st.write(f"**Firmware:** v2.1.3")
    st.write(f"**Signal:** {st.session_state.signal} dBm")
    st.write(f"**Battery:** {st.session_state.battery}%")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

def main():
    st.set_page_config(page_title="GutAngle", page_icon="⬡", layout="wide")

    if not st.session_state.authenticated:
        login_page()
        return

    # Sidebar
    with st.sidebar:
        st.title("GutAngle")
        page = st.radio("Navigation", ["Dashboard", "EGG Signals", "Posture", "History", "Settings", "Bluetooth"])

        if st.button("Start Simulation"):
            start_simulation()
        if st.button("Stop Simulation"):
            stop_simulation()

        # Update session time
        if st.session_state.simulating:
            st.session_state.session_time += 1

    if page == "Dashboard":
        dashboard_page()
    elif page == "EGG Signals":
        egg_signals_page()
    elif page == "Posture":
        posture_page()
    elif page == "History":
        history_page()
    elif page == "Settings":
        settings_page()
    elif page == "Bluetooth":
        bluetooth_page()

if __name__ == "__main__":
    main()
