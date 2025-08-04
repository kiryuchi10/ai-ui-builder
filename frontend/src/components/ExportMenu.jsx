import { useState } from 'react';
import { Download, ExternalLink, Loader2, CheckCircle } from 'lucide-react';

export default function ExportMenu({ generatedCode, componentName = "GeneratedComponent", isDisabled = false }) {
  const [isOpen] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState({});

  const exportOptions = [
    { value: 'react-app', label: 'Complete React App', icon: '⚛️', description: 'Full project with dependencies', popular: true },
    { value: 'component', label: 'React Component', icon: '🧩', description: 'Single component file' },
    { value: 'html', label: 'Static HTML', icon: '🌐', description: 'HTML with inline CSS' },
    { value: 'json', label: 'JSON Schema', icon: '📋', description: 'Component structure data' },
    { value: 'figma', label: 'Figma Design Tokens', icon: '🎨', description: 'Design tokens for Figma' }
  ];

  const deploymentOptions = [
    { value: 'vercel', label: 'Deploy to Vercel', icon: '▲', description: 'Deploy to Vercel platform' },
    { value: 'netlify', label: 'Deploy to Netlify', icon: '🌐', description: 'Deploy to Netlify platform' },
    { value: 'render', label: 'Deploy to Render', icon: '🚀', description: 'Deploy to Render platform' },
    { value: 'github-pages', label: 'GitHub Pages', icon: '📄', description: 'Deploy to GitHub Pages' }
  ];

  const handleExport = async (exportType) => {
    if (!generatedCode) {
      alert('Please generate code first');
      return;
    }

    setIsExporting(true);
    setExportStatus(prev => ({ ...prev, [exportType]: 'loading' }));

    try {
      const response = await fetch('/api/v1/export/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: generatedCode,
          component_name: componentName,
          export_type: exportType,
          options: {
            include_tests: true,
            include_storybook: exportType === 'react-app',
            include_router: exportType === 'react-app'
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const result = await response.json();
      
      if (result.download_url) {
        // Trigger download
        const link = document.createElement('a');
        link.href = result.download_url;
        link.download = `${componentName}-${exportType}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else if (result.files) {
        // Download individual files
        Object.entries(result.files).forEach(([filename, content]) => {
          const blob = new Blob([content], { type: 'text/plain' });
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        });
      }

      setExportStatus(prev => ({ ...prev, [exportType]: 'success' }));
      
      // Reset status after 3 seconds
      setTimeout(() => {
        setExportStatus(prev => ({ ...prev, [exportType]: null }));
      }, 3000);

    } catch (error) {
      console.error('Export failed:', error);
      setExportStatus(prev => ({ ...prev, [exportType]: 'error' }));
      alert('Export failed. Please try again.');
      
      setTimeout(() => {
        setExportStatus(prev => ({ ...prev, [exportType]: null }));
      }, 3000);
    } finally {
      setIsExporting(false);
    }
  };

  const handleDeploy = async (platform) => {
    if (!generatedCode) {
      alert('Please generate code first');
      return;
    }

    setIsExporting(true);
    setExportStatus(prev => ({ ...prev, [platform]: 'loading' }));

    try {
      const response = await fetch('/api/v1/export/deploy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: generatedCode,
          component_name: componentName,
          platform: platform,
          config: {}
        }),
      });

      if (!response.ok) {
        throw new Error('Deployment failed');
      }

      const result = await response.json();
      
      if (result.deployment_url) {
        // Open deployment URL
        window.open(result.deployment_url, '_blank');
      }

      setExportStatus(prev => ({ ...prev, [platform]: 'success' }));
      
      setTimeout(() => {
        setExportStatus(prev => ({ ...prev, [platform]: null }));
      }, 3000);

    } catch (error) {
      console.error('Deployment failed:', error);
      setExportStatus(prev => ({ ...prev, [platform]: 'error' }));
      alert('Deployment failed. Please try again.');
      
      setTimeout(() => {
        setExportStatus(prev => ({ ...prev, [platform]: null }));
      }, 3000);
    } finally {
      setIsExporting(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'loading': return <Loader2 className="w-4 h-4 animate-spin" />;
      case 'success': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'error': return <div className="w-4 h-4 bg-red-500 rounded-full" />;
      default: return null;
    }
  };

  if (isDisabled && !generatedCode) return null;

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="p-2 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg mr-3">
            <Download className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Export & Deploy</h3>
            <p className="text-gray-600 text-sm">Download or deploy your generated UI</p>
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="space-y-6">
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Download className="w-5 h-5 mr-2 text-green-600" />
            Export Options
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {exportOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleExport(option.value)}
                disabled={isExporting || !generatedCode}
                className="relative flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-green-300 hover:shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                {option.popular && (
                  <div className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                    Popular
                  </div>
                )}
                
                <span className="text-2xl">{option.icon}</span>
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium text-gray-900 group-hover:text-green-600">
                    {option.label}
                  </div>
                  <div className="text-xs text-gray-500">{option.description}</div>
                </div>
                
                <div className="flex items-center">
                  {getStatusIcon(exportStatus[option.value])}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Deployment Options */}
        <div>
          <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <ExternalLink className="w-5 h-5 mr-2 text-blue-600" />
            One-Click Deploy
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {deploymentOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleDeploy(option.value)}
                disabled={isExporting || !generatedCode}
                className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
              >
                <span className="text-2xl">{option.icon}</span>
                <div className="flex-1 text-left">
                  <div className="text-sm font-medium text-gray-900 group-hover:text-blue-600">
                    {option.label}
                  </div>
                  <div className="text-xs text-gray-500">{option.description}</div>
                </div>
                
                <div className="flex items-center">
                  {getStatusIcon(exportStatus[option.value])}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Status Message */}
        {!generatedCode && (
          <div className="text-center py-6 bg-gray-50 rounded-lg border border-gray-200">
            <Download className="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-600 font-medium">Generate code first to enable export options</p>
            <p className="text-gray-400 text-sm">Your UI will be ready for download and deployment</p>
          </div>
        )}
      </div>
    </div>
  );
}