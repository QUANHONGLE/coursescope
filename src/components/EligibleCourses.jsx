import { useState, useMemo } from "react";
import CourseCard from "./CourseCard";
import { ChevronDown, ChevronRight } from "lucide-react";

const EligibleCourses = ({ courses, allCourses, requiredCourses, electiveCourses, onAdd, onOpenDetail, onOpenGrades, skippedPlanning = false }) => {
  const [requiredExpanded, setRequiredExpanded] = useState(false);
  const [electivesExpanded, setElectivesExpanded] = useState(false);
  const [otherExpanded, setOtherExpanded] = useState(false);
  const [showAllOther, setShowAllOther] = useState(false);

  // Create sets of course codes for quick lookup
  const requiredCourseCodes = new Set(requiredCourses.map(c => c.code));
  const electiveCourseCodes = new Set(electiveCourses.map(c => c.code));

  const getCourseType = (courseCode) => {
    if (requiredCourseCodes.has(courseCode)) return 'required';
    if (electiveCourseCodes.has(courseCode)) return 'elective';
    return null;
  };

  // Categorize courses into three groups - memoize to avoid recalculation
  const eligibleRequired = useMemo(() =>
    courses.filter(c => requiredCourseCodes.has(c.code)),
    [courses, requiredCourseCodes]
  );

  const eligibleElectives = useMemo(() =>
    courses.filter(c => electiveCourseCodes.has(c.code)),
    [courses, electiveCourseCodes]
  );

  // Use all available courses for the third section (not filtered by prerequisites)
  const allAvailableCourses = allCourses || [];

  // Limit initial render for performance, show more on demand
  const INITIAL_LIMIT = 50;

  const renderSection = (title, courses, expanded, setExpanded, allowPagination = false) => {
    if (courses.length === 0) return null;

    const shouldLimit = allowPagination && !showAllOther && courses.length > INITIAL_LIMIT;
    const displayedCourses = shouldLimit ? courses.slice(0, INITIAL_LIMIT) : courses;

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
          <>
            <div className="p-4 pt-0 grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {displayedCourses.map((c) => (
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
            {shouldLimit && (
              <div className="p-4 pt-0 text-center">
                <button
                  onClick={() => setShowAllOther(true)}
                  className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-xl text-sm font-medium transition-colors"
                >
                  Show {courses.length - INITIAL_LIMIT} more courses
                </button>
              </div>
            )}
          </>
        )}
      </div>
    );
  };

  return (
    <section className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">
          {skippedPlanning ? "All Courses" : "Eligible Courses"}
        </h2>
        <span className="text-sm text-gray-500">
          {allAvailableCourses.length} total result{allAvailableCourses.length !== 1 ? "s" : ""}
        </span>
      </div>

      {allAvailableCourses.length === 0 ? (
        <div className="rounded-xl border bg-white p-6 text-sm text-gray-600">
          No courses match your filters. Try clearing some filters.
        </div>
      ) : (
        <div className="space-y-3">
          {!skippedPlanning && renderSection("Eligible Required Courses", eligibleRequired, requiredExpanded, setRequiredExpanded, false)}
          {!skippedPlanning && renderSection("Eligible Electives", eligibleElectives, electivesExpanded, setElectivesExpanded, false)}
          {renderSection(skippedPlanning ? "All Courses" : "All Available Courses", allAvailableCourses, otherExpanded, setOtherExpanded, true)}
        </div>
      )}
    </section>
  );
};

export default EligibleCourses;
