import { useState, useEffect } from "react";
import axios from "axios";
import './App.css';

// Import icons (you can use any icon library)
const SparklesIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.847a4.5 4.5 0 003.09 3.09L15.75 12l-2.847.813a4.5 4.5 0 00-3.09 3.091zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z"/>
  </svg>
);

const HistoryIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path fillRule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z" clipRule="evenodd"/>
  </svg>
);

const ZapIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path fillRule="evenodd" d="M14.615 1.595a.75.75 0 01.359.852L12.982 9.75h7.268a.75.75 0 01.548 1.262l-10.5 11.25a.75.75 0 01-1.272-.71l1.992-7.302H3.75a.75.75 0 01-.548-1.262l10.5-11.25a.75.75 0 01.913-.143z" clipRule="evenodd"/>
  </svg>
);

const SendIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z"/>
  </svg>
);

const LoaderIcon = ({ className }) => (
  <svg className={`loading-spinner ${className}`} viewBox="0 0 24 24" fill="currentColor">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.25"/>
    <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
  </svg>
);

const EyeIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 15a3 3 0 100-6 3 3 0 000 6z"/>
    <path fillRule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12.001 3.75c4.97 0 9.185 3.223 10.675 7.69.12.362.12.752 0 1.113-1.487 4.471-5.705 7.697-10.677 7.697-4.97 0-9.186-3.223-10.675-7.69a1.762 1.762 0 010-1.113zM17.25 12a5.25 5.25 0 11-10.5 0 5.25 5.25 0 0110.5 0z" clipRule="evenodd"/>
  </svg>
);

const CodeIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path fillRule="evenodd" d="M14.447 3.027a.75.75 0 01.527.92l-4.5 16.5a.75.75 0 01-1.448-.394l4.5-16.5a.75.75 0 01.921-.526zM16.72 6.22a.75.75 0 011.06 0l5.25 5.25a.75.75 0 010 1.06l-5.25 5.25a.75.75 0 11-1.06-1.06L21.44 12l-4.72-4.72a.75.75 0 010-1.06zm-9.44 0a.75.75 0 010 1.06L2.56 12l4.72 4.72a.75.75 0 11-1.06 1.06L.97 12.53a.75.75 0 010-1.06l5.25-5.25a.75.75 0 011.06 0z" clipRule="evenodd"/>
  </svg>
);

const DownloadIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path fillRule="evenodd" d="M12 2.25a.75.75 0 01.75.75v11.69l3.22-3.22a.75.75 0 111.06 1.06l-4.5 4.5a.75.75 0 01-1.06 0l-4.5-4.5a.75.75 0 111.06-1.06l3.22 3.22V3a.75.75 0 01.75-.75zm-9 13.5a.75.75 0 01.75.75v2.25a1.5 1.5 0 001.5 1.5h13.5a1.5 1.5 0 001.5-1.5V16.5a.75.75 0 011.5 0v2.25a3 3 0 01-3 3H5.25a3 3 0 01-3-3V16.5a.75.75 0 01.75-.75z" clipRule="evenodd"/>
  </svg>
);

const LayoutIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path fillRule="evenodd" d="M1.5 7.125c0-1.036.84-1.875 1.875-1.875h6c1.036 0 1.875.84 1.875 1.875v3.75c0 1.036-.84 1.875-1.875 1.875h-6A1.875 1.875 0 011.5 10.875v-3.75zm12 1.5c0-1.036.84-1.875 1.875-1.875h5.25c1.036 0 1.875.84 1.875 1.875v8.25c0 1.036-.84 1.875-1.875 1.875h-5.25a1.875 1.875 0 01-1.875-1.875v-8.25zM3 16.125c0-1.036.84-1.875 1.875-1.875h5.25c1.036 0 1.875.84 1.875 1.875v2.25c0 1.036-.84 1.875-1.875 1.875h-5.25A1.875 1.875 0 013 18.375v-2.25z" clipRule="evenodd"/>
  </svg>
);

const ExternalLinkIcon = () => (
  <svg viewBox="0 0 24 24" fill="currentColor">
    <path fillRule="evenodd" d="M15.75 2.25H21a.75.75 0 01.75.75v5.25a.75.75 0 01-1.5 0V4.81L8.03 17.03a.75.75 0 01-1.06-1.06L19.19 3.75h-3.44a.75.75 0 010-1.5zm-10.5 4.5a1.5 1.5 0 00-1.5 1.5v9.75a1.5 1.5 0 001.5 1.5h9.75a1.5 1.5 0 001.5-1.5V10.5a.75.75 0 011.5 0v7.5a3 3 0 01-3 3H5.25a3 3 0 01-3-3V8.25a3 3 0 013-3h7.5a.75.75 0 010 1.5h-7.5z" clipRule="evenodd"/>
  </svg>
);

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [currentStep, setCurrentStep] = useState(-1);
  const [generatedCode, setGeneratedCode] = useState("");
  const [deployUrl, setDeployUrl] = useState("");
  const [wireframeUrl, setWireframeUrl] = useState("");
  const [githubRepo, setGithubRepo] = useState("");
  const [previewData, setPreviewData] = useState(null);
  const [history, setHistory] = useState([]);
  const [toast, setToast] = useState(null);

  // Define generation steps
  const steps = [
    { name: "Analyzing", icon: "🔍" },
    { name: "Designing", icon: "🎨" },
    { name: "Coding", icon: "⚛️" },
    { name: "Building", icon: "🔨" },
    { name: "Deploying", icon: "🚀" }
  ];

  // Load history on mount
  useEffect(() => {
    // Initialize with some mock history
    setHistory([
      { prompt: "Modern dashboard with charts", timestamp: new Date().toISOString(), status: 'success' },
      { prompt: "Landing page for SaaS", timestamp: new Date().toISOString(), status: 'success' }
    ]);
  }, []);

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
  };

  const addToHistory = (promptText, status = 'pending') => {
    const historyItem = {
      prompt: promptText,
      timestamp: new Date().toISOString(),
      status
    };
    setHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10 items
  };

  const updateHistoryStatus = (promptText, status) => {
    setHistory(prev => prev.map(item => 
      item.prompt === promptText ? { ...item, status } : item
    ));
  };

  const handleGenerateUI = async () => {
    if (!prompt.trim()) {
      showToast("Please enter a prompt", "warning");
      return;
    }

    // Reset state
    setCurrentStep(0);
    setGeneratedCode("");
    setDeployUrl("");
    setWireframeUrl("");
    setGithubRepo("");
    setPreviewData(null);

    // Add to history
    addToHistory(prompt);

    // Simulate step progression
    const stepDuration = 1500;

    try {
      // Step 1: Analyzing
      setTimeout(() => setCurrentStep(1), stepDuration);

      // Step 2: Designing  
      setTimeout(() => {
        setCurrentStep(2);
        setPreviewData({
          structure: "Modern dashboard with sidebar navigation, main content area, and responsive grid layout",
          features: ["Responsive Design", "Dark Mode", "Interactive Charts", "Real-time Updates"]
        });
      }, stepDuration * 2);

      // Step 3: Coding
      setTimeout(() => {
        setCurrentStep(3);
        setGeneratedCode(`import React from 'react';
import './Dashboard.css';

export default function Dashboard() {
  return (
    <div className="dashboard">
      <aside className="sidebar">
        <h2>Navigation</h2>
        <nav>
          <a href="#dashboard">Dashboard</a>
          <a href="#analytics">Analytics</a>
          <a href="#settings">Settings</a>
        </nav>
      </aside>
      <main className="main-content">
        <header className="header">
          <h1>Dashboard</h1>
        </header>
        <div className="content-grid">
          <div className="card">
            <h3>Sales Overview</h3>
            <p>Your sales data visualization</p>
          </div>
          <div className="card">
            <h3>Recent Activity</h3>
            <p>Latest user interactions</p>
          </div>
        </div>
      </main>
    </div>
  );
}`);
      }, stepDuration * 3);

      // Step 4: Building & Deploying
      setTimeout(async () => {
        setCurrentStep(4);
        
        try {
          // Make actual API call if needed
          // const response = await axios.post(`${API_URL}/generate-ui/`, { prompt });
          
          // Mock successful completion
          setWireframeUrl("https://figma.com/mock-wireframe");
          setGithubRepo("user/generated-ui-project");
          setDeployUrl("https://generated-ui.onrender.com");
          
          updateHistoryStatus(prompt, 'success');
          showToast("UI generated successfully!", "success");
          
        } catch (error) {
          console.error(error);
          updateHistoryStatus(prompt, 'error');
          showToast("Error generating UI. Please try again.", "error");
        }
        
        setCurrentStep(5); // Complete
      }, stepDuration * 4);

    } catch (error) {
      console.error(error);
      updateHistoryStatus(prompt, 'error');
      showToast("An unexpected error occurred", "error");
      setCurrentStep(-1);
    }
  };

  const handleExport = (exportType) => {
    showToast(`Exporting as ${exportType}...`, "info");
    console.log(`Exporting as: ${exportType}`);
  };

  const handleSelectHistory = (historyItem) => {
    setPrompt(historyItem.prompt);
    showToast("Prompt loaded from history", "info");
  };

  const handleClearHistory = () => {
    setHistory([]);
    showToast("History cleared", "info");
  };

  const isGenerating = currentStep >= 0 && currentStep < steps.length;

  return (
    <div className="app-container">
      <div className="container">
        {/* Header */}
        <div className="header">
          <div className="header-icon">
            <SparklesIcon />
          </div>
          <h1 className="main-title">AI UI Builder</h1>
          <p className="subtitle">
            Transform your ideas into beautiful, functional React components with the power of AI. 
            Just describe what you want, and watch the magic happen.
          </p>
        </div>

        {/* Recent Projects */}
        {history.length > 0 && (
          <div className="glass-card recent-projects">
            <h3>
              <HistoryIcon />
              Recent Projects
            </h3>
            <div className="history-grid">
              {history.slice(0, 2).map((item, index) => (
                <div
                  key={index}
                  className="history-item"
                  onClick={() => handleSelectHistory(item)}
                >
                  <div className="history-title">{item.prompt}</div>
                  <div className="history-meta">
                    <span>{new Date(item.timestamp).toLocaleDateString()}</span>
                    <span className={`status-badge status-${item.status}`}>
                      {item.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Input Section */}
        <div className="glass-card input-section">
          <label className="input-label">
            <SparklesIcon />
            Describe your dream UI
          </label>
          <div className="textarea-wrapper">
            <textarea
              className="main-textarea"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Create a modern SaaS dashboard with dark theme, interactive charts, user management table, and a clean sidebar navigation..."
              rows={4}
              disabled={isGenerating}
            />
            <div className="textarea-footer">
              <div className="char-counter">
                <span>{prompt.length}/1000</span>
                <div className="status-dot"></div>
              </div>
            </div>
          </div>
          <div className="input-footer">
            <div className="tip-text">
              <ZapIcon />
              Tip: Be specific about colors, layout, and functionality
            </div>
            <button
              className="generate-btn"
              onClick={handleGenerateUI}
              disabled={!prompt.trim() || isGenerating}
            >
              {isGenerating ? (
                <>
                  <LoaderIcon className="w-5 h-5" />
                  Generating Magic...
                </>
              ) : (
                <>
                  <SendIcon />
                  Generate UI
                </>
              )}
            </button>
          </div>
        </div>

        {/* Progress Steps */}
        {isGenerating && (
          <div className="glass-card progress-section">
            <div className="progress-container">
              <div className="progress-line">
                <div 
                  className="progress-fill"
                  style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
                ></div>
              </div>
              {steps.map((step, index) => {
                const isActive = index === currentStep;
                const isCompleted = index < currentStep;
                return (
                  <div key={index} className="step-item">
                    <div className={`step-circle ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                      {isActive ? (
                        <LoaderIcon className="w-6 h-6" />
                      ) : isCompleted ? (
                        '✓'
                      ) : (
                        step.icon
                      )}
                    </div>
                    <span className={`step-name ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}>
                      {step.name}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Main Content Grid */}
        <div className="content-grid">
          {/* Left Column */}
          <div>
            {/* Preview Panel */}
            <div className="glass-card preview-panel">
              <div className="panel-header">
                <div className="panel-title">
                  <EyeIcon />
                  Live Preview
                </div>
              </div>
              <div className="preview-content">
                {previewData ? (
                  <div>
                    <div className="preview-structure">
                      <LayoutIcon className="structure-icon" />
                      <p><strong>UI Structure Preview</strong></p>
                      <p>{previewData.structure}</p>
                    </div>
                    {previewData.features && (
                      <div>
                        <h4><strong>Features:</strong></h4>
                        <div className="feature-tags">
                          {previewData.features.map((feature, index) => (
                            <span key={index} className="feature-tag">
                              {feature}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="preview-placeholder">
                    <LayoutIcon />
                    <p>Preview will appear here once generation starts</p>
                  </div>
                )}
              </div>
            </div>

            {/* Export Options */}
            <div className="glass-card export-section" style={{ marginTop: '2rem' }}>
              <div className="export-title">
                <DownloadIcon />
                Export Options
              </div>
              <div className="export-grid">
                {['React', 'Vue', 'HTML/CSS', 'Figma'].map((format) => (
                  <button
                    key={format}
                    className="export-btn"
                    onClick={() => handleExport(format)}
                    disabled={!generatedCode}
                  >
                    {format}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div>
            {/* Code Display */}
            <div className="glass-card code-panel">
              <div className="panel-header">
                <div className="panel-title">
                  <CodeIcon />
                  Generated Code
                </div>
                {generatedCode && (
                  <div className="panel-action">
                    <DownloadIcon />
                  </div>
                )}
              </div>
              <div className="code-content">
                {generatedCode ? (
                  <pre className="code-block">
                    <code>{generatedCode}</code>
                  </pre>
                ) : (
                  <div className="preview-placeholder">
                    <CodeIcon />
                    <p>Generated code will appear here</p>
                  </div>
                )}
              </div>
            </div>

            {/* Result Links */}
            {(wireframeUrl || deployUrl || githubRepo) && (
              <div className="glass-card results-section" style={{ marginTop: '2rem' }}>
                <div className="results-title">
                  <SparklesIcon />
                  Your Project is Ready! 🎉
                </div>
                <div>
                  {wireframeUrl && (
                    <a href={wireframeUrl} target="_blank" rel="noopener noreferrer" className="result-link">
                      <SparklesIcon className="result-icon" />
                      <div className="result-info">
                        <h4>View Wireframe</h4>
                        <p>Open in Figma</p>
                      </div>
                      <ExternalLinkIcon className="result-external" />
                    </a>
                  )}
                  {githubRepo && (
                    <div className="result-link">
                      <CodeIcon className="result-icon" />
                      <div className="result-info">
                        <h4>Repository</h4>
                        <p>github.com/{githubRepo}</p>
                      </div>
                    </div>
                  )}
                  {deployUrl && (
                    <a href={deployUrl} target="_blank" rel="noopener noreferrer" className="result-link">
                      <ExternalLinkIcon className="result-icon" />
                      <div className="result-info">
                        <h4>Live Application</h4>
                        <p>View deployed app</p>
                      </div>
                      <ExternalLinkIcon className="result-external" />
                    </a>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Toast Notifications */}
        {toast && (
          <div 
            className={`toast ${toast.type}`}
            onClick={() => setToast(null)}
          >
            {toast.message}
          </div>
        )}
      </div>
    </div>
  );
}