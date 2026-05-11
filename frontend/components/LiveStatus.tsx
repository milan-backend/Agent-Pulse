"use client"

type Props = {
  connected: boolean
}

export default function LiveStatus({
  connected
}: Props) {
  return (
    <div
      className={`rounded-xl px-4 py-2 font-bold ${
        connected
          ? "bg-green-500/20 text-green-300"
          : "bg-red-500/20 text-red-300"
      }`}
    >
      WebSocket: {connected ? "Connected" : "Disconnected"}
    </div>
  )
}