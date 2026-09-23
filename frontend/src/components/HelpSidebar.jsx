import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const GUIDE_STEPS = [
  {
    step: '1',
    title: 'Connect Your Data',
    icon: '🔌',
    desc: 'Pick a preloaded demo (Hospital or E-commerce), paste a database URL, or upload a .csv / .sql file to get started.',
  },
  {
    step: '2',
    title: 'Ask in Plain English',
    icon: '💬',
    desc: 'Type questions naturally or use the microphone for voice queries — no SQL knowledge required.',
  },
  {
    step: '3',
    title: 'Smart Visualizations',
    icon: '📊',
    desc: 'Review structured results in formatted tables or toggle to interactive bar and line charts for aggregations.',
  },
  {
    step: '4',
    title: 'Inspect Behind the Scenes',
    icon: '🔍',
    desc: 'Click "</> View SQL" on any answer to reveal the exact query, execution explanation, and confidence score.',
  },
  {
    step: '5',
    title: 'Safe Write Confirmations',
    icon: '🛡️',
    desc: 'Any data changes (INSERT, UPDATE, DELETE) trigger a mandatory confirmation dialog before executing.',
  },
  {
    step: '6',
    title: 'Session Query History',
    icon: '⏱️',
    desc: 'Open the History drawer anytime to revisit, inspect, or re-run prior questions from your active session.',
  },
];

export default function HelpSidebar({ isOpen, onClose }) {
  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-900/25 backdrop-blur-xs z-50 transition-opacity"
          />

          {/* Left Drawer */}
          <motion.aside
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 280 }}
            className="fixed top-0 bottom-0 left-0 z-50 w-80 sm:w-96 bg-white/90 backdrop-blur-xl border-r border-slate-200/80 shadow-2xl flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-5 border-b border-slate-200/70 bg-gradient-to-r from-teal-50/60 to-white flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-8 h-8 rounded-xl bg-teal-600 text-white flex items-center justify-center font-bold text-sm shadow-sm">
                  ?
                </span>
                <div>
                  <h3 className="font-bold text-sm text-slate-800 tracking-tight">
                    User Guide & Orientation
                  </h3>
                  <p className="text-[11px] text-slate-500">
                    Get oriented in 30 seconds
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={onClose}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                title="Close Guide"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Steps List */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5">
              {GUIDE_STEPS.map((item) => (
                <div
                  key={item.step}
                  className="p-3.5 rounded-xl bg-white/70 border border-slate-200/70 shadow-2xs hover:border-teal-300/70 transition-colors flex items-start gap-3"
                >
                  <span className="text-xl shrink-0 mt-0.5" aria-hidden="true">
                    {item.icon}
                  </span>
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700 bg-teal-50 px-1.5 py-0.5 rounded border border-teal-200/50">
                        Step {item.step}
                      </span>
                      <h4 className="text-xs sm:text-sm font-semibold text-slate-800">
                        {item.title}
                      </h4>
                    </div>
                    <p className="text-xs text-slate-600 leading-relaxed pt-1">
                      {item.desc}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Footer Tip */}
            <div className="p-4 border-t border-slate-200/70 bg-slate-50/70 text-center">
              <div className="inline-flex items-center gap-1.5 text-[11px] text-teal-800 font-medium">
                <span>💡</span>
                <span>Press Enter to send a query, or Esc to close dialogs.</span>
              </div>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
