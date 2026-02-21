"""
data_handler.py
---------------
Privacy-safe candidate data collection and storage for TalentScout.
Handles PII masking in compliance with GDPR best practices.
"""

import json
import hashlib
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# Directory where candidate profiles are saved (simulated backend)
CANDIDATES_DIR = Path("candidates")


@dataclass
class CandidateProfile:
    """Represents a screened candidate's collected information."""
    full_name: str = ""
    email: str = ""          # stored as SHA-256 hash for privacy
    phone: str = ""          # stored masked (e.g. ****5678)
    years_experience: str = ""
    desired_positions: str = ""
    current_location: str = ""
    tech_stack: str = ""
    session_id: str = ""
    screening_date: str = ""
    status: str = "Screened - Pending Review"

    def is_complete(self) -> bool:
        """Returns True if all mandatory fields have been collected."""
        mandatory = [
            self.full_name, self.email, self.phone,
            self.years_experience, self.desired_positions,
            self.current_location, self.tech_stack
        ]
        return all(f.strip() for f in mandatory)

    def get_summary(self) -> str:
        """Returns a human-readable summary (safe for display – PII masked)."""
        return (
            f"Name: {self.full_name}\n"
            f"Email: {_mask_email(self.email)}\n"
            f"Phone: {_mask_phone(self.phone)}\n"
            f"Experience: {self.years_experience} years\n"
            f"Position(s): {self.desired_positions}\n"
            f"Location: {self.current_location}\n"
            f"Tech Stack: {self.tech_stack}"
        )


# ---------------------------------------------------------------------------
# PII Masking helpers (GDPR-aligned)
# ---------------------------------------------------------------------------

def _hash_email(email: str) -> str:
    """One-way SHA-256 hash of email address for storage."""
    return hashlib.sha256(email.strip().lower().encode()).hexdigest()


def _mask_email(email: str) -> str:
    """Display-safe email mask: j***@example.com"""
    if "@" not in email:
        return email
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}"


def _mask_phone(phone: str) -> str:
    """Display-safe phone mask: shows last 4 digits only."""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) >= 4:
        return f"****{digits[-4:]}"
    return "****"


# ---------------------------------------------------------------------------
# Storage functions
# ---------------------------------------------------------------------------

def save_candidate(profile: CandidateProfile, session_id: str) -> str:
    """
    Saves a candidate profile to a JSON file in the candidates/ directory.
    PII fields are hashed/masked before writing.
    Returns the path to the saved file.
    """
    CANDIDATES_DIR.mkdir(exist_ok=True)

    # Build privacy-safe record
    record = asdict(profile)
    record["email_hash"] = _hash_email(profile.email)
    record["email"] = _mask_email(profile.email)        # replace raw email
    record["phone"] = _mask_phone(profile.phone)        # replace raw phone
    record["session_id"] = session_id
    record["screening_date"] = datetime.now().isoformat()

    filename = CANDIDATES_DIR / f"candidate_{session_id[:8]}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)

    return str(filename)


def load_all_candidates() -> list[dict]:
    """
    Loads all saved candidate profiles from the candidates/ directory.
    Returns a list of candidate records (PII already masked in storage).
    """
    if not CANDIDATES_DIR.exists():
        return []

    profiles = []
    for json_file in CANDIDATES_DIR.glob("candidate_*.json"):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                profiles.append(json.load(f))
        except (json.JSONDecodeError, IOError):
            continue  # skip corrupt files

    return profiles
