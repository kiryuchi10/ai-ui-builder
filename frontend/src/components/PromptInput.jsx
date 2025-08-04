export default function PromptInput({ prompt, setPrompt, isGenerating, onSubmit }) {
  return (
    <div className="mb-6">
      <label className="block text-sm font-semibold mb-2 text-gray-700">
        Describe your UI:
      </label>
      <textarea
        className="w-full border border-gray-300 rounded-lg px-4 py-3 resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
        placeholder="e.g., A modern dashboard for sales analytics with charts, tables, and a clean sidebar navigation"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        disabled={isGenerating}
        rows={4}
      />
      <div className="mt-2 text-xs text-gray-500">
        💡 Tip: Be specific about layout, colors, and functionality for better results
      </div>
      <button
        onClick={onSubmit}
        className="mt-4 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 font-medium"
        disabled={isGenerating || !prompt.trim()}
      >
        {isGenerating ? "Generating UI..." : "Generate UI"}
      </button>
    </div>
  );
}