# Guide des Tests - EGOEJO

Ce document décrit comment exécuter les tests pour le projet EGOEJO.

## Tests Backend (Django)

### Prérequis

```bash
cd backend
pip install -r requirements.txt
```

### Exécution des tests

#### Avec Django test runner (recommandé)

```bash
cd backend
python manage.py test
```

#### Avec pytest (avec couverture de code)

```bash
cd backend
pytest --cov=core --cov-report=html --cov-report=term-missing
```

Les rapports de couverture seront générés dans `backend/htmlcov/`.

### Structure des tests

Les tests sont organisés dans `backend/core/tests.py` :

- **IntentTestCase** : Tests pour le modèle Intent et les endpoints associés
  - Création d'intentions
  - Validation des champs
  - Honeypot anti-spam
  - Endpoints admin (liste, export, suppression)
  - Filtres et recherche

- **ProjetCagnotteTestCase** : Tests pour les modèles Projet et Cagnotte

### Variables d'environnement pour les tests

Les tests utilisent des variables d'environnement définies dans le code :
- `ADMIN_TOKEN` : Token pour l'authentification admin
- `RESEND_API_KEY` : Désactivé en test (vide)

### Coverage

Pour obtenir un rapport de couverture détaillé :

```bash
cd backend
pytest --cov=core --cov-report=html
open htmlcov/index.html  # Sur macOS/Linux
```

## Tests Frontend (React)

### Prérequis

```bash
cd frontend
npm install
```

### Exécution des tests

#### Mode watch (développement)

```bash
cd frontend
npm run test
```

#### Mode run (CI/CD)

```bash
cd frontend
npm run test -- --run
```

#### Interface utilisateur

```bash
cd frontend
npm run test:ui
```

#### Avec couverture

```bash
cd frontend
npm run test:coverage
```

### Structure des tests

Les tests sont organisés dans `frontend/src/pages/__tests__/` :

- **Rejoindre.test.jsx** : Tests pour le formulaire de rejoindre
  - Rendu du formulaire
  - Validation des champs
  - Soumission réussie
  - Gestion des erreurs

### Configuration

La configuration des tests se trouve dans :
- `frontend/vitest.config.js` : Configuration Vitest
- `frontend/src/test/setup.js` : Setup global des tests

## CI/CD

### GitHub Actions

Le workflow CI/CD est défini dans `.github/workflows/ci.yml` :

1. **Backend Tests** :
   - Setup PostgreSQL
   - Installation des dépendances
   - Migration de la base de données
   - Exécution des tests Django
   - Exécution de pytest avec couverture
   - Upload de la couverture sur Codecov

2. **Frontend Tests** :
   - Setup Node.js
   - Installation des dépendances
   - Exécution des tests
   - Build de l'application

3. **Lint Backend** :
   - Vérification avec flake8
   - Vérification du formatage avec black
   - Vérification des imports avec isort

### Déclenchement

Le workflow se déclenche automatiquement sur :
- Push sur les branches `main` et `develop`
- Pull requests vers `main` et `develop`

## Ajout de nouveaux tests

### Backend

1. Ajouter une nouvelle classe de test dans `backend/core/tests.py`
2. Hériter de `TestCase`
3. Implémenter les méthodes `setUp()` et `tearDown()` si nécessaire
4. Ajouter des méthodes `test_*` pour chaque cas de test

Exemple :

```python
class MonTestCase(TestCase):
    def setUp(self):
        # Préparation des données de test
        pass
    
    def test_ma_fonctionnalite(self):
        # Test de la fonctionnalité
        response = self.client.get('/api/endpoint/')
        self.assertEqual(response.status_code, 200)
```

### Frontend

1. Créer un fichier `*.test.jsx` dans `frontend/src/pages/__tests__/`
2. Importer les dépendances nécessaires
3. Utiliser `@testing-library/react` pour rendre les composants
4. Utiliser `@testing-library/user-event` pour simuler les interactions

Exemple :

```jsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MonComposant from '../MonComposant';

describe('MonComposant', () => {
  it('renders correctly', () => {
    render(<MonComposant />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

## Bonnes pratiques

1. **Tests unitaires** : Tester une fonctionnalité isolée
2. **Tests d'intégration** : Tester l'interaction entre plusieurs composants
3. **Couverture** : Viser au moins 80% de couverture de code
4. **Nommage** : Utiliser des noms descriptifs pour les tests
5. **Isolation** : Chaque test doit être indépendant
6. **Setup/Teardown** : Nettoyer les données après chaque test

## Dépannage

### Erreurs de base de données

Si les tests échouent avec des erreurs de base de données :
- Vérifier que PostgreSQL est installé et démarré
- Vérifier les variables d'environnement dans les tests
- Utiliser une base de données de test séparée

### Erreurs de modules

Si les tests échouent avec des erreurs d'import :
- Vérifier que toutes les dépendances sont installées
- Vérifier que les chemins d'import sont corrects
- Exécuter `pip install -r requirements.txt` ou `npm install`

### Tests lents

Pour accélérer les tests :
- Utiliser des fixtures au lieu de créer des données à chaque test
- Utiliser des mocks pour les appels API externes
- Paralléliser les tests avec `pytest-xdist` (backend) ou `vitest --threads` (frontend)

