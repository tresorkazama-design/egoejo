# Plan de Tests Bloquants - Pages Accueil & Vision

**Date** : 2025-01-27  
**Rôle** : QA Lead + Mainteneur CI  
**Objectif** : Rendre opposables (bloquants) les exigences d'audit sur Accueil (/) et Vision (/vision)

---

## 1. CARTOGRAPHIE DES FICHIERS CONCERNÉS

### 1.1 Composants React

| Fichier | Rôle | Lignes clés |
|---------|------|-------------|
| `frontend/frontend/src/app/pages/Home.jsx` | Page Accueil (/) | Ligne 87: `<a href="#soutenir">`, Ligne 146: Section `#soutenir` |
| `frontend/frontend/src/app/pages/Vision.jsx` | Page Vision (/vision) | Ligne 78: Section `vision-principles`, Ligne 120: Section `vision-glossary`, Ligne 180: Disclaimer citations |
| `frontend/frontend/src/components/Layout.jsx` | Layout global | Ligne 57-110: Gestion hash navigation, Ligne 150-170: Skip-link |

### 1.2 Routes

| Fichier | Rôle | Routes définies |
|---------|------|----------------|
| `frontend/frontend/src/app/router.jsx` | Configuration React Router | Ligne 63: `path: '/'`, Ligne 80: `path: 'vision'` |

### 1.3 Internationalisation (i18n)

| Fichier | Langue | Clés critiques |
|---------|--------|----------------|
| `frontend/frontend/src/locales/fr.json` | Français | `home.soutenir_desc`, `vision.principles_*`, `vision.glossary_*`, `accessibility.skip_to_main` |
| `frontend/frontend/src/locales/en.json` | Anglais | Mêmes clés |
| `frontend/frontend/src/locales/es.json` | Espagnol | Mêmes clés |
| `frontend/frontend/src/locales/de.json` | Allemand | Mêmes clés |
| `frontend/frontend/src/locales/ar.json` | Arabe | Mêmes clés |
| `frontend/frontend/src/locales/sw.json` | Swahili | Mêmes clés |

### 1.4 Tests Existants

| Fichier | Type | Couverture actuelle |
|---------|------|-------------------|
| `frontend/frontend/e2e/audit-compliance-accueil-vision.spec.js` | E2E Playwright | ✅ Tests A1-A3, B4-B8 (8 tests) |
| `frontend/frontend/src/app/pages/__tests__/Home.audit-compliance.test.jsx` | Unit Testing Library | ✅ Tests B7, B8 (3 tests) |
| `frontend/frontend/src/app/pages/__tests__/Vision.audit-compliance.test.jsx` | Unit Testing Library | ✅ Tests B4, B5, B6 (5 tests) |
| `frontend/frontend/src/components/__tests__/Layout.i18n-skip-link.test.jsx` | Unit Testing Library | ✅ Test A3 (2 tests) |
| `frontend/frontend/scripts/audit-home-vision.js` | Audit statique Node | ✅ 3 règles (donation_text_nets, vision_i18n_*, skip_link_i18n) |

### 1.5 Règles de Conformité

| Fichier | Rôle |
|---------|------|
| `docs/egoejo_compliance/home-vision.rules.json` | 10 règles définies (critical, high, medium) |

---

## 2. LISTE DES EXIGENCES À TESTER

### 2.1 Navigation/Accessibilité (A)

| ID | Exigence | Fichiers concernés | Test actuel |
|----|----------|-------------------|-------------|
| **A1** | Le lien "Soutenir" scroll vers `#soutenir` (visible dans viewport) sur desktop et mobile | `Home.jsx` (ligne 87), `Layout.jsx` (ligne 57-110) | ✅ E2E `audit-compliance-accueil-vision.spec.js:A1` |
| **A2** | Le skip-link "Aller au contenu principal" focus et scroll vers `#main-content` | `Layout.jsx` (ligne 150-170) | ✅ E2E `audit-compliance-accueil-vision.spec.js:A2` |
| **A3** | Le skip-link est traduit via i18n (PAS de texte hardcodé uniquement FR) | `Layout.jsx`, `locales/*.json` | ✅ Unit `Layout.i18n-skip-link.test.jsx`, ✅ Audit statique |

### 2.2 Conformité Éditoriale Minimale (B)

| ID | Exigence | Fichiers concernés | Test actuel |
|----|----------|-------------------|-------------|
| **B4** | Vision contient section "Principes fondamentaux" explicite avec 3 principes | `Vision.jsx` (ligne 78), `locales/*.json` | ✅ Unit `Vision.audit-compliance.test.jsx:B4` (2 tests), ✅ E2E `audit-compliance-accueil-vision.spec.js:B4` |
| **B5** | Vision contient glossaire (définitions) pour : vivant, SAKA, EUR, silo, compostage, alliance, gardiens | `Vision.jsx` (ligne 120), `locales/*.json` | ✅ Unit `Vision.audit-compliance.test.jsx:B5` (2 tests), ✅ E2E `audit-compliance-accueil-vision.spec.js:B5` |
| **B6** | Vision contient disclaimer contextuel sur les citations autochtones | `Vision.jsx` (ligne 180), `locales/*.json` | ✅ Unit `Vision.audit-compliance.test.jsx:B6`, ✅ E2E `audit-compliance-accueil-vision.spec.js:B6` |
| **B7** | Accueil contient note explicite SAKA/EUR (pas de conversion, pas d'équivalence monétaire) | `Home.jsx`, `locales/*.json` | ✅ Unit `Home.audit-compliance.test.jsx:B7` (2 tests), ✅ E2E `audit-compliance-accueil-vision.spec.js:B7` |
| **B8** | Le texte "100% des dons" est corrigé en "100% des dons nets (après frais…)" ou formulation équivalente non trompeuse | `Home.jsx`, `locales/*.json` | ✅ Unit `Home.audit-compliance.test.jsx:B8`, ✅ E2E `audit-compliance-accueil-vision.spec.js:B8`, ✅ Audit statique `audit-home-vision.js:checkDonationText` |

---

## 3. PLAN TESTABLE EN 3 NIVEAUX

### 3.1 NIVEAU 1 : E2E Playwright (Navigation + Scroll + Focus)

**Objectif** : Vérifier le comportement utilisateur réel (navigation, scroll, focus)

**Fichier existant** : `frontend/frontend/e2e/audit-compliance-accueil-vision.spec.js`

**Tests à compléter/renforcer** :

| Test ID | Description | Status actuel | Améliorations nécessaires |
|---------|-------------|---------------|--------------------------|
| **E2E-A1** | Lien "Soutenir" scroll vers `#soutenir` (desktop) | ✅ Existe | Ajouter test mobile (viewport mobile) |
| **E2E-A1-MOBILE** | Lien "Soutenir" scroll vers `#soutenir` (mobile) | ❌ Manquant | **À CRÉER** : Test avec viewport mobile (375x667) |
| **E2E-A2** | Skip-link focus et scroll vers `#main-content` | ✅ Existe | Vérifier que le focus est bien transféré (accessibilité) |
| **E2E-A3** | Skip-link traduit (pas hardcodé FR) | ✅ Existe | Vérifier toutes les langues supportées (FR, EN, ES, DE, AR, SW) |
| **E2E-B4** | Vision contient section "Principes fondamentaux" avec 3 principes | ✅ Existe | Vérifier le contenu exact des 3 principes |
| **E2E-B5** | Vision contient glossaire (vivant, gardiens, alliance) | ✅ Existe | Vérifier tous les termes (vivant, SAKA, EUR, silo, compostage, alliance, gardiens) |
| **E2E-B6** | Vision contient disclaimer citations autochtones | ✅ Existe | Vérifier le texte exact du disclaimer |
| **E2E-B7** | Accueil contient note SAKA/EUR | ✅ Existe | Vérifier que la note ne contient PAS "conversion" ou "équivalence monétaire" |
| **E2E-B8** | Texte "100% des dons nets" corrigé | ✅ Existe | Vérifier le texte exact avec "nets" ou mention de frais |

**Fichiers à créer/modifier** :

```
frontend/frontend/e2e/audit-compliance-accueil-vision.spec.js
  → Ajouter test E2E-A1-MOBILE (ligne ~50)
  → Renforcer E2E-A3 pour toutes les langues (ligne ~80)
  → Renforcer E2E-B5 pour tous les termes du glossaire (ligne ~150)
```

**Spécifications à ajouter** :

```javascript
// E2E-A1-MOBILE : Test mobile
test('A1-MOBILE) Le lien "Soutenir" scroll vers #soutenir (mobile)', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
  await page.goto('/');
  // ... même logique que E2E-A1
});

// E2E-A3 : Test toutes les langues
test('A3) Le skip-link est traduit dans toutes les langues supportées', async ({ page }) => {
  const languages = ['fr', 'en', 'es', 'de', 'ar', 'sw'];
  for (const lang of languages) {
    await setupMockOnlyTest(page, { language: lang });
    await page.goto('/');
    const skipLink = page.locator('a[href="#main-content"]').first();
    const text = await skipLink.textContent();
    // Vérifier que le texte n'est pas "Aller au contenu principal" (hardcodé FR)
    expect(text).not.toBe('Aller au contenu principal');
  }
});
```

---

### 3.2 NIVEAU 2 : Unit Tests Testing Library (Présence de sections/strings)

**Objectif** : Vérifier la présence de sections, strings, et structure DOM

**Fichiers existants** :
- `frontend/frontend/src/app/pages/__tests__/Home.audit-compliance.test.jsx`
- `frontend/frontend/src/app/pages/__tests__/Vision.audit-compliance.test.jsx`
- `frontend/frontend/src/components/__tests__/Layout.i18n-skip-link.test.jsx`

**Tests à compléter/renforcer** :

| Test ID | Description | Status actuel | Améliorations nécessaires |
|---------|-------------|---------------|--------------------------|
| **UNIT-A3** | Skip-link utilise i18n (pas hardcodé) | ✅ Existe | Vérifier toutes les langues supportées |
| **UNIT-B4** | Vision contient section "Principes fondamentaux" | ✅ Existe | Vérifier le contenu exact des 3 principes (titre + description) |
| **UNIT-B5** | Vision contient glossaire | ✅ Existe | Vérifier tous les termes (7 termes : vivant, SAKA, EUR, silo, compostage, alliance, gardiens) |
| **UNIT-B6** | Vision contient disclaimer | ✅ Existe | Vérifier le texte exact du disclaimer |
| **UNIT-B7** | Accueil contient note SAKA/EUR | ✅ Existe | Vérifier que la note existe ET ne contient PAS "conversion" ou "équivalence monétaire" |
| **UNIT-B8** | Texte "100% des dons nets" | ✅ Existe | Vérifier le texte exact avec "nets" ou mention de frais |

**Fichiers à créer/modifier** :

```
frontend/frontend/src/app/pages/__tests__/Home.audit-compliance.test.jsx
  → Renforcer UNIT-B7 : Vérifier présence + absence de termes interdits (ligne ~20)
  → Renforcer UNIT-B8 : Vérifier texte exact avec "nets" (ligne ~40)

frontend/frontend/src/app/pages/__tests__/Vision.audit-compliance.test.jsx
  → Renforcer UNIT-B4 : Vérifier contenu exact des 3 principes (ligne ~30)
  → Renforcer UNIT-B5 : Vérifier tous les 7 termes du glossaire (ligne ~60)

frontend/frontend/src/components/__tests__/Layout.i18n-skip-link.test.jsx
  → Renforcer UNIT-A3 : Tester toutes les langues supportées (ligne ~15)
```

**Spécifications à ajouter** :

```javascript
// UNIT-B4 : Vérifier contenu exact des 3 principes
it('B4) Section "Principes fondamentaux" contient les 3 principes avec titre ET description', () => {
  const { container } = renderWithProviders(<Vision />);
  const principlesSection = screen.getByTestId('vision-principles');
  
  // Vérifier les 3 principes
  const principles = [
    'Structure relationnelle > instrumentale',
    'Anti-accumulation',
    'Logique de cycle'
  ];
  
  principles.forEach(principle => {
    expect(principlesSection).toHaveTextContent(principle);
  });
});

// UNIT-B5 : Vérifier tous les 7 termes du glossaire
it('B5) Glossaire contient les 7 termes requis', () => {
  const { container } = renderWithProviders(<Vision />);
  const glossarySection = screen.getByTestId('vision-glossary');
  
  const requiredTerms = [
    'vivant', 'SAKA', 'EUR', 'silo', 'compostage', 'alliance', 'gardiens'
  ];
  
  requiredTerms.forEach(term => {
    expect(glossarySection).toHaveTextContent(term);
  });
});
```

---

### 3.3 NIVEAU 3 : Audit Statique Node (Grep/Règles textuelles)

**Objectif** : Vérifier les règles textuelles dans le code source (grep, regex, parsing)

**Fichier existant** : `frontend/frontend/scripts/audit-home-vision.js`

**Règles à compléter/renforcer** :

| Règle ID | Description | Status actuel | Améliorations nécessaires |
|----------|-------------|---------------|--------------------------|
| **STATIC-donation_text_nets** | "100 % des dons" doit inclure "nets" ou mention de frais | ✅ Existe | Vérifier aussi dans les fichiers JSX (pas seulement JSON) |
| **STATIC-vision_i18n_principles** | Clés i18n vision.principles_* requises | ✅ Existe | Vérifier toutes les langues (6 langues) |
| **STATIC-vision_i18n_glossary** | Clés i18n vision.glossary_* requises | ✅ Existe | Vérifier toutes les langues (6 langues) |
| **STATIC-skip_link_i18n** | Skip-link pas hardcodé FR | ✅ Existe | Vérifier que t("accessibility.skip_to_main") est utilisé |
| **STATIC-home_saka_eur_note** | Note SAKA/EUR présente | ❌ Manquant | **À CRÉER** : Vérifier présence dans Home.jsx ou locales |
| **STATIC-vision_principles_section** | Section "Principes fondamentaux" présente | ❌ Manquant | **À CRÉER** : Vérifier data-testid="vision-principles" dans Vision.jsx |
| **STATIC-vision_glossary_section** | Section glossaire présente | ❌ Manquant | **À CRÉER** : Vérifier data-testid="vision-glossary" dans Vision.jsx |
| **STATIC-vision_disclaimer** | Disclaimer citations présent | ❌ Manquant | **À CRÉER** : Vérifier data-testid="vision-citations-disclaimer" dans Vision.jsx |

**Fichiers à créer/modifier** :

```
frontend/frontend/scripts/audit-home-vision.js
  → Ajouter checkHomeSakaEurNote() (ligne ~250)
  → Ajouter checkVisionPrinciplesSection() (ligne ~280)
  → Ajouter checkVisionGlossarySection() (ligne ~310)
  → Ajouter checkVisionDisclaimer() (ligne ~340)
  → Appeler ces nouvelles fonctions dans main() (ligne ~500)
```

**Spécifications à ajouter** :

```javascript
// STATIC-home_saka_eur_note
function checkHomeSakaEurNote() {
  const ruleId = 'home_saka_eur_note';
  const rule = rules.rules.find(r => r.id === ruleId);
  if (!rule) return;
  
  let hasViolation = false;
  const violationDetails = [];
  
  // Vérifier dans Home.jsx
  const homePath = join(PAGES_DIR, 'Home.jsx');
  const homeContent = readFile(homePath);
  if (homeContent) {
    // Vérifier présence de data-testid="home-saka-eur-note" OU texte contenant "SAKA" et "EUR"
    const hasTestId = /data-testid=["']home-saka-eur-note["']/.test(homeContent);
    const hasSakaEurText = /SAKA.*EUR|EUR.*SAKA/i.test(homeContent);
    const hasForbiddenTerms = /conversion|équivalence monétaire/i.test(homeContent);
    
    if (!hasTestId && !hasSakaEurText) {
      hasViolation = true;
      violationDetails.push('Home.jsx - Note SAKA/EUR absente');
    }
    if (hasForbiddenTerms) {
      hasViolation = true;
      violationDetails.push('Home.jsx - Termes interdits (conversion, équivalence monétaire) présents');
    }
  }
  
  // Vérifier dans locales/*.json
  for (const localeFile of LOCALE_FILES) {
    const content = readFile(localeFile);
    if (!content) continue;
    
    try {
      const localeData = JSON.parse(content);
      // Vérifier clé home.saka_eur_note ou équivalent
      const hasNote = localeData.home?.saka_eur_note || 
                     (localeData.home?.soutenir_desc && 
                      /SAKA.*EUR|EUR.*SAKA/i.test(localeData.home.soutenir_desc));
      
      if (!hasNote) {
        hasViolation = true;
        violationDetails.push(`${localeFile} - Note SAKA/EUR absente`);
      }
    } catch (error) {
      // Ignorer erreurs de parsing
    }
  }
  
  checks.push({
    id: ruleId,
    ok: !hasViolation,
    details: hasViolation ? violationDetails.join('; ') : 'Note SAKA/EUR présente et conforme',
    severity: rule.severity
  });
}

// STATIC-vision_principles_section
function checkVisionPrinciplesSection() {
  const ruleId = 'vision_principles_section';
  const rule = rules.rules.find(r => r.id === ruleId);
  if (!rule) return;
  
  let hasViolation = false;
  const violationDetails = [];
  
  const visionPath = join(PAGES_DIR, 'Vision.jsx');
  const visionContent = readFile(visionPath);
  if (!visionContent) {
    checks.push({ id: ruleId, ok: false, details: 'Vision.jsx introuvable', severity: rule.severity });
    return;
  }
  
  // Vérifier data-testid="vision-principles"
  const hasTestId = /data-testid=["']vision-principles["']/.test(visionContent);
  // Vérifier section avec H2 "Principes fondamentaux"
  const hasH2Principles = /<h2[^>]*>.*Principes fondamentaux/i.test(visionContent);
  // Vérifier les 3 principes
  const hasPrinciple1 = /Structure relationnelle.*instrumentale/i.test(visionContent);
  const hasPrinciple2 = /Anti-accumulation/i.test(visionContent);
  const hasPrinciple3 = /Logique de cycle/i.test(visionContent);
  
  if (!hasTestId || !hasH2Principles) {
    hasViolation = true;
    violationDetails.push('Vision.jsx - Section "Principes fondamentaux" absente ou mal structurée');
  }
  if (!hasPrinciple1 || !hasPrinciple2 || !hasPrinciple3) {
    hasViolation = true;
    violationDetails.push('Vision.jsx - Un ou plusieurs principes manquants');
  }
  
  checks.push({
    id: ruleId,
    ok: !hasViolation,
    details: hasViolation ? violationDetails.join('; ') : 'Section "Principes fondamentaux" présente avec 3 principes',
    severity: rule.severity
  });
}

// STATIC-vision_glossary_section
function checkVisionGlossarySection() {
  const ruleId = 'vision_glossary_section';
  const rule = rules.rules.find(r => r.id === ruleId);
  if (!rule) return;
  
  let hasViolation = false;
  const violationDetails = [];
  
  const visionPath = join(PAGES_DIR, 'Vision.jsx');
  const visionContent = readFile(visionPath);
  if (!visionContent) {
    checks.push({ id: ruleId, ok: false, details: 'Vision.jsx introuvable', severity: rule.severity });
    return;
  }
  
  // Vérifier data-testid="vision-glossary"
  const hasTestId = /data-testid=["']vision-glossary["']/.test(visionContent);
  // Vérifier section avec H2 "Glossaire"
  const hasH2Glossary = /<h2[^>]*>.*Glossaire/i.test(visionContent);
  // Vérifier les 7 termes requis
  const requiredTerms = ['vivant', 'SAKA', 'EUR', 'silo', 'compostage', 'alliance', 'gardiens'];
  const missingTerms = requiredTerms.filter(term => {
    const regex = new RegExp(term, 'i');
    return !regex.test(visionContent);
  });
  
  if (!hasTestId || !hasH2Glossary) {
    hasViolation = true;
    violationDetails.push('Vision.jsx - Section "Glossaire" absente ou mal structurée');
  }
  if (missingTerms.length > 0) {
    hasViolation = true;
    violationDetails.push(`Vision.jsx - Termes manquants : ${missingTerms.join(', ')}`);
  }
  
  checks.push({
    id: ruleId,
    ok: !hasViolation,
    details: hasViolation ? violationDetails.join('; ') : 'Section "Glossaire" présente avec tous les termes requis',
    severity: rule.severity
  });
}

// STATIC-vision_disclaimer
function checkVisionDisclaimer() {
  const ruleId = 'vision_disclaimer';
  const rule = rules.rules.find(r => r.id === ruleId);
  if (!rule) return;
  
  let hasViolation = false;
  const violationDetails = [];
  
  const visionPath = join(PAGES_DIR, 'Vision.jsx');
  const visionContent = readFile(visionPath);
  if (!visionContent) {
    checks.push({ id: ruleId, ok: false, details: 'Vision.jsx introuvable', severity: rule.severity });
    return;
  }
  
  // Vérifier data-testid="vision-citations-disclaimer"
  const hasTestId = /data-testid=["']vision-citations-disclaimer["']/.test(visionContent);
  // Vérifier texte du disclaimer (citations autochtones, respect des cultures)
  const hasDisclaimerText = /citations autochtones|respect des cultures|indigenous/i.test(visionContent);
  
  if (!hasTestId || !hasDisclaimerText) {
    hasViolation = true;
    violationDetails.push('Vision.jsx - Disclaimer citations autochtones absent ou incomplet');
  }
  
  checks.push({
    id: ruleId,
    ok: !hasViolation,
    details: hasViolation ? violationDetails.join('; ') : 'Disclaimer citations autochtones présent',
    severity: rule.severity
  });
}
```

---

## 4. CHECKLIST COMPLÈTE

### 4.1 Tests E2E (Playwright)

- [x] **E2E-A1** : Lien "Soutenir" scroll vers `#soutenir` (desktop) - ✅ Existe
- [ ] **E2E-A1-MOBILE** : Lien "Soutenir" scroll vers `#soutenir` (mobile) - ❌ **À CRÉER**
- [x] **E2E-A2** : Skip-link focus et scroll vers `#main-content` - ✅ Existe
- [x] **E2E-A3** : Skip-link traduit (pas hardcodé FR) - ✅ Existe (à renforcer pour toutes les langues)
- [x] **E2E-B4** : Vision contient section "Principes fondamentaux" - ✅ Existe
- [x] **E2E-B5** : Vision contient glossaire - ✅ Existe (à renforcer pour tous les termes)
- [x] **E2E-B6** : Vision contient disclaimer - ✅ Existe
- [x] **E2E-B7** : Accueil contient note SAKA/EUR - ✅ Existe
- [x] **E2E-B8** : Texte "100% des dons nets" - ✅ Existe

### 4.2 Tests Unit (Testing Library)

- [x] **UNIT-A3** : Skip-link utilise i18n - ✅ Existe (à renforcer pour toutes les langues)
- [x] **UNIT-B4** : Vision contient section "Principes fondamentaux" - ✅ Existe (à renforcer pour contenu exact)
- [x] **UNIT-B5** : Vision contient glossaire - ✅ Existe (à renforcer pour tous les termes)
- [x] **UNIT-B6** : Vision contient disclaimer - ✅ Existe
- [x] **UNIT-B7** : Accueil contient note SAKA/EUR - ✅ Existe (à renforcer pour absence de termes interdits)
- [x] **UNIT-B8** : Texte "100% des dons nets" - ✅ Existe

### 4.3 Audit Statique (Node.js)

- [x] **STATIC-donation_text_nets** : "100 % des dons" avec "nets" - ✅ Existe
- [x] **STATIC-vision_i18n_principles** : Clés i18n vision.principles_* - ✅ Existe
- [x] **STATIC-vision_i18n_glossary** : Clés i18n vision.glossary_* - ✅ Existe
- [x] **STATIC-skip_link_i18n** : Skip-link pas hardcodé - ✅ Existe
- [ ] **STATIC-home_saka_eur_note** : Note SAKA/EUR présente - ❌ **À CRÉER**
- [ ] **STATIC-vision_principles_section** : Section "Principes fondamentaux" - ❌ **À CRÉER**
- [ ] **STATIC-vision_glossary_section** : Section glossaire - ❌ **À CRÉER**
- [ ] **STATIC-vision_disclaimer** : Disclaimer citations - ❌ **À CRÉER**

---

## 5. FICHIERS À CRÉER/MODIFIER

### 5.1 Fichiers à modifier

1. **`frontend/frontend/e2e/audit-compliance-accueil-vision.spec.js`**
   - Ajouter test E2E-A1-MOBILE (ligne ~50)
   - Renforcer E2E-A3 pour toutes les langues (ligne ~80)
   - Renforcer E2E-B5 pour tous les termes du glossaire (ligne ~150)

2. **`frontend/frontend/src/app/pages/__tests__/Home.audit-compliance.test.jsx`**
   - Renforcer UNIT-B7 : Vérifier absence de termes interdits (ligne ~20)
   - Renforcer UNIT-B8 : Vérifier texte exact avec "nets" (ligne ~40)

3. **`frontend/frontend/src/app/pages/__tests__/Vision.audit-compliance.test.jsx`**
   - Renforcer UNIT-B4 : Vérifier contenu exact des 3 principes (ligne ~30)
   - Renforcer UNIT-B5 : Vérifier tous les 7 termes du glossaire (ligne ~60)

4. **`frontend/frontend/src/components/__tests__/Layout.i18n-skip-link.test.jsx`**
   - Renforcer UNIT-A3 : Tester toutes les langues supportées (ligne ~15)

5. **`frontend/frontend/scripts/audit-home-vision.js`**
   - Ajouter `checkHomeSakaEurNote()` (ligne ~250)
   - Ajouter `checkVisionPrinciplesSection()` (ligne ~280)
   - Ajouter `checkVisionGlossarySection()` (ligne ~310)
   - Ajouter `checkVisionDisclaimer()` (ligne ~340)
   - Appeler ces nouvelles fonctions dans `main()` (ligne ~500)

### 5.2 Fichiers à créer

Aucun nouveau fichier à créer (tous les fichiers de tests existent déjà).

---

## 6. SPÉCIFICATIONS DÉTAILLÉES

### 6.1 E2E-A1-MOBILE

**Fichier** : `frontend/frontend/e2e/audit-compliance-accueil-vision.spec.js`
**Ligne** : ~50 (après E2E-A1)

```javascript
test('A1-MOBILE) Le lien "Soutenir" scroll vers #soutenir (mobile)', async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE
  await page.goto('/');
  await page.waitForLoadState('networkidle');
  
  const initialScrollY = await page.evaluate(() => window.scrollY);
  const soutenirLink = page.locator('a[href="#soutenir"]').first();
  await expect(soutenirLink).toBeVisible({ timeout: 5000 });
  
  await soutenirLink.click();
  await page.waitForFunction(() => window.location.hash === '#soutenir', { timeout: 5000 });
  await waitForElementInViewport(page, '#soutenir', { timeout: 5000 });
  
  const finalScrollY = await page.evaluate(() => window.scrollY);
  expect(finalScrollY).toBeGreaterThan(initialScrollY);
  await expect(page).toHaveURL(/#soutenir/);
});
```

### 6.2 STATIC-home_saka_eur_note

**Fichier** : `frontend/frontend/scripts/audit-home-vision.js`
**Ligne** : ~250 (après `checkSkipLinkHardcoded`)

```javascript
function checkHomeSakaEurNote() {
  const ruleId = 'home_saka_eur_note';
  const rule = rules.rules.find(r => r.id === ruleId);
  if (!rule) {
    checks.push({ id: ruleId, ok: false, details: 'Règle non trouvée dans rules.json' });
    return;
  }
  
  console.log('🔍 Vérification : Note SAKA/EUR sur Accueil...');
  let hasViolation = false;
  const violationDetails = [];
  
  // Vérifier dans Home.jsx
  const homePath = join(PAGES_DIR, 'Home.jsx');
  const homeContent = readFile(homePath);
  if (homeContent) {
    const hasTestId = /data-testid=["']home-saka-eur-note["']/.test(homeContent);
    const hasSakaEurText = /SAKA.*EUR|EUR.*SAKA/i.test(homeContent);
    const hasForbiddenTerms = /conversion|équivalence monétaire/i.test(homeContent);
    
    if (!hasTestId && !hasSakaEurText) {
      hasViolation = true;
      violationDetails.push('Home.jsx - Note SAKA/EUR absente');
    }
    if (hasForbiddenTerms) {
      hasViolation = true;
      violationDetails.push('Home.jsx - Termes interdits présents');
    }
  }
  
  // Vérifier dans locales/*.json
  for (const localeFile of LOCALE_FILES) {
    const content = readFile(localeFile);
    if (!content) continue;
    
    try {
      const localeData = JSON.parse(content);
      const hasNote = localeData.home?.saka_eur_note || 
                     (localeData.home?.soutenir_desc && 
                      /SAKA.*EUR|EUR.*SAKA/i.test(localeData.home.soutenir_desc));
      
      if (!hasNote) {
        hasViolation = true;
        const relativePath = localeFile.replace(ROOT_DIR + '/', '');
        violationDetails.push(`${relativePath} - Note SAKA/EUR absente`);
      }
    } catch (error) {
      // Ignorer erreurs de parsing
    }
  }
  
  checks.push({
    id: ruleId,
    ok: !hasViolation,
    details: hasViolation ? violationDetails.join('; ') : 'Note SAKA/EUR présente et conforme',
    severity: rule.severity
  });
}
```

---

## 7. RÉSUMÉ

### 7.1 Couverture actuelle

- **E2E** : 8/9 tests (89%) - Manque test mobile
- **Unit** : 10/10 tests (100%) - Tous existent, certains à renforcer
- **Audit statique** : 4/8 règles (50%) - 4 règles manquantes

### 7.2 Actions prioritaires

1. **CRITIQUE** : Ajouter 4 règles d'audit statique manquantes
2. **ÉLEVÉ** : Ajouter test E2E mobile (E2E-A1-MOBILE)
3. **MOYEN** : Renforcer tests existants (langues multiples, termes complets)

### 7.3 Fichiers à modifier

- `e2e/audit-compliance-accueil-vision.spec.js` : +1 test, +2 renforcements
- `scripts/audit-home-vision.js` : +4 fonctions
- Tests unitaires : +4 renforcements

---

**Date de création** : 2025-01-27  
**Statut** : Plan complet, prêt pour implémentation
