# 🦅 Canari V2.0 - Anti-Code Rot Pipeline

**Document** : Documentation du pipeline de surveillance du code V2.0 dormant  
**Date** : 2025-12-19  
**Version** : 1.0  
**Workflow** : `.github/workflows/nightly-investment-check.yml`

---

## 🎯 OBJECTIF

Détecter automatiquement si le code V2.0 (dormant) casse silencieusement au fil des évolutions de la V1.6.

**Problème** : Le code V2.0 est présent mais désactivé par `ENABLE_INVESTMENT_FEATURES=False`. Si des modifications V1.6 cassent le code V2.0, nous ne le saurons qu'au moment de l'activer (trop tard).

**Solution** : Pipeline "Canari" qui teste V2.0 toutes les nuits et alerte si des régressions sont détectées.

---

## 🏗️ ARCHITECTURE

### Workflow GitHub Actions

**Fichier** : `.github/workflows/nightly-investment-check.yml`

**Déclenchement** :
- **Cron** : Toutes les nuits à 3h00 UTC (`0 3 * * *`)
- **Manuel** : `workflow_dispatch` (exécution à la demande)

**Jobs** :

1. **`test-v1-baseline`** : Tests V1.6 (baseline)
   - `ENABLE_INVESTMENT_FEATURES=False`
   - Vérifie que V1.6 fonctionne correctement

2. **`test-v2-canary`** : Tests V2.0 (canari)
   - `ENABLE_INVESTMENT_FEATURES=True`
   - Vérifie que V2.0 reste fonctionnel

3. **`analyze-and-alert`** : Analyse et alerte
   - Compare les résultats V1.6 vs V2.0
   - Crée une issue GitHub si Code Rot détecté

---

## 🔍 LOGIQUE DE DÉTECTION

### Code Rot Détecté Si

- ✅ V1.6 passe (baseline OK)
- ❌ V2.0 échoue (canari KO)

**Exemple** :
```
V1.6 Baseline: ✅ 329 tests, 0 échecs
V2.0 Canari:   ❌ 329 tests, 5 échecs
→ 🚨 CODE ROT DÉTECTÉ
```

### Pas de Code Rot Si

- ✅ V1.6 passe ET V2.0 passe
- ❌ V1.6 échoue ET V2.0 échoue (problème général, pas spécifique V2.0)

---

## 📊 RÉSULTATS

### Artifacts Uploadés

- `test-results-v1-baseline/` : Résultats tests V1.6
- `test-results-v2-canary/` : Résultats tests V2.0

**Contenu** :
- `test-results-*.xml` : Résultats JUnit XML
- `test-output-*.txt` : Logs complets des tests

### Issue GitHub Créée

**Si Code Rot détecté** :
- **Titre** : `🦅 [Canari V2.0] Code Rot Détecté - YYYY-MM-DD`
- **Labels** : `canari-v2.0`, `code-rot`, `bug`, `v2.0-dormant`
- **Contenu** : Résultats détaillés + Actions requises

**Évite les doublons** :
- Si une issue ouverte existe déjà, elle est mise à jour avec un commentaire
- Pas de création d'issue multiple pour le même problème

---

## 🚨 ALERTES

### Conditions d'Alerte

**Alerte créée SI et SEULEMENT SI** :
1. V1.6 passe (baseline OK)
2. V2.0 échoue (canari KO)
3. Aucune issue ouverte existante (ou mise à jour si existe)

**Pas d'alerte si** :
- V1.6 et V2.0 passent tous les deux
- V1.6 échoue (problème général, pas spécifique V2.0)
- Issue déjà ouverte (mise à jour au lieu de création)

---

## 🔧 CONFIGURATION

### Variables d'Environnement

**V1.6 Baseline** :
```yaml
ENABLE_INVESTMENT_FEATURES: 'False'
ENABLE_SAKA: 'True'
SAKA_COMPOST_ENABLED: 'True'
SAKA_SILO_REDIS_ENABLED: 'True'
```

**V2.0 Canari** :
```yaml
ENABLE_INVESTMENT_FEATURES: 'True'  # ⭐ Activé pour le canari
ENABLE_SAKA: 'True'
SAKA_COMPOST_ENABLED: 'True'
SAKA_SILO_REDIS_ENABLED: 'True'
```

### Services Requis

- **PostgreSQL 15** : Base de données de test
- **Redis 7** : Cache et Channels

---

## 📋 UTILISATION

### Exécution Automatique

Le workflow s'exécute automatiquement toutes les nuits à 3h00 UTC.

### Exécution Manuelle

```bash
# Via GitHub Actions UI
Actions → Nightly Investment Check → Run workflow

# Via GitHub CLI
gh workflow run "nightly-investment-check.yml"
```

---

## 🔍 DÉBOGAGE

### Vérifier les Résultats

1. **Consulter le workflow** :
   - GitHub Actions → `🦅 Canari V2.0 - Anti-Code Rot`
   - Vérifier les jobs `test-v1-baseline` et `test-v2-canary`

2. **Télécharger les artifacts** :
   - `test-results-v1-baseline/` : Logs V1.6
   - `test-results-v2-canary/` : Logs V2.0

3. **Comparer les échecs** :
   - Identifier les tests qui échouent en V2.0 mais passent en V1.6
   - Analyser les différences dans les logs

### Exemple d'Analyse

```bash
# Télécharger les artifacts
gh run download <run-id>

# Comparer les résultats
diff test-results-v1-baseline/test-output-v1.txt \
     test-results-v2-canary/test-output-v2.txt
```

---

## ✅ ACTIONS EN CAS DE CODE ROT

### 1. Identifier le Problème

- Consulter l'issue GitHub créée automatiquement
- Analyser les logs de tests (artifacts)
- Identifier les tests en échec spécifiques à V2.0

### 2. Corriger le Code

- Analyser pourquoi V2.0 casse alors que V1.6 fonctionne
- Corriger le code V2.0 pour maintenir la compatibilité
- Vérifier que les corrections n'impactent pas V1.6

### 3. Vérifier la Correction

- Relancer le workflow manuellement
- Vérifier que V2.0 passe maintenant
- Fermer l'issue GitHub une fois corrigé

---

## 📚 RÉFÉRENCES

- **Architecture Sleeping Giant** : `docs/architecture/ARCHITECTURE_SLEEPING_GIANT_V1.6_V2.0.md`
- **Guide Dormance V2.0** : `docs/production/GUIDE_V2_DORMANCY.md`
- **Workflow** : `.github/workflows/nightly-investment-check.yml`

---

## 🎯 MÉTRIQUES DE SUCCÈS

### Objectifs

- **Détection précoce** : Code Rot détecté avant activation V2.0
- **Taux de faux positifs** : < 5%
- **Temps de résolution** : < 48h après détection

### Monitoring

- **Fréquence d'exécution** : Quotidienne (3h UTC)
- **Couverture** : 100% des tests backend + frontend
- **Alertes** : Issues GitHub automatiques

---

## 🔄 AMÉLIORATIONS FUTURES

### Phase 2

- [ ] Tests de performance V2.0 vs V1.6
- [ ] Détection de régressions de performance
- [ ] Alertes par email (en plus des issues GitHub)

### Phase 3

- [ ] Tests d'intégration E2E V2.0
- [ ] Vérification de la compatibilité des migrations
- [ ] Dashboard de santé V2.0

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : Documentation DevOps**

