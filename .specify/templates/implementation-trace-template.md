# 实现追溯清单模板

**需求 ID**: [REQ_ID]
**生成时间**: [TIMESTAMP]
**覆盖率**: X/Y (XX%)

---

## 执行摘要

| 指标 | 值 |
|------|------|
| 总需求数 | X |
| 已实现 | X |
| 部分实现 | X |
| 未实现 | X |
| 覆盖率 | XX% |

---

## 需求追溯清单

### FR-001: [需求描述]

- **设计位置**: design.md L[行号]
- **规范位置**: spec.md FR-001
- **代码位置**: `[模块]/[文件].py:[方法名]()`
- **测试位置**: `test/test_[模块].py:test_[方法名]`
- **状态**: ✅ 已实现 | ⚠️ 部分实现 | ❌ 未实现
- **备注**: [如有未实现或部分实现，说明原因]

### FR-002: [需求描述]

- **设计位置**: design.md L[行号]
- **规范位置**: spec.md FR-002
- **代码位置**: `[模块]/[文件].py:[方法名]()`
- **测试位置**: `test/test_[模块].py:test_[方法名]`
- **状态**: ✅ 已实现 | ⚠️ 部分实现 | ❌ 未实现
- **备注**: [如有未实现或部分实现，说明原因]

---

## 业务校验规则追溯

> 本节追溯设计文档中要求的业务校验规则是否在代码中实现。

| 校验规则 | 设计位置 | 代码位置 | 状态 |
|----------|----------|----------|------|
| V7 环境 DB 授权校验 | design.md L120 | `service/import_service.py:_check_db_enabled()` | ✅ |
| V7 用户角色校验 | design.md L150 | - | ❌ |
| 目标用户归属校验 | design.md L180 | - | ❌ |
| 客户端升级前置校验 | design.md L200 | - | ❌ |

---

## 错误码追溯

> 本节追溯设计文档中定义的错误码是否在代码中实现。

| 错误码 | 设计位置 | 代码位置 | 状态 |
|--------|----------|----------|------|
| V7V8.Import.DbAuthRequired | design.md L300 | `exception/error_codes.py:L50` | ✅ |
| V7V8.Import.UserNotFound | design.md L310 | `exception/error_codes.py:L60` | ✅ |
| V7V8.Migrate.ClientUpgradeRequired | design.md L320 | - | ❌ |

---

## API 接口追溯

> 本节追溯设计文档中定义的 API 接口是否在代码中实现。

| 接口 | 方法 | 设计位置 | 代码位置 | 状态 |
|------|------|----------|----------|------|
| /api/v1/v7-environments | POST | design.md L400 | `web/v7_env_views.py:create` | ✅ |
| /api/v1/v7-environments | GET | design.md L420 | `web/v7_env_views.py:list` | ✅ |
| /api/v1/import-jobs | POST | design.md L450 | `web/import_views.py:create` | ✅ |
| /api/v1/import-jobs/{id}/export | GET | design.md L480 | `web/import_views.py:export` | ⚠️ |

---

## 未实现项清单

| 编号 | 类型 | 描述 | 原因 | 优先级 | 建议 |
|------|------|------|------|--------|------|
| G1 | 业务校验 | V7 用户角色校验 | 设计文档未明确接口 | P0 | 补充实现 |
| G2 | 业务校验 | 目标用户归属校验 | 依赖用户服务接口 | P0 | 待接口就绪后补充 |
| G3 | 错误码 | ClientUpgradeRequired | 遗漏 | P1 | 补充错误码定义 |

---

## 变更历史

| 日期 | 版本 | 变更内容 | 操作人 |
|------|------|----------|--------|
| [DATE] | 1.0 | 初始生成 | speckit.implement |
| [DATE] | 1.1 | 补充 FR-003 实现 | [USER] |

---

## 使用说明

### 状态标记

- ✅ **已实现**: 功能完整实现，有对应测试
- ⚠️ **部分实现**: 功能部分实现，缺少部分校验或边界处理
- ❌ **未实现**: 功能未实现或仅有占位代码

### 更新规则

1. **speckit.implement 完成后**: 自动生成此清单
2. **代码修改后**: 手动更新对应条目的代码位置和状态
3. **speckit.speccheck 执行时**: 自动验证清单与代码的一致性

### 代码标注规范

在代码中使用以下格式标注设计追溯：

```python
def create_user_import_job(self, ...):
    """
    创建用户导入作业

    设计追溯:
    - FR-020: 系统必须支持从 V7 导入用户
    - FR-021: 系统必须支持用户重名处理规则
    - FR-026: 系统必须限制仅管理员可执行导入
    """
    # 实现代码
```
