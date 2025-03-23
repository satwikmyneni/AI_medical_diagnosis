import streamlit as st
import joblib
import numpy as np
import os

# Configure page settings and remove sidebar
st.set_page_config(
    page_title="Blood Pressure Checker",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS styling
st.markdown("""
    <style>
        /* Remove sidebar completely */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Back button container */
        .top-left-container {
            position: fixed;
            top: 60px;
            left: 20px;
            z-index: 9999;
        }
        
        /* Back button styling */
        .top-left-button {
            background: linear-gradient(145deg, #4CAF50, #2E7D32);
            color: white !important;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none !important;
            display: inline-block;
        }
        
        .top-left-button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        
        /* Ensure main content doesn't overlap */
        .stApp {
            margin-top: 70px !important;
        }

        /* Center the Predict button with animation */
        .stButton > button {
            display: block;
            margin: 0 auto;
            background: linear-gradient(145deg, #8e44ad, #6c3483);
            color: white;
            border-radius: 8px;
            padding: 10px 24px;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease-in-out, box-shadow 0.3s ease-in-out;
        }

        .stButton > button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4);
        }
        /* Prediction status styling */
        .prediction-box {
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 5px solid;
            color: #000000 !important;
        }
        .Normal { border-color: #4CAF50; background: #e8f5e9; }
        .Prehypertension { border-color: #FFC107; background: #fff8e1; }
        .Hypertension-Stage-1 { border-color: #f44336; background: #ffebee; }
        .Hypertension-Stage-2 { border-color: #d32f2f; background: #ffcdd2; }
        
        .prediction-box h3, .prediction-box p {
            color: #000000 !important;
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)

# Back to Home Button (same as previous)
st.markdown(
    '''
    <div class="top-left-container">
        <a href="/" class="top-left-button">
            ⬅️ Back to Home
        </a>
    </div>
    ''',
    unsafe_allow_html=True
)


# Load the model pipeline
try:
    pipeline = joblib.load('models/bp_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
    gender_map = pipeline['gender_mapping']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Title
st.title('Blood Pressure Status Prediction')

# User inputs
col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120, value=30)
with col2:
    gender = st.selectbox('Gender', ['Male', 'Female'])

col3, col4 = st.columns(2)
with col3:
    weight = st.number_input('Weight (kg)', min_value=30.0, value=70.0, 
                           help="Healthy range varies by height and age")
with col4:
    height = st.number_input('Height (cm)', min_value=100.0, value=170.0)

col5, col6 = st.columns(2)
with col5:
    systolic = st.number_input('Systolic BP (mmHg)', min_value=70.0, value=120.0,
                             help="Normal: <120 mmHg")
with col6:
    diastolic = st.number_input('Diastolic BP (mmHg)', min_value=40.0, value=80.0,
                              help="Normal: <80 mmHg")

col7, col8 = st.columns(2)
with col7:
    cholesterol = st.number_input('Cholesterol (mg/dL)', min_value=100.0, value=200.0,
                                help="Normal: <200 mg/dL")
with col8:
    pulse = st.number_input('Pulse Rate (bpm)', min_value=40.0, value=72.0,
                          help="Normal resting: 60-100 bpm")

# Calculate BMI
bmi = weight / ((height/100) ** 2)
st.markdown(f"**Calculated BMI:** {bmi:.1f} ({'Healthy' if 18.5 <= bmi <= 24.9 else 'Check BMI'})")

# Predict button
if st.button('Predict Blood Pressure Status'):
    try:
        # Prepare input data
        input_data = np.array([[
            age,
            gender_map[gender],
            weight,
            height,
            bmi,
            systolic,
            diastolic,
            cholesterol,
            pulse
        ]])
        
        # Scale features
        scaled_data = scaler.transform(input_data)
        
        # Predict
        prediction = model.predict(scaled_data)
        condition = encoder.inverse_transform(prediction)[0]
        
        # Get probabilities
        probabilities = model.predict_proba(scaled_data)[0]
        
        # Display result
        st.markdown(f"""
            <div class="prediction-box {condition.replace(' ', '-')}">
                <h3>{condition}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Interpretation
        st.subheader("Clinical Interpretation:")
        if condition == "Normal":
            st.success("Blood pressure within normal range. Maintain healthy habits!")
        elif condition == "Prehypertension":
            st.warning("Elevated blood pressure. Recommendations:")
            st.markdown("- Monitor regularly\n- Reduce sodium intake\n- Increase physical activity")
        elif "Stage 1" in condition:
            st.error("Stage 1 Hypertension. Recommendations:")
            st.markdown("- Consult doctor\n- Lifestyle changes\n- Possible medication")
        else:
            st.error("Stage 2 Hypertension. Recommendations:")
            st.markdown("- Immediate medical consultation\n- Regular monitoring\n- Medication required")

    except Exception as e:
        st.error(f"Prediction failed: {str(e)}")

# Reference information
with st.expander("📋 Blood Pressure Guidelines"):
    st.markdown("""
        **Blood Pressure Categories:**
        - Normal: <120/<80 mmHg
        - Prehypertension: 120-139/80-89 mmHg
        - Stage 1 Hypertension: 140-159/90-99 mmHg
        - Stage 2 Hypertension: ≥160/≥100 mmHg
        
        **Risk Factors:**
        - BMI ≥25 (Overweight)
        - Cholesterol ≥200 mg/dL
        - Pulse ≥100 bpm (Tachycardia)
        
        *Based on American Heart Association guidelines*
    """)
