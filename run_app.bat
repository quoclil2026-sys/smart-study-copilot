@echo off
title Smart Study Copilot - Khoi chay Ung dung
echo ========================================================
echo   DANG KHOI CHAY SMART STUDY COPILOT...
echo   He thong se tu dong mo trinh duyet sau vai giay!
echo ========================================================
cd /d "%~dp0"
python -m streamlit run app.py
pause
