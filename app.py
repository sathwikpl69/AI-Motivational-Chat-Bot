import streamlit as st
import google.generativeai as genai
import os
import pyttsx3  # Text-to-Speech
import speech_recognition as sr  # Speech-to-Text
import sounddevice as sd  # For recording audio
import numpy as np
import scipy.io.wavfile as wav
from dotenv import load_dotenv
import threading

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

# Initialize text-to-speech engine
tts_engine = pyttsx3.init()

# Function to speak text using Text-to-Speech engine in a separate thread
def speak(text):
    """Speak the text using Text-to-Speech engine."""
    def run_tts():
        for chunk in text.split('. '):  # Break long responses into smaller sentences
            tts_engine.say(chunk)
        tts_engine.runAndWait()

    # Run the TTS engine in a separate thread to avoid blocking the main event loop
    tts_thread = threading.Thread(target=run_tts)
    tts_thread.start()

# Function to record audio using sounddevice
def record_audio(duration=5, samplerate=44100):
    st.write("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()  # Wait for recording to finish
    st.write("Recording complete!")
    return audio, samplerate

# Speech-to-Text Input
st.write("🎙️ **Speak your message (requires microphone)**")
recognizer = sr.Recognizer()
audio_input = st.button("Start Voice Input")

prompt = ""  # Initialize prompt

if audio_input:
    try:
        # Use sounddevice to record audio
        audio, samplerate = record_audio()
        wav.write('temp_audio.wav', samplerate, audio)  # Save the audio as a WAV file

        # Use SpeechRecognition to convert audio to text
        with sr.AudioFile('temp_audio.wav') as source:
            audio_data = recognizer.record(source)
            prompt = recognizer.recognize_google(audio_data)
            st.write(f"**You said:** {prompt}")
    except sr.RequestError:
        st.write("Microphone is not accessible. Please check permissions.")
    except sr.UnknownValueError:
        st.write("Could not understand the audio. Please try again.")
    except Exception as e:
        st.write(f"Error: {e}")

# Text Input (for fallback if no voice input is given)
text_prompt = st.chat_input("Type your message here...")
if text_prompt:
    prompt = text_prompt  # Use text input if provided

# Process input and generate chatbot response
if prompt:
    # Append user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate chatbot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                motivational_prompt = (
                    "You are a motivational coach. Provide a positive and uplifting response in bullet points along with some related motivational quotes for which different bullet point symbol and boldify whatever you feel necessary. "
                    f"User's message: {prompt}"
                )
                response = model.generate_content(motivational_prompt).text
            except Exception as e:
                response = f"An error occurred: {e}"

            # Display chatbot response
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            # Speak the chatbot response
            speak(response)
