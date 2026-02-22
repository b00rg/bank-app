import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { CreditCard, Lock, Smartphone } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { useVoice } from "@/context/VoiceContext";

const physicalCards = [
  { id: 1, type: "Current Account", number: "****4821", balance: "£3,842.50", active: true },
  { id: 2, type: "Savings", number: "****7192", balance: "£12,430.00", active: true },
];

const virtualCards = [
  { id: 3, type: "Online Shopping", number: "****8844", balance: "£0.00", active: true },
  { id: 4, type: "Subscriptions", number: "****2291", balance: "£120.00", active: true },
];

const CardsScreen = () => {
  const navigate = useNavigate();
  const { speak } = useVoice();

  useEffect(() => {
    speak("cards");
  }, [speak]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 pb-4">
        <div className="pt-6 pb-2 fade-in">
          <p className="text-body text-muted-foreground">Your</p>
          <h1 className="text-balance text-foreground">Cards.</h1>
          <p className="text-body text-muted-foreground mt-2">
            Manage your accounts and cards.
          </p>
        </div>

        {/* Physical cards */}
        <div className="mt-6 slide-up">
          <h2 className="text-heading-sm text-foreground mb-3">Physical cards</h2>
          <div className="space-y-4">
            {physicalCards.map((card) => (
              <button
                key={card.id}
                onClick={() => {
                  speak(`card${card.id}`);
                  navigate(`/card/${card.id}/transactions`);
                }}
                className="btn-press w-full text-left rounded-2xl p-6 bg-secondary text-secondary-foreground shadow-md"
                aria-label={`${card.type}, ${card.number}`}
              >
                <div className="flex items-center justify-between mb-6">
                  <CreditCard size={28} />
                  <span className="text-xs font-semibold opacity-70 uppercase tracking-wider">
                    {card.active ? "Active" : "Frozen"}
                  </span>
                </div>
                <p className="text-2xl font-mono font-semibold tracking-widest mb-4">{card.number}</p>
                <div className="flex justify-between items-end">
                  <div>
                    <p className="text-xs opacity-70">{card.type}</p>
                    <p className="text-xl font-semibold">{card.balance}</p>
                  </div>
                  <Lock size={18} className="opacity-50" />
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Virtual cards */}
        <div className="mt-8 slide-up">
          <h2 className="text-heading-sm text-foreground mb-3">Virtual cards</h2>
          <div className="space-y-4">
            {virtualCards.map((card) => (
              <button
                key={card.id}
                onClick={() => navigate(`/card/${card.id}/transactions`)}
                className="btn-press w-full text-left rounded-2xl p-6 border-2 border-dashed border-primary/40 bg-primary/5 text-foreground hover:border-primary/60 hover:bg-primary/10 transition-colors"
                aria-label={`Virtual ${card.type}, ${card.number}`}
              >
                <div className="flex items-center justify-between mb-6">
                  <Smartphone size={28} className="text-primary" />
                  <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                    {card.active ? "Active" : "Paused"}
                  </span>
                </div>
                <p className="text-2xl font-mono font-semibold tracking-widest mb-4 text-foreground">{card.number}</p>
                <div className="flex justify-between items-end">
                  <div>
                    <p className="text-xs text-muted-foreground">{card.type}</p>
                    <p className="text-xl font-semibold text-foreground">{card.balance}</p>
                  </div>
                  <Lock size={18} className="text-muted-foreground opacity-50" />
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
      <BottomNav />
    </div>
  );
};

export default CardsScreen;
