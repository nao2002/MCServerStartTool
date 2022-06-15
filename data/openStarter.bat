@echo off
cd /d %~dp0
if exist "%~2"\"%~3" (
    start "MCServer" startServer %1 %2 %3 %4 %5 %6
) else (
    exit 1
)