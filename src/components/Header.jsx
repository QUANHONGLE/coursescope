import { motion } from "framer-motion";

const Header = ({ onChangeMajor, selectedMajor }) => (
  <header className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b">
    <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-2xl bg-black text-white grid place-items-center text-xs">
          CS
        </div>
        <h1 className="text-lg font-semibold tracking-tight">CourseScope</h1>
      </div>
      <div className="flex items-center gap-4">
        {selectedMajor && (
          <div className="text-xs text-gray-600">
            {selectedMajor.name} · {selectedMajor.concentration}
          </div>
        )}
        {onChangeMajor && (
          <button
            onClick={onChangeMajor}
            className="relative text-xs px-3 py-1.5 rounded-lg border border-gray-200 hover:border-gray-300 text-gray-700 hover:text-black font-medium transition-colors overflow-hidden"
          >
            <motion.div
              className="absolute inset-0 opacity-40"
              style={{
                backgroundImage: "linear-gradient(90deg, #fef3c7, #fde68a, #fcd34d, #fbbf24, #fde68a, #fef3c7)",
                backgroundSize: "200% 100%"
              }}
              animate={{
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "linear"
              }}
            />
            <motion.div
              className="absolute inset-0 opacity-30"
              style={{
                backgroundImage: "linear-gradient(90deg, #ddd6fe, #c4b5fd, #a78bfa, #8b5cf6, #c4b5fd, #ddd6fe)",
                backgroundSize: "200% 100%"
              }}
              animate={{
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "linear"
              }}
            />
            <motion.div
              className="absolute inset-0 opacity-30"
              style={{
                backgroundImage: "linear-gradient(90deg, #bfdbfe, #93c5fd, #60a5fa, #3b82f6, #93c5fd, #bfdbfe)",
                backgroundSize: "200% 100%"
              }}
              animate={{
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"]
              }}
              transition={{
                duration: 5,
                repeat: Infinity,
                ease: "linear"
              }}
            />
            <span className="relative z-10">Change Major</span>
          </button>
        )}
        <span className="text-xs text-gray-500">MVP · Unified course planning</span>
      </div>
    </div>
  </header>
);

export default Header;