@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Testes locais da urna
echo Testando gravacao, bloqueio, repeticao e apuracao...
echo Nao altera os votos reais.
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -m unittest -v test_servidor_urna
) else (
  python -m unittest -v test_servidor_urna
)
echo.
pause
