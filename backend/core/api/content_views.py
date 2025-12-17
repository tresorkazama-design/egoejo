from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache

from core.models import EducationalContent
from core.serializers import EducationalContentSerializer
from core.services.saka import harvest_saka, SakaReason


class EducationalContentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    ViewSet pour gérer les contenus éducatifs (podcasts, vidéos, PDF, articles, etc.).
    
    Endpoints disponibles :
    - GET  /api/contents/                  : Liste des contenus (filtrable par status)
    - GET  /api/contents/{id}/             : Détail d'un contenu
    - POST /api/contents/                  : Proposer un nouveau contenu (status=pending)
    - POST /api/contents/{id}/publish/     : Publier un contenu (status=published)
    - POST /api/contents/{id}/mark-consumed/ : Marquer un contenu comme consommé (récolte SAKA)
    
    Permissions : AllowAny (public)
    
    Note : Les contenus publiés sont mis en cache pendant 10 minutes pour améliorer les performances.
    """

    serializer_class = EducationalContentSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Liste les contenus éducatifs disponibles.
        
        Méthode : GET
        URL : /api/contents/
        Permissions : AllowAny (public)
        
        Query params :
          - status (str, optionnel) : Filtre par statut
            * "published" : Contenus publiés (par défaut, mis en cache 10 min)
            * "pending" : Contenus en attente de validation
            * "draft" : Brouillons
            * "rejected" : Contenus rejetés
        
        Réponse :
          - 200 OK : Liste de contenus éducatifs
            [
              {
                "id": int,
                "title": str,
                "slug": str,
                "type": str,  # "podcast", "video", "pdf", "article", "poeme", "chanson", "autre"
                "status": str,  # "draft", "pending", "published", "rejected"
                "category": str,  # "ressources", "guides", "videos", "racines-philosophie", "autres"
                "description": str,
                "content": str,
                "tags": list,
                "author": int | null,
                "file": str | null,  # URL du fichier si uploadé
                "audio_file": str | null,  # URL de l'audio généré automatiquement
                "created_at": str,  # ISO 8601
                "updated_at": str,  # ISO 8601
                ...
              },
              ...
            ]
        
        Cache : Les contenus publiés sont mis en cache Redis pendant 10 minutes.
        """
        status_param = request.query_params.get("status", "published")
        
        # Cache uniquement pour les contenus publiés
        if status_param == "published":
            cache_key = 'educational_contents_published'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                queryset = self.get_queryset().filter(status="published")
                serializer = self.get_serializer(queryset, many=True)
                cached_data = serializer.data
                # Mettre en cache pour 10 minutes
                cache.set(cache_key, cached_data, 600)
            
            return Response(cached_data)
        
        # Pas de cache pour les autres statuts
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        """
        Retourne le queryset des contenus éducatifs, filtré par status si fourni.
        
        Tri : Par date de création décroissante (plus récents en premier).
        """
        qs = EducationalContent.objects.all().order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        """
        Crée un nouveau contenu éducatif.
        
        Méthode : POST
        URL : /api/contents/
        Permissions : AllowAny (public, mais l'auteur sera null si non authentifié)
        
        Body JSON (requis) :
          {
            "title": str,  # Titre du contenu
            "slug": str,  # Slug unique (généré automatiquement si non fourni)
            "type": str,  # "podcast", "video", "pdf", "article", "poeme", "chanson", "autre"
            "category": str,  # "ressources", "guides", "videos", "racines-philosophie", "autres"
            "description": str,  # Description courte
            "content": str,  # Contenu complet (markdown supporté)
            "tags": list,  # Liste de tags
            "file": file,  # Fichier uploadé (optionnel, PDF, audio, vidéo, image)
            ...
          }
        
        Comportement :
          - Le contenu est créé avec status="pending" (en attente de validation)
          - L'auteur est défini si l'utilisateur est authentifié, sinon null
          - Si un fichier est uploadé :
            * Scan antivirus asynchrone (Celery)
            * Validation du type MIME (PDF, audio, vidéo, image)
          - Génération d'embedding en arrière-plan pour la recherche sémantique
          - Invalidation du cache des contenus publiés
        
        Réponse :
          - 201 Created : Contenu créé avec les données complètes
          - 400 Bad Request : Erreur de validation
        
        Note : Le contenu doit être validé par un admin via l'endpoint /publish/ avant d'être visible publiquement.
        """
        author = self.request.user if self.request.user.is_authenticated else None
        content = serializer.save(
            author=author,
            status="pending",  # les contenus proposés vont en "en attente"
        )
        
        # Scanner le fichier si uploadé (tâche asynchrone)
        if content.file:
            try:
                from core.tasks_security import scan_file_antivirus, validate_file_type
                scan_file_antivirus.delay(content.file.name)
                # Valider le type MIME
                allowed_types = ['application/pdf', 'audio/', 'video/', 'image/']
                validate_file_type.delay(content.file.name, allowed_types)
            except Exception:
                # Ignorer si Celery non disponible
                pass
        
        # Générer embedding en arrière-plan (tâche asynchrone)
        try:
            from core.tasks_embeddings import generate_embedding_task
            # Utiliser Sentence Transformers par défaut (gratuit)
            generate_embedding_task.delay('sentence-transformers', content.id, 'educational_content')
        except Exception:
            # Ignorer si Celery non disponible
            pass
        
        # Invalider le cache (au cas où un admin publierait directement)
        cache.delete('educational_contents_published')

    @action(detail=True, methods=["post"], url_path="mark-consumed")
    def mark_consumed(self, request, pk=None):
        """
        Marque un contenu comme consommé et déclenche la récolte SAKA.
        
        Méthode : POST
        URL : /api/contents/{id}/mark-consumed/
        Permissions : IsAuthenticated (requis)
        
        Body JSON (optionnel) :
          {
            "progress": int  // Pourcentage de consommation (0-100), défaut: 100
          }
        
        Comportement :
          - Si progress >= 80% (seuil de consommation) :
            * Le contenu est considéré comme "lu/écouté"
            * Récolte de grains SAKA (Knowledge Mining) pour l'utilisateur
            * Raison SAKA : CONTENT_READ
          - Si progress < 80% :
            * Retourne une erreur 400 avec message explicatif
        
        Réponse (succès) :
          - 200 OK :
            {
              "ok": true,
              "message": "Contenu marqué comme consommé. Grains SAKA récoltés.",
              "content_id": int,
              "progress": int
            }
        
        Réponse (échec) :
          - 400 Bad Request :
            {
              "ok": false,
              "message": "Progression insuffisante (X% < 80%)",
              "progress": int
            }
          - 401 Unauthorized : Si l'utilisateur n'est pas authentifié
        
        Note : Cette action fait partie du système SAKA (Phase 1) pour récompenser l'engagement
        dans la consommation de contenu éducatif.
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentification requise'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        content = self.get_object()
        progress = request.data.get('progress', 100)
        
        # Seuil de consommation (ex: 80% pour considérer comme "lu/écouté")
        CONSUMPTION_THRESHOLD = 80
        
        if progress >= CONSUMPTION_THRESHOLD:
            # Récolter des grains SAKA (Knowledge Mining)
            harvest_saka(
                user=request.user,
                reason=SakaReason.CONTENT_READ,
                metadata={'content_id': content.id, 'progress': progress}
            )
            
            return Response({
                'ok': True,
                'message': 'Contenu marqué comme consommé. Grains SAKA récoltés.',
                'content_id': content.id,
                'progress': progress,
            })
        else:
            return Response({
                'ok': False,
                'message': f'Progression insuffisante ({progress}% < {CONSUMPTION_THRESHOLD}%)',
                'progress': progress,
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        """
        Publie un contenu (change le status de "pending" à "published").
        
        Méthode : POST
        URL : /api/contents/{id}/publish/
        Permissions : AllowAny (mais généralement utilisé par les admins)
        
        Body JSON : Aucun requis
        
        Comportement :
          - Change le status du contenu à "published"
          - Génère automatiquement l'audio du contenu en arrière-plan (TTS)
            * Utilise le provider configuré (OpenAI par défaut, ou ElevenLabs)
            * Vérifie le hash pour éviter les régénérations inutiles
          - Invalide le cache des contenus publiés
        
        Réponse :
          - 200 OK : Contenu publié avec les données complètes
          - 404 Not Found : Si le contenu n'existe pas
        
        Note : 
          - Généralement appelé par un admin après validation du contenu
          - La génération d'audio est asynchrone (Celery) et peut prendre quelques minutes
          - Le contenu devient visible publiquement après publication
        """
        content = self.get_object()
        content.status = "published"
        content.save(update_fields=["status", "updated_at"])
        
        # Générer l'audio automatiquement lors de la publication (tâche asynchrone)
        # CORRECTION Chantier 2 : Hash-based caching - vérifie le hash avant génération
        try:
            from core.tasks_audio import generate_audio_content
            import os
            # Utiliser OpenAI par défaut (ou ElevenLabs si configuré)
            provider = os.environ.get('TTS_PROVIDER', 'openai')
            voice = os.environ.get('TTS_VOICE', 'alloy')
            # La tâche generate_audio_content vérifie déjà le hash (audio_source_hash)
            # et skip si identique (évite régénération payante)
            generate_audio_content.delay(content.id, provider, voice)
        except Exception:
            # Ignorer si Celery non disponible
            pass
        
        # Invalider le cache
        cache.delete('educational_contents_published')
        
        serializer = self.get_serializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)



