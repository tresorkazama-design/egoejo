import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Loader } from './Loader';
import { fetchAPI, handleAPIError } from '../utils/api';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../utils/i18n';

const ChatList = React.memo(function ChatList({ onSelectThread, selectedThreadId }) {
  const [threads, setThreads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { language } = useLanguage();

  const loadThreads = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchAPI('/chat/threads/');
      setThreads(data.results || data || []);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadThreads();
  }, [loadThreads]);

  const formatDate = useCallback((dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return t('chat.just_now', language);
    if (minutes < 60) return `${minutes}${t('chat.min_ago', language)}`;
    if (hours < 24) return `${hours}${t('chat.hours_ago', language)}`;
    if (days < 7) return `${days}${t('chat.days_ago', language)}`;
    return date.toLocaleDateString(language);
  }, [language]);

  if (loading) {
    return (
      <div className="chat-list">
        <Loader message={t('common.loading', language)} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="chat-list">
        <div className="chat-list__error">
          <p>{t('common.error', language)}: {error}</p>
        </div>
      </div>
    );
  }

  if (threads.length === 0) {
    return (
      <div className="chat-list">
        <div className="chat-list__empty">
          <p>{t('chat.no_threads', language)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-list">
      <div className="chat-list__header">
        <h3>{t('chat.threads', language)}</h3>
      </div>
      <div className="chat-list__items">
        {threads.map((thread) => (
          <button
            key={thread.id}
            type="button"
            className={`chat-list__item ${selectedThreadId === thread.id ? 'is-active' : ''}`}
            onClick={() => onSelectThread(thread)}
          >
            <div className="chat-list__item-header">
              <h4 className="chat-list__item-title">
                {thread.title || t('chat.untitled_thread', language)}
              </h4>
              {thread.last_message_at && (
                <span className="chat-list__item-time">
                  {formatDate(thread.last_message_at)}
                </span>
              )}
            </div>
            {thread.participants && thread.participants.length > 0 && (
              <div className="chat-list__item-participants">
                {thread.participants.slice(0, 3).map((p) => (
                  <span key={p.id} className="chat-list__item-participant">
                    {p.username || p.email}
                  </span>
                ))}
                {thread.participants.length > 3 && (
                  <span className="chat-list__item-participant-more">
                    +{thread.participants.length - 3}
                  </span>
                )}
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  );
});

ChatList.displayName = 'ChatList';

export default ChatList;

