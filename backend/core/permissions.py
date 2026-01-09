"""
Permissions personnalisées pour EGOEJO.
"""
from rest_framework import permissions
from django.conf import settings


class IsInvestmentFeatureEnabled(permissions.BasePermission):
    """
    Pare-feu absolu : Si la feature est False dans les settings,
    l'API renvoie 403 (Forbidden) pour cacher l'existence de l'endpoint.
    
    Utilisation : Appliquer cette permission sur toutes les vues investment
    pour bloquer l'accès si ENABLE_INVESTMENT_FEATURES = False.
    """
    message = "Cette fonctionnalité n'est pas disponible."

    def has_permission(self, request, view):
        """
        Vérifie si la feature investment est activée.
        Si False, retourne False (403 Forbidden).
        """
        if not settings.ENABLE_INVESTMENT_FEATURES:
            return False  # Renvoie 403 Forbidden
        return True


class IsFounderOrReadOnly(permissions.BasePermission):
    """
    Permission pour les fondateurs (groupe Founders_V1_Protection).
    Les fondateurs ont tous les droits, les autres sont en lecture seule.
    """
    message = "Vous devez être fondateur pour effectuer cette action."

    def has_permission(self, request, view):
        # Lecture autorisée pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Écriture réservée aux fondateurs
        if request.user.is_authenticated:
            return request.user.groups.filter(name=settings.FOUNDER_GROUP_NAME).exists()
        
        return False


# ==============================================
# PERMISSIONS CMS - GESTION DE CONTENU
# ==============================================

# Noms des groupes Django pour les rôles CMS
CONTENT_EDITOR_GROUP_NAME = 'Content_Editors'
CONTENT_CONTRIBUTOR_GROUP_NAME = 'Content_Contributors'
CONTENT_REVIEWER_GROUP_NAME = 'Content_Reviewers'


def is_user_in_group(user, group_name):
    """
    Vérifie si un utilisateur appartient à un groupe Django.
    
    Args:
        user: Utilisateur Django
        group_name: Nom du groupe
    
    Returns:
        bool: True si l'utilisateur est dans le groupe
    """
    if not user or not user.is_authenticated:
        return False
    return user.groups.filter(name=group_name).exists()


def is_content_admin(user):
    """
    Vérifie si un utilisateur est admin (superuser ou staff).
    
    Args:
        user: Utilisateur Django
    
    Returns:
        bool: True si l'utilisateur est admin
    """
    if not user or not user.is_authenticated:
        return False
    return user.is_superuser or user.is_staff


def is_content_editor(user):
    """
    Vérifie si un utilisateur est editor (admin ou groupe Content_Editors).
    
    Args:
        user: Utilisateur Django
    
    Returns:
        bool: True si l'utilisateur est editor
    """
    if is_content_admin(user):
        return True
    return is_user_in_group(user, CONTENT_EDITOR_GROUP_NAME)


def is_content_contributor(user):
    """
    Vérifie si un utilisateur est contributor (admin, editor, ou groupe Content_Contributors).
    
    Args:
        user: Utilisateur Django
    
    Returns:
        bool: True si l'utilisateur est contributor
    """
    if is_content_editor(user):
        return True
    return is_user_in_group(user, CONTENT_CONTRIBUTOR_GROUP_NAME)


class CanPublishContent(permissions.BasePermission):
    """
    Permission pour publier un contenu.
    
    Autorisé :
    - Admin (superuser ou staff)
    
    Refusé :
    - Contributor
    - Utilisateur anonyme
    """
    message = "Vous devez être admin pour publier un contenu."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return is_content_admin(request.user)

    def has_object_permission(self, request, view, obj):
        """
        Vérifie les permissions au niveau de l'objet.
        Par défaut, utilise has_permission.
        """
        return self.has_permission(request, view)


class CanRejectContent(permissions.BasePermission):
    """
    Permission pour rejeter un contenu.
    
    Autorisé :
    - Admin (superuser ou staff)
    - Editor (groupe Content_Editors)
    
    Refusé :
    - Contributor
    - Utilisateur anonyme
    """
    message = "Vous devez être admin ou editor pour rejeter un contenu."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return is_content_editor(request.user)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CanArchiveContent(permissions.BasePermission):
    """
    Permission pour archiver un contenu.
    
    Autorisé :
    - Admin (superuser ou staff)
    
    Refusé :
    - Contributor
    - Utilisateur anonyme
    """
    message = "Vous devez être admin pour archiver un contenu."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return is_content_admin(request.user)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CanUnpublishContent(permissions.BasePermission):
    """
    Permission pour dépublication (unpublish) d'un contenu.
    
    Autorisé :
    - Admin (superuser ou staff)
    - Editor (groupe Content_Editors)
    
    Refusé :
    - Contributor
    - Utilisateur anonyme
    """
    message = "Vous devez être admin ou editor pour dépublication un contenu."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return is_content_editor(request.user)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class CanCreateContent(permissions.BasePermission):
    """
    Permission pour créer un contenu.
    
    Autorisé :
    - Admin (superuser ou staff)
    - Editor (groupe Content_Editors)
    - Contributor (groupe Content_Contributors)
    - Utilisateur authentifié (peut proposer un contenu)
    
    Refusé :
    - Utilisateur anonyme → 401 Unauthorized (pas de token)
    """
    message = "Vous devez être authentifié pour créer un contenu."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # Lecture autorisée pour tous
            return True
        # Création nécessite authentification stricte
        if not request.user or not request.user.is_authenticated:
            return False  # DRF retournera 403, mais le code dans perform_create retourne 401
        return True

    def has_object_permission(self, request, view, obj):
        # Un contributor peut modifier seulement ses propres contenus en draft/pending
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if is_content_editor(request.user):
            # Editor peut modifier tous les contenus
            return True
        
        if is_content_contributor(request.user):
            # Contributor peut modifier seulement ses propres contenus en draft/pending
            if obj.author != request.user:
                return False
            if obj.status not in ['draft', 'pending']:
                return False
            return True
        
        return False
