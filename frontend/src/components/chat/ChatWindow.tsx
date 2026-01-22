'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { streamChat, uploadChatImage, type ChatChunk } from '@/lib/api';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  imageUrl?: string;
  photos?: Array<{
    slug: string;
    title: string;
    image_url: string;
    price_range?: { min: number; max: number };
  }>;
  isStreaming?: boolean;
}

interface ChatWindowProps {
  conversationId: string | null;
  onConversationIdChange: (id: string) => void;
  onClose: () => void;
  onNewMessage: () => void;
}

export default function ChatWindow({
  conversationId,
  onConversationIdChange,
  onClose,
  onNewMessage,
}: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Add welcome message if no conversation
  useEffect(() => {
    if (!conversationId && messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          role: 'assistant',
          content:
            "Hi! I'm here to help you find the perfect print for your space. You can tell me what you're looking for, upload a photo of your room to see how prints would look, or just browse and ask questions. What can I help you with today?",
        },
      ]);
    }
  }, [conversationId, messages.length]);

  const handleSendMessage = useCallback(
    async (content: string, imageFile?: File) => {
      if (!content.trim() && !imageFile) return;

      setError(null);
      setIsLoading(true);

      // Upload image first if provided
      let imageUrl: string | undefined;
      if (imageFile) {
        try {
          const result = await uploadChatImage(imageFile);
          imageUrl = result.url;
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Failed to upload image');
          setIsLoading(false);
          return;
        }
      }

      // Add user message
      const userMessageId = `user-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          id: userMessageId,
          role: 'user',
          content,
          imageUrl,
        },
      ]);

      // Add placeholder for assistant response
      const assistantMessageId = `assistant-${Date.now()}`;
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          isStreaming: true,
        },
      ]);

      try {
        // Get cart ID from cookie/localStorage if available
        const cartId = localStorage.getItem('cart_id') || undefined;

        // Stream the response
        let currentConversationId = conversationId;
        let accumulatedContent = '';
        const photos: Message['photos'] = [];

        for await (const chunk of streamChat(
          content,
          currentConversationId || undefined,
          imageUrl,
          cartId
        )) {
          switch (chunk.type) {
            case 'conversation_id':
              if (chunk.id && !currentConversationId) {
                currentConversationId = chunk.id;
                onConversationIdChange(chunk.id);
              }
              break;

            case 'text':
              if (chunk.content) {
                accumulatedContent += chunk.content;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantMessageId
                      ? { ...m, content: accumulatedContent }
                      : m
                  )
                );
              }
              break;

            case 'tool_result':
              // Extract photos from tool results
              if (chunk.result && Array.isArray(chunk.result)) {
                for (const item of chunk.result) {
                  if (item.slug && item.title && item.image_url) {
                    photos.push({
                      slug: item.slug,
                      title: item.title,
                      image_url: item.image_url,
                      price_range: item.price_range,
                    });
                  }
                }
              } else if (chunk.result && typeof chunk.result === 'object') {
                const result = chunk.result as Record<string, unknown>;
                if (result.slug && result.title && result.image_url) {
                  photos.push({
                    slug: result.slug as string,
                    title: result.title as string,
                    image_url: result.image_url as string,
                    price_range: result.price_range as { min: number; max: number },
                  });
                }
              }
              break;

            case 'error':
              setError(chunk.message || 'An error occurred');
              break;

            case 'done':
              // Finalize the message
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMessageId
                    ? { ...m, isStreaming: false, photos: photos.length > 0 ? photos : undefined }
                    : m
                )
              );
              onNewMessage();
              break;
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to send message');
        // Remove the streaming message on error
        setMessages((prev) => prev.filter((m) => m.id !== assistantMessageId));
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, onConversationIdChange, onNewMessage]
  );

  const handleNewConversation = useCallback(() => {
    setMessages([
      {
        id: 'welcome',
        role: 'assistant',
        content:
          "Hi! I'm here to help you find the perfect print for your space. You can tell me what you're looking for, upload a photo of your room to see how prints would look, or just browse and ask questions. What can I help you with today?",
      },
    ]);
    onConversationIdChange('');
    localStorage.removeItem('chat_conversation_id');
  }, [onConversationIdChange]);

  return (
    <div className="fixed bottom-6 right-6 z-50 w-[400px] max-w-[calc(100vw-48px)] h-[600px] max-h-[calc(100vh-100px)] bg-white dark:bg-gray-900 rounded-lg shadow-2xl flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-green-500 rounded-full" />
          <h3 className="font-medium text-gray-900 dark:text-gray-100">
            Shopping Assistant
          </h3>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleNewConversation}
            className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition"
            title="New conversation"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition"
            title="Close"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {error && (
          <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded text-sm">
            {error}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
    </div>
  );
}
