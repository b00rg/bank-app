#!/bin/bash
# =============================================================
# Alma – Alert curl test suite
# Run against: http://localhost:8000
# Prerequisites:
#   1. Backend running:  uvicorn main:app --reload
#   2. Twilio sandbox opted-in by carer phone number
#   3. .env populated with STRIPE_SECRET_KEY, TWILIO_* vars
# =============================================================

BASE="http://localhost:8000"
CARER_PHONE="[INSERT NUMBER HERE]"   # ← change to a real opted-in number
USER_EMAIL="test_$(date +%s)@alma.test"

echo ""
echo "============================================="
echo " STEP 1 — Create a user (starts a session)"
echo "============================================="
curl -s -c cookies.txt -X POST "$BASE/api/user/create" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Mary Tester\", \"email\": \"$USER_EMAIL\"}" | jq .

echo ""
echo "============================================="
echo " STEP 2 — Register a carer"
echo " EXPECTED: Carer receives WhatsApp registration message"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X POST "$BASE/api/carer/register" \
  -H "Content-Type: application/json" \
  -d "{\"carer_name\": \"John Carer\", \"carer_phone\": \"$CARER_PHONE\"}" | jq .

echo ""
echo "============================================="
echo " STEP 3 — Get carer (verify registration)"
echo "============================================="
curl -s -b cookies.txt "$BASE/api/carer" | jq .

echo ""
echo "============================================="
echo " STEP 4 — Normal payment (no alert expected)"
echo " Amount: €50 | No suspicious description"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X POST "$BASE/api/payments/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 50.00, "description": "Grocery shopping"}' | jq .

echo ""
echo "============================================="
echo " STEP 5 — Large payment alert (≥ €200)"
echo " EXPECTED: Carer receives 💸 large payment WhatsApp"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X POST "$BASE/api/payments/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 250.00, "description": "New TV purchase"}' | jq .

echo ""
echo "============================================="
echo " STEP 6 — Suspicious description (elevated)"
echo " Keyword: 'gift card'"
echo " EXPECTED: Carer receives 🚨 fraud alert WhatsApp"
echo "           alma_message warns about scam pattern"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X POST "$BASE/api/payments/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.00, "description": "Buy gift card for friend"}' | jq .

echo ""
echo "============================================="
echo " STEP 7 — Suspicious description: bitcoin"
echo " EXPECTED: Elevated risk, carer alerted"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X POST "$BASE/api/payments/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 500.00, "description": "Bitcoin investment opportunity"}' | jq .

echo ""
echo "============================================="
echo " STEP 8 — Suspicious description: HMRC scam"
echo " EXPECTED: Elevated risk, carer alerted"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X POST "$BASE/api/payments/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 300.00, "description": "HMRC urgent tax payment"}' | jq .

echo ""
echo "============================================="
echo " STEP 9 — Stripe Radar: elevated risk card"
echo " Uses FORCE_RISK_LEVEL=elevated (set in .env)"
echo " EXPECTED: 🚨 fraud WhatsApp + elevated alma_message"
echo "============================================="
echo "  → Set FORCE_RISK_LEVEL=elevated in .env, restart server, then run:"
echo "  curl -s -b cookies.txt -X POST $BASE/api/payments/test-radar | jq ."

echo ""
echo "============================================="
echo " STEP 10 — Stripe Radar: highest risk card"
echo " Uses FORCE_RISK_LEVEL=highest (set in .env)"
echo " EXPECTED: Payment BLOCKED, 🚨 WhatsApp alert"
echo "============================================="
echo "  → Set FORCE_RISK_LEVEL=highest in .env, restart server, then run:"
echo "  curl -s -b cookies.txt -X POST $BASE/api/payments/test-radar | jq ."

echo ""
echo "============================================="
echo " STEP 11 — Remove carer"
echo " EXPECTED: Carer removed from session"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X DELETE "$BASE/api/carer" | jq .

echo ""
echo "============================================="
echo " STEP 12 — Suspicious payment WITHOUT carer"
echo " EXPECTED: No WhatsApp (no carer), but alma_message"
echo "           still warns about the scam pattern"
echo "============================================="
curl -s -b cookies.txt -c cookies.txt -X POST "$BASE/api/payments/create" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.00, "description": "Lottery prize claim"}' | jq .

echo ""
echo "============================================="
echo " STEP 13 — Webhook: simulate payment_intent.succeeded"
echo " Simulates Stripe calling your webhook directly"
echo " NOTE: Skips signature check if STRIPE_WEBHOOK_SECRET unset"
echo "============================================="
curl -s -X POST "$BASE/api/webhooks/stripe" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"payment_intent.succeeded\",
    \"data\": {
      \"object\": {
        \"id\": \"pi_test_123\",
        \"amount\": 15000,
        \"currency\": \"eur\",
        \"customer\": \"cus_test\",
        \"latest_charge\": null,
        \"metadata\": {
          \"carer_phone\": \"$CARER_PHONE\",
          \"carer_name\": \"John Carer\",
          \"user_name\": \"Mary Tester\"
        }
      }
    }
  }" | jq .

echo ""
echo "============================================="
echo " STEP 14 — Webhook: simulate payment_intent.payment_failed"
echo " EXPECTED: Carer receives ⚠️ failure WhatsApp"
echo "============================================="
curl -s -X POST "$BASE/api/webhooks/stripe" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"payment_intent.payment_failed\",
    \"data\": {
      \"object\": {
        \"id\": \"pi_test_456\",
        \"amount\": 5000,
        \"currency\": \"eur\",
        \"customer\": \"cus_test\",
        \"latest_charge\": null,
        \"last_payment_error\": {
          \"message\": \"Your card has insufficient funds.\"
        },
        \"metadata\": {
          \"carer_phone\": \"$CARER_PHONE\",
          \"carer_name\": \"John Carer\",
          \"user_name\": \"Mary Tester\"
        }
      }
    }
  }" | jq .

echo ""
echo "============================================="
echo " STEP 15 — Webhook: large payment succeeded"
echo " EXPECTED: Carer receives 💸 large payment alert"
echo "============================================="
curl -s -X POST "$BASE/api/webhooks/stripe" \
  -H "Content-Type: application/json" \
  -d "{
    \"type\": \"payment_intent.succeeded\",
    \"data\": {
      \"object\": {
        \"id\": \"pi_test_789\",
        \"amount\": 45000,
        \"currency\": \"eur\",
        \"customer\": \"cus_test\",
        \"latest_charge\": null,
        \"metadata\": {
          \"carer_phone\": \"$CARER_PHONE\",
          \"carer_name\": \"John Carer\",
          \"user_name\": \"Mary Tester\"
        }
      }
    }
  }" | jq .

echo ""
echo "============================================="
echo " ALL TESTS COMPLETE"
echo " Check your WhatsApp ($CARER_PHONE) for messages"
echo " Check server logs for ✅ ❌ 💬 output"
echo "============================================="

# Clean up cookie jar
rm -f cookies.txt