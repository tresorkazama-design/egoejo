"""
EGOEJO Compliance Test : Redistribution du Silo SAKA

LOI EGOEJO :
"Le Silo ne peut pas être vidé par un seul acteur. La redistribution suit une règle collective."

Ce test vérifie que :
- Le Silo ne peut pas être vidé par un seul acteur
- La redistribution suit une règle collective
- Aucune redistribution individualisée arbitraire n'est possible

Violation du Manifeste EGOEJO si :
- Un seul acteur peut vider le Silo
- La redistribution n'est pas collective
- Des redistributions individualisées arbitraires sont possibles
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import override_settings

from core.models.saka import SakaWallet, SakaTransaction, SakaSilo
from core.services.saka import harvest_saka, redistribute_saka_silo, run_saka_compost_cycle, SakaReason

User = get_user_model()


class TestSiloRedistribution:
    """
    Tests de conformité : Redistribution du Silo SAKA
    
    RÈGLE ABSOLUE : Le Silo ne peut pas être vidé par un seul acteur.
    """
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_SILO_REDIS_ENABLED=True,
        SAKA_SILO_REDIS_RATE=0.1,  # 10% du Silo
        SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
    )
    def test_silo_ne_peut_pas_etre_vide_par_un_seul_acteur(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Un seul acteur peut vider le Silo.
        
        Test : Vérifier que la redistribution ne vide jamais complètement le Silo.
        """
        # Créer plusieurs utilisateurs
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'test_silo_user_{i}',
                email=f'test_silo_user_{i}@example.com',
                password='testpass123'
            )
            users.append(user)
        
        # Récolter du SAKA pour chaque utilisateur
        for user in users:
            harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
        
        # Alimenter le Silo via compostage
        # (simuler que certains wallets sont inactifs et compostés)
        silo, _ = SakaSilo.objects.get_or_create()
        silo.total_balance = 1000  # Silo avec 1000 grains
        silo.save()
        
        initial_silo_balance = silo.total_balance
        
        # Exécuter la redistribution (10% du Silo = 100 grains)
        redistribute_result = redistribute_saka_silo(rate=0.1)
        
        assert redistribute_result['ok'] is True, (
            f"VIOLATION DU MANIFESTE EGOEJO : La redistribution a échoué. "
            f"Raison : {redistribute_result.get('reason', 'unknown')}"
        )
        
        # Vérifier que le Silo n'a pas été vidé
        silo.refresh_from_db()
        final_silo_balance = silo.total_balance
        
        assert final_silo_balance > 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le Silo a été vidé par la redistribution. "
            f"Solde final : {final_silo_balance}. "
            f"Le Silo ne peut pas être vidé par un seul acteur."
        )
        
        # Vérifier que le Silo a été débité correctement (10% seulement)
        expected_debit = int(initial_silo_balance * 0.1)
        actual_debit = initial_silo_balance - final_silo_balance
        
        assert actual_debit == expected_debit, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le Silo a été débité incorrectement. "
            f"Débit attendu : {expected_debit}, Débit actuel : {actual_debit}. "
            f"La redistribution doit suivre une règle collective (taux fixe)."
        )
        
        # Vérifier que le Silo contient encore au moins 90% de son solde initial
        remaining_percentage = (final_silo_balance / initial_silo_balance) * 100
        assert remaining_percentage >= 90, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le Silo a été vidé de plus de 10%. "
            f"Pourcentage restant : {remaining_percentage}%. "
            f"Le Silo ne peut pas être vidé par un seul acteur."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_SILO_REDIS_ENABLED=True,
        SAKA_SILO_REDIS_RATE=0.05,  # 5% du Silo
        SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
    )
    def test_redistribution_suit_regle_collective(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        La redistribution ne suit pas une règle collective.
        
        Test : Vérifier que la redistribution est égale pour tous les wallets éligibles.
        """
        # Créer plusieurs utilisateurs avec activité
        users = []
        for i in range(4):
            user = User.objects.create_user(
                username=f'test_collective_user_{i}',
                email=f'test_collective_user_{i}@example.com',
                password='testpass123'
            )
            # Récolter du SAKA pour rendre le wallet éligible
            harvest_saka(user, SakaReason.CONTENT_READ, amount=50)
            users.append(user)
        
        # Alimenter le Silo (utiliser id=1 pour cohérence avec le service)
        silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        silo.total_balance = 1000
        silo.save()
        
        initial_silo_balance = silo.total_balance
        
        # Récupérer les soldes initiaux des wallets APRÈS la récolte
        initial_balances = {}
        for user in users:
            wallet = user.saka_wallet
            wallet.refresh_from_db()  # S'assurer d'avoir le solde à jour
            initial_balances[user.id] = wallet.balance
        
        # Exécuter la redistribution (5% du Silo = 50 grains, répartis entre 4 wallets = 12.5 grains chacun)
        redistribute_result = redistribute_saka_silo(rate=0.05)
        
        assert redistribute_result['ok'] is True, (
            f"VIOLATION DU MANIFESTE EGOEJO : La redistribution a échoué. "
            f"Raison : {redistribute_result.get('reason', 'unknown')}"
        )
        
        # Vérifier que tous les wallets éligibles ont reçu la même part
        per_wallet = redistribute_result.get('per_wallet', 0)
        assert per_wallet > 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Aucun wallet n'a reçu de redistribution. "
            f"Per wallet : {per_wallet}. "
            f"La redistribution doit être collective."
        )
        
        # Vérifier que tous les wallets ont reçu la même part
        for user in users:
            wallet = user.saka_wallet
            wallet.refresh_from_db()
            expected_balance = initial_balances[user.id] + per_wallet
            assert wallet.balance == expected_balance, (
                f"VIOLATION DU MANIFESTE EGOEJO : Le wallet de {user.username} n'a pas reçu la part collective. "
                f"Solde attendu : {expected_balance}, Solde actuel : {wallet.balance}. "
                f"La redistribution doit être égale pour tous les wallets éligibles."
            )
        
        # Vérifier que le total redistribué correspond au calcul collectif
        total_redistributed = redistribute_result.get('redistributed', 0)
        expected_total = per_wallet * len(users)
        assert total_redistributed == expected_total, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le total redistribué ne correspond pas au calcul collectif. "
            f"Total attendu : {expected_total}, Total actuel : {total_redistributed}. "
            f"La redistribution doit suivre une règle collective."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_SILO_REDIS_ENABLED=True,
        SAKA_SILO_REDIS_RATE=0.1,
        SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
    )
    def test_aucune_redistribution_individualisee_arbitraire(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Des redistributions individualisées arbitraires sont possibles.
        
        Test : Vérifier que la redistribution ne peut pas être ciblée sur un seul wallet.
        """
        # Créer plusieurs utilisateurs
        users = []
        for i in range(3):
            user = User.objects.create_user(
                username=f'test_no_individual_user_{i}',
                email=f'test_no_individual_user_{i}@example.com',
                password='testpass123'
            )
            harvest_saka(user, SakaReason.CONTENT_READ, amount=50)
            users.append(user)
        
        # Alimenter le Silo (utiliser id=1 pour cohérence avec le service)
        silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        silo.total_balance = 1000
        silo.save()
        
        initial_silo_balance = silo.total_balance
        
        # Récupérer les soldes initiaux APRÈS la récolte
        initial_balances = {}
        for user in users:
            wallet = user.saka_wallet
            wallet.refresh_from_db()  # S'assurer d'avoir le solde à jour
            initial_balances[user.id] = wallet.balance
        
        # Exécuter la redistribution
        redistribute_result = redistribute_saka_silo(rate=0.1)
        
        assert redistribute_result['ok'] is True, (
            f"VIOLATION DU MANIFESTE EGOEJO : La redistribution a échoué. "
            f"Raison : {redistribute_result.get('reason', 'unknown')}"
        )
        
        # Vérifier que TOUS les wallets éligibles ont reçu la redistribution
        per_wallet = redistribute_result.get('per_wallet', 0)
        eligible_wallets = redistribute_result.get('eligible_wallets', 0)
        
        assert eligible_wallets == len(users), (
            f"VIOLATION DU MANIFESTE EGOEJO : Tous les wallets éligibles n'ont pas été inclus. "
            f"Wallets éligibles attendus : {len(users)}, Wallets éligibles actuels : {eligible_wallets}. "
            f"La redistribution doit être collective, pas individualisée."
        )
        
        # Vérifier qu'aucun wallet n'a reçu plus que sa part
        for user in users:
            wallet = user.saka_wallet
            wallet.refresh_from_db()
            received = wallet.balance - initial_balances[user.id]
            assert received == per_wallet, (
                f"VIOLATION DU MANIFESTE EGOEJO : Le wallet de {user.username} a reçu une redistribution individualisée. "
                f"Reçu : {received}, Part collective : {per_wallet}. "
                f"Aucune redistribution individualisée arbitraire n'est autorisée."
            )
        
        # Vérifier que le total redistribué correspond à la règle collective
        total_redistributed = redistribute_result.get('redistributed', 0)
        expected_total = per_wallet * len(users)
        assert total_redistributed == expected_total, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le total redistribué ne correspond pas à la règle collective. "
            f"Total attendu : {expected_total}, Total actuel : {total_redistributed}. "
            f"La redistribution doit suivre une règle collective, pas être individualisée."
        )
    
    @pytest.mark.django_db
    @override_settings(
        ENABLE_SAKA=True,
        SAKA_SILO_REDIS_ENABLED=True,
        SAKA_SILO_REDIS_RATE=0.5,  # 50% du Silo (taux élevé pour tester)
        SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
    )
    def test_silo_reste_toujours_alimente(self):
        """
        VIOLATION DU MANIFESTE EGOEJO si :
        Le Silo peut être complètement vidé.
        
        Test : Vérifier que le Silo reste toujours alimenté (même avec un taux élevé).
        """
        # Créer plusieurs utilisateurs
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'test_silo_always_fed_user_{i}',
                email=f'test_silo_always_fed_user_{i}@example.com',
                password='testpass123'
            )
            harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
            users.append(user)
        
        # Alimenter le Silo (utiliser id=1 pour cohérence avec le service)
        silo, _ = SakaSilo.objects.get_or_create(
            id=1,
            defaults={
                'total_balance': 0,
                'total_composted': 0,
                'total_cycles': 0,
            }
        )
        silo.total_balance = 1000
        silo.save()
        
        initial_silo_balance = silo.total_balance
        
        # Exécuter plusieurs redistributions successives
        for i in range(3):
            redistribute_result = redistribute_saka_silo(rate=0.5)
            
            silo.refresh_from_db()
            current_silo_balance = silo.total_balance
            
            # Vérifier que le Silo n'est jamais vide
            assert current_silo_balance > 0, (
                f"VIOLATION DU MANIFESTE EGOEJO : Le Silo a été vidé après {i+1} redistribution(s). "
                f"Solde actuel : {current_silo_balance}. "
                f"Le Silo ne peut pas être complètement vidé."
            )
            
            # Vérifier que le Silo reste alimenté (même après plusieurs redistributions)
            if i < 2:  # Pas la dernière itération
                assert current_silo_balance < initial_silo_balance, (
                    f"VIOLATION DU MANIFESTE EGOEJO : Le Silo n'a pas été débité après redistribution {i+1}. "
                    f"Solde actuel : {current_silo_balance}, Solde initial : {initial_silo_balance}. "
                    f"La redistribution doit débité le Silo."
                )
        
        # Vérifier que le Silo contient encore du SAKA
        silo.refresh_from_db()
        assert silo.total_balance > 0, (
            f"VIOLATION DU MANIFESTE EGOEJO : Le Silo a été complètement vidé après plusieurs redistributions. "
            f"Solde final : {silo.total_balance}. "
            f"Le Silo doit toujours rester alimenté."
        )

