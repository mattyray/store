'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { getPhoto, addToCart } from '@/lib/api';
import type { Photo, ProductVariant } from '@/types';
import CropOverlay from '@/components/CropOverlay';

export default function PhotoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [photo, setPhoto] = useState<Photo | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedVariant, setSelectedVariant] = useState<ProductVariant | null>(null);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchPhoto = async () => {
      try {
        const data = await getPhoto(slug);
        setPhoto(data);
        // Select first available variant by default
        const firstAvailable = data.variants?.find((v) => v.is_available);
        if (firstAvailable) setSelectedVariant(firstAvailable);
      } catch (error) {
        console.error('Failed to fetch photo:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPhoto();
  }, [slug]);

  const handleAddToCart = async () => {
    if (!selectedVariant) return;

    setAdding(true);
    setMessage('');
    try {
      await addToCart(selectedVariant.id);
      setMessage('Added to cart!');
      setTimeout(() => {
        router.push('/cart');
      }, 1000);
    } catch (error) {
      setMessage('Failed to add to cart. Please try again.');
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (!photo) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-gray-500 mb-4">Photo not found</p>
        <Link href="/photos" className="text-blue-600 hover:text-blue-700">
          Browse all prints
        </Link>
      </div>
    );
  }

  const paperVariants = photo.variants?.filter((v) => v.material === 'paper' && v.is_available) || [];
  const aluminumVariants = photo.variants?.filter((v) => v.material === 'aluminum' && v.is_available) || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Image */}
        <div className={`relative ${
          photo.orientation === 'vertical'
            ? 'aspect-[2/3]'
            : photo.orientation === 'square'
              ? 'aspect-square'
              : 'aspect-[3/2]'
        } bg-gray-100 rounded overflow-hidden`}>
          {photo.image ? (
            <>
              <Image
                src={photo.image}
                alt={photo.title}
                fill
                className="object-cover"
                sizes="(max-width: 1024px) 100vw, 50vw"
                priority
              />
              {selectedVariant && (
                <CropOverlay
                  widthInches={selectedVariant.width_inches}
                  heightInches={selectedVariant.height_inches}
                  sourceRatio={
                    photo.orientation === 'vertical'
                      ? 2 / 3
                      : photo.orientation === 'square'
                        ? 1
                        : 3 / 2
                  }
                />
              )}
            </>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No image available
            </div>
          )}
        </div>

        {/* Details */}
        <div>
          <Link
            href={`/collections/${photo.collection_slug}`}
            className="text-sm text-blue-600 hover:text-blue-700 mb-2 inline-block"
          >
            {photo.collection_name}
          </Link>
          <h1 className="text-3xl font-light tracking-wide mb-2">{photo.title}</h1>
          <p className="text-gray-500 mb-6">{photo.location}</p>

          {photo.description && (
            <p className="text-gray-600 mb-8 leading-relaxed">{photo.description}</p>
          )}

          {/* Variant Selection */}
          <div className="space-y-6">
            {paperVariants.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-3">Archival Paper</h3>
                <div className="flex flex-wrap gap-2">
                  {paperVariants.map((variant) => (
                    <button
                      key={variant.id}
                      onClick={() => setSelectedVariant(variant)}
                      className={`px-4 py-2 border rounded text-sm transition ${
                        selectedVariant?.id === variant.id
                          ? 'border-blue-600 bg-blue-50 text-blue-600'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {variant.size} - ${variant.price}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {aluminumVariants.length > 0 && (
              <div>
                <h3 className="text-sm font-medium mb-3">Aluminum</h3>
                <div className="flex flex-wrap gap-2">
                  {aluminumVariants.map((variant) => (
                    <button
                      key={variant.id}
                      onClick={() => setSelectedVariant(variant)}
                      className={`px-4 py-2 border rounded text-sm transition ${
                        selectedVariant?.id === variant.id
                          ? 'border-blue-600 bg-blue-50 text-blue-600'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {variant.size} - ${variant.price}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Selected Variant Details */}
          {selectedVariant && (
            <div className="mt-8 p-4 bg-gray-100 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-900 dark:text-gray-100">{selectedVariant.display_name}</span>
                <span className="text-xl font-semibold text-gray-900 dark:text-gray-100">${selectedVariant.price}</span>
              </div>
            </div>
          )}

          {/* Add to Cart */}
          <button
            onClick={handleAddToCart}
            disabled={!selectedVariant || adding}
            className="mt-6 w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {adding ? 'Adding...' : 'Add to Cart'}
          </button>

          {message && (
            <p className={`mt-3 text-sm text-center ${message.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>
              {message}
            </p>
          )}

          {/* Info */}
          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700 space-y-4 text-sm text-gray-600 dark:text-gray-300">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">Archival Paper Prints</h4>
              <p>Museum-quality archival pigment inks on Hahnemühle Photo Rag paper. Unframed.</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">Aluminum Prints</h4>
              <p>HD metal prints with vibrant colors and exceptional durability. Ready to hang with float mount.</p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-gray-100 mb-1">Shipping</h4>
              <p>Free shipping on orders over $500. Most orders ship within 5-7 business days.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
