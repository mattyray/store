'use client';

import { useCallback, useState } from 'react';

interface WallUploaderProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
}

export default function WallUploader({ onUpload, isUploading }: WallUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);

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

  return (
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
  );
}
