import streamlit as st
import mediapipe as mp
import numpy as np
import cv2
import logging
from PIL import Image

# Set up logging to capture errors in the terminal instead of showing them in Streamlit UI
logging.basicConfig(level=logging.ERROR)

# Initialize Mediapipe Pose and Drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Header Section
st.markdown(
    """
    <div style="background-color:#2F4F4F;padding:10px;border-radius:10px;">
    <h1 style="color:white;text-align:center;">Training Arena</h1>
    </div>
    <br>
    """,
    unsafe_allow_html=True,
)

# If not signed in, show warning and redirect to login page
if 'signedin' not in st.session_state:
    st.session_state.signedin = False

if not st.session_state['signedin']:
    st.markdown("## Welcome to the Yoga arena")
    st.warning("Please sign in to continue")



if st.session_state['signedin']:
    # Display Training Introduction & GIF
    st.write("Welcome to the Training Page! Choose an exercise and get real-time feedback on your form.")
    st.image("./gif/ham.gif")  # Ensure the file exists in the correct path

    # Dropdown Menu for Exercise Selection
    exercise = st.selectbox("Select an Exercise", ["-- Select --", "Bicep Curl", "Squat", "Push-up"])

    # Initialize session state variables for camera control
    if "run_camera" not in st.session_state:
        st.session_state.run_camera = False

    # Only show camera controls if Bicep Curl is selected
    if exercise == "Bicep Curl":
        st.sidebar.header("Configuration")
        confidence_threshold = st.sidebar.slider("Detection Confidence", 0.1, 1.0, 0.5, 0.1)
        tracking_threshold = st.sidebar.slider("Tracking Confidence", 0.1, 1.0, 0.5, 0.1)

        # Start & Stop Buttons
        start_button = st.sidebar.button("Start Camera")
        stop_button = st.sidebar.button("Stop Camera")

        # Handle button clicks
        if start_button:
            st.session_state.run_camera = True
        if stop_button:
            st.session_state.run_camera = False

        # Function to calculate angle between three points
        def calculate_angle(a, b, c):
            try:
                a = np.array(a)
                b = np.array(b)
                c = np.array(c)
                radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
                angle = np.abs(radians * 180.0 / np.pi)
                if angle > 180.0:
                    angle = 360 - angle
                return angle
            except Exception as e:
                logging.error(f"Angle Calculation Error: {e}")
                return 0  # Default to 0 if error occurs

        # Camera Feed
        if st.session_state.run_camera:
            st.write("📹 Camera is ON. Get Ready to Perform Bicep Curls!")
            cap = cv2.VideoCapture(0)  # Capture from webcam
            stframe = st.empty()  # Streamlit placeholder for video frames

            counter = 0  # Rep counter
            stage = None  # "up" or "down"

            # Setup Mediapipe Pose
            with mp_pose.Pose(
                min_detection_confidence=confidence_threshold, 
                min_tracking_confidence=tracking_threshold
            ) as pose:
                while st.session_state.run_camera and cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        logging.error("Unable to read from camera. Please check your webcam.")
                        break

                    try:
                        # Convert to RGB
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        image.flags.writeable = False
                        results = pose.process(image)

                        # Convert back to BGR
                        image.flags.writeable = True
                        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                        if results.pose_landmarks:
                            landmarks = results.pose_landmarks.landmark

                            # Extract shoulder, elbow, and wrist landmarks
                            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                            # Calculate angle
                            angle = calculate_angle(shoulder, elbow, wrist)

                            # Display angle
                            cv2.putText(image, str(angle),
                                        tuple(np.multiply(elbow, [640, 480]).astype(int)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

                            # Rep counting logic
                            if angle > 150:
                                stage = "down"
                            if angle < 40 and stage == 'down':
                                stage = "up"
                                counter += 1

                        # Display Rep Counter
                        cv2.rectangle(image, (0, 0), (225, 73), (245, 117, 16), -1)
                        cv2.putText(image, 'REPS', (15, 12), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                        cv2.putText(image, str(counter), 
                                    (10, 60), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
                        cv2.putText(image, 'STAGE', (65, 12), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
                        cv2.putText(image, stage if stage else "None", 
                                    (60, 60), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

                        # Draw Pose Landmarks
                        if results.pose_landmarks:
                            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                                    mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2), 
                                                    mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))

                        # Show Image in Streamlit
                        stframe.image(image, channels="BGR", use_container_width=True)

                    except Exception as e:
                        logging.error(f"Error in Camera Processing: {e}")
                        continue  # Skip this frame if an error occurs

                cap.release()
                st.write("📷 Camera Stopped.")
