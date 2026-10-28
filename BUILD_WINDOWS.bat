@echo off
setlocal
cd /d "%~dp0"
title Student Exam Prediction - Python 3.14 Offline Builder

echo ==========================================================
echo BUILD STANDALONE WINDOWS APP - PYTHON 3.14
echo ==========================================================
echo BUILD PC requires Windows x64, Python 3.14 x64, and internet.
echo OFFLINE PC requires Windows x64 only; no Python or internet.
echo.

where py >nul 2>nul
if errorlevel 1 goto no_launcher
py -3.14 --version
if errorlevel 1 goto no_python

rem Recreate the virtual environment to ensure it uses Python 3.14.
if exist ".venv" rmdir /s /q ".venv"
if exist ".venv" goto venv_remove_failed
py -3.14 -m venv .venv
if errorlevel 1 goto venv_failed

set "PYTHON=%CD%\.venv\Scripts\python.exe"
"%PYTHON%" --version
if errorlevel 1 goto venv_failed

echo.
echo Installing Python 3.14-compatible dependencies...
"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 goto install_failed
"%PYTHON%" -m pip install -r requirements-build.txt
if errorlevel 1 goto install_failed

if not exist "app.py" goto missing_app
if not exist "model.pkl" goto missing_model

echo.
echo Building the standalone application...
"%PYTHON%" -m PyInstaller --noconfirm --clean --onedir --console --name StudentExamPrediction --collect-all flask --collect-all sklearn --collect-all numpy --collect-all scipy --collect-all joblib --collect-all threadpoolctl app.py
if errorlevel 1 goto build_failed

copy /Y model.pkl dist\StudentExamPrediction\model.pkl >nul
if errorlevel 1 goto copy_failed
if not exist "dist\StudentExamPrediction\prediction_history.json" copy /Y prediction_history.json dist\StudentExamPrediction\prediction_history.json >nul

rem Create the launch scripts without parenthesized command blocks.
echo @echo off>dist\StudentExamPrediction\RUN_APP.bat
echo cd /d "%%~dp0">>dist\StudentExamPrediction\RUN_APP.bat
echo start "" "StudentExamPrediction.exe">>dist\StudentExamPrediction\RUN_APP.bat

echo $ErrorActionPreference = 'Stop'>dist\StudentExamPrediction\RUN_APP.ps1
echo Set-Location -LiteralPath $PSScriptRoot>>dist\StudentExamPrediction\RUN_APP.ps1
echo Start-Process -FilePath (Join-Path $PSScriptRoot 'StudentExamPrediction.exe')>>dist\StudentExamPrediction\RUN_APP.ps1

echo STUDENT EXAM RESULT PREDICTION - OFFLINE>dist\StudentExamPrediction\README_OFFLINE.txt
echo Copy this entire folder to the offline Windows PC.>>dist\StudentExamPrediction\README_OFFLINE.txt
echo Run RUN_APP.bat or RUN_APP.ps1.>>dist\StudentExamPrediction\README_OFFLINE.txt
echo No Python, pip, Flask, NumPy, SciPy, or scikit-learn installation is needed on the target PC.>>dist\StudentExamPrediction\README_OFFLINE.txt
echo Browser opens at http://127.0.0.1:5000.>>dist\StudentExamPrediction\README_OFFLINE.txt
echo Keep the application console window open while using the application.>>dist\StudentExamPrediction\README_OFFLINE.txt

echo.
echo BUILD SUCCESSFUL.
echo Copy the ENTIRE folder below to USB, then to the offline PC:
echo %CD%\dist\StudentExamPrediction
echo.
pause
exit /b 0

:no_launcher
echo ERROR: Python Launcher py.exe was not found.
echo Install Python 3.14 x64 with the Python Launcher enabled.
goto failed
:no_python
echo ERROR: Python 3.14 was not found by py -3.14.
echo Confirm Python 3.14 x64 is installed correctly.
goto failed
:venv_remove_failed
echo ERROR: Could not remove the existing .venv folder. Close programs using it and retry.
goto failed
:venv_failed
echo ERROR: Could not create or run the Python 3.14 virtual environment.
goto failed
:install_failed
echo ERROR: Dependency installation failed. Check the internet and pip output above.
goto failed
:missing_app
echo ERROR: app.py is missing from this folder.
goto failed
:missing_model
echo ERROR: model.pkl is missing from this folder.
goto failed
:build_failed
echo ERROR: PyInstaller build failed. Review the error output above.
goto failed
:copy_failed
echo ERROR: Could not copy model.pkl into the build folder.
goto failed
:failed
echo.
echo BUILD FAILED. Review the error above.
pause
exit /b 1
