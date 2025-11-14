from rest_framework import serializers
from .models import Projet, Cagnotte, Contribution, Intent

class ProjetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projet
        fields = '__all__'

class CagnotteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cagnotte
        fields = '__all__'

class ContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        fields = '__all__'

class IntentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intent
        fields = '__all__'
        read_only_fields = ['ip', 'user_agent', 'created_at']