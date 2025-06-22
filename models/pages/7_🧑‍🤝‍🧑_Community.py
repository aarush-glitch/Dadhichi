import streamlit as st
from streamlit_lottie import st_lottie
import requests
import pandas as pd
import random
from firebase_admin import firestore
db = firestore.client()

# Load Lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        return None

lottie_events = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_u4yrau.json")
lottie_progress = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_2szqu88a.json")
lottie_community = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_i8xxlqfs.json")

# Page setup
st.set_page_config(page_title="Community Engagement", page_icon="🌟", layout="wide")

# Sign-in check
if 'signedin' not in st.session_state:
    st.session_state.signedin = False

if not st.session_state['signedin']:
    st.markdown(
        """
        <div style="background-color:#2F4F4F;padding:10px;border-radius:10px;">
        <h1 style="color:white;text-align:center;">Community Engagement</h1>
        </div>
        <br>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## Join the fitness revolution with your friends!")
    st.warning("Please sign in to access this feature.")
else:
    user_name = st.session_state["username"]

    # Header
    st.markdown(
        """
        <div style="background-color:#2F4F4F;padding:10px;border-radius:10px;">
        <h1 style="color:white;text-align:center;">Community Engagement</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("Join the fitness revolution with your friends and compete in exciting challenges!")

    # ---- EVENTS ----
    with st.container():
        st.write("---")
        st.header("🎉 Events and Challenges")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Current Highlight: Step Count Hierarchy")
            st.write("""
                Compete with your friends to see who takes the most steps in a week!  
                🌟 **Start Date:** Monday  
                🏆 **End Date:** Sunday  
                🎁 **Rewards:**  
                - 🥇 1st Place: $50 Gift Card  
                - 🥈 2nd Place: Resistance Band Set  
                - 🥉 3rd Place: Fitness Water Bottle  
                """)
            st.markdown("**Join Now and Climb the Leaderboard!**")
        with col2:
            if lottie_events:
                st_lottie(lottie_events, height=300, key="events")

    # ---- LEADERBOARD ----
    with st.container():
        st.write("---")
        st.header("🏅 Leaderboard")

        def fetch_leaderboard():
            users_ref = db.collection('weekly_steps')
            docs = users_ref.order_by("steps", direction=firestore.Query.DESCENDING).limit(10).stream()
            data = [{"Name": doc.id, "Steps This Week": doc.to_dict()['steps']} for doc in docs]
            df = pd.DataFrame(data)
            df["Rank"] = range(1, len(df) + 1)
            return df

        leaderboard_df = fetch_leaderboard()
        leaderboard_df.set_index("Rank", inplace=True)
        st.dataframe(leaderboard_df, use_container_width=True)

    # ---- PERSONAL PROGRESS ----
    with st.container():
        st.write("---")
        st.header("📊 Your Progress")
        st.write("Track your performance and compare it with your friends!")

        col1, col2 = st.columns([2, 1])
        with col1:
            user_doc = db.collection("weekly_steps").document(user_name).get()
            user_steps = user_doc.to_dict().get("steps", 0) if user_doc.exists else 0

            st.progress(min(user_steps / 60000, 1.0))  # cap at 100%
            st.write(f"**Your Progress:** {user_steps} steps")

            # Step update UI
            new_steps = st.number_input("Update your weekly steps", min_value=0, step=1000)
            if st.button("Save Steps"):
                db.collection("weekly_steps").document(user_name).set({"steps": new_steps})
                st.success("Steps updated! Please refresh the page to see changes.")

        with col2:
            if lottie_progress:
                st_lottie(lottie_progress, height=300, key="progress")

    # ---- COMMUNITY STATS ----
    with st.container():
        st.write("---")
        st.header("🌍 Community Motivation")
        st.write("Together, we’re stronger! Here's how the community is doing:")

        def fetch_community_stats():
            users_ref = db.collection("weekly_steps").stream()
            total_steps = 0
            count = 0
            for doc in users_ref:
                data = doc.to_dict()
                steps = data.get("steps", 0)
                total_steps += steps
                count += 1
            return total_steps, count

        total_steps, total_users = fetch_community_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Steps Taken This Week", f"{total_steps:,}", delta="↑ from last week")
            st.metric("Active Participants", f"{total_users}", delta="↑ active users")
        with col2:
            if lottie_community:
                st_lottie(lottie_community, height=300, key="community")
