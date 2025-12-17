from rest_framework import mixins, viewsets, permissions
from rest_framework.response import Response

from core.models import Engagement
from core.serializers import EngagementSerializer


class EngagementViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet pour gérer les engagements d'aide (offres d'aide déposées par les membres).
    
    Endpoints disponibles :
    - GET  /api/engagements/               : Liste tous les engagements
    - POST /api/engagements/               : Créer un nouvel engagement
    
    Permissions : AllowAny (public)
    
    Note : Correspond au formulaire "Je veux aider" côté frontend.
    Les engagements peuvent être liés à une demande d'aide spécifique (HelpRequest)
    ou être des offres générales.
    """

    serializer_class = EngagementSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Liste les engagements d'aide disponibles.
        
        Méthode : GET
        URL : /api/engagements/
        Permissions : AllowAny (public)
        
        Query params :
          - help_request (int, optionnel) : ID d'une demande d'aide (HelpRequest)
            Filtre les engagements liés à cette demande spécifique.
            Exemple : /api/engagements/?help_request=123
        
        Réponse :
          - 200 OK : Liste d'engagements
            [
              {
                "id": int,
                "user": int | null,  # ID utilisateur si authentifié, sinon null
                "help_request": int | null,  # ID demande d'aide si lié
                "help_types": list,  # Liste des types d'aide
                "domains": list,  # Domaines d'expertise
                "availability": str,  # Disponibilité
                "scope": str,  # "local", "international", "both"
                "anonymity": str,  # "pseudo", "team_only"
                "status": str,  # "new", "in_review", "active", "archived"
                "notes": str,  # Notes additionnelles
                "created_at": str,  # ISO 8601
                "updated_at": str,  # ISO 8601
                ...
              },
              ...
            ]
        
        Tri : Par date de création décroissante (plus récents en premier).
        """
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Retourne le queryset des engagements, filtré par help_request si fourni.
        
        Tri : Par date de création décroissante (plus récents en premier).
        
        Query params supportés :
          - help_request (int, optionnel) : ID d'une demande d'aide (HelpRequest)
            Filtre les engagements liés à cette demande spécifique.
        """
        qs = Engagement.objects.all().order_by("-created_at")

        help_request_id = self.request.query_params.get("help_request")
        if help_request_id:
            qs = qs.filter(help_request_id=help_request_id)

        return qs

    def perform_create(self, serializer):
        """
        Crée un nouvel engagement d'aide.
        
        Méthode : POST
        URL : /api/engagements/
        Permissions : AllowAny (public, mais l'utilisateur sera null si non authentifié)
        
        Body JSON (requis) :
          {
            "help_request": int | null,  # ID demande d'aide si lié, sinon null
            "help_types": list,  # Liste des types d'aide ["financier", "temps", "competences", "materiel"]
            "domains": list,  # Domaines d'expertise
            "availability": str,  # Disponibilité
            "scope": str,  # "local", "international", "both"
            "anonymity": str,  # "pseudo", "team_only"
            "notes": str,  # Notes additionnelles
            ...
          }
        
        Comportement :
          - L'engagement est créé avec status="new" (nouvel engagement)
          - L'utilisateur est défini si authentifié, sinon null
          - Peut être lié à une demande d'aide spécifique (help_request)
        
        Réponse :
          - 201 Created : Engagement créé avec les données complètes
          - 400 Bad Request : Erreur de validation
        
        Note : 
          - Les engagements sont visibles selon les règles d'anonymité définies
          - L'équipe EGOEJO peut voir tous les engagements pour les matcher avec les besoins
        """
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user, status="new")


