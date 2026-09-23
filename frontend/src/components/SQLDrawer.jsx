import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function SQLDrawer({ queryData, isOpen, onClose }) {
  const [copied, setCopied] = useState(false);

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

  if (!queryData) return null;

  const {
    sql = '',
    explanation = '',
    confidence = 0,
    query_type = 'select',
    query_id = 'N/A',
  } = queryData;

  const handleCopy = () => {
    if (sql) {
      navigator.clipboard.writeText(sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  // Confidence badge calculation
  const confVal = typeof confidence === 'number' ? confidence : 1.0;
  const confPercent = Math.round(confVal * 100);

  let badgeColorClass = 'bg-emerald-50 text-emerald-800 border-emerald-200/80';
  let badgeDotClass = 'bg-emerald-500';
  let badgeLabel = 'High Confidence';

  if (confVal < 0.5) {
    badgeColorClass = 'bg-rose-50 text-rose-800 border-rose-200/80';
    badgeDotClass = 'bg-rose-500';
    badgeLabel = 'Low Confidence';
  } else if (confVal <= 0.8) {
    badgeColorClass = 'bg-amber-50 text-amber-800 border-amber-200/80';
    badgeDotClass = 'bg-amber-500';
    badgeLabel = 'Medium Confidence';
  }

  const isWrite = query_type === 'write';

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

          {/* Right Drawer */}
          <motion.aside
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 280 }}
            className="fixed top-0 bottom-0 right-0 z-50 w-full sm:w-[460px] md:w-[500px] bg-white/92 backdrop-blur-xl border-l border-slate-200/80 shadow-2xl flex flex-col overflow-hidden"
          >
            {/* Drawer Header */}
            <div className="p-5 border-b border-slate-200/70 bg-gradient-to-r from-white to-slate-50/80 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <span className="w-8 h-8 rounded-xl bg-teal-600 text-white flex items-center justify-center font-mono font-bold text-xs shadow-sm">
                  &lt;/&gt;
                </span>
                <div>
                  <h3 className="font-bold text-sm text-slate-800 tracking-tight">
                    Generated SQL Query
                  </h3>
                  <p className="text-[11px] text-slate-500 font-mono">
                    Query #{query_id}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={onClose}
                className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                title="Close SQL Drawer"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Drawer Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              
              {/* Status and Confidence Badges */}
              <div className="flex flex-wrap items-center justify-between gap-2 p-3 rounded-xl bg-slate-50/80 border border-slate-200/70">
                <div className="flex items-center gap-2">
                  <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${badgeColorClass}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${badgeDotClass} animate-pulse`}></span>
                    {confPercent}% ({badgeLabel})
                  </span>

                  {isWrite ? (
                    <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-100 text-amber-900 border border-amber-300">
                      Write Operation
                    </span>
                  ) : (
                    <span className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-800 border border-blue-200/70">
                      Read Only (SELECT)
                    </span>
                  )}
                </div>

                <button
                  type="button"
                  onClick={handleCopy}
                  className="px-2.5 py-1 rounded-lg bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 text-xs font-medium transition-all shadow-2xs flex items-center gap-1"
                >
                  {copied ? (
                    <>
                      <span className="text-teal-600 font-semibold">✓ Copied</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <span>Copy SQL</span>
                    </>
                  )}
                </button>
              </div>

              {/* SQL Code Box */}
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                  SQLite Syntax
                </label>
                <div className="relative group">
                  <pre className="bg-slate-900 text-teal-300 font-mono text-xs sm:text-sm p-4 rounded-xl overflow-x-auto border border-slate-800 shadow-md leading-relaxed whitespace-pre-wrap">
                    <code>{sql || '-- No SQL query generated'}</code>
                  </pre>
                </div>
              </div>

              {/* Natural Language Explanation */}
              {explanation && (
                <div className="p-4 rounded-xl bg-teal-50/50 border border-teal-100 space-y-1">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-teal-800 flex items-center gap-1.5">
                    <span>💡</span> Query Explanation
                  </h4>
                  <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                    {explanation}
                  </p>
                </div>
              )}

              {/* Security & Validation Notice */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200/80 text-[11px] text-slate-600 space-y-1">
                <span className="font-semibold text-slate-700 block">
                  🔒 Engine Validation:
                </span>
                <p>
                  This query was parsed with AST validation. Write operations always require dual confirmation before affecting database records.
                </p>
              </div>

            </div>

            {/* Footer */}
            <div className="p-4 border-t border-slate-200/70 bg-slate-50/80 flex justify-end">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-semibold text-slate-700 bg-white hover:bg-slate-100 border border-slate-200 rounded-xl transition-all shadow-2xs"
              >
                Close Drawer
              </button>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
