@echo off
REM AETHER C2 Server Startup Script for Windows
REM Provides convenient server launching with IP and port options

setlocal enabledelayedexpansion

REM Colors (using Windows 10+ color codes)
set "INFO=[*]"
set "SUCCESS=[+]"
set "ERROR=[-]"

REM Default values
set "HOST=0.0.0.0"
set "PORT=443"

REM Parse arguments
:parse_args
if "%1"=="" goto start_server
if "%1"=="--help" goto show_help
if "%1"=="-h" (
    if "%2"=="" (
        echo %ERROR% Missing value for -h
        goto show_help
    )
    set "HOST=%2"
    shift
    shift
    goto parse_args
)
if "%1"=="--host" (
    if "%2"=="" (
        echo %ERROR% Missing value for --host
        goto show_help
    )
    set "HOST=%2"
    shift
    shift
    goto parse_args
)
if "%1"=="--port" (
    if "%2"=="" (
        echo %ERROR% Missing value for --port
        goto show_help
    )
    set "PORT=%2"
    shift
    shift
    goto show_help
)
if "%1"=="-p" (
    if "%2"=="" (
        echo %ERROR% Missing value for -p
        goto show_help
    )
    set "PORT=%2"
    shift
    shift
    goto parse_args
)
echo %ERROR% Unknown option: %1
goto show_help

:show_help
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║           AETHER C2 SERVER - STARTUP SCRIPT (WINDOWS)              ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo USAGE:
echo   start_server.bat [OPTIONS]
echo.
echo OPTIONS:
echo   -h, --host HOST     Set bind host/IP (default: 0.0.0.0)
echo   -p, --port PORT     Set bind port (default: 443)
echo   --help              Show this help message
echo.
echo EXAMPLES:
echo   start_server.bat                          # Start on 0.0.0.0:443
echo   start_server.bat --host 127.0.0.1         # Start on 127.0.0.1:443
echo   start_server.bat --port 8443              # Start on 0.0.0.0:8443
echo   start_server.bat -h 192.168.1.100 -p 9999  # Custom host and port
echo.
echo COMMON SCENARIOS:
echo   Local testing:      start_server.bat --host 127.0.0.1 --port 8443
echo   Private network:    start_server.bat --host 192.168.1.100 --port 443
echo   Public facing:      start_server.bat --host 0.0.0.0 --port 443
echo   Custom port:        start_server.bat --port 5000
echo.
exit /b 1

:start_server
cls
echo.
echo ╔════════════════════════════════════════════════════════════════════╗
echo ║                    AETHER C2 SERVER                               ║
echo ║                   Starting Server...                              ║
echo ╚════════════════════════════════════════════════════════════════════╝
echo.
echo %INFO% Configuration:
echo   Host: %HOST%
echo   Port: %PORT%
echo.
echo %SUCCESS% Starting AETHER server...
echo.

REM Change to server directory
cd /d "%~dp0server" || (
    echo %ERROR% Cannot find server directory
    exit /b 1
)

REM Check if Python is available
where python >nul 2>nul
if errorlevel 1 (
    where python3 >nul 2>nul
    if errorlevel 1 (
        echo %ERROR% Python is not installed or not in PATH
        exit /b 1
    )
    set "PYTHON=python3"
) else (
    set "PYTHON=python"
)

REM Check if aether_server.py exists
if not exist "aether_server.py" (
    echo %ERROR% aether_server.py not found
    exit /b 1
)

REM Start the server with arguments
%PYTHON% aether_server.py --host %HOST% --port %PORT%
