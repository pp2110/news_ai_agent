import React from 'react';
import { ExternalLink, Calendar, Newspaper } from 'lucide-react';
import { Article } from '../types';

interface ArticleCardProps {
  article: Article;
}

const ArticleCard: React.FC<ArticleCardProps> = ({ article }) => {
  const formattedDate = new Date(article.date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  return (
    <a
      href={article.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden"
    >
      <div className="p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-3 flex items-start justify-between">
          <span>{article.title}</span>
          <ExternalLink className="w-5 h-5 text-blue-600 flex-shrink-0 ml-2" />
        </h3>
        <p className="text-gray-600 mb-4">{article.content}</p>
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4" />
            <span>{formattedDate}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Newspaper className="w-4 h-4" />
            <span>{article.source}</span>
          </div>
        </div>
      </div>
    </a>
  );
};

export default ArticleCard;