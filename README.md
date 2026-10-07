# github_repos

GitHub 账号与多仓库管理的自动化脚本归档。

## 文件说明

| 文件 | 作用 |
|------|------|
| `sync_config.json` | 同步目标仓库与路径的配置文件 |
| `multi_repo_manager.py` | 多仓库批量管理（批量 commit / push /状态检查） |
| `auto_sync.py` | 定时自动同步脚本 |
| `auto_sync.bat` | Windows 侧的计划任务入口 |
| `github_setup_complete.bat` | 一次性环境初始化 |
| `sync.log` / `sync_service.log` | 运行日志 |

## 用法

编辑 `sync_config.json` 声明要管理的仓库，然后：

```bash
python3 multi_repo_manager.py status   # 查看各仓库状态
python3 auto_sync.py                # 执行一次同步
```

Windows 用户用 `auto_sync.bat` 挂计划任务。

## 注意

- 本仓库含个人路径与账号信息，仅供个人使用
- 脚本日志未做脱敏，公开前请先清理