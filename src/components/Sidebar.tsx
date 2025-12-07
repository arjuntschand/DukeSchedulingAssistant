import React from 'react';
import type { Conversation } from '../types';

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
}) => {
  return (
    <aside className="hidden md:flex md:flex-col w-72 border-r border-slate-200 bg-slate-50/90 backdrop-blur-sm">
      <div className="px-5 pt-5 pb-4 border-b border-slate-200">
        <div className="flex items-center justify-between gap-2 mb-4">
          <h1 className="text-base font-semibold text-slate-900 leading-snug">
            <span className="block">Duke Degree &amp; Course</span>
            <span className="block">Planning Chatbot</span>
          </h1>
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-dukeBlue text-xs font-bold tracking-tight text-white shadow-md shadow-dukeBlue/30">
            DU
          </span>
        </div>
        <p className="text-sm text-slate-600 leading-relaxed">
          Pratt School of Engineering majors only. Ask about degree requirements, prerequisites, and planning.
        </p>
        <button
          type="button"
          onClick={onNewConversation}
          className="mt-4 inline-flex items-center justify-center w-full rounded-full bg-dukeBlue text-white px-4 py-2 text-sm font-semibold shadow-sm hover:bg-dukeBlue/90 transition-colors"
        >
          New chat
        </button>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="px-4 pt-3 pb-2 text-[11px] font-semibold text-slate-500 uppercase tracking-wide border-b border-slate-200">
          Conversations
        </div>
        <div className="flex-1 overflow-y-auto px-3 py-3 space-y-1.5">
          {conversations.length === 0 && (
            <p className="text-xs text-slate-500 px-2 py-1.5">
              No chats yet. Start a new conversation to begin planning your Pratt degree.
            </p>
          )}
          {conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            return (
              <button
                key={conv.id}
                type="button"
                onClick={() => onSelectConversation(conv.id)}
                className={`w-full text-left px-3.5 py-2.5 rounded-xl text-xs border flex flex-col gap-0.5 transition-colors ${
                  isActive
                    ? 'bg-dukeBlue/5 border-dukeBlue/50 text-slate-900'
                    : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                }`}
              >
                <span className="font-semibold truncate">{conv.title || 'New chat'}</span>
                <span className="text-[11px] text-slate-500">
                  {new Date(conv.createdAt).toLocaleString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: '2-digit',
                  })}
                </span>
              </button>
            );
          })}
        </div>
        <div className="px-4 py-3 border-t border-slate-200 text-[11px] text-slate-500" />
      </div>
    </aside>
  );
};
