import { useRef } from 'react';
import { SendHorizontal } from 'lucide-react';
import { useState } from 'react';

export default function ChatInput({ onSend, isLoading, disabled }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const handleSend = () => {
    if (!text.trim() || isLoading || disabled) return;
    onSend(text.trim());
    setText('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 150) + 'px';
    }
  };

  return (
    <div className="chat-input-wrapper">
      <textarea
        ref={textareaRef}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        onInput={handleInput}
        placeholder="Ask anything about your knowledge base..."
        rows={1}
        disabled={disabled}
      />
      <button className="btn btn-primary btn-icon" onClick={handleSend} disabled={!text.trim() || isLoading || disabled}>
        <SendHorizontal size={18} />
      </button>
    </div>
  );
}
