import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getHistory } from '../api/client';

const INITIAL_MOCK_HISTORY = [
  { id: 'h1', nl_query: 'Show count of patients by age group', timestamp: '2 minutes ago' },
  { id: 'h2', nl_query: 'List top 5 products by total revenue', timestamp: '15 minutes ago' },
  { id: 'h3', nl_query: 'Show me patients admitted after March 1st', timestamp: '1 hour ago' },
  { id: 'h4', nl_query: 'Get monthly order totals for 2026', timestamp: '3 hours ago' },
];

export default function HistorySidebar({ sessionId, isOpen, onClose, onSelectHistory }) {
  const [historyItems, setHistoryItems] = useState(INITIAL_MOCK_HISTORY);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistoryData = async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory(sessionId);
      if (data && Array.isArray(data.conversations) && data.conversations.length > 0) {
        setHistoryItems(data.conversations);
      }
    } catch (err) {
      console.warn('History API error, falling back to cached view:', err.message);
      setError('Could not refresh live history. Showing recent queries.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistoryData();
  }, [sessionId]);

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
          {/* Mobile and tablet backdrop overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-900/25 backdrop-blur-xs z-40 transition-opacity"
          />

          {/* Sidebar Drawer */}
          <motion.aside
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 280 }}
            className="fixed top-0 bottom-0 left-0 z-40 w-72 sm:w-80 bg-white/92 backdrop-blur-xl border-r border-slate-200/80 shadow-2xl flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="p-4 border-b border-slate-200/70 flex items-center justify-between bg-slate-50/70">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="font-bold text-sm text-slate-800 tracking-tight">
                  Query History
                </h3>
              </div>

              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={fetchHistoryData}
                  title="Refresh history"
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
                >
                  <svg className={`w-4 h-4 ${loading ? 'animate-spin text-teal-600' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>

                <button
                  type="button"
                  onClick={onClose}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                  title="Close History"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* History List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {error && (
                <div className="p-2.5 mb-2 rounded-xl bg-amber-50 border border-amber-200 text-[11px] text-amber-800 flex items-center justify-between gap-2">
                  <span>{error}</span>
                  <button
                    onClick={fetchHistoryData}
                    className="underline font-semibold shrink-0 hover:text-amber-950"
                  >
                    Retry
                  </button>
                </div>
              )}

              {loading ? (
                <div className="p-6 text-center text-xs text-slate-500 flex items-center justify-center gap-2">
                  <svg className="animate-spin w-4 h-4 text-teal-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Loading query history...</span>
                </div>
              ) : (
                historyItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      if (onSelectHistory) onSelectHistory(item.nl_query);
                      if (onClose) onClose();
                    }}
                    className="w-full text-left p-3 rounded-xl bg-white/70 hover:bg-teal-50/70 border border-slate-200/70 hover:border-teal-300/70 transition-all group shadow-2xs"
                  >
                    <p className="text-xs sm:text-sm font-medium text-slate-800 line-clamp-2 group-hover:text-teal-800 transition-colors">
                      {item.nl_query}
                    </p>
                    <span className="text-[10px] text-slate-400 mt-1 block">
                      {item.timestamp}
                    </span>
                  </button>
                ))
              )}
            </div>

            {/* Sidebar Footer */}
            <div className="p-3 border-t border-slate-200/70 bg-slate-50/70 text-center">
              <p className="text-[11px] text-slate-500">
                Click any entry to paste into chat input
              </p>
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
