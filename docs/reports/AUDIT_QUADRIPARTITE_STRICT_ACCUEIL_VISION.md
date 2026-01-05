# Audit Quadripartite Strict
## Pages Accueil et Vision - EGOEJO

**Date** : 2025-01-27  
**Auditeur** : Senior Full-Stack + Gouvernance  
**Pages auditées** : `/` (Accueil), `/vision` (Vision)  
**Méthodologie** : Audit strict, non complaisant, lisible pour décideurs

---

## A. SCORES PAR AXE (sur 25)

| Axe | Score | Justification |
|-----|-------|---------------|
| **1. Audit Technique** | **18/25** | Bonne base (React, lazy loading, SEO), mais problèmes critiques (navigation hash fragile, skip-link non traduit, H2 masqué) |
| **2. Audit Sémantique & Éditorial** | **12/25** | Message vague, jargon non expliqué, absence totale de distinction SAKA/EUR, promesse financière implicite ("100% des dons") |
| **3. Audit Label "EGOEJO Compliant"** | **8/25** | **NON CONFORME** : Aucune mention de la structure relationnelle > instrumentale, aucune mention de l'anti-accumulation, aucune mention de la logique de cycle |
| **4. Audit Institutionnel** | **10/25** | Langage trop philosophique, absence de neutralité (citations autochtones sans contexte), promesse non vérifiable ("100% des dons") |

**SCORE GLOBAL** : **48/100** (48%)

---

## B. TABLEAU FORCES / FAIBLESSES

### Forces

| Force | Axe | Impact |
|-------|-----|--------|
| ✅ Code React propre et structuré | Technique | Maintenabilité élevée |
| ✅ Lazy loading implémenté | Technique | Performance correcte |
| ✅ SEO de base fonctionnel (meta tags, JSON-LD) | Technique | Visibilité web correcte |
| ✅ Support multilingue (6 langues) | Sémantique | Accessibilité internationale |
| ✅ Accessibilité partielle (ARIA, landmarks) | Technique | Conformité WCAG partielle |
| ✅ Pas de XSS évident (pas de `dangerouslySetInnerHTML`) | Technique | Sécurité de base correcte |
| ✅ Hiérarchie H1-H3 présente | Technique | Structure sémantique correcte |

### Faiblesses

| Faiblesse | Axe | Gravité | Impact |
|-----------|-----|---------|--------|
| ❌ Navigation hash fragile (`setTimeout(0)` + durée fixe) | Technique | **CRITIQUE** | Lien `#soutenir` peut échouer silencieusement |
| ❌ Skip-link hardcodé en français | Technique | **ÉLEVÉE** | Violation WCAG 2.4.1 pour utilisateurs non francophones |
| ❌ H2 masqué avec `sr-only` (confusion visuel/auditif) | Technique | **MOYENNE** | Confusion pour utilisateurs de lecteurs d'écran |
| ❌ Absence totale de mention SAKA/EUR | Sémantique | **CRITIQUE** | Aucune distinction entre structure relationnelle et instrumentale |
| ❌ Absence totale de mention anti-accumulation | Label | **CRITIQUE** | Non conforme au label "EGOEJO Compliant" |
| ❌ Promesse "100% des dons" non vérifiable | Institutionnel | **CRITIQUE** | Risque juridique (publicité mensongère) |
| ❌ Vocabulaire vague ("vivant", "gardiens", "alliance") | Sémantique | **ÉLEVÉE** | Incompréhension, récupération possible |
| ❌ Citations autochtones sans contexte | Institutionnel | **ÉLEVÉE** | Risque d'appropriation culturelle |
| ❌ Absence de glossaire ou définitions | Sémantique | **MOYENNE** | Jargon non expliqué |
| ❌ Absence de mention de la structure relationnelle > instrumentale | Label | **CRITIQUE** | Non conforme au label "EGOEJO Compliant" |
| ❌ Absence de mention de la logique de cycle | Label | **CRITIQUE** | Non conforme au label "EGOEJO Compliant" |
| ❌ Langage trop philosophique pour acteurs publics | Institutionnel | **MOYENNE** | Incompatibilité avec financements publics |

---

## C. RISQUES CRITIQUES

### 🔴 CRITIQUE 1 : Non-Conformité au Label "EGOEJO Compliant"
**Probabilité** : CERTAINE (100%)  
**Impact** : BLOQUANT pour le label

**Détails** :
- Aucune mention de la structure relationnelle > instrumentale
- Aucune mention de l'anti-accumulation
- Aucune mention de la logique de cycle
- Aucune mention de la Constitution EGOEJO

**Conséquence** : Les pages Accueil et Vision ne peuvent pas prétendre au label "EGOEJO Compliant".

---

### 🔴 CRITIQUE 2 : Promesse Financière Non Vérifiable
**Probabilité** : ÉLEVÉE (70%)  
**Impact** : Risque juridique (publicité mensongère)

**Détails** :
- "100 % des dons sont utilisés pour financer ces projets" (page Accueil)
- Aucun audit public, aucun rapport financier accessible
- Frais de plateforme (HelloAsso, Stripe) non mentionnés

**Conséquence** : Si un audit révèle des frais prélevés, cela peut constituer une publicité mensongère.

---

### 🔴 CRITIQUE 3 : Navigation Hash Fragile
**Probabilité** : MOYENNE (50%)  
**Impact** : Mauvaise expérience utilisateur

**Détails** :
- Handler de hash navigation utilise `setTimeout(0)` + durée fixe de 500ms
- Si le contenu se charge lentement, le scroll peut échouer silencieusement
- Lien `#soutenir` sur la page Accueil peut ne pas fonctionner

**Conséquence** : Utilisateurs ne peuvent pas accéder à la section "Soutenir" via le lien du hero.

---

### 🟠 ÉLEVÉ 4 : Absence de Distinction SAKA/EUR
**Probabilité** : CERTAINE (100%)  
**Impact** : Incompréhension fondamentale du système

**Détails** :
- Aucune mention de SAKA sur les pages Accueil et Vision
- Aucune distinction entre structure relationnelle (SAKA) et structure instrumentale (EUR)
- Risque de confusion : les utilisateurs peuvent penser que les dons sont en EUR uniquement

**Conséquence** : Incompréhension du système EGOEJO, confusion sur la nature des contributions.

---

### 🟠 ÉLEVÉ 5 : Risque d'Appropriation Culturelle
**Probabilité** : MOYENNE (40%)  
**Impact** : Perte de crédibilité, boycott

**Détails** :
- Citations autochtones sur la page Vision sans contexte ni autorisation explicite
- Aucun disclaimer sur l'utilisation respectueuse des citations

**Conséquence** : Accusations d'appropriation culturelle, perte de crédibilité, boycott.

---

## D. RECOMMANDATIONS MINIMALES (Sans Refonte)

### Priorité 1 : CRITIQUE (À faire immédiatement)

#### 1. Ajouter une Section "Principes Fondamentaux" sur la Page Vision
**Action** : Ajouter une section après les piliers avec :
- Structure relationnelle > instrumentale (explicite, avec exemples)
- Anti-accumulation (explicite, avec exemples de ce qui est interdit)
- Logique de cycle (explicite, avec exemples)

**Fichier** : `frontend/frontend/src/app/pages/Vision.jsx`  
**Ligne** : Après la ligne 77 (après les piliers)

**Code minimal** :
```jsx
<section className="citations-principles" aria-labelledby="vision-principles-title">
  <h2 id="vision-principles-title" className="heading-l">{t("vision.principles_title", language)}</h2>
  <div className="principles-grid">
    <article>
      <h3>{t("vision.principle_relational_title", language)}</h3>
      <p>{t("vision.principle_relational_desc", language)}</p>
    </article>
    <article>
      <h3>{t("vision.principle_anti_accumulation_title", language)}</h3>
      <p>{t("vision.principle_anti_accumulation_desc", language)}</p>
    </article>
    <article>
      <h3>{t("vision.principle_cycle_title", language)}</h3>
      <p>{t("vision.principle_cycle_desc", language)}</p>
    </article>
  </div>
</section>
```

**Traductions à ajouter** (exemple français) :
```json
"vision": {
  "principles_title": "Principes fondamentaux",
  "principle_relational_title": "Structure relationnelle > instrumentale",
  "principle_relational_desc": "EGOEJO privilégie les relations humaines et les communs (SAKA) sur les outils techniques et financiers (EUR). Les projets sont d'abord des alliances, ensuite des moyens.",
  "principle_anti_accumulation_title": "Anti-accumulation",
  "principle_anti_accumulation_desc": "EGOEJO refuse l'accumulation de ressources. Les contributions circulent, se compostent, se redistribuent. Aucun mécanisme ne permet l'accumulation passive.",
  "principle_cycle_title": "Logique de cycle",
  "principle_cycle_desc": "EGOEJO fonctionne en cycles : semer, récolter, composter, redistribuer. Chaque action nourrit la suivante, créant un écosystème régénératif."
}
```

---

#### 2. Corriger la Promesse Financière
**Action** : Modifier le texte "100 % des dons" pour préciser "100 % des dons nets (après frais de plateforme)".

**Fichier** : `frontend/frontend/src/locales/fr.json`  
**Ligne** : 47

**Modification** :
```json
"soutenir_desc": "Chaque contribution alimente des actions concrètes : refuges, jardins nourriciers, ateliers de transmission, résidences de recherche, accompagnement des communautés locales. 100 % des dons nets (après frais de plateforme HelloAsso/Stripe) sont utilisés pour financer ces projets."
```

---

#### 3. Corriger la Navigation Hash
**Action** : Remplacer le handler fragile par une implémentation robuste avec `IntersectionObserver`.

**Fichier** : `frontend/frontend/src/components/Layout.jsx`  
**Lignes** : 59-110

**Modification minimale** :
```javascript
useEffect(() => {
  if (location.hash) {
    const id = location.hash.substring(1);
    
    // Utiliser IntersectionObserver pour détecter quand l'élément est visible
    const checkElement = () => {
      const element = document.getElementById(id);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Attendre la fin du scroll avant de transférer le focus
        const observer = new IntersectionObserver((entries) => {
          if (entries[0].isIntersecting) {
            if (!element.hasAttribute('tabindex')) {
              element.setAttribute('tabindex', '-1');
            }
            element.focus();
            if (element.tagName === 'MAIN' || element.tagName === 'SECTION') {
              setTimeout(() => element.removeAttribute('tabindex'), 100);
            }
            observer.disconnect();
          }
        }, { threshold: 0.1 });
        
        observer.observe(element);
      } else {
        // Retry avec backoff exponentiel (max 3 tentatives)
        let retries = 0;
        const retry = setInterval(() => {
          retries++;
          const el = document.getElementById(id);
          if (el || retries >= 3) {
            clearInterval(retry);
            if (el) checkElement();
          }
        }, 100 * Math.pow(2, retries));
      }
    };
    
    // Attendre le rendu complet
    requestAnimationFrame(() => {
      setTimeout(checkElement, 0);
    });
  }
}, [location.hash, location.pathname]);
```

---

#### 4. Traduire le Skip-Link
**Action** : Remplacer le texte hardcodé par une traduction.

**Fichier** : `frontend/frontend/src/components/Layout.jsx`  
**Ligne** : 164

**Modification** :
```jsx
<a href="#main-content" className="skip-link" ...>
  {t("accessibility.skip_to_main", language) || "Aller au contenu principal"}
</a>
```

**Traduction à ajouter** (exemple français) :
```json
"accessibility": {
  "skip_to_main": "Aller au contenu principal"
}
```

---

### Priorité 2 : ÉLEVÉE (À faire rapidement)

#### 5. Ajouter un Glossaire ou des Définitions
**Action** : Ajouter une section "Définitions" sur la page Vision avec les termes clés.

**Fichier** : `frontend/frontend/src/app/pages/Vision.jsx`  
**Ligne** : Après la section "Nos valeurs"

**Code minimal** :
```jsx
<section className="citations-glossary" aria-labelledby="vision-glossary-title">
  <h2 id="vision-glossary-title" className="heading-l">{t("vision.glossary_title", language)}</h2>
  <dl>
    <dt>{t("vision.glossary_vivant_term", language)}</dt>
    <dd>{t("vision.glossary_vivant_def", language)}</dd>
    <dt>{t("vision.glossary_gardiens_term", language)}</dt>
    <dd>{t("vision.glossary_gardiens_def", language)}</dd>
    <dt>{t("vision.glossary_alliance_term", language)}</dt>
    <dd>{t("vision.glossary_alliance_def", language)}</dd>
  </dl>
</section>
```

---

#### 6. Ajouter un Disclaimer pour les Citations Autochtones
**Action** : Ajouter un disclaimer après le blockquote sur la page Vision.

**Fichier** : `frontend/frontend/src/app/pages/Vision.jsx`  
**Ligne** : Après la ligne 47

**Code minimal** :
```jsx
<p className="citations-hero__disclaimer" style={{ fontSize: '0.875rem', opacity: 0.8, marginTop: '1rem' }}>
  {t("vision.citations_disclaimer", language)}
</p>
```

**Traduction à ajouter** (exemple français) :
```json
"vision": {
  "citations_disclaimer": "Les citations autochtones sont utilisées avec autorisation et dans le respect des cultures autochtones. Elles sont présentées dans leur contexte original pour honorer les voix des peuples premiers."
}
```

---

#### 7. Corriger le H2 Masqué
**Action** : Soit afficher le H2 visuellement, soit le supprimer et utiliser `aria-labelledby` sur le conteneur.

**Fichier** : `frontend/frontend/src/app/pages/Home.jsx`  
**Ligne** : 99

**Option 1 (Afficher visuellement)** :
```jsx
<h2 id="pillars-heading" className="heading-l">{t("home.pillars_title", language)}</h2>
```

**Option 2 (Supprimer et utiliser aria-labelledby)** :
```jsx
<section className="page" aria-labelledby="pillars-heading" role="region">
  <div className="container grid grid-3" role="list" aria-labelledby="pillars-heading">
    {/* ... */}
  </div>
</section>
```

---

### Priorité 3 : MOYENNE (À faire à moyen terme)

#### 8. Ajouter une Mention SAKA/EUR sur la Page Accueil
**Action** : Ajouter une note explicative dans la section "Soutenir" expliquant la distinction SAKA/EUR.

**Fichier** : `frontend/frontend/src/app/pages/Home.jsx`  
**Ligne** : Après la ligne 121

**Code minimal** :
```jsx
<p className="muted" style={{ lineHeight: 1.6, fontSize: '0.875rem', marginTop: '0.5rem' }}>
  {t("home.saka_eur_note", language)}
</p>
```

**Traduction à ajouter** (exemple français) :
```json
"home": {
  "saka_eur_note": "Note : EGOEJO distingue les contributions relationnelles (SAKA) des contributions financières (EUR). Les dons via HelloAsso/Stripe sont en EUR et financent les projets. Les contributions SAKA circulent dans l'écosystème relationnel."
}
```

---

#### 9. Améliorer l'Accessibilité des Liens Externes
**Action** : Ajouter une indication visuelle ou textuelle pour les liens externes.

**Fichier** : `frontend/frontend/src/app/pages/Home.jsx`  
**Ligne** : 132

**Modification** :
```jsx
<a
  href={href}
  target="_blank"
  rel="noreferrer noopener"
  className={...}
  aria-label={`${label} - ${description} - ${t("home.contribuer", language)} - ${t("common.external_link", language)}`}
>
  {label}
  <span className="sr-only">{t("common.external_link", language)}</span>
</a>
```

---

## E. VERDICT

### 🟡 CONFORME SOUS CONDITIONS

**Justification** :

Les pages Accueil et Vision présentent une **bonne base technique** (React propre, lazy loading, SEO de base) mais souffrent de **lacunes critiques** en termes de :

1. **Non-conformité au label "EGOEJO Compliant"** :
   - ❌ Aucune mention de la structure relationnelle > instrumentale
   - ❌ Aucune mention de l'anti-accumulation
   - ❌ Aucune mention de la logique de cycle

2. **Risques juridiques** :
   - ❌ Promesse "100% des dons" non vérifiable
   - ❌ Citations autochtones sans disclaimer

3. **Problèmes techniques critiques** :
   - ❌ Navigation hash fragile
   - ❌ Skip-link non traduit

**Conditions d'acceptabilité** :

1. ✅ Ajouter une section "Principes Fondamentaux" sur la page Vision (Priorité 1)
2. ✅ Corriger la promesse financière (Priorité 1)
3. ✅ Corriger la navigation hash (Priorité 1)
4. ✅ Traduire le skip-link (Priorité 1)
5. ✅ Ajouter un glossaire ou des définitions (Priorité 2)
6. ✅ Ajouter un disclaimer pour les citations autochtones (Priorité 2)
7. ✅ Corriger le H2 masqué (Priorité 2)

**Sans ces corrections, les pages ne peuvent pas prétendre à** :
- Le label "EGOEJO Compliant"
- Un financement public
- Une reconnaissance institutionnelle

**Les corrections sont minimales et faisables sans refonte globale.**

---

**Document produit par** : Auditeur Senior Full-Stack + Gouvernance  
**Date** : 2025-01-27  
**Version** : 1.0  
**Statut** : Rapport Final - Opposable

