Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Title($text) {
  Write-Host ""
  Write-Host ("=" * 80)
  Write-Host ("= " + $text)
  Write-Host ("=" * 80)
}

function Run-Proc {
  param(
    [Parameter(Mandatory)] [string]$Exe,
    [Parameter()] [string[]]$Args = @(),
    [Parameter(Mandatory)] [string]$Name,
    [switch]$IgnoreExitCode
  )
  $argLine = ($Args -join " ")
  Write-Host "→ $Name : $Exe $argLine"
  try {
    $p = Start-Process -FilePath $Exe -ArgumentList $argLine -NoNewWindow -Wait -PassThru -ErrorAction Stop
    if (-not $IgnoreExitCode -and $p.ExitCode -ne 0) {
      throw "Exit code $($p.ExitCode)"
    }
    Write-Host "✔ $Name OK" -ForegroundColor Green
    return $true
  } catch {
    Write-Host "✖ $Name ÉCHEC" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor DarkRed
    return $false
  }
}

function Has-Lock($file) { Test-Path -Path $file -PathType Leaf }

function Detect-PM {
  param([string]$dir)
  if (Has-Lock (Join-Path $dir "pnpm-lock.yaml"))   { return @{ pm="pnpm"; exe="pnpm"; install=@("install","--frozen-lockfile") } }
  if (Has-Lock (Join-Path $dir "yarn.lock"))         { return @{ pm="yarn"; exe="yarn";  install=@("install","--frozen-lockfile") } }
  if (Has-Lock (Join-Path $dir "package-lock.json")) { return @{ pm="npm";  exe="npm";   install=@("ci") } }
  return @{ pm="npm"; exe="npm"; install=@("install") }
}

function Package-HasScript {
  param([object]$pkgJson, [string]$scriptName)
  if (-not $pkgJson.scripts) { return $false }
  return $pkgJson.scripts.PSObject.Properties.Name -contains $scriptName
}

function Has-DevDep {
  param([object]$pkgJson, [string]$dep)
  if (-not ($pkgJson.PSObject.Properties.Name -contains "devDependencies")) { return $false }
  if ($null -eq $pkgJson.devDependencies) { return $false }
  return $pkgJson.devDependencies.PSObject.Properties.Name -contains $dep
}

function Get-EnvKeys {
  param([string]$file)
  if (-not (Test-Path $file)) { return @() }
  Get-Content $file |
    Where-Object { $_ -match '^\s*[A-Za-z_][A-Za-z0-9_]*\s*=' } |
    ForEach-Object { ($_ -replace '\s*=\s*.*$','').Trim() } |
    Where-Object { $_ -ne "" } |
    Sort-Object -Unique
}

# ── 1) ÉTAT GIT
Write-Title "ÉTAT GIT DU DÉPÔT"
if (Test-Path ".git") {
  Run-Proc -Exe "git" -Args @("--version") -Name "Git version"          | Out-Null
  Run-Proc -Exe "git" -Args @("fetch","--all","--prune") -Name "Mise à jour des refs distantes" | Out-Null
  Run-Proc -Exe "git" -Args @("status","-sb") -Name "Statut (branche, ahead/behind, fichiers modifiés)" | Out-Null
  Run-Proc -Exe "git" -Args @("log","--oneline","--decorate","--graph","-n","15") -Name "Historique récent" | Out-Null
  Run-Proc -Exe "git" -Args @("diff","--name-status") -Name "Fichiers modifiés/non indexés" | Out-Null
} else {
  Write-Host "Ce dossier ne semble pas être un dépôt Git (.git manquant)." -ForegroundColor Yellow
}

# ── 2) PROJET COURANT (et sous-dossiers)
Write-Title "DÉTECTION DES PROJETS NODE"
$packageFiles = Get-ChildItem -Recurse -File -Filter "package.json" | Where-Object { $_.FullName -notmatch "\\node_modules\\|/node_modules/" }
if (-not $packageFiles) {
  Write-Host "Aucun package.json trouvé (hors node_modules)."
  exit 0
}

$summary = @()

foreach ($pkg in $packageFiles) {
  $dir = Split-Path $pkg.FullName -Parent
  Write-Title "PROJET: $dir"

  Push-Location $dir
  try {
    $pmInfo = Detect-PM -dir $dir
    $pmExe  = $pmInfo.exe
    $pkgJson = Get-Content "package.json" -Raw | ConvertFrom-Json

    $res = [ordered]@{
      Path       = $dir
      PM         = $pmInfo.pm
      Install    = $false
      Lint       = "SKIP"
      Typecheck  = "SKIP"
      Test       = "SKIP"
      Build      = "SKIP"
      Audit      = "SKIP"
      Prettier   = "SKIP"
      Outdated   = "SKIP"
      EnvCheck   = "OK"
    }

    # Install
    $res.Install = Run-Proc -Exe $pmExe -Args $pmInfo.install -Name "Install des dépendances"

    # Lint
    $hasEslintrc = @(Get-ChildItem -Force -Name | Where-Object { $_ -like ".eslintrc*" }).Count -gt 0
    if (Package-HasScript $pkgJson "lint") {
      $res.Lint = Run-Proc -Exe $pmExe -Args @("run","lint") -Name "Linting"
    } elseif ($hasEslintrc -or (Has-DevDep $pkgJson "eslint")) {
      $res.Lint = Run-Proc -Exe "npx" -Args @("-y","eslint",".") -Name "Linting (auto)"
    }

    # Typecheck
    if (Package-HasScript $pkgJson "typecheck") {
      $res.Typecheck = Run-Proc -Exe $pmExe -Args @("run","typecheck") -Name "TypeScript type-check"
    } elseif (Has-DevDep $pkgJson "typescript") {
      $res.Typecheck = Run-Proc -Exe "npx" -Args @("-y","tsc","--noEmit") -Name "TypeScript type-check (auto)"
    }

    # Tests
    $env:CI = "true"
    if (Package-HasScript $pkgJson "test") {
      if ($pmInfo.pm -eq "npm")      { $res.Test = Run-Proc -Exe "npm"  -Args @("run","test","--silent") -Name "Tests unitaires" }
      elseif ($pmInfo.pm -eq "yarn") { $res.Test = Run-Proc -Exe "yarn" -Args @("test","--silent") -Name "Tests unitaires" }
      else                            { $res.Test = Run-Proc -Exe "pnpm" -Args @("test","--silent") -Name "Tests unitaires" }
    }

    # Build
    if (Package-HasScript $pkgJson "build") {
      $res.Build = Run-Proc -Exe $pmExe -Args @("run","build") -Name "Build"
    }

    # Prettier
    if (Package-HasScript $pkgJson "prettier:check") {
      $res.Prettier = Run-Proc -Exe $pmExe -Args @("run","prettier:check") -Name "Prettier (check)"
    } elseif (Has-DevDep $pkgJson "prettier") {
      $res.Prettier = Run-Proc -Exe "npx" -Args @("-y","prettier","--check",".") -Name "Prettier (auto)"
    }

    # Audit (ne bloque pas si vulnérabilités)
    if     ($pmInfo.pm -eq "npm")  { $res.Audit = Run-Proc -Exe "npm"  -Args @("audit","--audit-level=moderate","--omit=dev") -Name "Audit sécurité (npm)" -IgnoreExitCode }
    elseif ($pmInfo.pm -eq "yarn") { $res.Audit = Run-Proc -Exe "yarn" -Args @("audit","--level","moderate")                 -Name "Audit sécurité (yarn)" -IgnoreExitCode }
    elseif ($pmInfo.pm -eq "pnpm") { $res.Audit = Run-Proc -Exe "pnpm" -Args @("audit","--prod")                              -Name "Audit sécurité (pnpm)" -IgnoreExitCode }

    # Outdated (informatif)
    if     ($pmInfo.pm -eq "npm")  { $res.Outdated = Run-Proc -Exe "npm"  -Args @("outdated") -Name "Packages obsolètes" -IgnoreExitCode }
    elseif ($pmInfo.pm -eq "yarn") { $res.Outdated = Run-Proc -Exe "yarn" -Args @("outdated") -Name "Packages obsolètes" -IgnoreExitCode }
    elseif ($pmInfo.pm -eq "pnpm") { $res.Outdated = Run-Proc -Exe "pnpm" -Args @("outdated") -Name "Packages obsolètes" -IgnoreExitCode }

    # Vérif .env vs .env.example (⚠️ garantir un tableau)
    $exampleCandidates = @(
      Join-Path $dir ".env.example";
      Join-Path $dir ".env.template";
      Join-Path $dir ".env.sample"
    ) | Where-Object { Test-Path $_ }

    if ($exampleCandidates.Count -gt 0) {
      $example = $exampleCandidates[0]
      $realEnvCandidates = @(Get-ChildItem -File -Filter ".env*" | Where-Object { $_.Name -notmatch "example|template|sample" })
      $required = Get-EnvKeys $example
      $present  = @()
      foreach ($e in $realEnvCandidates) { $present += Get-EnvKeys $e.FullName }
      $present = $present | Sort-Object -Unique
      $missing = Compare-Object -ReferenceObject $required -DifferenceObject $present -PassThru | Where-Object { $_ -ne "" }

      if ($missing.Count -gt 0) {
        $res.EnvCheck = "MANQUANT: " + ($missing -join ", ")
        Write-Host "Variables .env manquantes: $($missing -join ", ")" -ForegroundColor Yellow
      } else {
        Write-Host "Variables d'environnement : OK"
      }
    } else {
      Write-Host "Aucun .env.example trouvé — vérification ignorée." -ForegroundColor Yellow
    }

    $summary += [pscustomobject]$res
  }
  finally {
    Pop-Location
  }
}

Write-Title "RÉSUMÉ DES PROJETS"
$summary | Format-Table -AutoSize
