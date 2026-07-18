import { useState, useCallback } from 'react';
import { sendChatMessage, fetchChatHistory, fetchChatSessions } from '../services/api';
import toast from 'react-hot-toast';

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (data) => {
    const userMsg = { id: Date.now().toString(), role: 'user', message: data.message, created_at: new Date().toISOString() };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    try {
      const res = await sendChatMessage({
        ...data,
        session_id: activeSession,
      });
      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        message: res.response,
        agent_type: res.agent_type,
        citations: res.citations || [],
        confidence_score: res.confidence_score,
        suggested_followups: res.suggested_followups || [],
        related_entities: res.related_entities || [],
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
      if (res.session_id) setActiveSession(res.session_id);
      return res;
    } catch (e) {
      toast.error('Failed to send message');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [activeSession]);

  const loadHistory = useCallback(async (sessionId) => {
    setIsLoading(true);
    try {
      const data = await fetchChatHistory(sessionId);
      setMessages(data.messages || []);
      setActiveSession(sessionId);
    } catch (e) {
      toast.error('Failed to load chat history');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const data = await fetchChatSessions();
      setSessions(data.sessions || data || []);
    } catch (e) {
      // silently fail for sessions
    }
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const startNewSession = useCallback(() => {
    setActiveSession(null);
    setMessages([]);
  }, []);

  return {
    messages, sessions, isLoading, activeSession,
    setActiveSession, sendMessage, loadHistory, loadSessions,
    clearMessages, startNewSession,
  };
}
