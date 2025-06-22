import streamlit as st
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from firebase_admin import firestore
import datetime

# Streamlit page config
st.set_page_config(page_title="Dadhichi - AI Fitness Coach", page_icon="🧠", layout="wide")

# Styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #0066cc;
        text-align: center;
    }
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        background-color: rgb(30, 54, 103);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: rgb(30, 54, 103);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .assistant-message {
        background-color: rgb(30, 54, 103);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .error-message {
        background-color:rgb(199, 47, 70);
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Check user login
if "signedin" not in st.session_state:
    st.session_state.signedin = False

if not st.session_state.signedin:
    st.warning("🔒 Please sign in to access Dadhichi's chatbot.")
else:
    st.markdown('<h1 class="main-header">🧠 Dadhichi</h1>', unsafe_allow_html=True)
    st.write("I'm your personal AI fitness and nutrition coach powered by Llama 3. Ask me anything about workouts, diet, or yoga!👋")

    # Firebase (if needed later)
    db = firestore.client()

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Define model
    model = OllamaLLM(
        model="llama3.2:3b",
        temperature=0.7,
        base_url="http://localhost:11434"
    )

    # Prompt template with context
    SYSTEM_CONTEXT = (
        "You are Dadhichi, an expert AI fitness and nutrition coach specializing in Indian lifestyle. "
        "Provide specific, actionable advice for workouts, diet plans, and yoga routines. "
        "Focus on practical solutions using common Indian foods and home exercises. "
        "Be motivational but realistic. Break down complex concepts into simple steps. "
        "You must only answer fitness and diet related questions. If the user asks for anything else, remind them that you are here to help them through their fitness journey."
    )
    template = ChatPromptTemplate.from_template("{context}\n\nUser: {question}")
    prompt = template.format(context=SYSTEM_CONTEXT, question="{question}")

    def generate_response(question):
        try:
            full_prompt = prompt.replace("{question}", question)
            return model.invoke(full_prompt)
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return f"⚠️ Error: {str(e)}"

    # Chat container
    st.subheader("Chat with Dadhichi")

    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for chat in st.session_state.chat_history:
            if "Error" in chat["assistant"]:
                st.markdown(f'<div class="error-message"><strong>⚠ Error:</strong> {chat["assistant"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="user-message"><strong>🧑 You:</strong> {chat["user"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="assistant-message"><strong>🧠 Dadhichi:</strong> {chat["assistant"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Input form
    with st.form("chat_form"):
        user_input = st.text_area("Ask about fitness, nutrition, or yoga:", height=100, key="user_input")
        submitted = st.form_submit_button("Send")

        if submitted and user_input:
            with st.spinner("Dadhichi is thinking..."):
                response = generate_response(user_input)
                st.session_state.chat_history.append({
                    "user": user_input,
                    "assistant": response
                })
                st.rerun()

    # Footer
    st.markdown("---")
    st.write("""
        *Note: Dadhichi provides fitness guidance only, not medical advice. 
        For personalized health advice, consult a qualified professional.*
    """)
