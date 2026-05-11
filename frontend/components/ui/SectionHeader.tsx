interface Props {
  title: string
  subtitle: string
}

export default function SectionHeader({
  title,
  subtitle,
}: Props) {

  return (
    <div className="mb-8">

      <h2 className="
        text-4xl
        font-black
        text-white
      ">
        {title}
      </h2>

      <p className="
        text-gray-400
        mt-2
      ">
        {subtitle}
      </p>

    </div>
  )
}