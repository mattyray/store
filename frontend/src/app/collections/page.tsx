import Link from 'next/link';
import Image from 'next/image';
import { getCollections } from '@/lib/api';
import type { Collection } from '@/types';

export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'Collections | Matthew Raynor Photography',
  description: 'Explore our curated collections of fine art Hamptons photography.',
};

export default async function CollectionsPage() {
  let collections: Collection[] = [];

  try {
    const data = await getCollections();
    collections = data.results || [];
  } catch (error) {
    console.error('Failed to fetch collections:', error);
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Collections</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Explore themed series of photographs capturing the essence of the Hamptons.
        </p>
      </div>

      {collections.length === 0 ? (
        <p className="text-center text-gray-500">No collections available yet.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {collections.map((collection) => (
            <Link
              key={collection.id}
              href={`/collections/${collection.slug}`}
              className="group block"
            >
              <div className="relative aspect-[16/9] overflow-hidden bg-gray-200 rounded">
                {collection.cover_image ? (
                  <Image
                    src={collection.cover_image}
                    alt={collection.name}
                    fill
                    className="object-cover transition-transform duration-500 group-hover:scale-105"
                    sizes="(max-width: 768px) 100vw, 50vw"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">
                    {collection.name}
                  </div>
                )}
                <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition" />
                <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/70 to-transparent">
                  <h2 className="text-xl font-medium text-white mb-1">{collection.name}</h2>
                  <p className="text-sm text-gray-200">{collection.photo_count} prints</p>
                  {collection.is_limited_edition && (
                    <span className="inline-block mt-2 px-2 py-1 bg-white/20 text-white text-xs rounded">
                      Limited Edition
                    </span>
                  )}
                </div>
              </div>
              {collection.description && (
                <p className="mt-3 text-sm text-gray-600 line-clamp-2">{collection.description}</p>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
