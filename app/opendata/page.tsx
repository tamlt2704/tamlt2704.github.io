'use client';

import { useState } from 'react';

const sampleData = [
  { id: 1, name: 'Population', value: 8500000, category: 'Demographics' },
  { id: 2, name: 'GDP', value: 1200000, category: 'Economy' },
  { id: 3, name: 'Temperature', value: 22, category: 'Environment' },
  { id: 4, name: 'Unemployment', value: 5.2, category: 'Economy' },
  { id: 5, name: 'Education Budget', value: 450000, category: 'Education' },
];

const categories = ['All', ...new Set(sampleData.map(item => item.category))];

export default function OpenData() {
  const [selectedCategory, setSelectedCategory] = useState('All');
  
  const filteredData = selectedCategory === 'All' 
    ? sampleData 
    : sampleData.filter(item => item.category === selectedCategory);

  const maxValue = Math.max(...sampleData.map(item => item.value));

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-6">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8 text-center">
          Open Data Visualization
        </h1>
        
        <div className="flex flex-wrap gap-2 mb-8 justify-center">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg transition-colors ${
                selectedCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Bar Chart
            </h2>
            <div className="space-y-4">
              {filteredData.map(item => (
                <div key={item.id} className="flex items-center gap-4">
                  <div className="w-24 text-sm text-gray-600 dark:text-gray-400 truncate">
                    {item.name}
                  </div>
                  <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-6 relative">
                    <div
                      className="bg-blue-600 h-6 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${(item.value / maxValue) * 100}%` }}
                    >
                      <span className="text-white text-xs font-medium">
                        {item.value.toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
              Data Table
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-2 text-gray-900 dark:text-white">Name</th>
                    <th className="text-left py-2 text-gray-900 dark:text-white">Value</th>
                    <th className="text-left py-2 text-gray-900 dark:text-white">Category</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredData.map(item => (
                    <tr key={item.id} className="border-b border-gray-100 dark:border-gray-800">
                      <td className="py-2 text-gray-700 dark:text-gray-300">{item.name}</td>
                      <td className="py-2 text-gray-700 dark:text-gray-300">{item.value.toLocaleString()}</td>
                      <td className="py-2">
                        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                          {item.category}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
            Statistics
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{filteredData.length}</div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Total Items</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {Math.max(...filteredData.map(item => item.value)).toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Max Value</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">
                {Math.min(...filteredData.map(item => item.value)).toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Min Value</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {Math.round(filteredData.reduce((sum, item) => sum + item.value, 0) / filteredData.length).toLocaleString()}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">Average</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}