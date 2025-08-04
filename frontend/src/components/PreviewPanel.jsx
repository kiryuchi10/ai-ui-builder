export default function PreviewPanel({ prompt, previewData }) {
  return (
    <div className="border border-gray-200 rounded-lg p-6 bg-gradient-to-br from-gray-50 to-white shadow-sm mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-800">UI Preview</h3>
        <div className="flex space-x-1">
          <div className="w-3 h-3 bg-red-400 rounded-full"></div>
          <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
          <div className="w-3 h-3 bg-green-400 rounded-full"></div>
        </div>
      </div>
      
      {previewData ? (
        <div className="space-y-4">
          <div className="p-4 bg-white border border-gray-200 rounded-lg">
            <div className="text-sm text-gray-600 mb-2">Generated UI Structure:</div>
            <div className="text-gray-800">{previewData.structure || 'Component structure will appear here'}</div>
          </div>
          
          {previewData.features && (
            <div className="grid grid-cols-2 gap-3">
              {previewData.features.map((feature, idx) => (
                <div key={idx} className="flex items-center space-x-2 p-2 bg-blue-50 rounded-md">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-blue-800">{feature}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 rounded-lg flex items-center justify-center">
            <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <p className="text-gray-500 mb-2">Preview will appear here</p>
          {prompt && (
            <div className="text-sm text-gray-600 bg-gray-100 rounded-md p-3 max-w-md mx-auto">
              <span className="font-medium">Building: </span>
              "{prompt}"
            </div>
          )}
        </div>
      )}
    </div>
  );
}