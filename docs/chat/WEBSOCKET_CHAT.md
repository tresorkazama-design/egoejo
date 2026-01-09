# 💬 WebSocket Chat - Documentation Technique EGOEJO

**Date** : 2025-01-27  
**Version** : 1.0  
**Objectif** : Documentation complète du système WebSocket Chat EGOEJO

---

## 🎯 Vue d'Ensemble

Le système WebSocket Chat EGOEJO permet la communication en temps réel entre les membres de la communauté via Django Channels. Il utilise WebSocket pour la réception de messages en temps réel et REST API pour l'envoi de messages.

**Caractéristiques** :
- ✅ Authentification JWT requise
- ✅ Vérification de membership (seuls les participants peuvent se connecter)
- ✅ Heartbeat ping/pong pour maintenir la connexion
- ✅ Typing indicator (indicateur de frappe)
- ✅ Broadcast de messages en temps réel
- ✅ Tests E2E complets

---

## 📁 Architecture

### Backend

**Fichiers Principaux** :
- **`backend/core/consumers.py`** : `ChatConsumer` (WebSocket consumer)
  - `connect()` : Authentification + vérification membership
  - `disconnect()` : Nettoyage de la connexion
  - `receive_json()` : Gestion ping/pong et typing indicator
  - `chat_message()` : Réception de messages broadcastés
  - `chat_typing()` : Réception de typing indicators

- **`backend/core/routing.py`** : Routes WebSocket
  - `ws/chat/<int:thread_id>/` : Connexion WebSocket pour un thread

- **`backend/config/asgi.py`** : Configuration ASGI
  - `AuthMiddlewareStack` : Authentification WebSocket
  - `URLRouter` : Routing WebSocket

- **`backend/core/models/chat.py`** : Modèles
  - `ChatThread` : Thread de conversation
  - `ChatMessage` : Message de chat
  - `ChatMembership` : Appartenance à un thread (rôles : owner, moderator, member)

- **`backend/core/api/chat.py`** : API REST
  - `ChatThreadViewSet` : Gestion des threads
  - `ChatMessageViewSet` : Gestion des messages (POST crée et broadcast)

- **`backend/core/api/common.py`** : Utilitaires
  - `broadcast_to_group()` : Broadcast de messages via Channels

### Frontend

**Fichiers Principaux** :
- **`frontend/frontend/src/hooks/useWebSocket.js`** : Hook React pour WebSocket
  - Gestion de la connexion
  - Reconnexion automatique (5 tentatives max)
  - Heartbeat ping/pong (toutes les 30 secondes)
  - Authentification via token JWT

- **`frontend/frontend/src/components/ChatWindow.jsx`** : Composant chat
  - Utilise `useWebSocket` pour la connexion
  - Gestion des messages en temps réel
  - Typing indicator
  - Scroll automatique

---

## 🔐 Authentification

### WebSocket Authentication

L'authentification WebSocket utilise `AuthMiddlewareStack` de Django Channels :

1. **Token JWT dans l'URL** : Le token est passé en query parameter
   ```
   ws://127.0.0.1:8000/ws/chat/1/?token=eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

2. **AuthMiddlewareStack** : Authentifie automatiquement l'utilisateur depuis le token
   - Si le token est valide → `scope['user']` = User authentifié
   - Si le token est invalide/absent → `scope['user']` = AnonymousUser

3. **Vérification dans ChatConsumer** :
   ```python
   user = self.scope['user']
   if user.is_anonymous:
       await self.close(code=4401)  # Unauthorized
       return
   ```

### Codes de Fermeture

- **4401** : Unauthorized (utilisateur anonyme)
- **4403** : Forbidden (utilisateur non-membre du thread)
- **1000** : Normal closure (fermeture normale)

---

## 🔄 Flux de Messages

### 1. Envoi de Message (REST API)

**POST** `/api/chat/messages/`

**Body** :
```json
{
  "thread": 1,
  "content": "Mon message"
}
```

**Processus** :
1. Validation du message (utilisateur doit être membre du thread)
2. Création du message en DB
3. Broadcast via `broadcast_to_group()` :
   ```python
   broadcast_to_group(f"chat_thread_{thread.pk}", "chat_message", data)
   ```
4. Tous les WebSocket connectés au thread reçoivent le message

### 2. Réception de Message (WebSocket)

**Format du message reçu** :
```json
{
  "type": "chat_message",
  "payload": {
    "id": 1,
    "thread": 1,
    "author": {
      "id": 1,
      "username": "user1",
      "email": "user1@example.com"
    },
    "content": "Mon message",
    "created_at": "2025-01-27T10:00:00Z"
  }
}
```

**Processus** :
1. `ChatConsumer.chat_message()` est appelé automatiquement par Channels
2. Le message est envoyé à tous les WebSocket connectés au groupe `chat_thread_{thread_id}`
3. Le frontend reçoit le message et l'affiche

---

## 💓 Heartbeat (Ping/Pong)

### Objectif

Maintenir la connexion WebSocket active et détecter les connexions mortes.

### Implémentation

**Frontend** : Envoie un `ping` toutes les 30 secondes
```javascript
ws.send(JSON.stringify({ type: 'ping' }));
```

**Backend** : Répond avec un `pong`
```python
if message_type == 'ping':
    await self.send_json({'type': 'pong'})
```

**Frontend** : Vérifie qu'un `pong` est reçu dans les 60 dernières secondes
- Si pas de `pong` depuis 60s → reconnexion automatique

---

## ⌨️ Typing Indicator

### Objectif

Indiquer aux autres utilisateurs qu'un utilisateur est en train de taper.

### Implémentation

**Frontend** : Envoie un typing indicator
```javascript
ws.send(JSON.stringify({
  type: 'typing',
  is_typing: true
}));
```

**Backend** : Broadcast le typing indicator au groupe
```python
if message_type == 'typing':
    await self.channel_layer.group_send(
        self.group_name,
        {
            'type': 'chat_typing',
            'payload': {
                'user_id': self.scope['user'].pk,
                'is_typing': bool(content.get('is_typing')),
            },
        },
    )
```

**Format du message reçu** :
```json
{
  "type": "chat_typing",
  "payload": {
    "user_id": 1,
    "is_typing": true
  }
}
```

---

## 🧪 Tests

### Tests Backend (pytest)

**Fichier** : `backend/core/tests/websocket/test_chat_consumer.py`

**Tests Inclus** :
- ✅ `test_anon_close_4401` : Anon rejeté avec code 4401
- ✅ `test_authenticated_user_connects` : Utilisateur authentifié membre peut se connecter
- ✅ `test_non_member_close_4403` : Non-membre rejeté avec code 4403
- ✅ `test_member_can_connect` : Membre peut se connecter
- ✅ `test_member_after_joining` : Utilisateur peut se connecter après avoir rejoint
- ✅ `test_ping_pong` : Heartbeat ping/pong fonctionne
- ✅ `test_typing_indicator_sent` : Typing indicator est envoyé
- ✅ `test_typing_indicator_broadcast` : Typing indicator est broadcasté
- ✅ `test_receive_chat_message` : Message chat est reçu via WebSocket

**Exécution** :
```bash
pytest backend/core/tests/websocket/test_chat_consumer.py -v
```

### Tests E2E (Playwright)

**Fichier** : `frontend/frontend/e2e/chat-websocket.spec.js`

**Tests Inclus** :
- ✅ `User A se connecte, envoie message via REST, reçoit via WebSocket`
- ✅ `Typing indicator fonctionne`
- ✅ `Heartbeat ping/pong fonctionne`

**Exécution** :
```bash
# Mode full-stack (nécessite backend + frontend)
E2E_MODE=full-stack npx playwright test e2e/chat-websocket.spec.js
```

---

## 🚀 Comment Lancer Localement

### Prérequis

1. **Backend** : Django + Channels + Redis
   ```bash
   # Installer les dépendances
   cd backend
   pip install -r requirements.txt
   
   # Démarrer Redis (requis pour Channels)
   redis-server
   
   # Démarrer Django (avec Channels)
   python manage.py runserver
   ```

2. **Frontend** : React + Vite
   ```bash
   cd frontend/frontend
   npm install
   npm run dev
   ```

### Configuration

**Variables d'environnement Backend** :
```bash
# Redis pour Channels
REDIS_URL=redis://127.0.0.1:6379/0

# JWT Secret
SECRET_KEY=your-secret-key
```

**Variables d'environnement Frontend** :
```bash
# API URL
REACT_APP_API_URL=http://127.0.0.1:8000/api

# WebSocket URL (optionnel, déduit de API_URL)
REACT_APP_WS_URL=ws://127.0.0.1:8000
```

### Test Manuel

1. **Créer un compte** : Aller sur `/register` et créer un compte
2. **Se connecter** : Aller sur `/login` et se connecter
3. **Créer un thread** : Utiliser l'API REST ou l'interface
4. **Ouvrir le chat** : Aller sur `/chat` et sélectionner un thread
5. **Envoyer un message** : Taper un message et l'envoyer
6. **Vérifier en temps réel** : Le message doit apparaître immédiatement

---

## 🔒 Sécurité

### Authentification

- ✅ JWT requis pour se connecter au WebSocket
- ✅ Vérification automatique via `AuthMiddlewareStack`
- ✅ Rejet des utilisateurs anonymes (code 4401)

### Permissions

- ✅ Vérification de membership avant connexion
- ✅ Seuls les participants peuvent se connecter
- ✅ Rejet des non-membres (code 4403)

### Validation

- ✅ Validation côté serveur pour tous les messages
- ✅ Vérification que l'utilisateur est membre du thread avant envoi
- ✅ Protection CSRF pour les requêtes REST

---

## 📊 Modération (P1/P2)

### Modération Minimale

**Fichiers** :
- `backend/core/models/chat_moderation.py` : Modèle `ChatMessageReport`
- `backend/core/api/chat_moderation.py` : API de modération

**Fonctionnalités** :
- ✅ Signalement de messages (`POST /api/chat/reports/`)
- ✅ Stockage des signalements pour audit
- ✅ Statuts : pending, reviewed, dismissed
- ✅ Un utilisateur ne peut signaler un message qu'une fois

**Endpoint** :
```
POST /api/chat/reports/
{
  "message": 1,
  "reason": "Contenu inapproprié"
}
```

**Limitations** :
- ⚠️ Pas d'action automatique (pas de suppression automatique)
- ⚠️ Modération manuelle uniquement (admin doit examiner)

---

## ⚡ Rate-Limit (P1/P2 - Non Implémenté)

**Fichier** : `backend/core/tests/websocket/test_chat_rate_limit.py`

**Statut** : Placeholder avec `@pytest.mark.xfail`

**Tests** :
- ⚠️ `test_rate_limit_messages` : Rate-limit sur les messages (non implémenté)
- ⚠️ `test_rate_limit_typing` : Rate-limit sur les typing indicators (non implémenté)

**À Implémenter** :
- Limiter le nombre de messages par seconde
- Limiter le nombre de typing indicators par seconde
- Rejeter les messages si limite dépassée

---

## 🐛 Dépannage

### Le WebSocket ne se connecte pas

1. **Vérifier Redis** : Redis doit être démarré pour Channels
   ```bash
   redis-cli ping  # Doit retourner PONG
   ```

2. **Vérifier le token JWT** : Le token doit être valide et présent dans l'URL
   ```javascript
   const token = localStorage.getItem('token');
   const wsUrl = `ws://127.0.0.1:8000/ws/chat/1/?token=${token}`;
   ```

3. **Vérifier les CORS** : En développement, vérifier que CORS est configuré
   ```python
   # backend/config/settings.py
   CORS_ALLOWED_ORIGINS = ['http://localhost:5173']
   ```

4. **Vérifier les logs** : Vérifier les logs Django pour les erreurs
   ```bash
   python manage.py runserver --verbosity 2
   ```

### Les messages n'apparaissent pas

1. **Vérifier la connexion WebSocket** : Statut "Connecté" dans l'interface
2. **Vérifier les permissions** : Être membre du thread
3. **Vérifier la console** : Erreurs JavaScript dans la console
4. **Vérifier le backend** : `broadcast_to_group()` est appelé

### Erreur 4401 (Unauthorized)

- L'utilisateur n'est pas authentifié
- Vérifier que le token est présent dans `localStorage`
- Vérifier que le token est valide (non expiré)

### Erreur 4403 (Forbidden)

- L'utilisateur n'est pas membre du thread
- Vérifier les membres du thread via l'API : `GET /api/chat/threads/{id}/`
- Ajouter l'utilisateur au thread si nécessaire

---

## 📚 Références

- **Code Source** :
  - `backend/core/consumers.py` : ChatConsumer
  - `backend/core/routing.py` : Routes WebSocket
  - `backend/core/api/chat.py` : API REST
  - `frontend/frontend/src/hooks/useWebSocket.js` : Hook React

- **Tests** :
  - `backend/core/tests/websocket/test_chat_consumer.py` : Tests backend
  - `frontend/frontend/e2e/chat-websocket.spec.js` : Tests E2E

- **Documentation** :
  - `frontend/frontend/CHAT_IMPLEMENTATION.md` : Documentation frontend
  - Django Channels : https://channels.readthedocs.io/

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-27

