#!/usr/bin/env python
"""
Script pour tester la génération audio (TTS)
Usage: python scripts/test_audio_generation.py [--content-id ID] [--provider openai|elevenlabs] [--voice VOICE]
"""
import os
import sys
import django
import argparse

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models.content import EducationalContent
from core.tasks_audio import generate_audio_content


def main():
    parser = argparse.ArgumentParser(description='Tester la génération audio (TTS)')
    parser.add_argument(
        '--content-id',
        type=int,
        help='ID du contenu éducatif (si non spécifié, utilise le premier contenu publié)'
    )
    parser.add_argument(
        '--provider',
        choices=['openai', 'elevenlabs'],
        default=None,
        help='Provider TTS (défaut: depuis TTS_PROVIDER env ou openai)'
    )
    parser.add_argument(
        '--voice',
        default=None,
        help='Voix à utiliser (défaut: depuis TTS_VOICE env ou alloy)'
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Exécution synchrone (bloquante) au lieu d\'asynchrone'
    )
    
    args = parser.parse_args()
    
    # Récupérer le contenu
    if args.content_id:
        try:
            content = EducationalContent.objects.get(id=args.content_id)
        except EducationalContent.DoesNotExist:
            print(f"❌ Contenu avec ID {args.content_id} non trouvé")
            sys.exit(1)
    else:
        # Utiliser le premier contenu publié
        content = EducationalContent.objects.filter(status='published').first()
        if not content:
            print("❌ Aucun contenu publié trouvé")
            sys.exit(1)
    
    print(f"📄 Contenu sélectionné:")
    print(f"   ID: {content.id}")
    print(f"   Titre: {content.title}")
    print(f"   Statut: {content.status}")
    print(f"   Audio existant: {'Oui' if content.audio_file else 'Non'}")
    print()
    
    # Déterminer provider et voice
    provider = args.provider or os.environ.get('TTS_PROVIDER', 'openai')
    voice = args.voice or os.environ.get('TTS_VOICE', 'alloy')
    
    print(f"🎙️  Configuration TTS:")
    print(f"   Provider: {provider}")
    print(f"   Voice: {voice}")
    print()
    
    # Vérifier la clé API
    if provider == 'openai':
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY non configuré")
            print("   Configurez-la dans .env ou variables d'environnement")
            sys.exit(1)
    elif provider == 'elevenlabs':
        api_key = os.environ.get('ELEVENLABS_API_KEY')
        if not api_key:
            print("❌ ELEVENLABS_API_KEY non configuré")
            print("   Configurez-la dans .env ou variables d'environnement")
            sys.exit(1)
    
    try:
        if args.sync:
            # Exécution synchrone (pour test)
            print("⏳ Génération audio en cours (peut prendre 30-60 secondes)...")
            result = generate_audio_content(content.id, provider, voice)
            print(f"✅ Résultat: {result}")
            
            # Rafraîchir le contenu
            content.refresh_from_db()
            if content.audio_file:
                print(f"✅ Fichier audio généré: {content.audio_file}")
            else:
                print("⚠️  Aucun fichier audio généré (vérifier les logs)")
        else:
            # Exécution asynchrone via Celery
            task = generate_audio_content.delay(content.id, provider, voice)
            print(f"✅ Tâche Celery lancée!")
            print(f"   Task ID: {task.id}")
            print(f"   Statut: {task.status}")
            print()
            print("💡 Pour suivre l'exécution:")
            print(f"   - Via Flower: http://localhost:5555")
            print(f"   - Via logs Celery: celery -A config worker -l info")
            print(f"   - Vérifier résultat: GET /api/contents/{content.id}/")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

