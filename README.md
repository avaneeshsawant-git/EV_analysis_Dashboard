# 🇮🇳 India EV Adoption & ICE → EV Transition Analysis

An **AI-driven interactive dashboard** that analyzes India’s transition from  
**Internal Combustion Engine (ICE)** vehicles to **Electric Vehicles (EVs)**  
using real vehicle registration data.

Built with **Streamlit**, **Python**, and **Machine Learning**, the project focuses on
**trend analysis, regional comparison, adoption drivers, readiness assessment, and forecasting**.

---

## 📌 Problem Statement

India’s EV adoption is increasing, but the transition from ICE vehicles is **uneven across states and vehicle segments**.  
Despite similar economic conditions, some regions adopt EVs rapidly while others lag behind.

This inconsistency makes it difficult for:
- Policymakers to design targeted EV policies
- Manufacturers to plan production and supply chains
- Infrastructure planners to allocate charging resources effectively

---

## 🎯 Objectives

- Analyze **EV vs ICE distribution** across Indian states
- Track **EV adoption trends over time**
- Identify **key drivers of EV adoption**
- Compare **regional EV penetration**
- Build a **state-level EV Readiness Index**
- **Forecast future EV adoption** using an AI model
- Present insights via an **interactive dashboard**

---

## 🧠 Solution Overview

The solution is an **interactive Streamlit dashboard** that enables users to:
- Explore EV adoption trends by state and vehicle segment
- Compare EV penetration across regions
- Understand market-level drivers influencing EV adoption
- Measure state readiness for EV transition
- Predict future EV market share using Machine Learning

The design prioritizes **interpretability, usability, and decision support** over black-box prediction.

---

## 📊 Dashboard Features

### 1️⃣ Market Trends
- EV share growth over time
- ICE vs EV substitution analysis
- Year-wise and segment-wise trends

### 2️⃣ Regional Comparison
- State-wise EV penetration ranking
- Identification of leading and lagging states

### 3️⃣ Drivers of EV Adoption
- Relationship between total vehicle market size and EV penetration
- Highlights adoption patterns beyond market scale

### 4️⃣ EV Readiness Index
A composite score (0–100) based on:
- Current EV penetration
- EV growth momentum

Helps identify states most prepared for accelerated EV transition.

### 5️⃣ Forecasting (AI Component)
- Linear Regression model
- Interactive year selector
- Predicts future EV adoption percentage
- Explainable and policy-friendly forecasting

---

## 🤖 Machine Learning Model

- **Model Used:** Linear Regression  
- **Target Variable:** EV market share (%)  

### Why Linear Regression?
- Suitable for limited historical time-series data
- High interpretability for policymakers
- Avoids overfitting and black-box behavior

**Performance:**
- Explains ~85–95% variance (R²) in historical EV adoption trends
- Designed for **short-term trend forecasting**, not exact numeric prediction

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **Data Processing:** Pandas, NumPy  
- **Visualization:** Plotly  
- **Machine Learning:** Scikit-learn  

---

## 📂 Dataset

- Indian EV & ICE vehicle registration data
- State-wise vehicle segmentation data
- EV policy dataset (contextual)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/india-ev-transition.git
cd india-ev-transition

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate


pip install -r requirements.txt

streamlit run app.py
```





