from rest_framework import serializers
from core.models import EducationalContent, ContentLike, ContentComment
from core.security.sanitization import sanitize_string


class EducationalContentSerializer(serializers.ModelSerializer):
    """
    Serializer pour EducationalContent avec sanitization XSS.
    
    Sanitize automatiquement title et description pour prévenir les attaques XSS.
    """
    
    def validate_title(self, value):
        """Sanitize le titre pour prévenir XSS"""
        if value:
            return sanitize_string(value, max_length=255, allow_html=False)
        return value
    
    def validate_description(self, value):
        """Sanitize la description pour prévenir XSS"""
        if value:
            # Si HTML est autorisé dans le futur, utiliser allow_html=True avec bleach
            # Pour l'instant, on échappe tout le HTML
            return sanitize_string(value, allow_html=False)
        return value
    
    class Meta:
        model = EducationalContent
        fields = [
            "id",
            "title",
            "slug",
            "type",
            "status",
            "description",
            "external_url",
            "file",
            "created_at",
            "likes_count",
            "comments_count",
        ]
        read_only_fields = ("status", "created_at", "likes_count", "comments_count")


class ContentCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentComment
        fields = [
            "id",
            "text",
            "display_name",
            "created_at",
        ]
        read_only_fields = ("created_at",)


class ContentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentLike
        fields = [
            "id",
            "content",
            "created_at",
        ]
        read_only_fields = ("created_at",)


# -------------------------------------------------------------------
# Compatibilité avec l'ancien code : alias vers les nouveaux serializers
# -------------------------------------------------------------------


class ContenuEducatifSerializer(EducationalContentSerializer):
    class Meta(EducationalContentSerializer.Meta):
        pass


class CommentaireSerializer(ContentCommentSerializer):
    class Meta(ContentCommentSerializer.Meta):
        pass


class LikeSerializer(ContentLikeSerializer):
    class Meta(ContentLikeSerializer.Meta):
        pass





