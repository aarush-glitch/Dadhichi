import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
import datetime
import requests
from dotenv import load_dotenv
import os

# Firebase Admin initialization
if not firebase_admin._apps:
    # Service account key
    cred = credentials.Certificate("dadhichi-login-974192bf5e2b.json")  
    firebase_admin.initialize_app(cred)

db = firestore.client()
load_dotenv() 
# Firebase Web API key (from Firebase console > Project settings > General > Web API key)
API_KEY = os.getenv('API_KEY')

# Sign up user using Admin SDK
def signup_user(name, email, password, username):
    try:
        user = auth.create_user(email=email, password=password, uid=username)
        db.collection("users").document(user.uid).set({
            "name": name,
            "email": email,
            "username": username,
            "created_at": datetime.datetime.now()
        })
        st.success("Account created!")
    except Exception as e:
        st.error(e)

# Login user using Firebase REST API
def login_user(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        res = requests.post(url, json=payload)
        res.raise_for_status()
        user_data = res.json()

        st.session_state.username = user_data['localId']
        st.session_state.useremail = user_data['email']
        st.session_state.signedin = True
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {e.response.json()['error']['message']}")

# Sign out user
def signout_user():
    st.session_state.signedin = False
    st.session_state.username = ""
    st.session_state.useremail = ""

# Streamlit UI
st.title("🔐 Account")

if 'signedin' not in st.session_state:
    st.session_state.signedin = False

if st.session_state['signedin']:
    st.success(f"Welcome back, {st.session_state.useremail}")
    
    try:
        user_doc = db.collection("users").document(st.session_state.username).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            st.subheader("Your Profile Information:")
            st.write(f"👤 Name: {user_data.get('name')}")
            st.write(f"📧 Email: {user_data.get('email')}")
            st.write(f"🆔 Username: {user_data.get('username')}")
            st.write(f"🕒 Joined on: {user_data.get('created_at').strftime('%Y-%m-%d %H:%M:%S')}")
            st.session_state.name = user_data.get('name') 
            def upload_weekly_steps(username, step_count):
                week_str = datetime.now().strftime("%Y-W%U")  # Example: 2025-W16
                doc_ref = db.collection("users").document(username).collection("steps").document(week_str)
                doc_ref.set({
                    "steps": step_count,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })           
        else:
            st.warning("User record not found in the database")
    except Exception as e:
        st.error(f"Error fetching user data: {e}")
        
        
    st.button("Sign Out", on_click=signout_user)

if not st.session_state['signedin']:
    option = st.selectbox("Choose an option", ["Login", "Create Account"])

    if option == "Create Account":
        st.subheader("Create New Account")
        name = st.text_input("Name")
        email = st.text_input("Email")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            if name and email and username and password:
                signup_user(name, email, password, username)
            else:
                st.warning("Please fill in all fields")

    elif option == "Login":
        st.subheader("Login to Your Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        st.button("Login", on_click=login_user, args=(email, password))
