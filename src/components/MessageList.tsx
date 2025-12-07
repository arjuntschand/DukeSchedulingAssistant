import React, { useEffect, useRef } from 'react';
import type { ChatMessage } from '../types';
import { MessageBubble } from './MessageBubble';

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [messages.length, isLoading]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-5 py-5 space-y-2 bg-slate-50"
    >
      {messages.length === 0 && !isLoading && (
        <div className="h-full flex items-center justify-center text-center text-slate-500 text-base">
          <div>
            <p className="font-semibold text-slate-800 mb-1">Welcome to the Pratt Degree Planning Assistant</p>
            <p>Ask about Pratt majors, prerequisites, course planning, study abroad, and overload rules.</p>
          </div>
        </div>
      )}

      {messages.map((m) => (
        <MessageBubble key={m.id} message={m} />
      ))}

      {isLoading && (
        <div className="mt-2 flex gap-2 items-center text-xs text-slate-500">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-dukeLightBlue opacity-60" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-dukeLightBlue" />
          </span>
          Thinking about your Pratt degree plan…
        </div>
      )}
    </div>
  );
};
