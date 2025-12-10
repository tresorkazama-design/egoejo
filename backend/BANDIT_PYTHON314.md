# ⚠️ Compatibilité Bandit avec Python 3.14

**Date** : 2025-12-09  
**Problème** : Bandit 1.8.6 n'est pas encore complètement compatible avec Python 3.14

---

## 🔍 Problème Identifié

Lors de l'exécution de Bandit avec Python 3.14, on peut rencontrer l'erreur suivante :

```
AttributeError: module 'ast' has no attribute 'Num'
```

Cette erreur est due à des changements dans le module `ast` de Python 3.14 qui ne sont pas encore pris en charge par Bandit 1.8.6.

---

## ✅ Solutions

### Option 1 : Utiliser Python 3.11 ou 3.12 pour les audits (Recommandé)

Créer un environnement virtuel avec Python 3.11/3.12 spécifiquement pour les audits de sécurité :

```powershell
# Installer Python 3.12 (si pas déjà installé)
# Télécharger depuis https://www.python.org/downloads/

# Créer un environnement virtuel avec Python 3.12
py -3.12 -m venv venv-audit

# Activer l'environnement
.\venv-audit\Scripts\Activate.ps1

# Installer Bandit et Safety
pip install bandit safety

# Exécuter Bandit
bandit -r core/ -ll

# Exécuter Safety
safety check
```

### Option 2 : Attendre une mise à jour de Bandit

Bandit devrait être mis à jour pour supporter Python 3.14 dans une future version. Surveiller :
- [Bandit GitHub](https://github.com/PyCQA/bandit)
- [Bandit PyPI](https://pypi.org/project/bandit/)

### Option 3 : Utiliser des alternatives

#### Semgrep (Recommandé)

```powershell
# Installer Semgrep
pip install semgrep

# Exécuter Semgrep
semgrep --config=auto backend/core/
```

#### SonarQube / SonarLint

- SonarLint : Extension pour IDE
- SonarQube : Solution complète d'analyse de code

---

## 📊 État Actuel

- **Bandit Version** : 1.8.6
- **Python Version** : 3.14.0
- **Compatibilité** : ⚠️ Partielle (erreurs avec certaines fonctionnalités)

---

## 🔍 Vérification

Pour vérifier si Bandit fonctionne avec votre version de Python :

```powershell
cd backend
python --version
bandit --version
bandit -r core/ -ll
```

Si vous obtenez des erreurs `AttributeError: module 'ast' has no attribute 'Num'`, utilisez l'Option 1.

---

## 📝 Notes

- Les vulnérabilités détectées par Bandit dans les bibliothèques externes ne sont pas critiques (elles sont dans les dépendances, pas dans votre code)
- Le code source du projet (`core/` et `config/`) ne contient pas de vulnérabilités détectées par Bandit
- Les audits de sécurité peuvent être effectués avec Python 3.11/3.12 sans impact sur le développement

---

## ✅ Recommandation

**Utiliser Python 3.12 pour les audits de sécurité** tout en continuant à développer avec Python 3.14. Cela permet de :
- Effectuer des audits de sécurité complets
- Continuer à utiliser Python 3.14 pour le développement
- Éviter les problèmes de compatibilité

---

**Dernière mise à jour** : 2025-12-09

