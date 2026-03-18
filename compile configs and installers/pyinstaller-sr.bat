"../.venv/Scripts/pyinstaller.exe" --noconfirm --onedir --windowed --clean ^
--workpath C:\Users\jeremy\Desktop\output\work ^
--icon "X:/Documents/Python Workspace/SpeeDReaD/resources/sr_logo.ico" ^
--add-data "X:/Documents/Python Workspace/SpeeDReaD/resources;resources/" ^
--add-data "X:/Documents/Python Workspace/SpeeDReaD/README.md;." ^
--add-data "X:/Documents/Python Workspace/SpeeDReaD/README.html;." ^
--distpath "C:\Users\jeremy\Desktop\output" ^
"../main.py" --name="SpeeDReaD"