import React, { useState, useCallback, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Home, CreditCard, HelpCircle, Mic } from "lucide-react";
import VoiceOverlay from "./VoiceOverlay";

const tabs = [
  { label: "Home", icon: Home, path: "/dashboard" },
  { label: "Cards", icon: CreditCard, path: "/cards" },
  { label: "Support", icon: HelpCircle, path: "/support" },
];

const BottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const [voiceState, setVoiceState] = useState("idle"); // 'idle' | 'listening' | 'processing' | 'success'
  const [voiceResult, setVoiceResult] = useState(null);
  const timeoutRef = useRef(null);

  const handleMicDown = useCallback((e) => {
    if (e.cancelable) e.preventDefault();
    setVoiceState("listening");
  }, []);

  const handleMicUp = useCallback(() => {
    if (voiceState !== "listening") return;
    setVoiceState("processing");

    // Simulate backend call
    timeoutRef.current = setTimeout(async () => {
      // Mock backend response
      const mockResponse = {
        intent: "TRANSFER_DRAFT",
        amount: "20.00",
        currency: "EUR",
        payee_label: "Anna",
        assistant_say: "Transfer of €20.00 to Anna drafted!",
        summary: {
          from: "Account 1",
          to: "Anna",
          amount: "20.00",
          currency: "EUR",
          status: "Pending",
        },
      };

      setVoiceResult(mockResponse);
      setVoiceState("success");

      // Auto-dismiss after 3 seconds and navigate
      timeoutRef.current = setTimeout(() => {
        setVoiceState("idle");
        setVoiceResult(null);
        navigate("/dashboard", {
          state: {
            amount: mockResponse.amount,
            currency: mockResponse.currency,
            payee: mockResponse.payee_label,
            summary: mockResponse.summary,
          },
        });
      }, 5000);
    }, 10000);
  }, [voiceState, navigate]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  useEffect(() => {
    const handleGlobalUp = () => {
      if (voiceState === "listening") handleMicUp();
    };
    window.addEventListener("pointerup", handleGlobalUp);
    window.addEventListener("touchend", handleGlobalUp);
    return () => {
      window.removeEventListener("pointerup", handleGlobalUp);
      window.removeEventListener("touchend", handleGlobalUp);
    };
  }, [voiceState, handleMicUp]);

  return (
    <>
      <VoiceOverlay currentState={voiceState} result={voiceResult} />

      <nav
        className="flex items-center justify-around bg-secondary px-2 py-2 gap-1 relative z-40"
        role="tablist"
        aria-label="Main navigation"
      >
        {tabs.map((tab) => {
          const isActive =
            location.pathname === tab.path ||
            (tab.path === "/dashboard" && location.pathname.startsWith("/send"));
          const Icon = tab.icon;

          return (
            <button
              key={tab.label}
              role="tab"
              aria-selected={isActive}
              aria-label={tab.label}
              onClick={() => navigate(tab.path)}
              className={`btn-press flex flex-col items-center gap-1 min-w-[64px] min-h-[48px] px-2 py-1.5 rounded-xl transition-colors ${
                isActive
                  ? "text-secondary-foreground"
                  : "text-secondary-foreground/50 hover:text-secondary-foreground/80"
              }`}
            >
              <Icon size={24} strokeWidth={isActive ? 2.5 : 2} />
              <span className="text-xs font-semibold">{tab.label}</span>
            </button>
          );
        })}

        <div className="relative flex flex-col items-center gap-1 min-w-[56px] min-h-[48px]">
          <button
            type="button"
            aria-label="Hold for voice command"
            onPointerDown={handleMicDown}
            className={`relative flex flex-col items-center justify-center min-w-[44px] min-h-[44px] rounded-full transition-all duration-300 select-none touch-none ${
              voiceState !== "idle"
                ? "bg-primary text-primary-foreground scale-90 opacity-0 pointer-events-none"
                : "bg-secondary-foreground/15 text-secondary-foreground hover:bg-secondary-foreground/25"
            }`}
          >
            <Mic size={22} strokeWidth={2.5} />
          </button>
          <span
            className={`text-[10px] font-semibold text-secondary-foreground/70 transition-opacity ${
              voiceState !== "idle" ? "opacity-0" : "opacity-100"
            }`}
          >
            Voice
          </span>
        </div>
      </nav>
    </>
  );
};

export default BottomNav;