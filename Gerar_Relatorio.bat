@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Relatorio da Urna
echo Relatorio de apuracao do Gremio Estudantil
echo Execute de preferencia depois de encerrar a votacao.
echo.
where py >nul 2>&1
if %errorlevel%==0 (
    py -3 servidor_urna.py --relatorio
) else (
    python servidor_urna.py --relatorio
)
echo.
echo O arquivo CSV fica na pasta Urna_Gremio_Dados_Privados
echo criada AO LADO da pasta deste repositorio.
pause
