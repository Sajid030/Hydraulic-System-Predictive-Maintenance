import streamlit as st
import numpy as np
import joblib

# Load Scaled parameters
scaler = joblib.load("scaler.pkl", "rb")

# Load trained models
cooler_model = joblib.load("models/cooler_model.pkl")
valve_model = joblib.load("models/valve_model.pkl")
pump_model = joblib.load("models/pump_model.pkl")
accumulator_model = joblib.load("models/accumulator_model.pkl")

# UI title
st.title("Hydraulic System Maintenance Predictor")
st.markdown("Enter your system's sensor readings below:")

# Input fields
ps = [st.number_input(f"Pressure Sensor {i+1} (in bar)", min_value=0.0, value=0.0) for i in range(6)]
eps1 = st.number_input("Electrical Power Sensor (in watt)", min_value=0.0, value=0.0)
fs = [st.number_input(f"Volume Flow Sensor {i+1} (in l/min)", min_value=0.0, value=0.0) for i in range(2)]
ts = [st.number_input(f"Temperature Sensor {i+1} (in °C)", min_value=0.0, value=0.0) for i in range(4)]
vs1 = st.number_input("Vibration Sensor (in mm/s)", min_value=0.0, value=0.0)
ce = st.number_input("Cooling Efficiency (in %)", min_value=0.0, value=0.0)
cp = st.number_input("Cooling Power (in kW)", min_value=0.0, value=0.0)
se = st.number_input("System Efficiency Factor (in %)", min_value=0.0, value=0.0)
stable_flag = st.selectbox("Was the system stable during reading?", ["Yes", "No"])

# Convert stable flag
stable_val = 0 if stable_flag == "Yes" else 1

# Separate raw input (without stable_val) and scale it
raw_input_features = np.array(ps + [eps1] + fs + ts + [vs1, ce, cp, se]).reshape(1, -1)
scaled_input = scaler.transform(raw_input_features)

# Combine scaled input with stable_val
final_input = np.hstack((scaled_input, [[stable_val]]))  # ensure it's 2D

if st.button("Predict Maintenance Needs"):
    # Warning if system was unstable
    if stable_val == 1:
        st.warning("⚠️ System was not stable during reading. Predictions may be noisy or less accurate.")

    # Make predictions
    cooler_status = cooler_model.predict(final_input)[0]
    valve_status = valve_model.predict(final_input)[0]
    pump_status = pump_model.predict(final_input)[0]
    accumulator_status = accumulator_model.predict(final_input)[0]

    st.subheader("🔍 Prediction Result:")

    # alert icons
    danger = "❌"
    warning = "⚠️"
    success = "✅"

    # Cooler condition
    if cooler_status == 0:
        st.error(f"{danger} Cooler: Immediate maintenance required.")
    elif cooler_status == 1:
        st.warning(f"{warning} Cooler: Reduced efficiency. Service recommended.")
    else:
        st.success(f"{success} Cooler: Operating at full efficiency.")

    # Valve condition
    if valve_status == 0:
        st.error(f"{danger} Valve: Critical failure risk! Urgent maintenance needed.")
    elif valve_status == 1:
        st.warning(f"{warning} Valve: Severe lag observed. Schedule maintenance.")
    elif valve_status == 2:
        st.warning(f"{warning} Valve: Minor lag detected. Monitor performance.")
    else:
        st.success(f"{success} Valve: Functioning optimally.")

    # Pump leakage
    if pump_status == 2:
        st.error(f"{danger} Pump: Severe internal leakage detected! Immediate action required.")
    elif pump_status == 1:
        st.warning(f"{warning} Pump: Weak leakage detected. Plan maintenance.")
    else:
        st.success(f"{success} Pump: No leakage. Operating normally.")

    # Hydraulic accumulator
    if accumulator_status == 0:
        st.error(f"{danger} Accumulator: Pressure critically low. Immediate servicing required.")
    elif accumulator_status == 1:
        st.warning(f"{warning} Accumulator: Severely reduced pressure. Maintenance advised.")
    elif accumulator_status == 2:
        st.warning(f"{warning} Accumulator: Slight pressure reduction. Monitor regularly.")
    else:
        st.success(f"{success} Accumulator: Optimal pressure maintained.")