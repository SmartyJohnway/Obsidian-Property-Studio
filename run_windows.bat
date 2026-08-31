@echo off
REM Obsidian Property Studio - local launcher for Windows 11
REM Requires Python 3.10+ ("py" launcher) and: py -m pip install -r requirements.txt
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py -m app %*
) else (
  python -m app %*
)
endlocal
