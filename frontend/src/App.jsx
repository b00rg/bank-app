import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { VoiceProvider } from "@/context/VoiceContext";
import PhoneFrame from "./components/PhoneFrame";
import AuthScreen from "./pages/AuthScreen";
import LoginScreen from "./pages/LoginScreen";
import Dashboard from "./pages/Dashboard";
import AccountDetail from "./pages/AccountDetail";
import Transactions from "./pages/Transactions";
import SendMoney from "./pages/SendMoney";
import CardsScreen from "./pages/CardsScreen";
import SupportScreen from "./pages/SupportScreen";
import NotFound from "./pages/NotFound";
import OverseerLogin from "./pages/OverseerLogin";
import OverseerDashboard from "./pages/OverseerDashboard";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <VoiceProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <PhoneFrame>
            <Routes>
              <Route path="/" element={<AuthScreen />} />
              <Route path="/overseer" element={<OverseerLogin />} />
              <Route path="/overseer/dashboard" element={<OverseerDashboard />} />
              <Route path="/pin" element={<LoginScreen />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/account/:id" element={<AccountDetail />} />
              <Route path="/account/:id/transactions" element={<Transactions />} />
              <Route path="/card/:id/transactions" element={<Transactions />} />
              <Route path="/send" element={<SendMoney />} />
              <Route path="/cards" element={<CardsScreen />} />
              <Route path="/support" element={<SupportScreen />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </PhoneFrame>
        </BrowserRouter>
      </VoiceProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
