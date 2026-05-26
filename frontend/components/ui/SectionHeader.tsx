"use client";

interface Props {
  title: string;
  subtitle?: string;
  centered?: boolean;
  size?: "sm" | "md" | "lg";
}

export default function SectionHeader({
  title,
  subtitle,
  centered = false,
  size = "lg",
}: Props) {

  return (

    <div
      className={
        centered
          ? "text-center"
          : ""
      }
    >

      {/* TITLE */}

      <h1
        className={`
          ${
            size === "sm"
              ? `
                  text-3xl
                  md:text-4xl
                `
              : size === "md"
              ? `
                  text-4xl
                  md:text-5xl
                `
              : `
                  text-5xl
                  md:text-6xl
                `
          }
          font-black
          tracking-tight
          leading-none
        `}
      >

        <span className="
          bg-gradient-to-r
          from-cyan-300
          via-cyan-400
          to-blue-500
          bg-clip-text
          text-transparent
        ">

          {title}

        </span>

      </h1>

      {/* SUBTITLE */}

      {subtitle && (

        <p className="
          mt-4
          max-w-3xl
          text-lg
          text-zinc-400
          leading-relaxed
        ">

          {subtitle}

        </p>

      )}

    </div>

  );
}