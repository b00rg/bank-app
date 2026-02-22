import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "@/lib/api";

const OverseerLogin = () => {
  const navigate = useNavigate();
  const [number, setNumber] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await apiClient.overseer.login(number, password);
      navigate("/overseer/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-between h-full px-6 py-8 fade-in">
      <div className="w-full max-w-sm mt-8 slide-up">
        {/* Logo / Branding */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl font-semibold text-primary-foreground">O</span>
          </div>
          <h1 className="text-heading text-foreground">Overseer Portal</h1>
          <p className="text-body text-muted-foreground mt-1">
            Manage your users' accounts
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-semibold text-foreground block mb-1.5">
              Phone Number
            </label>
            <input
              type="tel"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              placeholder="+353 1 234 5678"
              required
              className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
            />
          </div>

          <div>
            <label className="text-sm font-semibold text-foreground block mb-1.5">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="btn-press w-full py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold min-h-[56px] mt-2 disabled:opacity-50"
          >
            {isLoading ? "Logging in..." : "Log In as Overseer"}
          </button>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}
        </form>
      </div>

      {/* Toggle */}
      <button
        onClick={() => navigate("/")}
        className="text-body text-muted-foreground mt-6 mb-4"
      >
        <span className="font-semibold text-foreground underline">
          Back to User Login
        </span>
      </button>
    </div>
  );
};

export default OverseerLogin;
