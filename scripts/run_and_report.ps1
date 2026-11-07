param(
    [Parameter(Mandatory = $true)]
    [string]$ModelId
)

Set-Location -LiteralPath (Join-Path $PSScriptRoot '..')
$pythonPath = Join-Path (Get-Location).Path '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    Write-Host "Python executable not found: $pythonPath"
    exit 1
}

$capturePath = Join-Path ([System.IO.Path]::GetTempPath()) ("llm-run-{0}.log" -f [guid]::NewGuid())
try {
    & $pythonPath -m llm_stability_lab run --model $ModelId 2>&1 | Tee-Object -FilePath $capturePath
    $runExitCode = $LASTEXITCODE
    if ($runExitCode -ne 0) {
        Write-Host "Experiment run failed with exit code $runExitCode. Report was not generated."
        exit $runExitCode
    }

    $runLine = Select-String -LiteralPath $capturePath -Pattern 'Run ([0-9]{8}T[0-9]{6}Z_[a-f0-9]+) saved to' |
        Select-Object -Last 1
    if ($null -eq $runLine) {
        Write-Host 'Completed run ID was not found in output. Report was not generated.'
        exit 1
    }

    $runId = $runLine.Matches[0].Groups[1].Value
    Write-Host "Generating report for run $runId"
    & $pythonPath -m llm_stability_lab report $runId
    exit $LASTEXITCODE
}
finally {
    Remove-Item -LiteralPath $capturePath -ErrorAction SilentlyContinue
}
