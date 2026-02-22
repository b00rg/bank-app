import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { CreditCard, Lock, Smartphone, Plus } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { useVoice } from "@/context/VoiceContext";
import { apiClient } from "@/lib/api";

const mockPhysicalCards = [
  { id: 1, type: "Current Account", number: "****4821", balance: "£3,842.50", active: true },
  { id: 2, type: "Savings", number: "****7192", balance: "£12,430.00", active: true },
];

const CardsScreen = () => {
  const navigate = useNavigate();
  const { speak } = useVoice();
  const [virtualCards, setVirtualCards] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    speak("cards");
    fetchCards();
  }, [speak]);

  const fetchCards = async () => {
    try {
      setIsLoading(true);
      const cardData = await apiClient.cards.getCard();
      if (cardData && cardData.card_id) {
        setVirtualCards([{
          id: cardData.card_id,
          type: "Virtual Card",
          number: `****${cardData.last4}`,
          status: cardData.status,
          active: cardData.status === "active",
          balance: cardData.balance || "€0.00",
        }]);
      }
    } catch (err) {
      console.warn("Failed to fetch card:", err.message);
      setVirtualCards([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCard = async () => {
    try {
      setIsLoading(true);
      const newCard = await apiClient.cards.createVirtualCard();
      setVirtualCards([{
        id: newCard.card_id,
        type: "Virtual Card",
        number: `****${newCard.last4}`,
        status: newCard.status,
        active: newCard.status === "active",
        balance: "€0.00",
      }]);
      speak("card created");
    } catch (err) {
      setError(err.message);
      speak("error creating card");
    } finally {
      setIsLoading(false);
    }
  };

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
            {mockPhysicalCards.map((card) => (
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
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-heading-sm text-foreground">Virtual cards</h2>
            <button
              onClick={handleCreateCard}
              disabled={isLoading}
              className="p-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              aria-label="Create new virtual card"
            >
              <Plus size={20} />
            </button>
          </div>

          {error && (
            <div className="p-3 bg-red-100 text-red-800 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          {isLoading && virtualCards.length === 0 ? (
            <div className="text-center py-6 text-muted-foreground">
              Loading cards...
            </div>
          ) : virtualCards.length === 0 ? (
            <div className="text-center py-8 border-2 border-dashed border-primary/40 rounded-2xl bg-primary/5">
              <Smartphone size={32} className="mx-auto text-primary mb-2" />
              <p className="text-muted-foreground mb-3">No virtual cards yet</p>
              <button
                onClick={handleCreateCard}
                disabled={isLoading}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-semibold hover:bg-primary/90 disabled:opacity-50"
              >
                Create Your First Card
              </button>
            </div>
          ) : (
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
          )}
        </div>
      </div>
      <BottomNav />
    </div>
  );
};

export default CardsScreen;
