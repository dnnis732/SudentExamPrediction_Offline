STUDENT EXAM RESULT PREDICTION - PYTHON 3.14 OFFLINE BUILD KIT
=============================================================

BUILD_WINDOWS.bat / BUILD_WINDOWS.ps1
- Run on a Windows x64 build PC with internet and Python 3.14 x64.
- Python 3.14 must be available using the `py -3.14` launcher command.
- The script creates/recreates .venv if it was made with another Python version.
- Installs compatible dependencies and creates dist\StudentExamPrediction.

RUN_APP.bat / RUN_APP.ps1 (inside dist\StudentExamPrediction)
- Copy the entire dist\StudentExamPrediction folder to the offline Windows x64 PC.
- Run either launcher on the offline PC.
- The target PC does not need Python, pip, Flask, NumPy, SciPy, or scikit-learn.
- Keep the application console window open while using the web interface.

RUN_OFFLINE.bat / RUN_OFFLINE.ps1
- Convenience launchers in this build kit. They work after the app is built.
- For distribution, copy the entire dist\StudentExamPrediction folder.

IMPORTANT
- This ZIP is a build kit, not a precompiled Windows EXE.
- Build on Windows; PyInstaller builds for the operating system where it runs.
- Internet is needed on the BUILD PC to download dependencies; the built app
  works locally at http://127.0.0.1:5000 without internet.
- The model was serialized with scikit-learn 1.9.1, so the build pins that
  version to avoid loading it with a different scikit-learn release.
- If the build fails, keep the full error output so the failed step can be fixed.
