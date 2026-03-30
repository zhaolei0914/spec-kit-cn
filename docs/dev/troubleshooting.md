# B. 常见问题与排障

## 1. `specify init` 下载失败 / rate limit

现象：

- GitHub API 返回 403/429
- CLI 输出 rate limit 信息

处理：

- 使用 `--github-token` 或设置 `GH_TOKEN/GITHUB_TOKEN`

## 2. 企业网络 TLS/代理问题

现象：

- TLS 校验失败、连接超时

处理：

- 本地实验可用 `--skip-tls`（不建议长期/生产使用）
- 优先在网络侧解决代理/证书链

## 3. `--here` 合并覆盖了文件

现象：

- 当前目录非空，合并覆盖了部分文件

处理：

- 不要在重要目录直接 `--here`，先用临时目录验证
- 依赖 `.vscode/settings.json` 的 deep merge，但其它文件可能直接覆盖

## 4. scripts 在 Linux/macOS 不可执行

现象：

- `.specify/scripts/*.sh` 没有执行权限

处理：

- `specify init` 会尝试自动 chmod（只对 shebang 的 .sh）
- 仍失败时：确认文件系统/挂载权限

## 5. 找不到当前 feature / plan.md

现象：

- `check-prerequisites` 报：`plan.md not found`

处理：

- 确认在 `NNN-xxx` 分支
- 或设置 `SPECIFY_FEATURE=NNN-xxx`
- 确认 `specs/NNN-xxx/plan.md` 已生成（先跑 `/speckit.plan`）

## 6. agent 上下文没有更新

现象：

- `.windsurf/rules/...` 或 `CLAUDE.md` 未变化

处理：

- `plan.md` 是否包含脚本可解析字段（例如 `**Language/Version**:`）
- 确认 `update-agent-context` 脚本被实际执行（plan 命令会触发）

## 7. bash 与 PowerShell 行为不一致

现象：

- Windows 跑 ps1 与 Linux 跑 sh 产物不同

处理：

- 维护者需要同步修改两套脚本
- 使用 `--script sh|ps` 强制对齐验证
