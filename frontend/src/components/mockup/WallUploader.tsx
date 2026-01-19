'use client';

import { useCallback, useState } from 'react';
import Image from 'next/image';

// Sample wall configurations - images stored in /public/sample-walls/
const SAMPLE_WALLS = [
  {
    id: 'modern-living',
    name: 'Modern Living Room',
    image: '/sample-walls/modern-living.jpg',
    description: 'Clean white wall with sofa',
  },
  {
    id: 'cozy-bedroom',
    name: 'Cozy Bedroom',
    image: '/sample-walls/cozy-bedroom.jpg',
    description: 'Bedroom with neutral tones',
  },
  {
    id: 'minimal-office',
    name: 'Minimal Office',
    image: '/sample-walls/minimal-office.jpg',
    description: 'Home office space',
  },
  {
    id: 'gallery-wall',
    name: 'Gallery Wall',
    image: '/sample-walls/gallery-wall.jpg',
    description: 'White wall ready for art',
  },
];

interface WallUploaderProps {
  onUpload: (file: File) => void;
  onSelectSampleWall?: (wallUrl: string) => void;
  isUploading: boolean;
}

export default function WallUploader({ onUpload, onSelectSampleWall, isUploading }: WallUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [showSamples, setShowSamples] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        onUpload(file);
      }
    },
    [onUpload]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        onUpload(file);
      }
    },
    [onUpload]
  );

  const handleSampleSelect = useCallback(
    async (wallUrl: string) => {
      if (onSelectSampleWall) {
        onSelectSampleWall(wallUrl);
      }
    },
    [onSelectSampleWall]
  );

  if (showSamples) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
            Choose a Sample Room
          </h3>
          <button
            onClick={() => setShowSamples(false)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            Upload your own instead
          </button>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {SAMPLE_WALLS.map((wall) => (
            <button
              key={wall.id}
              onClick={() => handleSampleSelect(wall.image)}
              disabled={isUploading}
              className="relative aspect-[4/3] rounded-lg overflow-hidden border-2 border-transparent hover:border-blue-500 transition group disabled:opacity-50"
            >
              <Image
                src={wall.image}
                alt={wall.name}
                fill
                className="object-cover"
                sizes="(max-width: 768px) 50vw, 200px"
                unoptimized
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              <div className="absolute bottom-0 left-0 right-0 p-2 text-left">
                <p className="text-sm font-medium text-white">{wall.name}</p>
                <p className="text-xs text-gray-200">{wall.description}</p>
              </div>
            </button>
          ))}
        </div>

        {isUploading && (
          <div className="flex items-center justify-center gap-2 text-gray-600 dark:text-gray-400">
            <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
            <span>Loading...</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragging
            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
          }
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
        `}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
      >
        {isUploading ? (
          <div className="flex flex-col items-center gap-4">
            <div className="w-10 h-10 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin" />
            <p className="text-gray-600 dark:text-gray-400">Uploading...</p>
          </div>
        ) : (
          <>
            <div className="mb-4">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>

            <p className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">
              Upload a photo of your wall
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
              Drag and drop or click to select
            </p>

            <label className="inline-block">
              <span className="px-6 py-2 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 rounded cursor-pointer hover:bg-gray-800 dark:hover:bg-gray-200 transition">
                Choose File
              </span>
              <input
                type="file"
                accept="image/*"
                capture="environment"
                onChange={handleFileSelect}
                className="hidden"
              />
            </label>

            <p className="text-xs text-gray-400 dark:text-gray-500 mt-4">
              Supports JPEG, PNG, WebP up to 10MB
            </p>
          </>
        )}
      </div>

      {/* Sample walls option */}
      {onSelectSampleWall && !isUploading && (
        <div className="text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
            Don&apos;t have a wall photo?
          </p>
          <button
            onClick={() => setShowSamples(true)}
            className="text-sm text-blue-600 dark:text-blue-400 hover:underline font-medium"
          >
            Use a sample room instead
          </button>
        </div>
      )}
    </div>
  );
}
