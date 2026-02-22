import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiClient } from "@/lib/api";

const AuthScreen = () => {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [overseerName, setOverseerName] = useState("");
  const [overseerNumber, setOverseerNumber] = useState("");
  const [overseerPassword, setOverseerPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      if (isSignup) {
        await apiClient.auth.signup(name, email, password, overseerName, overseerNumber, overseerPassword);
      } else {
        await apiClient.auth.login(email, password);
      }
      navigate("/dashboard");
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
            <span className="text-2xl font-semibold text-primary-foreground">B</span>
          </div>
          <h1 className="text-heading text-foreground">
            {isSignup ? "Create Account" : "Welcome Back"}
          </h1>
          <p className="text-body text-muted-foreground mt-1">
            {isSignup ? "Sign up to get started" : "Log in to your account"}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {isSignup && (
            <>
              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Full Name
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Alma Smith"
                  required
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Overseer Name
                </label>
                <input
                  type="text"
                  value={overseerName}
                  onChange={(e) => setOverseerName(e.target.value)}
                  placeholder="John Doe"
                  required
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Overseer Number
                </label>
                <input
                  type="tel"
                  value={overseerNumber}
                  onChange={(e) => setOverseerNumber(e.target.value)}
                  placeholder="+353 1 234 5678"
                  required
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Overseer Password
                </label>
                <input
                  type="password"
                  value={overseerPassword}
                  onChange={(e) => setOverseerPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>
            </>
          )}

          <div>
            <label className="text-sm font-semibold text-foreground block mb-1.5">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="mail@example.com"
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
            {isLoading ? "Loading..." : isSignup ? "Sign Up" : "Log In"}
          </button>

          {error && (
            <p className="text-sm text-red-500 mt-2">{error}</p>
          )}
        </form>
      </div>

      {/* Toggle */}
      <div className="space-y-3 w-full max-w-sm">
        <button
          onClick={() => setIsSignup(!isSignup)}
          className="text-body text-muted-foreground"
        >
          {isSignup ? "Already have an account? " : "Don't have an account? "}
          <span className="font-semibold text-foreground underline">
            {isSignup ? "Log In" : "Sign Up"}
          </span>
        </button>

        <div className="pt-2 border-t border-border">
          <button
            onClick={() => navigate("/overseer")}
            className="w-full py-3 rounded-xl bg-secondary text-secondary-foreground font-semibold hover:opacity-90 transition"
          >
            Overseer Sign In
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthScreen;
