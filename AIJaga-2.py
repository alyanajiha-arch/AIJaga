"""
AiJaga — retro "AiJaga TV" health assistant, built with Streamlit.

Run it with:
    pip install -r requirements.txt
    streamlit run app.py

Pages: Home (3 mode boxes) -> Chat-box, Quiz, Video.
"""

import html
import json

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AiJaga", page_icon="🩺", layout="wide")

# ---------------------------------------------------------------------------
# 1. Colours (Bright and Dark themes)
# ---------------------------------------------------------------------------
THEMES = {
    "bright": {
        "page": "#F6F1E7", "frame": "#EBC99D", "frame_edge": "#D4A774", "frame_text": "#6E4F2C",
        "screen": "#E1EEEA", "scan": "rgba(255,255,255,0.5)", "ink": "#1C2B33", "sub": "#344A50",
        "card": "#FFFFFF", "chat_bg": "#F2F7F5", "teal": "#2D6A5C", "coral": "#E36F52",
        "chip": "#D3EAE2", "btn_text": "#FFFFFF", "good": "#BDE5CF", "bad": "#F6C9BD",
    },
    "dark": {
        "page": "#111517", "frame": "#3B3229", "frame_edge": "#2A231C", "frame_text": "#B49673",
        "screen": "#13221F", "scan": "rgba(0,0,0,0.28)", "ink": "#E4F1ED", "sub": "#A8C3BC",
        "card": "#1A2E2A", "chat_bg": "#152623", "teal": "#5CC0A6", "coral": "#F08A6E",
        "chip": "#1F3A34", "btn_text": "#0D1916", "good": "#235A45", "bad": "#6A2F25",
    },
}

# ---------------------------------------------------------------------------
# 2. Content
# ---------------------------------------------------------------------------
QUICK_QUESTIONS = [
    "Why do I get headaches?",
    "How to lower blood pressure",
    "First aid for burns",
    "Tips for better sleep",
    "Healthy eating basics",
]

QUIZ = [
    {"q": "How long should you scrub your hands with soap when washing them?",
     "options": ["About 5 seconds", "At least 20 seconds", "Exactly 2 minutes"], "answer": 1,
     "explain": "Scrub for at least 20 seconds — about as long as humming “Happy Birthday” twice."},
    {"q": "What is the best first aid for a minor burn?",
     "options": ["Put ice directly on it", "Spread butter or toothpaste on it",
                 "Cool it under cool running water for about 20 minutes"], "answer": 2,
     "explain": "Cool running water helps. Ice, butter and toothpaste can make the skin damage worse."},
    {"q": "How much sleep do most adults need each night?",
     "options": ["4–5 hours", "7–9 hours", "11–12 hours"], "answer": 1,
     "explain": "Most adults need 7 to 9 hours of sleep a night to feel and work their best."},
    {"q": "What is a normal resting heart rate for most adults?",
     "options": ["30–40 beats per minute", "60–100 beats per minute", "120–150 beats per minute"], "answer": 1,
     "explain": "For most adults a resting heart rate between 60 and 100 beats per minute is normal. Very fit people can be lower."},
    {"q": "Which of these can be a sign of dehydration?",
     "options": ["Pale, clear urine", "A runny nose", "Feeling very thirsty with dark yellow urine"], "answer": 2,
     "explain": "Strong thirst and dark yellow urine are common signs your body needs more fluids."},
]

# Put a real video link (YouTube or .mp4) in "url" and it will play on the Video page.
VIDEOS = [
    {"title": "Washing your hands the right way", "tag": "HYGIENE", "url": None,
     "desc": "Learn the simple steps that wash away germs and help stop infections from spreading."},
    {"title": "First aid for burns", "tag": "FIRST AID", "url": None,
     "desc": "What to do in the first minutes after a minor burn — and what not to put on it."},
    {"title": "CPR basics", "tag": "FIRST AID", "url": None,
     "desc": "An introduction to hands-only CPR. Always call 999 first in a real emergency."},
    {"title": "Building a healthy plate", "tag": "NUTRITION", "url": None,
     "desc": "How to balance vegetables, protein and whole grains in your everyday meals."},
    {"title": "Better sleep habits", "tag": "WELLBEING", "url": None,
     "desc": "Small changes to your evening routine that can help you sleep more soundly."},
    {"title": "Spotting dehydration", "tag": "EVERYDAY HEALTH", "url": None,
     "desc": "Common signs that your body needs more fluids, and easy ways to stay hydrated."},
]

WELCOME = ("Hi, welcome to AiJaga! I'm Dr. AiJaga.\n"
           "Ask me a health question by typing, adding a photo, or recording a voice note.")
PLACEHOLDER_REPLY = ("Thanks for your question! My medical answers are being connected, so a full "
                     "reply is coming soon. If this is urgent, please see a doctor or call 999.")
DISCLAIMER = "AiJaga shares general health information, not a diagnosis. In an emergency, call 999."
TEXT_SIZES = [("Small", 15), ("Normal", 17), ("Large", 20), ("Extra large", 23)]

# Pixel-art doctor, drawn as an SVG of little squares.
DOCTOR_SVG = """
<svg width="{w}" height="{h}" viewBox="0 0 16 20" shape-rendering="crispEdges" role="img" aria-label="Dr. AiJaga">
<rect x="6" y="0" width="4" height="1" fill="#C9D3D0"/><rect x="7" y="0" width="2" height="1" fill="#E36F52"/>
<rect x="3" y="1" width="10" height="1" fill="#1C2B33"/>
<rect x="3" y="2" width="1" height="5" fill="#1C2B33"/><rect x="12" y="2" width="1" height="5" fill="#1C2B33"/>
<rect x="4" y="1" width="8" height="2" fill="#4A2E22"/>
<rect x="4" y="3" width="8" height="4" fill="#F2C29B"/>
<rect x="6" y="4" width="1" height="2" fill="#1C2B33"/><rect x="9" y="4" width="1" height="2" fill="#1C2B33"/>
<rect x="5" y="5" width="1" height="1" fill="#E36F52"/><rect x="10" y="5" width="1" height="1" fill="#E36F52"/>
<rect x="4" y="7" width="8" height="1" fill="#1C2B33"/><rect x="7" y="6" width="2" height="1" fill="#1C2B33"/>
<rect x="7" y="8" width="2" height="1" fill="#F2C29B"/>
<rect x="3" y="8" width="10" height="11" fill="#1C2B33"/>
<rect x="4" y="9" width="8" height="9" fill="#FFFFFF"/>
<rect x="5" y="8" width="6" height="4" fill="#1C2B33"/><rect x="6" y="9" width="4" height="3" fill="#2D6A5C"/>
<rect x="7" y="9" width="2" height="1" fill="#F2C29B"/>
<rect x="7" y="12" width="2" height="2" fill="#E36F52"/>
<rect x="10" y="12" width="2" height="1" fill="#2D6A5C"/>
</svg>
"""

# ---------------------------------------------------------------------------
# 3. Session state (remembers things between clicks)
# ---------------------------------------------------------------------------
DEFAULTS = {
    "page": "home",
    "theme": "bright",
    "messages": [{"role": "bot", "text": WELCOME}],
    "text_size": 1,
    "read_aloud": False,
    "speak": None,
    "quiz_i": 0, "quiz_pick": None, "quiz_score": 0, "quiz_done": False,
    "video_i": 0, "video_seen": set(), "video_playing": False,
}
for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, (list, set)) else value

S = st.session_state
C = THEMES[S.theme]


def go(page):
    S.page = page


# ---------------------------------------------------------------------------
# 4. Retro "AiJaga TV" styling
# ---------------------------------------------------------------------------
def inject_css():
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Silkscreen:wght@400;700&family=Nunito:wght@500;600;700&display=swap');

#MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0; }}
.stApp {{ background: {C['page']}; }}
html, body, .stApp, p, label, li, input, textarea {{ font-family: 'Nunito', sans-serif; color: {C['ink']}; }}

/* The TV body and screen */
.block-container {{
  max-width: 1240px; margin: 24px auto 0; padding: 26px 30px 30px !important;
  background-color: {C['screen']};
  background-image: repeating-linear-gradient(0deg, {C['scan']} 0 2px, transparent 2px 5px);
  border: 8px solid {C['frame_edge']}; border-radius: 28px;
  box-shadow: 0 0 0 26px {C['frame']}, 0 26px 0 26px {C['frame']};
}}

.pixel {{ font-family: 'Silkscreen', monospace; font-weight: 700; letter-spacing: 1px; }}
.sub {{ color: {C['sub']}; }}
h1, h2, h3 {{ font-family: 'Silkscreen', monospace !important; color: {C['ink']} !important; letter-spacing: 1px; }}

.card {{ background: {C['card']}; border: 4px solid {C['ink']}; box-shadow: 8px 8px 0 {C['ink']};
         padding: 20px 22px; margin-bottom: 18px; color: {C['ink']}; }}
.tag {{ display: inline-block; padding: 4px 12px; background: {C['coral']}; border: 3px solid {C['ink']};
        color: #1C2B33; font-family: 'Silkscreen', monospace; font-weight: 700; font-size: 14px; letter-spacing: 1px; }}
.logo {{ display: flex; align-items: center; gap: 12px; }}
.logo-box {{ width: 30px; height: 30px; background: {C['teal']}; box-shadow: 5px 5px 0 {C['coral']}; }}
.xp-label {{ font-family: 'Silkscreen', monospace; font-size: 12px; letter-spacing: 2px; color: {C['sub']}; }}
.xp-bar {{ height: 18px; border: 3px solid {C['ink']}; background: {C['card']}; }}
.xp-fill {{ height: 100%; background: {C['coral']}; }}

/* Buttons: chunky pixel style */
.stButton > button, .stFormSubmitButton > button {{
  border: 3px solid {C['ink']} !important; border-radius: 0 !important;
  background: {C['chip']} !important; color: {C['ink']} !important;
  box-shadow: 4px 4px 0 {C['ink']}; font-weight: 700; min-height: 46px;
}}
.stButton > button:hover {{ transform: translate(-2px, -2px); box-shadow: 6px 6px 0 {C['ink']}; }}
.stButton > button[kind="primary"], .stFormSubmitButton > button {{
  background: #2D6A5C !important; color: #FFFFFF !important;
  font-family: 'Silkscreen', monospace; letter-spacing: 1px;
}}
.stButton > button p, .stFormSubmitButton > button p {{ color: inherit !important; white-space: normal; }}

/* Text boxes */
.stTextInput input, [data-testid="stChatInput"] textarea {{
  border-radius: 0 !important; background: {C['card']} !important; color: {C['ink']} !important;
}}
.stTextInput > div > div, [data-testid="stChatInput"] {{ border: 3px solid {C['ink']} !important; border-radius: 0 !important; }}

/* Mode cards on the home page */
.mode {{ text-align: center; min-height: 190px; display: flex; flex-direction: column;
         align-items: center; justify-content: center; gap: 10px; }}
.mode .title {{ font-family: 'Silkscreen', monospace; font-weight: 700; font-size: 22px; color: {C['teal']}; }}

/* Chat bubbles */
.chat-log {{ background: {C['chat_bg']}; border: 3px solid {C['ink']}; padding: 18px;
             max-height: 460px; overflow-y: auto; margin-bottom: 14px; }}
.bubble {{ border: 3px solid {C['ink']}; box-shadow: 5px 5px 0 {C['ink']}; padding: 12px 16px;
           margin: 0 0 16px; max-width: 80%; white-space: pre-line; line-height: 1.5; }}
.bubble.bot {{ background: {C['card']}; color: {C['ink']}; }}
.bubble.user {{ background: {C['teal']}; color: {C['btn_text']}; margin-left: auto; }}
.who {{ display: block; font-family: 'Silkscreen', monospace; font-size: 11px; letter-spacing: 2px; margin-bottom: 4px; opacity: .85; }}

.video-screen {{ aspect-ratio: 16/9; background: #1C2B33; border: 4px solid {C['ink']};
                 display: flex; align-items: center; justify-content: center; flex-direction: column; gap: 12px;
                 background-image: repeating-linear-gradient(0deg, rgba(255,255,255,.05) 0 2px, transparent 2px 5px); }}
.play {{ width: 76px; height: 76px; background: #E36F52; border: 4px solid #fff; display: flex;
         align-items: center; justify-content: center; color: #fff; font-size: 30px; }}

.tv-footer {{ display: flex; justify-content: space-between; align-items: center;
              margin: 40px -30px -30px; padding: 22px 36px; background: {C['frame']}; }}
.grille span {{ display: inline-block; width: 8px; height: 36px; margin-right: 8px; border-radius: 3px; background: {C['frame_edge']}; }}
.knob {{ display: inline-block; width: 40px; height: 40px; border-radius: 50%; background: {C['frame_edge']}; margin-left: 14px; }}
.led {{ display: inline-block; width: 13px; height: 13px; border-radius: 50%; background: {C['coral']}; margin-left: 14px; }}
.disclaimer {{ text-align: center; font-size: 14px; color: {C['sub']}; margin-top: 18px; }}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 5. Shared pieces
# ---------------------------------------------------------------------------
def top_bar(xp_label, xp_percent, show_home=True):
    left, middle, right = st.columns([2.2, 2.4, 1.6])
    with left:
        if show_home:
            st.button("◂ HOME", on_click=go, args=("home",), key=f"home_{S.page}")
        st.markdown("<div class='logo'><div class='logo-box'></div>"
                    f"<span class='pixel' style='font-size:26px;color:{C['teal']}'>AiJaga</span></div>",
                    unsafe_allow_html=True)
    with middle:
        st.markdown(f"<div class='xp-label'>{xp_label}</div>"
                    f"<div class='xp-bar'><div class='xp-fill' style='width:{xp_percent}%'></div></div>",
                    unsafe_allow_html=True)
    with right:
        b, d = st.columns(2)
        b.button("BRIGHT", key=f"bright_{S.page}", use_container_width=True,
                 type="primary" if S.theme == "bright" else "secondary",
                 on_click=lambda: S.update(theme="bright"))
        d.button("DARK", key=f"dark_{S.page}", use_container_width=True,
                 type="primary" if S.theme == "dark" else "secondary",
                 on_click=lambda: S.update(theme="dark"))


def tv_footer():
    st.markdown(f"<p class='disclaimer'>{DISCLAIMER}</p>"
                "<div class='tv-footer'>"
                "<div class='grille'><span></span><span></span><span></span><span></span><span></span></div>"
                f"<span class='pixel' style='color:{C['frame_text']};font-size:18px;letter-spacing:3px'>AIJAGA TV</span>"
                "<div><span class='knob'></span><span class='knob'></span><span class='led'></span></div>"
                "</div>", unsafe_allow_html=True)


def speak_if_needed():
    """Read text aloud in the browser using its built-in speech voice."""
    if S.speak:
        components.html(
            "<script>try{const s=window.parent.speechSynthesis||window.speechSynthesis;"
            f"s.cancel();s.speak(new SpeechSynthesisUtterance({json.dumps(S.speak)}));}}catch(e){{}}</script>",
            height=0)
        S.speak = None


# ---------------------------------------------------------------------------
# 6. Pages
# ---------------------------------------------------------------------------
def home_page():
    top_bar("LEVEL 1 · HEALTH HERO", 30, show_home=False)

    st.markdown(
        "<div style='display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:28px;margin-top:20px'>"
        f"<div style='text-align:center'>{DOCTOR_SVG.format(w=104, h=130)}<br><span class='tag'>DR. AIJAGA</span></div>"
        "<div class='card' style='max-width:440px;margin:0'>"
        "<div class='pixel sub' style='font-size:12px'>DR. AIJAGA</div>"
        "<p style='font-size:20px;font-weight:600;margin:6px 0 0'>I am Dr. AiJaga, ready to help you! "
        "Pick a mode below to press start.</p></div></div>"
        "<h1 style='text-align:center;font-size:46px;margin:24px 0 0'>Hi, welcome to AiJaga</h1>"
        "<p class='pixel sub' style='text-align:center;font-size:17px'>CHOOSE YOUR MODE...</p>",
        unsafe_allow_html=True)

    modes = [
        ("chat", "CHAT-BOX", "Ask Dr. AiJaga anything by text, photo or voice",
         f"<svg width='60' height='68' viewBox='0 0 8 9' shape-rendering='crispEdges'>"
         f"<rect x='2' y='0' width='4' height='4' fill='{C['ink']}'/><rect x='0' y='5' width='8' height='4' fill='{C['ink']}'/>"
         f"<rect x='5' y='6' width='2' height='2' fill='{C['coral']}'/></svg>"),
        ("quiz", "QUIZ", "Test your health knowledge and level up",
         f"<span class='pixel' style='font-size:56px;color:{C['coral']}'>( ? )</span>"),
        ("video", "VIDEO", "Watch short health and first-aid videos",
         f"<svg width='84' height='63' viewBox='0 0 12 9' shape-rendering='crispEdges'>"
         f"<rect width='12' height='9' fill='{C['ink']}'/><rect x='1' y='1' width='10' height='7' fill='{C['chip']}'/>"
         f"<rect x='4' y='2' width='1' height='5' fill='{C['teal']}'/><rect x='5' y='3' width='1' height='3' fill='{C['teal']}'/>"
         f"<rect x='6' y='4' width='1' height='1' fill='{C['teal']}'/></svg>"),
    ]
    _, *cols, _ = st.columns([0.3, 1, 1, 1, 0.3], gap="large")
    for col, (page, title, desc, icon) in zip(cols, modes):
        with col:
            st.markdown(f"<div class='card mode'>{icon}<div class='title'>{title}</div>"
                        f"<div class='sub' style='font-weight:600'>{desc}</div></div>", unsafe_allow_html=True)
            st.button(f"OPEN {title} ▸", key=f"open_{page}", on_click=go, args=(page,),
                      type="primary", use_container_width=True)
    tv_footer()


def bot_reply(text):
    S.messages.append({"role": "bot", "text": text})
    if S.read_aloud:
        S.speak = text


def ask(question):
    question = (question or "").strip()
    if question:
        S.messages.append({"role": "user", "text": question})
        bot_reply(PLACEHOLDER_REPLY)


def chat_page():
    asked = sum(1 for m in S.messages if m["role"] == "user")
    top_bar("LEVEL 1 · HEALTH HERO", min(30 + asked * 10, 100))
    size_name, size_px = TEXT_SIZES[S.text_size]

    left, right = st.columns([1, 2.6], gap="large")

    with left:
        st.markdown(f"<div class='card' style='text-align:center'>{DOCTOR_SVG.format(w=104, h=130)}<br>"
                    "<span class='tag'>DR. AIJAGA</span>"
                    "<p class='sub' style='margin-top:12px'>Your friendly medical assistant. Ask by typing, "
                    "sending a photo or recording a voice note.</p></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:15px;margin:10px 0 4px'>ACCESSIBILITY</h3>", unsafe_allow_html=True)
        st.markdown(f"**Text size: {size_name}**")
        a, b = st.columns(2)
        a.button("A−", key="smaller", use_container_width=True,
                 on_click=lambda: S.update(text_size=max(0, S.text_size - 1)))
        b.button("A+", key="bigger", use_container_width=True,
                 on_click=lambda: S.update(text_size=min(len(TEXT_SIZES) - 1, S.text_size + 1)))
        st.checkbox("Read Dr. AiJaga's replies aloud", key="read_aloud")
        st.caption("Tip: press Enter to send. Every reply has a Listen button.")

    with right:
        st.markdown("<div style='display:flex;justify-content:space-between;align-items:center'>"
                    "<h2 style='font-size:20px;margin:0'>HI, WELCOME TO AIJAGA</h2>"
                    "<span class='pixel sub' style='font-size:12px'>"
                    "<span style='display:inline-block;width:10px;height:10px;background:#2FAE5E;margin-right:8px'></span>"
                    "DR. AIJAGA IS ONLINE</span></div>", unsafe_allow_html=True)

        # Message history
        for i, msg in enumerate(S.messages):
            who = "DR. AIJAGA" if msg["role"] == "bot" else "PLAYER 1"
            if msg.get("image") is not None:
                st.image(msg["image"], width=220)
            st.markdown(f"<div class='bubble {msg['role']}' style='font-size:{size_px}px'>"
                        f"<span class='who'>{who}</span>{html.escape(msg['text'])}</div>",
                        unsafe_allow_html=True)
            if msg["role"] == "bot":
                st.button("🔊 Listen", key=f"listen_{i}", on_click=lambda t=msg["text"]: S.update(speak=t))

        # Quick questions
        st.markdown("<div class='pixel sub' style='font-size:11px;letter-spacing:2px;margin-top:10px'>"
                    "QUICK QUESTIONS</div>", unsafe_allow_html=True)
        q_cols = st.columns(len(QUICK_QUESTIONS))
        for col, q in zip(q_cols, QUICK_QUESTIONS):
            col.button(q, key=f"quick_{q}", on_click=ask, args=(q,), use_container_width=True)

        # Photo and voice note
        with st.expander("📷 Add a photo  ·  🎙 Record a voice note"):
            photo = st.file_uploader("Send a photo", type=["png", "jpg", "jpeg"], key="photo")
            if photo is not None and st.button("Send photo", key="send_photo"):
                S.messages.append({"role": "user", "text": "(Photo sent)", "image": photo.getvalue()})
                bot_reply("Thanks for the photo! Photo checking is coming soon. "
                          "For now, please also describe what you see in words.")
                st.rerun()
            if hasattr(st, "audio_input"):
                voice = st.audio_input("Record a voice note", key="voice")
                if voice is not None and st.button("Send voice note", key="send_voice"):
                    S.messages.append({"role": "user", "text": "(Voice note sent)"})
                    bot_reply("Thanks for the voice note! Voice support is coming soon. "
                              "For now, please type your question.")
                    st.rerun()

        # Typing box
        with st.form("ask_form", clear_on_submit=True, border=False):
            box, send = st.columns([5, 1])
            question = box.text_input("Your healthcare question", label_visibility="collapsed",
                                      placeholder="Type your healthcare question here...")
            if send.form_submit_button("SEND", use_container_width=True):
                ask(question)
                st.rerun()

    speak_if_needed()
    tv_footer()


def quiz_page():
    total = len(QUIZ)
    i, pick = S.quiz_i, S.quiz_pick
    answered = pick is not None
    shown = total if S.quiz_done else i + 1
    done_count = total if S.quiz_done else i + (1 if answered else 0)
    top_bar(f"SCORE {S.quiz_score} / {total} · QUESTION {shown} OF {total}", round(done_count / total * 100))

    st.markdown("<h1 style='text-align:center;font-size:38px;margin-top:20px'>( ? ) HEALTH QUIZ</h1>",
                unsafe_allow_html=True)
    _, mid, _ = st.columns([0.6, 2, 0.6])

    with mid:
        if S.quiz_done:
            score = S.quiz_score
            msg = ("Perfect score — you are a true Health Hero!" if score == total
                   else "Great job! A little more practice and you’ll ace it." if score >= 3
                   else "Good start! Try again to level up.")
            st.markdown(f"<div class='card' style='text-align:center'><span class='tag'>LEVEL COMPLETE!</span>"
                        f"<p class='pixel' style='font-size:44px;margin:16px 0'>{score} / {total}</p>"
                        f"<p class='sub' style='font-size:19px;font-weight:600'>{msg}</p></div>",
                        unsafe_allow_html=True)
            a, b = st.columns(2)
            a.button("PLAY AGAIN", type="primary", use_container_width=True,
                     on_click=lambda: S.update(quiz_i=0, quiz_pick=None, quiz_score=0, quiz_done=False))
            b.button("ASK DR. AIJAGA", use_container_width=True, on_click=go, args=("chat",))
        else:
            item = QUIZ[i]
            st.markdown(f"<div class='card'><span class='tag'>QUESTION {i + 1}</span>"
                        f"<h2 style='font-family:Nunito,sans-serif !important;font-size:24px;letter-spacing:0;"
                        f"margin:14px 0 0'>{item['q']}</h2></div>", unsafe_allow_html=True)

            def choose(k):
                if S.quiz_pick is None:
                    S.quiz_pick = k
                    if k == QUIZ[S.quiz_i]["answer"]:
                        S.quiz_score += 1

            for k, option in enumerate(item["options"]):
                label = option
                if answered and k == item["answer"]:
                    label = "✓ " + option
                elif answered and k == pick:
                    label = "✕ " + option
                st.button(label, key=f"opt_{i}_{k}", on_click=choose, args=(k,),
                          disabled=answered, use_container_width=True)

            if answered:
                if pick == item["answer"]:
                    st.success("★ CORRECT! +1 XP — " + item["explain"])
                else:
                    st.error("✕ NOT QUITE — " + item["explain"])
                last = i == total - 1
                st.button("SEE SCORE ▸" if last else "NEXT ▸", type="primary",
                          on_click=(lambda: S.update(quiz_done=True)) if last
                          else (lambda: S.update(quiz_i=S.quiz_i + 1, quiz_pick=None)))
    tv_footer()


def video_page():
    n = len(VIDEOS)
    watched = len(S.video_seen)
    top_bar(f"WATCHED {watched} OF {n} VIDEOS", round(watched / n * 100))
    current = VIDEOS[S.video_i]

    def select(k):
        S.video_i = k % n
        S.video_playing = False

    def play():
        S.video_playing = True
        S.video_seen.add(S.video_i)

    player, playlist = st.columns([2.2, 1], gap="large")

    with player:
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center'>"
                    f"<h2 style='font-size:20px;margin:0'>NOW PLAYING</h2><span class='tag'>{current['tag']}</span></div>",
                    unsafe_allow_html=True)
        if S.video_playing and current["url"]:
            st.video(current["url"])
        else:
            text = "[ YOUR VIDEO PLAYS HERE ]" if S.video_playing else "PRESS PLAY"
            st.markdown(f"<div class='video-screen'><div class='play'>▶</div>"
                        f"<span class='pixel' style='color:#D3EAE2;font-size:14px'>{text}</span></div>",
                        unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-family:Nunito,sans-serif !important;font-size:24px;letter-spacing:0'>"
                    f"{current['title']}</h3><p class='sub' style='font-size:17px'>{current['desc']}</p>",
                    unsafe_allow_html=True)
        a, b, c, d = st.columns(4)
        a.button("▶ PLAY", type="primary", use_container_width=True, on_click=play)
        b.button("◂ PREV", use_container_width=True, on_click=select, args=(S.video_i - 1,))
        c.button("NEXT ▸", use_container_width=True, on_click=select, args=(S.video_i + 1,))
        d.button("TAKE THE QUIZ", use_container_width=True, on_click=go, args=("quiz",))

    with playlist:
        st.markdown("<h2 style='font-size:16px;margin:0 0 10px'>PLAYLIST</h2>", unsafe_allow_html=True)
        for k, v in enumerate(VIDEOS):
            mark = "▶ " if k == S.video_i else ("✓ " if k in S.video_seen else "")
            st.button(f"{k + 1:02d} · {mark}{v['title']}", key=f"vid_{k}", on_click=select, args=(k,),
                      type="primary" if k == S.video_i else "secondary", use_container_width=True)
    tv_footer()


# ---------------------------------------------------------------------------
# 7. Show the right page
# ---------------------------------------------------------------------------
inject_css()
{"home": home_page, "chat": chat_page, "quiz": quiz_page, "video": video_page}[S.page]()