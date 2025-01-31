import streamlit as st
import requests
from streamlit_chat import message
import uuid

endpoint = st.secrets["endpoint"]
api_key = st.secrets["api_key"]

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown(
    """
        <style>
                .stAppHeader {
                    background-color: rgba(255, 255, 255, 0.0);  /* Transparent background */
                    visibility: visible;  /* Ensure the header is visible */
                }

               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)
st.header("OCS GPT")

# Custom CSS for chat bubbles and layout
st.markdown("""
    <style>
    .assistant-bubble {
        background-color: #e0e0e0;
        color: black;
        border-radius: 10px;
        padding: 10px;
        margin: 5px;
        width: fit-content;
        max-width: 70%;
        align-self: flex-start;
        word-wrap: break-word;
        margin-right: auto;  /* Align assistant messages to the left */
    }
    </style>
""", unsafe_allow_html=True)

# Placeholder for chat history
chat_placeholder = st.empty()

# Display chat history
with chat_placeholder.container():
    for i, msg in enumerate(st.session_state.messages):
        unique_key = f"{msg['role']}_{i}_{uuid.uuid4()}"
        if msg['role'] == 'user':
            message(msg['content'], is_user=True, key=unique_key, avatar_style="icons")
        else:
            with st.chat_message("assistant"):
                st.markdown(f"<div class='assistant-bubble'>{msg['content']}</div>", unsafe_allow_html=True)

# Input area using st.chat_input
if prompt := st.chat_input("Hi OCS!", key="chat_input"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Send user message to the API
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }
    data = {
        "model": "gpt-35-turbo",
        "messages": st.session_state.messages,  # Include the entire conversation history
        "max_tokens": 800,
        "temperature": 0.7,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }

    response = requests.post(endpoint, headers=headers, json=data)

    if response.status_code == 200:
        completion = response.json()
        response_text = completion['choices'][0]['message']['content'].strip()
        
        # Add assistant message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Update chat history
        with chat_placeholder.container():
            for i, msg in enumerate(st.session_state.messages):
                unique_key = f"{msg['role']}_{i}_{uuid.uuid4()}"
                if msg['role'] == 'user':
                    message(msg['content'], is_user=True, key=unique_key, avatar_style="icons")
                else:
                    message(msg['content'], is_user=False, key=unique_key, avatar_style="icons")
    else:
        st.error(f"Error: {response.status_code}, {response.text}")
