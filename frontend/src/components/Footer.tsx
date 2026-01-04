'use client';

import Link from 'next/link';
import { useState } from 'react';
import { subscribeNewsletter } from '@/lib/api';

export default function Footer() {
  const [email, setEmail] = useState('');
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setStatus('loading');
    try {
      const res = await subscribeNewsletter(email);
      setStatus('success');
      setMessage(res.message);
      setEmail('');
    } catch {
      setStatus('error');
      setMessage('Something went wrong. Please try again.');
    }
  };

  return (
    <footer className="bg-gray-50 border-t border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <h3 className="text-lg font-light tracking-wide mb-4">Matthew Raynor Photography</h3>
            <p className="text-sm text-gray-600 mb-6 max-w-md">
              Fine art photography prints of the Hamptons. Museum-quality archival paper and aluminum prints for collectors and art enthusiasts.
            </p>

            {/* Newsletter */}
            <form onSubmit={handleSubscribe} className="flex gap-2 max-w-sm">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="flex-1 px-4 py-2 text-sm border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                disabled={status === 'loading'}
                className="px-4 py-2 bg-gray-900 text-white text-sm rounded hover:bg-gray-800 transition disabled:opacity-50"
              >
                {status === 'loading' ? '...' : 'Subscribe'}
              </button>
            </form>
            {message && (
              <p className={`mt-2 text-sm ${status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                {message}
              </p>
            )}
          </div>

          {/* Links */}
          <div>
            <h4 className="text-sm font-medium mb-4">Shop</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/collections" className="hover:text-gray-900">Collections</Link></li>
              <li><Link href="/photos" className="hover:text-gray-900">All Prints</Link></li>
              <li><Link href="/gift-cards" className="hover:text-gray-900">Gift Cards</Link></li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-medium mb-4">Info</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li><Link href="/about" className="hover:text-gray-900">About</Link></li>
              <li><Link href="/contact" className="hover:text-gray-900">Contact</Link></li>
              <li><Link href="/track-order" className="hover:text-gray-900">Track Order</Link></li>
              <li><Link href="/shipping" className="hover:text-gray-900">Shipping & Returns</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-200 text-center text-sm text-gray-500">
          <p>&copy; {new Date().getFullYear()} Matthew Raynor Photography. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
