"""
app.py
------
TalentScout Hiring Assistant — Streamlit UI
Built with LangChain + Groq | Professional corporate design
Includes Admin Dashboard to view saved profiles.
"""

import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from chatbot import TalentScoutBot, Stage
from data_handler import load_all_candidates

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TalentScout – AI Hiring Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS — Professional dark-mode theme
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #111827 50%, #0d1117 100%);
    color: #e2e8f0;
}

/* ── Header banner ── */
.ts-header {
    background: linear-gradient(90deg, #3730a3 0%, #4f46e5 50%, #312e81 100%);
    padding: 1.5rem 2rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    display: flex;
    align-items: center;
    gap: 1rem;
    border-left: 4px solid #818cf8;
}

.ts-header h1 {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 600;
    color: white;
    letter-spacing: -0.5px;
}

.ts-header p {
    margin: 0;
    color: #c7d2fe;
    font-size: 0.9rem;
}

/* ── Chat container ── */
.chat-container {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 1.5rem;
    min-height: 500px;
    max-height: 560px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

/* ── Message bubbles ── */
.msg-bot {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.2rem;
    align-items: flex-start;
}

.msg-user {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.2rem;
    align-items: flex-start;
    flex-direction: row-reverse;
}

.avatar-bot {
    width: 36px; height: 36px;
    background: #4f46e5;
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    font-weight: bold;
    color: white;
    flex-shrink: 0;
}

.avatar-user {
    width: 36px; height: 36px;
    background: #0ea5e9;
    border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem;
    font-weight: bold;
    color: white;
    flex-shrink: 0;
}

.bubble-bot {
    background: rgba(79, 70, 229, 0.1);
    border: 1px solid rgba(79, 70, 229, 0.2);
    border-radius: 4px 12px 12px 12px;
    padding: 0.9rem 1.1rem;
    max-width: 78%;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.65;
}

.bubble-user {
    background: rgba(14, 165, 233, 0.1);
    border: 1px solid rgba(14, 165, 233, 0.2);
    border-radius: 12px 4px 12px 12px;
    padding: 0.9rem 1.1rem;
    max-width: 78%;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.65;
}

.msg-label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.4);
    margin-bottom: 3px;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ── Input area ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 6px !important;
    color: #e2e8f0 !important;
    padding: 0.75rem 1rem !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: #4f46e5 !important;
    box-shadow: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #4f46e5 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button:hover {
    background: #4338ca !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

.profile-field {
    display: flex;
    flex-direction: column;
    margin-bottom: 0.7rem;
}

.profile-label {
    font-size: 0.7rem;
    color: #818cf8;
    text-transform: uppercase;
    font-weight: 600;
    margin-bottom: 2px;
}

.profile-value {
    font-size: 0.85rem;
    color: #e2e8f0;
}

.badge {
    display: inline-block;
    background: rgba(79, 70, 229, 0.2);
    border: 1px solid rgba(79, 70, 229, 0.4);
    color: #c7d2fe;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.75rem;
    margin: 2px;
}

.stage-badge {
    background: #3730a3;
    color: white;
    border-radius: 4px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.8rem;
    border: 1px solid #4f46e5;
}

/* ── Progress ── */
.stProgress > div > div > div {
    background: #4f46e5 !important;
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session State Initialisation
# ─────────────────────────────────────────────────────────────────────────────

def init_session():
    """Initialise all session state variables."""
    if "bot" not in st.session_state:
        st.session_state.bot = TalentScoutBot()
    if "messages" not in st.session_state:
        # Seed with the greeting message
        st.session_state.messages = [
            {"role": "assistant", "content": st.session_state.bot.get_greeting()}
        ]
    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended = False
    if "profile_saved" not in st.session_state:
        st.session_state.profile_saved = False
    if "saved_path" not in st.session_state:
        st.session_state.saved_path = ""
    if "api_key_ok" not in st.session_state:
        st.session_state.api_key_ok = bool(os.getenv("GROQ_API_KEY"))


init_session()

# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
        <div style="font-size:1.4rem; font-weight:700; color:white; display:flex; align-items:center; gap:0.5rem;">
            <div style="background:#4f46e5; padding:0.2rem 0.5rem; border-radius:4px; font-size:1rem;">TS</div>
            TalentScout
        </div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.2rem;">Recruitment Portal</div>
    </div>
    """, unsafe_allow_html=True)
    
    app_mode = st.radio("Navigation", ["Candidate Screening", "Admin Dashboard"], index=0, label_visibility="collapsed")
    
    st.markdown("---")
    
    if app_mode == "Candidate Screening":
        bot: TalentScoutBot = st.session_state.bot
        
        # Stage progress
        current_step, total_steps = bot.get_stage_progress()
        progress_pct = current_step / total_steps if total_steps > 0 else 0

        st.markdown(f"""
        <div class="stage-badge">Stage: {bot.get_stage_label()}</div>
        """, unsafe_allow_html=True)
        st.progress(progress_pct)
        st.caption(f"Step {current_step} of {total_steps}")
        st.markdown("---")

        # Candidate profile card
        st.markdown("**Candidate Profile**")
        profile = bot.profile

        def profile_row(label: str, value: str, is_tags: bool = False):
            if not value:
                return
            if is_tags:
                tags = "".join(
                    f'<span class="badge">{t.strip()}</span>'
                    for t in value.replace(",", " ").split()
                    if t.strip()
                )
                st.markdown(f"""
                <div class="profile-field">
                    <span class="profile-label">{label}</span>
                    <div>{tags}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="profile-field">
                    <span class="profile-label">{label}</span>
                    <span class="profile-value">{value}</span>
                </div>
                """, unsafe_allow_html=True)

        with st.container():
            profile_row("Full Name", profile.full_name)
            profile_row("Email", f"{profile.email[:1]}***@{profile.email.split('@')[1]}" if "@" in profile.email else profile.email)
            profile_row("Phone", f"****{profile.phone[-4:]}" if len(profile.phone) >= 4 else profile.phone)
            profile_row("Experience", f"{profile.years_experience} yrs" if profile.years_experience else "")
            profile_row("Position(s)", profile.desired_positions)
            profile_row("Location", profile.current_location)
            profile_row("Tech Stack", profile.tech_stack, is_tags=True)

        if not any([profile.full_name, profile.email, profile.phone]):
            st.caption("_Profile fields will populate as collected._")

        st.markdown("---")

        # Save profile button
        if bot.stage.name in ["ASK_QUESTIONS", "FAREWELL"] and profile.is_complete():
            if not st.session_state.profile_saved:
                if st.button("Save Candidate Profile", use_container_width=True):
                    path = bot.save_profile()
                    st.session_state.profile_saved = True
                    st.session_state.saved_path = path
                    st.success("Profile saved successfully.")
            else:
                st.success("Profile saved.")
                st.caption(f"`{st.session_state.saved_path}`")

        # New session button
        if st.session_state.conversation_ended:
            if st.button("Start New Session", use_container_width=True):
                for key in ["bot", "messages", "conversation_ended", "profile_saved", "saved_path"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    st.markdown("""
    <div style="text-align:center; color:rgba(255,255,255,0.3); font-size:0.7rem; margin-top:2rem;">
        TalentScout Proprietary<br>Confidential System
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Main Views
# ─────────────────────────────────────────────────────────────────────────────

# --- Admin Dashboard View ---
if app_mode == "Admin Dashboard":
    st.markdown("""
    <div class="ts-header">
        <div>
            <h1>Admin Dashboard</h1>
            <p>Candidate Profile Review System</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Simple Authentication
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
        
    if not st.session_state.admin_authenticated:
        admin_password = st.text_input("Enter Admin Password", type="password")
        # In a real app, this should be an environment variable. Using a hardcoded password for demonstration.
        if st.button("Login"):
            if admin_password == os.getenv("ADMIN_PASSWORD", "admin123"):
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()
        
    if st.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    candidates = load_all_candidates()
    if not candidates:
        st.info("No candidate profiles found in the system.")
    else:
        df = pd.DataFrame(candidates)
        # Reorder and format columns for better readability
        display_df = df.copy()
        date_col = 'screening_date'
        if date_col in display_df.columns:
            display_df[date_col] = pd.to_datetime(display_df[date_col]).dt.strftime('%Y-%m-%d %H:%M')
            
        st.write(f"**Total Candidates Profiled:** {len(candidates)}")
        st.dataframe(display_df, use_container_width=True)
    
    st.stop()


# --- Candidate Screening View ---
st.markdown("""
<div class="ts-header">
    <div>
        <h1>Hiring Assistant Screening</h1>
        <p>Candidate Information Collection & Assessment</p>
    </div>
</div>
""", unsafe_allow_html=True)

if not st.session_state.api_key_ok:
    st.warning(
        "GROQ_API_KEY not found. Please verify your .env configuration. "
        "System initialization requires a valid key from console.groq.com."
    )

bot: TalentScoutBot = st.session_state.bot

# ── Chat History Rendering
chat_html_parts = []
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"].replace("\n", "<br>")

    if role == "assistant":
        chat_html_parts.append(f"""
<div class="msg-bot">
    <div class="avatar-bot">TS</div>
    <div>
        <div class="msg-label">Scout · TalentScout AI</div>
        <div class="bubble-bot">{content}</div>
    </div>
</div>
""")
    else:
        chat_html_parts.append(f"""
<div class="msg-user">
    <div class="avatar-user">CT</div>
    <div>
        <div class="msg-label" style="text-align:right;">Candidate</div>
        <div class="bubble-user">{content}</div>
    </div>
</div>
""")

all_chat_html = "\n".join(chat_html_parts)
st.markdown(
    f'<div class="chat-container" id="chat-end">{all_chat_html}</div>',
    unsafe_allow_html=True
)

st.markdown("""
<script>
    const chatBox = document.querySelector('.chat-container');
    if (chatBox) { chatBox.scrollTop = chatBox.scrollHeight; }
</script>
""", unsafe_allow_html=True)

# ── Input Area
if not st.session_state.conversation_ended:
    placeholder_texts = {
        "GREETING": "Press Enter to begin...",
        "COLLECT_NAME": "Enter your full name...",
        "COLLECT_EMAIL": "Enter your email address...",
        "COLLECT_PHONE": "Enter your phone number...",
        "COLLECT_EXPERIENCE": "e.g. 3 years...",
        "COLLECT_POSITION": "e.g. Backend Engineer...",
        "COLLECT_LOCATION": "e.g. New York, USA...",
        "COLLECT_TECH_STACK": "e.g. Python, SQL, Docker...",
        "ASK_QUESTIONS": "Enter your response...",
        "FAREWELL": "Type 'finish' to conclude...",
    }
    current_placeholder = placeholder_texts.get(bot.stage.name, "Enter your message...")

    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.chat_input(current_placeholder)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Processing response..."):
            response = bot.chat(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})

        if bot.stage.name == "FAREWELL":
            st.session_state.conversation_ended = True
            if bot.profile.is_complete() and not st.session_state.profile_saved:
                path = bot.save_profile()
                st.session_state.profile_saved = True
                st.session_state.saved_path = path

        st.rerun()
else:
    st.markdown("""
    <div style="background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.1); 
                border-radius:8px; padding:1.5rem; text-align:center; margin-top:1rem;">
        <h3 style="margin:0 0 0.5rem 0; color:#e2e8f0; font-size:1.2rem;">Screening Completed</h3>
        <p style="color:#94a3b8; margin:0; font-size:0.9rem;">
            The session has concluded. Return to the Admin Dashboard to review the profile, 
            or use the sidebar to start a new session.
        </p>
    </div>
    """, unsafe_allow_html=True)
