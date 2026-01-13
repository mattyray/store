import Link from 'next/link';

export const metadata = {
  title: 'About | Matthew Raynor Photography',
  description: 'Learn about Matthew Raynor and the fine art photography of the Hamptons.',
};

export default function AboutPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4 text-gray-900 dark:text-gray-100">About</h1>
      </div>

      <div className="prose prose-lg max-w-none text-gray-600 dark:text-gray-400">
        <p className="lead text-xl text-gray-700 dark:text-gray-300 mb-8">
          Matthew Raynor is a fine art photographer based in the Hamptons, capturing the
          timeless beauty of Long Island&apos;s East End through his lens.
        </p>

        <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mt-12 mb-4">The Work</h2>
        <p>
          Each photograph in this collection represents a moment of quiet beauty found
          in the landscapes, seascapes, and hidden corners of the Hamptons. From the
          golden light of summer sunsets over Montauk to the moody winter skies above
          Southampton, these images capture the essence of a place cherished by many.
        </p>

        <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mt-12 mb-4">The Prints</h2>
        <p>
          Every print is produced using museum-quality materials and techniques to ensure
          your artwork will be treasured for generations. We offer two premium options:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 my-8">
          <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Archival Paper</h3>
            <p className="text-sm">
              Giclée prints on Hahnemühle Photo Rag, a 100% cotton, acid-free fine art paper.
              Printed with archival pigment inks rated for 100+ years of color stability.
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
            <h3 className="font-medium text-gray-900 dark:text-gray-100 mb-2">Aluminum</h3>
            <p className="text-sm">
              HD metal prints with exceptional color vibrancy and depth. Images are infused
              directly into specially coated aluminum for a stunning, ready-to-hang display.
            </p>
          </div>
        </div>

        <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mt-12 mb-4">Shipping & Handling</h2>
        <p>
          All prints are carefully packaged and shipped with insurance. Paper prints
          ship in rigid tubes, while aluminum prints ship in custom protective crates.
          Most orders ship within 5-7 business days.
        </p>

        <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mt-12 mb-4">Custom Orders</h2>
        <p>
          Looking for a specific size or framing option? Need a print for a commercial
          project or special occasion? I&apos;m happy to work with you on custom orders.
        </p>
      </div>

      <div className="mt-12 text-center">
        <Link
          href="/contact"
          className="inline-block px-8 py-3 bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-sm font-medium rounded hover:bg-gray-800 dark:hover:bg-gray-200 transition"
        >
          Get in Touch
        </Link>
      </div>
    </div>
  );
}
