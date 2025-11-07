import { motion } from "framer-motion";
import { Pill } from "./ui";
import { useState } from "react";

const CourseCard = ({ course, courseType, onAdd, onOpenDetail, onOpenGrades }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isGradeHovered, setIsGradeHovered] = useState(false);
  const [isDetailHovered, setIsDetailHovered] = useState(false);

  // Get underline color based on course level
  const getUnderlineColor = () => {
    const level = course.level;
    if (level <= 100) {
      return "border-green-300";
    } else if (level === 200) {
      return "border-lime-300";
    } else if (level === 300) {
      return "border-yellow-300";
    } else if (level >= 400) {
      return "border-red-300";
    }
    return "border-gray-300"; // fallback
  };

  // Get background color based on course type
  const getBackgroundColor = () => {
    return 'bg-white';
  };

  return (
    <motion.div
      layout
      className={`rounded-2xl border ${getBackgroundColor()} p-4 shadow-sm flex flex-col gap-3 relative h-full`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="space-y-2">
        <div>
          <h3 className={`text-lg font-bold leading-tight pb-1 border-b-2 ${getUnderlineColor()}`}>
            {course.code}
          </h3>
          <div className="text-sm text-gray-600 mt-1.5">
            {course.title}
          </div>
        </div>
        <div className="flex flex-wrap gap-2">
          <Pill type="credits" value={course.credits}>
            {course.creditsUndergrad !== undefined && course.creditsGrad !== undefined && course.creditsUndergrad !== course.creditsGrad
              ? `${course.creditsUndergrad}/${course.creditsGrad} Credits`
              : `${course.credits} Credit${course.credits !== 1 ? "s" : ""}`
            }
          </Pill>
          <Pill type="level" value={course.level}>
            Level {course.level}
          </Pill>
          <Pill type="difficulty" value={course.difficulty}>
            {course.difficulty}
          </Pill>
        </div>
      </div>
      <div className="flex flex-col gap-2 pt-1 mt-auto">
        <motion.button
          className="px-3 py-2 rounded-xl border hover:bg-gray-50 text-left flex items-center justify-between overflow-hidden relative"
          onClick={() => onOpenGrades(course)}
          onHoverStart={() => setIsGradeHovered(true)}
          onHoverEnd={() => setIsGradeHovered(false)}
        >
          <span>Grade Distribution</span>
          <div className="flex items-end gap-0.5 h-4">
            {[
              { color: 'bg-green-500', height: 'h-3' },
              { color: 'bg-lime-500', height: 'h-3.5' },
              { color: 'bg-yellow-500', height: 'h-2.5' },
              { color: 'bg-red-500', height: 'h-2' },
              { color: 'bg-gray-400', height: 'h-1' }
            ].map((bar, index) => (
              <motion.div
                key={index}
                className={`w-1.5 ${bar.color} ${bar.height} rounded-sm`}
                initial={{ x: -20, opacity: 0 }}
                animate={{
                  x: isGradeHovered ? 0 : -20,
                  opacity: isGradeHovered ? 1 : 0
                }}
                transition={{
                  duration: 0.3,
                  ease: "easeOut",
                  delay: isGradeHovered ? index * 0.05 : 0
                }}
              />
            ))}
          </div>
          
        </motion.button>
        <motion.button
          className="px-3 py-2 rounded-xl border hover:bg-gray-50 text-left flex items-center justify-between overflow-hidden"
          onClick={() => onOpenDetail(course)}
          onHoverStart={() => setIsDetailHovered(true)}
          onHoverEnd={() => setIsDetailHovered(false)}
        >
          <span>Course Detail</span>
          <motion.div
            className="flex flex-col gap-0.5"
            initial={{ x: -20, opacity: 0 }}
            animate={{
              x: isDetailHovered ? 0 : -20,
              opacity: isDetailHovered ? 1 : 0
            }}
            transition={{
              duration: 0.3,
              ease: "easeOut"
            }}
          >
            <div className="w-4 h-[2px] bg-gray-700 rounded-full"></div>
            <div className="w-3 h-[2px] bg-gray-500 rounded-full"></div>
            <div className="w-3.5 h-[2px] bg-gray-400 rounded-full"></div>
          </motion.div>
        </motion.button>
        <motion.button
          className="bg-black text-white rounded-xl flex items-center justify-center overflow-hidden"
          onHoverStart={() => setIsHovered(true)}
          onHoverEnd={() => setIsHovered(false)}
          onClick={() => onAdd(course)}
          animate={{
            paddingLeft: "16px",
            paddingRight: "16px",
            paddingTop: "8px",
            paddingBottom: "8px",
          }}
          transition={{ duration: 0.2, ease: "easeInOut" }}
        >
          <motion.span 
            className="flex items-center justify-center gap-2"
            animate={{
              gap: isHovered ? "8px" : "0px"
            }}
          >
            <span className="text-lg">+</span>
            <motion.span
              initial={{ width: 0, opacity: 0 }}
              animate={{ 
                width: isHovered ? "auto" : 0,
                opacity: isHovered ? 1 : 0
              }}
              className="text-sm font-medium overflow-hidden whitespace-nowrap"
            >
              Add to Plan
            </motion.span>
          </motion.span>
        </motion.button>
      </div>
    </motion.div>
  );
};

export default CourseCard;