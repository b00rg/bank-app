import React from "react";

const PhoneFrame = ({ children }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-muted p-4">
      <div
        className="phone-frame relative w-[400px] h-[780px] bg-background rounded-[2.5rem] border-2 border-border overflow-hidden flex flex-col"
        role="application"
        aria-label="Banking App"
      >
        {/* Status bar */}
        <div className="flex items-center justify-between px-6 pt-3 pb-1">
          <span className="text-sm font-semibold text-foreground">9:41</span>
          <div className="flex gap-1.5 items-center">
            <div className="w-4 h-3 rounded-sm bg-foreground opacity-50" />
            <div className="w-4 h-3 rounded-sm bg-foreground opacity-50" />
            <div className="w-6 h-3 rounded-md bg-foreground opacity-60" />
          </div>
        </div>
        {/* App content */}
        <div className="flex-1 overflow-y-auto overflow-x-hidden">
          {children}
        </div>
      </div>
    </div>
  );
};

export default PhoneFrame;
