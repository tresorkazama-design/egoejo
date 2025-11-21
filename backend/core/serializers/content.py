from rest_framework import serializers
from core.models import EducationalContent, ContentLike, ContentComment


class EducationalContentSerializer(serializers.ModelSerializer):
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





