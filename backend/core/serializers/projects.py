"""
Sérialiseurs pour les projets et médias associés.
"""

from rest_framework import serializers

from core.models import Media, Projet


class ProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = "__all__"


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ("id", "fichier", "description", "projet")

