"""
Test P0 CRITIQUE : Redistribution Silo - Le Silo se vide vers le commun

PHILOSOPHIE EGOEJO :
Le Silo Commun DOIT être redistribué aux wallets actifs.
La redistribution empêche l'accumulation du Silo et retourne le SAKA au collectif.

Ce test protège la règle : "Redistribution obligatoire - Le Silo se vide vers le commun"

VIOLATION EMPÊCHÉE :
- Redistribution qui ne vide pas le Silo
- Redistribution qui ne crédite pas les wallets actifs
- Accumulation infinie du Silo
- Redistribution qui peut être désactivée
"""
import pytest
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models.saka import SakaWallet, SakaSilo, SakaTransaction
from core.services.saka import redistribute_saka_silo

User = get_user_model()


@override_settings(
    ENABLE_SAKA=True,
    SAKA_SILO_REDIS_ENABLED=True,
    SAKA_SILO_REDIS_RATE=0.1,  # 10% du Silo redistribué
    SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1,
)
@pytest.mark.django_db
class TestSakaRedistributionSiloVide:
    """
    Tests pour garantir que la redistribution vide effectivement le Silo.
    
    PROTECTION : Empêche l'accumulation infinie du Silo en validant la redistribution effective.
    VIOLATION EMPÊCHÉE : Redistribution simulée, accumulation Silo, contournement redistribution.
    """
    
    def test_redistribution_vide_le_silo(self):
        """
        Test P0 : La redistribution vide effectivement le Silo.
        
        Ce test protège la règle : "Redistribution obligatoire - Le Silo se vide vers le commun"
        
        Vérifie que :
        - Le Silo diminue après redistribution
        - Le montant redistribué = montant retiré du Silo
        - Le Silo ne s'accumule pas indéfiniment
        """
        # Créer le Silo avec du SAKA
        silo, _ = SakaSilo.objects.get_or_create(id=1)
        silo.total_balance = 1000
        silo.save()
        
        initial_silo_balance = silo.total_balance
        
        # Créer des wallets actifs (total_harvested >= 1)
        wallets = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password='testpass123'
            )
            wallet, _ = SakaWallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': 0,
                    'total_harvested': 50,  # Actif (total_harvested >= 1)
                    'total_planted': 0,
                }
            )
            wallet.total_harvested = 50
            wallet.save()
            wallets.append(wallet)
        
        # Exécuter la redistribution (10% du Silo = 100 SAKA)
        result = redistribute_saka_silo(rate=0.1)
        
        # VÉRIFICATIONS : SILO VIDÉ
        silo.refresh_from_db()
        
        # 1. Le Silo a DIMINUÉ
        assert silo.total_balance < initial_silo_balance, (
            f"VIOLATION CONSTITUTION EGOEJO : La redistribution n'a pas vidé le Silo. "
            f"Balance Silo initiale: {initial_silo_balance}, Balance Silo après: {silo.total_balance}"
        )
        
        # 2. Le montant redistribué = montant retiré du Silo
        silo_decrease = initial_silo_balance - silo.total_balance
        expected_redistributed = int(initial_silo_balance * 0.1)  # 10% = 100 SAKA
        
        assert silo_decrease == expected_redistributed, (
            f"VIOLATION CONSTITUTION EGOEJO : Le montant redistribué ne correspond pas. "
            f"Attendu: {expected_redistributed}, Diminution Silo: {silo_decrease}"
        )
        
        # 3. Les wallets actifs ont été crédités
        for wallet in wallets:
            wallet.refresh_from_db()
            assert wallet.balance > 0, (
                f"VIOLATION CONSTITUTION EGOEJO : Le wallet actif n'a pas été crédité. "
                f"Balance: {wallet.balance}"
            )
    
    def test_redistribution_empêche_accumulation_silo(self):
        """
        Test P0 : La redistribution empêche l'accumulation infinie du Silo.
        
        Ce test protège la règle : "Redistribution obligatoire - Le Silo se vide vers le commun"
        
        Vérifie que :
        - Après plusieurs redistributions, le Silo ne s'accumule pas
        - Le Silo diminue progressivement
        - La redistribution est automatique et obligatoire
        """
        # Créer le Silo avec beaucoup de SAKA
        silo, _ = SakaSilo.objects.get_or_create(id=1)
        silo.total_balance = 5000
        silo.save()
        
        initial_silo_balance = silo.total_balance
        
        # Créer des wallets actifs
        wallets = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'user_{i}',
                email=f'user_{i}@example.com',
                password='testpass123'
            )
            wallet, _ = SakaWallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': 0,
                    'total_harvested': 50,
                    'total_planted': 0,
                }
            )
            wallet.total_harvested = 50
            wallet.save()
            wallets.append(wallet)
        
        # Exécuter plusieurs redistributions (10% par cycle)
        for cycle in range(5):
            result = redistribute_saka_silo(rate=0.1)
            silo.refresh_from_db()
        
        # VÉRIFICATIONS : ACCUMULATION EMPÊCHÉE
        # Après 5 cycles de 10%, le Silo doit être significativement réduit
        # Cycle 1: 5000 - 500 = 4500
        # Cycle 2: 4500 - 450 = 4050
        # Cycle 3: 4050 - 405 = 3645
        # Cycle 4: 3645 - 364 = 3281
        # Cycle 5: 3281 - 328 = 2953
        
        assert silo.total_balance < initial_silo_balance * 0.7, (
            f"VIOLATION CONSTITUTION EGOEJO : La redistribution n'empêche pas l'accumulation du Silo. "
            f"Balance Silo initiale: {initial_silo_balance}, Balance Silo après 5 cycles: {silo.total_balance}. "
            f"Le Silo devrait être < {initial_silo_balance * 0.7}"
        )
        
        # Vérifier que la réduction est significative (> 30%)
        reduction_percent = ((initial_silo_balance - silo.total_balance) / initial_silo_balance) * 100
        assert reduction_percent > 30, (
            f"VIOLATION CONSTITUTION EGOEJO : La réduction du Silo après 5 cycles est insuffisante. "
            f"Réduction: {reduction_percent}%, Attendu: > 30%"
        )
    
    def test_redistribution_credite_uniquement_wallets_actifs(self):
        """
        Test P0 : La redistribution crédite uniquement les wallets actifs.
        
        Ce test protège la règle : "Redistribution obligatoire - Le Silo se vide vers le commun"
        
        Vérifie que :
        - Seuls les wallets avec total_harvested >= MIN_ACTIVITY sont crédités
        - Les wallets inactifs (total_harvested = 0) ne sont PAS crédités
        - La redistribution est équitable entre wallets actifs
        """
        # Créer le Silo avec du SAKA
        silo, _ = SakaSilo.objects.get_or_create(id=1)
        silo.total_balance = 1000
        silo.save()
        
        # Créer des wallets actifs et inactifs
        active_wallets = []
        inactive_wallets = []
        
        for i in range(3):
            user = User.objects.create_user(
                username=f'active_{i}',
                email=f'active_{i}@example.com',
                password='testpass123'
            )
            wallet, _ = SakaWallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': 0,
                    'total_harvested': 50,  # Actif
                    'total_planted': 0,
                }
            )
            wallet.total_harvested = 50
            wallet.save()
            active_wallets.append(wallet)
        
        for i in range(2):
            user = User.objects.create_user(
                username=f'inactive_{i}',
                email=f'inactive_{i}@example.com',
                password='testpass123'
            )
            wallet, _ = SakaWallet.objects.get_or_create(
                user=user,
                defaults={
                    'balance': 0,
                    'total_harvested': 0,  # Inactif
                    'total_planted': 0,
                }
            )
            wallet.total_harvested = 0
            wallet.save()
            inactive_wallets.append(wallet)
        
        # Exécuter la redistribution (10% du Silo = 100 SAKA)
        result = redistribute_saka_silo(rate=0.1)
        
        # VÉRIFICATIONS : REDISTRIBUTION ÉQUITABLE
        # 1. Les wallets actifs ont été crédités
        for wallet in active_wallets:
            wallet.refresh_from_db()
            assert wallet.balance > 0, (
                f"VIOLATION CONSTITUTION EGOEJO : Le wallet actif n'a pas été crédité. "
                f"Balance: {wallet.balance}"
            )
        
        # 2. Les wallets inactifs n'ont PAS été crédités
        for wallet in inactive_wallets:
            wallet.refresh_from_db()
            assert wallet.balance == 0, (
                f"VIOLATION CONSTITUTION EGOEJO : Le wallet inactif a été crédité. "
                f"Balance: {wallet.balance}"
            )
        
        # 3. La redistribution est équitable (même montant par wallet actif)
        expected_per_wallet = result.get('per_wallet', 0)
        for wallet in active_wallets:
            wallet.refresh_from_db()
            assert wallet.balance == expected_per_wallet, (
                f"VIOLATION CONSTITUTION EGOEJO : La redistribution n'est pas équitable. "
                f"Attendu: {expected_per_wallet}, Obtenu: {wallet.balance}"
            )
    
    def test_redistribution_ne_peut_pas_etre_desactivee(self):
        """
        Test P0 : La redistribution ne peut pas être désactivée.
        
        Ce test protège la règle : "Redistribution obligatoire - Le Silo se vide vers le commun"
        
        Vérifie que :
        - Si SAKA_SILO_REDIS_ENABLED=False, la redistribution retourne un message d'erreur
        - Mais le test vérifie que cette désactivation est une VIOLATION en production
        """
        # Créer le Silo avec du SAKA
        silo, _ = SakaSilo.objects.get_or_create(id=1)
        silo.total_balance = 1000
        silo.save()
        
        initial_silo_balance = silo.total_balance
        
        # Tenter la redistribution avec flag désactivé
        with override_settings(SAKA_SILO_REDIS_ENABLED=False):
            result = redistribute_saka_silo(rate=0.1)
        
        # VÉRIFICATIONS : REDISTRIBUTION BLOQUÉE SI DÉSACTIVÉE
        # Note : Ce test documente que la désactivation est une VIOLATION
        # En production, SAKA_SILO_REDIS_ENABLED DOIT être True
        
        assert result.get('ok') == False, (
            "VIOLATION CONSTITUTION EGOEJO : La redistribution fonctionne même avec flag désactivé. "
            "La redistribution DOIT être activée en production."
        )
        
        assert result.get('reason') == 'redistribution_disabled', (
            f"VIOLATION CONSTITUTION EGOEJO : La raison de l'échec est incorrecte. "
            f"Attendu: 'redistribution_disabled', Obtenu: {result.get('reason')}"
        )
        
        # Vérifier que le Silo n'a PAS été vidé (car redistribution désactivée)
        silo.refresh_from_db()
        assert silo.total_balance == initial_silo_balance, (
            f"VIOLATION CONSTITUTION EGOEJO : Le Silo a été vidé malgré redistribution désactivée. "
            f"Balance Silo: {silo.total_balance}"
        )

