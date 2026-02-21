# TalentScout AI Hiring Assistant

TalentScout is a professional, AI-powered recruitment screening and interview training platform built with Python, Streamlit, and LangChain utilizing the Groq inference engine. The application acts as a virtual recruiter named "Scout", gathering essential candidate information and then gracefully transitioning into a role-specific technical interview trainer.

## 🎯 Features

- **Sequential Information Gathering:** Systematically collects candidate details (Name, Email, Phone, Experience, Location, Desired Position, and Tech Stack).
- **Dynamic Interview Training:** Generates role-specific, tailored technical and behavioral questions based on the candidate's exact tech stack and desired position.
- **Interactive Feedback:** Evaluates candidate answers in real-time, providing constructive feedback and interview coaching.
- **Privacy-First Data Handling:** Masks sensitive PII (hashing emails, obfuscating phone numbers) before saving profiles locally.
- **Admin Dashboard:** A secure, password-protected portal for recruiters to review captured candidate profiles.
- **Premium UI:** A custom-styled, dark-themed Streamlit interface that feels professional, corporate, and polished.

## 🛠️ Technology Stack

- **Frontend:** Streamlit 1.32+
- **LLM Orchestration:** LangChain 1.x (LCEL - LangChain Expression Language)
- **Inference Engine:** Groq API (`llama-3.3-70b-versatile` model)
- **Data Storage:** Local JSON persistence (simulated backend)
- **Language:** Python 3.10+

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python installed on your Windows/macOS/Linux machine.

### 2. Clone and Install Dependencies
```bash
# Clone the repository (if applicable)
# Navigate to the project directory
cd path/to/project

# Create a virtual environment (optional but recommended)
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Environment Configuration
You need a free Groq API key to run the language model.
1. Get your free API key at [console.groq.com](https://console.groq.com/keys).
2. Copy the `.env.example` file to create a new file named `.env`.
3. Add your Groq API key to the `.env` file:
```ini
GROQ_API_KEY=your_groq_api_key_here
ADMIN_PASSWORD=your_custom_admin_password
```

### 4. Running the Application
Launch the Streamlit server:
```bash
streamlit run app.py
```
The application will open in your default web browser at `http://localhost:8501`.

---

## 🔐 Admin Dashboard Management

The application features a secure Admin Dashboard where recruiters can view processed candidate profiles.
By default, the password is: `admin123`

**How to change the Admin Password:**
We've included a dedicated CLI script to safely manage the dashboard password. Run the following command in your terminal and follow the prompts:
```bash
python change_admin_password.py
```

## 📁 Project Structure

```text
├── app.py                     # Main Streamlit UI and routing (Candidate vs Admin view)
├── chatbot.py                 # LangChain LCEL conversation engine & state management
├── prompts.py                 # System and interaction prompt templates
├── data_handler.py            # Privacy-safe JSON storage and PII masking
├── change_admin_password.py   # Utility script to update the Admin Dashboard password
├── requirements.txt           # Python package dependencies
├── .env.example               # Example environment variables
└── candidates/                # Auto-generated directory containing saved JSON profiles
```

## 🤝 Usage Guide & Flow

1. **Greeting:** The candidate is welcomed and informed about data privacy.
2. **Data Collection:** Scout sequentially asks for basic contact and professional details.
3. **Tech Stack & Role:** The candidate declares their technologies and target role (e.g., "Senior Backend Engineer").
4. **Interview Training:** Scout switches gears and generates 2-3 technical questions per technology, plus 2 scenario-based questions tailored to the candidate's target role.
5. **Feedback Loop:** As the candidate answers the questions, Scout provides detailed feedback, pointing out strengths and areas for improvement.
6. **Completion:** The candidate types "finish" to end the session. The secure, hashed profile is saved, and recruiters can view it immediately on the Admin Dashboard.
