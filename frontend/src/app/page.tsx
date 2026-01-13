import Link from 'next/link';
import Image from 'next/image';
import { getFeaturedPhotos, getCollections } from '@/lib/api';
import PhotoCard from '@/components/PhotoCard';
import type { Photo, Collection } from '@/types';

export default async function HomePage() {
  let featuredPhotos: Photo[] = [];
  let collections: Collection[] = [];

  try {
    [featuredPhotos, { results: collections }] = await Promise.all([
      getFeaturedPhotos(),
      getCollections(),
    ]);
  } catch (error) {
    console.error('Failed to fetch data:', error);
  }

  return (
    <div>
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center bg-gray-900">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-gray-900/50" />
        <div className="relative z-10 text-center text-white px-4">
          <h1 className="text-4xl md:text-6xl font-light tracking-wide mb-4">
            Matthew Raynor Photography
          </h1>
          <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Fine art prints of the Hamptons. Museum-quality archival paper and aluminum prints.
          </p>
          <Link
            href="/collections"
            className="inline-block px-8 py-3 bg-white text-gray-900 text-sm font-medium rounded hover:bg-gray-100 transition"
          >
            Explore Collections
          </Link>
        </div>
      </section>

      {/* Featured Photos */}
      {featuredPhotos.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-light tracking-wide mb-2 text-gray-900 dark:text-gray-100">Featured Works</h2>
            <p className="text-gray-600 dark:text-gray-400">Curated selections from the collection</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredPhotos.slice(0, 6).map((photo) => (
              <PhotoCard key={photo.id} photo={photo} />
            ))}
          </div>
          <div className="text-center mt-12">
            <Link
              href="/photos"
              className="inline-block px-8 py-3 border border-gray-900 dark:border-gray-100 text-gray-900 dark:text-gray-100 text-sm font-medium rounded hover:bg-gray-900 hover:text-white dark:hover:bg-gray-100 dark:hover:text-gray-900 transition"
            >
              View All Prints
            </Link>
          </div>
        </section>
      )}

      {/* Collections */}
      {collections.length > 0 && (
        <section className="bg-gray-50 dark:bg-gray-800 py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-2xl font-light tracking-wide mb-2 text-gray-900 dark:text-gray-100">Collections</h2>
              <p className="text-gray-600 dark:text-gray-400">Explore themed series of photographs</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {collections.map((collection) => (
                <Link
                  key={collection.id}
                  href={`/collections/${collection.slug}`}
                  className="group block"
                >
                  <div className="relative aspect-[3/2] overflow-hidden bg-gray-200 rounded-sm">
                    {collection.cover_image ? (
                      <Image
                        src={collection.cover_image}
                        alt={collection.name}
                        fill
                        className="object-cover transition-transform duration-500 group-hover:scale-105"
                        sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        {collection.name}
                      </div>
                    )}
                    <div className="absolute inset-0 bg-black/30 group-hover:bg-black/40 transition" />
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-white">
                      <h3 className="text-xl font-medium">{collection.name}</h3>
                      <p className="text-sm text-gray-200 mt-1">{collection.photo_count} prints</p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* About Teaser */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h2 className="text-2xl font-light tracking-wide mb-6 text-gray-900 dark:text-gray-100">About the Artist</h2>
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed mb-8">
          Matthew Raynor captures the timeless beauty of the Hamptons through fine art photography.
          Each print is produced using museum-quality materials, from archival pigment inks to
          hand-finished aluminum panels, ensuring your piece will be treasured for generations.
        </p>
        <Link
          href="/about"
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          Learn More
        </Link>
      </section>

      {/* Gift Cards CTA */}
      <section className="bg-blue-600 text-white py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-2xl font-light tracking-wide mb-4">Give the Gift of Art</h2>
          <p className="text-blue-100 mb-8">
            Share the beauty of the Hamptons with a gift card for any occasion.
          </p>
          <Link
            href="/gift-cards"
            className="inline-block px-8 py-3 bg-white text-blue-600 text-sm font-medium rounded hover:bg-gray-100 transition"
          >
            Purchase Gift Card
          </Link>
        </div>
      </section>
    </div>
  );
}
