"""
Endpoints API pour le tableau de bord d'impact utilisateur
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.db.models import Sum, Count, Q, F
from decimal import Decimal

from core.models.impact import ImpactDashboard
from core.models.fundraising import Contribution
from core.models.intents import Intent
from finance.models import UserWallet, WalletPocket, WalletTransaction


class ImpactDashboardView(APIView):
    """
    Endpoint pour obtenir le tableau de bord d'impact d'un utilisateur.
    GET /api/impact/dashboard/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Récupérer ou créer le dashboard
        dashboard, created = ImpactDashboard.objects.get_or_create(user=user)

        # Mettre à jour les métriques si nécessaire (ou si créé)
        # Utiliser Celery pour calculer en arrière-plan si disponible
        try:
            from core.tasks import update_impact_dashboard_metrics
            # Mettre à jour en arrière-plan (non-bloquant)
            update_impact_dashboard_metrics.delay(user.id)
        except Exception:
            # Fallback sur calcul synchrone si Celery non disponible
            if created:
                dashboard.update_metrics()
            else:
                # Mettre à jour si les métriques sont anciennes (plus de 1 heure)
                from django.utils import timezone
                from datetime import timedelta
                if timezone.now() - dashboard.last_updated > timedelta(hours=1):
                    dashboard.update_metrics()

        # Calculer le message d'impact
        impact_message = self._generate_impact_message(dashboard)

        return Response({
            'total_contributions': float(dashboard.total_contributions),
            'projects_supported': dashboard.projects_supported,
            'cagnottes_contributed': dashboard.cagnottes_contributed,
            'intentions_submitted': dashboard.intentions_submitted,
            'impact_message': impact_message,
            'last_updated': dashboard.last_updated.isoformat(),
        })

    def _generate_impact_message(self, dashboard):
        """
        Génère un message personnalisé selon l'impact de l'utilisateur.
        """
        if dashboard.projects_supported > 0:
            return f"Grâce à vous, {dashboard.projects_supported} projet(s) ont avancé !"
        elif dashboard.intentions_submitted > 0:
            return f"Vous avez soumis {dashboard.intentions_submitted} intention(s) !"
        else:
            return "Commencez votre impact en soutenant un projet ou en soumettant une intention."


class GlobalAssetsView(APIView):
    """
    Endpoint pour obtenir le patrimoine global de l'utilisateur.
    GET /api/impact/global-assets/
    
    Retourne :
    - cash_balance : solde disponible du UserWallet
    - pockets : liste des poches (nom, type, montant actuel)
    - donations : total des dons à vie + métriques d'impact
    - equity_portfolio : positions d'investissement (si V2.0 actif)
    - social_dividend : valeur estimée du dividende social
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # 1. Cash Balance (solde principal du wallet)
        wallet, _ = UserWallet.objects.get_or_create(user=user)
        cash_balance = str(wallet.balance.quantize(Decimal('0.01')))
        
        # 2. Pockets (sous-comptes)
        pockets = WalletPocket.objects.filter(wallet=wallet).values(
            'id', 'name', 'pocket_type', 'current_amount'
        )
        pockets_list = [
            {
                'id': p['id'],
                'name': p['name'],
                'type': p['pocket_type'],
                'amount': str(Decimal(str(p['current_amount'])).quantize(Decimal('0.01')))
            }
            for p in pockets
        ]
        
        # 3. Donations (agrégations ORM - pas de boucles Python)
        # Total des dons via WalletTransaction (PLEDGE_DONATION)
        donations_total = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='PLEDGE_DONATION'
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        # Total des contributions via Cagnotte (si applicable)
        # Note: Contribution.montant est un FloatField, on doit le convertir en Decimal
        contributions_agg = Contribution.objects.filter(
            user=user
        ).aggregate(
            total=Sum('montant')
        )
        contributions_total = Decimal(str(contributions_agg['total'] or 0)).quantize(Decimal('0.01'))
        
        # Total combiné (arrondi précis)
        total_donations = (donations_total + contributions_total).quantize(Decimal('0.01'))
        
        # Métriques d'impact (compteur d'unités d'impact)
        # Exemple : nombre de projets soutenus, nombre de cagnottes
        metrics_count = Contribution.objects.filter(
            user=user
        ).values('cagnotte__projet').distinct().count()
        
        # 4. Equity Portfolio (V2.0 - seulement si feature activée)
        is_equity_active = settings.ENABLE_INVESTMENT_FEATURES
        equity_positions = []
        equity_valuation = Decimal('0')
        
        if is_equity_active:
            try:
                from investment.models import ShareholderRegister
                
                # Récupérer les positions avec agrégations ORM
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
                
                for pos in positions:
                    equity_positions.append({
                        'project_id': pos['project_id'],
                        'project_title': pos['project_title'],
                        'shares': pos['number_of_shares'],
                        'valuation': str(Decimal(str(pos['amount_invested'])).quantize(Decimal('0.01')))
                    })
                    equity_valuation += Decimal(str(pos['amount_invested']))
                
                equity_valuation = equity_valuation.quantize(Decimal('0.01'))
            except ImportError:
                # Module investment non disponible
                pass
        
        # 5. Social Dividend (valeur estimée symbolique)
        # Exemple : conversion de l'impact en euros (approximation)
        # Basé sur les métriques d'impact (arbres plantés, heures de formation, etc.)
        # Pour l'instant, calcul simple basé sur les dons
        social_dividend_value = (total_donations * Decimal('0.1')).quantize(Decimal('0.01'))  # 10% symbolique
        
        return Response({
            'cash_balance': cash_balance,
            'pockets': pockets_list,
            'donations': {
                'total_amount': str(total_donations),
                'metrics_count': metrics_count
            },
            'equity_portfolio': {
                'is_active': is_equity_active,
                'positions': equity_positions,
                'valuation': str(equity_valuation) if is_equity_active else "0.00"
            },
            'social_dividend': {
                'estimated_value': str(social_dividend_value)
            }
        })

