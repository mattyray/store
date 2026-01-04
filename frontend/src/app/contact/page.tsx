'use client';

import { useState } from 'react';
import { submitContactForm } from '@/lib/api';

export default function ContactPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setStatus('idle');

    try {
      await submitContactForm({ name, email, subject, message });
      setStatus('success');
      setName('');
      setEmail('');
      setSubject('');
      setMessage('');
    } catch {
      setStatus('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <h1 className="text-3xl font-light tracking-wide mb-4">Contact</h1>
        <p className="text-gray-600">
          Have a question about a print, custom sizing, or anything else? Get in touch.
        </p>
      </div>

      {status === 'success' ? (
        <div className="text-center py-12 bg-green-50 rounded-lg">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h2 className="text-xl font-medium mb-2">Message Sent!</h2>
          <p className="text-gray-600">Thank you for reaching out. I&apos;ll get back to you soon.</p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email *</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Subject</label>
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="General Inquiry"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Message *</label>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required
              rows={6}
              className="w-full px-4 py-2 border border-gray-200 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {status === 'error' && (
            <p className="text-red-600 text-sm">Failed to send message. Please try again.</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gray-900 text-white font-medium rounded hover:bg-gray-800 transition disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send Message'}
          </button>
        </form>
      )}

      <div className="mt-12 pt-12 border-t border-gray-200 text-center text-sm text-gray-600">
        <p className="mb-2">You can also reach me directly at:</p>
        <a href="mailto:hello@matthewraynor.com" className="text-blue-600 hover:text-blue-700">
          hello@matthewraynor.com
        </a>
      </div>
    </div>
  );
}
