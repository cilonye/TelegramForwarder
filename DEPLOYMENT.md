# TelegramForwarder – Authoritative Deployment & Operations Guide

> **This document is the single source of truth for deploying, operating, and maintaining TelegramForwarder in production.**
> It is designed to be reused verbatim across servers with zero drift.

---

## 1. Supported Platforms

- Windows Server 2019+
- Windows 10/11 (headless or desktop)
- Ubuntu / Debian / RHEL-based Linux

Scheduler-based execution has been **fully removed**. The application runs **only as a long-running service**.

---

## 2. Architecture Overview

TelegramForwarder is a **long-running, event-driven Telegram daemon**.

### Key Properties
- No polling
- Persistent Telegram connection (Telethon)
- Single process
- Auto-restart on failure
- Graceful shutdown
- Deterministic startup

### Directory Model (Strict)
```
TelegramForwarder/
├── app/        # Application logic
├── utility/    # One-time ops utilities
├── config/     # Runtime configuration
├── runtime/    # Logs, health, state
├── deploy/     # OS automation
```

---

## 3. Configuration Model

### config/config.yaml (Source of Truth)

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

## 4. Secrets Management

Secrets are **encrypted at rest**.

Files:
- `secret.key` – encryption key
- `.env` – encrypted secrets

Utilities:
```bash
python utility/generate_key.py
python utility/encrypt_secrets.py
```

Secrets loaded at runtime via Fernet.

---

## 5. Health & Watchdog System

### Health File

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

---

## 6. Automatic Telegram Session Repair

### Problem Solved
- Corrupt `.session` files
- Auth invalidation
- Telegram-side disconnects

### Behavior

On startup:
1. Attempt client.start()
2. If session fails:
   - Log error
   - Delete session file
   - Re-authenticate
   - Continue without manual intervention

This guarantees **self-healing authentication**.

---

## 7. Windows Deployment (Native Service ONLY)

### Prerequisites

- Python 3.11+
- Administrator access

### Install Steps

```powershell
cd C:\TelegramForwarder
deploy\windows_install.ps1
```

### Install Windows Service (NSSM)

```powershell
cd C:\TelegramForwarder
deploy\windows_service_install.ps1
```

### Verify

- services.msc → TelegramForwarder → Running
- runtime\health.status = RUNNING

### Important

❌ Task Scheduler is NOT used
❌ No scheduled tasks should exist

---

## 8. Linux Deployment (systemd)

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

## 9. Logging

- runtime/logs/forwarder.log
- Rotating, capped at 5MB x 3

Windows Service logs:
- service.out.log
- service.err.log

---

## 10. Redeployment Without Drift

To redeploy:

1. Stop service
2. Replace code
3. Keep:
   - config/
   - runtime/
   - secret.key
   - .env
4. Start service

No state corruption.

---

## 11. Troubleshooting

### Duplicate Messages
- Ensure only ONE service instance

### No Messages Forwarded
- Check keywords
- Check health file
- Check logs

### Service Won’t Start
- Verify venv
- Verify secrets
- Check NSSM logs

---

## 12. Operational Guarantees

✔ Continuous operation
✔ Zero polling
✔ Restart-safe
✔ Crash-safe
✔ Reboot-safe
✔ Ops-friendly
✔ Enterprise-ready

---

## 13. Decommissioning

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

## 14. Final Windows Service Architecture:
Windows Boot
   ↓
TelegramForwarder (Windows Service)
   ↓
venv\Scripts\python.exe app\main.py
   ↓
Async event loop (Telethon)
   ↓
Continuous Telegram connection

## 15. Ops information Summary
### 15.1 Install the Windows Service
#### Run PowerShell as Administrator: 
``` cd C:\TelegramForwarder ```
``` deploy\windows_service_install.ps1```

### 15.2 Verify Service Health
#### 15.2.1 Using Services UI 
services.msc 
→ TelegramForwarder 
→ Status: Running 
→ Startup Type: Automatic 

#### 15.2.2 Using Health File
``` runtime\health.status ```

#### 15.2.3 Using Logs 
runtime\logs\forwarder.log
runtime\logs\service.out.log
runtime\logs\service.err.log

### 15.3 Verify Restart Behavior
#### 15.3.1 Using Powershell commands
``` Stop-Service TelegramForwarder ```

#### 15.3.2 Using Powershell commands
``` Start-Service TelegramForwarder ```

**This document may be reused verbatim for every deployment.**