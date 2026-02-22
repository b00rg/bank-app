import React from "react";
import { Phone, MessageCircle, FileText } from "lucide-react";
import BottomNav from "@/components/BottomNav";

const supportOptions = [
  {
    icon: Phone,
    title: "Call Us",
    description: "Speak to a real person. We're here 24/7.",
    action: "0800 123 4567",
  },
  {
    icon: MessageCircle,
    title: "Send a Message",
    description: "We'll reply within 1 hour.",
    action: "Start a chat",
  },
  {
    icon: FileText,
    title: "Common Questions",
    description: "Find answers to common queries.",
    action: "Browse FAQs",
  },
];

const SupportScreen = () => {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-6 pb-4">
        <div className="pt-6 pb-2 fade-in">
          <p className="text-body text-muted-foreground">Need help?</p>
          <h1 className="text-balance text-foreground">Support.</h1>
          <p className="text-body text-muted-foreground mt-2">
            We're always here for you.
          </p>
        </div>

        <div className="space-y-4 mt-4 slide-up">
          {supportOptions.map((option, i) => {
            const Icon = option.icon;
            return (
              <button
                key={i}
                className="btn-press w-full text-left flex items-start gap-4 bg-card rounded-2xl p-5 border border-border hover:border-foreground/20 transition-colors"
                aria-label={option.title}
              >
                <div className="w-12 h-12 rounded-xl bg-muted flex items-center justify-center shrink-0">
                  <Icon size={22} className="text-foreground" />
                </div>
                <div>
                  <p className="text-body font-semibold text-foreground">{option.title}</p>
                  <p className="text-sm text-muted-foreground mt-0.5">{option.description}</p>
                  <p className="text-sm font-semibold text-primary mt-2">{option.action}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>
      <BottomNav />
    </div>
  );
};

export default SupportScreen;
