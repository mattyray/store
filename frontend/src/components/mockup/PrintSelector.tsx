'use client';

import Image from 'next/image';
import type { Photo, ProductVariant } from '@/types';

interface PrintSelectorProps {
  photos: Photo[];
  selectedPhoto: Photo | null;
  selectedVariant: ProductVariant | null;
  onSelectPhoto: (photo: Photo) => void;
  onSelectVariant: (variant: ProductVariant) => void;
  onAddPrint: () => void;
  disabled?: boolean;
}

export default function PrintSelector({
  photos,
  selectedPhoto,
  selectedVariant,
  onSelectPhoto,
  onSelectVariant,
  onAddPrint,
  disabled,
}: PrintSelectorProps) {
  // Group variants by material
  const paperVariants = selectedPhoto?.variants?.filter((v) => v.material === 'paper') || [];
  const aluminumVariants = selectedPhoto?.variants?.filter((v) => v.material === 'aluminum') || [];

  return (
    <div className={`space-y-4 ${disabled ? 'opacity-50 pointer-events-none' : ''}`}>
      {/* Photo Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Select Photo
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 max-h-48 sm:max-h-40 overflow-y-auto">
          {photos.map((photo) => (
            <button
              key={photo.id}
              onClick={() => onSelectPhoto(photo)}
              className={`
                relative aspect-square rounded overflow-hidden border-2 transition
                ${selectedPhoto?.id === photo.id
                  ? 'border-blue-500 ring-2 ring-blue-500/30'
                  : 'border-transparent hover:border-gray-300 dark:hover:border-gray-600'
                }
              `}
            >
              <Image
                src={photo.thumbnail || photo.image}
                alt={photo.title}
                fill
                className="object-cover"
              />
            </button>
          ))}
        </div>
      </div>

      {/* Size Selection */}
      {selectedPhoto && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Select Size
          </label>

          {/* Paper Prints */}
          {paperVariants.length > 0 && (
            <div className="mb-3">
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Paper (Matted)</p>
              <div className="flex flex-wrap gap-2">
                {paperVariants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => onSelectVariant(variant)}
                    className={`
                      px-3 py-1.5 text-sm rounded border transition
                      ${selectedVariant?.id === variant.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                      }
                    `}
                  >
                    {variant.size}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Aluminum Prints */}
          {aluminumVariants.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Aluminum</p>
              <div className="flex flex-wrap gap-2">
                {aluminumVariants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => onSelectVariant(variant)}
                    className={`
                      px-3 py-1.5 text-sm rounded border transition
                      ${selectedVariant?.id === variant.id
                        ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                        : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                      }
                    `}
                  >
                    {variant.size}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add Print Button */}
      {selectedPhoto && selectedVariant && (
        <button
          onClick={onAddPrint}
          className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition text-sm font-medium"
        >
          Add to Wall
        </button>
      )}
    </div>
  );
}
