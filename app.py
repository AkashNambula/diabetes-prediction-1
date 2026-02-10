import streamlit as st
import pandas as pd
import joblib
from auth import init_database, register_user, login_user, save_prediction, get_user_predictions, get_user_by_id

# Page configuration
st.set_page_config(page_title="Diabetes Prediction App", layout="wide")

# Initialize database
init_database()

# Initialize session state
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
if 'user_info' not in st.session_state:
    st.session_state.user_info = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# Load the saved model and scaler
try:
    loaded_model = joblib.load('stacked_ensemble_rf_model.pkl')
    loaded_scaler = joblib.load('scaler.joblib')
except FileNotFoundError:
    st.error("Error: Model or Scaler file not found. Make sure 'stacked_ensemble_rf_model.pkl' and 'scaler.joblib' are in the same directory.")
    st.stop()

# Function to display login page
def login_page():
    st.title('🔐 Diabetes Prediction App - Login')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True):
            if username and password:
                success, user_info, message = login_user(username, password)
                if success:
                    st.session_state.user_logged_in = True
                    st.session_state.user_info = user_info
                    st.session_state.current_page = 'prediction'
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both username and password")
    
    with col2:
        st.subheader("Register New Account")
        new_username = st.text_input("Create Username", key="register_username")
        email = st.text_input("Email Address", key="register_email")
        full_name = st.text_input("Full Name", key="register_fullname")
        new_password = st.text_input("Create Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
        
        if st.button("Register", use_container_width=True):
            if not (new_username and email and full_name and new_password and confirm_password):
                st.warning("Please fill all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long")
            else:
                success, message = register_user(new_username, email, new_password, full_name)
                if success:
                    st.success(message)
                else:
                    st.error(message)

# Function to display prediction page
def prediction_page():
    st.sidebar.title("🔐 User Profile")
    st.sidebar.write(f"**Welcome, {st.session_state.user_info['full_name']}!**")
    st.sidebar.write(f"Username: {st.session_state.user_info['username']}")
    
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.user_logged_in = False
        st.session_state.user_info = None
        st.session_state.current_page = 'login'
        st.rerun()
    
    st.title('🏥 Diabetes Prediction App')
    st.write('Enter the patient details below to predict if they have diabetes.')
    
    # Create tabs for prediction and history
    tab1, tab2 = st.tabs(["Prediction", "Prediction History"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            pregnancies = st.number_input('Number of Pregnancies', min_value=0, max_value=20, value=1)
            glucose = st.number_input('Glucose Level', min_value=0, max_value=200, value=120)
            blood_pressure = st.number_input('Blood Pressure', min_value=0, max_value=120, value=70)
            skin_thickness = st.number_input('Skin Thickness', min_value=0, max_value=100, value=20)
        
        with col2:
            insulin = st.number_input('Insulin Level', min_value=0, max_value=900, value=79)
            bmi = st.number_input('BMI', min_value=0.0, max_value=70.0, value=25.0)
            dpf = st.number_input('Diabetes Pedigree Function', min_value=0.0, max_value=3.0, value=0.3)
            age = st.number_input('Age', min_value=0, max_value=120, value=30)
        
        # Create a DataFrame from user inputs
        user_input_df = pd.DataFrame({
            'Pregnancies': [pregnancies],
            'Glucose': [glucose],
            'BloodPressure': [blood_pressure],
            'SkinThickness': [skin_thickness],
            'Insulin': [insulin],
            'BMI': [bmi],
            'DiabetesPedigreeFunction': [dpf],
            'Age': [age]
        })
        
        if st.button('🔍 Predict Diabetes', use_container_width=True):
            # Scale the user input using the loaded scaler
            user_input_scaled = loaded_scaler.transform(user_input_df)
            
            # Make prediction
            prediction = loaded_model.predict(user_input_scaled)
            
            # Save prediction to database
            save_prediction(
                st.session_state.user_info['id'],
                pregnancies, glucose, blood_pressure, skin_thickness,
                insulin, bmi, dpf, age, int(prediction[0])
            )
            
            # Display result
            st.divider()
            if prediction[0] == 0:
                st.success('✅ The model predicts: **No Diabetes**')
            else:
                st.warning('⚠️ The model predicts: **Diabetes**')
            st.divider()
        
        st.info("📋 Disclaimer: This is a predictive model and not a medical diagnosis. Please consult with a healthcare professional for accurate diagnosis.")
    
    with tab2:
        st.subheader("Your Prediction History")
        predictions = get_user_predictions(st.session_state.user_info['id'])
        
        if predictions:
            # Create a dataframe from predictions
            df = pd.DataFrame(
                predictions,
                columns=['ID', 'Pregnancies', 'Glucose', 'Blood Pressure', 'Skin Thickness',
                        'Insulin', 'BMI', 'Diabetes Pedigree', 'Age', 'Prediction', 'Date']
            )
            
            # Add prediction label
            df['Prediction Result'] = df['Prediction'].apply(
                lambda x: '✅ No Diabetes' if x == 0 else '⚠️ Diabetes'
            )
            
            # Display the dataframe
            st.dataframe(
                df[['ID', 'Pregnancies', 'Glucose', 'Blood Pressure', 'Insulin', 'BMI', 'Age', 'Prediction Result', 'Date']],
                use_container_width=True
            )
        else:
            st.info("No predictions yet. Make your first prediction above!")

# Main app logic
if st.session_state.user_logged_in:
    prediction_page()
else:
    login_page()
