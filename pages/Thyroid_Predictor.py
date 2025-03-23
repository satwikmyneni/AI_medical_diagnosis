import streamlit as st
import joblib  # Changed from pickle to joblib
import numpy as np
import pandas as pd

# Configure page settings and remove sidebar
st.set_page_config(
    page_title="Thyroid Checker",
    page_icon="🦋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS styling for back button and predict button
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
            color: #000000 !important;  /* Force black text */
        }
        .Normal { border-color: #4CAF50; background: #e8f5e9; }
        .Hypothyroidism { border-color: #FF9800; background: #fff3e0; }
        .Hyperthyroidism { border-color: #f44336; background: #ffebee; }
        .Borderline { border-color: #2196F3; background: #e3f2fd; }
        
        /* Force dark text in all cases */
        .prediction-box h3, .prediction-box p {
            color: #000000 !important;
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)

# Back to Home Button
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
    pipeline = joblib.load('models/thyroid_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Title
st.title('Thyroid Disorder Prediction')

# User inputs with medical units
col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120, value=30)
with col2:
    TSH = st.number_input('TSH (mIU/L)', min_value=0.0, value=2.5, 
                        help="Normal range: 0.4-4.0 mIU/L")

col3, col4 = st.columns(2)
with col3:
    T3 = st.number_input('T3 (pg/mL)', min_value=0.0, value=3.0,
                       help="Normal range: 2.3-4.2 pg/mL")
with col4:
    T4 = st.number_input('T4 (μg/dL)', min_value=0.0, value=7.5,
                       help="Normal range: 5.0-12.0 μg/dL")

col5, col6 = st.columns(2)
with col5:
    TT4 = st.number_input('Total T4 (μg/dL)', min_value=0.0, value=80.0,
                        help="Normal range: 60-120 μg/dL")
with col6:
    T4U = st.number_input('T4 Uptake (%)', min_value=0.0, value=30.0,
                        help="Normal range: 25-35%")

FTI = st.number_input('FTI (μg/dL)', min_value=0.0, value=300.0,
                    help="Normal range: 200-400 μg/dL")

# Predict button
if st.button('Predict Thyroid Condition'):
    try:
        # Create input array
        input_data = np.array([[age, TSH, T3, T4, TT4, T4U, FTI]])
        
        # Scale features
        scaled_data = scaler.transform(input_data)
        
        # Make prediction
        prediction = model.predict(scaled_data)
        condition = encoder.inverse_transform(prediction)[0]
        
        # Get probabilities
        probabilities = model.predict_proba(scaled_data)[0]
        
        # Create prediction display
        st.markdown(f"""
            <div class="prediction-box {condition}">
                <h3 style="margin:0; color: var(--text-color);">
                    {condition} Detected
                </h3>
                <p style="margin:0.5rem 0 0 0;">
                    Confidence: {max(probabilities)*100:.1f}%
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Show interpretation
        st.subheader("Interpretation:")
        if condition == "Normal":
            st.success("Thyroid function appears within normal parameters.")
        elif condition == "Hypothyroidism":
            st.warning("Potential underactive thyroid detected. Recommendations:")
            st.markdown("- Confirm with TSH and Free T4 tests\n- Consider thyroid antibody tests\n- Monitor symptoms")
        elif condition == "Hyperthyroidism":
            st.error("Potential overactive thyroid detected. Recommendations:")
            st.markdown("- Thyroid ultrasound recommended\n- Check thyroid antibodies\n- Monitor heart rate")
        else:
            st.info("Borderline thyroid function. Recommendations:")
            st.markdown("- Repeat tests in 2-4 weeks\n- Monitor for symptom changes\n- Consider TSH monitoring")

    except Exception as e:
        st.error(f"Prediction failed: {str(e)}")
        st.write("Please check your input values and try again.")

# Reference information
with st.expander("📋 Clinical Reference Guide"):
    st.markdown("""
        **Normal Thyroid Function Ranges:**
        - TSH: 0.4-4.0 mIU/L
        - Free T3: 2.3-4.2 pg/mL
        - Free T4: 0.8-1.8 ng/dL
        - Total T4: 5.0-12.0 μg/dL
        - T4 Uptake: 25-35%
        - FTI: 200-400 μg/dL

        **Key Patterns:**
        - 🟢 **Normal**: All values within reference ranges
        - 🟠 **Hypothyroidism**: High TSH + Low T4/T3
        - 🔴 **Hyperthyroidism**: Low TSH + High T4/T3
        - 🔵 **Borderline**: Values near threshold limits

        *Note: Always consult with an endocrinologist for clinical diagnosis.*
    """)