import streamlit as st
import base64
from openai import OpenAI
import requests

# Page setup
st.set_page_config(page_title="Tairn Telepathy", page_icon="🐉", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS for Sleek Minimalist UI & Floating Dragon Orb
st.markdown("""
    <style>
    /* Dark Dragon Theme Base */
    .stApp {
        background-color: #0b0c10;
        color: #e0e0e0;
    }
    
    /* Hide Streamlit Chrome */
    header, footer, #MainMenu { visibility: hidden !important; }
    
    /* Header Styling */
    .tairn-header {
        text-align: center;
        padding: 10px 0 10px 0;
    }
    .tairn-title {
        color: #d4af37;
        font-family: 'Cinzel', serif, sans-serif;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 2px;
        margin: 5px 0 0 0;
    }
    .tairn-sub {
        color: #888888;
        font-size: 11px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* Chat Messages styling */
    div[data-testid="stChatMessage"] {
        background-color: #141519;
        border-radius: 15px;
        padding: 12px 18px;
        margin-bottom: 10px;
        border: 1px solid #22232a;
    }

    /* Completely hide default audio playback bars */
    div[data-testid="stAudio"], audio {
        display: none !important;
        height: 0px !important;
        opacity: 0 !important;
    }

    /* Clean up the audio input component wrapper completely */
    div[data-testid="stAudioInput"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 20px 0 !important;
    }

    /* Hide the waveform container, timer text, and extra elements */
    div[data-testid="stAudioInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    /* Hide waveform canvas and secondary buttons */
    div[data-testid="stAudioInput"] canvas,
    div[data-testid="stAudioInput"] button:not(:first-child) {
        display: none !important;
    }

    /* Target the primary recording button into a glowing golden orb */
    div[data-testid="stAudioInput"] button:first-child {
        background: radial-gradient(circle, #ffd700 0%, #b89628 70%, #6e5812 100%) !important;
        border: 2px solid #ffd700 !important;
        border-radius: 50% !important;
        width: 75px !important;
        height: 75px !important;
        box-shadow: 0 0 25px rgba(212, 175, 55, 0.6) !important;
        transition: all 0.25s ease-in-out !important;
        position: relative !important;
        cursor: pointer !important;
    }

    /* Replace default mic icon with Dragon Emoji in center of orb */
    div[data-testid="stAudioInput"] button:first-child * {
        font-size: 0px !important;
    }
    div[data-testid="stAudioInput"] button:first-child::after {
        content: "🐉";
        font-size: 36px !important;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        line-height: 1;
    }

    /* FIERY RED ORB STATE: Active / Recording / Listening */
    div[data-testid="stAudioInput"] button:first-child:active,
    div[data-testid="stAudioInput"] button:first-child[aria-pressed="true"] {
        background: radial-gradient(circle, #ff4d4d 0%, #c0392b 70%, #781e1e 100%) !important;
        border-color: #ff3333 !important;
        box-shadow: 0 0 40px rgba(255, 51, 51, 0.95) !important;
        transform: scale(0.94);
    }
    </style>
""", unsafe_allow_html=True)

# Header SVG
st.markdown("""
    <div class="tairn-header">
        <svg width="65" height="65" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="50" cy="50" r="45" fill="#d4af37" fill-opacity="0.1"/>
          <path d="M15 52C28 35 42 38 50 48C58 38 72 35 85 52C70 56 58 68 50 82C42 68 30 56 15 52Z" fill="#18191e" stroke="#d4af37" stroke-width="1.5"/>
          <path d="M50 22L41 38L45 50L50 55L55 50L59 38L50 22Z" fill="#0d0e12" stroke="#d4af37" stroke-width="1.5"/>
          <circle cx="46" cy="38" r="1.8" fill="#ffd700"/>
          <circle cx="54" cy="38" r="1.8" fill="#ffd700"/>
          <path d="M50 82L47 88L50 95L53 88L50 82Z" fill="#d4af37"/>
        </svg>
        <div class="tairn-title">TAIRNEANACH</div>
        <div class="tairn-sub">Black Morningstartail • Basgiath War College</div>
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

def play_invisible_audio(audio_bytes):
    """Plays voice output invisibly in background."""
    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
    audio_html = f"""
    <iframe src="about:blank" style="display:none;" id="audio_frame"></iframe>
    <audio autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
    </audio>
    """
    st.components.v1.html(
        f"""
        <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
        """,
        height=0,
    )

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# Render existing chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "🐉" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# Single Floating Dragon Orb Button
audio_file = st.audio_input("Record voice", label_visibility="collapsed", key="dragon_mic")

# Text Input Box
user_text_input = st.chat_input("Speak or type telepathically to Tairn...")

user_text = None

# PRIORITIZE TEXT INPUT FIRST
if user_text_input:
    user_text = user_text_input

# PROCESS VOICE INPUT ONLY IF IT'S NEW AUDIO
elif audio_file and audio_file != st.session_state.last_processed_audio:
    st.session_state.last_processed_audio = audio_file
    with st.spinner("Tairn hears your mind..."):
        audio_file.name = "input.wav"
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        user_text = transcript.text

# Process and respond
if user_text:
    st.session_state.messages.append({"role": "user", "content": user_text})
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
                play_invisible_audio(audio_bytes)

    st.session_state.messages.append({"role": "assistant", "content": tairn_reply})
    
