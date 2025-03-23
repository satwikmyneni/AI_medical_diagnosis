import streamlit as st
import joblib
import numpy as np
import os

# Configure page settings
st.set_page_config(
    page_title="Fever Type Predictor",
    page_icon="🤒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS styling (similar to previous implementations)
st.markdown("""
    <style>
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
        .Viral-Fever { border-color: #4CAF50; background: #e8f5e9; }
        .Bacterial-Fever { border-color: #2196F3; background: #e3f2fd; }
        .Dengue-Fever { border-color: #f44336; background: #ffebee; }
        .Malaria { border-color: #FF9800; background: #fff3e0; }
    </style>
""", unsafe_allow_html=True)

# Back to Home Button (same as previous implementations)
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
    pipeline = joblib.load('models/fever_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
    gender_map = pipeline['gender_mapping']
    severity_map = pipeline['severity_mapping']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Title
st.title('Fever Type Prediction')

# User inputs
col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120, value=30)
with col2:
    gender = st.selectbox('Gender', ['Male', 'Female'])

col3, col4 = st.columns(2)
with col3:
    temp = st.number_input('Body Temperature (°C)', min_value=35.0, max_value=45.0, value=37.0)
with col4:
    duration = st.number_input('Duration (Days)', min_value=1, max_value=14, value=3)

col5, col6 = st.columns(2)
with col5:
    heart_rate = st.number_input('Heart Rate (bpm)', min_value=40, max_value=200, value=80)
with col6:
    severity = st.selectbox('Severity Level', ['None', 'Mild', 'Moderate', 'Severe'])

col7, col8 = st.columns(2)
with col7:
    dehydration = st.selectbox('Dehydration Level', ['None', 'Mild', 'Moderate', 'Severe'])
with col8:
    headache = st.selectbox('Headache', ['No', 'Yes'])

col9, col10 = st.columns(2)
with col9:
    muscle_pain = st.selectbox('Muscle Pain', ['No', 'Yes'])
with col10:
    fatigue = st.selectbox('Fatigue', ['No', 'Yes'])

chills = st.selectbox('Chills', ['No', 'Yes'])

# Predict button
if st.button('Predict Fever Type'):
    try:
        # Prepare input data
        input_data = np.array([[
            age,
            gender_map[gender],
            temp,
            headache == 'Yes',
            muscle_pain == 'Yes',
            fatigue == 'Yes',
            chills == 'Yes',
            severity_map[severity],
            severity_map[dehydration],
            duration,
            heart_rate
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
                <p>Confidence: {max(probabilities)*100:.1f}%</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Interpretation
        st.subheader("Clinical Interpretation:")
        if condition == "Viral Fever":
            st.info("Typical viral infection. Recommendations:")
            st.markdown("- Rest and hydration\n- Symptomatic treatment\n- Monitor for complications")
        elif condition == "Bacterial Fever":
            st.warning("Possible bacterial infection. Recommendations:")
            st.markdown("- Consider antibiotic therapy\n- Blood culture recommended\n- Monitor WBC count")
        elif condition == "Dengue Fever":
            st.error("Suspected dengue infection. Recommendations:")
            st.markdown("- Monitor platelet count\n- Watch for hemorrhagic signs\n- Hospitalization if severe")
        else:
            st.error("Malaria suspected. Recommendations:")
            st.markdown("- Blood smear for parasites\n- Antimalarial treatment\n- Monitor for complications")

    except Exception as e:
        st.error(f"Prediction failed: {str(e)}")

# Reference information
with st.expander("📋 Clinical Guidelines"):
    st.markdown("""
        **Key Differentiators:**
        - Viral Fever: Gradual onset, <39°C, normal WBC
        - Bacterial Fever: >39°C, localized symptoms, elevated WBC
        - Dengue: High fever + rash + thrombocytopenia
        - Malaria: Cyclic fever + travel history
        
        **Critical Values:**
        - Danger Signs: Temp >40°C, HR >120, Duration >7 days
        - Emergency: Bleeding, confusion, severe dehydration
        
        *Based on WHO fever management guidelines*
    """)