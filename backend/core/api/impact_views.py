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
import logging

from core.models.impact import ImpactDashboard
from core.models.fundraising import Contribution
from core.models.intents import Intent
from finance.models import UserWallet, WalletPocket, WalletTransaction
from finance.services import _to_decimal
from core.services.saka import get_saka_balance

logger = logging.getLogger(__name__)


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
        except ImportError:
            # Module core.tasks non disponible - OK, on continue avec calcul synchrone
            logger.warning(
                f"Module core.tasks non disponible - calcul synchrone pour user {user.id}"
            )
            if created:
                dashboard.update_metrics()
            else:
                # Mettre à jour si les métriques sont anciennes (plus de 1 heure)
                from django.utils import timezone
                from datetime import timedelta
                if timezone.now() - dashboard.last_updated > timedelta(hours=1):
                    dashboard.update_metrics()
        except Exception as e:
            # Erreur inattendue - ON LOG CRITIQUE ET ON CONTINUE
            logger.critical(
                f"Erreur critique lors du lancement de la tâche de mise à jour dashboard pour user {user.id}: {e}",
                exc_info=True
            )
            # Fallback sur calcul synchrone pour ne pas bloquer l'utilisateur
            if created:
                dashboard.update_metrics()
            else:
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

    def _get_or_create_wallet(self, user):
        """
        Récupère ou crée le wallet utilisateur.
        
        Args:
            user: Utilisateur
        
        Returns:
            UserWallet
        """
        return UserWallet.objects.get_or_create(user=user)[0]

    def _get_cash_balance(self, wallet):
        """
        Récupère le solde principal du wallet (formaté en string).
        
        OPTIMISATION MÉMOIRE : Utilise le helper _to_decimal centralisé.
        
        Args:
            wallet: UserWallet
        
        Returns:
            str: Solde formaté avec 2 décimales
        """
        return str(_to_decimal(wallet.balance))

    def _get_pockets(self, wallet):
        """
        Récupère la liste des poches (sous-comptes) du wallet.
        
        Args:
            wallet: UserWallet
        
        Returns:
            list: Liste des poches avec id, name, type, amount
        """
        pockets = WalletPocket.objects.filter(wallet=wallet).values(
            'id', 'name', 'pocket_type', 'current_amount'
        )
        return [
            {
                'id': p['id'],
                'name': p['name'],
                'type': p['pocket_type'],
                'amount': str(_to_decimal(p['current_amount']))
            }
            for p in pockets
        ]

    def _get_donations(self, user, wallet):
        """
        Calcule le total des dons et les métriques d'impact.
        
        Args:
            user: Utilisateur
            wallet: UserWallet
        
        Returns:
            dict: {'total_amount': Decimal, 'metrics_count': int}
        """
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
        contributions_total = _to_decimal(contributions_agg['total'] or 0)
        
        # Total combiné (arrondi précis)
        total_donations = (donations_total + contributions_total).quantize(Decimal('0.01'))
        
        # OPTIMISATION SQL : Utiliser aggregate avec Count distinct au lieu de values().distinct().count()
        # Évite le scan complet de table et génère un COUNT(DISTINCT ...) en SQL
        metrics_count = Contribution.objects.filter(
            user=user
        ).aggregate(
            count=Count('cagnotte__projet', distinct=True)
        )['count'] or 0
        
        return {
            'total_amount': total_donations,
            'metrics_count': metrics_count
        }

    def _get_equity_portfolio(self, user):
        """
        Récupère le portefeuille d'actions (V2.0 - seulement si feature activée).
        
        Args:
            user: Utilisateur
        
        Returns:
            dict: {'is_active': bool, 'positions': list, 'valuation': Decimal}
        """
        is_equity_active = settings.ENABLE_INVESTMENT_FEATURES
        equity_positions = []
        equity_valuation = Decimal('0')
        
        if is_equity_active:
            try:
                from investment.models import ShareholderRegister
                
                # OPTIMISATION SQL : Récupérer les positions avec agrégations ORM et prefetch_related
                # pour éviter N+1 queries si on accède aux relations du projet plus tard
                positions = ShareholderRegister.objects.filter(
                    investor=user
                ).select_related(
                    'project',
                    'project__community'  # Précharger la communauté si nécessaire
                ).annotate(
                    project_title=F('project__titre'),
                    project_id=F('project__id')
                ).values(
                    'project_id',
                    'project_title',
                    'number_of_shares',
                    'amount_invested'
                )
                
                for pos in positions:
                    amount_invested = _to_decimal(pos['amount_invested'])
                    equity_positions.append({
                        'project_id': pos['project_id'],
                        'project_title': pos['project_title'],
                        'shares': pos['number_of_shares'],
                        'valuation': str(amount_invested)
                    })
                    equity_valuation += amount_invested
                
                equity_valuation = equity_valuation.quantize(Decimal('0.01'))
            except ImportError:
                # Module investment non disponible
                pass
        
        return {
            'is_active': is_equity_active,
            'positions': equity_positions,
            'valuation': equity_valuation
        }

    def _get_social_dividend(self, total_donations):
        """
        Calcule la valeur estimée du dividende social (symbolique).
        
        Args:
            total_donations: Total des dons (Decimal)
        
        Returns:
            Decimal: Valeur estimée du dividende social
        """
        # Conversion de l'impact en euros (approximation)
        # Basé sur les métriques d'impact (arbres plantés, heures de formation, etc.)
        # Pour l'instant, calcul simple basé sur les dons (10% symbolique)
        return (total_donations * Decimal('0.1')).quantize(Decimal('0.01'))

    def _get_saka_data(self, user):
        """
        Récupère les données SAKA (Protocole SAKA - Monnaie interne d'engagement).
        
        Args:
            user: Utilisateur
        
        Returns:
            dict: Données SAKA (balance, total_harvested, total_planted, total_composted)
        """
        if getattr(settings, 'ENABLE_SAKA', False):
            return get_saka_balance(user)
        else:
            # Retourner des zéros si SAKA est désactivé
            return {
                'balance': 0,
                'total_harvested': 0,
                'total_planted': 0,
                'total_composted': 0
            }

    def get(self, request):
        """
        REFACTORING "Divide & Conquer" : Découpée en sous-méthodes atomiques pour améliorer la lisibilité.
        """
        user = request.user
        
        # 1. Cash Balance (solde principal du wallet)
        wallet = self._get_or_create_wallet(user)
        cash_balance = self._get_cash_balance(wallet)
        
        # 2. Pockets (sous-comptes)
        pockets_list = self._get_pockets(wallet)
        
        # 3. Donations (agrégations ORM - pas de boucles Python)
        donations_data = self._get_donations(user, wallet)
        
        # 4. Equity Portfolio (V2.0 - seulement si feature activée)
        equity_data = self._get_equity_portfolio(user)
        
        # 5. Social Dividend (valeur estimée symbolique)
        social_dividend_value = self._get_social_dividend(donations_data['total_amount'])
        
        # 6. SAKA (Protocole SAKA - Monnaie interne d'engagement)
        saka_data = self._get_saka_data(user)
        
        return Response({
            'cash_balance': cash_balance,
            'pockets': pockets_list,
            'donations': {
                'total_amount': str(donations_data['total_amount']),
                'metrics_count': donations_data['metrics_count']
            },
            'equity_portfolio': {
                'is_active': equity_data['is_active'],
                'positions': equity_data['positions'],
                'valuation': str(equity_data['valuation']) if equity_data['is_active'] else "0.00"
            },
            'social_dividend': {
                'estimated_value': str(social_dividend_value)
            },
            'saka': {
                'balance': saka_data['balance'],
                'total_harvested': saka_data['total_harvested'],
                'total_planted': saka_data['total_planted'],
                'total_composted': saka_data['total_composted']
            }
        })

