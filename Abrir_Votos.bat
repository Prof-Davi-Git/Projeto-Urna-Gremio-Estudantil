@echo off
chcp 65001 >nul
set "PASTA=%~dp0..\Urna_Gremio_Dados_Privados"
if not exist "%PASTA%" (
  echo Ainda nao ha votos oficiais salvos. 
  echo Para testar sem misturar com a eleicao, abra Iniciar_Teste.bat.
  pause
  exit /b
)
start "" "%PASTA%"
