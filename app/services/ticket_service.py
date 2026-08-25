"""
Ticket service.
Handles ticket generation with structured schema.
"""

import uuid
from datetime import datetime
from typing import Dict, Optional
import json

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ticket import Ticket, TicketPriority, TicketStatus


class TicketService:
    """
    Service for creating structured tickets from translated text.
    Uses Gemini or OpenAI to extract structured information with fallback to rule-based extraction.
    """
    
    def __init__(self):
        self.groq_client = None
        self.gemini_model = None
        self.use_groq = False
        self.use_gemini = False
        self.use_openai = False

        # ── Groq (primary — already working for STT + translation) ──
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self.use_groq = True
                pass  # Groq ready
            except Exception as e:
                pass  # Groq init failed
        else:
            pass  # Groq API key not set

        # ── Gemini (secondary fallback — initialized independently) ──
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                self.use_gemini = True
                pass  # Gemini ready
            except Exception as e:
                pass  # Gemini init failed

        if not self.use_groq and not self.use_gemini:
            pass  # No AI API available
    
    async def generate_ticket_from_text(
        self,
        english_text: str,
        japanese_text: Optional[str] = None
    ) -> Dict:
        """
        Generate structured ticket data from translated text.
        Uses Groq → Gemini → rule-based fallback.
        """
        # 1️⃣ Groq (fast, reliable, same API already working for translation)
        if self.use_groq:
            try:
                return await self._groq_generate_ticket(english_text)
            except Exception as e:
                import traceback
                print(f"❌ [Ticket] Groq failed: {type(e).__name__}: {str(e)}")
                print(traceback.format_exc())

        # 2️⃣ Gemini fallback
        if self.use_gemini:
            try:
                return await self._gemini_generate_ticket(english_text)
            except Exception as e:
                print(f"⚠️ [Ticket] Gemini failed: {e}")

        # 3️⃣ Rule-based fallback (always works)
        print(f"🎫 Generating ticket (rule-based fallback): {english_text[:50]}...")
        return self._mock_generate_ticket(english_text)

    async def _groq_generate_ticket(self, english_text: str) -> Dict:
        """Generate ticket using Groq API with model fallback chain."""
        print(f"🎫 [Ticket] Generating with Groq: {english_text[:50]}...")

        TICKET_PROMPT = """You are a technical support ticket analyzer.
Extract structured information from the problem description and return ONLY valid JSON:
{
    "title": "Clear concise title (max 100 chars)",
    "description": "Detailed technical description",
    "priority": "low|medium|high|critical",
    "category": "bug|feature_request|incident|question",
    "technical_area": "backend|frontend|database|infrastructure|network|other"
}
Output ONLY the JSON object, no markdown, no explanation."""

        # Try multiple models in order
        models_to_try = ["meta-llama/llama-prompt-guard-2-86m", "meta-llama/llama-prompt-guard-2-22m"]
        completion = None
        
        for model_name in models_to_try:
            try:
                print(f"[DEBUG] Ticket generation trying model: {model_name}")
                completion = self.groq_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": TICKET_PROMPT},
                        {"role": "user", "content": english_text}
                    ],
                    temperature=0.1,
                    max_tokens=512
                )
                print(f"[DEBUG] Model {model_name} succeeded!")
                break
            except Exception as e:
                print(f"[DEBUG] Model {model_name} failed: {str(e)[:100]}")
                continue
        
        if not completion:
            raise RuntimeError("All Groq models failed for ticket generation")
        
        response_text = completion.choices[0].message.content.strip()
        # Strip markdown code blocks if model adds them
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[-1]
        if response_text.endswith("```"):
            response_text = response_text.rsplit("```", 1)[0]
        response_text = response_text.strip()

        ticket_data = json.loads(response_text)
        if ticket_data.get("priority") not in ["low", "medium", "high", "critical"]:
            ticket_data["priority"] = "medium"

        print(f"✅ [Ticket] Groq done: [{ticket_data.get('priority','?').upper()}] {ticket_data.get('title','')[:60]}")
        return ticket_data
    
    async def _gemini_generate_ticket(self, english_text: str) -> Dict:
        """Generate ticket using Gemini API."""
        print(f"🎫 Generating ticket with Gemini: {english_text[:50]}...")
        
        prompt = """You are a technical support ticket analyzer.
Extract structured information from the user's problem description and return ONLY valid JSON with this exact schema:
{
    "title": "Clear, concise title (max 200 chars)",
    "description": "Detailed technical description",
    "priority": "low|medium|high|critical",
    "category": "bug|feature_request|incident|question",
    "technical_area": "backend|frontend|database|infrastructure|network|other"
}

Rules:
- Title must be actionable and specific
- Description should preserve all technical details
- Priority based on urgency and impact
- Output ONLY the JSON, no markdown, no explanations

Problem description:
""" + english_text
        
        response = self.gemini_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        ticket_data = json.loads(response_text)
        
        # Validate priority
        if ticket_data.get("priority") not in ["low", "medium", "high", "critical"]:
            ticket_data["priority"] = "medium"
        
        print(f"✅ Gemini ticket generated: {ticket_data.get('title', '')[:50]}")
        
        return ticket_data
    
    async def _openai_generate_ticket(self, english_text: str) -> Dict:
        """Generate ticket using OpenAI API."""
        print(f"🎫 Generating ticket with OpenAI: {english_text[:50]}...")
        
        system_prompt = """You are a technical support ticket analyzer.
Extract structured information from the user's problem description and return ONLY valid JSON with this exact schema:
{
    "title": "Clear, concise title (max 200 chars)",
    "description": "Detailed technical description",
    "priority": "low|medium|high|critical",
    "category": "bug|feature_request|incident|question",
    "technical_area": "backend|frontend|database|infrastructure|network|other"
}

Rules:
- Title must be actionable and specific
- Description should preserve all technical details
- Priority based on urgency and impact
- Be deterministic, not random"""
        
        response = self.openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": english_text}
            ],
            temperature=0.2,  # Very low for consistency
            max_tokens=800
        )
        
        ticket_data = json.loads(response.choices[0].message.content.strip())
        
        # Validate priority
        if ticket_data.get("priority") not in ["low", "medium", "high", "critical"]:
            ticket_data["priority"] = "medium"
        
        return ticket_data
    
    def _mock_generate_ticket(self, english_text: str) -> Dict:
        """
        Rule-based ticket generation for development/testing.
        Analyzes text for keywords to determine priority and category.
        """
        text_lower = english_text.lower()
        
        # Determine priority based on urgency keywords
        priority = "medium"
        if any(word in text_lower for word in ["critical", "urgent", "immediately", "down", "crash", "emergency"]):
            priority = "critical"
        elif any(word in text_lower for word in ["high", "important", "asap", "soon", "quickly"]):
            priority = "high"
        elif any(word in text_lower for word in ["minor", "small", "trivial", "whenver"]):
            priority = "low"
        
        # Determine category based on keywords
        category = "incident"
        if any(word in text_lower for word in ["feature", "enhancement", "add", "improve"]):
            category = "feature_request"
        elif any(word in text_lower for word in ["bug", "error", "broken", "not working", "failed"]):
            category = "bug"
        elif any(word in text_lower for word in ["question", "how", "what", "why"]):
            category = "question"
        
        # Determine technical area
        technical_area = "other"
        if any(word in text_lower for word in ["server", "backend", "api", "service"]):
            technical_area = "backend"
        elif any(word in text_lower for word in ["database", "db", "sql", "query", "data"]):
            technical_area = "database"
        elif any(word in text_lower for word in ["ui", "frontend", "interface", "button", "display"]):
            technical_area = "frontend"
        elif any(word in text_lower for word in ["network", "connection", "timeout", "dns"]):
            technical_area = "network"
        elif any(word in text_lower for word in ["infrastructure", "deploy", "production", "environment"]):
            technical_area = "infrastructure"
        
        # Generate concise title
        title = english_text[:100] if len(english_text) <= 100 else english_text[:97] + "..."
        
        # If text is very short, make it the title
        if len(english_text) < 50:
            title = english_text
        
        ticket_data = {
            "title": title,
            "description": english_text,
            "priority": priority,
            "category": category,
            "technical_area": technical_area
        }
        
        print(f"🎫 MOCK Ticket: [{priority.upper()}] {technical_area} - {title[:50]}...")
        
        return ticket_data
    
    async def create_ticket(
        self,
        db: Session,
        conversation_id: int,
        ticket_data: Dict
    ) -> Ticket:
        """
        Create ticket in database.
        
        Args:
            db: Database session
            conversation_id: Related conversation ID
            ticket_data: Structured ticket data
        
        Returns:
            Created Ticket instance
        """
        
        # Generate unique ticket number
        ticket_number = f"TKT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        ticket = Ticket(
            ticket_number=ticket_number,
            conversation_id=conversation_id,
            title=ticket_data["title"],
            description=ticket_data["description"],
            priority=TicketPriority(ticket_data["priority"]),
            category=ticket_data.get("category"),
            technical_area=ticket_data.get("technical_area"),
            status=TicketStatus.OPEN
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        return ticket


# Singleton instance
ticket_service = TicketService()
