export default function ResultLinks({ wireframeUrl, deployUrl, githubRepo, codeUrl }) {
  const links = [
    {
      url: wireframeUrl,
      label: 'View Wireframe',
      icon: '🎨',
      description: 'Design mockup',
      color: 'purple'
    },
    {
      url: codeUrl || (githubRepo && `https://github.com/${githubRepo}`),
      label: 'View Code',
      icon: '📂',
      description: 'Source repository',
      color: 'gray'
    },
    {
      url: deployUrl,
      label: 'Live Demo',
      icon: '🚀',
      description: 'Deployed application',
      color: 'green'
    }
  ].filter(link => link.url);

  if (links.length === 0) return null;

  return (
    <div className="mt-6">
      <h4 className="text-sm font-semibold text-gray-700 mb-3">Generated Resources</h4>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {links.map((link, idx) => (
          <a
            key={idx}
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className={`group flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-all duration-200 ${
              link.color === 'purple' ? 'hover:border-purple-300 hover:bg-purple-50' :
              link.color === 'green' ? 'hover:border-green-300 hover:bg-green-50' :
              'hover:border-gray-300 hover:bg-gray-50'
            }`}
          >
            <div className="text-2xl">{link.icon}</div>
            <div className="flex-1">
              <div className={`font-medium ${
                link.color === 'purple' ? 'text-purple-700 group-hover:text-purple-800' :
                link.color === 'green' ? 'text-green-700 group-hover:text-green-800' :
                'text-gray-700 group-hover:text-gray-800'
              }`}>
                {link.label}
              </div>
              <div className="text-sm text-gray-500">{link.description}</div>
            </div>
            <svg className="w-4 h-4 text-gray-400 group-hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </a>
        ))}
      </div>
    </div>
  );
}