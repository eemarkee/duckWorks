@echo off
REM Navigate to the directory where the Python script is located
cd /d "D:\duckWorks\utilities\python\scripts\windowStore"

REM Run the Python script with the --load command
"C:\ProgramData\Anaconda3\envs\ml\python.exe" windowStore.py --load "testLayout.json"

REM Pause to keep the command prompt open (optional)
::pause
