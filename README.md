# Voice-to-Ticket AI System

## What This Is

An **automated incident intake + routing system** that:
1. Takes Japanese voice input from clients
2. Transcribes and translates technical issues accurately
3. Creates structured support tickets
4. Assigns tickets to developers deterministically

**NOT** a chatbot. **NOT** a translation demo. **NOT** an AI playground.

---

## The Problem We Solve

Japanese clients cannot clearly communicate technical issues to English-speaking dev teams.
Manual ticket handling causes:
- Delays in response time
- Misrouting to wrong developers
- Loss of context and technical details

---

## System Architecture

**Style:** Modular Monolith (NOT microservices)

```
Japanese Voice Input
        ↓
    [Whisper STT]
        ↓
Japanese Transcript
        ↓
  [LLM Translation]
        ↓
English Translation
        ↓
 [Ticket Generation]
        ↓
  Structured Ticket
        ↓
[Auto-Assignment Logic]
        ↓
Assigned Developer
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | FastAPI | Async API, auto-docs |
| STT | OpenAI Whisper | Japanese speech recognition |
| Translation | LLM (GPT-4) | Context-aware technical translation |
| Database | PostgreSQL | Structured data, audit trail |
| Storage | Local/S3 | Encrypted audio files |

---

## Project Structure

```
voice-ticket-ai/
│
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   └── security.py      # Auth helpers
│   │
│   ├── api/
│   │   ├── voice.py         # Voice upload endpoints
│   │   ├── ticket.py        # Ticket management
│   │   └── admin.py         # Admin dashboard
│   │
│   ├── services/
│   │   ├── stt_service.py          # Whisper transcription
│   │   ├── translation_service.py  # Japanese → English
│   │   ├── ticket_service.py       # Ticket generation
│   │   └── assignment_service.py   # Developer assignment
│   │
│   ├── models/
│   │   ├── conversation.py  # Voice data + metadata
│   │   ├── ticket.py        # Actionable ticket
│   │   └── developer.py     # Dev skills + availability
│   │
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   │
│   └── utils/
│       ├── audio.py
│       └── text.py
│
├── migrations/              # Database migrations
├── tests/                   # Unit & integration tests
├── storage/                 # Audio file storage
├── requirements.txt
└── README.md
```

---

## Domain Objects (Core Concepts)

### 1. Conversation
Voice data + metadata
- Audio file path
- Duration, format
- Processing status

### 2. Transcript
Japanese text + English text
- Original Japanese transcription
- Cleaned English translation

### 3. Ticket
Actionable engineering artifact
- Title, description
- Priority, category
- Technical area
- Assignment logic trail

### 4. Developer
Skill + availability + ownership
- Technical skills/areas
- Current workload
- Capacity limits

**Do NOT mix these concepts.**

---

## The Golden Path (v1 Happy Flow)

This is the ONLY flow we support initially:

1. **User uploads Japanese audio** → `/api/voice/upload`
2. **System stores audio securely** → Local storage
3. **STT produces Japanese text** → Whisper
4. **Translation produces clean English** → LLM
5. **Ticket is generated with schema** → Structured format
6. **Ticket is assigned to a developer** → Deterministic logic
7. **Admin can view everything** → Dashboard

No branches. No "what if user cancels". That comes later.

---

## Setup Instructions

### 1. Prerequisites
```bash
Python 3.10+
PostgreSQL 14+
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/voice_ticket_db
OPENAI_API_KEY=your-openai-api-key
SECRET_KEY=your-secret-key
AUDIO_STORAGE_PATH=./storage/audio
DEBUG=True
```

### 4. Database Setup
```bash
# Create database
createdb voice_ticket_db

# Run migrations (after creating migration files)
alembic upgrade head
```

### 5. Run Application
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access API Documentation
```
http://localhost:8000/docs
```

---

## API Endpoints

### Voice Processing
- `POST /api/voice/upload` - Upload Japanese audio
- `GET /api/voice/status/{conversation_id}` - Check processing status

### Ticket Management
- `GET /api/tickets/{ticket_number}` - Get ticket details
- `GET /api/tickets/` - List tickets (with filters)

### Admin Dashboard
- `GET /api/admin/dashboard` - System overview
- `GET /api/admin/conversations` - All conversations
- `GET /api/admin/developers` - Developer stats

---

## Success Criteria

### ✅ Project is successful if:
- Random Japanese audio → correct dev gets ticket
- Admin can replay audio + see assignment logic
- Every ticket has consistent structure
- System is deterministic (same input = same output)

### ❌ Project is a failure if:
- Output varies every run
- Assignment feels random
- Tickets read like chat logs
- Can't explain why a dev was chosen

---

## What's OUT OF SCOPE (v1)

❌ Emotional chat responses  
❌ Long conversations  
❌ Voice reply back to user  
❌ Complex ML training  
❌ Multi-language support (beyond Japanese/English)  
❌ Real-time voice streaming  

**If you try to include these early, you're sabotaging yourself.**

---

## Development Workflow

### 1. Database Changes
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### 2. Run Tests
```bash
pytest tests/
```

### 3. Code Formatting
```bash
black app/
flake8 app/
```

---

## Assignment Logic (Deterministic)

```python
1. Filter active developers
2. Match technical area with developer skills
3. Check current workload (active tickets count)
4. Assign to developer with:
   - Matching technical area (if exists)
   - Lowest current workload
   - Under capacity limit
5. Store assignment reason for audit
```

**No randomness. No black box. Transparent and explainable.**

---

## Security Considerations

- Audio files stored with encryption (implement in production)
- API key authentication
- Rate limiting on uploads
- Input validation on all endpoints
- SQL injection prevention (SQLAlchemy ORM)
- CORS configuration

---

## Future Enhancements (Post-v1)

- Real-time WebSocket updates
- Admin UI dashboard
- Email notifications to developers
- Ticket priority auto-escalation
- Developer performance analytics
- Multi-tenant support
- Advanced audio preprocessing

---

## Common Issues & Troubleshooting

### Whisper Model Not Loading
```bash
# Download model manually
python -c "import whisper; whisper.load_model('base')"
```

### Database Connection Failed
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

### Audio Upload Fails
- Check file size limits
- Verify storage directory permissions
- Confirm audio format is supported

---

## Contributing

1. Keep code focused on the core problem
2. Follow the modular monolith pattern
3. Write deterministic, testable code
4. Document assignment logic clearly
5. No feature creep without justification

---

## License

MIT License

---

## Contact

For questions about the system architecture or implementation decisions, refer to this README first.

**Remember:** This is an automated incident intake + routing system. Keep it focused.
