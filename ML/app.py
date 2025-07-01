from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import streamlit as st


class TitanicInput(BaseModel):
    Pclass: int
    Sex: str
    Age: float
    Fare: float
    Embarked: str


app = FastAPI()

# Load the trained model
model = joblib.load("Cours-Data-Science-M2/ML/titanic_pipeline.pkl")


@app.post("/predict")
def predict(data: TitanicInput):
    df = pd.DataFrame([data.dict()])
    prediction = model.predict(df)[0]
    return {"prediction": int(prediction)}


# Streamlit app for Titanic survival prediction
st.set_page_config(
    page_title="Titanic Survival Predictor",
    page_icon="🚢",
    layout="wide"
)
st.title("🚢 Titanic Survival Predictor")
st.markdown("---")

st.info(
    "📊 This machine learning model predicts whether a passenger would have survived the Titanic disaster based on "
    "their characteristics.")

st.subheader("👤 Enter Passenger Information")

# User inputs
input_col1, input_col2 = st.columns(2)

with input_col1:
    Pclass = st.selectbox(
        "🎫 Passenger Class",
        [1, 2, 3],
        help="1 = First Class, 2 = Second Class, 3 = Third Class"
    )

    Sex = st.selectbox(
        "👤 Gender",
        ["male", "female"]
    )

    Age = st.slider(
        "🎂 Age",
        min_value=0,
        max_value=100,
        value=25,
        help="Age in years"
    )

with input_col2:
    Fare = st.slider(
        "💰 Fare",
        min_value=0.0,
        max_value=500.0,
        value=32.0,
        help="Ticket price in pounds"
    )

    Embarked = st.selectbox(
        "🏙️ Port of Embarkation",
        ["S", "C", "Q"],
        help="S = Southampton, C = Cherbourg, Q = Queenstown"
    )

st.markdown("---")

# Prediction button
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
with col_btn2:
    predict_button = st.button("🔮 Predict Survival", type="primary", use_container_width=True)

# Prediction result
if predict_button:
    X_new = pd.DataFrame([[Pclass, Sex, Age, Fare, Embarked]],
                         columns=["Pclass", "Sex", "Age", "Fare", "Embarked"])
    pred = model.predict(X_new)
    probability = model.predict_proba(X_new)[0]

    st.markdown("### 📋 Prediction Result")

    if pred[0] == 1:
        st.success(f"✅ **SURVIVED** - Probability: {probability[1]:.2%}")
        st.balloons()
    else:
        st.error(f"❌ **DID NOT SURVIVE** - Probability: {probability[0]:.2%}")

    st.markdown("### 📊 Additional Information")

    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.metric("Survival Probability", f"{probability[1]:.1%}")
    with info_col2:
        st.metric("Risk Level", f"{probability[0]:.1%}")

# To run this app: streamlit run Cours-Data-Science-M2/ML/app.py
