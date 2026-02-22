import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { LogOut, CreditCard, History, Pause, Play } from "lucide-react";
import BottomNav from "@/components/BottomNav";
import { apiClient } from "@/lib/api";

const OverseerDashboard = () => {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userCards, setUserCards] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [showCreateCardModal, setShowCreateCardModal] = useState(false);
  const [spendingLimit, setSpendingLimit] = useState("100");
  const [expirationMonths, setExpirationMonths] = useState("12");
  const [billingAddress, setBillingAddress] = useState("");
  const [billingCity, setBillingCity] = useState("");
  const [billingPostal, setBillingPostal] = useState("");
  const [blockedCategories, setBlockedCategories] = useState([]);
  const [activeTab, setActiveTab] = useState("users"); // 'users' or 'cards'

  const categoryOptions = [
    "Alcohol & Tobacco",
    "Gambling",
    "Adult Entertainment",
    "Fast Food",
    "Subscriptions",
  ];

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      const data = await apiClient.overseer.getUsers();
      setUsers(data.users || []);
      if (data.users && data.users.length > 0) {
        setSelectedUser(data.users[0]);
      }
    } catch (err) {
      setError(err.message);
      console.error("Failed to fetch users:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCard = async () => {
    if (!selectedUser) return;
    
    try {
      setIsLoading(true);
      const newCard = await apiClient.cards.createVirtualCard(
        parseFloat(spendingLimit),
        parseInt(expirationMonths),
        billingAddress,
        billingCity,
        billingPostal,
        blockedCategories
      );
      setUserCards([...userCards, {
        id: newCard.card_id,
        type: "Virtual Card",
        number: `****${newCard.last4}`,
        status: newCard.status,
        active: newCard.status === "active",
        balance: "€0.00",
        spendingLimit: `€${spendingLimit}`,
      }]);
      setShowCreateCardModal(false);
      setSpendingLimit("100");
      setExpirationMonths("12");
      setBillingAddress("");
      setBillingCity("");
      setBillingPostal("");
      setBlockedCategories([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleBlockedCategory = (category) => {
    if (blockedCategories.includes(category)) {
      setBlockedCategories(blockedCategories.filter((c) => c !== category));
    } else {
      setBlockedCategories([...blockedCategories, category]);
    }
  };

  const handleFreezeCard = async (cardId) => {
    try {
      await apiClient.cards.freezeCard(cardId);
      setUserCards(
        userCards.map((card) =>
          card.id === cardId ? { ...card, active: false } : card
        )
      );
    } catch (err) {
      setError(err.message);
    }
  };

  const handleUnfreezeCard = async (cardId) => {
    try {
      await apiClient.cards.unfreezeCard(cardId);
      setUserCards(
        userCards.map((card) =>
          card.id === cardId ? { ...card, active: true } : card
        )
      );
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLogout = async () => {
    try {
      await apiClient.auth.logout();
      navigate("/");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="bg-primary text-primary-foreground px-6 py-4 flex items-center justify-between">
        <div>
          <p className="text-sm opacity-90">Overseer Portal</p>
          <h1 className="text-heading-sm">Account Manager</h1>
        </div>
        <button
          onClick={handleLogout}
          className="p-2 rounded-lg bg-primary-foreground/20 hover:bg-primary-foreground/30 transition"
        >
          <LogOut size={20} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-4">
        {error && (
          <div className="p-4 bg-red-100 text-red-800 rounded-lg mb-4">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Loading...</p>
          </div>
        ) : (
          <>
            {/* Users Section */}
            <div className="mb-6">
              <h2 className="text-heading-sm text-foreground mb-3">Your Users</h2>
              <div className="space-y-2">
                {users.map((user, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setSelectedUser(user);
                      setActiveTab("cards");
                    }}
                    className={`w-full text-left p-4 rounded-xl border-2 transition ${
                      selectedUser?.email === user.email
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-card border-border hover:border-primary/50"
                    }`}
                  >
                    <p className="font-semibold">{user.name}</p>
                    <p className="text-sm opacity-70">{user.email}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Selected User Details */}
            {selectedUser && (
              <div className="space-y-4">
                <h3 className="text-heading-sm text-foreground">
                  {selectedUser.name}'s Cards
                </h3>

                {/* Create Card Button */}
                <button
                  onClick={() => setShowCreateCardModal(true)}
                  disabled={isLoading}
                  className="w-full py-3 rounded-xl bg-primary text-primary-foreground font-semibold hover:bg-primary/90 disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  <CreditCard size={18} />
                  Create Virtual Card
                </button>

                {/* Cards List */}
                {userCards.length === 0 ? (
                  <div className="text-center py-8 border-2 border-dashed border-primary/40 rounded-xl bg-primary/5">
                    <CreditCard size={32} className="mx-auto text-primary mb-2" />
                    <p className="text-muted-foreground">No cards created yet</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {userCards.map((card) => (
                      <div
                        key={card.id}
                        className="p-4 rounded-xl bg-card border-2 border-border"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <p className="font-semibold">Virtual Card</p>
                          <span className={`text-xs font-semibold px-2 py-1 rounded ${
                            card.active
                              ? "bg-green-100 text-green-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}>
                            {card.active ? "Active" : "Frozen"}
                          </span>
                        </div>
                        <p className="text-xl font-mono font-semibold tracking-widest mb-2">
                          {card.number}
                        </p>
                        <p className="text-sm text-muted-foreground mb-4">Balance: {card.balance}</p>
                        
                        {/* Freeze/Unfreeze Button */}
                        <button
                          onClick={() => card.active ? handleFreezeCard(card.id) : handleUnfreezeCard(card.id)}
                          className={`w-full py-2 rounded-lg font-semibold flex items-center justify-center gap-2 transition ${
                            card.active
                              ? "bg-yellow-100 text-yellow-900 hover:bg-yellow-200"
                              : "bg-green-100 text-green-900 hover:bg-green-200"
                          }`}
                        >
                          {card.active ? (
                            <>
                              <Pause size={16} />
                              Freeze Card
                            </>
                          ) : (
                            <>
                              <Play size={16} />
                              Unfreeze Card
                            </>
                          )}
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Transaction History */}
                <div className="mt-6 pt-6 border-t border-border">
                  <h4 className="text-heading-sm text-foreground mb-3 flex items-center gap-2">
                    <History size={20} />
                    Transaction History
                  </h4>
                  <div className="p-4 rounded-xl bg-card border-2 border-border text-center text-muted-foreground">
                    <p className="text-sm">No transactions yet</p>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <BottomNav />

      {/* Create Card Modal */}
      {showCreateCardModal && (
        <div className="fixed inset-0 bg-black/50 flex items-end z-50">
          <div className="w-full bg-card rounded-t-2xl p-6 animate-in slide-in-from-bottom max-h-[90vh] overflow-y-auto">
            <h3 className="text-heading-sm text-foreground mb-4">Create Virtual Card</h3>
            
            <div className="space-y-4">
              {/* Spending Limit */}
              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Weekly Spending Limit (€)
                </label>
                <input
                  type="number"
                  value={spendingLimit}
                  onChange={(e) => setSpendingLimit(e.target.value)}
                  placeholder="100"
                  min="0"
                  step="10"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              {/* Expiration */}
              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Card Expiration (Months)
                </label>
                <input
                  type="number"
                  value={expirationMonths}
                  onChange={(e) => setExpirationMonths(e.target.value)}
                  placeholder="12"
                  min="1"
                  max="60"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              {/* Billing Address */}
              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Billing Address
                </label>
                <input
                  type="text"
                  value={billingAddress}
                  onChange={(e) => setBillingAddress(e.target.value)}
                  placeholder="123 Main Street"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              {/* Billing City */}
              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  City
                </label>
                <input
                  type="text"
                  value={billingCity}
                  onChange={(e) => setBillingCity(e.target.value)}
                  placeholder="Dublin"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              {/* Billing Postal Code */}
              <div>
                <label className="text-sm font-semibold text-foreground block mb-1.5">
                  Postal Code
                </label>
                <input
                  type="text"
                  value={billingPostal}
                  onChange={(e) => setBillingPostal(e.target.value)}
                  placeholder="D01 1AA"
                  className="w-full px-4 py-3 rounded-xl border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary min-h-[48px]"
                />
              </div>

              {/* Blocked Categories */}
              <div>
                <label className="text-sm font-semibold text-foreground block mb-2">
                  Block Categories
                </label>
                <div className="space-y-2">
                  {categoryOptions.map((category) => (
                    <button
                      key={category}
                      onClick={() => toggleBlockedCategory(category)}
                      className={`w-full text-left px-4 py-3 rounded-xl border-2 transition ${
                        blockedCategories.includes(category)
                          ? "bg-primary/20 border-primary text-foreground"
                          : "bg-card border-border hover:border-primary/50"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                          blockedCategories.includes(category)
                            ? "bg-primary border-primary"
                            : "border-border"
                        }`}>
                          {blockedCategories.includes(category) && (
                            <span className="text-primary-foreground text-sm">✓</span>
                          )}
                        </div>
                        <span className="font-medium">{category}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => {
                    setShowCreateCardModal(false);
                    setSpendingLimit("100");
                    setExpirationMonths("12");
                    setBillingAddress("");
                    setBillingCity("");
                    setBillingPostal("");
                    setBlockedCategories([]);
                  }}
                  className="flex-1 py-3 rounded-xl border-2 border-border text-foreground font-semibold hover:bg-primary/10"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCreateCard}
                  disabled={isLoading}
                  className="flex-1 py-3 rounded-xl bg-primary text-primary-foreground font-semibold hover:bg-primary/90 disabled:opacity-50"
                >
                  {isLoading ? "Creating..." : "Create Card"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OverseerDashboard;
