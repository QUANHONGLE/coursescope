import { useMemo } from "react";
import { Pill } from "./ui";
import { motion, AnimatePresence } from "framer-motion";

const PlanSummary = ({ selected, onRemove }) => {
  const totalCredits = useMemo(
    () => selected.reduce((sum, c) => sum + c.credits, 0),
    [selected]
  );
  
  const workload = useMemo(() => {
    const counts = { Easy: 0, Moderate: 0, Challenging: 0 };
    selected.forEach((c) => counts[c.difficulty]++);
    return `${counts.Challenging} challenging / ${counts.Moderate} moderate / ${counts.Easy} easy`;
  }, [selected]);

  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-lg font-semibold">Plan Summary</h2>
        <div className="mt-2 flex flex-wrap gap-2">
          <Pill>Total Credits: {totalCredits}</Pill>
          <Pill>Balance: {workload}</Pill>
        </div>
      </div>
      {selected.length === 0 ? (
        <div className="rounded-xl border bg-white p-6 text-sm text-gray-600">
          Your plan is empty. Add courses from the Eligible list to see them
          here.
        </div>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          <AnimatePresence mode="popLayout">
            {selected.map((c) => (
              <motion.div
                key={c.id}
                layout
                initial={{ opacity: 0, scale: 0.8, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.8, y: -20 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                className="rounded-2xl border bg-white p-4 flex flex-col gap-2 relative"
              >
                <div>
                  <div className="text-sm text-gray-500">{c.code}</div>
                  <div className="font-medium">{c.title}</div>
                  <div className="flex flex-wrap gap-1 mt-2">
                    <Pill type="credits" value={c.credits}>
                      {c.credits} cr
                    </Pill>
                    <Pill type="level" value={c.level}>
                      Level {c.level}
                    </Pill>
                    <Pill type="difficulty" value={c.difficulty}>
                      {c.difficulty}
                    </Pill>
                  </div>
                </div>
                <button
                  className="text-sm underline hover:text-black self-end mt-auto"
                  onClick={() => onRemove(c.id)}
                >
                  Remove
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </section>
  );
};

export default PlanSummary;