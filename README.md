![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white) 
![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-FF4B4B?logo=streamlit&logoColor=white) 
![Status](https://img.shields.io/badge/Status-Completed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-lightgrey)
![GitHub last commit](https://img.shields.io/github/last-commit/Arvindhbabu/Data-Science-Capstone-Project)


# 🚀 SpaceY Launch Prediction Dashboard

An interactive machine learning-powered web dashboard that predicts the success of SpaceX booster landings using public data, logistic regression, and modern data visualization tools.

> 🌐 Live App: [Click here to visit](https://your-streamlit-link.streamlit.app)  
> 📁 Repo: [GitHub Source Code](https://github.com/your-username/spacey-dashboard)



## 🧠 Project Overview

This capstone project simulates the role of a **data scientist at SpaceY**, a fictional competitor to SpaceX. Using publicly available SpaceX launch data, we:

- Predict whether the **booster will land successfully**
- Visualize success rates across **orbits** and **launch sites**
- Provide an interactive tool for engineers and stakeholders

  
![Project](https://github.com/Arvindhbabu/Data-Science-Capstone-Project/blob/88aba9293e653fb7946867a89d2f0414b46c8562/dashboard/Description.png)
---

## 📊 Features

| Feature | Description |
|--------|-------------|
| 🚀 **Launch Simulation Inputs** | Select payload mass, orbit type, booster version, and launch site |
| ✅ **Booster Landing Prediction** | ML model predicts whether the booster will land |
| 📈 **Prediction Confidence** | Displays probability/confidence in prediction |
| 🌐 **Launch Site Map** | Interactive Folium map showing launch locations |
| 📉 **Orbit vs Success Rate** | Plotly visualization of orbit-wise success trends |

---

## 💻 Tech Stack

- **Python 3.10**
- **Pandas, NumPy** – Data wrangling
- **Scikit-learn** – Model training (Logistic Regression)
- **Joblib** – Model serialization
- **Plotly** – Interactive orbit visualizations
- **Folium + streamlit-folium** – Maps
- **Streamlit** – Dashboard frontend & backend

---

## 📁 Project Structure

spacey_capstone/

├── dashboard/  
 
│   ├── app.py                 
│   ├── model.pkl              
│   └── scaler.pkl

├──data/  
│   ├──cleaned_spacex_launches.csv  

├──notebooks/                
│   ├── SpaceY_Modeling.ipynb   

├── requirements.txt          
├──README.md             


---



### 🛰️ Launch Site
![Launch Sites](https://github.com/Arvindhbabu/Data-Science-Capstone-Project/blob/0cfae298937dc597a9f7c7b687c070f4761cd82a/dashboard/launch_site.jpg)

---

## 🚧 How It Works

1. Load historical SpaceX launch data
2. Clean and one-hot encode categorical variables
3. Train a **logistic regression** model to predict success (1 = landed, 0 = failed)
4. Build a **Streamlit dashboard** to accept launch parameters as user input
5. Predict in real-time and display result + visualizations

---

## 📦 Installation & Local Use

```bash
git clone https://github.com/your-username/spacey-dashboard.git
cd spacey-dashboard
pip install -r requirements.txt
streamlit run dashboard/app.py


