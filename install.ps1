# Promptsmith installer (Windows PowerShell)
param([ValidateSet("all","claude","codex")][string]$Target = "all")
$ErrorActionPreference = "Stop"
$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Target -in "all","claude") {
  $dest = Join-Path $HOME ".claude\commands"
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item "$Dir\commands\claude\promptsmith.md" "$dest\promptsmith.md" -Force
  Write-Host "✔ Claude Code: /promptsmith installed -> $dest\promptsmith.md"
}
if ($Target -in "all","codex") {
  $codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
  $dest = Join-Path $codexHome "prompts"
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Copy-Item "$Dir\commands\codex\promptsmith.md" "$dest\promptsmith.md" -Force
  Write-Host "✔ Codex CLI: /prompts:promptsmith installed -> $dest\promptsmith.md"
}
Write-Host "Restart your CLI session to pick up the new command."
