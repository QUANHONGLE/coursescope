import { motion } from "framer-motion";
import { Pill } from "./ui";
import { useState } from "react";

const CourseCard = ({ course, onAdd, onOpenDetail, onOpenGrades }) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isGradeHovered, setIsGradeHovered] = useState(false);

  return (
    <motion.div
      layout
      className="rounded-2xl border bg-white p-4 shadow-sm flex flex-col gap-3 relative h-full"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="space-y-2">
        <div>
          <div className="text-sm text-gray-500">{course.code}</div>
          <h3 className="text-base font-semibold leading-tight">
            {course.title}
          </h3>
        </div>
        <div className="flex flex-wrap gap-2">
          <Pill type="credits" value={course.credits}>
            {course.credits} Credit{course.credits !== 1 ? "s" : ""}
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
          <motion.div
            className="flex items-end gap-0.5 h-4"
            initial={{ x: 20, opacity: 0 }}
            animate={{ 
              x: isGradeHovered ? 0 : 20,
              opacity: isGradeHovered ? 1 : 0
            }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            <div className="w-1.5 bg-green-500 h-3 rounded-sm"></div>
            <div className="w-1.5 bg-lime-500 h-3.5 rounded-sm"></div>
            <div className="w-1.5 bg-yellow-500 h-2.5 rounded-sm"></div>
            <div className="w-1.5 bg-red-500 h-2 rounded-sm"></div>
            <div className="w-1.5 bg-gray-400 h-1 rounded-sm"></div>
          </motion.div>
          
        </motion.button>
        <button
          className="px-3 py-2 rounded-xl border hover:bg-gray-50 text-left"
          onClick={() => onOpenDetail(course)}
        >
          Course Detail
        </button>
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