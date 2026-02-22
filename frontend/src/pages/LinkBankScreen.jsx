import React, { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiClient } from "@/lib/api";

const LinkBankScreen = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [error, setError] = useState("");

  // When TrueLayer redirects back with ?code=..., auto-exchange it
  useEffect(() => {
    const code = searchParams.get("code");
    if (!code) return;

    // user_id comes back via ?state= (threaded through TrueLayer OAuth)
    // fall back to localStorage for same-origin flows
    const userId = searchParams.get("state") || localStorage.getItem("user_id");
    if (!userId) {
      setError("Session expired. Please sign up again.");
      setStatus("error");
      return;
    }
    localStorage.setItem("user_id", userId);

    const exchangeCode = async () => {
      setStatus("loading");
      try {
        await apiClient.truelayer.linkBank(userId, code);
        setStatus("success");
        // Small delay so user sees the success state
        setTimeout(() => navigate("/dashboard"), 1500);
      } catch (err) {
        setError(err.message || "Failed to link bank account.");
        setStatus("error");
      }
    };

    exchangeCode();
  }, [searchParams, navigate]);

  const handleLinkBank = async () => {
    setStatus("loading");
    setError("");
    try {
      const { auth_url } = await apiClient.truelayer.getAuthUrl();
      const userId = localStorage.getItem("user_id");
      const urlWithState = userId ? `${auth_url}&state=${encodeURIComponent(userId)}` : auth_url;
      window.location.href = urlWithState;
    } catch (err) {
      setError(err.message || "Failed to get bank authorization URL.");
      setStatus("idle");
    }
  };

  const handleSkip = () => navigate("/dashboard");

  return (
    <div className="flex flex-col items-center justify-between h-full px-6 py-8 fade-in">
      <div className="w-full max-w-sm mt-8 slide-up">
        {/* Icon */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl font-semibold text-primary-foreground">B</span>
          </div>
          <h1 className="text-heading text-foreground">Link Your Bank</h1>
          <p className="text-body text-muted-foreground mt-1">
            Connect your bank account to get started
          </p>
        </div>

        {status === "loading" && !searchParams.get("code") && (
          <p className="text-center text-muted-foreground">Redirecting to your bank...</p>
        )}

        {status === "loading" && searchParams.get("code") && (
          <div className="text-center">
            <p className="text-muted-foreground">Linking your bank account...</p>
            <div className="mt-4 w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          </div>
        )}

        {status === "success" && (
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-3">
              <span className="text-green-600 text-xl font-bold">&#10003;</span>
            </div>
            <p className="text-foreground font-semibold">Bank linked successfully!</p>
            <p className="text-muted-foreground text-sm mt-1">Taking you to your dashboard...</p>
          </div>
        )}

        {status === "error" && (
          <div className="space-y-4">
            <p className="text-sm text-red-500 text-center">{error}</p>
            <button
              onClick={handleLinkBank}
              className="btn-press w-full py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold min-h-[56px]"
            >
              Try Again
            </button>
          </div>
        )}

        {status === "idle" && (
          <div className="space-y-4">
            {/* Steps */}
            <div className="bg-card border border-border rounded-2xl p-4 space-y-3">
              <StepItem number="1" text="We redirect you to your bank's secure login" />
              <StepItem number="2" text="You authorise read-only access" />
              <StepItem number="3" text="We securely save your token so you can view balances &amp; transactions" />
            </div>

            <button
              onClick={handleLinkBank}
              className="btn-press w-full py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold min-h-[56px]"
            >
              Link Your Bank
            </button>
          </div>
        )}
      </div>

      {status === "idle" && (
        <div className="w-full max-w-sm">
          <button
            onClick={handleSkip}
            className="text-body text-muted-foreground w-full text-center"
          >
            Skip for now
          </button>
        </div>
      )}
    </div>
  );
};

const StepItem = ({ number, text }) => (
  <div className="flex items-start gap-3">
    <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center flex-shrink-0 mt-0.5">
      <span className="text-xs font-bold text-primary-foreground">{number}</span>
    </div>
    <p className="text-sm text-foreground" dangerouslySetInnerHTML={{ __html: text }} />
  </div>
);

export default LinkBankScreen;
