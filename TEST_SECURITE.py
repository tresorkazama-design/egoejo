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
        print("   ✅ Chiffrement fonctionne correctement")
        print(f"   Donnée originale: {test_data}")
        print(f"   Donnée chiffrée: {encrypted[:50]}...")
        print(f"   Donnée déchiffrée: {decrypted}")
    else:
        print("   ❌ Erreur: les données ne correspondent pas")
except Exception as e:
    print(f"   ❌ Erreur lors du test de chiffrement: {e}")

# Test 2: Sanitization
print("\n2. Test de la sanitization...")
try:
    from core.security.sanitization import sanitize_string, sanitize_email
    
    # Test XSS
    xss_input = "<script>alert('XSS')</script>"
    cleaned = sanitize_string(xss_input)
    if "<script>" not in cleaned:
        print("   ✅ Protection XSS fonctionne")
        print(f"   Input: {xss_input}")
        print(f"   Output: {cleaned}")
    else:
        print("   ❌ Erreur: XSS non bloqué")
    
    # Test email
    try:
        email = sanitize_email("test@example.com")
        print(f"   ✅ Validation email fonctionne: {email}")
    except Exception as e:
        print(f"   ❌ Erreur validation email: {e}")
        
except Exception as e:
    print(f"   ❌ Erreur lors du test de sanitization: {e}")

# Test 3: Middleware
print("\n3. Test des middlewares...")
try:
    from core.security.middleware import SecurityHeadersMiddleware, DataProtectionMiddleware
    
    print("   ✅ SecurityHeadersMiddleware importé")
    print("   ✅ DataProtectionMiddleware importé")
except Exception as e:
    print(f"   ❌ Erreur lors de l'import des middlewares: {e}")

# Test 4: Logging
print("\n4. Test du logging sécurisé...")
try:
    from core.security.logging import SecureFormatter
    
    print("   ✅ SecureFormatter importé")
except Exception as e:
    print(f"   ❌ Erreur lors de l'import du logging: {e}")

print("\n" + "=" * 60)
print("TESTS TERMINÉS")
print("=" * 60)

