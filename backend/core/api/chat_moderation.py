"""
API de modération pour le chat (P1/P2).

Modération minimale : report message -> stored
"""
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from core.models import ChatMessage, ChatMessageReport
from core.serializers import ChatMessageSerializer


class ChatMessageReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour signaler des messages de chat.
    
    Modération minimale : stocker les signalements pour audit.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retourne les signalements de l'utilisateur ou tous si admin"""
        user = self.request.user
        if user.is_staff:
            return ChatMessageReport.objects.all().select_related('message', 'reporter', 'reviewed_by')
        return ChatMessageReport.objects.filter(reporter=user).select_related('message', 'reporter')
    
    def perform_create(self, serializer):
        """Crée un signalement"""
        message = serializer.validated_data['message']
        
        # Vérifier que l'utilisateur peut signaler ce message (doit être membre du thread)
        if not message.thread.participants.filter(pk=self.request.user.pk).exists():
            raise PermissionDenied("Vous ne pouvez signaler que les messages des threads auxquels vous participez.")
        
        # Vérifier qu'il n'a pas déjà signalé ce message
        if ChatMessageReport.objects.filter(message=message, reporter=self.request.user).exists():
            raise ValidationError("Vous avez déjà signalé ce message.")
        
        serializer.save(reporter=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def review(self, request, pk=None):
        """Marque un signalement comme examiné (admin uniquement)"""
        report = self.get_object()
        report.mark_reviewed(request.user)
        return Response({'status': 'reviewed'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def dismiss(self, request, pk=None):
        """Marque un signalement comme rejeté (admin uniquement)"""
        report = self.get_object()
        report.mark_dismissed(request.user)
        return Response({'status': 'dismissed'}, status=status.HTTP_200_OK)


class ChatMessageViewSetWithReport(viewsets.ModelViewSet):
    """
    Extension de ChatMessageViewSet avec action report.
    
    À utiliser si on veut ajouter l'action report directement sur ChatMessageViewSet.
    """
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def report(self, request, pk=None):
        """Signale un message"""
        message = self.get_object()
        
        # Vérifier que l'utilisateur peut signaler ce message
        if not message.thread.participants.filter(pk=request.user.pk).exists():
            raise PermissionDenied("Vous ne pouvez signaler que les messages des threads auxquels vous participez.")
        
        # Vérifier qu'il n'a pas déjà signalé ce message
        if ChatMessageReport.objects.filter(message=message, reporter=request.user).exists():
            raise ValidationError("Vous avez déjà signalé ce message.")
        
        reason = request.data.get('reason', '')
        report = ChatMessageReport.objects.create(
            message=message,
            reporter=request.user,
            reason=reason
        )
        
        return Response({
            'id': report.id,
            'status': 'created',
            'message': 'Message signalé avec succès'
        }, status=status.HTTP_201_CREATED)

