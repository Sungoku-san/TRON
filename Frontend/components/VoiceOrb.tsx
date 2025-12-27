"use client"
import { motion } from "framer-motion"

type Props = {
  state: "idle" | "listening" | "thinking" | "speaking"
}

export default function VoiceOrb({ state }: Props) {
  const colorMap: any = {
    idle: "bg-blue-500",
    listening: "bg-yellow-400",
    thinking: "bg-purple-500",
    speaking: "bg-green-400",
  }

  return (
    <motion.div
      animate={{ scale: [1, 1.15, 1] }}
      transition={{ repeat: Infinity, duration: 1.4 }}
      className={`w-32 h-32 rounded-full ${colorMap[state]} blur-sm shadow-2xl`}
    />
  )
}