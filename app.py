import streamlit as st
from openai import OpenAI
import requests

# Page setup
st.set_page_config(page_title="Tairn Telepathy", page_icon="🐉", layout="centered", initial_sidebar_state="collapsed")

# Inject Custom CSS for Gemini/Grok style UI
st.markdown("""
    <style>
    /* Dark Dragon Theme Setup */
    .stApp {
        background-color: #0b0c10;
        color: #e0e0e0;
    }
    
    /* Hide top Streamlit elements */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    
    /* Central Glowing Title/Orb Header */
    .header-container {
        text-align: center;
        padding-top: 10px;
        padding-bottom: 20px;
    }
    .header-title {
        color: #d4af37;
        font-family: 'Cinzel', serif, sans-serif;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 0px;
    }
    .header-sub {
        color: #888888;
        font-size: 13px;
    }

    /* Chat Messages styling */
    div[data-testid="stChatMessage"] {
        background-color: #15161a;
        border-radius: 15px;
        padding: 12px 18px;
        margin-bottom: 10px;
        border: 1px solid #222328;
    }
    
    /* Bottom Floating Action Bar */
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #0b0c10;
        padding: 15px 20px;
        border-top: 1px solid #1a1b20;
        z-index: 9999;
    }
    
    /* Clean audio input styling */
    div[data-testid="stAudioInput"] {
        background: transparent !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
    <div class="header-container">
        <div class="header-title">🐉 TAIRN</div>
        <div class="header-sub">Telepathic Dragon Connection</div>
    </div>
""", unsafe_allow_html=True)

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
    """Sends text to ElevenLabs and returns audio bytes."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.85
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"ElevenLabs Error ({response.status_code}): {response.text}")
        return None

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Container for main chat display
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            avatar = "🐉" if msg["role"] == "assistant" else "👤"
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

# Bottom Input Interface
st.markdown("---")
col1, col2 = st.columns([1, 4])

with col1:
    audio_file = st.audio_input("Record", label_visibility="collapsed")

with col2:
    text_file = st.chat_input("Speak or type to Tairn...")

user_text = None

# Process Input
if audio_file:
    with st.spinner("Transcribing mind connection..."):
        audio_file.name = "input.wav"
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        user_text = transcript.text

elif text_file:
    user_text = text_file

if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.write(user_text)

        with st.chat_message("assistant", avatar="🐉"):
            with st.spinner("Tairn speaks..."):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages
                )
                tairn_reply = response.choices[0].message.content
                st.write(tairn_reply)
                
                audio_bytes = generate_elevenlabs_audio(tairn_reply)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": tairn_reply})
