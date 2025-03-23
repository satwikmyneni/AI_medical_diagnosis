import streamlit as st
import joblib
import numpy as np
import os

# Configure page settings
st.set_page_config(
    page_title="Diabetes Predictor",
    page_icon="🩸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS styling (consistent with previous implementations)
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
        .Non-Diabetic { border-color: #4CAF50; background: #e8f5e9; }
        .Pre-Diabetes { border-color: #FFC107; background: #fff8e1; }
        .Type-1-Diabetes { border-color: #f44336; background: #ffebee; }
        .Type-2-Diabetes { border-color: #2196F3; background: #e3f2fd; }
        .Gestational-Diabetes { border-color: #9C27B0; background: #f3e5f5; }
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
    pipeline = joblib.load('models/diabetes_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
    gender_map = pipeline['gender_mapping']
    family_history_map = pipeline['family_history_mapping']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Title
st.title('Diabetes Risk Assessment')

# User inputs
col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120, value=30)
with col2:
    gender = st.selectbox('Gender', ['Male', 'Female'])

col3, col4 = st.columns(2)
with col3:
    bmi = st.number_input('BMI', min_value=10.0, max_value=50.0, value=22.0,
                        help="Normal range: 18.5-24.9")
with col4:
    glucose = st.number_input('Glucose Level (mg/dL)', min_value=50, value=90,
                            help="Normal fasting: <100 mg/dL")

col5, col6 = st.columns(2)
with col5:
    hba1c = st.number_input('HbA1c (%)', min_value=4.0, max_value=15.0, value=5.0,
                          help="Normal: <5.7%")
with col6:
    fasting = st.number_input('Fasting Blood Sugar (mg/dL)', min_value=50, value=90,
                            help="Normal: 70-100 mg/dL")

col7, col8 = st.columns(2)
with col7:
    post_meal = st.number_input('Post-Meal Blood Sugar (mg/dL)', min_value=50, value=120,
                              help="Normal (2hr after eating): <140 mg/dL")
with col8:
    family_history = st.selectbox('Family History of Diabetes', ['No', 'Yes'])

# Predict button
if st.button('Assess Diabetes Risk'):
    try:
        # Prepare input data
        input_data = np.array([[
            age,
            gender_map[gender],
            bmi,
            glucose,
            hba1c,
            fasting,
            post_meal,
            family_history_map[family_history]
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
        
        # Clinical interpretation
        st.subheader("Medical Guidance:")
        if "Non-Diabetic" in condition:
            st.success("Healthy parameters. Recommendations:")
            st.markdown("- Maintain balanced diet\n- Regular exercise\n- Annual checkups")
        elif "Pre-Diabetes" in condition:
            st.warning("Early warning signs. Recommendations:")
            st.markdown("- Lifestyle modifications\n- Monitor glucose levels\n- Consult dietitian")
        elif "Type 1" in condition:
            st.error("Insulin-dependent diabetes. Recommendations:")
            st.markdown("- Insulin therapy\n- Frequent monitoring\n- Endocrinologist consultation")
        elif "Type 2" in condition:
            st.error("Metabolic disorder. Recommendations:")
            st.markdown("- Oral medications\n- Dietary changes\n- Regular exercise")
        else:
            st.warning("Pregnancy-related. Recommendations:")
            st.markdown("- Close monitoring\n- Specialized diet\n- Obstetrician coordination")

    except Exception as e:
        st.error(f"Prediction failed: {str(e)}")

# Clinical guidelines expander
with st.expander("📋 Diabetes Diagnostic Criteria"):
    st.markdown("""
        **ADA Guidelines:**
        - Normal: Fasting <100, HbA1c <5.7%
        - Pre-Diabetes: Fasting 100-125, HbA1c 5.7-6.4%
        - Diabetes: Fasting ≥126, HbA1c ≥6.5%
        
        **Risk Factors:**
        - BMI ≥25 (Overweight)
        - Family history
        - Age ≥45 years
        
        **Emergency Values:**
        - Fasting >250 mg/dL
        - Random glucose >300 mg/dL
        - HbA1c >10%
        
        *Based on American Diabetes Association standards*
    """)