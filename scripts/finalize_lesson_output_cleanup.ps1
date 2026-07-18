$ErrorActionPreference = 'Stop'

function U([int[]]$CodePoints) {
    return -join ($CodePoints | ForEach-Object { [char]$_ })
}

$output = (Resolve-Path (Join-Path $PSScriptRoot '..\\output')).Path
$targets = @(
    Join-Path $output (U @(0x5716, 0x7247))
    Join-Path $output (U @(0x7C21, 0x5831))
)

foreach ($target in $targets) {
    if ($target -notlike (Join-Path $output '*')) {
        throw "Cleanup target is outside output: $target"
    }

    if (Test-Path -LiteralPath $target) {
        Remove-Item -LiteralPath $target -Recurse -Force
        Write-Host "Removed: $target"
    }
}

Write-Host 'Remaining output folders:'
Get-ChildItem -LiteralPath $output -Force | Select-Object Name, Mode
