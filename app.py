import streamlit as st


st.set_page_config(
    page_title="NEO Health AI",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        /* Nuclear sidebar removal */
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

        /* Main content full width fix */
        .stApp {
            margin-left: 0 !important;
            margin-right: 0 !important;
            padding: 0 !important;
            max-width: 100vw !important;
        }

        /* Remove header residual space */
        header[data-testid="stHeader"] {
            display: none !important;
        }

        /* Block container adjustments */
        .block-container {
            padding: 1rem 0 0 0 !important;
            max-width: 100% !important;
        }

        /* Override any inline styles */
        div[style*="transform: translateX(0px)"] {
            transform: translateX(-100%) !important;
            transition: none !important;
        }
            /* Bigger header and box text */
        .header-title {
            font-size: 5rem !important;
            font-weight: bold !important;
            text-align: left !important;
            margin-left: 15% !important; /* Leftish center */
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
    });
    </script>
    """, unsafe_allow_html=True)

# Load custom CSS for styling
def load_css():
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Rest of your original code remains unchanged below this line
# ... [Keep all your existing HTML components and JavaScript] ...


# Title Header
st.markdown("<h1 class='header-title'>🔬NEO Health AI</h1>", unsafe_allow_html=True)

# Live Health Tips Marquee
st.markdown(
    """
    <div class="marquee">
        <span>Health Tips: 💧 Stay Hydrated | 🥗 Eat Balanced Meals | 🏃‍♂️ Exercise Regularly | 😴 Get Enough Sleep | 🧘‍♀️ Avoid Stress | 🩺 Regular Checkups Matter</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Info Section
st.markdown(
    """
    <div class="info-section">
        <h2>Empowering You for a Healthier Life</h2>
        <p>We provide AI-powered medical predictions to help you stay ahead of potential health risks.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Disease Prediction Modules
st.markdown(
    """
    <div class="disease-grid">
        <div class="disease-box">
            <h3>🩸</h3>
            <h3>Diabetes Predictor</h3>
            <p>Evaluate your diabetes risk with AI-based analysis.</p>
            <a href="/Diabetes_Predictor" target="_self"><button>Check Now</button></a>
        </div>
        <div class="disease-box">
            <h3>🤒</h3>
            <h3>Fever Type Predictor</h3>
            <p>Identify the type of fever you might have.</p>
            <a href="/Fever_Type_Predictor" target="_self"><button>Check Now</button></a>
        </div>
        <div class="disease-box">
            <h3>🦋</h3>
            <h3>Thyroid Checker</h3>
            <p>Detect potential thyroid imbalances.</p>
            <a href="/Thyroid_Predictor" target="_self"><button>Check Now</button></a>
        </div>
        <div class="disease-box">
            <h3>💪</h3>
            <h3>Blood Pressure Checker</h3>
            <p>Monitor your blood pressure status.</p>
            <a href="/Blood_Pressure_Predictor" target="_self"><button>Check Now</button></a>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Back to Top Button
st.markdown(
    """
    <button id="backToTop" onclick="scrollToTop()">🔝 Back to Top</button>
    """,
    unsafe_allow_html=True
)
# Floating Chat Button
st.markdown(
    """
    <button id="chatButton" onclick="alert('Chat feature coming soon!')">💬 Chat</button>
    """,
    unsafe_allow_html=True
)

# Footer Section
st.markdown(
    """
    <footer>
        <p id = "footer_1" Stay healthy, stay strong. Together, we predict and prevent!></p>
    </footer>
    """,
    unsafe_allow_html=True
)

# JavaScript for interactivity
st.markdown(
    """
    <script>
        // Scroll to Top functionality
        const backToTopButton = document.getElementById("backToTop");
        window.onscroll = () => {
            if (document.documentElement.scrollTop > 100) {
                backToTopButton.style.display = "block";
            } else {
                backToTopButton.style.display = "none";
            }
        };
        function scrollToTop() {
            window.scrollTo({ top: 0, behavior: "smooth" });
        }

    </script>
    """,
    unsafe_allow_html=True
)