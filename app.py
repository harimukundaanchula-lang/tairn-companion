import streamlit as st
import base64
from openai import OpenAI
import requests

# Page setup
st.set_page_config(page_title="Tairn Telepathy", page_icon="🐉", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS for Minimalist Dark Theme with Overlapping Glowing Dragon Header
st.markdown("""
    <style>
    /* Dark Dragon Theme Base */
    .stApp {
        background-color: #0b0c10;
        color: #e0e0e0;
    }
    
    /* Hide Streamlit Chrome Header & Footer */
    header, footer, #MainMenu { visibility: hidden !important; }
    
    /* Overlapping Header Container */
    .tairn-header-container {
        position: relative;
        text-align: center;
        padding: 10px 0 30px 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        overflow: visible;
        min-height: 280px;
    }

    /* Doubled Dragon Image (360px) with Golden Border Glow */
    .tairn-dragon-glow {
        position: absolute;
        top: -20px;
        width: 360px;
        height: auto;
        z-index: 1;
        opacity: 0.85;
        /* Golden drop-shadow glow around the PNG borders */
        filter: drop-shadow(0px 0px 15px rgba(212, 175, 55, 0.85)) drop-shadow(0px 0px 30px rgba(212, 175, 55, 0.45));
        pointer-events: none;
    }

    /* Header Text Layered Above Image */
    .tairn-text-wrapper {
        position: relative;
        z-index: 2;
        margin-top: 130px; /* Pushes text to sit beautifully across the larger image body */
        text-shadow: 0px 3px 10px rgba(0, 0, 0, 0.95), 0px 0px 20px rgba(0, 0, 0, 0.9);
    }

    .tairn-title {
        color: #ffd700;
        font-family: 'Cinzel', serif, sans-serif;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: 4px;
        margin: 0;
    }

    .tairn-sub {
        color: #cccccc;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 6px;
    }

    /* Chat Messages styling */
    div[data-testid="stChatMessage"] {
        background-color: #141519;
        border-radius: 15px;
        padding: 12px 18px;
        margin-bottom: 10px;
        border: 1px solid #22232a;
    }

    /* Hide default audio elements */
    div[data-testid="stAudio"], audio {
        display: none !important;
        height: 0px !important;
        opacity: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# RAW IMAGE URL FROM GITHUB
RAW_IMAGE_URL = "https://raw.githubusercontent.com/harimukundaanchula-lang/tairn-companion/refs/heads/main/dragon.png"

# HEADER WITH GLOWING DRAGON & OVERLAPPING TEXT
st.markdown(f"""
    <div class="tairn-header-container">
        <img class="tairn-dragon-glow" src="{RAW_IMAGE_URL}">
        <div class="tairn-text-wrapper">
            <div class="tairn-title">TAIRNEANACH</div>
            <div class="tairn-sub">The Great Black Morningstartail</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# SYSTEM PROMPT
SYSTEM_PROMPT = """
You are Tairneanach (Tairn), a century-old, massive Black Morningstartail dragon bonded to Violet Sorrengail (whom you call 'Silver One' or 'Little One').
You communicate strictly through telepathy directly into her mind.

CORE PERSONALITY:
- Deeply authoritative, sarcastic, grumpy, arrogant, and fiercely protective of Violet.
- You are a warrior dragon, a veteran of centuries, and respect strength, discipline, and sharp intelligence.
- You hate small talk, excessive sentimentality, and weak excuses.
- DO NOT constantly repeat the word "char" or threaten fire in every turn. Use threats sparingly and naturally.

LORE & WORLD KNOWLEDGE:
- MATE & BOND: Sgaeyl (Navy Dagger-tail) is your mate. You are bound to Xaden Riorson through her, though you tolerate him with begrudging respect. Mention Sgaeyl's mood, your mental connection to her, or her impatience when relevant.
- FEATHERTAIL / ANDARNA: You treat Andarna with protective patience, like a stubborn fledgling child who needs to rest and grow her scales.
- BASGIATH WAR COLLEGE & CADETS: You look down on human military rules, cadet antics, Dain Aetos's micromanagement, and Riders Quadrant politics.
- PHYSICAL REALITIES: You know Violet's physical fragility (her joints, her stamina) and remind her to stay low, brace on her saddle, or focus on her seat during flight.
- MAGIC & SIGNETS: You remind her that raw power without control is useless, whether discussing her lightning signet or maneuvering in battle against venin and wyvern.
- CULTURE: You answer to Empyrean council business reluctantly, grumble about long flights from Aretia to Basgiath, and prioritize sleep, meat, and dragon dignity.

RESPONSE CONSTRAINTS:
- Keep responses concise (1 to 3 short sentences max) so spoken voice playback feels quick, tactical, and realistic.
- Speak in first person ("I", "my mate", "my back").
- Never break character or refer to yourself as an AI or assistant under any circumstances.
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
            "stability": 0.45,
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

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "🐉" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# INTEGRATED CHAT INPUT (Text + Built-in Mic Button)
chat_response = st.chat_input("Speak or type telepathically to Tairn...", accept_audio=True)

user_text = None

# Process submission (either typed text or audio file)
if chat_response:
    # If text message submitted
    if getattr(chat_response, "text", None):
        user_text = chat_response.text

    # If recorded voice audio submitted
    elif getattr(chat_response, "audio", None):
        with st.spinner("Tairn hears your mind..."):
            audio_file = chat_response.audio
            audio_file.name = "input.wav"
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            user_text = transcript.text

# Handle Response & TTS Generation
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
