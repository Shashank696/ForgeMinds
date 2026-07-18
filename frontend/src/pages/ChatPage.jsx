import { useState, useEffect } from 'react';
import { Plus, MessageSquare } from 'lucide-react';
import useChat from '../hooks/useChat';
import ChatWindow from '../components/chat/ChatWindow';
import ChatInput from '../components/chat/ChatInput';
import { AGENT_TYPE_LABELS, AGENT_TYPE_COLORS } from '../utils/constants';
import { formatRelativeTime } from '../utils/formatters';

export default function ChatPage() {
  const { messages, sessions, isLoading, activeSession, sendMessage, loadHistory, loadSessions, startNewSession } = useChat();
  const [agentType, setAgentType] = useState('auto');

  useEffect(() => { loadSessions(); }, [loadSessions]);

  const handleSend = (text) => {
    sendMessage({ message: text, agent_type: agentType });
  };

  const handleSessionClick = (s) => {
    loadHistory(s.session_id);
  };

  return (
    <div className="chat-layout">
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <button className="btn btn-primary w-full" onClick={startNewSession}>
            <Plus size={16} /> New Chat
          </button>
        </div>
        <div className="chat-sessions-list">
          {sessions.map((s) => (
            <div key={s.session_id} className={`chat-session-item ${activeSession === s.session_id ? 'active' : ''}`} onClick={() => handleSessionClick(s)}>
              <div className="flex items-center gap-sm">
                <MessageSquare size={14} />
                <span className="truncate">{s.title}</span>
              </div>
              <p className="text-xs text-muted" style={{ marginTop: 2 }}>{s.message_count} messages · {formatRelativeTime(s.last_message_at)}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="chat-main">
        <div className="flex gap-xs" style={{ padding: 'var(--spacing-sm) var(--spacing-xl)', borderBottom: '1px solid var(--color-border)', overflow: 'auto' }}>
          {Object.entries(AGENT_TYPE_LABELS).map(([key, label]) => (
            <button key={key} className={`tab ${agentType === key ? 'active' : ''}`} onClick={() => setAgentType(key)}
              style={agentType === key ? { borderBottomColor: AGENT_TYPE_COLORS[key], color: AGENT_TYPE_COLORS[key] } : {}}>
              {label}
            </button>
          ))}
        </div>

        <ChatWindow messages={messages} isLoading={isLoading} onFollowup={handleSend} />

        <div className="chat-input-area">
          <ChatInput onSend={handleSend} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
