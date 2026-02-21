"""
chatbot.py
----------
LangChain 1.x LCEL-powered conversation engine for TalentScout Hiring Assistant.
Uses Groq inference via ChatGroq with lazy LLM initialisation (so UI renders even without key).
"""

import os
import uuid
import re
from enum import Enum, auto
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory

from prompts import (
    MAIN_CHAT_PROMPT,
    TECH_QUESTIONS_PROMPT,
    FAREWELL_TEMPLATE,
    FALLBACK_MESSAGE,
    GREETING_MESSAGE,
)
from data_handler import CandidateProfile, save_candidate

load_dotenv()

EXIT_KEYWORDS = {"bye", "goodbye", "exit", "quit", "stop", "end", "done", "finish", "terminate"}

OFF_TOPIC_PATTERNS = [
    r"\bweather\b", r"\bjoke\b", r"\brecipe\b", r"\bsports?\b",
    r"\blatest news\b", r"\bstock price\b", r"\bcrypto\b",
    r"\bwhat is (?!your|the (next|screening|purpose|tech|stack))",
    r"\bwho is (?!your)",
    r"\btell me (a|about|something)",
]


class Stage(Enum):
    GREETING = auto()
    COLLECT_NAME = auto()
    COLLECT_EMAIL = auto()
    COLLECT_PHONE = auto()
    COLLECT_EXPERIENCE = auto()
    COLLECT_POSITION = auto()
    COLLECT_LOCATION = auto()
    COLLECT_TECH_STACK = auto()
    ASK_QUESTIONS = auto()
    FAREWELL = auto()


STAGE_LABELS = {
    Stage.GREETING: "Welcome",
    Stage.COLLECT_NAME: "Full Name",
    Stage.COLLECT_EMAIL: "Email Address",
    Stage.COLLECT_PHONE: "Phone Number",
    Stage.COLLECT_EXPERIENCE: "Years of Experience",
    Stage.COLLECT_POSITION: "Desired Position(s)",
    Stage.COLLECT_LOCATION: "Current Location",
    Stage.COLLECT_TECH_STACK: "Tech Stack",
    Stage.ASK_QUESTIONS: "Technical Questions",
    Stage.FAREWELL: "Complete",
}


class TalentScoutBot:
    """
    Manages the TalentScout screening conversation with lazy LLM initialisation.
    The LLM is only created when the first actual chat() call is made,
    so the Streamlit UI can render correctly even without an API key present.
    """

    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.stage = Stage.GREETING
        self.profile = CandidateProfile(session_id=self.session_id)
        self.tech_questions: str = ""
        self.questions_delivered = False

        # Lazy-initialised fields
        self._llm = None
        self._chain = None
        self._history_store: dict[str, InMemoryChatMessageHistory] = {}

    # ── LLM lazy init ─────────────────────────────────────────────────────────

    def _ensure_llm(self):
        """Initialises the LLM and chain on first use."""
        if self._llm is not None:
            return  # already initialised

        from langchain_groq import ChatGroq  # import here to avoid top-level validation

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Please add it to your .env file.\n"
                "Get your free key at: https://console.groq.com/keys"
            )

        self._llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=api_key,
            temperature=0.7,
        )

        base_chain = MAIN_CHAT_PROMPT | self._llm
        self._chain = RunnableWithMessageHistory(
            base_chain,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self._history_store:
            self._history_store[session_id] = InMemoryChatMessageHistory()
        return self._history_store[session_id]

    # ── Public API ────────────────────────────────────────────────────────────

    def get_greeting(self) -> str:
        return GREETING_MESSAGE

    def chat(self, user_input: str) -> str:
        user_input = user_input.strip()

        # Exit detection (no LLM needed)
        if self._detect_exit(user_input):
            self.stage = Stage.FAREWELL
            return self._farewell_static()

        # Off-topic fallback (no LLM needed)
        if self._is_off_topic(user_input):
            return FALLBACK_MESSAGE + self._reprompt_current_stage()

        # Capture field from user answer
        self._capture_field(user_input)

        # Advance stage
        self._advance_stage()

        # Initialise LLM (raises ValueError if key missing)
        try:
            self._ensure_llm()
        except ValueError as e:
            return f"⚠️ **Configuration Error:** {e}"

        # Generate tech questions (dedicated chain)
        if self.stage == Stage.ASK_QUESTIONS and not self.questions_delivered:
            self.tech_questions = self._generate_tech_questions()
            self.questions_delivered = True
            
            # Add context to history so the main LLM can evaluate the answers
            history = self._get_session_history(self.session_id)
            history.add_user_message(user_input)
            history.add_ai_message(self.tech_questions)
            
            return self.tech_questions

        # Farewell
        if self.stage == Stage.FAREWELL:
            return self._generate_farewell()

        # Normal LLM response
        try:
            response = self._chain.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": self.session_id}},
            )
            return response.content
        except Exception as e:
            return (
                f"I'm experiencing a brief technical issue. Let's continue!\n\n"
                + self._reprompt_current_stage()
            )

    def save_profile(self) -> str:
        return save_candidate(self.profile, self.session_id)

    def get_stage_progress(self) -> tuple[int, int]:
        stages = list(Stage)
        current = stages.index(self.stage)
        return current, len(stages) - 1

    def get_stage_label(self) -> str:
        return STAGE_LABELS.get(self.stage, "")

    # ── Private helpers ───────────────────────────────────────────────────────

    def _detect_exit(self, text: str) -> bool:
        words = set(re.sub(r"[^\w\s]", "", text.lower()).split())
        return bool(words & EXIT_KEYWORDS)

    def _is_off_topic(self, text: str) -> bool:
        text_lower = text.lower()
        for pattern in OFF_TOPIC_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

    def _capture_field(self, user_input: str):
        stage_to_field = {
            Stage.COLLECT_NAME: "full_name",
            Stage.COLLECT_EMAIL: "email",
            Stage.COLLECT_PHONE: "phone",
            Stage.COLLECT_EXPERIENCE: "years_experience",
            Stage.COLLECT_POSITION: "desired_positions",
            Stage.COLLECT_LOCATION: "current_location",
            Stage.COLLECT_TECH_STACK: "tech_stack",
        }
        field = stage_to_field.get(self.stage)
        if field:
            setattr(self.profile, field, user_input)

    def _advance_stage(self):
        # Do not automatically advance past ASK_QUESTIONS so the candidate can interact
        if self.stage == Stage.ASK_QUESTIONS:
            return
            
        stage_order = list(Stage)
        idx = stage_order.index(self.stage)
        if idx < len(stage_order) - 1:
            self.stage = stage_order[idx + 1]

    def _reprompt_current_stage(self) -> str:
        reprompts = {
            Stage.GREETING: "Could you please start by telling me your **full name**?",
            Stage.COLLECT_NAME: "Could you please share your **full name**?",
            Stage.COLLECT_EMAIL: "Could you please provide your **email address**?",
            Stage.COLLECT_PHONE: "Could you please share your **phone number**?",
            Stage.COLLECT_EXPERIENCE: "How many **years of professional experience** do you have?",
            Stage.COLLECT_POSITION: "What **position(s)** are you looking for? (e.g. Backend Engineer, Data Scientist)",
            Stage.COLLECT_LOCATION: "What is your **current location** (city, country)?",
            Stage.COLLECT_TECH_STACK: "Please list your **tech stack** — programming languages, frameworks, databases, and tools you're proficient in.",
            Stage.ASK_QUESTIONS: "Let's continue with the technical questions.",
            Stage.FAREWELL: "Thank you for your time!",
        }
        return reprompts.get(self.stage, "Let's continue with your screening.")

    def _generate_tech_questions(self) -> str:
        try:
            chain = TECH_QUESTIONS_PROMPT | self._llm
            result = chain.invoke({
                "name": self.profile.full_name or "Candidate",
                "experience": self.profile.years_experience or "unknown",
                "position": self.profile.desired_positions or "Software Engineer",
                "tech_stack": self.profile.tech_stack,
            })
            intro = (
                f"Thank you, **{self.profile.full_name or 'Candidate'}**. Based on your tech stack, "
                f"here are your technical screening questions.\n"
                f"Please answer each one to the best of your ability. Take your time.\n\n"
            )
            outro = (
                "\n\n---\n**That concludes the technical questions.** "
                "Feel free to elaborate on any answer, or type **`finish`** when you are ready to conclude."
            )
            return intro + result.content + outro
        except Exception as e:
            return (
                "I encountered an issue generating technical questions. "
                f"Could you please confirm your tech stack once more?\n\nError: {e}"
            )

    def _generate_farewell(self) -> str:
        candidate_summary = self.profile.get_summary()
        farewell_input = FAREWELL_TEMPLATE.format(candidate_summary=candidate_summary)
        try:
            response = self._chain.invoke(
                {"input": farewell_input},
                config={"configurable": {"session_id": self.session_id}},
            )
            return response.content
        except Exception:
            return self._farewell_static()

    def _farewell_static(self) -> str:
        name = self.profile.full_name or "Candidate"
        return (
            f"Thank you for your time, **{name}**.\n\n"
            "Your profile has been successfully submitted to the TalentScout team. "
            "A recruiter will review your application and reach out within 3-5 business days.\n\n"
            "We wish you the best in your career pursuits.\n\n"
            "*— Scout, TalentScout AI Assistant*"
        )
