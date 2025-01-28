import React, { useState } from 'react';
import { Search, Newspaper, ArrowLeft, Gamepad2, Globe2, Cpu, Clapperboard } from 'lucide-react';

interface NewsItem {
  headline: string;
  summary: string;
  source: string;
  url: string;
  date?: string;
  image_url?: string;
}

interface Category {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  imageUrl: string;
}

function App() {
  const [searchTopic, setSearchTopic] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<NewsItem[]>([]);
  const [activeView, setActiveView] = useState<'categories' | 'results'>('categories');
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const categories: Category[] = [
    {
      id: 'sports',
      name: 'Sports',
      icon: <Gamepad2 className="h-6 w-6" />,
      description: 'Latest updates from the world of sports',
      imageUrl: 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?auto=format&fit=crop&q=80&w=800'
    },
    {
      id: 'politics',
      name: 'International Politics',
      icon: <Globe2 className="h-6 w-6" />,
      description: 'Global political news and analysis',
      imageUrl: 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&q=80&w=800'
    },
    {
      id: 'technology',
      name: 'Technology',
      icon: <Cpu className="h-6 w-6" />,
      description: 'Latest tech innovations and updates',
      imageUrl: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=800'
    },
    {
      id: 'hollywood',
      name: 'Hollywood',
      icon: <Clapperboard className="h-6 w-6" />,
      description: 'Entertainment news and celebrity updates',
      imageUrl: 'https://images.unsplash.com/photo-1616469829581-73993eb86b02?auto=format&fit=crop&q=80&w=800'
    }
  ];

  const fetchNews = async (topic: string) => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/news', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch news');
      }

      const data = await response.json();
      return JSON.parse(data.news_summary);
    } catch (error) {
      console.error('Error fetching news:', error);
      return [];
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchTopic.trim()) return;
    console.log(searchTopic.trim())
    setIsLoading(true);
    setActiveView('results');
    setActiveCategory(null);
    
    const newsResults = await fetchNews(searchTopic);
    setResults(newsResults);
    setIsLoading(false);
  };

  const handleCategoryClick = async (categoryId: string) => {
    setIsLoading(true);
    setActiveView('results');
    setActiveCategory(categoryId);
    setSearchTopic('');

    const newsResults = await fetchNews(categoryId);
    setResults(newsResults);
    setIsLoading(false);
  };

  const handleBackToCategories = () => {
    setActiveView('categories');
    setActiveCategory(null);
    setResults([]);
    setSearchTopic('');
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-center space-x-3">
            <Newspaper className="h-8 w-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">NewsAI</h1>
          </div>
        </div>
      </header>

      {/* Search Section */}
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <form onSubmit={handleSearch} className="relative">
          <input
            type="text"
            value={searchTopic}
            onChange={(e) => setSearchTopic(e.target.value)}
            placeholder="Enter a topic to search news..."
            className="w-full px-4 py-3 pl-12 text-lg rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <button
            type="submit"
            className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Search
          </button>
        </form>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {activeView === 'results' && (
          <div className="mb-8">
            <button
              onClick={handleBackToCategories}
              className="inline-flex items-center text-blue-600 hover:text-blue-800"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Categories
            </button>
          </div>
        )}

        {isLoading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : activeView === 'categories' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {categories.map((category) => (
              <div
                key={category.id}
                onClick={() => handleCategoryClick(category.id)}
                className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer group"
              >
                <div className="relative">
                  <img
                    src={category.imageUrl}
                    alt={category.name}
                    className="w-full h-48 object-cover group-hover:opacity-90 transition-opacity duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent to-black/60" />
                  <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
                    <div className="flex items-center space-x-3 mb-2">
                      {category.icon}
                      <h3 className="text-xl font-bold">{category.name}</h3>
                    </div>
                    <p className="text-sm text-gray-200">{category.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {results.map((item, index) => (
              <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
                {item.image_url && (
                  <div className="relative h-48 overflow-hidden">
                    <img
                      src={item.image_url}
                      alt={item.headline}
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                      }}
                    />
                  </div>
                )}
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium text-blue-600">{item.source}</span>
                    {item.date && (
                      <span className="text-xs text-gray-500">{formatDate(item.date)}</span>
                    )}
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2 hover:text-blue-600 transition-colors">
                    <a href={item.url} target="_blank" rel="noopener noreferrer">
                      {item.headline}
                    </a>
                  </h3>
                  <p className="text-gray-600 text-sm mb-4 line-clamp-3">{item.summary}</p>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Read more →
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;