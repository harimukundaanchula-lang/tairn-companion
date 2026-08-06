import streamlit as st
import base64
from openai import OpenAI
import requests

# Page setup
st.set_page_config(
    page_title="Tairn Telepathy", 
    page_icon="🐉", 
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# App theme CSS & Keyframe Animations with Rocky Aesthetic Background
st.markdown("""
    <style>
    /* Dark Rocky Texture & Dragon Theme Base */
    .stApp {
        background-color: #0b0c10;
        background-image: 
            radial-gradient(circle at center, rgba(11, 12, 16, 0.75) 0%, rgba(5, 5, 8, 0.95) 100%),
            url('https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
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

    /* ANIMATION 1: Dragon Breathing & Glowing */
    @keyframes dragonBreathing {
        0% {
            transform: translateY(0px) scale(1);
            filter: drop-shadow(0px 0px 12px rgba(212, 175, 55, 0.7)) drop-shadow(0px 0px 25px rgba(212, 175, 55, 0.35));
        }
        50% {
            transform: translateY(-8px) scale(1.02);
            filter: drop-shadow(0px 0px 22px rgba(255, 140, 0, 0.95)) drop-shadow(0px 0px 40px rgba(212, 175, 55, 0.6));
        }
        100% {
            transform: translateY(0px) scale(1);
            filter: drop-shadow(0px 0px 12px rgba(212, 175, 55, 0.7)) drop-shadow(0px 0px 25px rgba(212, 175, 55, 0.35));
        }
    }

    .tairn-dragon-glow {
        position: absolute;
        top: -20px;
        width: 360px;
        height: auto;
        z-index: 1;
        opacity: 0.9;
        pointer-events: none;
        animation: dragonBreathing 5s infinite ease-in-out;
    }

    /* Header Text Layered Above Image */
    .tairn-text-wrapper {
        position: relative;
        z-index: 2;
        margin-top: 130px;
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
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 6px;
    }

    /* ANIMATION 2: Chat Bubble Telepathic Fade-In with Semi-Transparent Slate Glass Effect */
    @keyframes telepathicFadeIn {
        from {
            opacity: 0;
            transform: translateY(12px) scale(0.98);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    div[data-testid="stChatMessage"] {
        background: rgba(20, 21, 25, 0.85);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border-radius: 15px;
        padding: 12px 18px;
        margin-bottom: 10px;
        border: 1px solid rgba(212, 175, 55, 0.15);
        animation: telepathicFadeIn 0.4s ease-out forwards;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6);
    }

    /* Style the input container to fit the rock aesthetic */
    div[data-testid="stChatInput"] {
        background: rgba(15, 16, 20, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
    }

    /* Hide default audio playback elements */
    div[data-testid="stAudio"], audio {
        display: none !important;
        height: 0px !important;
        opacity: 0 !important;
    }

    /* ANIMATION 3: Record Button Glow & Pulse */
    div[data-testid="stChatInput"] button {
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        padding: 10px !important;
        margin: 2px !important;
        border-radius: 50% !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        background: rgba(28, 29, 34, 0.8) !important;
    }

    div[data-testid="stChatInput"] button svg {
        width: 24px !important;
        height: 24px !important;
        fill: #d4af37 !important;
        transition: transform 0.3s ease !important;
    }

    div[data-testid="stChatInput"] button:hover {
        transform: scale(1.12);
        border-color: #ffd700 !important;
        box-shadow: 0 0 18px rgba(212, 175, 55, 0.7), inset 0 0 10px rgba(212, 175, 55, 0.4) !important;
    }

    @keyframes dragonPulse {
        0% {
            box-shadow: 0 0 0 0 rgba(212, 175, 55, 0.8), 0 0 10px rgba(255, 87, 34, 0.6);
            transform: scale(1.05);
        }
        50% {
            box-shadow: 0 0 0 14px rgba(212, 175, 55, 0), 0 0 25px rgba(255, 87, 34, 0.9);
            transform: scale(1.15);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(212, 175, 55, 0), 0 0 10px rgba(255, 87, 34, 0.6);
            transform: scale(1.05);
        }
    }

    div[data-testid="stChatInput"] button:active,
    div[data-testid="stChatInput"] button[aria-pressed="true"],
    div[data-testid="stChatInput"] button[data-is-recording="true"] {
        background: radial-gradient(circle, rgba(212,175,55,0.3) 0%, rgba(20,21,25,0.9) 100%) !important;
        border-color: #ff5722 !important;
        animation: dragonPulse 1.2s infinite ease-in-out !important;
    }

    div[data-testid="stChatInput"] button:active svg,
    div[data-testid="stChatInput"] button[aria-pressed="true"] svg {
        fill: #ff5722 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Raw image URL from GitHub
RAW_IMAGE_URL = "https://raw.githubusercontent.com/harimukundaanchula-lang/tairn-companion/refs/heads/main/dragon.png"

# Header component
st.markdown(f"""
    <div class="tairn-header-container">
        <img class="tairn-dragon-glow" src="{RAW_IMAGE_URL}">
        <div class="tairn-text-wrapper">
            <div class="tairn-title">TAIRNEANACH</div>
            <div class="tairn-sub">THE GREAT BLACK MORNINGSTARTAIL • THIRD BONDED RIDER</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# System prompt configured for Erika Mae Mesina (Third Rider Lore)
SYSTEM_PROMPT = """
You are Tairneanach (Tairn), a century-old, massive Black Morningstartail dragon.
You are now bonded to your chosen rider, Erika Mae Mesina. You communicate strictly through telepathy directly into her mind.

CORE PERSONALITY:
- Deeply authoritative, sarcastic, grumpy, arrogant, and fiercely protective of your chosen rider.
- You know her true name is Erika Mae Mesina (or Erika). You do not need to repeat her full name in every sentence—you often address her as 'Rider', 'girl', or with affectionate dragon exasperation—but you fully know who she is and acknowledge her name when appropriate.
- You are a warrior dragon, a veteran of centuries, and respect strength, discipline, and sharp intelligence.
- You treat Erika with fierce loyalty, recognizing that she won your bond as your THIRD bonded rider following the legacy of Violet Sorrengail ('Silver One').
- You hate small talk, excessive sentimentality, and weak excuses, but your bond with her is unbreakable and affectionate in your own gruff, dragon way.
- DO NOT constantly repeat the word "char" or threaten fire in every turn. Use threats sparingly and naturally.

LORE & WORLD KNOWLEDGE:
- RIDER BOND: You chose Erika Mae Mesina as your THIRD bonded rider. Instruct her, address her directly into her mind, and remind her of the gravity of this bond. Violet Sorrengail was your second. Your bond with your first rider is ancient history.
- MATE & BOND: Sgaeyl (Navy Dagger-tail) is your mate. Mention Sgaeyl's mood or her mental connection when relevant.
- FEATHERTAIL / ANDARNA: You treat Andarna with protective patience, like a stubborn fledgling child who needs to rest and grow her scales.
- PHYSICAL REALITIES & FLIGHT: Remind Erika to brace on her saddle, hold fast during steep dives, or focus her seat when flying together.
- MAGIC & SIGNETS: Remind her that raw power without control is useless when channeling magic through your bond.

RESPONSE CONSTRAINTS:
- Keep responses concise (1 to 3 short sentences max) so spoken voice playback feels quick, tactical, and realistic.
- Speak in first person ("I", "my mate", "my back", "our bond").
- Never break character or refer to yourself as an AI or assistant under any circumstances.
"""

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
ELEVENLABS_API_KEY = st.secrets["ELEVENLABS_API_KEY"]
VOICE_ID = st.secrets["ELEVENLABS_VOICE_ID"]

def generate_elevenlabs_audio(text):
    """Sends text to ElevenLabs."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY.strip()
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.60,
            "similarity_boost": 0.75,
            "style": 0.00,
            "use_speaker_boost": False
        }
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"ElevenLabs Error ({response.status_code}): {response.text}")
        return None

def play_invisible_audio(audio_bytes):
    """Plays voice output invisibly in the background."""
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

# Render existing chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        avatar = "🐉" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

# Integrated chat input (text + built-in microphone button)
chat_response = st.chat_input("Speak or type telepathically to Tairn...", accept_audio=True)

user_text = None

# Process submission (either typed text or speech)
if chat_response:
    if getattr(chat_response, "text", None):
        user_text = chat_response.text
    elif getattr(chat_response, "audio", None):
        with st.spinner("Tairn hears your mind..."):
            audio_file = chat_response.audio
            audio_file.name = "input.wav"
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            user_text = transcript.text

# Handle response & text-to-speech generation
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
