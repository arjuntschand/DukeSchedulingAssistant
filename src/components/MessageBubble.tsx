import type { ChatMessage } from '../types';
import React from 'react';

interface MessageBubbleProps {
  message: ChatMessage;
}

const roleLabel: Record<ChatMessage['role'], string> = {
  user: 'You',
  assistant: 'Assistant',
  system: 'System',
};

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full mb-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[80%] rounded-3xl px-4 py-3 text-sm leading-relaxed shadow-[0_6px_16px_rgba(15,23,42,0.05)] border
        ${isUser ? 'bg-dukeLightBlue/10 text-slate-900 border-dukeBlue/40' : 'bg-white text-slate-900 border-slate-100'}`}
      >
        <div className="text-[11px] uppercase tracking-wide font-semibold text-slate-500 mb-1 flex items-center gap-1">
          <span
            className={`inline-flex h-1.5 w-1.5 rounded-full ${
              isUser ? 'bg-dukeBlue' : 'bg-emerald-500'
            }`}
          />
          {roleLabel[message.role]}
        </div>
        <p className="whitespace-pre-wrap break-words">{message.content}</p>
      </div>
    </div>
  );
};
