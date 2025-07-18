# app.py
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
from PIL import Image
import folium
from streamlit_folium import st_folium
import plotly.express as px

# Set up paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'model.pkl')
scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')
data_path = os.path.join(BASE_DIR, '..', 'data', 'cleaned_spacex_launches.csv')
image_path = os.path.join(BASE_DIR, 'launch_site.jpg')  # ✅ RELATIVE path

# Load assets
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
df = pd.read_csv(data_path)

# App title
st.title("🛰️ SpaceY Launch Dashboard")

# Display image
st.subheader("🚀 SpaceX Launch Site Overview")
try:
    image = Image.open(image_path)
    st.image(image, caption="Primary Launch Location - SpaceX", use_container_width=True)
except FileNotFoundError:
    st.warning("Launch site image not found. Please check the file path or upload it to your repo.")

# Sidebar inputs
st.sidebar.title("🔧 Launch Prediction Input")
mass = st.sidebar.slider("Payload Mass (kg)", 0, 10000, 5000)
site = st.sidebar.selectbox("Launch Site", df['Launch site'].unique())
orbit = st.sidebar.selectbox("Orbit", df['Orbit'].unique())
booster = st.sidebar.selectbox("Booster Version", df['Version, booster[h]'].unique())

# Encode input
input_df = pd.DataFrame({
    'Payload mass': [mass],
    'Launch site': [site],
    'Orbit': [orbit],
    'Version, booster[h]': [booster]
})
input_encoded = pd.get_dummies(input_df)

# Align with model input
X_columns = model.feature_names_in_
for col in X_columns:
    if col not in input_encoded.columns:
        input_encoded[col] = 0
input_encoded = input_encoded[X_columns]

# Scale + Predict
input_scaled = scaler.transform(input_encoded)
prediction = model.predict(input_scaled)[0]
confidence = model.predict_proba(input_scaled)[0][int(prediction)]

# Show prediction
st.subheader("🎯 Launch Prediction Result")
st.success("✅ Booster Landing Successful!" if prediction == 1 else "❌ Booster Failed to Land.")
st.write(f"📊 Prediction Confidence: **{confidence * 100:.2f}%**")

# Map
st.subheader("🗺️ Launch Site Map")
m = folium.Map(location=[28.5, -80.6], zoom_start=3)
for site in df['Launch site'].unique():
    folium.Marker(location=[28.5, -80.6], popup=site).add_to(m)
st_folium(m, width=700)

# Orbit Plot
st.subheader("📈 Orbit vs Success Rate")
orbit_plot = df.groupby('Orbit')['Landing_Success'].mean().reset_index()
fig = px.bar(orbit_plot, x='Orbit', y='Landing_Success', title='🚀 Orbit vs Landing Success Rate')
st.plotly_chart(fig) 

#streamlit run app.py