import { useEffect, useRef, useState, useCallback } from 'react';
import { logger } from '../utils/logger';

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
    reconnectAttempts = 5,
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

        // Tentative de reconnexion avec backoff exponentiel
        if (
          shouldReconnectRef.current &&
          reconnect &&
          reconnectCountRef.current < reconnectAttempts
        ) {
          reconnectCountRef.current += 1;
          // Backoff exponentiel: 1s, 2s, 4s, 8s, 16s...
          const backoffDelay = Math.min(
            reconnectInterval * Math.pow(2, reconnectCountRef.current - 1),
            30000 // Max 30 secondes
          );
          
          logger.debug(`Tentative de reconnexion ${reconnectCountRef.current}/${reconnectAttempts} dans ${backoffDelay}ms...`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, backoffDelay);
        } else if (reconnectCountRef.current >= reconnectAttempts) {
          logger.warn('Nombre maximum de tentatives de reconnexion atteint');
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

