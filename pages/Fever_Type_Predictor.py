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
    page_title="Fever Type Predictor",
    page_icon="🤒",
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
        .Viral-Fever { border-color: #4CAF50; background: #e8f5e9; }
        .Bacterial-Fever { border-color: #2196F3; background: #e3f2fd; }
        .Dengue-Fever { border-color: #f44336; background: #ffebee; }
        .Malaria { border-color: #FF9800; background: #fff3e0; }
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
    pipeline = joblib.load('models/fever_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
    gender_map = pipeline['gender_mapping']
    severity_map = pipeline['severity_mapping']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Report Upload Section
with st.expander("📁 Upload Medical Report (CSV/Image/PDF)"):
    uploaded_file = st.file_uploader("Upload report", 
                                   type=["csv", "png", "jpg", "jpeg", "pdf"],
                                   key="fever_report_uploader")
    
    col_temp, col_clear = st.columns(2)
    with col_temp:
        template_csv = open('templates/fever_template.csv', 'rb')
        st.download_button(
            label="Download CSV Template",
            data=template_csv,
            file_name="fever_template.csv",
            mime="text/csv",
            key="fever_template_download"
        )
    with col_clear:
        if st.button("🧹 Clear Data", key="fever_clear_data"):
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
                    'age': ['age', 'patient age'],
                    'gender': ['gender', 'sex'],
                    'temp': ['temp', 'temperature'],
                    'duration': ['duration', 'days'],
                    'heart_rate': ['heart_rate', 'hr', 'pulse'],
                    'severity': ['severity', 'severity_level'],
                    'dehydration': ['dehydration', 'hydration'],
                    'headache': ['headache', 'head_pain'],
                    'muscle_pain': ['muscle_pain', 'myalgia'],
                    'fatigue': ['fatigue', 'tiredness'],
                    'chills': ['chills', 'shivering']
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
                        value = df[source_col].iloc[0]
                        if key in ['headache', 'muscle_pain', 'fatigue', 'chills']:
                            extracted[key] = 'Yes' if value else 'No'
                        else:
                            extracted[key] = value

            if uploaded_file.type != "text/csv":
                patterns = {
                    'age': r"(Age|AGE)\W*(\d+)\s*(years|yrs)?\b",
                    'temp': r"(Temp|Temperature)\W*(\d+\.?\d*)\s*°?C?\b",
                    'duration': r"(Duration|Days)\W*(\d+)\s*(days)?\b",
                    'heart_rate': r"(Heart Rate|HR)\W*(\d+)\s*(bpm)?\b",
                    'severity': r"(Severity)\W*(None|Mild|Moderate|Severe)\b",
                    'dehydration': r"(Dehydration)\W*(None|Mild|Moderate|Severe)\b",
                    'gender': r"(Gender|Sex)\W*(Male|Female)\b",
                    'headache': r"(Headache)\W*(Yes|No)\b",
                    'muscle_pain': r"(Muscle Pain|Myalgia)\W*(Yes|No)\b",
                    'fatigue': r"(Fatigue)\W*(Yes|No)\b",
                    'chills': r"(Chills)\W*(Yes|No)\b"
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        try:
                            value = match.group(2).strip()
                            if key in ['headache', 'muscle_pain', 'fatigue', 'chills']:
                                extracted[key] = 'Yes' if value.lower() == 'yes' else 'No'
                            else:
                                extracted[key] = value
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

st.title('Fever Type Prediction')

col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120, 
                        value=validate_value('age', 30, 0, 120), key="fever_age_input")
with col2:
    gender = st.selectbox('Gender', ['Male', 'Female'],
                        index=0 if st.session_state.get('gender', 'Male') == 'Male' else 1,
                        key="fever_gender_select")

col3, col4 = st.columns(2)
with col3:
    temp = st.number_input('Temperature (°C)', min_value=35.0, max_value=45.0,
                         value=validate_value('temp', 37.0, 35.0, 45.0), key="fever_temp_input")
with col4:
    duration = st.number_input('Duration (Days)', min_value=1, max_value=14,
                              value=validate_value('duration', 3, 1, 14), key="fever_duration_input")

col5, col6 = st.columns(2)
with col5:
    heart_rate = st.number_input('Heart Rate (bpm)', min_value=40, max_value=200,
                                value=validate_value('heart_rate', 80, 40, 200), key="fever_hr_input")
with col6:
    severity = st.selectbox('Severity Level', ['None', 'Mild', 'Moderate', 'Severe'],
                           index=['None', 'Mild', 'Moderate', 'Severe'].index(
                               st.session_state.get('severity', 'None')),
                           key="fever_severity_select")

col7, col8 = st.columns(2)
with col7:
    dehydration = st.selectbox('Dehydration Level', ['None', 'Mild', 'Moderate', 'Severe'],
                              index=['None', 'Mild', 'Moderate', 'Severe'].index(
                                  st.session_state.get('dehydration', 'None')),
                              key="fever_dehydration_select")
with col8:
    headache = st.selectbox('Headache', ['No', 'Yes'],
                           index=0 if st.session_state.get('headache', 'No') == 'No' else 1,
                           key="fever_headache_select")

col9, col10 = st.columns(2)
with col9:
    muscle_pain = st.selectbox('Muscle Pain', ['No', 'Yes'],
                              index=0 if st.session_state.get('muscle_pain', 'No') == 'No' else 1,
                              key="fever_muscle_select")
with col10:
    fatigue = st.selectbox('Fatigue', ['No', 'Yes'],
                          index=0 if st.session_state.get('fatigue', 'No') == 'No' else 1,
                          key="fever_fatigue_select")

chills = st.selectbox('Chills', ['No', 'Yes'],
                     index=0 if st.session_state.get('chills', 'No') == 'No' else 1,
                     key="fever_chills_select")

# Prediction Logic
if st.button('Predict Fever Type', key="fever_predict_button"):
    try:
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
        
        scaled_data = scaler.transform(input_data)
        prediction = model.predict(scaled_data)
        condition = encoder.inverse_transform(prediction)[0]
        probabilities = model.predict_proba(scaled_data)[0]
        
        st.markdown(f"""
            <div class="prediction-box {condition.replace(' ', '-')}">
                <h3>{condition}</h3>
            </div>
        """, unsafe_allow_html=True)

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

# Guidelines
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
