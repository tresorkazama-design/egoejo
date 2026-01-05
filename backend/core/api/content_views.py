from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.cache import cache
from django.core.exceptions import ValidationError

from core.models import EducationalContent
from core.serializers import EducationalContentSerializer
from core.services.saka import harvest_saka, SakaReason
from core.permissions import (
    CanPublishContent,
    CanRejectContent,
    CanArchiveContent,
    CanUnpublishContent,
    CanCreateContent,
)


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
    - POST /api/contents/                  : Proposer un nouveau contenu (status=pending) - IsAuthenticated
    - POST /api/contents/{id}/publish/     : Publier un contenu (status=published) - CanPublishContent
    - POST /api/contents/{id}/reject/      : Rejeter un contenu (status=rejected) - CanRejectContent
    - POST /api/contents/{id}/archive/    : Archiver un contenu (status=archived) - CanArchiveContent
    - POST /api/contents/{id}/unpublish/   : Dépublication (status=draft) - CanUnpublishContent
    - POST /api/contents/{id}/mark-consumed/ : Marquer un contenu comme consommé (récolte SAKA) - IsAuthenticated
    
    Permissions :
    - Lecture (GET) : AllowAny (public)
    - Création (POST /api/contents/) : IsAuthenticated (contributor, editor, admin)
    - Publication/Rejet/Archivage : CanPublishContent / CanRejectContent / CanArchiveContent (editor, admin uniquement)
    
    Note : Les contenus publiés sont mis en cache pendant 10 minutes pour améliorer les performances.
    """

    serializer_class = EducationalContentSerializer
    permission_classes = [permissions.IsAuthenticated]  # Par défaut sécurisé, surchargé par get_permissions() pour list/retrieve
    
    def get_permissions(self):
        """
        Instancie et retourne la liste des permissions requises pour cette action.
        """
        if self.action in ['list', 'retrieve']:
            # Lecture publique autorisée
            return [permissions.AllowAny()]
        elif self.action == 'create':
            # Création nécessite authentification stricte
            # IsAuthenticated retourne 401 si pas de token, CanCreateContent vérifie les rôles
            return [permissions.IsAuthenticated(), CanCreateContent()]
        elif self.action == 'publish':
            # Publication nécessite editor/admin
            return [permissions.IsAuthenticated(), CanPublishContent()]
        elif self.action == 'reject':
            # Rejet nécessite editor/admin
            return [permissions.IsAuthenticated(), CanRejectContent()]
        elif self.action == 'archive':
            # Archivage nécessite editor/admin
            return [permissions.IsAuthenticated(), CanArchiveContent()]
        elif self.action == 'unpublish':
            # Dépublication nécessite editor/admin
            return [permissions.IsAuthenticated(), CanUnpublishContent()]
        elif self.action == 'mark_consumed':
            # Marquer consommé nécessite authentification
            return [permissions.IsAuthenticated()]
        else:
            # Par défaut, authentification requise
            return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        Liste les contenus éducatifs disponibles avec pagination.
        
        Méthode : GET
        URL : /api/contents/
        Permissions : AllowAny (public)
        
        Query params :
          - status (str, optionnel) : Filtre par statut
            * "published" : Contenus publiés (par défaut, mis en cache 10 min)
            * "pending" : Contenus en attente de validation
            * "draft" : Brouillons
            * "rejected" : Contenus rejetés
          - page (int, optionnel) : Numéro de page (défaut: 1)
          - page_size (int, optionnel) : Nombre d'éléments par page (défaut: 20, max: 100)
        
        Réponse paginée :
          - 200 OK : 
            {
              "count": int,  # Nombre total de résultats
              "next": str | null,  # URL de la page suivante
              "previous": str | null,  # URL de la page précédente
              "results": [
                {
                  "id": int,
                  "title": str,
                  "slug": str,
                  "type": str,
                  "status": str,
                  "category": str,
                  "description": str,
                  ...
                },
                ...
              ]
            }
        
        Cache : Les contenus publiés sont mis en cache Redis pendant 10 minutes (sans pagination pour compatibilité).
        """
        status_param = request.query_params.get("status", "published")
        page = request.query_params.get("page")
        page_size = request.query_params.get("page_size")
        
        # Si pas de pagination demandée et status=published, utiliser le cache (rétrocompatibilité)
        if status_param == "published" and not page and not page_size:
            cache_key = 'educational_contents_published'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                queryset = self.get_queryset().filter(status="published")
                serializer = self.get_serializer(queryset, many=True)
                cached_data = serializer.data
                # Mettre en cache pour 10 minutes
                cache.set(cache_key, cached_data, 600)
            
            return Response(cached_data)
        
        # Utiliser la pagination DRF pour les autres cas (avec pagination)
        # La pagination est gérée automatiquement par DRF via DEFAULT_PAGINATION_CLASS
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
        Permissions : IsAuthenticated (requis via CanCreateContent)
        
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
          - L'auteur est défini si l'utilisateur est authentifié (requis)
          - Si un fichier est uploadé :
            * Scan antivirus asynchrone (Celery)
            * Validation du type MIME (PDF, audio, vidéo, image)
          - Génération d'embedding en arrière-plan pour la recherche sémantique
          - Invalidation du cache des contenus publiés
          - Log l'action dans AuditLog
        
        Réponse :
          - 201 Created : Contenu créé avec les données complètes
          - 400 Bad Request : Erreur de validation
          - 401 Unauthorized : Si l'utilisateur n'est pas authentifié
        
        Note : Le contenu doit être validé par un editor/admin via l'endpoint /publish/ avant d'être visible publiquement.
        """
        if not self.request.user.is_authenticated:
            return Response(
                {'error': 'Authentification requise pour créer un contenu'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        author = self.request.user
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
        
        # Log l'action
        from core.api.common import log_action
        log_action(
            self.request.user,
            "content_create",
            "educational_content",
            content.id,
            {
                "title": content.title,
                "type": content.type,
                "status": content.status,
                "author_id": content.author.id if content.author else None,
            }
        )
        
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
        if not self.request.user.is_authenticated:
            return Response(
                {'error': 'Authentification requise'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        content = self.get_object()
        progress = self.request.data.get('progress', 100)
        
        # Seuil de consommation (ex: 80% pour considérer comme "lu/écouté")
        CONSUMPTION_THRESHOLD = 80
        
        if progress >= CONSUMPTION_THRESHOLD:
            # Récolter des grains SAKA (Knowledge Mining)
            harvest_saka(
                user=self.request.user,
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
        
        BLOQUANT : La publication est refusée si le contenu n'est pas conforme
        à la Constitution éditoriale EGOEJO (aucun contournement possible).
        
        Méthode : POST
        URL : /api/contents/{id}/publish/
        Permissions : IsAuthenticated + CanPublishContent (editor/admin uniquement)
        
        Body JSON (optionnel) :
          {
            "rejection_reason": str  // Raison de publication (optionnel)
          }
        
        Comportement :
          - Vérifie la conformité éditoriale AVANT publication (BLOQUANT)
          - Change le status du contenu à "published" si conforme
          - Génère automatiquement l'audio du contenu en arrière-plan (TTS)
            * Utilise le provider configuré (OpenAI par défaut, ou ElevenLabs)
            * Vérifie le hash pour éviter les régénérations inutiles
          - Invalide le cache des contenus publiés
          - Log l'action dans AuditLog
        
        Réponse :
          - 200 OK : Contenu publié avec les données complètes
          - 400 Bad Request : Si le contenu n'est pas conforme (violations critiques)
          - 403 Forbidden : Si l'utilisateur n'a pas la permission
          - 404 Not Found : Si le contenu n'existe pas
        
        Note : 
          - Généralement appelé par un editor/admin après validation du contenu
          - La génération d'audio est asynchrone (Celery) et peut prendre quelques minutes
          - Le contenu devient visible publiquement après publication
          - AUCUN CONTOURNEMENT POSSIBLE : La compliance est vérifiée systématiquement
        """
        content = self.get_object()
        old_status = content.status
        
        # VÉRIFICATION DE COMPLIANCE ÉDITORIALE (BLOQUANT)
        # Aucun contournement possible - vérification systématique avant publication
        from core.compliance.content_compliance_matrix import ContentComplianceMatrix
        
        # Simuler le statut "published" pour vérifier la compliance
        # (on vérifie AVANT de changer le statut)
        original_status = content.status
        content.status = "published"  # Temporaire pour la vérification
        
        compliance_score = ContentComplianceMatrix.check_content_compliance(content)
        
        # Restaurer le statut original
        content.status = original_status
        content.refresh_from_db()
        
        # Si le contenu n'est pas conforme (échecs critiques), BLOQUER la publication
        if not compliance_score.is_compliant:
            critical_failures = [
                result for result in compliance_score.results
                if not result.passed and result.severity == "critical"
            ]
            
            error_details = []
            for failure in critical_failures:
                error_details.append({
                    'criterion': failure.criterion.value,
                    'message': failure.message,
                    'details': failure.details or {},
                })
            
            return Response(
                {
                    'error': 'PUBLICATION BLOQUÉE : Le contenu n\'est pas conforme à la Constitution éditoriale EGOEJO',
                    'compliance_score': compliance_score.overall_score,
                    'critical_failures': len(critical_failures),
                    'violations': error_details,
                    'message': (
                        f"Le contenu '{content.title}' (ID: {content.id}) ne peut pas être publié car il viole "
                        f"{len(critical_failures)} critère(s) critique(s) de la Constitution éditoriale EGOEJO.\n"
                        "Aucun contournement possible. Corrigez les violations avant de publier."
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Utiliser la méthode transition_to pour valider la transition
        try:
            content.transition_to("published", user=self.request.user)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rafraîchir pour obtenir les valeurs mises à jour (published_by, published_at)
        content.refresh_from_db()
        
        # Log l'action
        from core.api.common import log_action
        log_action(
            self.request.user,
            "content_publish",
            "educational_content",
            content.id,
            {
                "old_status": old_status,
                "new_status": "published",
                "published_by": self.request.user.id,
            }
        )
        
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

    @action(detail=True, methods=["post"], url_path="reject")
    def reject(self, request, pk=None):
        """
        Rejette un contenu (change le status de "pending" à "rejected").
        
        Méthode : POST
        URL : /api/contents/{id}/reject/
        Permissions : IsAuthenticated + CanRejectContent (editor/admin uniquement)
        
        Body JSON (requis) :
          {
            "rejection_reason": str  // Raison du rejet (optionnel mais recommandé)
          }
        
        Comportement :
          - Change le status du contenu à "rejected"
          - Enregistre la raison du rejet (si fournie)
          - Invalide le cache des contenus publiés
          - Log l'action dans AuditLog
        
        Réponse :
          - 200 OK : Contenu rejeté avec les données complètes
          - 403 Forbidden : Si l'utilisateur n'a pas la permission
          - 404 Not Found : Si le contenu n'existe pas
        """
        content = self.get_object()
        old_status = content.status
        rejection_reason = self.request.data.get('rejection_reason', '')
        
        # Utiliser la méthode transition_to pour valider la transition
        try:
            content.transition_to("rejected", user=self.request.user)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log l'action
        from core.api.common import log_action
        log_action(
            self.request.user,
            "content_reject",
            "educational_content",
            content.id,
            {
                "old_status": old_status,
                "new_status": "rejected",
                "rejected_by": self.request.user.id,
                "rejection_reason": rejection_reason,
            }
        )
        
        # Invalider le cache
        cache.delete('educational_contents_published')
        
        serializer = self.get_serializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="archive")
    def archive(self, request, pk=None):
        """
        Archive un contenu (change le status de "published" à "archived").
        
        Méthode : POST
        URL : /api/contents/{id}/archive/
        Permissions : IsAuthenticated + CanArchiveContent (editor/admin uniquement)
        
        Body JSON : Aucun requis
        
        Comportement :
          - Change le status du contenu à "archived"
          - Invalide le cache des contenus publiés
          - Log l'action dans AuditLog
        
        Réponse :
          - 200 OK : Contenu archivé avec les données complètes
          - 403 Forbidden : Si l'utilisateur n'a pas la permission
          - 404 Not Found : Si le contenu n'existe pas
        """
        content = self.get_object()
        old_status = content.status
        
        # Utiliser la méthode transition_to pour valider la transition
        try:
            content.transition_to("archived", user=self.request.user)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log l'action
        from core.api.common import log_action
        log_action(
            self.request.user,
            "content_archive",
            "educational_content",
            content.id,
            {
                "old_status": old_status,
                "new_status": "archived",
                "archived_by": self.request.user.id,
            }
        )
        
        # Invalider le cache
        cache.delete('educational_contents_published')
        
        serializer = self.get_serializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unpublish")
    def unpublish(self, request, pk=None):
        """
        Dépublication d'un contenu (change le status de "published" à "draft").
        
        Méthode : POST
        URL : /api/contents/{id}/unpublish/
        Permissions : IsAuthenticated + CanUnpublishContent (editor/admin uniquement)
        
        Body JSON : Aucun requis
        
        Comportement :
          - Change le status du contenu à "draft"
          - Invalide le cache des contenus publiés
          - Log l'action dans AuditLog
        
        Réponse :
          - 200 OK : Contenu dépublication avec les données complètes
          - 403 Forbidden : Si l'utilisateur n'a pas la permission
          - 404 Not Found : Si le contenu n'existe pas
        """
        content = self.get_object()
        old_status = content.status
        
        # Note : unpublish n'est pas dans les transitions autorisées du workflow V1
        # On permet cette transition pour les admins/editors (rétrocompatibilité)
        # Dans le workflow strict, published -> archived est la seule transition depuis published
        if old_status == "published":
            # Pour unpublish, on passe à draft (transition non standard mais nécessaire)
            content.status = "draft"
            if self.request.user and self.request.user.is_authenticated:
                content.modified_by = self.request.user
            content.save(update_fields=["status", "modified_by", "updated_at"])
        else:
            return Response(
                {'error': f'Impossible de dépublication un contenu avec le statut {old_status}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log l'action
        from core.api.common import log_action
        log_action(
            self.request.user,
            "content_unpublish",
            "educational_content",
            content.id,
            {
                "old_status": old_status,
                "new_status": "draft",
                "unpublished_by": self.request.user.id,
            }
        )
        
        # Invalider le cache
        cache.delete('educational_contents_published')
        
        serializer = self.get_serializer(content)
        return Response(serializer.data, status=status.HTTP_200_OK)



