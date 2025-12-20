# 🏛️ ORGANISME DE CERTIFICATION EGOEJO GUARDIAN
## Système de Certification Externe

**Document** : Spécification de l'organisme de certification externe  
**Date** : 2025-12-19  
**Version** : 1.0  
**Statut** : Spécification technique

---

## 🎯 VISION

L'**Organisme de Certification EGOEJO Guardian** est un système externe et indépendant qui certifie la conformité des projets avec la Constitution EGOEJO. Il permet à tout projet tiers d'obtenir une certification "EGOEJO Compliant" et d'afficher un badge de conformité.

---

## 🏗️ ARCHITECTURE

### Composants

```
┌─────────────────────────────────────────────────────────┐
│  ORGANISME DE CERTIFICATION EGOEJO GUARDIAN             │
│  (Service Externe Indépendant)                           │
└─────────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│   API REST   │ │  Dashboard  │ │  Database  │
│   (Certif)   │ │  (Admin)    │ │  (Audit)   │
└──────────────┘ └─────────────┘ └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│   Projet A   │ │  Projet B   │ │  Projet C  │
│  (Certifié)  │ │ (En cours)  │ │ (Rejeté)   │
└──────────────┘ └─────────────┘ └────────────┘
```

---

## 🔌 API DE CERTIFICATION

### Endpoints Principaux

#### 1. Soumettre un Projet pour Certification

**Endpoint** : `POST /api/v1/certification/submit`

**Request Body** :
```json
{
  "project_name": "Mon Projet EGOEJO",
  "project_url": "https://github.com/user/project",
  "repository_url": "https://github.com/user/project.git",
  "contact_email": "contact@project.com",
  "description": "Description du projet",
  "version": "1.0.0"
}
```

**Response** :
```json
{
  "certification_id": "cert_abc123",
  "status": "pending",
  "submitted_at": "2025-12-19T10:00:00Z",
  "estimated_review_time": "5-7 business days"
}
```

---

#### 2. Vérifier le Statut de Certification

**Endpoint** : `GET /api/v1/certification/{certification_id}`

**Response** :
```json
{
  "certification_id": "cert_abc123",
  "status": "certified",
  "project_name": "Mon Projet EGOEJO",
  "certified_at": "2025-12-20T14:30:00Z",
  "expires_at": "2026-12-20T14:30:00Z",
  "badge_url": "https://guardian.egoejo.org/badges/cert_abc123.svg",
  "report_url": "https://guardian.egoejo.org/reports/cert_abc123.pdf"
}
```

**Status possibles** :
- `pending` : En attente de vérification
- `in_review` : En cours de vérification
- `certified` : Certifié EGOEJO Compliant
- `rejected` : Rejeté (non conforme)
- `expired` : Certification expirée
- `revoked` : Certification révoquée

---

#### 3. Télécharger le Badge de Certification

**Endpoint** : `GET /api/v1/certification/{certification_id}/badge`

**Response** : Image SVG/PNG du badge "EGOEJO Compliant"

**Formats** :
- SVG (recommandé) : `?format=svg`
- PNG : `?format=png&size=large|medium|small`

---

#### 4. Obtenir le Rapport de Certification

**Endpoint** : `GET /api/v1/certification/{certification_id}/report`

**Response** : PDF du rapport de certification détaillé

---

#### 5. Vérifier la Conformité d'un Repository

**Endpoint** : `POST /api/v1/certification/verify`

**Request Body** :
```json
{
  "repository_url": "https://github.com/user/project.git",
  "branch": "main",
  "commit_sha": "abc123..."
}
```

**Response** :
```json
{
  "is_compliant": true,
  "violations": [],
  "checks": {
    "no_saka_eur_conversion": {
      "status": "pass",
      "message": "Aucune conversion SAKA/EUR détectée"
    },
    "no_financial_return": {
      "status": "pass",
      "message": "Aucun rendement financier sur SAKA détecté"
    },
    "no_monetary_display": {
      "status": "pass",
      "message": "Aucun affichage monétaire du SAKA détecté"
    },
    "saka_priority": {
      "status": "pass",
      "message": "SAKA est prioritaire et non désactivé"
    },
    "anti_accumulation": {
      "status": "pass",
      "message": "Mécanisme d'anti-accumulation présent"
    },
    "saka_cycle": {
      "status": "pass",
      "message": "Cycle SAKA complet et incompressible"
    }
  },
  "score": 100,
  "certification_eligible": true
}
```

---

## 🛡️ PROCESSUS DE CERTIFICATION

### Étape 1 : Soumission

1. Le projet soumet une demande de certification via l'API
2. Le système génère un `certification_id` unique
3. Le statut est défini à `pending`

---

### Étape 2 : Vérification Automatique

1. **Clonage du Repository** : Le système clone le repository GitHub/GitLab
2. **Analyse du Code** : Exécution du Guardian EGOEJO sur le code source
3. **Vérification des Tests** : Vérification de la présence de tests de compliance
4. **Vérification de la Documentation** : Vérification de la présence de documentation Constitution EGOEJO

**Vérifications effectuées** :
- ✅ Absence de conversion SAKA ↔ EUR
- ✅ Absence de mécanismes de rendement financier
- ✅ Priorité de la structure relationnelle (SAKA)
- ✅ Anti-accumulation SAKA
- ✅ Cycle SAKA incompressible
- ✅ Présence de tests de compliance
- ✅ Documentation Constitution EGOEJO

---

### Étape 3 : Vérification Manuelle (Optionnelle)

Pour les projets complexes, une vérification manuelle peut être effectuée par un auditeur certifié EGOEJO Guardian.

---

### Étape 4 : Décision

**Certification accordée** si :
- Toutes les vérifications automatiques passent
- Aucune violation critique détectée
- Tests de compliance présents et passants
- Documentation Constitution EGOEJO présente

**Certification refusée** si :
- Violation critique détectée
- Tests de compliance absents ou échouants
- Documentation Constitution EGOEJO absente

---

### Étape 5 : Émission du Badge

1. Génération du badge "EGOEJO Compliant"
2. Génération du rapport de certification PDF
3. Notification au projet (email)
4. Publication sur le registre public des certifications

---

## 🎨 BADGE DE CERTIFICATION

### Design

Le badge "EGOEJO Compliant" est un badge SVG/PNG qui peut être intégré dans :
- README.md du projet
- Site web du projet
- Documentation
- Page GitHub/GitLab

**Exemple de badge** :
```
┌─────────────────────────────┐
│   🏛️ EGOEJO COMPLIANT       │
│                             │
│   ✅ Constitution Respectée │
│   ✅ SAKA/EUR Séparés       │
│   ✅ Cycle SAKA Intact      │
│                             │
│   Certifié le 2025-12-20    │
│   ID: cert_abc123           │
└─────────────────────────────┘
```

---

### Intégration dans README.md

```markdown
[![EGOEJO Compliant](https://guardian.egoejo.org/badges/cert_abc123.svg)](https://guardian.egoejo.org/certifications/cert_abc123)

> **Ce badge atteste du respect des règles EGOEJO. Il n'atteste ni d'un rendement financier, ni d'une performance économique.**
```

---

## 📊 REGISTRE PUBLIC DES CERTIFICATIONS

### Endpoint Public

**Endpoint** : `GET /api/v1/certifications/public`

**Response** :
```json
{
  "total_certified": 42,
  "certifications": [
    {
      "certification_id": "cert_abc123",
      "project_name": "Mon Projet EGOEJO",
      "project_url": "https://github.com/user/project",
      "certified_at": "2025-12-20T14:30:00Z",
      "status": "certified"
    },
    ...
  ]
}
```

---

## 🔄 RENOUVELLEMENT ET RÉVOCATION

### Renouvellement

- **Durée de validité** : 1 an
- **Renouvellement automatique** : Si le projet reste conforme
- **Notification** : 30 jours avant expiration

### Révocation

La certification peut être révoquée si :
- Violation détectée après certification
- Non-conformité lors d'une vérification périodique
- Demande de révocation du projet

---

## 🛠️ IMPLÉMENTATION TECHNIQUE

### Stack Technologique

- **Backend** : Django REST Framework
- **Database** : PostgreSQL
- **Queue** : Celery + Redis
- **Storage** : S3/R2 pour badges et rapports
- **Frontend** : React (Dashboard admin)

### Composants

#### 1. Service de Certification

**Fichier** : `certification/services.py`

```python
class CertificationService:
    def submit_project(self, project_data):
        """Soumet un projet pour certification"""
        pass
    
    def verify_repository(self, repo_url, branch, commit_sha):
        """Vérifie la conformité d'un repository"""
        pass
    
    def generate_badge(self, certification_id):
        """Génère le badge de certification"""
        pass
    
    def generate_report(self, certification_id):
        """Génère le rapport de certification PDF"""
        pass
```

#### 2. Guardian Externe

**Fichier** : `certification/guardian_external.py`

```python
class ExternalGuardian:
    def clone_repository(self, repo_url, branch):
        """Clone un repository externe"""
        pass
    
    def run_guardian_checks(self, repo_path):
        """Exécute les vérifications Guardian"""
        pass
    
    def check_compliance_tests(self, repo_path):
        """Vérifie la présence de tests de compliance"""
        pass
    
    def check_documentation(self, repo_path):
        """Vérifie la présence de documentation Constitution"""
        pass
```

#### 3. Modèles de Données

**Fichier** : `certification/models.py`

```python
class Certification(models.Model):
    certification_id = models.CharField(max_length=64, unique=True)
    project_name = models.CharField(max_length=255)
    project_url = models.URLField()
    repository_url = models.URLField()
    status = models.CharField(max_length=20)  # pending, certified, rejected, etc.
    submitted_at = models.DateTimeField()
    certified_at = models.DateTimeField(null=True)
    expires_at = models.DateTimeField(null=True)
    score = models.IntegerField(default=0)
    report_url = models.URLField(null=True)
    badge_url = models.URLField(null=True)

class CertificationCheck(models.Model):
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE)
    check_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)  # pass, fail, warning
    message = models.TextField()
    details = models.JSONField(default=dict)
```

---

## 📋 CHECKLIST DE CERTIFICATION

### Vérifications Automatiques

- [ ] **Aucune conversion SAKA ↔ EUR**
  - Pattern : `convert.*saka.*eur`, `saka.*exchange.*rate`
  - Status : `pass` / `fail`

- [ ] **Aucun rendement financier sur SAKA**
  - Pattern : `saka.*roi`, `saka.*yield`, `saka.*interest`
  - Status : `pass` / `fail`

- [ ] **Aucun affichage monétaire du SAKA**
  - Pattern : `saka.*€`, `saka.*\$`, `saka.*euro`
  - Status : `pass` / `fail`

- [ ] **SAKA prioritaire et non désactivé**
  - Pattern : `ENABLE_SAKA.*=.*False`, `disable.*saka`
  - Status : `pass` / `fail`

- [ ] **Anti-accumulation SAKA**
  - Vérification : Présence de mécanisme de compostage
  - Status : `pass` / `fail`

- [ ] **Cycle SAKA incompressible**
  - Vérification : Présence de toutes les étapes (Récolte → Usage → Compost → Silo → Redistribution)
  - Status : `pass` / `fail`

### Vérifications Complémentaires

- [ ] **Tests de compliance présents**
  - Fichiers : `tests/compliance/` ou équivalent
  - Status : `pass` / `fail` / `warning`

- [ ] **Documentation Constitution EGOEJO présente**
  - Fichiers : `docs/architecture/CONSTITUTION_EGOEJO.md` ou équivalent
  - Status : `pass` / `fail` / `warning`

- [ ] **Guardian EGOEJO intégré**
  - Fichiers : `.egoejo/guardian.py` ou équivalent
  - Status : `pass` / `fail` / `warning`

---

## 🚀 DÉPLOIEMENT

### Infrastructure

- **Hébergement** : Railway / Render / AWS
- **Domain** : `guardian.egoejo.org`
- **SSL** : Certificat Let's Encrypt
- **CDN** : Cloudflare (pour badges)

### Variables d'Environnement

```bash
# Database
DATABASE_URL=postgresql://...

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
S3_BUCKET=egoejo-guardian-badges

# GitHub API (pour clonage)
GITHUB_TOKEN=...

# Email (notifications)
SMTP_HOST=...
SMTP_USER=...
SMTP_PASSWORD=...
```

---

## 📈 MÉTRIQUES ET STATISTIQUES

### Dashboard Public

- Nombre total de projets certifiés
- Nombre de projets en cours de certification
- Taux de réussite de certification
- Projets les plus récemment certifiés

### Dashboard Admin

- Statistiques détaillées par vérification
- Temps moyen de certification
- Taux de réjection par raison
- Historique des certifications

---

## 🔐 SÉCURITÉ

### Authentification

- **API Keys** : Pour les projets soumettant des certifications
- **OAuth** : Pour l'accès au dashboard admin
- **JWT** : Pour les sessions utilisateur

### Protection

- **Rate Limiting** : Limitation des requêtes API
- **CORS** : Configuration CORS pour badges
- **Validation** : Validation stricte des entrées
- **Audit Log** : Logging de toutes les actions

---

## 📝 DOCUMENTATION

### Pour les Projets

- Guide de soumission de certification
- Guide d'intégration du badge
- FAQ Certification
- Exemples de projets certifiés

### Pour les Auditeurs

- Guide de vérification manuelle
- Checklist d'audit
- Procédures de révocation
- Escalade des violations

---

## 🎯 ROADMAP

### Phase 1 : MVP (Minimum Viable Product)

- [ ] API de soumission de certification
- [ ] Vérification automatique basique
- [ ] Génération de badge SVG
- [ ] Dashboard admin simple

### Phase 2 : Fonctionnalités Avancées

- [ ] Vérification manuelle par auditeurs
- [ ] Génération de rapport PDF
- [ ] Registre public des certifications
- [ ] Système de renouvellement automatique

### Phase 3 : Écosystème

- [ ] Marketplace de projets certifiés
- [ ] Intégration GitHub Actions
- [ ] Plugin VSCode pour vérification locale
- [ ] API webhooks pour notifications

---

## 📞 CONTACT

Pour toute question sur la certification :
- **Email** : certification@egoejo.org
- **Documentation** : https://guardian.egoejo.org/docs
- **Support** : https://guardian.egoejo.org/support

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : Spécification technique**

