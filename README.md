# TechFixAI — Voice-to-Ticket AI System

## 🎯 Overview

An **enterprise-grade automated incident intake + routing system** that transforms multilingual voice input into structured, actionable support tickets with intelligent developer assignment.

**Core Flow:**
1. Japanese clients record technical issues via voice
2. System transcribes (Japanese) using Groq Whisper
3. System translates (English) using Groq LLaMA
4. Generates structured technical tickets automatically
5. Routes to best-fit developers using deterministic assignment logic
6. Enables real-time developer–client communication via chat interface

**NOT** a chatbot. **NOT** a translation demo. **NOT** an AI playground.

**Live:** [https://techfixai.up.railway.app](https://techfixai.up.railway.app)

---

## ✨ Key Features

### Authentication ✅
- Email/password signup and login (no email verification required — instant access)
- Google OAuth 2.0 (one-click sign-in)
- Session cookies (httponly, SameSite=lax)
- Password hashing with PBKDF2-SHA256 (no length limit)

### Voice Input & Processing ✅
- Real-time audio capture using Web Audio API with visual waveform (20 animated bars)
- Live recording timer with MM:SS format
- Optional screenshot/image upload (PNG, JPG, max 50MB)
- Microphone permission handling with user-friendly alerts
- Client metadata (ID, environment, urgency override)
- Process step indicators (Recording → Encryption → Analysis → Assignment)

### Transcription & Translation ✅
- Speech-to-Text using Groq Whisper (whisper-large-v3) — Japanese support
- Context-aware technical translation via Groq LLaMA (llama-3.1-8b-instant)
- Split-view display: Original Japanese (left) | English Translation (right)
- Both transcripts stored for audit trail
- Graceful mock fallback if GROQ_API_KEY not set

### Ticket Generation & Assignment ✅
- Structured ticket schema (Number, Title, Category, Priority, Technical Area)
- AI-generated via Groq LLaMA with rule-based fallback
- **Deterministic assignment rules** (no AI randomness):
  - Backend/Infrastructure + High/Critical → Backend Team
  - Frontend/UI + Any Priority → Frontend Team
  - Database + High/Critical → Backend Team
  - Default → Least loaded developer

### Developer Tools ✅
- Developer directory with team statistics cards
- Real-time developer chat interface on ticket detail page
- Quick action buttons (Mark as Resolved, In Progress, On Hold)
- Auto-delete tickets after resolution

### Admin Dashboard ✅
- Ticket management (CRUD operations)
- Assignment routing audit trail
- Developer performance metrics
- System health check endpoint

---

## 🏗️ System Architecture

**Style:** Modular Monolith (NOT microservices)

```
Japanese Audio Upload
        ↓
/api/voice/upload  →  Audio saved to storage/audio/
        ↓
STT (Groq whisper-large-v3)
   Japanese → Text
        ↓
Translation (Groq llama-3.1-8b-instant)
   Japanese Text → English Text
        ↓
Ticket Generation (Groq llama-3.1-8b-instant)
   English Text → Structured JSON ticket
        ↓
Deterministic Assignment Logic
   Ticket fields → Best-fit Developer
        ↓
Assigned Developer + Chat Interface
```

---

## 💻 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI + Uvicorn | Async API, auto-docs, high performance |
| **Frontend** | Jinja2 + HTML/CSS/JS | Server-side rendering + interactive components |
| **STT** | Groq Whisper (whisper-large-v3) | Japanese speech recognition |
| **Translation** | Groq LLaMA (llama-3.1-8b-instant) | Context-aware technical translation |
| **Ticket Gen** | Groq LLaMA (llama-3.1-8b-instant) | Structured JSON ticket generation |
| **DB (local)** | SQLite | Zero-config local development |
| **DB (prod)** | PostgreSQL (Railway) | ACID compliance, audit trail |
| **ORM** | SQLAlchemy 2.0 | Database abstraction, auto-migration |
| **Auth** | Session cookies + Google OAuth 2.0 | Web authentication |
| **Password** | PBKDF2-SHA256 (passlib) | No 72-byte limit, no bcrypt issues |
| **Encryption** | Fernet AES-256 (cryptography) | Audio at rest |
| **Deployment** | Railway | Zero-config cloud hosting |

---

## 📁 Project Structure

```
TechFixAI/
│
├── app/
│   ├── main.py                      # FastAPI app + middleware + router registration
│   │
│   ├── core/
│   │   ├── config.py                # All settings (env vars with defaults)
│   │   └── security.py              # API key auth helper
│   │
│   ├── api/
│   │   ├── voice.py                 # Voice upload + background STT/translation pipeline
│   │   ├── ticket.py                # Ticket CRUD + status updates + auto-delete
│   │   ├── admin.py                 # Admin dashboard stats endpoints
│   │   ├── developer.py             # Developer directory API
│   │   ├── auth.py                  # Google OAuth 2.0 routes
│   │   └── web.py                   # HTML page routes (login/signup/dashboard etc.)
│   │
│   ├── services/
│   │   ├── stt_service.py           # Groq Whisper STT (Groq → OpenAI → mock fallback)
│   │   ├── translation_service.py   # Groq LLaMA translation (Groq → Gemini → mock)
│   │   ├── ticket_service.py        # Groq LLaMA ticket generation (Groq → Gemini → rules)
│   │   ├── assignment_service.py    # Deterministic developer assignment (rules-based)
│   │   └── email_service.py         # SMTP email helper (optional — reserved for future use)
│   │
│   ├── models/
│   │   ├── conversation.py          # Voice + transcript + translation + status
│   │   ├── ticket.py                # Ticket ORM model
│   │   ├── developer.py             # Developer ORM model
│   │   └── user.py                  # User accounts + password + OAuth fields
│   │
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy declarative base
│   │   ├── session.py               # DB session + pool config
│   │   └── init_db.py               # Table creation + safe ADD COLUMN migration
│   │
│   ├── static/
│   │   ├── css/
│   │   └── js/
│   │       ├── voice-recorder.js    # Web Audio API recording service
│   │       ├── ui-components.js     # Reusable UI components
│   │       └── app.js               # Global utilities + API client
│   │
│   ├── templates/                   # Jinja2 HTML templates (Bootstrap 5 dark theme)
│   │   ├── base.html                # Navbar, footer, common CSS/JS
│   │   ├── home.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── upload.html              # Voice recording + file upload
│   │   ├── tickets.html
│   │   ├── ticket_detail.html       # Ticket + developer chat
│   │   ├── developers.html
│   │   ├── dashboard.html
│   │   ├── documentation.html
│   │   ├── security.html
│   │   ├── privacy.html
│   │   ├── about.html
│   │   └── support.html
│   │
│   └── utils/
│       ├── audio.py                 # Audio duration + validation helpers
│       ├── encryption.py            # AES-256 Fernet encrypt/decrypt
│       ├── audit.py                 # Audit log writer
│       └── text.py                  # Text processing utilities
│
├── audit.py                         # Root-level audit log (used by scheduler)
├── scheduler.py                     # Background cleanup tasks (data retention)
├── .env.example                     # Environment variable template
├── .gitignore                       # .env never committed — secrets always safe
├── requirements.txt                 # Python dependencies
├── Procfile                         # Railway/Heroku process definition
├── railway.toml                     # Railway deployment config
├── nixpacks.toml                    # Build config for Railway
└── storage/
    └── audio/                       # Uploaded audio files (ephemeral on Railway)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Groq API key (free at [https://console.groq.com](https://console.groq.com))
- No PostgreSQL needed locally — SQLite is used automatically

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

Database tables and seed developers are created automatically on first run. No manual migration needed.

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Groq key — STT + translation + ticket gen |
| `SECRET_KEY` | ✅ Yes | Session signing + audio encryption key |
| `DATABASE_URL` | No | PostgreSQL URL (defaults to SQLite locally) |
| `GOOGLE_CLIENT_ID` | No | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth Client Secret |
| `GOOGLE_REDIRECT_URI` | No | OAuth callback URL (required on Railway) |
| `OPENAI_API_KEY` | No | OpenAI Whisper fallback |
| `GEMINI_API_KEY` | No | Gemini fallback for translation/ticket gen |
| `ENCRYPTION_ENABLED` | No | AES-256 audio encryption (default: true) |
| `DATA_RETENTION_DAYS` | No | Auto-delete older than N days (default: 30) |
| `SMTP_HOST` | No | SMTP host for future email features |
| `SMTP_USER` | No | SMTP email address |
| `SMTP_PASSWORD` | No | SMTP App Password |
| `APP_BASE_URL` | No | Public URL e.g. `https://techfixai.up.railway.app` |
| `CORS_ORIGINS` | No | Comma-separated allowed CORS origins |

---

## 🎬 User Workflows

### Client (Japanese Speaker)
1. Sign up at `/signup` or log in at `/login` (Google or email)
2. Visit `/upload`
3. Click record and speak the technical issue in Japanese
4. Optional: attach screenshot
5. Submit → view ticket number, Japanese original, English translation
6. Chat with assigned developer in real-time

### Developer (English Speaker)
1. Visit `/tickets` to see new tickets
2. Open a ticket → see Japanese original + English translation + assignment reason
3. Chat with client, update status via quick action buttons
4. Mark resolved → ticket auto-deletes in 5 seconds

### Admin
1. Visit `/dashboard` for system overview
2. Monitor ticket counts, priorities, developer workloads
3. View assignment reasoning and audit trail

---

## 🔧 Assignment Logic (Deterministic, No AI)

Rules applied in order:

1. **Backend/Infrastructure + High/Critical priority** → Backend Team developer
2. **Frontend/UI + Any priority** → Frontend Team developer
3. **Database + High/Critical priority** → Backend Team developer
4. **Default** → Least loaded developer (fewest active tickets)

Every ticket stores a human-readable assignment reason:
```
"Rule: Backend/Infrastructure + HIGH priority → Backend Team"
"Default: Assigned to least loaded developer (2 active tickets)"
```

No randomness. No black box. Fully explainable routing.

---

## 🛡️ Security

### Audio Encryption at Rest ✅
- Audio bytes encrypted with **Fernet (AES-128-CBC + HMAC-SHA256)**
- Key derived from `SECRET_KEY` via SHA-256
- Toggle with `ENCRYPTION_ENABLED=true/false`

### Data Retention ✅
- Scheduler runs nightly — purges audio files and DB records older than `DATA_RETENTION_DAYS`
- All deletions logged to audit trail

### Audit Logging ✅
- Every upload, ticket creation and cleanup logged to `logs/audit.log` (JSON lines)
- Zero payload logging — no sensitive data ever written to logs

### Auth Security ✅
- Passwords hashed with PBKDF2-SHA256 via passlib — no length restrictions
- Session cookies: `httponly=True`, `samesite=lax`
- `.env` in `.gitignore` — credentials never committed to git

---

## 📖 API Reference

### Voice
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/voice/upload` | Upload Japanese audio + optional image + metadata |
| GET | `/api/voice/status/{conversation_id}` | Processing status + transcripts + ticket |
| POST | `/api/voice/translate` | Translate text between EN and JA |

### Tickets
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tickets/` | List tickets (filterable by status/priority/area) |
| GET | `/api/tickets/{ticket_number}` | Get ticket with full conversation details |
| PATCH | `/api/tickets/{ticket_number}/status` | Update status (triggers auto-delete on resolve) |
| DELETE | `/api/tickets/{ticket_number}` | Permanently delete ticket + conversation |

### Developers
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/developers/` | List all developers with active/resolved stats |
| GET | `/api/developers/{id}` | Get developer detail + ticket history |
| PATCH | `/api/developers/{id}/status` | Update developer status (online/busy/offline) |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/admin/dashboard` | System overview (tickets, devs, conversations) |
| GET | `/api/admin/conversations` | List all conversations with status |
| GET | `/api/admin/developers` | Developer workload report |

### Auth
| Method | Endpoint | Description |
|---|---|---|
| GET | `/auth/google` | Redirect to Google OAuth consent screen |
| GET | `/auth/google/callback` | Google OAuth callback + session creation |

### Web Pages
| Path | Description |
|---|---|
| `/` | Home page |
| `/login` | Login (email or Google) |
| `/signup` | Sign up (email) |
| `/upload` | Voice recording + file upload |
| `/tickets` | Ticket list |
| `/tickets/{number}` | Ticket detail + chat |
| `/developers` | Developer team directory |
| `/dashboard` | Admin dashboard |
| `/documentation` | API reference |
| `/security` | Security info |
| `/about` | About page |
| `/support` | Support center |
| `/health` | Health check (JSON) |

---

## 🐛 Troubleshooting

### Transcription returns mock Japanese text
- Verify `GROQ_API_KEY` is set in `.env` and restart the server
- Check Railway logs for `[STT] Groq API ready` at startup
- Test key at [console.groq.com](https://console.groq.com)

### Login fails / wrong password error
- Accounts created before the pbkdf2_sha256 migration (March 2026) use a different hash — sign up again with a new account
- Railway must be redeployed with the latest commit

### Google OAuth fails on Railway
- Add `GOOGLE_REDIRECT_URI=https://your-app.up.railway.app/auth/google/callback` to Railway variables
- Add the same URL to Authorized Redirect URIs in Google Cloud Console

### Database column errors on Railway
- App runs `_migrate_add_missing_columns()` automatically on each startup — just trigger a redeploy

### Audio upload rejected
- Supported: WAV, MP3, M4A, WebM, OGG, MP4
- Max size: 50MB
- `storage/audio/` is auto-created on startup

---

## 🚢 Deploying to Railway

1. Push to GitHub
2. Create a Railway project → **Deploy from GitHub repo**
3. Optional: Add a **PostgreSQL** plugin for persistent data (without it, SQLite data resets on redeploy)
4. Set environment variables in Railway dashboard → Variables

| Variable | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `SECRET_KEY` | `openssl rand -hex 32` output |
| `DATABASE_URL` | Auto-set by Railway PostgreSQL plugin |
| `GOOGLE_CLIENT_ID` | From Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | From Google Cloud Console |
| `GOOGLE_REDIRECT_URI` | `https://your-app.up.railway.app/auth/google/callback` |
| `APP_BASE_URL` | `https://your-app.up.railway.app` |

Railway auto-detects `Procfile` and deploys. Build config is in `nixpacks.toml`.

---

## 📅 Version

**TechFixAI v1.1** — March 2026

| Version | Date | Changes |
|---|---|---|
| v1.1 | Mar 2026 | Switched to PBKDF2-SHA256 (no bcrypt limit), removed verification gate, Google OAuth stable, full code audit cleanup |
| v1.0 | Feb 2026 | Initial release: Groq STT/translation/tickets, deterministic assignment, Railway deployment |

---

**Built for multilingual technical support — bridging Japanese and English incident communications.**
