import React from "react";
import { useNavigate } from "react-router-dom";
import { ArrowUpLeft } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { useVoice } from "@/context/VoiceContext";

const accounts = [
  { id: 1, name: "Account 1", type: "Personal Account", sortCode: "08-09-10", accountNumber: "4239489238", balance: 1239.05 },
  { id: 2, name: "Account 2", type: "Personal Account", sortCode: "08-09-10", accountNumber: "4239489238", balance: 1239.05 },
  { id: 3, name: "Account 3", type: "Personal Account", sortCode: "08-09-10", accountNumber: "4239489238", balance: 1239.05 },
];

const Dashboard = () => {
  const navigate = useNavigate();
  const { speak } = useVoice();

const handleAccountClick = (account) => {
  speak(`account${account.id}`);
  navigate(`/account/${account.id}`);
};

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 pb-4">
        {/* Header - match Figma: Welcome back, Alma. */}
        <div className="pt-6 pb-2 fade-in">
          <p className="text-sm text-muted-foreground">Welcome back,</p>
          <h1 className="text-balance text-foreground">Alma.</h1>
        </div>

        <p className="text-body text-muted-foreground mb-6 slide-up">
          Click an account to make a transaction and view details.
        </p>

        {/* Account Cards - white, rounded, subtle shadow */}
        <div className="space-y-4 slide-up">
          {accounts.map((account) => (
            <button
              key={account.id}
              onClick={() => handleAccountClick(account)}
              className="btn-press w-full text-left bg-card rounded-[20px] p-6 card-shadow border-0 hover:shadow-[0_4px_16px_rgba(79,55,47,0.12)] transition-shadow"
              aria-label={`${account.name}, balance €${account.balance.toFixed(2)}`}
            >
              <div className="flex items-center gap-2 mb-1">
                <ArrowUpLeft size={18} className="text-foreground shrink-0" />
                <span className="text-heading-sm text-foreground">{account.name}</span>
              </div>
              <p className="text-sm text-muted-foreground mb-4">{account.type}</p>

              <div className="space-y-4">
                <div className="space-y-0.5">
                  <p className="text-sm text-muted-foreground">Sort Code</p>
                  <p className="text-body font-semibold text-foreground">{account.sortCode}</p>
                </div>
                <div className="space-y-0.5">
                  <p className="text-sm text-muted-foreground">Account Number</p>
                  <p className="text-body font-semibold text-foreground">{account.accountNumber}</p>
                </div>
                <div className="space-y-0.5">
                  <p className="text-sm text-muted-foreground">Balance</p>
                  <p className="text-body font-semibold text-foreground">€{account.balance.toFixed(2)}</p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default Dashboard;
