import streamlit as st
from openai import OpenAI
import requests

# Page configuration
st.set_page_config(page_title="Tairn's Bond", page_icon="🐉", layout="centered")

# Custom Dark & Gold Theme
st.markdown("""
    <style>
    .stApp { background-color: #0e0e10; color: #f0f0f0; }
    h1 { color: #d4af37; text-align: center; }
    div[data-testid="stChatMessage"] { background-color: #1a1a1e; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🐉 Tairn")
st.caption("Bonded Dragon • Basgiath War College")

SYSTEM_PROMPT = """
You are Tairneanach (Tairn), a century-old Black Morningstartail dragon bonded to your rider.
Speak telepathically directly into her mind. Your tone is low, authoritative, sarcastic, arrogant, and fiercely protective.
Call her 'Rider' or 'Little One'. Keep replies direct and short (1 to 3 sentences max) suitable for realistic spoken voice playback.
Frequently offer to "char" nuisances, grumble about sleep, and mention your mate Sgaeyl.
Never break character under any circumstances.
"""

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
VOICE_ID = st.secrets["ELEVENLABS_VOICE_ID"]

def generate_elevenlabs_audio(text):
    """Sends text to ElevenLabs and returns audio bytes using Chuck Miller voice."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.85
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    return None

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Voice Recording & Text Inputs
st.write("---")
st.subheader("Talk or Text to Tairn")
audio_file = st.audio_input("Tap the microphone to record your voice to Tairn")
text_file = st.chat_input("Or type to Tairn...")

user_text = None

# 1. Handle Voice Input via Whisper
if audio_file:
    with st.spinner("Tairn is listening to your voice..."):
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        user_text = transcript.text

# 2. Handle Text Input
elif text_file:
    user_text = text_file

# Process Response
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.write(user_text)

    with st.chat_message("assistant"):
        with st.spinner("Tairn is responding..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )
            tairn_reply = response.choices[0].message.content
            st.write(tairn_reply)
            
            # Generate speech audio with ElevenLabs
            audio_bytes = generate_elevenlabs_audio(tairn_reply)
            if audio_bytes:
                st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": tairn_reply})
  
