@echo off
setlocal

echo PyInstaller をインストールします...
pip install pyinstaller

echo exe をビルドします...
pyinstaller --onefile --windowed reset_chrome_pref_gui_list.py

echo.
echo dist フォルダ内に exe が生成されました。
pause
