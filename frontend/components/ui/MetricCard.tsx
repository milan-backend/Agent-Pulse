interface Props {
  title: string
  value: string | number
  color?: string
  subtitle?: string
}

export default function MetricCard({
  title,
  value,
  color = "text-cyan-400",
  subtitle,
}: Props) {

  return (
    <div className="
      bg-[#091121]
      border
      border-white/10
      rounded-3xl
      p-6
      hover:border-cyan-500/30
      transition-all
      duration-300
    ">

      <p className="
        text-gray-400
        mb-3
        tracking-wide
      ">
        {title}
      </p>

      <h2 className={`
        text-5xl
        font-black
        ${color}
      `}>
        {value}
      </h2>

      {subtitle && (
        <p className="
          mt-3
          text-sm
          text-gray-500
        ">
          {subtitle}
        </p>
      )}

    </div>
  )
}