import React, { useState, useEffect, useRef } from 'react';
import { useWebSocket } from '../hooks/useWebSocket';
import { fetchAPI, handleAPIError } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../utils/i18n';
import { Loader } from './Loader';
import CardTilt from './CardTilt';
import { logger } from '../utils/logger';

export default function ChatWindow({ thread }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState(new Set());
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  const { token, user, onLogout } = useAuth();
  const { language } = useLanguage();
  const wsDisconnectRef = useRef(null);

  // URL WebSocket - convertir HTTP en WS
  const getWebSocketUrl = () => {
    if (!thread || !token) return null; // Ne pas créer l'URL si pas de token
    const apiBase = import.meta.env.VITE_API_URL 
      ? `${import.meta.env.VITE_API_URL}/api` 
      : 'http://localhost:8000/api';
    const wsBase = apiBase.replace(/^http/, 'ws').replace('/api', '');
    return `${wsBase}/ws/chat/${thread.id}/`;
  };
  
  const wsUrl = getWebSocketUrl();

  // Connexion WebSocket
  const { isConnected, sendMessage: sendWSMessage, disconnect: disconnectWS } = useWebSocket(wsUrl, {
    onOpen: () => {
      logger.info('WebSocket connecté avec succès');
    },
    onError: (error) => {
      logger.error('Erreur WebSocket:', error);
      setError(t('chat.websocket_error', language));
      setIsConnected(false);
    },
    onClose: (event) => {
      if (event.code === 4401) {
        setError(t('chat.auth_error', language));
      } else if (event.code === 4403) {
        setError(t('chat.permission_error', language));
      } else if (event.code !== 1000 && event.code !== 1001) {
        logger.warn('WebSocket fermé:', event.code, event.reason);
      }
    },
    onMessage: (data) => {
      if (data.type === 'chat_message') {
        setMessages((prev) => {
          const exists = prev.find((m) => m.id === data.payload.id);
          if (exists) {
            return prev.map((m) => (m.id === data.payload.id ? data.payload : m));
          }
          return [...prev, data.payload];
        });
        scrollToBottom();
      } else if (data.type === 'chat_typing') {
        const { user_id, is_typing } = data.payload;
        setTypingUsers((prev) => {
          const next = new Set(prev);
          if (is_typing) {
            next.add(user_id);
          } else {
            next.delete(user_id);
          }
          return next;
        });
      }
    },
  });

  useEffect(() => {
    if (thread) {
      loadMessages();
    }
  }, [thread]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Enregistrer la fonction de déconnexion WebSocket
  useEffect(() => {
    wsDisconnectRef.current = disconnectWS;
    const unregister = onLogout(() => {
      if (wsDisconnectRef.current) {
        wsDisconnectRef.current();
      }
    });
    return unregister;
  }, [disconnectWS, onLogout]);

  const loadMessages = async () => {
    if (!thread) return;
    try {
      setLoading(true);
      const data = await fetchAPI(`/chat/messages/?thread=${thread.id}`);
      setMessages(data.results || data || []);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  const scrollToBottom = () => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !thread || !token) return;

    const messageContent = newMessage.trim();
    setNewMessage('');
    setIsTyping(false);
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    sendWSMessage({ type: 'typing', is_typing: false });

    // Optimistic update: afficher le message immédiatement
    const tempMessage = {
      id: `temp-${Date.now()}`,
      author: user,
      content: messageContent,
      created_at: new Date().toISOString(),
      is_sending: true,
    };

    setMessages((prev) => [...prev, tempMessage]);
    scrollToBottom();

    try {
      const messageData = {
        thread: thread.id,
        content: messageContent,
      };

      const response = await fetchAPI('/chat/messages/', {
        method: 'POST',
        body: JSON.stringify(messageData),
      });

      // Remplacer le message temporaire par le message réel du serveur
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === tempMessage.id ? (response.id ? response : { ...response, id: response.id || `msg-${Date.now()}` }) : msg
        )
      );
    } catch (err) {
      // En cas d'erreur, retirer le message temporaire et afficher l'erreur
      setMessages((prev) => prev.filter((msg) => msg.id !== tempMessage.id));
      setError(handleAPIError(err));
      
      // Restaurer le message dans le champ de saisie pour permettre une nouvelle tentative
      setNewMessage(messageContent);
    }
  };

  const handleTyping = (e) => {
    setNewMessage(e.target.value);

    if (!isTyping) {
      setIsTyping(true);
      sendWSMessage({ type: 'typing', is_typing: true });
    }

    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    typingTimeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      sendWSMessage({ type: 'typing', is_typing: false });
    }, 3000);
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString(language, { hour: '2-digit', minute: '2-digit' });
  };

  if (!thread) {
    return (
      <div className="chat-window chat-window--empty">
        <div className="chat-window__empty">
          <p>{t('chat.select_thread', language)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-window__header">
        <h3>{thread.title || t('chat.untitled_thread', language)}</h3>
        <div className="chat-window__status">
          <span className={`chat-window__status-dot ${isConnected ? 'is-connected' : ''}`} />
          <span>{isConnected ? t('chat.connected', language) : t('chat.disconnected', language)}</span>
        </div>
      </div>

      <div className="chat-window__messages">
        {loading ? (
          <Loader message={t('common.loading', language)} />
        ) : error ? (
          <div className="chat-window__error">
            <p>{t('common.error', language)}: {error}</p>
          </div>
        ) : messages.length === 0 ? (
          <div className="chat-window__empty-messages">
            <p>{t('chat.no_messages', language)}</p>
          </div>
        ) : (
          messages.map((message) => {
            const isOwn = message.author?.id === user?.id;
            return (
              <CardTilt key={message.id}>
                <div className={`chat-message ${isOwn ? 'is-own' : ''}`}>
                  <div className="chat-message__content">
                    {!isOwn && (
                      <div className="chat-message__author">
                        {message.author?.username || message.author?.email || t('chat.anonymous', language)}
                      </div>
                    )}
                    <div className="chat-message__text">{message.content}</div>
                    <div className="chat-message__meta">
                      <span className="chat-message__time">{formatTime(message.created_at)}</span>
                      {message.edited_at && (
                        <span className="chat-message__edited">{t('chat.edited', language)}</span>
                      )}
                    </div>
                  </div>
                </div>
              </CardTilt>
            );
          })
        )}
        {typingUsers.size > 0 && (
          <div className="chat-window__typing">
            <span>{t('chat.typing', language)}...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-window__input" onSubmit={handleSendMessage}>
        <input
          type="text"
          value={newMessage}
          onChange={handleTyping}
          placeholder={t('chat.type_message', language)}
          className="chat-window__input-field"
          disabled={!isConnected || !token}
        />
        <button
          type="submit"
          className="btn btn-primary chat-window__send-btn"
          disabled={!newMessage.trim() || !isConnected || !token}
        >
          {t('chat.send', language)}
        </button>
      </form>
    </div>
  );
}

