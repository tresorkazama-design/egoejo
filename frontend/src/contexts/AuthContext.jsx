import React, { createContext, useState, useEffect, useContext, useRef } from 'react';
import { logger } from '../utils/logger';
import { fetchAPI, handleAPIError } from '../utils/api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const logoutCallbacksRef = useRef(new Set());

  // Fonction pour enregistrer un callback de déconnexion (pour WebSocket, etc.)
  const onLogout = (callback) => {
    logoutCallbacksRef.current.add(callback);
    return () => {
      logoutCallbacksRef.current.delete(callback);
    };
  };

  useEffect(() => {
    // Au chargement, si on a un token, on essaie de récupérer l'utilisateur
    if (token) {
      fetchUser(token);
    } else {
      setLoading(false);
    }
  }, [token]);

  // OPTIMISATION RÉSEAU : Utiliser fetchAPI centralisé avec retry et gestion Auth automatique
  const fetchUser = async (currentToken) => {
    try {
      // fetchAPI gère automatiquement les headers Auth et le retry
      const userData = await fetchAPI('/auth/me/', {
        headers: {
          'Authorization': `Bearer ${currentToken}`
        }
      });
      setUser(userData);
    } catch (error) {
      logger.error("Erreur lors de la récupération de l'utilisateur", error);
      // Si le token est invalide ou erreur réseau après retry, on déconnecte
      logout();
    } finally {
      setLoading(false);
    }
  };

  // OPTIMISATION RÉSEAU : Utiliser fetchAPI centralisé avec retry
  const login = async (username, password) => {
    try {
      // fetchAPI gère automatiquement le retry et les headers
      const data = await fetchAPI('/auth/login/', {
        method: 'POST',
        body: JSON.stringify({ username, password })
      });

      localStorage.setItem('token', data.access); // On stocke le token d'accès
      localStorage.setItem('refresh_token', data.refresh); // On stocke le refresh token
      setToken(data.access);
      // fetchUser sera appelé automatiquement via le useEffect
      return true;
    } catch (error) {
      // fetchAPI gère déjà les erreurs, on les propage
      throw error;
    }
  };

  // OPTIMISATION RÉSEAU : Utiliser fetchAPI centralisé avec retry
  const register = async (userData) => {
    try {
      // fetchAPI gère automatiquement le retry et les headers
      await fetchAPI('/auth/register/', {
        method: 'POST',
        body: JSON.stringify(userData)
      });
      
      // Inscription réussie, on peut connecter l'utilisateur directement ou le rediriger vers le login
      return true;
    } catch (error) {
      // fetchAPI gère déjà les erreurs, on les propage
      throw error;
    }
  };

  const logout = () => {
    // Appeler tous les callbacks de déconnexion (pour fermer WebSocket, etc.)
    logoutCallbacksRef.current.forEach((callback) => {
      try {
        callback();
      } catch (error) {
        logger.error('Erreur dans callback de déconnexion:', error);
      }
    });

    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    onLogout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};