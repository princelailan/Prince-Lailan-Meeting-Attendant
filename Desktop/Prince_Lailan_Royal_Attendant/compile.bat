@echo off
pyinstaller --onefile --windowed --icon=assets/tiara.ico --add-data "royal_schedule.csv;." --add-data "tiara.png;." princess_lailan_meetings.py
mkdir dist\Royal_Package
copy dist\princess_lailan_meetings.exe dist\Royal_Package
copy royal_schedule.csv dist\Royal_Package
copy tiara.png dist\Royal_Package
cd dist
powershell Compress-Archive -Path Royal_Package -DestinationPath Prince_Lailan_Royal_Attendant.zip

--splash assets/royal_splash.png