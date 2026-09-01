# Accessible Banking App

Voice-first mobile banking app. Hold a button, speak a command, such as "Transfer 20 euros to Anna", and the app confirms and executes the action through a minimal UI.

Built at HackEurope. Designed around accessibility: low-vision, screen reader, and voice-first interaction as primary use cases, not add-ons.

## How it works

1. User holds the voice button and speaks a command.
2. Gemini parses the speech into a structured intent (action, amount, recipient, etc).
3. The backend validates and executes the action against TrueLayer.
4. ElevenLabs generates spoken confirmation; the UI shows a minimal visual confirmation in parallel.

## Features

- Voice commands for transfers, balance checks, and payments
- Live transcription and natural text-to-speech via ElevenLabs
- Real bank account linking, balance fetching, and payment initiation via TrueLayer OAuth
- Carer dashboard: real-time notifications, transaction monitoring, approval flows, spending limits. Trusted people stay informed without controlling the account

## Accessibility

- Screen reader support throughout
- High-contrast, low-vision-friendly UI
- Voice as a primary input method, not a fallback

## Tech stack

**Frontend**: React + Vite (TypeScript), Tailwind CSS. Mobile phone-frame interface with voice overlay transitions.

**Backend**: Python, FastAPI. Session middleware, CORS, modular routes for users, payments, transactions, and voice processing.

**Voice pipeline**: Gemini (speech-to-intent), ElevenLabs (live transcription, text-to-speech).

**Banking**: TrueLayer OAuth (account linking, balance, payment initiation).

## Setup

Requires API keys for TrueLayer, Gemini, and ElevenLabs. See `.env.example` for required variables, and `TRUELAYER_API_GUIDE.md` for TrueLayer-specific setup.

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

See `ONBOARDING_GUIDE.md` for further setup detail.

## Team / Context

Built in a hackathon setting at HackEurope, not production-hardened.
