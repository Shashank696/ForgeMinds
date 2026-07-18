import { useState } from 'react';
import { sendMessage as apiSendMessage, getChatHistory, getChatSessions } from '../services/api';

export default function useChat() {
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (data) => {
    setIsLoading(true);
    try {
      const res = await apiSendMessage(data);
      setMessages([...messages, { type: 'user', ...data }, { type: 'agent', ...res.data }]);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const loadHistory = async (sessionId) => {
    setIsLoading(true);
    try {
      const res = await getChatHistory(sessionId);
      setMessages(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, sendMessage, sessions, loadHistory };
}
