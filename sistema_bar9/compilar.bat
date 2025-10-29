@echo off
echo Compilando Sistema Bar...
echo.

echo 1. Limpando compilações anteriores...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo 2. Criando diretórios necessários...
mkdir recibos 2>nul
mkdir recibos_pdf 2>nul
mkdir logs 2>nul

echo 3. Compilando com PyInstaller...
pyinstaller sistema_bar.spec

echo.
echo Compilação concluída!
echo O executável está em: dist\SistemaBar\
echo.
echo Para testar:
echo   dist\SistemaBar\SistemaBar.exe touchscreen
echo   dist\SistemaBar\SistemaBar.exe gerente
pause