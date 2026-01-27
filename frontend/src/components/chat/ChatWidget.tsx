'use client';

import { useState, useEffect } from 'react';
import ChatWindow from './ChatWindow';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [hasUnread, setHasUnread] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  // Load conversation ID from localStorage on mount
  useEffect(() => {
    const savedId = localStorage.getItem('chat_conversation_id');
    if (savedId) {
      setConversationId(savedId);
    }
  }, []);

  // Save conversation ID to localStorage when it changes
  useEffect(() => {
    if (conversationId) {
      localStorage.setItem('chat_conversation_id', conversationId);
    }
  }, [conversationId]);

  // Show tooltip on first visit (after a short delay)
  useEffect(() => {
    const hasSeenTooltip = localStorage.getItem('chat_tooltip_seen');
    if (!hasSeenTooltip && !isOpen) {
      const timer = setTimeout(() => {
        setShowTooltip(true);
        // Auto-hide after 8 seconds
        setTimeout(() => {
          setShowTooltip(false);
          localStorage.setItem('chat_tooltip_seen', 'true');
        }, 8000);
      }, 3000); // Show after 3 seconds on page
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // Hide tooltip and mark as seen when chat opens
  useEffect(() => {
    if (isOpen) {
      setHasUnread(false);
      setShowTooltip(false);
      localStorage.setItem('chat_tooltip_seen', 'true');
    }
  }, [isOpen]);

  return (
    <>
      {/* Chat Window */}
      {isOpen && (
        <ChatWindow
          conversationId={conversationId}
          onConversationIdChange={setConversationId}
          onClose={() => setIsOpen(false)}
          onNewMessage={() => {
            if (!isOpen) setHasUnread(true);
          }}
        />
      )}

      {/* Tooltip bubble */}
      {showTooltip && !isOpen && (
        <div className="fixed bottom-24 right-6 z-50 animate-fade-in">
          <div className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl px-4 py-3 max-w-[220px]">
            <p className="text-sm text-gray-700 dark:text-gray-200">
              Need help finding the perfect print? Chat with me!
            </p>
            {/* Triangle pointer */}
            <div className="absolute -bottom-2 right-6 w-4 h-4 bg-white dark:bg-gray-800 rotate-45 shadow-xl" />
            {/* Close button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowTooltip(false);
                localStorage.setItem('chat_tooltip_seen', 'true');
              }}
              className="absolute -top-2 -right-2 w-6 h-6 bg-gray-200 dark:bg-gray-600 rounded-full flex items-center justify-center text-gray-500 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors"
              aria-label="Dismiss"
            >
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`
          fixed bottom-6 right-6 z-50
          w-14 h-14 rounded-full
          bg-gray-900 dark:bg-gray-100
          text-white dark:text-gray-900
          shadow-lg hover:shadow-xl
          transition-all duration-200
          flex items-center justify-center
          ${isOpen ? 'scale-0 opacity-0' : 'scale-100 opacity-100'}
        `}
        aria-label={isOpen ? 'Close chat' : 'Open chat'}
      >
        {/* Pulse ring animation */}
        <span className="absolute inset-0 rounded-full bg-gray-900 dark:bg-gray-100 animate-ping opacity-20" />

        {/* Chat icon */}
        <svg
          className="w-6 h-6 relative z-10"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>

        {/* Unread indicator */}
        {hasUnread && (
          <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full z-20" />
        )}
      </button>
    </>
  );
}
