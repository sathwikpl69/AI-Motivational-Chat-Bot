import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Streamlit chatbot UI
st.set_page_config(page_title="Motivational Chatbot", page_icon="🤖", layout="wide")
st.title("Motivational Chatbot")

# Chat history storage
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process chatbot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Add a motivational context to the prompt
                motivational_prompt = (
                    "You are a motivational coach. Provide a positive and uplifting response in bullet points along with some related motivational quotes for which different bullet point symbol and boldify whatever you feel necessary. "
                    f"User's message: {prompt}"
                )
                # Generate response using the generative AI model
                response = model.generate_content(motivational_prompt).text
            except Exception as e:
                response = f"An error occurred: {e}"

            # Display chatbot response
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
