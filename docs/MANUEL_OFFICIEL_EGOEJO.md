# 📘 MANUEL OFFICIEL EGOEJO

**Version** : 1.0.0  
**Date** : 2025-01-06  
**Statut** : Document de Référence Factuel  
**Méthodologie** : Basé exclusivement sur le code, les tests, la CI et les documents existants

---

## ⚠️ AVERTISSEMENT IMPORTANT

Ce manuel décrit **uniquement ce qui est réellement implémenté** dans le code source, testé automatiquement, et documenté. Aucune projection, aucune intention non codée, aucun embellissement.

**Critère de validation** : Un auditeur externe hostile, une fondation prudente, ou une équipe future sans connaissance des fondateurs doit pouvoir vérifier chaque affirmation dans le code source.

---

## 1. NATURE DU PROJET

### 1.1 Ce qu'est EGOEJO aujourd'hui

**EGOEJO** est une application web full-stack (Django backend + React/Vite frontend) qui permet :

1. **Référencement de projets régénératifs** : Des projets locaux (refuges, jardins nourriciers, ateliers) peuvent être référencés sur la plateforme
2. **Collecte de dons** : Les utilisateurs peuvent faire des dons en Euro (EUR) via Stripe pour financer ces projets
3. **Système d'engagement interne (SAKA)** : Les utilisateurs peuvent gagner et dépenser des unités SAKA (grains) pour participer à la gouvernance (votes, soutien de projets)
4. **Gouvernance participative** : Système de votes et de sondages pour la prise de décision collective

**Périmètre fonctionnel réel** (basé sur `README.md` et le code) :

- **Backend** : API Django REST avec authentification JWT, WebSockets (Channels), base de données PostgreSQL
- **Frontend** : SPA React/Vite avec Three.js pour visualisation 3D, i18n (FR, EN, AR, DE, ES, SW)
- **Paiements** : Intégration Stripe pour les dons (webhook `payment_intent.succeeded`)
- **Temps réel** : WebSockets pour chat et votes
- **Monitoring** : Système d'alertes critiques (email + webhook Slack optionnel)

**Ce que EGOEJO n'est PAS** (basé sur les tests de compliance) :

- ❌ Une plateforme d'investissement (fonctionnalité V2.0 dormante, protégée par feature flag)
- ❌ Un système de conversion SAKA ↔ EUR (strictement interdit, testé automatiquement)
- ❌ Un système de rendement financier (tests bloquants empêchent toute promesse de rendement)

### 1.2 Structure technique réelle

**Répertoires principaux** (basé sur `README.md`) :

- `backend/` : API Django + tests
- `frontend/` : SPA React/Vite
- `docs/` : Documentation (constitution, audits, gouvernance, institutionnel)
- `.github/workflows/` : Workflows CI/CD (compliance, tests, PR bot)

**Dépendances principales** (basé sur `backend/requirements.txt` et `frontend/package.json`) :

- **Backend** : Django 5.2.9, Django REST Framework, Channels (WebSockets), Stripe, PostgreSQL
- **Frontend** : React, Vite, Three.js, React Query, i18next

---

## 2. ARCHITECTURE RÉELLE

### 2.1 Double structure SAKA / Euro

**Séparation technique réelle** (basé sur `backend/core/models/saka.py` et `backend/finance/models.py`) :

#### Modèle SAKA (`SakaWallet`)

**Fichier** : `backend/core/models/saka.py`

**Champs** :
- `balance` : `PositiveIntegerField` (grains SAKA, entiers positifs uniquement)
- `total_harvested` : `PositiveIntegerField` (total jamais récolté)
- `total_planted` : `PositiveIntegerField` (total jamais planté/engagé)
- `total_composted` : `PositiveIntegerField` (total jamais composté)
- `last_activity_date` : `DateTimeField` (dernière activité SAKA)

**Aucun champ monétaire** : Pas de `balance_eur`, pas de `exchange_rate`, pas de conversion.

#### Modèle Euro (`UserWallet`)

**Fichier** : `backend/finance/models.py`

**Champs** :
- `balance` : `DecimalField(max_digits=12, decimal_places=2)` (EUR, décimales)
- `transactions` : Relation vers `WalletTransaction` (historique des transactions EUR)

**Aucun champ SAKA** : Pas de `balance_saka`, pas de conversion.

### 2.2 Ce qui est techniquement séparé

**Séparation au niveau modèle** (vérifié par `backend/tests/compliance/test_saka_eur_separation.py`) :

1. **Tables distinctes** :
   - `core_sakawallet` : Table PostgreSQL pour les portefeuilles SAKA
   - `finance_userwallet` : Table PostgreSQL pour les portefeuilles EUR

2. **Aucune ForeignKey croisée** :
   - `SakaWallet` n'a pas de relation vers `UserWallet`
   - `UserWallet` n'a pas de relation vers `SakaWallet`
   - Seul lien : `user` (OneToOneField vers `User`)

3. **Services distincts** :
   - `backend/core/services/saka.py` : Services SAKA uniquement (`harvest_saka`, `spend_saka`, `run_saka_compost_cycle`, `redistribute_saka_silo`)
   - `backend/finance/ledger_services/ledger.py` : Services financiers uniquement (allocation Stripe, calcul frais)

### 2.3 Ce qui est volontairement non-convertible

**Interdictions encodées** (vérifiées par tests automatiques) :

#### Test de séparation SAKA/EUR

**Fichier** : `backend/tests/compliance/test_saka_eur_separation.py`

**Patterns interdits détectés** :
- `convert.*saka.*to.*eur|convert.*eur.*to.*saka` : Conversion explicite
- `saka.*=.*eur|eur.*=.*saka` : Affectation directe
- `saka.*\*.*eur|eur.*\*.*saka` : Multiplication (taux de change)
- `saka.*/.*eur|eur.*/.*saka` : Division (taux de change)
- `price.*saka|saka.*price` : Prix du SAKA
- `exchange.*saka|saka.*exchange` : Échange SAKA
- `rate.*saka.*eur|rate.*eur.*saka` : Taux de change
- `value.*saka.*eur|value.*eur.*saka` : Valeur EUR du SAKA

**Action** : Le test `test_aucune_conversion_saka_eur_dans_code()` **échoue** si un pattern interdit est détecté.

#### PR Bot

**Fichier** : `.github/scripts/egoejo_pr_bot.py`

**Vérifications automatiques** :
- Scan des fichiers modifiés pour détecter les patterns interdits
- Blocage de la PR si violation détectée (workflow `egoejo-pr-bot.yml`)

**Références précises au code** :

```python
# backend/core/models/saka.py, ligne 194
# RÈGLE ABSOLUE : Aucune conversion SAKA ↔ EUR n'est autorisée.
```

```python
# backend/tests/compliance/test_saka_eur_separation.py, ligne 88-97
# Patterns interdits : conversion SAKA ↔ EUR
forbidden_patterns = [
    r'convert.*saka.*to.*eur|convert.*eur.*to.*saka',
    r'saka.*=.*eur|eur.*=.*saka',
    # ...
]
```

---

## 3. SAKA : RÈGLES EFFECTIVEMENT ENCODÉES

### 3.1 Anti-accumulation

**Mécanisme réel** (basé sur `backend/core/services/saka.py` et `backend/config/settings.py`) :

#### Compostage automatique

**Fonction** : `run_saka_compost_cycle()` (ligne 443 de `backend/core/services/saka.py`)

**Paramètres configurables** (via variables d'environnement) :
- `SAKA_COMPOST_ENABLED` : Active/désactive le compostage (défaut : `False`)
- `SAKA_COMPOST_INACTIVITY_DAYS` : Durée d'inactivité avant compost (défaut : `90` jours)
- `SAKA_COMPOST_RATE` : Pourcentage de balance à composter (défaut : `0.10` = 10%)
- `SAKA_COMPOST_MIN_BALANCE` : Balance minimale pour composter (défaut : `50` SAKA)
- `SAKA_COMPOST_MIN_AMOUNT` : Montant minimum à composter (défaut : `10` SAKA)

**Logique réelle** :
1. Identifie les wallets inactifs depuis `SAKA_COMPOST_INACTIVITY_DAYS` jours
2. Calcule le montant à composter : `min(balance * SAKA_COMPOST_RATE, balance - SAKA_COMPOST_MIN_BALANCE)`
3. Diminue le `balance` du wallet
4. Augmente le `total_composted` du wallet
5. Crée une entrée `SakaCompostLog` (traçabilité)
6. Alimente le `SakaSilo` (réservoir commun)

**Validation** : `backend/config/settings.py` (lignes 586-602) valide que :
- `SAKA_COMPOST_RATE > 0` et `<= 1.0`
- `SAKA_COMPOST_INACTIVITY_DAYS` entre 1 et 365

**Tests** : `backend/tests/compliance/test_saka_compost_depreciation_effective.py` vérifie que :
- Le compostage diminue réellement le solde
- Le compostage ne peut pas être contourné
- Le compostage retourne au Silo

#### Redistribution du Silo

**Fonction** : `redistribute_saka_silo()` (ligne 691 de `backend/core/services/saka.py`)

**Paramètres configurables** :
- `SAKA_SILO_REDIS_ENABLED` : Active/désactive la redistribution (défaut : `False`)
- `SAKA_SILO_REDIS_RATE` : Pourcentage du Silo redistribué par cycle (défaut : `0.05` = 5%)
- `SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY` : Activité minimale pour être éligible (défaut : `1`)

**Logique réelle** :
1. Calcule le montant à redistribuer : `Silo.balance * SAKA_SILO_REDIS_RATE`
2. Identifie les wallets éligibles (activité >= `SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY`)
3. Redistribue équitablement entre les wallets éligibles
4. Crée des `SakaTransaction` de type `REDISTRIBUTION`

**Tests** : `backend/tests/compliance/test_silo_redistribution.py` vérifie que :
- Le Silo ne peut pas être vidé par un seul acteur
- La redistribution suit les règles collectives
- Aucune redistribution individualisée arbitraire

### 3.2 Compostage : réel vs paramétrable

**État réel** (basé sur `backend/config/settings.py`, lignes 543-631) :

#### Paramètres par défaut

- `SAKA_COMPOST_ENABLED = False` : **Désactivé par défaut**
- `SAKA_COMPOST_INACTIVITY_DAYS = 90` : 90 jours d'inactivité
- `SAKA_COMPOST_RATE = 0.10` : 10% de la balance
- `SAKA_COMPOST_MIN_BALANCE = 50` : Minimum 50 SAKA pour composter
- `SAKA_COMPOST_MIN_AMOUNT = 10` : Minimum 10 SAKA compostés

#### Validation en production

**Code** : `backend/config/settings.py` (lignes 552-556)

```python
if ENABLE_SAKA and not SAKA_COMPOST_ENABLED:
    raise ImproperlyConfigured(
        "SAKA_COMPOST_ENABLED doit être True en production si ENABLE_SAKA=True. "
        "Le compostage est obligatoire pour éviter l'accumulation."
    )
```

**Action** : Si `ENABLE_SAKA=True` et `SAKA_COMPOST_ENABLED=False`, Django lève `ImproperlyConfigured` au démarrage.

**Limite connue** : Cette validation n'empêche pas un administrateur de modifier les settings après le démarrage (via variable d'environnement ou modification directe).

### 3.3 Pouvoirs admin réellement bloqués

**Protections implémentées** (basé sur `backend/core/models/saka.py`) :

#### Protection au niveau modèle

**Fichier** : `backend/core/models/saka.py` (lignes 186-235)

**Mécanisme** : `save()` vérifie si la modification est autorisée via `AllowSakaMutation` context manager.

**Code réel** :
```python
def save(self, *args, **kwargs):
    # Autoriser la création initiale (pk None)
    if self.pk is None:
        return super().save(*args, **kwargs)
    
    # Vérifier si la mutation est autorisée (via service SAKA)
    if not is_saka_mutation_allowed():
        # Vérifier si des champs SAKA protégés sont modifiés
        protected_fields = ['balance', 'total_harvested', 'total_planted', 'total_composted']
        # ... vérification et ValidationError si modification directe
```

**Action** : Si modification directe détectée (sans `AllowSakaMutation`), lève `ValidationError` avec message "VIOLATION CONSTITUTION EGOEJO".

#### Protection au niveau QuerySet

**Fichier** : `backend/core/models/saka.py` (lignes 55-109)

**Mécanisme** : `SakaWalletQuerySet.update()` est **toujours bloqué**.

**Code réel** :
```python
def update(self, **kwargs):
    # BLOQUER TOUTE tentative de update(), même si aucun champ protégé n'est modifié
    error_msg = (
        "VIOLATION CONSTITUTION EGOEJO : Direct update() is forbidden on SakaWallet. "
        "Use SakaTransaction service (harvest_saka, spend_saka, compost, redistribute)."
    )
    logger.critical(error_msg)
    raise ValidationError(error_msg)
```

**Action** : Toute tentative de `SakaWallet.objects.update()` lève `ValidationError`.

#### Protection au niveau admin Django

**Fichier** : `backend/core/admin.py` (vérifié par `backend/tests/compliance/test_admin_protection.py`)

**Mécanisme** : `readonly_fields` sur les champs SAKA protégés.

**Tests** : `test_modification_directe_sakawallet_possible_mais_logged()` vérifie que :
- La modification directe dans l'admin est possible (limite connue)
- Mais elle est loggée et alerte est envoyée

**Limite connue** : L'admin Django peut techniquement modifier les champs SAKA si `readonly_fields` n'est pas configuré correctement. Le test vérifie que l'alerte est envoyée, mais ne bloque pas la modification.

### 3.4 Limites connues

#### Limite 1 : raw() SQL non bloqué au niveau ORM

**Description** : Les requêtes SQL directes (`SakaWallet.objects.raw()`, `connection.cursor().execute()`) contournent les protections ORM.

**Détection** : `backend/core/models/saka.py` (lignes 245-363) - Signal `post_save` détecte les modifications sans `SakaTransaction` correspondante.

**Code réel** :
```python
@receiver(post_save, sender=SakaWallet)
def log_and_alert_saka_wallet_changes(sender, instance, created, **kwargs):
    # DÉTECTION RAW() SQL : Vérifier la cohérence avec les transactions SAKA
    # Si la modification n'a pas de SakaTransaction correspondante, c'est un contournement
    if not matching_transaction and abs_delta > 0:
        send_critical_alert(
            title="INTEGRITY BREACH DETECTED",
            payload={
                "violation_type": "saka_wallet_bypass",
                # ...
            }
        )
```

**Action** : Alerte critique envoyée (email + webhook si activé), mais la modification n'est **pas bloquée**.

**Référence** : `docs/reports/AUDIT_COLLEGE_SENIOR_2025_FINAL_V3.md` (Risque #2, ligne 97)

#### Limite 2 : Signal post_save ne détecte pas raw() SQL

**Description** : Le signal `post_save` n'est **pas déclenché** par `raw()` SQL.

**Code réel** : `backend/core/models/saka.py` (lignes 360-363)

```python
# NOTE IMPORTANTE : raw() SQL ne déclenche PAS le signal post_save
# Le signal post_save ne peut détecter que les modifications via save().
# Pour détecter raw() SQL, il faudrait un trigger SQL ou un audit de cohérence périodique.
```

**Action** : Détection indirecte via incohérence avec `SakaTransaction` (si modification sans transaction correspondante dans les 5 dernières minutes).

**Limite** : Si `raw() SQL` crée aussi une `SakaTransaction` factice, la détection échoue.

#### Limite 3 : Admin Django peut modifier (avec alerte)

**Description** : L'admin Django peut techniquement modifier les champs SAKA si `readonly_fields` n'est pas configuré.

**Test** : `backend/tests/compliance/test_admin_protection.py::test_modification_directe_sakawallet_possible_mais_logged`

**Action** : Alerte envoyée, mais modification non bloquée.

---

## 4. EURO : RÔLE EXACT

### 4.1 Ce que l'Euro permet

**Fonctionnalités réelles** (basé sur `backend/finance/models.py` et `backend/finance/ledger_services/ledger.py`) :

#### Collecte de dons

**Modèle** : `WalletTransaction` avec type `PLEDGE_DONATION`

**Processus** :
1. Paiement Stripe via webhook `payment_intent.succeeded`
2. Extraction des frais Stripe réels depuis `balance_transaction.fee`
3. Calcul proportionnel des frais (donation vs tip)
4. Création de `WalletTransaction` avec :
   - `amount_gross` : Montant brut (avant frais)
   - `stripe_fee` : Part des frais allouée
   - `amount_net` : Montant net (après frais)
5. Allocation vers `PROJECT_ESCROW` (ledger pour les projets)

**Code réel** : `backend/finance/ledger_services/ledger.py` (fonction `allocate_payment_to_ledgers`, ligne 88)

**Tests** : `backend/finance/tests/test_stripe_segregation.py` vérifie que :
- `Sum(Net) + Sum(Fees) = Total Payment` (intégrité financière)
- Répartition proportionnelle correcte (donation vs tip)

#### Gestion des tips

**Modèle** : `WalletTransaction` avec type `DEPOSIT` (pour tips)

**Processus** :
1. Même processus que les dons
2. Allocation vers `OPERATING` (ledger pour l'association)
3. Frais Stripe proportionnels calculés

**Code réel** : `backend/finance/ledger_services/ledger.py` (lignes 88-200)

### 4.2 Ce que l'Euro ne permet pas

**Interdictions encodées** :

#### Aucune conversion SAKA ↔ EUR

**Vérifié par** : `backend/tests/compliance/test_saka_eur_separation.py`

**Action** : Test échoue si pattern de conversion détecté.

#### Aucun rendement financier sur SAKA

**Vérifié par** : `backend/tests/compliance/test_saka_no_financial_return.py`

**Patterns interdits** :
- `saka.*interest.*rate` : Intérêt sur SAKA
- `saka.*dividend.*payment` : Dividende basé sur SAKA
- `saka.*yield.*calculation` : Rendement SAKA
- `saka.*roi` : Return on Investment SAKA
- `saka.*apy` : Annual Percentage Yield SAKA

**Action** : Test échoue si pattern détecté.

### 4.3 Murs techniques existants

#### Séparation au niveau base de données

**Tables distinctes** :
- `core_sakawallet` : Table SAKA
- `finance_userwallet` : Table EUR

**Aucune contrainte de clé étrangère** entre les deux tables.

#### Séparation au niveau code

**Services distincts** :
- `backend/core/services/saka.py` : Services SAKA uniquement
- `backend/finance/ledger_services/ledger.py` : Services financiers uniquement

**Aucune fonction de conversion** dans aucun service.

#### Tests automatiques bloquants

**Fichiers** :
- `backend/tests/compliance/test_saka_eur_separation.py` : Détecte les conversions
- `backend/tests/compliance/test_saka_eur_etancheite.py` : Vérifie l'étanchéité
- `backend/tests/compliance/test_no_saka_eur_conversion.py` : Scan récursif du code

**Action** : CI échoue si violation détectée.

---

## 5. GOUVERNANCE RÉELLE

### 5.1 Ce qui est automatisé

#### PR Bot

**Fichier** : `.github/scripts/egoejo_pr_bot.py`

**Workflow** : `.github/workflows/egoejo-pr-bot.yml`

**Vérifications automatiques** :
1. **Séparation SAKA/EUR** : Détecte les patterns de conversion
2. **Anti-accumulation** : Détecte la désactivation du compostage
3. **Cycle SAKA** : Vérifie l'incompressibilité du cycle
4. **Gouvernance éditoriale** : Détecte le vocabulaire financier interdit
5. **Label Finance-Audit** : Vérifie que les modifications financières ont le label requis

**Action** : Bloque la PR si violation détectée (workflow échoue, merge impossible si Branch Protection Rules configurées).

**Limite connue** : Branch Protection Rules doivent être configurées manuellement dans GitHub UI (voir `docs/governance/BRANCH_PROTECTION.md`).

#### Tests de compliance automatiques

**Workflow** : `.github/workflows/egoejo-compliance.yml`

**Tests exécutés** :
- `backend/tests/compliance/test_saka_eur_separation.py`
- `backend/tests/compliance/test_no_saka_accumulation.py`
- `backend/tests/compliance/test_saka_compost_depreciation_effective.py`
- `backend/tests/compliance/test_saka_cycle_incompressible.py`
- Et autres tests marqués `@pytest.mark.egoejo_compliance`

**Action** : Workflow échoue si un test de compliance échoue.

**Référence** : `.github/workflows/egoejo-compliance.yml`

#### Audit de contenu

**Script** : `scripts/audit_content.py`

**Vérifications** :
- **Blacklist** : Détecte les mots interdits (financiers, spirituels)
- **Whitelist** : Vérifie la présence de mots requis (Subsistance, Contribution, Régénération)
- **Exclusions** : Exclut les documents de compliance (`docs/legal/`, `docs/constitution/`, etc.)

**Action** : Bloque le déploiement si violation détectée.

**Référence** : `scripts/audit_content.py`

### 5.2 Ce qui dépend encore d'actions humaines

#### Branch Protection Rules GitHub

**État** : Documentation créée (`docs/governance/BRANCH_PROTECTION.md`), mais **non configurée** dans GitHub UI.

**Action requise** : Configuration manuelle dans GitHub Settings → Branches → Add rule pour `main`.

**Risque** : Sans Branch Protection Rules, un développeur peut merger une PR même si les tests de compliance échouent.

**Référence** : `docs/reports/AUDIT_COLLEGE_SENIOR_2025_FINAL_V3.md` (Risque #1, ligne 57)

#### Review de PR

**État** : PR Bot commente les PR, mais la review humaine est requise pour merger.

**Action requise** : Au moins 1 approbation requise (si Branch Protection Rules configurées).

### 5.3 PR bots existants

#### EGOEJO PR Bot

**Fichier** : `.github/scripts/egoejo_pr_bot.py`

**Fonctionnalités** :
- Analyse les fichiers modifiés dans la PR
- Détecte les violations philosophiques (conversion SAKA/EUR, désactivation compostage, etc.)
- Détecte les violations techniques (modifications directes, etc.)
- Vérifie le label "Finance-Audit" pour les modifications financières
- Commente la PR avec l'analyse
- Bloque la PR si violation critique détectée

**Workflow** : `.github/workflows/egoejo-pr-bot.yml`

**Référence** : `.github/scripts/egoejo_pr_bot.py` (lignes 61-986)

### 5.4 Limites connues

#### Limite 1 : Branch Protection Rules non configurées

**Description** : Les workflows sont bloquants, mais GitHub permet toujours le merge si Branch Protection Rules ne sont pas configurées.

**Impact** : Un développeur peut contourner toutes les protections en mergant manuellement.

**Correctif** : Suivre `docs/governance/BRANCH_PROTECTION.md` pour configurer manuellement.

#### Limite 2 : PR Bot ne bloque pas si GitHub API échoue

**Description** : Si l'API GitHub échoue, le PR Bot peut ne pas commenter, mais le workflow peut quand même passer.

**Impact** : Violations non détectées si API GitHub indisponible.

---

## 6. SÉCURITÉ & AUDITABILITÉ

### 6.1 Alertes réellement branchées

#### Système d'alertes critiques

**Fichier** : `backend/core/utils/alerts.py`

**Fonction** : `send_critical_alert()`

**Canaux** :
1. **Email** : `mail_admins()` (Django) - **Toujours activé** si `ALERT_EMAIL_ENABLED=True`
2. **Webhook/Slack** : `send_webhook_alert()` - **Optionnel** si `ALERT_WEBHOOK_ENABLED=True`

**Configuration** (basé sur `backend/config/settings.py`, lignes 472-480) :
- `ALERT_EMAIL_ENABLED` : Active/désactive les alertes email (défaut : `True`)
- `ALERT_WEBHOOK_ENABLED` : Active/désactive les webhooks (défaut : `False`)
- `ALERT_WEBHOOK_URL` : URL du webhook (Slack ou générique)
- `ALERT_WEBHOOK_TYPE` : Type de webhook (`slack` ou `generic`)

**Dédoublonnage** : Cache de 5 minutes (`DEDUPE_CACHE_TTL = 300`) pour éviter le spam.

**Tests** : `backend/core/tests/utils/test_alerts.py` (20 tests : 11 email + 9 webhook)

#### Détection de violations SAKA

**Fichier** : `backend/core/models/saka.py` (lignes 245-363)

**Signal** : `post_save` sur `SakaWallet`

**Détections** :
1. **Contournement détecté** : Modification sans `SakaTransaction` correspondante dans les 5 dernières minutes
2. **Modification massive** : Modification > 10000 SAKA (seuil critique)

**Action** : Appel à `send_critical_alert()` avec payload structuré.

**Code réel** :
```python
@receiver(post_save, sender=SakaWallet)
def log_and_alert_saka_wallet_changes(sender, instance, created, **kwargs):
    # DÉTECTION RAW() SQL : Vérifier la cohérence avec les transactions SAKA
    if not matching_transaction and abs_delta > 0:
        send_critical_alert(
            title="INTEGRITY BREACH DETECTED",
            payload={
                "violation_type": "saka_wallet_bypass",
                # ...
            }
        )
```

### 6.2 Logs existants

#### CriticalAlertEvent

**Modèle** : `backend/core/models/alerts.py` (lignes 12-252)

**Enregistrement** : Automatique lors de l'envoi d'une alerte (via `send_critical_alert()`)

**Champs** :
- `created_at` : Date et heure
- `event_type` : Type d'événement (ex: "INTEGRITY BREACH DETECTED")
- `severity` : Sévérité (`critical`, `high`, `medium`, `low`)
- `channel` : Canal d'envoi (`email`, `webhook`, `both`)
- `fingerprint` : Empreinte unique (dedupe_key)
- `payload_excerpt` : Extrait du payload (champs principaux)

**Méthodes** :
- `count_for_month(year, month)` : Compte les alertes par mois
- `count_by_event_type_for_month(year, month)` : Compte par type
- `count_by_channel_for_month(year, month)` : Compte par canal

**Tests** : `backend/core/tests/models/test_critical_alert_event.py`

#### SakaTransaction

**Modèle** : `backend/core/models/saka.py` (lignes 366-680)

**Enregistrement** : Automatique lors de chaque opération SAKA (`harvest_saka`, `spend_saka`, `run_saka_compost_cycle`, `redistribute_saka_silo`)

**Champs** :
- `user` : Utilisateur concerné
- `direction` : `EARN` ou `SPEND`
- `amount` : Montant (grains SAKA)
- `reason` : Raison (ex: `CONTENT_READ`, `POLL_VOTE`, `COMPOST`, `REDISTRIBUTION`)
- `created_at` : Date et heure

**Traçabilité** : Historique complet de toutes les opérations SAKA.

### 6.3 Tests critiques

#### Tests de compliance P0 (bloquants)

**Marqueur** : `@pytest.mark.egoejo_compliance`

**Fichiers** :
- `backend/tests/compliance/test_saka_eur_separation.py` : Séparation SAKA/EUR
- `backend/tests/compliance/test_no_saka_accumulation.py` : Anti-accumulation
- `backend/tests/compliance/test_saka_compost_depreciation_effective.py` : Compostage effectif
- `backend/tests/compliance/test_saka_cycle_incompressible.py` : Cycle incompressible
- `backend/tests/compliance/test_saka_no_financial_return.py` : Pas de rendement financier

**Action** : CI échoue si un test de compliance échoue.

**Workflow** : `.github/workflows/egoejo-compliance.yml`

#### Tests de permissions

**Fichiers** :
- `backend/tests/compliance/test_api_endpoints_protection.py` : Protection des endpoints API
- `backend/tests/compliance/test_admin_protection.py` : Protection admin Django

**Action** : CI échoue si un test de permissions échoue.

**Workflow** : `.github/workflows/audit-global.yml` (job `backend-permissions`)

### 6.4 Ce qui est détecté vs ce qui est bloqué

#### Détecté mais non bloqué

1. **raw() SQL** : Détecté via signal `post_save` (incohérence avec `SakaTransaction`), alerte envoyée, mais modification non bloquée
2. **Modification admin Django** : Détecté, alerte envoyée, mais modification possible si `readonly_fields` non configuré

#### Bloqué

1. **update() sur SakaWallet** : `ValidationError` levée, modification impossible
2. **save() direct sans AllowSakaMutation** : `ValidationError` levée, modification impossible
3. **Patterns de conversion SAKA/EUR** : Test échoue, CI bloque la PR
4. **Désactivation compostage** : Test échoue, CI bloque la PR

---

## 7. CONTENU & ÉDITORIAL

### 7.1 Règles réellement testées

#### Promesses interdites

**Script** : `scripts/audit_content.py`

**Blacklist** (mots interdits) :
- **Financiers** : "Investissement", "Rendement", "ROI", "Dividende", "Spéculation", "Crypto"
- **Spirituels** : "Vibration", "5D", "Ascension", "Canalisation"

**Action** : Bloque le déploiement si mot interdit détecté (sauf dans documents de compliance).

**Référence** : `scripts/audit_content.py` (lignes 45-85)

#### SAKA ≠ Argent

**Test frontend** : `frontend/frontend/eslint-rules/__tests__/no-monetary-symbols.test.js`

**Vérifications** :
- Aucun symbole monétaire (€, $, £) associé au SAKA
- Aucun affichage d'équivalent monétaire du SAKA

**Action** : Test ESLint échoue si violation détectée.

**Référence** : `frontend/frontend/eslint-rules/__tests__/no-monetary-symbols.test.js`

### 7.2 Ce qui est opposable aujourd'hui

#### Endpoints publics de vérification

**URLs** :
- `/api/public/egoejo-compliance.json` : Statut de conformité EGOEJO
- `/api/public/egoejo-constitution.json` : Statut constitutionnel
- `/api/compliance/alerts/metrics/` : Métriques d'alertes critiques

**Format** : JSON structuré, accessible sans authentification.

**Référence** :
- `backend/core/api/compliance_views.py` (fonction `egoejo_compliance_status`)
- `backend/core/api/public_compliance.py` (fonction `egoejo_constitution_status`)
- `backend/core/api/compliance_views.py` (fonction `critical_alert_metrics`)

#### Badges SVG dynamiques

**URLs** :
- `/api/public/egoejo-compliance-badge.svg` : Badge de conformité
- `/api/public/egoejo-constitution.svg` : Badge constitutionnel

**Format** : SVG généré dynamiquement selon le statut.

**Référence** : `backend/core/api/compliance_views.py` (fonction `egoejo_compliance_badge`)

---

## 8. INSTITUTIONNEL

### 8.1 Ce qui est déjà présentable

#### Documents institutionnels

**Fichiers** :
- `docs/institutionnel/NOTE_CONCEPTUELLE_ONU.md` : Note pour organisations internationales
- `docs/institutionnel/NOTE_CONCEPTUELLE_FONDATIONS.md` : Note pour fondations
- `docs/institutionnel/ONU_PACK_FR.md` et `ONU_PACK_EN.md` : Pack institutionnel ONU

**Contenu** :
- Modèle 4P (People, Planet, Purpose, Prosperity)
- Séparation SAKA/EUR
- Mécanismes anti-dérive (alertes critiques, métriques publiques)
- Transparence et auditabilité

**Statut** : Documents complets, prêts pour présentation.

#### Constitution technique

**Fichier** : `docs/constitution/CONSTITUTION_TRADUCTION_PHILOSOPHIQUE_TECHNIQUE.md`

**Contenu** :
- Traduction philosophique → technique
- Règles encodées (séparation SAKA/EUR, anti-accumulation, compostage)
- Hash SHA-256 pour versioning

**Statut** : Document actif et enforcé.

#### Métriques publiques

**Endpoint** : `/api/compliance/alerts/metrics/`

**Format** :
```json
{
  "total_alerts": 42,
  "alerts_by_month": [
    {"month": "2025-01", "count": 5},
    ...
  ],
  "last_alert_at": "2025-01-05T10:30:00Z"
}
```

**Statut** : Opérationnel, accessible publiquement.

**Référence** : `docs/observability/CRITICAL_ALERT_METRICS.md`

### 8.2 Ce qui reste à compléter

#### Branch Protection Rules

**État** : Documentation créée, mais **non configurée** dans GitHub UI.

**Action requise** : Configuration manuelle (voir `docs/governance/BRANCH_PROTECTION.md`).

**Impact** : Risque critique de merge de code non conforme.

#### Tests de permissions CMS

**État** : Partiellement corrigés, certains tests attendent encore 401 au lieu d'accepter 401/403.

**Action requise** : Compléter les corrections des tests de permissions CMS.

**Référence** : `docs/reports/AUDIT_COLLEGE_SENIOR_2025_FINAL_V3.md` (Condition de Publication #2)

#### Détection/alerte améliorée pour raw() SQL

**État** : Détection existante via signal `post_save`, mais peut être améliorée.

**Action requise** : Ajouter trigger SQL ou audit de cohérence périodique.

**Référence** : `docs/reports/AUDIT_COLLEGE_SENIOR_2025_FINAL_V3.md` (Condition de Publication #3)

---

## 9. LIMITES CONNUES ET RISQUES ASSUMÉS

### 9.1 Limites techniques

#### Limite 1 : raw() SQL non bloqué

**Description** : Les requêtes SQL directes contournent les protections ORM.

**Détection** : Signal `post_save` détecte les incohérences, alerte envoyée.

**Blocage** : Non bloqué au niveau ORM.

**Risque** : Un développeur malveillant peut modifier `SakaWallet` via `raw() SQL` sans être bloqué.

**Mitigation** : Alerte critique envoyée, audit de cohérence possible.

#### Limite 2 : Admin Django peut modifier (avec alerte)

**Description** : L'admin Django peut techniquement modifier les champs SAKA si `readonly_fields` n'est pas configuré.

**Détection** : Alerte envoyée si modification détectée.

**Blocage** : Non bloqué si `readonly_fields` non configuré.

**Risque** : Un administrateur peut modifier directement les soldes SAKA.

**Mitigation** : Alerte envoyée, audit possible via `CriticalAlertEvent`.

#### Limite 3 : Branch Protection Rules non configurées

**Description** : Les workflows sont bloquants, mais GitHub permet le merge si Branch Protection Rules ne sont pas configurées.

**Impact** : Un développeur peut merger une PR même si les tests de compliance échouent.

**Risque** : Code non conforme peut être mergé en production.

**Mitigation** : Documentation créée, configuration manuelle requise.

### 9.2 Risques assumés

#### Risque 1 : Compostage désactivable

**Description** : `SAKA_COMPOST_ENABLED` peut être mis à `False` via variable d'environnement.

**Validation** : Django lève `ImproperlyConfigured` si `ENABLE_SAKA=True` et `SAKA_COMPOST_ENABLED=False`, mais seulement au démarrage.

**Risque** : Un administrateur peut désactiver le compostage après le démarrage.

**Mitigation** : Tests de compliance vérifient que le compostage est activé en production.

#### Risque 2 : Dépendance à l'action humaine

**Description** : Certaines protections dépendent de l'action humaine (Branch Protection Rules, review de PR).

**Risque** : Erreur humaine peut contourner les protections.

**Mitigation** : Documentation complète, processus clair.

#### Risque 3 : Détection réactive vs préventive

**Description** : Certaines violations sont détectées après coup (signal `post_save`), pas bloquées en amont.

**Risque** : Violation peut se produire avant détection.

**Mitigation** : Alertes critiques envoyées immédiatement, audit possible.

---

## 10. RÉFÉRENCES TECHNIQUES

### 10.1 Fichiers clés

#### Modèles

- `backend/core/models/saka.py` : Modèles SAKA (`SakaWallet`, `SakaTransaction`, `SakaSilo`, etc.)
- `backend/finance/models.py` : Modèles financiers (`UserWallet`, `WalletTransaction`, `EscrowContract`)
- `backend/core/models/alerts.py` : Modèle d'alertes (`CriticalAlertEvent`)

#### Services

- `backend/core/services/saka.py` : Services SAKA (`harvest_saka`, `spend_saka`, `run_saka_compost_cycle`, `redistribute_saka_silo`)
- `backend/finance/ledger_services/ledger.py` : Services financiers (allocation Stripe, calcul frais)
- `backend/core/utils/alerts.py` : Système d'alertes (`send_critical_alert`, `send_webhook_alert`)

#### Tests de compliance

- `backend/tests/compliance/test_saka_eur_separation.py` : Séparation SAKA/EUR
- `backend/tests/compliance/test_no_saka_accumulation.py` : Anti-accumulation
- `backend/tests/compliance/test_saka_compost_depreciation_effective.py` : Compostage effectif
- `backend/tests/compliance/test_saka_cycle_incompressible.py` : Cycle incompressible
- `backend/tests/compliance/test_saka_no_financial_return.py` : Pas de rendement financier

#### Workflows CI/CD

- `.github/workflows/egoejo-pr-bot.yml` : PR Bot EGOEJO
- `.github/workflows/egoejo-compliance.yml` : Tests de compliance
- `.github/workflows/audit-global.yml` : Audit global (tests backend, frontend, permissions)

#### Scripts

- `scripts/audit_content.py` : Audit de contenu (blacklist/whitelist)
- `.github/scripts/egoejo_pr_bot.py` : PR Bot (analyse de conformité)

### 10.2 Endpoints API publics

- `GET /api/public/egoejo-compliance.json` : Statut de conformité
- `GET /api/public/egoejo-constitution.json` : Statut constitutionnel
- `GET /api/compliance/alerts/metrics/` : Métriques d'alertes critiques

### 10.3 Configuration

**Fichier** : `backend/config/settings.py`

**Variables SAKA** :
- `ENABLE_SAKA` : Active/désactive le protocole SAKA
- `SAKA_COMPOST_ENABLED` : Active/désactive le compostage
- `SAKA_COMPOST_INACTIVITY_DAYS` : Durée d'inactivité avant compost
- `SAKA_COMPOST_RATE` : Taux de compostage (0.0 à 1.0)
- `SAKA_SILO_REDIS_ENABLED` : Active/désactive la redistribution
- `SAKA_SILO_REDIS_RATE` : Taux de redistribution (0.0 à 1.0)

**Variables alertes** :
- `ALERT_EMAIL_ENABLED` : Active/désactive les alertes email
- `ALERT_WEBHOOK_ENABLED` : Active/désactive les webhooks
- `ALERT_WEBHOOK_URL` : URL du webhook
- `ALERT_WEBHOOK_TYPE` : Type de webhook (`slack` ou `generic`)

---

## 11. VALIDATION PAR UN AUDITEUR EXTERNE

### 11.1 Comment vérifier chaque affirmation

#### Affirmation : "SAKA et EUR sont strictement séparés"

**Vérification** :
1. Lire `backend/core/models/saka.py` : Vérifier qu'aucun champ EUR dans `SakaWallet`
2. Lire `backend/finance/models.py` : Vérifier qu'aucun champ SAKA dans `UserWallet`
3. Exécuter `pytest backend/tests/compliance/test_saka_eur_separation.py -v` : Vérifier que les tests passent
4. Lire `.github/scripts/egoejo_pr_bot.py` : Vérifier que les patterns de conversion sont détectés

#### Affirmation : "Le compostage est obligatoire en production"

**Vérification** :
1. Lire `backend/config/settings.py` (lignes 552-556) : Vérifier la validation `ImproperlyConfigured`
2. Lire `backend/core/services/saka.py` (fonction `run_saka_compost_cycle`) : Vérifier la logique de compostage
3. Exécuter `pytest backend/tests/compliance/test_saka_compost_depreciation_effective.py -v` : Vérifier que les tests passent

#### Affirmation : "Les alertes critiques sont envoyées automatiquement"

**Vérification** :
1. Lire `backend/core/utils/alerts.py` (fonction `send_critical_alert`) : Vérifier l'implémentation
2. Lire `backend/core/models/saka.py` (signal `post_save`) : Vérifier les appels à `send_critical_alert`
3. Exécuter `pytest backend/core/tests/utils/test_alerts.py -v` : Vérifier que les tests passent
4. Vérifier `backend/config/settings.py` (lignes 472-480) : Vérifier la configuration

### 11.2 Tests à exécuter pour validation complète

```bash
# Tests de compliance (bloquants)
pytest backend/tests/compliance/ -v -m egoejo_compliance

# Tests d'alertes
pytest backend/core/tests/utils/test_alerts.py -v

# Tests de métriques
pytest backend/core/tests/api/test_critical_alert_metrics.py -v

# Tests de séparation SAKA/EUR
pytest backend/tests/compliance/test_saka_eur_separation.py -v

# Tests d'anti-accumulation
pytest backend/tests/compliance/test_no_saka_accumulation.py -v
```

### 11.3 Documents à consulter

- `docs/constitution/CONSTITUTION_TRADUCTION_PHILOSOPHIQUE_TECHNIQUE.md` : Constitution technique
- `docs/reports/AUDIT_COLLEGE_SENIOR_2025_FINAL_V3.md` : Audit final avec risques identifiés
- `docs/observability/CRITICAL_ALERT_METRICS.md` : Documentation métriques
- `docs/security/ALERTING_EMAIL.md` : Documentation alertes email
- `docs/security/ALERTING_SLACK.md` : Documentation alertes Slack
- `docs/governance/BRANCH_PROTECTION.md` : Documentation Branch Protection Rules

---

## 12. CONCLUSION

### 12.1 État actuel

**Forces** :
- ✅ Séparation SAKA/EUR strictement encodée et testée
- ✅ Anti-accumulation implémentée (compostage + redistribution)
- ✅ Système d'alertes critiques opérationnel (email + webhook)
- ✅ Tests de compliance bloquants en CI
- ✅ PR Bot automatisé
- ✅ Métriques publiques et auditables
- ✅ Documentation institutionnelle complète

**Faiblesses** :
- ⚠️ Branch Protection Rules non configurées (risque critique)
- ⚠️ raw() SQL non bloqué au niveau ORM (détecté mais non bloqué)
- ⚠️ Admin Django peut modifier (avec alerte mais non bloqué)
- ⚠️ Tests de permissions CMS partiellement corrigés

### 12.2 Recommandations

**Immédiat** :
1. Configurer Branch Protection Rules dans GitHub UI (voir `docs/governance/BRANCH_PROTECTION.md`)
2. Compléter les tests de permissions CMS

**Court terme (1 mois)** :
1. Améliorer la détection/alerte pour raw() SQL (trigger SQL ou audit périodique)
2. Configurer `readonly_fields` sur `SakaWallet` dans l'admin Django

**Moyen terme (3-6 mois)** :
1. Implémenter un trigger SQL pour bloquer raw() SQL au niveau base de données
2. Ajouter un audit de cohérence périodique (tâche Celery)

---

**Dernière mise à jour** : 2025-01-06  
**Version** : 1.0.0  
**Méthodologie** : Basé exclusivement sur le code, les tests, la CI et les documents existants

