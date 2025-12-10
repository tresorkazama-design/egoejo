from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache

from core.models import EducationalContent
from core.serializers import EducationalContentSerializer


class EducationalContentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """
    - GET  /api/contents/                  : liste des contenus (filtrable par status)
      * ?status=published                  : contenus publiés
      * ?status=pending                    : contenus en attente
    - GET  /api/contents/{id}/             : détail
    - POST /api/contents/                  : proposer un contenu (status=pending)
    - POST /api/contents/{id}/publish/     : publier un contenu (status=published)
    """

    serializer_class = EducationalContentSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Liste des contenus avec cache pour les contenus publiés
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
        qs = EducationalContent.objects.all().order_by("-created_at")
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
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

    @action(detail=True, methods=["post"], url_path="publish")
    def publish(self, request, pk=None):
        """
        Passe ce contenu en 'published'.
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



