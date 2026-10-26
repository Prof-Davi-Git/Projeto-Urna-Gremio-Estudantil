@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Urna Gremio - MODO TESTE
echo ==================================================
echo              MODO TESTE - URNA
echo Votos de teste NUNCA entram na apuracao oficial.
echo ==================================================
echo.
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 servidor_urna.py --teste --porta 8766
) else (
    python servidor_urna.py --teste --porta 8766
)
echo.
pause
