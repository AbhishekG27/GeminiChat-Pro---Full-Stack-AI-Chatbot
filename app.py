import streamlit as st
import requests
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="💬",
    layout="centered"
)

# Custom CSS for chat messages
st.markdown("""
<style>
.user-message {
    background-color: #e6f3ff;
    padding: 15px;
    border-radius: 15px;
    margin: 5px 0;
}
.bot-message {
    background-color: #f0f0f0;
    padding: 15px;
    border-radius: 15px;
    margin: 5px 0;
}
.message-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'conversation_id' not in st.session_state:
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")

# API endpoint
API_URL = "http://127.0.0.1:8000/api"

def send_message(message: str):
    """Send message to API and get response"""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={
                "message": message,
                "conversation_id": st.session_state.conversation_id
            }
        )
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def get_chat_history():
    """Retrieve chat history from API"""
    try:
        response = requests.get(
            f"{API_URL}/history/{st.session_state.conversation_id}"
        )
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# Main app title
st.title("💬 AI Chatbot")

# Sidebar for settings and info
with st.sidebar:
    st.header("About")
    st.write("This is an AI chatbot powered by Gemini 1.5 Pro.")
    
    st.header("Conversation ID")
    st.write(f"Current conversation: {st.session_state.conversation_id}")
    
    if st.button("Start New Conversation"):
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
        st.session_state.messages = []
        st.rerun()

# Chat interface
chat_container = st.container()

# Display chat messages
with chat_container:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <b>You:</b><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bot-message">
                <b>Bot:</b><br>{message["content"]}
            </div>
            """, unsafe_allow_html=True)

# Input form
with st.form(key="message_form", clear_on_submit=True):
    user_input = st.text_area("Type your message:", key="user_input", height=100)
    col1, col2 = st.columns([1, 5])
    
    with col1:
        submit_button = st.form_submit_button("Send")
    
    if submit_button and user_input.strip():
        # Add user message to state
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Get bot response
        with st.spinner("Thinking..."):
            response = send_message(user_input)
            
            if response:
                # Add bot response to state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["response"]
                })
        
        # Rerun to update the chat display
        st.rerun()

# Add a download button for chat history
if st.session_state.messages:
    if st.button("Download Chat History"):
        chat_history = get_chat_history()
        if chat_history:
            # Convert chat history to downloadable format
            history_str = json.dumps(chat_history, indent=2)
            st.download_button(
                label="Download JSON",
                data=history_str,
                file_name=f"chat_history_{st.session_state.conversation_id}.json",
                mime="application/json"
            )