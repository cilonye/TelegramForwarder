$Root = Resolve-Path "$PSScriptRoot\.."
$ServiceName = "TelegramForwarder"
$NSSM = "$Root\deploy\nssm\nssm.exe"

if (Get-Service -Name $ServiceName -ErrorAction SilentlyContinue) {
    & $NSSM stop $ServiceName
    & $NSSM remove $ServiceName confirm
    Write-Host "TelegramForwarder service removed."
} else {
    Write-Host "Service not found."
}
