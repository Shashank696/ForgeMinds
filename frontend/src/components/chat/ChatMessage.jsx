import { Bot, Copy, Check } from 'lucide-react';
import { useState } from 'react';
import AgentIndicator from './AgentIndicator';
import ConfidenceBadge from '../common/ConfidenceBadge';
import CitationCard from '../common/CitationCard';

function renderMarkdown(text) {
  if (!text) return null;
  return text.split('\n\n').map((block, i) => {
    const html = block
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\n/g, '<br/>');
    return <p key={i} dangerouslySetInnerHTML={{ __html: html }} />;
  });
}

export default function ChatMessage({ message, onFollowup }) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === 'user';
  const text = message.message || message.content || '';

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`chat-message ${isUser ? 'user' : 'assistant'}`}>
      <div className="chat-message-avatar">
        {isUser ? 'U' : <Bot size={16} />}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="chat-message-content">
          {renderMarkdown(text)}
        </div>
        {!isUser && (
          <>
            <div className="chat-message-meta">
              {message.agent_type && <AgentIndicator agentType={message.agent_type} />}
              {message.confidence_score != null && <ConfidenceBadge score={message.confidence_score} />}
              <button className="btn btn-ghost btn-sm" onClick={handleCopy} style={{ marginLeft: 'auto' }}>
                {copied ? <Check size={13} /> : <Copy size={13} />}
              </button>
            </div>
            {message.citations?.length > 0 && (
              <div className="chat-citations">
                {message.citations.map((c, i) => <CitationCard key={i} citation={c} />)}
              </div>
            )}
            {message.suggested_followups?.length > 0 && (
              <div className="chat-followups">
                {message.suggested_followups.map((q, i) => (
                  <button key={i} className="chat-followup-chip" onClick={() => onFollowup?.(q)}>{q}</button>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
