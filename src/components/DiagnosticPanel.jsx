import { useState, useEffect } from "react";

const DiagnosticPanel = ({ completedCourses, allCourses, eligibleCourses, selectedCourses }) => {
  const [isOpen, setIsOpen] = useState(false);

  if (!completedCourses) return null;

  const completedArray = Array.from(completedCourses);
  const selectedArray = selectedCourses || [];
  
  // Find courses that should be eligible based on completed courses
  const coursesWithPrereqs = allCourses.filter(c => 
    c.prerequisites && c.prerequisites.length > 0
  );

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-4 py-2 bg-purple-600 text-white rounded-xl shadow-lg hover:bg-purple-700"
      >
        🔍 Debug Info {isOpen ? "▼" : "▲"}
      </button>
      
      {isOpen && (
        <div className="mt-2 w-96 max-h-96 overflow-y-auto bg-white border-2 border-purple-600 rounded-xl shadow-xl p-4 text-sm">
          <h3 className="font-bold mb-2">Diagnostic Information</h3>
          
          <div className="mb-3 p-2 bg-blue-50 rounded">
            <strong>Completed Courses ({completedArray.length}):</strong>
            <div className="text-xs mt-1 space-y-1">
              {completedArray.map(code => (
                <div key={code} className="text-blue-700">• {code}</div>
              ))}
            </div>
          </div>

          <div className="mb-3 p-2 bg-purple-50 rounded">
            <strong>Courses in Plan ({selectedArray.length}):</strong>
            <div className="text-xs mt-1 space-y-1">
              {selectedArray.length === 0 ? (
                <div className="text-gray-500 italic">No courses in plan yet</div>
              ) : (
                selectedArray.map(course => (
                  <div key={course.code} className="text-purple-700">
                    • {course.code}: {course.title}
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mb-3 p-2 bg-green-50 rounded">
            <strong>Eligible Courses ({eligibleCourses.length}):</strong>
            <div className="text-xs mt-1 space-y-1">
              {eligibleCourses.slice(0, 10).map(course => (
                <div key={course.code} className="text-green-700">
                  • {course.code}: {course.title}
                  {course.prerequisites?.length > 0 && (
                    <div className="ml-4 text-gray-600">
                      Prereqs: {course.prerequisites.join(", ")}
                    </div>
                  )}
                </div>
              ))}
              {eligibleCourses.length > 10 && (
                <div className="text-gray-500">... and {eligibleCourses.length - 10} more</div>
              )}
            </div>
          </div>

          <div className="mb-3 p-2 bg-red-50 rounded">
            <strong>Blocked Courses (missing prereqs):</strong>
            <div className="text-xs mt-1 space-y-1 max-h-40 overflow-y-auto">
              {coursesWithPrereqs
                .filter(course => {
                  if (completedArray.includes(course.code)) return false;
                  if (selectedArray.some(s => s.code === course.code)) return false;
                  return !course.prerequisites.every(p => completedArray.includes(p));
                })
                .slice(0, 10)
                .map(course => {
                  const missing = course.prerequisites.filter(p => !completedArray.includes(p));
                  return (
                    <div key={course.code} className="text-red-700">
                      • {course.code}: {course.title}
                      <div className="ml-4 text-gray-600">
                        Missing: {missing.join(", ")}
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>

          <div className="text-xs text-gray-500 mt-2 pt-2 border-t">
            Total courses: {allCourses.length} | 
            With prereqs: {coursesWithPrereqs.length}
          </div>
        </div>
      )}
    </div>
  );
};

export default DiagnosticPanel;