"""
Services financiers pour EGOEJO.

Ce package contient :
- ledger.py : Services de répartition proportionnelle des frais Stripe

NOTE : Le fichier finance/services.py existe au même niveau et contient
les services principaux. Les imports depuis finance.services (fichier)
continuent de fonctionner normalement.
"""

# Ce package ne re-exporte rien pour éviter les conflits avec finance/services.py
__all__ = []
