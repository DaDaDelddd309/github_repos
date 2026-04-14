@echo off
REM GitHub 一键配置完成脚本
REM 在完成浏览器GitHub登录后运行此脚本

echo ========================================
echo GitHub 本地仓库配置
echo ========================================

REM 检查认证状态
echo.
echo [1/4] 检查GitHub登录状态...
gh auth status
if errorlevel 1 (
    echo GitHub未登录！请先在浏览器完成登录: https://github.com/login/device
    echo 登录完成后运行此脚本
    pause
    exit /b 1
)

echo GitHub已登录！

REM 创建仓库
echo.
echo [2/4] 创建GitHub仓库...
cd /d E:\github_repos
git add -A
git commit -m "Initial commit" 2>nul
gh repo create github_repos --private --source=. --push

echo.
echo [3/4] 设置定时同步任务...
schtasks /delete /TN "GitHubAutoSync" /F 2>nul
schtasks /create /TN "GitHubAutoSync" /TR "python E:\github_repos\auto_sync.py" /SC MINUTE /MO 30 /F

echo.
echo [4/4] 启动同步服务...
taskkill /F /IM python.exe /T 2>nul
cd E:\github_repos
start /B python auto_sync.py

echo.
echo ========================================
echo 配置完成！
echo 仓库地址: https://github.com/DaDaDelddd309/github_repos
echo 同步间隔: 30分钟
echo ========================================
pause
