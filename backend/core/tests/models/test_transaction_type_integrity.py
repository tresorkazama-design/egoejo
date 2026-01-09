"""
Tests data integrity - transaction_type toujours non-null

Objectif: Garantir que transaction_type ne peut jamais être null (régression)
Risque couvert: Corruption données, régressions
Niveau: P0 (BLOQUANT)
Temps visé: ~30s
Déterministe: Oui
"""
import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from core.models.saka import SakaTransaction

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.critical
@pytest.mark.egoejo_compliance
class TestTransactionTypeIntegrity:
    """
    Tests pour garantir que transaction_type est toujours non-null.
    
    Vérifie:
    - Création avec transaction_type None → ValidationError
    - Création avec transaction_type vide → ValidationError
    - Création avec transaction_type valide → Succès
    """
    
    def test_transaction_type_cannot_be_none(self):
        """Vérifie que transaction_type ne peut pas être None."""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        
        # Tentative de création avec transaction_type=None
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            SakaTransaction.objects.create(
                user=user,
                amount=100,
                direction='EARN',
                reason='test',
                transaction_type=None  # VIOLATION
            )
        
        # Vérifier que l'erreur mentionne transaction_type
        error_msg = str(exc_info.value)
        assert 'transaction_type' in error_msg.lower() or 'obligatoire' in error_msg.lower()
    
    def test_transaction_type_cannot_be_empty(self):
        """Vérifie que transaction_type ne peut pas être vide."""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        
        # Tentative de création avec transaction_type=''
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            SakaTransaction.objects.create(
                user=user,
                amount=100,
                direction='EARN',
                reason='test',
                transaction_type=''  # VIOLATION
            )
        
        error_msg = str(exc_info.value)
        assert 'transaction_type' in error_msg.lower() or 'obligatoire' in error_msg.lower()
    
    def test_transaction_type_must_be_valid(self):
        """Vérifie que transaction_type doit être dans les choix valides."""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        
        # Tentative de création avec transaction_type invalide
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            SakaTransaction.objects.create(
                user=user,
                amount=100,
                direction='EARN',
                reason='test',
                transaction_type='INVALID_TYPE'  # VIOLATION
            )
        
        error_msg = str(exc_info.value)
        assert 'transaction_type' in error_msg.lower() or 'invalide' in error_msg.lower()
    
    def test_transaction_type_valid_creation_succeeds(self):
        """Vérifie que création avec transaction_type valide réussit."""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        
        # Création avec transaction_type valide
        transaction = SakaTransaction.objects.create(
            user=user,
            amount=100,
            direction='EARN',
            reason='test',
            transaction_type='HARVEST'  # VALIDE
        )
        
        assert transaction.transaction_type == 'HARVEST'
        assert transaction.transaction_type is not None
        assert transaction.transaction_type != ''
    
    def test_transaction_type_coherence_with_direction(self):
        """Vérifie la cohérence transaction_type / direction."""
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
        
        # EARN avec transaction_type SPEND → doit échouer
        with pytest.raises((ValidationError, ValueError)) as exc_info:
            SakaTransaction.objects.create(
                user=user,
                amount=100,
                direction='EARN',
                reason='test',
                transaction_type='SPEND'  # INCOHÉRENT avec direction='EARN'
            )
        
        error_msg = str(exc_info.value)
        assert 'incompatible' in error_msg.lower() or 'transaction_type' in error_msg.lower()


