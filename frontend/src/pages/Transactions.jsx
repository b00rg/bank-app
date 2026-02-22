import React, { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { ArrowLeft, ChevronDown, ChevronUp } from "lucide-react";
import BottomNav from "@/components/BottomNav";

const accounts = [
  { id: 1, name: "Account 1", balance: 2156.0 },
  { id: 2, name: "Account 2", balance: 1239.05 },
  { id: 3, name: "Account 3", balance: 1239.05 },
];

const cardNames = {
  1: "Card 1",
  2: "Card 2",
};

const transactionsByMonth = {
  December: [],
  November: [
    { name: "Shell London", date: "5 December 2020", amount: -30.0, initials: "SL" },
    { name: "Tesco Express", date: "5 December 2020", amount: -12.34, initials: "TE" },
  ],
  October: [
    { name: "Amazon UK", date: "15 October 2020", amount: -45.99, initials: "AM" },
    { name: "Salary", date: "1 October 2020", amount: 2500.0, initials: "SA" },
  ],
  September: [
    { name: "Netflix", date: "10 September 2020", amount: -9.99, initials: "NF" },
  ],
  August: [
    { name: "Waitrose", date: "20 August 2020", amount: -67.42, initials: "WR" },
  ],
  July: [
    { name: "British Gas", date: "5 July 2020", amount: -120.0, initials: "BG" },
  ],
};

const months = Object.keys(transactionsByMonth);

const Transactions = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const isCard = location.pathname.startsWith("/card/");
  const account = accounts.find((a) => a.id === Number(id)) || accounts[0];
  const displayName = isCard ? (cardNames[Number(id)] || `Card ${id}`) : account.name;
  const backPath = isCard ? "/cards" : `/account/${id}`;
  const [openMonth, setOpenMonth] = useState("November");

  const toggleMonth = (month) => {
    setOpenMonth(openMonth === month ? null : month);
  };

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

          <div className="mt-6">
            <p className="text-sm text-muted-foreground tracking-wide uppercase">Current balance</p>
            <p className="text-heading-lg text-foreground mt-1">
              €{account.balance.toLocaleString("en", { minimumFractionDigits: 2 })}
            </p>
          </div>
        </div>

        {/* Year Header */}
        <div className="bg-secondary text-secondary-foreground rounded-xl px-5 py-2.5 mb-1">
          <p className="text-body font-semibold text-center tracking-wide">2026</p>
        </div>

        {/* Month Accordions */}
        <div className="slide-up">
          {months.map((month) => {
            const isOpen = openMonth === month;
            const transactions = transactionsByMonth[month];

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
