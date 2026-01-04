'use client';

import { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { getOrderBySession } from '@/lib/api';
import type { Order } from '@/types';

function OrderSuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!sessionId) {
      setError('No order session found');
      setLoading(false);
      return;
    }

    const fetchOrder = async () => {
      try {
        const data = await getOrderBySession(sessionId);
        setOrder(data);
      } catch (err) {
        setError('Could not find your order. Please check your email for confirmation.');
      } finally {
        setLoading(false);
      }
    };

    fetchOrder();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-16 text-center">
        <h1 className="text-3xl font-light tracking-wide mb-4">Order Status</h1>
        <p className="text-gray-600 mb-8">{error}</p>
        <Link
          href="/"
          className="inline-block px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Return Home
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-16 text-center">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h1 className="text-3xl font-light tracking-wide mb-4">Thank You!</h1>
      <p className="text-gray-600 mb-8">
        Your order has been confirmed and a receipt has been sent to {order?.customer_email}.
      </p>

      <div className="bg-gray-50 rounded-lg p-6 mb-8">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Order Number</p>
            <p className="font-medium">{order?.order_number}</p>
          </div>
          <div>
            <p className="text-gray-500">Total</p>
            <p className="font-medium">${order?.total}</p>
          </div>
        </div>
      </div>

      <p className="text-sm text-gray-500 mb-8">
        Most orders ship within 5-7 business days. You&apos;ll receive a shipping confirmation email with tracking information once your order is on its way.
      </p>

      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          href="/photos"
          className="px-8 py-3 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
        >
          Continue Shopping
        </Link>
        <Link
          href="/track-order"
          className="px-8 py-3 border border-gray-300 text-gray-700 text-sm font-medium rounded hover:bg-gray-50 transition"
        >
          Track Order
        </Link>
      </div>
    </div>
  );
}

export default function OrderSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin" />
      </div>
    }>
      <OrderSuccessContent />
    </Suspense>
  );
}
