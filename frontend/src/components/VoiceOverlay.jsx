import React from "react";
import { Mic, Loader2, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

const VoiceOverlay = ({ currentState }) => {
  // currentState can be: 'idle', 'listening', 'processing'

  if (currentState === "idle") return null;

  return (
    <div className="absolute inset-0 z-50 flex flex-col items-center justify-center overflow-hidden">
      {/* Backdrop with blur */}
      <div 
        className={cn(
          "absolute inset-0 bg-secondary/95 backdrop-blur-md transition-opacity duration-300",
          currentState === "idle" ? "opacity-0" : "opacity-100"
        )} 
      />

      {/* Content Container */}
      <div className="relative z-10 flex flex-col items-center justify-center w-full h-full">
        
        {/* LISTENING STATE */}
        {currentState === "listening" && (
          <div className="flex flex-col items-center mic-transition-enter">
            <div className="relative flex items-center justify-center">
              {/* Ripple Effects */}
              <div className="absolute w-24 h-24 bg-primary/20 rounded-full voice-ripple delay-100" />
              <div className="absolute w-24 h-24 bg-primary/15 rounded-full voice-ripple delay-300" />
              <div className="absolute w-24 h-24 bg-primary/10 rounded-full voice-ripple delay-500" />
              
              {/* Main Mic Bubble */}
              <div className="relative w-24 h-24 bg-primary rounded-full flex items-center justify-center shadow-2xl shadow-black/20">
                <Mic className="w-10 h-10 text-primary-foreground" />
              </div>
            </div>

            <div className="mt-8 space-y-2 text-center">
              <h2 className="text-2xl font-semibold text-secondary-foreground">Listening...</h2>
              <p className="text-secondary-foreground/60 text-sm">Keep holding to speak</p>
            </div>
            
            {/* Visual Waveform Simulation */}
            <div className="flex items-center gap-1 mt-8 h-8">
               {[...Array(5)].map((_, i) => (
                 <div 
                   key={i} 
                   className="w-1.5 bg-primary rounded-full animate-pulse" 
                   style={{ 
                     height: `${Math.random() * 100}%`,
                     animationDuration: `${0.5 + Math.random() * 0.5}s` 
                   }}
                 />
               ))}
            </div>
          </div>
        )}

        {/* PROCESSING STATE */}
        {currentState === "processing" && (
          <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
            <div className="relative w-24 h-24 flex items-center justify-center">
              {/* Spinning Ring */}
              <div className="absolute inset-0 rounded-full border-4 border-primary/20 border-t-primary processing-spin" />
            </div>

            <div className="mt-8 space-y-2 text-center">
              <h2 className="text-xl font-medium text-secondary-foreground">Processing</h2>
              <p className="text-secondary-foreground/60 text-sm">Analyzing your request...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceOverlay;