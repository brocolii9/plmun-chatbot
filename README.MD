# PLMun AI Chatbot

A bilingual (English / Filipino / Taglish) conversational AI system for the
PLMun Registrar's Office. Built with FastAPI, MySQL, and a custom
Multinomial Naive Bayes classifier.

---

## Features

### Student Side

- Register / Login with JWT authentication
- Guest mode (no account required)
- Text-based chat with intent classification
- Bilingual responses (auto-detects English vs Filipino/Taglish)
- Confidence gate (no hallucination — refers to Registrar when unsure)
- Voice input (STT via Web Speech API)
- Voice output (TTS — pre-recorded MP3s + OS voices with gender picker)
- Conversation history with rename and delete
- Developer mode toggle (Ctrl+Shift+D)

### Admin Side (AdminLTE)

- Separate admin login (JWT)
- Real-time analytics dashboard
- Knowledge Base CRUD (create / edit / delete)
- Conversation logs viewer (paginated)
- Role-based access (super_admin / content_editor)

---

## Stack

| Layer    | Technology                          |
| -------- | ----------------------------------- |
| Backend  | Python 3.12 + FastAPI               |
| NLP      | Pure-Python Multinomial Naive Bayes |
| Database | MySQL 8.0 (SQLAlchemy ORM)          |
| Auth     | JWT (bcrypt password hashing)       |
| Frontend | HTML / CSS / JavaScript (vanilla)   |
| Admin UI | AdminLTE 3.2                        |
| Icons    | Font Awesome 6.5 (bundled locally)  |

---

## Setup

### Prerequisites

- Python 3.12+
- MySQL 8.0+
- Git

### Installation

```bash
git clone https://github.com/brocoli19/plmun-chatbot.git
cd plmun-chatbot
```
