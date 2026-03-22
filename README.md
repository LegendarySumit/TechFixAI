<div align="center">

# 🎙️ TechFixAI

**Production-ready Voice-to-Ticket Incident Platform**

![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.11-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?logo=railway&logoColor=white)
![Jinja2](https://img.shields.io/badge/Jinja2-B41717?logo=jinja&logoColor=white)

*Japanese Voice Capture • AI Transcription & Translation • Smart Ticket Generation • Deterministic Dev Assignment*

[Live Demo](#) • [Features](#-features) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack)

</div>

---

## 📖 About

**TechFixAI** is a production-grade incident management platform that bridges the language gap in Japanese software teams. It captures voice-recorded incident reports in Japanese, transcribes and translates them using Groq Whisper with technical context awareness, and automatically generates structured support tickets — all in one seamless background pipeline.

The platform goes beyond simple transcription. After a voice report is submitted, TechFixAI deterministically assigns the right developer based on incident type and severity — no random shuffling, no manual triage. Built on FastAPI with SQLAlchemy and Jinja2-rendered pages, it supports SQLite locally and PostgreSQL in production on Railway.

TechFixAI ships production-ready: full auth with Google OAuth, rate limiting, CAPTCHA, security headers, structured logging, Sentry integration, and Prometheus metrics — all configured and ready to deploy.

---

## ✨ Features

- ✅ Voice upload pipeline — Audio → STT → Translation → Ticket → Assignment as a background task
- ✅ Japanese-to-English translation with technical context awareness
- ✅ Deterministic developer assignment by incident type and severity
- ✅ Chat voice helper — transcribe and translate without creating a ticket
- ✅ Full auth system — email/password + Google OAuth + secure session cookies
- ✅ CAPTCHA support on login and signup (Cloudflare Turnstile style)
- ✅ Granular rate limiting for global traffic, auth, uploads, and translation
- ✅ Admin dashboard with aggregated stats, conversations, and developer metrics
- ✅ Health and Prometheus metrics endpoints
- ✅ Structured logging with request IDs and sensitive value redaction
- ✅ Security headers, HTTPS enforcement, CORS validation, brute-force lockout
- ✅ Optional Sentry integration for error tracking and tracing

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — Core web framework and API routing
- **SQLAlchemy** — ORM and database abstraction
- **Starlette** — Middleware (request ID, security headers, rate limiting)
- **Jinja2** — Server-rendered HTML templates
- **Uvicorn** — ASGI server

### Database
- **SQLite** — Local development default
- **PostgreSQL** — Production via `DATABASE_URL`

### AI Services
- **Groq Whisper** — Primary speech-to-text transcription
- **OpenAI** — Optional fallback
- **Gemini** — Optional fallback

### Infrastructure & Auth
- **Railway** — Deployment target
- **Google OAuth 2.0** — Social login
- **Sentry** — Optional error tracking and tracing
- **Prometheus** — Optional metrics scraping

---

## 📁 Project Structure

```
TechFixAI/
├── app/
│   ├── main.py                  # App entry point, route registration
│   ├── models/                  # SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py              # Login, signup, logout, Google OAuth
│   │   ├── voice.py             # Voice upload, chat-transcribe, status
│   │   ├── tickets.py           # Ticket CRUD and status management
│   │   ├── admin.py             # Dashboard, conversations, developers
│   │   └── pages.py             # Jinja2 page routes
│   ├── services/
│   │   ├── stt.py               # Groq Whisper STT integration
│   │   ├── translation.py       # Technical-context translation
│   │   ├── ticket_generator.py  # Ticket structuring logic
│   │   └── assignment.py        # Deterministic developer assignment
│   ├── middleware/
│   │   ├── rate_limit.py        # Route-specific rate limiters
│   │   ├── request_id.py        # Request ID injection
│   │   └── security.py          # Security headers, HTTPS enforcement
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── upload.html
│   │   ├── dashboard.html
│   │   ├── tickets.html
│   │   └── developers.html
│   └── config.py                # Settings and env variable validation
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── secret-hygiene.yml
│       └── uptime-checks.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/LegendarySumit/TechFixAI.git
cd TechFixAI

# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload
```

Open → [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## ⚙️ Configuration

### Required in Production

```env
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://...
CORS_ORIGINS=https://your-frontend.vercel.app
```

### Common Production Variables

```env
PUBLIC_DEPLOYMENT=true
FORCE_HTTPS=true
SESSION_COOKIE_SECURE=true
APP_BASE_URL=https://your-backend-domain.railway.app
ADMIN_EMAILS=admin@example.com,other@example.com
```

### AI Service Keys

```env
GROQ_API_KEY=your_groq_key        # Required
OPENAI_API_KEY=your_openai_key    # Optional fallback
GEMINI_API_KEY=your_gemini_key    # Optional fallback
```

### Google OAuth

```env
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=https://your-backend-domain.railway.app/auth/google/callback
```

### SMTP (Optional)

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=your_password
FROM_EMAIL=noreply@example.com
```

> ⚠️ `APP_BASE_URL` must point to the **backend** URL. `CORS_ORIGINS` must contain **frontend** origin(s). No trailing slashes.

---

## 📚 Usage

1. **Sign up or log in** at `/signup` or `/login` — Google OAuth available
2. **Upload a voice report** at `/upload` — select a Japanese audio file and submit
3. The pipeline runs in the background: transcription → translation → ticket → assignment
4. **Track tickets** at `/tickets` — click any ticket for full detail
5. **Chat transcription** — use the voice helper to transcribe without creating a ticket
6. **Admin dashboard** at `/dashboard` — stats, developer workload, conversation logs

---

## 🔌 API Endpoints

### Voice

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/voice/upload` | Upload audio, start pipeline |
| `POST` | `/api/voice/chat-transcribe` | STT + translation only, no ticket |
| `GET` | `/api/voice/status/{conversation_id}` | Poll processing status |

### Tickets

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/tickets` | List tickets with filters |
| `GET` | `/api/tickets/{ticket_number}` | Ticket detail |
| `PATCH` | `/api/tickets/{ticket_number}/status` | Update status (admin) |
| `DELETE` | `/api/tickets/{ticket_number}` | Delete ticket (owner or admin) |

### Admin

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/dashboard` | Aggregated stats (auth required) |
| `GET` | `/api/admin/conversations` | Conversation list (auth required) |
| `GET` | `/api/admin/developers` | Developer stats (auth required) |

### Auth & Observability

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/auth/google` | Initiate Google OAuth |
| `GET` | `/auth/google/callback` | OAuth callback |
| `GET` | `/health` | Health check (`200` healthy, `503` degraded) |
| `GET` | `/metrics` | Prometheus metrics (when enabled) |

---

## 🧠 Deterministic Assignment Rules

Assignment is fully rule-based — no randomness:

1. **Backend/infrastructure** + high or critical → Backend team
2. **Frontend/UI** incident → Frontend team
3. **Database** + high or critical → Backend team
4. **Fallback** → Least loaded developer

---

## 🐛 Troubleshooting

**Startup fails during settings load?**
- Verify `CORS_ORIGINS` is not empty and uses a valid format
- Ensure `APP_BASE_URL` points to the backend domain, not the frontend
- Confirm `DATABASE_URL` is a valid PostgreSQL connection string

**Voice upload not processing?**
- Check that `GROQ_API_KEY` is set and valid
- Poll `/api/voice/status/{conversation_id}` for pipeline progress

**Google OAuth failing?**
- Ensure `GOOGLE_REDIRECT_URI` matches exactly what's registered in Google Cloud Console

---

## 🔮 Future Enhancements

- [ ] Multi-language support beyond Japanese
- [ ] Slack / Teams notifications on ticket creation
- [ ] SLA tracking and breach alerts
- [ ] ML-based developer assignment
- [ ] Mobile app for on-the-go voice reporting
- [ ] Webhook support for external integrations
- [ ] Role-based access control (RBAC) for teams

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 👨‍💻 Author

**LegendarySumit**

- GitHub: [@LegendarySumit](https://github.com/LegendarySumit)
- Project: [TechFixAI](https://github.com/LegendarySumit/TechFixAI)
- Live Demo: [https://techfixai.up.railway.app/](https://techfixai.up.railway.app/)

---

<div align="center">

**🎙️ From voice to resolved — no translation lost.**

*TechFixAI · Built for Japanese engineering teams*

---

**⭐ Star this repo if you find it helpful!**

</div>
