@echo off
title Day du an len GitHub
echo ===================================================================
echo               HUONG DAN DAY DU AN LEN GITHUB
echo ===================================================================
echo 1. Hay vao https://github.com tao 1 repository moi ten la smart-study-copilot
echo 2. Copy duong link HTTPS cua repo vua tao
echo ===================================================================
set /p repo_url="Dan duong link GitHub cua ban vao day roi an Enter: "

if "%repo_url%"=="" (
    echo Ban chua nhap link! Vui long chay lai.
    pause
    exit /b
)

cd /d "%~dp0"
git remote remove origin >nul 2>&1
git remote add origin %repo_url%

echo.
echo [1/2] Dang day toan bo cac nhanh (main, dev, feat/...) len GitHub...
git push -u origin --all

echo.
echo [2/2] Dang day toan bo cac Tag phien ban (v0.1, v1.0, v2.0, v3.0) len GitHub...
git push --tags

echo.
echo ===================================================================
echo  THANH CONG! Toan bo ma nguon va lich su commit da co tren GitHub.
echo ===================================================================
pause
