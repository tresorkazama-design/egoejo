# Démarrage rapide sur Windows (PowerShell)

Ces commandes PowerShell sont adaptées au projet **EGOEJO** et évitent l'erreur `Set-Location : Impossible de trouver le chemin d'accès ...` en vérifiant d'abord l'existence du dossier.

## 1. Se placer dans le dossier du projet
Adaptez la valeur de `$projectPath` à **votre** emplacement réel avant d'exécuter les commandes :

```powershell
$projectPath = 'C:\Users\treso\Downloads\egoejo\frontend'

if (-not (Test-Path -Path $projectPath)) {
    Write-Error "Le dossier '$projectPath' est introuvable. Modifiez la variable \$projectPath pour correspondre à votre installation locale."
    return
}

Set-Location -Path $projectPath
```

> Astuce : pour connaître le chemin exact, ouvrez l'Explorateur Windows, naviguez jusqu'au dossier `egoejo`, puis cliquez dans la barre d'adresse pour copier le chemin complet.

## 2. Créer (ou mettre à jour) `.env.local`

Si le fichier n'existe pas encore, vous pouvez le générer avec les variables indispensables :

```powershell
@"
DATABASE_URL=postgres://user:password@host:5432/dbname
ADMIN_TOKEN=remplacez_moi
RESEND_API_KEY=optionnel
NOTIFY_EMAIL=optionnel
FRONTEND_URL=http://localhost:5173
"@ | Set-Content -Encoding UTF8 '.env.local'
```

Modifiez les valeurs en fonction de votre environnement (base PostgreSQL, jeton admin, etc.).

## 3. Installer les dépendances

```powershell
npm install
```

## 4. Démarrer l'API Express

```powershell
node .\server.js
```

Conservez cette console ouverte pour garder l'API sur `http://localhost:5000`.

## 5. Lancer le front-end Vite

Dans **une nouvelle** fenêtre PowerShell :

```powershell
Set-Location -Path $projectPath
npm run dev
```

Le front s'exécute sur `http://localhost:5173` et communique avec l'API précédente.

## 6. Tests rapides via PowerShell

- **Vérifier les variables d'environnement**
  ```powershell
  Invoke-RestMethod -Uri 'http://localhost:5000/api/debug-env'
  ```

- **Soumettre un formulaire “Rejoindre”**
  ```powershell
  Invoke-RestMethod -Uri 'http://localhost:5000/api/rejoindre' `
                    -Method Post `
                    -ContentType 'application/json' `
                    -Body (@{ nom = 'Test'; email = 'test@example.com'; profil = 'Curieux' } | ConvertTo-Json)
  ```

- **Télécharger les intentions au format JSON pour l'admin**
  ```powershell
  Invoke-RestMethod -Uri 'http://localhost:5000/api/export-intents?format=json' `
                    -Headers @{ Authorization = 'Bearer remplacez_moi' }
  ```

---

En adaptant la variable `$projectPath` à votre arborescence locale, ces commandes fonctionnent sans erreur « chemin introuvable » et couvrent les actions essentielles pour travailler rapidement sur EGOEJO.
