@echo off
setlocal

set SCRIPT_DIR=%~dp0

where python >nul 2>nul
if errorlevel 1 (
    echo Python が見つかりません / Python not found.
    echo https://www.python.org/ からインストールしてください / Please install from https://www.python.org/
    pause
    exit /b
)

python "%SCRIPT_DIR%reset_chrome_pref_gui_list.py"

echo.
echo 終了しました / Done.
pause
