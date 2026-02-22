import React from "react";
import { Mic, CheckCircle2 } from "lucide-react";

const VoiceOverlay = ({ currentState, result }) => {
  if (currentState === "idle") return null;

  return (
    <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-secondary/95 backdrop-blur-md px-8">

      {currentState === "listening" && (
        <div className="flex flex-col items-center gap-6">
          <div className="relative w-20 h-20 bg-primary rounded-full flex items-center justify-center voice-recording-pulse">
            <Mic className="w-8 h-8 text-primary-foreground" />
          </div>
          <p className="text-secondary-foreground/70 text-sm">Listening...</p>
        </div>
      )}

      {currentState === "processing" && (
        <div className="flex flex-col items-center gap-6">
          <div className="w-20 h-20 rounded-full border-4 border-primary/20 border-t-primary processing-spin" />
          <p className="text-secondary-foreground/70 text-sm">Processing...</p>
        </div>
      )}

      {currentState === "success" && result && (
        <div className="flex flex-col items-center gap-6 text-center bounce-check">
          <CheckCircle2 className="w-16 h-16 text-primary" />
          <div>
            <p className="text-secondary-foreground text-xl font-semibold">
              Transferred €{result.summary.amount}
            </p>
            <p className="text-secondary-foreground/60 mt-1">
              to {result.summary.to}
            </p>
          </div>
        </div>
      )}

    </div>
  );
};

export default VoiceOverlay;