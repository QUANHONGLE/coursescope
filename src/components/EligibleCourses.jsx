import CourseCard from "./CourseCard";

const EligibleCourses = ({ courses, onAdd, onOpenDetail, onOpenGrades }) => (
  <section className="space-y-3">
    <div className="flex items-center justify-between">
      <h2 className="text-lg font-semibold">Eligible Courses</h2>
      <span className="text-sm text-gray-500">
        {courses.length} result{courses.length !== 1 ? "s" : ""}
      </span>
    </div>
    {courses.length === 0 ? (
      <div className="rounded-xl border bg-white p-6 text-sm text-gray-600">
        No courses match your filters. Try clearing some filters or revising
        your completed courses.
      </div>
    ) : (
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        {courses.map((c) => (
          <CourseCard
            key={c.id}
            course={c}
            onAdd={onAdd}
            onOpenDetail={onOpenDetail}
            onOpenGrades={onOpenGrades}
          />
        ))}
      </div>
    )}
  </section>
);

export default EligibleCourses;