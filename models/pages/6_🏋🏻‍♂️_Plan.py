import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from firebase_admin import firestore
import datetime

model = OllamaLLM(model="llama3.2:3b", temperature=0)

# Firebase Firestore client initialization
db = firestore.client()

# Header Section
if 'signedin' not in st.session_state:
    st.session_state.signedin = False

if not st.session_state['signedin']:
    st.markdown(
        """
        <div style="background-color:#2F4F4F;padding:10px;border-radius:10px;">
        <h1 style="color:white;text-align:center;">Workout Planning AI Arena</h1>
        </div>
        <br>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## We help track your calories to reach your goals!")
    st.warning("Please sign in to continue")

else:
    # Streamlit UI for logged-in users
    st.title("🏋️ Dadhichi - Personalized Workout Plan Generator")
    
    # User chooses whether to create a new plan or view old plans
    option = st.selectbox("Choose an option", ["Create New Plan", "View Old Plans"])

    if option == "Create New Plan":
        # Collect User Inputs for generating a new workout plan
        goal = st.selectbox("Choose your fitness goal:", ["Lose weight", "Build muscle", "Improve Endurance", "General fitness"]).lower()
        duration = st.slider("How much time do you have for your workout?", 15, 120, 30)
        intensity = st.selectbox("Select workout intensity:", ["Low", "Medium", "High"]).lower()
        location = st.selectbox("Where will you work out?", ["Gym", "Home", "Outdoor"]).lower()
        type = st.selectbox("What do you prefer, yoga or training?", ["Yoga", "Training"]).lower()

        # Optional user notes
        user_notes = st.text_area("Any injuries, preferences, or goals you'd like to consider?", "")

        # Generate Plan button
        if st.button("Generate Plan"):
            context = f"""
            You are Sage Dadhichi, a certified personal trainer AI. The AI embodiement of Sage dadhichi here to guide and plan a workout for the user.
            Based on the user's input below, generate a personalized workout plan which includes exercises, sets, reps, and duration if the user chooses to train or different yoga poses if the user chooses yoga.
            Do not keep the prompt too long, make it to the point suggest exercises strictly based on user requirements, you do not need to mention an alternative to the exercise you mentioned.
            
            User goal: {goal}
            Workout duration: {duration} minutes
            Workout intensity: {intensity}
            Workout location: {location}
            Workout type: {type}
            
            Important Point 1: If workout type is yoga, you must not suggest any training exercises.
            Important Point 2: If workout type is training, you must not suggest any yoga poses.
            
            Additional notes: {user_notes}
            
            Your response should include:
            1. A workout plan (Step-by-step) suited for the user input.
            2. A short motivational message to the user.
            """
            
            prompt = ChatPromptTemplate.from_template(context)
            chain = prompt | model
            result = chain.invoke({
                "context": context,
                "question": "Can you create a workout plan for me?"
            })

            # Save result in session_state
            st.session_state.generated_plan = result.strip()
            st.session_state.generated_inputs = {
                "goal": goal,
                "duration": duration,
                "intensity": intensity,
                "location": location,
                "type": type,
                "notes": user_notes
            }
        
        if "generated_plan" in st.session_state and st.session_state.generated_plan:
            st.subheader("🏋🏻‍♂️ Your Personalized Workout Plan:")
            st.markdown(st.session_state.generated_plan)

            # Option to save the plan
            plan_name = st.text_input("Enter a name for this plan:")
            if st.button("✅ Approve and Save this Plan"):
                if plan_name:
                    try:
                        user_id = st.session_state.username  # same as document ID in your "users" collection
                        
                        db.collection("users").document(user_id).collection("plans").add({
                            "plan_name": plan_name,
                            "plan": st.session_state.generated_plan,
                            **st.session_state.generated_inputs,
                            "timestamp": datetime.datetime.now()
                        })
                        st.success("✅ Your workout plan has been saved to your profile.")
                        # Clear after saving
                        del st.session_state.generated_plan
                        del st.session_state.generated_inputs
                        
                    except Exception as e:
                        st.error(f"Failed to save workout plan: {e}")
                else:
                    st.warning("Please enter a name for the plan before saving.")

    elif option == "View Old Plans":
        # Fetch and display old plans
        user_id = st.session_state.username
        plans_ref = db.collection("users").document(user_id).collection("plans")
        plans = plans_ref.stream()
        
        old_plans = []
        for plan in plans:
            plan_data = plan.to_dict()
            old_plans.append(plan_data)
        
        if old_plans:
            st.subheader("Your Old Workout Plans:")
            for i, plan in enumerate(old_plans):
                st.write(f"**{plan['plan_name']}**")
                st.write(f"Goal: {plan['goal']}, Duration: {plan['duration']} mins")
                st.write(f"Intensity: {plan['intensity']}, Location: {plan['location']}")
                st.write(f"Type: {plan['type']}")
                st.write(f"Notes: {plan['notes']}")
                st.write(f"Timestamp: {plan['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(plan['plan'])
                st.text("_____________________________________________________________________________________________________________________________________")
        else:
            st.warning("You don't have any saved plans yet.")
