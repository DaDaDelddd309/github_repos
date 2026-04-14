#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""GitHub 自动同步脚本 - 带定时功能"""
import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

REPO_DIR = Path("E:/github_repos")
LOG_FILE = REPO_DIR / "sync.log"
CONFIG_FILE = REPO_DIR / "sync_config.json"

def log(msg):
    """写日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def is_git_repo():
    """检查是否是git仓库"""
    return (REPO_DIR / ".git").is_dir()

def init_repo():
    """初始化git仓库"""
    try:
        subprocess.run(["git", "init"], cwd=REPO_DIR, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "DaDaDelddd309"], cwd=REPO_DIR, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "309195895@qq.com"], cwd=REPO_DIR, capture_output=True, check=True)
        log("Git仓库初始化完成")
        return True
    except Exception as e:
        log(f"初始化失败: {e}")
        return False

def get_changes():
    """获取更改文件列表"""
    try:
        result = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_DIR, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return ""

def commit_and_push():
    """提交并推送"""
    try:
        # 添加所有文件
        subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, capture_output=True)

        changes = get_changes()
        if not changes:
            log("无更改")
            return True

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"Auto-sync {timestamp}"

        # 提交
        subprocess.run(["git", "commit", "-m", message], cwd=REPO_DIR, capture_output=True, check=True)
        log(f"已提交: {message}")

        # 推送
        result = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)
        if result.returncode == 0:
            log("推送成功")
            return True
        else:
            log(f"推送失败: {result.stderr}")
            return False

    except Exception as e:
        log(f"同步失败: {e}")
        return False

def sync_once():
    """执行一次同步"""
    log("=" * 40)
    log("开始同步检查")

    if not is_git_repo():
        log("不是Git仓库，初始化...")
        if not init_repo():
            return False
        log("已初始化，但还没有远程仓库，需要先添加远程仓库")

    return commit_and_push()

def main():
    """主函数"""
    interval_minutes = 30  # 默认30分钟同步一次

    # 检查配置文件
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                interval_minutes = config.get('interval_minutes', 30)
        except:
            pass

    log(f"GitHub自动同步已启动 (间隔: {interval_minutes}分钟)")
    log(f"仓库路径: {REPO_DIR}")
    log(f"日志文件: {LOG_FILE}")

    # 首次同步
    sync_once()

    # 定时循环
    while True:
        time.sleep(interval_minutes * 60)
        sync_once()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("同步已停止")
        sys.exit(0)
