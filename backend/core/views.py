from rest_framework import generics, permissions, status
from .models import Projet, Cagnotte, Contribution, Intent
from .serializers import ProjetSerializer, CagnotteSerializer, ContributionSerializer, IntentSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import re
import os
from django.http import HttpResponse

class ProjetListCreate(generics.ListCreateAPIView):
    queryset = Projet.objects.all().order_by('-created_at')
    serializer_class = ProjetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CagnotteListCreate(generics.ListCreateAPIView):
    queryset = Cagnotte.objects.all().order_by('-created_at')
    serializer_class = CagnotteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def contribute(request, pk):
    return Response({'detail': 'Endpoint désactivé'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def rejoindre(request):
    """
    Endpoint pour soumettre une intention de rejoindre.
    Remplace la route serverless Vercel.
    """
    data = request.data
    
    # Honeypot anti-spam : si website est rempli, on dit OK mais on ne stocke pas
    if data.get('website'):
        return Response({'ok': True, 'id': None}, status=status.HTTP_200_OK)
    
    # Validation des champs requis
    nom = data.get('nom', '').strip()
    email = data.get('email', '').strip()
    profil = data.get('profil', '').strip()
    message = data.get('message', '').strip()
    document_url = data.get('document_url', '').strip() or None
    
    if not nom or not email or not profil:
        return Response({'ok': False, 'error': 'Champs manquants'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validation email
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        return Response({'ok': False, 'error': 'Email invalide'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validation longueur message
    if message and len(message) > 2000:
        return Response({'ok': False, 'error': 'Message trop long'}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    
    # Récupération IP et User-Agent
    ip = None
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif 'REMOTE_ADDR' in request.META:
        ip = request.META['REMOTE_ADDR']
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Création de l'intent
    try:
        intent = Intent.objects.create(
            nom=nom,
            email=email,
            profil=profil,
            message=message or None,
            ip=ip,
            user_agent=user_agent or None,
            document_url=document_url
        )
        
        # Envoi d'email via Resend (si configuré)
        try:
            resend_api_key = os.environ.get('RESEND_API_KEY')
            notify_email = os.environ.get('NOTIFY_EMAIL', 'tresor.kazama@gmail.com')
            
            if resend_api_key:
                try:
                    from resend import Resend
                    resend = Resend(resend_api_key)
                    resend.emails.send({
                        'from': 'EGOEJO <noreply@egoejo.com>',
                        'to': notify_email,
                        'subject': 'Nouvelle intention reçue (EGOEJO)',
                        'text': f'Nom: {nom}\nEmail: {email}\nProfil: {profil}\nMessage:\n{message or "(vide)"}'
                    })
                except ImportError:
                    # Resend n'est pas installé, on continue sans email
                    pass
        except Exception as e:
            # Ne pas faire échouer la requête si l'email échoue
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Resend error: {e}')
        
        return Response({
            'ok': True,
            'id': intent.id,
            'created_at': intent.created_at.isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'ok': False, 'error': 'Erreur serveur'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def admin_data(request):
    """
    Endpoint pour récupérer les intentions avec filtres (admin).
    Authentification par token dans le header Authorization: Bearer <token>
    Supports: from, to, profil, q (recherche), limit, offset
    """
    # Vérification du token
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else ''
    admin_token = os.environ.get('ADMIN_TOKEN')
    
    if not admin_token or token != admin_token:
        return Response({'ok': False, 'error': 'Token invalide.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        from django.db.models import Q
        from datetime import datetime
        
        queryset = Intent.objects.all()
        
        # Filtre par date (from)
        from_date = request.query_params.get('from')
        if from_date:
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=from_datetime)
            except ValueError:
                pass
        
        # Filtre par date (to)
        to_date = request.query_params.get('to')
        if to_date:
            try:
                to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
                # Ajouter 23:59:59 pour inclure toute la journée
                to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(created_at__lte=to_datetime)
            except ValueError:
                pass
        
        # Filtre par profil
        profil = request.query_params.get('profil')
        if profil:
            queryset = queryset.filter(profil=profil)
        
        # Recherche (nom, email, message)
        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(nom__icontains=q) |
                Q(email__icontains=q) |
                Q(message__icontains=q)
            )
        
        # Pagination
        limit = min(int(request.query_params.get('limit', 200)), 1000)
        offset = max(int(request.query_params.get('offset', 0)), 0)
        
        # Compter le total avant la pagination
        total_count = queryset.count()
        
        # Appliquer la pagination et l'ordre
        intents = queryset.order_by('-created_at')[offset:offset + limit]
        
        serializer = IntentSerializer(intents, many=True)
        return Response({
            'ok': True,
            'rows': serializer.data,
            'count': len(serializer.data),
            'total': total_count,
            'limit': limit,
            'offset': offset
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Admin data error: {e}')
        return Response({'ok': False, 'error': 'Erreur serveur BDD.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def export_intents(request):
    """
    Endpoint pour exporter les intentions en CSV.
    Authentification par token dans le header Authorization: Bearer <token>
    Supports les mêmes filtres que admin_data: from, to, profil, q
    """
    # Vérification du token
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else ''
    admin_token = os.environ.get('ADMIN_TOKEN')
    
    if not admin_token or token != admin_token:
        return Response({'ok': False, 'error': 'Token invalide.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        from django.db.models import Q
        from datetime import datetime
        
        queryset = Intent.objects.all()
        
        # Appliquer les mêmes filtres que admin_data
        from_date = request.query_params.get('from')
        if from_date:
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
                queryset = queryset.filter(created_at__gte=from_datetime)
            except ValueError:
                pass
        
        to_date = request.query_params.get('to')
        if to_date:
            try:
                to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
                to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(created_at__lte=to_datetime)
            except ValueError:
                pass
        
        profil = request.query_params.get('profil')
        if profil:
            queryset = queryset.filter(profil=profil)
        
        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(nom__icontains=q) |
                Q(email__icontains=q) |
                Q(message__icontains=q)
            )
        
        intents = queryset.order_by('-created_at')[:10000]  # Limite à 10000 pour CSV
        
        # Création du CSV
        header = "id,nom,email,profil,message,created_at,ip,user_agent,document_url\n"
        rows = []
        for intent in intents:
            msg = (intent.message or "").replace('"', '""')
            rows.append([
                str(intent.id),
                intent.nom,
                intent.email,
                intent.profil,
                msg,
                intent.created_at.isoformat() if intent.created_at else "",
                intent.ip or "",
                (intent.user_agent or "").replace('"', '""'),
                intent.document_url or "",
            ])
        
        csv_content = header + "\n".join([','.join([f'"{cell}"' for cell in row]) for row in rows])
        
        response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename=intents.csv'
        return response
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Export error: {e}')
        return Response({'ok': False, 'error': 'Erreur serveur BDD.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.AllowAny])
def delete_intent(request, intent_id):
    """
    Endpoint pour supprimer une intention (admin).
    Authentification par token dans le header Authorization: Bearer <token>
    """
    # Vérification du token
    auth_header = request.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip() if auth_header.startswith('Bearer ') else ''
    admin_token = os.environ.get('ADMIN_TOKEN')
    
    if not admin_token or token != admin_token:
        return Response({'ok': False, 'error': 'Token invalide.'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        intent = Intent.objects.get(pk=intent_id)
        intent.delete()
        return Response({'ok': True, 'deleted': True}, status=status.HTTP_200_OK)
    except Intent.DoesNotExist:
        return Response({'ok': False, 'error': 'Intention non trouvée.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Delete error: {e}')
        return Response({'ok': False, 'error': 'Erreur serveur BDD.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)