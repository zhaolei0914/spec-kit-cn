# 命令模板变更日志

## [2.0.0] - 2026-03-30

### 新增

- **harness-auto.md**: 全自动需求交付引擎 (核心入口)，支持三级调度 (subagent/session-split/single)
- **harness-audit.md**: Harness 全面审计评分 (A-F)，五维度评分
- **harness-forensics.md**: 失败事后调查，根因分析和改进建议
- **harness-status.md**: 显示当前工作流状态和下一步操作建议
- **harness-pause.md**: 暂停工作，生成 handoff.json 交接文件
- **harness-resume.md**: 从 handoff.json 恢复暂停的工作，支持上下文隔离协议
- **harness-checkpoint.md**: 手动创建 Git 检查点快照
- **harness-restore.md**: 从 Git 检查点恢复制品

### 改造

- **所有命令**: 新增「步骤 0: Harness 初始化」和「步骤 N: Harness 收尾」
- **0-制定项目上下文**: 步骤 0 增加 Harness 全套文件初始化 (config.yml, state.md 等)
- **1-需求分析**: 步骤 N 增加决策记录到 audit-log.md
- **2-需求规范**: 步骤 N 增加 lint-specs.sh + post-spec checkpoint
- **3-开发设计**: 步骤 N 增加 consistency-check.sh + post-design checkpoint
- **4-实施步骤**: 步骤 N 增加 lint + post-tasks checkpoint
- **5-实施前检测**: 步骤 N 增加 Harness Audit 评分 + pre-implement checkpoint
- **6-编写代码**: 步骤 N 增加两阶段审查 + TDD 纪律检查 + 原子提交 + security scan + post-implement checkpoint
- **8-生成测试用例**: 步骤 N 增加 RED-GREEN-REFACTOR 验证
- **9-测试验证**: 步骤 N 增加 quality-metrics.md 更新
- **10-同步文档**: 步骤 0/N 标准 Harness 初始化/收尾
- **11-归档需求**: 步骤 N 增加 Instinct 提取 + Forensics 分析 + quality-metrics 更新
