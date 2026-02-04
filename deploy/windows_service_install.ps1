# ================================
# TelegramForwarder Windows Service Installer
# ================================

$ErrorActionPreference = "Stop"

# Project root = parent of deploy/
$Root = Resolve-Path "$PSScriptRoot\.."

$ServiceName = "TelegramForwarder"
$NSSM = "$Root\deploy\nssm\nssm.exe"
$Python = "$Root\venv\Scripts\python.exe"
$App = "$Root\app\main.py"

Write-Host "Installing TelegramForwarder Windows Service from $Root"

# Remove existing service if present
if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    Write-Host "Existing service found. Removing..."
    & $NSSM stop $ServiceName
    & $NSSM remove $ServiceName confirm
}

# Create service
& $NSSM install $ServiceName $Python $App

# Working directory
& $NSSM set $ServiceName AppDirectory $Root

# Restart behavior
& $NSSM set $ServiceName AppExit Default Restart
& $NSSM set $ServiceName RestartDelay 5000

# Logging
& $NSSM set $ServiceName AppStdout "$Root\runtime\logs\service.out.log"
& $NSSM set $ServiceName AppStderr "$Root\runtime\logs\service.err.log"
& $NSSM set $ServiceName AppRotateFiles 1
& $NSSM set $ServiceName AppRotateOnline 1
& $NSSM set $ServiceName AppRotateBytes 10485760

# Startup
Set-Service -Name $ServiceName -StartupType Automatic

# Start service
Start-Service $ServiceName

Write-Host "TelegramForwarder service installed and started successfully."
