import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, Check, Delete, ChevronDown, ChevronUp } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useVoice } from "@/context/VoiceContext";

const contacts = [
  { id: 1, name: "Sarah", relation: "Granddaughter", initials: "SA", color: "bg-primary/20 text-primary" },
  { id: 2, name: "James", relation: "Son", initials: "JA", color: "bg-secondary/20 text-secondary" },
  { id: 3, name: "Dr. Wilson", relation: "Doctor", initials: "DW", color: "bg-accent text-accent-foreground" },
  { id: 4, name: "Mrs. Chen", relation: "Neighbour", initials: "MC", color: "bg-muted text-muted-foreground" },
];

const SendMoney = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [selectedContact, setSelectedContact] = useState(null);
  const [amount, setAmount] = useState("");
  const [newAccountOpen, setNewAccountOpen] = useState(false);
  const [newAccount, setNewAccount] = useState({ name: "", sortCode: "", accountNumber: "" });
  const { speak } = useVoice();

  const handleDigit = (d) => {
    if (d === "." && amount.includes(".")) return;
    if (amount.includes(".") && amount.split(".")[1].length >= 2) return;
    if (amount.length >= 7) return;
    setAmount(amount + d);
  };

  const handleDeleteDigit = () => setAmount(amount.slice(0, -1));

  const recipientName = selectedContact?.name || newAccount.name;

  const handleContinue = () => {
    speak('continue');
    }

  const handleNewAccountContinue = () => {
    if (newAccount.name && newAccount.sortCode && newAccount.accountNumber) {
      setSelectedContact(null);
      setStep(2);
    }
  };

  const goBack = () => {
    if (step === 1) navigate("/dashboard");
    else setStep(step - 1);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center gap-3 px-5 pt-4 pb-3">
        <button
          onClick={goBack}
          className="btn-press w-10 h-10 rounded-full bg-muted flex items-center justify-center"
          aria-label="Go back"
        >
          <ArrowLeft size={20} className="text-foreground" />
        </button>
        <h1 className="text-heading-sm text-foreground">Send Money</h1>
      </div>

      {/* Progress */}
      <div className="flex gap-2 px-5 mb-4">
        {[1, 2, 3, 4].map((s) => (
          <div
            key={s}
            className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
              s <= step ? "bg-primary" : "bg-border"
            }`}
          />
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-5 pb-6">
        {/* Step 1: Choose Contact */}
        {step === 1 && (
          <div className="fade-in">
            <h2 className="text-heading text-foreground mb-2">
              Who are you sending money to?
            </h2>
            <p className="text-body text-muted-foreground mb-5">
              Choose someone from your contacts.
            </p>
            <div className="space-y-3">
              {contacts.map((contact) => (
                <button
                  key={contact.id}
                  onClick={() => {
                    speak(`contact${contact.id}`);
                    setSelectedContact(contact);
                    setNewAccountOpen(false);
                    setStep(2);
                  }}
                  className={`btn-press w-full flex items-center gap-4 p-4 rounded-2xl border-2 transition-colors ${
                    selectedContact?.id === contact.id
                      ? "border-primary bg-primary/5"
                      : "border-border bg-card hover:border-primary/30"
                  }`}
                  aria-label={`Send to ${contact.name}, ${contact.relation}`}
                >
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center font-semibold ${contact.color}`}>
                    {contact.initials}
                  </div>
                  <div className="text-left">
                    <p className="text-body font-semibold text-foreground">{contact.name}</p>
                    <p className="text-sm text-muted-foreground">{contact.relation}</p>
                  </div>
                </button>
              ))}
            </div>

            {/* Send to new account */}
            <div className="mt-6">
              <button
                onClick={() => {
                  speak("sendmoneytonewaccount");
                  setNewAccountOpen(!newAccountOpen);
                }}
                className={`btn-press w-full flex items-center justify-between p-4 border-2 transition-colors ${
                  newAccountOpen
                    ? "rounded-t-2xl border-b-0 border-border bg-card"
                    : "rounded-2xl border-border bg-card hover:border-primary/30"
                }`}
                aria-expanded={newAccountOpen}
              >
                <span className="text-body font-semibold text-foreground">Send to a new account</span>
                {newAccountOpen ? (
                  <ChevronUp size={20} className="text-muted-foreground" />
                ) : (
                  <ChevronDown size={20} className="text-muted-foreground" />
                )}
              </button>

              {newAccountOpen && (
                <div className="p-5 rounded-b-2xl border-2 border-t-0 border-border bg-card space-y-4 fade-in">
                  <div className="space-y-2">
                    <Label htmlFor="recipient-name" className="text-sm text-muted-foreground">Recipient Name</Label>
                    <Input
                      id="recipient-name"
                      placeholder="e.g. John Smith"
                      value={newAccount.name}
                      onChange={(e) => setNewAccount({ ...newAccount, name: e.target.value })}
                      className="rounded-xl min-h-[48px] text-base"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="sort-code" className="text-sm text-muted-foreground">Sort Code</Label>
                    <Input
                      id="sort-code"
                      placeholder="e.g. 12-34-56"
                      value={newAccount.sortCode}
                      onChange={(e) => setNewAccount({ ...newAccount, sortCode: e.target.value })}
                      className="rounded-xl min-h-[48px] text-base"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="account-number" className="text-sm text-muted-foreground">Account Number</Label>
                    <Input
                      id="account-number"
                      placeholder="e.g. 12345678"
                      value={newAccount.accountNumber}
                      onChange={(e) => setNewAccount({ ...newAccount, accountNumber: e.target.value })}
                      className="rounded-xl min-h-[48px] text-base"
                    />
                  </div>
                  <button
                    onClick={() => {
                      handleContinue();
                      handleNewAccountContinue();
                    }}
                    disabled={!newAccount.name || !newAccount.sortCode || !newAccount.accountNumber}
                    className="btn-press w-full py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold disabled:opacity-40 transition-opacity min-h-[56px]"
                  >
                    Continue
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Step 2: Amount */}
        {step === 2 && (
          <div className="fade-in flex flex-col items-center">
            <h2 className="text-heading text-foreground mb-1 text-center">
              How much?
            </h2>
            <p className="text-body text-muted-foreground mb-6 text-center">
              Sending to {recipientName}
            </p>

            <div className="text-balance text-foreground mb-8 min-h-[50px] text-center" aria-live="polite">
              £{amount || "0"}
            </div>

            <div className="grid grid-cols-3 gap-2 w-full max-w-[260px]">
              {["1","2","3","4","5","6","7","8","9",".","0",""].map((d, i) => (
                d === "" ? (
                  <button
                    key={i}
                    onClick={handleDeleteDigit}
                    className="btn-press aspect-square rounded-xl bg-card flex items-center justify-center border border-border min-h-[56px]"
                    aria-label="Delete"
                  >
                    <Delete size={20} className="text-muted-foreground" />
                  </button>
                ) : (
                  <button
                    key={i}
                    onClick={() => handleDigit(d)}
                    className="btn-press aspect-square rounded-xl bg-card text-foreground text-xl font-semibold flex items-center justify-center border border-border hover:bg-muted transition-colors min-h-[56px]"
                    aria-label={d === "." ? "Decimal point" : `Digit ${d}`}
                  >
                    {d}
                  </button>
                )
              ))}
            </div>

            <button
              onClick={() => {
                handleContinue();
                if (amount && parseFloat(amount) > 0) {
                  setStep(3);
                }
              }}
              disabled={!amount || parseFloat(amount) <= 0}
              className="btn-press w-full mt-6 py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold disabled:opacity-40 transition-opacity min-h-[56px]"
              aria-label="Continue to review"
            >
              Continue
            </button>
          </div>
        )}

        {/* Step 3: Review */}
        {step === 3 && (
          <div className="fade-in">
            <h2 className="text-heading text-foreground mb-2 text-center">
              Review your transfer
            </h2>
            <p className="text-body text-muted-foreground mb-6 text-center">
              Please check everything is correct.
            </p>

            <div className="bg-card rounded-2xl border-2 border-border p-6 space-y-4 mb-6">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Sending to</span>
                <span className="text-body font-semibold text-foreground">{recipientName}</span>
              </div>
              <div className="h-px bg-border" />
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Amount</span>
                <span className="text-heading text-primary font-semibold">£{parseFloat(amount).toFixed(2)}</span>
              </div>
              <div className="h-px bg-border" />
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">From</span>
                <span className="text-body font-semibold text-foreground">Current Account</span>
              </div>
            </div>

            <button
              onClick={() => {
                speak('moneysent');
                setStep(4);
              }}
              className="btn-press w-full py-4 rounded-2xl bg-primary text-primary-foreground text-body-lg font-semibold min-h-[56px]"
              aria-label="Confirm and send money"
            >
              Send £{parseFloat(amount).toFixed(2)}
            </button>
          </div>
        )}

        {/* Step 4: Success */}
        {step === 4 && (
          //handleContinue(),
          <div className="fade-in flex flex-col items-center justify-center pt-8">
            <div className="w-20 h-20 rounded-full bg-primary flex items-center justify-center mb-6 bounce-check">
              <Check size={40} className="text-primary-foreground" strokeWidth={3} />
            </div>
            <h2 className="text-heading-lg text-foreground mb-2 text-center">
              Money Sent!
            </h2>
            <p className="text-body text-muted-foreground text-center mb-2">
              £{parseFloat(amount).toFixed(2)} has been sent to {recipientName}.
            </p>
            <p className="text-sm text-muted-foreground text-center mb-8">
              It should arrive within a few minutes.
            </p>

            <button
              onClick={() => {
                speak("dashboard");
                navigate("/dashboard");
              }}
              className="btn-press w-full py-4 rounded-2xl bg-secondary text-secondary-foreground text-body-lg font-semibold min-h-[56px]"
              aria-label="Go back to home"
            >
              Back to Home
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SendMoney;
