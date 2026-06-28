# 🤖📚 AI-Powered Study Assistant

> **An intelligent, document-driven study companion for GATE and college exams — powered by Google Gemini AI.**
> Upload your notes, ask questions, generate summaries, and practice exam-style questions — all in one sleek interface.

---

## 🔖 Badges

![AI Powered](https://img.shields.io/badge/AI-Powered-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Demo Images

![demo](https://github.com/Tanmay1112004/AI-Powered-Study-Assistant/blob/main/screenshots/Screenshot_7-2-2026_191923_probable-cod-97qgx7pr7vjvfp4wp-8501.app.github.dev.jpeg)   

![demo](https://github.com/Tanmay1112004/AI-Powered-Study-Assistant/blob/main/screenshots/Screenshot_7-2-2026_191958_probable-cod-97qgx7pr7vjvfp4wp-8501.app.github.dev.jpeg)     

![demo](https://github.com/Tanmay1112004/AI-Powered-Study-Assistant/blob/main/screenshots/Screenshot_7-2-2026_192043_probable-cod-97qgx7pr7vjvfp4wp-8501.app.github.dev.jpeg)  

---

## 📌 Overview

**AI-Powered Study Assistant** is a smart learning tool designed to help students prepare efficiently for **GATE and university exams**.
It leverages **Google Gemini 2.0 Flash** to understand your study materials and provide:

* Instant summaries
* Concept explanations
* Practice questions
* Document-based Q&A

No fluff. Just focused learning.

---

## ✨ Key Features

### 🎯 Core Capabilities

* 📁 **Multi-Format Upload** — PDF, DOCX, TXT, MD
* 📝 **Smart Summarization** — Clear, exam-oriented summaries
* ❓ **Question Generation** — GATE & college-level practice questions
* 💡 **Concept Explanation** — Simplified, student-friendly answers
* 💬 **Document Chat** — Ask questions directly from your notes

### ⚙️ Technical Highlights

* 🤖 **Gemini 2.0 Flash** — Latest Google Generative AI
* 🔍 **Lightweight RAG** — Context-aware document responses
* 🎨 **Modern Streamlit UI** — Clean, fast, responsive
* ⚡ **Real-Time Output** — Near-instant results
* 📱 **Cross-Device Support** — Desktop, tablet, mobile

---

## 🚀 Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Tanmay1112004/ai-study-assistant.git
cd ai-study-assistant
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Get Gemini API Key

1. Visit **Google AI Studio**
2. Create a free API key
3. Copy and keep it ready

### 4️⃣ Run the App

```bash
streamlit run app.py
```

### 5️⃣ Open in Browser

```
http://localhost:8501
```

---

## 📁 Project Structure

```
ai-study-assistant/
│
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
└── chroma_db/           # Vector store (auto-generated)
```

---

## 🧭 How It Works

### 🔑 Step 1: Configure API Key

1. Launch the app
2. Enter Gemini API key in the sidebar
3. Click **Validate API Key**

### 📄 Step 2: Upload Documents

1. Open **Upload Documents** tab
2. Upload supported files
3. Click **Process Documents**

### 🧠 Step 3: Use AI Features

* **Summarize** → Quick revision notes
* **Generate Questions** → Exam practice
* **Explain Topics** → Concept clarity
* **Chat** → Ask doubts from documents

---

## 🧠 Architecture Overview

```
User Input
   │
   ▼
Streamlit UI
   │
   ▼
Document Processing ──▶ Gemini AI
   │                        │
   ▼                        ▼
Vector Store         Contextual Responses
```

---

## 📊 Supported File Formats

| Format | Capability      | Max Size |
| ------ | --------------- | -------- |
| PDF    | Text extraction | 10 MB    |
| DOCX   | Text extraction | 10 MB    |
| TXT    | Direct input    | 10 MB    |
| MD     | Direct input    | 10 MB    |

---

## 💡 Example Use Cases

### 🎓 GATE Exam Prep

1. Upload syllabus & notes
2. Generate topic-wise summaries
3. Create practice questions
4. Clarify weak areas

### 🏫 College Assignments

1. Upload lecture notes
2. Generate summaries
3. Create assignment questions
4. Chat for quick doubts

### ⚡ Quick Revision

1. Upload all notes
2. Get condensed summaries
3. Generate mock tests
4. Self-evaluate instantly

---

## ⚡ Performance Tips

* Split very large PDFs
* Use clean, readable documents
* Ask specific questions
* Avoid scanned PDFs without text

---

## 🔐 Security & Privacy

* 🔑 API keys are **session-only**
* 📄 Documents processed **locally**
* 🚫 No persistent data storage
* 🗑 Temporary files auto-cleaned

---

## 🚨 Troubleshooting

| Issue             | Fix                            |
| ----------------- | ------------------------------ |
| Invalid API Key   | Enable billing in Google Cloud |
| File Upload Error | Ensure size < 10MB             |
| No Text Extracted | Try another document           |
| App Slow          | Reduce file size               |
| Port Busy         | Use `--server.port 8502`       |

### Debug Commands

```bash
python -c "import streamlit"
python -c "import google.generativeai"
streamlit run app.py --logger.level=debug
```

---

## 📱 Mobile Access

Access the app on the same network:

```
http://<your-ip>:8501
```

Fully responsive — no extra setup.

---

## 📈 Educational Impact

### 👨‍🎓 Students

* Faster revision
* Better concept clarity
* Personalized practice
* 24/7 doubt solving

### 👩‍🏫 Educators

* Automated question creation
* Content summarization
* Time-saving workflows

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push & open a PR

### 💡 Roadmap Ideas

* Mobile app
* Offline support
* More file formats
* Progress tracking
* Collaboration tools

---

## 📄 License

This project is licensed under the **MIT License**.
See the `LICENSE` file for details.

---

## 🙏 Acknowledgments

* **Google Gemini Team**
* **Streamlit Team**
* Open-source contributors
* Student testers

---

## ⭐ Star the Project

If this helped you, **drop a star** ⭐ — it genuinely helps!

---

## 🎯 Ready to Learn Smarter?

```bash
streamlit run app.py
```

**Happy Studying & All the Best! 🚀🎓**

--- 
