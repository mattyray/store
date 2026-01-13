export const metadata = {
  title: 'Shipping & Returns | Matthew Raynor Photography',
  description: 'Shipping information and return policy for fine art photography prints.',
};

export default function ShippingPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <h1 className="text-3xl font-light tracking-wide mb-8 text-gray-900 dark:text-gray-100">
        Shipping & Returns
      </h1>

      <div className="prose prose-gray dark:prose-invert max-w-none space-y-8">
        <section>
          <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mb-4">Shipping</h2>
          <div className="space-y-4 text-gray-600 dark:text-gray-400">
            <p>
              All prints are made to order and carefully packaged to ensure they arrive in perfect condition.
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Processing Time:</strong> Most orders ship within 5-7 business days.
              </li>
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Free Shipping:</strong> Orders over $500 qualify for free shipping within the continental United States.
              </li>
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Standard Shipping:</strong> $15 flat rate for orders under $500.
              </li>
              <li>
                <strong className="text-gray-900 dark:text-gray-100">International Shipping:</strong> Available upon request. Please contact us for a quote.
              </li>
            </ul>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mb-4">Packaging</h2>
          <div className="space-y-4 text-gray-600 dark:text-gray-400">
            <p>
              Each print is carefully packaged to protect it during transit:
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Paper Prints:</strong> Shipped flat between rigid cardboard with protective tissue paper.
              </li>
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Aluminum Prints:</strong> Shipped in custom-fit boxes with foam corner protectors.
              </li>
            </ul>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mb-4">Returns & Exchanges</h2>
          <div className="space-y-4 text-gray-600 dark:text-gray-400">
            <p>
              Your satisfaction is our priority. If you&apos;re not completely happy with your purchase:
            </p>
            <ul className="list-disc pl-5 space-y-2">
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Return Window:</strong> Returns accepted within 30 days of delivery.
              </li>
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Condition:</strong> Items must be in original, undamaged condition.
              </li>
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Refunds:</strong> Full refund to original payment method, minus shipping costs.
              </li>
              <li>
                <strong className="text-gray-900 dark:text-gray-100">Damaged Items:</strong> If your print arrives damaged, please contact us within 48 hours with photos of the damage for a full replacement.
              </li>
            </ul>
          </div>
        </section>

        <section>
          <h2 className="text-xl font-medium text-gray-900 dark:text-gray-100 mb-4">Contact Us</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Questions about shipping or returns? Email us at{' '}
            <a href="mailto:hello@matthewraynor.com" className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300">
              hello@matthewraynor.com
            </a>
          </p>
        </section>
      </div>
    </div>
  );
}
