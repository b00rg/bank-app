import React, { createContext, useContext, useRef, useCallback } from 'react';

const VoiceContext = createContext(null);

export const VoiceProvider = ({ children }) => {
  const audioRef = useRef(new Audio());

  const speak = useCallback((soundKey) => {
    if (!soundKey) return;

    // Construct path to public folder
    const audioPath = `/audio/${soundKey}.mp3`;

    // Stop current sound if playing
    audioRef.current.pause();
    audioRef.current.currentTime = 0;

    // Load and play new sound
    audioRef.current.src = audioPath;
    
    // Simple error handling if file doesn't exist
    audioRef.current.play().catch((e) => {
      console.warn(`Audio file missing for key: ${soundKey}`, e);
    });
  }, []);

  return (
    <VoiceContext.Provider value={{ speak }}>
      {children}
    </VoiceContext.Provider>
  );
};

export const useVoice = () => useContext(VoiceContext);