'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { useParams, useRouter } from 'next/navigation';
import { getProduct, addProductToCart } from '@/lib/api';
import { useCart } from '@/contexts/CartContext';
import type { Product } from '@/types';

export default function BookDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { refreshCart } = useCart();
  const slug = params.slug as string;

  const [book, setBook] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [message, setMessage] = useState('');
  const [quantity, setQuantity] = useState(1);

  useEffect(() => {
    const fetchBook = async () => {
      try {
        const data = await getProduct(slug);
        setBook(data);
      } catch (error) {
        console.error('Failed to fetch book:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, [slug]);

  const handleAddToCart = async () => {
    if (!book) return;

    setAdding(true);
    setMessage('');
    try {
      await addProductToCart(book.id, quantity);
      await refreshCart();
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

  if (!book) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-gray-500 mb-4">Book not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Book Image */}
        <div className="relative aspect-[3/4] bg-gray-100 rounded overflow-hidden">
          {book.image ? (
            <Image
              src={book.image}
              alt={book.title}
              fill
              className="object-contain"
              sizes="(max-width: 1024px) 100vw, 50vw"
              priority
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No image available
            </div>
          )}
        </div>

        {/* Book Details */}
        <div>
          <p className="text-sm text-gray-500 uppercase tracking-wider mb-2">
            {book.product_type_display}
          </p>
          <h1 className="text-3xl font-light tracking-wide mb-2">{book.title}</h1>
          {book.author && (
            <p className="text-lg text-gray-600 mb-4">by {book.author}</p>
          )}

          {book.description && (
            <p className="text-gray-600 mb-6 leading-relaxed">{book.description}</p>
          )}

          {book.long_description && (
            <div className="mb-8 prose prose-gray max-w-none">
              <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                {book.long_description}
              </p>
            </div>
          )}

          {/* Price */}
          <div className="mb-6">
            <div className="flex items-baseline gap-3">
              <span className="text-3xl font-medium">${book.price}</span>
              {book.is_on_sale && book.compare_at_price && (
                <span className="text-lg text-gray-400 line-through">
                  ${book.compare_at_price}
                </span>
              )}
            </div>
            {!book.is_in_stock && (
              <p className="text-red-600 text-sm mt-1">Out of stock</p>
            )}
          </div>

          {/* Quantity Selector */}
          {book.is_in_stock && (
            <div className="mb-6">
              <label className="text-sm font-medium mb-2 block">Quantity</label>
              <div className="flex items-center border border-gray-200 rounded w-fit">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  -
                </button>
                <span className="px-4 py-2 min-w-[50px] text-center">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  +
                </button>
              </div>
            </div>
          )}

          {/* Add to Cart */}
          <button
            onClick={handleAddToCart}
            disabled={!book.is_in_stock || adding}
            className="w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {adding ? 'Adding...' : book.is_in_stock ? 'Add to Cart' : 'Out of Stock'}
          </button>

          {message && (
            <p className={`mt-3 text-sm text-center ${message.includes('Failed') ? 'text-red-600' : 'text-green-600'}`}>
              {message}
            </p>
          )}

          {/* Book Details */}
          <div className="mt-8 pt-8 border-t border-gray-200 space-y-3 text-sm">
            <h4 className="font-medium text-gray-900">Details</h4>
            <dl className="grid grid-cols-2 gap-2 text-gray-600">
              {book.publisher && (
                <>
                  <dt className="font-medium">Publisher</dt>
                  <dd>{book.publisher}</dd>
                </>
              )}
              {book.publication_year && (
                <>
                  <dt className="font-medium">Year</dt>
                  <dd>{book.publication_year}</dd>
                </>
              )}
              {book.pages && (
                <>
                  <dt className="font-medium">Pages</dt>
                  <dd>{book.pages}</dd>
                </>
              )}
              {book.dimensions && (
                <>
                  <dt className="font-medium">Dimensions</dt>
                  <dd>{book.dimensions}</dd>
                </>
              )}
              {book.isbn && (
                <>
                  <dt className="font-medium">ISBN</dt>
                  <dd>{book.isbn}</dd>
                </>
              )}
            </dl>
          </div>

          {/* Shipping Info */}
          <div className="mt-6 pt-6 border-t border-gray-200 text-sm text-gray-600">
            <h4 className="font-medium text-gray-900 mb-2">Shipping</h4>
            <p>Free shipping on orders over $500. Most orders ship within 3-5 business days.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
