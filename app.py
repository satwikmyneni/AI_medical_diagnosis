import streamlit as st
import random

st.set_page_config(
    page_title="NEO Health AI",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .st-emotion-cache-6qob1r, 
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"] {
            display: none !important;
            visibility: hidden !important;
            width: 0 !important;
            height: 0 !important;
            opacity: 0 !important;
            transform: translateX(-100%) !important;
        }

        .stApp {
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding: 0 !important;
            max-width: 100vw !important;
            background: linear-gradient(135deg, #f8fdff, #e6f7ff) !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            color: #333 !important;
        }

        header[data-testid="stHeader"] {
            display: none !important;
        }

        .block-container {
            padding: 1rem 0 0 0 !important;
            max-width: 100% !important;
        }

        div[style*="transform: translateX(0px)"] {
            transform: translateX(-100%) !important;
            transition: none !important;
        }
        
        .header-title {
            font-size: 3.5rem !important;
            font-weight: bold !important;
            text-align: center !important;
            margin: 0 auto !important;
            color: #0d5c75;
            padding: 1.5rem 0;
            position: relative;
        }
        
        .header-title:after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 4px;
            background: #25DAC5;
            border-radius: 2px;
        }
        
        .marquee-container {
            background: #e3f2fd;
            border-radius: 0;
            padding: 12px 0;
            margin: 1rem auto;
            max-width: 90%;
            border-top: 2px solid #bbdefb;
            border-bottom: 2px solid #bbdefb;
            overflow: hidden;
            position: relative;
        }
        
        .marquee {
            font-size: 1.1rem;
            padding: 8px 0;
            color: #0d47a1;
            display: flex;
            align-items: center;
            white-space: nowrap;
            animation: marquee 25s linear infinite;
        }
        
        @keyframes marquee {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        
        .info-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin: 2rem auto;
            max-width: 80%;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
        
        .info-section h2 {
            font-size: 2.2rem;
            margin-bottom: 20px;
            color: #0d5c75;
        }
        
        .info-section p {
            font-size: 1.1rem;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            color: #555;
        }
        
        .disease-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            max-width: 90%;
            margin: 3rem auto;
        }
        
        .disease-box {
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .disease-box-content {
            flex-grow: 1;
        }
        
        .disease-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border-color: #bbdefb;
        }
        
        .disease-box h3 {
            font-size: 1.8rem;
            margin: 15px 0;
            color: #0d5c75;
        }
        
        .disease-box p {
            font-size: 1rem;
            line-height: 1.6;
            margin-bottom: 25px;
            color: #555;
        }
        
        .disease-box button {
            background: #0d5c75;
            color: white;
            border: none;
            padding: 10px 25px;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: auto;
        }
        
        .disease-box button:hover {
            background: #0d47a1;
            transform: translateY(-2px);
        }
        
        .disease-box .icon {
            font-size: 3rem;
            margin-bottom: 15px;
            color: #25DAC5;
        }
        
        .health-tips-section {
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin: 3rem auto;
            max-width: 80%;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
        
        .health-tips-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .health-tips-header h2 {
            font-size: 2rem;
            color: #0d5c75;
            margin-bottom: 10px;
        }
        
        .health-tips-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .health-tip {
            background: #e3f2fd;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s ease;
            border-left: 4px solid #0d5c75;
        }
        
        .health-tip:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 10px rgba(0,0,0,0.08);
        }
        
        .health-tip h4 {
            color: #0d47a1;
            margin-top: 0;
            margin-bottom: 10px;
            font-size: 1.3rem;
        }
        
        .health-tip p {
            color: #555;
            margin-bottom: 0;
        }
                
        #backToTop {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #0d5c75;
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.3rem;
            cursor: pointer;
            display: none;
            justify-content: center;
            align-items: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        #backToTop:hover {
            background: #0d47a1;
            transform: translateY(-3px);
        }
        
        #chatButton {
            position: fixed;
            bottom: 30px;
            left: 30px;
            background: #0d5c75;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 1.5rem;
            cursor: pointer;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
            transition: all 0.3s ease;
            z-index: 1000;
        }
        
        #chatButton:hover {
            background: #0d47a1;
            transform: scale(1.05);
        }
        
        footer {
            background: #0d5c75;
            padding: 40px 0 20px;
            text-align: center;
            margin-top: 4rem;
            color: white;
        }
        
        footer p {
            font-size: 1.1rem;
            margin-bottom: 20px;
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .footer-link {
            color: white;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .footer-link:hover {
            color: #bbdefb;
            text-decoration: underline;
        }
        
        .copyright {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-top: 20px;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .info-section, .disease-box, .marquee-container, 
        .health-tips-section, .health-game-section {
            animation: fadeIn 0.8s ease forwards;
        }
        
        @media (max-width: 768px) {
            .header-title {
                font-size: 2.5rem !important;
            }
            
            .disease-grid, .health-tips-grid {
                grid-template-columns: 1fr;
                max-width: 95%;
            }
            
            .info-section, .health-tips-section, .health-game-section {
                max-width: 95%;
                padding: 20px;
            }
            
            .options-container {
                grid-template-columns: 1fr;
            }
        }
    </style>

    <script>
    // Permanent sidebar lockdown
    document.addEventListener('DOMContentLoaded', function() {
        // Immediate sidebar removal
        const style = document.createElement('style');
        style.textContent = `
            [data-testid="stSidebar"],
            [data-testid="collapsedControl"] {
                display: none !important;
                visibility: hidden !important;
            }
        `;
        document.head.appendChild(style);

        // Click event blocker
        document.body.addEventListener('click', function(e) {
            if (e.target.closest('[data-testid="collapsedControl"]')) {
                e.stopImmediatePropagation();
                e.preventDefault();
            }
        }, true);

        // Continuous layout enforcement
        const enforceLayout = () => {
            document.querySelectorAll('[data-testid="stSidebar"]').forEach(el => {
                el.style.transform = 'translateX(-100%)';
                el.style.width = '0';
            });
            document.querySelector('.stApp').style.marginLeft = '0';
        };

        // Run immediately and every second
        enforceLayout();
        setInterval(enforceLayout, 1000);

        // MutationObserver for dynamic changes
        new MutationObserver(enforceLayout).observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Scroll to Top functionality
        const backToTopButton = document.getElementById("backToTop");
        window.onscroll = () => {
            if (document.documentElement.scrollTop > 100) {
                backToTopButton.style.display = "flex";
            } else {
                backToTopButton.style.display = "none";
            }
        };
        
        function scrollToTop() {
            window.scrollTo({ top: 0, behavior: "smooth" });
        }
    });
    
    </script>
    """, unsafe_allow_html=True)

# Title Header
st.markdown("<h1 class='header-title'>NEO Health AI</h1>", unsafe_allow_html=True)

# Live Health Tips Marquee
st.markdown(
    """
    <div class="marquee-container">
        <div class="marquee">
            Health Tips: 💧 Drink 8 glasses of water daily | 🥗 Include vegetables in every meal | 🏃‍♂️ 30 minutes of exercise daily | 😴 Aim for 7-9 hours of sleep | 🧘‍♀️ Practice mindfulness for stress | 🩺 Schedule annual checkups | 🍎 Eat fruits for snacks | 🚭 Avoid tobacco products | 🍷 Limit alcohol to moderate levels | ☀️ Use sunscreen daily
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Info Section
st.markdown(
    """
    <div class="info-section">
        <h2>Empowering Your Health Journey</h2>
        <p>We provide AI-powered health insights to help you make informed decisions about your well-being. Our advanced algorithms analyze health data to identify potential risks and offer personalized recommendations.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Disease Prediction Modules with aligned buttons
st.markdown(
    """
    <div class="disease-grid">
        <div class="disease-box">
            <div class="disease-box-content">
                <div class="icon">🩸</div>
                <h3>Diabetes Predictor</h3>
                <p>Assess your risk for diabetes based on lifestyle and health metrics with our AI analysis.</p>
            </div>
            <a href="/Diabetes_Predictor" target="_self"><button>Check Now</button></a>
        </div>
        <div class="disease-box">
            <div class="disease-box-content">
                <div class="icon">🤒</div>
                <h3>Fever Type Predictor</h3>
                <p>Identify potential causes of fever based on symptoms and vital signs.</p>
            </div>
            <a href="/Fever_Type_Predictor" target="_self"><button>Check Now</button></a>
        </div>
        <div class="disease-box">
            <div class="disease-box-content">
                <div class="icon">🦋</div>
                <h3>Thyroid Checker</h3>
                <p>Evaluate potential thyroid imbalances through comprehensive symptom analysis.</p>
            </div>
            <a href="/Thyroid_Predictor" target="_self"><button>Check Now</button></a>
        </div>
        <div class="disease-box">
            <div class="disease-box-content">
                <div class="icon">💪</div>
                <h3>Blood Pressure Checker</h3>
                <p>Monitor your blood pressure status and receive personalized recommendations.</p>
            </div>
            <a href="/Blood_Pressure_Predictor" target="_self"><button>Check Now</button></a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Health Tips Section
st.markdown(
    """
    <div class="health-tips-section">
        <div class="health-tips-header">
            <h2>Daily Health Tips</h2>
            <p>Practical advice for maintaining a healthy lifestyle</p>
        </div>
        <div class="health-tips-grid">
            <div class="health-tip">
                <h4>Hydration</h4>
                <p>Start your day with a glass of water and carry a water bottle to ensure you drink 8 glasses throughout the day.</p>
            </div>
            <div class="health-tip">
                <h4>Nutrition</h4>
                <p>Fill half your plate with colorful vegetables and fruits at every meal for essential vitamins and fiber.</p>
            </div>
            <div class="health-tip">
                <h4>Exercise</h4>
                <p>Aim for at least 150 minutes of moderate exercise weekly - even short 10-minute sessions add up.</p>
            </div>
            <div class="health-tip">
                <h4>Sleep Quality</h4>
                <p>Maintain a consistent sleep schedule and create a dark, quiet bedroom environment for better rest.</p>
            </div>
            <div class="health-tip">
                <h4>Stress Management</h4>
                <p>Practice deep breathing exercises for 5 minutes daily to reduce stress and improve mental clarity.</p>
            </div>
            <div class="health-tip">
                <h4>Preventive Care</h4>
                <p>Schedule annual checkups even when you feel healthy - early detection is key for many health conditions.</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Back to Top Button
st.markdown(
    """
    <button id="backToTop" onclick="scrollToTop()">↑</button>
    """,
    unsafe_allow_html=True
)

# Floating Chat Button
st.markdown(
    """
    <button id="chatButton" onclick="alert('Chat with our health assistant! Our virtual nurse is available 24/7 to answer your health questions.')">💬</button>
    """,
    unsafe_allow_html=True
)

# Footer Section
st.markdown(
    """
    <footer>
        <div class="footer-links">
            <a href="#" class="footer-link">About Us</a>
            <a href="#" class="footer-link">Privacy Policy</a>
            <a href="#" class="footer-link">Terms of Service</a>
            <a href="#" class="footer-link">Contact</a>
            <a href="#" class="footer-link">FAQs</a>
        </div>
        <p>Stay healthy, stay strong. Together, we predict and prevent!</p>
        <p class="copyright">© 2023 NEO Health AI. All rights reserved. This content is for informational purposes only and not medical advice.</p>
    </footer>
    """,
    unsafe_allow_html=True
)