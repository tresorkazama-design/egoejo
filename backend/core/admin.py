# backend/core/admin.py

from django.contrib import admin
from .models import Projet, Cagnotte, Contribution, Media, Intent # <-- Importez Media et Intent

# 1. Définir l'interface en ligne (pour ajouter plusieurs fichiers dans la même page)
class MediaInline(admin.TabularInline):
    model = Media
    extra = 1 # Affiche un champ d'upload vide par défaut

# 2. Définir le modèle Projet
class ProjetAdmin(admin.ModelAdmin):
    inlines = [MediaInline]
    # Ici, nous pouvons retirer l'ancien champ 'image' de la vue principale (si on veut)
    # fields = ('titre', 'description', 'categorie', 'impact_score', 'created_at') # Exemple si on veut masquer le champ image unique

# 3. Enregistrement des modèles
admin.site.register(Projet, ProjetAdmin) # <-- Enregistrez en utilisant la classe ProjetAdmin

admin.site.register(Cagnotte)
admin.site.register(Contribution)
# Media est géré via ProjetAdmin, donc pas besoin de l'enregistrer ici.

# Admin pour Intent
class IntentAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'profil', 'created_at']
    list_filter = ['profil', 'created_at']
    search_fields = ['nom', 'email']
    readonly_fields = ['ip', 'user_agent', 'created_at']

admin.site.register(Intent, IntentAdmin)