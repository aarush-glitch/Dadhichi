import requests
import json
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt  # Importing matplotlib for custom bar charts
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.metrics.pairwise import cosine_similarity

ACCESS_TOKEN = ('OMITTED ACCESS TOKEN')

BASE_URL = 'https://api.fitbit.com/1/user/OMITTED'

# Headers for authentication
headers = {
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

# Function to get daily activity data (steps, distance, etc.)
def get_daily_activity(date='today'):
    url = f'{BASE_URL}/activities/date/{date}.json'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['activities'][0]  # Return the first activity data
    else:
        print(f'Error: {response.status_code}')
        return None

# Function to get heart rate data
def get_heart_rate(date='today'):
    url = f'{BASE_URL}/activities/heart/date/{date}/1d.json'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['activities-heart'][0]  # Return the first heart rate data
    else:
        print(f'Error: {response.status_code}')
        return None

# Function to get user's profile info
def get_profile():
    url = f'{BASE_URL}/profile.json'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['user']
    else:
        print(f'Error: {response.status_code}')
        return None

# Function to simulate retrieving user data (for testing, we will generate synthetic data)
def generate_synthetic_data(n_users=100):
    data = {
        'user_id': np.arange(1, n_users + 1),
        'steps': np.random.randint(3000, 10000, n_users),  # Steps per day
        'calories_burned': np.random.randint(150, 350, n_users),  # Calories burned
        'sleep_duration': np.random.uniform(6, 9, n_users),  # Hours of sleep
        'heart_rate': np.random.randint(60, 100, n_users),  # Average heart rate
        'weight': np.random.uniform(50, 90, n_users)  # Weight in kg
    }
    df = pd.DataFrame(data)
    return df

# Weight Prediction Model (Regression)
def predict_weight(df):
    X = df[['steps', 'calories_burned', 'sleep_duration', 'heart_rate']]  # Features
    y = df['weight']  # Target (weight)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Linear Regression Model
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)

    # Random Forest Model
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    # Predict weights on the test set
    lr_predictions = lr_model.predict(X_test)
    rf_predictions = rf_model.predict(X_test)

    # Evaluate the models
    lr_mae = mean_absolute_error(y_test, lr_predictions)
    rf_mae = mean_absolute_error(y_test, rf_predictions)

    lr_r2 = r2_score(y_test, lr_predictions)
    rf_r2 = r2_score(y_test, rf_predictions)

    return {
        'lr_mae': lr_mae,
        'rf_mae': rf_mae,
        'lr_r2': lr_r2,
        'rf_r2': rf_r2
    }

# Fitness Goal Recommendation (Content-based)
def recommend_fitness_goals(df, goal_type, weight_goal, current_weight):
    if goal_type == "Lose Weight":
        target_weight = current_weight - weight_goal
        target_steps = df['steps'].mean() + (weight_goal * 100)
        target_calories = df['calories_burned'].mean() + (weight_goal * 50)
        target_sleep = 7.5
    elif goal_type == "Gain Weight":
        target_weight = current_weight + weight_goal
        target_steps = df['steps'].mean() - (weight_goal * 30)
        target_calories = df['calories_burned'].mean() + (weight_goal * 100)
        target_sleep = 8

    plan = {
        'target_weight': target_weight,
        'steps_goal': target_steps,
        'calories_goal': target_calories,
        'sleep_goal': target_sleep
    }

    return plan

# Streamlit Front-End
def main():
    st.title("Fitbit Data and Fitness Goal Recommendation")

    # Get user's profile data
    profile = get_profile()
    st.subheader("User Profile !")

    if profile:
        st.write(f"Hello, {profile['fullName']}!")
        st.image(profile['avatar150'], width=150)
    else:
        st.write("Could not fetch user profile.")

    # Ask the user for their fitness goal
    st.subheader("Set Your Goal !")
    goal_type = st.selectbox("What is your fitness goal?", ("Lose Weight", "Gain Weight"))

    weight_goal = st.number_input("How much weight do you want to change? (in kg)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)

    # Display synthetic data for now, but this should be replaced by real Fitbit data
    st.subheader("Fitness Data (Simulated) !")
    df = generate_synthetic_data()  # Generate synthetic data for demonstration

    # Show a sample of the user's data
    st.write(df.head())

    # Get current weight from user's data (using synthetic data for demo)
    current_weight = df['weight'].iloc[0]  # For demo, taking the first user's weight

    # Fitness Goal Recommendation
    st.subheader("Fitness Goal Recommendation!")
    recommended_goals = recommend_fitness_goals(df, goal_type, weight_goal, current_weight)

    st.write(f"Recommended Fitness Goals to Achieve Your Target Weight Change of {weight_goal} kg:")
    st.write(f"Target Weight: {recommended_goals['target_weight']} kg")
    st.write(f"Steps Goal: {recommended_goals['steps_goal']} steps per day")
    st.write(f"Calories Goal: {recommended_goals['calories_goal']} calories burned per day")
    st.write(f"Sleep Goal: {recommended_goals['sleep_goal']} hours of sleep per day")

    # Additional tips based on goal type
    st.subheader("Additional Tips for Your Fitness Journey!")
    if goal_type == "Lose Weight":
        st.write("""
            - Aim to achieve your daily steps goal consistently.
            - Maintain a calorie deficit (burning more than you consume).
            - Ensure you get enough sleep, as rest is crucial for weight loss and recovery.
            - Stay hydrated and focus on balanced nutrition.
        """)
    else:
        st.write("""
            - Focus on strength training exercises to build muscle.
            - Ensure a calorie surplus (consume more than you burn).
            - Get adequate sleep for muscle recovery.
            - Stay hydrated and prioritize protein in your diet.
        """)

    # Display graphs at the end
    st.subheader("Analysis of past performance!")

    # Bar chart for Steps per day
    st.write("Steps per day")
    st.bar_chart(df['steps'])

    # Bar chart for Heart Rate per day
    st.write("Heart rate per day")
    st.bar_chart(df['heart_rate'])

    # Bar chart for Calories burned per day
    st.write("Calories burned per day")
    st.bar_chart(df['calories_burned'])

if __name__ == "__main__":
    main()
