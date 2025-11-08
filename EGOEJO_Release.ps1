param(
  [string]$Alias = "egoejo.vercel.app"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "== Build ==" -ForegroundColor Cyan
Remove-Item -Recurse -Force .\dist -ErrorAction SilentlyContinue
npm run build

git add -A
try { git commit -m "chore(release): build & deploy" | Out-Null } catch {}

Write-Host "== Deploy ==" -ForegroundColor Cyan
$n = npx vercel --prod

Write-Host "== Align alias ==" -ForegroundColor Cyan
$ready = (npx vercel ls --prod | Select-String 'https://\S+\.vercel\.app\s+● Ready' | ForEach-Object { ($_ -split '\s+')[0] } | Select-Object -First 1)
if ($ready) { npx vercel alias set $ready $Alias | Out-Null }

$URL = "https://$Alias"
Write-Host "== Smoke tests ==" -ForegroundColor Cyan
Invoke-WebRequest "$URL/api/health" -Method Head -UseBasicParsing | Select StatusCode,@{n='Type';e={$_.Headers['Content-Type']}} | Format-Table | Out-Host
try {
  $h = Invoke-RestMethod "$URL/api/admin-intents?limit=1" -Headers @{ Authorization = "Bearer $env:ADMIN_TOKEN" }
  "admin-intents ok=$($h.ok) count=$($h.count)" | Out-Host
} catch { "admin-intents: $($_.Exception.Message)" | Out-Host }

$tag = "v0.1." + (Get-Date -f yyyyMMdd-HHmm)
git tag -a $tag -m "Release $tag"
git push --tags
Write-Host "Done. URL: $URL" -ForegroundColor Green
