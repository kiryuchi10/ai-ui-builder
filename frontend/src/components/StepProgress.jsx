export default function StepProgress({ steps, currentStep }) {
  return (
    <div className="flex justify-between items-center my-8 px-4">
      {steps.map((step, idx) => {
        const isActive = idx === currentStep;
        const isDone = idx < currentStep;
        const isUpcoming = idx > currentStep;

        return (
          <div key={step.name} className="flex flex-col items-center flex-1">
            <div
              className={`rounded-full w-12 h-12 flex items-center justify-center border-2 transition-all duration-300 ${
                isDone 
                  ? 'border-green-500 bg-green-50 text-green-600' :
                isActive 
                  ? 'border-blue-500 bg-blue-50 text-blue-600' :
                  'border-gray-300 bg-white text-gray-400'
              }`}
            >
              {isDone ? (
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              ) : isActive ? (
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              ) : (
                <span className="text-sm font-medium">{idx + 1}</span>
              )}
            </div>
            <p className={`text-sm mt-2 text-center max-w-20 ${
              isActive ? 'text-blue-600 font-medium' : 
              isDone ? 'text-green-600' : 
              'text-gray-500'
            }`}>
              {step.name}
            </p>
            {idx < steps.length - 1 && (
              <div className={`absolute h-0.5 w-full mt-6 ${
                isDone ? 'bg-green-500' : 'bg-gray-300'
              }`} style={{ 
                left: '50%', 
                width: 'calc(100% - 3rem)',
                zIndex: -1 
              }} />
            )}
          </div>
        );
      })}
    </div>
  );
}