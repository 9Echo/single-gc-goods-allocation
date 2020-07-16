@echo off
python manage.py
taskkill /f /im cmd.exe
exit