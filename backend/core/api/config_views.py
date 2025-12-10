"""
API endpoint pour récupérer la configuration des feature flags.
Permet au frontend de savoir quelles fonctionnalités sont activées.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings


class FeaturesConfigView(APIView):
    """
    Endpoint pour récupérer la configuration des features (V1.6/V2.0).
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        Retourne la configuration des features activées.
        """
        return Response({
            'investment_enabled': settings.ENABLE_INVESTMENT_FEATURES,
            'commission_rate': settings.EGOEJO_COMMISSION_RATE,
            'stripe_fee_estimate': settings.STRIPE_FEE_ESTIMATE,
            'founder_group_name': settings.FOUNDER_GROUP_NAME,
        })

