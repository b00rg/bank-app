# Accessible Banking App

Voice-first mobile banking app. Hold a button, speak a command, such as "Transfer 20 euros to Anna", and the app confirms and executes the action through a minimal UI.

Built at HackEurope. Designed around accessibility: low-vision, screen reader, and voice-first interaction as primary use cases, not add-ons.

## How it works

1. User holds the voice button and speaks a command.
2. Gemini parses the speech into a structured intent (action, amount, recipient, etc).
3. The backend validates the request, checks the payee, and creates a Stripe payment (PaymentIntent or Connect transfer, depending on payee type).
4. Stripe Radar scores the payment for fraud risk. The description is also checked against a scam-pattern list tuned for scams that target elderly and disabled users (gift cards, wire transfers, urgency language, fake refunds, and similar).
5. Depending on risk level, the payment goes through, gets flagged with a carer alert, or gets blocked outright.
6. ElevenLabs generates spoken confirmation; the UI shows a minimal visual confirmation in parallel.

## Features

- Voice commands for transfers, balance checks, and payments
- Live transcription and natural text-to-speech via ElevenLabs
- Stripe-backed payments: customer accounts, PaymentIntents, and Connect transfers to individual payees
- Stripe Issuing virtual cards with weekly spending limits and blocked merchant categories (gambling, dating/escort services, tobacco), plus freeze/unfreeze and limit updates
- Fraud detection combining Stripe Radar risk scores with a custom scam-pattern check, tuned for scams that target elderly and disabled users
- Carer registration: link a trusted contact by phone, with an SMS confirmation on registration
- Carer dashboard: real-time SMS alerts on fraud risk, large payments, and failed payments; transaction monitoring; spending limits. Trusted people stay informed without controlling the account

## Accessibility

- Screen reader support throughout
- High-contrast, low-vision-friendly UI
- Voice as a primary input method, not a fallback

## Tech stack

**Frontend**: React + Vite (TypeScript), Tailwind CSS. Mobile phone-frame interface with voice overlay transitions.

**Backend**: Python, FastAPI. Session middleware, CORS, modular routes for users, payments, transactions, and voice processing.

**Voice pipeline**: Gemini (speech-to-intent), ElevenLabs (live transcription, text-to-speech).

**Payments**: Stripe (Customers, PaymentIntents, Connect transfers, Issuing virtual cards, Radar, webhooks).

## Setup

Requires API keys for Stripe, Gemini, and ElevenLabs. See `.env.example` for required variables.

Stripe-specific environment variables:
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `DEFAULT_WEEKLY_LIMIT` (optional, cents, defaults to 50000 / €500)
- `FORCE_RISK_LEVEL` (optional, for testing: `normal`, `elevated`, or `highest`; leave unset in production)

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
