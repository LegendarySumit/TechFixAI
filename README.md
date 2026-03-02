<div align="center">

# 🎙️ TechFixAI

**Enterprise-Grade Voice-to-Ticket AI System**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-FF6B6B?logo=ai&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?logo=railway&logoColor=white)

*Transform multilingual voice into structured support tickets with intelligent routing*

🌐 **[Live Demo](https://techfixai.up.railway.app)** • [Features](#-key-features) • [Quick Start](#-quick-start) • [API Docs](#-api-reference)

</div>

---

## 🎯 Overview

**TechFixAI** is an **enterprise-grade automated incident intake and routing system** that transforms multilingual voice input into structured, actionable support tickets with intelligent developer assignment.

### Core Flow
```
Japanese Audio Recording
        ↓
Groq Whisper STT (whisper-large-v3)
        ↓
Groq LLaMA Translation (Japanese → English)
        ↓
AI-Powered Ticket Generation
        ↓
Deterministic Developer Assignment
        ↓
Real-Time Developer-Client Chat
```

**This is NOT:**
❌ A chatbot  
❌ A translation demo  
❌ An AI playground

**This IS:**
✅ An enterprise incident management system  
✅ A multilingual support automation platform  
✅ A production-ready workflow orchestrator

---

## ✨ Key Features

### 🔐 Authentication
- Email/password signup and login (instant access, no verification)
- Google OAuth 2.0 (one-click sign-in)
- Session cookies (`httponly`, `SameSite=lax`)
- PBKDF2-SHA256 password hashing (no length limit)

### 🎙️ Voice Input & Processing
- Real-time audio capture with **Web Audio API**
- Visual waveform display (20 animated bars)
- Live recording timer (MM:SS format)
- Optional screenshot/image upload (PNG, JPG, max 50MB)
- Microphone permission handling
- Process step indicators (Recording → Encryption → Analysis → Assignment)

### 🌐 Transcription & Translation
- **Speech-to-Text:** Groq Whisper (whisper-large-v3) — Japanese support
- **Translation:** Groq LLaMA (llama-3.1-8b-instant) — Context-aware technical translation
- Split-view display: **Original Japanese (left)** | **English Translation (right)**
- Audit trail with both transcripts stored
- Graceful mock fallback if `GROQ_API_KEY` not set

### 🎫 Ticket Generation & Assignment
- **Structured ticket schema:** Number, Title, Category, Priority, Technical Area
- AI-generated via Groq LLaMA with rule-based fallback
- **Deterministic assignment rules** (no AI randomness):
  - Backend/Infrastructure + High/Critical → Backend Team
  - Frontend/UI + Any Priority → Frontend Team
  - Database + High/Critical → Backend Team
  - Default → Least loaded developer

### 👨‍💻 Developer Tools
- Developer directory with team statistics cards
- Real-time developer chat interface on ticket detail page
- Quick action buttons (Mark as Resolved, In Progress, On Hold)
- Auto-delete tickets after resolution (5 seconds)

### 📊 Admin Dashboard
- Ticket management (CRUD operations)
- Assignment routing audit trail
- Developer performance metrics
- System health check endpoint (`/health`)

---

## 🏗️ System Architecture

**Style:** Modular Monolith (NOT microservices)
```
┌─────────────────────────────────────────────────────────────┐
│                    Japanese Audio Upload                    │
└────────────────────┬────────────────────────────────────────┘
                     ↓
            /api/voice/upload
         Audio saved to storage/audio/
                     ↓
        ┌────────────────────────┐
        │  Groq Whisper STT      │
        │  Japanese → Text       │
        └────────┬───────────────┘
                 ↓
        ┌────────────────────────┐
        │  Groq LLaMA Translation│
        │  Japanese → English    │
        └────────┬───────────────┘
                 ↓
        ┌────────────────────────┐
        │  Groq LLaMA Ticket Gen │
        │  English → JSON Ticket │
        └────────┬───────────────┘
                 ↓
        ┌────────────────────────┐
        │  Deterministic Logic   │
        │  Ticket → Developer    │
        └────────┬───────────────┘
                 ↓
        ┌────────────────────────┐
        │  Assigned Developer    │
        │  + Chat Interface      │
        └────────────────────────┘
```

---

## 💻 Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)

- **FastAPI + Uvicorn** — Async API, auto-docs, high performance
- **SQLAlchemy 2.0** — ORM with auto-migration
- **PostgreSQL** (prod) / **SQLite** (local) — ACID compliance

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white)

- **Jinja2** — Server-side rendering
- **Bootstrap 5** — Dark theme UI
- **Web Audio API** — Real-time recording with waveform

### AI & ML
![Groq](https://img.shields.io/badge/Groq-FF6B6B?logo=ai&logoColor=white)

- **Groq Whisper** (whisper-large-v3) — Japanese speech recognition
- **Groq LLaMA** (llama-3.1-8b-instant) — Translation & ticket generation

### Security & Auth
- **Session cookies** — httponly, SameSite=lax
- **Google OAuth 2.0** — One-click sign-in
- **PBKDF2-SHA256** (passlib) — Password hashing, no length limit
- **Fernet AES-256** (cryptography) — Audio encryption at rest

### Deployment
![Railway](https://img.shields.io/badge/Railway-0B0D0E?logo=railway&logoColor=white)

- **Railway** — Zero-config cloud hosting
- **PostgreSQL Plugin** — Persistent data storage

---

## 📁 Project Structure
```
TechFixAI/
├── app/
│   ├── main.py                      # FastAPI app + middleware + router registration
│   ├── core/
│   │   ├── config.py                # Environment variables with defaults
│   │   └── security.py              # API key auth helper
│   ├── api/
│   │   ├── voice.py                 # Voice upload + STT/translation pipeline
│   │   ├── ticket.py                # Ticket CRUD + status updates
│   │   ├── admin.py                 # Admin dashboard endpoints
│   │   ├── developer.py             # Developer directory API
│   │   ├── auth.py                  # Google OAuth 2.0 routes
│   │   └── web.py                   # HTML page routes
│   ├── services/
│   │   ├── stt_service.py           # Groq Whisper STT
│   │   ├── translation_service.py   # Groq LLaMA translation
│   │   ├── ticket_service.py        # Groq LLaMA ticket generation
│   │   ├── assignment_service.py    # Deterministic developer assignment
│   │   └── email_service.py         # SMTP email (future use)
│   ├── models/
│   │   ├── conversation.py          # Voice + transcript + translation
│   │   ├── ticket.py                # Ticket ORM model
│   │   ├── developer.py             # Developer ORM model
│   │   └── user.py                  # User accounts + OAuth
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy declarative base
│   │   ├── session.py               # DB session + pool config
│   │   └── init_db.py               # Table creation + migrations
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │       ├── voice-recorder.js    # Web Audio API recording
│   │       ├── ui-components.js     # Reusable UI components
│   │       └── app.js               # Global utilities + API client
│   ├── templates/                   # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── upload.html              # Voice recording interface
│   │   ├── ticket_detail.html       # Ticket + developer chat
│   │   └── ...
│   └── utils/
│       ├── audio.py                 # Audio validation
│       ├── encryption.py            # AES-256 Fernet
│       ├── audit.py                 # Audit logging
│       └── text.py                  # Text processing
├── scheduler.py                     # Background cleanup tasks
├── requirements.txt
├── Procfile                         # Railway process definition
├── railway.toml
└── storage/
    └── audio/                       # Uploaded audio files
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Groq API key ([Get free key](https://console.groq.com))

### Setup (3 minutes)

**1. Clone and install**
```bash
git clone https://github.com/LegendarySumit/TechFixAI.git
cd TechFixAI
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

**2. Configure environment**
```bash
cp .env.example .env
```

Minimum required `.env`:
```env
GROQ_API_KEY=gsk_your_key_here
SECRET_KEY=any-random-string-at-least-32-chars
```

**3. Start server**
```bash
uvicorn app.main:app --reload
```

**4. Open browser**
```
http://localhost:8000
```

✅ Database tables and seed developers are created automatically on first run!

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Groq API key for STT + translation + ticket generation |
| `SECRET_KEY` | ✅ Yes | Session signing + audio encryption key |
| `DATABASE_URL` | No | PostgreSQL URL (defaults to SQLite locally) |
| `GOOGLE_CLIENT_ID` | No | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth Client Secret |
| `GOOGLE_REDIRECT_URI` | No | OAuth callback URL (required on Railway) |
| `OPENAI_API_KEY` | No | OpenAI Whisper fallback |
| `GEMINI_API_KEY` | No | Gemini fallback for translation/ticket gen |
| `ENCRYPTION_ENABLED` | No | AES-256 audio encryption (default: true) |
| `DATA_RETENTION_DAYS` | No | Auto-delete older than N days (default: 30) |
| `APP_BASE_URL` | No | Public URL (e.g., `https://techfixai.up.railway.app`) |

---

## 🎬 User Workflows

### 📞 Client (Japanese Speaker)

1. **Sign up** at `/signup` or **log in** at `/login` (Google or email)
2. Visit `/upload`
3. Click **Record** and speak the technical issue in Japanese
4. Optional: Attach screenshot
5. **Submit** → View ticket number, Japanese original, English translation
6. **Chat** with assigned developer in real-time

### 👨‍💻 Developer (English Speaker)

1. Visit `/tickets` to see new tickets
2. **Open a ticket** → See Japanese original + English translation + assignment reason
3. **Chat with client**, update status via quick action buttons
4. **Mark resolved** → Ticket auto-deletes in 5 seconds

### 🔧 Admin

1. Visit `/dashboard` for system overview
2. Monitor ticket counts, priorities, developer workloads
3. View assignment reasoning and audit trail

---

## 🧠 Assignment Logic (Deterministic, No AI)

Rules applied in order:

| Condition | Assignment |
|-----------|------------|
| **Backend/Infrastructure** + **High/Critical** | → Backend Team developer |
| **Frontend/UI** + **Any Priority** | → Frontend Team developer |
| **Database** + **High/Critical** | → Backend Team developer |
| **Default** | → Least loaded developer (fewest active tickets) |

**Every ticket stores a human-readable assignment reason:**
```
"Rule: Backend/Infrastructure + HIGH priority → Backend Team"
"Default: Assigned to least loaded developer (2 active tickets)"
```

✅ **No randomness**  
✅ **No black box**  
✅ **Fully explainable routing**

---

## 📖 API Reference

### Voice Endpoints
```
POST   /api/voice/upload                      # Upload Japanese audio + metadata
GET    /api/voice/status/{conversation_id}    # Get processing status
POST   /api/voice/translate                   # Translate text (EN ↔ JA)
```

### Ticket Endpoints
```
GET    /api/tickets/                  # List tickets (filterable)
GET    /api/tickets/{ticket_number}   # Get ticket details
PATCH  /api/tickets/{ticket_number}/status    # Update status
DELETE /api/tickets/{ticket_number}   # Delete ticket
```

### Developer Endpoints
```
GET    /api/developers/           # List all developers
GET    /api/developers/{id}       # Get developer detail
PATCH  /api/developers/{id}/status # Update status (online/busy/offline)
```

### Admin Endpoints
```
GET    /api/admin/dashboard       # System overview
GET    /api/admin/conversations   # All conversations
GET    /api/admin/developers      # Developer workload report
```

### Auth Endpoints
```
GET    /auth/google               # Redirect to Google OAuth
GET    /auth/google/callback      # Google OAuth callback
```

---

## 🛡️ Security Features

### 🔐 Audio Encryption at Rest
- Audio encrypted with **Fernet (AES-128-CBC + HMAC-SHA256)**
- Key derived from `SECRET_KEY` via SHA-256
- Toggle with `ENCRYPTION_ENABLED=true/false`

### 🗑️ Data Retention
- Scheduler runs nightly
- Purges audio files and DB records older than `DATA_RETENTION_DAYS`
- All deletions logged to audit trail

### 📝 Audit Logging
- Every upload, ticket creation, and cleanup logged to `logs/audit.log` (JSON lines)
- Zero payload logging — no sensitive data in logs

### 🔑 Auth Security
- Passwords hashed with **PBKDF2-SHA256** (no length restrictions)
- Session cookies: `httponly=True`, `samesite=lax`
- `.env` in `.gitignore` — credentials never committed

---

## 🚢 Deploying to Railway

### Step-by-Step

1. **Push to GitHub**
2. Create Railway project → **Deploy from GitHub repo**
3. **Add PostgreSQL plugin** (optional, for persistent data)
4. **Set environment variables** in Railway dashboard:

| Variable | Value |
|----------|-------|
| `GROQ_API_KEY` | Your Groq API key |
| `SECRET_KEY` | `openssl rand -hex 32` output |
| `DATABASE_URL` | Auto-set by PostgreSQL plugin |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | `https://your-app.up.railway.app/auth/google/callback` |
| `APP_BASE_URL` | `https://your-app.up.railway.app` |

Railway auto-detects `Procfile` and deploys. Build config is in `nixpacks.toml`.

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Transcription returns mock text** | Verify `GROQ_API_KEY` in `.env`, restart server |
| **Login fails** | Accounts pre-March 2026 need re-registration (pbkdf2 migration) |
| **Google OAuth fails** | Add `GOOGLE_REDIRECT_URI` to Railway variables + Google Console |
| **Database column errors** | Auto-migration runs on startup — redeploy on Railway |
| **Audio upload rejected** | Max 50MB, supported: WAV, MP3, M4A, WebM, OGG, MP4 |

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Languages** | Python, JavaScript, HTML, CSS |
| **API Endpoints** | 20+ RESTful routes |
| **Services** | 5 AI/ML integrations |
| **Database Tables** | 4 core models |
| **Auth Methods** | 2 (Email + Google OAuth) |
| **Supported Languages** | Japanese, English |
| **Production Ready** | ✅ YES |

---

## 📅 Version History

| Version | Date | Changes |
|---------|------|---------|
| **v1.1** | Mar 2026 | PBKDF2-SHA256, no verification gate, Google OAuth stable |
| **v1.0** | Feb 2026 | Initial release: Groq STT/translation/tickets, deterministic assignment |

---

## 🔮 Future Enhancements

- [ ] Multi-language support (Chinese, Korean, Spanish)
- [ ] SMS/Email notifications for ticket updates
- [ ] Advanced analytics dashboard
- [ ] Mobile app (iOS/Android)
- [ ] Integration with Slack/Microsoft Teams
- [ ] Voice response generation (TTS)
- [ ] Bulk ticket import/export
- [ ] Custom developer assignment rules via UI

---

## 📄 License

MIT License — Free to use and modify

---

## 👨‍💻 Author

**LegendarySumit**

- GitHub: [@LegendarySumit](https://github.com/LegendarySumit)
- Project: [TechFixAI](https://github.com/LegendarySumit/TechFixAI)
- Live Demo: [https://techfixai.up.railway.app](https://techfixai.up.railway.app)

---

## 🙏 Acknowledgments

- **Groq** — For ultra-fast AI inference
- **FastAPI** — For modern Python API framework
- **Railway** — For seamless cloud deployment
- Built for multilingual technical support teams worldwide

---

<div align="center">

**🎙️ Bridging language barriers in technical support**

*Built for Japanese-English incident communications*

---

**⭐ Star this repo if you find it helpful!**

**🚀 Open to contributions, feedback, and enterprise partnerships**

*Version 1.1 • Production Ready • March 2026*

</div>