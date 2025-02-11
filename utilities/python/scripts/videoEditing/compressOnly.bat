@echo off
REM Check if an argument (file path) was provided
if "%~1"=="" (
    echo Please drag and drop a video file onto this .bat file.
    pause
    exit /b
)

REM Call the Python script with the "none" direction
python "%~dp0rotateFunctions\rotateVideo.py" "%~1" none nvidia 28

REM Keep the command prompt open to view any output or errors
if %errorlevel% neq 0 (
    echo An error occurred. Press any key to close...
    pause
)
