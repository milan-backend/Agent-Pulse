interface Props {
  status?: string
}

export default function StatusBadge({
  status,
}: Props) {

  const normalizedStatus =
    (
      status || "unknown"
    ).toLowerCase()

  const styles: any = {
    completed:
      "bg-green-500/20 text-green-400 border-green-500/30",

    running:
      "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",

    failed:
      "bg-red-500/20 text-red-400 border-red-500/30",

    retry:
      "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",

    cache_hit:
      "bg-purple-500/20 text-purple-400 border-purple-500/30",

    blocked:
      "bg-pink-500/20 text-pink-400 border-pink-500/30",

    pending:
      "bg-amber-500/20 text-amber-300 border-amber-500/30",

    paused:
      "bg-orange-500/20 text-orange-300 border-orange-500/30",

    killed:
      "bg-rose-500/20 text-rose-300 border-rose-500/30",
  }

  return (
    <div
      className={`
        px-4
        py-2
        rounded-full
        border
        text-sm
        font-bold
        uppercase
        tracking-wider
        inline-flex
        items-center
        gap-2
        ${styles[normalizedStatus] ||
          "bg-gray-500/20 text-gray-300 border-gray-500/20"}
      `}
    >
      <div className="w-2 h-2 rounded-full bg-current" />

      {
        normalizedStatus.replace(
          "_",
          " "
        )
      }
    </div>
  )
}