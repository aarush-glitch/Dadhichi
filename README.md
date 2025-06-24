# Dadhichi 💪

Team: CodeK  
Product: Dadhichi (named after the saint known for self-sacrifice)


 🚀 Overview

Dadhichi is an integrated fitness companion that bridges gaps in existing fitness apps – combining real-time form correction, LLM chatbot guidance, workout planning, wearable insights, nutrition analysis, and community support in a single platform.


## 🎯 Features

1. Real-time Pose Correction  
   - Uses OpenCV and MediaPipe for live form feedback during exercises.

2. LLM-powered Chatbot  
   - Built with Ollama’s Llama 3.2 model to provide motivation, Q&A support, and emotional check‑ins.

3. Smart Workout Planner
   - Also driven by Llama 3.2, creating tailored workout routines based on user goals.

4. Fitbit Integration
   - Utilizes the Fitbit API to fetch user activity data (steps, sleep, heart rate) and generate daily recommendations.

5. Macro Analysis  
   - Uses a CSV dataset to analyze and provide macro-nutrient insights (proteins, carbs, fats).

6. Community Features**  
   - Enables users to share progress, tips, challenges, and stay accountable.

7. **User Authentication & Data Storage**  
   - Firebase Auth for secure user sign-up/login.  
   - Cloud Firestore to store workout plans, progress logs, and community interactions.

---

## 🛠 Tech Stack

- **UI & App Framework:** Streamlit  
- **Computer Vision:** OpenCV | MediaPipe  
- **Large Language Model:** Ollama – Llama 3.2  
- **Wearable Integration:** Fitbit API  
- **Backend & DB:** Firebase Authentication & Firestore  
- **Macro Data Handling:** CSV-based lookup table

---

## ⚙️ Setup & Run

1. Clone the repo*
   ```bash
   git clone <REPO_URL>
   cd dadhichi
   
2. Install dependencies
   pip install -r requirements.txt
   
3. Configure environment variables
Set up:

FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET

FIREBASE_API_KEY, etc.

4. Launch the app

bash
Copy
Edit
streamlit run account.py
