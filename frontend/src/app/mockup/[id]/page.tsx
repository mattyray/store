'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { getMockup } from '@/lib/api';
import type { SavedMockup } from '@/types';

export default function MockupViewPage() {
  const params = useParams();
  const mockupId = params.id as string;

  const [mockup, setMockup] = useState<SavedMockup | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMockup = async () => {
      try {
        const data = await getMockup(mockupId);
        setMockup(data);
      } catch (err) {
        setError('Mockup not found');
      } finally {
        setLoading(false);
      }
    };

    fetchMockup();
  }, [mockupId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !mockup) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <p className="text-gray-500 mb-4">{error || 'Mockup not found'}</p>
        <Link href="/photos" className="text-blue-600 hover:text-blue-700">
          Browse prints
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-light tracking-wide text-gray-900 dark:text-gray-100 mb-2">
          Wall Mockup
        </h1>
        <p className="text-gray-500 dark:text-gray-400">
          See how this artwork looks in a room
        </p>
      </div>

      {/* Mockup Image */}
      <div className="relative aspect-video bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden mb-8">
        <Image
          src={mockup.mockup_image}
          alt="Wall mockup"
          fill
          className="object-contain"
        />
      </div>

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <a
          href={mockup.mockup_image}
          download="wall-mockup.jpg"
          className="px-6 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 font-medium rounded hover:bg-gray-800 dark:hover:bg-gray-200 transition text-center"
        >
          Download Image
        </a>
        <Link
          href="/photos"
          className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded hover:bg-gray-50 dark:hover:bg-gray-800 transition text-center"
        >
          Browse More Prints
        </Link>
      </div>

      {/* Info */}
      <div className="mt-12 text-center">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Created with the Matthew Raynor Photography wall visualizer
        </p>
        <Link
          href="/"
          className="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          Visit the store
        </Link>
      </div>
    </div>
  );
}
