import { useEffect, useRef } from 'react';
import { Brain } from 'lucide-react';
import ChatMessage from './ChatMessage';

export default function ChatWindow({ messages = [], isLoading, onFollowup }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (!messages.length && !isLoading) {
    return (
      <div className="chat-welcome">
        <Brain size={56} />
        <h2>ForgeMinds AI Copilot</h2>
        <p className="text-secondary" style={{ maxWidth: 400 }}>Ask questions about your documents, equipment, maintenance procedures, compliance requirements, or root cause analysis.</p>
        <div className="flex flex-wrap gap-sm justify-center" style={{ marginTop: 'var(--spacing-md)' }}>
          {['What is the maintenance schedule for P-101?', 'Show compliance gaps for OISD-154', 'Explain the last compressor failure'].map((q) => (
            <button key={q} className="chat-followup-chip" onClick={() => onFollowup?.(q)}>{q}</button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="chat-messages">
      {messages.map((msg, i) => (
        <ChatMessage key={msg.id || i} message={msg} onFollowup={onFollowup} />
      ))}
      {isLoading && (
        <div className="chat-message assistant">
          <div className="chat-message-avatar"><Brain size={16} /></div>
          <div className="chat-message-content">
            <div className="typing-indicator"><span /><span /><span /></div>
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
