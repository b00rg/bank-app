import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowUpLeft } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { useVoice } from "@/context/VoiceContext";
import { apiClient } from "@/lib/api";

const Dashboard = () => {
  const navigate = useNavigate();
  const { speak } = useVoice();
  const [accounts, setAccounts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchAccounts();
  }, []);

  const fetchAccounts = async () => {
    try {
      setIsLoading(true);
      const userId = localStorage.getItem("user_id");
      if (!userId) {
        setError("No user session found. Please log in.");
        return;
      }
      const data = await apiClient.truelayer.getMyAccounts(userId);
      setAccounts(data.accounts || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAccountClick = (account) => {
    speak(`account${account.account_id}`);
    navigate(`/account/${encodeURIComponent(account.account_id)}`, { state: { account } });
  };

  const formatSortCode = (sc) => {
    if (!sc) return null;
    return sc.replace(/(\d{2})(\d{2})(\d{2})/, "$1-$2-$3");
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 pb-4">
        <div className="pt-6 pb-2 fade-in">
          <p className="text-sm text-muted-foreground">Welcome back,</p>
          <h1 className="text-balance text-foreground">Alma.</h1>
        </div>

        <p className="text-body text-muted-foreground mb-6 slide-up">
          Click an account to make a transaction and view details.
        </p>

        {error && (
          <div className="p-4 bg-red-100 text-red-800 rounded-lg mb-4">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Loading accounts...</p>
          </div>
        ) : accounts.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">No accounts found</p>
          </div>
        ) : (
          <div className="space-y-4 slide-up">
            {accounts.map((account) => (
              <button
                key={account.account_id}
                onClick={() => handleAccountClick(account)}
                className="btn-press w-full text-left bg-card rounded-[20px] p-6 card-shadow border-2 border-foreground/40 hover:shadow-[0_8px_32px_rgba(79,55,47,0.18)] transition-all duration-200"
                aria-label={`${account.name}, balance ${account.currency} ${account.balance?.toFixed(2)}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <ArrowUpLeft size={25} className="text-foreground shrink-0" />
                  <span className="text-heading-sm text-foreground">{account.name}</span>
                </div>
                <p className="text-sm text-muted-foreground mb-4">{account.type}</p>

                <div className="space-y-4">
                  {formatSortCode(account.sort_code) && (
                    <div className="space-y-0.5">
                      <p className="text-sm text-muted-foreground">Sort Code</p>
                      <p className="text-body font-semibold text-foreground">{formatSortCode(account.sort_code)}</p>
                    </div>
                  )}
                  {account.account_number && (
                    <div className="space-y-0.5">
                      <p className="text-sm text-muted-foreground">Account Number</p>
                      <p className="text-body font-semibold text-foreground">{account.account_number}</p>
                    </div>
                  )}
                  {account.iban && !account.account_number && (
                    <div className="space-y-0.5">
                      <p className="text-sm text-muted-foreground">IBAN</p>
                      <p className="text-body font-semibold text-foreground">{account.iban}</p>
                    </div>
                  )}
                  <div className="space-y-0.5">
                    <p className="text-sm text-muted-foreground">Balance</p>
                    <p className="text-body font-semibold text-foreground">
                      {account.currency} {account.balance?.toFixed(2) ?? "—"}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      <BottomNav />
    </div>
  );
};

export default Dashboard;
