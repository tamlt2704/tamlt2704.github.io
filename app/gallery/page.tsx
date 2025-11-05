'use client';

import Image from "next/image";
import { useState } from "react";

const photos = [
  { id: 1, src: "/next.svg", alt: "Next.js Logo", caption: "Next.js - The React Framework", date: "2024-01-15", size: "large", tags: ["web", "framework"] },
  { id: 2, src: "/vercel.svg", alt: "Vercel Logo", caption: "Vercel - Deploy with Confidence", date: "2024-02-20", size: "medium", tags: ["deployment", "web"] },
  { id: 3, src: "/file.svg", alt: "File Icon", caption: "Document Management System", date: "2024-03-10", size: "small", tags: ["document", "system"] },
  { id: 4, src: "/globe.svg", alt: "Globe Icon", caption: "Global Network Connection", date: "2024-04-05", size: "large", tags: ["network", "global"] },
  { id: 5, src: "/window.svg", alt: "Window Icon", caption: "Modern UI Components", date: "2024-05-12", size: "medium", tags: ["ui", "design"] },
];

const allTags = [...new Set(photos.flatMap(photo => photo.tags))];

const getSizeClass = (size: string) => {
  switch (size) {
    case 'small': return 'col-span-1 row-span-1';
    case 'medium': return 'col-span-1 row-span-2';
    case 'large': return 'col-span-2 row-span-2';
    default: return 'col-span-1 row-span-1';
  }
};

export default function Gallery() {
  const [selectedPhoto, setSelectedPhoto] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'timeline'>('grid');
  const [selectedTag, setSelectedTag] = useState<string>('all');
  
  const filteredPhotos = selectedTag === 'all' 
    ? photos 
    : photos.filter(photo => photo.tags.includes(selectedTag));
  
  const sortedPhotos = [...filteredPhotos].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">
            Photo Gallery
          </h1>
          
          <div className="flex flex-wrap gap-2 mb-4">
            <button
              onClick={() => setSelectedTag('all')}
              className={`px-3 py-1 rounded-full text-sm transition-colors ${
                selectedTag === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              All
            </button>
            {allTags.map(tag => (
              <button
                key={tag}
                onClick={() => setSelectedTag(tag)}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  selectedTag === tag
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                viewMode === 'grid'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('timeline')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                viewMode === 'timeline'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              Timeline
            </button>
          </div>
        </div>
        
        {viewMode === 'grid' ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {filteredPhotos.map((photo) => (
            <div
              key={photo.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden cursor-pointer hover:scale-105 transition-transform"
              onClick={() => setSelectedPhoto(photo.id)}
            >
              <div className="aspect-square relative">
                <Image
                  src={photo.src}
                  alt={photo.alt}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="p-2">
                <p className="text-xs text-gray-800 dark:text-gray-200 font-medium truncate">
                  {photo.caption}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(photo.date).toLocaleDateString()}
                </p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {photo.tags.map(tag => (
                    <span key={tag} className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-1 rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-blue-600"></div>
              {sortedPhotos.map((photo, index) => (
                <div key={photo.id} className="relative flex items-center mb-8">
                  <div className="absolute left-6 w-4 h-4 bg-blue-600 rounded-full border-4 border-white dark:border-gray-900"></div>
                  <div className="ml-16 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 flex gap-4 cursor-pointer hover:shadow-xl transition-shadow"
                       onClick={() => setSelectedPhoto(photo.id)}>
                    <div className="w-24 h-24 relative flex-shrink-0">
                      <Image
                        src={photo.src}
                        alt={photo.alt}
                        fill
                        className="object-cover rounded-lg"
                      />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                        {photo.caption}
                      </h3>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                        {new Date(photo.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {photo.tags.map(tag => (
                          <span key={tag} className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {selectedPhoto && (
          <div
            className="fixed inset-0 bg-black/80 flex items-center justify-center z-50"
            onClick={() => setSelectedPhoto(null)}
          >
            <div className="max-w-4xl max-h-full p-4">
              <Image
                src={photos.find(p => p.id === selectedPhoto)?.src || ""}
                alt={photos.find(p => p.id === selectedPhoto)?.alt || ""}
                width={800}
                height={600}
                className="max-w-full max-h-full object-contain mb-4"
              />
              <div className="text-white text-center">
                <p className="text-lg mb-2">
                  {photos.find(p => p.id === selectedPhoto)?.caption}
                </p>
                <p className="text-sm text-gray-300 mb-2">
                  {new Date(photos.find(p => p.id === selectedPhoto)?.date || '').toLocaleDateString()}
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {photos.find(p => p.id === selectedPhoto)?.tags.map(tag => (
                    <span key={tag} className="text-sm bg-blue-600 text-white px-3 py-1 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}