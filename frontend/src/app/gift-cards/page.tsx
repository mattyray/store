'use client';

import { useState } from 'react';
import { purchaseGiftCard } from '@/lib/api';

const AMOUNTS = [100, 250, 500, 1000, 2500];

export default function GiftCardsPage() {
  const [selectedAmount, setSelectedAmount] = useState(250);
  const [recipientEmail, setRecipientEmail] = useState('');
  const [recipientName, setRecipientName] = useState('');
  const [purchaserEmail, setPurchaserEmail] = useState('');
  const [purchaserName, setPurchaserName] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { checkout_url } = await purchaseGiftCard({
        amount: selectedAmount,
        recipient_email: recipientEmail,
        recipient_name: recipientName,
        purchaser_email: purchaserEmail,
        purchaser_name: purchaserName,
        message,
      });
      window.location.href = checkout_url;
    } catch (err) {
      setError('Failed to process gift card. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Gift Cards</h1>
        <p className="text-gray-600">
          Give the gift of fine art photography. Perfect for any occasion.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Amount Selection */}
        <div>
          <label className="block text-sm font-medium mb-3">Select Amount</label>
          <div className="grid grid-cols-5 gap-2">
            {AMOUNTS.map((amount) => (
              <button
                key={amount}
                type="button"
                onClick={() => setSelectedAmount(amount)}
                className={`py-3 rounded border text-sm font-medium transition ${
                  selectedAmount === amount
                    ? 'border-blue-600 bg-blue-50 text-blue-600'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                ${amount}
              </button>
            ))}
          </div>
        </div>

        {/* Recipient Info */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Recipient Information</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Email *</label>
              <input
                type="email"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="recipient@email.com"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Name</label>
              <input
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Recipient's name"
              />
            </div>
          </div>
        </div>

        {/* Your Info */}
        <div className="space-y-4">
          <h3 className="text-sm font-medium">Your Information</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Email *</label>
              <input
                type="email"
                value={purchaserEmail}
                onChange={(e) => setPurchaserEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Name</label>
              <input
                type="text"
                value={purchaserName}
                onChange={(e) => setPurchaserName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Your name"
              />
            </div>
          </div>
        </div>

        {/* Personal Message */}
        <div>
          <label className="block text-sm font-medium mb-1">Personal Message (Optional)</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={3}
            maxLength={500}
            className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Add a personal message to include with the gift card..."
          />
          <p className="text-xs text-gray-500 mt-1">{message.length}/500 characters</p>
        </div>

        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading || !recipientEmail || !purchaserEmail}
          className="w-full py-4 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Processing...' : `Purchase $${selectedAmount} Gift Card`}
        </button>

        <p className="text-sm text-gray-500 text-center">
          The recipient will receive their gift card via email immediately after purchase.
          Gift cards are valid for one year from the date of purchase.
        </p>
      </form>
    </div>
  );
}
