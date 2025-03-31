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
    page_title="Diabetes Predictor",
    page_icon="🩸",
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
            top: 60px;
            left: 20px;
            z-index: 9999;
        }
        .top-left-button {
            background: linear-gradient(145deg, #4CAF50, #2E7D32);
            color: white !important;
            padding: 10px 20px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
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
        .Non-Diabetic { border-color: #4CAF50; background: #e8f5e9; }
        .Pre-Diabetes { border-color: #FFC107; background: #fff8e1; }
        .Type-1-Diabetes { border-color: #f44336; background: #ffebee; }
        .Type-2-Diabetes { border-color: #2196F3; background: #e3f2fd; }
        .Gestational-Diabetes { border-color: #9C27B0; background: #f3e5f5; }
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
    pipeline = joblib.load('models/diabetes_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
    gender_map = pipeline['gender_mapping']
    family_history_map = pipeline['family_history_mapping']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Report Upload Section
with st.expander("📁 Upload Lab Report (CSV/Image/PDF)", expanded=False):
    uploaded_file = st.file_uploader("Upload medical report", 
                                   type=["csv", "png", "jpg", "jpeg", "pdf"],
                                   key="report_uploader")
    
    col_temp, col_clear = st.columns(2)
    with col_temp:
        template_csv = open('datasets/diabetes_template.csv', 'rb')
        st.download_button(
            label="Download CSV Template",
            data=template_csv,
            file_name="diabetes_template.csv",
            mime="text/csv",
            key="template_download"
        )
    with col_clear:
        if st.button("🧹 Clear Uploaded Data", key="clear_data"):
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
                    'bmi': ['bmi', 'body mass index'],
                    'glucose': ['glucose', 'blood glucose', 'glu'],
                    'hba1c': ['hba1c', 'a1c', 'glycated hemoglobin'],
                    'fasting': ['fasting', 'fbs', 'fasting blood sugar'],
                    'post_meal': ['post meal', 'postprandial', 'ppbs'],
                    'family_history': ['family history', 'diabetes history']
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
                    'glucose': r"(Glucose|GLU)\W*(\d+\.?\d*)\s*(mg/dL|mmol/L)?\b",
                    'bmi': r"(BMI|Body Mass Index)\W*(\d+\.?\d*)",
                    'hba1c': r"(HbA1c|A1C)\W*(\d+\.?\d*)\s*%?",
                    'fasting': r"(Fasting|FBS)\W*(\d+\.?\d*)\s*(mg/dL|mmol/L)?\b",
                    'post_meal': r"(Post\s*Meal|Postprandial|PPBS)\W*(\d+\.?\d*)\s*(mg/dL|mmol/L)?\b",
                    'gender': r"(Gender|Sex)\W*([MF])",
                    'family_history': r"(Family\s*History)\W*(Yes|No|Positive|Negative)"
                }

                for key, pattern in patterns.items():
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        try:
                            value = matches[0][1].strip()
                            unit = matches[0][2].lower() if len(matches[0])>2 else ''
                            
                            if key == 'gender':
                                extracted[key] = 'Male' if value.upper() == 'M' else 'Female'
                            elif key == 'family_history':
                                extracted[key] = 'Yes' if value.lower() in ['yes', 'positive'] else 'No'
                            elif key in ['glucose', 'fasting', 'post_meal'] and 'mmol/l' in unit:
                                extracted[key] = float(value) * 18.0182
                            else:
                                extracted[key] = float(value)
                        except:
                            continue

            if extracted:
                st.session_state.update(extracted)
                st.success(f"Processed in {time.time()-start_time:.1f}s")
            else:
                st.warning("No values found in document")

            uploaded_file = None
            st.session_state.file_processed = True

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Input Fields with Unique Keys
def validate_value(key, default, min_val, max_val):
    value = st.session_state.get(key, default)
    return default if not (min_val <= value <= max_val) else value

st.title('Diabetes Risk Assessment')

col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120, 
                        value=validate_value('age', 30, 0, 120), key="age_input")
with col2:
    gender = st.selectbox('Gender', ['Male', 'Female'],
                        index=0 if st.session_state.get('gender', 'Male') == 'Male' else 1,
                        key="gender_select")

col3, col4 = st.columns(2)
with col3:
    bmi = st.number_input('BMI', min_value=10.0, max_value=50.0,
                        value=validate_value('bmi', 22.0, 10.0, 50.0),
                        help="Normal range: 18.5-24.9", key="bmi_input")
with col4:
    glucose = st.number_input('Glucose Level (mg/dL)', min_value=50, 
                            value=validate_value('glucose', 90, 50, 300),
                            help="Normal fasting: <100 mg/dL", key="glucose_input")

col5, col6 = st.columns(2)
with col5:
    hba1c = st.number_input('HbA1c (%)', min_value=4.0, max_value=15.0,
                          value=validate_value('hba1c', 5.0, 4.0, 15.0),
                          help="Normal: <5.7%", key="hba1c_input")
with col6:
    fasting = st.number_input('Fasting Blood Sugar (mg/dL)', min_value=50,
                            value=validate_value('fasting', 90, 50, 300),
                            help="Normal: 70-100 mg/dL", key="fasting_input")

col7, col8 = st.columns(2)
with col7:
    post_meal = st.number_input('Post-Meal Blood Sugar (mg/dL)', min_value=50,
                              value=validate_value('post_meal', 120, 50, 300),
                              help="Normal (2hr after eating): <140 mg/dL", key="postmeal_input")
with col8:
    family_history = st.selectbox('Family History of Diabetes', ['No', 'Yes'],
                                index=0 if st.session_state.get('family_history', 'No') == 'No' else 1,
                                key="family_history_select")

# Prediction Logic
if st.button('Assess Diabetes Risk', key="predict_button"):
    try:
        input_data = np.array([[
            age, gender_map[gender], bmi, glucose,
            hba1c, fasting, post_meal, family_history_map[family_history]
        ]])
        
        scaled_data = scaler.transform(input_data)
        prediction = model.predict(scaled_data)
        condition = encoder.inverse_transform(prediction)[0]
        
        st.markdown(f"""
            <div class="prediction-box {condition.replace(' ', '-')}">
                <h3>{condition}</h3>
            </div>
        """, unsafe_allow_html=True)

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

# Guidelines
with st.expander("📋 Diabetes Diagnostic Criteria"):  # Removed key="guidelines_expander"
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