"""
Sérialiseurs pour les cagnottes et contributions.
"""

from rest_framework import serializers

from core.models import Cagnotte, Contribution

from .accounts import UserSummarySerializer


class CagnotteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cagnotte
        fields = "__all__"


class ContributionSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = Contribution
        fields = "__all__"
        read_only_fields = ("created_at",)

