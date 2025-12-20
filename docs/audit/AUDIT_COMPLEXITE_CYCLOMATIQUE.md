# 🔥 AUDIT CRITIQUE - Complexité Cyclomatique

**Date** : 2025-12-19  
**Auditeur** : Senior Code Auditor (Cynique)  
**Mission** : Chasse à la Complexité Cyclomatique - Identifier les 3 fonctions les plus complexes

---

## 💀 TOP 3 DES FONCTIONS LES PLUS COMPLEXES

### 1. 🥇 `pledge_funds()` - `backend/finance/services.py:14-126`

**Complexité Cyclomatique Estimée** : **~15-18**

**Pourquoi c'est illisible** :
- **12+ conditions if/else imbriquées**
- **Logique V1.6 (DONATION) et V2.0 (EQUITY) mélangée**
- **Validations dispersées** (idempotence, KYC, funding_type, share_price, multiples)
- **Calculs financiers mélangés avec validations métier**
- **Pas de séparation des responsabilités**

**Code Actuel** :
```python
@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION', idempotency_key=None):
    # ❌ 12+ if/else imbriqués
    if idempotency_key:
        if WalletTransaction.objects.filter(...).exists():
            raise ValidationError(...)
    
    if pledge_type == 'EQUITY' and not settings.ENABLE_INVESTMENT_FEATURES:
        raise ValidationError(...)
    
    if pledge_type == 'EQUITY' and project.funding_type not in ['EQUITY', 'HYBRID']:
        raise ValidationError(...)
    
    if pledge_type == 'DONATION' and project.funding_type not in ['DONATION', 'HYBRID']:
        raise ValidationError(...)
    
    wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=user)
    amount = Decimal(str(amount)).quantize(cents, rounding=ROUND_HALF_UP)
    
    if wallet.balance < amount:
        raise ValidationError(...)
    
    if pledge_type == 'EQUITY':
        if not hasattr(user, 'is_kyc_verified') or not user.is_kyc_verified:
            raise ValidationError(...)
        
        if project.share_price:
            share_price = Decimal(str(project.share_price)).quantize(...)
            if amount < share_price:
                raise ValidationError(...)
            
            shares = int(amount / share_price)
            if shares == 0:
                raise ValidationError(...)
            amount = (Decimal(str(shares)) * share_price).quantize(...)
    
    wallet.balance = (wallet.balance - amount).quantize(...)
    wallet.save()
    
    tx_type = 'PLEDGE_DONATION' if pledge_type == 'DONATION' else 'PLEDGE_EQUITY'
    tx = WalletTransaction.objects.create(...)
    escrow = EscrowContract.objects.create(...)
    
    if pledge_type == 'EQUITY' and project.share_price:
        # ... logique ShareholderRegister ...
        if not created:
            shareholder.number_of_shares += shares
            shareholder.amount_invested = ...
            shareholder.save()
    
    return escrow
```

**Refactorisation Proposée** :
```python
@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION', idempotency_key=None):
    """
    Fonction principale orchestratrice - DÉLÉGUE aux sous-fonctions
    """
    # 1. Validation idempotence
    _validate_idempotency(idempotency_key)
    
    # 2. Validation métier (séparée par type)
    if pledge_type == 'EQUITY':
        _validate_equity_pledge(user, project, amount)
    else:
        _validate_donation_pledge(project)
    
    # 3. Calculs financiers (normalisation montant)
    normalized_amount = _normalize_amount(amount, pledge_type, project)
    
    # 4. Mouvement financier (commun)
    wallet = _lock_and_get_wallet(user)
    _check_balance_sufficient(wallet, normalized_amount)
    
    # 5. Création transaction et escrow
    tx = _create_pledge_transaction(wallet, project, normalized_amount, pledge_type, idempotency_key)
    escrow = _create_escrow_contract(user, project, normalized_amount, tx)
    
    # 6. Logique spécifique V2.0 (si Equity)
    if pledge_type == 'EQUITY':
        _register_equity_shares(user, project, normalized_amount)
    
    return escrow


def _validate_idempotency(idempotency_key):
    """Validation idempotence (évite double dépense)"""
    if not idempotency_key:
        return
    
    if WalletTransaction.objects.filter(idempotency_key=idempotency_key).exists():
        raise ValidationError("Cette transaction a déjà été traitée.")


def _validate_equity_pledge(user, project, amount):
    """Validation spécifique investissement (V2.0)"""
    if not settings.ENABLE_INVESTMENT_FEATURES:
        raise ValidationError("L'investissement n'est pas encore ouvert sur la plateforme.")
    
    if project.funding_type not in ['EQUITY', 'HYBRID']:
        raise ValidationError("Ce projet n'accepte pas les investissements.")
    
    if not hasattr(user, 'is_kyc_verified') or not user.is_kyc_verified:
        raise ValidationError("Veuillez valider votre identité (KYC) avant d'investir.")


def _validate_donation_pledge(project):
    """Validation spécifique don (V1.6)"""
    if project.funding_type not in ['DONATION', 'HYBRID']:
        raise ValidationError("Ce projet n'accepte pas les dons.")


def _normalize_amount(amount, pledge_type, project):
    """Normalise le montant selon le type de pledge"""
    cents = Decimal('0.01')
    amount = Decimal(str(amount)).quantize(cents, rounding=ROUND_HALF_UP)
    
    if pledge_type == 'EQUITY' and project.share_price:
        return _adjust_amount_to_share_multiple(amount, project.share_price)
    
    return amount


def _adjust_amount_to_share_multiple(amount, share_price):
    """Ajuste le montant au multiple exact du prix d'action"""
    cents = Decimal('0.01')
    share_price = Decimal(str(share_price)).quantize(cents, rounding=ROUND_HALF_UP)
    
    if amount < share_price:
        raise ValidationError(f"Montant minimum: {share_price} € (prix d'une action).")
    
    shares = int(amount / share_price)
    if shares == 0:
        raise ValidationError("Montant insuffisant pour acheter au moins une action.")
    
    return (Decimal(str(shares)) * share_price).quantize(cents, rounding=ROUND_HALF_UP)


def _lock_and_get_wallet(user):
    """Verrouille et récupère le wallet (évite race condition)"""
    wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=user)
    return wallet


def _check_balance_sufficient(wallet, amount):
    """Vérifie que le solde est suffisant"""
    if wallet.balance < amount:
        raise ValidationError("Solde insuffisant.")


def _create_pledge_transaction(wallet, project, amount, pledge_type, idempotency_key):
    """Crée la transaction financière"""
    cents = Decimal('0.01')
    wallet.balance = (wallet.balance - amount).quantize(cents, rounding=ROUND_HALF_UP)
    wallet.save()
    
    tx_type = 'PLEDGE_DONATION' if pledge_type == 'DONATION' else 'PLEDGE_EQUITY'
    
    return WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=tx_type,
        related_project=project,
        description=f"{pledge_type} pour {project.titre}",
        idempotency_key=idempotency_key
    )


def _create_escrow_contract(user, project, amount, tx):
    """Crée le contrat d'escrow"""
    return EscrowContract.objects.create(
        user=user,
        project=project,
        amount=amount,
        status='LOCKED',
        pledge_transaction=tx
    )


def _register_equity_shares(user, project, amount):
    """Enregistre les actions pour un investissement (V2.0)"""
    if not project.share_price:
        return
    
    from investment.models import ShareholderRegister
    
    cents = Decimal('0.01')
    share_price = Decimal(str(project.share_price)).quantize(cents, rounding=ROUND_HALF_UP)
    shares = int(amount / share_price)
    
    shareholder, created = ShareholderRegister.objects.select_for_update().get_or_create(
        project=project,
        investor=user,
        defaults={
            'number_of_shares': shares,
            'amount_invested': amount.quantize(cents, rounding=ROUND_HALF_UP)
        }
    )
    
    if not created:
        shareholder.number_of_shares += shares
        shareholder.amount_invested = (
            Decimal(str(shareholder.amount_invested)) + amount
        ).quantize(cents, rounding=ROUND_HALF_UP)
        shareholder.save()
```

**Bénéfices** :
- ✅ **Complexité réduite** : Chaque fonction < 5 lignes de logique
- ✅ **Testabilité** : Chaque sous-fonction testable indépendamment
- ✅ **Lisibilité** : `pledge_funds()` devient un orchestrateur clair
- ✅ **Maintenabilité** : Modifications isolées (ex: changer logique KYC = 1 fonction)

---

### 2. 🥈 `GlobalAssetsView.get()` - `backend/core/api/impact_views.py:87-215`

**Complexité Cyclomatique Estimée** : **~12-15**

**Pourquoi c'est illisible** :
- **128 lignes dans une seule méthode**
- **6 sections différentes** (Cash, Pockets, Donations, Equity, Social Dividend, SAKA)
- **Logique conditionnelle V2.0 mélangée** (if is_equity_active, try/except ImportError)
- **Calculs financiers répétitifs** (quantize partout)
- **Pas de séparation des responsabilités**

**Code Actuel** :
```python
def get(self, request):
    user = request.user
    
    # 1. Cash Balance (15 lignes avec if/else)
    wallet, _ = UserWallet.objects.get_or_create(user=user)
    if isinstance(wallet.balance, Decimal):
        cash_balance = str(wallet.balance.quantize(Decimal('0.01')))
    else:
        cash_balance = str(Decimal(str(wallet.balance)).quantize(Decimal('0.01')))
    
    # 2. Pockets (10 lignes)
    pockets = WalletPocket.objects.filter(wallet=wallet).values(...)
    pockets_list = [...]
    
    # 3. Donations (20 lignes avec agrégations)
    donations_total = WalletTransaction.objects.filter(...).aggregate(...)
    contributions_agg = Contribution.objects.filter(...).aggregate(...)
    total_donations = ...
    
    # 4. Equity Portfolio (30 lignes avec if/try/except)
    is_equity_active = settings.ENABLE_INVESTMENT_FEATURES
    equity_positions = []
    equity_valuation = Decimal('0')
    
    if is_equity_active:
        try:
            from investment.models import ShareholderRegister
            positions = ShareholderRegister.objects.filter(...)
            for pos in positions:
                equity_positions.append(...)
                equity_valuation += ...
        except ImportError:
            pass
    
    # 5. Social Dividend (5 lignes)
    social_dividend_value = ...
    
    # 6. SAKA (15 lignes avec if/else)
    if getattr(settings, 'ENABLE_SAKA', False):
        saka_data = get_saka_balance(user)
    else:
        saka_data = {...}
    
    return Response({...})  # 20 lignes de dict
```

**Refactorisation Proposée** :
```python
class GlobalAssetsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Orchestrateur principal - délègue aux sous-méthodes"""
        user = request.user
        wallet = self._get_or_create_wallet(user)
        
        return Response({
            'cash_balance': self._get_cash_balance(wallet),
            'pockets': self._get_pockets(wallet),
            'donations': self._get_donations(user, wallet),
            'equity_portfolio': self._get_equity_portfolio(user),
            'social_dividend': self._get_social_dividend(user, wallet),
            'saka': self._get_saka_data(user)
        })
    
    def _get_or_create_wallet(self, user):
        """Récupère ou crée le wallet utilisateur"""
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        return wallet
    
    def _get_cash_balance(self, wallet):
        """Formate le solde cash (Decimal → string)"""
        cents = Decimal('0.01')
        if isinstance(wallet.balance, Decimal):
            return str(wallet.balance.quantize(cents))
        return str(Decimal(str(wallet.balance)).quantize(cents))
    
    def _get_pockets(self, wallet):
        """Récupère et formate les pockets"""
        pockets = WalletPocket.objects.filter(wallet=wallet).values(
            'id', 'name', 'pocket_type', 'current_amount'
        )
        
        cents = Decimal('0.01')
        return [
            {
                'id': p['id'],
                'name': p['name'],
                'type': p['pocket_type'],
                'amount': str(Decimal(str(p['current_amount'])).quantize(cents))
            }
            for p in pockets
        ]
    
    def _get_donations(self, user, wallet):
        """Calcule le total des dons (WalletTransaction + Contribution)"""
        cents = Decimal('0.01')
        
        # Dons via WalletTransaction
        donations_total = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='PLEDGE_DONATION'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        # Contributions via Cagnotte
        contributions_agg = Contribution.objects.filter(
            user=user
        ).aggregate(total=Sum('montant'))
        contributions_total = Decimal(
            str(contributions_agg['total'] or 0)
        ).quantize(cents)
        
        total_donations = (donations_total + contributions_total).quantize(cents)
        
        # Métriques d'impact
        metrics_count = Contribution.objects.filter(
            user=user
        ).values('cagnotte__projet').distinct().count()
        
        return {
            'total_amount': str(total_donations),
            'metrics_count': metrics_count
        }
    
    def _get_equity_portfolio(self, user):
        """Récupère le portefeuille d'actions (V2.0)"""
        is_equity_active = settings.ENABLE_INVESTMENT_FEATURES
        
        if not is_equity_active:
            return {
                'is_active': False,
                'positions': [],
                'valuation': "0.00"
            }
        
        try:
            from investment.models import ShareholderRegister
            from django.db.models import F
            
            positions = ShareholderRegister.objects.filter(
                investor=user
            ).select_related('project').annotate(
                project_title=F('project__titre'),
                project_id=F('project__id')
            ).values(
                'project_id',
                'project_title',
                'number_of_shares',
                'amount_invested'
            )
            
            equity_positions = []
            equity_valuation = Decimal('0')
            cents = Decimal('0.01')
            
            for pos in positions:
                equity_positions.append({
                    'project_id': pos['project_id'],
                    'project_title': pos['project_title'],
                    'shares': pos['number_of_shares'],
                    'valuation': str(Decimal(str(pos['amount_invested'])).quantize(cents))
                })
                equity_valuation += Decimal(str(pos['amount_invested']))
            
            equity_valuation = equity_valuation.quantize(cents)
            
            return {
                'is_active': True,
                'positions': equity_positions,
                'valuation': str(equity_valuation)
            }
        except ImportError:
            # Module investment non disponible
            return {
                'is_active': False,
                'positions': [],
                'valuation': "0.00"
            }
    
    def _get_social_dividend(self, user, wallet):
        """Calcule le dividende social (valeur estimée symbolique)"""
        # Récupérer total_donations (réutiliser logique)
        donations_data = self._get_donations(user, wallet)
        total_donations = Decimal(donations_data['total_amount'])
        
        # 10% symbolique
        social_dividend_value = (total_donations * Decimal('0.1')).quantize(Decimal('0.01'))
        
        return {
            'estimated_value': str(social_dividend_value)
        }
    
    def _get_saka_data(self, user):
        """Récupère les données SAKA (si activé)"""
        if not getattr(settings, 'ENABLE_SAKA', False):
            return {
                'balance': 0,
                'total_harvested': 0,
                'total_planted': 0,
                'total_composted': 0
            }
        
        saka_data = get_saka_balance(user)
        return {
            'balance': saka_data['balance'],
            'total_harvested': saka_data['total_harvested'],
            'total_planted': saka_data['total_planted'],
            'total_composted': saka_data['total_composted']
        }
```

**Bénéfices** :
- ✅ **Méthode principale** : 10 lignes au lieu de 128
- ✅ **Séparation claire** : Chaque section = 1 méthode
- ✅ **Testabilité** : Chaque méthode testable indépendamment
- ✅ **Réutilisabilité** : `_get_donations()` réutilisable ailleurs

---

### 3. 🥉 `vote()` - `backend/core/api/polls.py:119-250+`

**Complexité Cyclomatique Estimée** : **~10-12**

**Pourquoi c'est illisible** :
- **130+ lignes dans une seule méthode**
- **4 méthodes de vote différentes** (quadratic, ranked, approval, simple)
- **Logique SAKA mélangée** avec logique de vote
- **Try/except multiples** pour gérer les erreurs
- **Variables accumulées** (votes_data, rankings_data, saka_spent, etc.)

**Code Actuel** (extrait) :
```python
@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
def vote(self, request, pk=None):
    poll = self.get_object()
    
    # ❌ 130+ lignes avec if/elif/else pour chaque méthode de vote
    if poll.voting_method == 'quadratic':
        votes_data = request.data.get("votes", [])
        max_points = poll.max_points or 100
        total_points = sum(v.get('points', 0) for v in votes_data)
        
        if total_points > max_points:
            return Response({...}, status=400)
        
        intensity = int(request.data.get("intensity", 1))
        intensity = max(1, min(intensity, 5))
        
        saka_cost_per = getattr(settings, "SAKA_VOTE_COST_PER_INTENSITY", 5)
        saka_cost = intensity * saka_cost_per
        
        if getattr(settings, "ENABLE_SAKA", False):
            if spend_saka(...):
                saka_spent = saka_cost
            else:
                # ... fallback ...
        
        # ... création votes ...
    
    elif poll.voting_method == 'ranked':
        rankings_data = request.data.get("rankings", [])
        # ... logique ranked ...
    
    elif poll.voting_method == 'approval':
        option_ids = request.data.get("options", [])
        # ... logique approval ...
    
    else:  # simple
        option_id = request.data.get("option_id")
        # ... logique simple ...
    
    # ... log_action, return Response ...
```

**Refactorisation Proposée** :
```python
@action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
def vote(self, request, pk=None):
    """Orchestrateur principal - délègue selon la méthode de vote"""
    poll = self.get_object()
    
    # Vérification éligibilité (une seule fois)
    if not self._can_user_vote(request.user, poll):
        return Response(
            {"detail": "Vous n'êtes pas autorisé à voter."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Déléguer selon la méthode de vote
    vote_handler = self._get_vote_handler(poll.voting_method)
    
    try:
        result = vote_handler(poll, request)
        return Response(result, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def _can_user_vote(self, user, poll):
        """Vérifie si l'utilisateur peut voter"""
        # Logique de vérification (déjà existante)
        return True  # Simplifié
    
    def _get_vote_handler(self, voting_method):
        """Retourne le handler approprié selon la méthode"""
        handlers = {
            'quadratic': self._handle_quadratic_vote,
            'ranked': self._handle_ranked_vote,
            'approval': self._handle_approval_vote,
            'simple': self._handle_simple_vote,
        }
        return handlers.get(voting_method, self._handle_simple_vote)
    
    def _handle_quadratic_vote(self, poll, request):
        """Gère le vote quadratique avec boost SAKA"""
        votes_data = request.data.get("votes", [])
        max_points = poll.max_points or 100
        
        # Validation points
        total_points = sum(v.get('points', 0) for v in votes_data)
        if total_points > max_points:
            raise ValidationError(
                f"Total de points ({total_points}) dépasse le maximum ({max_points})"
            )
        
        # Calcul intensité et coût SAKA
        intensity = self._calculate_intensity(request.data)
        saka_spent = self._try_spend_saka_for_vote(request.user, intensity)
        
        # Création des votes
        votes_created = []
        for vote_data in votes_data:
            vote = PollVote.objects.create(
                poll=poll,
                user=request.user,
                option_id=vote_data['option_id'],
                points=vote_data.get('points', 0),
                intensity=intensity,
                saka_spent=saka_spent if vote_data == votes_data[0] else 0
            )
            votes_created.append(vote)
        
        return self._build_vote_response(poll, votes_created, saka_spent)
    
    def _handle_ranked_vote(self, poll, request):
        """Gère le vote par classement"""
        rankings_data = request.data.get("rankings", [])
        
        if not rankings_data:
            raise ValidationError("Aucun classement fourni.")
        
        votes_created = []
        for rank, option_id in enumerate(rankings_data, start=1):
            vote = PollVote.objects.create(
                poll=poll,
                user=request.user,
                option_id=option_id,
                rank=rank
            )
            votes_created.append(vote)
        
        return self._build_vote_response(poll, votes_created, 0)
    
    def _handle_approval_vote(self, poll, request):
        """Gère le vote par approbation (plusieurs options)"""
        option_ids = request.data.get("options", [])
        
        if not option_ids:
            raise ValidationError("Aucune option sélectionnée.")
        
        votes_created = []
        for option_id in option_ids:
            vote = PollVote.objects.create(
                poll=poll,
                user=request.user,
                option_id=option_id,
                approved=True
            )
            votes_created.append(vote)
        
        return self._build_vote_response(poll, votes_created, 0)
    
    def _handle_simple_vote(self, poll, request):
        """Gère le vote simple (une seule option)"""
        option_id = request.data.get("option_id")
        
        if not option_id:
            raise ValidationError("Aucune option sélectionnée.")
        
        vote = PollVote.objects.create(
            poll=poll,
            user=request.user,
            option_id=option_id
        )
        
        return self._build_vote_response(poll, [vote], 0)
    
    def _calculate_intensity(self, request_data):
        """Calcule l'intensité du vote (1-5)"""
        intensity = int(request_data.get("intensity", 1))
        return max(1, min(intensity, 5))
    
    def _try_spend_saka_for_vote(self, user, intensity):
        """Tente de dépenser SAKA pour boost vote"""
        if not getattr(settings, "ENABLE_SAKA", False):
            return 0
        
        if not getattr(settings, "SAKA_VOTE_ENABLED", False):
            return 0
        
        saka_cost_per = getattr(settings, "SAKA_VOTE_COST_PER_INTENSITY", 5)
        saka_cost = intensity * saka_cost_per
        
        if spend_saka(user, saka_cost, reason="poll_boost"):
            return saka_cost
        
        return 0
    
    def _build_vote_response(self, poll, votes_created, saka_spent):
        """Construit la réponse standardisée"""
        # Log action
        log_action(
            votes_created[0].user,
            "poll_vote",
            "poll",
            poll.pk
        )
        
        return {
            "poll_id": poll.id,
            "votes_created": len(votes_created),
            "saka_spent": saka_spent,
            "poll": self.get_serializer(poll).data
        }
```

**Bénéfices** :
- ✅ **Méthode principale** : 15 lignes au lieu de 130+
- ✅ **Séparation claire** : Chaque méthode de vote = 1 handler
- ✅ **Testabilité** : Chaque handler testable indépendamment
- ✅ **Extensibilité** : Ajouter nouvelle méthode = 1 handler + 1 ligne dans dict

---

## 📊 RÉSUMÉ DES COMPLEXITÉS

| Fonction | Fichier | Complexité | Lignes | Refactorisation |
|----------|---------|-------------|--------|-----------------|
| `pledge_funds()` | `finance/services.py` | **15-18** | 112 | ✅ 10 sous-fonctions |
| `GlobalAssetsView.get()` | `core/api/impact_views.py` | **12-15** | 128 | ✅ 7 sous-méthodes |
| `vote()` | `core/api/polls.py` | **10-12** | 130+ | ✅ 4 handlers + helpers |

---

## 🎯 RECOMMANDATIONS

### Priorité 1 : Refactoriser `pledge_funds()` (4h)
- **Impact** : Fonction critique (finance)
- **Risque** : Bugs financiers = perte d'argent
- **Bénéfice** : Testabilité + Maintenabilité

### Priorité 2 : Refactoriser `GlobalAssetsView.get()` (3h)
- **Impact** : Performance API (128 lignes = lent)
- **Risque** : Timeout si logique complexe
- **Bénéfice** : Performance + Lisibilité

### Priorité 3 : Refactoriser `vote()` (2h)
- **Impact** : Extensibilité (nouveaux types de vote)
- **Risque** : Bugs de vote = perte de confiance
- **Bénéfice** : Extensibilité + Testabilité

---

**Document généré le : 2025-12-19**  
**Auditeur : Senior Code Auditor (Cynique)**  
**Statut : 🔥 COMPLEXITÉ CYCLOMATIQUE IDENTIFIÉE - REFACTORISATION RECOMMANDÉE**

