from django.db import models
from django.contrib.auth.models import User

class Projet(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    categorie = models.CharField(max_length=100, blank=True, null=True)
    impact_score = models.IntegerField(blank=True, null=True)
    image = models.FileField(upload_to='projets/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.titre

class Cagnotte(models.Model):
    titre = models.CharField(max_length=255)
    description = models.TextField()
    montant_cible = models.FloatField()
    montant_collecte = models.FloatField(default=0)
    projet = models.ForeignKey(Projet, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.titre

class Contribution(models.Model):
    cagnotte = models.ForeignKey(Cagnotte, on_delete=models.CASCADE, related_name='contributions')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    montant = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
# backend/core/models.py

# ... Vos classes Projet, Cagnotte, Contribution restent au-dessus ...

class Media(models.Model):
    # Le FileField accepte tout type de fichier (vidéo, PDF, image)
    fichier = models.FileField(upload_to='projets_medias/', blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    
    # Clé étrangère vers le modèle Projet (relation Un Projet a Plusieurs Médias)
    projet = models.ForeignKey(
        'Projet', 
        on_delete=models.CASCADE, 
        related_name='medias' # Permet d'accéder aux fichiers depuis Projet.medias.all()
    )

    def __str__(self):
        return f"Média pour: {self.projet.titre}"

class Intent(models.Model):
    """Modèle pour stocker les intentions de rejoindre l'organisation"""
    nom = models.CharField(max_length=255)
    email = models.EmailField()
    profil = models.CharField(max_length=100)
    message = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    document_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Intention"
        verbose_name_plural = "Intentions"

    def __str__(self):
        return f"{self.nom} ({self.email}) - {self.profil}"