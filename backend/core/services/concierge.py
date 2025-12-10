"""
Services pour le Concierge Support
Logique d'éligibilité et gestion des threads de support
"""
from django.db.models import Sum, Q
from decimal import Decimal
from finance.models import WalletTransaction
from core.models.fundraising import Contribution


def is_user_concierge_eligible(user):
    """
    Vérifie si un utilisateur est éligible au Concierge Support.
    
    Conditions d'éligibilité :
    1. user.is_premium = True
    OU
    2. Total des dons >= 500€
    OU
    3. Total des investissements >= 1000€ (si V2.0 actif)
    
    Args:
        user: Utilisateur à vérifier
    
    Returns:
        bool: True si éligible, False sinon
    """
    # Condition 1 : Premium
    if hasattr(user, 'is_premium') and user.is_premium:
        return True
    
    # Condition 2 : Total des dons >= 500€
    # Via WalletTransaction (PLEDGE_DONATION)
    wallet = getattr(user, 'wallet', None)
    if wallet:
        donations_total = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='PLEDGE_DONATION'
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')
        
        if donations_total >= Decimal('500'):
            return True
    
    # Via Contribution (Cagnotte)
    contributions_total = Contribution.objects.filter(
        user=user
    ).aggregate(
        total=Sum('montant')
    )['total'] or 0
    
    if contributions_total and Decimal(str(contributions_total)) >= Decimal('500'):
        return True
    
    # Condition 3 : Total des investissements >= 1000€ (V2.0)
    from django.conf import settings
    if settings.ENABLE_INVESTMENT_FEATURES:
        try:
            from investment.models import ShareholderRegister
            
            investments_total = ShareholderRegister.objects.filter(
                investor=user
            ).aggregate(
                total=Sum('amount_invested')
            )['total'] or Decimal('0')
            
            if investments_total >= Decimal('1000'):
                return True
        except ImportError:
            pass
    
    return False


def get_or_create_concierge_thread(user):
    """
    Récupère ou crée le thread SUPPORT_CONCIERGE pour un utilisateur.
    
    Args:
        user: Utilisateur
    
    Returns:
        tuple: (ChatThread, created)
    
    Raises:
        PermissionDenied: Si l'utilisateur n'est pas éligible
    """
    from core.models.chat import ChatThread, ChatMembership
    from django.core.exceptions import PermissionDenied
    
    # Vérifier l'éligibilité
    if not is_user_concierge_eligible(user):
        raise PermissionDenied(
            "Vous n'êtes pas éligible au Concierge Support. "
            "Conditions : Premium, ou 500€+ de dons, ou 1000€+ d'investissements."
        )
    
    # Récupérer ou créer le thread
    thread, created = ChatThread.objects.get_or_create(
        created_by=user,
        thread_type=ChatThread.THREAD_TYPE_SUPPORT_CONCIERGE,
        defaults={
            'title': f'Support Concierge - {user.username}',
            'is_private': True,
        }
    )
    
    # S'assurer que l'utilisateur est participant
    if created:
        ChatMembership.objects.create(
            thread=thread,
            user=user,
            role=ChatMembership.ROLE_OWNER
        )
    else:
        # Vérifier que l'utilisateur est toujours participant
        if not thread.participants.filter(pk=user.pk).exists():
            ChatMembership.objects.get_or_create(
                thread=thread,
                user=user,
                defaults={'role': ChatMembership.ROLE_OWNER}
            )
    
    return thread, created

