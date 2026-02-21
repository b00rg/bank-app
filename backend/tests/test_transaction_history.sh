#!/bin/bash
# =============================================================
# Alma – Transaction tests
# Prerequisites: server running + user session with payments made
# =============================================================

BASE="http://localhost:8000"
COOKIE_JAR="cookies.txt"

echo ""
echo "--- STEP 1: Create user + make a test payment (so transactions exist) ---"
curl -s -X POST "$BASE/api/user/create" \
  -H "Content-Type: application/json" \
  -c $COOKIE_JAR \
  -d '{"name": "Margaret", "email": "margaret@test.com"}' | jq .

echo ""
echo "--- STEP 2: Make a test radar payment (creates real Stripe charge) ---"
echo "EXPECTED: payment processed"
curl -s -b $COOKIE_JAR -X POST "$BASE/api/payments/test-radar" | jq .

echo ""
echo "--- STEP 3: Fetch latest 10 transactions ---"
echo "EXPECTED: list with amount, status, risk_level for the charge above"
curl -s -b $COOKIE_JAR -X GET "$BASE/api/transactions" | jq .

echo ""
echo "--- STEP 4: Fetch transactions without session ---"
echo "EXPECTED: 401 No user session found"
curl -s -X GET "$BASE/api/transactions" | jq .

rm -f $COOKIE_JAR