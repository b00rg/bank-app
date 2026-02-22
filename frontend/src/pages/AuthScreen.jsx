import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const AuthScreen = () => {
  const navigate = useNavigate();
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate("/");
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
            <div>
              <label className="text-sm font-semibold text-foreground block mb-1.5">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Alma Smith"
                className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
              />
            </div>
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
              className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground text-body placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
            />
          </div>

          <button
            type="submit"
            className="btn-press w-full py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold min-h-[56px] mt-2"
            onClick={() => navigate("/dashboard")}
          >
            {isSignup ? "Sign Up" : "Log In"}
          </button>
        </form>
      </div>

      {/* Toggle */}
      <button
        onClick={() => setIsSignup(!isSignup)}
        className="text-body text-muted-foreground mt-6 mb-4"
      >
        {isSignup ? "Already have an account? " : "Don't have an account? "}
        <span className="font-semibold text-foreground underline">
          {isSignup ? "Log In" : "Sign Up"}
        </span>
      </button>
    </div>
  );
};

export default AuthScreen;
