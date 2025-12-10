# Guide pour Acheter le Nom de Domaine EGOEJO

## 📋 Informations du Projet

- **Nom du projet**: EGOEJO
- **Description**: Collectif pour le vivant
- **Domaine suggéré**: `egoejo.org` ou `egoejo.com`

## 🌐 Options de Domaines

### Option 1 : `.org` (Recommandé pour une organisation)
- **Domaine**: `egoejo.org`
- **Avantages**: 
  - Idéal pour les organisations à but non lucratif
  - Plus professionnel pour un collectif
  - Moins cher que `.com`
- **Prix approximatif**: 10-15€/an

### Option 2 : `.com` (Standard)
- **Domaine**: `egoejo.com`
- **Avantages**:
  - Le plus reconnu
  - Meilleur pour le référencement
  - Plus facile à retenir
- **Prix approximatif**: 10-20€/an

### Option 3 : `.fr` (Pour la France)
- **Domaine**: `egoejo.fr`
- **Avantages**:
  - Localisation française
  - Bon pour le SEO local
- **Prix approximatif**: 5-10€/an

## 🛒 Où Acheter le Domaine

### 1. OVH (Recommandé pour la France)
**Site**: https://www.ovh.com

**Avantages**:
- Service français
- Support en français
- Prix compétitifs
- Interface simple

**Étapes**:
1. Aller sur https://www.ovh.com
2. Cliquer sur "Domaines" → "Rechercher un nom de domaine"
3. Entrer "egoejo" dans la recherche
4. Vérifier la disponibilité de `.org`, `.com`, `.fr`
5. Ajouter au panier
6. Créer un compte OVH (si nécessaire)
7. Payer (carte bancaire, PayPal, etc.)

**Prix**:
- `.org`: ~12€/an
- `.com`: ~12€/an
- `.fr`: ~8€/an

### 2. Namecheap (International)
**Site**: https://www.namecheap.com

**Avantages**:
- Interface en anglais
- Prix très compétitifs
- Protection WHOIS gratuite
- Support 24/7

**Étapes**:
1. Aller sur https://www.namecheap.com
2. Rechercher "egoejo"
3. Vérifier la disponibilité
4. Ajouter au panier
5. Créer un compte
6. Payer

**Prix**:
- `.org`: ~10-12$/an
- `.com`: ~10-15$/an

### 3. Google Domains (Maintenant Squarespace Domains)
**Site**: https://domains.squarespace.com

**Avantages**:
- Interface simple
- Intégration avec Google Workspace
- DNS facile à configurer

**Prix**:
- `.org`: ~12$/an
- `.com`: ~12$/an

### 4. Gandi (Recommandé pour les développeurs)
**Site**: https://www.gandi.net

**Avantages**:
- Service français
- Très professionnel
- API disponible
- Support technique excellent

**Prix**:
- `.org`: ~15€/an
- `.com`: ~15€/an
- `.fr`: ~10€/an

## 📝 Checklist d'Achat

### Avant l'achat
- [ ] Vérifier la disponibilité du domaine
- [ ] Vérifier les variantes (egoejo.org, egoejo.com, egoejo.fr)
- [ ] Vérifier si le domaine est déjà pris (et à quel prix)
- [ ] Choisir le registraire
- [ ] Préparer les informations de contact

### Informations nécessaires
- **Nom complet**
- **Email** (important pour les notifications)
- **Adresse postale**
- **Téléphone**
- **Moyen de paiement** (carte bancaire, PayPal, etc.)

### Pendant l'achat
- [ ] Créer un compte sur le registraire
- [ ] Ajouter le domaine au panier
- [ ] Vérifier les options (protection WHOIS, email, etc.)
- [ ] Choisir la durée (1 an minimum, souvent moins cher pour plusieurs années)
- [ ] Payer

### Après l'achat
- [ ] Vérifier l'email de confirmation
- [ ] Noter les identifiants de connexion
- [ ] Configurer les DNS (voir section suivante)

## ⚙️ Configuration DNS pour Vercel

Une fois le domaine acheté, vous devez le configurer pour pointer vers Vercel.

### 1. Dans Vercel

1. Aller sur https://vercel.com
2. Sélectionner votre projet **frontend**
3. Aller dans **Settings** → **Domains**
4. Cliquer sur **"Add"**
5. Entrer votre domaine (ex: `egoejo.org`)
6. Vercel vous donnera les enregistrements DNS à configurer

### 2. Dans votre registraire (ex: OVH)

1. Se connecter à votre compte
2. Aller dans **Domaines** → Votre domaine
3. Cliquer sur **Zone DNS** ou **DNS**
4. Ajouter les enregistrements fournis par Vercel :

**Exemple d'enregistrements Vercel**:
```
Type: A
Name: @
Value: 76.76.21.21

Type: CNAME
Name: www
Value: cname.vercel-dns.com
```

### 3. Vérification

- Attendre 24-48h pour la propagation DNS
- Vérifier avec: https://dnschecker.org
- Tester l'accès au site

## 🔒 Protection et Sécurité

### Protection WHOIS (Recommandé)
- Masque vos informations personnelles dans le WHOIS
- Prix: souvent gratuit ou ~5€/an
- À activer lors de l'achat

### Renouvellement automatique
- Activer le renouvellement automatique
- Évite la perte du domaine
- Configurez un rappel par email

### Verrouillage du domaine
- Activez le verrouillage du domaine
- Empêche les transferts non autorisés
- Souvent gratuit

## 💰 Budget Estimé

### Coût annuel minimum
- **Domaine .org**: ~12€/an
- **Protection WHOIS**: Gratuit ou ~5€/an
- **Total**: ~12-17€/an

### Coût pour plusieurs années
- **3 ans**: ~36-51€ (économies possibles)
- **5 ans**: ~60-85€ (économies possibles)

## 🎯 Recommandation

Pour EGOEJO, je recommande :

1. **Domaine principal**: `egoejo.org`
   - Idéal pour un collectif
   - Professionnel
   - Pas trop cher

2. **Domaine secondaire** (optionnel): `egoejo.com`
   - Pour protéger la marque
   - Rediriger vers `.org`

3. **Registraire**: **OVH** ou **Gandi**
   - Service français
   - Support en français
   - Fiable

## 📞 Support

Si vous avez des questions :
- **OVH**: https://www.ovh.com/fr/support/
- **Gandi**: https://www.gandi.net/fr/support
- **Namecheap**: https://www.namecheap.com/support/

## ⚠️ Points d'Attention

1. **Ne pas laisser expirer le domaine** - Configurez le renouvellement automatique
2. **Vérifier les emails** - Les notifications importantes arrivent par email
3. **Sauvegarder les identifiants** - Dans un gestionnaire de mots de passe
4. **Protection WHOIS** - Activez-la pour la confidentialité
5. **DNS** - Configurez correctement pour que Vercel fonctionne

## 🚀 Prochaines Étapes

1. ✅ Choisir le registraire
2. ✅ Acheter le domaine `egoejo.org`
3. ✅ Configurer les DNS dans Vercel
4. ✅ Attendre la propagation (24-48h)
5. ✅ Tester l'accès au site
6. ✅ Configurer HTTPS (automatique avec Vercel)

---

**Note**: Une fois le domaine acheté, vous pourrez mettre à jour `VITE_APP_URL` dans Vercel pour utiliser votre propre domaine au lieu de l'URL Vercel par défaut.

