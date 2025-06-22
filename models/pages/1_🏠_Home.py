import requests
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
import time  # For delay before redirecting
import subprocess  # For running the streamlit command
import base64
from io import BytesIO

# Convert image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    return encoded

# Use the function
logo_base64 = get_base64_image("./images/dadhichi.png")

# Configure page
st.set_page_config(page_title="DADHICHI", page_icon=":tada:", layout="wide")

# Function to load Lottie animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("./styles/styles.css")

# ---- LOAD ASSETS ----
lottie_coding = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_FYx0Ph.json")
music = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_ikk4jhps.json")
podcast = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_JjpNLdaKYX.json")

img_contact_form = Image.open("./images/home.jpg")
img_lottie_animation = Image.open("./images/home.jpg")

# Load logo
# logo = Image.open("./images/dadhichi.png")  # Replace with the correct path to your logo file

# Display logo and header in a styled container
with st.container():
    st.markdown(
        f"""
        <div style='background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%); padding: 2rem 0 1rem 0; border-radius: 1.5rem; text-align: center; margin-bottom: 2rem;'>
            <img src='data:image/png;base64,{logo_base64}' width='300' style='box-shadow: 0 4px 24px rgba(0,0,0,0.15); margin-bottom: 1rem;' />
            <h3 style='color: #e0f7fa;'>Step into a fitter future: Welcome to your fitness revolution!</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

# Request to Login
if 'signedin' not in st.session_state:
    st.session_state['signedin'] = False

if not st.session_state['signedin']:
    st.warning("Please sign in to continue")

# ---- ABOUT US ----
with st.container():
    st.markdown("<div class='card-section soft-card'>", unsafe_allow_html=True)
    st.write("## About us :point_down:")
    left_column, right_column = st.columns([2, 1])
    with left_column:
        st.markdown(
            """
            <div style='font-size: 1.2rem; line-height: 1.7;'>
            - We are thrilled to have you here on our platform dedicated to empowering and inspiring individuals on their journey towards a healthier and fitter lifestyle. Whether you're a seasoned fitness enthusiast or just starting your fitness journey, we have everything you need to reach your goals and achieve the best version of yourself.<br><br>
            - What sets us apart is the fact that we provide personalized assistance at the comfort of your home or any place of your choice at a price that is both convenient and much cheaper than traditional gyms.<br><br>
            Let your fitness journey start here!<br>
            Join us today and embark on a transformative experience that will enhance your physical and mental well-being. Let's build strength, resilience, and a healthier future together!
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

# ---- PROJECTS ----
with st.container():
    st.markdown("<div class='card-section soft-card'>", unsafe_allow_html=True)
    st.write("---")
    st.header("Get fit, Jam on, Repeat :headphones:")
    st.write("##")
    image_column, text_column = st.columns((1, 2))
    with image_column:
        st_lottie(music, height=250, key="music")
    with text_column:
        st.subheader("Workout music 🎵")
        st.write("Power up your workout with the ultimate music fuel!")
        if st.button("Have a Listen... 🎧", key="music_button"):
            st.markdown("<script>window.open('https://open.spotify.com/playlist/6N0Vl77EzPm13GIOlEkoJn?si=9207b7744d094bd3', '_blank')</script>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with st.container():
    st.markdown("<div class='card-section soft-card'>", unsafe_allow_html=True)
    image_column, text_column = st.columns((1, 2))
    with image_column:
        st_lottie(podcast, height=250, key="podcast")
    with text_column:
        st.subheader("Podcast 🎙")
        st.write("Take your workouts to the next level with our immersive podcast that pumps you up from start to finish!")
        if st.button("Have a listen... 🎙", key="podcast_button"):
            st.markdown("<script>window.open('https://open.spotify.com/playlist/09Ig7KfohF5WmU9RhbDBjs?si=jyZ79y3wQgezrEDHim0NvQ', '_blank')</script>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
