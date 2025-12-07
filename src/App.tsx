import React, { useCallback, useMemo, useState } from 'react';
import { ChatLayout } from './components/ChatLayout';
import type { ChatMessage, Conversation, PrattProfile } from './types';

const createMessage = (role: ChatMessage['role'], content: string): ChatMessage => ({
  id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
  role,
  content,
  timestamp: new Date().toISOString(),
});

const App: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([{
    id: `conv-${Date.now()}`,
    title: 'New chat',
    messages: [],
    createdAt: new Date().toISOString(),
  }]);
  const [activeConversationId, setActiveConversationId] = useState<string>(
    () => conversations[0]?.id ?? `conv-${Date.now()}`,
  );
  const [isLoading, setIsLoading] = useState(false);
  const [prattProfile, setPrattProfile] = useState<PrattProfile>({
    major: '',
    classYear: '',
    semester: '',
    currentCourses: [],
    completedCourses: [],
  });

  const activeConversation = useMemo(
    () => conversations.find((c) => c.id === activeConversationId) ?? conversations[0],
    [conversations, activeConversationId],
  );

  const updateConversationMessages = (conversationId: string, updater: (prev: ChatMessage[]) => ChatMessage[]) => {
    setConversations((prev) =>
      prev.map((conv) => (conv.id === conversationId ? { ...conv, messages: updater(conv.messages) } : conv)),
    );
  };

  const handleNewConversation = useCallback(() => {
    const id = `conv-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    const newConversation: Conversation = {
      id,
      title: 'New chat',
      messages: [],
      createdAt: new Date().toISOString(),
    };
    setConversations((prev) => [newConversation, ...prev]);
    setActiveConversationId(id);
  }, []);

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!activeConversation) return;

      const userMessage = createMessage('user', content);

      // set title from first user message if still default
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === activeConversation.id && (conv.title === 'New chat' || !conv.title)
            ? { ...conv, title: content.slice(0, 80) }
            : conv,
        ),
      );

      updateConversationMessages(activeConversation.id, (prev) => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const payload = {
          message: content,
          history: [...(activeConversation?.messages ?? []), userMessage],
          prattProfile,
        };

        const response = await fetch('http://localhost:8000/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`HTTP error ${response.status}`);
        }

        const data = (await response.json()) as {
          reply?: string;
          retrieved_chunks?: string[];
        };

        const assistantContent =
          data.reply?.trim() ||
          'This is where the Duke degree planning model will respond once the backend is connected.';

        const assistantMessage = createMessage('assistant', assistantContent);
        updateConversationMessages(activeConversation.id, (prev) => {
          const next = [...prev, assistantMessage];

          if (data.retrieved_chunks && data.retrieved_chunks.length > 0) {
            const debugContent =
              'Sources used (retrieved context):\n\n' +
              data.retrieved_chunks
                .map((chunk, index) => `[${index + 1}] ${chunk}`)
                .join('\n\n---\n\n');

            const debugMessage = createMessage('assistant', debugContent);
            next.push(debugMessage);
          }

          return next;
        });
      } catch (error) {
        // Frontend-only mock behavior for now
        // eslint-disable-next-line no-console
        console.error('Error calling /api/chat (backend not implemented yet):', error);
        const assistantMessage = createMessage(
          'assistant',
          'I was unable to reach the chat service. In the full version, I will use Pratt engineering degree handbooks to reason about requirements, prerequisites, study abroad, and overload policies.',
        );
        updateConversationMessages(activeConversation.id, (prev) => [...prev, assistantMessage]);
      } finally {
        setIsLoading(false);
      }
    },
    [activeConversation, prattProfile],
  );

  return (
    <ChatLayout
      conversations={conversations}
      activeConversationId={activeConversation?.id ?? ''}
      messages={activeConversation?.messages ?? []}
      isLoading={isLoading}
      onSendMessage={handleSendMessage}
      onNewConversation={handleNewConversation}
      onSelectConversation={setActiveConversationId}
      prattProfile={prattProfile}
      onChangePrattProfile={setPrattProfile}
    />
  );
};

export default App;
