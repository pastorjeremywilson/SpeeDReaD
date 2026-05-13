"../.win_venv/Scripts/pyinstaller.exe" --noconfirm --onedir --windowed --clean ^
--workpath C:\Users\pasto\Desktop\output\work ^
--icon "../resources/sr_logo.ico" ^
--add-data "../resources;resources/" ^
--add-data "../README.md;." ^
--add-data "../README.html;." ^
--distpath "C:\Users\pasto\Desktop\output" ^
"../main.py" --name="SpeeDReaD"