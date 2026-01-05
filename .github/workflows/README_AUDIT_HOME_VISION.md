# Workflow GitHub Actions - Audit Compliance Pages Accueil & Vision

**Fichier** : `.github/workflows/audit-home-vision.yml`  
**Statut** : ✅ BLOQUANT (requis sur PR et push main)

---

## 🎯 Objectif

Ce workflow garantit que les pages **Accueil** (`/`) et **Vision** (`/vision`) respectent toutes les exigences de l'audit quadripartite strict.

---

## 📋 Déclencheurs

Le workflow s'exécute automatiquement sur :
- ✅ **Pull Request** vers `main` ou `develop`
- ✅ **Push** sur `main`

---

## 🔧 Étapes du Workflow

### 1. Checkout code
- Utilise `actions/checkout@v4`

### 2. Setup Node.js
- Version : `18`
- Cache npm activé (accélère les builds suivants)
- Cache basé sur `frontend/frontend/package-lock.json`

### 3. Install dependencies
- Commande : `npm ci` (installation propre et reproductible)
- Working directory : `frontend/frontend`

### 4. Run ESLint
- Commande : `npm run lint`
- **BLOQUANT** : Échec si erreurs de linting

### 5. Run unit tests (Audit Compliance)
- Tests ciblés :
  - `src/app/pages/__tests__/Home.audit-compliance.test.jsx`
  - `src/app/pages/__tests__/Vision.audit-compliance.test.jsx`
  - `src/components/__tests__/Layout.i18n-skip-link.test.jsx`
- **BLOQUANT** : Échec si tests échouent

### 6. Install Playwright browsers
- Installe Chromium avec dépendances système
- Nécessaire pour les tests E2E

### 7. Run E2E tests (Audit Compliance)
- Tests ciblés :
  - `e2e/audit-compliance-accueil-vision.spec.js`
  - `e2e/home.spec.js`
  - `e2e/navigation-sections.spec.js`
- Mode : `mock-only` (pas besoin de backend)
- **BLOQUANT** : Échec si tests échouent

### 8. Generate test summary
- Génère un résumé dans `$GITHUB_STEP_SUMMARY`
- Affiche les résultats des tests unitaires et E2E
- Liste les exigences testées

### 9. Upload Playwright report
- Upload le rapport Playwright en tant qu'artifact
- Rétention : 7 jours
- Nom : `playwright-report-audit-home-vision`

### 10. Fail if tests failed
- Échoue explicitement si les tests ont échoué
- Message d'erreur explicite

---

## 📊 Résumé Généré

Le workflow génère automatiquement un résumé dans l'interface GitHub Actions avec :

- ✅/❌ Statut des tests unitaires
- ✅/❌ Statut des tests E2E
- 📋 Liste des exigences testées
- 📚 Liens vers la documentation

---

## 🎯 Exigences Testées

### A. Navigation/Accessibilité
1. Le lien "Soutenir" scroll vers #soutenir (desktop et mobile)
2. Le skip-link focus et scroll vers #main-content
3. Le skip-link est traduit via i18n (PAS de texte hardcodé uniquement FR)

### B. Conformité Éditoriale Minimale
4. Vision contient section "Principes fondamentaux" avec 3 principes
5. Vision contient glossaire (vivant, gardiens, alliance)
6. Vision contient disclaimer citations autochtones
7. Accueil contient note explicite SAKA/EUR
8. Texte "100% des dons" corrigé en "100% des dons nets"

---

## 🚀 Commandes Locales

### Tests unitaires
```bash
cd frontend/frontend
npm run test:run -- src/app/pages/__tests__/Home.audit-compliance.test.jsx src/app/pages/__tests__/Vision.audit-compliance.test.jsx src/components/__tests__/Layout.i18n-skip-link.test.jsx
```

### Tests E2E
```bash
cd frontend/frontend
npm run test:e2e -- e2e/audit-compliance-accueil-vision.spec.js e2e/home.spec.js e2e/navigation-sections.spec.js
```

### Script raccourci (package.json)
```bash
cd frontend/frontend
npm run test:e2e:audit
```

---

## 📝 Patterns Playwright

### Filtrer les tests d'audit uniquement
```bash
# Pattern 1 : Fichiers spécifiques
npm run test:e2e -- e2e/audit-compliance-accueil-vision.spec.js e2e/home.spec.js e2e/navigation-sections.spec.js

# Pattern 2 : Script raccourci
npm run test:e2e:audit

# Pattern 3 : Grep pattern
npx playwright test --grep "audit|home|vision|navigation.*section"
```

---

## ⚙️ Configuration Requise

### Branch Protection Rules

Pour rendre ce workflow **BLOQUANT** sur les PR, configurez dans GitHub :

1. Allez dans **Settings** → **Branches**
2. Ajoutez/modifiez la règle pour `main` et `develop`
3. Cochez **Require status checks to pass before merging**
4. Sélectionnez **audit-home-vision** dans la liste

---

## 🔍 Dépannage

### Les tests échouent en CI mais passent localement

1. Vérifiez que les sections requises sont présentes :
   - Section "Principes fondamentaux" sur Vision
   - Glossaire sur Vision
   - Disclaimer citations autochtones sur Vision
   - Note SAKA/EUR sur Accueil
   - Texte "100% des dons nets" sur Accueil

2. Vérifiez que le skip-link utilise la traduction :
   - `t("accessibility.skip_to_main", language)`
   - Pas de texte hardcodé "Aller au contenu principal"

3. Vérifiez les logs GitHub Actions pour les erreurs spécifiques

### Les tests E2E échouent

1. Vérifiez que Playwright est installé : `npx playwright install`
2. Vérifiez que le serveur de développement démarre correctement
3. Vérifiez les screenshots dans l'artifact `playwright-report-audit-home-vision`

---

## 📚 Documentation Associée

- [TESTS_AUDIT_COMPLIANCE_ACCUEIL_VISION.md](../frontend/frontend/TESTS_AUDIT_COMPLIANCE_ACCUEIL_VISION.md)
- [AUDIT_QUADRIPARTITE_STRICT_ACCUEIL_VISION.md](../docs/reports/AUDIT_QUADRIPARTITE_STRICT_ACCUEIL_VISION.md)

---

**Dernière mise à jour** : 2025-01-27

