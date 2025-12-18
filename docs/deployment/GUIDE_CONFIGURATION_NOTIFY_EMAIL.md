# 📧 Guide de Configuration - NOTIFY_EMAIL

**Date** : 17 Décembre 2025  
**Objectif** : Configurer l'email pour recevoir les alertes de monitoring SAKA

---

## 🎯 Objectif

La variable `NOTIFY_EMAIL` permet de recevoir des alertes par email lorsque :
- Celery Beat est inactif
- Le compostage échoue
- La redistribution échoue
- Redis n'est pas accessible

---

## 📋 Configuration

### 1. Ajouter la Variable d'Environnement

#### Sur Railway

1. Allez dans **Variables** de votre service backend
2. Ajoutez la variable :
   - **Nom** : `NOTIFY_EMAIL`
   - **Valeur** : `votre-email@example.com`
3. Redémarrez le service

#### Sur Vercel

1. Allez dans **Settings** → **Environment Variables**
2. Ajoutez la variable pour l'environnement **Production**
3. Redéployez

### 2. Configuration Email (Django)

Assurez-vous que Django est configuré pour envoyer des emails :

#### Variables Requises

```bash
# Backend SMTP (exemple avec Resend)
RESEND_API_KEY=re_xxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@egoejo.org
NOTIFY_EMAIL=votre-email@example.com
```

#### Configuration dans settings.py

Vérifiez que `settings.py` contient :

```python
# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.resend.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'resend'
EMAIL_HOST_PASSWORD = os.environ.get('RESEND_API_KEY')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@egoejo.org')
NOTIFY_EMAIL = os.environ.get('NOTIFY_EMAIL')
```

---

## 🧪 Test de l'Envoi d'Email

### Test Manuel

```python
# Dans Django shell
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='[EGOEJO] Test d\'alerte',
    message='Ceci est un test d\'alerte SAKA.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[settings.NOTIFY_EMAIL],
    fail_silently=False,
)
```

### Test via Tâche Celery

```python
from core.tasks_monitoring import check_celery_beat_health

# Exécuter la tâche
result = check_celery_beat_health.delay()
print(result.get())
```

---

## 📧 Types d'Alertes

### 1. Celery Beat Inactif

**Déclencheur** : Aucun compostage détecté depuis 8 jours  
**Fréquence** : Tous les jours à 2h UTC  
**Email** : `[EGOEJO] Alerte : Celery Beat peut être inactif`

### 2. Échec de Compostage

**Déclencheur** : Wallets éligibles mais aucun compostage récent  
**Fréquence** : Lundi à 3h30 UTC (après le cycle de compostage)  
**Email** : `[EGOEJO] Alerte : Compostage non exécuté`

### 3. Redis Inaccessible

**Déclencheur** : Erreur de connexion Redis  
**Fréquence** : Toutes les heures  
**Email** : `[EGOEJO] Alerte : Redis non accessible`

---

## 🔍 Vérification

### Vérifier que NOTIFY_EMAIL est défini

```bash
# Dans les logs du service
grep "NOTIFY_EMAIL" logs

# Ou via l'API (si endpoint admin)
curl https://votre-domaine.com/api/admin/config/
```

### Vérifier que les emails sont envoyés

1. Attendez qu'une alerte soit déclenchée
2. Vérifiez votre boîte email
3. Vérifiez les logs pour confirmer l'envoi

---

## ⚠️ Points d'Attention

### Emails Non Reçus

Si vous ne recevez pas d'emails :
1. Vérifiez que `NOTIFY_EMAIL` est bien défini
2. Vérifiez que la configuration SMTP est correcte
3. Vérifiez les logs pour voir les erreurs d'envoi
4. Vérifiez le dossier spam

### Trop d'Emails

Si vous recevez trop d'emails :
1. Vérifiez que les tâches de monitoring ne s'exécutent pas trop souvent
2. Ajustez les seuils dans `tasks_monitoring.py`
3. Désactivez temporairement certaines alertes

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Guide de référence

