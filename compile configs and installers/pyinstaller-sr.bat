"../venv/Scripts/pyinstaller.exe" --noconfirm --onedir --windowed --clean ^
--workpath C:\Users\pasto\Desktop\output\work ^
--icon "X:/Documents/Python Workspace/SpeeDReaD/src/resources/icons.ico" ^
--add-data "X:/Documents/Python Workspace/SpeeDReaD/src/resources;resources/" ^
--add-data "X:/Documents/Python Workspace/SpeeDReaD/src;src/" ^
--add-data "X:/Documents/Python Workspace/SpeeDReaD/README.md;." ^
--add-data "X:/Documents/Python Workspace/SpeeDReaD/README.html;." ^
--distpath "C:\Users\pasto\Desktop\output" ^
"../src/SpeeDReaD.py" --name="SpeeDReaD"