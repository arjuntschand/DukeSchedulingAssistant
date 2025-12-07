import React from 'react';
import type { ChatMessage, Conversation, PrattProfile } from '../types';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { Sidebar } from './Sidebar';
import { PrattProfilePanel } from './PrattProfilePanel';

interface ChatLayoutProps {
  conversations: Conversation[];
  activeConversationId: string;
  messages: ChatMessage[];
  isLoading: boolean;
  onSendMessage: (message: string) => void;
  onNewConversation: () => void;
  onSelectConversation: (id: string) => void;
  prattProfile: PrattProfile;
  onChangePrattProfile: (profile: PrattProfile) => void;
}

export const ChatLayout: React.FC<ChatLayoutProps> = ({
  conversations,
  activeConversationId,
  messages,
  isLoading,
  onSendMessage,
  onNewConversation,
  onSelectConversation,
  prattProfile,
  onChangePrattProfile,
}) => {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 flex text-[15px]">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewConversation={onNewConversation}
        onSelectConversation={onSelectConversation}
      />

      {/* Main chat area */}
      <main className="flex-1 flex flex-col">
        <header className="md:hidden px-4 pt-4 pb-3 border-b border-slate-200 bg-white/90 backdrop-blur flex items-center justify-between shadow-sm">
          <div>
            <p className="text-base font-semibold text-slate-900">Duke Degree &amp; Course Planning Chatbot</p>
            <p className="text-xs text-slate-600">Pratt Engineering majors only.</p>
          </div>
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-dukeBlue text-xs font-bold tracking-tight text-white shadow-md shadow-dukeBlue/30">
            DU
          </span>
        </header>

        <div className="flex-1 flex flex-col max-w-5xl w-full mx-auto px-4 md:px-8 py-4 md:py-6 gap-4">
          <PrattProfilePanel profile={prattProfile} onChange={onChangePrattProfile} />
          <div className="flex-1 rounded-3xl border border-slate-200 bg-white shadow-[0_10px_30px_rgba(15,23,42,0.06)] flex flex-col overflow-hidden">
            <MessageList messages={messages} isLoading={isLoading} />
            <ChatInput disabled={isLoading} onSend={onSendMessage} />
          </div>
        </div>
      </main>
    </div>
  );
};
