import { notFound } from 'next/navigation';
import { getCollection } from '@/lib/api';
import PhotoCard from '@/components/PhotoCard';

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  try {
    const collection = await getCollection(slug);
    const description = collection.description || `Explore the ${collection.name} collection.`;
    return {
      title: `${collection.name} | Matthew Raynor Photography`,
      description,
      openGraph: {
        title: `${collection.name} — Matthew Raynor Photography`,
        description,
        images: collection.cover_image ? [{ url: collection.cover_image, alt: collection.name }] : [],
        type: 'website',
      },
      twitter: {
        card: 'summary_large_image',
        title: `${collection.name} — Matthew Raynor Photography`,
        description,
        images: collection.cover_image ? [collection.cover_image] : [],
      },
    };
  } catch {
    return {
      title: 'Collection Not Found',
    };
  }
}

export default async function CollectionPage({ params }: Props) {
  const { slug } = await params;

  let collection;
  try {
    collection = await getCollection(slug);
  } catch {
    notFound();
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">{collection.name}</h1>
        {collection.description && (
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">{collection.description}</p>
        )}
        {collection.is_limited_edition && (
          <span className="inline-block mt-4 px-3 py-1 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm rounded">
            Limited Edition
          </span>
        )}
      </div>

      {collection.photos?.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400">No photos in this collection yet.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {collection.photos?.map((photo) => (
            <PhotoCard key={photo.id} photo={photo} />
          ))}
        </div>
      )}
    </div>
  );
}
