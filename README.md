# Diabetes Care Portal

A Streamlit-based Diabetes Care Portal featuring patient authentication, real-time ML risk assessment, and a personal health dashboard for tracking medical history.

## Key Features
*   **Secure Authentication**: Patient registration and login system.
*   **AI Risk Assessment**: Uses a Stacked Ensemble Random Forest model to predict diabetes risk based on health metrics (Glucose, BMI, Blood Pressure, etc.).
*   **Patient Dashboard**: A personalized view for users to manage their health profile.
*   **History Tracking**: integrated database to save and retrieve past assessment results over time.
*   **Professional UI**: Designed with a clean, medical-grade interface using custom CSS.

## Tech Stack
*   **Frontend/App**: Streamlit
*   **ML Model**: Scikit-Learn (Random Forest)
*   **Database**: MySQL / SQLite supported
*   **Data Processing**: Pandas, Joblib

## Installation

1. Clone the repository:
```bash
git clone https://github.com/AkashNambula/diabetes-prediction-1.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

MY PROJECT DEMO VIDEO LINK:
https://drive.google.com/file/d/1ib5h_aGJgiEPktSSpMoW2E1x1ObiUQGP/view?usp=sharing
