import { motion } from "framer-motion";

const MajorSelection = ({ onSelectMajor, selectedMajor }) => {
  const majors = [
    {
      id: 1,
      name: "Computer Science",
      concentration: "Software Engineering",
      description: "Focus on software development, design patterns, and engineering practices.",
      color: "blue"
    }
    // More majors can be added here later
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">Choose Your Major</h1>
        <p className="text-gray-600">
          Select your major and concentration to see your course requirements
        </p>
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
            <p className="text-sm text-gray-600 mb-2">{major.concentration}</p>
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