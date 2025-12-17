import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import ChatList from '../../components/ChatList';
import ChatWindow from '../../components/ChatWindow';

export default function Chat() {
  const [selectedThread, setSelectedThread] = useState(null);
  const { token, user, loading } = useAuth();
  const { language } = useLanguage();

  // Afficher un loader pendant le chargement de l'authentification
  if (loading) {
    return (
      <div className="page page--citations">
        <section className="citations-hero">
          <div className="citations-hero__badge">{t('common.loading', language)}</div>
          <h1 className="citations-hero__title">{t('chat.title', language)}</h1>
          <p className="citations-hero__subtitle">
            {t('common.loading', language)}...
          </p>
        </section>
      </div>
    );
  }

  // Vérifier l'authentification après le chargement
  if (!token || !user) {
    return (
      <div className="page page--citations">
        <section className="citations-hero">
          <div className="citations-hero__badge">{t('chat.auth_required', language)}</div>
          <h1 className="citations-hero__title">{t('chat.title', language)}</h1>
          <p className="citations-hero__subtitle">
            {t('chat.auth_required_desc', language)}
          </p>
        </section>
      </div>
    );
  }

  return (
    <div className="page page--chat">
      <section className="citations-hero">
        <div className="citations-hero__badge">{t('chat.badge', language)}</div>
        <h1 className="citations-hero__title">{t('chat.title', language)}</h1>
        <p className="citations-hero__subtitle">
          {t('chat.subtitle', language)}
        </p>
      </section>

      <div className="chat-container">
        <div className="chat-container__sidebar">
          <ChatList
            onSelectThread={setSelectedThread}
            selectedThreadId={selectedThread?.id}
          />
        </div>
        <div className="chat-container__main">
          <ChatWindow thread={selectedThread} />
        </div>
      </div>
    </div>
  );
}

