export default function LiveIndicator() {
  return (
    <div className="
      flex
      items-center
      gap-2
      text-green-400
      font-bold
      animate-pulse
    ">
      <div className="
        w-3
        h-3
        rounded-full
        bg-green-400
      " />

      LIVE
    </div>
  )
}