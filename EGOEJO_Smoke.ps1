param([string]$URL = "https://egoejo.vercel.app")

function Out-Result($ok, $label, $extra="") {
  if ($ok) { Write-Host ("[OK]  " + $label) -ForegroundColor Green }
  else     { Write-Host ("[KO]  " + $label + $(if($extra){" -> " + $extra} else {""})) -ForegroundColor Red }
}

Write-Host "=== EGOEJO – Smoke Tests (prod) ===" -ForegroundColor Cyan
Write-Host "URL: $URL" -ForegroundColor DarkCyan

# 0) Charger ADMIN_TOKEN si absent (depuis .env local)
if (-not $env:ADMIN_TOKEN -and (Test-Path .\.env)) {
  $line = (Get-Content .\.env -Raw) -split "`r?`n" | ? { $_ -match '^\s*ADMIN_TOKEN\s*=' } | Select -First 1
  if ($line) { $env:ADMIN_TOKEN = ($line -replace '^\s*ADMIN_TOKEN\s*=\s*','').Trim().Trim('"').Trim("'") }
}

# 1) /api/health
try {
  $health = Invoke-RestMethod "$URL/api/health"
  $ok = $health.ok -and $health.db -and [string]::IsNullOrWhiteSpace($health.frontend) -eq $false -and [string]::IsNullOrWhiteSpace($health.node) -eq $false
  Out-Result $ok "/api/health (ok, db, node, frontend)"
} catch { Out-Result $false "/api/health" $_.Exception.Message }

# 2) /api/debug-env (tolérant: trim, sans slash final, insensible casse)
try {
  $dbg = Invoke-RestMethod "$URL/api/debug-env"
  $feRaw  = ($dbg.env.FRONTEND_URL -as [string])
  $fe     = $feRaw.Trim().TrimEnd('/').ToLowerInvariant()
  $urlNorm= $URL.Trim().TrimEnd('/').ToLowerInvariant()
  Out-Result ($fe -eq $urlNorm) "/api/debug-env FRONTEND_URL=$feRaw"
} catch { Out-Result $false "/api/debug-env" $_.Exception.Message }

# 3) /api/rejoindre : idempotence (même email/jour => même id)
try {
  $email = "smoke-$([int](Get-Random))@example.com"
  $body1 = @{ nom='Smoke'; email=$email; profil='je-protege'; message='M1'; website='' } | ConvertTo-Json
  $r1 = Invoke-RestMethod -Uri "$URL/api/rejoindre" -Method POST -ContentType 'application/json' -Body $body1

  $body2 = @{ nom='Smoke'; email=$email; profil='je-protege'; message='M2'; website='' } | ConvertTo-Json
  $r2 = Invoke-RestMethod -Uri "$URL/api/rejoindre" -Method POST -ContentType 'application/json' -Body $body2

  $ok = $r1.ok -and $r2.ok -and ($r1.id -eq $r2.id)
  Out-Result $ok "/api/rejoindre idempotent" ("id1="+$r1.id+" id2="+$r2.id)
} catch { Out-Result $false "/api/rejoindre" $_.Exception.Message }

# 4) /api/export-intents : 401 sans token, 200 avec token
try {
  $unauth = $true
  try { Invoke-WebRequest "$URL/api/export-intents" -Method GET -UseBasicParsing | Out-Null; $unauth = $false } catch { $unauth = ($_.Exception.Response.StatusCode.value__ -eq 401) }
  Out-Result $unauth "/api/export-intents refuse sans token"

  $csvPath = "$env:USERPROFILE\Desktop\intents-smoke.csv"
  $H = @{ Authorization = "Bearer $($env:ADMIN_TOKEN)" }
  Invoke-WebRequest "$URL/api/export-intents?from=$(Get-Date -f yyyy-MM-dd)&to=$(Get-Date -f yyyy-MM-dd)" -Headers $H -OutFile $csvPath | Out-Null
  Out-Result (Test-Path $csvPath) "/api/export-intents avec token -> intents-smoke.csv"
} catch { Out-Result $false "/api/export-intents (avec token)" $_.Exception.Message }

# 5) Headers cache (asset) & no-store (index.html)
try {
  $asset = (Get-ChildItem .\dist\assets -Filter *.js | Select-Object -First 1).Name
  $h1 = Invoke-WebRequest -Uri "$URL/assets/$asset" -Method Head -UseBasicParsing
  Out-Result ($h1.Headers['Cache-Control'] -match 'immutable') "Cache assets (immutable)"

  $h2 = Invoke-WebRequest -Uri "$URL/index.html" -Method Head -UseBasicParsing
  Out-Result ($h2.Headers['Cache-Control'] -match 'no-store') "index.html no-store"
} catch { Out-Result $false "Headers cache/no-store" $_.Exception.Message }

# 6) Headers sécurité (Referrer-Policy, X-Content-Type-Options) sur / ET /:path*
try {
  $hRoot = Invoke-WebRequest -Uri "$URL/" -Method Head -UseBasicParsing
  $okRoot = ($hRoot.Headers['Referrer-Policy'] -match 'strict-origin-when-cross-origin') -and ($hRoot.Headers['X-Content-Type-Options'] -match 'nosniff')

  $hPath = Invoke-WebRequest -Uri "$URL/any-path" -Method Head -UseBasicParsing
  $okPath = ($hPath.Headers['Referrer-Policy'] -match 'strict-origin-when-cross-origin') -and ($hPath.Headers['X-Content-Type-Options'] -match 'nosniff')

  Out-Result ($okRoot -and $okPath) "Headers sécurité (/, /:path*)"
} catch { Out-Result $false "Headers sécurité" $_.Exception.Message }

# 7) SPA/404 rewrite
try {
  $resp = Invoke-WebRequest -Uri "$URL/does-not-exist-path" -UseBasicParsing
  Out-Result ($resp.Headers['Content-Type'] -match 'text/html') "SPA rewrite (routes inconnues -> index.html)"
} catch { Out-Result $false "SPA rewrite" $_.Exception.Message }

Write-Host "=== Fin des tests ===" -ForegroundColor Cyan
