@echo off
setlocal EnableExtensions EnableDelayedExpansion

chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

for %%I in ("%~dp0.") do set "ROOT=%%~fI"
cd /d "%ROOT%"

if defined SHD_VENV_DIR (
    for %%I in ("%SHD_VENV_DIR%") do set "VENV_DIR=%%~fI"
) else (
    set "VENV_DIR=%ROOT%\.venv"
)

if defined SHD_LOCAL_PY_DIR (
    for %%I in ("%SHD_LOCAL_PY_DIR%") do set "LOCAL_PY_DIR=%%~fI"
) else (
    set "LOCAL_PY_DIR=%ROOT%\.python311"
)

set "APP_FILE=%ROOT%\main.py"
set "REQ_FILE=%ROOT%\requirements.txt"
set "DOWNLOAD_DIR=%ROOT%\.downloads"
set "PYTHON_VERSION=3.11.11"
set "PYTHON_INSTALLER=python-%PYTHON_VERSION%-amd64.exe"
set "PYTHON_MIRROR_URL=https://mirrors.tuna.tsinghua.edu.cn/python/%PYTHON_VERSION%/%PYTHON_INSTALLER%"
set "PYTHON_OFFICIAL_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/%PYTHON_INSTALLER%"
set "PIP_MIRROR_TUNA=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"
set "PIP_MIRROR_USTC=https://mirrors.ustc.edu.cn/pypi/simple"

set "NO_LAUNCH="
if /I "%~1"=="--no-launch" set "NO_LAUNCH=1"

if not exist "%APP_FILE%" (
    echo [ERROR] main.py not found.
    goto :fail
)

if not exist "%REQ_FILE%" (
    echo [ERROR] requirements.txt not found.
    goto :fail
)

set "RUN_PY="
set "BASE_PY="
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

call :resolve_venv_python
if defined RUN_PY goto :deps

call :resolve_base_python
if not defined BASE_PY (
    call :install_python
    if errorlevel 1 goto :fail
    set "BASE_PY=%LOCAL_PY_DIR%\python.exe"
)

call :create_venv
if errorlevel 1 goto :fail
set "RUN_PY=%VENV_DIR%\Scripts\python.exe"

:deps
call :ensure_dependencies "%RUN_PY%"
if errorlevel 1 goto :fail

if defined NO_LAUNCH (
    echo [OK] Environment is ready.
    goto :success
)

echo [INFO] Starting GUI...
"%RUN_PY%" "%APP_FILE%"
set "APP_EXIT=%ERRORLEVEL%"
if not "%APP_EXIT%"=="0" (
    echo [ERROR] main.py exited with code %APP_EXIT%.
    goto :fail
)

goto :success

:resolve_venv_python
if exist "%VENV_PY%" (
    call :accept_python "%VENV_PY%"
    if not errorlevel 1 (
        set "RUN_PY=%VENV_PY%"
        echo [INFO] Using existing virtual environment.
    )
)
exit /b 0

:resolve_base_python
if exist "%LOCAL_PY_DIR%\python.exe" (
    call :accept_python "%LOCAL_PY_DIR%\python.exe"
    if not errorlevel 1 (
        set "BASE_PY=%LOCAL_PY_DIR%\python.exe"
        echo [INFO] Using project-local Python.
        exit /b 0
    )
)

for %%I in (
    "%LocalAppData%\Programs\Python\Python310\python.exe"
    "%LocalAppData%\Programs\Python\Python311\python.exe"
    "%ProgramFiles%\Python310\python.exe"
    "%ProgramFiles%\Python311\python.exe"
    "%ProgramFiles%\Python\Python310\python.exe"
    "%ProgramFiles%\Python\Python311\python.exe"
) do (
    call :accept_python "%%~fI"
    if not errorlevel 1 (
        set "BASE_PY=%%~fI"
        echo [INFO] Found system Python: %%~fI
        exit /b 0
    )
)

for /f "delims=" %%I in ('where.exe python 2^>nul') do (
    call :accept_python "%%~fI"
    if not errorlevel 1 (
        set "BASE_PY=%%~fI"
        echo [INFO] Found Python from PATH: %%~fI
        exit /b 0
    )
)

exit /b 0

:accept_python
set "CANDIDATE=%~f1"
if "%CANDIDATE%"=="" exit /b 1
if not exist "%CANDIDATE%" exit /b 1
echo(!CANDIDATE!| findstr /I /C:"\WindowsApps\" >nul
if not errorlevel 1 exit /b 1
"%~1" -c "import sys; raise SystemExit(0 if (3,10) <= sys.version_info[:2] < (3,12) else 1)" >nul 2>&1
if errorlevel 1 exit /b 1
exit /b 0

:install_python
echo [INFO] No usable Python found. Installing Python %PYTHON_VERSION% to .python311 ...
if not exist "%DOWNLOAD_DIR%" mkdir "%DOWNLOAD_DIR%" >nul 2>&1
set "INSTALLER_PATH=%DOWNLOAD_DIR%\%PYTHON_INSTALLER%"

call :download_file "%PYTHON_MIRROR_URL%" "%INSTALLER_PATH%"
if errorlevel 1 (
    echo [WARN] TUNA Python mirror download failed, retrying from python.org ...
    call :download_file "%PYTHON_OFFICIAL_URL%" "%INSTALLER_PATH%"
    if errorlevel 1 (
        echo [ERROR] Failed to download Python installer.
        exit /b 1
    )
)

if not exist "%LOCAL_PY_DIR%" mkdir "%LOCAL_PY_DIR%" >nul 2>&1

start "" /wait "%INSTALLER_PATH%" /quiet InstallAllUsers=0 TargetDir="%LOCAL_PY_DIR%" AssociateFiles=0 Shortcuts=0 PrependPath=0 Include_doc=0 Include_test=0 Include_launcher=0 Include_tcltk=1 Include_pip=1 Include_venv=1 SimpleInstall=0
if not exist "%LOCAL_PY_DIR%\python.exe" (
    echo [ERROR] Python install did not produce %LOCAL_PY_DIR%\python.exe
    exit /b 1
)

echo [INFO] Python installed to %LOCAL_PY_DIR%
exit /b 0

:download_file
set "DL_URL=%~1"
set "DL_OUT=%~2"
if exist "%DL_OUT%" del /f /q "%DL_OUT%" >nul 2>&1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%DL_URL%' -OutFile '%DL_OUT%'" >nul
if errorlevel 1 exit /b 1
if not exist "%DL_OUT%" exit /b 1
exit /b 0

:create_venv
echo [INFO] Creating virtual environment...
if exist "%VENV_DIR%" (
    "%BASE_PY%" -m venv "%VENV_DIR%" --clear
 ) else (
    "%BASE_PY%" -m venv "%VENV_DIR%"
)
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
)
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [ERROR] Virtual environment is incomplete.
    exit /b 1
)
exit /b 0

:ensure_dependencies
set "TARGET_PY=%~1"
"%TARGET_PY%" -c "import PySide6, cv2, numpy, PIL, yaml, scipy, pandas, seaborn, torch, torchvision" >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Dependencies already available.
    exit /b 0
)

echo [INFO] Installing dependencies from domestic mirrors...
call :install_with_mirror "%TARGET_PY%" "%PIP_MIRROR_TUNA%"
if errorlevel 1 (
    echo [WARN] TUNA mirror install failed, retrying with USTC mirror...
    call :install_with_mirror "%TARGET_PY%" "%PIP_MIRROR_USTC%"
    if errorlevel 1 (
        echo [ERROR] Dependency installation failed.
        exit /b 1
    )
)

"%TARGET_PY%" -c "import PySide6, cv2, numpy, PIL, yaml, scipy, pandas, seaborn, torch, torchvision" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Dependencies still missing after installation.
    exit /b 1
)

echo [INFO] Dependencies installed successfully.
exit /b 0

:install_with_mirror
set "TARGET_PY=%~1"
set "MIRROR_URL=%~2"
"%TARGET_PY%" -m pip install --upgrade pip setuptools wheel -i "%MIRROR_URL%" --retries 2 --timeout 120
if errorlevel 1 exit /b 1
"%TARGET_PY%" -m pip install --prefer-binary -r "%REQ_FILE%" -i "%MIRROR_URL%" --retries 2 --timeout 120
if errorlevel 1 exit /b 1
exit /b 0

:fail
echo.
echo [FAIL] Startup script failed.
if not defined NO_LAUNCH pause
exit /b 1

:success
endlocal
exit /b 0
