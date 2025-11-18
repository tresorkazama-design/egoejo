"""
Sérialiseurs pour les contenus éducatifs, likes et commentaires.
"""

from rest_framework import serializers

from core.models import ContenuEducatif, Like, Commentaire


class ContenuEducatifSerializer(serializers.ModelSerializer):
    """Serializer pour les contenus éducatifs."""
    
    type_contenu_display = serializers.CharField(source='get_type_contenu_display', read_only=True)
    auteur_username = serializers.CharField(source='auteur.username', read_only=True, allow_null=True)
    likes_count = serializers.SerializerMethodField()
    commentaires_count = serializers.SerializerMethodField()
    user_has_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = ContenuEducatif
        fields = (
            'id',
            'titre',
            'description',
            'type_contenu',
            'type_contenu_display',
            'fichier',
            'auteur',
            'auteur_username',
            'is_validated',
            'likes_count',
            'commentaires_count',
            'user_has_liked',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('auteur', 'created_at', 'updated_at')
    
    def get_likes_count(self, obj):
        """Retourne le nombre de likes."""
        return obj.likes.count()
    
    def get_commentaires_count(self, obj):
        """Retourne le nombre de commentaires validés."""
        return obj.commentaires.filter(is_validated=True).count()
    
    def get_user_has_liked(self, obj):
        """Vérifie si l'utilisateur actuel a liké ce contenu."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def create(self, validated_data):
        """Assigne automatiquement l'auteur lors de la création."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['auteur'] = request.user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    """Serializer pour les likes."""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Like
        fields = ('id', 'contenu', 'user', 'user_username', 'created_at')
        read_only_fields = ('user', 'created_at')
    
    def create(self, validated_data):
        """Assigne automatiquement l'utilisateur lors de la création."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)


class CommentaireSerializer(serializers.ModelSerializer):
    """Serializer pour les commentaires."""
    
    user_username = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    
    class Meta:
        model = Commentaire
        fields = (
            'id',
            'contenu',
            'user',
            'user_username',
            'texte',
            'is_validated',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('user', 'is_validated', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        """Assigne automatiquement l'utilisateur lors de la création."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        return super().create(validated_data)

