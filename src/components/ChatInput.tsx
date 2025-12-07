import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  disabled?: boolean;
  onSend: (message: string) => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({ disabled, onSend }) => {
  const [value, setValue] = useState('');
  const textAreaRef = useRef<HTMLTextAreaElement | null>(null);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    const el = textAreaRef.current;
    if (!el) return;
    el.style.height = '0px';
    const scrollHeight = el.scrollHeight;
    const maxHeight = 120; // px
    el.style.height = `${Math.min(scrollHeight, maxHeight)}px`;
  }, [value]);

  return (
    <div className="border-t border-slate-200 bg-slate-50/95 backdrop-blur px-4 py-3">
      <div className="max-w-3xl mx-auto flex items-end gap-3">
        <div className="flex-1 flex items-end bg-white border border-slate-200 rounded-3xl px-4 py-3 shadow-[inset_0_0_0_1px_rgba(148,163,184,0.25)]">
          <textarea
            ref={textAreaRef}
            rows={1}
            value={value}
            disabled={disabled}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about Pratt majors, prerequisites, course planning, study abroad, overload rules, etc."
            className="flex-1 bg-transparent resize-none outline-none text-base text-slate-900 placeholder:text-slate-500 leading-relaxed max-h-32"
          />
        </div>
        <button
          type="button"
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="inline-flex items-center justify-center rounded-full bg-dukeBlue text-white px-5 py-2.5 text-base font-semibold shadow-md shadow-dukeBlue/30 disabled:opacity-60 disabled:cursor-not-allowed hover:bg-dukeBlue/90 transition-colors"
        >
          Send
        </button>
      </div>
      <p className="mt-1 text-[11px] text-slate-500 text-center max-w-3xl mx-auto">
        Press Enter to send, Shift+Enter for a new line.
      </p>
    </div>
  );
};
