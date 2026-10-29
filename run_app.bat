@echo off
cd /d "%~dp0"
title QueryChat RAG Assistant
echo Starting QueryChat GUI...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%.
    pause
)

