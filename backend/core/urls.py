from django.urls import path
from .views import (
    ProjetListCreate, CagnotteListCreate, contribute,
    rejoindre, admin_data, export_intents, delete_intent
)

urlpatterns = [
    path('projets/', ProjetListCreate.as_view(), name='projet-list-create'),
    path('cagnottes/', CagnotteListCreate.as_view(), name='cagnotte-list-create'),
    path('cagnottes/<int:pk>/contribute/', contribute, name='cagnotte-contribute'),
    # Routes pour les intentions
    path('intents/rejoindre/', rejoindre, name='intent-rejoindre'),
    path('intents/admin/', admin_data, name='intent-admin-data'),
    path('intents/export/', export_intents, name='intent-export'),
    path('intents/<int:intent_id>/delete/', delete_intent, name='intent-delete'),
]