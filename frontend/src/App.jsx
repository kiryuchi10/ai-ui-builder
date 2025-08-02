import { useState } from "react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [deployUrl, setDeployUrl] = useState("");

  const handleGenerateUI = async () => {
    if (!prompt.trim()) return alert("Please enter a prompt");

    setLoading(true);
    setStatus("Generating UI... (Sending request to backend)");
    setDeployUrl("");

    try {
      const response = await axios.post(`${API_URL}/generate-ui/`, { prompt });

      const data = response.data;
      setStatus("✅ Process completed!");
      if (data.render && data.render.status === "success") {
        setDeployUrl(`https://dashboard.render.com/web/${data.render.deployment.id}`);
      }
    } catch (error) {
      console.error(error);
      setStatus("❌ Error generating UI. Check backend logs.");
    }

    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-gray-800 mb-4">AI-Powered UI Builder</h1>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Describe your UI (e.g., SaaS dashboard with charts and sidebar)"
        className="w-full max-w-xl h-32 p-4 border rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-blue-400 mb-4"
      />
      <button
        onClick={handleGenerateUI}
        disabled={loading}
        className="bg-blue-500 text-white px-6 py-3 rounded-lg shadow hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? "Generating..." : "Generate UI"}
      </button>

      {status && (
        <div className="mt-6 p-4 bg-white rounded shadow-md w-full max-w-xl text-gray-700">
          <p>{status}</p>
          {deployUrl && (
            <a
              href={deployUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 underline"
            >
              View on Render
            </a>
          )}
        </div>
      )}
    </div>
  );
}
