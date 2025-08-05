"use client";
import React, { useState } from "react";
import { auth } from "./firebase";
import { User } from "firebase/auth";

interface TripPackage {
  flight: {
    airline: string;
    depart_time: string;
    arrive_time: string;
    cost: number;
    booking_url: string;
  };
  hotel: {
    name: string;
    cost: number;
    distance_from_poi_km: number;
    booking_url: string;
  };
  total_score: number;
  total_cost: number;
  duration: number;
  start_date: string;
  end_date: string;
  loyalty_analysis?: {
    cash_price: number;
    hotel_loyalty_options: Array<{
      program: string;
      program_code: string;
      points_needed: number;
      points_available: number;
      recommendation: string;
      savings: number;
      effective_value: number;
    }>;
    best_recommendation?: {
      program: string;
      program_code: string;
      points_needed: number;
      recommendation: string;
      savings: number;
    };
    user_balances: Record<string, number>;
  };
}

interface PlanTripResponse {
  packages: TripPackage[];
  user_input: any;
  generated_at: string;
  session_id: string;
}

export default function Home() {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<PlanTripResponse | null>(null);
  const [error, setError] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showLoyaltyModal, setShowLoyaltyModal] = useState(false);
  
  // Priority toggles
  const [priorities, setPriorities] = useState({
    prioritize_flight_time: false,
    prioritize_hotel_quality: false,
    prioritize_cost: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResults(null);
    
    // Send natural language input for parsing
    const mockRequest = {
      user_input: input, // Send the raw user input for backend parsing
    };
    try {
      let idToken = undefined;
      const user: User | null = auth.currentUser;
      if (user) {
        idToken = await user.getIdToken();
      } else {
        setError("请先登录后再提交请求！");
        setLoading(false);
        return;
      }
      const res = await fetch("http://localhost:8000/api/plan-trip", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify(mockRequest),
      });
      if (!res.ok) {
        if (res.status === 401) {
          setError("未授权，请重新登录后再试。");
        } else {
          setError("Backend error");
        }
        setLoading(false);
        return;
      }
      const data = await res.json();
      setResults(data);
      setSessionId(data.session_id);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(amount);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) {
      return "bg-gradient-to-r from-emerald-400 to-green-500"; // Excellent - Green
    } else if (score >= 70) {
      return "bg-gradient-to-r from-amber-400 to-orange-500"; // Good - Amber/Orange
    } else {
      return "bg-gradient-to-r from-red-400 to-pink-500"; // Fair - Red/Pink
    }
  };

  const handleRegenerate = async () => {
    if (!sessionId) return;
    
    setLoading(true);
    setError("");
    
    try {
      let idToken = undefined;
      const user: User | null = auth.currentUser;
      if (user) {
        idToken = await user.getIdToken();
      }
      
      const res = await fetch("http://localhost:8000/api/regenerate-trip", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: idToken ? `Bearer ${idToken}` : "",
        },
        body: JSON.stringify({ session_id: sessionId }),
      });
      
      if (!res.ok) {
        setError("Failed to regenerate options");
        setLoading(false);
        return;
      }
      
      const data = await res.json();
      setResults(data);
    } catch (err: any) {
      setError(err.message || "Failed to regenerate");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex flex-col items-center py-8 px-4">
      <div className="w-full max-w-5xl">
        {/* Main Card */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8 text-gray-900">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              Smart Holiday Booking Assistant
            </h1>
            <p className="text-gray-600 text-lg">Plan your perfect trip with AI-powered recommendations</p>
          </div>

          {/* Chat Interface */}
          <div className="mb-8">
            <div className="flex items-end space-x-3 mb-6">
              <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white px-6 py-4 rounded-2xl rounded-bl-md max-w-[85%] shadow-lg">
                <p className="text-lg leading-relaxed">
                  I want to visit London for 3–5 days in August with 2 kids and go to the National Gallery.
                </p>
              </div>
              <div className="w-3 h-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"></div>
            </div>
          </div>

          {/* Input Form */}
          <form onSubmit={handleSubmit} className="flex gap-3 mb-6">
            <input
              className="flex-1 border-2 border-gray-200 rounded-2xl px-6 py-4 focus:outline-none focus:ring-4 focus:ring-blue-200 focus:border-blue-400 text-gray-900 bg-white/90 backdrop-blur-sm placeholder-gray-500 text-lg transition-all duration-300 shadow-lg"
              type="text"
              placeholder="Describe your dream vacation... (e.g., 'I want to visit Tokyo from London for 5 days in August with 2 kids')"
              value={input}
              onChange={e => setInput(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-4 rounded-2xl font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 text-lg"
              disabled={loading || !input.trim()}
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent"></div>
                  <span>Planning...</span>
                </div>
              ) : (
                "Plan Trip"
              )}
            </button>
          </form>

          {/* Priority Settings */}
          <div className="mb-6 p-6 bg-gradient-to-r from-gray-50 to-blue-50 rounded-2xl border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">🎯 Trip Priorities</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={priorities.prioritize_flight_time}
                  onChange={(e) => setPriorities(prev => ({
                    ...prev,
                    prioritize_flight_time: e.target.checked,
                    prioritize_hotel_quality: e.target.checked ? false : prev.prioritize_hotel_quality,
                    prioritize_cost: e.target.checked ? false : prev.prioritize_cost,
                  }))}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700">✈️ Prioritize Flight Time</span>
              </label>
              
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={priorities.prioritize_hotel_quality}
                  onChange={(e) => setPriorities(prev => ({
                    ...prev,
                    prioritize_hotel_quality: e.target.checked,
                    prioritize_flight_time: e.target.checked ? false : prev.prioritize_flight_time,
                    prioritize_cost: e.target.checked ? false : prev.prioritize_cost,
                  }))}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700">🏨 Prioritize Hotel Quality</span>
              </label>
              
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={priorities.prioritize_cost}
                  onChange={(e) => setPriorities(prev => ({
                    ...prev,
                    prioritize_cost: e.target.checked,
                    prioritize_flight_time: e.target.checked ? false : prev.prioritize_flight_time,
                    prioritize_hotel_quality: e.target.checked ? false : prev.prioritize_hotel_quality,
                  }))}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-gray-700">💰 Prioritize Cost</span>
              </label>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-lg">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Results */}
          {results && (
            <div className="mt-8">
              <div className="mb-6 text-center">
                <h2 className="text-2xl font-bold text-gray-800 mb-2">✨ Your Perfect Trip Options</h2>
                <p className="text-gray-600 mb-4">
                  Generated at {new Date(results.generated_at).toLocaleString()}
                </p>
                <button
                  onClick={handleRegenerate}
                  disabled={loading}
                  className="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-6 py-3 rounded-xl font-semibold hover:from-cyan-600 hover:to-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                      <span>Regenerating...</span>
                    </div>
                  ) : (
                    <div className="flex items-center space-x-2">
                      <span>🌀</span>
                      <span>Regenerate Options</span>
                    </div>
                  )}
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-h-[600px] overflow-y-auto pr-2">
                {results.packages.map((pkg, idx) => (
                  <div 
                    key={idx} 
                    className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:scale-105 border border-gray-100 overflow-hidden"
                  >
                    {/* Card Header */}
                    <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-6 text-white relative overflow-hidden">
                      <div className="absolute top-0 right-0 w-20 h-20 bg-white/10 rounded-full -mr-10 -mt-10"></div>
                      <div className="absolute bottom-0 left-0 w-16 h-16 bg-white/10 rounded-full -ml-8 -mb-8"></div>
                      
                      <div className="flex justify-between items-start relative z-10">
                        <div>
                          <span className="font-bold text-2xl">Option {idx + 1}</span>
                          <div className="text-blue-100 mt-1">
                            {formatDate(pkg.start_date)} - {formatDate(pkg.end_date)}
                          </div>
                          <div className="text-blue-100 text-sm">
                            {pkg.duration} days
                          </div>
                        </div>
                        <div className="text-right flex flex-col items-end">
                          <div className={`${getScoreColor(pkg.total_score)} text-white px-3 py-1 rounded-full text-sm font-semibold whitespace-nowrap shadow-lg`}>
                            Score: {pkg.total_score}
                          </div>
                          <div className="text-2xl font-bold mt-2">
                            {formatCurrency(pkg.total_cost)}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Flight Details */}
                    <div className="p-6 border-b border-gray-100">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                            <span className="text-blue-600 text-lg">✈️</span>
                          </div>
                          <span className="font-semibold text-gray-800">Flight</span>
                        </div>
                        <span className="text-lg font-bold text-blue-600">
                          {formatCurrency(pkg.flight.cost)}
                        </span>
                      </div>
                      <div className="space-y-1">
                        <div className="font-medium text-gray-900">{pkg.flight.airline}</div>
                        <div className="text-gray-600 flex items-center space-x-2">
                          <span>{pkg.flight.depart_time}</span>
                          <span className="text-blue-500">→</span>
                          <span>{pkg.flight.arrive_time}</span>
                        </div>
                        <div className="mt-2">
                          <a 
                            href={pkg.flight.booking_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors"
                          >
                            <span>🔗</span>
                            <span>Book Flight</span>
                            <span className="text-xs">↗</span>
                          </a>
                        </div>
                      </div>
                    </div>

                    {/* Hotel Details */}
                    <div className="p-6">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                            <span className="text-green-600 text-lg">🏨</span>
                          </div>
                          <span className="font-semibold text-gray-800">Hotel</span>
                        </div>
                        <span className="text-lg font-bold text-green-600">
                          {formatCurrency(pkg.hotel.cost)}/night
                        </span>
                      </div>
                      <div className="space-y-1">
                        <div className="font-medium text-gray-900">{pkg.hotel.name}</div>
                        <div className="text-gray-600 flex items-center space-x-2">
                          <span>📍</span>
                          <span>{pkg.hotel.distance_from_poi_km} km from POI</span>
                        </div>
                        <div className="mt-2">
                          <a 
                            href={pkg.hotel.booking_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center space-x-1 text-green-600 hover:text-green-800 text-sm font-medium transition-colors"
                          >
                            <span>🔗</span>
                            <span>Book Hotel</span>
                            <span className="text-xs">↗</span>
                          </a>
                        </div>
                      </div>
                    </div>

                    {/* Loyalty Comparison */}
                    <div className="p-6 border-t border-gray-100 bg-gradient-to-r from-amber-50 to-orange-50">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
                            <span className="text-amber-600 text-lg">💎</span>
                          </div>
                          <span className="font-semibold text-gray-800">Loyalty Options</span>
                        </div>
                        <button 
                          onClick={() => setShowLoyaltyModal(true)}
                          className="text-sm text-amber-600 hover:text-amber-700 underline"
                        >
                          Update Balances
                        </button>
                      </div>
                      
                      <div className="space-y-3">
                        {/* Cash Option */}
                        <div className="bg-white rounded-lg p-3 border border-gray-200">
                          <div className="flex justify-between items-center">
                            <div className="flex items-center space-x-2">
                              <span className="text-green-600">💰</span>
                              <span className="font-medium text-gray-800">Pay Cash</span>
                            </div>
                            <span className="font-bold text-gray-900">{formatCurrency(pkg.total_cost)}</span>
                          </div>
                        </div>

                        {/* Points Options */}
                        {pkg.loyalty_analysis?.hotel_loyalty_options.map((option, idx) => (
                          <div key={idx} className="bg-white rounded-lg p-3 border border-gray-200">
                            <div className="flex justify-between items-center">
                              <div className="flex items-center space-x-2">
                                <span className="text-blue-600">🎫</span>
                                <span className="font-medium text-gray-800">Use Points</span>
                                <span className="text-xs text-gray-500">({option.program})</span>
                              </div>
                              <div className="text-right">
                                <div className="font-bold text-blue-600">{option.points_needed.toLocaleString()} pts</div>
                                <div className="text-xs text-gray-500">Value: {formatCurrency(option.points_needed * option.effective_value)}</div>
                              </div>
                            </div>
                          </div>
                        ))}

                        {/* Recommendation */}
                        {pkg.loyalty_analysis?.best_recommendation && (
                          <div className="bg-gradient-to-r from-emerald-500 to-green-500 rounded-lg p-3 text-white">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <span>💡</span>
                                <span className="font-semibold">Recommendation</span>
                              </div>
                              <span className="font-bold">{pkg.loyalty_analysis.best_recommendation.recommendation}</span>
                            </div>
                            <div className="text-sm text-emerald-100 mt-1">
                              {pkg.loyalty_analysis.best_recommendation.savings > 0 
                                ? `Save ${formatCurrency(pkg.loyalty_analysis.best_recommendation.savings)} with ${pkg.loyalty_analysis.best_recommendation.program}`
                                : `Best value with ${pkg.loyalty_analysis.best_recommendation.program}`
                              }
                            </div>
                          </div>
                        )}

                        {/* No Loyalty Options */}
                        {!pkg.loyalty_analysis?.hotel_loyalty_options.length && (
                          <div className="bg-gray-100 rounded-lg p-3 border border-gray-200">
                            <div className="flex items-center space-x-2">
                              <span className="text-gray-500">ℹ️</span>
                              <span className="text-sm text-gray-600">No loyalty options available</span>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Book Now Button */}
                    <div className="p-6 pt-0">
                      <button className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-3 px-4 rounded-xl font-semibold hover:from-green-600 hover:to-emerald-600 transition-all duration-300 transform hover:scale-105 shadow-lg">
                        Book This Package
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Loyalty Balance Modal */}
      {showLoyaltyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-gray-800">💎 Loyalty Program Balances</h3>
              <button 
                onClick={() => setShowLoyaltyModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="text-sm text-gray-600 mb-4">
                Update your loyalty program balances to get personalized recommendations.
              </div>
              
              {/* IHG */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-gray-800">IHG Rewards</span>
                  <span className="text-sm text-gray-500">InterContinental Hotels Group</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="number" 
                    placeholder="Points balance"
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    defaultValue="25000"
                  />
                  <span className="text-sm text-gray-500">points</span>
                </div>
              </div>

              {/* Marriott */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-gray-800">Marriott Bonvoy</span>
                  <span className="text-sm text-gray-500">Marriott International</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="number" 
                    placeholder="Points balance"
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    defaultValue="15000"
                  />
                  <span className="text-sm text-gray-500">points</span>
                </div>
              </div>

              {/* Hilton */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-gray-800">Hilton Honors</span>
                  <span className="text-sm text-gray-500">Hilton Worldwide</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="number" 
                    placeholder="Points balance"
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    defaultValue="30000"
                  />
                  <span className="text-sm text-gray-500">points</span>
                </div>
              </div>

              {/* American Airlines */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold text-gray-800">American Airlines</span>
                  <span className="text-sm text-gray-500">AAdvantage</span>
                </div>
                <div className="flex items-center space-x-2">
                  <input 
                    type="number" 
                    placeholder="Miles balance"
                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    defaultValue="45000"
                  />
                  <span className="text-sm text-gray-500">miles</span>
                </div>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button 
                onClick={() => setShowLoyaltyModal(false)}
                className="flex-1 bg-gray-200 text-gray-800 py-2 px-4 rounded-lg font-medium hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={() => {
                  // TODO: Save loyalty balances
                  setShowLoyaltyModal(false);
                }}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-colors"
              >
                Save & Update
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
