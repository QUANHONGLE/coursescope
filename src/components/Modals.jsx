import ModalShell from "./ModalShell";
import { Pill } from "./ui";

export const CourseDetailModal = ({ course, open, onClose }) => (
  <ModalShell
    open={open}
    onClose={onClose}
    title={course ? `${course.code} — Details` : "Course Details"}
  >
    {course && (
      <div className="space-y-4">
        <div className="text-sm text-gray-700 leading-6">
          {course.description}
        </div>
        <div className="flex gap-2 text-sm">
          <Pill type="credits" value={course.credits}>
            {course.credits} credit{course.credits !== 1 ? "s" : ""}
          </Pill>
          <Pill type="level" value={course.level}>
            Level {course.level}
          </Pill>
          <Pill type="difficulty" value={course.difficulty}>
            {course.difficulty}
          </Pill>
        </div>
        <div className="text-sm">
          <span className="font-medium">Prerequisites:</span>{" "}
          {course.prereqChain || "See catalog"}
        </div>
      </div>
    )}
  </ModalShell>
);

export const GradeDistributionModal = ({ course, open, onClose }) => (
  <ModalShell
    open={open}
    onClose={onClose}
    title={
      course ? `${course.code} — Grade Distribution` : "Grade Distribution"
    }
  >
    {course && (
      <div className="space-y-4">
        <p className="text-sm text-gray-700">
          Demo chart placeholder. Show A—F bars by semester + instructors.
        </p>
        <div className="flex flex-wrap gap-2">
          {(course.instructors || []).map((n) => (
            <Pill key={n}>Instructor: {n}</Pill>
          ))}
        </div>
        <div className="h-40 w-full rounded-xl border border-dashed grid place-items-center text-sm text-gray-500">
          A—F stacked bars here
        </div>
      </div>
    )}
  </ModalShell>
);