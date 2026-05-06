@echo off
REM KC-251 News Editor - Launcher
REM УкраїнськА версія

SetLocal EnableDelayedExpansion
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo ===============================================
    echo ПОМИЛКА: Python не встановлено!
    echo ===============================================
    echo.
    echo Завантажте Python з: https://www.python.org
    echo.
    echo При встановленнях вибере опцію:
    echo "Add Python to PATH"
    echo.
    echo ===============================================
    pause
    exit /b 1
)

REM Check if tkinter is available
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    color 0E
    echo.
    echo ===============================================
    echo ПОМИЛКА: tkinter не встановлено!
    echo ===============================================
    echo.
    echo Переінсталюйте Python з опцією:
    echo "tcl/tk and IDLE"
    echo.
    echo ===============================================
    pause
    exit /b 1
)

REM Check if news.json exists
if not exist "news.json" (
    color 0E
    echo.
    echo ===============================================
    echo ПОМИЛКА: Не знайден файл news.json!
    echo ===============================================
    echo.
    echo Переконайтесь, що файл news.json
    echo знаходиться в тій же папці.
    echo.
    echo ===============================================
    pause
    exit /b 1
)

REM Launch the editor
color 0A
echo Запускаю редактор новостей KC-251...
echo.
python news_editor.py

if errorlevel 1 (
    color 0C
    echo.
    echo ПОМИЛКА: Не вдалося запустити програму!
    pause
    exit /b 1
)
