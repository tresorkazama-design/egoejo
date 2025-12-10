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

