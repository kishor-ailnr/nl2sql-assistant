import { motion } from 'framer-motion';

export default function MessageBubble({ role, content, timestamp }) {
  const isUser = role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex w-full my-2.5 ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-[85%] sm:max-w-[75%] md:max-w-[65%] flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
        
        {/* Message Bubble Box */}
        <div
          className={`px-4 py-3 text-sm leading-relaxed shadow-xs transition-colors duration-150 break-words ${
            isUser
              ? 'bg-gradient-to-r from-teal-600 to-teal-700 text-white rounded-2xl rounded-br-xs shadow-sm shadow-teal-700/10'
              : 'bg-white/80 backdrop-blur-md text-slate-800 border border-slate-200/70 rounded-2xl rounded-bl-xs shadow-2xs'
          }`}
        >
          {content}
        </div>

        {/* Timestamp */}
        {timestamp && (
          <span className="text-[10px] text-slate-400 mt-1 px-1 font-sans">
            {timestamp}
          </span>
        )}
      </div>
    </motion.div>
  );
}
