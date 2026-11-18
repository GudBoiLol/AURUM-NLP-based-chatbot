@echo off
title AURUM - AI Chatbot Server
color 0E
echo.
echo  ═══════════════════════════════════════════
echo     AURUM — Adaptive Understanding ^& 
echo     Response Unified Model
echo     NLP Chatbot v1.0
echo  ═══════════════════════════════════════════
echo.
echo  Installing dependencies...
pip install -r requirements.txt --quiet
echo.
echo  Starting AURUM server...
echo  Open your browser at: http://127.0.0.1:5000
echo.
python app.py
pause
