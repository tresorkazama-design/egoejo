#!/usr/bin/env python3
"""
Script de simulation webhook HelloAsso pour tests locaux.

Usage:
    python scripts/simulate_webhook_helloasso.py \
        --user-id 1 \
        --project-id 1 \
        --amount 100.00 \
        --backend-url http://localhost:8000

Ce script génère un payload webhook HelloAsso réaliste et l'envoie au backend.
Utile pour tester les webhooks sans avoir besoin d'un compte HelloAsso.
"""
import argparse
import json
import hmac
import hashlib
import requests
import uuid
from decimal import Decimal


def create_helloasso_signature(payload: bytes, secret: str) -> str:
    """Crée une signature HelloAsso pour les tests"""
    return hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()


def create_helloasso_webhook_payload(
    user_id: int,
    project_id: int,
    amount: Decimal,
    payment_id: str = None
) -> dict:
    """Crée un payload webhook HelloAsso réaliste"""
    if payment_id is None:
        payment_id = f"payment_test_{uuid.uuid4().hex[:8]}"
    
    amount_cents = int(amount * 100)
    # Estimation des frais HelloAsso (0.8% + 0.25€)
    fee_cents = int((amount_cents * 0.008) + 25)
    
    return {
        "eventType": "Payment",
        "eventId": f"evt_test_{uuid.uuid4().hex[:8]}",
        "data": {
            "payment": {
                "id": payment_id,
                "amount": amount_cents,
                "fee": fee_cents,
                "currency": "EUR",
                "metadata": {
                    "user_id": str(user_id),
                    "project_id": str(project_id),
                    "donation_amount": str(amount),
                    "tip_amount": "0.00"
                }
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Simule un webhook HelloAsso')
    parser.add_argument('--user-id', type=int, required=True, help='ID utilisateur')
    parser.add_argument('--project-id', type=int, required=True, help='ID projet')
    parser.add_argument('--amount', type=float, required=True, help='Montant (EUR)')
    parser.add_argument('--backend-url', type=str, default='http://localhost:8000', help='URL backend')
    parser.add_argument('--webhook-secret', type=str, default='', help='Secret webhook (optionnel)')
    parser.add_argument('--skip-signature', action='store_true', help='Ignorer la signature (dev uniquement)')
    
    args = parser.parse_args()
    
    # Créer le payload
    payload = create_helloasso_webhook_payload(
        user_id=args.user_id,
        project_id=args.project_id,
        amount=Decimal(str(args.amount))
    )
    
    payload_bytes = json.dumps(payload).encode('utf-8')
    
    # Créer la signature si un secret est fourni
    headers = {'Content-Type': 'application/json'}
    if args.webhook_secret and not args.skip_signature:
        signature = create_helloasso_signature(payload_bytes, args.webhook_secret)
        headers['X-HelloAsso-Signature'] = signature
        print(f"[INFO] Signature créée: {signature[:50]}...")
    else:
        print("[WARNING] Aucune signature webhook (mode dev uniquement)")
    
    # Envoyer la requête
    webhook_url = f"{args.backend_url}/api/payments/helloasso/webhook/"
    print(f"[INFO] Envoi webhook vers: {webhook_url}")
    print(f"[INFO] Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            data=payload_bytes,
            headers=headers,
            timeout=10
        )
        
        print(f"\n[RESULT] Status: {response.status_code}")
        print(f"[RESULT] Response: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ Webhook traité avec succès")
        else:
            print(f"\n❌ Erreur: {response.status_code}")
            return 1
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Erreur de connexion: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

