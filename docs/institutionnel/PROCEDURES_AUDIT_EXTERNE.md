 # 📋 PROCÉDURES D'AUDIT EXTERNE EGOEJO

**Date** : 2025-01-03  
**Version** : 1.0  
**Objectif** : Rendre le projet "Audit-Ready" pour n'importe quel cabinet comptable ou ONG.

---

## 🎯 Vue d'Ensemble

Ce document fournit les procédures complètes pour un audit externe du système EGOEJO, couvrant :

1. **Intégrité SAKA** : Vérification que les balances SAKA sont cohérentes avec les transactions
2. **Dons EUR** : Rapprochement bancaire (Stripe vs Base de données)
3. **Checklist Auditeur** : Liste de contrôle pour un audit tiers

---

## 1️⃣ VÉRIFICATION DE L'INTÉGRITÉ SAKA

### Principe Fondamental

**Règle d'Intégrité** : `Somme(Balances SAKA) = Somme(Transactions EARN) - Somme(Transactions SPEND)`

Chaque grain SAKA doit être traçable via une `SakaTransaction`. Aucune modification directe du solde SAKA n'est autorisée (Constitution EGOEJO).

### Méthode 1 : Via Endpoint API (Recommandé)

**Endpoint** : `GET /api/compliance/integrity/` (à créer - voir section "Implémentation Recommandée")

**Réponse Attendue** :
```json
{
  "status": "compliant" | "non-compliant",
  "saka_integrity": {
    "total_wallet_balances": 150000,
    "total_earn_transactions": 200000,
    "total_spend_transactions": 50000,
    "calculated_balance": 150000,
    "discrepancy": 0,
    "is_valid": true
  },
  "timestamp": "2025-01-03T10:00:00Z"
}
```

**Interprétation** :
- `is_valid: true` → Intégrité SAKA vérifiée
- `is_valid: false` → Violation détectée, investigation requise
- `discrepancy` → Écart entre balance calculée et balance réelle (doit être 0)

### Méthode 2 : Requête SQL Directe (Audit Avancé)

**Accès** : Accès en lecture seule à la base de données PostgreSQL (via credentials fournis par l'équipe EGOEJO)

**Requête SQL** :
```sql
-- Calcul de l'intégrité SAKA
WITH wallet_totals AS (
    SELECT COALESCE(SUM(balance), 0) AS total_balances
    FROM core_sakawallet
),
transaction_totals AS (
    SELECT 
        COALESCE(SUM(CASE WHEN direction = 'EARN' THEN amount ELSE 0 END), 0) AS total_earn,
        COALESCE(SUM(CASE WHEN direction = 'SPEND' THEN amount ELSE 0 END), 0) AS total_spend
    FROM core_sakatransaction
)
SELECT 
    wt.total_balances AS total_wallet_balances,
    tt.total_earn AS total_earn_transactions,
    tt.total_spend AS total_spend_transactions,
    (tt.total_earn - tt.total_spend) AS calculated_balance,
    (wt.total_balances - (tt.total_earn - tt.total_spend)) AS discrepancy,
    CASE 
        WHEN (wt.total_balances - (tt.total_earn - tt.total_spend)) = 0 THEN true
        ELSE false
    END AS is_valid
FROM wallet_totals wt, transaction_totals tt;
```

**Résultat Attendu** :
- `is_valid` = `true`
- `discrepancy` = `0`

### Méthode 3 : Vérification par Utilisateur (Audit Granulaire)

**Requête SQL** :
```sql
-- Vérification de l'intégrité SAKA par utilisateur
SELECT 
    u.id AS user_id,
    u.username,
    sw.balance AS wallet_balance,
    COALESCE(SUM(CASE WHEN st.direction = 'EARN' THEN st.amount ELSE 0 END), 0) AS total_earn,
    COALESCE(SUM(CASE WHEN st.direction = 'SPEND' THEN st.amount ELSE 0 END), 0) AS total_spend,
    (COALESCE(SUM(CASE WHEN st.direction = 'EARN' THEN st.amount ELSE 0 END), 0) - 
     COALESCE(SUM(CASE WHEN st.direction = 'SPEND' THEN st.amount ELSE 0 END), 0)) AS calculated_balance,
    (sw.balance - (COALESCE(SUM(CASE WHEN st.direction = 'EARN' THEN st.amount ELSE 0 END), 0) - 
                   COALESCE(SUM(CASE WHEN st.direction = 'SPEND' THEN st.amount ELSE 0 END), 0))) AS discrepancy
FROM auth_user u
LEFT JOIN core_sakawallet sw ON sw.user_id = u.id
LEFT JOIN core_sakatransaction st ON st.user_id = u.id
GROUP BY u.id, u.username, sw.balance
HAVING (sw.balance - (COALESCE(SUM(CASE WHEN st.direction = 'EARN' THEN st.amount ELSE 0 END), 0) - 
                      COALESCE(SUM(CASE WHEN st.direction = 'SPEND' THEN st.amount ELSE 0 END), 0))) != 0
ORDER BY ABS(discrepancy) DESC;
```

**Résultat Attendu** : Aucune ligne retournée (tous les utilisateurs ont une intégrité vérifiée)

### Détection des Violations

**Signaux d'Alerte** :
1. `discrepancy != 0` → Modification directe du solde SAKA détectée
2. Email d'alerte reçu (`[URGENT] EGOEJO INTEGRITY BREACH DETECTED`) → Violation en temps réel
3. Logs Django (`logger.critical`) → Tentative de contournement détectée

**Actions en Cas de Violation** :
1. Consulter les logs Django (`django.log`) pour identifier la source
2. Vérifier les emails d'alerte envoyés aux admins
3. Examiner les `SakaTransaction` récentes (dernières 24h) pour identifier l'anomalie
4. Contacter l'équipe EGOEJO pour investigation approfondie

---

## 2️⃣ VÉRIFICATION DES DONS EUROS

### Principe Fondamental

**Règle de Rapprochement** : `Somme(Stripe Charges) = Somme(WalletTransaction DEPOSIT) + Frais Stripe`

Tous les dons doivent être traçables depuis Stripe jusqu'à la base de données EGOEJO.

### Champs Exportables pour Rapprochement Bancaire

#### A. Transactions Stripe (Source de Vérité)

**Export Stripe** : Dashboard Stripe → Payments → Export CSV

**Champs Requis** :
- `charge_id` : ID unique de la charge Stripe
- `payment_intent_id` : ID de l'intention de paiement
- `amount` : Montant en centimes (ex: 5000 = 50.00 €)
- `currency` : Devise (EUR)
- `status` : Statut (succeeded, failed, refunded)
- `created` : Date/heure de création (ISO 8601)
- `customer_email` : Email du donateur
- `description` : Description du paiement
- `fee` : Frais Stripe (en centimes)
- `net` : Montant net après frais (en centimes)

#### B. Transactions Base de Données (EGOEJO)

**Table** : `finance_wallettransaction`

**Champs Exportables** :
```sql
SELECT 
    wt.id AS transaction_id,
    wt.created_at AS transaction_date,
    wt.amount AS amount_eur,
    wt.transaction_type,
    wt.description,
    wt.idempotency_key,
    u.id AS user_id,
    u.email AS user_email,
    u.username,
    ec.id AS escrow_id,
    ec.status AS escrow_status,
    p.id AS project_id,
    p.titre AS project_title
FROM finance_wallettransaction wt
LEFT JOIN finance_userwallet uw ON uw.id = wt.wallet_id
LEFT JOIN auth_user u ON u.id = uw.user_id
LEFT JOIN finance_escrowcontract ec ON ec.pledge_transaction_id = wt.id
LEFT JOIN core_projet p ON p.id = ec.project_id OR p.id = wt.related_project_id
WHERE wt.transaction_type IN ('DEPOSIT', 'PLEDGE_DONATION', 'RELEASE', 'REFUND')
ORDER BY wt.created_at DESC;
```

**Export CSV** :
```bash
# Via Django Admin ou script Python
python manage.py export_donations_csv --output donations_export.csv --date-from 2025-01-01 --date-to 2025-12-31
```

#### C. Rapprochement Automatique

**Script Python de Rapprochement** (à créer) :
```python
# scripts/audit_reconcile_donations.py
import csv
from decimal import Decimal
from datetime import datetime

def reconcile_stripe_vs_db(stripe_csv_path, db_export_csv_path):
    """
    Rapproche les transactions Stripe avec les transactions DB EGOEJO.
    
    Returns:
        dict: Rapport de rapprochement avec écarts identifiés
    """
    # Charger Stripe CSV
    stripe_transactions = {}
    with open(stripe_csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['status'] == 'succeeded':
                charge_id = row['charge_id']
                stripe_transactions[charge_id] = {
                    'amount': Decimal(row['amount']) / 100,  # Convertir centimes en euros
                    'fee': Decimal(row['fee']) / 100,
                    'net': Decimal(row['net']) / 100,
                    'date': datetime.fromisoformat(row['created']),
                    'email': row['customer_email']
                }
    
    # Charger DB Export CSV
    db_transactions = {}
    with open(db_export_csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            transaction_id = row['transaction_id']
            db_transactions[transaction_id] = {
                'amount': Decimal(row['amount_eur']),
                'date': datetime.fromisoformat(row['transaction_date']),
                'email': row['user_email'],
                'type': row['transaction_type']
            }
    
    # Rapprochement
    discrepancies = []
    matched = []
    
    for charge_id, stripe_tx in stripe_transactions.items():
        # Chercher correspondance par montant et email (approximatif)
        matched_db = None
        for db_id, db_tx in db_transactions.items():
            if (abs(stripe_tx['net'] - db_tx['amount']) < Decimal('0.01') and
                stripe_tx['email'] == db_tx['email'] and
                abs((stripe_tx['date'] - db_tx['date']).total_seconds()) < 3600):  # 1h de tolérance
                matched_db = db_tx
                matched.append({
                    'stripe_charge_id': charge_id,
                    'db_transaction_id': db_id,
                    'amount': stripe_tx['net']
                })
                break
        
        if not matched_db:
            discrepancies.append({
                'type': 'stripe_not_in_db',
                'stripe_charge_id': charge_id,
                'amount': stripe_tx['net'],
                'date': stripe_tx['date']
            })
    
    # Vérifier transactions DB non matchées
    for db_id, db_tx in db_transactions.items():
        if db_id not in [m['db_transaction_id'] for m in matched]:
            discrepancies.append({
                'type': 'db_not_in_stripe',
                'db_transaction_id': db_id,
                'amount': db_tx['amount'],
                'date': db_tx['date']
            })
    
    return {
        'total_stripe_transactions': len(stripe_transactions),
        'total_db_transactions': len(db_transactions),
        'matched': len(matched),
        'discrepancies': discrepancies,
        'match_rate': len(matched) / len(stripe_transactions) if stripe_transactions else 0
    }
```

### Vérification "100% des Dons Nets"

**Règle** : `Somme(Dons Bruts) - Frais Stripe - Commission EGOEJO = Somme(Dons Versés aux Projets)`

**Requête SQL** :
```sql
-- Vérification "100% des dons nets"
WITH stripe_deposits AS (
    SELECT 
        COALESCE(SUM(amount), 0) AS total_deposits
    FROM finance_wallettransaction
    WHERE transaction_type = 'DEPOSIT'
),
donations_pledged AS (
    SELECT 
        COALESCE(SUM(amount), 0) AS total_pledged
    FROM finance_wallettransaction
    WHERE transaction_type = 'PLEDGE_DONATION'
),
commissions AS (
    SELECT 
        COALESCE(SUM(amount), 0) AS total_commissions
    FROM finance_wallettransaction
    WHERE transaction_type = 'COMMISSION'
),
releases AS (
    SELECT 
        COALESCE(SUM(amount), 0) AS total_released
    FROM finance_wallettransaction
    WHERE transaction_type = 'RELEASE'
)
SELECT 
    sd.total_deposits AS total_stripe_deposits,
    dp.total_pledged AS total_donations_pledged,
    c.total_commissions AS total_egoejo_commissions,
    r.total_released AS total_released_to_projects,
    (dp.total_pledged - c.total_commissions) AS net_donations_after_commission,
    (r.total_released - (dp.total_pledged - c.total_commissions)) AS discrepancy
FROM stripe_deposits sd, donations_pledged dp, commissions c, releases r;
```

**Résultat Attendu** :
- `discrepancy` = `0` (ou très proche de 0, tolérance de 0.01 € pour arrondis)

---

## 3️⃣ CHECKLIST AUDITEUR TIERS

### A. Sécurité & Accès

- [ ] **Vérifier l'absence de clés API Admin actives en production**
  - **Méthode** : Consulter `backend/config/settings.py` → `ADMIN_API_KEY` doit être `None` ou vide en production
  - **Vérification** : `grep -r "ADMIN_API_KEY" backend/config/settings.py | grep -v "#"`
  
- [ ] **Vérifier les permissions Django Admin**
  - **Méthode** : Accéder à `/admin/` avec un compte test → Vérifier que `SakaWallet` est en `readonly_fields`
  - **Vérification** : `backend/core/admin.py` → `SakaWalletAdmin.readonly_fields` doit contenir `balance`, `total_harvested`, `total_planted`, `total_composted`

- [ ] **Vérifier les logs de modification manuelle SAKA**
  - **Méthode** : Consulter les logs Django (`django.log`) et les emails d'alerte
  - **Recherche** : `grep -i "VIOLATION CONSTITUTION EGOEJO" django.log`
  - **Vérification** : Aucune violation détectée dans les 30 derniers jours

### B. Intégrité SAKA

- [ ] **Vérifier l'intégrité globale SAKA**
  - **Méthode** : Exécuter la requête SQL de la section "Méthode 2" (Vérification de l'Intégrité SAKA)
  - **Résultat Attendu** : `is_valid = true`, `discrepancy = 0`

- [ ] **Vérifier l'intégrité par utilisateur**
  - **Méthode** : Exécuter la requête SQL de la section "Méthode 3" (Vérification par Utilisateur)
  - **Résultat Attendu** : Aucune ligne retournée (tous les utilisateurs ont une intégrité vérifiée)

- [ ] **Vérifier l'absence de modifications directes SAKA**
  - **Méthode** : Consulter les logs Django et les emails d'alerte
  - **Recherche** : `grep -i "Modification directe de SakaWallet" django.log`
  - **Vérification** : Aucune modification directe détectée

- [ ] **Vérifier les limites MANUAL_ADJUST**
  - **Méthode** : Vérifier que les transactions `MANUAL_ADJUST` respectent les limites (1000 SAKA/24h, 500 SAKA/transaction)
  - **Requête SQL** :
    ```sql
    SELECT 
        user_id,
        SUM(amount) AS total_manual_adjust_24h,
        COUNT(*) AS transaction_count
    FROM core_sakatransaction
    WHERE reason = 'manual_adjust'
      AND created_at >= NOW() - INTERVAL '24 hours'
    GROUP BY user_id
    HAVING SUM(amount) > 1000 OR MAX(amount) > 500;
    ```
  - **Résultat Attendu** : Aucune ligne retournée

### C. Dons EUR

- [ ] **Rapprochement Stripe vs Base de Données**
  - **Méthode** : Exporter les transactions Stripe (CSV) et les transactions DB (SQL), exécuter le script de rapprochement
  - **Résultat Attendu** : `match_rate >= 0.99` (99% de correspondance minimum)

- [ ] **Vérification "100% des Dons Nets"**
  - **Méthode** : Exécuter la requête SQL de la section "Vérification 100% des Dons Nets"
  - **Résultat Attendu** : `discrepancy = 0` (ou < 0.01 € pour arrondis)

- [ ] **Vérification des Escrow Contracts**
  - **Méthode** : Vérifier que tous les dons sont cantonnés dans des `EscrowContract`
  - **Requête SQL** :
    ```sql
    SELECT 
        wt.id AS transaction_id,
        wt.amount,
        wt.transaction_type,
        ec.id AS escrow_id,
        ec.status AS escrow_status
    FROM finance_wallettransaction wt
    LEFT JOIN finance_escrowcontract ec ON ec.pledge_transaction_id = wt.id
    WHERE wt.transaction_type = 'PLEDGE_DONATION'
      AND ec.id IS NULL;
    ```
  - **Résultat Attendu** : Aucune ligne retournée (tous les dons sont cantonnés)

### D. Traçabilité & Audit Logs

- [ ] **Vérifier l'existence des AuditLogs**
  - **Méthode** : Consulter la table `core_auditlog`
  - **Requête SQL** :
    ```sql
    SELECT 
        action_type,
        COUNT(*) AS count,
        MIN(created_at) AS first_log,
        MAX(created_at) AS last_log
    FROM core_auditlog
    GROUP BY action_type
    ORDER BY count DESC;
    ```
  - **Vérification** : Les logs couvrent au moins les 12 derniers mois

- [ ] **Vérifier la traçabilité des modifications SAKA**
  - **Méthode** : Vérifier que chaque modification SAKA a une `SakaTransaction` correspondante
  - **Requête SQL** : Voir section "Détection des Violations"
  - **Résultat Attendu** : Aucune violation détectée

### E. Conformité Philosophique

- [ ] **Vérifier l'absence de conversion SAKA ↔ EUR**
  - **Méthode** : Scanner le code source pour des patterns de conversion
  - **Recherche** : `grep -ri "convert.*saka.*eur\|convert.*eur.*saka" backend/`
  - **Résultat Attendu** : Aucun résultat (sauf dans les tests de compliance)

- [ ] **Vérifier la séparation SAKA/EUR dans le frontend**
  - **Méthode** : Vérifier que le badge "Non monétaire" est présent sur les affichages SAKA
  - **Fichier** : `frontend/frontend/src/components/dashboard/FourPStrip.jsx`
  - **Vérification** : Badge "Non monétaire" présent, tooltip explicite SAKA↔EUR non convertible

- [ ] **Vérifier les tests de compliance**
  - **Méthode** : Exécuter les tests de compliance EGOEJO
  - **Commande** : `pytest backend/tests/compliance/ -v -m egoejo_compliance`
  - **Résultat Attendu** : Tous les tests passent

### F. Documentation & Transparence

- [ ] **Vérifier l'existence des documents institutionnels**
  - **Fichiers Requis** :
    - `docs/institutionnel/NOTE_CONCEPTUELLE_FONDATIONS.md`
    - `docs/institutionnel/NOTE_CONCEPTUELLE_ONU.md`
    - `docs/institutionnel/PITCH_ETAT_COLLECTIVITES.md`
    - `docs/institutionnel/PROCEDURES_AUDIT_EXTERNE.md` (ce document)

- [ ] **Vérifier l'endpoint de compliance public**
  - **Endpoint** : `GET /api/public/egoejo-compliance.json`
  - **Vérification** : Endpoint accessible sans authentification, retourne un JSON valide avec `compliance_status`

---

## 4️⃣ IMPLÉMENTATION RECOMMANDÉE

### Endpoint `/api/compliance/integrity/`

**Fichier à Créer** : `backend/core/api/compliance_views.py` (ajouter la fonction)

**Code Recommandé** :
```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Sum, Q
from core.models.saka import SakaWallet, SakaTransaction

@api_view(['GET'])
@permission_classes([AllowAny])  # Public endpoint pour audit externe
def saka_integrity_check(request):
    """
    Endpoint public pour vérifier l'intégrité SAKA.
    
    GET /api/compliance/integrity/
    
    Returns:
        JsonResponse: Rapport d'intégrité SAKA
    """
    # Calculer la somme des balances SAKA
    total_wallet_balances = SakaWallet.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    # Calculer la somme des transactions EARN
    total_earn = SakaTransaction.objects.filter(
        direction='EARN'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Calculer la somme des transactions SPEND
    total_spend = SakaTransaction.objects.filter(
        direction='SPEND'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Calculer la balance théorique
    calculated_balance = total_earn - total_spend
    
    # Calculer l'écart
    discrepancy = total_wallet_balances - calculated_balance
    
    # Déterminer si l'intégrité est valide
    is_valid = (discrepancy == 0)
    
    return Response({
        'status': 'compliant' if is_valid else 'non-compliant',
        'saka_integrity': {
            'total_wallet_balances': total_wallet_balances,
            'total_earn_transactions': total_earn,
            'total_spend_transactions': total_spend,
            'calculated_balance': calculated_balance,
            'discrepancy': discrepancy,
            'is_valid': is_valid
        },
        'timestamp': timezone.now().isoformat()
    })
```

**Ajouter dans `backend/core/urls.py`** :
```python
from core.api.compliance_views import saka_integrity_check

urlpatterns = [
    # ... autres routes ...
    path("compliance/integrity/", saka_integrity_check, name="saka-integrity-check"),
]
```

---

## 5️⃣ CONTACTS & SUPPORT

**Pour Questions d'Audit** :
- Email : audit@egoejo.org (à créer)
- Documentation : `docs/institutionnel/`
- Endpoint Compliance : `GET /api/public/egoejo-compliance.json`

**Pour Accès Base de Données** :
- Contacter l'équipe technique EGOEJO
- Fournir : Nom du cabinet, Nom de l'auditeur, Période d'audit, Justification

---

## 📊 RAPPORT D'AUDIT TYPE

**Structure Recommandée** :

1. **Résumé Exécutif**
   - Date d'audit
   - Période couverte
   - Score de conformité global

2. **Intégrité SAKA**
   - Résultat de la vérification
   - Écarts identifiés (si applicable)
   - Recommandations

3. **Dons EUR**
   - Rapprochement Stripe vs DB
   - Vérification "100% des Dons Nets"
   - Recommandations

4. **Conformité Philosophique**
   - Séparation SAKA/EUR
   - Anti-accumulation
   - Recommandations

5. **Conclusion**
   - Conformité globale
   - Points d'attention
   - Recommandations prioritaires

---

**Statut** : ✅ **DOCUMENTATION CRÉÉE**  
**Prochaine Étape** : Implémenter l'endpoint `/api/compliance/integrity/` (voir section 4)

