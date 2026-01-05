"""
Test de protection : Limites sur MANUAL_ADJUST pour empêcher l'émission arbitraire de SAKA.

PHILOSOPHIE EGOEJO :
Empêche l'émission arbitraire de SAKA via SakaReason.MANUAL_ADJUST.
- Limite stricte : 1000 SAKA/jour/utilisateur (même pour admin)
- Double validation requise pour montants > 500 SAKA

Constitution: no direct SAKA mutation - Anti-accumulation stricte.
"""
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from core.services.saka import harvest_saka, SakaReason, MANUAL_ADJUST_DAILY_LIMIT, MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD
from core.models.saka import SakaTransaction

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.egoejo_compliance
class TestManualAdjustLimits:
    """
    Tests pour vérifier les limites sur MANUAL_ADJUST.
    
    TAG : @egoejo_compliance - Test BLOQUANT pour la protection philosophique EGOEJO
    """
    
    @pytest.fixture
    def admin_user(self, db):
        """Utilisateur admin pour les tests"""
        user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user
    
    @pytest.fixture
    def regular_user(self, db):
        """Utilisateur régulier pour les tests"""
        user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='testpass123'
        )
        return user
    
    def test_manual_adjust_within_daily_limit_allowed(self, admin_user):
        """
        Vérifie qu'un MANUAL_ADJUST dans la limite quotidienne est autorisé.
        """
        # Activer SAKA pour le test
        from django.test import override_settings
        with override_settings(ENABLE_SAKA=True):
            # Créditer 500 SAKA (sous la limite de 1000)
            result = harvest_saka(
                user=admin_user,
                reason=SakaReason.MANUAL_ADJUST,
                amount=500
            )
            
            assert result is not None
            assert result.amount == 500
            assert result.direction == 'EARN'
            assert result.reason == SakaReason.MANUAL_ADJUST.value
    
    def test_manual_adjust_exceeds_daily_limit_rejected(self, admin_user):
        """
        Vérifie qu'un MANUAL_ADJUST dépassant 1000 SAKA/jour est rejeté.
        
        Constitution EGOEJO: anti-accumulation stricte.
        
        NOTE: Dans une transaction atomique, les transactions créées dans la même transaction
        ne sont pas visibles. Ce test vérifie donc la limite sur des transactions commitées.
        Pour une protection parfaite, utiliser un compteur dans le wallet (futur).
        """
        from django.test import override_settings
        from django.db import transaction
        
        with override_settings(ENABLE_SAKA=True):
            # Créditer 500 SAKA (sous la limite, sous le seuil de double validation)
            # Utiliser des transactions séparées pour que les transactions soient visibles
            with transaction.atomic():
                result1 = harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=500
                )
                assert result1 is not None
            
            # Créditer 500 SAKA supplémentaires dans une nouvelle transaction
            # (total = 1000, limite atteinte)
            with transaction.atomic():
                result2 = harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=500
                )
                assert result2 is not None
            
            # Tentative de créditer 1 SAKA supplémentaire (total = 1001 > 1000)
            # Dans une nouvelle transaction pour que les transactions précédentes soient visibles
            with transaction.atomic():
                with pytest.raises(ValidationError) as exc_info:
                    harvest_saka(
                        user=admin_user,
                        reason=SakaReason.MANUAL_ADJUST,
                        amount=1
                    )
                
                error_message = str(exc_info.value)
                assert "VIOLATION CONSTITUTION EGOEJO" in error_message
                assert "Limite quotidienne MANUAL_ADJUST dépassée" in error_message
                assert str(MANUAL_ADJUST_DAILY_LIMIT) in error_message
    
    def test_manual_adjust_single_transaction_exceeds_daily_limit_rejected(self, admin_user):
        """
        Vérifie qu'une seule transaction MANUAL_ADJUST > 1000 SAKA est rejetée.
        
        NOTE: La double validation se fait AVANT la vérification de la limite quotidienne,
        donc une transaction de 1500 SAKA échoue à cause de la double validation (> 500),
        pas à cause de la limite quotidienne.
        """
        from django.test import override_settings
        with override_settings(ENABLE_SAKA=True):
            # Tentative de créditer 1500 SAKA en une seule fois (> limite de 1000)
            # NOTE: Échoue à cause de la double validation (> 500) AVANT la limite quotidienne
            with pytest.raises(ValidationError) as exc_info:
                harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=1500
                )
            
            error_message = str(exc_info.value)
            assert "VIOLATION CONSTITUTION EGOEJO" in error_message
            # La double validation se fait en premier, donc le message est "nécessite une double validation"
            assert "nécessite une double validation" in error_message
            assert str(MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD) in error_message
    
    def test_manual_adjust_exceeds_dual_approval_threshold_rejected(self, admin_user):
        """
        Vérifie qu'un MANUAL_ADJUST > 500 SAKA nécessite une double validation (rejeté pour l'instant).
        
        Constitution EGOEJO: anti-accumulation stricte.
        TODO: Implémenter le mécanisme de double validation.
        """
        from django.test import override_settings
        with override_settings(ENABLE_SAKA=True):
            # Tentative de créditer 501 SAKA (> seuil de 500)
            with pytest.raises(ValidationError) as exc_info:
                harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=501
                )
            
            error_message = str(exc_info.value)
            assert "VIOLATION CONSTITUTION EGOEJO" in error_message
            assert "nécessite une double validation" in error_message
            assert str(MANUAL_ADJUST_DUAL_APPROVAL_THRESHOLD) in error_message
            assert "TODO" in error_message  # Indique que le mécanisme n'est pas encore implémenté
    
    def test_manual_adjust_exactly_dual_approval_threshold_allowed(self, admin_user):
        """
        Vérifie qu'un MANUAL_ADJUST = 500 SAKA (seuil exact) est autorisé.
        """
        from django.test import override_settings
        with override_settings(ENABLE_SAKA=True):
            # Créditer exactement 500 SAKA (seuil de double validation)
            result = harvest_saka(
                user=admin_user,
                reason=SakaReason.MANUAL_ADJUST,
                amount=500
            )
            
            assert result is not None
            assert result.amount == 500
    
    def test_manual_adjust_daily_limit_resets_next_day(self, admin_user):
        """
        Vérifie que la limite quotidienne se réinitialise le jour suivant.
        """
        from django.test import override_settings
        from django.db import transaction
        
        with override_settings(ENABLE_SAKA=True):
            # Créditer 500 SAKA aujourd'hui (sous la limite, sous le seuil de double validation)
            with transaction.atomic():
                result1 = harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=500
                )
                assert result1 is not None
            
            # Créditer 500 SAKA supplémentaires (total = 1000, limite atteinte)
            with transaction.atomic():
                result2 = harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=500
                )
                assert result2 is not None
            
            # Vérifier qu'une nouvelle transaction est rejetée aujourd'hui
            with transaction.atomic():
                with pytest.raises(ValidationError) as exc_info:
                    harvest_saka(
                        user=admin_user,
                        reason=SakaReason.MANUAL_ADJUST,
                        amount=1
                    )
                
                error_message = str(exc_info.value)
                assert "VIOLATION CONSTITUTION EGOEJO" in error_message
                assert "Limite quotidienne MANUAL_ADJUST dépassée" in error_message
            
            # Simuler le jour suivant en modifiant la date de création de la transaction
            # (Dans un vrai scénario, on attendrait le jour suivant)
            # Pour ce test, on vérifie que la logique de date fonctionne
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            # Modifier la date des transactions existantes pour simuler hier
            SakaTransaction.objects.filter(
                user=admin_user,
                reason=SakaReason.MANUAL_ADJUST.value,
                created_at__date=today
            ).update(created_at=timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time())))
            
            # Maintenant, une nouvelle transaction devrait être autorisée
            with transaction.atomic():
                result3 = harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=500
                )
                assert result3 is not None
                assert result3.amount == 500
    
    def test_manual_adjust_limit_applies_to_all_users(self, regular_user):
        """
        Vérifie que la limite de 1000 SAKA/jour s'applique à tous les utilisateurs (pas seulement admin).
        """
        from django.test import override_settings
        from django.db import transaction
        
        with override_settings(ENABLE_SAKA=True):
            # Créditer 500 SAKA (sous la limite, sous le seuil de double validation)
            with transaction.atomic():
                result1 = harvest_saka(
                    user=regular_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=500
                )
                assert result1 is not None
            
            # Créditer 500 SAKA supplémentaires (total = 1000, limite atteinte)
            with transaction.atomic():
                result2 = harvest_saka(
                    user=regular_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=500
                )
                assert result2 is not None
            
            # Vérifier qu'une nouvelle transaction est rejetée
            with transaction.atomic():
                with pytest.raises(ValidationError) as exc_info:
                    harvest_saka(
                        user=regular_user,
                        reason=SakaReason.MANUAL_ADJUST,
                        amount=1
                    )
                
                error_message = str(exc_info.value)
                assert "VIOLATION CONSTITUTION EGOEJO" in error_message
                assert "Limite quotidienne MANUAL_ADJUST dépassée" in error_message
    
    def test_manual_adjust_dual_approval_threshold_is_strict(self, admin_user):
        """
        Vérifie que le seuil de double validation est strict (> 500, pas >= 500).
        """
        from django.test import override_settings
        with override_settings(ENABLE_SAKA=True):
            # 500 SAKA doit être autorisé (seuil exact)
            result1 = harvest_saka(
                user=admin_user,
                reason=SakaReason.MANUAL_ADJUST,
                amount=500
            )
            assert result1 is not None
            
            # 501 SAKA doit être rejeté (dépasse le seuil)
            with pytest.raises(ValidationError) as exc_info:
                harvest_saka(
                    user=admin_user,
                    reason=SakaReason.MANUAL_ADJUST,
                    amount=501
                )
            
            error_message = str(exc_info.value)
            assert "nécessite une double validation" in error_message

