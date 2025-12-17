import React, { createContext, useState, useEffect, useContext, useRef } from 'react';
import { logger } from '../utils/logger';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);
  const logoutCallbacksRef = useRef(new Set());

  // URL de l'API Backend
  const API_BASE = import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/api` 
    : 'http://localhost:8000/api';

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

  const fetchUser = async (currentToken) => {
    try {
      const response = await fetch(`${API_BASE}/auth/me/`, {
        headers: {
          'Authorization': `Bearer ${currentToken}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Si le token est invalide, on déconnecte
        logout();
      }
    } catch (error) {
      logger.error("Erreur lors de la récupération de l'utilisateur", error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Erreur de connexion");
      }

      const data = await response.json();
      localStorage.setItem('token', data.access); // On stocke le token d'accès
      localStorage.setItem('refresh_token', data.refresh); // On stocke le refresh token
      setToken(data.access);
      // fetchUser sera appelé automatiquement via le useEffect
      return true;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
      try {
          const response = await fetch(`${API_BASE}/auth/register/`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(userData)
          });

          if (!response.ok) {
              const errorData = await response.json();
              // On essaie de formater l'erreur proprement
              let errorMessage = "Erreur d'inscription";
              if (typeof errorData === 'object') {
                  errorMessage = Object.entries(errorData).map(([key, val]) => `${key}: ${val}`).join(', ');
              }
              throw new Error(errorMessage);
          }
          
          // Inscription réussie, on peut connecter l'utilisateur directement ou le rediriger vers le login
          return true;

      } catch (error) {
          throw error;
      }
  }

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