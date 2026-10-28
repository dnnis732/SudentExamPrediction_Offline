@echo off
setlocal
cd /d "%~dp0"
if not exist "dist\StudentExamPrediction\RUN_APP.bat" (
  echo The standalone app has not been built yet.
  echo Run BUILD_WINDOWS.bat first on a Windows PC with internet.
  pause
  exit /b 1
)
call "dist\StudentExamPrediction\RUN_APP.bat"
