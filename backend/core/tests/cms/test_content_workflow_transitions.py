"""
Tests unitaires pour les transitions de workflow CMS V1.

Vérifie que les transitions autorisées fonctionnent et que les transitions invalides sont bloquées.
"""

import pytest
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.utils import timezone

from core.models import EducationalContent
from core.permissions import (
    CONTENT_EDITOR_GROUP_NAME,
    CONTENT_CONTRIBUTOR_GROUP_NAME,
)


@pytest.fixture
def contributor_user(db):
    """Utilisateur avec rôle Contributor"""
    user = User.objects.create_user(
        username='contributor',
        email='contributor@example.com',
        password='testpass123'
    )
    group, _ = Group.objects.get_or_create(name=CONTENT_CONTRIBUTOR_GROUP_NAME)
    user.groups.add(group)
    return user


@pytest.fixture
def editor_user(db):
    """Utilisateur avec rôle Editor"""
    user = User.objects.create_user(
        username='editor',
        email='editor@example.com',
        password='testpass123'
    )
    group, _ = Group.objects.get_or_create(name=CONTENT_EDITOR_GROUP_NAME)
    user.groups.add(group)
    return user


@pytest.fixture
def admin_user(db):
    """Utilisateur avec rôle Admin (superuser)"""
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
def content_draft(db, contributor_user):
    """Contenu en brouillon"""
    return EducationalContent.objects.create(
        title='Draft Content',
        slug='draft-content',
        type='article',
        status='draft',
        description='Description draft',
        author=contributor_user,
    )


@pytest.fixture
def content_pending(db, contributor_user):
    """Contenu en attente de validation"""
    return EducationalContent.objects.create(
        title='Pending Content',
        slug='pending-content',
        type='article',
        status='pending',
        description='Description pending',
        author=contributor_user,
    )


@pytest.fixture
def content_published(db, admin_user):
    """Contenu publié"""
    content = EducationalContent.objects.create(
        title='Published Content',
        slug='published-content',
        type='article',
        status='published',
        description='Description published',
        author=admin_user,
    )
    content.published_by = admin_user
    content.published_at = timezone.now()
    content.save()
    return content


@pytest.mark.django_db
class TestWorkflowTransitions:
    """Tests des transitions de workflow"""
    
    def test_draft_to_pending_contributor(self, content_draft, contributor_user):
        """Un contributor peut soumettre un brouillon (draft -> pending)"""
        content_draft.transition_to("pending", user=contributor_user)
        content_draft.refresh_from_db()
        assert content_draft.status == "pending"
        assert content_draft.modified_by == contributor_user
    
    def test_draft_to_pending_editor(self, content_draft, editor_user):
        """Un editor peut soumettre un brouillon (draft -> pending)"""
        content_draft.transition_to("pending", user=editor_user)
        content_draft.refresh_from_db()
        assert content_draft.status == "pending"
        assert content_draft.modified_by == editor_user
    
    def test_draft_to_pending_anonymous_forbidden(self, content_draft):
        """Un utilisateur anonyme ne peut pas soumettre un brouillon"""
        # Créer un utilisateur anonyme (non authentifié)
        anonymous_user = User.objects.create_user(
            username='anonymous',
            email='anonymous@example.com',
            password='testpass123'
        )
        # Ne pas ajouter de groupe, donc pas contributor ni editor
        with pytest.raises(ValidationError, match="Seuls les Contributors et Editors"):
            content_draft.transition_to("pending", user=anonymous_user)
    
    def test_pending_to_published_admin(self, content_pending, admin_user):
        """Un admin peut publier un contenu (pending -> published)"""
        content_pending.transition_to("published", user=admin_user)
        content_pending.refresh_from_db()
        assert content_pending.status == "published"
        assert content_pending.published_by == admin_user
        assert content_pending.published_at is not None
        assert content_pending.modified_by == admin_user
    
    def test_pending_to_published_editor_forbidden(self, content_pending, editor_user):
        """Un editor ne peut pas publier (seuls les admins)"""
        with pytest.raises(ValidationError, match="Seuls les Admins"):
            content_pending.transition_to("published", user=editor_user)
    
    def test_pending_to_rejected_editor(self, content_pending, editor_user):
        """Un editor peut rejeter un contenu (pending -> rejected)"""
        content_pending.transition_to("rejected", user=editor_user)
        content_pending.refresh_from_db()
        assert content_pending.status == "rejected"
        assert content_pending.modified_by == editor_user
    
    def test_pending_to_rejected_admin(self, content_pending, admin_user):
        """Un admin peut rejeter un contenu (pending -> rejected)"""
        content_pending.transition_to("rejected", user=admin_user)
        content_pending.refresh_from_db()
        assert content_pending.status == "rejected"
        assert content_pending.modified_by == admin_user
    
    def test_pending_to_rejected_contributor_forbidden(self, content_pending, contributor_user):
        """Un contributor ne peut pas rejeter"""
        with pytest.raises(ValidationError, match="Seuls les Editors et Admins"):
            content_pending.transition_to("rejected", user=contributor_user)
    
    def test_published_to_archived_admin(self, content_published, admin_user):
        """Un admin peut archiver un contenu (published -> archived)"""
        content_published.transition_to("archived", user=admin_user)
        content_published.refresh_from_db()
        assert content_published.status == "archived"
        assert content_published.modified_by == admin_user
    
    def test_published_to_archived_editor_forbidden(self, content_published, editor_user):
        """Un editor ne peut pas archiver (seuls les admins)"""
        with pytest.raises(ValidationError, match="Seuls les Admins"):
            content_published.transition_to("archived", user=editor_user)
    
    def test_rejected_to_draft(self, db, contributor_user):
        """Un contenu rejeté peut retourner en draft"""
        content = EducationalContent.objects.create(
            title='Rejected Content',
            slug='rejected-content',
            type='article',
            status='rejected',
            description='Description rejected',
            author=contributor_user,
        )
        content.transition_to("draft", user=contributor_user)
        content.refresh_from_db()
        assert content.status == "draft"
    
    def test_rejected_to_pending(self, db, contributor_user):
        """Un contenu rejeté peut retourner en pending"""
        content = EducationalContent.objects.create(
            title='Rejected Content',
            slug='rejected-content-2',
            type='article',
            status='rejected',
            description='Description rejected',
            author=contributor_user,
        )
        content.transition_to("pending", user=contributor_user)
        content.refresh_from_db()
        assert content.status == "pending"
    
    def test_archived_no_transition(self, db, admin_user):
        """Un contenu archivé ne peut pas changer de statut (terminal)"""
        content = EducationalContent.objects.create(
            title='Archived Content',
            slug='archived-content',
            type='article',
            status='archived',
            description='Description archived',
            author=admin_user,
        )
        with pytest.raises(ValidationError, match="Transition non autorisée"):
            content.transition_to("published", user=admin_user)
    
    def test_draft_to_published_forbidden(self, content_draft, admin_user):
        """draft -> published est interdit (doit passer par pending)"""
        with pytest.raises(ValidationError, match="Transition non autorisée"):
            content_draft.transition_to("published", user=admin_user)
    
    def test_published_to_pending_forbidden(self, content_published, admin_user):
        """published -> pending est interdit"""
        with pytest.raises(ValidationError, match="Transition non autorisée"):
            content_published.transition_to("pending", user=admin_user)
    
    def test_pending_to_draft_forbidden(self, content_pending, contributor_user):
        """pending -> draft est interdit (doit être rejeté d'abord)"""
        with pytest.raises(ValidationError, match="Transition non autorisée"):
            content_pending.transition_to("draft", user=contributor_user)
    
    def test_can_transition_to_valid(self, content_draft, contributor_user):
        """can_transition_to retourne True pour une transition valide"""
        can, msg = content_draft.can_transition_to("pending", user=contributor_user)
        assert can is True
        assert msg == ""
    
    def test_can_transition_to_invalid(self, content_draft):
        """can_transition_to retourne False pour une transition invalide"""
        can, msg = content_draft.can_transition_to("published")
        assert can is False
        assert "Transition non autorisée" in msg
    
    def test_transition_tracks_published_by(self, content_pending, admin_user):
        """La transition vers published enregistre published_by et published_at"""
        assert content_pending.published_by is None
        assert content_pending.published_at is None
        
        content_pending.transition_to("published", user=admin_user)
        content_pending.refresh_from_db()
        
        assert content_pending.published_by == admin_user
        assert content_pending.published_at is not None
    
    def test_transition_tracks_modified_by(self, content_draft, contributor_user):
        """La transition enregistre modified_by"""
        assert content_draft.modified_by is None
        
        content_draft.transition_to("pending", user=contributor_user)
        content_draft.refresh_from_db()
        
        assert content_draft.modified_by == contributor_user

