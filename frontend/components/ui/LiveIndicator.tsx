"use client";

export default function LiveIndicator() {

  return (

    <div className="
      flex
      items-center
      gap-4
      rounded-full
      border
      border-emerald-500/20
      bg-emerald-500/10
      px-6
      py-3
      shadow-[0_0_30px_rgba(16,185,129,0.15)]
    ">

      {/* DOT */}

      <div className="
        relative
        flex
        h-4
        w-4
      ">

        <span className="
          absolute
          inline-flex
          h-full
          w-full
          animate-ping
          rounded-full
          bg-emerald-400
          opacity-75
        " />

        <span className="
          relative
          inline-flex
          h-4
          w-4
          rounded-full
          bg-emerald-400
        " />

      </div>

      {/* TEXT */}

      <div className="
        flex
        items-center
        gap-3
      ">

        <span className="
          text-sm
          font-black
          tracking-[0.2em]
          text-emerald-400
        ">

          LIVE

        </span>

        <span className="
          hidden
          md:block
          text-sm
          text-zinc-400
        ">

          Runtime Active

        </span>

      </div>

    </div>

  );
}