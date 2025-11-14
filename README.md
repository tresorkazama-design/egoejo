# EGOEJO Full Stack

## Structure

- `backend/` – API Django + tests
- `frontend/` – SPA React/Vite (production bundle dans `dist/`)
- `admin-panel/` – placeholder historique
- `docker-compose.yml` – orchestration locale
- `Makefile` – scripts d’automatisation (`backend-test`, `frontend-test`, `frontend-build`, `predeploy`)

## Prérequis

- Node.js ≥ 18
- Python 3.10+ (SQLite par défaut, Postgres si `DB_*` définies)
- npm & pip disponibles dans le PATH

## Configurer l’environnement backend

1. Copier le modèle :
   ```bash
   cp backend/env.template backend/.env
   ```
2. Renseigner les variables dans `backend/.env` :

   | Variable | Description | Defaut |
   | --- | --- | --- |
   | `DJANGO_SECRET_KEY` | clé Django | _obligatoire_ |
   | `ADMIN_TOKEN` | token Bearer admin | _obligatoire pour l’admin_ |
   | `RESEND_API_KEY` / `NOTIFY_EMAIL` | notifications email | optionnel |
   | `DB_*` | configuration Postgres | si vides → SQLite auto (`db.sqlite3`) |
   | `DEBUG` | `1` en dev | `0` |
   | `DISABLE_THROTTLE_FOR_TESTS` | couper throttling DRF pendant les tests | `0` |
   | `SECURE_SSL_REDIRECT` | forcer HTTPS | `1` (désactivé si `DEBUG=1`)
   | `APP_BASE_URL` | URL utilisée dans certains mails/tests | `http://localhost:5173` |

## Variables frontend

- `VITE_API_URL` : URL publique de l’API (ex. `http://localhost:8000`).

## Lancer localement

```bash
# Backend
cd backend
python -m venv venv
# Windows PowerShell : .\venv\Scripts\Activate.ps1
# macOS/Linux : source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend
cd ../frontend
npm install
npm run dev
```

## Scripts Makefile

```bash
make backend-test      # cd backend && DISABLE_THROTTLE_FOR_TESTS=1 DEBUG=1 python -m pytest
make frontend-test     # npm test -- --run
make frontend-build    # npm run build
make predeploy         # enchaîne les trois commandes ci-dessus
```
*(Sur Windows sans Make, exécute simplement les commandes visibles dans chaque règle.)*

## Tests

- Backend :
  ```bash
  DISABLE_THROTTLE_FOR_TESTS=1 DEBUG=1 python manage.py test
  ```
- Frontend :
  ```bash
  npm run test
  ```

## Build & déploiement frontend

```bash
npm run build
# Résultat : frontend/dist/ (chunks séparés vendor/gsap/three…)
```
Déploie ensuite `dist/` sur Netlify, Vercel ou via Nginx (voir guide de déploiement).

## Déploiement backend (exemple Render/Heroku)

1. Définir les variables d’environnement (section précédente).
2. `python manage.py migrate` puis `python manage.py collectstatic --noinput`.
3. Démarrer Gunicorn : `gunicorn config.wsgi` (Procfile/Render `start-command`).

## Sécurité

- Ne jamais committer `.env`.
- Régénérer `DJANGO_SECRET_KEY` pour la production.
- Mettre à jour `ADMIN_TOKEN` sur le serveur.
- Maintenir dépendances `pip` / `npm` à jour.

## Historique

Voir [`CHANGELOG.md`](CHANGELOG.md) pour les détails des versions.
