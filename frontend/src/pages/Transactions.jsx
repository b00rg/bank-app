import React, { useState, useEffect } from "react";
import { useNavigate, useParams, useLocation } from "react-router-dom";
import { ArrowLeft, ChevronDown, ChevronUp } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { apiClient } from "@/lib/api";
import { useSpeech } from "@/hooks/useSpeech";

const cardNames = {
  1: "Card 1",
  2: "Card 2",
};

const mockTransactionsByMonth = {
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

const Transactions = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const location = useLocation();
  const { speak } = useSpeech();
  const isCard = location.pathname.startsWith("/card/");
  const [accountData, setAccountData] = useState(null);
  const [transactionsByMonth, setTransactionsByMonth] = useState(mockTransactionsByMonth);
  const [months, setMonths] = useState(Object.keys(mockTransactionsByMonth));
  const [loading, setLoading] = useState(true);
  const [openMonth, setOpenMonth] = useState("November");

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);

        if (isCard) {
          // Card transactions - keep mock data for now
          setTransactionsByMonth(mockTransactionsByMonth);
          setMonths(Object.keys(mockTransactionsByMonth));
          setAccountData({
            name: cardNames[Number(id)] || `Card ${id}`,
            balance: 0,
          });
          return;
        }

        // Fetch account and transactions from TrueLayer
        const accountsRes = await apiClient.truelayer.getAccounts();
        const accounts = Array.isArray(accountsRes)
          ? accountsRes
          : accountsRes?.results || accountsRes?.accounts || [];

        const account = accounts.find((a) => a.id === id);

        if (!account) {
          setAccountData(null);
          setTransactionsByMonth(mockTransactionsByMonth);
          setMonths(Object.keys(mockTransactionsByMonth));
          setLoading(false);
          return;
        }

        setAccountData(account);

        // Fetch transactions
        const transactionsRes = await apiClient.truelayer.getAccountTransactions(id);
        const transactions = Array.isArray(transactionsRes)
          ? transactionsRes
          : transactionsRes?.results || transactionsRes?.transactions || [];

        // Group transactions by month
        const grouped = {};

        transactions.forEach((tx) => {
          try {
            const date = new Date(tx.timestamp || tx.date || tx.posting_date);
            if (isNaN(date.getTime())) return;

            const monthYear = date.toLocaleString("en-US", {
              month: "long",
              year: "numeric",
            });

            if (!grouped[monthYear]) {
              grouped[monthYear] = [];
            }

            // Extract initials from merchant name
            const merchantName = tx.merchant_name || tx.description || "Transaction";
            const initials = merchantName
              .split(" ")
              .map((w) => w[0])
              .join("")
              .toUpperCase()
              .slice(0, 2);

            grouped[monthYear].push({
              name: merchantName,
              date: date.toLocaleDateString("en-GB", {
                day: "numeric",
                month: "long",
                year: "numeric",
              }),
              amount: tx.amount || 0,
              initials: initials || "TX",
              timestamp: date,
            });
          } catch (e) {
            // Skip malformed transactions
          }
        });

        // Sort months by date descending
        const monthKeys = Object.keys(grouped).sort((a, b) => {
          const dateA = new Date(`${a} 1`);
          const dateB = new Date(`${b} 1`);
          return dateB - dateA;
        });

        // Sort transactions within each month by date descending
        monthKeys.forEach((month) => {
          grouped[month].sort((a, b) => b.timestamp - a.timestamp);
        });

        setTransactionsByMonth(grouped);
        setMonths(monthKeys);
        setOpenMonth(monthKeys[0] || "November");
      } catch (error) {
        console.error("Failed to fetch transactions:", error);
        setTransactionsByMonth(mockTransactionsByMonth);
        setMonths(Object.keys(mockTransactionsByMonth));
        setAccountData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [id, isCard]);

  const displayName = accountData?.name || (isCard ? `Card ${id}` : "Account");
  const displayBalance = accountData?.balance || 0;
  const currency = accountData?.currency || "€";
  const backPath = isCard ? "/cards" : `/account/${id}`;

  const toggleMonth = (month) => {
    setOpenMonth(openMonth === month ? null : month);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 pb-4">
        {/* Header */}
        <div className="flex items-center gap-3 pt-6 pb-2">
          <button
            onClick={() => navigate(backPath)}
            className="btn-press w-10 h-10 rounded-full bg-muted flex items-center justify-center"
            aria-label="Go back"
          >
            <ArrowLeft size={20} className="text-foreground" />
          </button>
        </div>

        <div className="fade-in mt-2 mb-8">
          <p className="text-body text-muted-foreground">{displayName}</p>
          <h1 className="text-balance text-foreground">Transactions</h1>

          <div className="mt-6">
            <p className="text-sm text-muted-foreground tracking-wide uppercase">Current balance</p>
            {loading ? (
              <p className="text-heading-lg text-foreground mt-1">Loading...</p>
            ) : (
              <p className="text-heading-lg text-foreground mt-1">
                {currency}
                {displayBalance.toLocaleString("en", { minimumFractionDigits: 2 })}
              </p>
            )}
          </div>
        </div>

        {/* Year Header - show most recent year */}
        {months.length > 0 && (
          <div className="bg-secondary text-secondary-foreground rounded-xl px-5 py-2.5 mb-1">
            <p className="text-body font-semibold text-center tracking-wide">
              {new Date(months[0]).getFullYear()}
            </p>
          </div>
        )}

        {/* Month Accordions */}
        <div className="slide-up">
          {months.map((month) => {
            const isOpen = openMonth === month;
            const transactions = transactionsByMonth[month];

            return (
              <div key={month} className={`${isOpen ? "bg-card rounded-2xl border border-border my-2 px-4" : "border-b border-border"}`}>
                <button
                  onClick={() => toggleMonth(month)}
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
                    {transactions.length === 0 ? (
                      <p className="text-sm text-muted-foreground py-2">No transactions</p>
                    ) : (
                      transactions.map((tx, i) => (
                        <div
                          key={i}
                          className="bg-muted rounded-xl p-4 flex items-center gap-4"
                        >
                          <div className="w-10 h-10 rounded-full bg-secondary/20 flex items-center justify-center text-sm font-semibold text-foreground">
                            {tx.initials}
                          </div>
                          <div className="flex-1">
                            <p className="text-body font-semibold text-foreground">{tx.name}</p>
                            <p className="text-sm text-muted-foreground">{tx.date}</p>
                          </div>
                          <p className={`text-body font-semibold ${tx.amount < 0 ? "text-destructive" : "text-primary"}`}>
                            {tx.amount < 0 ? "-" : "+"}€{Math.abs(tx.amount).toFixed(2)}
                          </p>
                        </div>
                      ))
                    )}
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
