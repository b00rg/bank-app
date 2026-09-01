# Accessible Banking App

Mobile banking app built for accessibility, with a carer/trusted-contact layer for users who want a trusted person kept in the loop on their finances.

Built at HackEurope.

## How it works

1. User initiates a payment (transfer or merchant payment) through the app.
2. The backend validates the request, checks the payee, and creates a Stripe payment (PaymentIntent or Connect transfer, depending on payee type).
3. Stripe Radar scores the payment for fraud risk. The description is also checked against a scam-pattern list tuned for scams that target elderly and disabled users (gift cards, wire transfers, urgency language, fake refunds, and similar).
4. Depending on risk level, the payment goes through, gets flagged with a carer alert, or gets blocked outright.

## Features

- Stripe-backed payments: customer accounts, PaymentIntents, and Connect transfers to individual payees
- Stripe Issuing virtual cards with weekly spending limits and blocked merchant categories (gambling, dating/escort services, tobacco), plus freeze/unfreeze and limit updates
- Fraud detection combining Stripe Radar risk scores with a custom scam-pattern check, tuned for scams that target elderly and disabled users
- Carer registration: link a trusted contact by phone, with an SMS confirmation on registration
- Carer dashboard: real-time SMS alerts on fraud risk, large payments, and failed payments; transaction monitoring; spending limits. Trusted people stay informed without controlling the account

## Accessibility

- Screen reader support throughout
- High-contrast, low-vision-friendly UI

## Tech stack

**Frontend**: React + Vite (TypeScript), Tailwind CSS. Mobile phone-frame interface.

**Backend**: Python, FastAPI. Session middleware, CORS, modular routes for users, payments, transactions, cards, and carer alerts.

**Payments**: Stripe (Customers, PaymentIntents, Connect transfers, Issuing virtual cards, Radar, webhooks).

## Setup

Requires a Stripe API key. See `.env.example` for required variables.

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
