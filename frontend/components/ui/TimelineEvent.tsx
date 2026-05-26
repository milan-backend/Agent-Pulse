import StatusBadge from "./StatusBadge"

interface Props {
  event: string
  timestamp: string
  cost?: number
}

export default function TimelineEvent({
  event,
  timestamp,
  cost,
}: Props) {

  return (
    <div className="
      relative
      pl-10
      border-l
      border-cyan-500/20
      pb-8
    ">

      <div className="
        absolute
        -left-[9px]
        top-1
        w-4
        h-4
        rounded-full
        bg-cyan-400
        shadow-lg
        shadow-cyan-400/40
      " />

      <div className="
        bg-[#091121]
        border
        border-white/10
        rounded-2xl
        p-5
      ">

        <div className="
          flex
          items-center
          justify-between
        ">

          <StatusBadge
            status={
              event ||
              "unknown"
            }
          />

          <p className="
            text-gray-500
            text-sm
          ">
            {
              timestamp
                ? new Date(
                    timestamp
                  ).toLocaleString()
                : "N/A"
            }
          </p>

        </div>

        {cost !== undefined && (
          <p
            className="
              mt-4
              text-green-400
              font-semibold
            "
          >
            Cost: $
            {
              Number(cost).toFixed(4)
            }
          </p>
        )}

      </div>

    </div>
  )
}