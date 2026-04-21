param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$projectExe = Join-Path $PSScriptRoot "..\dist\AtlasXCursorStudio\AtlasXCursorStudio.exe"
$running = Get-Process AtlasXCursorStudio -ErrorAction SilentlyContinue | Where-Object { $_.Path -eq (Resolve-Path $projectExe -ErrorAction SilentlyContinue) }
if ($running) {
    Write-Host "Stopping running Atlas-X Cursor Studio before build..."
    $running | Stop-Process -Force
    Start-Sleep -Milliseconds 800
}

Write-Host "Building Atlas-X Cursor Studio with PyInstaller..."
$buildArgs = @("-m", "PyInstaller", "--noconfirm", "atlas_cursor_studio.spec")
if ($Clean) {
    $buildArgs += "--clean"
}
python @buildArgs
Write-Host "Build complete. Output directory: dist\AtlasXCursorStudio"
Write-Host "Executable: dist\AtlasXCursorStudio\AtlasXCursorStudio.exe"
