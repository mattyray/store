'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4">
      <h2 className="text-2xl font-light tracking-wide mb-4 text-gray-900 dark:text-gray-100">
        Something went wrong
      </h2>
      <p className="text-gray-500 dark:text-gray-400 mb-8 text-center max-w-md">
        We encountered an unexpected error. Please try again.
      </p>
      <button
        onClick={reset}
        className="px-8 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded hover:bg-gray-800 dark:hover:bg-gray-200 transition"
      >
        Try Again
      </button>
    </div>
  );
}
