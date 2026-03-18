../.linux_venv/bin/pyinstaller --noconfirm --clean --windowed -i "../resources/icon.ico" \
--add-data="../resources:resources/" \
--add-data="../README.md:." \
--add-data="../README.html:." \
--distpath="/home/jeremy/Desktop/output/dist/SpeeDReaD" \
--workpath="/home/jeremy/Desktop/output/work/SpeeDReaD" \
--name=SpeeDReaD ../main.py
pause
