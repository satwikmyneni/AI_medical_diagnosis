import streamlit as st
import joblib
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract
import re
import tempfile
from PyPDF2 import PdfReader
import time

# Configure page settings
st.set_page_config(
    page_title="Blood Pressure Checker",
    page_icon="💪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS styling
st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .top-left-container {
            position: fixed;
            top: 80px;
            left: 20px;
            z-index: 9999;
            text-decoration: none;
        }
        .top-left-button {
            background: linear-gradient(145deg, #4CAF50, #2E7D32);
            color: white !important;
            padding: 10px 20px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
            text-decoration: none;
        }
        .top-left-button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        .stApp {
            margin-top: 70px !important;
        }
        .stButton > button {
            display: block;
            margin: 0 auto;
            background: linear-gradient(145deg, #8e44ad, #6c3483);
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }
        .prediction-box {
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 5px solid;
        }
        .Normal { border-color: #4CAF50; background: #e8f5e9; }
        .Prehypertension { border-color: #FFC107; background: #fff8e1; }
        .Hypertension-Stage-1 { border-color: #f44336; background: #ffebee; }
        .Hypertension-Stage-2 { border-color: #d32f2f; background: #ffcdd2; }
    </style>
""", unsafe_allow_html=True)

# Back to Home Button
st.markdown('''
    <div class="top-left-container">
        <a href="/" class="top-left-button">⬅️ Back to Home</a>
    </div>
''', unsafe_allow_html=True)

# Load model pipeline
try:
    pipeline = joblib.load('models/bp_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
    gender_map = pipeline['gender_mapping']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Report Upload Section
with st.expander("📁 Upload Medical Report (CSV/Image/PDF)"):
    uploaded_file = st.file_uploader("Upload report", 
                                   type=["csv", "png", "jpg", "jpeg", "pdf"],
                                   key="bp_report_uploader")
    
    col_temp, col_clear = st.columns(2)
    with col_temp:
        template_csv = open('templates/bp_template.csv', 'rb')
        st.download_button(
            label="Download CSV Template",
            data=template_csv,
            file_name="bp_template.csv",
            mime="text/csv",
            key="bp_template_download"
        )
    with col_clear:
        if st.button("🧹 Clear Data", key="bp_clear_data"):
            st.session_state.clear()
            st.experimental_rerun()

    if uploaded_file is not None:
        try:
            start_time = time.time()
            extracted = {}
            
            if uploaded_file.type == "application/pdf":
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    reader = PdfReader(tmp.name)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                
                if len(text.strip()) < 50:
                    st.info("Attempting OCR on PDF pages...")
                    for page in reader.pages:
                        for img in page.images:
                            with tempfile.NamedTemporaryFile(delete=False) as tmp_img:
                                tmp_img.write(img.data)
                                image = Image.open(tmp_img.name)
                                text += pytesseract.image_to_string(image) + "\n"

            elif uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                text = pytesseract.image_to_string(image)

            elif uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
                column_map = {
                    'age': ['age', 'patient age', 'years'],
                    'gender': ['gender', 'sex'],
                    'weight': ['weight', 'wt', 'body weight'],
                    'height': ['height', 'ht', 'body height'],
                    'systolic': ['systolic', 'sys', 'sbp'],
                    'diastolic': ['diastolic', 'dia', 'dbp'],
                    'cholesterol': ['cholesterol', 'chol', 'tc'],
                    'pulse': ['pulse', 'heart rate', 'hr']
                }
                
                matched_cols = {}
                for col in df.columns:
                    col_lower = col.strip().lower()
                    for key, aliases in column_map.items():
                        if col_lower in aliases:
                            matched_cols[key] = col
                            break
                
                if len(matched_cols) >= 5:
                    for key, source_col in matched_cols.items():
                        extracted[key] = df[source_col].iloc[0]

            if uploaded_file.type != "text/csv":
                patterns = {
                    'age': r"(Age|AGE)\W*(\d+)\s*(years|yrs)?\b",
                    'weight': r"(Weight|WT)\W*(\d+\.?\d*)\s*(kg)?\b",
                    'height': r"(Height|HT)\W*(\d+\.?\d*)\s*(cm)?\b",
                    'systolic': r"(Systolic|SBP)\W*(\d+\.?\d*)\s*(mmHg)?\b",
                    'diastolic': r"(Diastolic|DBP)\W*(\d+\.?\d*)\s*(mmHg)?\b",
                    'cholesterol': r"(Cholesterol|CHOL)\W*(\d+\.?\d*)\s*(mg/dL)?\b",
                    'pulse': r"(Pulse|HR)\W*(\d+\.?\d*)\s*(bpm)?\b",
                    'gender': r"(Gender|Sex)\W*([MF])"
                }

                for key, pattern in patterns.items():
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        try:
                            value = matches[0][1].strip()
                            if key == 'gender':
                                extracted[key] = 'Male' if value.upper() == 'M' else 'Female'
                            else:
                                extracted[key] = float(value)
                        except:
                            continue

            if extracted:
                st.session_state.update(extracted)
                st.success(f"Processed in {time.time()-start_time:.1f}s")
            else:
                st.warning("No values found in document")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Input Fields with Validation
def validate_value(key, default, min_val, max_val):
    value = st.session_state.get(key, default)
    return default if not (min_val <= value <= max_val) else value

st.title('Blood Pressure Status Prediction')

col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120, 
                        value=validate_value('age', 30, 0, 120), key="bp_age_input")
with col2:
    gender = st.selectbox('Gender', ['Male', 'Female'],
                        index=0 if st.session_state.get('gender', 'Male') == 'Male' else 1,
                        key="bp_gender_select")

col3, col4 = st.columns(2)
with col3:
    weight = st.number_input('Weight (kg)', min_value=30.0, 
                           value=validate_value('weight', 70.0, 30.0, 300.0),
                           key="bp_weight_input")
with col4:
    height = st.number_input('Height (cm)', min_value=100.0, 
                           value=validate_value('height', 170.0, 100.0, 250.0),
                           key="bp_height_input")

# Calculate BMI
bmi = weight / ((height/100) ** 2)
st.markdown(f"**Calculated BMI:** {bmi:.1f}")

col5, col6 = st.columns(2)
with col5:
    systolic = st.number_input('Systolic BP (mmHg)', min_value=70.0, 
                             value=validate_value('systolic', 120.0, 70.0, 250.0),
                             key="bp_systolic_input")
with col6:
    diastolic = st.number_input('Diastolic BP (mmHg)', min_value=40.0, 
                              value=validate_value('diastolic', 80.0, 40.0, 150.0),
                              key="bp_diastolic_input")

col7, col8 = st.columns(2)
with col7:
    cholesterol = st.number_input('Cholesterol (mg/dL)', min_value=100.0, 
                                value=validate_value('cholesterol', 200.0, 100.0, 400.0),
                                key="bp_cholesterol_input")
with col8:
    pulse = st.number_input('Pulse Rate (bpm)', min_value=40.0, 
                          value=validate_value('pulse', 72.0, 40.0, 200.0),
                          key="bp_pulse_input")

# Prediction Logic
if st.button('Predict Blood Pressure Status', key="bp_predict_button"):
    try:
        input_data = np.array([[
            age, gender_map[gender], weight, height, bmi,
            systolic, diastolic, cholesterol, pulse
        ]])
        
        scaled_data = scaler.transform(input_data)
        prediction = model.predict(scaled_data)
        condition = encoder.inverse_transform(prediction)[0]
        probabilities = model.predict_proba(scaled_data)[0]
        
        st.markdown(f"""
            <div class="prediction-box {condition.replace(' ', '-')}">
                <h3>{condition}</h3>
            </div>
        """, unsafe_allow_html=True)

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

# Guidelines
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
        - Pulse ≥100 bpm
        *Based on American Heart Association guidelines*
    """)
