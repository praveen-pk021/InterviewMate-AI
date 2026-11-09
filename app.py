import json
import random

import streamlit as st

from gnani_api import transcribe_audio
from evaluator import evaluate_answer
from timbre_api import generate_voice
from db import get_attempts, get_statistics, init_db, save_attempt


init_db()


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Interview Practice",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# DESIGN SYSTEM
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Inter:wght@400;500;600&display=swap');

:root {
    --paper:    #F6F3EC;
    --surface:  #FFFDF9;
    --ink:      #1E1D1A;
    --muted:    #6E6A60;
    --rule:     #DDD7CA;
    --accent:   #1F4A3A;
    --accent-soft: #E3ECE7;
    --warn:     #8A5A12;
    --bad:      #8C2F25;
}

/* Base */
html, body, .stApp {
    background: var(--paper) !important;
    color: var(--ink);
    font-family: 'Inter', system-ui, sans-serif;
}

#MainMenu, footer, [data-testid="stHeader"] { visibility: hidden; height: 0; }

.block-container {
    max-width: 1180px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}

h1, h2, h3 {
    font-family: 'Newsreader', Georgia, serif !important;
    color: var(--ink) !important;
    font-weight: 500 !important;
    letter-spacing: -0.01em;
}

p, label, .stMarkdown, .stCaption, small {
    color: var(--muted);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--rule);
}
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-size: 1.15rem !important;
}

/* Inputs */
[data-baseweb="select"] > div,
.stTextArea textarea {
    background: var(--surface) !important;
    border: 1px solid var(--rule) !important;
    border-radius: 6px !important;
    color: var(--ink) !important;
    box-shadow: none !important;
}
.stTextArea textarea:focus,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}

/* Buttons */
.stButton > button {
    background: var(--ink);
    color: var(--surface);
    border: 1px solid var(--ink);
    border-radius: 6px;
    padding: 0.6rem 1.1rem;
    font-weight: 500;
    font-size: 0.92rem;
    transition: background 0.15s ease;
}
.stButton > button:hover {
    background: var(--accent);
    border-color: var(--accent);
    color: var(--surface);
}
.stButton > button:focus:not(:active) {
    color: var(--surface);
    border-color: var(--accent);
}

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border: 1px solid var(--rule) !important;
    border-radius: 10px;
    box-shadow: 0 1px 0 rgba(30, 29, 26, 0.03);
}

/* Audio input */
[data-testid="stAudioInput"] {
    background: var(--paper);
    border-radius: 8px;
}

/* Progress */
.stProgress > div > div > div > div {
    background: var(--accent);
}

/* Alerts: keep them quiet */
[data-testid="stAlert"] {
    border-radius: 8px;
    border: 1px solid var(--rule);
    background: var(--paper);
}

hr {
    border: none;
    border-top: 1px solid var(--rule);
    margin: 2.5rem 0;
}

/* Masthead */
.masthead {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--ink);
    margin-bottom: 2.25rem;
}
.masthead-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2.4rem;
    font-weight: 500;
    color: var(--ink);
    line-height: 1.05;
}
.masthead-meta {
    font-size: 0.78rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    text-align: right;
}

/* Section kicker */
.kicker {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.25rem;
}

.section-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.7rem;
    color: var(--ink);
    margin: 0 0 1.25rem 0;
}

/* Question block */
.question-text {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.55rem;
    line-height: 1.35;
    color: var(--ink);
    padding: 1rem 0 0.5rem 0;
}

.tag-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 0.75rem;
}
.tag {
    font-size: 0.75rem;
    padding: 0.2rem 0.6rem;
    border: 1px solid var(--rule);
    border-radius: 4px;
    color: var(--muted);
    background: var(--paper);
}

.placeholder-text {
    color: var(--muted);
    font-size: 0.95rem;
    line-height: 1.6;
    padding: 0.5rem 0;
}

/* Score */
.score-block {
    display: flex;
    align-items: baseline;
    gap: 0.4rem;
    margin: 0.5rem 0 1rem 0;
}
.score-number {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 4rem;
    line-height: 1;
    color: var(--accent);
}
.score-total {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.4rem;
    color: var(--muted);
}

.verdict {
    display: inline-block;
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.3rem 0.7rem;
    border-radius: 4px;
    margin-top: 0.5rem;
}
.verdict-good    { background: var(--accent-soft); color: var(--accent); }
.verdict-average { background: #F3EAD7; color: var(--warn); }
.verdict-low     { background: #F5E4E1; color: var(--bad); }

.ideal-answer {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.12rem;
    line-height: 1.7;
    color: var(--ink);
}

.footer-note {
    text-align: center;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    color: var(--muted);
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# INTERVIEW QUESTIONS
# --------------------------------------------------

questions = {
    "Python": {
        "Easy": [
            "What is Python?",
            "What is the difference between a list and a tuple?",
            "What are Python variables?",
        ],
        "Medium": [
            "Explain list comprehension.",
            "What are Python decorators?",
            "Explain shallow copy and deep copy.",
        ],
        "Hard": [
            "Explain Python memory management.",
            "What are generators?",
            "Explain multithreading and multiprocessing.",
        ],
    },
    "SQL": {
        "Easy": [
            "What is a primary key?",
            "What is SQL?",
            "What is a foreign key?",
        ],
        "Medium": [
            "Explain INNER JOIN and LEFT JOIN.",
            "What is the difference between WHERE and HAVING?",
            "What is a subquery?",
        ],
        "Hard": [
            "Explain SQL window functions.",
            "How do you optimize a slow SQL query?",
            "Explain database indexing.",
        ],
    },
    "DSA": {
        "Easy": [
            "What is an array?",
            "What is linear search?",
            "What is time complexity?",
        ],
        "Medium": [
            "Explain binary search.",
            "Explain stack and queue.",
            "Explain bubble sort.",
        ],
        "Hard": [
            "Explain dynamic programming.",
            "How does a hash table work?",
            "Explain graph traversal.",
        ],
    },
    "HR": {
        "Easy": [
            "Tell me about yourself.",
            "What are your strengths?",
            "Why should we hire you?",
        ],
        "Medium": [
            "Describe a challenge you overcame.",
            "How do you handle teamwork?",
            "Where do you see yourself in five years?",
        ],
        "Hard": [
            "Describe a time you handled failure.",
            "How do you handle workplace disagreements?",
            "Why should we choose you over other candidates?",
        ],
    },
}


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "question": "",
    "answer_text": "",
    "evaluation": None,
    "voice_audio": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.markdown("### Session setup")
st.sidebar.caption("Choose what you want to practice.")

st.sidebar.divider()

category = st.sidebar.selectbox("Category", ["Python", "SQL", "DSA", "HR"])
difficulty = st.sidebar.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
language = st.sidebar.selectbox(
    "Speaking language",
    ["English (India)", "Hindi", "Telugu", "Kannada"],
)

language_codes = {
    "English (India)": "en-IN",
    "Hindi": "hi-IN",
    "Telugu": "te-IN",
    "Kannada": "kn-IN",
}

st.sidebar.divider()
st.sidebar.caption("Interview Practice · v1.0")


# --------------------------------------------------
# MASTHEAD
# --------------------------------------------------

st.markdown(f"""
<div class="masthead">
    <div class="masthead-title">Interview Practice</div>
    <div class="masthead-meta">{category} &nbsp;/&nbsp; {difficulty} &nbsp;/&nbsp; {language}</div>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# QUESTION
# --------------------------------------------------

st.markdown('<div class="kicker">Step 1</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Draw a question</div>', unsafe_allow_html=True)

with st.container(border=True):

    if st.button("Draw a new question", use_container_width=False):
        st.session_state.question = random.choice(
            questions[category][difficulty]
        )
        st.session_state.answer_text = ""
        st.session_state.evaluation = None
        st.session_state.voice_audio = None

    if st.session_state.question:
        st.markdown(f"""
        <div class="tag-row">
            <span class="tag">{category}</span>
            <span class="tag">{difficulty}</span>
        </div>
        <div class="question-text">{st.session_state.question}</div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="placeholder-text">No question yet. '
            'Pick a category and difficulty in the sidebar, '
            'then draw a question.</div>',
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# ANSWER
# --------------------------------------------------

if st.session_state.question:

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="kicker">Step 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your answer</div>', unsafe_allow_html=True)

    voice_col, answer_col = st.columns([1, 1.5], gap="large")

    # Voice input
    with voice_col:
        with st.container(border=True):
            st.markdown("**Spoken answer**")
            st.caption("Record your answer and convert it to text.")

            audio = st.audio_input("Record")

            if audio is not None:
                st.audio(audio)

                if st.button("Convert to text", use_container_width=True):
                    try:
                        with st.spinner("Transcribing..."):
                            transcript = transcribe_audio(
                                audio,
                                language_codes[language],
                            )

                        if not transcript or not transcript.strip():
                            raise ValueError("No speech was recognized.")

                        st.session_state.answer_text = transcript
                        st.session_state.evaluation = None
                        st.session_state.voice_audio = None
                        st.success("Transcription complete.")

                    except Exception as error:
                        st.error(f"Transcription failed: {error}")

    # Written answer
    with answer_col:
        with st.container(border=True):
            st.markdown("**Written answer**")
            st.caption("Type your answer or edit the transcript.")

            answer = st.text_area(
                "Your response",
                key="answer_text",
                height=220,
                placeholder="Write your answer here.",
                label_visibility="collapsed",
            )

            st.caption(f"{len(answer)} characters")

    st.markdown("")

    if st.button("Submit for evaluation"):

        if not answer.strip():
            st.warning("Please write or record an answer first.")

        else:
            try:
                with st.spinner("Evaluating your answer..."):
                    result = evaluate_answer(
                        question=st.session_state.question,
                        answer=answer,
                        category=category,
                        difficulty=difficulty,
                    )

                st.session_state.evaluation = result
                st.session_state.voice_audio = None

                try:
                    save_attempt(
                        category,
                        difficulty,
                        st.session_state.question,
                        answer,
                        result,
                    )
                except Exception as history_error:
                    st.warning(
                        f"Evaluation succeeded, but this attempt could not be saved: {history_error}"
                    )

            except Exception as error:
                st.error(f"Evaluation failed: {error}")
                st.info("Your answer has been kept. You can submit it again.")


# --------------------------------------------------
# REPORT
# --------------------------------------------------

result = st.session_state.evaluation

if result is not None:

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="kicker">Step 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Evaluation</div>', unsafe_allow_html=True)

    score_col, summary_col = st.columns([1, 2], gap="large")

    verdict = result["verdict"]
    if verdict == "Excellent" or verdict == "Good":
        verdict_class = "verdict-good"
    elif verdict == "Average":
        verdict_class = "verdict-average"
    else:
        verdict_class = "verdict-low"

    with score_col:
        with st.container(border=True):
            st.markdown("**Score**")
            st.markdown(f"""
            <div class="score-block">
                <span class="score-number">{result["score"]:.1f}</span>
                <span class="score-total">/ 10</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(max(0.0, min(1.0, result["score"] / 10)))
            st.markdown(
                f'<span class="verdict {verdict_class}">{verdict}</span>',
                unsafe_allow_html=True,
            )

    with summary_col:
        with st.container(border=True):
            st.markdown("**Summary**")
            st.write(result["summary"])

    strengths_col, improve_col = st.columns(2, gap="large")

    with strengths_col:
        with st.container(border=True):
            st.markdown("**Strengths**")
            for item in result["strengths"]:
                st.markdown(f"- {item}")

    with improve_col:
        with st.container(border=True):
            st.markdown("**Areas to improve**")
            for item in result["improvements"]:
                st.markdown(f"- {item}")

    with st.container(border=True):
        st.markdown("**Model answer**")
        st.markdown(
            f'<div class="ideal-answer">{result["ideal_answer"]}</div>',
            unsafe_allow_html=True,
        )

    # Audio feedback
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="kicker">Audio</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Listen to feedback</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.caption("Generate a spoken version of the evaluation.")

        feedback_text = f"""
        Your score is {result['score']} out of 10.

        {result['summary']}

        Strengths: {', '.join(result['strengths'])}.

        Areas to improve: {', '.join(result['improvements'])}.

        Model answer: {result['ideal_answer']}
        """

        if st.button("Generate audio", use_container_width=True):
            try:
                with st.spinner("Generating audio..."):
                    audio_bytes = generate_voice(
                        feedback_text,
                        language="en-IN",
                        voice="Yashvi",
                    )
                st.session_state.voice_audio = audio_bytes

            except Exception as error:
                st.error(f"Audio generation failed: {error}")

        if st.session_state.voice_audio is not None:
            st.audio(st.session_state.voice_audio, format="audio/wav")


# --------------------------------------------------
# INTERVIEW HISTORY
# --------------------------------------------------

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="kicker">Progress</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Interview history</div>', unsafe_allow_html=True)

try:
    attempts = get_attempts()
    stats = get_statistics()

    if attempts:
        metric_cols = st.columns(4)
        metric_cols[0].metric("Total attempts", stats["total"])
        metric_cols[1].metric("Average score", f'{stats["average"]:.1f} / 10')
        metric_cols[2].metric("Latest score", f'{stats["latest"]:.1f} / 10')
        metric_cols[3].metric("Change from previous", f'{stats["improvement"]:+.1f}')
        st.caption("Scores across saved attempts")
        st.line_chart(
            {"Score": [float(attempt["score"]) for attempt in attempts]},
            y_label="Score out of 10",
        )

        for attempt in reversed(attempts):
            heading = (
                f'{attempt["created_at"]} · {attempt["category"]} · '
                f'{attempt["difficulty"]} · {float(attempt["score"]):.1f}/10'
            )
            with st.expander(heading):
                st.markdown("**Question**")
                st.write(attempt["question"])
                st.markdown("**Your answer**")
                st.write(attempt["answer"])
                st.markdown("**Summary**")
                st.write(attempt.get("summary") or "No summary saved.")
                for label, field in (("Strengths", "strengths"), ("Areas to improve", "improvements")):
                    st.markdown(f"**{label}**")
                    try:
                        items = json.loads(attempt.get(field) or "[]")
                    except (TypeError, json.JSONDecodeError):
                        items = []
                    if items:
                        for item in items:
                            st.markdown(f"- {item}")
                    else:
                        st.caption("None recorded")
                st.markdown("**Model answer**")
                st.write(attempt.get("ideal_answer") or "No model answer saved.")
    else:
        st.info("Your evaluated attempts will appear here.")
except Exception as history_error:
    st.warning(f"Could not load interview history: {history_error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    '<div class="footer-note">INTERVIEW PRACTICE</div>',
    unsafe_allow_html=True,
)
