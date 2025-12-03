# 🏗️ Architecture Frontend ↔ Backend - EGOEJO

## Vue d'ensemble

Le projet EGOEJO utilise une **architecture séparée** (SPA + API REST) :

- **Frontend** : Application React (Vite) qui tourne sur `http://localhost:5173`
- **Backend** : API Django REST Framework qui tourne sur `http://localhost:8000`

Ils communiquent via des **requêtes HTTP/HTTPS** et **WebSockets**.

---

## 📡 Communication HTTP (REST API)

### 1. Configuration Frontend

**Fichier : `frontend/frontend/src/utils/api.js`**

```javascript
// URL de base de l'API (configurable via variable d'environnement)
export const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api` 
  : 'http://127.0.0.1:8000/api';

// Fonction utilitaire pour faire des appels API
export const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Ajouter le token JWT si l'utilisateur est connecté
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, config);
  // ... gestion des erreurs
  return response.json();
};
```

### 2. Configuration Backend (Django)

**Fichier : `backend/config/settings.py`**

```python
# CORS : Autoriser les requêtes depuis le frontend
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Frontend Vite
    'http://127.0.0.1:5173',
]

# REST Framework : Configuration de l'API
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## 🔄 Flux de Communication

### Exemple 1 : Récupérer la liste des projets

**Frontend (`Projets.jsx`) :**
```javascript
import { fetchAPI } from '../../utils/api';

function Projets() {
  const [projets, setProjets] = useState([]);
  
  useEffect(() => {
    // Appel API vers Django
    fetchAPI('/projets/')
      .then(data => setProjets(data.results))
      .catch(error => console.error(error));
  }, []);
  
  return <div>{/* Afficher les projets */}</div>;
}
```

**Backend (`core/views.py`) :**
```python
from rest_framework.views import APIView
from rest_framework.response import Response

class ProjetListCreate(APIView):
    def get(self, request):
        # Récupérer les projets depuis la base de données
        projets = Projet.objects.filter(status='published')
        serializer = ProjetSerializer(projets, many=True)
        return Response({'results': serializer.data})
```

**Requête HTTP :**
```
GET http://127.0.0.1:8000/api/projets/
Headers:
  Content-Type: application/json
  Authorization: Bearer <token_jwt> (si connecté)
```

**Réponse HTTP :**
```json
{
  "results": [
    {
      "id": 1,
      "titre": "Projet 1",
      "description": "Description du projet"
    }
  ]
}
```

---

### Exemple 2 : Authentification (Login)

**Frontend (`Login.jsx`) :**
```javascript
const handleLogin = async (username, password) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    // Stocker le token JWT
    localStorage.setItem('token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
  } catch (error) {
    console.error('Erreur de connexion', error);
  }
};
```

**Backend (`core/api/auth_views.py`) :**
```python
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(APIView):
    def post(self, request):
        # Créer un nouvel utilisateur
        user = User.objects.create_user(...)
        # Retourner les tokens JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
```

---

### Exemple 3 : Créer une intention (Rejoindre)

**Frontend (`Rejoindre.jsx`) :**
```javascript
const handleSubmit = async (formData) => {
  try {
    const result = await fetchAPI('/intents/rejoindre/', {
      method: 'POST',
      body: JSON.stringify(formData)
    });
    // Succès !
  } catch (error) {
    // Gérer l'erreur
  }
};
```

**Backend (`core/views.py`) :**
```python
@csrf_exempt
def rejoindre(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        intent = Intent.objects.create(
            nom=data['nom'],
            email=data['email'],
            profil=data['profil']
        )
        return JsonResponse({'id': intent.id, 'status': 'created'})
```

---

## 🔌 Communication WebSocket (Temps Réel)

### Configuration

**Frontend (`hooks/useWebSocket.js`) :**
```javascript
const ws = new WebSocket('ws://127.0.0.1:8000/ws/chat/1/?token=<jwt_token>');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Recevoir un nouveau message
};
```

**Backend (`core/consumers.py`) :**
```python
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Authentifier via JWT
        user = await self.authenticate()
        await self.accept()
    
    async def receive(self, text_data):
        # Recevoir un message du frontend
        data = json.loads(text_data)
        # Diffuser aux autres utilisateurs
        await self.channel_layer.group_send(...)
```

---

## 🔐 Authentification JWT

### Flux complet

1. **Login** : Frontend envoie `username` + `password` → Backend retourne `access_token` + `refresh_token`
2. **Stockage** : Frontend stocke les tokens dans `localStorage`
3. **Requêtes suivantes** : Frontend ajoute `Authorization: Bearer <token>` dans les headers
4. **Validation** : Django vérifie le token à chaque requête
5. **Refresh** : Si le token expire, utiliser `refresh_token` pour obtenir un nouveau `access_token`

---

## 🌐 CORS (Cross-Origin Resource Sharing)

### Pourquoi CORS est nécessaire ?

Le frontend (`localhost:5173`) et le backend (`localhost:8000`) sont sur des **origines différentes** (ports différents).

**Sans CORS** : Le navigateur bloque les requêtes entre origines différentes.

**Avec CORS** : Django autorise explicitement les requêtes depuis le frontend.

**Configuration Django :**
```python
# backend/config/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Frontend
    'http://127.0.0.1:5173',
]
```

---

## 📊 Schéma de Communication

```
┌─────────────────┐                    ┌─────────────────┐
│   FRONTEND      │                    │    BACKEND      │
│   (React)       │                    │   (Django)      │
│                 │                    │                 │
│  localhost:5173 │                    │  localhost:8000 │
└────────┬────────┘                    └────────┬────────┘
         │                                      │
         │  1. Requête HTTP GET /api/projets/  │
         │─────────────────────────────────────>│
         │                                      │
         │                                      │ 2. Interroge la DB
         │                                      │    (PostgreSQL/SQLite)
         │                                      │
         │  3. Réponse JSON {results: [...]}   │
         │<─────────────────────────────────────│
         │                                      │
         │  4. Affiche les projets dans l'UI   │
         │                                      │
```

---

## 🔧 Variables d'Environnement

### Frontend (`.env`)
```env
VITE_API_URL=http://127.0.0.1:8000
```

### Backend (`.env`)
```env
DJANGO_SECRET_KEY=...
DEBUG=1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DB_NAME=egoejo_db
DB_USER=egoejo_user
DB_PASSWORD=egoejo_password
```

---

## 🚀 Démarrage

### 1. Démarrer le Backend
```bash
cd backend
python manage.py runserver
# → http://127.0.0.1:8000
```

### 2. Démarrer le Frontend
```bash
cd frontend/frontend
npm run dev
# → http://localhost:5173
```

### 3. Communication
Le frontend fait automatiquement des requêtes vers `http://127.0.0.1:8000/api/` grâce à `VITE_API_URL`.

---

## 📝 Résumé

1. **Frontend React** = Interface utilisateur (UI)
2. **Backend Django** = API REST + Base de données
3. **Communication** = HTTP (REST) + WebSocket (temps réel)
4. **Authentification** = JWT (tokens)
5. **CORS** = Autorise les requêtes cross-origin
6. **Variables d'env** = Configuration flexible (dev/prod)

Les deux services tournent **indépendamment** et communiquent via le **réseau** (HTTP/WebSocket).

