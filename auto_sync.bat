@echo off
REM ============================================
REM GitHub 自动同步脚本
REM 路径: E:\github_repos\auto_sync.bat
REM ============================================
setlocal enabledelayedexpansion

set "REPO_DIR=E:\github_repos"
set "LOG_FILE=E:\github_repos\sync.log"
set "GIT_DIR=E:\github_repos\.git"

echo [%date% %time%] ====== 开始同步 ====== >> "%LOG_FILE%"

REM 检查是否是git仓库
if not exist "%GIT_DIR%" (
    echo [%date% %time%] 不是Git仓库，初始化中... >> "%LOG_FILE%"
    cd /d "%REPO_DIR%"
    git init
    git config user.name "DaDaDelddd309"
    git config user.email "309195895@qq.com"
    echo [%date% %time%] Git仓库初始化完成 >> "%LOG_FILE%"
)

cd /d "%REPO_DIR%"

REM 添加所有更改
git add -A >> "%LOG_FILE%" 2>&1

REM 检查是否有更改
for /f %%i in ('git status --porcelain') do set "HAS_CHANGES=1"

if defined HAS_CHANGES (
    echo [%date% %time%] 发现更改，提交中... >> "%LOG_FILE%"
    git commit -m "Auto-sync %date% %time%" >> "%LOG_FILE%" 2>&1

    REM 尝试推送到远程
    git push origin main >> "%LOG_FILE%" 2>&1
    if errorlevel 1 (
        echo [%date% %time%] push失败，可能没有远程仓库 >> "%LOG_FILE%"
    ) else (
        echo [%date% %time%] 推送成功 >> "%LOG_FILE%"
    )
) else (
    echo [%date% %time%] 无更改 >> "%LOG_FILE%"
)

echo [%date% %time%] ====== 同步完成 ====== >> "%LOG_FILE%"
