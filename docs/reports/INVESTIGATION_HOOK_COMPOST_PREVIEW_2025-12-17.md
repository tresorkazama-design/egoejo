# 🔍 Investigation : Hook useSakaCompostPreview() Ne S'Exécute Pas

**Date** : 17 Décembre 2025  
**Problème** : L'API `/api/saka/compost-preview/` n'est jamais appelée dans les tests E2E

---

## 📋 Analyse du Code

### 1. Hook `useSakaCompostPreview()` (`frontend/frontend/src/hooks/useSaka.js`)

```javascript
export const useSakaCompostPreview = () => {
  const { user } = useAuth();
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadPreview = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return; // ⚠️ Si user est null, l'API n'est jamais appelée
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchAPI('/api/saka/compost-preview/');
      setPreview(data);
    } catch (err) {
      console.error('Erreur chargement preview compost SAKA:', err);
      setError(err.message || 'Erreur lors du chargement de la preview');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadPreview();
  }, [loadPreview]);

  return {
    data: preview,
    loading,
    error,
    refetch: loadPreview,
  };
};
```

**Logique** :
1. Le hook obtient `user` via `useAuth()`
2. `loadPreview` est un `useCallback` qui dépend de `user`
3. Si `user` est `null`, `loadPreview` retourne sans appeler l'API
4. Un `useEffect` appelle `loadPreview()` quand `loadPreview` change
5. Si `user` change de `null` à un objet, `loadPreview` change et le `useEffect` se réexécute

### 2. Composant Dashboard (`frontend/frontend/src/app/pages/Dashboard.jsx`)

```javascript
export default function Dashboard() {
  const { user } = useAuth();
  // ...
  
  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }
    loadAssets();
  }, [user]);

  // ⚠️ RETOURS PRÉCOCES
  if (!user) {
    return (
      <div>Veuillez vous connecter...</div>
    );
  }

  if (loading) {
    return (
      <Loader message="Chargement..." />
    );
  }

  if (!assets) return null;

  // ✅ Le hook est appelé ICI, après tous les retours précoces
  const { data: silo, loading: isSiloLoading } = useSakaSilo();
  const { data: compost } = useSakaCompostPreview();
  
  // ...
}
```

**Logique** :
1. Le composant vérifie `if (!user)` et retourne tôt si l'utilisateur n'est pas connecté
2. Le composant vérifie `if (loading)` et retourne un loader
3. Le composant vérifie `if (!assets)` et retourne `null`
4. **Le hook `useSakaCompostPreview()` est appelé APRÈS ces vérifications**

### 3. AuthContext (`frontend/frontend/src/contexts/AuthContext.jsx`)

```javascript
useEffect(() => {
  // Au chargement, si on a un token, on essaie de récupérer l'utilisateur
  if (token) {
    fetchUser(token);
  } else {
    setLoading(false);
  }
}, [token]);
```

**Logique** :
1. Le `AuthContext` vérifie `localStorage.getItem('token')` au chargement
2. Si un token existe, il appelle `/api/auth/me/` pour récupérer l'utilisateur
3. Si le token n'existe pas, `user` reste `null`

---

## 🔍 Problème Identifié

### Scénario dans les Tests E2E

1. **Avant la navigation** : `context.addInitScript()` définit le token dans `localStorage`
2. **Navigation vers `/dashboard`** : Le composant Dashboard se monte
3. **AuthContext** : Détecte le token et appelle `/api/auth/me/` (✅ **CETTE API EST APPELÉE**)
4. **Dashboard** : Vérifie `if (!user)` - `user` est encore `null` car l'API n'a pas encore répondu
5. **Dashboard** : Retourne tôt avec "Veuillez vous connecter..."
6. **Le hook `useSakaCompostPreview()` n'est JAMAIS appelé** car le composant a retourné tôt

### Problème de Timing

Le problème est un **problème de timing** :

- Le composant Dashboard se monte **AVANT** que l'API `/api/auth/me/` ait répondu
- Le composant vérifie `if (!user)` et retourne tôt
- Le hook `useSakaCompostPreview()` n'est jamais appelé car il est après les retours précoces
- Même si l'API `/api/auth/me/` répond plus tard et que `user` est défini, le composant a déjà retourné tôt

---

## ✅ Solutions Proposées

### Solution 1 : Attendre que `user` soit chargé AVANT de vérifier (Recommandée)

Modifier le composant Dashboard pour attendre que `user` soit chargé :

```javascript
export default function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  // ...
  
  // Attendre que l'authentification soit terminée
  if (authLoading) {
    return (
      <div className="dashboard-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <Loader message="Vérification de l'authentification..." />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="dashboard-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Patrimoine Vivant</h1>
        <p>Veuillez vous connecter pour voir votre patrimoine.</p>
      </div>
    );
  }

  // Maintenant, user est défini, les hooks peuvent s'exécuter
  const { data: silo, loading: isSiloLoading } = useSakaSilo();
  const { data: compost } = useSakaCompostPreview();
  
  // ...
}
```

**Avantages** :
- Le hook s'exécute toujours si `user` est défini
- Plus robuste et prévisible

**Inconvénients** :
- Nécessite de modifier le composant Dashboard

### Solution 2 : Déplacer les hooks AVANT les retours précoces

Déplacer les hooks avant les vérifications :

```javascript
export default function Dashboard() {
  const { user } = useAuth();
  
  // ✅ Déplacer les hooks AVANT les retours précoces
  const { data: silo, loading: isSiloLoading } = useSakaSilo();
  const { data: compost } = useSakaCompostPreview();
  
  // Maintenant, les vérifications
  if (!user) {
    return (
      <div>Veuillez vous connecter...</div>
    );
  }
  
  // ...
}
```

**Avantages** :
- Les hooks s'exécutent toujours, même si le composant retourne tôt
- Le hook peut détecter quand `user` change de `null` à un objet

**Inconvénients** :
- Les hooks s'exécutent même si `user` est `null` (mais ils gèrent déjà ce cas)

### Solution 3 : Utiliser `useEffect` dans le hook pour réagir aux changements de `user`

Le hook utilise déjà `useEffect`, mais on peut améliorer la logique :

```javascript
export const useSakaCompostPreview = () => {
  const { user } = useAuth();
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      setPreview(null);
      return;
    }

    // Appeler l'API directement dans useEffect
    const loadPreview = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchAPI('/api/saka/compost-preview/');
        setPreview(data);
      } catch (err) {
        console.error('Erreur chargement preview compost SAKA:', err);
        setError(err.message || 'Erreur lors du chargement de la preview');
      } finally {
        setLoading(false);
      }
    };

    loadPreview();
  }, [user]); // Dépendre directement de user, pas de loadPreview

  return {
    data: preview,
    loading,
    error,
    refetch: () => {
      // Implémenter refetch si nécessaire
    },
  };
};
```

**Avantages** :
- Plus simple et direct
- Réagit immédiatement aux changements de `user`

**Inconvénients** :
- Nécessite de modifier le hook

---

## 🎯 Recommandation

**Solution 1 + Solution 3** : Combiner les deux solutions pour une approche robuste :

1. **Modifier le Dashboard** pour attendre que `authLoading` soit `false` avant de vérifier `user`
2. **Simplifier le hook** pour dépendre directement de `user` dans `useEffect`

Cela garantit que :
- Le composant attend que l'authentification soit terminée
- Le hook s'exécute toujours si `user` est défini
- Le hook réagit immédiatement aux changements de `user`

---

## 📝 Prochaines Étapes

1. **Implémenter la Solution 1** : Modifier le Dashboard pour attendre `authLoading`
2. **Implémenter la Solution 3** : Simplifier le hook pour dépendre directement de `user`
3. **Réactiver les tests E2E** : Retirer `test.skip()` une fois les corrections implémentées
4. **Vérifier** : Exécuter `npx playwright test e2e/saka-cycle-visibility.spec.js` pour confirmer que tous les tests passent

---

**Date de création** : 17 Décembre 2025  
**Statut** : ⏳ En attente d'implémentation

