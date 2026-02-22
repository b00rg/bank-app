// API client for backend communication
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      credentials: "include", // send cookies with requests
      ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
  },

  // Auth endpoints
  auth: {
    signup: (userId, name, email) =>
      apiClient.request("/api/truelayer/onboard", {
        method: "POST",
        body: JSON.stringify({ user_id: userId, name, email }),
      }),
    login: (email, password) =>
      apiClient.request("/api/user/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      }),
    logout: () =>
      apiClient.request("/api/user/logout", { method: "POST" }),
    getProfile: () =>
      apiClient.request("/api/user/me"),
  },

  // User endpoints
  user: {
    getProfile: () =>
      apiClient.request("/api/user/me"),
    getAccounts: () =>
      apiClient.request("/api/truelayer/accounts"),
    getCards: () =>
      apiClient.request("/api/issuing/card"),
  },

  // Transactions endpoints
  transactions: {
    getHistory: (accountId) =>
      apiClient.request(`/api/transactions`),
    getCardTransactions: () =>
      apiClient.request(`/api/issuing/card/transactions`),
  },

  // Payments endpoints
  payments: {
    send: (recipient, amount, accountId) =>
      apiClient.request("/api/payments/create", {
        method: "POST",
        body: JSON.stringify({ recipient, amount, accountId }),
      }),
  },

  // Issuing/Cards endpoints
  cards: {
    createVirtualCard: (weeklyLimitEuros = 100, expirationMonths = 12, billingAddress = "", billingCity = "", billingPostal = "", blockedCategories = []) =>
      apiClient.request("/api/issuing/card/create", { 
        method: "POST",
        body: JSON.stringify({ 
          weekly_limit_euros: weeklyLimitEuros,
          expiration_months: expirationMonths,
          billing_address: billingAddress,
          billing_city: billingCity,
          billing_postal: billingPostal,
          blocked_categories: blockedCategories
        })
      }),
    getCard: () =>
      apiClient.request("/api/issuing/card"),
    freezeCard: (cardId) =>
      apiClient.request("/api/issuing/card/freeze", {
        method: "POST",
        body: JSON.stringify({ card_id: cardId }),
      }),
    unfreezeCard: (cardId) =>
      apiClient.request("/api/issuing/card/unfreeze", {
        method: "POST",
        body: JSON.stringify({ card_id: cardId }),
      }),
    updateSpendingLimit: (cardId, weeklyLimitEuros) =>
      apiClient.request("/api/issuing/card/limit", {
        method: "POST",
        body: JSON.stringify({ card_id: cardId, weekly_limit_euros: weeklyLimitEuros }),
      }),
    getCardTransactions: () =>
      apiClient.request("/api/issuing/card/transactions"),
  },

  // TrueLayer endpoints
  truelayer: {
    getAuthUrl: () =>
      apiClient.request("/api/truelayer/auth-url"),
    linkBank: (userId, authCode) =>
      apiClient.request("/api/truelayer/link-bank", {
        method: "POST",
        body: JSON.stringify({ user_id: userId, auth_code: authCode }),
      }),
    getAccounts: () =>
      apiClient.request("/api/truelayer/accounts"),
    getAccountTransactions: (accountId) =>
      apiClient.request(`/api/truelayer/accounts/${accountId}/transactions`),
    getAccountBalance: (accountId) =>
      apiClient.request(`/api/truelayer/accounts/${accountId}/balance`),
    getMyAccounts: (userId) =>
      apiClient.request(`/api/truelayer/my-accounts?user_id=${encodeURIComponent(userId)}`),
    getMyTransactions: (accountId, userId) =>
      apiClient.request(`/api/truelayer/my-transactions/${encodeURIComponent(accountId)}?user_id=${encodeURIComponent(userId)}`),
  },

  // Overseer endpoints
  overseer: {
    login: (number, password) =>
      apiClient.request("/api/overseer/login", {
        method: "POST",
        body: JSON.stringify({ number, password }),
      }),
    getUsers: () =>
      apiClient.request("/api/overseer/users"),
  },
};
