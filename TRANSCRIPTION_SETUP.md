# 🎤 Audio Transcription Setup Guide

## Quick Setup (2 minutes)

Your transcription service is configured to use **cloud-based APIs** (no large downloads needed!).

### Option 1: Groq API (Recommended - FREE & FASTEST)

1. **Get FREE API Key:**
   - Visit: https://console.groq.com
   - Sign up (GitHub/Google login available)
   - Go to "API Keys" section
   - Click "Create API Key"
   - Copy your key

2. **Add to `.env` file:**
   ```env
   GROQ_API_KEY="gsk_your_api_key_here"
   ```

3. **Done!** 🎉
   - Supports Japanese audio transcription
   - Uses Whisper Large V3 (most accurate)
   - Very fast (usually < 3 seconds)
   - Completely free tier available

### Option 2: OpenAI Whisper API (Alternative)

1. **Get API Key:**
   - Visit: https://platform.openai.com
   - Sign up and add payment method
   - Go to API Keys section
   - Create new API key

2. **Add to `.env` file:**
   ```env
   OPENAI_API_KEY="sk-your_openai_key_here"
   ```

3. **Cost:** ~$0.006 per minute of audio

## Current Status

✅ **Translation:** Working (using Gemini API)  
✅ **Ticket Generation:** Working (using Gemini API)  
⚠️ **Transcription:** Using MOCK mode (needs API key)

## Test Your Setup

1. Add your API key to `.env`
2. Restart the server: `python -m uvicorn app.main:app --reload`
3. Upload Japanese audio at http://localhost:8000/upload
4. Check console logs for: `✅ Groq API configured for STT`

## Troubleshooting

**Still seeing mock transcriptions?**
- Make sure you added the API key to `.env` file (not `config.py`)
- Restart the FastAPI server
- Check console for error messages

**Groq API errors?**
- Verify API key is correct (starts with `gsk_`)
- Check https://console.groq.com for usage limits
- Try OpenAI as fallback

## Why Cloud-Based?

- ✅ **No storage:** No 100+ MB model downloads
- ✅ **Fast:** API calls complete in seconds
- ✅ **Accurate:** Uses latest Whisper models
- ✅ **Simple:** Just add API key and go
- ✅ **Japanese:** Full support for Japanese audio

---

**Recommended:** Use Groq - it's free, fastest, and super accurate!
