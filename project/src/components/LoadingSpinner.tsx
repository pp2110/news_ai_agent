import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center space-y-4">
      <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
      <p className="text-lg font-medium text-gray-600">Gathering the latest news for you...</p>
    </div>
  );
};

export default LoadingSpinner;