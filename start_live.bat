@echo off
title BongoBazaar - Live Server & Public Tunnel
cd /d "%~dp0"
echo ============================================================
echo      BongoBazaar - Live Public Server Launcher
echo ============================================================
echo [1/2] Starting Local Server on http://127.0.0.1:5000 ...
start /b py app.py
timeout /t 2 >nul
echo [2/2] Generating Public Live Link with Cloudflare Tunnel...
cloudflared.exe tunnel --url http://127.0.0.1:5000
pause
