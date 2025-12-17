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
        Retourne la configuration des features activées (V1.6/V2.0/V2.1 SAKA).
        """
        return Response({
            'investment_enabled': settings.ENABLE_INVESTMENT_FEATURES,
            'commission_rate': settings.EGOEJO_COMMISSION_RATE,
            'stripe_fee_estimate': settings.STRIPE_FEE_ESTIMATE,
            'founder_group_name': settings.FOUNDER_GROUP_NAME,
            # SAKA Protocol (V2.1) - Flag principal
            'saka_enabled': getattr(settings, 'ENABLE_SAKA', False),
            # Phase 2 SAKA (V2.1)
            'saka_vote_enabled': getattr(settings, 'SAKA_VOTE_ENABLED', False),
            'saka_project_boost_enabled': getattr(settings, 'SAKA_PROJECT_BOOST_ENABLED', False),
            # Phase 3 SAKA
            'saka_compost_enabled': getattr(settings, 'SAKA_COMPOST_ENABLED', False),
        })

