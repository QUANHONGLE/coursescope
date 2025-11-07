import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ModalShell from "./ModalShell";
import { Pill } from "./ui";

const API_URL = "http://127.0.0.1:5001/api";

const highlightCourseCodes = (text) => {
  if (!text) return text;

  // Regex to match course codes like "CS 141", "MATH 180", etc.
  const courseCodeRegex = /\b([A-Z]{2,4})\s+(\d{3})\b/g;

  const parts = [];
  let lastIndex = 0;
  let match;

  while ((match = courseCodeRegex.exec(text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    // Add the course code as a pill
    parts.push(
      <span
        key={match.index}
        className="inline-block px-2 py-0.5 mx-0.5 bg-blue-50 border border-blue-200 rounded-full text-blue-900 font-medium text-xs"
      >
        {match[0]}
      </span>
    );

    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
};

export const CourseDetailModal = ({ course, open, onClose }) => {
  // Get underline color based on course level
  const getUnderlineColor = (level) => {
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

  const customTitle = course ? (
    <div className={`flex items-center gap-2 border-b-2 pb-2 ${getUnderlineColor(course.level)}`}>
      <span className="font-semibold">
        {course.code}
      </span>
      <span className="text-gray-500">—</span>
      <span className="font-semibold">Details</span>
    </div>
  ) : (
    "Course Details"
  );

  return (
    <ModalShell
      open={open}
      onClose={onClose}
      title={customTitle}
    >
      {course && (
        <div className="space-y-4">
        <div className="text-sm text-gray-700 leading-6">
          {highlightCourseCodes(course.description)}
        </div>
        <div className="flex gap-2 text-sm">
          <Pill type="credits" value={course.credits}>
            {course.creditsUndergrad !== undefined && course.creditsGrad !== undefined && course.creditsUndergrad !== course.creditsGrad
              ? `${course.creditsUndergrad}/${course.creditsGrad} Credits`
              : `${course.credits} credit${course.credits !== 1 ? "s" : ""}`
            }
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
          {course.prerequisiteGroups && course.prerequisiteGroups.length > 0 ? (
            <span className="inline-flex flex-wrap gap-1 items-center">
              {course.prerequisiteGroups.map((group, groupIdx) => (
                <span key={groupIdx} className="inline-flex flex-wrap items-center gap-1">
                  {group.length > 1 && <span className="text-gray-500 text-xs">(</span>}
                  {group.map((prereq, prereqIdx) => (
                    <span key={prereqIdx} className="inline-flex items-center gap-1">
                      <span className="px-2 py-0.5 bg-blue-50 border border-blue-200 rounded-full text-blue-900 font-medium text-xs">
                        {prereq}
                      </span>
                      {prereqIdx < group.length - 1 && (
                        <span className="text-gray-500 text-xs">or</span>
                      )}
                    </span>
                  ))}
                  {group.length > 1 && <span className="text-gray-500 text-xs">)</span>}
                  {groupIdx < course.prerequisiteGroups.length - 1 && (
                    <span className="text-gray-700 text-xs font-semibold mx-1">and</span>
                  )}
                </span>
              ))}
            </span>
          ) : (
            "None"
          )}
        </div>
      </div>
    )}
    </ModalShell>
  );
};

const GradeBar = ({ label, percentage, count, color, delay = 0 }) => (
  <div className="flex items-center gap-3">
    <div className="w-8 text-sm font-semibold text-gray-700">{label}</div>
    <div className="flex-1 bg-gray-100 rounded-full h-8 overflow-hidden relative flex items-center">
      <motion.div
        className={`h-full ${color} absolute left-0 top-0`}
        initial={{ width: 0 }}
        animate={{ width: `${Math.max(percentage, 3)}%` }}
        transition={{
          duration: 0.8,
          ease: "easeOut",
          delay: delay
        }}
      />
      <motion.span
        className="absolute right-3 text-black text-xs font-semibold whitespace-nowrap z-10"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{
          duration: 0.3,
          delay: delay + 0.4
        }}
      >
        {percentage}%
      </motion.span>
    </div>
    <motion.div
      className="w-24 text-right text-sm text-gray-600"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{
        duration: 0.3,
        delay: delay + 0.4
      }}
    >
      {count} Student{count !== 1 ? 's' : ''}
    </motion.div>
  </div>
);

export const GradeDistributionModal = ({ course, open, onClose }) => {
  const [gradeData, setGradeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedSemester, setSelectedSemester] = useState("average");
  const [filterMode, setFilterMode] = useState("semester"); // "semester" or "instructor"
  const [showAllInstructors, setShowAllInstructors] = useState(false);

  // Helper function to format instructor name
  const formatInstructorName = (instructor) => {
    if (!instructor || instructor.trim() === '' || instructor.trim() === ',' || instructor === 'null' || instructor === 'undefined') {
      return 'Instructor Not Specified';
    }
    return instructor;
  };

  // Helper function to display instructor list with grouped unspecified and show more/less
  const displayInstructorList = (instructorsList, showAll = false) => {
    const specifiedInstructors = instructorsList.filter(i => i !== 'Instructor Not Specified');
    const unspecifiedCount = instructorsList.length - specifiedInstructors.length;

    const result = [];
    const displayLimit = 10;
    const shouldTruncate = specifiedInstructors.length > displayLimit;
    const instructorsToShow = (showAll || !shouldTruncate) ? specifiedInstructors : specifiedInstructors.slice(0, displayLimit);

    // Add specified instructors
    instructorsToShow.forEach((instructor, idx) => {
      result.push(
        <span key={`specified-${idx}`} className="px-2 py-0.5 bg-gray-100 rounded-full text-gray-700">
          {instructor}
        </span>
      );
    });

    // Add unspecified count if any
    if (unspecifiedCount > 0) {
      result.push(
        <span key="unspecified" className="px-2 py-0.5 bg-gray-100 rounded-full text-gray-600 italic">
          {unspecifiedCount} instructor{unspecifiedCount !== 1 ? 's' : ''} unspecified
        </span>
      );
    }

    return { elements: result, shouldTruncate, totalCount: specifiedInstructors.length };
  };

  useEffect(() => {
    if (open && course) {
      fetchGradeData();
      setShowAllInstructors(false); // Reset when modal opens
    }
  }, [open, course]);

  const fetchGradeData = async () => {
    if (!course) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/courses/${encodeURIComponent(course.code)}/grades`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setGradeData(data);
      
      // Reset to average view when data loads
      setSelectedSemester("average");
    } catch (err) {
      console.error("Error fetching grade data:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getGroupedData = () => {
    if (!gradeData || !gradeData.has_data) return null;

    if (filterMode === "semester") {
      // Group by semester (average multiple instructors if same semester)
      const semesterMap = new Map();

      gradeData.distributions.forEach((dist) => {
        const key = dist.semester;
        if (!semesterMap.has(key)) {
          semesterMap.set(key, []);
        }
        semesterMap.get(key).push(dist);
      });

      const grouped = [];
      semesterMap.forEach((dists, semester) => {
        // Average all distributions for this semester
        const totalA = dists.reduce((sum, d) => sum + d.grades.A, 0);
        const totalB = dists.reduce((sum, d) => sum + d.grades.B, 0);
        const totalC = dists.reduce((sum, d) => sum + d.grades.C, 0);
        const totalD = dists.reduce((sum, d) => sum + d.grades.D, 0);
        const totalF = dists.reduce((sum, d) => sum + d.grades.F, 0);
        const totalW = dists.reduce((sum, d) => sum + d.grades.W, 0);
        const totalS = dists.reduce((sum, d) => sum + d.grades.S, 0);
        const totalU = dists.reduce((sum, d) => sum + d.grades.U, 0);
        const totalStudents = dists.reduce((sum, d) => sum + d.total_students, 0);
        const letterGradeTotal = totalA + totalB + totalC + totalD + totalF;

        grouped.push({
          key: semester,
          label: semester,
          semester: semester,
          instructors: dists.map(d => formatInstructorName(d.instructor)).join(' • '),
          instructorsList: dists.map(d => formatInstructorName(d.instructor)),
          grades: { A: totalA, B: totalB, C: totalC, D: totalD, F: totalF, W: totalW, S: totalS, U: totalU },
          percentages: {
            A: letterGradeTotal > 0 ? Math.round((totalA / letterGradeTotal) * 1000) / 10 : 0,
            B: letterGradeTotal > 0 ? Math.round((totalB / letterGradeTotal) * 1000) / 10 : 0,
            C: letterGradeTotal > 0 ? Math.round((totalC / letterGradeTotal) * 1000) / 10 : 0,
            D: letterGradeTotal > 0 ? Math.round((totalD / letterGradeTotal) * 1000) / 10 : 0,
            F: letterGradeTotal > 0 ? Math.round((totalF / letterGradeTotal) * 1000) / 10 : 0,
            W: totalStudents > 0 ? Math.round((totalW / totalStudents) * 1000) / 10 : 0,
          },
          total_students: totalStudents,
          instructorCount: dists.length
        });
      });

      return grouped;
    } else {
      // Group by instructor (average multiple semesters if same instructor)
      const instructorMap = new Map();

      gradeData.distributions.forEach((dist) => {
        const key = formatInstructorName(dist.instructor);
        if (!instructorMap.has(key)) {
          instructorMap.set(key, []);
        }
        instructorMap.get(key).push(dist);
      });

      const grouped = [];
      instructorMap.forEach((dists, instructor) => {
        // Average all distributions for this instructor
        const totalA = dists.reduce((sum, d) => sum + d.grades.A, 0);
        const totalB = dists.reduce((sum, d) => sum + d.grades.B, 0);
        const totalC = dists.reduce((sum, d) => sum + d.grades.C, 0);
        const totalD = dists.reduce((sum, d) => sum + d.grades.D, 0);
        const totalF = dists.reduce((sum, d) => sum + d.grades.F, 0);
        const totalW = dists.reduce((sum, d) => sum + d.grades.W, 0);
        const totalS = dists.reduce((sum, d) => sum + d.grades.S, 0);
        const totalU = dists.reduce((sum, d) => sum + d.grades.U, 0);
        const totalStudents = dists.reduce((sum, d) => sum + d.total_students, 0);
        const letterGradeTotal = totalA + totalB + totalC + totalD + totalF;

        grouped.push({
          key: instructor,
          label: instructor,
          instructor: instructor,
          semesters: dists.map(d => d.semester).join(' • '),
          semestersList: dists.map(d => d.semester),
          grades: { A: totalA, B: totalB, C: totalC, D: totalD, F: totalF, W: totalW, S: totalS, U: totalU },
          percentages: {
            A: letterGradeTotal > 0 ? Math.round((totalA / letterGradeTotal) * 1000) / 10 : 0,
            B: letterGradeTotal > 0 ? Math.round((totalB / letterGradeTotal) * 1000) / 10 : 0,
            C: letterGradeTotal > 0 ? Math.round((totalC / letterGradeTotal) * 1000) / 10 : 0,
            D: letterGradeTotal > 0 ? Math.round((totalD / letterGradeTotal) * 1000) / 10 : 0,
            F: letterGradeTotal > 0 ? Math.round((totalF / letterGradeTotal) * 1000) / 10 : 0,
            W: totalStudents > 0 ? Math.round((totalW / totalStudents) * 1000) / 10 : 0,
          },
          total_students: totalStudents,
          semesterCount: dists.length
        });
      });

      return grouped;
    }
  };

  const getAllInstructors = () => {
    if (!gradeData || !gradeData.has_data) return [];

    // Get unique instructors from all distributions
    const instructorSet = new Set();
    gradeData.distributions.forEach(dist => {
      instructorSet.add(formatInstructorName(dist.instructor));
    });

    return Array.from(instructorSet).sort();
  };

  const getDisplayData = () => {
    if (!gradeData || !gradeData.has_data) return null;

    if (selectedSemester === "average") {
      return {
        title: "Average Across All Data",
        data: gradeData.average,
        subtitle: `Based on ${gradeData.average.semesters_count} semester${gradeData.average.semesters_count !== 1 ? 's' : ''} (${gradeData.average.total_students} total students)`,
        showAllInstructors: true
      };
    } else {
      const grouped = getGroupedData();
      const item = grouped[selectedSemester];

      if (filterMode === "semester") {
        return {
          title: item.semester,
          data: item,
          subtitle: item.instructorCount > 1
            ? `${item.total_students} students across ${item.instructorCount} instructor${item.instructorCount !== 1 ? 's' : ''}`
            : null,
          singleInstructor: item.instructorCount === 1 ? item.instructors : null,
          totalStudents: item.total_students
        };
      } else {
        return {
          title: item.instructor,
          data: item,
          subtitle: item.semesterCount > 1
            ? `${item.total_students} students across ${item.semesterCount} semester${item.semesterCount !== 1 ? 's' : ''}`
            : null,
          singleSemester: item.semesterCount === 1 ? item.semesters : null,
          totalStudents: item.total_students
        };
      }
    }
  };

  const displayData = getDisplayData();

  // Get underline color based on course level
  const getUnderlineColorForGrades = (level) => {
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

  const customTitle = course ? (
    <div className={`flex items-center gap-2 border-b-2 pb-2 ${getUnderlineColorForGrades(course.level)}`}>
      <span className="font-semibold">
        {course.code}
      </span>
      <span className="text-gray-500">—</span>
      <span className="font-semibold">Grade Distribution</span>
    </div>
  ) : (
    "Grade Distribution"
  );

  return (
    <ModalShell
      open={open}
      onClose={onClose}
      title={customTitle}
    >
      {course && (
        <div className="space-y-4">
          {loading && (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
              <p className="mt-2 text-sm text-gray-600">Loading grade data...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-800">
              <p className="font-semibold">Error loading grade data</p>
              <p className="mt-1">{error}</p>
            </div>
          )}

          {!loading && !error && gradeData && !gradeData.has_data && (
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center">
              <p className="text-gray-700 font-medium">No grade data available</p>
              <p className="text-sm text-gray-600 mt-2">
                Grade distribution data has not been imported for this course yet.
              </p>
            </div>
          )}

          {!loading && !error && gradeData && gradeData.has_data && (
            <>
              {/* Filter Mode Toggle */}
              <div className="flex gap-2 border-b pb-3">
                <button
                  onClick={() => {
                    setFilterMode("semester");
                    setSelectedSemester("average");
                  }}
                  className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filterMode === "semester"
                      ? "bg-black text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  📅 By Semester
                </button>
                <button
                  onClick={() => {
                    setFilterMode("instructor");
                    setSelectedSemester("average");
                  }}
                  className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filterMode === "instructor"
                      ? "bg-black text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                  }`}
                >
                  👤 By Instructor
                </button>
              </div>

              {/* Data Selector */}
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-600">
                  {filterMode === "semester" ? "Select Semester:" : "Select Instructor:"}
                </label>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setSelectedSemester("average")}
                    className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                      selectedSemester === "average"
                        ? "bg-black text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    📊 Overall Average
                  </button>
                  {getGroupedData()?.map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => setSelectedSemester(idx)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        selectedSemester === idx
                          ? "bg-black text-white"
                          : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {item.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Grade Distribution Chart */}
              {displayData && (
                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold text-gray-900">{displayData.title}</h4>
                    {displayData.subtitle && (
                      <p className="text-xs text-gray-600 mt-0.5">{displayData.subtitle}</p>
                    )}
                    {displayData.singleInstructor && (
                      <div className="flex items-center gap-2 mt-1 text-xs">
                        <span className="text-gray-600">{displayData.totalStudents} students</span>
                        <span className="text-gray-400">•</span>
                        <span className="px-2 py-0.5 bg-blue-50 border border-blue-200 rounded-full text-gray-700">
                          {displayData.singleInstructor}
                        </span>
                      </div>
                    )}
                    {displayData.singleSemester && (
                      <div className="flex items-center gap-2 mt-1 text-xs">
                        <span className="text-gray-600">{displayData.totalStudents} students</span>
                        <span className="text-gray-400">•</span>
                        <span className="px-2 py-0.5 bg-purple-50 border border-purple-200 rounded-full text-gray-700">
                          {displayData.singleSemester}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="space-y-2 bg-gray-50 rounded-xl p-4">
                    <GradeBar
                      label="A"
                      percentage={displayData.data.percentages.A}
                      count={displayData.data.grades.A}
                      color="bg-green-500"
                      delay={0}
                    />
                    <GradeBar
                      label="B"
                      percentage={displayData.data.percentages.B}
                      count={displayData.data.grades.B}
                      color="bg-lime-500"
                      delay={0.1}
                    />
                    <GradeBar
                      label="C"
                      percentage={displayData.data.percentages.C}
                      count={displayData.data.grades.C}
                      color="bg-yellow-500"
                      delay={0.2}
                    />
                    <GradeBar
                      label="D"
                      percentage={displayData.data.percentages.D}
                      count={displayData.data.grades.D}
                      color="bg-orange-500"
                      delay={0.3}
                    />
                    <GradeBar
                      label="F"
                      percentage={displayData.data.percentages.F}
                      count={displayData.data.grades.F}
                      color="bg-red-500"
                      delay={0.4}
                    />
                    {displayData.data.grades.W > 0 && (
                      <GradeBar
                        label="W"
                        percentage={displayData.data.percentages.W}
                        count={displayData.data.grades.W}
                        color="bg-gray-400"
                        delay={0.5}
                      />
                    )}
                  </div>

                  {/* Summary Stats */}
                  <div className="flex gap-2 flex-wrap">
                    <Pill>
                      A/B Rate: {(displayData.data.percentages.A + displayData.data.percentages.B).toFixed(1)}%
                    </Pill>
                    <Pill>
                      Pass Rate: {(100 - displayData.data.percentages.F - displayData.data.percentages.W).toFixed(1)}%
                    </Pill>
                    {displayData.data.grades.W > 0 && (
                      <Pill>
                        Withdrawal: {displayData.data.percentages.W}%
                      </Pill>
                    )}
                  </div>

                  {/* Show additional info for grouped data and overall average */}
                  <motion.div
                    className="overflow-hidden"
                    initial={false}
                    animate={{
                      height: (selectedSemester === "average" && displayData?.showAllInstructors) ||
                              (selectedSemester !== "average" &&
                               ((filterMode === "semester" && getGroupedData()[selectedSemester]?.instructorCount > 1) ||
                                (filterMode === "instructor" && getGroupedData()[selectedSemester]?.semesterCount > 1)))
                        ? "auto"
                        : 0
                    }}
                    transition={{
                      duration: 0.4,
                      ease: [0.4, 0.0, 0.2, 1],
                      delay: (selectedSemester === "average" && displayData?.showAllInstructors) ||
                             (selectedSemester !== "average" &&
                              ((filterMode === "semester" && getGroupedData()[selectedSemester]?.instructorCount > 1) ||
                               (filterMode === "instructor" && getGroupedData()[selectedSemester]?.semesterCount > 1)))
                        ? 0
                        : 0.2
                    }}
                  >
                    <div className="text-xs text-gray-600 pt-2 border-t">
                      <div className="pb-2">
                        <AnimatePresence mode="wait">
                          {selectedSemester === "average" && displayData?.showAllInstructors && (
                            <motion.div
                              key="all-instructors"
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              exit={{ opacity: 0 }}
                              transition={{ duration: 0.2 }}
                            >
                              <div className="flex flex-wrap gap-2 items-center">
                                <span className="font-medium text-gray-700">All Instructors:</span>
                                {(() => {
                                  const instructorList = getAllInstructors();
                                  const { elements, shouldTruncate, totalCount } = displayInstructorList(instructorList, showAllInstructors);
                                  return (
                                    <>
                                      {elements}
                                      {shouldTruncate && (
                                        <button
                                          onClick={() => setShowAllInstructors(!showAllInstructors)}
                                          className="px-2 py-0.5 bg-blue-100 hover:bg-blue-200 rounded-full text-blue-700 font-medium transition-colors"
                                        >
                                          {showAllInstructors ? 'Show Less' : `Show ${totalCount - 10} More`}
                                        </button>
                                      )}
                                    </>
                                  );
                                })()}
                              </div>
                            </motion.div>
                          )}
                          {selectedSemester !== "average" && filterMode === "semester" && getGroupedData()[selectedSemester]?.instructorCount > 1 && (
                            <motion.div
                              key={`instructors-${selectedSemester}`}
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              exit={{ opacity: 0 }}
                              transition={{ duration: 0.2 }}
                            >
                              <div className="flex flex-wrap gap-2 items-center">
                                <span className="font-medium text-gray-700">Instructors:</span>
                                {(() => {
                                  const instructorList = getGroupedData()[selectedSemester].instructorsList;
                                  const { elements, shouldTruncate, totalCount } = displayInstructorList(instructorList, showAllInstructors);
                                  return (
                                    <>
                                      {elements}
                                      {shouldTruncate && (
                                        <button
                                          onClick={() => setShowAllInstructors(!showAllInstructors)}
                                          className="px-2 py-0.5 bg-blue-100 hover:bg-blue-200 rounded-full text-blue-700 font-medium transition-colors"
                                        >
                                          {showAllInstructors ? 'Show Less' : `Show ${totalCount - 10} More`}
                                        </button>
                                      )}
                                    </>
                                  );
                                })()}
                              </div>
                            </motion.div>
                          )}
                          {selectedSemester !== "average" && filterMode === "instructor" && getGroupedData()[selectedSemester]?.semesterCount > 1 && (
                            <motion.div
                              key={`semesters-${selectedSemester}`}
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              exit={{ opacity: 0 }}
                              transition={{ duration: 0.2 }}
                            >
                              <div className="flex flex-wrap gap-2 items-center">
                                <span className="font-medium text-gray-700">Semesters:</span>
                                {getGroupedData()[selectedSemester].semestersList.map((semester, idx) => (
                                  <span key={idx} className="px-2 py-0.5 bg-gray-100 rounded-full text-gray-700">
                                    {semester}
                                  </span>
                                ))}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  </motion.div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </ModalShell>
  );
};