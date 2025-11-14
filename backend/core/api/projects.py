"""
Endpoints REST pour la gestion des projets.
"""

from rest_framework import generics, permissions

from core.models import Projet
from core.serializers import ProjetSerializer


class ProjetListCreate(generics.ListCreateAPIView):
    queryset = Projet.objects.all().order_by("-created_at")
    serializer_class = ProjetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

