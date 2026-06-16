"use client";

import { useEffect, useState } from "react";
import { createCheckout, getCurrentPlan } from "@/components/api";
import { initializePaddle, Paddle } from "@paddle/paddle-js";
import { CreditCard, Rocket, Shield, Cpu, CheckCircle2, Sparkles, Globe } from "lucide-react";

// Updated pricing matrix with precise math matching international conversion (₹26,085 & ₹180,300)
const plansData = (isIndia: boolean, billingCycle: "monthly" | "yearly") => [
  {
    name: "Free",
    price: isIndia ? "₹0" : "$0",
    description: "For solo runtime experimentation",
    features: [
      "Shared Community API Key Tier",
      "Auto-Prompt to add your own key on HTTP 429",
      "Bring Your Own API Key (BYOK) Ready",
      "Agent State Controls (Pause / Resume / Kill)",
      "Audit & Event History Logs Active",
      "1 Active AI Agent Capacity",
      "1 Concurrent Agent Execution Window",
      "10 Total Runtime Hours Limit",
      "Live WebSocket Dashboard Updates",
      "Standard Performance Analytics",
      "No RAG Knowledge Document Uploads"
    ],
    button: "Current Plan",
    disabled: true,
    glow: "from-slate-700/40 to-slate-900/40",
    border: "border-slate-700/40",
  },
  {
    name: "Pro",
    // 💡 CALCULATION: ₹26,085 / 12 = ₹2,174 (Correct parity with $276/yr)
    price: isIndia 
      ? (billingCycle === "monthly" ? "₹2,499" : "₹2,174") 
      : (billingCycle === "monthly" ? "$29" : "$23"),
    description: "Advanced runtime monitoring and guardrails built for growing developer teams",
    features: [
      "Bring Your Own API Key (BYOK) Native Integration",
      "Agent State Controls (Pause / Resume / Kill)",
      "Automated Budget Ceiling Guardrails",
      "State Loop & Infinite Execution Detection",
      "Multi-Workspace Partitioning Active",
      "Model Context Protocol (MCP Layer Access)",
      "RAG Documents Enabled (Up to 20 files)",
      "10 Active AI Agent Capacity",
      "5 Concurrent Agent Executions",
      "100 Total Runtime Hours Limit",
      "10 Team Member Seats Allocated",
      "Workspace Bulk Controls (Kill All / Resume All)",
      "Priority Asynchronous Execution Queues"
    ],
    button: "Upgrade to Pro",
    planKey: "pro",
    featured: true,
    glow: "from-cyan-500/20 to-blue-500/10",
    border: "border-cyan-400/30",
  },
  {
    name: "Enterprise",
    // 💡 CALCULATION: ₹180,300 / 12 = ₹15,025 (Correct parity with $1,908/yr)
    price: isIndia 
      ? (billingCycle === "monthly" ? "₹16,999" : "₹15,025") 
      : (billingCycle === "monthly" ? "$199" : "$159"),
    description: "Full scaling capacity and high-throughput logging for high-volume agent frameworks",
    features: [
      "Bring Your Own API Key (BYOK) Native Integration",
      "Agent State Controls (Pause / Resume / Kill)",
      "Automated Budget Ceiling Guardrails",
      "Enterprise Role-Based Access Control (RBAC)",
      "RAG Knowledge Documents (Up to 1,000 files)",
      "100 Active AI Agent Capacity",
      "100 Concurrent Agent Executions",
      "10,000 Total Runtime Hours Limit",
      "100 Team Member Seats Allocated",
      "Infinite Telemetry Audit Log History",
      "Workspace Bulk Controls (Kill All / Resume All)"
    ],
    button: "Upgrade to Enterprise",
    planKey: "enterprise",
    glow: "from-fuchsia-500/20 to-cyan-500/10",
    border: "border-fuchsia-400/30",
  }
];

export default function BillingPage() {
  const [currentPlan, setCurrentPlan] = useState("free");
  const [isIndia, setIsIndia] = useState(true);
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const [detectingRegion, setDetectingRegion] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState(false);

  useEffect(() => {
    const locateUserRegion = async () => {
      try {
        const response = await fetch("https://ip-api.com/json/");
        const data = await response.json();
        if (data && data.countryCode) {
          setIsIndia(data.countryCode === "IN");
        }
      } catch (err) {
        setIsIndia(true);
      } finally {
        setDetectingRegion(false);
      }
    };
    locateUserRegion();
  }, []);

  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://checkout.razorpay.com/v1/checkout.js";
    script.async = true;
    document.body.appendChild(script);
    return () => { if (document.body.contains(script)) document.body.removeChild(script); };
  }, []);

  useEffect(() => {
    const loadPlan = async () => {
      try {
        const data = await getCurrentPlan();
        setCurrentPlan((data?.plan || "free").toLowerCase());
      } catch {
        setCurrentPlan("free");
      }
    };
    loadPlan();
  }, []);

  const handleCheckout = async (planName: string) => {
    setCheckoutLoading(true);
    try {
      const selectedGateway = isIndia ? "razorpay" : "paddle";
      const response = await createCheckout(planName, selectedGateway, billingCycle);

      if (selectedGateway === "paddle") {
        const paddleInstance: Paddle | undefined = await initializePaddle({
          environment: response.environment,
          token: response.client_token
        });

        if (!paddleInstance) throw new Error("Paddle.js failed to initialize.");

        paddleInstance.Checkout.open({
          items: [{ priceId: response.price_id, quantity: 1 }],
          customData: response.custom_data,
          settings: {
            displayMode: "overlay",
            theme: "dark",
            locale: "en",
            successUrl: response.success_url
          }
        });
        return;
      }

      const options = {
        key: response.key_id,
        amount: response.amount,
        currency: response.currency,
        name: "Agent Pulse",
        description: `Upgrade to ${planName.toUpperCase()} (${billingCycle.toUpperCase()})`,
        order_id: response.order_id,
        handler: function (razorpayResponse: any) {
          window.location.href = razorpayResponse.razorpay_payment_id ? response.success_url : response.cancel_url;
        },
        modal: { ondismiss: () => console.log("Wizard closed.") },
        theme: { color: "#22d3ee" }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.open();

    } catch (error) {
      console.error(error);
      alert("Checkout failed. Check logs.");
    } finally {
      setCheckoutLoading(false);
    }
  };

  const dynamicPlans = plansData(isIndia, billingCycle);

  return (
    <div className="min-h-screen bg-[#020817] text-white overflow-y-auto relative p-4 md:p-8">
      <div className="absolute top-0 right-0 h-[500px] w-[500px] rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-0 h-[500px] w-[500px] rounded-full bg-fuchsia-500/10 blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        
        <div className="rounded-[40px] border border-cyan-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-6 md:p-8 overflow-hidden relative mb-6">
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="flex items-center gap-5">
              <div className="h-16 w-16 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 flex items-center justify-center shrink-0">
                <CreditCard size={32} className="text-cyan-300" />
              </div>
              <div>
                <h1 className="text-3xl md:text-5xl font-black tracking-tight leading-none">AI Runtime Pricing</h1>
                <p className="mt-2 text-slate-400 text-sm md:text-base max-w-xl">
                  Scale autonomous AI agents seamlessly.
                  {detectingRegion ? " (Sniffing locale...)" : isIndia ? " 🇮🇳 INR Tier Active" : " 🌐 USD Tier Active"}
                </p>
              </div>
            </div>

            <div className="bg-slate-900/90 border border-slate-800 p-1.5 rounded-2xl flex items-center gap-2 self-start md:self-auto shrink-0">
              <button onClick={() => setIsIndia(true)} className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${isIndia ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20" : "text-slate-400 hover:text-slate-200"}`}>🇮🇳 INR</button>
              <button onClick={() => setIsIndia(false)} className={`px-4 py-2 rounded-xl text-xs font-mono font-bold transition-all ${!isIndia ? "bg-cyan-500/10 text-cyan-300 border border-cyan-500/20" : "text-slate-400 hover:text-slate-200"}`}><Globe size={12} /> USD</button>
            </div>
          </div>
        </div>

        <div className="flex justify-center mb-8">
          <div className="bg-slate-950 border border-slate-800 p-1 rounded-2xl flex items-center relative shadow-2xl">
            <button onClick={() => setBillingCycle("monthly")} className={`px-6 py-2.5 rounded-xl text-xs font-black font-mono tracking-widest uppercase transition-all duration-300 ${billingCycle === "monthly" ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-black shadow-lg shadow-cyan-500/20" : "text-slate-400 hover:text-slate-200"}`}>Monthly Base</button>
            <button onClick={() => setBillingCycle("yearly")} className={`px-6 py-2.5 rounded-xl text-xs font-black font-mono tracking-widest uppercase transition-all duration-300 flex items-center gap-2 ${billingCycle === "yearly" ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-black shadow-lg shadow-cyan-500/20" : "text-slate-400 hover:text-slate-200"}`}>
              Yearly Loop <span className="bg-green-500/20 text-green-400 text-[9px] px-2 py-0.5 rounded-md border border-green-500/30">SAVE 20%</span>
            </button>
          </div>
        </div>

        <div className="mb-8 rounded-[32px] border border-green-500/20 bg-[linear-gradient(180deg,#071120_0%,#091525_100%)] p-6 md:p-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-300 font-black text-xs md:text-sm uppercase tracking-widest">Your Current Plan</p>
              <h2 className="text-3xl md:text-4xl font-black mt-1">{currentPlan.toUpperCase()}</h2>
            </div>
            <div className="px-4 py-2 rounded-full bg-green-500/10 border border-green-500/20 text-green-300 font-black text-xs">ACTIVE</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch">
          {dynamicPlans.map((plan) => (
            <div key={plan.name} className={`relative rounded-[36px] border ${plan.border} bg-[linear-gradient(180deg,#0b1220_0%,#091525_100%)] p-6 md:p-8 flex flex-col justify-between overflow-hidden backdrop-blur-xl transition-all duration-300 min-h-[700px] ${plan.featured ? "shadow-[0_0_50px_rgba(34,211,238,0.15)] ring-1 ring-cyan-400/20" : ""}`}>
              <div className={`absolute inset-0 bg-gradient-to-br ${plan.glow} opacity-30 pointer-events-none`} />
              <div className="relative z-10 flex flex-col h-full justify-between">
                <div>
                  {plan.featured && <div className="inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-500/10 px-3 py-1 mb-4"><Sparkles size={12} className="text-cyan-300" /><span className="text-[10px] font-black text-cyan-300 tracking-wider">MOST POPULAR</span></div>}
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl md:text-3xl font-black tracking-tight">{plan.name}</h2>
                    <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center shrink-0">{plan.name === "Enterprise" ? <Shield size={20} className="text-fuchsia-300" /> : plan.name === "Pro" ? <Rocket size={20} className="text-cyan-300" /> : <Cpu size={20} className="text-slate-300" />}</div>
                  </div>
                  <div className="mb-6">
                    <div className="flex items-end gap-1.5"><span className="text-4xl md:text-5xl font-black tracking-tight">{plan.price}</span><span className="text-slate-400 text-xs font-mono mb-1">/{billingCycle === "monthly" ? "month" : "month, billed yearly"}</span></div>
                    <p className="mt-2 text-slate-400 text-xs leading-relaxed min-h-[32px]">{plan.description}</p>
                  </div>
                  <div className="space-y-3.5 border-t border-slate-900 pt-5 mb-8">
                    {plan.features.map((feature) => (<div key={feature} className="flex items-start gap-2.5"><CheckCircle2 size={14} className="text-cyan-300 mt-0.5 shrink-0" /><span className="text-slate-200 text-xs font-medium leading-normal">{feature}</span></div>))}
                  </div>
                </div>
                <button disabled={currentPlan === plan.name.toLowerCase() || checkoutLoading} onClick={() => plan.planKey && handleCheckout(plan.planKey)} className={`w-full py-4 rounded-xl font-black font-mono text-xs uppercase tracking-widest transition-all mt-auto ${currentPlan === plan.name.toLowerCase() ? "bg-green-600/20 border border-green-500/30 text-green-400 cursor-not-allowed" : "bg-cyan-400 text-black hover:shadow-[0_0_25px_rgba(34,211,238,0.35)] active:scale-[0.99]"} ${checkoutLoading ? "opacity-50 cursor-wait" : ""}`}>{currentPlan === plan.name.toLowerCase() ? "Current Active Plan" : checkoutLoading ? "Building Session..." : plan.button}</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}