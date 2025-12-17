"""
Sérialiseurs pour les projets et médias associés.
"""

from rest_framework import serializers

from core.models import Media, Projet
from core.models.impact import ProjectImpact4P


class ProjectImpact4PSerializer(serializers.ModelSerializer):
    """
    Serializer dédié pour les scores 4P d'un projet.
    Structure uniformisée avec les noms p1_financier, p2_saka, p3_social, p4_sens.
    """
    p1_financier = serializers.DecimalField(
        source='financial_score',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    p2_saka = serializers.IntegerField(
        source='saka_score',
        read_only=True
    )
    p3_social = serializers.IntegerField(
        source='social_score',
        read_only=True
    )
    p4_sens = serializers.IntegerField(
        source='purpose_score',
        read_only=True
    )
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = ProjectImpact4P
        fields = ['p1_financier', 'p2_saka', 'p3_social', 'p4_sens', 'updated_at']


class ProjetSerializer(serializers.ModelSerializer):
    """
    Serializer pour les projets avec support du score 4P.
    Expose impact_4p avec une structure uniformisée.
    """
    impact_4p = serializers.SerializerMethodField()
    
    class Meta:
        model = Projet
        fields = "__all__"
    
    def get_impact_4p(self, obj):
        """
        Retourne les scores 4P du projet, ou des valeurs par défaut si non calculés.
        Structure uniformisée : p1_financier, p2_saka, p3_social, p4_sens.
        """
        try:
            impact_4p = obj.impact_4p
            return {
                "p1_financier": float(impact_4p.financial_score),
                "p2_saka": impact_4p.saka_score,
                "p3_social": impact_4p.social_score,
                "p4_sens": impact_4p.purpose_score,
                "updated_at": impact_4p.updated_at.isoformat() if impact_4p.updated_at else None,
            }
        except ProjectImpact4P.DoesNotExist:
            # Retourner des valeurs par défaut si le 4P n'a pas encore été calculé
            return {
                "p1_financier": 0.0,
                "p2_saka": 0,
                "p3_social": 0,
                "p4_sens": 0,
                "updated_at": None,
            }


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ("id", "fichier", "description", "projet")

