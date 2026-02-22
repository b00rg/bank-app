import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Fingerprint, Delete } from "lucide-react";

const LoginScreen = () => {
  const [pin, setPin] = useState("");
  const [error, setError] = useState(false);
  const navigate = useNavigate();

  const handleDigit = (digit) => {
    if (pin.length < 4) {
      const newPin = pin + digit;
      setPin(newPin);
      setError(false);
      if (newPin.length === 4) {
        setTimeout(() => {
          if (newPin === "1234") {
            navigate("/dashboard");
          } else {
            setError(true);
            setPin("");
          }
        }, 400);
      }
    }
  };

  const handleDelete = () => {
    setPin(pin.slice(0, -1));
    setError(false);
  };

  const handleFaceId = () => {
    setTimeout(() => navigate("/dashboard"), 600);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 18) return "Good Afternoon";
    return "Good Evening";
  };

  return (
    <div className="flex flex-col items-center justify-between h-full px-6 py-8 fade-in">
      {/* Greeting */}
      <div className="text-center mt-4 slide-up">
        <div className="w-16 h-16 rounded-full bg-secondary flex items-center justify-center mx-auto mb-4">
          <span className="text-2xl font-semibold text-secondary-foreground">M</span>
        </div>
        <h1 className="text-heading text-foreground mb-1">
          {getGreeting()}, Alma
        </h1>
        <p className="text-body text-muted-foreground">
          Enter your PIN to log in
        </p>
      </div>

      {/* PIN Dots */}
      <div className="flex gap-4 my-6" role="status" aria-label={`${pin.length} of 4 digits entered`}>
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className={`w-4 h-4 rounded-full transition-all duration-200 ${
              i < pin.length
                ? error
                  ? "bg-destructive scale-110"
                  : "bg-foreground scale-110"
                : "bg-border"
            }`}
          />
        ))}
      </div>
      {error && (
        <p className="text-destructive text-sm font-semibold -mt-4 mb-2" role="alert">
          Wrong PIN. Please try again.
        </p>
      )}

      {/* Number Pad */}
      <div className="grid grid-cols-3 gap-3 w-full max-w-[280px]">
        {["1", "2", "3", "4", "5", "6", "7", "8", "9"].map((digit) => (
          <button
            key={digit}
            onClick={() => handleDigit(digit)}
            className="btn-press w-full aspect-square rounded-2xl bg-card text-foreground text-heading font-semibold flex items-center justify-center border border-border hover:bg-muted transition-colors min-h-[64px]"
            aria-label={`Digit ${digit}`}
          >
            {digit}
          </button>
        ))}
        <button
          onClick={handleFaceId}
          className="btn-press w-full aspect-square rounded-2xl bg-secondary text-secondary-foreground flex items-center justify-center min-h-[64px]"
          aria-label="Log in with Face ID"
        >
          <Fingerprint size={28} />
        </button>
        <button
          onClick={() => handleDigit("0")}
          className="btn-press w-full aspect-square rounded-2xl bg-card text-foreground text-heading font-semibold flex items-center justify-center border border-border hover:bg-muted transition-colors min-h-[64px]"
          aria-label="Digit 0"
        >
          0
        </button>
        <button
          onClick={handleDelete}
          className="btn-press w-full aspect-square rounded-2xl bg-card text-muted-foreground flex items-center justify-center border border-border hover:bg-muted transition-colors min-h-[64px]"
          aria-label="Delete last digit"
        >
          <Delete size={24} />
        </button>
      </div>

      {/* <p className="text-sm text-muted-foreground mt-4">
        Hint: PIN is <strong>1234</strong>
      </p> */}
    </div>
  );
};

export default LoginScreen;
