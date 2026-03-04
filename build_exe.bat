@echo off
setlocal

echo PyInstaller をインストールします / Installing PyInstaller...
pip install pyinstaller

echo exe をビルドします / Building exe...
pyinstaller --onefile --windowed reset_chrome_pref_gui_list.py

echo.
echo dist フォルダに exe が生成されました / exe created in dist folder.
pause
