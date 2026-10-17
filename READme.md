# 🐧 Linux Practice Lab

An AI-powered Linux learning platform designed to help learners practise Linux commands, test their knowledge, and improve their system administration skills.

## ✨ Features

- 📚 Topic-based Linux quizzes
- 📝 Randomized and AI-generated exam papers
- 🤖 AI Linux tutor powered by Groq
- ⌨️ Practical Linux command challenges
- 📊 Score history and progress tracking
- 🎨 Dark purple interface with lime, green, and burgundy accents
- 📥 Downloadable score history

## 📖 Topics Covered

- Basic Linux Commands
- Users and Groups
- Package Management
- Permissions and Ownership
- Processes and Services
- Environment Variables and Bash
- Archives and Compression
- SSH and Networking
- File Search and Text Processing
- Cron and System Monitoring
- Logs and Troubleshooting

## 🛠️ Technologies

- Python
- Streamlit
- Groq API
- Large Language Models (LLMs)
- JSON
- python-dotenv

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/20pwele5276-jpg/Linux_Practice_Lab.git
cd Linux_Practice_Lab
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install streamlit groq python-dotenv
```

## 🔑 API Configuration

Create a `.env` file in the project directory:

```text
GROQ_API_KEY=your_groq_api_key
```

Replace the placeholder with your own API key.

**Never commit your `.env` file or expose your API key publicly.**

## ▶️ Run the Application

```bash
python -m streamlit run main.py
```

Open the local URL shown in your terminal, usually `http://localhost:8501`.

## 📈 Progress Tracking

Quiz and command-practice attempts are saved locally in `score_history.json`. This file is generated when you complete activities.

## ⚠️ Notes

- AI-generated content requires a valid API key and an available model.
- The application can fall back to built-in questions when AI paper generation fails.
- Command practice checks submitted text; it does not execute commands on your computer.
- AI-generated explanations and questions should be checked against reliable Linux documentation.

## 👩‍💻 Author

**Wajiha Gul**

GitHub: [20pwele5276-jpg](https://github.com/20pwele5276-jpg)

