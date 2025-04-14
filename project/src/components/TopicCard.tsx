import React from 'react';
import { Newspaper } from 'lucide-react';

interface TopicCardProps {
  topic: string;
  onSelect: (topic: string) => void;
}

const TopicCard: React.FC<TopicCardProps> = ({ topic, onSelect }) => {
  return (
    <button
      onClick={() => onSelect(topic)}
      className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 flex flex-col items-center space-y-3 w-full"
    >
      <Newspaper className="w-8 h-8 text-blue-600" />
      <span className="text-lg font-semibold text-gray-800">{topic}</span>
    </button>
  );
};

export default TopicCard;