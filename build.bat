@echo off
echo Diretorio atual:
cd
echo.

echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

echo.
echo Instalando dependencias necessarias...
python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install mysql-connector-python
python -m pip install python-dotenv
python -m pip install werkzeug

echo.
echo Criando arquivos .spec...
python -m PyInstaller --name Sistema_Escolar --onefile --windowed --add-data ".env;." --add-data "db_config.py;." --hidden-import mysql.connector --hidden-import dotenv --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.messagebox --hidden-import mysql.connector.locales.eng --hidden-import mysql.connector.locales.pt_BR main.py

python -m PyInstaller --name Cadastro_Usuario --onefile --windowed --add-data ".env;." --add-data "db_config.py;." --hidden-import mysql.connector --hidden-import dotenv --hidden-import tkinter --hidden-import tkinter.ttk --hidden-import tkinter.messagebox --hidden-import mysql.connector.locales.eng --hidden-import mysql.connector.locales.pt_BR cadastro_usuario.py

echo.
echo Verificando se o arquivo .env existe...
if not exist .env (
    echo ERRO: Arquivo .env nao encontrado!
    pause
    exit /b 1
)

echo.
echo Criando executaveis...
echo.

REM Executa o PyInstaller com mais informacoes
python -m PyInstaller --clean --noconfirm Sistema_Escolar.spec
if errorlevel 1 (
    echo ERRO ao criar Sistema_Escolar.exe
    pause
    exit /b 1
)

python -m PyInstaller --clean --noconfirm Cadastro_Usuario.spec
if errorlevel 1 (
    echo ERRO ao criar Cadastro_Usuario.exe
    pause
    exit /b 1
)

echo.
echo Verificando se os executaveis foram criados...
if exist dist\Sistema_Escolar.exe (
    echo Sistema_Escolar.exe criado com sucesso!
) else (
    echo ERRO: Sistema_Escolar.exe nao foi criado!
)

if exist dist\Cadastro_Usuario.exe (
    echo Cadastro_Usuario.exe criado com sucesso!
) else (
    echo ERRO: Cadastro_Usuario.exe nao foi criado!
)

echo.
echo Copiando arquivo .env para a pasta dist...
copy .env dist\.env

echo.
echo Pressione qualquer tecla para abrir a pasta dist...
pause > nul
start explorer dist 