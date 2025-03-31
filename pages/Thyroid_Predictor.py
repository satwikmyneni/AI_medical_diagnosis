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
    page_title="Thyroid Checker",
    page_icon="🦋",
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
            text-decoration: none;
        }
        .prediction-box {
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 5px solid;
        }
        .Normal { border-color: #4CAF50; background:#4CAF50 ; }
        .Hypothyroidism { border-color: #FF9800; background: #FF9800; }
        .Hyperthyroidism { border-color: #f44336; background: #f44336; }
        .Borderline { border-color: #2196F3; background: #2196F3; }
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
    pipeline = joblib.load('models/thyroid_model.pkl')
    model = pipeline['model']
    scaler = pipeline['scaler']
    encoder = pipeline['encoder']
except Exception as e:
    st.error(f"Error loading model: {str(e)}")
    st.stop()

# Report Upload Section
with st.expander("📁 Upload Lab Report (CSV/Image/PDF)"):
    uploaded_file = st.file_uploader("Upload report", 
                                   type=["csv", "png", "jpg", "jpeg", "pdf"],
                                   key="thyroid_report_uploader")
    
    col_temp, col_clear = st.columns(2)
    with col_temp:
        template_csv = open('templates/thyroid_template.csv', 'rb')
        st.download_button(
            label="Download CSV Template",
            data=template_csv,
            file_name="thyroid_template.csv",
            mime="text/csv",
            key="thyroid_template_download"
        )
    with col_clear:
        if st.button("🧹 Clear Data", key="thyroid_clear_data"):
            st.session_state.clear()
            st.rerun()

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
                    'TSH': ['tsh', 'thyroid stimulating hormone'],
                    'T3': ['t3', 'triiodothyronine'],
                    'T4': ['t4', 'thyroxine'],
                    'TT4': ['tt4', 'total t4'],
                    'T4U': ['t4u', 't4 uptake'],
                    'FTI': ['fti', 'free thyroid index']
                }
                
                matched_cols = {}
                for col in df.columns:
                    col_lower = col.strip().lower()
                    for key, aliases in column_map.items():
                        if col_lower in aliases:
                            matched_cols[key] = col
                            break
                
                if len(matched_cols) >= 4:
                    for key, source_col in matched_cols.items():
                        extracted[key] = df[source_col].iloc[0]

            if uploaded_file.type != "text/csv":
                patterns = {
                    'age': r"(Age|AGE)\W*(\d+)\s*(years|yrs)?\b",
                    'TSH': r"(TSH)\W*(\d+\.?\d*)\s*(mIU/L)?\b",
                    'T3': r"(T3|Triiodothyronine)\W*(\d+\.?\d*)\s*(pg/mL)?\b",
                    'T4': r"(T4|Thyroxine)\W*(\d+\.?\d*)\s*(μg/dL)?\b",
                    'TT4': r"(Total T4|TT4)\W*(\d+\.?\d*)\s*(μg/dL)?\b",
                    'T4U': r"(T4 Uptake|T4U)\W*(\d+\.?\d*)\s*%?\b",
                    'FTI': r"(FTI|Free Thyroid Index)\W*(\d+\.?\d*)\s*(μg/dL)?\b"
                }

                for key, pattern in patterns.items():
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        try:
                            value = float(match.group(2))
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

st.title('Thyroid Disorder Prediction')

col1, col2 = st.columns(2)
with col1:
    age = st.number_input('Age (Years)', min_value=0, max_value=120,
                        value=validate_value('age', 30, 0, 120), key="thy_age_input")
with col2:
    TSH = st.number_input('TSH (mIU/L)', min_value=0.0,
                        value=validate_value('TSH', 2.5, 0.0, 100.0), key="thy_tsh_input")

col3, col4 = st.columns(2)
with col3:
    T3 = st.number_input('T3 (pg/mL)', min_value=0.0,
                       value=validate_value('T3', 3.0, 0.0, 20.0), key="thy_t3_input")
with col4:
    T4 = st.number_input('T4 (μg/dL)', min_value=0.0,
                       value=validate_value('T4', 7.5, 0.0, 50.0), key="thy_t4_input")

col5, col6 = st.columns(2)
with col5:
    TT4 = st.number_input('Total T4 (μg/dL)', min_value=0.0,
                        value=validate_value('TT4', 80.0, 0.0, 200.0), key="thy_tt4_input")
with col6:
    T4U = st.number_input('T4 Uptake (%)', min_value=0.0,
                        value=validate_value('T4U', 30.0, 0.0, 100.0), key="thy_t4u_input")

FTI = st.number_input('FTI (μg/dL)', min_value=0.0,
                    value=validate_value('FTI', 300.0, 0.0, 1000.0), key="thy_fti_input")

# Prediction Logic
if st.button('Predict Thyroid Condition', key="thy_predict_button"):
    try:
        input_data = np.array([[age, TSH, T3, T4, TT4, T4U, FTI]])
        scaled_data = scaler.transform(input_data)
        prediction = model.predict(scaled_data)
        condition = encoder.inverse_transform(prediction)[0]
        probabilities = model.predict_proba(scaled_data)[0]
        
        st.markdown(f"""
            <div class="prediction-box {condition}">
                <h3>{condition} Detected</h3>
                <p>Confidence: {max(probabilities)*100:.1f}%</p>
                <h3 style="margin:0; color: var(--text-color);">
                    {condition} Detected
                </h3>
            </div>
        """, unsafe_allow_html=True)

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

# Guidelines
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
        - 🟢 Normal: All values within reference ranges
        - 🟠 Hypothyroidism: High TSH + Low T4/T3
        - 🔴 Hyperthyroidism: Low TSH + High T4/T3
        - 🔵 Borderline: Values near threshold limits
        *Note: Always consult with an endocrinologist for clinical diagnosis.*
    """)

