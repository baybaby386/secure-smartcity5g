import streamlit as st
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from streamlit_option_menu import option_menu
import base64

# ------------------ App Config ------------------
st.set_page_config(page_title="Smart City Security", layout="wide")

# ------------------ Background Setup ------------------
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

def set_background(png_file):
    bin_str = get_base64(png_file)
    if bin_str:
        st.markdown(f'''
            <style>
            .stApp {{
                background-image: url("data:image/jpeg;base64,{bin_str}");
                background-size: cover;
            }}
            </style>
        ''', unsafe_allow_html=True)

set_background('background/3.jfif')

# ------------------ Navigation Menu ------------------
selected = option_menu(None, ["Home", "Overview", "Prediction"],
    icons=["house", "info-circle", "shield-check"], default_index=0,
    orientation="horizontal")

if selected == "Home":
    st.title("🏙️ Welcome to Smart City Security")
    st.image("1.jpg", width=500)

elif selected == "Overview":
    st.title("📜 Project Overview")
    st.markdown("""
    - 📶 **Real-time threat detection** using **federated learning**
    - 🧠 **Hybrid XGBoost + LightGBM** for intelligent classification
    - 🔒 **Privacy-Focused**: No direct scanning of devices!
    """)

elif selected == "Prediction":
    st.title("🔍 AI-Powered Threat Prediction")
    
    # Load model once at start
    @st.cache(allow_output_mutation=True)
    def load_ai_model():
        return load_model("Model.h5")

    model = load_ai_model()
    class_labels = ['Normal', 'Dos', 'Probe', 'R2L', 'U2R']

    input_mode = st.radio("Select Input Mode", ["Manual Entry", "CSV Upload"])

    def predict(data):
        data = np.array(data).reshape(data.shape[0], data.shape[1], 1)
        preds = model.predict(data)
        return [class_labels[i] for i in np.argmax(preds, axis=1)]

    if input_mode == "Manual Entry":
        sample_input = [0.] * 32  # Example 32 features
        user_input = st.text_area("Enter 32 comma-separated values", value=", ".join(map(str, sample_input)))

        if st.button("Predict"):
            try:
                values = list(map(float, user_input.strip().split(',')))
                if len(values) != 32:
                    st.error("❌ Enter exactly 32 values.")
                else:
                    result = predict([values])
                    st.success(f"✅ Predicted Class: {result[0]}")
            except:
                st.error("Invalid input. ❌")

    elif input_mode == "CSV Upload":
        uploaded_file = st.file_uploader("📂 Upload CSV with 32 features", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            if df.shape[1] != 32:
                st.error("CSV must have exactly 32 columns. ❌")
            else:
                st.success("✅ File loaded.")
                if st.button("Predict All"):
                    pred = predict(df.values)
                    df['Prediction'] = pred
                    st.dataframe(df)
                    st.download_button("Download Results", df.to_csv(index=False), "results.csv", "text/csv")
