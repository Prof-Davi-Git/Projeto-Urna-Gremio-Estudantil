@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Urna Gremio - Servidor Local
echo ============================================
echo        URNA DO GREMIO ESTUDANTIL
echo ============================================
echo A janela precisa permanecer aberta durante a votacao.
echo.
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 servidor_urna.py
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        python servidor_urna.py
    ) else (
        echo ERRO: Python 3 nao foi encontrado neste computador.
        echo Instale Python 3 antes do dia da eleicao.
    )
)
echo.
echo O servidor foi encerrado.
pause
