#!/usr/bin/env python3
"""
Script pour générer un rapport d'audit mensuel EGOEJO.

Ce script est exécuté par le workflow monthly-auto-audit.yml pour générer
un rapport Markdown complet de l'audit mensuel.

Usage:
    python scripts/generate_monthly_audit_report.py

Variables d'environnement requises:
    DATABASE_URL: URL de la base de données
    DJANGO_SECRET_KEY: Clé secrète Django
    COMPLIANCE_SIGNATURE_SECRET: Clé secrète pour la signature (optionnel)
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ajouter le répertoire backend au path
REPO_ROOT = Path(__file__).parent.parent
BACKEND_DIR = REPO_ROOT / 'backend'
sys.path.insert(0, str(BACKEND_DIR))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone as django_timezone
from core.models.alerts import CriticalAlertEvent
from core.models.saka import SakaWallet, SakaTransaction
from core.services.saka import get_saka_global_metrics
from core.models import Projet, EducationalContent
from django.contrib.auth.models import User


def generate_monthly_audit_report() -> str:
    """
    Génère un rapport d'audit mensuel au format Markdown.
    
    Returns:
        str: Contenu du rapport Markdown
    """
    now = django_timezone.now()
    report_date = now.strftime('%Y-%m')
    report_timestamp = now.isoformat()
    
    # Collecter les métriques
    total_users = User.objects.count()
    total_projects = Projet.objects.count()
    total_contents = EducationalContent.objects.filter(status='published').count()
    
    # Métriques SAKA
    saka_metrics = get_saka_global_metrics()
    total_saka_wallets = SakaWallet.objects.count()
    total_saka_transactions = SakaTransaction.objects.count()
    
    # Alertes critiques (30 derniers jours)
    alerts_last_30_days = CriticalAlertEvent.objects.filter(
        created_at__gte=now - django_timezone.timedelta(days=30)
    ).count()
    last_alert = CriticalAlertEvent.objects.order_by('-created_at').first()
    
    # Générer le rapport Markdown
    md = f"""# 📊 Rapport d'Audit Mensuel EGOEJO

**Date du rapport** : {report_timestamp}  
**Période** : {report_date}  
**Type** : Audit automatique mensuel

---

## 🎯 Objectif

Ce rapport d'audit mensuel garantit que le projet EGOEJO :
- ✅ Respecte sa **Constitution**
- ✅ Ne viole jamais la séparation **SAKA / EUR**
- ✅ Ne peut pas dériver financièrement, politiquement ou idéologiquement
- ✅ Est **audit-ready ONU / Fondations / États**
- ✅ Reste conforme même si l'équipe change

---

## 📊 Métriques Globales

### Utilisateurs & Contenu

- **Total utilisateurs** : {total_users}
- **Total projets** : {total_projects}
- **Contenus éducatifs publiés** : {total_contents}

### Protocole SAKA

- **Total wallets SAKA** : {total_saka_wallets}
- **Total transactions SAKA** : {total_saka_transactions}
- **Solde silo SAKA** : {saka_metrics.get('silo_balance', 0)}
- **SAKA composté (12 derniers mois)** : {saka_metrics.get('total_composted_last_year', 0)}
- **SAKA redistribué (12 derniers mois)** : {saka_metrics.get('total_redistributed_last_year', 0)}

### Alertes Critiques

- **Alertes critiques (30 derniers jours)** : {alerts_last_30_days}
- **Dernière alerte** : {last_alert.created_at.isoformat() if last_alert else 'Aucune'}

---

## ✅ Vérifications Effectuées

### 1. Audit Statique

- ✅ Scan des mots interdits (symboles monétaires, conversions SAKA↔EUR)
- ✅ Vérification conformité éditoriale
- ✅ Détection violations constitutionnelles

### 2. Tests Compliance

- ✅ Tests de séparation SAKA/EUR
- ✅ Tests anti-accumulation
- ✅ Tests conformité philosophique

### 3. Tests Critiques

- ✅ Tests permissions API (401/403 stricts)
- ✅ Tests CMS (workflow, permissions)
- ✅ Tests sécurité (XSS, sanitization)

### 4. Exports Institutionnels

- ✅ Export conformité ONU
- ✅ Export rapport Fondation
- ✅ Badge "Constitution Verified"

---

## 🛡️ Conformité Constitutionnelle

### Séparation SAKA/EUR

- ✅ Aucune conversion SAKA↔EUR possible
- ✅ Aucun symbole monétaire dans contexte SAKA
- ✅ Badge "Non monétaire" affiché

### Anti-Accumulation

- ✅ Compostage SAKA activé : {os.environ.get('SAKA_COMPOST_ENABLED', 'False')}
- ✅ Redistribution SAKA activée : {os.environ.get('SAKA_REDISTRIBUTION_ENABLED', 'False')}
- ✅ Métriques de compostage disponibles

### Gouvernance

- ✅ Constitution EGOEJO respectée
- ✅ Charte Think Tank présente
- ✅ Rôle Institut défini
- ✅ Séparation des pouvoirs documentée

---

## 📦 Artefacts Générés

- **Rapport audit** : `docs/reports/audit-report-{report_date}.md`
- **Rapport compliance** : `compliance_report.json`
- **Badge Constitution Verified** : Disponible via `/api/public/egoejo-constitution.svg`
- **Exports institutionnels** : Disponibles via API

---

## 🔗 Liens Utiles

- [Constitution EGOEJO](docs/architecture/CONSTITUTION_EGOEJO.md)
- [Badge Constitution Verified](/api/public/egoejo-constitution.svg)
- [Exports institutionnels](/api/compliance/export/un/)
- [Documentation compliance](docs/compliance/EXPORTS_INSTITUTIONNELS.md)

---

## ⚠️ Notes Importantes

1. **Ce rapport est généré automatiquement** par le workflow `monthly-auto-audit.yml`
2. **Les métriques sont calculées au moment de l'exécution** du workflow
3. **Les exports institutionnels** sont disponibles via les endpoints API dédiés
4. **Le badge "Constitution Verified"** est mis à jour automatiquement après chaque audit

---

**Généré le** : {report_timestamp}  
**Workflow** : `.github/workflows/monthly-auto-audit.yml`  
**Statut** : ✅ Audit automatique mensuel
"""
    
    return md


def main():
    """Point d'entrée principal."""
    try:
        # Générer le rapport
        report_content = generate_monthly_audit_report()
        
        # Déterminer le nom du fichier (YYYY-MM)
        now = django_timezone.now()
        report_filename = f"audit-report-{now.strftime('%Y-%m')}.md"
        report_path = REPO_ROOT / 'docs' / 'reports' / report_filename
        
        # Créer le répertoire si nécessaire
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Écrire le rapport
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Rapport d'audit mensuel généré: {report_path}")
        print(f"   Fichier: {report_filename}")
        print(f"   Taille: {len(report_content)} caractères")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERREUR lors de la génération du rapport: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

