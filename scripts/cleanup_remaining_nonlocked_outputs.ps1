$ErrorActionPreference = 'Stop'

function U([int[]]$points) { return -join ($points | ForEach-Object { [char]$_ }) }

$output = (Resolve-Path (Join-Path $PSScriptRoot '..\output')).Path
$targets = @(
  (Join-Path $output (U 0x65B0, 0x5A92, 0x9AD4)),
  (Join-Path $output (U 0x7DB2, 0x7AD9))
)
foreach ($target in $targets) {
  if ($target -notlike (Join-Path $output '*')) { throw "Refusing cleanup outside output: $target" }
  if (Test-Path -LiteralPath $target) { Remove-Item -LiteralPath $target -Recurse -Force }
}
