import React, { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { ArrowLeft, ChevronDown, ChevronUp } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { useVoice } from "@/context/VoiceContext";
import { apiClient } from "@/lib/api";

const groupByMonth = (transactions) => {
  const groups = {};
  for (const tx of transactions) {
    const date = new Date(tx.timestamp);
    const key = date.toLocaleString("en", { month: "long", year: "numeric" });
    if (!groups[key]) groups[key] = [];
    groups[key].push(tx);
  }
  return groups;
};

const getInitials = (description = "") => {
  const words = description.trim().split(/\s+/);
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase();
  return description.slice(0, 2).toUpperCase();
};

const Transactions = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const { speak } = useVoice();
  const isCard = location.pathname.startsWith("/card/");

  const account = location.state?.account || { account_id: id, name: "Account", balance: null, currency: "" };
  const backPath = isCard ? "/cards" : `/account/${id}`;

  const [grouped, setGrouped] = useState({});
  const [openMonth, setOpenMonth] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isCard) {
      setIsLoading(false);
      return;
    }
    const fetchTransactions = async () => {
      try {
        setIsLoading(true);
        const userId = localStorage.getItem("user_id");
        const accountId = decodeURIComponent(id);
        const data = await apiClient.truelayer.getMyTransactions(accountId, userId);
        const groups = groupByMonth(data.transactions || []);
        setGrouped(groups);
        const months = Object.keys(groups);
        if (months.length > 0) setOpenMonth(months[0]);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTransactions();
  }, [id, isCard]);

  const months = Object.keys(grouped);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 pb-4">
        {/* Header */}
        <div className="flex items-center gap-3 pt-6 pb-2">
          <button
            onClick={() => navigate(backPath, { state: { account } })}
            className="btn-press w-10 h-10 rounded-full bg-muted flex items-center justify-center"
            aria-label="Go back"
          >
            <ArrowLeft size={20} className="text-foreground" />
          </button>
        </div>

        <div className="fade-in mt-2 mb-8">
          <p className="text-body text-muted-foreground">{account.name}</p>
          <h1 className="text-balance text-foreground">Transactions</h1>

          {account.balance != null && (
            <div className="mt-6">
              <p className="text-sm text-muted-foreground tracking-wide uppercase">Current balance</p>
              <p className="text-heading-lg text-foreground mt-1">
                {account.currency} {account.balance.toLocaleString("en", { minimumFractionDigits: 2 })}
              </p>
            </div>
          )}
        </div>

        {isLoading && (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Loading transactions...</p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-100 text-red-800 rounded-lg mb-4">{error}</div>
        )}

        {!isLoading && !error && months.length === 0 && (
          <p className="text-muted-foreground text-center py-8">No transactions found</p>
        )}

        {!isLoading && months.length > 0 && (
          <div className="slide-up">
            {months.map((month) => {
              const isOpen = openMonth === month;
              const txs = grouped[month];

              return (
                <div
                  key={month}
                  className={`${isOpen ? "bg-card rounded-2xl border border-border my-2 px-4" : "border-b border-border"}`}
                >
                  <button
                    onClick={() => setOpenMonth(isOpen ? null : month)}
                    className="btn-press w-full flex items-center justify-between py-4 min-h-[56px]"
                    aria-expanded={isOpen}
                    aria-label={`${month} transactions`}
                  >
                    <span className="text-body-lg font-semibold text-foreground">{month}</span>
                    {isOpen ? (
                      <ChevronUp size={22} className="text-foreground" />
                    ) : (
                      <ChevronDown size={22} className="text-foreground" />
                    )}
                  </button>

                  {isOpen && (
                    <div className="pb-4 space-y-3 fade-in">
                      {txs.map((tx, i) => (
                        <div key={tx.transaction_id || i} className="bg-muted rounded-xl p-4 flex items-center gap-4">
                          <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center text-sm font-semibold text-foreground flex-shrink-0">
                            {getInitials(tx.description)}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-body font-semibold text-foreground truncate">{tx.description}</p>
                            <p className="text-sm text-muted-foreground">
                              {new Date(tx.timestamp).toLocaleDateString("en", { day: "numeric", month: "long", year: "numeric" })}
                            </p>
                          </div>
                          <p className={`text-body font-semibold flex-shrink-0 ${tx.amount < 0 ? "text-destructive" : "text-primary"}`}>
                            {tx.amount < 0 ? "-" : "+"}
                            {tx.currency} {Math.abs(tx.amount).toFixed(2)}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Make Payment Button */}
        <button
          onClick={() => {
            speak("sendmoney");
            navigate("/send");
          }}
          className="btn-press w-full mt-6 mb-4 py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold min-h-[56px]"
          aria-label="Make Payment"
        >
          Make Payment
        </button>
      </div>

      <BottomNav />
    </div>
  );
};

export default Transactions;
