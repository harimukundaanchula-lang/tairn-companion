import streamlit as st
import base64
from openai import OpenAI
import requests

# Page setup
st.set_page_config(page_title="Tairn Telepathy", page_icon="🐉", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS for Minimalist Dark Theme
st.markdown("""
    <style>
    /* Dark Dragon Theme Base */
    .stApp {
        background-color: #0b0c10;
        color: #e0e0e0;
    }
    
    /* Hide Streamlit Chrome Header & Footer */
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

    /* Hide default audio elements */
    div[data-testid="stAudio"], audio {
        display: none !important;
        height: 0px !important;
        opacity: 0 !important;
    }

    /* Clean simple audio input wrapper */
    div[data-testid="stAudioInput"] {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        margin-top: 10px !important;
        margin-bottom: 5px !important;
        padding: 0 !important;
    }

    div[data-testid="stAudioInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    
    div[data-testid="stAudioInput"] canvas,
    div[data-testid="stAudioInput"] button:not(:first-child) {
        display: none !important;
    }

    /* Simple Mic Button Styling */
    div[data-testid="stAudioInput"] button:first-child {
        background-color: #1c1d22 !important;
        border: 1px solid #33353d !important;
        border-radius: 50% !important;
        width: 52px !important;
        height: 52px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }

    div[data-testid="stAudioInput"] button:first-child:hover {
        border-color: #d4af37 !important;
        background-color: #25272e !important;
    }

    div[data-testid="stAudioInput"] button:first-child:active,
    div[data-testid="stAudioInput"] button:first-child[aria-pressed="true"] {
        background-color: #d32f2f !important;
        border-color: #ff5252 !important;
        box-shadow: 0 0 15px rgba(211, 47, 47, 0.8) !important;
    }

    div[data-testid="stAudioInput"] button:first-child svg {
        fill: #e0e0e0 !important;
        width: 22px !important;
        height: 22px !important;
    }
    </style>
""", unsafe_allow_html=True)

# DRAGON EMBLEM SVG HEADER (Redesigned Dragon Emblem)
st.markdown("""
    <div class="tairn-header">
        <svg width="75" height="75" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Outer Subtle Gold Glow Ring -->
          <circle cx="50" cy="50" r="44" fill="#141519" stroke="#d4af37" stroke-width="1.5" stroke-opacity="0.6"/>
          
          <!-- Wings Spread -->
          <path d="M50 38C38 22 20 20 12 30C22 38 34 42 46 48C32 50 20 58 14 68C26 66 38 60 48 54Z" fill="#d4af37"/>
          <path d="M50 38C62 22 80 20 88 30C78 38 66 42 54 48C68 50 80 58 86 68C74 66 62 60 52 54Z" fill="#d4af37"/>
          
          <!-- Dragon Head and Horns -->
          <path d="M50 18L46 28L48 38L50 42L52 38L54 28L50 18Z" fill="#ffd700"/>
          <path d="M46 26L40 20L44 30Z" fill="#d4af37"/>
          <path d="M54 26L60 20L56 30Z" fill="#d4af37"/>
          
          <!-- Dragon Eyes -->
          <circle cx="48" cy="30" r="1.2" fill="#000000"/>
          <circle cx="52" cy="30" r="1.2" fill="#000000"/>
          
          <!-- Body and Tail -->
          <path d="M48 42C48 58 45 68 50 85C52 68 52 58 52 42Z" fill="#ffd700"/>
          
          <!-- Morningstartail Blade Tip -->
          <path d="M50 85L44 78L50 92L56 78L50 85Z" fill="#d4af37"/>
        </svg>
        <div class="tairn-title">TAIRNEANACH</div>
        <div class="tairn-sub">Black Morningstartail • Basgiath War College</div>
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

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "🐉" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# Standard Simple Record Button placed right above text input
audio_file = st.audio_input("Record voice", label_visibility="collapsed", key="simple_mic")

# Text Input Box
user_text_input = st.chat_input("Speak or type telepathically to Tairn...")

user_text = None

# PRIORITIZE TEXT INPUT
if user_text_input:
    user_text = user_text_input

# PROCESS VOICE INPUT ONLY IF NEW
elif audio_file and audio_file != st.session_state.last_processed_audio:
    st.session_state.last_processed_audio = audio_file
    with st.spinner("Tairn hears your mind..."):
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
    
