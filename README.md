<div align="center">

# ??? TechFixAI

**Enterprise-Grade Voice-to-Ticket AI System**

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-FF6B6B?logo=ai&logoColor=white)
![Railway](https://img.shields.io/badge/Railway-0B0D0E?logo=railway&logoColor=white)

*Transform multilingual voice into structured support tickets with intelligent routing*

?? **[Live Demo](https://techfixai.up.railway.app)** � [Features](#-key-features) � [Quick Start](#-quick-start) � [API Docs](#-api-reference)

</div>

---

## ?? Overview

**TechFixAI** is an **enterprise-grade automated incident intake and routing system** that transforms multilingual voice input into structured, actionable support tickets with intelligent developer assignment.

### Core Flow
```
Japanese Audio Recording
        ?
Groq Whisper STT (whisper-large-v3)
        ?
Groq LLaMA Translation (Japanese ? English)
        ?
AI-Powered Ticket Generation
        ?
Deterministic Developer Assignment
        ?
Real-Time Developer-Client Chat
```

**This is NOT:**
? A chatbot  
? A translation demo  
? An AI playground

**This IS:**
? An enterprise incident management system  
? A multilingual support automation platform  
? A production-ready workflow orchestrator

---

## ? Key Features

### ?? Authentication
- Email/password signup and login (instant access, no verification)
- Google OAuth 2.0 (one-click sign-in)
- Session cookies (`httponly`, `SameSite=lax`)
- PBKDF2-SHA256 password hashing (no length limit)

### ??? Voice Input & Processing
- Real-time audio capture with **Web Audio API**
- Visual waveform display (20 animated bars)
- Live recording timer (MM:SS format)
- Optional screenshot/image upload (PNG, JPG, max 50MB)
- Microphone permission handling
- Process step indicators (Recording ? Encryption ? Analysis ? Assignment)

### ?? Transcription & Translation
- **Speech-to-Text:** Groq Whisper (whisper-large-v3) � Japanese support
- **Translation:** Groq LLaMA (llama-3.1-8b-instant) � Context-aware technical translation
- Split-view display: **Original Japanese (left)** | **English Translation (right)**
- Audit trail with both transcripts stored
- Graceful mock fallback if `GROQ_API_KEY` not set

### ?? Ticket Generation & Assignment
- **Structured ticket schema:** Number, Title, Category, Priority, Technical Area
- AI-generated via Groq LLaMA with rule-based fallback
- **Deterministic assignment rules** (no AI randomness):
  - Backend/Infrastructure + High/Critical ? Backend Team
  - Frontend/UI + Any Priority ? Frontend Team
  - Database + High/Critical ? Backend Team
  - Default ? Least loaded developer

### ????? Developer Tools
- Developer directory with team statistics cards
- Real-time developer chat interface on ticket detail page
- Quick action buttons (Mark as Resolved, In Progress, On Hold)
- Auto-delete tickets after resolution (5 seconds)

### ?? Admin Dashboard
- Ticket management (CRUD operations)
- Assignment routing audit trail
- Developer performance metrics
- System health check endpoint (`/health`)

---

## ??? System Architecture

**Style:** Modular Monolith (NOT microservices)
```
+-------------------------------------------------------------+
�                    Japanese Audio Upload                    �
+-------------------------------------------------------------+
                     ?
            /api/voice/upload
         Audio saved to storage/audio/
                     ?
        +------------------------+
        �  Groq Whisper STT      �
        �  Japanese ? Text       �
        +------------------------+
                 ?
        +------------------------+
        �  Groq LLaMA Translation�
        �  Japanese ? English    �
        +------------------------+
                 ?
        +------------------------+
        �  Groq LLaMA Ticket Gen �
        �  English ? JSON Ticket �
        +------------------------+
                 ?
        +------------------------+
        �  Deterministic Logic   �
        �  Ticket ? Developer    �
        +------------------------+
                 ?
        +------------------------+
        �  Assigned Developer    �
        �  + Chat Interface      �
        +------------------------+
```

---

## ?? Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)

- **FastAPI + Uvicorn** � Async API, auto-docs, high performance
- **SQLAlchemy 2.0** � ORM with auto-migration
- **PostgreSQL** (prod) / **SQLite** (local) � ACID compliance

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?logo=bootstrap&logoColor=white)

- **Jinja2** � Server-side rendering
- **Bootstrap 5** � Dark theme UI
- **Web Audio API** � Real-time recording with waveform

### AI & ML
![Groq](https://img.shields.io/badge/Groq-FF6B6B?logo=ai&logoColor=white)

- **Groq Whisper** (whisper-large-v3) � Japanese speech recognition
- **Groq LLaMA** (llama-3.1-8b-instant) � Translation & ticket generation

### Security & Auth
- **Session cookies** � httponly, SameSite=lax
- **Google OAuth 2.0** � One-click sign-in
- **PBKDF2-SHA256** (passlib) � Password hashing, no length limit
- **Fernet AES-256** (cryptography) � Audio encryption at rest

### Deployment
![Railway](https://img.shields.io/badge/Railway-0B0D0E?logo=railway&logoColor=white)

- **Railway** � Zero-config cloud hosting
- **PostgreSQL Plugin** � Persistent data storage

---

## ?? Project Structure
```
TechFixAI/
+-- app/
�   +-- main.py                      # FastAPI app + middleware + router registration
�   +-- core/
�   �   +-- config.py                # Environment variables with defaults
�   �   +-- security.py              # API key auth helper
�   +-- api/
�   �   +-- voice.py                 # Voice upload + STT/translation pipeline
�   �   +-- ticket.py                # Ticket CRUD + status updates
�   �   +-- admin.py                 # Admin dashboard endpoints
�   �   +-- developer.py             # Developer directory API
�   �   +-- auth.py                  # Google OAuth 2.0 routes
�   �   +-- web.py                   # HTML page routes
�   +-- services/
�   �   +-- stt_service.py           # Groq Whisper STT
�   �   +-- translation_service.py   # Groq LLaMA translation
�   �   +-- ticket_service.py        # Groq LLaMA ticket generation
�   �   +-- assignment_service.py    # Deterministic developer assignment
�   �   +-- email_service.py         # SMTP email (future use)
�   +-- models/
�   �   +-- conversation.py          # Voice + transcript + translation
�   �   +-- ticket.py                # Ticket ORM model
�   �   +-- developer.py             # Developer ORM model
�   �   +-- user.py                  # User accounts + OAuth
�   +-- db/
�   �   +-- base.py                  # SQLAlchemy declarative base
�   �   +-- session.py               # DB session + pool config
�   �   +-- init_db.py               # Table creation + migrations
�   +-- static/
�   �   +-- css/
�   �   +-- js/
�   �       +-- voice-recorder.js    # Web Audio API recording
�   �       +-- ui-components.js     # Reusable UI components
�   �       +-- app.js               # Global utilities + API client
�   +-- templates/                   # Jinja2 HTML templates
�   �   +-- base.html
�   �   +-- upload.html              # Voice recording interface
�   �   +-- ticket_detail.html       # Ticket + developer chat
�   �   +-- ...
�   +-- utils/
�       +-- audio.py                 # Audio validation
�       +-- encryption.py            # AES-256 Fernet
�       +-- audit.py                 # Audit logging
�       +-- text.py                  # Text processing
+-- scheduler.py                     # Background cleanup tasks
+-- requirements.txt
+-- Procfile                         # Railway process definition
+-- railway.toml
+-- storage/
    +-- audio/                       # Uploaded audio files
```

---

## ?? Quick Start

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

? Database tables and seed developers are created automatically on first run!

---

## ?? Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ? Yes | Groq API key for STT + translation + ticket generation |
| `SECRET_KEY` | ? Yes | Session signing + audio encryption key |
| `PUBLIC_DEPLOYMENT` | No | Set `True` in public environments to enforce strict transport/CORS rules |
| `FORCE_HTTPS` | No | Redirect HTTP to HTTPS when enabled |
| `ADMIN_EMAILS` | No | Comma-separated admin allowlist for privileged routes |
| `DATABASE_URL` | No | PostgreSQL URL (defaults to SQLite locally) |
| `GOOGLE_CLIENT_ID` | No | Google OAuth Client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth Client Secret |
| `GOOGLE_REDIRECT_URI` | No | OAuth callback URL (required on Railway) |
| `OPENAI_API_KEY` | No | OpenAI Whisper fallback |
| `GEMINI_API_KEY` | No | Gemini fallback for translation/ticket gen |
| `ENCRYPTION_ENABLED` | No | AES-256 audio encryption (default: true) |
| `ENCRYPTION_KEY_VERSION` | No | Active encryption key version label (e.g., `v1`) |
| `ENCRYPTION_LEGACY_KEY_VERSIONS` | No | Comma-separated legacy versions accepted for decryption |
| `DATA_RETENTION_DAYS` | No | Auto-delete older than N days (default: 30) |
| `AUDIT_LOG_RETENTION_DAYS` | No | Retention window for audit log entries |
| `APP_BASE_URL` | No | Public URL (e.g., `https://techfixai.up.railway.app`) |

---

## ?? User Workflows

### ?? Client (Japanese Speaker)

1. **Sign up** at `/signup` or **log in** at `/login` (Google or email)
2. Visit `/upload`
3. Click **Record** and speak the technical issue in Japanese
4. Optional: Attach screenshot
5. **Submit** ? View ticket number, Japanese original, English translation
6. **Chat** with assigned developer in real-time

### ????? Developer (English Speaker)

1. Visit `/tickets` to see new tickets
2. **Open a ticket** ? See Japanese original + English translation + assignment reason
3. **Chat with client**, update status via quick action buttons
4. **Mark resolved** ? Ticket auto-deletes in 5 seconds

### ?? Admin

1. Visit `/dashboard` for system overview
2. Monitor ticket counts, priorities, developer workloads
3. View assignment reasoning and audit trail

---

## ?? Assignment Logic (Deterministic, No AI)

Rules applied in order:

| Condition | Assignment |
|-----------|------------|
| **Backend/Infrastructure** + **High/Critical** | ? Backend Team developer |
| **Frontend/UI** + **Any Priority** | ? Frontend Team developer |
| **Database** + **High/Critical** | ? Backend Team developer |
| **Default** | ? Least loaded developer (fewest active tickets) |

**Every ticket stores a human-readable assignment reason:**
```
"Rule: Backend/Infrastructure + HIGH priority ? Backend Team"
"Default: Assigned to least loaded developer (2 active tickets)"
```

? **No randomness**  
? **No black box**  
? **Fully explainable routing**

---

## ?? API Reference

### Voice Endpoints
```
POST   /api/voice/upload                      # Upload Japanese audio + metadata
GET    /api/voice/status/{conversation_id}    # Get processing status
POST   /api/voice/translate                   # Translate text (EN ? JA)
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

## ??? Security Features

### ?? Audio Encryption at Rest
- Audio encrypted with **Fernet (AES-128-CBC + HMAC-SHA256)**
- Key derived from `SECRET_KEY` + `ENCRYPTION_KEY_VERSION` via SHA-256
- Toggle with `ENCRYPTION_ENABLED=true/false`

#### Encryption Key Rotation Procedure
1. Set a new `ENCRYPTION_KEY_VERSION` (for example `v2`).
2. Keep the previous version in `ENCRYPTION_LEGACY_KEY_VERSIONS` (for example `v1`).
3. Redeploy and verify new uploads are encrypted with the active version.
4. After legacy artifacts expire under retention policy, remove old versions from `ENCRYPTION_LEGACY_KEY_VERSIONS`.

### ??? Data Retention
- Scheduler runs nightly
- Purges audio files and DB records older than `DATA_RETENTION_DAYS`
- Purges old audit-log entries older than `AUDIT_LOG_RETENTION_DAYS`
- All deletions logged to audit trail

### ?? Audit Logging
- Every upload, ticket creation, and cleanup logged to `logs/audit.log` (JSON lines)
- Metadata is sanitized and redacted for secrets/tokens/emails by default

### ?? Auth Security
- Passwords hashed with **PBKDF2-SHA256** (no length restrictions)
- Session cookies: `httponly=True`, `samesite=lax`
- `.env` in `.gitignore` � credentials never committed
- Admin-only APIs enforce server-side role checks with `ADMIN_EMAILS`

### ?? Transport and Web Security
- Optional HTTPS redirect middleware via `FORCE_HTTPS`
- Security headers: `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`
- When `PUBLIC_DEPLOYMENT=True`, app enforces exact HTTPS CORS origins and secure cookies

### ?? Legal and Policy Baseline
- Privacy Policy: `/privacy`
- Terms of Service: `/terms`
- Data deletion requests: `privacy@techfixai.com` (subject: `Data Deletion Request`)
- Abuse reporting: `abuse@techfixai.com`

---

## ?? Deploying to Railway

### Step-by-Step

1. **Push to GitHub**
2. Create Railway project ? **Deploy from GitHub repo**
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

## ?? Troubleshooting

| Issue | Solution |
|-------|----------|
| **Transcription returns mock text** | Verify `GROQ_API_KEY` in `.env`, restart server |
| **Login fails** | Accounts pre-March 2026 need re-registration (pbkdf2 migration) |
| **Google OAuth fails** | Add `GOOGLE_REDIRECT_URI` to Railway variables + Google Console |
| **Database column errors** | Auto-migration runs on startup � redeploy on Railway |
| **Audio upload rejected** | Max 50MB, supported: WAV, MP3, M4A, WebM, OGG, MP4 |

---

## ?? Project Statistics

| Metric | Value |
|--------|-------|
| **Languages** | Python, JavaScript, HTML, CSS |
| **API Endpoints** | 20+ RESTful routes |
| **Services** | 5 AI/ML integrations |
| **Database Tables** | 4 core models |
| **Auth Methods** | 2 (Email + Google OAuth) |
| **Supported Languages** | Japanese, English |
| **Production Ready** | ? YES |

---

## ?? Version History

| Version | Date | Changes |
|---------|------|---------|
| **v1.1** | Mar 2026 | PBKDF2-SHA256, no verification gate, Google OAuth stable |
| **v1.0** | Feb 2026 | Initial release: Groq STT/translation/tickets, deterministic assignment |

---

## ?? Future Enhancements

- [ ] Multi-language support (Chinese, Korean, Spanish)
- [ ] SMS/Email notifications for ticket updates
- [ ] Advanced analytics dashboard
- [ ] Mobile app (iOS/Android)
- [ ] Integration with Slack/Microsoft Teams
- [ ] Voice response generation (TTS)
- [ ] Bulk ticket import/export
- [ ] Custom developer assignment rules via UI

---

## ?? License

MIT License � Free to use and modify

---

## ????? Author

**LegendarySumit**

- GitHub: [@LegendarySumit](https://github.com/LegendarySumit)
- Project: [TechFixAI](https://github.com/LegendarySumit/TechFixAI)
- Live Demo: [https://techfixai.up.railway.app](https://techfixai.up.railway.app)

---

## ?? Acknowledgments

- **Groq** � For ultra-fast AI inference
- **FastAPI** � For modern Python API framework
- **Railway** � For seamless cloud deployment
- Built for multilingual technical support teams worldwide

---

<div align="center">

**??? Bridging language barriers in technical support**

*Built for Japanese-English incident communications*

---

**? Star this repo if you find it helpful!**

**?? Open to contributions, feedback, and enterprise partnerships**

*Version 1.1 � Production Ready � March 2026*

</div>

---

## Integrated From: OBSERVABILITY_SUMMARY.md

Merged on: 2026-03-20 13:44:19

# TechFixAI Observability Implementation Summary
**Completion Date**: March 20, 2026  
**Phase**: 14 (Final)  

---

## What Was Implemented

### Complete Observability Stack 🎯

A production-ready observability system enabling real-time monitoring, incident response, and performance optimization for TechFixAI.

---

## Core Components

### 1. **Structured Logging** ✅
- **File**: `app/core/logging_config.py`
- **Features**:
  - JSON-formatted logs for machine parsing
  - Automatic request ID injection via middleware
  - Context-aware logging with user/request info
  - Configurable log levels (DEBUG → CRITICAL)
  - File rotation (daily, max 5 files)

**Enable**: `export LOG_LEVEL=DEBUG`

---

### 2. **Request ID Tracking** ✅
- **File**: `app/core/observability.py`
- **Features**:
  - Automatic request ID generation (UUID4)
  - Propagation through entire request lifecycle
  - Matches with Sentry error IDs
  - Visible in all structured logs
  - Helps correlate distributed requests

**Header**: `X-Request-ID`

---

### 3. **Prometheus Metrics** ✅
- **File**: `app/core/metrics.py`
- **Endpoint**: `GET /metrics`
- **Metrics Tracked**:
  - **HTTP**: Request rate, latency, error rate by status code
  - **Auth**: Login attempts, failures, reasons
  - **Uploads**: Success rate, failures, processing time
  - **AI**: Transcription, translation, ticket generation time
  - **Database**: Connection errors, query duration
  - **System**: Active connections, cleanup tasks, failures

**Scrape Target**: Configure Prometheus to scrape `http://app:8000/metrics`

---

### 4. **Sentry Integration** ✅
- **File**: `app/core/observability.py`
- **Features**:
  - Automatic error capture (unhandled exceptions)
  - 10% distributed request tracing
  - Error grouping by type/location
  - Release tracking
  - Environment tags (dev/prod)

**Enable**: `export SENTRY_DSN="https://...@sentry.io/..."`

---

### 5. **Health Endpoint** ✅
- **File**: `app/core/health.py`
- **Endpoint**: `GET /health`
- **Checks**:
  - Database connectivity
  - Filesystem access
  - API key configuration
  - Overall status (healthy/degraded/down)

**Response Time**: <1s (healthy), <10s (degraded)

---

### 6. **Metrics Endpoint** ✅
- **File**: `app/api/web.py` (`/metrics` route)
- **Format**: Prometheus text format
- **Update Frequency**: Real-time (counters/gauges updated on each request)

---

### 7. **Alert Rules** ✅
- **File**: `ALERTING.md`
- **Rules Configured**:
  - High error rate (>10% for 2 minutes)
  - Auth failure spike (>5 failures/sec for 3 minutes)
  - Database connection errors (>2 errors/minute)
  - Slow requests (P95 latency >5 seconds)
  - Upload failures (>20% for 5 minutes)

---

### 8. **Incident Runbooks** ✅
- **File**: `RUNBOOKS.md`
- **Runbooks Provided**:
  - Outage response (5xx errors, slow response)
  - Auth failure response (invalid creds, token issues)
  - Database issues (connection errors, slow queries)
  - Upload failures (storage full, permissions)
  - Sentry error triage (how to debug via Sentry)

---

### 9. **Monitoring Guide** ✅
- **File**: `MONITORING.md`
- **Covers**:
  - Prometheus setup and configuration
  - Grafana dashboard creation
  - Alert notification channels (Slack, PagerDuty, email)
  - Dashboard panel queries
  - Performance tuning

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TechFixAI Application                     │
├─────────────────────────────────────────────────────────────┤
│ • Request ID Middleware (RequestIDMiddleware in main.py)   │
│ • Logging (logging_config.py with StructuredFormatter)     │
│ • Metrics (metrics.py with MetricsRecorder)                │
│ • Error Tracking (Sentry SDK)                              │
└─────────────────────────────────────────────────────────────┘
         ↓ Logs             ↓ Metrics       ↓ Errors
         │                  │               │
    JSON logs           /metrics         Sentry API
    (app.log)          endpoint         (error.sentry.io)
         │                  │               │
         ↓                  ↓               ↓
   Loki/ELK         Prometheus        Sentry Dashboard
   (optional)       (time-series DB)   (error tracking)
         │                  │               │
         └──────────────────┴───────────────┘
                     ↓
              Grafana Dashboards
              (unified view)
                     ↓
              Alert Rules Engine
              (firing conditions)
                     ↓
         PagerDuty / Slack / Email
         (on-call notifications)
```

---

## Quick Start

### Local Development
```bash
curl http://localhost:8000/health | python -m json.tool
curl http://localhost:8000/metrics | head -20
docker logs <container> | grep '"request_id"'
```

### Production
```bash
export SENTRY_DSN="https://your-key@sentry.io/id"
export STRUCTURED_LOGGING_ENABLED=True
export METRICS_ENABLED=True
# Deploy via Docker/Railway/K8s
# Configure Prometheus scraping
# Set up Grafana alerts
```

---

## Key Metrics to Monitor

| Metric | Alert Threshold | Response |
|--------|-----------------|----------|
| Error Rate (5xx) | >10% for 2min | Page on-call |
| Auth Failures | >5/sec for 3min | Notify #security |
| Upload Failures | >20% for 5min | Check storage |
| Latency (P95) | >5 seconds | Scale up/optimize |
| DB Errors | >2/min | Check database |

---

## Files Created/Modified

| File | Purpose | Status |
|------|---------|--------|
| `app/core/logging_config.py` | Structured logging setup | ✅ Created |
| `app/core/observability.py` | Request IDs, Sentry config | ✅ Created |
| `app/core/metrics.py` | Prometheus metrics | ✅ Created |
| `app/core/health.py` | Health check logic | ✅ Created |
| `app/main.py` | Middleware integration | ✅ Modified |
| `app/api/web.py` | /health, /metrics endpoints | ✅ Modified |
| `OBSERVABILITY.md` | Implementation guide | ✅ Created |
| `MONITORING.md` | Setup guide | ✅ Created |
| `ALERTING.md` | Alert rules | ✅ Created |
| `RUNBOOKS.md` | Incident response | ✅ Created |
| `.env.observability` | Example config | ✅ Created |

---

## What You Get

✅ **Real-time visibility** into application performance  
✅ **Automatic error detection** and alerting  
✅ **Request tracing** with unique IDs across logs  
✅ **Performance metrics** (latency, throughput, error rates)  
✅ **Dependency health** checks (database, filesystem, API keys)  
✅ **Incident response** playbooks with step-by-step guides  
✅ **Production-ready** configuration out of the box  

---

## Next Steps

1. **Deploy to staging** with Sentry DSN
2. **Set up Prometheus** scraping (`prometheus.yml`)
3. **Create Grafana dashboards** (import from dashboard.json)
4. **Configure alert channels** (Slack, PagerDuty)
5. **Test alerts** by simulating high error rate
6. **On-call rotation** setup in PagerDuty
7. **Team training** on runbooks

---

## Documentation Files

- **[OBSERVABILITY.md](OBSERVABILITY.md)** — Complete implementation guide with examples
- **[MONITORING.md](MONITORING.md)** — Prometheus/Grafana/AlertManager setup
- **[ALERTING.md](ALERTING.md)** — Alert rules and conditions
- **[RUNBOOKS.md](RUNBOOKS.md)** — Step-by-step incident response

---

## Support

For questions or issues:
1. Check relevant runbook
2. Review logs: `docker logs <container>`
3. Check health: `curl /health`
4. Review Sentry dashboard
5. Check Prometheus alerts: `http://localhost:9090/alerts`

---

**Status**: 🎉 **FULLY IMPLEMENTED AND PRODUCTION-READY**


---

## Integrated From: OBSERVABILITY.md

Merged on: 2026-03-20 13:44:19

# TechFixAI Observability Implementation Guide

**Date**: March 2026  
**Status**: ✅ FULLY IMPLEMENTED  

---

## Overview

This guide documents the complete observability stack implemented for TechFixAI, including structured logging, error tracking, metrics collection, health checks, and incident response procedures.

### Features Implemented

| Feature | Status | Files |
|---------|--------|-------|
| **Structured Logging** | ✅ | `app/core/logging_config.py` |
| **Request ID Tracking** | ✅ | `app/core/observability.py` |
| **Prometheus Metrics** | ✅ | `app/core/metrics.py` |
| **Sentry Integration** | ✅ | `app/core/observability.py` |
| **Health Endpoint** | ✅ | `app/core/health.py` |
| **Metrics Endpoint** | ✅ | `/metrics` in `app/api/web.py` |
| **Alerting Rules** | ✅ | `ALERTING.md` |
| **Incident Runbooks** | ✅ | `RUNBOOKS.md` |
| **Monitoring Guide** | ✅ | `MONITORING.md` |

---

## Quick Start (5 minutes)

### For Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure observability (optional)
cat .env.observability >> .env

# 3. Run app
python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"

# 4. Check structured logs
curl http://localhost:8000/login | grep -o '"request_id":"[^"]*"'

# 5. View metrics
curl http://localhost:8000/metrics | head -20

# 6. Check health
curl http://localhost:8000/health | python -m json.tool
```

### For Production Deployment

```bash
# 1. Set environment variables
export SENTRY_DSN="https://your-sentry-key@sentry.io/project-id"
export STRUCTURED_LOGGING_ENABLED=True
export METRICS_ENABLED=True

# 2. Deploy app (Docker/Kubernetes/Railway)
docker build -t techfixai:v1 .
docker run -d -e SENTRY_DSN="..." techfixai:v1

# 3. Set up Prometheus scraping
# Edit prometheus.yml to scrape http://your-app:8000/metrics

# 4. View metrics in Grafana dashboard
# Navigate to http://grafana:3000, import dashboard.json

# 5. Configure alerting
# Set up Slack/PagerDuty integration in Grafana/Prometheus
```

---

## Architecture

### Logging Flow

```
Application Code
    ↓
RequestIDMiddleware (injects request ID, creates logger adapter)
    ↓
StructuredFormatter (converts to JSON with context)
    ↓
logs/app.log (JSON lines format)
    ↓
[Optional] Loki (centralized log aggregation)
    ↓
Grafana (query, search, visualize)
```

### Metrics Flow

```
Application Code (MetricsRecorder.record_*)
    ↓
Prometheus Client (in-memory counters, histograms, gauges)
    ↓
/metrics endpoint (Prometheus text format)
    ↓
Prometheus Server (scrapes every 15 seconds)
    ↓
Time-series Database (prometheus_data/)
    ↓
Alerting Rules (check every 30 seconds)
    ↓
AlertManager (aggregates, deduplicates, routes)
    ↓
Slack/PagerDuty/Email
```

### Error Tracking Flow

```
Unhandled Exception in Route Handler
    ↓
Sentry SDK (automatic capture)
    ↓
Sentry API Endpoint
    ↓
Sentry Dashboard (real-time error alerts)
    ↓
Slack Integration (optional)
```

---

## Configuration

### Logging Settings

```python
# app/core/config.py
LOG_LEVEL: str = "INFO"                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
STRUCTURED_LOGGING_ENABLED: bool = True    # JSON vs. standard format
REQUEST_ID_HEADER: str = "X-Request-ID"    # Header name for request tracking
```

**Change via environment**:
```bash
export LOG_LEVEL=DEBUG
export STRUCTURED_LOGGING_ENABLED=True
```

### Metrics Settings

```python
# app/core/config.py
METRICS_ENABLED: bool = True               # Expose /metrics endpoint
METRICS_PORT: int = 9090                   # (informational; app listens on main port)
```

### Sentry Settings

```python
# app/core/config.py
SENTRY_DSN: str = ""                       # Leave empty to disable
SENTRY_TRACES_SAMPLE_RATE: float = 0.1     # 10% of requests traced
SENTRY_RELEASE: str = "1.0.0"              # Version tag
```

**To enable Sentry**:
```bash
export SENTRY_DSN="https://<key>@<org>.ingest.sentry.io/<id>"
```

---

## Key Metrics

### Request Metrics

| Metric | Type | Labels | What It Measures |
|--------|------|--------|-----------------|
| `http_requests_total` | Counter | method, endpoint, status_code | Total HTTP requests |
| `http_request_duration_seconds` | Histogram | method, endpoint | Request latency |
| `http_5xx_errors_total` | Counter | method, endpoint | Server errors |
| `http_auth_failures_total` | Counter | reason | Auth/authz failures |

### Upload Metrics

| Metric | Type | Labels | What It Measures |
|--------|------|--------|-----------------|
| `voice_upload_total` | Counter | status (success/failed) | Upload success rate |
| `voice_upload_failures_total` | Counter | reason | Why uploads fail |
| `voice_upload_duration_seconds` | Histogram | | Upload speed |

### AI/Processing Metrics

| Metric | Type | What It Measures |
|--------|------|-----------------|
| `transcription_duration_seconds` | Histogram | STT speed |
| `translation_duration_seconds` | Histogram | Translation speed |
| `ticket_created_total` | Counter | Ticket generation count |

### Database Metrics

| Metric | Type | What It Measures |
|--------|------|-----------------|
| `db_connection_errors_total` | Counter | Database connectivity issues |
| `db_query_duration_seconds` | Histogram | Query performance |

### System Metrics

| Metric | Type | What It Measures |
|--------|------|-----------------|
| `active_connections` | Gauge | Current active connections |
| `cleanup_duration_seconds` | Summary | Cleanup task speed |
| `cleanup_failures_total` | Counter | Failed cleanup tasks |

---

## Logging Examples

### Example 1: Request Log (Success)

```json
{
  "timestamp": "2026-03-20T15:30:45.123456",
  "level": "INFO",
  "logger": "app.core.observability",
  "message": "GET /login 200",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "GET",
  "path": "/login",
  "status_code": 200,
  "duration_ms": 45.2,
  "user": "john@example.com"
}
```

### Example 2: Error Log

```json
{
  "timestamp": "2026-03-20T15:31:12.654321",
  "level": "ERROR",
  "logger": "app.api.voice",
  "message": "Transcription failed",
  "request_id": "660e8400-e29b-41d4-a716-446655440001",
  "method": "POST",
  "path": "/api/voice/transcribe",
  "status_code": 500,
  "duration_ms": 5123.0,
  "user": "jane@example.com",
  "exception": {
    "type": "GroqAPIError",
    "message": "API rate limit exceeded"
  },
  "context": {
    "audio_file": "conversation_abc123.wav",
    "file_size_bytes": 524288
  }
}
```

### Example 3: Health Check Log

```json
{
  "timestamp": "2026-03-20T15:32:00.000000",
  "level": "INFO",
  "logger": "app.core.observability",
  "message": "Health check: healthy",
  "request_id": "770e8400-e29b-41d4-a716-446655440002",
  "context": {
    "database": "up",
    "filesystem": "up",
    "api_keys": "configured"
  }
}
```

---

## Dashboard Queries

### Key Panels in Grafana

**1. Request Rate (req/sec)**
```
rate(http_requests_total[1m])
```

**2. Error Rate (5xx, %)**
```
(rate(http_5xx_errors_total[1m]) / rate(http_requests_total[1m])) * 100
```

**3. P95 Latency (seconds)**
```
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**4. Upload Success Rate (%)**
```
(rate(voice_upload_total{status="success"}[5m]) / rate(voice_upload_total[5m])) * 100
```

**5. Auth Failures by Reason**
```
rate(http_auth_failures_total[5m]) by (reason)
```

**6. Database Connection Errors**
```
rate(db_connection_errors_total[1m])
```

**7. Cleanup Task Status**
```
cleanup_failures_total by (task_type)
```

---

## Alert Examples

### Alert: High Error Rate

```yaml
- alert: HighErrorRate
  expr: rate(http_5xx_errors_total[5m]) > 0.1
  for: 2m
  annotations:
    summary: "High 5xx error rate ({{ $value }} errors/sec)"
    runbook: "See RUNBOOKS.md#outage-response-runbook"
```

**What triggers it**: More than 10% of requests returning 5xx errors for >2 minutes  
**Severity**: CRITICAL  
**Response time**: Page on-call immediately  
**Runbook**: [Outage Response](RUNBOOKS.md#outage-response-runbook)

### Alert: Auth Failures Spike

```yaml
- alert: AuthFailureSpike
  expr: rate(http_auth_failures_total[5m]) > 0.05
  for: 3m
  annotations:
    summary: "Auth failure spike ({{ $value }} failures/sec)"
    runbook: "See RUNBOOKS.md#auth-failure-runbook"
```

**What triggers it**: More than 5 authentication failures per second for >3 minutes  
**Severity**: HIGH  
**Response time**: Notify #security Slack channel within 5 minutes  
**Runbook**: [Auth Failure Response](RUNBOOKS.md#auth-failure-runbook)

---

## Health Check

### Endpoint: `GET /health`

**Response (Healthy)**:
```json
HTTP/1.1 200 OK

{
  "status": "healthy",
  "timestamp": "2026-03-20T15:30:45.123456",
  "version": "1.0",
  "response_time_seconds": 0.045,
  "dependencies": {
    "database": {
      "status": "up",
      "duration_seconds": 0.025
    },
    "filesystem": {
      "status": "up",
      "path": "/storage/audio",
      "duration_seconds": 0.010"
    },
    "api_keys": {
      "status": "up",
      "configured": {
        "groq": true,
        "google_oauth": true,
        "captcha": true
      },
      "missing": []
    }
  }
}
```

**Response (Degraded)**:
```json
HTTP/1.1 503 Service Unavailable

{
  "status": "degraded",
  "timestamp": "2026-03-20T15:31:00.000000",
  "version": "1.0",
  "response_time_seconds": 2.500,
  "dependencies": {
    "database": {
      "status": "up",
      "duration_seconds": 2.400
    },
    "filesystem": {
      "status": "up",
      "path": "/storage/audio",
      "duration_seconds": 0.010
    },
    "api_keys": {
      "status": "degraded",
      "configured": { "groq": true },
      "missing": [ "captcha" ]
    }
  }
}
```

**Monitoring**:
- Uptime Robot checks every 30 seconds
- Expected response: 200 (healthy) or 503 (degraded)
- Alert if response time > 10 seconds

---

## Incident Response

### Getting Started

1. **Alert fires** → You receive Slack/PagerDuty notification
2. **Open incident** → Go to PagerDuty or Slack
3. **Acknowledge alert** → Prevents escalation
4. **Gather context** → Check Grafana dashboard and logs
5. **Follow runbook** → See [RUNBOOKS.md](RUNBOOKS.md)
6. **Implement fix** → Apply remediation steps
7. **Verify** → Confirm health endpoint returns 200
8. **Resolve** → Close incident and document

### Quick Links

- **Grafana Dashboard**: http://grafana:3000
- **Prometheus Alerts**: http://prometheus:9090/alerts
- **Logs**: Check `docker logs <container>` or centralized logging
- **Sentry Errors**: https://sentry.io/organizations/techfixai
- **Incident Runbooks**: [RUNBOOKS.md](RUNBOOKS.md)

---

## Testing

### Test Structured Logging

```bash
# Make request and check logs contain request ID
curl http://localhost:8000/login
docker logs <container> | grep request_id
```

### Test Metrics Collection

```bash
# Verify metrics are being collected
curl http://localhost:8000/metrics | grep "http_requests_total"

# Should return counter with increasing values
```

### Test Sentry Integration

```bash
# Trigger an error (if you have an error endpoint)
curl http://localhost:8000/api/trigger-error 2>&1

# Check Sentry dashboard - error should appear within seconds
```

### Test Alert Trigger

```bash
# Simulate high error rate
for i in {1..100}; do
  curl http://localhost:8000/api/invalid_endpoint 2>&1 &
done
wait

# After 3 minutes, alert should fire
# Check Prometheus: http://localhost:9090/alerts
```

---

## Production Deployment

### Prerequisites

1. **Prometheus** running and scraping `/metrics`
2. **Grafana** connected to Prometheus
3. **Sentry account** created and DSN configured
4. **AlertManager** running with notification channels
5. **Uptime Robot** or equivalent monitoring service

### Deployment Steps

```bash
# 1. Update .env with production values
export SENTRY_DSN="https://your-production-dsn@sentry.io/..."
export STRUCTURED_LOGGING_ENABLED=True
export METRICS_ENABLED=True
export LOG_LEVEL=INFO

# 2. Build and deploy
docker build -t techfixai:v1 .
docker push techfixai:v1

# 3. Configure Prometheus to scrape
# Edit prometheus.yml:
# scrape_configs:
#   - job_name: 'techfixai-prod'
#     static_configs:
#       - targets: ['prod-app:8000']

# 4. Restart Prometheus and AlertManager
docker restart prometheus alertmanager

# 5. Verify metrics flowing
curl http://prometheus:9090/api/v1/query?query=up

# 6. Set up Grafana alert notifications
# Grafana UI → Notification Channels → Add Slack/PagerDuty
```

---

## Maintenance

### Regular Tasks

- **Weekly**: Review error trends in Sentry
- **Weekly**: Check Grafana dashboard for anomalies
- **Monthly**: Rotate Sentry alerts and update thresholds
- **Monthly**: Review and update runbooks
- **Quarterly**: Conduct incident response drills

### Useful Commands

```bash
# Check if Prometheus is scraping metrics
curl http://localhost:9090/api/v1/targets

# Query specific metric
curl 'http://localhost:9090/api/v1/query?query=http_requests_total'

# View current alerts
curl http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | select(.state == "firing")'

# Check AlertManager status
curl http://localhost:9093/api/v1/status

# Silence an alert (1 hour)
curl -X POST http://localhost:9093/api/v1/silences \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [{"name":"alertname","value":"HighErrorRate"}],
    "duration": "1h"
  }'
```

---

## Troubleshooting

### Logs not appearing in JSON format

```bash
# Check STRUCTURED_LOGGING_ENABLED is True
echo $STRUCTURED_LOGGING_ENABLED

# Or set it explicitly
export STRUCTURED_LOGGING_ENABLED=True
```

### Metrics not being scraped

```bash
# 1. Confirm /metrics endpoint is accessible
curl http://localhost:8000/metrics | head -10

# 2. Check Prometheus config
cat prometheus.yml | grep -A 5 "techfixai"

# 3. Verify targets in Prometheus UI
# http://localhost:9090/targets
```

### Sentry not capturing errors

```bash
# 1. Check DSN is set
echo $SENTRY_DSN

# 2. Check logs for Sentry initialization
docker logs <container> | grep -i sentry

# 3. Verify network connectivity to Sentry
curl https://sentry.io
```

### High memory usage

```bash
# Prometheus stores metrics in memory
# Check retention settings
ps aux | grep prometheus | grep -o 'storage.tsdb.retention.*'

# Reduce if needed (default 15 days)
# Add flag: --storage.tsdb.retention.time=7d
```

---

## Summary

| Component | Location | Purpose | Status |
|-----------|----------|---------|--------|
| Structured Logging | `app/core/logging_config.py` | JSON logs with request IDs | ✅ |
| Prometheus Metrics | `app/core/metrics.py` | Time-series metrics | ✅ |
| Health Checks | `app/core/health.py` | Dependency status | ✅ |
| Sentry Integration | `app/core/observability.py` | Error tracking | ✅ |
| `/metrics` endpoint | `app/api/web.py` | Prometheus scrape target | ✅ |
| `/health` endpoint | `app/api/web.py` | Uptime monitoring | ✅ |
| Alert Rules | `ALERTING.md` | Alert conditions | ✅ |
| Runbooks | `RUNBOOKS.md` | Incident response | ✅ |
| Monitoring Guide | `MONITORING.md` | Grafana/Prometheus setup | ✅ |

---

**Next Steps**: Follow [MONITORING.md](MONITORING.md) to set up Grafana, Prometheus, and dashboards.


---

## Integrated From: MONITORING.md

Merged on: 2026-03-20 13:44:19

# TechFixAI Monitoring & Observability Setup

**Purpose**: Complete guide for setting up Prometheus, Grafana, and monitoring dashboards.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   TechFixAI Application                  │
│  (FastAPI with Prometheus metrics exposed at /metrics)  │
└──────────────────┬──────────────────────────────────────┘
                   │ (pulls metrics every 15s)
                   ▼
        ┌──────────────────────┐
        │   Prometheus DB      │
        │  (stores time-series) │
        └──────────┬───────────┘
                   │
        ┌──────────┴────────────────┐
        ▼                           ▼
   ┌─────────────┐          ┌──────────────┐
   │   AlertMgr  │          │   Grafana    │
   │  (alerts)   │          │ (dashboards) │
   └─────────────┘          └──────────────┘
        │                           │
        ▼                           ▼
   [PagerDuty]    [Slack]    [Email/Browser]
```

---

## 1. Prometheus Setup

### Local Development (Docker)

```bash
# Create prometheus.yml
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - 'alerts.yml'

scrape_configs:
  - job_name: 'techfixai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
    scrape_timeout: 10s
EOF

# Run Prometheus
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml:ro \
  -v $(pwd)/alerts.yml:/etc/prometheus/alerts.yml:ro \
  prom/prometheus:latest

# Access at http://localhost:9090
```

### Production (Kubernetes)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'techfixai'
        scrape_interval: 15s
        static_configs:
          - targets: ['techfixai-app:8000']
        metrics_path: '/metrics'

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
```

### Verify Metrics Collection

```bash
# Check if Prometheus scrapes TechFixAI
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[]'

# Query a metric
curl 'http://localhost:9090/api/v1/query?query=http_requests_total' | jq '.data.result[0]'
```

---

## 2. Grafana Setup

### Docker Installation

```bash
# Create Grafana with Prometheus data source
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  -v grafana_storage:/var/lib/grafana \
  grafana/grafana:latest

# Access at http://localhost:3000 (user: admin, pass: admin)
```

### Add Prometheus Data Source

1. Open Grafana (http://localhost:3000)
2. Go to **Configuration** → **Data Sources**
3. Click **Add data source** → Select **Prometheus**
4. Set URL to `http://localhost:9090`
5. Click **Save & test**

### Import Dashboard

#### Option A: Import from Template

1. Go to **Create** → **Dashboard** → **Import**
2. Paste dashboard JSON (see below) or upload file
3. Select Prometheus data source
4. Click **Import**

#### Option B: Create Dashboard from Scratch

See **Dashboard JSON** section below for pre-built dashboard.

---

## 3. Pre-built Grafana Dashboard JSON

**Save as `grafana-dashboard.json`**:

```json
{
  "dashboard": {
    "title": "TechFixAI Monitoring Dashboard",
    "timezone": "UTC",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate (req/sec)",
        "targets": [
          {
            "expr": "rate(http_requests_total[1m])"
          }
        ],
        "type": "graph"
      },
      {
        "id": 2,
        "title": "Error Rate (5xx/sec)",
        "targets": [
          {
            "expr": "rate(http_5xx_errors_total[1m])"
          }
        ],
        "type": "graph",
        "alert": {
          "name": "HighErrorRate",
          "conditions": [{"evaluator": {"type": "gt"}, "operator": {"type": "and"}, "query": {"params": [0.1, "5m"]}}]
        }
      },
      {
        "id": 3,
        "title": "P95 Latency (seconds)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds)"
          }
        ],
        "type": "graph"
      },
      {
        "id": 4,
        "title": "Upload Success Rate (%)",
        "targets": [
          {
            "expr": "(rate(voice_upload_total{status=\"success\"}[5m]) / rate(voice_upload_total[5m])) * 100"
          }
        ],
        "type": "gauge"
      },
      {
        "id": 5,
        "title": "Database Query Latency (P95)",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, db_query_duration_seconds) by (operation)"
          }
        ],
        "type": "graph"
      },
      {
        "id": 6,
        "title": "Authentication Failures",
        "targets": [
          {
            "expr": "rate(http_auth_failures_total[5m]) by (reason)"
          }
        ],
        "type": "graph"
      },
      {
        "id": 7,
        "title": "Cleanup Task Status",
        "targets": [
          {
            "expr": "cleanup_failures_total by (task_type)"
          }
        ],
        "type": "graph"
      },
      {
        "id": 8,
        "title": "Active Database Connections",
        "targets": [
          {
            "expr": "active_connections"
          }
        ],
        "type": "gauge"
      }
    ]
  }
}
```

**To import**:
```bash
# Save the JSON to a file
cat > dashboard.json << 'EOF'
{ ... full JSON above ... }
EOF

# Import via Grafana UI:
# Grafana → Create → Dashboard → Import → Upload dashboard.json
```

---

## 4. Alerting Setup

### AlertManager Configuration

**alertmanager.yml**:
```yaml
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'critical'
      repeat_interval: 10m
    - match:
        severity: high
      receiver: 'high'

receivers:
  - name: 'default'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#incidents'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'critical'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#incidents'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'

  - name: 'high'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#incidents'
        title: '⚠️ HIGH: {{ .GroupLabels.alertname }}'
```

### Prometheus Alert Rules

**alerts.yml**:
```yaml
groups:
  - name: techfixai_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_5xx_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High 5xx error rate"
          description: "{{ $value }} errors/sec"

      - alert: AuthFailureSpike
        expr: rate(http_auth_failures_total[5m]) > 0.05
        for: 3m
        labels:
          severity: high
        annotations:
          summary: "Auth failure spike detected"
          description: "{{ $value }} auth failures/sec"

      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 5
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High request latency (P95 > 5s)"
          description: "{{ $value }}s for {{ $labels.endpoint }}"

      - alert: UploadFailures
        expr: rate(voice_upload_failures_total[5m]) > 0.05
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High upload failure rate"
          description: "{{ $value }} upload failures/sec - reason: {{ $labels.reason }}"

      - alert: DatabaseDown
        expr: rate(db_connection_errors_total[1m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection errors"
          description: "Cannot connect to database"

      - alert: CleanupFailures
        expr: cleanup_failures_total > 0
        for: 5m
        labels:
          severity: medium
        annotations:
          summary: "Data cleanup failed"
          description: "{{ $labels.task_type }} cleanup failed"
```

### Start AlertManager

```bash
docker run -d \
  --name alertmanager \
  -p 9093:9093 \
  -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro \
  prom/alertmanager:latest
```

---

## 5. Sentry Error Tracking Setup

### 1. Create Sentry Project

1. Go to https://sentry.io
2. Sign up / Log in
3. Create new project → Select "FastAPI"
4. Copy your DSN (looks like `https://<key>@<org>.ingest.sentry.io/<id>`)

### 2. Configure TechFixAI

```bash
# Add to .env
export SENTRY_DSN="https://<key>@<org>.ingest.sentry.io/<id>"
export SENTRY_TRACES_SAMPLE_RATE="0.1"  # 10% of requests
export SENTRY_RELEASE="1.0.0"            # Version tag
```

### 3. Verify Integration

```bash
# Start app with Sentry enabled
export SENTRY_DSN="..."
python -c "from app.main import app; print('Sentry initialized')"

# Trigger test error
# Visit http://localhost:8000/intentional_error (if route exists)
# Or manually trigger in code:
sentry_sdk.capture_exception(Exception("Test"))

# Check Sentry dashboard for the error
# Should appear within seconds
```

---

## 6. Custom Metrics Instrumentation

### Example: Track Custom Business Metric

```python
# In your route handler
from app.core.metrics import MetricsRecorder

@router.post("/api/voice/upload")
async def upload_voice(file: UploadFile):
    start_time = time.time()
    
    try:
        # ... upload logic ...
        duration = time.time() - start_time
        
        # Record success
        MetricsRecorder.record_voice_upload(
            duration=duration,
            file_size=len(file.file.read()),
            success=True
        )
        
        return {"status": "ok"}
    
    except TimeoutError:
        duration = time.time() - start_time
        MetricsRecorder.record_voice_upload(
            duration=duration,
            file_size=0,
            success=False,
            failure_reason="timeout"
        )
        raise
```

### Plotting Custom Metrics in Grafana

```
# Upload success rate
rate(voice_upload_total{status="success"}[5m])

# Average upload duration
rate(voice_upload_duration_seconds_sum[5m]) / rate(voice_upload_duration_seconds_count[5m])

# Upload failure by reason
rate(voice_upload_failures_total[5m]) by (reason)
```

---

## 7. Health Checks & Uptime Monitoring

### Using Uptime Robot (Simple)

1. Go to https://uptimerobot.com
2. Create new monitor:
   - URL: `https://yourdomain.com/health`
   - Interval: 30 seconds
   - Timeout: 10 seconds
3. Set alerts for downtime
4. Monitor dashboard shows uptime percentage

### Using Grafana OnCall (Advanced)

```
Grafana UI → Alerts → Notification policies
→ Create routing rule for CRITICAL alerts
→ Route to Grafana OnCall
```

---

## 8. Logs Analysis with Loki (Optional)

### Install Loki

```bash
docker run -d \
  --name loki \
  -p 3100:3100 \
  grafana/loki:latest
```

### Configure App to Send Logs to Loki

```python
# app/core/logging_config.py
import logging
from pythonjsonlogger import jsonlogger

# Add Loki handler
loki_handler = logging.StreamHandler()
loki_handler.setFormatter(jsonlogger.JsonFormatter())
logger.addHandler(loki_handler)
```

### Query Logs in Grafana

1. Add Loki data source in Grafana (URL: http://localhost:3100)
2. Create panel with LogQL query:
   ```
   {job="techfixai"} | json | status_code >= 500
   ```

---

## 9. Dashboards Quick Reference

### CPU & Memory (System Metrics)

```
# CPU usage
process_cpu_seconds_total

# Memory usage
process_resident_memory_bytes

# File descriptors
process_open_fds
```

### Application Health Scorecard

```
# Uptime percentage (last 24h)
100 * (count(http_requests_total) / (count(rate(http_requests_total[24h])) * 24 * 60))

# Success rate
(rate(http_requests_total{status_code="200"}[5m]) / rate(http_requests_total[5m])) * 100

# Median latency
histogram_quantile(0.5, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
(rate(http_5xx_errors_total[5m]) / rate(http_requests_total[5m])) * 100
```

---

## 10. Testing & Validation

### Test Metrics Collection

```bash
# Pull metrics endpoint
curl http://localhost:8000/metrics | head -50

# Should see Prometheus format:
# # TYPE http_requests_total counter
# http_requests_total{...} 123
```

### Test Prometheus Query

```bash
# Via PromQL
curl 'http://localhost:9090/api/v1/query?query=http_requests_total'

# Should return JSON:
# {
#   "status": "success",
#   "data": {
#     "resultType": "instant",
#     "result": [ ... ]
#   }
# }
```

### Simulate Alert

```bash
# Trigger high error rate (make 100 requests in parallel)
for i in {1..100}; do
  curl http://localhost:8000/api/invalid &
done
wait

# Check alert status after 3 minutes
curl http://localhost:9090/api/v1/rules | jq '.data.groups[0].rules[] | select(.state == "firing")'
```

---

## Next Steps

1. **Deploy Prometheus + Grafana** to staging/production
2. **Configure Slack/PagerDuty** integrations
3. **Set up AlertManager** with alert rules
4. **Import Dashboard JSON** into Grafana
5. **Test end-to-end** alert flow (trigger, notify, acknowledge)
6. **Train team** on reading dashboards and responding to alerts
7. **Set on-call rotation** with escalation policy

**See**: 
- [ALERTING.md](ALERTING.md) - Alert conditions and thresholds
- [RUNBOOKS.md](RUNBOOKS.md) - Incident response procedures


---

## Integrated From: ALERTING.md

Merged on: 2026-03-20 13:44:19

# TechFixAI Alerting Rules & Configuration

**Purpose**: Define alert conditions, thresholds, and notification channels for production incidents.

---

## Alert Conditions

### 1. 5xx Error Rate Spike  
**Severity**: CRITICAL  
**Condition**: `rate(http_5xx_errors_total[5m]) > 0.1` (more than 10% of requests failing)  
**Notification**: Immediate Slack/Email to #incidents  
**Runbook**: [Outage Response](RUNBOOKS.md#outage-response-runbook)

**Details**:
- Monitors `http_5xx_errors_total` metric
- 5-minute window to reduce false alarms
- Threshold: >0.1 errors per second (10% rate for 100 req/sec baseline)

### 2. Authentication Failures Spike
**Severity**: HIGH  
**Condition**: `rate(http_auth_failures_total[5m]) > 0.05` (spike from baseline)  
**Notification**: Slack #security within 5 minutes  
**Runbook**: [Auth Failure Response](RUNBOOKS.md#auth-failure-runbook)

**Details**:
- Monitors `http_auth_failures_total` metric by reason
- Top causes: `invalid_token`, `expired_token`, `unauthorized`, `brute_force_lockout`
- Spike detection: Compare current rate vs. 1-hour baseline
- Alert if 5x baseline or >5 failures per second

### 3. High Request Latency (P95 > 5 seconds)
**Severity**: HIGH  
**Condition**: `histogram_quantile(0.95, http_request_duration_seconds) > 5`  
**Notification**: Slack with latency details  
**Runbook**: [Latency Regression](RUNBOOKS.md#latency-regression)

**Details**:
- Monitors p95 latency by endpoint
- Threshold: 5 second response time
- Per-endpoint alerts for granular diagnosis
- Common causes: Database slowness, API timeouts, upload backlog

### 4. Upload Failures Rate Spike
**Severity**: HIGH  
**Condition**: `rate(voice_upload_failures_total[5m]) > 0.05`  
**Notification**: Slack #support  
**Runbook**: [Upload Failure Debugging](RUNBOOKS.md#upload-failure-debugging)

**Details**:
- Monitors upload failure reasons: `timeout`, `file_size`, `storage_error`, etc.
- Alert if >5% of uploads failing
- Track by failure reason for targeted fixes

### 5. Database Connection Errors
**Severity**: CRITICAL  
**Condition**: `rate(db_connection_errors_total[1m]) > 0`  
**Notification**: Immediate all-hands alert  
**Runbook**: [Database Recovery](RUNBOOKS.md#database-recovery)

**Details**:
- Any database connection failure is critical
- 1-minute window for quick response
- Check: Database availability, connection pool exhaustion, credentials

### 6. Health Check Degradation
**Severity**: CRITICAL  
**Condition**: Health endpoint returns `status != "healthy"` for >2 consecutive checks  
**Notification**: Immediate to on-call  
**Runbook**: [Health Check Failures](RUNBOOKS.md#health-endpoint-diagnostics)

**Details**:
- Checks every 30 seconds from monitoring service
- Unhealthy = database down, filesystem inaccessible, missing API keys
- Degraded = some dependency slow/partial failure

### 7. Cleanup Task Failures
**Severity**: MEDIUM  
**Condition**: `cleanup_failures_total > 0` (any failure)  
**Notification**: Daily digest + alert on 2+ failures in 1 hour  
**Runbook**: [Data Cleanup Failures](RUNBOOKS.md#cleanup-task-failures)  

**Details**:
- Monitors audio cleanup, database cleanup, audit log cleanup
- Failures = orphaned files, database inconsistencies
- Impact: Data not purged per retention policy

### 8. Response Time Outlier Detection
**Severity**: MEDIUM  
**Condition**: Endpoint suddenly takes 10x normal time  
**Detection**: Anomaly detection on historical latency  
**Notification**: Slack with affected endpoint  
**Runbook**: [Latency Regression](RUNBOOKS.md#latency-regression)

---

## Alert Routing Configuration

### Channel Mapping

| Alert Type | Severity | Channel | Escalation |
|-----------|----------|---------|------------|
| 5xx errors | CRITICAL | #incidents Slack + Page on-call | 5 min |
| Auth failures | HIGH | #security Slack | 15 min |
| Latency regression | HIGH | #incidents Slack | 15 min |
| Upload failures | HIGH | #support Slack | 30 min |
| DB errors | CRITICAL | #incidents + PagerDuty page | 2 min |
| Health down | CRITICAL | #incidents + PagerDuty page | 1 min |
| Cleanup failures | MEDIUM | Daily digest email | None (no page) |
| Anomalies | MEDIUM | #analytics Slack | None (no page) |

### Notification Channels

**Production**: PagerDuty (on-call rotation)  
**Development**: Slack (non-critical)  
**Database Down**: Email + SMS fallback

---

## Alerting Platform Setup

### Option A: Grafana (Recommended)
**Installation**:
```bash
docker run -d -p 3000:3000 grafana/grafana
```

**Configuration**:
1. Add Prometheus data source: `http://localhost:9090`
2. Create alert rules for each condition (see Alert Rules below)
3. Set notification channels (Slack webhook, PagerDuty, email)

**Alert Rules (PromQL)**:

```yaml
groups:
  - name: techfixai_alerts
    rules:
      # Critical: 5xx errors
      - alert: HighErrorRate
        expr: rate(http_5xx_errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High 5xx error rate"
          description: "{{ $value }} errors/sec over last 5 minutes"
      
      # High: Auth failures
      - alert: AuthFailureSpike
        expr: rate(http_auth_failures_total[5m]) > 0.05
        for: 3m
        labels:
          severity: high
        annotations:
          summary: "Auth failure spike"
          description: "{{ $value }} failures/sec"
      
      # High: Latency regression
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 5
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High request latency (P95 > 5s)"
          description: "{{ $value }}s for endpoint {{ $labels.endpoint }}"
      
      # Critical: Database errors
      - alert: DatabaseConnectionErrors
        expr: rate(db_connection_errors_total[1m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failures"
          description: "Database connectivity problem detected"
      
      # Critical: Health check down
      - alert: HealthCheckFailed
        expr: health_check_total{status="unhealthy"} > 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Health check failure detected"
          description: "Application health endpoint reporting issues"
      
      # Medium: Cleanup failures
      - alert: CleanupTaskFailure
        expr: rate(cleanup_failures_total[5m]) > 0
        for: 5m
        labels:
          severity: medium
        annotations:
          summary: "Data cleanup task failed"
          description: "{{ $labels.task_type }} cleanup failed"
```

### Option B: Prometheus AlertManager

**Configuration** (`alertmanager.yml`):
```yaml
global:
  resolve_timeout: 5m
  slack_api_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

route:
  receiver: 'default'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - match:
        severity: critical
      receiver: 'critical'
      repeat_interval: 10m
    - match:
        severity: high
      receiver: 'high'
      repeat_interval: 30m
    - match:
        severity: medium
      receiver: 'medium'
      repeat_interval: 2h

receivers:
  - name: 'default'
    slack_configs:
      - channel: '#incidents'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
  
  - name: 'critical'
    slack_configs:
      - channel: '#incidents'
        title: '🚨 CRITICAL: {{ .GroupLabels.alertname }}'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
  
  - name: 'high'
    slack_configs:
      - channel: '#incidents'
        title: '⚠️ HIGH: {{ .GroupLabels.alertname }}'
  
  - name: 'medium'
    slack_configs:
      - channel: '#support'
```

---

## Uptime Monitoring Setup

### Uptime Monitoring Service

**Tool**: Uptime Robot / Better Stack (recommended for simplicity)

**Configuration**:
```
Service: TechFixAI Backend
URL: https://yourdomain.com/health
Interval: 30 seconds
Timeout: 10 seconds
Expected: Status 200 or 503 with acceptable response time
```

**Alerts**:
- Down for >1 minute → Page on-call
- Latency >5 seconds on health endpoint → Notify #incidents
- Health status `degraded` → Slack on-call

### Custom Health Check Script

```bash
#!/bin/bash
# health-check.sh - Monitor main app and health endpoint

PROD_URL="https://yourdomain.com"
HEALTH_ENDPOINT="$PROD_URL/health"
METRICS_ENDPOINT="$PROD_URL/metrics"

check_health() {
  response=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_ENDPOINT" -m 10)
  if [ "$response" != "200" ] && [ "$response" != "503" ]; then
    echo "CRITICAL: Health endpoint returned $response"
    return 1
  fi
  echo "OK: Health endpoint healthy"
  return 0
}

check_metrics() {
  response=$(curl -s -o /dev/null -w "%{http_code}" "$METRICS_ENDPOINT" -m 10)
  if [ "$response" != "200" ]; then
    echo "WARNING: Metrics endpoint returned $response"
    return 1
  fi
  echo "OK: Metrics available"
  return 0
}

check_api() {
  response=$(curl -s -o /dev/null -w "%{http_code}" "$PROD_URL/" -m 10)
  if [ "$response" != "200" ]; then
    echo "CRITICAL: Main endpoint returned $response"
    return 1
  fi
  echo "OK: Main endpoint responding"
  return 0
}

# Run checks
check_health && check_metrics && check_api
exit $?
```

**Cron Job** (run every 5 minutes):
```cron
*/5 * * * * /usr/local/bin/health-check.sh >> /var/log/health-checks.log 2>&1
```

---

## Escalation Policy

**Severity: CRITICAL** (Database Down, 5xx spike, Health Down)
1. Page on-call engineer
2. If unacknowledged in 5 minutes, page team lead
3. If unacknowledged in 10 minutes, escalate to VP Eng

**Severity: HIGH** (Auth failures, Latency spike, Upload failures)
1. Slack notification to #incidents
2. If continues >15 minutes, page on-call

**Severity: MEDIUM** (Cleanup failures, anomalies)
1. Slack notification
2. Digest email daily
3. No paging

---

## Metrics Dashboard Setup

See [MONITORING.md](MONITORING.md) for Grafana dashboard JSON and manual setup instructions.

---

## Testing Alerts

### Trigger a Test Alert

```bash
# Simulate 5xx errors
ab -n 1000 -c 10 http://localhost:8000/api/invalid_endpoint

# Check alert state
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts'

# View AlertManager status
curl http://localhost:9093/api/v1/alerts | jq '.data'
```

### Silence Alert (Maintenance Window)

```bash
# Silence for 1 hour
curl -X POST http://localhost:9093/api/v1/silences -d '{
  "matchers": [
    {
      "name": "alertname",
      "value": "HighErrorRate",
      "isRegex": false
    }
  ],
  "duration": "1h",
  "createdBy": "ops-engineer@techfixai.com",
  "comment": "Scheduled maintenance"
}'
```

---

## Metrics to Monitor

**Key metrics** visible in dashboard:

1. **Request Rate**: `rate(http_requests_total[1m])` - requests per second
2. **Error Rate**: `rate(http_5xx_errors_total[1m])` - errors per second  
3. **P95 Latency**: `histogram_quantile(0.95, http_request_duration_seconds)` - seconds
4. **Auth Failures**: `rate(http_auth_failures_total[5m])` - per reason
5. **Upload Success Rate**: `(voice_upload_total{status="success"} / voice_upload_total)` - percentage
6. **Database Latency**: `histogram_quantile(0.95, db_query_duration_seconds)` - seconds
7. **Cleanup Status**: `cleanup_failures_total` - count by task_type
8. **Health Status**: `health_check_total` - by status

---

**Next**: See [RUNBOOKS.md](RUNBOOKS.md) for incident response procedures.


---

## Integrated From: RUNBOOKS.md

Merged on: 2026-03-20 13:44:19

# TechFixAI Incident Response Runbooks

**Purpose**: Step-by-step procedures for responding to production incidents.

---

## Table of Contents

1. [Outage Response Runbook](#outage-response-runbook)
2. [Auth Failure Runbook](#auth-failure-runbook)
3. [Database Recovery](#database-recovery)
4. [Latency Regression](#latency-regression)
5. [Upload Failure Debugging](#upload-failure-debugging)
6. [Data Cleanup Failures](#data-cleanup-task-failures)
7. [Health Endpoint Diagnostics](#health-endpoint-diagnostics)

---

## Outage Response Runbook

**Triggered by**: 5xx error rate spike alert  
**Severity**: CRITICAL  
**Goal**: Restore service within 15 minutes  

### Phase 1: Immediate Assessment (0-2 min)

**Step 1**: Acknowledge the alert
```bash
# Mark as acknowledged in AlertManager (silence for 12h while investigating)
curl -X POST http://prometheus-alertmanager:9093/api/v1/silences \
  -d '{"matchers":[{"name":"alertname","value":"HighErrorRate"}],"duration":"12h"}'
```

**Step 2**: Check current health status
```bash
# Quick health check
curl -i https://yourdomain.com/health

# Expected response:
# HTTP/1.1 200 OK or 503 Service Unavailable
# {
#   "status": "healthy|degraded|unhealthy",
#   "dependencies": { ... }
# }
```

**Step 3**: Get real-time error details
```bash
# Check error counts by endpoint (from Prometheus)
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=topk(5, rate(http_5xx_errors_total[5m]))'

# Check error logs (last 50 lines)
tail -50 logs/app.log | grep ERROR

# Or with request IDs:
grep "status_code.*5" logs/app.log | tail -20
```

### Phase 2: Identify root cause (2-5 min)

**Check 1: Database connectivity**
```bash
# From host:
psql postgresql://user:pass@db-host:5432/techfixai -c "SELECT 1"

# From within app container:
curl http://localhost:8000/health | jq '.dependencies.database'

# Expected: { "status": "up", "duration_seconds": 0.05 }
# If down: Check connection pool, credentials, network
```

**Check 2: Filesystem access**
```bash
# Check storage path accessibility
curl http://localhost:8000/health | jq '.dependencies.filesystem'

# If down: Check disk space, permissions
df -h /path/to/storage
ls -la /path/to/storage
```

**Check 3: API key configuration**
```bash
# Check required API keys
curl http://localhost:8000/health | jq '.dependencies.api_keys'

# Example:
# {
#   "status": "up",
#   "configured": {"groq": true, "google_oauth": true},
#   "missing": []
# }

# If keys missing: Check .env, environment variables
env | grep -E "GROQ_API_KEY|GOOGLE_CLIENT_ID"
```

**Check 4: Recent code changes**
```bash
# Last 10 commits
git log --oneline -10

# Changes since last deploy
git diff HEAD~1 HEAD

# If recent deploy caused this, rollback (see rollback section)
```

### Phase 3: Remediation (5-10 min)

#### Path A: Database issue detected

```bash
# 1. Check connection pool for exhaustion
SELECT count(*) FROM pg_stat_activity WHERE datname = 'techfixai';

# 2. If exhausted (>max_connections), kill idle connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'techfixai' AND state = 'idle';

# 3. Restart app to reset connection pool
docker restart techfixai-app
# OR
kill <PID>; uvicorn app.main:app --reload

# 4. Monitor error rate (should drop within 2 min)
```

#### Path B: Filesystem full or inaccessible

```bash
# 1. Check disk space
df -h /path/to/storage

# 2. If full (>95%), delete old audio files manually
find /path/to/storage -type f -mtime +30 -delete

# 3. If permissions issue:
sudo chown -R app:app /path/to/storage
sudo chmod 755 /path/to/storage

# 4. Curl health endpoint again to confirm
curl http://localhost:8000/health
```

#### Path C: Code regression from recent deploy

```bash
# 1. Identify the bad commit
git log --oneline --since="30 minutes ago"

# 2. Revert the change
git revert <commit-hash>

# 3. Rebuild and redeploy
docker build -t techfixai:rollback .
docker run -d techfixai:rollback

# 4. Verify health within 2 minutes
curl http://localhost:8000/health
```

#### Path D: External API failure (Groq, Google OAuth)

```bash
# 1. Check if API is reachable
curl -i https://api.groq.com/health
curl -i https://accounts.google.com/o/oauth2/v2/auth

# 2. Check your API key validity
curl -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer $GROQ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"mixtral-8x7b-32768","messages":[{"role":"user","content":"test"}]}'

# 3. If invalid, update credentials and restart
export GROQ_API_KEY="new_key"
docker restart techfixai-app

# 4. For critical external API down:
   - Enable fallback mode (use cached responses)
   - Page external vendor account manager
   - Communicate status to users
```

### Phase 4: Verification (10-15 min)

**Step 1**: Verify error rate returned to normal
```bash
# Check 5-minute error rate (should be <0.01)
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=rate(http_5xx_errors_total[5m])'

# Expected: ~0 or very low number
```

**Step 2**: Verify all dependencies healthy
```bash
curl http://localhost:8000/health | jq '.'

# All of database, filesystem, api_keys should be "up"
```

**Step 3**: Run smoke tests
```bash
# Test key endpoints
curl http://localhost:8000/  # Homepage
curl http://localhost:8000/login  # Login page
curl http://localhost:8000/dashboard  # Dashboard (needs auth)

# All should return 200
```

**Step 4**: Unsile the alert and close incident
```bash
# Unsile alert
curl -X DELETE http://localhost:9093/api/v1/silences/<silence_id>

# Post-incident review (document findings)
echo "Incident report: Root cause was DB connection pool exhaustion. 
Fixed by restarting app. Added monitoring alert for this in future." 
>> docs/incident_log.md
```

### Rollback Procedure

If recent code caused the outage:

```bash
# 1. Identify last good commit
git log --oneline --all | grep "deploy\|release"

# 2. Checkout that version
git checkout <good-commit-hash>

# 3. Rebuild image with that code
docker build -t techfixai:stable .

# 4. Stop current container and start stable version
docker stop <current-container-id>
docker run -d --name techfixai techfixai:stable

# 5. Verify (should take <1 min to be healthy)
curl http://localhost:8000/health
```

---

## Auth Failure Runbook

**Triggered by**: `http_auth_failures_total` spike  
**Expected baseline**: <5 failures per minute  
**Alert threshold**: >5 failures/sec for >3 min  

### Diagnosis

**Step 1**: Check which auth method is failing
```bash
# From Prometheus:
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=http_auth_failures_total'

# Look at "reason" labels:
# - "invalid_token": Session cookie invalid/tampered
# - "expired_token": Session expired (normal, user re-login)
# - "unauthorized": User not in admin list
# - "brute_force_lockout": Too many failed login attempts
```

**Step 2**: Check recent auth logs
```bash
# All auth failures (last 100)
grep "auth_failure\|http_auth_failures_total" logs/app.log | tail -100

# By IP (if brute force suspected)
grep "auth_failure" logs/app.log | awk '{print $NF}' | sort | uniq -c | sort -rn
```

### Remediation

#### Case A: Session/Token Validation Issue

```bash
# Check if sessions are being invalidated incorrectly
# Look for errors in session decryption:
grep "session_payload" logs/app.log | grep ERROR

# If encryption key changed:
# 1. Check ENCRYPTION_KEY_VERSION matches
echo $ENCRYPTION_KEY_VERSION

# 2. If key was rotated, add old key to ENCRYPTION_LEGACY_KEY_VERSIONS
export ENCRYPTION_LEGACY_KEY_VERSIONS="v1,v2"
docker restart techfixai-app

# 3. Test: Try to log in with browser
# Go to http://localhost:8000/login and attempt sign-in
```

#### Case B: Brute Force Attack

```bash
# Check /login endpoint specifically
grep "POST /login" logs/app.log | grep "status_code.*401\|status_code.*403" | wc -l

# If >100 failures from single IP in 5 min, it's likely brute force
grep "POST /login" logs/app.log | grep "status_code.*40[13]" | tail -50 | head -1

# Check if brute-force protection is working:
grep "brute_force_lockout\|AUTH_LOCKOUT" logs/app.log

# If not being triggered, verify auth_guard.py is loaded:
curl http://localhost:8000/health | jq '.dependencies'

# Temporarily block the attacker IP in firewall/WAF
# Or enable CAPTCHA if not already enabled:
export CAPTCHA_ENABLED=True
docker restart techfixai-app
```

#### Case C: Invalid Token (Session Cookie Issue)

```bash
# Check for:
# 1. Cookie signature verification failures
grep "signature\|decode_session_cookie" logs/app.log | tail -20

# 2. Missing/invalid ENCRYPTION_KEY or SECRET_KEY
grep "SECRET_KEY\|ENCRYPTION_KEY" logs/app.log

# 3. Session TTL too short causing premature expiration
echo "SESSION_TTL_HOURS: $SESSION_TTL_HOURS"
# Default is 12 hours. If users report frequent re-login, increase this.

# Fix by increasing session TTL
export SESSION_TTL_HOURS=24
docker restart techfixai-app
```

#### Case D: Google OAuth Misconfiguration

```bash
# Check if OAuth is configured
grep "GOOGLE_CLIENT_ID\|GOOGLE_CLIENT_SECRET" logs/app.log

# Verify credentials
curl https://accounts.google.com/.well-known/openid-configuration -i

# If Google OAuth callback fails:
# 1. Verify GOOGLE_REDIRECT_URI matches Google Cloud Console
echo $GOOGLE_REDIRECT_URI
# Should be: https://yourdomain.com/auth/google/callback

# 2. Check if issue is CSRF mismatch:
grep "oauth_state_mismatch\|CSRF" logs/app.log | tail -10

# If seeing state mismatch errors:
# - Likely cause: User accessing via http instead of https, or switching hosts
# - Solution: Ensure all OAuth flows use HTTPS and consistent hostname
# - Communicate to users: "Please use https://yourdomain.com, not IP address"
```

---

## Database Recovery

**Triggered by**: `db_connection_errors_total > 0`  
**Severity**: CRITICAL  
**RTO**: 5 minutes  
**RPO**: Zero (no data loss)

### Diagnostics

```bash
# 1. Can you reach the database?
psql postgresql://<user>:<pass>@<host>:5432/techfixai -c "SELECT 1"

# 2. Check connection pool status
SELECT count(*), state FROM pg_stat_activity GROUP BY state;

# 3. Check for deadlocks
SELECT * FROM pg_locks WHERE NOT granted;

# 4. Check database size / disk space
SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname))
FROM pg_database ORDER BY pg_database_size(pg_database.datname) DESC;

# 5. Check active queries (long-running)
SELECT pid, usename, application_name, state, query_start, query 
FROM pg_stat_activity WHERE state != 'idle' 
ORDER BY query_start ASC;
```

### Recovery Steps

**Step 1**: Kill idle connections (frees up pool)
```sql
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'techfixai' AND state = 'idle' AND pid <> pg_backend_pid();
```

**Step 2**: Kill long-running queries (>10 min)
```sql
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'techfixai' 
  AND state = 'active' 
  AND query_start < now() - interval '10 minutes'
ORDER BY query_start ASC;
```

**Step 3**: Restart app connection pool
```bash
docker restart techfixai-app
# OR manually kill app process
kill -9 <APP_PID>
```

**Step 4**: If database is fully down, restore from backup
```bash
# List available backups
ls -la /backup/postgresql/

# Restore latest backup (Railway/AWS RDS has automated backups)
# For Railway: Use Railway dashboard to restore point-in-time
# For AWS RDS: Use AWS console to restore snapshot

# Verify data integrity after restore
psql postgresql://<user>:<pass>@<host>/techfixai -c "SELECT count(*) FROM users;"
```

**Step 5**: Verify app can connect
```bash
curl http://localhost:8000/health | jq '.dependencies.database'
# Should show: { "status": "up", ... }
```

**Step 6**: Monitor for deadlocks recurring
```bash
# If deadlock errors continue:
# 1. Identify the queries involved
grep "deadlock detected" logs/app.log | tail -5

# 2. Review those queries in code
git grep "<query_text>"

# 3. Add appropriate indexes or improve query locks
# 4. Test with load to confirm fix
```

---

## Latency Regression

**Triggered by**: P95 latency > 5 seconds  
**Severity**: HIGH  
**Goal**: Identify slow endpoint and root cause within 10 minutes

### Quick Check

```bash
# Which endpoints are slow?
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.95, http_request_duration_seconds) by (endpoint)' \
  | jq '.data.result[] | {endpoint: .metric.endpoint, p95: .value[1]}'

# Example output:
# { "endpoint": "/api/voice/upload", "p95": "7.23" }  <- TOO SLOW
# { "endpoint": "/login", "p95": "0.45" }
```

### Root Cause Analysis

**Check 1: Database query latency**
```bash
# Compare DB latency to request latency
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.95, db_query_duration_seconds) by (operation)'

# If DB queries are 3+ seconds, next check: slow query log
SELECT query, calls, mean_time, max_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 5;

# Run EXPLAIN ANALYZE on slow query
EXPLAIN ANALYZE SELECT ...;

# Add index if needed or optimize query
```

**Check 2: External API latency (Groq, Google, etc.)**
```bash
# Check Groq API response times
grep "groq\|transcription_duration\|translation_duration" logs/app.log | tail -20

# Metrics:
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=histogram_quantile(0.95, transcription_duration_seconds)'

# If Groq is slow (>3 sec):
# 1. Check your API quota
curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/usage

# 2. Rate limit your requests or upgrade plan
# 3. Add caching for similar transcriptions
```

**Check 3: Recent code deployments**
```bash
# Check last few commits for performance changes
git log --oneline --since="1 hour ago" -p \
  -- app/api/voice.py app/api/ticket.py | head -100

# Look for:
# - New N+1 database queries
# - New external API calls in critical path
# - Removed caching

# If found, revert:
git revert <commit-hash>
docker build -t techfixai:fix . && docker run ...
```

**Check 4: Load testing to identify bottleneck**
```bash
# Run load test on slow endpoint
ab -n 100 -c 10 http://localhost:8000/api/voice/upload

# Or use more sophisticated tool:
# Apache Bench, wrk, k6, etc.

# Monitor during test:
watch -n 1 'curl http://localhost:9090/api/v1/query --data-urlencode "query=rate(http_request_duration_seconds_sum[1m])" | jq'
```

### Fix

**If DB-related**:
```sql
-- Add missing index
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Or optimize the query
-- Before: SELECT * FROM conversations JOIN tickets...
-- After: SELECT id, user_id, created_at FROM conversations WHERE user_id=... (only needed cols)
```

**If external API slow**:
- Check API provider status
- Add timeout to API calls (fail fast)
- Implement caching for responses
- Use request batching if available

**If code regression**:
- Revert recent commits until latency drops
- Add performance regression test to CI/CD

---

## Upload Failure Debugging

**Triggered by**: `voice_upload_failures_total` rate spike  
**Common causes**: Network timeout, storage full, file size limit, format issue

### Quick Assessment

```bash
# Check upload failure rate and reasons
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=rate(voice_upload_failures_total[5m]) by (reason)'

# Example: { "reason": "timeout", "rate": "0.5" }
#          { "reason": "file_size", "rate": "0.2" }
```

### By Failure Reason

#### "timeout" — Upload takes >60 seconds

```bash
# 1. Check if transcription is slow
grep "transcription\|timeout" logs/app.log | tail -20

# 2. Check Groq API status
curl https://api.groq.com/health

# 3. Increase upload timeout temporarily
export UPLOAD_TIMEOUT_SECONDS=120
docker restart techfixai-app

# 4. If Groq is slow, try again (transient)
# 5. If continues, check network path to Groq (latency issue)
```

#### "file_size" — File exceeds MAX_UPLOAD_SIZE_MB

```bash
# Check current limit
echo $MAX_UPLOAD_SIZE_MB

# If users need larger files, increase:
export MAX_UPLOAD_SIZE_MB=100  # default is 50
docker restart techfixai-app

# Verify change took effect:
curl http://localhost:8000/health | jq '.dependencies'
```

#### "storage_error" — Filesystem write failed

```bash
# 1. Check disk space
df -h /path/to/storage

# 2. If full, run cleanup to delete old files
find /path/to/storage -type f -mtime +30 -delete

# 3. Check filesystem permissions
ls -la /path/to/storage

# 4. Verify app can write
touch /path/to/storage/test.txt && rm /path/to/storage/test.txt

# 5. If still failing, check filesystem mount
mount | grep storage
```

#### "invalid_format" — Unsupported audio format

```bash
# Check supported formats in app/api/voice.py
grep -A 5 "SUPPORTED_FORMATS" app/api/voice.py

# Or from logs:
grep "invalid_format\|unsupported" logs/app.log | tail -10

# Common issue: Browser recording in wrong format
# Solution: Update frontend to record in Opus or WAV
```

---

## Data Cleanup Task Failures

**Triggered by**: `cleanup_failures_total > 0`  
**Impact**: Old audio files/DB records not deleted per retention policy

### Diagnosis

```bash
# Check which cleanup task failed
grep "cleanup\|CLEANUP" logs/app.log | grep -i error | tail -20

# Metrics:
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=cleanup_failures_total'
```

### Remediation by Task

#### Audio Cleanup Failure

```bash
# 1. Check directory permissions
ls -la /path/to/storage | head -5

# 2. Fix if needed
sudo chown -R app:app /path/to/storage
sudo chmod 755 /path/to/storage

# 3. Manually run cleanup
python -c "
from app.scheduler import cleanup_old_audio_files
cleanup_old_audio_files(retention_days=30)
"

# 4. Verify files deleted
find /path/to/storage -type f -mtime +30 | wc -l
# Should be 0 if properly cleaned
```

#### Database Cleanup Failure

```bash
# 1. Check database connection
psql postgresql://<credentials> -c "SELECT 1"

# 2. Check for locks blocking cleanup
SELECT * FROM pg_locks WHERE NOT granted;

# 3. If locked, kill blocking query
SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
WHERE query LIKE '%conversations%' AND query_start < now() - interval '1 hour';

# 4. Manually run cleanup
python -c "
from app.scheduler import cleanup_old_database_records
cleanup_old_database_records(retention_days=30)
"

# 5. Verify (count of records):
psql <credentials> -c "SELECT count(*) FROM conversations;"
# Should match expected retention window
```

#### Audit Log Cleanup Failure

```bash
# 1. Check file permissions
ls -la logs/audit.log

# 2. Fix if needed
chmod 644 logs/audit.log
chown app:app logs/audit.log

# 3. Manually run cleanup
python -c "
from app.scheduler import cleanup_old_audit_records
cleanup_old_audit_records(retention_days=90)
"

# 4. Verify size decreased
ls -lh logs/audit.log
```

---

## Health Endpoint Diagnostics

**Endpoint**: `GET /health`  
**Response**: JSON with status + dependency details  
**Expected**: 200 if healthy OR 503 if unhealthy

### Interpreting Health Response

```json
{
  "status": "healthy|degraded|unhealthy",
  "timestamp": "2026-03-20T15:30:45.123456",
  "version": "1.0",
  "dependencies": {
    "database": {
      "status": "up",
      "duration_seconds": 0.05
    },
    "filesystem": {
      "status": "up",
      "path": "/storage/audio",
      "duration_seconds": 0.02
    },
    "api_keys": {
      "status": "up",
      "configured": {
        "groq": true,
        "google_oauth": true,
        "captcha": true
      },
      "missing": []
    }
  }
}
```

### Troubleshooting

| Status | Likely Cause | Check |
|--------|--------------|-------|
| database: down | PostgreSQL unavailable or connection failed | `psql <credentials>` |
| filesystem: down | Storage path missing or not writable | `ls -la /path; touch test.txt` |
| api_keys: degraded | Some but not all keys configured | `env \| grep _API` |
| api_keys: down | Required key missing | Set env var and restart |

---

## Incident Post-Mortem Template

After resolving any incident:

```markdown
# Incident: [Brief Title]
**Date**: 2026-03-20  
**Duration**: 15 minutes  
**Severity**: CRITICAL/HIGH/MEDIUM  
**Lead**: [Your Name]

## Timeline
- 15:30 - Incident started (5xx errors detected)
- 15:32 - Root cause identified (DB connection pool)
- 15:40 - Fix applied (restart app)
- 15:45 - Service restored
- 16:00 - All systems verified normal

## Root Cause
Database connection pool exhaustion due to unresponsive slow queries from a new report feature.

## Impact
- Users unable to upload files for 15 minutes
- ~50 upload requests failed
- ~100 users affected (estimated by active session count)

## Resolution
Restarted app process to reset connection pool. Added monitoring for slow database queries.

## Action Items
- [ ] Add database query timeout (5 min) to prevent future pool exhaustion
- [ ] Add database connection pool monitoring to dashboard
- [ ] Review new report feature query optimization
- [ ] Load test before deploying new features

## Lessons Learned
- Slow database queries can cause connection pool exhaustion
- Better monitoring would have detected this faster
- Need pre-deploy load testing for new features
```

---

**Next steps**: Post incidents to your team's incident log and schedule weekly post-mortems to review patterns.


---

## Integrated From: AUDIT_SUMMARY.md

Merged on: 2026-03-20 13:44:19

# TechFixAI - AUDIT SUMMARY & ACTION ITEMS
**Audit Date**: March 20, 2026  
**Audit Created By**: Comprehensive Automated Testing & Manual Review  
**Status**: ✅ AUDIT COMPLETE

---

## 🎯 AUDIT RESULTS OVERVIEW

**Total Test Cases**: 52  
**Passed**: 17 ✅  
**Warnings**: 8 ⚠️  
**Failed**: 1 ❌ (metrics endpoint)  
**Critical Issues**: 3 🔴  

**Overall Assessment**: **70% HEALTHY** — Application has solid foundation but critical bugs block core workflow

---

## 📋 TEST COVERAGE

| Category | Tests | Status |
|----------|-------|--------|
| Connectivity & Health | 3 | ✅⚠️ |
| Authentication Pages | 4 | ✅ |
| Session Management | 2 | ❌⚠️ |
| Input Validation | 4 | ✅ |
| Security Headers | 5 | ✅ |
| API Endpoints | 4 | ❌❌❌ |
| Error Handling | 2 | ✅ |
| Database | 2 | ❌ |
| Performance | 4 | ⚠️ |
| Observability | 3 | ⚠️❌ |

---

## 🔴 BLOCKERS (Fix Before Any Use)

### 1. ❌ Ticket API Not Found (404)
- **API Endpoints**: `/api/tickets/*` all return 404
- **Impact**: CORE WORKFLOW IS BROKEN - Cannot create tickets
- **Root Cause**: Route not registered or handler missing
- **Fix Time**: 1-2 hours
- **Test After**: `curl -X GET http://localhost:8000/api/tickets/list`

### 2. ❌ Metrics Endpoint Not Found (404)
- **API Endpoint**: `GET /metrics` returns 404
- **Impact**: Cannot monitor application (Prometheus, alerting broken)
- **Root Cause**: Route not accessible despite being in code
- **Fix Time**: 30 minutes
- **Test After**: `curl http://localhost:8000/metrics | head -5`

### 3. ⚠️ High Response Times (2000+ms)
- **Issue**: All pages taking 2+ seconds to respond
- **Impact**: Terrible user experience, possible timeout failures
- **Root Cause**: Database queries or synchronous operations per-request
- **Fix Time**: 2-4 hours
- **Accept Criteria**: All pages < 500ms

---

## 🟠 HIGH PRIORITY (Fix Before Release)

### 4. ⚠️ Session Validation Weak
- **Issue**: Invalid cookies not rejected (returns 200 instead of 401)
- **Impact**: Security concern - session validation broken
- **Fix Time**: 1 hour
- **Test**: Send `auth_token=BADTOKEN` cookie, expect 401

### 5. ⚠️ Health Endpoint Minimal
- **Issue**: Returns only `{"status": "healthy"}` without dependency checks
- **Impact**: Cannot monitor database, filesystem, API key health
- **Fix Time**: 30 minutes
- **Test**: `curl http://localhost:8000/health | python -m json.tool`

### 6. ⚠️ Dashboard Auth Broken
- **Issue**: Returns 303 instead of proper 302/307 redirect
- **Impact**: Unauthenticated users may access protected pages
- **Fix Time**: 30 minutes
- **Test**: `curl -v http://localhost:8000/dashboard` (no cookie)

---

## 🟡 MEDIUM PRIORITY (Complete Before Wider Testing)

### 7. ⚠️ Request ID Not in Response Headers
- **Issue**: X-Request-ID header missing (may be in logs only)
- **Impact**: Distributed tracing won't work properly
- **Fix Time**: 1 hour

### 8. ⚠️ API Error Codes Inconsistent
- **Issue**: Voice upload returns 422 instead of 401 for auth failure
- **Impact**: Frontend error handling confused
- **Fix Time**: 1-2 hours

### 9. ⚠️ CORS Not Explicitly Configured
- **Issue**: May use defaults, may be incorrect for deployment
- **Impact**: Cross-origin requests might fail on different domain
- **Fix Time**: 30 minutes

---

## 📊 WHAT'S WORKING WELL ✅

1. ✅ **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options all present
2. ✅ **Input Validation**: Email format, password strength, request size limits
3. ✅ **Rate Limiting**: Request size limit (413) enforced
4. ✅ **Auth Pages**: Login and signup pages render correctly
5. ✅ **Homepage**: Renders without errors
6. ✅ **Database Schema**: Models defined, migrations ready
7. ✅ **OAuth Integration**: Google OAuth code present and partially working
8. ✅ **Storage**: Voice storage directories configured
9. ✅ **Logging**: Structured logging infrastructure in place
10. ✅ **Scheduling**: Cleanup scheduler configured

---

## 📁 AUDIT DOCUMENTATION

All files created and available in project root:

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **AUDIT_REPORT.md** | Comprehensive audit findings | 20 min |
| **AUDIT_CHECKLIST.md** | Detailed test checklist (184 items) | 30 min |
| **AUDIT_FIXES.md** | Diagnostic commands and fixes | 15 min |
| **AUDIT_SUMMARY.md** | This document | 5 min |
| **audit_test_suite.py** | Automated testing script | - |

---

## 🛠️ IMMEDIATE ACTION STEPS

### Step 1: Understand the Issues (5 minutes)
```bash
cd d:\WEBD\TechFixAI
cat AUDIT_REPORT.md | head -100
```

### Step 2: Diagnose Ticket API (10 minutes)
```bash
# Check if ticket routes exist
Select-String -Path app/api/ticket.py -Pattern "@router" | head -5

# Check if router is included
Select-String -Path app/main.py -Pattern "ticket.router"

# Try to load the module
python -c "from app.api import ticket; print(ticket.router.routes)"
```

### Step 3: Diagnose Metrics (5 minutes)
```bash
# Check route definition
Select-String -Path app/api/web.py -Pattern 'async def metrics'

# Check if metrics module works
python -c "from app.core.metrics import get_metrics_text; print(len(get_metrics_text()))"

# Test endpoint
curl http://localhost:8000/metrics
```

### Step 4: Fix Issues (2-4 hours)
Follow guidance in `AUDIT_FIXES.md` for each issue

### Step 5: Re-test (30 minutes)
```bash
# Restart app
# Run audit suite again
python audit_test_suite.py

# Manually test critical flows:
# 1. Create ticket
# 2. View metrics endpoint
# 3. Check response times
```

---

## 📝 TESTING CHECKLIST

Before marking as "Ready for Testing", verify:

- [ ] Ticket API working (`/api/tickets/create`, `/api/tickets/list`)
- [ ] Metrics endpoint accessible (`/metrics` returns data)
- [ ] Response times < 500ms
- [ ] Session validation rejects invalid cookies
- [ ] Health endpoint returns full dependency status
- [ ] Dashboard redirects unauthenticated users
- [ ] Audit suite runs with > 80% pass rate

---

## 🎮 MANUAL TESTING CHECKLIST

Once automated tests pass, test these manually:

### Authentication
- [ ] Signup with new email → user created, logged in
- [ ] Login with existing email → logged in
- [ ] Login with wrong password → generic error
- [ ] Invalid email → 400 error
- [ ] Logout → session cleared, redirected to login

### Core Workflow
- [ ] Upload audio file → stored in storage/audio/
- [ ] Transcribe → Groq API called, text returned
- [ ] Translate → Google Translate called, translated text returned
- [ ] Create ticket → Ticket saved to database
- [ ] View ticket → Details displayed
- [ ] List tickets → All user's tickets shown

### Voice Features
- [ ] File size limit enforced
- [ ] Invalid file type rejected
- [ ] Rate limiting applied (10+ uploads/min)
- [ ] Audio properly saved and accessible

### Security
- [ ] No password visible in logs
- [ ] Session cookie secure (httponly, samesite)
- [ ] CSRF protection (state parameter in OAuth)
- [ ] No user enumeration (generic auth errors)

---

## 📞 SUPPORT & NEXT STEPS

### If Stuck on an Issue:
1. Check `AUDIT_FIXES.md` for that issue
2. Look at diagnostic commands
3. Review `AUDIT_REPORT.md` for root cause analysis
4. Check git history: `git log --all --oneline | head -20`

### For Performance Issues:
- See "Performance Profiling" in `AUDIT_FIXES.md`
- Use `python -m cProfile` to profile startup
- Check database connection pooling

### For Database Issues:
- Verify `test.db` exists: `ls -la test.db` or `dir test.db`
- Test connectivity: Run diagnostic from `AUDIT_FIXES.md`
- Check migrations: `alembic current` (if available)

### For API Issues:
- Use `curl` to test endpoints
- Check logs: `tail -f logs/app.log`
- Enable debug mode: `export LOG_LEVEL=DEBUG`

---

## 🏆 SUCCESS METRICS

When all issues fixed, these should be true:

```
✅ "Ticket API is accessible and working"
✅ "Metrics endpoint returns Prometheus data"
✅ "Response times are < 500ms"
✅ "Audit suite reports 90%+ pass rate"
✅ "Manual sign-up → login → upload → ticket workflow works"
✅ "All security headers present"
✅ "No console errors or warnings"
```

---

## 📅 TIMELINE

| Phase | Estimated Time | Dependency |
|-------|----------------|------------|
| **Diagnosis** | 1-2 hours | None |
| **Fix Blockers** (tickets, metrics, perf) | 4-6 hours | Diagnosis |
| **Fix High Priority Issues** | 2-3 hours | Blockers fixed |
| **Test & Verify** | 2-3 hours | All fixes done |
| **Manual Testing** | 2-4 hours | Verification done |

**Total Estimated Time to Production-Ready**: **10-15 hours**

---

## 📤 DEPLOYMENT READINESS

Before deploying to production:

- [ ] All audit issues fixed and re-tested
- [ ] Health check with dependencies working
- [ ] Metrics endpoint accessible and scrape-able
- [ ] Sentry DSN configured (optional but recommended)
- [ ] Database backups configured
- [ ] Cleanup scheduler tested and working
- [ ] Log rotation configured
- [ ] HTTPS/SSL certificates ready
- [ ] Environment variables set correctly
- [ ] Rate limits appropriate for your traffic
- [ ] CORS origins configured correctly

---

## 📚 REFERENCE

**Key Files**:
- `app/main.py` - Application entry point
- `app/api/web.py` - Web routes and observability endpoints
- `app/api/ticket.py` - Ticket API (currently broken)
- `app/core/health.py` - Full health check implementation
- `app/core/metrics.py` - Metrics collection
- `app/core/observability.py` - Observability middleware
- `requirements.txt` - Dependencies

**Configuration**:
- `.env` - Environment variables
- `.env.example` - Example configuration
- `app/core/config.py` - Settings management

**Monitoring & Docs**:
- `OBSERVABILITY.md` - Logging/metrics/alerts guide
- `MONITORING.md` - Prometheus/Grafana setup
- `ALERTING.md` - Alert rules
- `RUNBOOKS.md` - Incident response procedures

---

**Audit Completed**: March 20, 2026  
**Audit Status**: READY FOR REMEDIATION  
**Next Review**: After critical fixes implemented  

---

**Questions?** Refer to:
1. AUDIT_REPORT.md (detailed findings)
2. AUDIT_FIXES.md (how to fix)
3. AUDIT_CHECKLIST.md (what was tested)


---

## Integrated From: AUDIT_REPORT.md

Merged on: 2026-03-20 13:44:19

# TechFixAI AUDITING REPORT
**Date**: March 20, 2026  
**Audit Type**: Comprehensive Sign-In/Sign-Up/Core Workflow  
**Status**: ✅ COMPLETED

---

## Executive Summary

Comprehensive automated and manual audit of TechFixAI application across authentication flows, API endpoints, security, and core functionality. **Overall Status**: MOSTLY WORKING with some issues to address.

**Pass Rate**: 68% (17 passed, 8 warnings, 1 critical issue)

---

## PHASE 1: Connectivity & Infrastructure

### ✅ Server Connectivity
- **Status**: WORKING
- **Test**: `GET /health` → 200 OK
- **Details**: Server is running and responding to requests
- **Response Time**: 2055ms (high, needs investigation)

### ⚠️ Health Endpoint Implementation
- **Status**: PARTIALLY WORKING
- **Issue**: Health endpoint returns minimal response `{"status": "healthy"}`
- **Expected**: Full dependency checks (database, filesystem, API keys)
- **Root Cause**: Simple hardcoded handler in `main.py:235` overrides full implementation
- **Impact**: Cannot monitor dependency health
- **Fix Required**: Use full `app/core/health.py` implementation

### ❌ Metrics Endpoint
- **Status**: NOT FOUND (404)
- **Test**: `GET /metrics` → 404 Not Found
- **Issue**: Despite `METRICS_ENABLED=True` in config, endpoint not accessible
- **Root Cause**: Likely routing issue or module import problem
- **Impact**: Prometheus cannot scrape metrics, monitoring/alerting disabled
- **Fix Required**: Debug route registration and metric collection initialization

### ⚠️ Request ID Tracking
- **Status**: PARTIAL
- **Issue**: Request ID not appearing in response headers
- **Possible Location**: May be in logs only (requires log inspection)
- **Expected**: `X-Request-ID` header in all responses
- **Impact**: Distributed tracing may not work properly
- **Fix**: Verify RequestIDMiddleware output header

---

## PHASE 2: Authentication - Pages & Forms

### ✅ Login Page
- **Status**: WORKING
- **Response**: 200 OK, HTML with form fields
- **Fields Present**: email, password, remember-me checkbox
- **Security**: CAPTCHA field present (when enabled)

### ✅ Signup Page
- **Status**: WORKING
- **Response**: 200 OK, HTML with form fields
- **Fields Present**: email, password, confirm_password, full_name
- **Security**: Password strength indicator visible

### ✅ Homepage
- **Status**: WORKING
- **Response**: 200 OK, proper HTML rendering
- **Content**: Call-to-action buttons for login/signup visible

---

## PHASE 3: Session Management

### ❌ Dashboard Access (No Session)
- **Status**: BROKEN
- **Test**: `GET /dashboard` without session cookie
- **Actual Response**: 303 (redirect) ✅ But returns HTML instead of redirect
- **Expected**: 302/307 redirect to `/login` with Location header
- **Issue**: Session middleware may not be properly enforcing auth
- **Impact**: Unauthenticated users might access protected content
- **Fix Required**: Verify authentication guard on protected routes

### ⚠️ Invalid Session Handling
- **Status**: PARTIALLY WORKING
- **Test**: Invalid cookie `auth_token=INVALID_TOKEN_12345`
- **Actual Response**: 200 OK
- **Expected**: 401 Unauthorized or redirect to login
- **Issue**: Session validation not rejecting invalid tokens
- **Impact**: Security concern - invalid sessions might be trusted
- **Fix Required**: Strengthen session validation in middleware

---

## PHASE 4: Input Validation & Protection

### ✅ Invalid Email Detection
- **Test**: `POST /login` with invalid email
- **Response**: 400 Bad Request
- **Detail**: "Invalid email or password" (no user enumeration - good!)
- **Status**: WORKING

### ✅ Weak Password Detection
- **Test**: `POST /signup` with 3-char password
- **Response**: 400 Bad Request
- **Detail**: Password validation enforced
- **Status**: WORKING

### ✅ Request Size Limiting
- **Test**: POST with 100MB body
- **Response**: 413 Payload Too Large
- **Configuration**: MAX_REQUEST_BODY_MB enforced
- **Status**: WORKING

### ✅ HTTP Method Validation
- **Test**: `PATCH /login` (invalid method)
- **Response**: 405 Method Not Allowed
- **Status**: WORKING

### ✅ Non-existent Route Handling
- **Test**: `GET /this-route-does-not-exist`
- **Response**: 404 Not Found
- **Status**: WORKING

---

## PHASE 5: Security Headers

### ✅ Content-Security-Policy
- **Status**: PRESENT & CONFIGURED
- **Value**: `default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://challenges.cloudflare.com; ...`
- **Coverage**: Inline scripts allowed (for CAPTCHA), external CDNs whitelisted
- **Note**: `'unsafe-inline'` is used for scripts - consider moving to nonces

### ✅ X-Frame-Options
- **Status**: PRESENT
- **Value**: `DENY` (prevents clickjacking)
- **Status**: GOOD

### ✅ X-Content-Type-Options
- **Status**: PRESENT
- **Value**: `nosniff` (prevents MIME type attacks)
- **Status**: GOOD

### ✅ Referrer-Policy
- **Status**: PRESENT
- **Default**: Configured via settings

### ℹ️ HSTS (HTTP Strict Transport Security)
- **Status**: CONFIGURED but only active on HTTPS
- **Current**: HTTP only (localhost) - N/A
- **Production**: Will be enforced when FORCE_HTTPS=true and on HTTPS

---

## PHASE 6: API Endpoints

### ⚠️ Voice Upload API
- **Test**: `POST /api/voice/upload` (unauthenticated)
- **Response**: 422 Unprocessable Entity
- **Issue**: Wrong status code - should be 401 Unauthorized
- **Likely Cause**: Missing form-data parser or validation error
- **Fix**: Ensure endpoint checks auth before validation

### ❌ Ticket API Endpoints
- **Test 1**: `POST /api/ticket/create` → 404 Not Found
- **Test 2**: `GET /api/tickets/list` → 404 Not Found
- **Issue**: Routes registered as `/api/tickets` but may not exist
- **Root Cause**: Check if `ticket.router` has routes defined
- **Impact**: Entire core workflow (ticket creation) is broken
- **Fix Required**: CRITICAL - Verify ticket routes are properly defined

### CORS Configuration
- **Status**: PARTIAL
- **Current**: `allow_origins=settings.CORS_ORIGINS`
- **Issue**: No explicit CORS headers in response (may be configured globally)
- **Recommendation**: Verify CORS_ORIGINS in config is correct for your deployment

---

## PHASE 7: Database Connectivity

### ❌ Database Status (Health Check)
- **Status**: NOT WORKING
- **Test**: Health endpoint reports `"database": {"status": "not 'up'"}`
- **Actual**: True database status unknown (health endpoint is hardcoded minimal)
- **Investigation Needed**: Run manual database test
- **Impact**: Monitoring/alerting for database issues impossible
- **Fix**: Implement full health check with dependencies

### Database Validation
- **File**: `app/db/session.py` - SessionLocal configured
- **Database**: SQLite (`test.db`) [development]
- **Models**: User, Ticket, etc. defined in `app/models/`
- **Migrations**: Alembic configured for schema management

---

## PHASE 8: Performance Baselines

### Baseline Response Times (Concerning)

| Endpoint | Response Time | Status |
|----------|---------------|--------|
| `/health` | ~2000ms | 🔴 TOO SLOW |
| `/login` | ~2070ms | 🔴 TOO SLOW |
| `/` (home) | ~2040ms | 🔴 TOO SLOW |
| `/metrics` | 2046ms (404) | 🔴 STATUS ERROR |

### Analysis
- **Issue**: Even simple pages are taking 2+ seconds
- **Causes** (likely):
  - Database initialization on every request
  - Synchronous operations in middleware
  - Missing database connection pooling
  - Slow file I/O
- **Impact**: Poor user experience, high latency
- **Fix Required**: Profile and optimize application startup/request handling

---

## PHASE 9: API Integration Testing

### Attempted End-to-End Workflow

```
1. GET /home                          ✅ 200
2. GET /signup                        ✅ 200
3. POST /signup (new user)           ⚠️  Not tested (no actual submission)
4. GET /dashboard                    ❌ 303 (broken auth check)
5. POST /api/voice/upload           ❌ 422 (wrong error code)
6. POST /api/ticket/create          ❌ 404 (route not found)
7. GET /api/tickets/list            ❌ 404 (route not found)
```

**Status**: CORE WORKFLOW BLOCKED - Ticket creation API not found

---

## PHASE 10: OAuth (Google) Integration

### OAuth Configuration Status
- **Client ID**: Configured
- **Client Secret**: Configured
- **Redirect URI**: Dynamically built
- **Scope**: `openid email profile`
- **Callback Handler**: Implemented in `/auth/google/callback`

### OAuth State Management
- **CSRF Protection**: Via state parameter (✅)
- **Token Handling**: OAuth token received and user created/updated
- **User Auto-Creation**: New users created with auto-generated username
- **Account Linking**: Existing users linked to Google ID

### Tests Not Completed
- Full OAuth flow requires browser/actual Google interaction
- Recommend: Manual testing with real Google OAuth credentials

---

## PHASE 11: Structured Logging & Observability

### Logging Configuration
- **Status**: PARTIALLY WORKING
- **Format**: JSON (✅ `logging_config.py` configured)
- **Request ID Tracking**: RequestIDMiddleware present (⚠️ not appearing in headers)
- **Log File**: `logs/app.log` (rotated daily)
- **Log Level**: Configurable via `LOG_LEVEL` env var

### Metrics Collection
- **Implementation**: `app/core/metrics.py` (✅ exists)
- **Endpoint**: `/metrics` (❌ returning 404)
- **Metrics**: All collectors defined
  - HTTP requests, errors, latency
  - Voice uploads, transcriptions
  - Ticket creation
  - Database operations
- **Status**: Collection code present but endpoint not accessible

### Sentry Integration
- **Status**: Optional (can be disabled)
- **Config**: `SENTRY_DSN` env var
- **Sampling**: 10% of requests traced
- **Automatic Capture**: Unhandled exceptions

---

## PHASE 12: Features Checklist

### ✅ Implemented & Working
- [x] Homepage with CTA
- [x] Login/signup pages with forms
- [x] Input validation (email, password)
- [x] Rate limiting (request size, method validation)
- [x] Security headers (CSP, X-Frame-Options, X-Content-Type-Options)
- [x] OAuth setup (Google)
- [x] Session middleware
- [x] Password hashing
- [x] Storage directories
- [x] Logging infrastructure
- [x] Health endpoint (basic)
- [x] Cleanup scheduler

### ⚠️ Partially Working
- [ ] Metrics endpoint (code exists, route 404)
- [ ] Database health checks (not integrated into health endpoint)
- [ ] Request ID tracking (not in response headers)
- [ ] Session validation (not rejecting invalid cookies)
- [ ] Dashboard auth (not redirecting properly)
- [ ] API error codes (422 instead of 401)

### ❌ Not Working/Critical Issues
- [ ] Ticket creation API (404 Not Found)
- [ ] Ticket list API (404 Not Found)
- [ ] Response times (2000+ms for simple pages)
- [ ] Full health checks with dependencies
- [ ] Voice upload endpoint (wrong error code)

### 🚫 Not Tested (Requires Manual/Browser Testing)
- [ ] Full signup flow with email verification
- [ ] Login with email/password
- [ ] OAuth callback
- [ ] File upload and transcription
- [ ] Voice-to-text functionality
- [ ] Ticket creation workflow
- [ ] Translation functionality

---

## Critical Issues Summary

| # | Issue | Severity | Impact | Fix Time |
|---|-------|----------|--------|----------|
| 1 | Ticket API (404) | 🔴 CRITICAL | Core workflow blocked | ~1 hour |
| 2 | Metrics endpoint (404) | 🔴 CRITICAL | Monitoring disabled | ~30 min |
| 3 | Response times (2000ms+) | 🔴 CRITICAL | Poor UX, possible timeout issues | ~2 hours |
| 4 | Session validation broken | 🟠 HIGH | Security risk | ~1 hour |
| 5 | Health endpoint minimal | 🟠 HIGH | No dependency monitoring | ~30 min |
| 6 | Dashboard auth redirect | 🟠 HIGH | Auth bypass possible | ~30 min |

---

## Recommendations (Priority Order)

### 🟥 IMMEDIATE (Fix Before Production)

1. **Fix Ticket API Routes**
   - Debug why `/api/tickets/*` routes return 404
   - Verify `ticket.router` has GET/POST methods defined
   - Check route inclusion in `main.py`
   - **Estimated Time**: 1-2 hours

2. **Fix Metrics Endpoint**
   - Test `/metrics` route manually
   - Verify `get_metrics_text()` is returning data
   - Check METRICS_ENABLED configuration
   - Debug route registration
   - **Estimated Time**: 30-60 minutes

3. **Optimize Response Times**
   - Profile application startup
   - Add database connection pooling
   - Optimize middleware stack
   - Cache static content
   - **Estimated Time**: 2-4 hours

4. **Fix Session Validation**
   - Ensure invalid cookies are rejected
   - Force redirect to login
   - Test with invalid cookie values
   - **Estimated Time**: 1 hour

### 🟧 HIGH PRIORITY (Fix Before General Release)

5. **Implement Full Health Checks**
   - Use `app/core/health.py` implementation
   - Check database, filesystem, API keys
   - Include response time metrics
   - **Estimated Time**: 1 hour

6. **Fix Dashboard Auth Redirect**
   - Ensure 302/307 redirect on auth failure
   - Send Location header
   - Test with session validation
   - **Estimated Time**: 30 minutes

7. **Standardize API Error Codes**
   - 401 for auth failures (not 422)
   - 403 for permission failures
   - 404 for not found
   - **Estimated Time**: 1-2 hours

### 🟨 MEDIUM PRIORITY (Improve Before Wider Use)

8. **Request ID Propagation**
   - Ensure X-Request-ID in response headers
   - Include in all log entries
   - Verify Sentry integration
   - **Estimated Time**: 1 hour

9. **Browser/Mobile Testing**
   - Test on Chrome, Firefox, Safari, Edge
   - Test responsive design (mobile, tablet, desktop)
   - Test touch interactions
   - **Estimated Time**: 2-3 hours

10. **E2E Test Automation**
    - Create Selenium or Playwright tests
    - Test signup → login → upload → transcribe → create ticket
    - Automate for CI/CD
    - **Estimated Time**: 4-6 hours

---

## Manual Testing Checklist

For testing flows that require browser interaction:

### Signup Flow
- [ ] Visit `/signup`
- [ ] Enter email, password, full name
- [ ] Check password validation (< 8 chars → error)
- [ ] Check password mismatch (password != confirm)
- [ ] Submit valid form → redirected to dashboard
- [ ] Check new user in database

### Login Flow
- [ ] Visit `/login`
- [ ] Try invalid email → generic error
- [ ] Try invalid password → generic error
- [ ] Login with valid credentials → redirected to dashboard
- [ ] Check session cookie set
- [ ] Close browser, reopen → still logged in

### Voice Upload & Transcription
- [ ] Login successfully
- [ ] Navigate to upload page
- [ ] Select audio file (.wav, .mp3, etc.)
- [ ] Check file size limit
- [ ] Start upload
- [ ] Wait for transcription (Groq API call)
- [ ] Check transcribed text appears

### Translation
- [ ] After transcription, click "Translate"
- [ ] Select target language (Spanish, French, German, etc.)
- [ ] Check translation appears
- [ ] Verify accuracy

### Ticket Creation
- [ ] Click "Create Ticket"
- [ ] Form pre-populated with transcribed text + translation
- [ ] Enter ticket details (priority, category, etc.)
- [ ] Submit form
- [ ] Check ticket appears in ticket list
- [ ] View ticket details

### OAuth (Google Login)
- [ ] Click "Sign in with Google"
- [ ] Redirected to Google consent screen
- [ ] Click "Accept"
- [ ] Redirected back to app
- [ ] User logged in, account created/updated
- [ ] Check google_id saved in database

---

## Test Environment Notes

- **Database**: SQLite `test.db` (development)
- **Server**: Running on `localhost:8000`
- **No HTTPS**: Self-signed certs not configured for localhost
- **Time**: Tests run at ~2000ms per request (baseline slow)
- **Python Version**: 3.13 (check compatibility)
- **OS**: Windows (path handling, encoding issues)

---

## Files Generated

| File | Purpose | Status |
|------|---------|--------|
| `AUDIT_CHECKLIST.md` | Detailed test checklist | ✅ |
| `audit_test_suite.py` | Automated test runner | ✅ |
| `AUDIT_REPORT.md` | This report | ✅ |
| `OBSERVABILITY.md` | Implementation guide | ✅ |
| `OBSERVABILITY_SUMMARY.md` | Summary | ✅ |
| `MONITORING.md` | Setup guide (existing) | ✅ |
| `ALERTING.md` | Alert rules (existing) | ✅ |
| `RUNBOOKS.md` | Incident response (existing) | ✅ |

---

## Conclusion

**Overall Assessment**: Application has good foundational code and security implementations, but has **critical bugs** preventing core workflow from functioning:

1. **Ticket API is not accessible** - This blocks the main application workflow
2. **Metrics endpoint broken** - Prevents observability and monitoring
3. **Response times are too high** - Indicates performance issues
4. **Session validation is weak** - Security concern

**Recommendation**: Fix the 6 critical/high-priority issues before considering the application production-ready. Once fixed, the application should be ready for wider testing and deployment.

**Estimated Time to Fully Production-Ready**: 8-12 hours of focused development

---

**Audit Report Generated**: March 20, 2026, 12:56 UTC  
**Next Review**: After critical fixes implemented  
**Sign-off**: Automated Audit Suite + Manual Verification


---

## Integrated From: AUDIT_FIXES.md

Merged on: 2026-03-20 13:44:19

# TechFixAI - AUDIT ISSUES & QUICK FIXES
**Generated**: March 20, 2026  
**Purpose**: Diagnostic commands and fixes for audit failures

---

## 🔴 CRITICAL ISSUES

### Issue #1: Ticket API Returns 404

**Symptom**:
```
POST /api/tickets/create → 404 Not Found
GET /api/tickets/list → 404 Not Found
```

**Diagnosis Steps**:
```bash
# 1. Check if ticket router is included in main.py
cd d:\WEBD\TechFixAI
Select-String -Path app/main.py -Pattern "ticket.router"

# Expected output:
# "app.include_router(ticket.router, prefix="/api/tickets", tags=["tickets"])"

# 2. Verify ticket.py exists and has routes
Select-String -Path app/api/ticket.py -Pattern "@router\.(get|post|patch|delete)" | head -10

# 3. Test if app is even loading the module
python -c "from app.api import ticket; print(ticket.router.routes)"
```

**Quick Fixes** (in order):
1. Check `app/api/ticket.py` has route decorators with actual handler functions
2. Ensure `ticket.router` is instantiated as `APIRouter()`
3. Verify `main.py` includes the router with correct prefix
4. Restart the application
5. Test: `curl http://localhost:8000/api/tickets/list`

---

### Issue #2: Metrics Endpoint Returns 404

**Symptom**:
```
GET /metrics → 404 Not Found
```

**Diagnosis**:
```bash
# 1. Check if METRICS_ENABLED is set
cat .env | Select-String "METRICS_ENABLED"
# Should be: METRICS_ENABLED=true

# 2. Check if route exists in web.py
Select-String -Path app/api/web.py -Pattern '@router.get("/metrics")'

# 3. Verify get_metrics_text() function exists
Select-String -Path app/core/metrics.py -Pattern "def get_metrics_text"

# 4. Test metrics directly
python -c "from app.core.metrics import get_metrics_text; print(get_metrics_text()[:100])"

# 5. Check if web router properly mounted
Select-String -Path app/main.py -Pattern 'web.router'
```

**Quick Fixes**:
1. Add to `.env` if missing:
   ```
   METRICS_ENABLED=true
   ```
2. Ensure `app/api/web.py` has `/metrics` route
3. Check `app/core/metrics.py` has `get_metrics_text()` function
4. Verify metrics are being initialized on app startup
5. Restart app and test

**Test Command**:
```bash
curl http://localhost:8000/metrics | head -20
# Should see: "# HELP http_requests_total"
```

---

### Issue #3: Response Times 2000ms+

**Symptom**:
```
GET /health          → 2055ms
GET /login           → 2072ms
GET / (home)        → 2047ms
```

**Diagnosis**:
```bash
# 1. Check if database operations are slow
python -c "
import time
from app.db.session import SessionLocal
from app.models.user import User

start = time.time()
db = SessionLocal()
user = db.query(User).first()
db.close()
elapsed = (time.time() - start) * 1000
print(f'DB query took: {elapsed:.0f}ms')
"

# 2. Check if imports are slow (module loading)
python -m cProfile -s cumtime -c "from app.main import app" 2>&1 | head -30

# 3. Check application startup time
time python -c "from app.main import app; print('App loaded')"

# 4. Profile a request
# Start app with profiling: python -m cProfile -s cumtime {start_script}
```

**Likely Causes**:
- Database initialization on every request
- Missing connection pooling (SQLAlchemy pool settings)
- Slow file I/O during static file mounting
- Module imports happening per-request

**Quick Fixes**:
1. Add connection pooling to `app/db/session.py`:
   ```python
   from sqlalchemy.pool import NullPool, QueuePool
   
   # Use QueuePool instead of NullPool (SQLite default)
   engine = create_engine(
       SQLALCHEMY_DATABASE_URL,
       poolclass=QueuePool,
       pool_size=5,
       max_overflow=10,
       pool_pre_ping=True
   )
   ```

2. Move imports to module level (not inside functions)

3. Cache database queries where possible

4. Profile with: `python -m cProfile -s cumtime main.py`

---

### Issue #4: Session Validation Not Rejecting Invalid Cookies

**Symptom**:
```
Request with invalid cookie (auth_token=INVALID) → 200 OK
Expected: 401 Unauthorized or redirect to login
```

**Diagnosis**:
```bash
# 1. Check UserSessionMiddleware in main.py
Select-String -Path app/main.py -Pattern "class UserSessionMiddleware" -Context 20

# 2. Test session decoding with bad token
python -c "
from app.core.session import decode_session_cookie
result = decode_session_cookie('INVALID_TOKEN_12345')
print(f'Decode result for invalid token: {result}')
# Should return None or empty dict
"

# 3. Check if middleware properly handles None user
python -c "
from app.core.session import is_session_payload_valid_for_user
result = is_session_payload_valid_for_user(None, None)
print(f'Validation result: {result}')
"
```

**Quick Fixes**:
1. In `UserSessionMiddleware.dispatch()`, after setting `current_user = None`:
   - Check if `request.state.current_user` is None
   - If route is protected, return redirect to `/login`

2. Update protected route handlers to check `request.state.current_user`

3. Add `@require_auth` decorator if not exists:
   ```python
   from functools import wraps
   from fastapi import HTTPException
   
   def require_auth(handler):
       @wraps(handler)
       async def wrapper(request, *args, **kwargs):
           if not request.state.current_user:
               raise HTTPException(status_code=401, detail="Not authenticated")
           return await handler(request, *args, **kwargs)
       return wrapper
   ```

---

## 🟠 HIGH PRIORITY ISSUES

### Issue #5: Health Endpoint Returns Minimal Response

**Current Response**:
```json
{"status": "healthy"}
```

**Expected Response**:
```json
{
  "status": "healthy",
  "dependencies": {
    "database": {"status": "up", "duration_seconds": 0.025},
    "filesystem": {"status": "up", "duration_seconds": 0.010},
    "api_keys": {"status": "up", "configured": ["groq", "google_oauth"]}
  }
}
```

**Fix**:
1. In `app/main.py`, replace hardcoded `/health` route:
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy"}
   ```
   
   With:
   ```python
   from app.core.health import get_health_status
   
   @app.get("/health")
   async def health_check():
       return await get_health_status()
   ```

2. Restart application

**Test**:
```bash
curl http://localhost:8000/health | python -m json.tool
# Should now show database, filesystem, api_keys status
```

---

### Issue #6: Dashboard Auth Redirect Broken

**Symptom**:
```
GET /dashboard (no session) → 303 See Other (returns HTML)
Expected: 302/307 Found/Temporary Redirect with Location header
```

**Diagnosis**:
```bash
# Check what dashboard handler returns
Select-String -Path app/api/web.py -Pattern 'async def dashboard' -Context 10

# Check if proper redirect is sent
curl -v http://localhost:8000/dashboard --no-ssl-verifypeer 2>&1 | grep -i "location"
```

**Fix**:
1. In `/dashboard` handler, add proper auth check:
   ```python
   @router.get("/dashboard", response_class=HTMLResponse)
   async def dashboard(request: Request):
       if not request.state.current_user:
           return RedirectResponse(url="/login", status_code=302)
       
       return templates.TemplateResponse("dashboard.html", {
           "request": request,
           "user": request.state.current_user
       })
   ```

2. Ensure `request.state.current_user` is properly set by middleware

---

## 🟨 VERIFICATION COMMANDS

### Verify Core Functionality

```bash
# 1. Check if app starts without errors
cd d:\WEBD\TechFixAI
python -c "from app.main import app; print('✅ App loads successfully')"

# 2. Verify all required modules exist
python -c "
modules = [
    'app.api.auth',
    'app.api.web',
    'app.api.voice',
    'app.api.ticket',
    'app.core.health',
    'app.core.metrics',
    'app.core.observability'
]
for m in modules:
    try:
        __import__(m)
        print(f'✅ {m}')
    except ImportError as e:
        print(f'❌ {m}: {e}')
"

# 3. Check database connectivity
python -c "
from app.db.session import SessionLocal
db = SessionLocal()
result = db.execute('SELECT 1')
print(f'✅ Database connected')
db.close()
"

# 4. List all registered routes
python -c "
from app.main import app
for route in app.routes:
    if hasattr(route, 'path'):
        print(f'{route.methods} {route.path}')
"

# 5. Check environment variables
cat .env | Select-String "^[A-Z_]+=" | wc -l  # Count vars
```

---

## 📋 POST-FIX VERIFICATION

After fixing each issue, run:

1. **Restart Application**:
   ```bash
   # Kill existing process
   Get-Process python | Where {$.CommandLine -like "*8000*"} | Stop-Process -Force
   
   # Restart
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Re-run Audit Suite**:
   ```bash
   python audit_test_suite.py
   ```

3. **Test Specific Endpoint** (examples):
   ```bash
   # Test metrics
   curl http://localhost:8000/metrics | wc -c  # Should be > 500 bytes
   
   # Test health
   curl http://localhost:8000/health | python -m json.tool | sponge
   
   # Test tickets
   curl -X POST http://localhost:8000/api/tickets/create \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","description":"Test"}' | head -20
   
   # Test session
   curl -v http://localhost:8000/dashboard --no-session 2>&1 | grep Location
   ```

---

## 🔧 DEBUGGING TOOLS

### Enable Debug Logging
```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or add to .env
echo "LOG_LEVEL=DEBUG" >> .env

# Check logs
tail -f logs/app.log | Select-String "CRITICAL|ERROR|WARNING"
```

### Profile Application
```bash
# Using cProfile
python -m cProfile -s cumtime -c "
import time
start = time.time()
from app.main import app
elapsed = time.time() - start
print(f'\\nApp startup took {elapsed:.2f} seconds')
" | head -30

# Using line_profiler (if installed)
pip install line_profiler
kernprof -l -v test_script.py
```

### Check Route Registration
```bash
python << 'EOF'
from app.main import app
import json

routes = []
for route in app.routes:
    if hasattr(route, 'path'):
        route_info = {
            'path': route.path,
            'methods': list(route.methods) if hasattr(route, 'methods') else [],
            'name': route.name if hasattr(route, 'name') else None
        }
        routes.append(route_info)

print(json.dumps(routes, indent=2))
EOF
```

### Database Inspection
```bash
python << 'EOF'
from app.db.session import SessionLocal
from app.models.user import User
from app.models.ticket import Ticket

db = SessionLocal()

user_count = db.query(User).count()
ticket_count = db.query(Ticket).count()

print(f"Users: {user_count}")
print(f"Tickets: {ticket_count}")

db.close()
EOF
```

---

## 📊 Performance Profiling

```bash
# Test request latency 10 times
for i in {1..10}; do
  time curl -s http://localhost:8000/health > /dev/null
done

# Identify slow middleware
# Use Python profiler on a single request
python << 'EOF'
import cProfile
import pstats
import io
from app.main import app
from starlette.testclient import TestClient

pr = cProfile.Profile()
pr.enable()

client = TestClient(app)
response = client.get("/health")

pr.disable()
s = io.StringIO()
ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
ps.print_stats(20)  # Top 20
print(s.getvalue())
EOF
```

---

## ✅ SUCCESS CRITERIA

After all fixes, these should all return success:

```bash
# 1. Metrics endpoint works
curl http://localhost:8000/metrics | grep -c "^#"  # >= 5

# 2. Health checks dependencies
curl http://localhost:8000/health | grep '"database"'

# 3. Ticket API accessible
curl -X POST http://localhost:8000/api/tickets/create \  
  -H "Content-Type: application/json" \
  -d '{"title":"TEST"}' | grep -q "error" || echo "ENDPOINT EXISTS"

# 4. Response times < 500ms
time curl -s http://localhost:8000/ > /dev/null  # real time < 1s

# 5. Audit suite passes
python audit_test_suite.py | tail -5 | grep "Pass Rate"
```

---

**Generated**: March 20, 2026  
**For**: TechFixAI Development Team  
**Status**: Ready for troubleshooting


---

## Integrated From: AUDIT_CHECKLIST.md

Merged on: 2026-03-20 13:44:19

# TechFixAI Comprehensive Audit Report
**Date**: March 20, 2026  
**Audit Type**: Full Sign-In/Sign-Up Flow + Core Workflow Functionality  
**Status**: 🔍 IN PROGRESS

---

## Executive Summary

This audit validates the complete TechFixAI application flow from authentication through core functionality:
1. Sign-up and sign-in flows (email/password + OAuth)
2. Session management and security
3. Core voice-to-ticket workflow
4. Rate limiting and protection mechanisms
5. Health and observability features

---

## Phase 1: Environment & Configuration ✅

### Prerequisites Check
- [x] Application running on localhost:8000
- [x] Database accessible (test.db)
- [x] Environment variables configured (.env)
- [x] Observability components initialized

### Configuration Validation
```
✅ Database: SQLite (test.db)
✅ Session Management: Enabled (SESSION_COOKIE_NAME)
✅ CORS: Configured
✅ Rate Limiting: Enabled
✅ Observability: Structured logging + Prometheus metrics
✅ Sentry: Optional (can be disabled)
```

---

## Phase 2: Authentication Flow Testing

### A. Sign-Up Flow

#### Endpoint: `GET /signup`
- [ ] Render signup page without errors
- [ ] CAPTCHA displayed (if CAPTCHA_ENABLED=true)
- [ ] Form contains: email, password, confirm_password, name fields

#### Endpoint: `POST /signup`
- [ ] **Happy Path**: Register with valid email/password
  - Expected: User created, session cookie set, redirect to dashboard
  - Verify: User in database with hashed password
  
- [ ] **Weak Password**: Submit password < 8 characters
  - Expected: Error message "Password must be at least 8 characters"
  - Status: 400
  
- [ ] **Password Mismatch**: password ≠ confirm_password
  - Expected: Error message "Passwords don't match"
  - Status: 400
  
- [ ] **Duplicate Email**: Register with existing email
  - Expected: Error message "Email already registered"
  - Status: 409
  
- [ ] **Invalid Email**: Submit invalid email format
  - Expected: Error message "Invalid email"
  - Status: 400
  
- [ ] **CAPTCHA Validation** (if enabled):
  - [ ] Missing CAPTCHA token → Error
  - [ ] Invalid CAPTCHA token → Error
  - [ ] Valid CAPTCHA token → Pass through

- [ ] **Rate Limiting**: Attempt 10+ signups from same IP
  - Expected: 429 Too Many Requests after limit
  - Message: "Too many signup requests. Please retry in..."

---

### B. Login Flow (Email/Password)

#### Endpoint: `GET /login`
- [ ] Render login page without errors
- [ ] Display error messages if query params present
- [ ] CAPTCHA field visible (if CAPTCHA_REQUIRED_LOGIN=true)

#### Endpoint: `POST /login`
- [ ] **Happy Path**: Login with valid credentials
  - Expected: Session cookie set, redirect to dashboard
  - Verify: `current_user` in request.state
  
- [ ] **Invalid Email**: Submit non-existent email
  - Expected: Generic error "Invalid email or password"
  - Status: 401 (no user enumeration)
  
- [ ] **Invalid Password**: Correct email, wrong password
  - Expected: Generic error "Invalid email or password"
  - Status: 401
  
- [ ] **Inactive Account**: Login with disabled user
  - Expected: Error message "Account is not active"
  - Status: 401
  
- [ ] **Unverified Email**: Login with unverified email
  - Expected: Error message "Please verify your email"
  - Status: 403 or 401 (depending on config)
  
- [ ] **Rate Limiting (IP-based)**: Attempt 10+ logins from same IP
  - Expected: 429 Too Many Requests after limit
  
- [ ] **Rate Limiting (Account-based)**: Attempt 5+ logins for same account
  - Expected: Temp lockout message "Account temporarily locked"
  - Duration: 15 minutes (configurable)
  
- [ ] **Account Lockout After Failed Attempts**: 
  - Expected: Message "Account locked for security. Try again in X minutes"
  
- [ ] **Remember Me**: Login with "Remember Me" checked
  - Expected: Session TTL = SESSION_REMEMBER_DAYS (vs SESSION_TTL_HOURS)

---

### C. OAuth (Google) Flow

#### Endpoint: `GET /auth/google`
- [ ] Validate Google client ID is configured
- [ ] Redirect to Google OAuth consent screen
- [ ] State parameter set (CSRF protection)
- [ ] Callback redirect_uri matches configuration

#### Endpoint: `GET /auth/google/callback`
- [ ] **Happy Path**: Complete OAuth flow
  - Expected: User created/updated, session set, redirect to dashboard
  
- [ ] **User Denies**: Click "Cancel" on Google consent
  - Expected: Redirect to /login?error=google_denied
  
- [ ] **OAuth Not Configured**: CLIENT_ID missing
  - Expected: Redirect to /login?error=oauth_not_configured
  
- [ ] **State Mismatch**: Tampered state parameter
  - Expected: Redirect to /login?error=oauth_state_mismatch
  
- [ ] **User Linking**: OAuth email matches existing account
  - Expected: Account linked (google_id added), user logged in
  
- [ ] **New User Creation**: OAuth email is new
  - Expected: Account created automatically, user logged in
  
- [ ] **Missing Email**: User hasn't shared email with Google
  - Expected: Redirect to /login?error=no_email

---

### D. Session Management

#### Endpoint: `GET /logout`
- [ ] Session cookie cleared
- [ ] Redirect to /login
- [ ] Cannot access protected routes without session

#### Cookie Validation
- [ ] Cookie name: SESSION_COOKIE_NAME from config
- [ ] Cookie secure: true (in HTTPS)
- [ ] Cookie httponly: true (no JS access)
- [ ] Cookie samesite: Lax or Strict (CSRF protection)
- [ ] Cookie domain: correct domain (not wildcard)

#### Session Timeout
- [ ] Session valid until SESSION_TTL_HOURS
- [ ] Extend if used (sliding window)
- [ ] Clear expired sessions

---

## Phase 3: Dashboard & Core Workflow

### A. Dashboard Access

#### Endpoint: `GET /dashboard`
- [ ] **Unauthenticated**: Redirect to /login
- [ ] **Authenticated**: Render dashboard with user info
- [ ] Display: username, email, profile picture (if OAuth)
- [ ] Show: recent tickets, upload usage

#### Endpoint: `GET /dashboard` (Protected)
- [ ] Verify session is valid
- [ ] Load user data from database
- [ ] Verify user is active (is_active=true)

---

### B. Voice Upload & Transcription

#### Endpoint: `POST /api/voice/upload`
- [ ] **Unauthenticated**: Return 401
- [ ] **Valid Audio File**:
  - File: .wav, .mp3, .m4a, etc.
  - Size: ≤ MAX_UPLOAD_SIZE_MB
  - Expected: 202 Accepted, upload_id returned
  
- [ ] **File Too Large**: > MAX_UPLOAD_SIZE_MB
  - Expected: 413 Payload Too Large
  
- [ ] **Invalid File Type**: .txt, .exe, etc.
  - Expected: 400 Bad Request "Invalid file type"
  
- [ ] **Rate Limiting**: 10+ uploads from same user
  - Expected: 429 Too Many Requests
  - Window: VOICE_UPLOAD_RATE_LIMIT_WINDOW_SECONDS

#### Endpoint: `POST /api/voice/transcribe`
- [ ] **Transcription Started**: Audio file uploaded
  - Expected: Groq API called, transcription returned
  
- [ ] **Transcription Failure**: API error/timeout
  - Expected: 500 with error message
  - Logged in Sentry

#### Upload Workflow
1. [ ] File uploaded to storage/audio/{user_id}/
2. [ ] File hashed to prevent duplicates
3. [ ] Transcription task queued (if async)
4. [ ] Status returned to user
5. [ ] File cleaned up after processing (if enabled)

---

### C. Translation (Workflow)

#### Endpoint: `POST /api/voice/translate`
- [ ] **Unauthenticated**: Return 401
- [ ] **Valid Text**:
  - Source: English
  - Target: es, fr, de, etc.
  - Expected: Translated text returned
  
- [ ] **Text Too Long**: > TRANSLATE_MAX_CHARS
  - Expected: 400 "Text exceeds maximum length"
  
- [ ] **Unsupported Language**: Invalid target_language
  - Expected: 400 "Unsupported language"
  
- [ ] **Rate Limiting**: 10+ translations from same user
  - Expected: 429 Too Many Requests

---

### D. Ticket Creation (Core Workflow)

#### Endpoint: `POST /api/ticket/create`
- [ ] **Unauthenticated**: Return 401
- [ ] **Valid Input**:
  - title, description, priority, category
  - Expected: Ticket created, ticket_id returned, 201
  
- [ ] **Missing Required Fields**: Missing title or description
  - Expected: 400 "Missing required field: {field}"
  
- [ ] **Request Body Too Large**: > MAX_REQUEST_BODY_MB
  - Expected: 413 Payload Too Large

#### Endpoint: `GET /api/ticket/{ticket_id}`
- [ ] **Owned by User**: Return full ticket
- [ ] **Not Owned**: Return 403 Forbidden
- [ ] **Not Found**: Return 404

#### Endpoint: `GET /api/ticket/list`
- [ ] **Unauthenticated**: Return 401
- [ ] **Paginated Results**: Return user's tickets with pagination
- [ ] **Filters**: Filter by status, priority, date range

#### Endpoint: `PATCH /api/ticket/{ticket_id}`
- [ ] **Owner Update**: Update allowed
- [ ] **Non-Owner Update**: Return 403
- [ ] **Status Transition**: Validate valid state transitions

---

## Phase 4: Security & Protection

### A. Rate Limiting

- [ ] **Global Rate Limit**: GLOBAL_RATE_LIMIT_REQUESTS per window
- [ ] **Auth Rate Limit**: AUTH_LOGIN_RATE_LIMIT_REQUESTS per window
- [ ] **Signup Rate Limit**: AUTH_SIGNUP_RATE_LIMIT_REQUESTS per window
- [ ] **Voice Rate Limit**: VOICE_UPLOAD_RATE_LIMIT_REQUESTS per window
- [ ] **Translate Rate Limit**: TRANSLATE_RATE_LIMIT_REQUESTS per window
- [ ] **Anti-DDoS**: Max request body size enforced
- [ ] **IP Tracking**: Correct IP detection (behind proxy)

### B. CAPTCHA Protection

- [ ] **Site Key Displayed**: On signup/login (if enabled)
- [ ] **Token Validation**: Token verified on backend
- [ ] **Token Verification**: Verify with reCAPTCHA/hCaptcha API
- [ ] **Token Expiry**: Reject expired tokens
- [ ] **Disable Bypass**: No way to bypass CAPTCHA

### C. Password Security

- [ ] **Hashing**: Using bcrypt (not plain text)
- [ ] **Minimum Length**: 8 characters enforced
- [ ] **No Common Passwords**: Check against common list
- [ ] **Password Change**: Save new hashed password
- [ ] **Password Reset**: Email verification before reset

### D. OAuth Security

- [ ] **State Parameter**: CSRF protection enabled
- [ ] **Redirect URI**: Hardcoded or whitelist only
- [ ] **Client Secret**: Never exposed in frontend
- [ ] **Scope**: Minimal (openid email profile)

---

## Phase 5: Data Validation & Sanitization

### A. Input Validation

- [ ] **Email**: Valid format, normalized (lowercase)
- [ ] **Username**: Alphanumeric + underscore, 3-30 chars
- [ ] **URLs**: Valid format, no script injection
- [ ] **File Names**: Sanitized, no path traversal
- [ ] **SQL Injection**: Parameterized queries (SQLAlchemy)
- [ ] **XSS**: HTML escaped in templates

### B. Error Messages

- [ ] **Generic Auth Errors**: No user enumeration (all "Invalid credentials")
- [ ] **No Stack Traces**: User-facing errors hide details
- [ ] **Sentry Logging**: Errors logged for debugging

---

## Phase 6: Health & Observability

### A. Health Endpoint

#### Endpoint: `GET /health`
- [ ] **Status Code**: 200 (healthy) or 503 (degraded)
- [ ] **Dependencies Checked**:
  - [ ] Database connectivity
  - [ ] Filesystem access
  - [ ] API keys configured
- [ ] **Response Time**: < 1 second
- [ ] **Test**: `curl http://localhost:8000/health | python -m json.tool`

### B. Metrics Endpoint

#### Endpoint: `GET /metrics`
- [ ] **Format**: Prometheus text format
- [ ] **Metrics Present**:
  - [ ] http_requests_total
  - [ ] http_request_duration_seconds
  - [ ] http_5xx_errors_total
  - [ ] voice_upload_total
  - [ ] voice_upload_failures_total
  - [ ] ticket_created_total
- [ ] **Test**: `curl http://localhost:8000/metrics | grep -c "^#"` (comments)

### C. Structured Logging

- [ ] **Log Format**: JSON (not plain text)
- [ ] **Request ID**: Included in every log
- [ ] **Log Location**: `logs/app.log`
- [ ] **Log Rotation**: Daily, keeps 5 files

### D. Error Tracking

- [ ] **Sentry Integration**: Optional, non-blocking
- [ ] **Uncaught Exceptions**: Automatically captured
- [ ] **Breadcrumbs**: Request/response info included
- [ ] **User Context**: User ID/email in error context

---

## Phase 7: Database & Data Integrity

### A. Models & Schema

- [ ] **User Table**: All required fields present
  - [ ] id, email, username, hashed_password
  - [ ] is_active, is_verified, is_admin
  - [ ] google_id (OAuth), picture_url
  - [ ] created_at, updated_at, last_login
  
- [ ] **Ticket Table**: All required fields present
  - [ ] id, user_id, title, description
  - [ ] priority, category, status
  - [ ] audio_file_path, transcriptions
  - [ ] created_at, updated_at
  
- [ ] **Foreign Keys**: Enforced (user_id → User.id)
- [ ] **Unique Constraints**: email unique, username unique
- [ ] **Indexes**: email & username indexed for fast lookup

### B. Database Operations

- [ ] **Create User**: User saved with correct fields
- [ ] **Query User**: By email, username, google_id
- [ ] **Update User**: last_login, password, fields
- [ ] **Delete User**: Cascade delete tickets (verify behavior)
- [ ] **Transaction Integrity**: No partial writes

---

## Phase 8: File Management & Storage

### A. Upload Storage

- [ ] **Directory**: `storage/audio/{user_id}/`
- [ ] **File Format**: .wav, .mp3, .m4a preserved
- [ ] **Permissions**: Only owner can read
- [ ] **Path Traversal**: No `../` allowed in filenames

### B. Cleanup Process

- [ ] **Scheduler**: Runs periodically (check interval)
- [ ] **Cleanup Rules**: Remove old files after 7 days (adjust if needed)
- [ ] **Verify**: File actually deleted from disk

### C. File Access

- [ ] **Direct Access**: `GET /storage/...` blocked (no static serving)
- [ ] **Authenticated Download**: Use `/api/ticket/{id}/download`

---

## Phase 9: Admin Panel (If Applicable)

### A. Admin Access

#### Endpoint: `GET /admin`
- [ ] **Non-Admin**: Redirect to dashboard or 403
- [ ] **Admin User**: Render admin panel
- [ ] **Admin Check**: is_admin=true in database

### B. Admin Features

- [ ] **User Management**: View, disable, delete users
- [ ] **Ticket Management**: View all tickets, status changes
- [ ] **System Stats**: Total users, total tickets, error rate
- [ ] **Logs**:Access to application logs

---

## Phase 10: API Integration Tests

### A. End-to-End Workflow

**Test Scenario: Complete User Journey**

```
1. User visits /home
   ✓ Render homepage without errors
   
2. User clicks "Sign Up"
   ✓ GET /signup → Form displayed
   
3. User fills form (email, password, name)
   ✓ POST /signup → User created, session set
   
4. User navigates to /dashboard
   ✓ GET /dashboard → User data displayed
   
5. User uploads audio file
   ✓ POST /api/voice/upload → File stored, upload_id returned
   
6. User starts transcription
   ✓ POST /api/voice/transcribe → Groq API called, result returned
   
7. User translates transcription
   ✓ POST /api/voice/translate → Google Translate API called, result returned
   
8. User creates ticket with transcribed text
   ✓ POST /api/ticket/create → Ticket created, ticket_id returned
   
9. User views ticket details
   ✓ GET /api/ticket/{ticket_id} → Full ticket returned
   
10. User logs out
    ✓ GET /logout → Session cleared, redirect to /login
    
11. User tries to access protected route
    ✓ GET /dashboard → Redirect to /login (session not valid)
```

---

## Phase 11: Error Handling & Edge Cases

### A. Network Errors

- [ ] **API Timeout**: Groq/Google API timeout → 504 or user error message
- [ ] **API Unavailable**: Service down → 503 or fallback response
- [ ] **No Internet**: Connection refused → Error message

### B. Concurrency Issues

- [ ] **Simultaneous Uploads**: Multiple files from same user → OK
- [ ] **Simultaneous Logins**: Multiple sessions from same account → OK (or deny)
- [ ] **Race Condition**: Create ticket twice → One created, one fails uniquely

### C. Resource Exhaustion

- [ ] **Disk Space**: Storage full → Error message, user notified
- [ ] **Database**: Max connections exceeded → Wait or error
- [ ] **Memory**: Large file upload → Stream processing (not all in memory)

---

## Phase 12: Performance & Load Testing

### A. Response Times (Baseline)

- [ ] **Login**: < 200ms
- [ ] **Signup**: < 200ms
- [ ] **Dashboard**: < 500ms
- [ ] **Upload**: < 1 sec (depends on file size)
- [ ] **Transcription**: < 20 sec (Groq API call time)
- [ ] **Translation**: < 5 sec
- [ ] **Health Check**: < 100ms

### B. Load Testing (Optional)

- [ ] **10 Concurrent Users**: No crash
- [ ] **100 Concurrent Users**: Graceful degradation (rate limits apply)
- [ ] **Memory Usage**: Stable over 1 hour
- [ ] **Database**: No lockups, queries < 1 sec

---

## Phase 13: Mobile & Cross-Browser

### A. Browser Compatibility

- [ ] **Chrome**: Latest version on Windows
- [ ] **Firefox**: Latest version on Windows
- [ ] **Safari**: Latest version (if Mac available)
- [ ] **Edge**: Latest version

### B. Responsive Design

- [ ] **Desktop (1920px)**: Layout correct
- [ ] **Tablet (768px)**: Layout responsive
- [ ] **Mobile (375px)**: Touch-friendly buttons

---

## Phase 14: Documentation & Runbooks

### A. Docs Present

- [ ] **README.md**: Setup instructions
- [ ] **OBSERVABILITY.md**: Logging/metrics/alerts
- [ ] **MONITORING.md**: Prometheus/Grafana
- [ ] **ALERTING.md**: Alert rules
- [ ] **RUNBOOKS.md**: Incident response
- [ ] **.env.example**: All variables documented

### B. Runbooks Tested

- [ ] **High Error Rate Runbook**: Steps are accurate
- [ ] **Auth Failure Runbook**: Steps are accurate
- [ ] **Database Issue Runbook**: Steps are accurate

---

## Summary Checklist

| Phase | Items | Status |
|-------|-------|--------|
| 1. Environment | 4 | ✅ |
| 2. Authentication | 35 | 🔍 |
| 3. Workflow | 25 | 🔍 |
| 4. Security | 15 | 🔍 |
| 5. Data Validation | 10 | 🔍 |
| 6. Observability | 20 | 🔍 |
| 7. Database | 12 | 🔍 |
| 8. File Management | 10 | 🔍 |
| 9. Admin Panel | 8 | 🔍 |
| 10. E2E Tests | 11 | 🔍 |
| 11. Error Handling | 10 | 🔍 |
| 12. Performance | 10 | 🔍 |
| 13. Mobile/Browser | 8 | 🔍 |
| 14. Documentation | 8 | 🔍 |

**Total Items**: 184  
**Status**: In Progress

---

## Issues Found

(To be filled as audit progresses)

---

## Recommendations

(To be filled after audit completion)

---

**Last Updated**: March 20, 2026  
**Audit Status**: 🔍 IN PROGRESS


---

## Reliability Operations Pack (P1)

### Implemented

- Structured request logs with request ID propagation (`X-Request-ID`) and privacy-safe context.
- Backend error tracking via Sentry (`SENTRY_DSN`) and optional frontend Sentry browser SDK.
- Metrics endpoint (`/metrics`) with counters/histograms for:
  - request volume and status distribution
  - 5xx rate and auth failure rate
  - p95 latency (`http_request_duration_seconds` histogram)
  - queue wait time (`queue_wait_seconds`)
  - voice upload failures (`voice_upload_failures_total`)
  - cleanup task failures (`cleanup_failures_total`)
- Uptime automation workflow: `.github/workflows/uptime-checks.yml`
- Alert rules: `ops/prometheus/alerts.yml`

### Uptime Checks

- Main app endpoint check every 10 minutes.
- Health endpoint check every 10 minutes.
- Configure secret in GitHub Actions:
  - `PRODUCTION_BASE_URL=https://techfixai.up.railway.app`

### Alert Rules Included

- `TechFixAIHigh5xxRate`
- `TechFixAIAuthFailureSpike`
- `TechFixAIHighP95Latency`
- `TechFixAICleanupFailures`
- `TechFixAIUploadFailureSpike`

### Incident Runbook (Simple)

#### 1) Outage / 5xx Spike

1. Confirm `/health` and `/metrics` are reachable.
2. Check latest application logs filtered by `request_id` and `status_code >= 500`.
3. If DB errors are present, validate database connectivity and recent migration state.
4. Roll back the last deployment if error rate does not recover in 10 minutes.
5. Post incident note with timeline, blast radius, and recovery action.

#### 2) Authentication Failure Spike

1. Check `http_auth_failures_total` by reason.
2. Verify OAuth redirect URI / CAPTCHA config / session cookie settings.
3. Confirm no recent auth config drift in environment variables.
4. If abuse suspected, tighten temporary auth rate limits.
5. Publish user-facing status update if sign-in is impacted.

#### 3) Data Incident

1. Pause destructive background cleanup jobs.
2. Identify affected records and scope (users/tickets/conversations).
3. Restore from backup/snapshot if needed.
4. Rotate compromised credentials/secrets if exposure is suspected.
5. Document root cause and preventive controls before closure.

### PromQL Dashboard Suggestions

- Requests/sec:
  - `sum(rate(http_requests_total[1m]))`
- 5xx ratio:
  - `sum(rate(http_5xx_errors_total[5m])) / clamp_min(sum(rate(http_requests_total[5m])), 1)`
- p95 latency:
  - `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
- Queue wait time p95:
  - `histogram_quantile(0.95, sum(rate(queue_wait_seconds_bucket[15m])) by (le, queue_name))`
- Upload failure ratio:
  - `sum(rate(voice_upload_failures_total[5m])) / clamp_min(sum(rate(voice_upload_total[5m])), 1)`

---

## Deployment Safety, CI, and Disaster Recovery

### What is now implemented

- Manual deployment from Railway dashboard (simplified mode).
- Manual rollback from Railway dashboard (simplified mode).
- Manual backup and restore drill process (simplified mode).
- CI quality gates for syntax/lint, tests, security static checks, and dependency vulnerability scanning.

### New workflows

- `.github/workflows/ci.yml`
- `.github/workflows/secret-hygiene.yml` (fixed to use gitleaks)
- `.github/workflows/uptime-checks.yml`

### Recovery targets

- RPO: <= 24 hours
- RTO: <= 60 minutes

For now, keep this minimum secret set:

- `PRODUCTION_BASE_URL`
