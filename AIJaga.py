"""
AiJaga - pixel-style healthcare chatbot (Streamlit)

Run in the VS Code terminal:
    python -m streamlit run aijaga_app.py

Optional real AI answers: set an ANTHROPIC_API_KEY environment variable
and install the library with:  python -m pip install anthropic
"""

import base64
import json
import os
import time

import streamlit as st
from PIL import Image

st.set_page_config(page_title="AiJaga", page_icon="🩺", layout="wide")

# ==============================================================
# 1. Pixel art (each rect = x, y, width, height, colour)
# ==============================================================
DOCTOR_ICON = [  # 16 x 16: doctor with stethoscope (the AiJaga logo)
    (5, 0, 6, 1, "#4a9cc7"), (4, 1, 8, 1, "#4a9cc7"), (3, 2, 10, 4, "#4a9cc7"),
    (4, 6, 8, 1, "#4a9cc7"), (5, 7, 6, 1, "#4a9cc7"), (6, 8, 4, 1, "#4a9cc7"),
    (3, 9, 10, 1, "#4a9cc7"), (2, 10, 12, 1, "#4a9cc7"), (1, 11, 14, 1, "#4a9cc7"),
    (0, 12, 16, 4, "#4a9cc7"),
    (5, 8, 1, 4, "#14324a"), (4, 12, 3, 1, "#14324a"), (4, 13, 1, 1, "#14324a"),
    (6, 13, 1, 1, "#14324a"), (10, 8, 1, 4, "#14324a"), (9, 12, 3, 1, "#14324a"),
    (9, 13, 1, 1, "#14324a"), (11, 13, 1, 1, "#14324a"), (9, 14, 3, 1, "#14324a"),
]
HEART = [  # drawn at the top right of the logo
    (14, 0, 2, 1, "#e43b5c"), (17, 0, 2, 1, "#e43b5c"), (13, 1, 7, 2, "#e43b5c"),
    (14, 3, 5, 1, "#e43b5c"), (15, 4, 3, 1, "#e43b5c"), (16, 5, 1, 1, "#e43b5c"),
    (14, 1, 1, 1, "#ff9fb2"),
]
MASCOT = [  # 16 x 20: Dr. AiJaga in a white coat
    (4, 0, 8, 1, "#3b2a20"), (3, 1, 10, 2, "#3b2a20"), (3, 3, 1, 1, "#3b2a20"), (12, 3, 1, 1, "#3b2a20"),
    (4, 3, 8, 1, "#f2c6a0"), (3, 4, 10, 3, "#f2c6a0"), (4, 7, 8, 1, "#f2c6a0"),
    (5, 8, 6, 1, "#f2c6a0"), (7, 9, 2, 1, "#f2c6a0"),
    (5, 5, 1, 1, "#1d2b35"), (10, 5, 1, 1, "#1d2b35"),
    (4, 6, 1, 1, "#ef7d57"), (11, 6, 1, 1, "#ef7d57"), (7, 7, 2, 1, "#b5523a"),
    (2, 10, 12, 1, "#1d2b35"), (1, 11, 14, 1, "#1d2b35"), (0, 12, 16, 8, "#1d2b35"),
    (2, 11, 12, 1, "#ffffff"), (1, 12, 14, 8, "#ffffff"),
    (6, 10, 4, 1, "#2f7a6b"), (7, 11, 2, 9, "#2f7a6b"),
    (5, 10, 1, 5, "#14324a"), (10, 10, 1, 5, "#14324a"), (4, 15, 3, 1, "#14324a"),
    (4, 16, 1, 1, "#14324a"), (6, 16, 1, 1, "#14324a"), (9, 15, 3, 1, "#14324a"),
    (9, 16, 1, 1, "#14324a"), (11, 16, 1, 1, "#14324a"), (9, 17, 3, 1, "#14324a"),
    (12, 12, 1, 1, "#e43b5c"), (14, 12, 1, 1, "#e43b5c"), (12, 13, 3, 1, "#e43b5c"), (13, 14, 1, 1, "#e43b5c"),
]


def pixel_svg(rects, vw, vh, width, label):
    height = int(width * vh / vw)
    body = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>' for x, y, w, h, c in rects)
    return (f'<svg viewBox="0 0 {vw} {vh}" width="{width}" height="{height}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{label}">{body}</svg>')


@st.cache_resource
def avatar_image():
    """Draw the doctor icon as a picture for the chat avatar."""
    scale = 6
    img = Image.new("RGB", (16 * scale, 16 * scale), "#fffbef")
    for x, y, w, h, c in DOCTOR_ICON:
        img.paste(c, (x * scale, y * scale, (x + w) * scale, (y + h) * scale))
    return img


# ==============================================================
# 2. Memory (session state)
# ==============================================================
WELCOME = ("Hi, welcome to AiJaga! I'm Dr. AiJaga.\n\n"
           "Ask me a health question by typing, adding a photo 📷, or recording a voice note 🎙️.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "text": WELCOME}]
st.session_state.setdefault("asked", 0)
st.session_state.setdefault("theme", "Bright")
st.session_state.setdefault("size", "Normal")
st.session_state.setdefault("autospeak", False)

# ==============================================================
# 3. Colours, text size and pixel styling
# ==============================================================
THEMES = {
    "Bright": dict(page="#fbf6ee", frame="#ecd0a6", edge="#d9ad78", screen="#e4efec", panel="#ffffff",
                   ink="#1d2b35", sub="#3d5361", accent="#23665a", on_accent="#ffffff", soft="#d3e9e3",
                   tag="#ef7d57", border="#1d2b35", shadow="#1d2b35", user="#23665a", tv="#6e4c28"),
    "Dark": dict(page="#0c0e18", frame="#3b3651", edge="#2a2640", screen="#141726", panel="#20243a",
                 ink="#f4f4f4", sub="#b9c5d1", accent="#5fd4be", on_accent="#10131f", soft="#2a3a48",
                 tag="#ef7d57", border="#c9d4df", shadow="#000000", user="#2f7a6b", tv="#d2cbef"),
}
SIZES = {"Small": 14, "Normal": 16, "Large": 18, "Extra large": 21}

t = THEMES[st.session_state.theme]
font_px = SIZES[st.session_state.size]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Nunito:wght@500;700;800&display=swap');

html {{ font-size: {font_px}px; }}
.stApp {{ background: {t['page']}; color: {t['ink']}; font-family: 'Nunito', sans-serif; }}
.stApp p, .stApp li, .stApp label, .stApp span {{ color: {t['ink']}; }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* The TV: screen + wooden frame */
[data-testid="stMainBlockContainer"] {{
    max-width: 1280px; margin: 56px auto 150px; padding: 28px 32px !important;
    background-color: {t['screen']};
    background-image: repeating-linear-gradient(0deg, rgba(0,0,0,.03) 0 2px, transparent 2px 4px);
    border: 10px solid {t['edge']}; border-radius: 28px;
    box-shadow: 0 0 0 26px {t['frame']}, 0 16px 0 26px {t['edge']};
}}
@media (max-width: 700px) {{
    [data-testid="stMainBlockContainer"] {{ margin: 24px 10px 90px; padding: 18px !important;
        box-shadow: 0 0 0 10px {t['frame']}; }}
}}

.pixel {{ font-family: 'Silkscreen', monospace; }}

/* Pixel cards */
.st-key-mascot, .st-key-access, .st-key-chatcard {{
    background: {t['panel']}; border: 4px solid {t['border']} !important; border-radius: 0 !important;
    box-shadow: 6px 6px 0 {t['shadow']}; padding: 18px;
}}

/* Chat bubbles */
[data-testid="stChatMessage"] {{
    background: {t['panel']}; border: 3px solid {t['border']}; border-radius: 0;
    box-shadow: 4px 4px 0 {t['shadow']}; padding: 12px 14px; margin-bottom: 10px;
}}
[class*="st-key-msg_user"] [data-testid="stChatMessage"] {{
    background: {t['user']}; flex-direction: row-reverse; text-align: right; margin-left: 12%;
}}
[class*="st-key-msg_user"] [data-testid="stChatMessage"] p {{ color: #ffffff; }}
[class*="st-key-msg_bot"] [data-testid="stChatMessage"] {{ margin-right: 12%; }}
[data-testid="stChatMessage"] img {{ image-rendering: pixelated; border-radius: 0 !important; }}

/* Buttons, quick questions, inputs */
.stButton button, .st-key-chip button, .st-key-theme button {{
    border: 3px solid {t['border']} !important; border-radius: 0 !important;
    box-shadow: 3px 3px 0 {t['shadow']}; background: {t['soft']} !important; color: {t['ink']} !important;
    font-weight: 700; min-height: 44px;
}}
.stButton button:active, .st-key-chip button:active {{ transform: translate(3px, 3px); box-shadow: none; }}
.st-key-theme button[aria-checked="true"], .st-key-chip button[aria-checked="true"] {{
    background: {t['accent']} !important; color: {t['on_accent']} !important;
}}
[data-testid="stChatInput"] {{
    border: 3px solid {t['border']} !important; border-radius: 0 !important;
    background: {t['panel']} !important; box-shadow: 4px 4px 0 {t['shadow']};
}}
[data-testid="stChatInput"] div {{ background-color: {t['panel']} !important; }}
[data-testid="stChatInput"] button, [data-testid="stChatInput"] svg {{ color: {t['ink']} !important; }}
[data-testid="stChatInput"] textarea::placeholder {{ color: {t['sub']} !important; }}
[data-testid="stChatInput"] textarea {{ color: {t['ink']} !important; font-size: 1rem !important; }}

/* Clear keyboard focus ring (accessibility) */
.stApp button:focus-visible, .stApp textarea:focus-visible, .stApp input:focus-visible {{
    outline: 3px solid {t['tag']} !important; outline-offset: 3px;
}}
</style>
""", unsafe_allow_html=True)

# ==============================================================
# 4. Dr. AiJaga's brain
# ==============================================================
IMAGE_REPLY = ("Thanks for the photo. I can't diagnose from a picture, but I can share general tips. "
               "Tell me what worries you about it, and see a doctor if it's painful, spreading, bleeding or not healing.")
VOICE_REPLY = ("I received your voice note 🎙️. You can play it back above. "
               "Voice-to-text isn't switched on yet, so please also type your question and I'll answer it.")


def rule_based_answer(q: str) -> str:
    m = q.lower()
    if "headache" in m or "migraine" in m:
        return ("Common headache triggers are not drinking enough water, poor sleep, stress, skipped meals and long screen time.\n\n"
                "Drink water, rest your eyes and keep regular sleep. See a doctor quickly if a headache is sudden and severe, "
                "follows a head injury, or comes with fever, a stiff neck, weakness or confusion.")
    if "blood pressure" in m or "hypertension" in m:
        return ("To help lower blood pressure: eat less salt, stay active for about 30 minutes most days, keep a healthy weight, "
                "limit alcohol, don't smoke and manage stress.\n\nCheck your readings regularly and follow your doctor's advice about any medicine.")
    if "burn" in m:
        return ("First aid for a burn: cool it under cool running water for 20 minutes. Remove rings or tight items nearby, "
                "then cover it loosely with cling film or a clean, non-fluffy cloth.\n\nDon't use ice, butter or toothpaste. "
                "Get medical help for large or deep burns, burns on the face or hands, or burns on a child.")
    if "sleep" in m or "insomnia" in m:
        return ("Most adults need 7 to 9 hours of sleep. Keep a regular bedtime, avoid screens and caffeine late in the day, "
                "and keep your room dark, quiet and cool.")
    if "fever" in m or "temperature" in m:
        return ("For a mild fever: rest, drink plenty of fluids and wear light clothing. Fever medicine like paracetamol can help; "
                "follow the dose on the label.\n\nSee a doctor if it lasts more than 3 days, is very high, or comes with a rash, "
                "stiff neck, confusion or trouble breathing.")
    if any(w in m for w in ["snack", "food", "eat", "diet"]):
        return "Healthy snack ideas: fresh fruit, a small handful of plain nuts, plain yoghurt, wholegrain crackers, or vegetable sticks with hummus."
    if any(w in m for w in ["doctor", "emergency", "hospital", "clinic"]):
        return ("See a doctor if symptoms are severe, last more than a few days, or keep coming back.\n\n"
                "Call 999 straight away for chest pain, trouble breathing, signs of a stroke (face drooping, arm weakness, "
                "slurred speech) or heavy bleeding.")
    if m.strip().split(" ")[0] in ("hi", "hello", "hey"):
        return "Hello! What health question can I help with today?"
    return ("Thanks for your question. I share general health information, not a diagnosis.\n\n"
            "Try one of the quick questions, or tell me more: what you feel, where, and for how long.")


def ai_answer(text: str, image_bytes, image_type):
    """Real AI reply with Claude (only used if ANTHROPIC_API_KEY is set)."""
    import anthropic

    content = []
    if image_bytes:
        content.append({"type": "image", "source": {"type": "base64", "media_type": image_type,
                                                    "data": base64.b64encode(image_bytes).decode()}})
    content.append({"type": "text", "text": text or "Please look at this photo."})
    response = anthropic.Anthropic().messages.create(
        model="claude-sonnet-5-5",
        max_tokens=500,
        system=("You are Dr. AiJaga, a friendly healthcare assistant in a retro pixel app. Give short, clear, general "
                "health information in simple English. Never diagnose. Advise seeing a doctor when needed, and calling "
                "999 (Malaysia) in an emergency."),
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text


def get_reply(text, image_bytes=None, image_type=None, has_audio=False):
    if os.environ.get("ANTHROPIC_API_KEY") and (text or image_bytes):
        try:
            return ai_answer(text, image_bytes, image_type)
        except Exception as e:  # no internet, missing library, etc.
            st.toast(f"AI is offline ({type(e).__name__}), using the built-in answers.")
    parts = []
    if has_audio:
        parts.append(VOICE_REPLY)
    if image_bytes:
        parts.append(IMAGE_REPLY)
    if text:
        parts.append(rule_based_answer(text))
    return "\n\n".join(parts)


def add_turn(text="", image=None, audio=None):
    """Save the user's message and Dr. AiJaga's reply."""
    image_bytes = image.getvalue() if image else None
    image_type = image.type if image else None
    audio_bytes = audio.getvalue() if audio else None
    st.session_state.messages.append({"role": "user", "text": text, "image": image_bytes, "audio": audio_bytes})
    reply = get_reply(text, image_bytes, image_type, has_audio=bool(audio_bytes))
    st.session_state.messages.append({"role": "assistant", "text": reply})
    st.session_state.asked += 1
    if st.session_state.autospeak:
        st.session_state.speak_next = reply


def speak(text):
    """Read text aloud using the browser's built-in voice."""
    clean = text.replace("\n", " ").replace("🎙️", "").replace("📷", "")
    st.iframe(f"""<script>
      try {{ const s = window.parent.speechSynthesis; s.cancel();
             s.speak(new SpeechSynthesisUtterance({json.dumps(clean)})); }} catch (e) {{}}
    </script>""", height=1)


def ask_chip():
    """Runs when a quick-question button is clicked."""
    question = st.session_state.chip
    if question:
        add_turn(question)
    st.session_state.chip = None


# ==============================================================
# 5. Header: logo, level bar, theme
# ==============================================================
level = 1 + st.session_state.asked // 7
xp = min(100, 30 + (st.session_state.asked % 7) * 10)

h1, h2, h3 = st.columns([3, 3, 2], vertical_alignment="center")
with h1:
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px">'
        f'{pixel_svg(DOCTOR_ICON + HEART, 20, 16, 60, "AiJaga logo: doctor with stethoscope and a heart")}'
        f'<span class="pixel" style="font-size:2rem;font-weight:700;color:{t["ink"]}">'
        f'<span style="color:{t["accent"]}">Ai</span>Jaga</span></div>',
        unsafe_allow_html=True)
with h2:
    st.markdown(
        f'<p class="pixel" style="margin:0 0 4px;font-size:.8rem;color:{t["sub"]}">LEVEL {level} · HEALTH HERO</p>'
        f'<div role="progressbar" aria-label="Health hero progress" aria-valuemin="0" aria-valuemax="100" '
        f'aria-valuenow="{xp}" style="height:16px;border:3px solid {t["border"]};background:{t["panel"]}">'
        f'<div style="height:100%;width:{xp}%;background:{t["tag"]}"></div></div>',
        unsafe_allow_html=True)
with h3:
    st.segmented_control("Colour theme", ["Bright", "Dark"], key="theme", required=True,
                         format_func=lambda x: (":material/light_mode: " if x == "Bright" else ":material/dark_mode: ") + x,
                         label_visibility="collapsed")

st.write("")

# ==============================================================
# 6. Main area: side panel + chat (stacks on small screens)
# ==============================================================
left, right = st.columns([1, 2.3], gap="large")

with left:
    with st.container(key="mascot"):
        st.markdown(
            f'<div style="text-align:center"><div style="display:flex;justify-content:center">'
            f'{pixel_svg(MASCOT, 16, 20, 128, "Dr. AiJaga, a pixel doctor with a stethoscope and heart badge")}</div>'
            f'<p class="pixel" style="display:inline-block;margin:10px 0;padding:4px 14px;background:{t["tag"]};'
            f'border:3px solid {t["border"]};color:#1d2b35;font-weight:700">DR. AIJAGA</p>'
            f'<p style="color:{t["sub"]};margin:0">Your friendly medical assistant. Ask by typing, sending a photo '
            f'or recording a voice note.</p></div>',
            unsafe_allow_html=True)

    st.write("")
    with st.container(key="access"):
        st.markdown('<p class="pixel" style="font-weight:700;margin:0">ACCESSIBILITY</p>', unsafe_allow_html=True)
        st.select_slider("Text size", options=list(SIZES), key="size")
        st.toggle("Read Dr. AiJaga's replies aloud", key="autospeak")
        st.caption("Tip: press Enter to send. Use Tab to move between buttons. Every reply has a Listen button.")

with right:
    with st.container(key="chatcard"):
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:8px">'
            f'<h1 class="pixel" style="margin:0;font-size:1.4rem;color:{t["ink"]}">Hi, welcome to AiJaga</h1>'
            f'<span class="pixel" style="font-size:.8rem;color:{t["sub"]}">'
            f'<span style="display:inline-block;width:10px;height:10px;background:#38b764"></span> DR. AIJAGA IS ONLINE</span></div>',
            unsafe_allow_html=True)

        chat_box = st.container(height=460, border=False)
        with chat_box:
            for i, msg in enumerate(st.session_state.messages):
                if msg["role"] == "assistant":
                    with st.container(key=f"msg_bot_{i}"):
                        with st.chat_message("assistant", avatar=avatar_image()):
                            st.markdown(msg["text"])
                            if st.button(":material/volume_up: Listen", key=f"listen_{i}",
                                         help="Read this reply aloud"):
                                speak(msg["text"])
                else:
                    with st.container(key=f"msg_user_{i}"):
                        with st.chat_message("user", avatar=":material/person:"):
                            if msg.get("image"):
                                st.image(msg["image"], width=260, caption="Photo you shared")
                            if msg.get("audio"):
                                st.audio(msg["audio"])
                            if msg.get("text"):
                                st.markdown(msg["text"])

        st.pills("Quick questions", key="chip", on_change=ask_chip, options=[
            "Why do I get headaches?", "How to lower blood pressure", "First aid for burns",
            "Tips for better sleep", "What to do for a fever", "Healthy snack ideas", "When should I see a doctor?",
        ])

        prompt = st.chat_input(
            "Type your healthcare question here…",
            accept_file=True, file_type=["png", "jpg", "jpeg", "webp"], accept_audio=True,
        )

        st.caption("AiJaga shares general health information, not a diagnosis. In an emergency, call 999.")

# Read the newest reply aloud if that setting is on
if st.session_state.get("speak_next"):
    speak(st.session_state.pop("speak_next"))

# ==============================================================
# 7. Handle a new message (text, photo and/or voice)
# ==============================================================
if prompt:
    with chat_box, st.spinner("Dr. AiJaga is typing…"):
        time.sleep(0.4)
        add_turn(
            text=(prompt.text or "").strip(),
            image=prompt.files[0] if prompt.files else None,
            audio=prompt.audio,
        )
    st.rerun()

# TV bottom bar
st.markdown(
    f'<div aria-hidden="true" style="display:flex;justify-content:space-between;align-items:center;'
    f'margin:40px -10px -10px;padding-top:10px">'
    f'<span style="letter-spacing:4px;color:{t["edge"]};font-size:2rem">▮▮▮▮▮</span>'
    f'<span class="pixel" style="color:{t["sub"]};font-weight:700">AiJaga TV</span>'
    f'<span style="color:{t["edge"]};font-size:2rem">● ● <span style="color:#ef7d57;font-size:1rem">●</span></span></div>',
    unsafe_allow_html=True)