# 🌱 Intégration Animation Compostage SAKA

**Document** : Guide d'intégration du composant de gamification visuelle du compostage  
**Date** : 2025-12-19  
**Version** : 1.0

---

## 🎯 Objectif

Transformer la perception négative du compostage ("perte", "expiration") en une expérience positive de "régénération" et "contribution" à l'écosystème collectif.

---

## 📦 Composants Créés

### 1. `CompostAnimation.tsx`

**Fichier** : `frontend/frontend/src/components/saka/CompostAnimation.tsx`

**Fonctionnalités** :
- Animation GSAP de particules (grains SAKA) qui tombent du wallet vers le Silo
- Trajectoire organique (arc) pour un effet naturel
- Effet de "pulsation" verte sur le Silo quand il reçoit les grains
- Optimisé pour mobile et low power mode

**Props** :
```typescript
interface CompostAnimationProps {
  amount: number;                    // Montant composté
  fromPosition?: { x: number; y: number };  // Position wallet
  toPosition?: { x: number; y: number };    // Position Silo
  onComplete?: () => void;           // Callback fin animation
  disabled?: boolean;                 // Désactiver animation
}
```

---

### 2. `CompostNotification.tsx`

**Fichier** : `frontend/frontend/src/components/saka/CompostNotification.tsx`

**Fonctionnalités** :
- Notification avec wording positif ("Régénération Collective")
- Intègre `CompostAnimation` automatiquement
- Version simplifiée pour mobile (`CompostNotificationSimple`)
- Auto-fermeture après 5 secondes

**Props** :
```typescript
interface CompostNotificationProps {
  amount: number;                    // Montant composté
  remainingBalance: number;           // Solde restant
  siloBalance: number;                // Solde Silo après compostage
  onClose?: () => void;              // Callback fermeture
  showAnimation?: boolean;           // Afficher animation
}
```

---

## 🔄 Changements de Wording

### Avant (Négatif)

- ❌ "-50 SAKA (Expiré)"
- ❌ "Perte de 50 grains"
- ❌ "Vos grains ont expiré"
- ❌ "Compostage : -50 SAKA"

### Après (Positif)

- ✅ "🌱 +50 grains retournés au Silo Commun"
- ✅ "Régénération Collective"
- ✅ "Contribution à l'écosystème collectif"
- ✅ "Vos grains inactifs contribuent maintenant à nourrir l'écosystème"

---

## 📍 Intégration dans SakaSeasons

### Option 1 : Notification lors du compostage

**Fichier** : `frontend/frontend/src/app/pages/SakaSeasons.tsx`

```tsx
import { useState, useEffect } from 'react';
import CompostNotification from '@/components/saka/CompostNotification';
import { useSakaCycles, useSakaSilo } from '@/hooks/useSakaCycles';

export default function SakaSeasonsPage() {
  const { cycles, loading: loadingCycles } = useSakaCycles();
  const { silo, loading: loadingSilo } = useSakaSilo();
  const [compostNotification, setCompostNotification] = useState<{
    amount: number;
    remainingBalance: number;
    siloBalance: number;
  } | null>(null);

  // Détecter un nouveau compostage (comparer avec état précédent)
  useEffect(() => {
    // Logique de détection du compostage
    // Comparer cycles précédents avec cycles actuels
    // Si nouveau compost détecté, afficher notification
  }, [cycles]);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Notification de compostage */}
      {compostNotification && (
        <CompostNotification
          amount={compostNotification.amount}
          remainingBalance={compostNotification.remainingBalance}
          siloBalance={compostNotification.siloBalance}
          onClose={() => setCompostNotification(null)}
        />
      )}

      {/* Contenu existant */}
      {/* ... */}
    </div>
  );
}
```

---

### Option 2 : Animation dans la section "Composté"

**Fichier** : `frontend/frontend/src/app/pages/SakaSeasons.tsx`

```tsx
import CompostAnimation, { useCompostPositions } from '@/components/saka/CompostAnimation';

export default function SakaSeasonsPage() {
  const walletRef = useRef<HTMLDivElement>(null);
  const siloRef = useRef<HTMLDivElement>(null);
  const positions = useCompostPositions(walletRef, siloRef);
  const [showAnimation, setShowAnimation] = useState(false);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      {/* Section Silo avec animation */}
      <section className="rounded-2xl border p-4 md:p-6 bg-muted/40">
        <div ref={siloRef} className="relative">
          <h2 className="text-xl font-semibold mb-2">Silo commun</h2>
          {silo && (
            <div className="flex items-baseline gap-4">
              <p className="text-3xl font-bold">
                {silo.total_balance.toLocaleString("fr-FR")} <span className="text-lg">grains</span>
              </p>
            </div>
          )}
        </div>
      </section>

      {/* Cycles avec animation */}
      {cycles.map((cycle) => (
        <article key={cycle.id} className="...">
          <div ref={walletRef} className="...">
            {/* Contenu cycle */}
          </div>
          
          {showAnimation && positions && cycle.stats?.saka_composted > 0 && (
            <CompostAnimation
              amount={cycle.stats.saka_composted}
              fromPosition={positions.from}
              toPosition={positions.to}
              onComplete={() => setShowAnimation(false)}
            />
          )}
        </article>
      ))}
    </div>
  );
}
```

---

## 📍 Intégration dans Dashboard

### Option 1 : Notification lors du compostage

**Fichier** : `frontend/frontend/src/app/pages/Dashboard.jsx`

```jsx
import { useState, useEffect } from 'react';
import CompostNotification from '../../components/saka/CompostNotification';
import { useSakaCompostPreview } from '../../hooks/useSaka';

export default function Dashboard() {
  const { data: compost } = useSakaCompostPreview();
  const [showCompostNotification, setShowCompostNotification] = useState(false);
  const [compostData, setCompostData] = useState(null);

  // Détecter quand le compostage vient de se produire
  useEffect(() => {
    // Comparer avec état précédent
    // Si nouveau compost détecté, afficher notification
    if (compost?.just_composted) {
      setCompostData({
        amount: compost.amount,
        remainingBalance: compost.remaining_balance,
        siloBalance: compost.silo_balance,
      });
      setShowCompostNotification(true);
    }
  }, [compost]);

  return (
    <div className="dashboard-page">
      {/* Notification de compostage */}
      {showCompostNotification && compostData && (
        <CompostNotification
          amount={compostData.amount}
          remainingBalance={compostData.remainingBalance}
          siloBalance={compostData.siloBalance}
          onClose={() => {
            setShowCompostNotification(false);
            setCompostData(null);
          }}
        />
      )}

      {/* Contenu existant */}
      {/* ... */}
    </div>
  );
}
```

---

### Option 2 : Remplacer le message d'avertissement

**Fichier** : `frontend/frontend/src/app/pages/Dashboard.jsx`

**Avant** :
```jsx
{compost?.enabled && compost?.eligible && compost.amount && compost.amount >= 20 && (
  <div style={{...}}>
    <h3>🌾 Vos grains vont bientôt retourner à la terre</h3>
    <p>
      Si vous restez inactif, environ <strong>{compost.amount} SAKA</strong> seront compostés...
    </p>
  </div>
)}
```

**Après** :
```jsx
{compost?.enabled && compost?.eligible && compost.amount && compost.amount >= 20 && (
  <div style={{
    padding: '1rem 1.5rem',
    backgroundColor: '#f0fdf4',
    border: '2px solid #84cc16',
    borderRadius: 'var(--radius)',
    marginBottom: '2rem',
  }}>
    <h3 style={{ color: '#166534' }}>
      🌱 Contribution à l'écosystème
    </h3>
    <p style={{ color: '#15803d' }}>
      Si vous restez inactif, environ <strong>{compost.amount} grains</strong> contribueront au Silo Commun lors du prochain cycle.
      {' '}Ils seront redistribués aux membres actifs de la communauté.
    </p>
  </div>
)}
```

---

## 🎨 Personnalisation

### Couleurs

Les couleurs suivent la palette "Vivant" :
- **Vert SAKA** : `#84cc16` (Silo, contribution)
- **Vert Nature** : `#166534` (Textes)
- **Vert Clair** : `#f0fdf4` (Fond)

### Animations

- **Durée** : ~2 secondes par défaut
- **Particules** : 1 particule = 10 grains (max 50 particules)
- **Trajectoire** : Arc organique (bezier curve)

### Responsive

- **Desktop** : Animation complète avec particules
- **Mobile** : Version simplifiée (`CompostNotificationSimple`)
- **Low Power** : Animation désactivée automatiquement

---

## ✅ Checklist d'Intégration

- [ ] Importer `CompostAnimation` et `CompostNotification`
- [ ] Remplacer wording négatif par wording positif
- [ ] Intégrer notification dans SakaSeasons ou Dashboard
- [ ] Tester l'animation (desktop et mobile)
- [ ] Vérifier low power mode (animation désactivée)
- [ ] Tester avec différents montants de compostage

---

## 📚 Références

- **Composant Animation** : `frontend/frontend/src/components/saka/CompostAnimation.tsx`
- **Composant Notification** : `frontend/frontend/src/components/saka/CompostNotification.tsx`
- **Styles** : `frontend/frontend/src/components/saka/CompostAnimation.css`
- **Page SakaSeasons** : `frontend/frontend/src/app/pages/SakaSeasons.tsx`
- **Page Dashboard** : `frontend/frontend/src/app/pages/Dashboard.jsx`

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : Guide d'intégration**

