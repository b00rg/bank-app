# TrueLayer Banking API - Complete Integration Guide

## Overview

TrueLayer provides Open Banking access to get account data and initiate payments. This integration uses:
- **Auth URL**: https://auth.truelayer.com
- **API URL**: https://api.truelayer.com

## Environment Setup

Add to `.env`:
```
TRUELAYER_CLIENT_ID=sandbox-bankapp-bece06
TRUELAYER_CLIENT_SECRET=your_client_secret
TRUELAYER_REDIRECT_URI=http://localhost:8000/api/truelayer/callback
TRUELAYER_ACCESS_TOKEN=your_access_token
```

## Complete OAuth Flow

### Step 1: Get Authorization URL
**Request:**
```bash
curl http://localhost:8000/api/truelayer/auth-url
```

**Response:**
```json
{
  "auth_url": "https://auth.truelayer.com/authorize?client_id=sandbox-bankapp-bece06&redirect_uri=http://localhost:8000/api/truelayer/callback&response_type=code&scope=accounts%20transactions%20balance%20payments"
}
```

**Action**: Redirect user to the `auth_url` in a browser window.

---

### Step 2: User Logs In & Approves
User logs into their bank and approves access. TrueLayer redirects to:
```
http://localhost:8000/api/truelayer/callback?code=AUTH_CODE&state=STATE
```

**Frontend captures the `code` from the URL query parameter.**

---

### Step 3: Exchange Code for Access Token
**Request:**
```bash
curl -X POST http://localhost:8000/api/truelayer/link-bank \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "auth_code": "AUTH_CODE_FROM_STEP_2"
  }'
```

**Response:**
```json
{
  "user_id": "user_123",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "accounts": {
    "results": [
      {
        "account_id": "acc_123456789",
        "account_type": "TRANSACTION_ACCOUNT",
        "currency": "GBP",
        "account_number": {
          "iban": "GB82WEST12345698765432",
          "number": "12345678",
          "sort_code": "123456"
        },
        "display_name": "Current Account"
      },
      {
        "account_id": "acc_987654321",
        "account_type": "SAVINGS_ACCOUNT",
        "currency": "GBP",
        "account_number": {
          "iban": "GB12WEST98765432123456",
          "number": "87654321",
          "sort_code": "654321"
        },
        "display_name": "Savings Account"
      }
    ]
  }
}
```

**Action**: Store the `access_token` securely in your database associated with `user_123`.

---

## Banking Operations

### Get All Accounts
**Request:**
```bash
curl http://localhost:8000/api/truelayer/accounts \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
{
  "results": [
    {
      "account_id": "acc_123456789",
      "account_type": "TRANSACTION_ACCOUNT",
      "currency": "GBP",
      "display_name": "Current Account"
    }
  ]
}
```

---

### Get Account Balance
**Request:**
```bash
curl http://localhost:8000/api/truelayer/accounts/acc_123456789/balance
```

**Response:**
```json
{
  "results": [
    {
      "account_id": "acc_123456789",
      "currency": "GBP",
      "available": 2500.50,
      "current": 2650.75,
      "overdraft": 0.00,
      "update_timestamp": "2026-02-21T10:30:00Z"
    }
  ]
}
```

---

### Get Transactions
**Request:**
```bash
curl http://localhost:8000/api/truelayer/accounts/acc_123456789/transactions?limit=20
```

**Response:**
```json
{
  "results": [
    {
      "transaction_id": "txn_abc123",
      "timestamp": "2026-02-21T10:30:00Z",
      "amount": 50.00,
      "currency": "GBP",
      "description": "Spotify Subscription",
      "transaction_type": "DEBIT",
      "transaction_category": "ENTERTAINMENT",
      "transaction_classification": [
        "PURCHASE",
        "SUBSCRIPTION"
      ],
      "merchant": {
        "name": "Spotify AB",
        "logo_uri": "https://logo.clearbit.com/spotify.com"
      },
      "running_balance": 2550.75,
      "booking_datetime": "2026-02-21T10:30:00Z"
    },
    {
      "transaction_id": "txn_def456",
      "timestamp": "2026-02-20T14:15:00Z",
      "amount": 1200.00,
      "currency": "GBP",
      "description": "Monthly Salary",
      "transaction_type": "CREDIT",
      "transaction_category": "TRANSFER",
      "transaction_classification": [
        "SALARY"
      ],
      "counterparty": {
        "name": "ACME Corp",
        "account_number": "87654321"
      },
      "running_balance": 2600.75,
      "booking_datetime": "2026-02-20T14:15:00Z"
    }
  ]
}
```

---

### Initiate Payment
**Request:**
```bash
curl -X POST http://localhost:8000/api/truelayer/payments/initiate \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.50,
    "currency": "GBP",
    "beneficiary_name": "John Doe",
    "beneficiary_account": "GB82WEST12345698765432"
  }'
```

**Response:**
```json
{
  "id": "pmt_123456",
  "resource_type": "payment",
  "status": "AUTHORIZING",
  "amount": 100.50,
  "currency": "GBP",
  "created_at": "2026-02-21T10:30:00Z",
  "payment_method": "SINGLE_PAYMENT",
  "user": {
    "id": "user_123"
  },
  "creditor_account": {
    "account_number": "GB82WEST12345698765432",
    "name": "John Doe"
  }
}
```

**Action**: Redirect user to approval page if `status` is `AUTHORIZING`. Payment will complete after user approves.

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/truelayer/auth-url` | Get OAuth authorization URL |
| POST | `/api/truelayer/link-bank` | Exchange auth code for access token |
| GET | `/api/truelayer/accounts` | Fetch all linked accounts |
| GET | `/api/truelayer/accounts/{account_id}/balance` | Get account balance |
| GET | `/api/truelayer/accounts/{account_id}/transactions` | Get transactions |
| POST | `/api/truelayer/payments/initiate` | Initiate a payment |

---

## Error Handling

All endpoints return errors in this format:
```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (invalid token)
- `404` - Resource not found
- `500` - Server error

---

## Security Best Practices

1. **Store access tokens securely** - Encrypt in database, don't expose in logs
2. **Implement token refresh** - Access tokens expire; check `expires_in` and refresh if needed
3. **Use HTTPS only** - Never send tokens over HTTP
4. **Validate redirects** - Verify redirect_uri matches your registered callback
5. **Add CSRF protection** - Use the `state` parameter in OAuth flow
6. **Rate limit** - Implement rate limiting on your API endpoints

---

## Testing with Sandbox

For testing without real bank data:
1. Use test credentials from TrueLayer Console
2. Test transactions appear in sandbox immediately
3. Payment operations show as `PENDING` in sandbox
4. No real money is transferred

---

## Webhook Notifications

To receive payment status updates, configure webhooks in TrueLayer Console:
- Payment completed
- Payment failed
- Payment cancelled

Your app can then update payment status in the database.
