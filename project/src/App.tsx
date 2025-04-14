import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Search, ArrowLeft } from 'lucide-react';
import { NewsResponse } from './types';
import TopicCard from './components/TopicCard';
import ArticleCard from './components/ArticleCard';
import LoadingSpinner from './components/LoadingSpinner';

const PREDEFINED_TOPICS = ['Politics', 'Technology', 'Sports', 'Entertainment', 'Finance Update'];

function App() {
  const [topic, setTopic] = useState('');
  const [newsData, setNewsData] = useState<NewsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchNews = async (searchTopic: string) => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.post('http://localhost:8000/api/v1/process-news/', {
        topic: searchTopic,
      });
      setNewsData(response.data);
      if (response.data.status === 'failed') {
        setError('Error fetching news. Please try again.');
      }
    } catch (err) {
      setError('Failed to fetch news. Please try again later.');
      setNewsData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (topic.trim()) {
      fetchNews(topic);
    }
  };

  const handleReset = () => {
    setNewsData(null);
    setTopic('');
    setError('');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <LoadingSpinner />
      </div>
    );
  }

  if (newsData && newsData.status === 'completed') {
    return (
      <div className="min-h-screen bg-gray-100 p-4 md:p-8">
        <button
          onClick={handleReset}
          className="mb-6 flex items-center text-blue-600 hover:text-blue-800 transition-colors"
        >
          <ArrowLeft className="w-5 h-5 mr-2" />
          Back to Search
        </button>
        
        <div className="max-w-4xl mx-auto space-y-8">
          <h1 className="text-3xl font-bold text-gray-800">
            News Results for "{newsData.topic}"
          </h1>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="prose max-w-none">
              <ReactMarkdown>{newsData.summary}</ReactMarkdown>
            </div>
          </div>

          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-gray-800">Related Articles</h2>
            <div className="grid gap-6">
              {newsData.articles.map((article, index) => (
                <ArticleCard key={index} article={article} />
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-12">
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-800">News Explorer</h1>
          <p className="text-lg text-gray-600">
            Discover the latest news on any topic that interests you
          </p>
        </div>

        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Enter a topic to search..."
            className="w-full px-6 py-4 text-lg rounded-lg shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-blue-600 hover:text-blue-800"
          >
            <Search className="w-6 h-6" />
          </button>
        </form>

        {error && (
          <div className="text-red-600 text-center p-4 bg-red-50 rounded-lg">
            {error}
          </div>
        )}

        <div className="space-y-6">
          <h2 className="text-2xl font-semibold text-gray-800 text-center">
            Popular Topics
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {PREDEFINED_TOPICS.map((topic) => (
              <TopicCard
                key={topic}
                topic={topic}
                onSelect={(selectedTopic) => fetchNews(selectedTopic)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;