#!/usr/bin/env python
"""
Script pour lancer la réduction dimensionnalité (Mycélium Numérique)
Usage: python scripts/launch_mycelium_reduction.py [--method tsne|umap] [--type both|projet|educational_content]
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

from core.tasks_mycelium import reduce_embeddings_to_3d


def main():
    parser = argparse.ArgumentParser(description='Lancer la réduction dimensionnalité pour le Mycélium Numérique')
    parser.add_argument(
        '--method',
        choices=['umap', 'tsne'],
        default='tsne',
        help='Méthode de réduction (default: tsne, recommandé pour Python 3.14+)'
    )
    parser.add_argument(
        '--type',
        choices=['both', 'projet', 'educational_content'],
        default='both',
        help='Type de contenu à traiter (default: both)'
    )
    parser.add_argument(
        '--sync',
        action='store_true',
        help='Exécution synchrone (bloquante) au lieu d\'asynchrone'
    )
    
    args = parser.parse_args()
    
    print(f"🚀 Lancement réduction dimensionnalité...")
    print(f"   Méthode: {args.method}")
    print(f"   Type: {args.type}")
    print(f"   Mode: {'Synchrone' if args.sync else 'Asynchrone (Celery)'}")
    print()
    
    try:
        if args.sync:
            # Exécution synchrone (pour test)
            print("⏳ Exécution en cours (peut prendre plusieurs minutes)...")
            result = reduce_embeddings_to_3d(args.type, args.method)
            print(f"✅ Résultat: {result}")
        else:
            # Exécution asynchrone via Celery
            task = reduce_embeddings_to_3d.delay(args.type, args.method)
            print(f"✅ Tâche Celery lancée!")
            print(f"   Task ID: {task.id}")
            print(f"   Statut: {task.status}")
            print()
            print("💡 Pour suivre l'exécution:")
            print(f"   - Via Flower: http://localhost:5555")
            print(f"   - Via logs Celery: celery -A config worker -l info")
            print(f"   - Vérifier résultat: GET /api/mycelium/data/")
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

