import { useState } from "react";
import CourseCard from "./CourseCard";
import { ChevronDown, ChevronRight } from "lucide-react";

const EligibleCourses = ({ courses, allCourses, requiredCourses, electiveCourses, onAdd, onOpenDetail, onOpenGrades }) => {
  const [requiredExpanded, setRequiredExpanded] = useState(false);
  const [electivesExpanded, setElectivesExpanded] = useState(false);
  const [otherExpanded, setOtherExpanded] = useState(false);

  // Create sets of course codes for quick lookup
  const requiredCourseCodes = new Set(requiredCourses.map(c => c.code));
  const electiveCourseCodes = new Set(electiveCourses.map(c => c.code));

  const getCourseType = (courseCode) => {
    if (requiredCourseCodes.has(courseCode)) return 'required';
    if (electiveCourseCodes.has(courseCode)) return 'elective';
    return null;
  };

  // Categorize courses into three groups
  const eligibleRequired = courses.filter(c => requiredCourseCodes.has(c.code));
  const eligibleElectives = courses.filter(c => electiveCourseCodes.has(c.code));
  // Use all available courses for the third section (not filtered by prerequisites)
  const allAvailableCourses = allCourses || [];

  const renderSection = (title, courses, expanded, setExpanded) => {
    if (courses.length === 0) return null;

    return (
      <div className="rounded-xl border bg-white shadow-sm overflow-hidden">
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center gap-2">
            {expanded ? (
              <ChevronDown className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-500" />
            )}
            <h3 className="text-lg font-semibold">{title}</h3>
            <span className="text-sm text-gray-500">
              ({courses.length} course{courses.length !== 1 ? "s" : ""})
            </span>
          </div>
        </button>

        {expanded && (
          <div className="p-4 pt-0 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {courses.map((c) => (
              <CourseCard
                key={c.id}
                course={c}
                courseType={getCourseType(c.code)}
                onAdd={onAdd}
                onOpenDetail={onOpenDetail}
                onOpenGrades={onOpenGrades}
              />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Eligible Courses</h2>
        <span className="text-sm text-gray-500">
          {courses.length} total result{courses.length !== 1 ? "s" : ""}
        </span>
      </div>

      {courses.length === 0 ? (
        <div className="rounded-xl border bg-white p-6 text-sm text-gray-600">
          No courses match your filters. Try clearing some filters or revising
          your completed courses.
        </div>
      ) : (
        <div className="space-y-3">
          {renderSection("Eligible Required Courses", eligibleRequired, requiredExpanded, setRequiredExpanded)}
          {renderSection("Eligible Electives", eligibleElectives, electivesExpanded, setElectivesExpanded)}
          {renderSection("All Available Courses", allAvailableCourses, otherExpanded, setOtherExpanded)}
        </div>
      )}
    </section>
  );
};

export default EligibleCourses;
