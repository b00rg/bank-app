import React, { useState, useCallback } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Home, CreditCard, HelpCircle, Mic } from "lucide-react";
import { useVoice } from "@/context/VoiceContext";

const tabs = [
  { label: "Home", icon: Home, path: "/dashboard" },
  { label: "Cards", icon: CreditCard, path: "/cards" },
  { label: "Support", icon: HelpCircle, path: "/support" },
];

const BottomNav = () => {
  const navigate = useNavigate();
  const { speak } = useVoice();
  const location = useLocation();
  const [isRecording, setIsRecording] = useState(false);

  const handleHomeClick = useCallback(() => {
    // home logic here
    speak('dashboard');
    navigate("/dashboard");
  }, [navigate]);

  const handleCardsClick = useCallback(() => {
    // cards logic here
    speak('cards');
    navigate("/cards");
  }, [navigate]);

  const handleSupportClick = useCallback(() => {
    // support logic here
    speak('support');
    navigate("/support");
  }, [navigate]);

  const tabHandlers = {
    Home: handleHomeClick,
    Cards: handleCardsClick,
    Support: handleSupportClick,
  };

  const handleMicPointerDown = useCallback(() => {
    setIsRecording(true);
    // start recording logic here
  }, []);

  const handleMicPointerUp = useCallback(() => {
    setIsRecording(false);
    // stop recording / send voice command here
  }, []);

  const handleMicPointerLeave = useCallback(() => {
    setIsRecording(false);
  }, []);

  const handleMicPointerCancel = useCallback(() => {
    setIsRecording(false);
  }, []);

  return (
    <nav
      className="flex items-center justify-around bg-secondary px-2 py-2 gap-1"
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
            onClick={tabHandlers[tab.label]}
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

      {/* Voice command: press and hold to "record" */}
      <div className="relative flex flex-col items-center gap-1 min-w-[56px] min-h-[48px]">
        {isRecording && (
          <span
            className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] font-semibold text-primary whitespace-nowrap voice-recording-pulse"
            aria-live="polite"
          >
            Listening…
          </span>
        )}
        <button
          type="button"
          aria-label={isRecording ? "Release to send voice command" : "Hold for voice command"}
          aria-pressed={isRecording}
          onPointerDown={handleMicPointerDown}
          onPointerUp={handleMicPointerUp}
          onPointerLeave={handleMicPointerLeave}
          onPointerCancel={handleMicPointerCancel}
          className={`relative flex flex-col items-center justify-center min-w-[44px] min-h-[44px] rounded-full transition-all duration-200 select-none touch-none ${
            isRecording
              ? "bg-primary text-primary-foreground scale-105 shadow-lg"
              : "bg-secondary-foreground/15 text-secondary-foreground hover:bg-secondary-foreground/25"
          }`}
        >
          {isRecording && (
            <span
              className="absolute inset-0 rounded-full border-2 border-primary border-opacity-60 voice-recording-ring"
              aria-hidden
            />
          )}
          <Mic size={22} strokeWidth={2.5} className="relative z-10" />
        </button>
        <span className="text-[10px] font-semibold text-secondary-foreground/70">Voice</span>
      </div>
    </nav>
  );
};

export default BottomNav;