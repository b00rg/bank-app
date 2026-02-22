import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ArrowLeft, Send, List } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { useVoice } from "@/context/VoiceContext";


const accounts = [
  { id: 1, name: "Account 1" },
  { id: 2, name: "Account 2" },
  { id: 3, name: "Account 3" },
];

const AccountDetail = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const account = accounts.find((a) => a.id === Number(id)) || accounts[0];
  const { speak } = useVoice();
  

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 flex flex-col px-6">
        {/* Back button */}
        <div className="flex items-center gap-3 pt-6 pb-2">
          <button
            onClick={() => navigate("/dashboard")}
            className="btn-press w-10 h-10 rounded-full bg-muted flex items-center justify-center"
            aria-label="Go back"
          >
            <ArrowLeft size={20} className="text-foreground" />
          </button>
        </div>

        {/* Centered content */}
        <div className="flex-1 flex flex-col items-center justify-center fade-in">
          <h1 className="text-heading-lg text-foreground mb-10 text-center">{account.name}</h1>

          <div className="space-y-4 w-full">
            <button
              onClick={() => {
                speak(`sendaccount${account.id}`);
                navigate("/send");
              }}
              className="btn-press w-full flex items-center justify-center gap-3 p-5 rounded-2xl bg-primary text-primary-foreground min-h-[64px]"
              aria-label="Send Money"
            >
              <Send size={24} />
              <span className="text-body-lg font-semibold">Send Money</span>
            </button>

            <button
              onClick={() => {
                speak(`account${account.id}Trans`);
                navigate(`/account/${account.id}/transactions`);
              }}
              className="btn-press w-full flex items-center justify-center gap-3 p-5 rounded-2xl bg-card border border-border text-foreground hover:bg-muted transition-colors min-h-[64px]"
              aria-label="See Transactions"
            >
              <List size={24} />
              <span className="text-body-lg font-semibold">See Transactions</span>
            </button>
          </div>
        </div>
      </div>

      <BottomNav />
    </div>
  );
};

export default AccountDetail;
