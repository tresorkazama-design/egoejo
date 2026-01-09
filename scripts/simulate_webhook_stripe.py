#!/usr/bin/env python3
"""
Script de simulation webhook Stripe pour tests locaux.

Usage:
    python scripts/simulate_webhook_stripe.py \
        --user-id 1 \
        --project-id 1 \
        --amount 100.00 \
        --tip 5.00 \
        --backend-url http://localhost:8000

Ce script génère un payload webhook Stripe réaliste et l'envoie au backend.
Utile pour tester les webhooks sans avoir besoin de Stripe CLI ou d'un compte Stripe.
"""
import argparse
import json
import hmac
import hashlib
import requests
import uuid
from decimal import Decimal


def create_stripe_signature(payload: bytes, secret: str, timestamp: int = None) -> str:
    """Crée une signature Stripe pour les tests"""
    import time
    if timestamp is None:
        timestamp = int(time.time())
    
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"t={timestamp},v1={signature}"


def create_stripe_webhook_payload(
    user_id: int,
    project_id: int,
    amount: Decimal,
    tip: Decimal = Decimal('0.00'),
    payment_intent_id: str = None
) -> dict:
    """Crée un payload webhook Stripe réaliste"""
    if payment_intent_id is None:
        payment_intent_id = f"pi_test_{uuid.uuid4().hex[:8]}"
    
    total_cents = int((amount + tip) * 100)
    donation_cents = int(amount * 100)
    tip_cents = int(tip * 100)
    
    # Estimation des frais Stripe (1.4% + 0.25€)
    estimated_fee_cents = int((total_cents * 0.014) + 25)
    
    return {
        "id": f"evt_test_{uuid.uuid4().hex[:8]}",
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "id": payment_intent_id,
                "amount": total_cents,
                "currency": "eur",
                "metadata": {
                    "user_id": str(user_id),
                    "project_id": str(project_id),
                    "donation_amount": str(amount),
                    "tip_amount": str(tip),
                    "target_type": "project"
                },
                "charges": {
                    "data": [{
                        "id": f"ch_test_{uuid.uuid4().hex[:8]}",
                        "balance_transaction": {
                            "fee": estimated_fee_cents
                        }
                    }]
                }
            }
        }
    }


def main():
    parser = argparse.ArgumentParser(description='Simule un webhook Stripe')
    parser.add_argument('--user-id', type=int, required=True, help='ID utilisateur')
    parser.add_argument('--project-id', type=int, required=True, help='ID projet')
    parser.add_argument('--amount', type=float, required=True, help='Montant don (EUR)')
    parser.add_argument('--tip', type=float, default=0.0, help='Montant tip (EUR)')
    parser.add_argument('--backend-url', type=str, default='http://localhost:8000', help='URL backend')
    parser.add_argument('--webhook-secret', type=str, default='', help='Secret webhook (optionnel)')
    parser.add_argument('--skip-signature', action='store_true', help='Ignorer la signature (dev uniquement)')
    
    args = parser.parse_args()
    
    # Créer le payload
    payload = create_stripe_webhook_payload(
        user_id=args.user_id,
        project_id=args.project_id,
        amount=Decimal(str(args.amount)),
        tip=Decimal(str(args.tip))
    )
    
    payload_bytes = json.dumps(payload).encode('utf-8')
    
    # Créer la signature si un secret est fourni
    headers = {'Content-Type': 'application/json'}
    if args.webhook_secret and not args.skip_signature:
        signature = create_stripe_signature(payload_bytes, args.webhook_secret)
        headers['Stripe-Signature'] = signature
        print(f"[INFO] Signature créée: {signature[:50]}...")
    else:
        print("[WARNING] Aucune signature webhook (mode dev uniquement)")
    
    # Envoyer la requête
    webhook_url = f"{args.backend_url}/api/finance/stripe/webhook/"
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

