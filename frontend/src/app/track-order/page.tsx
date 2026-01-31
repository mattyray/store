'use client';

import { useState } from 'react';
import { trackOrder } from '@/lib/api';

interface TrackingResult {
  order_number: string;
  status: string;
  tracking_number?: string;
  tracking_carrier?: string;
  tracking_url?: string;
}

export default function TrackOrderPage() {
  const [email, setEmail] = useState('');
  const [orderNumber, setOrderNumber] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TrackingResult | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await trackOrder(email, orderNumber);
      setResult(data);
    } catch {
      setError('Order not found. Please check your email and order number.');
    } finally {
      setLoading(false);
    }
  };

  const getStatusDisplay = (status: string) => {
    const statuses: Record<string, { label: string; color: string }> = {
      pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' },
      paid: { label: 'Paid', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' },
      processing: { label: 'Processing', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300' },
      shipped: { label: 'Shipped', color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' },
      delivered: { label: 'Delivered', color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' },
      cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' },
    };
    return statuses[status] || { label: status, color: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300' };
  };

  return (
    <div className="max-w-lg mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Track Your Order</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Enter your email and order number to check the status of your order.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="The email used for your order"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Order Number</label>
          <input
            type="text"
            value={orderNumber}
            onChange={(e) => setOrderNumber(e.target.value)}
            required
            className="w-full px-4 py-2 border border-gray-200 dark:border-gray-700 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., MR-240115-001"
          />
        </div>

        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50"
        >
          {loading ? 'Looking up...' : 'Track Order'}
        </button>
      </form>

      {result && (
        <div className="mt-8 p-6 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-medium">Order {result.order_number}</h2>
            <span className={`px-3 py-1 rounded-full text-sm ${getStatusDisplay(result.status).color}`}>
              {getStatusDisplay(result.status).label}
            </span>
          </div>

          {result.tracking_number ? (
            <div className="space-y-2 text-sm">
              <p>
                <span className="text-gray-500 dark:text-gray-400">Carrier:</span>{' '}
                {result.tracking_carrier || 'Standard Shipping'}
              </p>
              <p>
                <span className="text-gray-500 dark:text-gray-400">Tracking Number:</span>{' '}
                {result.tracking_url ? (
                  <a
                    href={result.tracking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-700"
                  >
                    {result.tracking_number}
                  </a>
                ) : (
                  result.tracking_number
                )}
              </p>
            </div>
          ) : (
            <p className="text-sm text-gray-600 dark:text-gray-400">
              {result.status === 'shipped' || result.status === 'delivered'
                ? 'Tracking information will be updated shortly.'
                : 'Tracking information will be available once your order ships.'}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
