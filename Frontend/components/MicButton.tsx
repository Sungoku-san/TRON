type Props = {
  onClick: () => void
}

export default function MicButton({ onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="p-4 rounded-full bg-red-600 hover:scale-110 transition shadow-lg"
    >
      🎤
    </button>
  )
}