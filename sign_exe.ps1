# sign_exe.ps1 — Sign CSVOperations.exe so Windows shows "Kiran Beethoju"
#                instead of "Unknown Publisher"
#
# USAGE (run in PowerShell after build_exe.bat):
#   .\sign_exe.ps1
#   .\sign_exe.ps1 -PfxPath "MyKey.pfx" -PfxPassword "secret"
#
# NOTE: A *self-signed* certificate removes "Unknown Publisher" and shows your
#       name, but Windows SmartScreen may still warn on first run.
#       For full SmartScreen trust (zero warnings), purchase an EV code-signing
#       certificate from DigiCert, Sectigo, or GlobalSign (~$300-500/yr).

param(
    [string]$ExePath    = "dist\CSVOperations\CSVOperations.exe",
    [string]$CertName   = "Kiran Beethoju",
    [string]$PfxPath    = "KiranB_CodeSign.pfx",
    [string]$PfxPassword = ""
)

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  CSV Operations — Code Signing Utility    " -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── 1. Create self-signed cert if PFX not found ───────────────────────────
if (-not (Test-Path $PfxPath)) {
    Write-Host "No PFX found at '$PfxPath'. Creating self-signed certificate..." -ForegroundColor Yellow
    Write-Host "Publisher name: $CertName" -ForegroundColor White

    $cert = New-SelfSignedCertificate `
        -Subject        "CN=$CertName" `
        -Type           CodeSigning `
        -HashAlgorithm  SHA256 `
        -CertStoreLocation "Cert:\CurrentUser\My" `
        -NotAfter       (Get-Date).AddYears(5)

    if (-not $PfxPassword) {
        Write-Host ""
        $secPwd = Read-Host "Set a password for the PFX file" -AsSecureString
    }
    else {
        $secPwd = ConvertTo-SecureString $PfxPassword -AsPlainText -Force
    }

    Export-PfxCertificate -Cert $cert -FilePath $PfxPath -Password $secPwd | Out-Null
    Write-Host "✓ Certificate created and saved to '$PfxPath'" -ForegroundColor Green
    Write-Host ""
}

# ── 2. Locate signtool.exe ────────────────────────────────────────────────
Write-Host "Searching for signtool.exe..." -ForegroundColor Gray

$signtool = Get-ChildItem `
    -Path   "C:\Program Files (x86)\Windows Kits","C:\Program Files\Windows Kits" `
    -Recurse `
    -Filter "signtool.exe" `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match "x64" } |
    Sort-Object FullName -Descending |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $signtool) {
    Write-Host ""
    Write-Host "✗ signtool.exe not found." -ForegroundColor Red
    Write-Host "  Install the Windows SDK from:" -ForegroundColor Yellow
    Write-Host "  https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Or install via winget:" -ForegroundColor Yellow
    Write-Host "  winget install Microsoft.WindowsSDK" -ForegroundColor Cyan
    exit 1
}

Write-Host "Found: $signtool" -ForegroundColor Green

# ── 3. Sign the EXE ──────────────────────────────────────────────────────
if (-not (Test-Path $ExePath)) {
    Write-Host ""
    Write-Host "✗ EXE not found at '$ExePath'" -ForegroundColor Red
    Write-Host "  Run build_exe.bat first." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Signing: $ExePath" -ForegroundColor White

if (-not $PfxPassword) {
    $secPwd = Read-Host "PFX password" -AsSecureString
    $bstr   = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secPwd)
    $PfxPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
}

& $signtool sign `
    /f  $PfxPath `
    /p  $PfxPassword `
    /fd sha256 `
    /td sha256 `
    /tr "http://timestamp.sectigo.com" `
    /d  "CSV Operations by Kiran Beethoju" `
    $ExePath

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ Signed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Windows will now show 'Kiran Beethoju' as the publisher." -ForegroundColor White
    Write-Host ""
    Write-Host "NEXT STEPS FOR FULL SMARTSCREEN TRUST:" -ForegroundColor Yellow
    Write-Host "  • Self-signed certs remove 'Unknown Publisher' but SmartScreen" -ForegroundColor Gray
    Write-Host "    may still warn on first run." -ForegroundColor Gray
    Write-Host "  • For zero warnings, buy an EV code-signing cert:" -ForegroundColor Gray
    Write-Host "    DigiCert  → https://www.digicert.com/signing/code-signing-certificates" -ForegroundColor Cyan
    Write-Host "    Sectigo   → https://sectigo.com/ssl-certificates-tls/code-signing" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "✗ Signing failed (exit code $LASTEXITCODE)" -ForegroundColor Red
    exit 1
}
