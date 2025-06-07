@echo off
REM Compilation de createur_miniature_optimise_final.py en .exe
pyinstaller --noconfirm --onefile --windowed --icon=mon_icone.ico createur_miniature_optimise_final.py
pause
