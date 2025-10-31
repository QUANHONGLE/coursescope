const Header = ({ onChangeMajor, selectedMajor }) => (
  <header className="sticky top-0 z-40 bg-white/80 backdrop-blur border-b">
    <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <div className="h-8 w-8 rounded-2xl bg-black text-white grid place-items-center text-xs">
          CS
        </div>
        <h1 className="text-lg font-semibold tracking-tight">CourseScope</h1>
      </div>
      <div className="flex items-center gap-4">
        {selectedMajor && (
          <div className="text-xs text-gray-600">
            {selectedMajor.name} · {selectedMajor.concentration}
          </div>
        )}
        {onChangeMajor && (
          <button
            onClick={onChangeMajor}
            className="text-xs text-gray-500 hover:text-black underline"
          >
            Change Major
          </button>
        )}
        <span className="text-xs text-gray-500">MVP · Unified course planning</span>
      </div>
    </div>
  </header>
);

export default Header;