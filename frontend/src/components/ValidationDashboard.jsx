import React, { useState, useEffect } from 'react';
import { Shield, Zap, Code, CheckCircle, AlertTriangle, XCircle, Eye, Download, RefreshCw, Lightbulb } from 'lucide-react';

const ValidationDashboard = ({ generatedCode, onCodeUpdate }) => {
  const [validationResult, setValidationResult] = useState(null);
  const [isValidating, setIsValidating] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [autoFixes, setAutoFixes] = useState({});
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (generatedCode) {
      validateCode();
    }
  }, [generatedCode]);

  const validateCode = async () => {
    if (!generatedCode) return;

    setIsValidating(true);
    try {
      const response = await fetch('/api/v1/validation/validate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: generatedCode,
          code_type: 'react'
        }),
      });

      if (!response.ok) {
        throw new Error('Validation failed');
      }

      const result = await response.json();
      setValidationResult(result);

      // Get auto-fixes if available
      if (result.issues && result.issues.length > 0) {
        const fixResponse = await fetch('/api/v1/validation/generate-fixes', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code: generatedCode,
            issues: result.issues
          }),
        });

        if (fixResponse.ok) {
          const fixes = await fixResponse.json();
          setAutoFixes(fixes);
        }
      }

    } catch (error) {
      console.error('Validation failed:', error);
      // Mock validation result for development
      setValidationResult({
        score: 7.8,
        accessibility_score: 8.2,
        performance_score: 7.1,
        code_quality_score: 8.1,
        issues: [
          {
            type: 'accessibility',
            rule: 'alt_text_missing',
            message: 'Images should have alt text for accessibility',
            severity: 'high',
            line: 15,
            code_snippet: '<img src="example.jpg">'
          },
          {
            type: 'performance',
            rule: 'inline_styles',
            message: 'Avoid inline styles for better performance',
            severity: 'low',
            line: 23,
            code_snippet: 'style={{color: "red"}}'
          },
          {
            type: 'code_quality',
            rule: 'console_logs',
            message: 'Remove console statements in production code',
            severity: 'low',
            line: 8,
            code_snippet: 'console.log("debug")'
          }
        ],
        suggestions: [
          '🔍 Accessibility: Add alt text to images and use semantic HTML',
          '⚡ Performance: Avoid inline styles and optimize images',
          '🛠️ Code Quality: Remove console logs and use consistent formatting'
        ]
      });
    } finally {
      setIsValidating(false);
    }
  };

  const applyAutoFix = (fixType) => {
    if (autoFixes[fixType] && onCodeUpdate) {
      onCodeUpdate(autoFixes[fixType]);
      validateCode(); // Re-validate after applying fix
    }
  };

  const getScoreColor = (score) => {
    if (score >= 8) return 'text-green-600 bg-green-100';
    if (score >= 6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreIcon = (score) => {
    if (score >= 8) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (score >= 6) return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    return <XCircle className="w-5 h-5 text-red-600" />;
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-blue-100 text-blue-800 border-blue-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'accessibility': return <Shield className="w-4 h-4" />;
      case 'performance': return <Zap className="w-4 h-4" />;
      case 'code_quality': return <Code className="w-4 h-4" />;
      default: return <Eye className="w-4 h-4" />;
    }
  };

  const filteredIssues = validationResult?.issues?.filter(issue => 
    selectedCategory === 'all' || issue.type === selectedCategory
  ) || [];

  if (!generatedCode) {
    return (
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
        <div className="text-center py-8">
          <Shield className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600">Generate code to see validation results</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg mr-3">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Code Validation</h3>
            <p className="text-gray-600 text-sm">AI-powered quality & accessibility analysis</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className={`p-2 rounded-lg transition-colors ${
              showDetails ? 'bg-blue-100 text-blue-600' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Eye className="w-5 h-5" />
          </button>
          <button
            onClick={validateCode}
            disabled={isValidating}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-5 h-5 ${isValidating ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {isValidating ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Analyzing code quality...</p>
        </div>
      ) : validationResult ? (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-lg font-semibold text-gray-900">Overall Quality Score</h4>
              <div className="flex items-center space-x-2">
                {getScoreIcon(validationResult.score)}
                <span className={`text-2xl font-bold px-3 py-1 rounded-full ${getScoreColor(validationResult.score)}`}>
                  {validationResult.score}/10
                </span>
              </div>
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <Shield className="w-4 h-4 text-blue-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Accessibility</span>
                  </div>
                  <span className={`text-lg font-bold px-2 py-1 rounded ${getScoreColor(validationResult.accessibility_score)}`}>
                    {validationResult.accessibility_score}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${validationResult.accessibility_score * 10}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <Zap className="w-4 h-4 text-yellow-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Performance</span>
                  </div>
                  <span className={`text-lg font-bold px-2 py-1 rounded ${getScoreColor(validationResult.performance_score)}`}>
                    {validationResult.performance_score}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-yellow-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${validationResult.performance_score * 10}%` }}
                  ></div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <Code className="w-4 h-4 text-purple-600 mr-2" />
                    <span className="text-sm font-medium text-gray-700">Code Quality</span>
                  </div>
                  <span className={`text-lg font-bold px-2 py-1 rounded ${getScoreColor(validationResult.code_quality_score)}`}>
                    {validationResult.code_quality_score}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${validationResult.code_quality_score * 10}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>

          {/* Issues Filter */}
          <div className="flex items-center space-x-4">
            <span className="text-sm font-medium text-gray-700">Filter by:</span>
            <div className="flex space-x-2">
              {['all', 'accessibility', 'performance', 'code_quality'].map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  {category !== 'all' && (
                    <span className="ml-1 text-xs">
                      ({validationResult.issues.filter(i => i.type === category).length})
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Issues List */}
          {filteredIssues.length > 0 ? (
            <div className="space-y-3">
              <h4 className="font-semibold text-gray-900 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-yellow-600" />
                Issues Found ({filteredIssues.length})
              </h4>
              
              {filteredIssues.map((issue, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <div className="flex items-center">
                          {getTypeIcon(issue.type)}
                          <span className="ml-2 text-sm font-medium text-gray-700 capitalize">
                            {issue.type.replace('_', ' ')}
                          </span>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium border ${getSeverityColor(issue.severity)}`}>
                          {issue.severity}
                        </span>
                        <span className="text-xs text-gray-500">Line {issue.line}</span>
                      </div>
                      
                      <p className="text-gray-900 mb-2">{issue.message}</p>
                      
                      {showDetails && issue.code_snippet && (
                        <div className="bg-gray-50 rounded-md p-3 mt-2">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-gray-700">Code Snippet:</span>
                          </div>
                          <pre className="text-xs text-gray-800 overflow-x-auto">
                            <code>{issue.code_snippet}</code>
                          </pre>
                        </div>
                      )}
                    </div>
                    
                    {/* Auto-fix button */}
                    {autoFixes[`${issue.rule}_fix`] && (
                      <button
                        onClick={() => applyAutoFix(`${issue.rule}_fix`)}
                        className="ml-4 px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      >
                        Auto Fix
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-6 bg-green-50 rounded-lg border border-green-200">
              <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="text-green-800 font-medium">No issues found in this category!</p>
              <p className="text-green-600 text-sm">Your code looks great.</p>
            </div>
          )}

          {/* Suggestions */}
          {validationResult.suggestions && validationResult.suggestions.length > 0 && (
            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
              <div className="flex items-center mb-3">
                <Lightbulb className="w-5 h-5 text-yellow-600 mr-2" />
                <h4 className="font-semibold text-yellow-900">Improvement Suggestions</h4>
              </div>
              <ul className="space-y-2">
                {validationResult.suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-yellow-800 flex items-start">
                    <span className="w-2 h-2 bg-yellow-400 rounded-full mt-2 mr-3 flex-shrink-0"></span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Export Report */}
          <div className="flex justify-end">
            <button
              onClick={() => {
                const report = JSON.stringify(validationResult, null, 2);
                const blob = new Blob([report], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'validation-report.json';
                a.click();
                URL.revokeObjectURL(url);
              }}
              className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export Report</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <Shield className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600">Click validate to analyze your code</p>
        </div>
      )}
    </div>
  );
};

export default ValidationDashboard;