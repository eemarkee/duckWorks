@echo off
REM Activate the Anaconda environment named 'ml'
CALL conda activate ml

REM Run the Python script
python test_organizer.py

REM Pause to keep the command prompt open
pause

REM Deactivate the environment
CALL conda deactivate
