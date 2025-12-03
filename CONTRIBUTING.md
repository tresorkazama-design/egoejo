# Guide de Contribution - EGOEJO

Merci de votre intérêt pour contribuer au projet EGOEJO ! Ce guide vous aidera à comprendre comment contribuer efficacement.

---

## 📋 Table des Matières

1. [Code de Conduite](#code-de-conduite)
2. [Comment Contribuer](#comment-contribuer)
3. [Processus de Développement](#processus-de-développement)
4. [Standards de Code](#standards-de-code)
5. [Tests](#tests)
6. [Documentation](#documentation)
7. [Pull Requests](#pull-requests)

---

## 🤝 Code de Conduite

- Soyez respectueux et inclusif
- Acceptez les critiques constructives
- Focalisez-vous sur ce qui est meilleur pour la communauté
- Montrez de l'empathie envers les autres membres

---

## 🚀 Comment Contribuer

### Signaler un Bug

1. Vérifiez que le bug n'a pas déjà été signalé
2. Créez une issue avec :
   - Description claire du problème
   - Étapes pour reproduire
   - Comportement attendu vs réel
   - Environnement (OS, navigateur, versions)

### Proposer une Fonctionnalité

1. Vérifiez que la fonctionnalité n'existe pas déjà
2. Créez une issue avec :
   - Description de la fonctionnalité
   - Cas d'usage
   - Bénéfices pour les utilisateurs

### Contribuer au Code

1. Fork le projet
2. Créez une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout de ma fonctionnalité'`)
4. Push vers la branche (`git push origin feature/ma-fonctionnalite`)
5. Ouvrez une Pull Request

---

## 💻 Processus de Développement

### Prérequis

- Node.js ≥ 18
- Python 3.11+
- PostgreSQL 15+ (optionnel, SQLite par défaut)
- Redis 6+ (pour WebSockets)

### Configuration Locale

1. **Cloner le projet** :
```bash
git clone https://github.com/votre-org/egoejo.git
cd egoejo
```

2. **Backend** :
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.template .env
# Éditer .env avec vos valeurs
python manage.py migrate
python manage.py runserver
```

3. **Frontend** :
```bash
cd frontend/frontend
npm install
npm run dev
```

---

## 📝 Standards de Code

### Frontend (React/JavaScript)

- **ESLint** : Le projet utilise ESLint avec règles strictes
- **Formatage** : Utilisez Prettier (si configuré) ou suivez le style existant
- **Noms** : 
  - Composants : PascalCase (`MyComponent.jsx`)
  - Hooks : camelCase avec préfixe `use` (`useCustomHook.js`)
  - Utilitaires : camelCase (`myUtility.js`)

**Exemple** :
```javascript
// ✅ Bon
import { logger } from '../utils/logger';

export default function MyComponent() {
  logger.info('Component mounted');
  return <div>Content</div>;
}

// ❌ Mauvais
console.log('Component mounted');
```

### Backend (Django/Python)

- **PEP 8** : Suivez les conventions PEP 8
- **Docstrings** : Documentez toutes les fonctions et classes
- **Type hints** : Utilisez les type hints quand possible

**Exemple** :
```python
# ✅ Bon
def get_projects(status: str = 'published') -> QuerySet:
    """
    Récupère les projets avec un statut donné.
    
    Args:
        status: Statut des projets à récupérer
        
    Returns:
        QuerySet des projets
    """
    return Projet.objects.filter(status=status)

# ❌ Mauvais
def get_projects(status='published'):
    return Projet.objects.filter(status=status)
```

---

## 🧪 Tests

### Frontend

```bash
# Tous les tests
npm test

# Tests avec couverture
npm run test:coverage

# Tests d'accessibilité
npm run test:a11y

# Tests E2E
npm run test:e2e
```

**Exigences** :
- ✅ Tous les tests doivent passer
- ✅ Couverture minimale : 80%
- ✅ Nouveaux composants doivent avoir des tests

### Backend

```bash
# Tous les tests
python manage.py test

# Avec pytest
pytest

# Avec couverture
pytest --cov
```

**Exigences** :
- ✅ Tous les tests doivent passer
- ✅ Couverture minimale : 80%
- ✅ Nouveaux endpoints doivent avoir des tests

---

## 📚 Documentation

### Code

- **Commentaires** : Expliquez le "pourquoi", pas le "quoi"
- **Docstrings** : Pour toutes les fonctions publiques
- **README** : Mettez à jour si vous ajoutez des fonctionnalités

### API

- **OpenAPI/Swagger** : La documentation est générée automatiquement
- **Exemples** : Ajoutez des exemples dans les docstrings

---

## 🔄 Pull Requests

### Avant de Soumettre

- [ ] Tous les tests passent
- [ ] Le code respecte les standards (ESLint/PEP 8)
- [ ] La documentation est à jour
- [ ] Les commits sont clairs et descriptifs
- [ ] Pas de console.log (utiliser le logger)
- [ ] Pas de secrets commités

### Template de PR

```markdown
## Description
Brève description des changements

## Type de changement
- [ ] Bug fix
- [ ] Nouvelle fonctionnalité
- [ ] Breaking change
- [ ] Documentation

## Tests
- [ ] Tests unitaires ajoutés/mis à jour
- [ ] Tests d'intégration ajoutés/mis à jour
- [ ] Tests manuels effectués

## Checklist
- [ ] Code respecte les standards
- [ ] Documentation mise à jour
- [ ] Tests passent
- [ ] Pas de breaking changes (ou documentés)
```

---

## 🎯 Bonnes Pratiques

### Git

- **Commits atomiques** : Un commit = une modification logique
- **Messages clairs** : Utilisez des messages descriptifs
- **Branches** : Utilisez des noms descriptifs (`feature/`, `fix/`, `docs/`)

### Code

- **DRY** : Don't Repeat Yourself
- **KISS** : Keep It Simple, Stupid
- **YAGNI** : You Aren't Gonna Need It
- **SOLID** : Principes SOLID

### Sécurité

- **Ne jamais committer** de secrets (tokens, clés, mots de passe)
- **Valider** toutes les entrées utilisateur
- **Échapper** les données avant affichage
- **Utiliser** le logger au lieu de console.log

---

## 📞 Questions ?

Si vous avez des questions, n'hésitez pas à :
- Créer une issue
- Contacter les mainteneurs
- Consulter la documentation

---

**Merci de contribuer à EGOEJO !** 🎉

