# ⚠️ Points de Vigilance - EGOEJO v1.3.0

**Date** : 2025-01-27  
**Version** : 1.3.0  
**Objectif** : Identifier et adresser la dette technique latente

---

## 🔴 Points de Vigilance Identifiés

### 1. Le "Mix" React (Dette Technique TypeScript)

**Problème** :
- Stack Frontend à la pointe (React 19, Three.js)
- Code contient encore des fichiers `.jsx`
- Migration TypeScript marquée "En Développement"
- Typage faible = risque #1 de bugs en production

**Impact** :
- Erreurs de typage en runtime (Three.js props complexes)
- Refactoring risqué sans typage statique
- Maintenance difficile avec codebase croissante
- Bugs potentiels avec WebSockets et 3D complexes

**Solution** : Voir Axe 3 (Sécurité & Qualité Code)

---

### 2. Complexité de Déploiement

**Problème** :
- Stack complexe : Celery, Redis, Daphne, Gunicorn, Workers
- Orchestration sur Railway devient plus complexe
- Risque de "perdre" des tâches en silence
- Monitoring crucial mais pas toujours configuré

**Composants à orchestrer** :
- Django (HTTP)
- Daphne (WebSockets)
- Celery Worker (tâches asynchrones)
- Redis (broker + cache + channels)
- PostgreSQL (base de données)
- Flower (monitoring Celery - optionnel)
- Sentry (monitoring erreurs)

**Risques** :
- Tâches Celery perdues si worker crash
- WebSockets déconnectés si Daphne redémarre
- Cache Redis perdu si Redis redémarre
- Monitoring insuffisant = problèmes invisibles

**Solutions** :
- Configuration robuste de monitoring (Flower + Sentry)
- Health checks pour tous les services
- Logs structurés et centralisés
- Alertes automatiques

---

## 🚀 Suggestions Stratégiques (Roadmap v1.4.0)

### Axe 1 : L'Intelligence Sémantique (RAG Léger)

**Objectif** : Créer des liens de sens, pas juste de mots.

**Pourquoi** :
- Relier "Philosophie" aux "Projets" (2025)
- Suggestion intelligente : projet "maraîchage sur sol vivant" → contenu "Biodynamie" (même sans mot-clé)
- Proximité vectorielle = suggestions conceptuelles

**Action Technique** :
1. Installer pgvector sur PostgreSQL
2. Créer tâche Celery pour génération embeddings
3. Endpoint recherche sémantique
4. Suggestions automatiques dans l'UI

**Priorité** : 🔴 HAUTE (déjà préparé avec champs embedding)

---

### Axe 2 : Gouvernance Décentralisée (Vote Quadratique)

**Objectif** : Mesurer l'intensité d'une préférence, pas juste la direction.

**Pourquoi** :
- Vote binaire (Oui/Non) limitant pour collectif
- Vote Quadratique : distribution de points (intensité)
- Jugement Majoritaire : classement par préférence
- Adapté aux décisions collectives complexes

**Action Technique** :
1. Ajouter `voting_method` au modèle Poll
2. Adapter frontend pour interface distribution points
3. Calcul résultats vote quadratique
4. Visualisation résultats avancée

**Priorité** : 🟡 MOYENNE (amélioration UX)

---

### Axe 3 : Sécurité & Qualité Code (Verrouillage)

**Objectif** : TypeScript Strict Mode + Scan Anti-Virus

**Pourquoi** :
- Typage faible = bugs en production
- Uploads malveillants = risque sécurité
- Qualité code = maintenabilité

**Action Technique** :
1. ESLint : interdire nouveaux fichiers `.jsx`
2. Forcer `.tsx` pour nouvelles features
3. Scan ClamAV sur uploads (tâche Celery)
4. Configuration TypeScript Strict

**Priorité** : 🔴 HAUTE (sécurité + qualité)

---

## 📋 Plan d'Implémentation

### Phase 1 : Intelligence Sémantique (Semaine 1-2)
- [ ] Installer pgvector
- [ ] Migration VectorField
- [ ] Tâche Celery génération embeddings
- [ ] Endpoint recherche sémantique
- [ ] UI suggestions

### Phase 2 : Vote Quadratique (Semaine 3-4)
- [ ] Modèle Poll étendu
- [ ] Frontend interface vote
- [ ] Calcul résultats
- [ ] Visualisation

### Phase 3 : Sécurité & Qualité (Semaine 5-6)
- [ ] ESLint configuration
- [ ] TypeScript Strict
- [ ] Scan ClamAV
- [ ] Documentation

---

**Dernière mise à jour** : 2025-01-27  
**Statut** : 📋 Plan d'action détaillé

