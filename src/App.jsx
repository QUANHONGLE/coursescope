import React, { useMemo, useState, useEffect } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Header from "./components/Header";
import FilterBar from "./components/FilterBar";
import EligibleCourses from "./components/EligibleCourses";
import PlanSummary from "./components/PlanSummary";
import { CourseDetailModal, GradeDistributionModal } from "./components/Modals";
import OnboardingSection from "./components/OnboardingSection";
import MajorSelection from "./components/MajorSelection";
import DiagnosticPanel from "./components/DiagnosticPanel";

const API_URL = "http://127.0.0.1:5001/api";

export default function App() {
  const [search, setSearch] = useState("");
  const [levelFilters, setLevelFilters] = useState(new Set());
  const [difficultyFilters, setDifficultyFilters] = useState(new Set());
  const [creditsFilters, setCreditsFilters] = useState(new Set());
  const [selected, setSelected] = useState([]);
  const [selectedMajor, setSelectedMajor] = useState(null);
  const [majorConfirmed, setMajorConfirmed] = useState(false);
  const [requiredCourses, setRequiredCourses] = useState([]);
  const [completedCourses, setCompletedCourses] = useState(null);
  const [allCourses, setAllCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [onboardingCollapsed, setOnboardingCollapsed] = useState(false);

  const [detailOpen, setDetailOpen] = useState(false);
  const [gradesOpen, setGradesOpen] = useState(false);
  const [activeCourse, setActiveCourse] = useState(null);

  // Fetch all courses from API on mount
  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/courses`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAllCourses(data);
      console.log("✓ Loaded courses:", data.length);
    } catch (error) {
      console.error("✗ Error fetching courses:", error);
      setAllCourses([]);
    } finally {
      setLoading(false);
    }
  };

  const handleMajorSelect = async (major) => {
    setSelectedMajor(major);
    setMajorConfirmed(true);
    
    // Fetch required courses for this major
    try {
      const response = await fetch(`${API_URL}/majors/${major.id}/requirements`);
      const data = await response.json();
      setRequiredCourses(data.requiredCourses);
      console.log("✓ Loaded major requirements:", data.requiredCourses.length);
    } catch (error) {
      console.error("✗ Error fetching major requirements:", error);
    }
  };

  const handleChangeMajor = () => {
    setMajorConfirmed(false);
    setCompletedCourses(null);
    setOnboardingCollapsed(false);
    setSelected([]);
  };

  const handleOnboardingComplete = (completed) => {
    console.log("📋 Completed courses received:", completed);
    console.log("📋 Type:", completed instanceof Set ? "Set" : Array.isArray(completed) ? "Array" : typeof completed);
    console.log("📋 Size/Length:", completed.size || completed.length);
    console.log("📋 Values:", Array.from(completed));
    setCompletedCourses(completed);
    setOnboardingCollapsed(true);
  };

  const toggleLevel = (lvl) =>
    setLevelFilters((prev) => {
      const n = new Set(prev);
      n.has(lvl) ? n.delete(lvl) : n.add(lvl);
      return n;
    });
    
  const toggleDifficulty = (d) =>
    setDifficultyFilters((prev) => {
      const n = new Set(prev);
      n.has(d) ? n.delete(d) : n.add(d);
      return n;
    });
    
  const toggleCredits = (c) =>
    setCreditsFilters((prev) => {
      const n = new Set(prev);
      n.has(c) ? n.delete(c) : n.add(c);
      return n;
    });
    
  const clearAll = () => {
    setSearch("");
    setLevelFilters(new Set());
    setDifficultyFilters(new Set());
    setCreditsFilters(new Set());
  };

  const filtered = useMemo(() => {
    if (!allCourses.length) return [];
    
    return allCourses.filter((c) => {
      const searchHit = [c.code, c.title, c.description].some((s) =>
        s.toLowerCase().includes(search.toLowerCase())
      );
      const levelHit = levelFilters.size ? levelFilters.has(c.level) : true;
      const diffHit = difficultyFilters.size
        ? difficultyFilters.has(c.difficulty)
        : true;
      const creditsHit = creditsFilters.size
        ? creditsFilters.has(c.credits)
        : true;
      return searchHit && levelHit && diffHit && creditsHit;
    });
  }, [search, levelFilters, difficultyFilters, creditsFilters, allCourses]);

  // Filter eligible courses based on completed prerequisites
  const eligibleCourses = useMemo(() => {
    if (completedCourses === null) return filtered;
    
    // Convert Set to Array for easier comparison
    const completedCodesArray = Array.from(completedCourses);
    
    // Get list of course codes already in the plan
    const selectedCodesArray = selected.map(c => c.code);
    
    console.log("🔍 Filtering eligible courses...");
    console.log("🔍 Completed courses:", completedCodesArray);
    console.log("🔍 Courses in plan:", selectedCodesArray);
    console.log("🔍 Total filtered courses:", filtered.length);
    
    const eligible = filtered.filter((course) => {
      // Skip courses that are already completed
      if (completedCodesArray.includes(course.code)) {
        console.log(`⏭️  Skipping ${course.code} - already completed`);
        return false;
      }
      
      // Skip courses that are already in the plan
      if (selectedCodesArray.includes(course.code)) {
        console.log(`📋 Skipping ${course.code} - already in plan`);
        return false;
      }
      
      // If no prerequisites, course is eligible
      if (!course.prerequisites || course.prerequisites.length === 0) {
        console.log(`✅ ${course.code} - no prerequisites needed`);
        return true;
      }
      
      // Check if all prerequisites are completed
      const allPrereqsMet = course.prerequisites.every((prereq) => 
        completedCodesArray.includes(prereq)
      );
      
      if (allPrereqsMet) {
        console.log(`✅ ${course.code} - all prerequisites met:`, course.prerequisites);
      } else {
        const missingPrereqs = course.prerequisites.filter(p => !completedCodesArray.includes(p));
        console.log(`❌ ${course.code} - missing prerequisites:`, missingPrereqs);
      }
      
      return allPrereqsMet;
    });
    
    console.log("🔍 Eligible courses count:", eligible.length);
    return eligible;
  }, [filtered, completedCourses, selected]);

  const addToPlan = (course) =>
    setSelected((prev) =>
      prev.find((x) => x.id === course.id) ? prev : [...prev, course]
    );
    
  const removeFromPlan = (id) =>
    setSelected((prev) => prev.filter((c) => c.id !== id));

  const openDetail = (c) => {
    setActiveCourse(c);
    setDetailOpen(true);
  };
  
  const openGrades = (c) => {
    setActiveCourse(c);
    setGradesOpen(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <Header onChangeMajor={majorConfirmed ? handleChangeMajor : null} selectedMajor={selectedMajor} />
      
      {loading ? (
        <main className="mx-auto max-w-6xl px-4 py-6 md:py-8">
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
            <p className="mt-4 text-gray-600">Loading courses...</p>
          </div>
        </main>
      ) : allCourses.length === 0 ? (
        <main className="mx-auto max-w-6xl px-4 py-6 md:py-8">
          <div className="text-center py-12 bg-red-50 border border-red-200 rounded-2xl">
            <p className="text-red-800 font-semibold">⚠️ Failed to load courses</p>
            <p className="mt-2 text-red-600 text-sm">Make sure the backend is running on http://localhost:5001</p>
            <button 
              onClick={fetchCourses}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-xl hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        </main>
      ) : !majorConfirmed ? (
        <main className="mx-auto max-w-6xl px-4 py-6 md:py-8">
          <MajorSelection onSelectMajor={handleMajorSelect} selectedMajor={selectedMajor} />
        </main>
      ) : (
        <main className="mx-auto max-w-6xl px-4 py-6 md:py-8 space-y-6">
          <OnboardingSection
            courses={requiredCourses}
            onComplete={handleOnboardingComplete}
            completedCourses={completedCourses}
            isCollapsed={onboardingCollapsed}
            setIsCollapsed={setOnboardingCollapsed}
          />
          
          <AnimatePresence>
            {completedCourses !== null && onboardingCollapsed && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className="space-y-6"
              >
                <FilterBar
                  search={search}
                  setSearch={setSearch}
                  levelFilters={levelFilters}
                  toggleLevel={toggleLevel}
                  difficultyFilters={difficultyFilters}
                  toggleDifficulty={toggleDifficulty}
                  creditsFilters={creditsFilters}
                  toggleCredits={toggleCredits}
                  clearAll={clearAll}
                />

                <div className="grid gap-6 lg:grid-cols-3">
                  <div className="lg:col-span-2 space-y-6">
                    <EligibleCourses
                      courses={eligibleCourses}
                      onAdd={addToPlan}
                      onOpenDetail={openDetail}
                      onOpenGrades={openGrades}
                    />
                  </div>
                  <div className="lg:col-span-1">
                    <div className="bg-white rounded-2xl border shadow-sm p-4 sticky top-[88px]">
                      <PlanSummary selected={selected} onRemove={removeFromPlan} />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </main>
      )}

      <CourseDetailModal
        course={activeCourse}
        open={detailOpen}
        onClose={() => setDetailOpen(false)}
      />
      <GradeDistributionModal
        course={activeCourse}
        open={gradesOpen}
        onClose={() => setGradesOpen(false)}
      />
      
      <DiagnosticPanel 
        completedCourses={completedCourses}
        allCourses={allCourses}
        eligibleCourses={eligibleCourses}
        selectedCourses={selected}
      />
    </div>
  );
}