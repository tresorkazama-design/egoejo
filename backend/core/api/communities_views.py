"""
API endpoints pour les Communautés EGOEJO.
V1 : Lecture seule (read-only) pour préparer la subsidiarité.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
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
    communities = Community.objects.filter(is_active=True).prefetch_related('members', 'projects')
    
    data = []
    for community in communities:
        data.append({
            "id": community.id,
            "name": community.name,
            "slug": community.slug,
            "description": community.description,
            "is_active": community.is_active,
            "created_at": community.created_at.isoformat() if community.created_at else None,
            "members_count": community.members.count(),
            "projects_count": community.projects.count(),
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
    community = get_object_or_404(Community, slug=slug, is_active=True)
    
    # Récupérer les projets associés (limité aux IDs et titres pour V1)
    projects_data = []
    for project in community.projects.all()[:20]:  # Limiter à 20 projets pour V1
        projects_data.append({
            "id": project.id,
            "titre": project.titre,
        })
    
    data = {
        "id": community.id,
        "name": community.name,
        "slug": community.slug,
        "description": community.description,
        "is_active": community.is_active,
        "created_at": community.created_at.isoformat() if community.created_at else None,
        "updated_at": community.updated_at.isoformat() if community.updated_at else None,
        "members_count": community.members.count(),
        "projects_count": community.projects.count(),
        "projects": projects_data,
    }
    
    return Response(data)

