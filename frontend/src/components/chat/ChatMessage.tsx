'use client';

import Image from 'next/image';
import Link from 'next/link';
import ReactMarkdown from 'react-markdown';

interface Photo {
  slug: string;
  title: string;
  image_url?: string;
  thumbnail_url?: string;
  url?: string;
  price_range?: { min: number; max: number };
}

interface MockupData {
  type: 'mockup';
  analysis: {
    id: string;
    wall_image_url: string;
    wall_bounds: { top: number; bottom: number; left: number; right: number };
    pixels_per_inch: number;
    confidence: number;
  };
  photo: {
    slug: string;
    title: string;
    image_url: string;
    thumbnail_url: string;
  };
  variant: {
    id: number;
    size: string;
    width_inches: number;
    height_inches: number;
    price: number;
  };
  message: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  imageUrl?: string;
  photos?: Photo[];
  mockup?: MockupData;
  isStreaming?: boolean;
}

interface ChatMessageProps {
  message: Message;
}

// Mockup preview component with proper print positioning
function MockupPreview({ mockup }: { mockup: MockupData }) {
  const { analysis, photo, variant } = mockup;
  const bounds = analysis.wall_bounds;

  // Calculate print size relative to the wall
  // Use pixels_per_inch to determine how big the print should appear
  const ppi = analysis.pixels_per_inch || 50; // fallback
  const printWidthPx = variant.width_inches * ppi;
  const printHeightPx = variant.height_inches * ppi;

  // Wall dimensions in pixels (from bounds)
  const wallWidth = bounds.right - bounds.left;
  const wallHeight = bounds.bottom - bounds.top;

  // Calculate print size as percentage of container
  // Assume image fills the container width, scale accordingly
  const printWidthPercent = Math.min((printWidthPx / wallWidth) * 100, 80);

  // Center the print horizontally within wall bounds, vertically centered
  const wallCenterX = (bounds.left + bounds.right) / 2;
  const wallCenterY = (bounds.top + bounds.bottom) / 2;

  // These are approximate - would need image dimensions for perfect positioning
  // For now, center in the detected wall area
  const leftPercent = 50; // Center horizontally
  const topPercent = 35; // Slightly above center (typical hanging height)

  return (
    <div className="mt-3 bg-white dark:bg-gray-700 rounded overflow-hidden">
      <div className="relative aspect-[3/4] bg-gray-100 dark:bg-gray-800 overflow-hidden">
        {/* Wall/room image */}
        <Image
          src={analysis.wall_image_url}
          alt="Your room"
          fill
          className="object-cover"
          unoptimized
        />
        {/* Print overlay */}
        <div
          className="absolute z-10 bg-white p-1 shadow-2xl"
          style={{
            top: `${topPercent}%`,
            left: `${leftPercent}%`,
            transform: 'translate(-50%, -50%)',
            width: `${printWidthPercent}%`,
            maxWidth: '70%',
          }}
        >
          <Image
            src={photo.image_url}
            alt={photo.title}
            width={400}
            height={300}
            className="w-full h-auto"
            unoptimized
          />
        </div>
      </div>
      <div className="p-3">
        <p className="font-medium text-sm text-gray-900 dark:text-gray-100">
          {photo.title}
        </p>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {variant.size} - ${variant.price.toLocaleString()}
        </p>
        <Link
          href={`/photos/${photo.slug}`}
          className="mt-2 inline-block text-xs text-blue-600 dark:text-blue-400 hover:underline"
        >
          View print details →
        </Link>
      </div>
    </div>
  );
}

// Parse JSON block from message content to extract photos
function parsePhotosFromContent(content: string): { cleanContent: string; photos: Photo[] } {
  const jsonMatch = content.match(/```json\s*(\{[\s\S]*?"photos"[\s\S]*?\})\s*```/);
  if (jsonMatch) {
    try {
      const data = JSON.parse(jsonMatch[1]);
      if (data.photos && Array.isArray(data.photos)) {
        return {
          cleanContent: content.replace(jsonMatch[0], '').trim(),
          photos: data.photos,
        };
      }
    } catch {
      // Invalid JSON, ignore
    }
  }
  return { cleanContent: content, photos: [] };
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  // Parse photos from content JSON block if present
  const { cleanContent, photos: parsedPhotos } = parsePhotosFromContent(message.content);

  // Deduplicate photos by slug - prefer tool result photos (they have more data)
  const photoMap = new Map<string, Photo>();
  for (const photo of (message.photos || [])) {
    photoMap.set(photo.slug, photo);
  }
  for (const photo of parsedPhotos) {
    if (!photoMap.has(photo.slug)) {
      photoMap.set(photo.slug, photo);
    }
  }
  const allPhotos = Array.from(photoMap.values());

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`
          max-w-[85%] rounded-lg px-4 py-2
          ${
            isUser
              ? 'bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
          }
        `}
      >
        {/* User's attached image */}
        {message.imageUrl && (
          <div className="mb-2 -mx-2 -mt-1">
            <Image
              src={message.imageUrl}
              alt="Attached image"
              width={200}
              height={150}
              className="rounded object-cover"
            />
          </div>
        )}

        {/* Message content */}
        <div className="text-sm prose prose-sm dark:prose-invert max-w-none prose-p:my-1 prose-headings:my-2 prose-ul:my-1 prose-li:my-0">
          {isUser ? (
            <p className="whitespace-pre-wrap m-0">{cleanContent}</p>
          ) : (
            <ReactMarkdown
              components={{
                // Compact styling for chat
                h2: ({ children }) => <h2 className="text-base font-semibold mt-3 mb-1">{children}</h2>,
                h3: ({ children }) => <h3 className="text-sm font-semibold mt-2 mb-1">{children}</h3>,
                p: ({ children }) => <p className="my-1">{children}</p>,
                ul: ({ children }) => <ul className="my-1 ml-4 list-disc">{children}</ul>,
                li: ({ children }) => <li className="my-0.5">{children}</li>,
                strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
              }}
            >
              {cleanContent}
            </ReactMarkdown>
          )}
          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
          )}
        </div>

        {/* Photo cards from search results */}
        {allPhotos.length > 0 && (
          <div className="mt-3 space-y-2">
            {allPhotos.slice(0, 6).map((photo, index) => {
              const imageUrl = photo.thumbnail_url || photo.image_url;
              const photoUrl = photo.url || `/photos/${photo.slug}`;
              if (!imageUrl) return null;

              return (
                <Link
                  key={`${photo.slug}-${index}`}
                  href={photoUrl}
                  className="block bg-white dark:bg-gray-700 rounded overflow-hidden hover:shadow-md transition"
                >
                  <div className="flex gap-3 p-2">
                    <div className="w-16 h-16 flex-shrink-0 relative">
                      <Image
                        src={imageUrl}
                        alt={photo.title}
                        fill
                        className="object-cover rounded"
                        sizes="64px"
                        unoptimized
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate text-gray-900 dark:text-gray-100">
                        {photo.title}
                      </p>
                      {photo.price_range && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          ${photo.price_range.min.toLocaleString()} - $
                          {photo.price_range.max.toLocaleString()}
                        </p>
                      )}
                    </div>
                    <svg
                      className="w-4 h-4 text-gray-400 flex-shrink-0 self-center"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </div>
                </Link>
              );
            })}
            {allPhotos.length > 6 && (
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                +{allPhotos.length - 6} more
              </p>
            )}
          </div>
        )}

        {/* Mockup preview */}
        {message.mockup && (
          <MockupPreview mockup={message.mockup} />
        )}
      </div>
    </div>
  );
}
