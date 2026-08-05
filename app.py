import streamlit as st
from openai import OpenAI
import requests

# Page setup
st.set_page_config(page_title="Tairn Telepathy", page_icon="🐉", layout="centered", initial_sidebar_state="collapsed")

# Inject Custom CSS for Gemini/Grok style UI + Dragon Mic Button Styling
st.markdown("""
    <style>
    /* Dark Dragon Theme */
    .stApp {
        background-color: #0b0c10;
        color: #e0e0e0;
    }
    
    /* Hide top Streamlit header/footer elements */
    header, footer, #MainMenu { visibility: hidden !important; }
    
    /* Header Styling */
    .tairn-header {
        text-align: center;
        padding: 10px 0 20px 0;
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
        font-size: 12px;
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

    /* Target Native Audio Input Button & Style as Dragon Button */
    div[data-testid="stAudioInput"] {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 15px 0;
    }
    div[data-testid="stAudioInput"] button {
        background: linear-gradient(135deg, #d4af37, #8a7322) !important;
        color: #0b0c10 !important;
        border: 2px solid #ffd700 !important;
        border-radius: 50% !important;
        width: 70px !important;
        height: 70px !important;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    /* Pulsing gold glow animation when hovering/active */
    div[data-testid="stAudioInput"] button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.8) !important;
    }

    /* Replace Mic Icon inside the native button with Dragon symbol 🐉 */
    div[data-testid="stAudioInput"] button * {
        font-size: 0px !important; /* hide default mic text/icon */
    }
    div[data-testid="stAudioInput"] button::after {
        content: "🐉";
        font-size: 32px !important;
        display: block;
    }
    </style>
""", unsafe_allow_html=True)

# Tairn Morningstartail Header SVG (Black Dragon, Gold Wings/Eyes)
st.markdown("""
    <div class="tairn-header">
        <svg width="70" height="70" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
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

# Circular Dragon Voice Button centered above the Chat Input
audio_file = st.audio_input("Record voice to Tairn", label_visibility="collapsed")

# Chat Text Input Box
user_text_input = st.chat_input("Speak or type telepathically to Tairn...")

user_text = None

if audio_file:
    with st.spinner("Tairn hears your mind..."):
        audio_file.name = "input.wav"
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        user_text = transcript.text

elif user_text_input:
    user_text = user_text_input

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
    
