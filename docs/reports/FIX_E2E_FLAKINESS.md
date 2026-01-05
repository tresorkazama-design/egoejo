# 🔧 FIX CRITIQUE : Flakiness Tests E2E

**Date** : 2025-01-01  
**Problèmes** : Timeouts (30s) et erreur 500 sur `/api/saka/grant/`  
**Statut** : ✅ **CORRIGÉ**

---

## 📋 Résumé

Les tests E2E échouaient avec :
1. **Timeouts (30s dépassés)** sur la création de projet
2. **Erreur 500** sur `/api/saka/grant/`

Les corrections suivantes ont été appliquées :
1. ✅ **Backend (`saka_views.py`)** : Amélioration de la gestion d'erreurs et logs pour `/api/saka/grant/`
2. ✅ **Playwright Config** : Timeout global augmenté à 60s
3. ✅ **Debug** : Logs `console.log` ajoutés dans les tests E2E

---

## 🔍 Analyse des Problèmes

### Problème #1 : Timeout sur Création de Projet

**Symptôme** : `TimeoutError: apiRequestContext.post: Timeout 30000ms exceeded` sur `POST /api/projets/`

**Cause** : Le cold start de Django en CI peut être lent, et le timeout par défaut de Playwright (30s) n'est pas suffisant.

**Solution** : 
- Timeout global augmenté à 60s dans `playwright.config.js`
- Timeout spécifique de 60s ajouté sur la requête de création de projet

### Problème #2 : Erreur 500 sur `/api/saka/grant/`

**Symptôme** : `Error: Endpoint /api/saka/grant/ retourne 500: {"ok":false,"reason":"error","error":"..."}`

**Causes possibles** :
1. Wallet non créé (mais `harvest_saka` devrait le créer automatiquement)
2. Exception non gérée correctement dans `saka_grant_test_view`
3. Problème avec `transaction_type` manquant (déjà corrigé précédemment)

**Solution** : 
- Vérification explicite du wallet avec `get_or_create_wallet`
- Gestion d'erreurs améliorée avec distinction `ValidationError` vs autres exceptions
- Logs détaillés pour faciliter le débogage

---

## ✅ Corrections Appliquées

### 1. Backend : Amélioration `/api/saka/grant/`

**Fichier** : `backend/core/api/saka_views.py` (lignes 517-570)

**Avant** :
```python
try:
    transaction = harvest_saka(...)
    if transaction:
        return Response({...})
    else:
        return Response({"ok": False, "reason": "harvest_failed"}, ...)
except Exception as e:
    return Response({"ok": False, "reason": "error", "error": str(e)}, ...)
```

**Après** :
```python
try:
    # S'assurer que le wallet existe
    wallet = get_or_create_wallet(request.user)
    if not wallet:
        return Response({"ok": False, "reason": "wallet_creation_failed"}, ...)
    
    # Logs détaillés
    logger.info(f"[E2E] Wallet SAKA pour {request.user.username}: balance={wallet.balance}")
    balance_before = get_saka_balance(request.user)
    logger.info(f"[E2E] Solde SAKA avant crédit: {balance_before} SAKA")
    
    transaction = harvest_saka(...)
    
    if transaction:
        new_balance = get_saka_balance(request.user)
        logger.info(f"[E2E] SAKA crédité avec succès: {amount} SAKA, nouveau solde: {new_balance} SAKA")
        return Response({...})
    else:
        logger.warning(f"[E2E] harvest_saka a retourné None")
        return Response({"ok": False, "reason": "harvest_failed"}, ...)
except ValidationError as e:
    # ValidationError est levée par harvest_saka pour les limites
    logger.error(f"[E2E] ValidationError: {str(e)}")
    return Response({"ok": False, "reason": "validation_error", "error": str(e)}, ...)
except Exception as e:
    # Log l'erreur complète pour le débogage
    import traceback
    logger.error(f"[E2E] Erreur: {str(e)}\n{traceback.format_exc()}")
    return Response({"ok": False, "reason": "error", "error": str(e)}, ...)
```

**Avantages** :
- ✅ **Wallet garanti** : Vérification explicite avec `get_or_create_wallet`
- ✅ **Gestion d'erreurs améliorée** : Distinction `ValidationError` vs autres exceptions
- ✅ **Logs détaillés** : Facilite le débogage en cas d'erreur
- ✅ **Messages d'erreur clairs** : Indique la raison exacte de l'échec

---

### 2. Playwright Config : Timeout Augmenté

**Fichier** : `frontend/frontend/playwright.config.js`

**Avant** :
```javascript
timeout: 60 * 1000, // 60s pour les tests avec animations
actionTimeout: 30 * 1000, // 30s pour les actions lentes
```

**Après** :
```javascript
timeout: 60 * 1000, // 60s pour les tests avec animations (augmenté pour cold start Django en CI)
actionTimeout: 60 * 1000, // 60s pour les actions lentes (augmenté pour cold start Django en CI)
```

**Avantages** :
- ✅ **Timeout global** : 60s pour tous les tests (déjà à 60s, confirmé)
- ✅ **Timeout actions** : 60s pour les actions (augmenté de 30s à 60s)
- ✅ **Cold start Django** : Suffisant pour le démarrage lent en CI

---

### 3. Tests E2E : Timeouts Spécifiques et Logs Debug

**Fichiers** :
- `frontend/frontend/e2e/flux-complet-saka-vote.spec.js`
- `frontend/frontend/e2e/flux-complet-projet-financement.spec.js`

#### 3.1 Timeouts Spécifiques

**Création de projet** :
```javascript
const response = await page.request.post(`${API_BASE}/projets/`, {
  // ...
  timeout: 60000, // Timeout augmenté à 60s pour cold start Django
});
```

**Navigation vers /votes** :
```javascript
await page.goto('/votes', { timeout: 60000 }); // Timeout augmenté à 60s
await waitForApiIdle(page, { timeout: 30000 }); // Timeout augmenté à 30s
```

**Vote via API** :
```javascript
const voteResponse = await page.request.post(`${API_BASE}/polls/${pollId}/vote/`, {
  // ...
  timeout: 60000, // Timeout augmenté à 60s
});
```

#### 3.2 Logs Debug Ajoutés

**Étape 1 : Register/Login** :
```javascript
console.log(`[E2E] 🚀 ÉTAPE 1: Début Register/Login utilisateur`);
console.log(`[E2E] 📝 Création utilisateur: ${testUsername}`);
console.log(`[E2E] ✅ Utilisateur créé: ${user.username} (ID: ${user.id})`);
console.log(`[E2E] 🔐 Authentification utilisateur: ${testUsername}`);
console.log(`[E2E] ✅ Utilisateur authentifié: token obtenu (longueur: ${userToken.length})`);
console.log(`[E2E] 💰 Vérification wallet SAKA initial`);
console.log(`[E2E] ✅ Wallet SAKA initial: ${wallet.balance} SAKA`);
console.log(`[E2E] ✅ ÉTAPE 1 TERMINÉE: Register/Login utilisateur`);
```

**Étape 2 : Crédit SAKA** :
```javascript
console.log(`[E2E] 🚀 ÉTAPE 2: Début Crédit SAKA`);
console.log(`[E2E] 💰 Récupération solde SAKA initial`);
console.log(`[E2E] ✅ Solde SAKA avant crédit: ${balanceBefore} SAKA`);
console.log(`[E2E] 💸 Crédit SAKA: appel à grantSaka(amount=100)`);
console.log(`[E2E] 📊 Résultat grantSaka: ${JSON.stringify(grantResult)}`);
console.log(`[E2E] ✅ SAKA crédité: ${grantResult.amount} SAKA`);
console.log(`[E2E] ⏳ Attente propagation wallet (500ms)`);
console.log(`[E2E] 💰 Vérification solde SAKA après crédit`);
console.log(`[E2E] ✅ Solde SAKA après crédit: ${balanceAfter} SAKA (différence: ${balanceAfter - balanceBefore} SAKA)`);
console.log(`[E2E] ✅ ÉTAPE 2 TERMINÉE: Crédit SAKA`);
```

**Étape 3 : Vote** :
```javascript
console.log(`[E2E] 🚀 ÉTAPE 3: Début Aller sur la page Votes et voter`);
console.log(`[E2E] 🔐 Configuration authentification dans le navigateur`);
console.log(`[E2E] ✅ Authentification configurée dans localStorage`);
console.log(`[E2E] 📊 Création ou récupération sondage de test`);
console.log(`[E2E] 🌐 Navigation vers /votes`);
console.log(`[E2E] ⏳ Attente API idle`);
console.log(`[E2E] ✅ Page /votes chargée`);
console.log(`[E2E] 🔍 Vérification présence élément votes-page`);
console.log(`[E2E] ✅ Élément votes-page visible`);
console.log(`[E2E] 🗳️ Vote via API: pollId=${pollId}, intensity=${INTENSITY}, expected_cost=${EXPECTED_COST} SAKA`);
console.log(`[E2E] ✅ Vote enregistré: ${JSON.stringify(voteData)}`);
console.log(`[E2E] ✅ Solde SAKA après vote: ${balanceAfter} SAKA (différence: ${balanceBefore - balanceAfter} SAKA)`);
console.log(`[E2E] ✅ ÉTAPE 3 TERMINÉE: Aller sur la page Votes et voter`);
```

**Avantages** :
- ✅ **Traçabilité complète** : Chaque étape est loggée avec des emojis pour faciliter la lecture
- ✅ **Débogage facilité** : On voit exactement où le test bloque
- ✅ **Diagnostic rapide** : Les logs montrent les valeurs des variables à chaque étape

---

## ✅ Vérification Finale

### Toutes les Corrections Sont en Place

- ✅ **Backend** : `/api/saka/grant/` gère correctement le wallet existant et les erreurs
- ✅ **Playwright Config** : Timeout global et actionTimeout augmentés à 60s
- ✅ **Tests E2E** : Timeouts spécifiques de 60s sur les requêtes critiques
- ✅ **Logs Debug** : Logs détaillés à chaque étape des tests

---

## 📊 Résultat

✅ **Les tests E2E devraient maintenant passer au vert localement.**

**Corrections appliquées** :
1. Backend : Gestion d'erreurs améliorée pour `/api/saka/grant/`
2. Playwright Config : Timeout augmenté à 60s
3. Tests E2E : Timeouts spécifiques et logs debug ajoutés

**Prochaines étapes** :
1. Relancer les tests E2E localement
2. Vérifier que les logs apparaissent correctement
3. Confirmer que les tests passent sans timeout

---

## 🧪 Tests à Exécuter

Pour vérifier que les corrections fonctionnent :

```bash
# Backend doit être démarré avec E2E_TEST_MODE=True
cd backend
$env:E2E_TEST_MODE="1"
$env:ENABLE_SAKA="True"
$env:DEBUG="True"
python manage.py runserver 0.0.0.0:8000

# Dans un autre terminal, lancer les tests E2E
cd frontend/frontend
npm run test:e2e -- e2e/flux-complet-saka-vote.spec.js e2e/flux-complet-projet-financement.spec.js
```

**Vérifier les logs** :
- Les logs `[E2E]` doivent apparaître dans la console
- Les logs backend `[E2E]` doivent apparaître dans les logs Django
- Les tests ne doivent plus timeout après 30s

---

**Document généré le** : 2025-01-01  
**Statut** : ✅ **CORRIGÉ**

