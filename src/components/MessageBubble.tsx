import type { ChatMessage } from '../types';
import React, { useState } from 'react';

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
  const [showContext, setShowContext] = useState(false);
  const [showFewshot, setShowFewshot] = useState(false);
  const hasContext =
    !!(message.sources && message.sources.length > 0) ||
    !!(message.retrievedChunks && message.retrievedChunks.length > 0);
  const hasFewshot = !!(message.fewshotChunks && message.fewshotChunks.length > 0);

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
        <p className="whitespace-pre-wrap break-words mb-1.5">{message.content}</p>

        {!isUser && (hasContext || hasFewshot) && (
          <div className="mt-1.5 border-t border-slate-100 pt-1.5">
            <div className="flex flex-wrap gap-3">
              {hasContext && (
                <button
                  type="button"
                  onClick={() => setShowContext((prev) => !prev)}
                  className="text-[11px] font-medium text-dukeBlue hover:text-dukeBlue/80 flex items-center gap-1"
                >
                  <span>{showContext ? 'Hide Retrieved Context' : 'Show Retrieved Context'}</span>
                  <span className="text-[9px]">▼</span>
                </button>
              )}

              {hasFewshot && (
                <button
                  type="button"
                  onClick={() => setShowFewshot((prev) => !prev)}
                  className="text-[11px] font-medium text-emerald-700 hover:text-emerald-600 flex items-center gap-1"
                >
                  <span>{showFewshot ? 'Hide Few-Shot Examples' : 'Show Few-Shot Examples'}</span>
                  <span className="text-[9px]">▼</span>
                </button>
              )}
            </div>

            {showContext && hasContext && (
              <div className="mt-2 space-y-2 text-[11px] text-slate-700 bg-slate-50/80 rounded-2xl px-3 py-2 border border-slate-100">
                {message.sources && message.sources.length > 0 ? (
                  message.sources.map((src, index) => {
                    const labelParts: string[] = [];
                    if (src.source_file) labelParts.push(src.source_file.split('/').slice(-1)[0]);
                    if (typeof src.page === 'number') labelParts.push(`p. ${src.page}`);
                    if (typeof src.chunk_index === 'number') labelParts.push(`chunk ${src.chunk_index}`);

                    const label = labelParts.join(' · ') || `Chunk ${index + 1}`;

                    const pdfAnchor = src.page ? `#page=${src.page}` : '';
                    const backendBase = 'http://localhost:8000';

                    const href = src.source_file
                      ? `${backendBase}/context-docs/${src.source_file}${pdfAnchor}`
                      : undefined;

                    return (
                      <div key={index} className="leading-snug">
                        <div className="font-semibold text-slate-800 flex items-center justify-between gap-2">
                          <span>[{index + 1}] {label}</span>
                          {href && (
                            <a
                              href={href}
                              target="_blank"
                              rel="noreferrer"
                              className="text-dukeBlue hover:text-dukeBlue/80 underline decoration-dotted"
                            >
                              View source
                            </a>
                          )}
                        </div>
                        <div className="mt-1 text-slate-700 whitespace-pre-wrap break-words">
                          {src.text}
                        </div>
                      </div>
                    );
                  })
                ) : (
                  message.retrievedChunks?.map((chunk, index) => (
                    <div key={index} className="leading-snug">
                      <div className="font-semibold text-slate-800">[{index + 1}] Context chunk</div>
                      <div className="mt-1 text-slate-700 whitespace-pre-wrap break-words">{chunk}</div>
                    </div>
                  ))
                )}
              </div>
            )}

            {showFewshot && hasFewshot && (
              <div className="mt-2 space-y-2 text-[11px] text-slate-700 bg-emerald-50/80 rounded-2xl px-3 py-2 border border-emerald-100">
                {message.fewshotChunks?.map((chunk, index) => (
                  <div key={index} className="leading-snug">
                    <div className="font-semibold text-emerald-900">Few-shot example #{index + 1}</div>
                    <div className="mt-1 text-emerald-800 whitespace-pre-wrap break-words">{chunk}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
