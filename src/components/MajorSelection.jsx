import { motion } from "framer-motion";
import { useState, useEffect } from "react";

const MajorSelection = ({ onSelectMajor, selectedMajor, onSkipPlanning }) => {
  const [majors, setMajors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/majors")
      .then(res => res.json())
      .then(data => {
        // Add descriptions for each major/concentration
        const descriptionsMap = {
          "null": "General Computer Science degree with flexible electives",
          "Computer Systems": "Focus on computer architecture, operating systems, and networks",
          "Human-Centered Computing": "Focus on human-computer interaction, UI/UX, and design",
          "Software Engineering": "Focus on software development, design patterns, and engineering practices",
          "Design": "Interdisciplinary focus on design thinking and creative computing"
        };

        // Remove duplicates based on name and concentration
        const uniqueMajorsMap = new Map();
        data.forEach(major => {
          const key = `${major.name}-${major.concentration || 'null'}`;
          // Keep the first occurrence of each unique major/concentration combo
          if (!uniqueMajorsMap.has(key)) {
            uniqueMajorsMap.set(key, major);
          }
        });

        const uniqueMajors = Array.from(uniqueMajorsMap.values());

        const enrichedMajors = uniqueMajors.map(major => ({
          ...major,
          description: descriptionsMap[major.concentration || "null"] || "Computer Science degree"
        }));

        setMajors(enrichedMajors);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching majors:", err);
        setError("Failed to load majors");
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2">Choose Your Major</h1>
          <p className="text-gray-600">Loading majors...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2">Choose Your Major</h1>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Choose Your Major</h1>
        <p className="text-gray-600">
          Select your major and concentration to see your course requirements
        </p>
        <button
          onClick={onSkipPlanning}
          className="mt-4 px-6 py-2.5 text-sm rounded-xl border border-gray-200 hover:border-gray-300 text-gray-700 hover:text-black font-medium transition-colors overflow-hidden relative"
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
          <span className="relative z-10">Skip Planning - Browse All Courses</span>
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {majors.map((major) => (
          <motion.button
            key={major.id}
            onClick={() => onSelectMajor(major)}
            className="text-left p-6 rounded-2xl border-2 bg-white hover:border-black transition-all"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="h-12 w-12 rounded-xl bg-black text-white grid place-items-center font-bold">
                CS
              </div>
              {selectedMajor?.id === major.id && (
                <span className="text-green-600 text-xl">✓</span>
              )}
            </div>
            <h3 className="font-semibold text-lg mb-1">{major.name}</h3>
            <p className="text-sm text-gray-600 mb-2">
              {major.concentration || "General"}
            </p>
            <p className="text-xs text-gray-500">{major.description}</p>
          </motion.button>
        ))}
      </div>

      {selectedMajor && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-center"
        >
          <button
            onClick={() => onSelectMajor(selectedMajor)}
            className="px-8 py-3 bg-black text-white rounded-xl hover:opacity-90 font-medium"
          >
            Continue with {selectedMajor.name}
          </button>
        </motion.div>
      )}
    </div>
  );
};

export default MajorSelection;