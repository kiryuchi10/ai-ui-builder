import React, { useState } from 'react';
import { Play, FileText, CheckCircle, AlertCircle, Download, Settings } from 'lucide-react';

const TestGenerator = ({ generatedCode, componentName }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [testConfig, setTestConfig] = useState({
    testTypes: ['unit', 'integration', 'accessibility'],
    framework: 'react',
    coverageTarget: 90
  });
  const [activeTab, setActiveTab] = useState('generate');

  

  const handleGenerateTests = async () => {
    if (!generatedCode || !componentName) {
      alert('Please generate a component first');
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/v1/testing/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          component_code: generatedCode,
          component_name: componentName,
          framework: testConfig.framework,
          test_types: testConfig.testTypes,
          coverage_target: testConfig.coverageTarget / 100
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate tests');
      }

      const result = await response.json();
      setTestResults(result);
      setActiveTab('results');
      
    } catch (error) {
      console.error('Test generation failed:', error);
      alert('Failed to generate tests. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExecuteTests = async () => {
    if (!testResults) return;

    try {
      const response = await fetch('/api/v1/testing/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          test_files: testResults.test_files,
          project_config: { framework: testConfig.framework }
        }),
      });

      const executionResult = await response.json();
      setTestResults(prev => ({
        ...prev,
        execution: executionResult
      }));
      
    } catch (error) {
      console.error('Test execution failed:', error);
      alert('Failed to execute tests. Please try again.');
    }
  };

  const downloadTestFiles = () => {
    if (!testResults) return;

    testResults.test_files.forEach(file => {
      const blob = new Blob([file.content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  };

  const getCoverageColor = (coverage) => {
    if (coverage >= 90) return 'text-green-600 bg-green-100';
    if (coverage >= 70) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="p-2 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg mr-3">
            <FileText className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Test Generator</h3>
            <p className="text-gray-600 text-sm">AI-powered comprehensive test suite generation</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveTab('config')}
            className={`p-2 rounded-lg transition-colors ${
              activeTab === 'config' ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-6 bg-gray-100 rounded-lg p-1">
        {['generate', 'config', 'results'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Generate Tab */}
      {activeTab === 'generate' && (
        <div className="space-y-6">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-2">Test Generation Overview</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                <span>Unit Tests</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                <span>Integration Tests</span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                <span>Accessibility Tests</span>
              </div>
            </div>
          </div>

          <div className="flex justify-center">
            <button
              onClick={handleGenerateTests}
              disabled={isGenerating || !generatedCode}
              className="px-8 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-xl hover:from-green-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2"
            >
              {isGenerating ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Generating Tests...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Generate Test Suite</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Configuration Tab */}
      {activeTab === 'config' && (
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              Test Types:
            </label>
            <div className="space-y-2">
              {['unit', 'integration', 'accessibility'].map((type) => (
                <label key={type} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={testConfig.testTypes.includes(type)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setTestConfig(prev => ({
                          ...prev,
                          testTypes: [...prev.testTypes, type]
                        }));
                      } else {
                        setTestConfig(prev => ({
                          ...prev,
                          testTypes: prev.testTypes.filter(t => t !== type)
                        }));
                      }
                    }}
                    className="mr-3 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-700 capitalize">{type} Tests</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Framework:
            </label>
            <select
              value={testConfig.framework}
              onChange={(e) => setTestConfig(prev => ({ ...prev, framework: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="react">React</option>
              <option value="vue">Vue.js</option>
              <option value="angular">Angular</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Coverage Target: {testConfig.coverageTarget}%
            </label>
            <input
              type="range"
              min="60"
              max="100"
              value={testConfig.coverageTarget}
              onChange={(e) => setTestConfig(prev => ({ ...prev, coverageTarget: parseInt(e.target.value) }))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>60%</span>
              <span>80%</span>
              <span>100%</span>
            </div>
          </div>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && testResults && (
        <div className="space-y-6">
          {/* Test Generation Results */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-semibold text-gray-900">Generated Test Suite</h4>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleExecuteTests}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>Run Tests</span>
                </button>
                <button
                  onClick={downloadTestFiles}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="text-2xl font-bold text-blue-600">{testResults.test_count}</div>
                <div className="text-sm text-gray-600">Total Tests</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className={`text-2xl font-bold ${getCoverageColor(testResults.coverage_estimate * 100).split(' ')[0]}`}>
                  {Math.round(testResults.coverage_estimate * 100)}%
                </div>
                <div className="text-sm text-gray-600">Est. Coverage</div>
              </div>
              <div className="text-center p-3 bg-white rounded-lg border">
                <div className="text-2xl font-bold text-purple-600">{testResults.test_files.length}</div>
                <div className="text-sm text-gray-600">Test Files</div>
              </div>
            </div>

            {/* Test Files */}
            <div className="space-y-3">
              {testResults.test_files.map((file, index) => (
                <div key={index} className="border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between p-3 bg-gray-100 rounded-t-lg">
                    <span className="font-medium text-gray-900">{file.filename}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      file.type === 'unit' ? 'bg-blue-100 text-blue-800' :
                      file.type === 'integration' ? 'bg-green-100 text-green-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {file.type}
                    </span>
                  </div>
                  <div className="p-3 bg-gray-50 rounded-b-lg">
                    <pre className="text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap">
                      {file.content.substring(0, 300)}...
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Test Execution Results */}
          {testResults.execution && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-semibold text-gray-900 mb-4">Test Execution Results</h4>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="text-center p-3 bg-white rounded-lg border">
                  <div className="text-xl font-bold text-green-600">{testResults.execution.results.passed}</div>
                  <div className="text-sm text-gray-600">Passed</div>
                </div>
                <div className="text-center p-3 bg-white rounded-lg border">
                  <div className="text-xl font-bold text-red-600">{testResults.execution.results.failed}</div>
                  <div className="text-sm text-gray-600">Failed</div>
                </div>
                <div className="text-center p-3 bg-white rounded-lg border">
                  <div className="text-xl font-bold text-blue-600">{testResults.execution.results.total}</div>
                  <div className="text-sm text-gray-600">Total</div>
                </div>
                <div className="text-center p-3 bg-white rounded-lg border">
                  <div className="text-xl font-bold text-purple-600">{testResults.execution.results.duration}s</div>
                  <div className="text-sm text-gray-600">Duration</div>
                </div>
              </div>

              {/* Coverage Breakdown */}
              <div className="bg-white rounded-lg p-4 border">
                <h5 className="font-medium text-gray-900 mb-3">Coverage Breakdown</h5>
                <div className="space-y-2">
                  {Object.entries(testResults.execution.coverage).map(([key, value]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600 capitalize">{key}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getCoverageColor(value).includes('green') ? 'bg-green-500' : 
                              getCoverageColor(value).includes('yellow') ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${value}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{value}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Suggestions */}
          {testResults.suggestions && testResults.suggestions.length > 0 && (
            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="flex items-center mb-3">
                <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
                <h4 className="font-semibold text-yellow-900">Improvement Suggestions</h4>
              </div>
              <ul className="space-y-2">
                {testResults.suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-yellow-800 flex items-start">
                    <span className="w-2 h-2 bg-yellow-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TestGenerator;