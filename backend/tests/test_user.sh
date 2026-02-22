# =============================================
# STEP 1 — Create a user
# EXPECTED: success, stripe_customer_id returned
# =============================================
curl -s -X POST http://localhost:8000/api/user/create \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"name": "Margaret", "email": "margaret@test.com"}' | jq .

# =============================================
# STEP 2 — Get current user (session check)
# EXPECTED: returns Margaret's name, email, stripe_customer
# =============================================
curl -s -X GET http://localhost:8000/api/user/me \
  -b cookies.txt | jq .

# =============================================
# STEP 3 — Create duplicate user (same email)
# EXPECTED: Stripe allows it (no unique email enforcement)
#           but good to know behaviour
# =============================================
curl -s -X POST http://localhost:8000/api/user/create \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"name": "Margaret", "email": "margaret@test.com"}' | jq .

# =============================================
# STEP 4 — Get user without a session (new terminal = no cookies)
# EXPECTED: 404 "No user session found"
# =============================================
curl -s -X GET http://localhost:8000/api/user/me | jq .

# =============================================
# STEP 5 — Logout
# EXPECTED: success, session cleared
# =============================================
curl -s -X POST http://localhost:8000/api/user/logout \
  -b cookies.txt -c cookies.txt | jq .

# =============================================
# STEP 6 — Get user after logout
# EXPECTED: 404 "No user session found"
# =============================================
curl -s -X GET http://localhost:8000/api/user/me \
  -b cookies.txt | jq .

# =============================================
# STEP 7 — Missing fields
# EXPECTED: 422 Unprocessable Entity
# =============================================
curl -s -X POST http://localhost:8000/api/user/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Margaret"}' | jq .

# =============================================
# STEP 8 — Empty strings
# EXPECTED: Stripe will likely accept but worth knowing
# =============================================
curl -s -X POST http://localhost:8000/api/user/create \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"name": "", "email": ""}' | jq .