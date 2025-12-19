# 🛡️ Installation du Guardian EGOEJO

## Vue d'ensemble

Le **Guardian EGOEJO** est un système de protection automatique qui empêche techniquement toute violation de la Constitution EGOEJO.

### Composants

1. **PR Bot GitHub Actions** : Vérifie automatiquement chaque Pull Request
2. **Pre-commit Hook** : Vérifie chaque commit local
3. **Constitution EGOEJO** : Documentation des règles absolues

---

## 🚀 Installation Rapide

### Linux / macOS

```bash
# Installer les hooks
./scripts/install-guardian-hooks.sh
```

### Windows (PowerShell)

```powershell
# Créer le hook pre-commit manuellement
Copy-Item .git/hooks/pre-commit-egoejo-guardian .git/hooks/pre-commit
```

---

## 📋 Vérifications Effectuées

Le Guardian vérifie automatiquement :

1. ✅ **Absence de conversion SAKA ↔ EUR**
   - Détecte : `convert.*saka.*eur`, `saka.*to.*eur`, `saka.*exchange.*rate`
   - **Action** : Bloque PR/commit

2. ✅ **Absence de rendement financier sur SAKA**
   - Détecte : `saka.*roi`, `saka.*yield`, `saka.*interest`, `saka.*dividend`
   - **Action** : Bloque PR/commit

3. ✅ **Priorité de la structure relationnelle (SAKA)**
   - Détecte : `disable.*saka`, `ENABLE_SAKA.*=.*False`
   - **Action** : Bloque PR/commit

4. ✅ **Anti-accumulation SAKA**
   - Détecte : `disable.*compost`, `skip.*compost`, `bypass.*compost`
   - **Action** : Bloque PR/commit

5. ✅ **Cycle SAKA incompressible**
   - Détecte : `skip.*saka.*cycle`, `compost.*without.*silo`
   - **Action** : Bloque PR/commit

---

## 🔧 Configuration

### GitHub Actions

Le PR Bot est automatiquement activé pour :
- Pull Requests vers `main` et `develop`
- Pushes vers `main` et `develop`

**Fichier** : `.github/workflows/pr-bot-egoejo-guardian.yml`

### Pre-commit Hook

Le hook est activé automatiquement après installation.

**Fichier** : `.git/hooks/pre-commit`

---

## 🚨 En Cas de Violation

### PR Bot

Si une violation est détectée dans une PR :
1. ❌ La PR est **bloquée**
2. 📝 Un commentaire détaille la violation
3. 🔍 Lien vers la Constitution EGOEJO

### Pre-commit Hook

Si une violation est détectée dans un commit :
1. ❌ Le commit est **refusé**
2. 📝 Message d'erreur détaillé
3. 🔍 Lien vers la Constitution EGOEJO

---

## 📚 Documentation

- **Constitution EGOEJO** : `docs/architecture/CONSTITUTION_EGOEJO.md`
- **Règles Absolues** : Voir section "RÈGLES ABSOLUES"
- **Exemples de Violations** : Voir section "EXEMPLES DE VIOLATIONS"

---

## ✅ Vérification de l'Installation

### Vérifier PR Bot

1. Créer une PR avec du code non conforme
2. Vérifier que la PR est bloquée par le Guardian

### Vérifier Pre-commit Hook

```bash
# Tester avec un commit non conforme
echo "def convert_saka_to_eur(amount): pass" >> test_violation.py
git add test_violation.py
git commit -m "Test violation"  # Devrait être bloqué
```

---

## 🛠️ Dépannage

### Le hook ne se déclenche pas

**Linux/macOS** :
```bash
chmod +x .git/hooks/pre-commit
```

**Windows** :
- Vérifier que Git Bash est utilisé (pas PowerShell pour les hooks)
- Ou utiliser le script d'installation

### Le PR Bot ne fonctionne pas

1. Vérifier que le workflow est activé dans GitHub
2. Vérifier les permissions GitHub Actions
3. Consulter les logs dans l'onglet "Actions"

---

**Le Guardian EGOEJO rend la trahison du projet techniquement impossible.**

