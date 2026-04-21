param(
    [switch]$Clean,
    [switch]$SkipPortableZip,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$distDir = Join-Path $root "dist\AtlasXCursorStudio"
$releaseDir = Join-Path $root "release"
$portableZip = Join-Path $releaseDir "AtlasXCursorStudio-portable.zip"
$installerScript = Join-Path $PSScriptRoot "installer.iss"
$installerPath = Join-Path $releaseDir "AtlasXCursorStudio-Setup-1.0.exe"

Write-Host "Building Atlas-X Cursor Studio release..."
$buildScript = Join-Path $PSScriptRoot "build.ps1"
if ($Clean) {
    & $buildScript -Clean
} else {
    & $buildScript
}

if (-not (Test-Path $distDir)) {
    throw "Missing dist directory: $distDir"
}

New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

if (-not $SkipPortableZip) {
    if (Test-Path $portableZip) {
        Remove-Item $portableZip -Force
    }
    Write-Host "Creating portable package: $portableZip"
    Compress-Archive -Path (Join-Path $distDir '*') -DestinationPath $portableZip -CompressionLevel Optimal
    if (-not (Test-Path $portableZip)) {
        throw "Portable package was not created: $portableZip"
    }
}

if ($SkipInstaller) {
    Write-Warning "Installer build skipped by parameter."
    exit 0
}

$isccCandidates = @(
    @(
        (Get-Command ISCC.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
        'C:\Program Files (x86)\Inno Setup 6\ISCC.exe',
        'C:\Program Files\Inno Setup 6\ISCC.exe',
        'C:\Users\zhangxi\AppData\Local\Programs\Inno Setup 6\ISCC.exe'
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique
)

if (-not $isccCandidates) {
    Write-Warning "Inno Setup 未安装，已生成便携压缩包。安装 Inno Setup 6 后重新运行 scripts\build_release.ps1 可生成安装器。"
    exit 0
}

$iscc = $isccCandidates[0]
Write-Host "Building installer with Inno Setup: $iscc"
& $iscc $installerScript
if (-not (Test-Path $installerPath)) {
    throw "Installer build finished but expected output was not found: $installerPath"
}

Write-Host "Installer build complete. Output directory: release"
Write-Host "Portable package: $portableZip"
Write-Host "Installer package: $installerPath"
