"""
Script de test pour vérifier que les modules de sécurité fonctionnent
À exécuter depuis le répertoire backend avec: python TEST_SECURITE.py
"""
import os
import sys
import django

# Configuration Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

print("=" * 60)
print("TEST DES MODULES DE SÉCURITÉ")
print("=" * 60)

# Test 1: Chiffrement
print("\n1. Test du chiffrement...")
try:
    from core.security.encryption import encrypt_sensitive_data, decrypt_sensitive_data
    
    test_data = "Donnée sensible à chiffrer"
    encrypted = encrypt_sensitive_data(test_data)
    decrypted = decrypt_sensitive_data(encrypted)
    
    if decrypted == test_data:
        print("   [OK] Chiffrement fonctionne correctement")
        print(f"   Donnee originale: {test_data}")
        print(f"   Donnee chiffree: {encrypted[:50]}...")
        print(f"   Donnee dechiffree: {decrypted}")
    else:
        print("   [ERREUR] Les donnees ne correspondent pas")
except Exception as e:
    print(f"   [ERREUR] Erreur lors du test de chiffrement: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Sanitization
print("\n2. Test de la sanitization...")
try:
    from core.security.sanitization import sanitize_string, sanitize_email
    
    # Test XSS
    xss_input = "<script>alert('XSS')</script>"
    cleaned = sanitize_string(xss_input)
    if "<script>" not in cleaned:
        print("   [OK] Protection XSS fonctionne")
        print(f"   Input: {xss_input}")
        print(f"   Output: {cleaned}")
    else:
        print("   [ERREUR] XSS non bloque")
    
    # Test email - Email principal du projet
    test_emails = [
        "ego.ejoo@gmail.com",
        "contact@egoejo.org",
        "test@example.com"
    ]
    
    for test_email in test_emails:
        try:
            email = sanitize_email(test_email)
            print(f"   [OK] Validation email fonctionne: {email}")
        except Exception as e:
            print(f"   [ERREUR] Email invalide '{test_email}': {e}")
    
    # Test d'emails invalides (doivent échouer)
    invalid_emails = [
        "email-sans-arobase.com",
        "email@",
        "@domain.com",
        "email avec espaces@domain.com"
    ]
    
    print("\n   Test d'emails invalides (doivent etre rejetes):")
    for invalid_email in invalid_emails:
        try:
            email = sanitize_email(invalid_email)
            print(f"   [ERREUR] Email invalide accepte par erreur: {invalid_email}")
        except Exception as e:
            print(f"   [OK] Email invalide correctement rejete: {invalid_email}")
        
except Exception as e:
    print(f"   [ERREUR] Erreur lors du test de sanitization: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Middleware
print("\n3. Test des middlewares...")
try:
    from core.security.middleware import SecurityHeadersMiddleware, DataProtectionMiddleware
    
    print("   [OK] SecurityHeadersMiddleware importe")
    print("   [OK] DataProtectionMiddleware importe")
except Exception as e:
    print(f"   [ERREUR] Erreur lors de l'import des middlewares: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Logging
print("\n4. Test du logging sécurisé...")
try:
    from core.security.logging import SecureFormatter
    
    print("   [OK] SecureFormatter importe")
except Exception as e:
    print(f"   [ERREUR] Erreur lors de l'import du logging: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTS TERMINÉS")
print("=" * 60)

