
import json
import os
import random
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    Groq = None

APP_DIR = Path(__file__).resolve().parent
HISTORY_FILE = APP_DIR / "score_history.json"

load_dotenv(APP_DIR / ".env")

st.set_page_config(
    page_title="Linux Practice Lab",
    page_icon="🐧",
    layout="wide",
)

MODEL = "openai/gpt-oss-120b"

TOPICS = [
    "Basic Linux Commands",
    "Users and Groups",
    "Package Management",
    "Permissions and Ownership",
    "Processes and Services",
    "Environment and Bash",
    "Archives and Compression",
    "SSH and Networking",
    "File Search and Text Processing",
    "Cron and System Monitoring",
    "Logs and Troubleshooting",
]

# Each question has a fixed answer key for reliable grading.
QUESTION_BANK = {
    "Basic Linux Commands": [
        ("Which command displays the current directory?",
         ["pwd", "ls", "cd", "mkdir"], 0,
         "pwd prints your current working directory."),
        ("Which command lists hidden files?",
         ["ls -a", "pwd", "whoami", "date"], 0,
         "The -a option includes hidden entries."),
        ("Which command creates a directory?",
         ["touch", "rm", "mkdir", "cat"], 2,
         "mkdir creates a directory."),
        ("Which command copies a file?",
         ["mv", "cp", "pwd", "cd"], 1,
         "cp copies files."),
        ("Which command displays the current username?",
         ["whoami", "hostname", "date", "clear"], 0,
         "whoami displays your effective username."),
    ],
    "Users and Groups": [
        ("Which command displays a user's group memberships?",
         ["groups", "touch", "pwd", "tar"], 0,
         "groups shows group memberships."),
        ("Which command creates a Linux user?",
         ["useradd", "mkdir", "chmod", "grep"], 0,
         "useradd creates a user account."),
        ("Which command changes a user's supplementary groups?",
         ["usermod", "chmod", "chown", "passwd"], 0,
         "usermod can modify account properties."),
        ("Which file stores local user account information?",
         ["/etc/passwd", "/etc/group", "/etc/hosts", "/etc/fstab"], 0,
         "/etc/passwd contains local account records, not password hashes."),
    ],
    "Package Management": [
        ("Which command refreshes APT package lists?",
         ["sudo apt update", "sudo apt remove", "sudo apt clean", "pwd"], 0,
         "apt update refreshes repository metadata."),
        ("Which command installs a package?",
         ["sudo apt install package", "sudo apt search package",
          "mkdir package", "ls package"], 0,
         "Replace package with the actual package name."),
        ("Which command removes an installed package?",
         ["sudo apt remove package", "sudo apt update",
          "sudo apt list", "pwd"], 0,
         "apt remove uninstalls a package."),
    ],
    "Permissions and Ownership": [
        ("Which command changes permissions?",
         ["chmod", "chown", "grep", "ps"], 0,
         "chmod changes file permissions."),
        ("Which command changes ownership?",
         ["chmod", "chown", "tar", "pwd"], 1,
         "chown changes file ownership."),
        ("What does r mean in permissions?",
         ["Read", "Run", "Rename", "Remove"], 0,
         "r means read permission."),
        ("What does chmod 755 give the owner?",
         ["Read, write, execute", "Read only", "Write only", "No access"], 0,
         "755 means owner rwx and group/others r-x."),
    ],
    "Processes and Services": [
        ("Which command lists processes?",
         ["ps", "mkdir", "touch", "cd"], 0,
         "ps displays process information."),
        ("Which command gives an interactive process view?",
         ["top", "pwd", "cp", "cat"], 0,
         "top displays live process and resource information."),
        ("Which command checks a systemd service?",
         ["systemctl status SERVICE", "chmod status SERVICE",
          "apt status SERVICE", "pwd status"], 0,
         "Replace SERVICE with the service name."),
        ("Which command sends a signal to a process?",
         ["kill", "mv", "tar", "groups"], 0,
         "kill sends a signal to a process."),
    ],
    "Environment and Bash": [
        ("Which command displays PATH?",
         ["echo $PATH", "pwd PATH", "ls PATH", "date PATH"], 0,
         "The shell expands $PATH to show its value."),
        ("How do you export a variable?",
         ["export NAME=value", "mkdir NAME", "chmod NAME", "cd NAME"], 0,
         "export makes a variable available to child processes."),
        ("Which file commonly stores interactive Bash settings?",
         [".bashrc", ".jpg", "hosts.txt", "package.json"], 0,
         ".bashrc commonly configures interactive Bash shells."),
    ],
    "Archives and Compression": [
        ("Which command creates a gzip tar archive?",
         ["tar -czf archive.tar.gz folder", "grep archive folder",
          "chmod archive folder", "pwd"], 0,
         "c creates, z compresses with gzip, and f specifies the archive."),
        ("Which command extracts a gzip tar archive?",
         ["tar -xzf archive.tar.gz", "tar -czf archive.tar.gz",
          "ls -x archive.tar.gz", "chmod archive.tar.gz"], 0,
         "x extracts the archive."),
        ("Which command compresses a file with gzip?",
         ["gzip file", "grep file", "groups file", "pwd"], 0,
         "gzip compresses a file."),
    ],
    "SSH and Networking": [
        ("Which command connects to a remote host?",
         ["ssh user@host", "cp user@host", "mkdir user@host", "chmod user@host"], 0,
         "Replace user and host with the appropriate values."),
        ("Which command tests connectivity using ICMP?",
         ["ping host", "pwd host", "chmod host", "touch host"], 0,
         "ping sends echo requests when permitted."),
        ("Which command shows network interface addresses?",
         ["ip addr", "apt addr", "chmod addr", "date addr"], 0,
         "ip addr shows interfaces and their addresses."),
    ],
    "File Search and Text Processing": [
        ("Which command searches text using a pattern?",
         ["grep", "mkdir", "whoami", "date"], 0,
         "grep finds lines matching a pattern."),
        ("Which command searches directory trees?",
         ["find", "chmod", "pwd", "groups"], 0,
         "find searches for files and directories."),
        ("What does a pipe do?",
         ["Passes output to another command", "Deletes a directory",
          "Changes username", "Reboots Linux"], 0,
         "A pipe sends one command's output to another command."),
        ("What does >> normally do?",
         ["Appends output to a file", "Deletes a file",
          "Lists directories", "Changes permissions"], 0,
         ">> appends output; > normally overwrites a file."),
    ],
    "Cron and System Monitoring": [
        ("Which command edits a user's cron jobs?",
         ["crontab -e", "cron edit", "chmod cron", "apt cron"], 0,
         "crontab -e edits the current user's scheduled jobs."),
        ("Which command reports filesystem disk space?",
         ["df -h", "du -h", "pwd", "groups"], 0,
         "df -h reports filesystem space in readable units."),
        ("Which command estimates directory usage?",
         ["du -sh folder", "df -h", "whoami", "ip addr"], 0,
         "du estimates storage usage."),
        ("Which command displays memory usage?",
         ["free -h", "mkdir", "touch", "grep"], 0,
         "free -h displays memory and swap information."),
    ],
    "Logs and Troubleshooting": [
        ("Which command queries the systemd journal?",
         ["journalctl", "chmod", "mkdir", "whoami"], 0,
         "journalctl queries systemd logs."),
        ("Which command displays the end of a file?",
         ["tail", "head", "pwd", "cd"], 0,
         "tail displays the last lines of a file."),
        ("What should you do first when a command fails?",
         ["Read the error and check the command",
          "Delete system files", "Always use sudo",
          "Immediately reinstall Linux"], 0,
         "Check syntax, paths, permissions, and error messages first."),
    ],
}


PRACTICE_TASKS = {
    "Display your current directory": (
        ["pwd"],
        "pwd prints your current working directory.",
    ),
    "List hidden files": (
        ["ls -a", "ls -la", "ls -al"],
        "The -a option includes hidden entries.",
    ),
    "Create a directory named practice": (
        ["mkdir practice"],
        "mkdir creates the directory.",
    ),
    "Display disk space in readable units": (
        ["df -h"],
        "df -h reports filesystem space.",
    ),
    "Display memory usage": (
        ["free -h"],
        "free -h displays memory and swap usage.",
    ),
    "Show running processes": (
        ["ps", "ps aux", "ps -ef", "top", "htop"],
        "ps lists processes; top and htop provide interactive views.",
    ),
    "Display network addresses": (
        ["ip addr", "ip address", "ip a"],
        "ip addr displays network interfaces and addresses.",
    ),
    "Show the last 10 lines of app.log": (
        ["tail app.log", "tail -n 10 app.log", "tail -10 app.log"],
        "tail displays the end of a file.",
    ),
}


def get_client():
    key = os.getenv("GROQ_API_KEY")
    if not key or Groq is None:
        return None
    return Groq(api_key=key)


def ask_llm(system_prompt, user_prompt):
    client = get_client()
    if client is None:
        raise RuntimeError(
            "Groq is not configured. Install groq and python-dotenv, "
            "then add GROQ_API_KEY to your .env file."
        )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def load_history():
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_result(category, topic, score, total):
    history = load_history()
    history.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "category": category,
        "topic": topic,
        "score": score,
        "total": total,
        "percentage": round(score / total * 100) if total else 0,
    })
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2),
        encoding="utf-8",
    )


def normalize(text):
    return " ".join(text.strip().lower().split())


def generate_paper(topic, count, difficulty):
    # The question bank remains available if the API is unavailable.
    bank = QUESTION_BANK[topic]
    fallback = random.sample(bank, min(count, len(bank)))
    fallback_questions = [
        {
            "question": q,
            "options": options,
            "answer": answer,
            "explanation": explanation,
        }
        for q, options, answer, explanation in fallback
    ]

    try:
        raw = ask_llm(
            "You are a Linux instructor creating accurate exam questions. "
            "Return ONLY valid JSON. Questions must have one unambiguous "
            "correct answer. Do not include markdown fences.",
            f"""
Create exactly {count} original multiple-choice Linux exam questions.
Topic: {topic}
Difficulty: {difficulty}

Return this JSON format:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "answer": 0,
      "explanation": "Why the answer is correct"
    }}
  ]
}}

Requirements:
- Each question must have exactly four options.
- answer must be an integer from 0 to 3.
- Questions must be technically accurate and relevant to Linux.
- Do not repeat questions within this paper.
- Do not make up commands or Linux options.
- Make distractors plausible but clearly incorrect.
""",
        )
        data = json.loads(raw)
        questions = data["questions"]

        valid = (
            len(questions) == count
            and all(
                isinstance(q.get("question"), str)
                and isinstance(q.get("options"), list)
                and len(q["options"]) == 4
                and isinstance(q.get("answer"), int)
                and 0 <= q["answer"] <= 3
                and isinstance(q.get("explanation"), str)
                for q in questions
            )
        )
        if not valid:
            raise ValueError("The generated paper did not pass validation.")

        return questions, "AI-generated paper"

    except Exception as error:
        st.warning(
            "AI paper generation was unavailable, so a randomized paper "
            "from the built-in question bank is being used. "
            f"Details: {error}"
        )
        return fallback_questions, "Randomized question-bank paper"


# ---------- Visual design: purple, lime, green and burgundy ----------

st.markdown("""
<style>
.stApp {
    background: linear-gradient(145deg, #100b1d, #211032 55%, #30102b);
    color: #caff70;
}
[data-testid="stSidebar"] {
    background: #160c25;
    border-right: 1px solid #58304f;
}
[data-testid="stSidebar"] * {
    color: #baff67 !important;
}
h1, h2, h3, h4 {
    color: #caff70 !important;
}
p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
    color: #b9ef9b;
}
div[data-testid="stMetric"] {
    background: #251434;
    border: 1px solid #68415e;
    padding: 16px;
    border-radius: 15px;
}
div[data-testid="stMetricValue"] {
    color: #caff70;
}
.stButton > button, .stFormSubmitButton > button {
    background: #5b183f;
    color: #d7ff8c;
    border: 1px solid #9b4771;
    border-radius: 10px;
    font-weight: 600;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    background: #315b37;
    color: #e4ffb8;
    border-color: #a9ed79;
}
div[data-testid="stAlert"] {
    background: #241633;
    border: 1px solid #714765;
    border-radius: 12px;
}
.hero {
    padding: 26px;
    border-radius: 20px;
    border: 1px solid #714765;
    background: linear-gradient(120deg, #241235, #451632);
    margin-bottom: 20px;
}
.hero h1 { color: #d5ff85 !important; }
.hero p { color: #a9efae !important; }
</style>
""", unsafe_allow_html=True)


# ---------- Navigation ----------

st.sidebar.title("🐧 Linux Practice Lab")
page = st.sidebar.radio(
    "Navigate",
    [
        "Dashboard",
        "Take a Test",
        "Exam Paper",
        "Command Practice",
        "AI Linux Tutor",
        "Score History",
    ],
)
st.sidebar.caption("Learn it. Practise it. Master it.")

if not get_client():
    st.sidebar.warning("AI tutor needs a valid Groq API key.")

# ---------- Dashboard ----------

if page == "Dashboard":
    st.markdown("""
    <div class="hero">
      <h1>Linux Practice Lab</h1>
      <p>Learn Linux, solve practical challenges, and test yourself with AI.</p>
    </div>
    """, unsafe_allow_html=True)

    history = load_history()
    attempts = len(history)
    average = (
        round(sum(x.get("percentage", 0) for x in history) / attempts)
        if attempts else 0
    )
    best = max((x.get("percentage", 0) for x in history), default=0)

    a, b, c = st.columns(3)
    a.metric("Course topics", len(TOPICS))
    b.metric("Saved attempts", attempts)
    c.metric("Average score", f"{average}%")

    st.subheader("Your course")
    st.write(
        "Choose a topic to revise, generate a fresh exam paper, "
        "practise commands, or ask the AI tutor for help."
    )
    st.progress(min(attempts / 20, 1.0))
    st.caption(f"Best score: {best}%" if attempts else "Your progress starts with your first attempt.")

    for topic in TOPICS:
        st.markdown(f"- 🟢 {topic}")

# ---------- Topic quiz ----------

elif page == "Take a Test":
    st.title("📝 Topic Revision")
    topic = st.selectbox("Choose a topic", TOPICS)
    bank = QUESTION_BANK[topic]

    if st.button("Start a fresh topic quiz"):
        questions = random.sample(bank, len(bank))
        st.session_state["topic_paper"] = [
            {
                "question": q,
                "options": options,
                "answer": answer,
                "explanation": explanation,
            }
            for q, options, answer, explanation in questions
        ]
        st.session_state["topic_paper_topic"] = topic
        st.session_state.pop("topic_result", None)

    paper = st.session_state.get("topic_paper")
    if paper and st.session_state.get("topic_paper_topic") == topic:
        with st.form("topic_quiz"):
            selections = []
            for i, q in enumerate(paper):
                st.markdown(f"**{i + 1}. {q['question']}**")
                order = list(range(4))
                random.seed(f"{topic}-{i}-{st.session_state.get('topic_paper_id', 0)}")
                random.shuffle(order)
                q["display_order"] = order
                selected = st.radio(
                    "Select an answer",
                    [q["options"][j] for j in order],
                    index=None,
                    key=f"topic_{i}_{st.session_state.get('topic_paper_id', 0)}",
                    label_visibility="collapsed",
                )
                selections.append((selected, order))
            submitted = st.form_submit_button("Submit quiz")

        if submitted:
            score = 0
            result_rows = []
            for q, (selected, order) in zip(paper, selections):
                correct_option = q["options"][q["answer"]]
                is_correct = selected == correct_option
                score += int(is_correct)
                result_rows.append({
                    "question": q["question"],
                    "selected": selected,
                    "correct": correct_option,
                    "is_correct": is_correct,
                    "explanation": q["explanation"],
                })
            save_result("Topic Quiz", topic, score, len(paper))
            st.session_state["topic_result"] = {
                "score": score,
                "total": len(paper),
                "rows": result_rows,
            }
            st.rerun()

    result = st.session_state.get("topic_result")
    if result:
        st.subheader(f"Score: {result['score']}/{result['total']}")
        for row in result["rows"]:
            with st.expander(
                f"{'✅' if row['is_correct'] else '❌'} {row['question']}"
            ):
                st.write(f"Your answer: {row['selected'] or 'Not answered'}")
                st.write(f"Correct answer: {row['correct']}")
                st.info(row["explanation"])

# ---------- Randomized / AI exam paper ----------

elif page == "Exam Paper":
    st.title("📄 Exam Paper Generator")
    st.write("Generate a fresh paper for revision or exam practice.")

    topic = st.selectbox("Exam topic", TOPICS, key="exam_topic")
    difficulty = st.select_slider(
        "Difficulty",
        options=["Beginner", "Intermediate", "Advanced"],
        value="Intermediate",
    )
    count = st.select_slider(
        "Number of questions",
        options=[5, 10, 15],
        value=5,
    )

    if st.button("Generate new paper", type="primary"):
        with st.spinner("Preparing your paper..."):
            
            paper, source = generate_paper(topic, count, difficulty)
            random.shuffle(paper)

            st.session_state["exam_paper"] = paper
            st.session_state["exam_source"] = source
            st.session_state["exam_id"] = random.randint(1, 10**9)

            st.session_state.pop("exam_result", None)
            st.session_state["exam_id"] = random.randint(1, 10**9)
            st.session_state.pop("exam_result", None)
        st.rerun()

    paper = st.session_state.get("exam_paper")
    if paper:
        st.caption(st.session_state.get("exam_source", "Practice paper"))
        exam_id = st.session_state.get("exam_id", 0)

        with st.form(f"exam_form_{exam_id}"):
            answers = []
            for i, q in enumerate(paper):
                st.markdown(f"**Question {i + 1}. {q['question']}**")
                order = list(range(4))
                random.Random(f"{exam_id}-{i}").shuffle(order)
                selected = st.radio(
                    "Choose one",
                    [q["options"][j] for j in order],
                    index=None,
                    key=f"exam_{exam_id}_{i}",
                    label_visibility="collapsed",
                )
                answers.append(selected)
            submitted = st.form_submit_button("Submit exam")

        if submitted:
            score = 0
            rows = []
            for q, selected in zip(paper, answers):
                correct_answer = q["options"][q["answer"]]
                is_correct = selected == correct_answer
                score += int(is_correct)
                rows.append({
                    "question": q["question"],
                    "selected": selected,
                    "correct": correct_answer,
                    "is_correct": is_correct,
                    "explanation": q["explanation"],
                })

            save_result("Exam Paper", topic, score, len(paper))
            st.session_state["exam_result"] = {
                "score": score,
                "total": len(paper),
                "rows": rows,
            }
            st.rerun()

        result = st.session_state.get("exam_result")
        if result:
            st.subheader(
                f"Result: {result['score']}/{result['total']} "
                f"({round(result['score'] / result['total'] * 100)}%)"
            )
            st.progress(result["score"] / result["total"])
            for row in result["rows"]:
                with st.expander(
                    f"{'✅' if row['is_correct'] else '❌'} {row['question']}"
                ):
                    st.write(f"Your answer: {row['selected'] or 'Not answered'}")
                    st.write(f"Correct answer: {row['correct']}")
                    st.info(row["explanation"])

# ---------- Command practice ----------

elif page == "Command Practice":
    st.title("⌨️ Command Practice")
    st.write("Write a command and receive feedback. Commands are not executed.")

    task_name = st.selectbox("Choose a task", list(PRACTICE_TASKS))
    accepted, explanation = PRACTICE_TASKS[task_name]
    answer = st.text_input("Your command", key=f"cmd_{task_name}")

    if st.button("Check command", type="primary"):
        cleaned = normalize(answer)
        valid = cleaned in [normalize(x) for x in accepted]

        if valid:
            st.success("Correct! +1 point")
        else:
            st.error("Not quite. Review the expected command and try again.")
            st.code(accepted[0])

        st.info(explanation)
        save_result("Command Practice", task_name, int(valid), 1)

    st.warning("This checker compares text. It does not run commands on your computer.")

# ---------- AI tutor ----------

elif page == "AI Linux Tutor":
    st.title("🤖 AI Linux Tutor")
    st.write("Ask about Linux commands, errors, concepts, or your course topics.")

    tutor_topic = st.selectbox("Topic", TOPICS)
    mode = st.radio(
        "Help style",
        ["Explain simply", "Give me a hint", "Quiz me", "Troubleshoot an error"],
        horizontal=True,
    )
    prompt = st.text_area(
        "Your question",
        placeholder="Example: Explain chmod 755 with a simple example.",
        height=130,
    )

    if st.button("Ask AI tutor", type="primary"):
        if not prompt.strip():
            st.warning("Write a question first.")
        else:
            system_prompt = (
                "You are a careful, beginner-friendly Linux instructor. "
                "Teach practical Linux skills accurately. Explain commands, "
                "options, examples, and risks. Never claim to have executed "
                "a command. Do not recommend destructive commands casually. "
                "For hints, guide the learner without immediately giving the "
                "full answer. For quizzes, ask one clear question and wait "
                "for the learner to respond. Distinguish Ubuntu commands "
                "from commands that may vary across distributions."
            )
            user_prompt = (
                f"Course topic: {tutor_topic}\n"
                f"Help style: {mode}\n"
                f"Learner's message: {prompt}"
            )
            with st.spinner("The AI tutor is thinking..."):
                try:
                    answer = ask_llm(system_prompt, user_prompt)
                    st.session_state["last_tutor_answer"] = answer
                except Exception as error:
                    st.error(f"AI tutor could not respond: {error}")

    if st.session_state.get("last_tutor_answer"):
        st.markdown("### Tutor response")
        st.markdown(st.session_state["last_tutor_answer"])

# ---------- History ----------

elif page == "Score History":
    st.title("📈 Score History")
    history = load_history()

    if not history:
        st.info("No scores yet. Complete a quiz or command challenge.")
    else:
        for item in reversed(history):
            st.markdown(
                f"**{item.get('category', 'Test')}** — {item['topic']} · "
                f"{item['score']}/{item['total']} "
                f"({item['percentage']}%) · {item['date']}"
            )

        st.download_button(
            "Download history",
            data=json.dumps(history, indent=2),
            file_name="linux_score_history.json",
            mime="application/json",
        )

st.sidebar.divider()
st.sidebar.caption("Purple • Lime • Green • Burgundy")
