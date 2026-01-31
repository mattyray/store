import { notFound } from 'next/navigation';
import { getPhoto } from '@/lib/api';
import PhotoDetailClient from './PhotoDetailClient';

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props) {
  const { slug } = await params;
  try {
    const photo = await getPhoto(slug);
    const priceRange = photo.price_range
      ? `From $${photo.price_range.min}`
      : '';
    const description = photo.description
      || `${photo.title} — fine art photography print by Matthew Raynor. ${photo.location}. ${priceRange}`.trim();

    return {
      title: `${photo.title} | Matthew Raynor Photography`,
      description,
      openGraph: {
        title: `${photo.title} — Fine Art Print`,
        description,
        images: photo.image ? [{ url: photo.image, alt: photo.title }] : [],
        type: 'website',
      },
      twitter: {
        card: 'summary_large_image',
        title: `${photo.title} — Fine Art Print`,
        description,
        images: photo.image ? [photo.image] : [],
      },
    };
  } catch {
    return {
      title: 'Photo Not Found | Matthew Raynor Photography',
    };
  }
}

export default async function PhotoDetailPage({ params }: Props) {
  const { slug } = await params;

  let photo;
  try {
    photo = await getPhoto(slug);
  } catch {
    notFound();
  }

  return <PhotoDetailClient photo={photo} />;
}
