import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const OnboardingSection = ({ courses = [], onComplete, completedCourses, isCollapsed: externalCollapsed, setIsCollapsed: setExternalCollapsed }) => {
  const [completed, setCompleted] = useState(completedCourses || new Set());
  const isCollapsed = externalCollapsed ?? (completedCourses !== null);

  const toggleCourse = (courseCode) => {
    setCompleted((prev) => {
      const n = new Set(prev);
      n.has(courseCode) ? n.delete(courseCode) : n.add(courseCode);
      return n;
    });
  };

  const handleConfirm = () => {
    onComplete(completed);
    if (setExternalCollapsed) setExternalCollapsed(true);
  };

  const handleEdit = () => {
    if (setExternalCollapsed) setExternalCollapsed(false);
  };

  return (
    <motion.div 
      className="bg-white rounded-2xl border shadow-sm overflow-hidden"
      layout
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      <motion.div layout className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">
              {isCollapsed ? "Completed Courses" : "Select Completed Courses"}
            </h2>
            <AnimatePresence mode="wait">
              {isCollapsed ? (
                <motion.p
                  key="collapsed"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                  className="text-sm text-gray-600 mt-1"
                >
                  {completed.size} course{completed.size !== 1 ? "s" : ""} completed
                </motion.p>
              ) : (
                <motion.p
                  key="expanded"
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.2 }}
                  className="text-sm text-gray-600 mt-1"
                >
                  Choose all courses you've already completed to see which courses you're eligible for.
                </motion.p>
              )}
            </AnimatePresence>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={isCollapsed ? handleEdit : handleConfirm}
            className="px-4 py-2 bg-black text-white rounded-xl hover:opacity-90"
          >
            {isCollapsed ? "Edit" : "Confirm"}
          </motion.button>
        </div>

        <AnimatePresence>
          {!isCollapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="overflow-hidden"
            >
              <div className="mt-4 space-y-4">
                <div className="max-h-96 overflow-y-auto space-y-2 p-2 border rounded-xl">
                  {courses
                    .sort((a, b) => {
                      // Extract numbers from course codes (e.g., "CS 141" -> 141)
                      const numA = parseInt(a.code.match(/\d+/)?.[0] || '0');
                      const numB = parseInt(b.code.match(/\d+/)?.[0] || '0');
                      return numA - numB;
                    })
                    .map((course) => (
                    <motion.label
                      key={course.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.2 }}
                      className="flex items-start gap-3 p-3 rounded-xl border hover:bg-gray-50 cursor-pointer transition"
                    >
                      <input
                        type="checkbox"
                        checked={completed.has(course.code)}
                        onChange={() => toggleCourse(course.code)}
                        className="mt-1 h-4 w-4 rounded border-gray-300"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{course.code}</span>
                          <span className="text-sm text-gray-500">•</span>
                          <span className="text-sm">{course.title}</span>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {course.credits} credits · Level {course.level}
                        </div>
                      </div>
                    </motion.label>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-2 border-t">
                  <span className="text-sm text-gray-600">
                    {completed.size} course{completed.size !== 1 ? "s" : ""} selected
                  </span>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
};

export default OnboardingSection;