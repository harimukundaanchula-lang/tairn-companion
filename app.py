import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import requests

# Page setup
st.set_page_config(page_title="Tairn Telepathy", page_icon="🐉", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS for Dark/Gold theme & layout
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
    
    /* Central Header with Custom Tairn Icon */
    .header-container {
        text-align: center;
        padding-top: 10px;
        padding-bottom: 15px;
    }
    .header-title {
        color: #d4af37;
        font-family: 'Cinzel', serif, sans-serif;
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 8px;
    }
    .header-sub {
        color: #888888;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Chat Messages styling */
    div[data-testid="stChatMessage"] {
        background-color: #141519;
        border-radius: 14px;
        padding: 12px 18px;
        margin-bottom: 10px;
        border: 1px solid #22232a;
    }
    </style>
""", unsafe_allow_html=True)

# Custom SVG Graphic: Black Morningstartail Dragon with Golden Eyes
TAIRN_SVG = """
<svg width="80" height="80" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <!-- Glowing Aura -->
  <circle cx="50" cy="50" r="45" fill="url(#goldGlow)" opacity="0.15"/>
  <!-- Dark Dragon Wings -->
  <path d="M15 52C28 35 42 38 50 48C58 38 72 35 85 52C70 56 58 68 50 82C42 68 30 56 15 52Z" fill="#18191e" stroke="#d4af37" stroke-width="1.5"/>
  <!-- Dragon Head/Snout (Black Morningstartail) -->
  <path d="M50 22L41 38L45 50L50 55L55 50L59 38L50 22Z" fill="#0d0e12" stroke="#d4af37" stroke-width="1.5"/>
  <!-- Golden Eyes (Fourth Wing Canon) -->
  <circle cx="46" cy="38" r="1.8" fill="#ffd700"/>
  <circle cx="54" cy="38" r="1.8" fill="#ffd700"/>
  <!-- Morningstartail Spikes -->
  <path d="M50 82L47 88L50 95L53 88L50 82Z" fill="#d4af37"/>
  <path d="M44 87L40 90L46 91L44 87Z" fill="#d4af37"/>
  <path d="M56 87L60 90L54 91L56 87Z" fill="#d4af37"/>
  <defs>
    <radialGradient id="goldGlow" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(50 50) scale(45)">
      <stop stop-color="#d4af37"/>
      <stop offset="1" stop-color="#d4af37" stop-opacity="0"/>
    </radialGradient>
  </defs>
</svg>
"""

# App Header
st.markdown(f"""
    <div class="header-container">
        {TAIRN_SVG}
        <div class="header-title">TAIRNEANACH</div>
        <div class="header-sub">Black Morningstartail • Basgiath War College</div>
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

# Text Input above Mic
user_text_input = st.chat_input("Speak or type telepathically to Tairn...")

# Press & Hold Mic Component with Animated Waves
mic_html = """
<div style="display: flex; justify-content: center; align-items: center; padding: 10px 0;">
  <style>
    .mic-container {
      position: relative;
      width: 70px;
      height: 70px;
      display: flex;
      justify-content: center;
      align-items: center;
    }
    .mic-btn {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: linear-gradient(135deg, #d4af37, #8a7322);
      border: 2px solid #ffd700;
      color: #0b0c10;
      font-size: 24px;
      display: flex;
      justify-content: center;
      align-items: center;
      cursor: pointer;
      user-select: none;
      outline: none;
      z-index: 2;
      box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
      transition: transform 0.1s ease;
    }
    .mic-btn:active, .mic-btn.holding {
      transform: scale(0.92);
      background: linear-gradient(135deg, #ffd700, #b89628);
    }
    .wave {
      position: absolute;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      border: 2px solid rgba(212, 175, 55, 0.6);
      opacity: 0;
      pointer-events: none;
      z-index: 1;
    }
    .holding ~ .wave-1 { animation: ripple 1.6s infinite ease-out; }
    .holding ~ .wave-2 { animation: ripple 1.6s infinite ease-out 0.5s; }
    .holding ~ .wave-3 { animation: ripple 1.6s infinite ease-out 1s; }

    @keyframes ripple {
      0% {
        transform: scale(1);
        opacity: 0.8;
      }
      100% {
        transform: scale(2.2);
        opacity: 0;
      }
    }
  </style>

  <div class="mic-container">
    <button id="micBtn" class="mic-btn">🎙️</button>
    <div class="wave wave-1"></div>
    <div class="wave wave-2"></div>
    <div class="wave wave-3"></div>
  </div>
</div>

<script>
  const btn = document.getElementById('micBtn');
  
  btn.addEventListener('mousedown', startHold);
  btn.addEventListener('mouseup', endHold);
  btn.addEventListener('mouseleave', endHold);
  btn.addEventListener('touchstart', (e) => { e.preventDefault(); startHold(); });
  btn.addEventListener('touchend', (e) => { e.preventDefault(); endHold(); });

  function startHold() {
    btn.classList.add('holding');
  }

  function endHold() {
    btn.classList.remove('holding');
  }
</script>
"""

# Render Mic button under text box
components.html(mic_html, height=100)

# Process Text Input
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
    
