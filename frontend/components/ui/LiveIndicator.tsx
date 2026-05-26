"use client";

interface Props {
  live?: boolean
  text?: string
}

export default function LiveIndicator({
  live = true,
  text = "Runtime Active",
}: Props) {

  return (

    <div
      className={`
        flex
        items-center
        gap-4
        rounded-full
        px-6
        py-3
        shadow-[0_0_30px_rgba(16,185,129,0.15)]

        ${
          live
            ? `
              border
              border-emerald-500/20
              bg-emerald-500/10
            `
            : `
              border
              border-red-500/20
              bg-red-500/10
            `
        }
      `}
    >

      {/* DOT */}

      <div className="
        relative
        flex
        h-4
        w-4
      ">

        <span
          className={`
            absolute
            inline-flex
            h-full
            w-full
            animate-ping
            rounded-full
            opacity-75

            ${
              live
                ? "bg-emerald-400"
                : "bg-red-400"
            }
          `}
        />

        <span
          className={`
            relative
            inline-flex
            h-4
            w-4
            rounded-full

            ${
              live
                ? "bg-emerald-400"
                : "bg-red-400"
            }
          `}
        />

      </div>

      {/* TEXT */}

      <div className="
        flex
        items-center
        gap-3
      ">

        <span
          className={`
            text-sm
            font-black
            tracking-[0.2em]

            ${
              live
                ? "text-emerald-400"
                : "text-red-400"
            }
          `}
        >

          {
            live
              ? "LIVE"
              : "OFFLINE"
          }

        </span>

        <span className="
          hidden
          md:block
          text-sm
          text-zinc-400
        ">

          {text}

        </span>

      </div>

    </div>

  );
}