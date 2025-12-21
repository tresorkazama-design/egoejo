import { useEffect, useRef, useState, useCallback } from 'react';
import { logger } from '../utils/logger';

// OPTIMISATION RÉSEAU : Limite stricte sur les tentatives de reconnexion pour éviter le DDoS involontaire
const MAX_RECONNECT_ATTEMPTS = 5;

/**
 * Hook personnalisé pour gérer une connexion WebSocket
 * @param {string} url - URL du WebSocket
 * @param {object} options - Options (onMessage, onError, onOpen, onClose, reconnect)
 */
export function useWebSocket(url, options = {}) {
  const {
    onMessage,
    onError,
    onOpen,
    onClose,
    reconnect = true,
    reconnectInterval = 3000,
    reconnectAttempts = MAX_RECONNECT_ATTEMPTS, // Utiliser la constante par défaut
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectCountRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const heartbeatIntervalRef = useRef(null);
  const lastPongRef = useRef(Date.now());

  const connect = useCallback(() => {
    if (!url || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      // Ajouter le token d'authentification si disponible
      const token = localStorage.getItem('token');
      if (!token) {
        logger.warn('Pas de token disponible pour la connexion WebSocket');
        setIsConnected(false);
        return;
      }
      const wsUrlWithAuth = `${url}?token=${encodeURIComponent(token)}`;
      logger.debug('Connexion WebSocket à:', wsUrlWithAuth.replace(token, 'TOKEN_HIDDEN'));
      const ws = new WebSocket(wsUrlWithAuth);
      wsRef.current = ws;

      ws.onopen = (event) => {
        setIsConnected(true);
        reconnectCountRef.current = 0;
        lastPongRef.current = Date.now();
        
        // Heartbeat: envoyer un ping toutes les 30 secondes
        heartbeatIntervalRef.current = setInterval(() => {
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            // Vérifier si on a reçu un pong récemment (dans les 60 dernières secondes)
            const timeSinceLastPong = Date.now() - lastPongRef.current;
            if (timeSinceLastPong > 60000) {
              logger.warn('Pas de pong reçu depuis 60s, reconnexion...');
              wsRef.current.close();
              return;
            }
            // Envoyer un ping (le serveur devrait répondre avec un pong)
            try {
              wsRef.current.send(JSON.stringify({ type: 'ping' }));
            } catch (err) {
              logger.error('Erreur envoi ping:', err);
            }
          }
        }, 30000);
        
        if (onOpen) onOpen(event);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Gérer les pongs du serveur
          if (data.type === 'pong') {
            lastPongRef.current = Date.now();
            return;
          }
          
          setLastMessage(data);
          if (onMessage) onMessage(data);
        } catch (error) {
          logger.error('Erreur parsing message WebSocket:', error);
        }
      };

      ws.onerror = (error) => {
        logger.error('Erreur WebSocket:', error);
        if (onError) onError(error);
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        
        // Nettoyer le heartbeat
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
          heartbeatIntervalRef.current = null;
        }
        
        if (onClose) onClose(event);

        // OPTIMISATION RÉSEAU : Tentative de reconnexion avec backoff exponentiel et limite stricte
        // Utiliser MAX_RECONNECT_ATTEMPTS pour éviter le DDoS involontaire sur le serveur
        const maxAttempts = Math.min(reconnectAttempts, MAX_RECONNECT_ATTEMPTS);
        
        if (
          shouldReconnectRef.current &&
          reconnect &&
          reconnectCountRef.current < maxAttempts
        ) {
          reconnectCountRef.current += 1;
          // Backoff exponentiel: 1s, 2s, 4s, 8s, 16s...
          const backoffDelay = Math.min(
            reconnectInterval * Math.pow(2, reconnectCountRef.current - 1),
            30000 // Max 30 secondes
          );
          
          logger.debug(`Tentative de reconnexion ${reconnectCountRef.current}/${maxAttempts} dans ${backoffDelay}ms...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, backoffDelay);
        } else if (reconnectCountRef.current >= maxAttempts) {
          logger.warn(`Nombre maximum de tentatives de reconnexion atteint (${maxAttempts}). Arrêt des reconnexions pour éviter le DDoS involontaire.`);
          // Ne plus tenter de reconnexion
          shouldReconnectRef.current = false;
        }
      };
    } catch (error) {
      logger.error('Erreur création WebSocket:', error);
      if (onError) onError(error);
    }
  }, [url, onMessage, onError, onOpen, onClose, reconnect, reconnectInterval, reconnectAttempts]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    logger.warn('WebSocket non connecté');
    return false;
  }, []);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    disconnect,
    reconnect: connect,
  };
}

