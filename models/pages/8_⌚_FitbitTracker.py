import requests
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import seaborn as sns
from dotenv import load_dotenv
import os

# --- API Token and Setup ---
# In production, use st.secrets["access_token"]
load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
BASE_URL = os.getenv('BASE_URL')

headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}

# --- API Functions ---
def get_profile():
    url = f'{BASE_URL}/profile.json'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data['user']
    else:
        print(f'Error: {response.status_code}')
        return None

def get_activity_time_series(start_date, end_date):
    try:
        url = f'{BASE_URL}/activities/steps/date/{start_date}/{end_date}.json'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get('activities-steps', [])
    except requests.RequestException as e:
        st.error(f"Steps API error: {e}")
        return None

def get_heart_rate_time_series(start_date, end_date):
    try:
        url = f'{BASE_URL}/activities/heart/date/{start_date}/{end_date}.json'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get('activities-heart', [])
    except requests.RequestException as e:
        st.warning(f"Heart rate API error: {e}")
        return None

def get_weight_time_series(start_date, end_date):
    try:
        url = f'{BASE_URL}/body/weight/date/{start_date}/{end_date}.json'
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get('body-weight', [])
    except requests.RequestException as e:
        st.error(f"Weight API error: {e}")
        return None

# --- Data Preparation ---
def prepare_data(steps_data, weight_data, heart_data=None):
    dfs = []
    
    if steps_data:
        steps_df = pd.DataFrame(steps_data)
        steps_df['dateTime'] = pd.to_datetime(steps_df['dateTime'])
        steps_df['steps'] = pd.to_numeric(steps_df['value'])
        dfs.append(steps_df[['dateTime', 'steps']])
    
    if weight_data:
        weight_df = pd.DataFrame(weight_data)
        weight_df['dateTime'] = pd.to_datetime(weight_df['dateTime'])
        weight_df['weight'] = pd.to_numeric(weight_df['value'])
        dfs.append(weight_df[['dateTime', 'weight']])
    
    if heart_data:
        heart_df = pd.DataFrame(heart_data)
        heart_df['dateTime'] = pd.to_datetime(heart_df['dateTime'])
        heart_df['heart_rate'] = heart_df['value'].apply(
            lambda x: x.get('restingHeartRate', np.nan) if isinstance(x, dict) else np.nan)
        dfs.append(heart_df[['dateTime', 'heart_rate']])
    
    if not dfs:
        return None
    
    df = dfs[0]
    for other_df in dfs[1:]:
        df = pd.merge(df, other_df, on='dateTime', how='outer')
    
    if 'weight' in df.columns:
        df['weight_change'] = df['weight'].diff().fillna(0)
    
    return df.sort_values('dateTime')

# --- Model & Recommendation ---
def train_model(df):
    if 'steps' not in df.columns or 'weight_change' not in df.columns:
        return None
    X = df[['steps']].values
    y = df['weight_change'].values
    model = LinearRegression().fit(X, y)
    return model

def recommend_steps(model, weight_to_lose, timeframe_days):
    if not model or timeframe_days <= 0:
        return None
    daily_loss = weight_to_lose / timeframe_days
    intercept = model.intercept_
    coef = model.coef_[0]
    if abs(coef) < 1e-6:
        return 10000
    required_steps = (daily_loss - intercept) / coef
    return int(np.clip(required_steps, 5000, 20000))

# --- Visualization ---
def plot_activity_data(df):
    import matplotlib.pyplot as plt
    import seaborn as sns
    import streamlit as st

    plt.style.use("dark_background")
    sns.set_palette("bright")  # Optional: ensures vivid colors

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_title("📊 Daily Activity Overview", fontsize=16, fontweight='bold', color='white')

    # Plot steps
    if 'steps' in df.columns:
        ax.plot(df['dateTime'], df['steps'], label='👣 Steps', color='deepskyblue', linewidth=2, marker='o')
        ax.set_ylabel('Steps', color='deepskyblue', fontsize=12)
        ax.tick_params(axis='y', labelcolor='deepskyblue')

    # Plot heart rate on secondary y-axis if available
    if 'heart_rate' in df.columns and not df['heart_rate'].isna().all():
        ax2 = ax.twinx()
        ax2.plot(df['dateTime'], df['heart_rate'], label='❤️ Heart Rate', color='tomato', linewidth=2, linestyle='--', marker='x')
        ax2.set_ylabel('Resting Heart Rate', color='tomato', fontsize=12)
        ax2.tick_params(axis='y', labelcolor='tomato')

    ax.set_xlabel('Date', fontsize=12, color='white')
    ax.tick_params(axis='x', labelrotation=45, labelcolor='white')

    ax.grid(True, linestyle=':', alpha=0.5)
    fig.tight_layout()

    # Optional: Combine legends from both axes
    lines, labels = ax.get_legend_handles_labels()
    if 'heart_rate' in df.columns and not df['heart_rate'].isna().all():
        lines2, labels2 = ax2.get_legend_handles_labels()
        lines += lines2
        labels += labels2
    ax.legend(lines, labels, loc='upper left', fontsize=10)

    st.pyplot(fig)



# --- Main App ---
def main():
    st.set_page_config("📊 Fitbit Health Dashboard", layout="wide")
    st.title("🏃 Fitbit Health Dashboard")
    
    # Date range - last 60 days
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')

    # Fetch data
    with st.spinner("Fetching data..."):
        steps = get_activity_time_series(start_date, end_date)
        weight = get_weight_time_series(start_date, end_date)
        heart = get_heart_rate_time_series(start_date, end_date)
    
    df = prepare_data(steps, weight, heart)

    if df is None or len(df) < 7:
        st.error("⚠ Not enough data. Ensure at least 7 days of step + weight data.")
        return

    profile = get_profile()
    st.subheader("User Profile !")
    if profile:
        st.write(f"Hello, {profile['fullName']}!")
        st.image(profile['avatar'], width=150)
    # Top metrics
    st.subheader("📌 Summary Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Steps", f"{int(df['steps'].mean()):,}")
    if 'heart_rate' in df.columns:
        col2.metric("Avg. Resting HR", f"{df['heart_rate'].mean():.1f} bpm")
    col3.metric("Weight Change (Total)", f"{df['weight_change'].sum():.2f} kg")

    # Tabs for layout
    tab1, tab2, tab3 = st.tabs(["📈 Trends", "🎯 Recommendations", "📂 Raw Data"])

    with tab1:
        st.markdown("### Activity and Heart Rate Trends")
        plot_activity_data(df)

    with tab2:
        st.markdown("### Personalized Step Goal")
        weight_to_lose = st.number_input("Weight to lose (kg)", 0.5, 50.0, 5.0, 0.5)
        weeks = st.number_input("Weeks", 1, 52, 8)
        if st.button("Calculate Goal"):
            model = train_model(df)
            if model:
                days = weeks * 7
                steps_needed = recommend_steps(model, weight_to_lose, days)
                current_avg = int(df['steps'].mean())
                st.metric("🚶 Daily Step Goal", steps_needed)
                if current_avg:
                    diff = max(0, steps_needed - current_avg)
                    st.info(f"You're currently averaging {current_avg:,} steps/day.")
                    if diff > 0:
                        st.write(f"Need to add {diff:,} steps/day ≈ {diff / 1300:.1f} km")
                    else:
                        st.success("You're already meeting your goal! 🎉")
            else:
                st.warning("Model training failed due to insufficient data.")

    with tab3:
        st.markdown("### Raw Merged Data")
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
