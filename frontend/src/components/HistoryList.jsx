import { useState } from 'react';

export default function HistoryList({ history = [], onSelectHistory, onClearHistory }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (history.length === 0) return null;

  return (
    <div className="mb-6 bg-white border border-gray-200 rounded-lg shadow-sm">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-gray-50 transition-colors duration-200"
      >
        <div className="flex items-center space-x-2">
          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="font-medium text-gray-700">Recent Prompts</span>
          <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
            {history.length}
          </span>
        </div>
        <svg 
          className={`w-4 h-4 text-gray-500 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="border-t border-gray-200">
          <div className="max-h-64 overflow-y-auto">
            {history.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
              >
                <button
                  onClick={() => onSelectHistory(item)}
                  className="flex-1 text-left group"
                >
                  <div className="text-sm text-gray-800 group-hover:text-blue-600 transition-colors duration-150 line-clamp-2">
                    {item.prompt}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(item.timestamp).toLocaleDateString()} at {new Date(item.timestamp).toLocaleTimeString()}
                  </div>
                </button>
                <div className="flex items-center space-x-2 ml-3">
                  {item.status === 'success' && (
                    <div className="w-2 h-2 bg-green-500 rounded-full" title="Successfully generated"></div>
                  )}
                  {item.status === 'error' && (
                    <div className="w-2 h-2 bg-red-500 rounded-full" title="Generation failed"></div>
                  )}
                  {item.status === 'pending' && (
                    <div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" title="In progress"></div>
                  )}
                </div>
              </div>
            ))}
          </div>
          
          {history.length > 0 && (
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
              <button
                onClick={onClearHistory}
                className="text-sm text-red-600 hover:text-red-700 transition-colors duration-150"
              >
                Clear History
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}