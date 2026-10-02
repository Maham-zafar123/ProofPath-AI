
import re
import streamlit as st
import fitz  # PyMuPDF
from docx import Document
from transformers import pipeline

st.set_page_config(
    page_title="ProofPath AI",
    page_icon="🧭",
    layout="wide"
)

DEMO_EMAIL = "demo@proofpath.ai"
DEMO_PASSWORD = "demo123"

SKILLS = [
    "Python", "Java", "C++", "JavaScript", "SQL", "HTML", "CSS",
    "React", "Node.js", "Express", "FastAPI", "Flask", "Streamlit",
    "MongoDB", "MySQL", "PostgreSQL", "SQLite",
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch",
    "Keras", "NLP", "RAG", "LangChain", "LangGraph",
    "Hugging Face", "Git", "Docker", "REST API", "Pandas", "NumPy"
]


@st.cache_resource(show_spinner=False)
def load_open_source_model():
    # Small Apache-2.0 model suitable for a lightweight MVP.
    return pipeline(
        "text2text-generation",
        model="google/flan-t5-small"
    )

def ai_generate(prompt, max_new_tokens=120):
    try:
        generator = load_open_source_model()
        result = generator(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=False
        )
        return result[0]["generated_text"].strip()
    except Exception:
        return None

def login_screen():
    st.title("🧭 ProofPath AI")
    st.subheader("Prepare to defend every claim on your CV.")
    st.caption("Demo login for reviewers")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login", type="primary"):
        if email == DEMO_EMAIL and password == DEMO_PASSWORD:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid demo credentials.")

def extract_text(uploaded_file):
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        data = uploaded_file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)

    if name.endswith(".docx"):
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs)

    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")

    return ""

def find_skills(text):
    found = []
    low = text.lower()
    aliases = {
        "node.js": ["node.js", "nodejs"],
        "c++": ["c++"],
        "rest api": ["rest api", "restful api", "apis"],
        "machine learning": ["machine learning", "ml"],
        "deep learning": ["deep learning"],
        "hugging face": ["hugging face", "huggingface"],
    }

    for skill in SKILLS:
        patterns = aliases.get(skill.lower(), [skill.lower()])
        if any(p in low for p in patterns):
            found.append(skill)
    return found

def detect_sections(text):
    headings = {
        "Education": ["education", "academic"],
        "Experience": ["experience", "employment", "internship"],
        "Projects": ["projects", "project"],
        "Skills": ["skills", "technical skills", "technologies"],
        "Achievements": ["achievements", "awards", "honors"],
    }
    low = text.lower()
    return [name for name, keys in headings.items() if any(k in low for k in keys)]

def risk_flags(text, skills):
    flags = []
    low = text.lower()

    vague_words = ["expert", "master", "proficient", "advanced", "excellent"]
    used_vague = [w for w in vague_words if re.search(rf"\b{re.escape(w)}\b", low)]
    if used_vague:
        flags.append(
            "Your CV uses strong skill-level words such as "
            + ", ".join(sorted(set(used_vague)))
            + ". Be ready to prove them with examples."
        )

    number_claims = re.findall(r"\b\d{2,3}%\b", text)
    if number_claims:
        flags.append(
            "You have measurable claims such as "
            + ", ".join(number_claims[:4])
            + ". Prepare how you measured each result."
        )

    if len(skills) >= 10:
        flags.append(
            f"You list {len(skills)} recognizable technical skills. "
            "Prioritize the ones you actually used in projects or internships."
        )

    if "team lead" in low or "team leader" in low or "led " in low:
        flags.append(
            "You mention leadership. Prepare one specific example of a decision, challenge, and result."
        )

    if not flags:
        flags.append(
            "No major risk flag found. Focus on explaining your projects, decisions, and personal contribution clearly."
        )

    return flags

def build_questions(text, skills):
    questions = []
    low = text.lower()

    # Core project questions
    questions.extend([
        "Tell me about the project on your CV that you are most proud of.",
        "What was your personal contribution to that project?",
        "What was the hardest technical problem you faced, and how did you solve it?",
        "If you rebuilt that project today, what would you improve?"
    ])

    # Skill-specific questions
    for skill in skills[:6]:
        questions.append(f"You listed {skill}. Where exactly did you use it, and why did you choose it?")
        questions.append(f"What is one limitation or challenge you faced while using {skill}?")

    # Claims
    percents = re.findall(r"\b\d{2,3}%\b", text)
    if percents:
        questions.append(
            f"Your CV includes a result like {percents[0]}. How did you calculate or verify that number?"
        )

    if "intern" in low or "internship" in low:
        questions.append("What did you learn from your internship that you did not learn at university?")

    if "fastapi" in low:
        questions.append("Explain the request flow in your FastAPI project from frontend input to backend response.")

    if "mongodb" in low:
        questions.append("Why did you use MongoDB instead of a relational database in that project?")

    # Deduplicate
    seen = set()
    final = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            final.append(q)
    return final[:14]

def answer_feedback(answer):
    words = answer.strip().split()
    feedback = []

    if len(words) < 25:
        feedback.append("Your answer is too short. Add what you did, why you did it, and the result.")
    elif len(words) > 180:
        feedback.append("Your answer is long. Try to keep the main explanation focused and interview-friendly.")
    else:
        feedback.append("Your answer length is reasonable.")

    low = answer.lower()
    if not any(x in low for x in ["because", "so that", "reason", "chose"]):
        feedback.append("Add your reasoning: explain why you made that technical choice.")

    if not any(x in low for x in ["result", "improved", "reduced", "achieved", "%", "learned"]):
        feedback.append("Add an outcome or lesson so the interviewer can see the impact.")

    if not any(x in low for x in ["i ", "my ", "i'm", "i was", "i implemented", "i built"]):
        feedback.append("Make your personal contribution clear by using 'I' statements.")

    return feedback

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login_screen()
    st.stop()

with st.sidebar:
    st.header("ProofPath AI")
    st.success("Demo mode")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

st.title("🧭 ProofPath AI")
st.write(
    "Upload a CV and get a preparation map showing which skills, claims, and projects you should be ready to explain."
)

uploaded = st.file_uploader("Upload CV", type=["pdf", "docx", "txt"])

if uploaded:
    text = extract_text(uploaded)

    if not text.strip():
        st.error("I could not extract text from this file. Please try a text-based PDF, DOCX, or TXT file.")
        st.stop()

    skills = find_skills(text)
    sections = detect_sections(text)
    flags = risk_flags(text, skills)
    questions = build_questions(text, skills)

    tab1, tab2, tab3 = st.tabs(["CV Analysis", "Interview Questions", "Practice Answer"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Detected skills", len(skills))
        c2.metric("Detected sections", len(sections))
        c3.metric("Practice questions", len(questions))

        st.subheader("Skills detected")
        if skills:
            st.write(" • ".join(skills))
        else:
            st.info("No common technical skills were detected automatically.")

        st.subheader("Preparation flags")
        for item in flags:
            st.warning(item)

        st.subheader("Sections detected")
        st.write(", ".join(sections) if sections else "No standard section headings detected.")

        with st.expander("Preview extracted CV text"):
            st.text(text[:6000])

    with tab2:
        st.subheader("Questions generated from your CV")
        for i, q in enumerate(questions, start=1):
            st.markdown(f"**{i}. {q}**")

        st.divider()
        st.subheader("Open-source AI follow-up")
        st.caption("Uses google/flan-t5-small. The first run may need to download the model.")
        if st.button("Generate AI follow-up question"):
            excerpt = " ".join(text.split())[:1800]
            prompt = (
                "You are a software engineering interviewer. "
                "Based only on this CV text, write one specific technical interview question "
                "that asks the candidate to explain something they personally built or used. "
                "Do not invent experience. CV: " + excerpt
            )
            with st.spinner("Generating question..."):
                generated = ai_generate(prompt, 80)
            if generated:
                st.success(generated)
            else:
                st.info("AI model could not load, so use the personalized questions above.")

    with tab3:
        st.subheader("Practice your answer")
        selected = st.selectbox("Choose a question", questions)
        answer = st.text_area(
            "Your answer",
            height=180,
            placeholder="Write your answer as if you were speaking to an interviewer..."
        )
        if st.button("Get feedback", type="primary"):
            if not answer.strip():
                st.error("Please write an answer first.")
            else:
                st.markdown("### Quick feedback")
                for item in answer_feedback(answer):
                    st.write("• " + item)

                prompt = (
                    "Give concise interview feedback in 3 short bullet points. "
                    "Check whether the answer is clear, explains the candidate's own contribution, "
                    "and gives technical reasoning. Do not invent facts. "
                    f"Question: {selected}\nAnswer: {answer}"
                )
                with st.spinner("Getting open-source AI feedback..."):
                    generated_feedback = ai_generate(prompt, 120)

                if generated_feedback:
                    st.markdown("### AI feedback")
                    st.write(generated_feedback)
                else:
                    st.caption("Open-source model unavailable; the quick feedback above still works.")

        st.caption(
            "AI component: google/flan-t5-small (open-source) is used for adaptive follow-up questions "
            "and answer feedback; deterministic checks provide a fallback if the model is unavailable."
        )
else:
    st.info("Upload a PDF, DOCX, or TXT CV to start.")
    st.markdown("""
**Demo credentials**

- Email: `demo@proofpath.ai`
- Password: `demo123`
""")
