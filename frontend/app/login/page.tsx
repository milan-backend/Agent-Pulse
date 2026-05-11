"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { loginUser } from "@/lib/auth";


export default function LoginPage() {

  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");


  const handleLogin = async () => {

    setLoading(true);
    setError("");

    try {

      const data = await loginUser(
        email,
        password,
      );
      console.log(data)

      if (data.error) {
        setError(data.error);
        setLoading(false);
        return;
      }

      localStorage.setItem(
        "token",
        data.access_token
      );

      router.push("/dashboard");

    } catch (err) {
      setError("Login failed");
    }

    setLoading(false);
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-6">

      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md">

        <h1 className="text-4xl font-extrabold text-slate-900 mb-2">
          Welcome Back
        </h1>

        <p className="text-slate-500 mb-8">
          Login to AgentPulse
        </p>


        <div className="space-y-4">

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
            onClick={handleLogin}
            disabled={loading}
            className="w-full bg-slate-900 text-white py-3 rounded-xl font-semibold hover:bg-slate-800"
          >
            {loading ? "Logging In..." : "Login"}
          </button>

        </div>
      </div>
    </div>
  );
}