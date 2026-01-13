import Image from 'next/image';
import Link from 'next/link';
import type { Photo } from '@/types';

interface PhotoCardProps {
  photo: Photo;
}

export default function PhotoCard({ photo }: PhotoCardProps) {
  const imageUrl = photo.thumbnail || photo.image;

  return (
    <Link href={`/photos/${photo.slug}`} className="group block">
      <div className="relative aspect-[4/3] overflow-hidden bg-gray-100 rounded-sm">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt={photo.title}
            fill
            className="object-cover transition-transform duration-500 group-hover:scale-105"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No image
          </div>
        )}
      </div>
      <div className="mt-3">
        <h3 className="text-sm font-medium text-gray-900 group-hover:text-blue-600 transition">
          {photo.title}
        </h3>
        <p className="text-sm text-gray-500 mt-1">{photo.location}</p>
        {photo.price_range && (
          <p className="text-sm text-gray-700 mt-1">From ${photo.price_range.min}</p>
        )}
      </div>
    </Link>
  );
}
