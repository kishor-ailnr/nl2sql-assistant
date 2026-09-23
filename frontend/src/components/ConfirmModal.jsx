import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ConfirmModal({ sql, explanation, onConfirm, onCancel, isOpen }) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Reset double-submit state whenever modal opens or closes
  useEffect(() => {
    if (isOpen) {
      setIsSubmitting(false);
    }
  }, [isOpen]);

  const handleConfirmClick = () => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    onConfirm();
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget && !isSubmitting) {
      onCancel();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div
          onClick={handleBackdropClick}
          className="fixed inset-0 bg-slate-900/35 backdrop-blur-xs z-50 flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 8 }}
            transition={{ duration: 0.2 }}
            className="bg-white/95 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/80 max-w-lg w-full p-6 text-slate-900 space-y-4"
          >
            {/* Header with Warning Icon */}
            <div className="flex items-start gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-700 flex items-center justify-center shrink-0 border border-amber-200">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-bold text-slate-900">
                  Confirm Data Modification
                </h3>
                <p className="text-xs text-amber-800 font-medium mt-0.5">
                  ⚠️ This query will modify or delete records in your database.
                </p>
              </div>
            </div>

            {/* Explanation */}
            {explanation && (
              <p className="text-xs sm:text-sm text-slate-700 leading-relaxed bg-amber-50/60 p-3 rounded-xl border border-amber-100/80">
                {explanation}
              </p>
            )}

            {/* SQL Code Preview */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                SQL Statement to Execute
              </label>
              <pre className="bg-slate-900 text-teal-300 font-mono text-xs p-3.5 rounded-xl overflow-x-auto border border-slate-800 max-h-40 leading-relaxed">
                <code>{sql || '-- No SQL specified'}</code>
              </pre>
            </div>

            {/* Modal Action Buttons */}
            <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-slate-100">
              <button
                type="button"
                onClick={onCancel}
                disabled={isSubmitting}
                className="px-4 py-2 text-xs sm:text-sm font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200/80 rounded-xl transition-all disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleConfirmClick}
                disabled={isSubmitting}
                className="px-4 py-2 text-xs sm:text-sm font-semibold text-white bg-amber-600 hover:bg-amber-700 rounded-xl shadow-sm transition-all flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <>
                    <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Executing...
                  </>
                ) : (
                  'Confirm & Execute'
                )}
              </button>
            </div>

          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
