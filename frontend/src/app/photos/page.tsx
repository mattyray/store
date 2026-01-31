'use client';

import { useState, useEffect } from 'react';
import { getPhotos } from '@/lib/api';
import PhotoCard from '@/components/PhotoCard';
import type { Photo } from '@/types';

export default function PhotosPage() {
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    orientation: '',
    material: '',
    ordering: '-created_at',
  });

  useEffect(() => {
    const fetchPhotos = async () => {
      setLoading(true);
      try {
        const params: Record<string, string> = {};
        if (filters.orientation) params.orientation = filters.orientation;
        if (filters.material) params.material = filters.material;
        if (filters.ordering) params.ordering = filters.ordering;

        const data = await getPhotos(params);
        setPhotos(data.results || []);
      } catch (error) {
        console.error('Failed to fetch photos:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPhotos();
  }, [filters]);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Shop All Prints</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Browse our complete collection of fine art photography prints.
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 justify-center mb-12">
        <select
          value={filters.orientation}
          onChange={(e) => setFilters({ ...filters, orientation: e.target.value })}
          className="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Orientations</option>
          <option value="horizontal">Horizontal</option>
          <option value="vertical">Vertical</option>
          <option value="square">Square</option>
        </select>

        <select
          value={filters.material}
          onChange={(e) => setFilters({ ...filters, material: e.target.value })}
          className="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Materials</option>
          <option value="paper">Archival Paper</option>
          <option value="aluminum">Aluminum</option>
        </select>

        <select
          value={filters.ordering}
          onChange={(e) => setFilters({ ...filters, ordering: e.target.value })}
          className="px-4 py-2 border border-gray-200 dark:border-gray-700 rounded text-sm bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="-created_at">Newest First</option>
          <option value="created_at">Oldest First</option>
          <option value="min_price">Price: Low to High</option>
          <option value="-min_price">Price: High to Low</option>
          <option value="title">Title A-Z</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block w-8 h-8 border-2 border-gray-300 border-t-gray-900 dark:border-gray-600 dark:border-t-gray-100 rounded-full animate-spin" />
        </div>
      ) : photos.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400">No photos found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {photos.map((photo) => (
            <PhotoCard key={photo.id} photo={photo} />
          ))}
        </div>
      )}
    </div>
  );
}
