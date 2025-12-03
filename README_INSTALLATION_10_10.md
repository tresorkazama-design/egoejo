# 🚀 Installation EGOEJO 10/10

Guide rapide pour installer et configurer toutes les améliorations 10/10.

---

## ⚡ Installation Rapide

### Windows (PowerShell)
```powershell
.\setup-10-10.ps1
```

### Linux/Mac (Bash)
```bash
chmod +x setup-10-10.sh
./setup-10-10.sh
```

---

## 📋 Installation Manuelle

### 1. Frontend

```bash
cd frontend/frontend
npm install
npm install --save-dev husky
npx husky init  # Si .git existe
```

### 2. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## ✅ Vérification

### Vérifier que tout est installé

```bash
# Frontend
cd frontend/frontend
npm run lint          # Doit fonctionner
npm test -- --run     # Doit fonctionner

# Backend
cd backend
source venv/bin/activate
python manage.py backup_db --help  # Doit afficher l'aide
```

---

## 🔧 Configuration Optionnelle

### 1. Husky (Pre-commit Hooks)

Si `.git` existe, Husky sera initialisé automatiquement. Sinon :

```bash
cd frontend/frontend
npx husky init
```

### 2. Lighthouse CI (Optionnel)

```bash
npm install -g @lhci/cli
```

### 3. Secrets GitHub (pour CD)

Configurer dans GitHub Settings → Secrets :
- `VERCEL_TOKEN`
- `VERCEL_ORG_ID`
- `VERCEL_PROJECT_ID`
- `RAILWAY_TOKEN`
- `RAILWAY_SERVICE_ID`

### 4. Rate Limiting IP (si nécessaire)

Décommenter dans `backend/config/settings.py` ligne 283 :
```python
'core.api.rate_limiting.IPRateThrottle',
```

---

## 📚 Documentation

- `CONTRIBUTING.md` - Guide de contribution
- `GUIDE_ARCHITECTURE.md` - Architecture détaillée
- `GUIDE_DEPLOIEMENT.md` - Guide de déploiement
- `GUIDE_TROUBLESHOOTING.md` - Résolution de problèmes
- `PLAN_10_10.md` - Plan d'action complet
- `VERIFICATION_10_10.md` - Vérification détaillée

---

## 🎯 Prochaines Étapes

1. ✅ Installation terminée
2. ⚙️ Configurer les secrets GitHub (si CD souhaité)
3. 🧪 Tester : `npm run lint` et `npm test -- --run`
4. 🚀 Commencer à développer !

---

**Le projet EGOEJO est maintenant à 10/10 !** 🎉

