import React, { useState, useEffect } from 'react';
import { Search, Clock, Star, Tag, Filter, Download, Trash2, Copy, Edit3, MoreVertical } from 'lucide-react';

const PromptMemory = ({ onSelectPrompt, currentPrompt }) => {
  const [prompts, setPrompts] = useState([]);
  const [filteredPrompts, setFilteredPrompts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [favorites, setFavorites] = useState(new Set());
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // Mock categories - in production, these would come from the API
  const categories = [
    { id: 'all', name: 'All Prompts', count: 0 },
    { id: 'dashboard', name: 'Dashboards', count: 0 },
    { id: 'landing', name: 'Landing Pages', count: 0 },
    { id: 'ecommerce', name: 'E-commerce', count: 0 },
    { id: 'blog', name: 'Blogs', count: 0 },
    { id: 'forms', name: 'Forms', count: 0 }
  ];

  useEffect(() => {
    loadPromptHistory();
  }, []);

  useEffect(() => {
    filterAndSortPrompts();
  }, [prompts, searchTerm, selectedCategory, sortBy]);

  const loadPromptHistory = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/v1/history/user123'); // Replace with actual user ID
      if (response.ok) {
        const data = await response.json();
        setPrompts(data.history || []);
      }
    } catch (error) {
      console.error('Failed to load prompt history:', error);
      // Mock data for development
      setPrompts([
        {
          id: 1,
          prompt: "Create a modern SaaS dashboard with dark theme, interactive charts, and user management",
          category: 'dashboard',
          timestamp: new Date(Date.now() - 86400000).toISOString(),
          status: 'success',
          tags: ['dashboard', 'dark-theme', 'charts'],
          generation_time: 45,
          usage_count: 3
        },
        {
          id: 2,
          prompt: "Design a landing page for a fintech startup with hero section and testimonials",
          category: 'landing',
          timestamp: new Date(Date.now() - 172800000).toISOString(),
          status: 'success',
          tags: ['landing', 'fintech', 'hero'],
          generation_time: 32,
          usage_count: 1
        },
        {
          id: 3,
          prompt: "Build an e-commerce product page with image gallery and reviews section",
          category: 'ecommerce',
          timestamp: new Date(Date.now() - 259200000).toISOString(),
          status: 'error',
          tags: ['ecommerce', 'product', 'gallery'],
          generation_time: 0,
          usage_count: 0
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const filterAndSortPrompts = () => {
    let filtered = prompts;

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(prompt => 
        prompt.prompt.toLowerCase().includes(searchTerm.toLowerCase()) ||
        prompt.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(prompt => prompt.category === selectedCategory);
    }

    // Sort prompts
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return new Date(b.timestamp) - new Date(a.timestamp);
        case 'oldest':
          return new Date(a.timestamp) - new Date(b.timestamp);
        case 'most-used':
          return b.usage_count - a.usage_count;
        case 'fastest':
          return a.generation_time - b.generation_time;
        case 'alphabetical':
          return a.prompt.localeCompare(b.prompt);
        default:
          return 0;
      }
    });

    setFilteredPrompts(filtered);
  };

  const toggleFavorite = (promptId) => {
    const newFavorites = new Set(favorites);
    if (newFavorites.has(promptId)) {
      newFavorites.delete(promptId);
    } else {
      newFavorites.add(promptId);
    }
    setFavorites(newFavorites);
  };

  const copyPrompt = (prompt) => {
    navigator.clipboard.writeText(prompt);
    // Show toast notification
  };

  const deletePrompt = async (promptId) => {
    if (window.confirm('Are you sure you want to delete this prompt?')) {
      try {
        await fetch(`/api/v1/history/${promptId}`, { method: 'DELETE' });
        setPrompts(prompts.filter(p => p.id !== promptId));
      } catch (error) {
        console.error('Failed to delete prompt:', error);
      }
    }
  };

  const exportPrompts = () => {
    const dataStr = JSON.stringify(filteredPrompts, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'prompt-history.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-800';
      case 'error': return 'bg-red-100 text-red-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category) => {
    const icons = {
      dashboard: '📊',
      landing: '🚀',
      ecommerce: '🛒',
      blog: '📝',
      forms: '📋'
    };
    return icons[category] || '💡';
  };

  return (
    <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg mr-3">
            <Clock className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">Prompt Memory</h3>
            <p className="text-gray-600 text-sm">Smart history with context awareness</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 rounded-lg transition-colors ${
              showFilters ? 'bg-purple-100 text-purple-600' : 'text-gray-400 hover:text-gray-600'
            }`}
          >
            <Filter className="w-5 h-5" />
          </button>
          <button
            onClick={exportPrompts}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
          >
            <Download className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4 mb-6">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            placeholder="Search prompts, tags, or categories..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200"
          />
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="bg-gray-50 rounded-lg p-4 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              {/* Sort Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="recent">Most Recent</option>
                  <option value="oldest">Oldest First</option>
                  <option value="most-used">Most Used</option>
                  <option value="fastest">Fastest Generation</option>
                  <option value="alphabetical">Alphabetical</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Prompt List */}
      <div className="space-y-3">
        {isLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
            <p className="text-gray-600 mt-2">Loading prompt history...</p>
          </div>
        ) : filteredPrompts.length === 0 ? (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-600">No prompts found</p>
            <p className="text-gray-400 text-sm">Try adjusting your search or filters</p>
          </div>
        ) : (
          filteredPrompts.map((prompt) => (
            <div
              key={prompt.id}
              className="border border-gray-200 rounded-lg p-4 hover:border-purple-300 hover:shadow-md transition-all duration-200 group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  {/* Prompt Text */}
                  <button
                    onClick={() => onSelectPrompt(prompt)}
                    className="text-left w-full group-hover:text-purple-600 transition-colors"
                  >
                    <p className="text-gray-900 font-medium line-clamp-2 mb-2">
                      {prompt.prompt}
                    </p>
                  </button>

                  {/* Metadata */}
                  <div className="flex items-center space-x-4 text-sm text-gray-500 mb-3">
                    <div className="flex items-center">
                      <span className="mr-1">{getCategoryIcon(prompt.category)}</span>
                      <span className="capitalize">{prompt.category}</span>
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      <span>{new Date(prompt.timestamp).toLocaleDateString()}</span>
                    </div>
                    {prompt.generation_time > 0 && (
                      <div className="flex items-center">
                        <span>⚡ {prompt.generation_time}s</span>
                      </div>
                    )}
                    {prompt.usage_count > 0 && (
                      <div className="flex items-center">
                        <span>🔄 {prompt.usage_count}x</span>
                      </div>
                    )}
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {prompt.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>

                  {/* Status */}
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(prompt.status)}`}>
                      {prompt.status}
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => toggleFavorite(prompt.id)}
                    className={`p-2 rounded-lg transition-colors ${
                      favorites.has(prompt.id)
                        ? 'text-yellow-500 hover:text-yellow-600'
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <Star className={`w-4 h-4 ${favorites.has(prompt.id) ? 'fill-current' : ''}`} />
                  </button>
                  <button
                    onClick={() => copyPrompt(prompt.prompt)}
                    className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
                  >
                    <Copy className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => deletePrompt(prompt.id)}
                    className="p-2 text-gray-400 hover:text-red-600 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Context Awareness Section */}
      {currentPrompt && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center mb-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
            <h4 className="font-medium text-blue-900">Context-Aware Suggestions</h4>
          </div>
          <p className="text-blue-800 text-sm mb-3">
            Based on your current prompt, here are similar prompts from your history:
          </p>
          <div className="space-y-2">
            {filteredPrompts
              .filter(p => p.prompt !== currentPrompt)
              .slice(0, 2)
              .map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => onSelectPrompt(suggestion)}
                  className="block w-full text-left p-2 bg-white rounded border border-blue-200 hover:border-blue-300 transition-colors"
                >
                  <p className="text-sm text-gray-700 line-clamp-1">{suggestion.prompt}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    Used {suggestion.usage_count}x • {suggestion.category}
                  </p>
                </button>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PromptMemory;