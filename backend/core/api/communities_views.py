"""
API endpoints pour les Communautés EGOEJO.
V1 : Lecture seule (read-only) pour préparer la subsidiarité.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count
from core.models.communities import Community


@api_view(["GET"])
@permission_classes([AllowAny])
def community_list_view(request):
    """
    GET /api/communities/
    
    Retourne la liste des communautés actives (lecture seule).
    
    Returns:
        list: [
            {
                "id": int,
                "name": str,
                "slug": str,
                "description": str | null,
                "is_active": bool,
                "created_at": "YYYY-MM-DDTHH:MM:SSZ",
                "members_count": int,
                "projects_count": int,
            },
            ...
        ]
    """
    # ÉRADICATION N+1 : Utiliser annotate(Count(...)) au lieu de .count() dans la boucle
    # Cela génère un COUNT SQL directement dans la requête principale
    communities = Community.objects.filter(is_active=True).annotate(
        members_count=Count('members', distinct=True),
        projects_count=Count('projects', distinct=True)
    )
    
    data = []
    for community in communities:
        data.append({
            "id": community.id,
            "name": community.name,
            "slug": community.slug,
            "description": community.description,
            "is_active": community.is_active,
            "created_at": community.created_at.isoformat() if community.created_at else None,
            "members_count": community.members_count,  # ✅ Utilise l'annotation au lieu de .count()
            "projects_count": community.projects_count,  # ✅ Utilise l'annotation au lieu de .count()
        })
    
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def community_detail_view(request, slug):
    """
    GET /api/communities/<slug>/
    
    Retourne les détails d'une communauté (lecture seule).
    
    Args:
        slug: Identifiant unique de la communauté
        
    Returns:
        dict: {
            "id": int,
            "name": str,
            "slug": str,
            "description": str | null,
            "is_active": bool,
            "created_at": "YYYY-MM-DDTHH:MM:SSZ",
            "updated_at": "YYYY-MM-DDTHH:MM:SSZ",
            "members_count": int,
            "projects_count": int,
            "projects": [  # Liste des projets associés (IDs seulement pour V1)
                {
                    "id": int,
                    "titre": str,
                },
                ...
            ]
        }
    """
    # ÉRADICATION N+1 : Utiliser annotate(Count(...)) au lieu de .count() après get_object_or_404
    community = Community.objects.filter(slug=slug, is_active=True).annotate(
        members_count=Count('members', distinct=True),
        projects_count=Count('projects', distinct=True)
    ).first()
    
    if not community:
        return Response(
            {"detail": "Communauté non trouvée"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # OPTIMISATION MÉMOIRE : QuerySet lazy avec LIMIT en SQL
    # Au lieu de charger tous les projets puis couper, on fait le LIMIT directement en SQL
    projects_qs = community.projects.select_related(
        'community'  # Précharger la communauté (déjà chargée, mais pour cohérence)
    )[:20]  # LIMIT 20 en SQL, pas en Python
    
    # OPTIMISATION MÉMOIRE : Utiliser values() pour ne charger que les champs nécessaires
    projects_data = list(
        projects_qs.values('id', 'titre')
    )
    
    data = {
        "id": community.id,
        "name": community.name,
        "slug": community.slug,
        "description": community.description,
        "is_active": community.is_active,
        "created_at": community.created_at.isoformat() if community.created_at else None,
        "updated_at": community.updated_at.isoformat() if community.updated_at else None,
        "members_count": community.members_count,  # ✅ Utilise l'annotation au lieu de .count()
        "projects_count": community.projects_count,  # ✅ Utilise l'annotation au lieu de .count()
        "projects": projects_data,
    }
    
    return Response(data)

