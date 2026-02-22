#!/bin/bash
# =============================================================
# Alma – Stripe Issuing test suite (IRELAND COMPLIANT, robust)
# =============================================================

BASE="http://localhost:8000"
CARER_PHONE="[insert no here]"  # Ensure this is your verified Twilio number

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COOKIE_JAR="$SCRIPT_DIR/cookies.txt"

rm -f "$COOKIE_JAR"

echo ""
echo "============================================="
echo " SETUP — Create user + register carer"
echo "============================================="

# --- Create user ---
echo ""
echo "--- Creating user ---"
CREATE_USER_RESPONSE=$(curl -s \
  -X POST "$BASE/api/user/create" \
  -H "Content-Type: application/json" \
  -c "$COOKIE_JAR" \
  -d '{"name": "Margaret", "email": "margaret@test.com"}')

echo "$CREATE_USER_RESPONSE" | jq . || echo "$CREATE_USER_RESPONSE"

# --- Register carer ---
echo ""
echo "--- Registering carer ---"
REGISTER_CARER_RESPONSE=$(curl -s \
  -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST "$BASE/api/carer/register" \
  -H "Content-Type: application/json" \
  -d "{\"carer_name\": \"John Carer\", \"carer_phone\": \"$CARER_PHONE\"}")

echo "$REGISTER_CARER_RESPONSE" | jq . || echo "$REGISTER_CARER_RESPONSE"

echo ""
echo "============================================="
echo " STEP 1 — Set up virtual card"
echo " EXPECTED: Success with card_id"
echo "============================================="

# --- Create virtual card with Ireland-safe address ---
CREATE_RESPONSE=$(curl -s \
  -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST "$BASE/api/issuing/card/create" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+353871234567",
    "line1": "1 Grafton Street",
    "city": "Dublin",
    "postal_code": "D02 XY19",
    "country": "IE"
  }')

echo "$CREATE_RESPONSE" | jq . || echo "$CREATE_RESPONSE"

# --- Extract card_id safely ---
CARD_ID=$(echo "$CREATE_RESPONSE" | jq -r '.card_id // empty')
if [ -z "$CARD_ID" ] || [ "$CARD_ID" == "null" ]; then
  echo "❌ Failed to create card. Exiting test."
  exit 1
fi
echo "Card ID: $CARD_ID"

echo ""
echo "============================================="
echo " STEP 2 — Get card details"
echo "============================================="
GET_CARD_RESPONSE=$(curl -s -b "$COOKIE_JAR" -X GET "$BASE/api/issuing/card")
echo "$GET_CARD_RESPONSE" | jq . || echo "$GET_CARD_RESPONSE"

echo ""
echo "============================================="
echo " STEP 3 — Freeze card"
echo "============================================="
FREEZE_RESPONSE=$(curl -s \
  -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST "$BASE/api/issuing/card/freeze" \
  -H "Content-Type: application/json" \
  -d "{\"card_id\": \"$CARD_ID\"}")

echo "$FREEZE_RESPONSE" | jq . || echo "$FREEZE_RESPONSE"

echo ""
echo "============================================="
echo " STEP 4 — Unfreeze card"
echo "============================================="
UNFREEZE_RESPONSE=$(curl -s \
  -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST "$BASE/api/issuing/card/unfreeze" \
  -H "Content-Type: application/json" \
  -d "{\"card_id\": \"$CARD_ID\"}")

echo "$UNFREEZE_RESPONSE" | jq . || echo "$UNFREEZE_RESPONSE"

echo ""
echo "============================================="
echo " STEP 5 — Update limit to €200"
echo "============================================="
UPDATE_LIMIT_RESPONSE=$(curl -s \
  -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
  -X POST "$BASE/api/issuing/card/limit" \
  -H "Content-Type: application/json" \
  -d "{\"card_id\": \"$CARD_ID\", \"weekly_limit_euros\": 200.00}")

echo "$UPDATE_LIMIT_RESPONSE" | jq . || echo "$UPDATE_LIMIT_RESPONSE"

echo ""
echo "============================================="
echo " TEST COMPLETE"
echo "============================================="

# --- Clean up ---
rm -f "$COOKIE_JAR"
