# Statut Public "EGOEJO Compliant" - Pages Accueil/Vision

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Actif

---

## 📋 Présentation

Le statut public "EGOEJO Compliant" pour les pages Accueil et Vision permet de vérifier automatiquement la conformité de ces pages aux exigences de l'audit quadripartite strict.

---

## 📄 Fichier de Règles

**Fichier** : `docs/egoejo_compliance/home-vision.rules.json`

**Structure** :
```json
{
  "version": "1.0",
  "rules": [
    {
      "id": "donation_text_nets",
      "description": "...",
      "test_ref": "...",
      "severity": "critical" | "high" | "medium"
    }
  ]
}
```

**Règles définies** :
1. `donation_text_nets` : "100 % des dons" doit inclure "nets" ou mention de frais
2. `vision_i18n_principles` : Clés i18n vision.principles_* requises
3. `vision_i18n_glossary` : Clés i18n vision.glossary_* requises
4. `skip_link_i18n` : Skip-link ne doit pas être hardcodé en FR
5. `home_saka_eur_note` : Note explicite SAKA/EUR sur Accueil
6. `vision_principles_section` : Section "Principes fondamentaux" sur Vision
7. `vision_glossary_section` : Glossaire sur Vision
8. `vision_disclaimer` : Disclaimer citations autochtones
9. `navigation_hash_soutenir` : Navigation hash #soutenir
10. `skip_link_functionality` : Fonctionnalité skip-link

---

## 🔧 Script d'Audit

**Fichier** : `frontend/frontend/scripts/audit-home-vision.js`

**Usage** :
```bash
npm run audit:home-vision
```

**Sortie JSON** :
```json
{
  "status": "compliant" | "conditional" | "non-compliant",
  "checks": [
    {
      "id": "donation_text_nets",
      "ok": true | false,
      "details": "...",
      "severity": "critical" | "high" | "medium"
    }
  ],
  "timestamp": "2025-01-27T12:00:00Z",
  "version": "1.0"
}
```

**Fichier généré** : `frontend/frontend/compliance-status.json`

---

## 🎨 Badges SVG

**Emplacement** : `frontend/frontend/public/badges/`

**Badges disponibles** :
- `egoejo-compliant.svg` : Statut compliant (vert)
- `egoejo-conditional.svg` : Statut conditional (orange)
- `egoejo-non-compliant.svg` : Statut non-compliant (rouge)
- `egoejo-compliant-current.svg` : Badge actuel (copié selon le statut)

**Usage** :
```bash
npm run audit:home-vision:badge
```

---

## 🚀 Intégration CI

**Workflow** : `.github/workflows/audit-home-vision.yml`

**Étapes** :
1. Exécution du script d'audit (`npm run audit:home-vision`)
2. Parsing du statut JSON
3. Copie du badge approprié
4. **Échec si `status != "compliant"`**

**Comportement** :
- ✅ `status === "compliant"` : CI passe
- ⚠️ `status === "conditional"` : CI passe (mais warning)
- ❌ `status === "non-compliant"` : CI échoue (bloquant)

---

## 📊 Statuts de Conformité

### Compliant

**Condition** : Toutes les règles `critical` et `high` sont respectées.

**Badge** : 🟢 Vert

**CI** : ✅ Passe

---

### Conditional

**Condition** : Toutes les règles `critical` passent, mais certaines règles `high` ou `medium` échouent.

**Badge** : 🟡 Orange

**CI** : ✅ Passe (mais warning)

**Note** : Peut être bloquant si `FAIL_ON_CONDITIONAL=true` est défini.

---

### Non-Compliant

**Condition** : Au moins une règle `critical` échoue.

**Badge** : 🔴 Rouge

**CI** : ❌ Échoue (bloquant)

---

## 🔍 Vérification Manuelle

### Local

```bash
cd frontend/frontend
npm run audit:home-vision
cat compliance-status.json
```

### Badge

```bash
cd frontend/frontend
npm run audit:home-vision:badge
ls public/badges/egoejo-compliant-current.svg
```

---

## 📚 Documentation Associée

- [AUDIT_QUADRIPARTITE_STRICT_ACCUEIL_VISION.md](../../reports/AUDIT_QUADRIPARTITE_STRICT_ACCUEIL_VISION.md)
- [TESTS_AUDIT_COMPLIANCE_ACCUEIL_VISION.md](../../../frontend/frontend/TESTS_AUDIT_COMPLIANCE_ACCUEIL_VISION.md)
- [home-vision.rules.json](./home-vision.rules.json)

---

**Dernière mise à jour** : 2025-01-27

