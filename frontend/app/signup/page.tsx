"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { signupUser } from "@/lib/auth";


export default function SignupPage() {

  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handleSignup = async () => {

    setLoading(true);
    setError("");

    try {

      const data = await signupUser({
        name,
        email,
        password
    });

      if (data.error) {
        setError(data.error);
        setLoading(false);
        return;
      }

      router.push("/login");

    } catch (err) {
      setError("Signup failed");
    }

    setLoading(false);
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">

      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">

        <h1 className="text-4xl font-extrabold text-slate-900 mb-2">
          Create Account
        </h1>

        <p className="text-slate-500 mb-8">
          Signup to AgentPulse
        </p>


        <div className="space-y-4">

          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border border-slate-300 rounded-xl px-4 py-3"
          />

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full border border-slate-300 rounded-xl px-4 py-3"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border border-slate-300 rounded-xl px-4 py-3"
          />

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <button
            onClick={handleSignup}
            disabled={loading}
            className="w-full bg-slate-900 text-white py-3 rounded-xl font-semibold hover:bg-slate-800"
          >
            {loading ? "Creating Account..." : "Signup"}
          </button>
          
          
          <div className="mt-6 text-center">

          <p className="text-sm text-gray-400">
           Already have an account?
          </p>

          <button
           onClick={() => router.push("/login")}
           className="
           mt-3
           px-5
           py-2
           rounded-xl
           bg-cyan-500/20
           border
           border-cyan-400/30
           text-cyan-300
          font-semibold
          hover:bg-cyan-500/30
          transition
    
    "
  >
    Login
  </button>

</div>
        </div>
      </div>
    </div>
  );
}