@echo off
setlocal

:: Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% equ 0 (
    goto :run_demo
)

echo uv is not installed. Installing uv...
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

echo.
echo =======================================================
echo uv has been installed! 
echo Rebooting the terminal to refresh the PATH variables...
echo =======================================================
echo.

:: Launch a new command prompt to refresh PATH and re-run this script
start cmd.exe /k "%~f0"
exit /b 0

:run_demo
echo Setting up environment and installing demo dependencies...
uv venv
call .venv\Scripts\activate.bat
uv pip install -r requirements_demo.txt

echo.
echo Launching the demo in your web browser...
start http://127.0.0.1:8050

echo Running the application...
uv run app.py
