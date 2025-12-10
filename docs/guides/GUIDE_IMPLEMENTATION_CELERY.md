# 🔧 Guide d'Implémentation Celery - EGOEJO

**Date** : 2025-01-27  
**Objectif** : Configurer Celery pour traitement asynchrone des tâches

---

## 📦 Installation

### 1. Installer les dépendances

```bash
cd backend
pip install celery flower
```

**Note** : `flower` est optionnel mais recommandé pour le monitoring.

### 2. Vérifier Redis

Celery utilise Redis comme broker. Vérifier que `REDIS_URL` est configuré :

```env
REDIS_URL=redis://localhost:6379/0
```

---

## ⚙️ Configuration

### 1. Fichiers créés

- ✅ `backend/config/celery.py` - Configuration Celery
- ✅ `backend/config/__init__.py` - Import Celery app
- ✅ `backend/core/tasks.py` - Tâches asynchrones
- ✅ `backend/core/__init__.py` - Découverte des tâches

### 2. Variables d'environnement

Aucune variable supplémentaire nécessaire. Celery utilise `REDIS_URL` existant.

---

## 🚀 Démarrage

### Développement Local

**Terminal 1 - Django** :
```bash
cd backend
python manage.py runserver
```

**Terminal 2 - Celery Worker** :
```bash
cd backend
celery -A config worker --loglevel=info
```

**Terminal 3 - Flower (optionnel, monitoring)** :
```bash
cd backend
celery -A config flower
```

Accéder à Flower : http://localhost:5555

### Production (Railway)

**Start Command** :
```bash
python manage.py migrate && celery -A config worker --loglevel=info --detach && daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

**Ou séparer en services** :
- Service 1 : Django + Daphne
- Service 2 : Celery Worker

---

## 📋 Tâches Disponibles

### 1. Envoi d'Emails

```python
from core.tasks import send_email_task

# Envoyer un email de manière asynchrone
send_email_task.delay(
    to_email='user@example.com',
    subject='Bienvenue',
    html_content='<h1>Bienvenue !</h1>'
)
```

### 2. Calculs ImpactDashboard

```python
from core.tasks import update_impact_dashboard_metrics

# Mettre à jour les métriques en arrière-plan
update_impact_dashboard_metrics.delay(user_id=123)
```

### 3. Traitement d'Images

```python
from core.tasks import process_image_task

# Traiter une image uploadée
process_image_task.delay(
    image_path='projets/image.jpg',
    max_width=1920,
    max_height=1080,
    quality=85
)
```

### 4. Email de Bienvenue

```python
from core.tasks import send_welcome_email

# Envoyer email de bienvenue
send_welcome_email.delay(user_id=123)
```

---

## 🔄 Intégration dans les Vues

### Exemple : Envoi d'email après inscription

```python
# backend/core/api/auth_views.py
from core.tasks import send_welcome_email

class RegisterView(APIView):
    def post(self, request):
        # Créer l'utilisateur
        user = User.objects.create(...)
        
        # Envoyer email en arrière-plan (non-bloquant)
        send_welcome_email.delay(user.id)
        
        return Response({'success': True})
```

### Exemple : Traitement d'image après upload

```python
# Dans votre vue d'upload
from core.tasks import process_image_task

def upload_image(request):
    # Sauvegarder l'image
    image = request.FILES['image']
    image_path = default_storage.save('projets/image.jpg', image)
    
    # Traiter en arrière-plan
    process_image_task.delay(image_path)
    
    return Response({'success': True, 'image_path': image_path})
```

---

## 📊 Monitoring

### Flower (Interface Web)

1. Démarrer Flower : `celery -A config flower`
2. Accéder à : http://localhost:5555
3. Voir :
   - Tâches en cours
   - Tâches terminées
   - Tâches échouées
   - Statistiques workers

### Logs

Les tâches loggent automatiquement :
- Succès : `logger.info()`
- Erreurs : `logger.error()`
- Retries : Automatiques avec backoff exponentiel

---

## 🧪 Tests

### Tester une tâche

```python
# Dans Django shell
from core.tasks import send_email_task

# Exécuter de manière synchrone (pour tests)
result = send_email_task('test@example.com', 'Test', '<p>Test</p>')
print(result)
```

### Mock Celery en tests

```python
# backend/core/tests.py
from unittest.mock import patch

@patch('core.tasks.send_email_task.delay')
def test_register_sends_email(mock_send_email):
    # Test que l'email est envoyé
    response = client.post('/api/auth/register/', {...})
    mock_send_email.assert_called_once()
```

---

## 🔍 Dépannage

### Worker ne démarre pas

```bash
# Vérifier Redis
redis-cli ping

# Vérifier REDIS_URL
echo $REDIS_URL
```

### Tâches en attente

```bash
# Voir les tâches en attente
celery -A config inspect active

# Purger les tâches
celery -A config purge
```

### Erreurs de connexion Redis

- Vérifier que Redis est démarré
- Vérifier `REDIS_URL` dans les variables d'environnement
- Vérifier que la DB Redis est différente de Channels (DB 0) et Cache (DB 1)

---

## 📚 Références

- [Celery Documentation](https://docs.celeryq.dev/)
- [Flower Documentation](https://flower.readthedocs.io/)
- [Django + Celery Best Practices](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)

---

**Dernière mise à jour** : 2025-01-27

