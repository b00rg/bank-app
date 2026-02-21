# Seamless Onboarding Flow

This document outlines the complete onboarding flow with user data persistence via CSV.

## Architecture

- **User Storage**: CSV file (`users_data.csv`) stores all user data
- **Onboarding Steps**: 3-step process (Create User → Get Auth URL → Link Bank)
- **Automatic Data Sync**: User profile and bank data stored together

## Complete Onboarding Flow

### Step 1: Create User Account

**Endpoint**: `POST /api/truelayer/onboard`

**Request**:
```bash
curl -X POST http://localhost:8000/api/truelayer/onboard \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+44 123 456 7890"
  }'
```

**Response**:
```json
{
  "status": "user_created",
  "user_id": "user_123",
  "message": "User created successfully",
  "next_step": "GET /api/truelayer/auth-url to link bank account"
}
```

**What Happens**:
- User data saved to `users_data.csv`
- User is ready to link their bank

---

### Step 2: Get Authorization URL

**Endpoint**: `GET /api/truelayer/auth-url`

**Request**:
```bash
curl http://localhost:8000/api/truelayer/auth-url
```

**Response**:
```json
{
  "auth_url": "https://auth.truelayer.com/authorize?client_id=...&redirect_uri=...&response_type=code&scope=...",
  "message": "Redirect user to this URL to authorize bank access"
}
```

**Action**: Frontend redirects user to the `auth_url` in a browser.

---

### Step 3: User Logs In & Approves

User visits the auth URL, logs into their bank, and approves access. TrueLayer redirects back to:
```
http://localhost:8000/api/truelayer/callback?code=AUTH_CODE&state=STATE
```

**What Your Frontend Should Do**:
1. Capture the `code` from the URL query params
2. Extract `user_id` from localStorage/session
3. Call `/link-bank` with both values

---

### Step 4: Link Bank Account

**Endpoint**: `POST /api/truelayer/link-bank`

**Request**:
```bash
curl -X POST http://localhost:8000/api/truelayer/link-bank \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "auth_code": "AUTH_CODE_FROM_CALLBACK"
  }'
```

**Response**:
```json
{
  "status": "bank_linked",
  "user_id": "user_123",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "accounts": [
    {
      "account_id": "acc_123456789",
      "account_type": "TRANSACTION_ACCOUNT",
      "currency": "GBP",
      "display_name": "Current Account"
    }
  ],
  "message": "Bank account linked successfully",
  "next_step": "GET /api/truelayer/accounts to fetch all accounts"
}
```

**What Happens**:
- Access token exchanged and stored in CSV
- Primary account selected and stored
- User now fully onboarded and ready to use banking features

---

### Step 5: Check User Profile

**Endpoint**: `GET /api/truelayer/user/{user_id}`

**Request**:
```bash
curl http://localhost:8000/api/truelayer/user/user_123
```

**Response**:
```json
{
  "user_id": "user_123",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+44 123 456 7890",
  "primary_account_id": "acc_123456789",
  "primary_account_name": "Current Account",
  "bank_linked": true,
  "created_at": "2026-02-21T10:30:00Z",
  "updated_at": "2026-02-21T10:35:00Z"
}
```

---

## CSV Data Structure

File: `users_data.csv`

```csv
user_id,name,email,phone,access_token,token_type,expires_in,primary_account_id,primary_account_name,created_at,updated_at
user_123,John Doe,john@example.com,+44 123 456 7890,eyJhbGciOiJIUzI1NiIs...,Bearer,3600,acc_123456789,Current Account,2026-02-21T10:30:00Z,2026-02-21T10:35:00Z
user_456,Jane Smith,jane@example.com,+44 987 654 3210,eyJhbGciOiJIUzI1NiIs...,Bearer,3600,acc_987654321,Savings Account,2026-02-21T11:00:00Z,2026-02-21T11:05:00Z
```

---

## Frontend Implementation Example

```javascript
// Step 1: Onboard user
async function onboardUser(userId, name, email, phone) {
  const response = await fetch('http://localhost:8000/api/truelayer/onboard', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, name, email, phone })
  });
  const data = await response.json();
  localStorage.setItem('user_id', userId);
  return data;
}

// Step 2: Get auth URL
async function getAuthUrl() {
  const response = await fetch('http://localhost:8000/api/truelayer/auth-url');
  const data = await response.json();
  // Redirect user to data.auth_url
  window.location.href = data.auth_url;
}

// Step 3 & 4: Handle callback and link bank
// Frontend redirects to callback, captures code from URL
async function linkBank(authCode) {
  const userId = localStorage.getItem('user_id');
  const response = await fetch('http://localhost:8000/api/truelayer/link-bank', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, auth_code: authCode })
  });
  const data = await response.json();
  // User is now fully onboarded!
  return data;
}

// Step 5: Get user profile anytime
async function getUserProfile(userId) {
  const response = await fetch(`http://localhost:8000/api/truelayer/user/${userId}`);
  return await response.json();
}
```

---

## Banking Operations (After Onboarding)

Once a user is onboarded with a linked bank, they can:

### Get All Accounts
```bash
curl http://localhost:8000/api/truelayer/accounts
```

### Get Account Balance
```bash
curl http://localhost:8000/api/truelayer/accounts/acc_123456789/balance
```

### Get Transactions
```bash
curl http://localhost:8000/api/truelayer/accounts/acc_123456789/transactions?limit=20
```

### Send Payment
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

---

## Error Handling

### User Already Exists
```json
{
  "detail": "User user_123 already exists"
}
```

### User Not Found (Not Onboarded)
```json
{
  "detail": "User user_123 not found. Call /onboard first."
}
```

### Invalid Auth Code
```json
{
  "detail": "Failed to get access token"
}
```

---

## Database Migration

When you're ready to move from CSV to a real database:

1. Create a `User` table with the same columns
2. Replace `user_storage.py` functions with database queries
3. All endpoint code remains the same!

This design keeps the API agnostic to storage layer.
