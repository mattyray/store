'use client';

import Image from 'next/image';
import Link from 'next/link';

interface Photo {
  slug: string;
  title: string;
  image_url?: string;
  thumbnail_url?: string;
  url?: string;
  price_range?: { min: number; max: number };
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  imageUrl?: string;
  photos?: Photo[];
  isStreaming?: boolean;
}

interface ChatMessageProps {
  message: Message;
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
        <div className="whitespace-pre-wrap text-sm">
          {cleanContent}
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
      </div>
    </div>
  );
}
