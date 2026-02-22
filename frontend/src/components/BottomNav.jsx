import React, { useState, useCallback, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Home, CreditCard, HelpCircle, Mic } from "lucide-react";
import VoiceOverlay from "./VoiceOverlay"; // Import the component we just made

const tabs = [
  { label: "Home", icon: Home, path: "/dashboard" },
  { label: "Cards", icon: CreditCard, path: "/cards" },
  { label: "Support", icon: HelpCircle, path: "/support" },
];

const BottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // State: 'idle', 'listening', 'processing'
  const [voiceState, setVoiceState] = useState("idle");
  const timeoutRef = useRef(null);

  // Start Listening
  const handleMicDown = useCallback((e) => {
    // Prevent default touch actions (scrolling, etc) while holding
    if(e.cancelable) e.preventDefault();
    setVoiceState("listening");
  }, []);

  // Stop Listening & Start Processing
  const handleMicUp = useCallback(() => {
    if (voiceState === "listening") {
      setVoiceState("processing");

      // Simulate API call delay (2 seconds)
      timeoutRef.current = setTimeout(() => {
        setVoiceState("idle");
        // Optional: Navigate or show a toast here after "success"
      }, 2500);
    }
  }, [voiceState]);

  // Clean up timeout if component unmounts
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  // Global event listener to catch 'pointerup' even if finger drags off button
  useEffect(() => {
    const handleGlobalUp = () => {
      if (voiceState === "listening") {
        handleMicUp();
      }
    };

    window.addEventListener('pointerup', handleGlobalUp);
    window.addEventListener('touchend', handleGlobalUp);
    return () => {
      window.removeEventListener('pointerup', handleGlobalUp);
      window.removeEventListener('touchend', handleGlobalUp);
    };
  }, [voiceState, handleMicUp]);

  return (
    <>
      {/* 
        The Overlay sits outside the nav structure conceptually, 
        but inside the component so it shares state.
        We use fixed positioning in the Overlay CSS to cover the phone screen.
      */}
      <VoiceOverlay currentState={voiceState} />

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

        {/* Voice Command Button */}
        <div className="relative flex flex-col items-center gap-1 min-w-[56px] min-h-[48px]">
          <button
            type="button"
            aria-label="Hold for voice command"
            onPointerDown={handleMicDown}
            // Note: onPointerUp is handled by window listener for better UX
            className={`relative flex flex-col items-center justify-center min-w-[44px] min-h-[44px] rounded-full transition-all duration-300 select-none touch-none ${
              voiceState !== 'idle'
                ? "bg-primary text-primary-foreground scale-90 opacity-0" // Hide visually when overlay takes over
                : "bg-secondary-foreground/15 text-secondary-foreground hover:bg-secondary-foreground/25"
            }`}
          >
            <Mic size={22} strokeWidth={2.5} />
          </button>
          <span 
            className={`text-[10px] font-semibold text-secondary-foreground/70 transition-opacity ${
              voiceState !== 'idle' ? 'opacity-0' : 'opacity-100'
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