#!/usr/bin/env python3
"""
Git多仓库管理器
支持配置化管理多个仓库

用法:
  python multi_repo_manager.py status
  python multi_repo_manager.py sync_all
  python multi_repo_manager.py add_repo 项目名 路径
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')

def load_config() -> dict:
    """加载配置文件"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'repositories': {},
        'github': {},
        'sync': {'auto_add': True, 'auto_commit': True, 'commit_prefix': '语音更新'},
        'excludes': []
    }

def save_config(config: dict):
    """保存配置文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def run_git(args: List[str], cwd: str) -> tuple:
    """执行git命令"""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=60,
            shell=True
        )
        return result.stdout or '', result.stderr or '', result.returncode
    except Exception as e:
        return '', str(e), -1

def get_repo_status(name: str, repo_config: dict) -> dict:
    """获取单个仓库状态"""
    path = repo_config['path']
    remote = repo_config.get('remote', 'origin')
    branch = repo_config.get('branch', 'main')

    status = {
        'name': name,
        'path': path,
        'exists': os.path.exists(path),
        'has_remote': False,
        'ahead': 0,
        'behind': 0,
        'changes': [],
        'branch': None,
        'remote_url': None
    }

    if not status['exists']:
        return status

    # 检查git仓库
    git_dir = os.path.join(path, '.git')
    if not os.path.exists(git_dir):
        return status

    status['is_git'] = True

    # 获取当前分支
    stdout, _, _ = run_git(['branch', '--show-current'], path)
    status['branch'] = stdout.strip() or '(detached)'

    # 获取远程URL
    stdout, _, _ = run_git(['remote', 'get-url', remote], path)
    if stdout:
        status['remote_url'] = stdout.strip()
        status['has_remote'] = True

    # 获取状态
    stdout, _, _ = run_git(['status', '-s'], path)
    if stdout:
        status['changes'] = [line.strip() for line in stdout.strip().split('\n') if line.strip()]

    # 获取领先/落后
    if status['has_remote']:
        stdout, _, _ = run_git(['rev-list', '--left-right', '--count', f'{branch}...{remote}/{branch}'], path)
        if stdout:
            parts = stdout.strip().split()
            if len(parts) == 2:
                status['ahead'], status['behind'] = int(parts[0]), int(parts[1])

    return status

def cmd_status(all_repos: bool = False):
    """查看仓库状态"""
    config = load_config()
    repos = config.get('repositories', {})

    if not all_repos and 'default' in repos:
        repos = {'default': repos['default']}

    print("=" * 60)
    print("Git仓库状态")
    print("=" * 60)

    for name, repo_config in repos.items():
        status = get_repo_status(name, repo_config)

        print(f"\n[{name}] {status['path']}")
        print("-" * 40)

        if not status['exists']:
            print("  [ERROR] 仓库路径不存在")
            continue

        print(f"  分支: {status['branch']}")

        if status['has_remote']:
            print(f"  远程: {status['remote_url']}")
            if status['ahead'] > 0:
                print(f"  ↑ 领先{status['ahead']}个提交")
            if status['behind'] > 0:
                print(f"  ↓ 落后{status['behind']}个提交")
        else:
            print("  [WARN] 无远程仓库配置")

        if status['changes']:
            print(f"  变动: {len(status['changes'])}个文件")
            for change in status['changes'][:5]:
                print(f"    {change}")
            if len(status['changes']) > 5:
                print(f"    ... 还有{len(status['changes']) - 5}个")
        else:
            print("  状态: 工作区干净")

def cmd_sync(repo_name: str = 'default', push: bool = True, pull: bool = True):
    """同步仓库"""
    config = load_config()
    repos = config.get('repositories', {})

    if repo_name not in repos:
        print(f"[ERROR] 未知仓库: {repo_name}")
        print(f"可用仓库: {', '.join(repos.keys())}")
        return

    repo_config = repos[repo_name]
    path = repo_config['path']
    remote = repo_config.get('remote', 'origin')
    branch = repo_config.get('branch', 'main')

    print(f"同步仓库: {repo_name} ({path})")

    if pull:
        print("  [1/3] 拉取远程...")
        run_git(['fetch', '--all'], path)
        stdout, stderr, code = run_git(['pull', remote, branch], path)
        if code == 0:
            print("    拉取成功")
        else:
            print(f"    拉取: {stdout or stderr}")

    sync_config = config.get('sync', {})
    if sync_config.get('auto_add') and sync_config.get('auto_commit'):
        print("  [2/3] 暂存并提交...")
        run_git(['add', '.'], path)
        msg = f"{sync_config.get('commit_prefix', '更新')} {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        stdout, stderr, code = run_git(['commit', '-m', msg], path)
        if 'nothing to commit' in (stdout + stderr).lower():
            print("    无新变动")
        elif code == 0:
            print(f"    提交成功: {msg}")
        else:
            print(f"    提交: {stdout or stderr}")

    if push:
        print("  [3/3] 推送到远程...")
        stdout, stderr, code = run_git(['push', '-u', remote, branch], path)
        if code == 0:
            print("    推送成功!")
        else:
            print(f"    推送: {stdout or stderr}")

def cmd_add_repo(name: str, path: str, remote: str = 'origin', branch: str = 'main'):
    """添加新仓库"""
    config = load_config()

    if not os.path.exists(path):
        print(f"[ERROR] 路径不存在: {path}")
        return

    if name in config['repositories']:
        print(f"[WARN] 仓库'{name}'已存在，将被覆盖")

    config['repositories'][name] = {
        'path': path,
        'remote': remote,
        'branch': branch
    }

    save_config(config)
    print(f"[OK] 仓库'{name}'已添加: {path}")

def cmd_list():
    """列出所有仓库"""
    config = load_config()
    repos = config.get('repositories', {})

    print("=" * 40)
    print("已配置仓库")
    print("=" * 40)

    if not repos:
        print("暂无仓库配置")
        return

    for name, repo_config in repos.items():
        status = get_repo_status(name, repo_config)
        sync_status = "✓" if not status['changes'] else "✗"
        print(f"  [{sync_status}] {name}")
        print(f"      路径: {repo_config['path']}")
        print(f"      远程: {repo_config.get('remote', 'origin')}/{repo_config.get('branch', 'main')}")

def main():
    # Windows终端编码
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

    if len(sys.argv) < 2:
        print("Git多仓库管理器")
        print("=" * 40)
        print("用法:")
        print("  status          - 查看默认仓库状态")
        print("  status -a       - 查看所有仓库状态")
        print("  sync [仓库名]    - 同步仓库(默认default)")
        print("  list            - 列出所有仓库")
        print("  add 名称 路径   - 添加新仓库")
        print("=" * 40)
        return

    cmd = sys.argv[1].lower()

    if cmd == 'status':
        all_repos = '-a' in sys.argv or '--all' in sys.argv
        cmd_status(all_repos)
    elif cmd == 'sync':
        repo_name = sys.argv[2] if len(sys.argv) > 2 else 'default'
        cmd_sync(repo_name)
    elif cmd == 'list':
        cmd_list()
    elif cmd == 'add':
        if len(sys.argv) < 4:
            print("用法: add 名称 路径 [远程] [分支]")
        else:
            name, path = sys.argv[2], sys.argv[3]
            remote = sys.argv[4] if len(sys.argv) > 4 else 'origin'
            branch = sys.argv[5] if len(sys.argv) > 5 else 'main'
            cmd_add_repo(name, path, remote, branch)
    else:
        print(f"未知命令: {cmd}")

if __name__ == '__main__':
    main()
