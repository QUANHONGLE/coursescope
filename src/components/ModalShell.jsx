import { motion, AnimatePresence } from "framer-motion";

const ModalShell = ({ open, onClose, title, children }) => (
  <AnimatePresence>
    {open && (
      <motion.div
        className="fixed inset-0 z-50 flex items-center justify-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <div className="absolute inset-0 bg-black/40" onClick={onClose} />
        <motion.div
          role="dialog"
          aria-modal="true"
          className="relative max-w-2xl w-[92%] max-h-[90vh] bg-white rounded-2xl shadow-xl p-6 overflow-y-auto"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 10, opacity: 0 }}
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold">{title}</h3>
            <button
              aria-label="Close"
              className="h-8 w-8 rounded-full hover:bg-gray-100 grid place-items-center"
              onClick={onClose}
            >
              ×
            </button>
          </div>
          {children}
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

export default ModalShell;