from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from core.serializers.accounts import RegisterSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    """
    Endpoint pour l'inscription d'un nouvel utilisateur.
    Accessible à tous (AllowAny).
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class CurrentUserView(APIView):
    """
    Endpoint pour récupérer les infos de l'utilisateur connecté (via Token).
    Nécessite d'être authentifié.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)