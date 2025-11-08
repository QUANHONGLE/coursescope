import { Chip, Pill } from "./ui";

const LEVELS = [100, 200, 300, 400];
const DIFFICULTIES = ["Light", "Moderate", "Challenging"];
const CREDITS = [0, 1, 2, 3, 4];
const DIFFICULTY_INFO = {
  Light: {
    label: "Light",
    desc: "Higher historic A/B rates, lighter expected workload.",
  },
  Moderate: {
    label: "Moderate",
    desc: "Balanced grade trends, steady weekly effort.",
  },
  Challenging: {
    label: "Challenging",
    desc: "Lower A-rate and/or heavier weekly workload.",
  },
};

const FilterBar = ({
  search,
  setSearch,
  levelFilters,
  toggleLevel,
  difficultyFilters,
  toggleDifficulty,
  creditsFilters,
  toggleCredits,
  clearAll,
}) => {
  const anyActive = !!(search || levelFilters.size || difficultyFilters.size || creditsFilters.size);
  
  return (
    <div className="bg-white rounded-2xl border shadow-sm p-3 md:p-4">
      <div className="grid gap-3 md:grid-cols-4">
        <div className="col-span-1">
          <label className="text-xs font-medium text-gray-600">Search</label>
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by code, title, or keyword…"
            className="mt-1 w-full rounded-xl border px-3 py-2 outline-none focus:ring-2 focus:ring-black"
          />
        </div>
        <div className="col-span-1">
          <label className="text-xs font-medium text-gray-600">Credit Hours</label>
          <div className="mt-1 flex flex-wrap gap-2">
            {CREDITS.map((c) => (
              <Chip
                key={c}
                type="credits"
                active={creditsFilters.has(c)}
                onClick={() => toggleCredits(c)}
                title={`Filter by ${c} hour${c !== 1 ? 's' : ''}`}
              >
                {c} hour{c !== 1 ? 's' : ''}
              </Chip>
            ))}
          </div>
        </div>
        <div className="col-span-1">
          <label className="text-xs font-medium text-gray-600">Course Level</label>
          <div className="mt-1 flex flex-wrap gap-2">
            {LEVELS.map((L) => (
              <Chip
                key={L}
                type="level"
                active={levelFilters.has(L)}
                onClick={() => toggleLevel(L)}
                title={`Filter level ${L}`}
              >
                {L}-level
              </Chip>
            ))}
          </div>
        </div>
        <div className="col-span-1">
          <label className="text-xs font-medium text-gray-600">
            Course Work Load
          </label>
          <div className="mt-1 flex flex-wrap gap-2">
            {DIFFICULTIES.map((d) => (
              <Chip
                key={d}
                type="difficulty"
                active={difficultyFilters.has(d)}
                onClick={() => toggleDifficulty(d)}
                title={DIFFICULTY_INFO[d]?.desc}
              >
                {d}
              </Chip>
            ))}
          </div>
        </div>
      </div>
      {anyActive && (
        <div className="pt-3 flex items-center justify-between">
          <div className="flex flex-wrap gap-2 text-xs">
            {search && <Pill>Search: "{search}"</Pill>}
            {[...creditsFilters].map((c) => (
              <Pill key={c}>{c} Hour{c !== 1 ? 's' : ''}</Pill>
            ))}
            {[...levelFilters].map((L) => (
              <Pill key={L}>Level {L}</Pill>
            ))}
            {[...difficultyFilters].map((d) => (
              <Pill key={d}>Difficulty: {d}</Pill>
            ))}
          </div>
          <button
            onClick={clearAll}
            className="text-sm underline text-gray-600 hover:text-black"
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
};

export default FilterBar;