# TelegramForwarder – Authoritative Deployment & Operations Guide

> **This document is the single source of truth for deploying, operating, and maintaining TelegramForwarder in production.**
> It is designed to be reused verbatim across servers with zero drift.
This document describes:
- Full deployment steps for **Windows and Linux**
- Environment preparation
- Telegram credential generation
- Service installation
- Continuous operation
- **Known deployment errors and exact fixes**

---

## 1. Supported Platforms

- Windows Server 2019+
- Windows 10/11 (headless or desktop)
- Ubuntu / Debian / RHEL-based Linux

Scheduler-based execution has been **fully removed**. The application runs **only as a long-running service**.

### Required
- Administrator / sudo access
- Internet access
- Git
- Python 3.9+

---

## 2. Architecture Overview

TelegramForwarder is a **long-running, event-driven Telegram daemon**.

### Key Properties
- No polling and runs continuously
- Persistent Telegram connection (Telethon)
- Single process
- Auto-restart on failure
- Graceful shutdown
- Deterministic startup
- Auto-restart on failure
- Survive reboots
- Use `config.yaml` as default truth
- Allow environment variable overrides

### Directory Model (Strict Deployment Design model)
```
TelegramForwarder/
├── app/        # Application logic
├── utility/    # One-time ops utilities
├── config/     # Runtime configuration
├── runtime/    # Logs, health, state
├── deploy/     # OS automation
```

---

## 3. Python and Git Installation

### Windows

1. Download Python from https://www.python.org/downloads/windows/. Download Git from: https://git-scm.com/download/win

During installation:
   - **Add Python to PATH**
   - Install for all users

2. Verify:
```powershell
python --version
pip --version
git --version
```

### Linux

1. Download 
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

2. Verify:
```bash
python3 --version
pip3 --version
git --version
```
## 4. Project Setup
###  Recommended Paths to clone Repository

You must see the file contents

```
git clone <REPO_URL> TelegramForwarder
cd TelegramForwarder
dir
```

- Windows (avoid spaces if possible):
```powershell
C:\TelegramForwarder
ls
```

- Linux:
```bash
/opt/TelegramForwarder
```

## 5. Create Virtual Environment
###  Create venv
```
python -m venv venv
```
###  Activate venv

- Windows
```powershell
venv\Scripts\activate
```

- Linux
```bash
source venv/bin/activate
```

### Verify Python Executable Exists
Test python executable in windows. If false, stop and recreate the venv.

```powershell
Test-Path .\venv\Scripts\python.exe
```
Must return: `True`

###  Install Dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

## 6. Telegram API Credentials
###  Generate API ID & Hash
1. Go to https://my.telegram.org
2. Login with your Telegram phone number
3. Select API development tools
4. Create an app
5. Save for later encryption:
   - api_id
   - api_hash (SECRET)

### Secrets Management
Secrets are **encrypted at rest**. This encryption generates the following files.
Run the ```generate_key.py``` and the ```encrypt_secrets.py``` in sequence to generate encryption key and to ecrypt the keys.
Secrets loaded at runtime via Fernet.

Files:
- `secret.key` – encryption key
- `.env` – encrypted secrets

Utilities:

- Windows
```powershell
utility/generate_key.py
utility/encrypt_secrets.py
```

- Linux
```bash
python utility/generate_key.py
python utility/encrypt_secrets.py
```

### Configure config/config.yaml (Source of Truth)
1. Run the ```list_telegram_chat.py``` script to ensure you have the right source and destination chat IDs.
2. Update the config yaml any Keyword a message must have before it can be forwarded. Keep empty if you want to forward all.
```yaml
telegram:
  source_chat_id: 123456
  destination_chat_ids:
    - -100111
    - -100222
  keywords:
    - alert
    - signal
```

### Environment Overrides (Optional)

| Variable | Effect |
|-------|-------|
| TF_SOURCE_CHAT_ID | Override source chat |
| TF_DESTINATION_CHAT_IDS | Comma-separated IDs |
| TF_KEYWORDS | Comma-separated keywords |
| TF_DISABLE_KEYWORDS | Disable filtering |

Overrides are applied **once at startup**.

---

## 7. First Mandatory Manual Run (CRITICAL)

This step must succeed before installing as a service. This creates the `.session` file.

You will be prompted to:
- Enter phone number
- Enter OTP

> Services cannot accept interactive input. Skipping this step guarantees service failure.

> Stop with Ctrl+C.

- Windows (PowerShell)
```powershell
cd C:\TelegramForwarder
& .\venv\Scripts\python.exe .\app\main.py
```

- Linux
```bash
Linux
python main.py
```

### Health File
Use this file to check the status of the run during the manual run.

```
runtime/health.status
```

States:
- STARTING
- RUNNING
- STOPPING
- STOPPED
- DEGRADED

### Watchdog Logic (Service-Level)

- If process exits → Service restarts
- If Telegram disconnects → Telethon reconnects
- If session becomes invalid → Automatic session repair (see below)


----

## 8. Windows Service Deployment (NSSM)
   ### 8.1 Download NSSM

- Download from: https://nssm.cc/download. Extract the ZIP.
- Place nssm.exe in: `C:\TelegramForwarder\deploy\nssm\nssm.exe`
- Verify: `Test-Path deploy\nssm\nssm.exe`

### 8.2 Install the Service

- Run the `windows_service_install.ps1` script. This script will:

   - Remove any existing TelegramForwarder service
   - Register python.exe as the service executable
 
   - Pass run.py safely via AppParameters
 
   - Set working directory
 
   - Configure restart policy
 
   - Configure log files
    
   - Start the service

```powershell
deploy\windows_service_install.ps1
```

- Debugging the `windows_service_install.ps1` script failure.

   - Paths with spaces MUST be quoted and passed via AppParameters. I encourage not to use paths with spaces for the project.
   - Run Service as Correct User (IMPORTANT)

      - By default, NSSM runs as LocalSystem. This LocalSystem user often cannot access files created by you in the Project directory, the virtual environment, the `.session` file
       
      - The fix is to edit the nssm:
      
         
         ``` C:\TelegramForwarder\deploy\nssm\nssm edit < Service_Name eg TelegramForwarder> ```
      - Set:
         
          Click `Log on` → Select `This account` → Enter `.\<YourWindowsUsername>` → Enter and comfirm your password → Apply and Ok.

          > You can look through the other tabs to ensure that the seeting aligns with your `windows_service_install.py` script.
      
      - Restart the service by running this command in powershell:
         
         `Start-Service TelegramForwarder`
      
      - Verify if the service is running by running this command in powershell: 
      
         `Get-Service TelegramForwarder`

### 8.3 Verify Logs

Open:

```
runtime\logs\service.out.log
runtime\logs\service.err.log
runtime\logs\telegram_forwarder.log
```
### 8.4 How to Safely Redeploy
This is safe to repeat indefinitely.

- Stop the service
``` Stop-Service TelegramForwarder ```

- Go to the folders and pull the new code.
``` git pull ```

- Reinstall requirements
``` .\venv\Scripts\pip.exe install -r requirements.txt ```

- Restart the services:
``` Restart-Service TelegramForwarder ```

### 8.5. Final Windows-Specific Rules (Non-Negotiable)

- Use `app\main.py` as entry point.

- Always quote paths with spaces. Perferabbly, don't use paths with spaces.

- Always complete Telegram auth manually especially if no `.session` file is present in the project.

- Always run NSSM service as the same user.

- If manual run fails, service will fail.

---

## 9. Logging

- runtime/logs/forwarder.log
- Rotating, capped at 5MB x 3

Windows Service logs:
- service.out.log
- service.err.log

---
 
## 10. Linux Deployment (systemd)

```bash
cd /opt/TelegramForwarder
chmod +x deploy/linux_install.sh
deploy/linux_install.sh

sudo cp deploy/telegramforwarder.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegramforwarder
sudo systemctl start telegramforwarder
```

Verify:
```bash
systemctl status telegramforwarder
cat runtime/health.status
```

---

## 11. Troubleshooting

### Run exactly what the service runs:
> The code below is a sample powershell command for a `C:\TelegramForwarder` root directory project. If this fails, the service will fail.

```powershell
& "C:\TelegramForwarder\venv\Scripts\python.exe" "C:\TelegramForwarder\run.py"
```

### No Messages Forwarded
- Check keywords
- Check health file
- Check logs

### Service Won’t Start
- Verify venv
- Verify secrets
- Check NSSM logs

---

## 12. Decommissioning

Windows:
```powershell
deploy\windows_service_uninstall.ps1
```

Linux:
```bash
sudo systemctl stop telegramforwarder
sudo systemctl disable telegramforwarder
```

---

## 13. Final Windows Service Architecture:
```
Windows Boot
   ↓
TelegramForwarder (Windows Service)
   ↓
venv\Scripts\python.exe app\main.py
   ↓
Async event loop (Telethon)
   ↓
Continuous Telegram connection
```

**This document may be reused verbatim for every deployment.**