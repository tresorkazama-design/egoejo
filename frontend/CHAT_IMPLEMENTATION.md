# 💬 Implémentation du Chat - EGOEJO

## Vue d'ensemble

Une interface de messagerie en temps réel complète a été implémentée avec WebSocket pour permettre aux membres de la communauté EGOEJO de communiquer instantanément.

## ✨ Fonctionnalités

### Backend (Déjà existant)
- ✅ **Modèles** : `ChatThread`, `ChatMessage`, `ChatMembership`
- ✅ **API REST** : Endpoints pour threads et messages
- ✅ **WebSocket** : `ChatConsumer` pour les messages en temps réel
- ✅ **Authentification** : JWT requis pour accéder au chat

### Frontend (Nouvellement créé)

#### 1. **Composants**
- **`ChatList.jsx`** : Liste des conversations avec aperçu
- **`ChatWindow.jsx`** : Fenêtre de chat avec messages en temps réel
- **`Chat.jsx`** : Page principale combinant liste et fenêtre

#### 2. **Hook personnalisé**
- **`useWebSocket.js`** : Gestion de la connexion WebSocket avec :
  - Reconnexion automatique
  - Gestion des erreurs
  - Authentification via token

#### 3. **Fonctionnalités**
- ✅ Messages en temps réel via WebSocket
- ✅ Indicateur de frappe (typing indicator)
- ✅ Statut de connexion (connecté/déconnecté)
- ✅ Scroll automatique vers les nouveaux messages
- ✅ Formatage des dates (il y a X minutes/heures/jours)
- ✅ Design immersif cohérent avec le reste du site
- ✅ Responsive (mobile-friendly)
- ✅ Support multilingue (i18n)

## 📁 Fichiers créés/modifiés

### Nouveaux fichiers
- `src/hooks/useWebSocket.js` - Hook WebSocket
- `src/components/ChatList.jsx` - Liste des conversations
- `src/components/ChatWindow.jsx` - Fenêtre de chat
- `src/app/pages/Chat.jsx` - Page principale

### Fichiers modifiés
- `src/app/router.jsx` - Route `/chat` ajoutée
- `src/components/Layout.jsx` - Lien "Chat" dans la navigation
- `src/locales/fr.json` - Traductions françaises
- `src/styles/global.css` - Styles CSS pour le chat

## 🎨 Design

Le chat utilise le même design system que le reste du site :
- Glassmorphism pour les conteneurs
- Couleurs cohérentes (accent, surface, text)
- Animations subtiles (slide-in pour les messages)
- CardTilt pour les messages (effet 3D au survol)
- Responsive avec sidebar qui devient une liste en mobile

## 🔌 Configuration WebSocket

### URL WebSocket
L'URL WebSocket est automatiquement générée à partir de l'URL de l'API :
- API : `http://127.0.0.1:8000/api`
- WebSocket : `ws://127.0.0.1:8000/ws/chat/{thread_id}/`

### Authentification
Le token JWT est automatiquement ajouté à l'URL WebSocket :
```
ws://127.0.0.1:8000/ws/chat/1/?token=eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Variables d'environnement
```env
REACT_APP_API_URL=http://127.0.0.1:8000/api
REACT_APP_WS_URL=ws://127.0.0.1:8000  # Optionnel, déduit de API_URL
```

## 📡 API Endpoints utilisés

### GET `/api/chat/threads/`
Récupère la liste des conversations de l'utilisateur connecté.

**Réponse** :
```json
{
  "results": [
    {
      "id": 1,
      "title": "Discussion Projet X",
      "participants": [...],
      "last_message_at": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-10T08:00:00Z"
    }
  ]
}
```

### GET `/api/chat/messages/?thread={thread_id}`
Récupère les messages d'une conversation.

**Réponse** :
```json
{
  "results": [
    {
      "id": 1,
      "thread": 1,
      "author": {
        "id": 1,
        "username": "user1",
        "email": "user1@example.com"
      },
      "content": "Bonjour !",
      "created_at": "2024-01-15T10:30:00Z",
      "edited_at": null
    }
  ]
}
```

### POST `/api/chat/messages/`
Crée un nouveau message.

**Body** :
```json
{
  "thread": 1,
  "content": "Mon message"
}
```

## 🔄 WebSocket Messages

### Messages envoyés

#### Indicateur de frappe
```json
{
  "type": "typing",
  "is_typing": true
}
```

### Messages reçus

#### Nouveau message
```json
{
  "type": "chat_message",
  "payload": {
    "id": 1,
    "thread": 1,
    "author": {...},
    "content": "Mon message",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

#### Indicateur de frappe
```json
{
  "type": "chat_typing",
  "payload": {
    "user_id": 1,
    "is_typing": true
  }
}
```

## 🌍 Traductions

Les traductions sont disponibles dans `src/locales/fr.json` :
- `chat.title` - "Chat"
- `chat.threads` - "Conversations"
- `chat.type_message` - "Tapez votre message..."
- `chat.send` - "Envoyer"
- `chat.connected` - "Connecté"
- Et plus...

**Note** : Les traductions pour les autres langues (en, ar, es, etc.) doivent être ajoutées dans les fichiers correspondants.

## 🚀 Utilisation

### Pour l'utilisateur
1. Se connecter avec un compte (JWT requis)
2. Aller sur `/chat`
3. Sélectionner une conversation dans la liste de gauche
4. Écrire et envoyer des messages
5. Les messages apparaissent en temps réel

### Pour créer une conversation
Utiliser l'API REST :
```bash
POST /api/chat/threads/
{
  "title": "Ma conversation",
  "participant_ids": [2, 3],
  "is_private": true
}
```

## 🔒 Sécurité

- ✅ Authentification JWT requise
- ✅ Vérification des permissions (seuls les participants peuvent voir/écrire)
- ✅ Validation côté serveur
- ✅ Protection CSRF pour les requêtes REST

## 📱 Responsive

- **Desktop** : Sidebar + fenêtre de chat côte à côte
- **Mobile** : Sidebar en haut (liste réduite), fenêtre de chat en dessous
- **Tablette** : Layout adaptatif

## 🎯 Améliorations futures possibles

- [ ] Création de conversations depuis l'interface
- [ ] Upload de fichiers/images
- [ ] Notifications push
- [ ] Recherche dans les messages
- [ ] Réactions aux messages (emoji)
- [ ] Messages épinglés
- [ ] Historique infini (pagination)
- [ ] Indicateur de lecture
- [ ] Mode sombre/clair (déjà géré par le thème global)

## 🐛 Dépannage

### Le WebSocket ne se connecte pas
1. Vérifier que le serveur Django Channels est démarré
2. Vérifier l'URL WebSocket dans la console du navigateur
3. Vérifier que le token JWT est valide
4. Vérifier les CORS si en développement

### Les messages n'apparaissent pas
1. Vérifier la connexion WebSocket (statut "Connecté")
2. Vérifier les permissions (être participant du thread)
3. Vérifier la console pour les erreurs
4. Vérifier que le backend envoie bien les messages via `broadcast_to_group`

### Erreur 4401 (Unauthorized)
- L'utilisateur n'est pas authentifié
- Vérifier que le token est présent dans localStorage

### Erreur 4403 (Forbidden)
- L'utilisateur n'est pas participant du thread
- Vérifier les membres du thread via l'API

## 📝 Notes techniques

- Le hook `useWebSocket` gère automatiquement la reconnexion (5 tentatives max)
- Les messages sont stockés localement dans le state React
- Le scroll automatique se fait avec `scrollIntoView`
- L'indicateur de frappe se désactive après 3 secondes d'inactivité
- Les dates sont formatées selon la langue de l'utilisateur

---

**Date de création** : $(date)
**Version** : 1.0.0

