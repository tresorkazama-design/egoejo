"""
Endpoints REST pour la gestion des contenus éducatifs.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound

from core.models import ContenuEducatif, Like, Commentaire
from core.serializers import (
    ContenuEducatifSerializer,
    LikeSerializer,
    CommentaireSerializer,
)


class ContenuEducatifViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des contenus éducatifs."""
    
    serializer_class = ContenuEducatifSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Retourne uniquement les contenus validés pour les utilisateurs non authentifiés."""
        queryset = ContenuEducatif.objects.select_related('auteur').prefetch_related(
            'likes', 'commentaires'
        ).order_by('-created_at')
        
        # Filtrer par type de contenu si spécifié
        type_contenu = self.request.query_params.get('type')
        if type_contenu:
            queryset = queryset.filter(type_contenu=type_contenu)
        
        # Filtrer par validation si l'utilisateur n'est pas admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_validated=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Assigne automatiquement l'auteur lors de la création."""
        serializer.save(auteur=self.request.user)
    
    def perform_update(self, serializer):
        """Seul l'auteur ou un admin peut modifier un contenu."""
        contenu = serializer.instance
        if contenu.auteur != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas la permission de modifier ce contenu.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Seul l'auteur ou un admin peut supprimer un contenu."""
        if instance.auteur != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas la permission de supprimer ce contenu.")
        instance.delete()
    
    @action(detail=True, methods=['post', 'delete'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Ajouter ou retirer un like sur un contenu."""
        contenu = self.get_object()
        
        if request.method == 'POST':
            # Ajouter un like
            like, created = Like.objects.get_or_create(
                contenu=contenu,
                user=request.user
            )
            if not created:
                return Response(
                    {'detail': 'Vous avez déjà liké ce contenu.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = LikeSerializer(like, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            # Retirer un like
            try:
                like = Like.objects.get(contenu=contenu, user=request.user)
                like.delete()
                return Response({'detail': 'Like retiré.'}, status=status.HTTP_200_OK)
            except Like.DoesNotExist:
                return Response(
                    {'detail': 'Vous n\'avez pas liké ce contenu.'},
                    status=status.HTTP_404_NOT_FOUND
                )
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def commentaires(self, request, pk=None):
        """Récupérer les commentaires validés d'un contenu."""
        contenu = self.get_object()
        commentaires = contenu.commentaires.filter(is_validated=True).select_related('user')
        
        # Si l'utilisateur est admin, on peut voir tous les commentaires
        if request.user.is_staff:
            commentaires = contenu.commentaires.all().select_related('user')
        
        serializer = CommentaireSerializer(commentaires, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def commenter(self, request, pk=None):
        """Ajouter un commentaire sur un contenu."""
        contenu = self.get_object()
        
        serializer = CommentaireSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(contenu=contenu, user=request.user)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentaireViewSet(viewsets.ModelViewSet):
    """ViewSet pour la gestion des commentaires."""
    
    serializer_class = CommentaireSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Retourne uniquement les commentaires validés pour les utilisateurs non authentifiés."""
        queryset = Commentaire.objects.select_related('user', 'contenu').order_by('-created_at')
        
        # Filtrer par contenu si spécifié
        contenu_id = self.request.query_params.get('contenu')
        if contenu_id:
            queryset = queryset.filter(contenu_id=contenu_id)
        
        # Filtrer par validation si l'utilisateur n'est pas admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_validated=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Assigne automatiquement l'utilisateur lors de la création."""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Seul l'auteur ou un admin peut modifier un commentaire."""
        commentaire = serializer.instance
        if commentaire.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas la permission de modifier ce commentaire.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Seul l'auteur ou un admin peut supprimer un commentaire."""
        if instance.user != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Vous n'avez pas la permission de supprimer ce commentaire.")
        instance.delete()

