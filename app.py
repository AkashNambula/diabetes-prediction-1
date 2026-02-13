
import streamlit as st
import pandas as pd
import joblib
import base64
from auth import init_database, register_user, login_user, save_prediction, get_user_predictions
import time

# Page configuration
st.set_page_config(
    page_title="Diabetes Care Portal", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Colors - Professional Hospital Palette
PRIMARY_COLOR = "#0077b6"  # Medical Blue
SECONDARY_COLOR = "#023e8a" # Deep Blue
ACCENT_COLOR = "#00b4d8"    # Light Blue
BACKGROUND_COLOR = "#ffffff" # Clean White
TEXT_COLOR = "#333333"       # Dark Gray
LIGHT_GRAY = "#f8f9fa"       # Very Light Gray for backgrounds

# Custom CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

    /* Global Typography */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        color: {TEXT_COLOR};
    }}
    
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Poppins', sans-serif;
        color: {SECONDARY_COLOR};
        font-weight: 600;
        margin-bottom: 0.5rem;
    }}

    /* =========================================
       1. PROFESSIONAL MEDICAL BACKGROUND (IMAGE)
       ========================================= */
       /* Handled via Python injection below to use local file */

    /* =========================================
       2. LAYOUT & SCROLLING FIXES
       ========================================= */
    /* Aggressive padding removal to prevent scrolling */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        max-width: 100%;
    }}
    
    /* Header Navigation Simulation */
    .header-nav {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 2rem;
        background-color: white;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 0.5rem; /* Reduced margin */
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    .logo-text {{
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        font-size: 1.4rem;
        color: {PRIMARY_COLOR};
    }}
    .nav-link {{
        color: {TEXT_COLOR};
        text-decoration: none;
        margin-left: 20px;
        font-weight: 500;
        font-size: 0.9rem;
    }}

    /* Login Card - Centered with Shadow */
    .login-container-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh; /* Full viewport height */
    }}
    
    /* Input Fields styling */
    .stTextInput input {{
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 0.75rem;
        font-size: 0.95rem;
        background-color: white;
    }}
    .stTextInput input:focus {{
        border-color: {PRIMARY_COLOR};
        box-shadow: 0 0 0 2px rgba(0, 119, 182, 0.2);
    }}
    
    /* Buttons */
    .stButton button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        font-weight: 500;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.2s ease;
    }}
    .stButton button:hover {{
        background-color: {SECONDARY_COLOR};
        box-shadow: 0 4px 6px rgba(0,0,0,0.15);
    }}
    
    /* Custom Footer - Fixed at bottom */
    .footer {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        padding: 1rem;
        text-align: center;
        color: rgba(255,255,255,0.8); /* Light text for contrast */
        font-size: 0.8rem;
        background: transparent; /* Or subtle gradient if needed */
        z-index: 100;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: white;
        border-right: 1px solid #eee;
    }}
    
    /* Removing default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Login Card Specifics for Contrast */
    [data-testid="stForm"] {{
        background-color: white !important;
        border: 2px solid {PRIMARY_COLOR};
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    </style>
    """, unsafe_allow_html=True)

# Helper function for card container
def card_container():
    return st.container(border=True)

# Initialize Resources
@st.cache_resource
def load_resources():
    try:
        model = joblib.load('stacked_ensemble_rf_model.pkl')
        scaler = joblib.load('scaler.joblib')
        return model, scaler
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None, None

@st.cache_resource
def init_db():
    init_database()

init_db()

# Session State
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'register_mode' not in st.session_state:
    st.session_state.register_mode = False

# Function to add background image (Diabetes Specific)
def add_bg_image(image_name='diabetes_bg_v3.png'):
    import os
    if os.path.exists(image_name):
        with open(image_name, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url(data:image/png;base64,{encoded_string});
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            /* Ensure main container is transparent */
            .main .block-container {{
                background: transparent;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# ==================== LOGIN PAGE ====================
def login_page():
    add_bg_image() # Inject specific background
    
    # Header
    st.markdown(f"""
        <div class="header-nav">
            <div class="logo-text">Diabetes Care Portal</div>
            <div>
                <span class="nav-link" style="color:#666">Patient Access</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Main Content - Centered Login using Columns for spacing
    # Using 'cols' to push content to center
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True) # Reduced Spacer
        
        # Login Card
        with st.container(border=True):
            st.markdown(f"""
                <div style="text-align: center; padding-bottom: 15px;">
                    <h2 style="color: {PRIMARY_COLOR}; margin:0;">Patient Login</h2>
                    <p style="color: #666; font-size: 0.85rem; margin-top:5px;">Secure Personal Health Portal</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                st.markdown("<br>", unsafe_allow_html=True)
                submit = st.form_submit_button("Sign In", use_container_width=True)
                
                if submit:
                    if username and password:
                        success, user_info, message = login_user(username, password)
                        if success:
                            st.session_state.user_logged_in = True
                            st.session_state.user_info = user_info
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please enter your username and password.")
            
            st.markdown("<div style='margin-top: 15px; text-align: center;'>", unsafe_allow_html=True)
            if st.button("New Patient Registration", type="secondary"):
                st.session_state.register_mode = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
    # Footer
    st.markdown("""
        <div class="footer">
            <p>&copy; 2024 Diabetes Care Portal. Empowering Health.</p>
        </div>
    """, unsafe_allow_html=True)

# ==================== REGISTER PAGE ====================
def register_page():
    # Header
    st.markdown(f"""
        <div class="header-nav">
            <div class="logo-text">Diabetes Care Portal</div>
            <div>
                <span class="nav-link">Patient Registration</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
             st.markdown(f"""
                <div style="text-align: center; padding-bottom: 20px;">
                    <h2 style="color: {PRIMARY_COLOR};">Create Account</h2>
                    <p style="color: #666; font-size: 0.9rem;">Join our diabetes care program.</p>
                </div>
            """, unsafe_allow_html=True)
             
             with st.form("register_form"):
                new_username = st.text_input("Username")
                email = st.text_input("Email Address")
                full_name = st.text_input("Full Name")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.form_submit_button("Register"):
                    if not (new_username and email and full_name and new_password and confirm_password):
                        st.warning("All fields are required.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters.")
                    else:
                        success, msg = register_user(new_username, email, new_password, full_name)
                        if success:
                            st.success("Registration Successful!")
                            time.sleep(1)
                            st.session_state.register_mode = False
                            st.rerun()
                        else:
                            st.error(msg)
            
             st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True)
             if st.button("Return to Login"):
                st.session_state.register_mode = False
                st.rerun()
             st.markdown("</div>", unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main_app():
    # Simple Navbar
    st.markdown(f"""
        <div class="header-nav">
            <div class="logo-text">Diabetes Care Portal</div>
            <div style="display: flex; align-items: center;">
                <span style="margin-right: 15px; font-weight: 500;">Welcome, {st.session_state.user_info['full_name']}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown(f"<h3 style='color:{PRIMARY_COLOR};'>My Health Dashboard</h3>", unsafe_allow_html=True)
        st.markdown("---")
        st.info(f"Member ID: {st.session_state.user_info['username']}")
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("Sign Out"):
            st.session_state.user_logged_in = False
            st.rerun()

    # Main Content
    st.markdown(f"<h2>Diabetes Risk Assessment</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666; margin-bottom: 30px;'>Enter your health metrics below to assess your diabetes risk.</p>", unsafe_allow_html=True)
    
    # Custom Tabs
    tab1, tab2 = st.tabs(["New Assessment", "My Health Records"])
    
    with tab1:
        with st.container(border=True):
            st.markdown(f"<h4 style='color: {PRIMARY_COLOR}; margin-bottom: 20px;'>Health Metrics</h4>", unsafe_allow_html=True)
            
            with st.form("assessment_form"):
                col1, col2 = st.columns(2)
                with col1:
                    pregnancies = st.number_input('Pregnancies', 0, 20, 0)
                    glucose = st.number_input('Glucose (mg/dL)', 0, 500, 100)
                    blood_pressure = st.number_input('Blood Pressure (mmHg)', 0, 200, 70)
                    skin_thickness = st.number_input('Skin Thickness (mm)', 0, 100, 20)
                
                with col2:
                    insulin = st.number_input('Insulin (µU/ml)', 0, 1000, 80)
                    bmi = st.number_input('BMI', 0.0, 100.0, 25.0)
                    dpf = st.number_input('Diabetes Pedigree Function', 0.0, 3.0, 0.5)
                    age = st.number_input('Age (years)', 0, 120, 30)
                    
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Check My Risk", type="primary")
                
                if submitted:
                    model, scaler = load_resources()
                    if model:
                        try:
                            input_data = pd.DataFrame([{
                                'Pregnancies': pregnancies, 'Glucose': glucose, 'BloodPressure': blood_pressure,
                                'SkinThickness': skin_thickness, 'Insulin': insulin, 'BMI': bmi,
                                'DiabetesPedigreeFunction': dpf, 'Age': age
                            }])
                            scaled = scaler.transform(input_data)
                            pred = model.predict(scaled)[0]
                            
                            # Save prediction to DB
                            save_prediction(st.session_state.user_info['id'], 
                                          pregnancies, glucose, blood_pressure, skin_thickness,
                                          insulin, bmi, dpf, age, int(pred))
                            
                            st.write("---") # Visual separator
                            if pred == 0:
                                st.success("Assessment Result: Low Risk (Negative)")
                                st.markdown("**Good news:** Your metrics indicate a low risk for diabetes. Keep maintaining a healthy lifestyle.")
                            else:
                                st.error("Assessment Result: High Risk (Positive)")
                                st.markdown("**Action Required:** Your metrics indicate a potential risk for diabetes. We strongly recommend consulting with a healthcare provider for a comprehensive evaluation.")
                        except Exception as e:
                            st.error(f"Error during prediction: {e}")
                    else:
                        st.error("Model resources failed to load. Please contact support.")
                        st.cache_resource.clear() # Clear cache to retry next time

    with tab2:
        with st.container(border=True):
            st.markdown(f"<h4 style='color: {PRIMARY_COLOR}; margin-bottom: 20px;'>My Past Assessments</h4>", unsafe_allow_html=True)
            
            history = get_user_predictions(st.session_state.user_info['id'])
            if history:
                df = pd.DataFrame(history, columns=['ID', 'Pregnancies', 'Glucose', 'BP', 'Skin', 'Insulin', 'BMI', 'DPF', 'Age', 'Prediction', 'Date'])
                df['Status'] = df['Prediction'].apply(lambda x: 'Low Risk' if x == 0 else 'High Risk')
                
                # Styling the dataframe
                st.dataframe(
                    df[['Date', 'Glucose', 'BMI', 'Age', 'Status']], 
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("You haven't completed any assessments yet.")

    # Footer
    st.markdown("""
        <div class="footer">
            <p>&copy; 2024 Diabetes Care Portal. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

# Router
if st.session_state.user_logged_in:
    main_app()
else:
    if st.session_state.register_mode:
        register_page()
    else:
        login_page()
