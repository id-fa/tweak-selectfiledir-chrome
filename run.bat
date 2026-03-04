@echo off
setlocal

set SCRIPT_DIR=%~dp0

where python >nul 2>nul
if errorlevel 1 (
    echo Python が見つかりません。
    echo https://www.python.org/ からインストールしてください。
    pause
    exit /b
)

python "%SCRIPT_DIR%reset_chrome_pref_gui_list.py"

echo.
echo 終了しました。
pause
