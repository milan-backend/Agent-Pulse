"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
const API_URL = process.env.NEXT_PUBLIC_API_URL

export default function SettingsPage() {
  const router = useRouter()

  const [apiKey, setApiKey] = useState("")
  const [maxSteps, setMaxSteps] = useState(20)
  const [maxRuntime, setMaxRuntime] = useState(2)
  const [maxCost, setMaxCost] = useState(3)

  useEffect(() => {
    loadCurrentApiKey()
  }, [])

  async function loadCurrentApiKey() {
    try {
      const token = localStorage.getItem("token")

      const response = await fetch(
        `${API_URL}/auth/me`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      if (data.api_key) {
        setApiKey(data.api_key)
      }
    } catch (error) {
      console.log(error)
    }
  }

  async function regenerateApiKey() {
    try {
      const token = localStorage.getItem("token")

      const response = await fetch(
        `${API_URL}/agents/regenerate-key`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      const data = await response.json()

      console.log(data)

      setApiKey(data.api_key)

      alert("API Key Regenerated Successfully")
    } catch (error) {
      console.log(error)
      alert("Failed to regenerate API key")
    }
  }

  async function copyApiKey() {
    try {
      await navigator.clipboard.writeText(apiKey)

      alert("API Key Copied")
    } catch (error) {
      console.log(error)
    }
  }

  async function saveSettings() {
    try {
      alert("Settings Saved Successfully")
    } catch (error) {
      console.log(error)
    }
  }

  async function stopAllAgents() {
    try {
      const token = localStorage.getItem("token")

      const response = await fetch(
        `${API_URL}/agents/kill`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.ok) {
        alert("All Agents Stopped")
      } else {
        alert("Failed To Stop Agents")
      }
    } catch (error) {
      console.log(error)
    }
  }

  async function resumeAgents() {
    try {
     const token = localStorage.getItem("token")

     const response = await fetch(
      `${API_URL}/agents/resume`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    )

     const data = await response.json()

     if (response.ok) {
      alert(data.message)
      console.log("Resumed Agents:", data.resumed_agents)
    }else {
      alert(data.detail || "Failed To Resume Agents")
    }

  } catch (error) {
     console.log(error)
     alert("Server Error")
  }
}

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="flex items-center justify-between mb-10">
        <div>
          <h1 className="text-6xl font-black text-cyan-400 mb-3">
            Settings
          </h1>

          <p className="text-gray-400 text-lg">
            Manage platform security, runtime controls and emergency systems.
          </p>
        </div>

        <button
          onClick={() => router.push("/dashboard")}
          className="px-6 py-3 rounded-xl bg-gray-900 border border-cyan-500 hover:bg-cyan-500 hover:text-black transition-all"
        >
          Back To Dashboard
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-[#07111f] border border-cyan-500 rounded-3xl p-8">
          <h2 className="text-5xl font-black text-cyan-400 mb-3">
            API Security
          </h2>

          <p className="text-gray-400 mb-8">
            Regenerate your platform API credentials.
          </p>

          <div className="bg-black border border-gray-800 rounded-2xl px-6 py-5 mb-6 overflow-x-auto">
            <p className="text-green-400 font-bold text-lg">
              {apiKey || "Loading API Key..."}
            </p>
          </div>

          <div className="flex gap-4">
            <button
              onClick={regenerateApiKey}
              className="flex-1 bg-cyan-400 text-black py-4 rounded-2xl font-bold text-lg hover:scale-105 transition-all"
            >
              Regenerate API Key
            </button>

            <button
              onClick={copyApiKey}
              className="px-8 bg-gray-700 rounded-2xl font-bold hover:bg-gray-600 transition-all"
            >
              Copy
            </button>
          </div>
        </div>

        <div className="bg-[#07111f] border border-cyan-500 rounded-3xl p-8">
          <h2 className="text-5xl font-black text-cyan-400 mb-3">
            Budget Controls
          </h2>

          <p className="text-gray-400 mb-8">
            Configure mission safety limits and runtime caps.
          </p>

          <div className="space-y-6">
            <div>
              <label className="block mb-2 text-gray-300">
                Max Mission Steps
              </label>

              <input
                type="number"
                value={maxSteps}
                onChange={(e) =>
                  setMaxSteps(Number(e.target.value))
                }
                className="w-full bg-black border border-gray-800 rounded-2xl px-5 py-4"
              />
            </div>

            <div>
              <label className="block mb-2 text-gray-300">
                Max Runtime (mins)
              </label>

              <input
                type="number"
                value={maxRuntime}
                onChange={(e) =>
                  setMaxRuntime(Number(e.target.value))
                }
                className="w-full bg-black border border-gray-800 rounded-2xl px-5 py-4"
              />
            </div>

            <div>
              <label className="block mb-2 text-gray-300">
                Max Cost ($)
              </label>

              <input
                type="number"
                value={maxCost}
                onChange={(e) =>
                  setMaxCost(Number(e.target.value))
                }
                className="w-full bg-black border border-gray-800 rounded-2xl px-5 py-4"
              />
            </div>

            <button
              onClick={saveSettings}
              className="w-full bg-cyan-400 text-black py-4 rounded-2xl font-bold text-lg hover:scale-105 transition-all"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>

      <div className="mt-10 bg-[#1a0707] border border-red-500 rounded-3xl p-8">
        <h2 className="text-5xl font-black text-red-400 mb-3">
          Danger Zone
        </h2>

        <p className="text-gray-400 mb-8">
          Emergency controls for shutting down all agents.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-black border border-gray-800 rounded-2xl p-6">
            <h3 className="text-3xl font-black text-white mb-3">
              Emergency Stop
            </h3>

            <p className="text-gray-400">
              Instantly terminate all running AI missions.
            </p>
          </div>

          <button
            onClick={stopAllAgents}
            className="bg-red-500 hover:bg-red-600 rounded-2xl text-3xl font-black transition-all"
          >
            STOP ALL AGENTS
          </button>
          <button
            onClick={resumeAgents}
            className="
              bg-green-500
              hover:bg-green-600
              active:scale-95
              rounded-2xl
              text-3xl
              font-black
              text-white
              transition-all
              duration-200
              shadow-lg
              p-6
              mt-4
              w-full
            "
        >
            RESUME AGENTS
           </button>
        </div>
      </div>
    </div>
  )
}