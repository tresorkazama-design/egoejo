# ✅ Guide de Vérification Complète - Activation SAKA

**Date** : 17 Décembre 2025  
**Objectif** : Vérifier que tout est correctement activé et fonctionnel

---

## 📋 Checklist de Vérification

### Étape 1 : Feature Flags ✅

- [ ] `ENABLE_SAKA=True` défini
- [ ] `SAKA_COMPOST_ENABLED=True` défini
- [ ] `SAKA_SILO_REDIS_ENABLED=True` défini
- [ ] `NOTIFY_EMAIL=votre-email@example.com` défini
- [ ] Service redémarré après ajout des variables

**Vérification** :
```bash
# Utiliser le script de vérification
.\scripts\verify-saka-activation.ps1 https://votre-domaine.com

# Ou manuellement
curl https://votre-domaine.com/api/config/features/
```

**Résultat attendu** :
```json
{
  "saka_enabled": true,
  "saka_compost_enabled": true,
  "saka_silo_redis_enabled": true
}
```

---

### Étape 2 : Celery Beat ✅

- [ ] Service Celery Beat est déployé
- [ ] Celery Beat est actif (vérifier les logs)
- [ ] Redis est accessible
- [ ] `REDIS_URL` est défini

**Vérification** :

1. **Vérifier les logs Celery Beat** :
   ```
   [logs] beat: Starting...
   [logs] Scheduler: Sending due task saka-compost-cycle
   ```

2. **Vérifier que les tâches sont planifiées** :
   - Compostage : Tous les lundis à 3h UTC
   - Redistribution : 1er du mois à 4h UTC
   - Monitoring : Tous les jours à 2h UTC

3. **Vérifier Redis** :
   ```bash
   # Tester la connexion Redis
   redis-cli -u $REDIS_URL ping
   # Réponse attendue: PONG
   ```

---

### Étape 3 : Configuration Email ✅

- [ ] `NOTIFY_EMAIL` est défini
- [ ] Configuration SMTP est correcte
- [ ] Test d'envoi d'email réussi

**Vérification** :

1. **Tester l'envoi d'email** :
   ```python
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   from django.conf import settings
   
   send_mail(
       subject='[EGOEJO] Test',
       message='Test',
       from_email=settings.DEFAULT_FROM_EMAIL,
       recipient_list=[settings.NOTIFY_EMAIL],
   )
   ```

2. **Vérifier votre boîte email**

---

### Étape 4 : Tests E2E en Production ✅

- [ ] Tests E2E passent en production
- [ ] Aucune erreur de timeout
- [ ] Tous les mocks fonctionnent

**Vérification** :

```bash
# Utiliser le script
.\scripts\run-e2e-production.ps1 https://votre-domaine.com

# Ou manuellement
cd frontend/frontend
export PLAYWRIGHT_BASE_URL=https://votre-domaine.com
npx playwright test --config=playwright.production.config.js
```

**Résultat attendu** : Tous les tests passent (12/12 pour saka-cycle-visibility)

---

### Étape 5 : Monitoring ✅

- [ ] Endpoints métriques accessibles
- [ ] Alertes configurées
- [ ] Dashboard de monitoring (si créé)

**Vérification** :

1. **Vérifier les endpoints métriques** (admin uniquement) :
   ```bash
   curl -H "Authorization: Bearer $ADMIN_TOKEN" \
        https://votre-domaine.com/api/saka/metrics/all/
   ```

2. **Vérifier les logs de monitoring** :
   - Chercher dans les logs : `[ALERTE]` ou `[MONITORING]`

---

## 🎯 Validation Finale

### Test Complet

1. **Vérifier les feature flags** : ✅
2. **Vérifier Celery Beat** : ✅
3. **Vérifier l'email** : ✅
4. **Exécuter les tests E2E** : ✅
5. **Vérifier le monitoring** : ✅

### Résultat Attendu

- ✅ Tous les feature flags activés
- ✅ Celery Beat actif et exécutant les tâches
- ✅ Emails d'alerte fonctionnels
- ✅ Tests E2E passent (100%)
- ✅ Métriques accessibles

---

## 🐛 Dépannage

### Problème : Feature flags non activés

**Solution** :
1. Vérifier que les variables sont bien définies
2. Vérifier que le service a été redémarré
3. Vérifier les logs pour voir les erreurs

### Problème : Celery Beat inactif

**Solution** :
1. Vérifier que le service Celery Beat est déployé
2. Vérifier que Redis est accessible
3. Vérifier les logs pour voir les erreurs

### Problème : Tests E2E échouent

**Solution** :
1. Vérifier que l'URL de production est correcte
2. Vérifier que tous les mocks sont configurés
3. Vérifier les timeouts dans la config

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Guide de référence

