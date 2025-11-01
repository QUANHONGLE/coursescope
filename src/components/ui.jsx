import clsx from "clsx";

export const Pill = ({ children, type = "default", value }) => {
  const getColorClasses = () => {
    // For difficulty pills (or course load)
    if (type === "difficulty") {
      const difficulty = value || children;
      if (typeof difficulty === 'string') {
        if (difficulty.includes("Light") || difficulty.includes("Light")) {
          return "bg-green-100 border-green-300 text-green-800";
        } else if (difficulty.includes("Moderate")) {
          return "bg-yellow-100 border-yellow-300 text-yellow-800";
        } else if (difficulty.includes("Challenging") || difficulty.includes("Heavy")) {
          return "bg-red-100 border-red-300 text-red-800";
        }
      }
    }
    
    // For level pills (gradient from green to red based on level)
    if (type === "level") {
      const levelValue = value || children;
      // Extract number from "Level 100" or just "100"
      const levelMatch = String(levelValue).match(/\d+/);
      const level = levelMatch ? parseInt(levelMatch[0]) : null;
      
      if (level !== null) {
        if (level <= 100) {
          return "bg-green-100 border-green-300 text-green-800";
        } else if (level === 200) {
          return "bg-lime-100 border-lime-300 text-lime-800";
        } else if (level === 300) {
          return "bg-yellow-100 border-yellow-300 text-yellow-800";
        } else if (level >= 400) {
          return "bg-red-100 border-red-300 text-red-800";
        }
      }
    }
    
    // For credits pills (1 credit = green, 4+ credits = red)
    if (type === "credits") {
      const creditsValue = value || children;
      // Extract number from "3 Credits" or just "3"
      const creditsMatch = String(creditsValue).match(/\d+/);
      const credits = creditsMatch ? parseInt(creditsMatch[0]) : null;
      
      if (credits !== null) {
        if (credits === 1) {
          return "bg-green-100 border-green-300 text-green-800";
        } else if (credits === 2) {
          return "bg-lime-100 border-lime-300 text-lime-800";
        } else if (credits === 3) {
          return "bg-yellow-100 border-yellow-300 text-yellow-800";
        } else if (credits >= 4) {
          return "bg-red-100 border-red-300 text-red-800";
        }
      }
    }
    
    // Default gray pill
    return "bg-gray-100 border-gray-200 text-gray-700";
  };

  return (
    <span className={clsx(
      "px-2 py-0.5 rounded-full text-xs border",
      getColorClasses()
    )}>
      {children}
    </span>
  );
};

export const Chip = ({ active, onClick, children, title, type = "default" }) => {
  // Color schemes based on type
  const getColorClasses = () => {
    if (type === "default") {
      return {
        inactive: "bg-white hover:bg-gray-100 border-gray-300",
        active: "bg-black text-white border-black"
      };
    }
    
    // For credits chips
    if (type === "credits") {
      // Extract number from children like "0 hours", "1 hour", "2 hours", etc.
      const childText = typeof children === 'string' ? children : String(children);
      const creditsMatch = childText.match(/\d+/);
      const credits = creditsMatch ? parseInt(creditsMatch[0]) : 0;
      
      if (credits === 0) {
        return {
          inactive: "bg-white hover:bg-gray-100 border-gray-300",
          active: "bg-gray-600 text-white border-gray-600"
        };
      } else if (credits === 1) {
        return {
          inactive: "bg-white hover:bg-green-50 hover:border-green-400 hover:text-green-700 border-gray-300",
          active: "bg-green-600 text-white border-green-600"
        };
      } else if (credits === 2) {
        return {
          inactive: "bg-white hover:bg-lime-50 hover:border-lime-400 hover:text-lime-700 border-gray-300",
          active: "bg-lime-600 text-white border-lime-600"
        };
      } else if (credits === 3) {
        return {
          inactive: "bg-white hover:bg-yellow-50 hover:border-yellow-400 hover:text-yellow-700 border-gray-300",
          active: "bg-yellow-600 text-white border-yellow-600"
        };
      } else if (credits >= 4) {
        return {
          inactive: "bg-white hover:bg-red-50 hover:border-red-400 hover:text-red-700 border-gray-300",
          active: "bg-red-600 text-white border-red-600"
        };
      }
    }
    
    // For difficulty chips
    if (type === "difficulty") {
      const difficulty = children;
      if (difficulty === "Light") {
        return {
          inactive: "bg-white hover:bg-green-50 hover:border-green-400 hover:text-green-700 border-gray-300",
          active: "bg-green-600 text-white border-green-600"
        };
      } else if (difficulty === "Moderate") {
        return {
          inactive: "bg-white hover:bg-yellow-50 hover:border-yellow-400 hover:text-yellow-700 border-gray-300",
          active: "bg-yellow-600 text-white border-yellow-600"
        };
      } else if (difficulty === "Challenging") {
        return {
          inactive: "bg-white hover:bg-red-50 hover:border-red-400 hover:text-red-700 border-gray-300",
          active: "bg-red-600 text-white border-red-600"
        };
      }
    }
    
    // For level chips (gradient from green to red based on level)
    if (type === "level") {
      // Handle both "100-level" strings and raw numbers
      const childText = typeof children === 'string' ? children : String(children);
      const level = parseInt(childText.replace("-level", ""));
      
      if (isNaN(level)) {
        return {
          inactive: "bg-white hover:bg-gray-100 border-gray-300",
          active: "bg-black text-white border-black"
        };
      }
      
      if (level <= 100) {
        return {
          inactive: "bg-white hover:bg-green-50 hover:border-green-400 hover:text-green-700 border-gray-300",
          active: "bg-green-600 text-white border-green-600"
        };
      } else if (level === 200) {
        return {
          inactive: "bg-white hover:bg-lime-50 hover:border-lime-400 hover:text-lime-700 border-gray-300",
          active: "bg-lime-600 text-white border-lime-600"
        };
      } else if (level === 300) {
        return {
          inactive: "bg-white hover:bg-yellow-50 hover:border-yellow-400 hover:text-yellow-700 border-gray-300",
          active: "bg-yellow-600 text-white border-yellow-600"
        };
      } else if (level >= 400) {
        return {
          inactive: "bg-white hover:bg-red-50 hover:border-red-400 hover:text-red-700 border-gray-300",
          active: "bg-red-600 text-white border-red-600"
        };
      }
    }
    
    // Fallback
    return {
      inactive: "bg-white hover:bg-gray-100 border-gray-300",
      active: "bg-black text-white border-black"
    };
  };
  
  const colors = getColorClasses();
  
  return (
    <button
      title={title}
      onClick={onClick}
      className={clsx(
        "px-3 py-1 rounded-full text-sm border transition",
        active ? colors.active : colors.inactive
      )}
    >
      {children}
    </button>
  );
};