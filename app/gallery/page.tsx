'use client';

import Image from "next/image";
import { useState } from "react";

const photos = [
  { id: 1, src: "/next.svg", alt: "Photo 1" },
  { id: 2, src: "/vercel.svg", alt: "Photo 2" },
  { id: 3, src: "/file.svg", alt: "Photo 3" },
  { id: 4, src: "/globe.svg", alt: "Photo 4" },
  { id: 5, src: "/window.svg", alt: "Photo 5" },
];

export default function Gallery() {
  const [selectedPhoto, setSelectedPhoto] = useState<number | null>(null);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-6">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8 text-center">
          Photo Gallery
        </h1>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {photos.map((photo) => (
            <div
              key={photo.id}
              className="aspect-square bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden cursor-pointer hover:scale-105 transition-transform"
              onClick={() => setSelectedPhoto(photo.id)}
            >
              <Image
                src={photo.src}
                alt={photo.alt}
                width={300}
                height={300}
                className="w-full h-full object-cover"
              />
            </div>
          ))}
        </div>

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
                className="max-w-full max-h-full object-contain"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}