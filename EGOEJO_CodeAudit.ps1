$ErrorActionPreference="Stop"
[Console]::OutputEncoding=[Text.UTF8Encoding]::new($false)
$SCAN=@(".\src",".\public",".\api",".\components")
$report=@()

$report+="=== Duplicates (content) ==="
$report+=(Get-ChildItem $SCAN -Recurse -File -Include *.js,*.jsx,*.ts,*.tsx,*.css,*.html |
  Get-FileHash -Algorithm SHA256 | Group-Object Hash | ? Count -gt 1 |
  % { $_.Group | % { (Resolve-Path -Relative $_.Path) } }) -join "`n"

$report+="`n=== Same basename ==="
$report+=(Get-ChildItem .\src -Recurse -File -Include *.js,*.jsx,*.ts,*.tsx |
  Select @{n='Base';e={$_.BaseName}}, FullName | Group-Object Base | ? Count -gt 1 |
  % { $_.Group | % { "$($_.Base)`t$($_.FullName)" } }) -join "`n"

$report+="`n=== Duplicate default exports ==="
$report+=(Get-ChildItem .\src -Recurse -File -Include *.js,*.jsx,*.ts,*.tsx | %{
  $c=Get-Content $_.FullName -Raw; if($c -match 'export\s+default\s+(\w+)'){[pscustomobject]@{E=$Matches[1];F=$_.FullName}}
} | Group-Object E | ? Count -gt 1 | % { $_.Group | % { "$($_.E)`t$($_.F)" } }) -join "`n"

$report+="`n=== Backups ==="
$report+=(Get-ChildItem $SCAN -Recurse -File -Include *.bak,*.backup*,*.old,*.copy,*backup*,*broken* |
  Sort LastWriteTime -Descending | % { "$($_.LastWriteTime.ToString('s'))`t$($_.Length)`t$($_.FullName)" }) -join "`n"

$report+="`n=== Large files (>200KB) ==="
$report+=(Get-ChildItem .\src,.\public -Recurse -File | ? Length -gt 200KB |
  Sort Length -Descending | % { "{0} KB`t{1}" -f [math]::Round($_.Length/1KB,1), $_.FullName }) -join "`n"

$path=".\\rapport_EGOEJO_code.txt"
$report | Out-File -Encoding UTF8 $path
Write-Host "✅ Rapport généré: $path"
