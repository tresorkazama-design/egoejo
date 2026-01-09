/**
 * Types TypeScript communs pour migration progressive
 * Ces types servent de base pour la migration TypeScript du frontend
 */

/**
 * Variantes de bouton
 */
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';

/**
 * Props de base pour les composants React
 */
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
  'aria-label'?: string;
  'data-testid'?: string;
}

/**
 * Props pour les composants de bouton
 */
export interface ButtonProps extends BaseComponentProps {
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  disabled?: boolean;
  variant?: ButtonVariant;
  type?: 'button' | 'submit' | 'reset';
}

/**
 * Réponse API générique
 */
export interface APIResponse<T = unknown> {
  data?: T;
  error?: string;
  detail?: string;
  status?: number;
}

/**
 * Options pour les appels API
 */
export interface APIOptions extends RequestInit {
  headers?: Record<string, string>;
}

/**
 * État de chargement
 */
export interface LoadingState {
  loading: boolean;
  error: string | null;
}

/**
 * État de chargement avec données
 */
export interface LoadingStateWithData<T> extends LoadingState {
  data: T | null;
}

/**
 * Hook personnalisé avec état de chargement
 */
export interface UseFetchResult<T> extends LoadingStateWithData<T> {
  refetch: () => Promise<void>;
}

/**
 * Configuration WebSocket
 */
export interface WebSocketConfig {
  url: string;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (data: unknown) => void;
}

/**
 * État WebSocket
 */
export interface WebSocketState {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  reconnectAttempts: number;
}

/**
 * Message WebSocket générique
 */
export interface WebSocketMessage<T = unknown> {
  type: string;
  data: T;
  timestamp?: string;
}

/**
 * Configuration Three.js pour composants 3D
 */
export interface ThreeJSConfig {
  enable: boolean;
  quality?: 'low' | 'medium' | 'high';
  maxFPS?: number;
  enableShadows?: boolean;
}

/**
 * Props pour composants avec Three.js
 */
export interface ThreeJSComponentProps extends BaseComponentProps {
  threeConfig?: ThreeJSConfig;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

/**
 * Configuration d'animation GSAP
 */
export interface GSAPAnimationConfig {
  duration?: number;
  ease?: string;
  delay?: number;
  onComplete?: () => void;
  onStart?: () => void;
}

/**
 * Configuration d'animation Framer Motion
 */
export interface FramerMotionConfig {
  initial?: Record<string, unknown>;
  animate?: Record<string, unknown>;
  exit?: Record<string, unknown>;
  transition?: Record<string, unknown>;
}

/**
 * Props pour composants avec animations
 */
export interface AnimatedComponentProps extends BaseComponentProps {
  animationConfig?: GSAPAnimationConfig | FramerMotionConfig;
  disableAnimation?: boolean;
}

/**
 * Utilisateur authentifié
 */
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  profile?: string;
}

/**
 * Contexte d'authentification
 */
export interface AuthContextValue {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  onLogout?: () => void;
}

/**
 * Contexte de langue
 */
export interface LanguageContextValue {
  language: string;
  setLanguage: (lang: string) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
}

/**
 * Contexte de notification
 */
export interface NotificationContextValue {
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
  showInfo: (message: string) => void;
  showWarning: (message: string) => void;
}

/**
 * Contexte de mode éco
 */
export interface EcoModeContextValue {
  ecoMode: boolean;
  toggleEcoMode: () => void;
  sobrietyLevel: number;
}

/**
 * Projet
 */
export interface Project {
  id: number;
  titre: string;
  description: string;
  montant_cible?: number;
  saka_score?: number;
  created_at?: string;
  updated_at?: string;
}

/**
 * Contenu éducatif
 */
export interface Content {
  id: number;
  title: string;
  content: string;
  category?: string;
  status?: 'draft' | 'published';
  created_at?: string;
  updated_at?: string;
}

/**
 * Message de chat
 */
export interface ChatMessage {
  id: number;
  content: string;
  user: User;
  thread_id: number;
  created_at: string;
  updated_at?: string;
}

/**
 * Thread de chat
 */
export interface ChatThread {
  id: number;
  title?: string;
  participants: User[];
  last_message?: ChatMessage;
  created_at: string;
  updated_at?: string;
}

/**
 * Erreur API standardisée
 */
export interface APIError extends Error {
  status?: number;
  detail?: string;
  code?: string;
}

/**
 * Configuration de l'environnement
 */
export interface EnvConfig {
  VITE_API_URL?: string;
  VITE_SENTRY_DSN?: string;
  MODE: 'development' | 'production' | 'test';
}

/**
 * Déclaration globale pour import.meta.env
 */
declare global {
  interface ImportMetaEnv extends EnvConfig {}
  
  interface Window {
    VITE_E2E?: boolean;
    __e2eActiveFetches?: Set<string>;
  }
}

export {};

