import type { MetadataRoute } from 'next';
import { getCollections, getPhotos, getProducts } from '@/lib/api';

const BASE_URL = 'https://store.matthewraynor.com';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: BASE_URL, changeFrequency: 'weekly', priority: 1.0 },
    { url: `${BASE_URL}/photos`, changeFrequency: 'weekly', priority: 0.9 },
    { url: `${BASE_URL}/collections`, changeFrequency: 'weekly', priority: 0.9 },
    { url: `${BASE_URL}/book`, changeFrequency: 'monthly', priority: 0.7 },
    { url: `${BASE_URL}/about`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${BASE_URL}/contact`, changeFrequency: 'monthly', priority: 0.5 },
    { url: `${BASE_URL}/gift-cards`, changeFrequency: 'monthly', priority: 0.6 },
    { url: `${BASE_URL}/shipping`, changeFrequency: 'monthly', priority: 0.4 },
  ];

  // Dynamic pages from API
  try {
    const [collectionsData, photosData, productsData] = await Promise.all([
      getCollections(),
      getPhotos(),
      getProducts({ product_type: 'book' }),
    ]);

    const collectionPages: MetadataRoute.Sitemap = (collectionsData?.results || []).map(
      (collection) => ({
        url: `${BASE_URL}/collections/${collection.slug}`,
        changeFrequency: 'weekly' as const,
        priority: 0.8,
      })
    );

    const photoPages: MetadataRoute.Sitemap = (photosData?.results || []).map((photo) => ({
      url: `${BASE_URL}/photos/${photo.slug}`,
      changeFrequency: 'monthly' as const,
      priority: 0.7,
    }));

    const bookPages: MetadataRoute.Sitemap = (productsData?.results || []).map((product) => ({
      url: `${BASE_URL}/book/${product.slug}`,
      changeFrequency: 'monthly' as const,
      priority: 0.6,
    }));

    return [...staticPages, ...collectionPages, ...photoPages, ...bookPages];
  } catch {
    // If API is unreachable during build, return static pages only
    return staticPages;
  }
}
