# 📊 Audit Mensuel Automatique EGOEJO

**Date de création** : 2025-12-10  
**Dernière mise à jour** : 2025-12-10  
**Statut** : ✅ **ACTIF**

---

## 🎯 Objectif

Le workflow d'audit mensuel automatique garantit que le projet EGOEJO :
- ✅ Respecte sa **Constitution**
- ✅ Ne viole jamais la séparation **SAKA / EUR**
- ✅ Ne peut pas dériver financièrement, politiquement ou idéologiquement
- ✅ Est **audit-ready ONU / Fondations / États**
- ✅ Reste conforme même si l'équipe change

---

## 📅 Déclenchement

### Schedule Automatique

Le workflow s'exécute **automatiquement le 1er de chaque mois à 2h00 UTC** :

```yaml
schedule:
  - cron: '0 2 1 * *'
```

### Déclenchement Manuel

Le workflow peut également être déclenché manuellement via l'interface GitHub Actions :

1. Aller dans **Actions** → **Monthly Auto-Audit EGOEJO**
2. Cliquer sur **Run workflow**
3. Sélectionner la branche (généralement `main`)
4. Cliquer sur **Run workflow**

---

## 🔍 Vérifications Effectuées

### 1. Audit Statique

- ✅ Scan des mots interdits (symboles monétaires, conversions SAKA↔EUR)
- ✅ Vérification conformité éditoriale
- ✅ Détection violations constitutionnelles

**Script** : `npm run audit:global` (frontend)

### 2. Tests Compliance

- ✅ Tests de séparation SAKA/EUR
- ✅ Tests anti-accumulation
- ✅ Tests conformité philosophique

**Commandes** :
```bash
pytest tests/compliance/ -v -m egoejo_compliance
```

### 3. Tests Critiques

- ✅ Tests permissions API (401/403 stricts)
- ✅ Tests CMS (workflow, permissions)
- ✅ Tests sécurité (XSS, sanitization)

**Commandes** :
```bash
pytest core/tests/api/test_*_permissions.py core/tests/cms/test_content_permissions.py -v -m critical
```

### 4. Génération Exports Institutionnels

- ✅ Export conformité ONU (JSON + Markdown)
- ✅ Export rapport Fondation (JSON + Markdown)

**Endpoints** :
- `/api/compliance/export/un/`
- `/api/compliance/export/foundation/`
- `/api/compliance/export/un/markdown/`
- `/api/compliance/export/foundation/markdown/`

### 5. Génération Badge

- ✅ Badge "Constitution Verified" (SVG + JSON)

**Endpoints** :
- `/api/public/egoejo-constitution.svg`
- `/api/public/egoejo-constitution.json`

**Script** : `scripts/generate_compliance_report.py`

### 6. Génération Rapport Audit

- ✅ Rapport Markdown complet (`audit-report-YYYY-MM.md`)

**Script** : `scripts/generate_monthly_audit_report.py`

---

## 📦 Artefacts Générés

Le workflow génère les artefacts suivants :

### Rapport Audit

- **Fichier** : `docs/reports/audit-report-YYYY-MM.md`
- **Format** : Markdown
- **Contenu** :
  - Métriques globales (utilisateurs, projets, contenus)
  - Métriques SAKA (wallets, transactions, compostage)
  - Alertes critiques (30 derniers jours)
  - Résumé des vérifications
  - Conformité constitutionnelle

### Rapport Compliance

- **Fichier** : `compliance_report.json`
- **Format** : JSON signé (HMAC-SHA256)
- **Contenu** :
  - Statut de conformité
  - Version de la Constitution
  - Dernière vérification
  - Checklist de conformité
  - Signature cryptographique

### Rapports de Tests

- **Fichier** : `backend/junit-compliance.xml`
- **Format** : JUnit XML
- **Contenu** : Résultats des tests compliance

- **Fichier** : `backend/junit-critical.xml`
- **Format** : JUnit XML
- **Contenu** : Résultats des tests critiques

### Badge Constitution Verified

- **SVG** : Disponible via `/api/public/egoejo-constitution.svg`
- **JSON** : Disponible via `/api/public/egoejo-constitution.json`
- **Statuts** :
  - 🟢 **Vert** : `compliant` (tous les tests passent, rapport frais et signé)
  - 🔴 **Rouge** : `non-compliant` (au moins un test échoue)
  - 🟠 **Orange** : `unknown` (rapport absent, signature invalide, ou rapport trop ancien)

### Exports Institutionnels

- **ONU** : Disponibles via `/api/compliance/export/un/` (JSON) et `/api/compliance/export/un/markdown/` (Markdown)
- **Fondation** : Disponibles via `/api/compliance/export/foundation/` (JSON) et `/api/compliance/export/foundation/markdown/` (Markdown)

---

## 📤 Upload Artefacts

Tous les artefacts sont uploadés dans un artifact GitHub Actions :

- **Nom** : `monthly-audit-report-{run_number}`
- **Rétention** : 90 jours
- **Contenu** :
  - `docs/reports/audit-report-*.md`
  - `compliance_report.json`
  - `backend/compliance-report.json`
  - `backend/junit-compliance.xml`
  - `backend/junit-critical.xml`

---

## 📢 Notifications

### Slack (Optionnel)

Si un webhook Slack est configuré (`SLACK_WEBHOOK_URL`), le workflow envoie une notification avec :
- Statut global (✅ SUCCÈS / ❌ ÉCHEC)
- Statut de chaque vérification
- Lien vers le rapport complet

**Configuration** :
1. Créer un webhook Slack
2. Ajouter le secret `SLACK_WEBHOOK_URL` dans GitHub Secrets
3. La notification sera envoyée automatiquement après chaque audit

**Note** : Le webhook n'est jamais exposé en clair dans les logs.

---

## 🔍 Consultation des Rapports

### Via GitHub Actions

1. Aller dans **Actions** → **Monthly Auto-Audit EGOEJO**
2. Sélectionner une exécution
3. Télécharger l'artifact `monthly-audit-report-{run_number}`
4. Consulter les fichiers dans l'artifact

### Via le Repository

Les rapports sont également commités dans `docs/reports/` :

```bash
# Lister les rapports disponibles
ls docs/reports/audit-report-*.md

# Consulter un rapport
cat docs/reports/audit-report-2025-12.md
```

### Via l'API

Les exports institutionnels sont disponibles via les endpoints API :

```bash
# Export ONU (JSON)
curl -H "Authorization: Bearer {token}" https://api.egoejo.org/api/compliance/export/un/

# Export ONU (Markdown)
curl -H "Authorization: Bearer {token}" https://api.egoejo.org/api/compliance/export/un/markdown/

# Badge Constitution Verified
curl https://api.egoejo.org/api/public/egoejo-constitution.svg
```

---

## ⚠️ En Cas d'Échec

Si un audit échoue :

1. **Consulter les logs** : Voir les détails dans GitHub Actions
2. **Identifier la cause** : Vérifier quelle vérification a échoué
3. **Corriger le problème** : Appliquer les corrections nécessaires
4. **Relancer manuellement** : Déclencher le workflow manuellement pour vérifier

### Exemples de Causes d'Échec

- ❌ **Audit statique** : Violation détectée (symbole monétaire, conversion SAKA↔EUR)
- ❌ **Tests compliance** : Test de conformité échoué
- ❌ **Tests critiques** : Test de permission ou sécurité échoué
- ❌ **Génération exports** : Erreur lors de la génération des exports
- ❌ **Génération badge** : Erreur lors de la génération du badge

---

## 🔗 Références

- **Workflow** : `.github/workflows/monthly-auto-audit.yml`
- **Script rapport** : `scripts/generate_monthly_audit_report.py`
- **Script compliance** : `scripts/generate_compliance_report.py`
- **Exports institutionnels** : `backend/core/api/institutional_exports.py`
- **Badge Constitution Verified** : `backend/core/api/public_compliance.py`
- **Documentation compliance** : `docs/compliance/EXPORTS_INSTITUTIONNELS.md`
- **Documentation tests** : `docs/testing/TESTS_OVERVIEW.md`

---

## 📝 Maintenance

### Modifier le Schedule

Pour modifier la fréquence ou l'heure d'exécution, éditer `.github/workflows/monthly-auto-audit.yml` :

```yaml
schedule:
  - cron: '0 2 1 * *'  # 1er de chaque mois à 2h00 UTC
```

### Ajouter une Vérification

1. Ajouter une étape dans le workflow
2. Mettre à jour le script `generate_monthly_audit_report.py` si nécessaire
3. Documenter la nouvelle vérification dans ce fichier

### Modifier le Format du Rapport

Éditer `scripts/generate_monthly_audit_report.py` pour modifier le format ou le contenu du rapport.

---

**Dernière mise à jour** : 2025-12-10  
**Statut** : ✅ **ACTIF**

