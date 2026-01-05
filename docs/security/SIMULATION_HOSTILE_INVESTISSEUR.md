# 🔴 Simulation Hostile : Investisseur Prédateur

**Date** : 2025-01-27  
**Objectif** : Identifier les vecteurs d'attaque et proposer des contre-mesures

---

## 🎯 Objectifs de l'Attaquant

1. **Monétiser le SAKA** : Convertir SAKA en EUR
2. **Supprimer le compost** : Désactiver le compostage obligatoire
3. **Introduire un rendement** : Rendre le SAKA accumulable et rentable

---

## 📊 Tableau Attaque → Défense (Priorisé par Gravité)

| Gravité | Vecteur d'Attaque | Objectif | Contre-Mesure Test | Contre-Mesure CI | Contre-Mesure Gouvernance |
|---------|-------------------|----------|-------------------|------------------|---------------------------|
| **🔴 CRITIQUE** | Modification directe `SakaWallet.balance` via Django Admin | Monétiser SAKA | ✅ Test détecte modification directe | ✅ CI bloque si test échoue | ⚠️ Audit logs + alerte |
| **🔴 CRITIQUE** | Création fonction `convert_saka_to_eur()` | Monétiser SAKA | ✅ Test scan code pour fonctions de conversion | ✅ CI bloque si fonction détectée | ⚠️ Review obligatoire PR |
| **🔴 CRITIQUE** | Désactivation `SAKA_COMPOST_ENABLED=False` | Supprimer compost | ✅ Test vérifie compostage obligatoire | ✅ CI bloque si compost désactivé | ⚠️ Variable protégée (read-only) |
| **🟠 ÉLEVÉE** | Modification `SAKA_COMPOST_RATE=0` | Supprimer compost | ✅ Test vérifie rate > 0 | ✅ CI bloque si rate = 0 | ⚠️ Validation settings |
| **🟠 ÉLEVÉE** | Désactivation redistribution `SAKA_SILO_REDIS_ENABLED=False` | Accumulation Silo | ✅ Test vérifie redistribution obligatoire | ✅ CI bloque si redistribution désactivée | ⚠️ Variable protégée |
| **🟠 ÉLEVÉE** | Création endpoint API `/api/saka/convert/` | Monétiser SAKA | ✅ Test scan routes pour endpoints conversion | ✅ CI bloque si endpoint détecté | ⚠️ Review obligatoire PR |
| **🟡 MOYENNE** | Modification frontend pour afficher SAKA comme monnaie | Monétiser SAKA | ✅ Test vérifie format "grains" | ✅ CI bloque si symbole monétaire détecté | ⚠️ Review frontend |
| **🟡 MOYENNE** | Modification `harvest_saka()` pour permettre accumulation | Accumulation | ✅ Test vérifie limites quotidiennes | ✅ CI bloque si limites supprimées | ⚠️ Review service SAKA |
| **🟡 MOYENNE** | Désactivation tests compliance | Contourner garde-fous | ✅ Test vérifie existence tests | ✅ CI bloque si tests manquants | ⚠️ Protection CI/CD |
| **🟢 FAIBLE** | Modification permissions admin | Accès non autorisé | ✅ Test vérifie permissions | ✅ CI bloque si permissions modifiées | ⚠️ Audit permissions |
| **🟢 FAIBLE** | Modification `SAKA_COMPOST_INACTIVITY_DAYS=999999` | Éviter compost | ✅ Test vérifie days < seuil max | ✅ CI bloque si days > seuil | ⚠️ Validation settings |

---

## 🛡️ Contre-Mesures Techniques Détaillées

### 1. 🔴 CRITIQUE : Modification Directe SakaWallet.balance

**Vecteur** :
```python
# Via Django Admin ou shell Django
wallet = SakaWallet.objects.get(user=user)
wallet.balance = 1000000  # Crédit massif
wallet.save()
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_admin_protection.py`

```python
@pytest.mark.egoejo_compliance
def test_direct_saka_wallet_modification_logged(self, mock_logger):
    """
    Vérifie qu'une modification directe du SakaWallet est loggée.
    """
    wallet.balance = 200
    wallet.save()
    
    mock_logger.warning.assert_called_with(
        f"Modification directe suspecte du SakaWallet..."
    )
```

**Défense CI** :
**Fichier** : `.github/workflows/egoejo-compliance.yml`

```yaml
- name: Run compliance tests
  run: pytest tests/compliance/test_admin_protection.py -v
```

**Défense Gouvernance** :
- ✅ Signal Django `post_save` loggue toute modification directe
- ⚠️ **À AJOUTER** : Alerte automatique (email/Slack) si modification détectée
- ⚠️ **À AJOUTER** : Blocage automatique si modification > seuil (ex: 10000 SAKA)

**Action Technique** :
```python
# backend/core/models/saka.py
@receiver(post_save, sender=SakaWallet)
def log_and_block_saka_wallet_changes(sender, instance, created, **kwargs):
    if not created and instance.pk:
        try:
            original = sender.objects.get(pk=instance.pk)
            if original.balance != instance.balance:
                # Log
                logger.critical(
                    f"Modification directe CRITIQUE du SakaWallet {instance.user.username}: "
                    f"{original.balance} → {instance.balance}"
                )
                
                # Alerte si modification > seuil
                if abs(instance.balance - original.balance) > 10000:
                    send_alert_email(
                        subject="ALERTE CRITIQUE : Modification SAKA suspecte",
                        message=f"Modification de {abs(instance.balance - original.balance)} SAKA"
                    )
        except sender.DoesNotExist:
            pass
```

---

### 2. 🔴 CRITIQUE : Création Fonction Conversion SAKA → EUR

**Vecteur** :
```python
# Nouveau fichier backend/core/services/saka_conversion.py
def convert_saka_to_eur(saka_amount: int, exchange_rate: float = 0.01) -> Decimal:
    """Convertit SAKA en EUR"""
    return Decimal(saka_amount) * Decimal(exchange_rate)
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_no_saka_eur_conversion.py`

```python
@pytest.mark.egoejo_compliance
def test_aucune_fonction_conversion_saka_vers_eur():
    """
    Scan du code pour détecter les fonctions de conversion.
    """
    # Scan patterns interdits
    patterns = load_conversion_patterns()
    
    for file_path in get_all_python_files():
        content = read_file(file_path)
        for pattern in patterns:
            assert not pattern.search(content), (
                f"VIOLATION : Fonction de conversion détectée dans {file_path}"
            )
```

**Défense CI** :
**Fichier** : `.github/workflows/egoejo-compliance.yml`

```yaml
- name: Scan code for conversion functions
  run: pytest tests/compliance/test_no_saka_eur_conversion.py -v
```

**Défense Gouvernance** :
- ✅ Test scan automatique du code
- ⚠️ **À AJOUTER** : Review obligatoire pour nouveaux fichiers `*saka*.py`
- ⚠️ **À AJOUTER** : Blocage PR si fonction de conversion détectée

**Action Technique** :
```python
# backend/tests/compliance/test_no_saka_eur_conversion.py
def test_scan_all_python_files_for_conversion():
    """
    Scan tous les fichiers Python pour détecter les fonctions de conversion.
    """
    forbidden_patterns = [
        r'def\s+convert.*saka.*eur',
        r'def\s+convert.*eur.*saka',
        r'saka.*\*\s*exchange_rate',
        r'exchange_rate.*\*\s*saka',
    ]
    
    for file_path in Path('backend').rglob('*.py'):
        content = file_path.read_text()
        for pattern in forbidden_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                pytest.fail(f"VIOLATION : Pattern de conversion détecté dans {file_path}")
```

---

### 3. 🔴 CRITIQUE : Désactivation Compostage

**Vecteur** :
```bash
# Variables d'environnement
SAKA_COMPOST_ENABLED=False
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_no_saka_accumulation.py`

```python
@pytest.mark.egoejo_compliance
def test_compostage_obligatoire_en_production():
    """
    Vérifie que le compostage est obligatoire en production.
    """
    with override_settings(DEBUG=False):
        assert getattr(settings, 'SAKA_COMPOST_ENABLED', False) == True, (
            "VIOLATION : Le compostage DOIT être activé en production"
        )
```

**Défense CI** :
**Fichier** : `.github/workflows/egoejo-compliance.yml`

```yaml
- name: Verify compost enabled in production
  env:
    DEBUG: "0"
    SAKA_COMPOST_ENABLED: "True"
  run: pytest tests/compliance/test_no_saka_accumulation.py::test_compostage_obligatoire_en_production -v
```

**Défense Gouvernance** :
- ✅ Test vérifie compostage obligatoire
- ⚠️ **À AJOUTER** : Validation settings au démarrage (fail-fast)
- ⚠️ **À AJOUTER** : Variable d'environnement protégée (read-only en production)

**Action Technique** :
```python
# backend/config/settings.py
# Validation au démarrage
if not DEBUG:
    if not os.environ.get('SAKA_COMPOST_ENABLED', 'False').lower() == 'true':
        raise RuntimeError(
            "CRITICAL : SAKA_COMPOST_ENABLED doit être True en production. "
            "Le compostage est obligatoire pour respecter la philosophie EGOEJO."
        )
```

---

### 4. 🟠 ÉLEVÉE : Modification SAKA_COMPOST_RATE=0

**Vecteur** :
```bash
SAKA_COMPOST_RATE=0  # Pas de compostage effectif
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_no_saka_accumulation.py`

```python
@pytest.mark.egoejo_compliance
def test_compost_rate_doit_etre_positif():
    """
    Vérifie que le taux de compostage est > 0.
    """
    rate = getattr(settings, 'SAKA_COMPOST_RATE', 0.1)
    assert rate > 0, (
        f"VIOLATION : SAKA_COMPOST_RATE doit être > 0 (actuel: {rate})"
    )
    assert rate <= 1.0, (
        f"VIOLATION : SAKA_COMPOST_RATE doit être <= 1.0 (actuel: {rate})"
    )
```

**Défense CI** :
```yaml
- name: Verify compost rate > 0
  run: pytest tests/compliance/test_no_saka_accumulation.py::test_compost_rate_doit_etre_positif -v
```

**Défense Gouvernance** :
- ✅ Test vérifie rate > 0
- ⚠️ **À AJOUTER** : Validation settings avec min/max

**Action Technique** :
```python
# backend/config/settings.py
SAKA_COMPOST_RATE = float(os.environ.get('SAKA_COMPOST_RATE', '0.10'))

# Validation
if SAKA_COMPOST_RATE <= 0 or SAKA_COMPOST_RATE > 1.0:
    raise ValueError(
        f"SAKA_COMPOST_RATE doit être entre 0 et 1 (actuel: {SAKA_COMPOST_RATE})"
    )
```

---

### 5. 🟠 ÉLEVÉE : Désactivation Redistribution Silo

**Vecteur** :
```bash
SAKA_SILO_REDIS_ENABLED=False  # Pas de redistribution
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_silo_redistribution.py`

```python
@pytest.mark.egoejo_compliance
def test_redistribution_obligatoire_si_silo_actif():
    """
    Vérifie que la redistribution est obligatoire si le Silo est actif.
    """
    if getattr(settings, 'SAKA_SILO_REDIS_ENABLED', False):
        rate = getattr(settings, 'SAKA_SILO_REDIS_RATE', 0.05)
        assert rate > 0, (
            "VIOLATION : Si SAKA_SILO_REDIS_ENABLED=True, SAKA_SILO_REDIS_RATE doit être > 0"
        )
```

**Défense CI** :
```yaml
- name: Verify silo redistribution
  run: pytest tests/compliance/test_silo_redistribution.py -v
```

**Défense Gouvernance** :
- ✅ Test vérifie redistribution obligatoire
- ⚠️ **À AJOUTER** : Validation cohérence settings

---

### 6. 🟠 ÉLEVÉE : Création Endpoint API Conversion

**Vecteur** :
```python
# backend/core/api/saka_views.py
@api_view(['POST'])
def convert_saka_to_eur(request):
    """Convertit SAKA en EUR"""
    saka_amount = request.data.get('amount')
    exchange_rate = 0.01
    eur_amount = saka_amount * exchange_rate
    return Response({'eur': eur_amount})
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_no_saka_eur_conversion.py`

```python
@pytest.mark.egoejo_compliance
def test_aucun_endpoint_api_conversion():
    """
    Vérifie qu'aucun endpoint API ne permet la conversion SAKA ↔ EUR.
    """
    # Scan des URLs
    from django.urls import get_resolver
    resolver = get_resolver()
    
    forbidden_patterns = ['convert', 'exchange', 'rate']
    
    for pattern in resolver.url_patterns:
        if any(forbidden in str(pattern.pattern).lower() for forbidden in forbidden_patterns):
            pytest.fail(f"VIOLATION : Endpoint suspect détecté : {pattern.pattern}")
```

**Défense CI** :
```yaml
- name: Scan API endpoints
  run: pytest tests/compliance/test_no_saka_eur_conversion.py::test_aucun_endpoint_api_conversion -v
```

**Défense Gouvernance** :
- ✅ Test scan endpoints
- ⚠️ **À AJOUTER** : Review obligatoire pour nouveaux endpoints SAKA

---

### 7. 🟡 MOYENNE : Modification Frontend Affichage Monétaire

**Vecteur** :
```typescript
// frontend/frontend/src/components/SakaBalance.jsx
const display = `${sakaAmount} €`;  // ❌ Affichage monétaire
```

**Défense Test** :
**Fichier** : `frontend/frontend/src/utils/__tests__/saka-protection.test.ts`

```typescript
it('should detect monetary symbols in SAKA display', () => {
  const dangerousDisplay = `Votre solde SAKA: 500€`;
  expect(containsMonetarySymbol(dangerousDisplay)).toBe(true);
});
```

**Défense CI** :
```yaml
- name: Test frontend SAKA protection
  run: npm test src/utils/__tests__/saka-protection.test.ts
```

**Défense Gouvernance** :
- ✅ Test vérifie format "grains"
- ⚠️ **À AJOUTER** : Linter ESLint pour détecter symboles monétaires

---

### 8. 🟡 MOYENNE : Modification harvest_saka() pour Accumulation

**Vecteur** :
```python
# backend/core/services/saka.py
def harvest_saka(user, reason: SakaReason, amount: Optional[int] = None):
    # Suppression des limites quotidiennes
    # wallet.balance += amount  # Sans limite
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_no_saka_accumulation.py`

```python
@pytest.mark.egoejo_compliance
def test_limites_quotidiennes_obligatoires():
    """
    Vérifie que les limites quotidiennes sont appliquées.
    """
    # Tentative de récolte > limite
    for i in range(SAKA_DAILY_LIMITS[SakaReason.CONTENT_READ] + 1):
        harvest_saka(user, SakaReason.CONTENT_READ)
    
    # Vérifier que la limite est respectée
    wallet.refresh_from_db()
    assert wallet.total_harvested <= SAKA_DAILY_LIMITS[SakaReason.CONTENT_READ] * SAKA_BASE_REWARDS[SakaReason.CONTENT_READ]
```

**Défense CI** :
```yaml
- name: Test anti-accumulation
  run: pytest tests/compliance/test_no_saka_accumulation.py -v
```

**Défense Gouvernance** :
- ✅ Test vérifie limites quotidiennes
- ⚠️ **À AJOUTER** : Review obligatoire pour modifications `harvest_saka()`

---

### 9. 🟡 MOYENNE : Désactivation Tests Compliance

**Vecteur** :
```python
# Suppression ou modification des tests
# backend/tests/compliance/test_no_saka_eur_conversion.py
# → Fichier supprimé ou tests commentés
```

**Défense Test** :
**Fichier** : `backend/tests/compliance/test_ci_cd_protection.py`

```python
@pytest.mark.egoejo_compliance
def test_compliance_tests_existent():
    """
    Vérifie que les tests de compliance existent.
    """
    required_tests = [
        'test_no_saka_eur_conversion.py',
        'test_no_saka_accumulation.py',
        'test_silo_redistribution.py',
    ]
    
    for test_file in required_tests:
        test_path = compliance_dir / test_file
        assert test_path.exists(), f"Test de compliance manquant : {test_file}"
```

**Défense CI** :
```yaml
- name: Verify compliance tests exist
  run: pytest tests/compliance/test_ci_cd_protection.py -v
```

**Défense Gouvernance** :
- ✅ Test vérifie existence tests
- ⚠️ **À AJOUTER** : Protection fichiers tests (read-only en production)

---

## 🚨 Actions Techniques Prioritaires

### Priorité 1 : CRITIQUE (À Implémenter Immédiatement)

1. **Alerte Automatique Modifications Directes**
   - Fichier : `backend/core/models/saka.py`
   - Action : Envoyer email/Slack si modification > seuil

2. **Validation Settings au Démarrage**
   - Fichier : `backend/config/settings.py`
   - Action : Fail-fast si compost désactivé en production

3. **Scan Automatique Code Conversion**
   - Fichier : `backend/tests/compliance/test_no_saka_eur_conversion.py`
   - Action : Scan tous les fichiers Python à chaque commit

### Priorité 2 : ÉLEVÉE (À Implémenter Court Terme)

4. **Validation Cohérence Settings**
   - Fichier : `backend/config/settings.py`
   - Action : Valider min/max pour tous les paramètres SAKA

5. **Protection Variables d'Environnement**
   - Fichier : `.github/workflows/egoejo-compliance.yml`
   - Action : Variables protégées (secrets GitHub)

6. **Review Obligatoire PR Critiques**
   - Fichier : `.github/PULL_REQUEST_TEMPLATE.md`
   - Action : Checklist pour modifications SAKA

### Priorité 3 : MOYENNE (À Implémenter Moyen Terme)

7. **Linter ESLint Frontend**
   - Fichier : `.eslintrc.js`
   - Action : Règle pour détecter symboles monétaires

8. **Audit Logs Centralisés**
   - Fichier : `backend/core/models/audit.py`
   - Action : Centraliser tous les logs de modifications SAKA

9. **Monitoring Temps Réel**
   - Fichier : `backend/core/tasks_monitoring.py`
   - Action : Dashboard pour surveiller modifications SAKA

---

## 📋 Checklist de Protection

### Tests de Compliance

- [x] Test modification directe SakaWallet
- [x] Test scan fonctions conversion
- [x] Test compostage obligatoire
- [x] Test redistribution obligatoire
- [x] Test limites quotidiennes
- [x] Test format frontend "grains"

### CI/CD

- [x] Workflow compliance bloquant
- [x] Pre-commit hook
- [ ] Scan automatique code conversion
- [ ] Validation settings au démarrage
- [ ] Protection variables d'environnement

### Gouvernance

- [x] Signal Django post_save
- [ ] Alerte automatique modifications
- [ ] Review obligatoire PR critiques
- [ ] Audit logs centralisés
- [ ] Monitoring temps réel

---

**Fin du Document**

*Dernière mise à jour : 2025-01-27*

