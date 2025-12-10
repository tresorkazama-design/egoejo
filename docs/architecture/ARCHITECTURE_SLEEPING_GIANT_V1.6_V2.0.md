# 🏗️ Architecture "The Sleeping Giant" - EGOEJO V1.6 + V2.0

**Version**: 2.0 (Hybride)  
**Date**: 2025-01-27  
**Statut**: V1.6 Actif ✅ | V2.0 Dormant 💤

---

## 🎯 Concept

**"The Sleeping Giant"** : Une architecture hybride où le code V2.0 (Investissement, KYC, Actions) est **déjà présent** mais **désactivé** par un simple feature flag. Le jour où vous obtenez l'agrément AMF, vous changez une variable d'environnement et la plateforme se transforme sans réécrire une ligne de code.

---

## 🎛️ Le Kill Switch

### Variable d'Environnement

```bash
# Dans Railway ou .env
ENABLE_INVESTMENT_FEATURES=False  # V1.6 (Dons uniquement)
ENABLE_INVESTMENT_FEATURES=True   # V2.0 (Investissement activé)
```

### Configuration (settings.py)

```python
# ==============================================
# EGOEJO FEATURE FLAGS (Le Cerveau Hybride)
# ==============================================
ENABLE_INVESTMENT_FEATURES = os.environ.get('ENABLE_INVESTMENT_FEATURES', 'False').lower() == 'true'

# Modèle Économique (5% + 3%)
EGOEJO_COMMISSION_RATE = float(os.environ.get('EGOEJO_COMMISSION_RATE', '0.05'))  # 5%
STRIPE_FEE_ESTIMATE = float(os.environ.get('STRIPE_FEE_ESTIMATE', '0.03'))  # 3%

# Sécurité Fondateur
FOUNDER_GROUP_NAME = os.environ.get('FOUNDER_GROUP_NAME', 'Founders')
```

---

## 🏗️ Structure de la Base de Données

### Modèle Projet (Hybride)

```python
class Projet(models.Model):
    # ... champs existants ...
    
    # Type de financement
    funding_type = models.CharField(
        max_length=10,
        choices=FundingType.choices,
        default=FundingType.DONATION
    )
    
    # Objectifs financiers distincts
    donation_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    investment_goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Dormant
    
    # Configuration V2.0 (Dormant)
    share_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_shares = models.IntegerField(null=True, blank=True)
    valuation_pre_money = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    @property
    def is_investment_open(self):
        """Vérifie si l'investissement est possible ET activé globalement"""
        return (
            settings.ENABLE_INVESTMENT_FEATURES and
            self.funding_type in ['EQUITY', 'HYBRID'] and
            self.investment_goal > 0
        )
```

### Application Finance (Wallet Universel)

**Fichier**: `backend/finance/models.py`

- **UserWallet** : Portefeuille utilisateur
- **WalletTransaction** : Transactions (DEPOSIT, PLEDGE_DONATION, PLEDGE_EQUITY, REFUND, RELEASE, COMMISSION)
- **EscrowContract** : Contrats d'escrow (cantonnement)

### Application Investment (V2.0 Dormant)

**Fichier**: `backend/investment/models.py`

- **ShareholderRegister** : Registre des actionnaires (ne se remplit que si `ENABLE_INVESTMENT_FEATURES=True`)

---

## 🧠 Le Cerveau Financier

### Service Unifié (finance/services.py)

```python
@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION'):
    """
    Fonction unique pour Don (V1.6) ET Investissement (V2.0).
    """
    # 1. Sécurité V2.0 : Bloquer si feature désactivée
    if pledge_type == 'EQUITY' and not settings.ENABLE_INVESTMENT_FEATURES:
        raise ValidationError("L'investissement n'est pas encore ouvert.")
    
    # 2. Logique V2.0 : Vérification KYC (Si Equity)
    if pledge_type == 'EQUITY':
        if not user.is_kyc_verified:
            raise ValidationError("Veuillez valider votre identité (KYC) avant d'investir.")
    
    # 3. Mouvement Financier (Commun V1.6/V2.0)
    wallet.balance -= amount
    tx = WalletTransaction.objects.create(...)
    escrow = EscrowContract.objects.create(...)
    
    # 4. Si Equity, créer/enregistrer les actions (V2.0)
    if pledge_type == 'EQUITY' and project.share_price:
        ShareholderRegister.objects.get_or_create(...)
    
    return escrow
```

---

## 🛡️ Protection Fondateur & Gouvernance

### Vote Pondéré (core/models/polls.py)

```python
class Poll(models.Model):
    is_shareholder_vote = models.BooleanField(
        default=False,
        help_text="Vote réservé aux actionnaires (V2.0)"
    )
    
    def get_vote_weight(self, user):
        """
        V1.6 : 1 personne = 1 voix
        V2.0 : 1 action = 1 voix (x100 pour Fondateurs)
        """
        if self.is_shareholder_vote:
            try:
                from investment.models import ShareholderRegister
                shares = ShareholderRegister.objects.get(
                    project=self.project, investor=user
                ).number_of_shares
                
                # PROTECTION FONDATEUR (Golden Share)
                if user.groups.filter(name=settings.FOUNDER_GROUP_NAME).exists():
                    return shares * 100
                return shares
            except:
                return 0
        
        # Mode V1.6 Standard
        return 1
```

---

## 🎨 Frontend : Interface Adaptative

### Contexte Config (frontend/src/contexts/ConfigContext.tsx)

```typescript
// API qui renvoie { investment_enabled: boolean }
const { data: config } = useFetch('/api/config/features/');

export const ProjectPage = ({ project }) => {
  return (
    <div>
      <h1>{project.title}</h1>
      
      {/* Barre de progression Dons */}
      <ProgressBar value={project.donation_current} max={project.donation_goal} />
      
      {/* SECTION V2.0 (DORMANT) */}
      {config.investment_enabled && project.funding_type !== 'DONATION' && (
        <div className="border border-gold p-4 mt-4">
          <h2>Devenez Actionnaire</h2>
          <p>Prix de l'action : {project.share_price} €</p>
          <button onClick={openInvestModal}>Investir (Equity)</button>
        </div>
      )}
      
      {/* Bouton Standard V1.6 */}
      <button onClick={openDonateModal}>Faire un Don</button>
    </div>
  );
};
```

---

## 🚀 Guide de Déploiement

### Backend

1. **Mettre `ENABLE_INVESTMENT_FEATURES = False`** dans `settings.py` ou variable d'environnement Railway.
2. **Lancer toutes les migrations** :
   ```bash
   python manage.py migrate
   ```
   La base de données aura les tables "Actions" et "Investisseurs" vides. C'est parfait.

### Frontend

Déployez le code qui contient les composants "Investir", mais cachés par la condition `config.investment_enabled`.

### Lancement V1.6

- Les utilisateurs voient une plateforme de dons ultra-robuste avec Wallet.
- Vous collectez vos 5% + 3% via le système Escrow unifié.

### Activation V2.0 (Le jour où vous avez l'agrément AMF)

1. **Changez `ENABLE_INVESTMENT_FEATURES = True`** (Variable d'env Railway).
2. **C'est tout.** Les boutons "Investir" apparaissent, le KYC devient obligatoire pour l'equity, et vous êtes une Fintech.

---

## 📋 Checklist Migration V1.6 → V2.0

- [ ] Obtenir agrément AMF
- [ ] Configurer KYC (service tiers : Stripe Identity, Onfido, etc.)
- [ ] Configurer signature électronique (YouSign, DocuSign)
- [ ] Mettre à jour `ENABLE_INVESTMENT_FEATURES=True` dans Railway
- [ ] Tester investissement sur projet de test
- [ ] Valider génération automatique des actions
- [ ] Valider vote pondéré actionnaires
- [ ] Communiquer le lancement V2.0

---

## 🔒 Sécurité

- **KYC obligatoire** pour investissement (V2.0)
- **Signature électronique** des bulletins de souscription
- **Protection Fondateur** : Vote pondéré x100 pour groupe "Founders"
- **Escrow** : Fonds verrouillés jusqu'à libération admin
- **Commission** : Calcul automatique (5% EGOEJO + 3% Stripe)

---

**C'est la version la plus complète, sécurisée et évolutive possible. Vous avez le moteur d'une banque dans la carrosserie d'une asso.**

