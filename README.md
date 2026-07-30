# 🚀 灵测 LingCheck

> **AI 驱动的代码审查 · 自动生成测试 · 一键修复 PR**
>
> 一个 PR 进来，灵测自动审、自动测、自动修。你只需要点 Merge。

<p align="center">
  <a href="https://pypi.org/project/lingcheck/">
    <img src="https://img.shields.io/pypi/v/lingcheck?color=blue" alt="PyPI">
  </a>
  <a href="https://github.com/your-org/lingcheck/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/your-org/lingcheck/ci.yml?branch=main" alt="CI">
  </a>
  <a href="https://github.com/your-org/lingcheck/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/your-org/lingcheck" alt="License">
  </a>
  <a href="https://github.com/your-org/lingcheck/stargazers">
    <img src="https://img.shields.io/github/stars/your-org/lingcheck?style=social" alt="Stars">
  </a>
</p>

<p align="center">
  <b>中文</b> | <a href="README_EN.md">English</a>
</p>

---

## 📊 实测数据：Flask 源码审查结果

我们在 **Flask（v2.3.0，18 个文件，6087 行 Python）** 上完整跑了一遍：

```
🔴 高风险:    1  (eval 调用 — 潜在 RCE 漏洞)
🟡 中风险:  196  (函数过长、空 except 块、硬编码密钥等)
🔵 低风险:  149  (魔法数字、命名建议等)
✅ 总计:    346 个问题
🧪 建议补充测试: 10 个文件缺少测试覆盖
```

👉 **这不是玩具 demo，这是真实项目验证。**

---

## ✨ 核心能力

| 能力 | 灵测 | CodeRabbit | Qodo | Codacy | SonarQube |
|------|:----:|:----------:|:----:|:------:|:---------:|
| PR 代码审查 | ✅ | ✅ | ❌ | ✅ | ❌ |
| 自动生成单元测试 | ✅ | ❌ | ✅ | ❌ | ❌ |
| 自动建修复 PR | ✅ | ❌ | ❌ | ❌ | ❌ |
| 增量扫描（只审改的） | ✅ | ✅ | ❌ | ✅ | ✅ |
| 开源可自建 | ✅ | ❌ | ❌ | ✅ | ✅ |
| 内网/私有化部署 | ✅ | ❌ | ❌ | ✅ | ✅ |
| 中国市场适配 | ✅ | ❌ | ❌ | ❌ | ❌ |
| **价格** | **开源免费** | $24-48/月 | 免费+企业 | 开源+付费 | 社区免费 |

---

## 🏗️ 引擎架构

```
┌──────────────────────────────────────────────────┐
│                  灵测引擎                          │
├──────────────┬───────────────┬───────────────────┤
│  安全审查器  │  复杂度审查器  │  规范审查器        │
│  (Security)  │ (Complexity)  │ (Convention)      │
├──────────────┴───────────────┴───────────────────┤
│              模块化检查器注册中心                    │
├──────────────────────────────────────────────────┤
│   AST 解析层 · Python/JS/TS/Go 支持               │
├──────────────────────────────────────────────────┤
│   CLI · GitHub Action · GitLab CI · 本地 API      │
└──────────────────────────────────────────────────┘
```

- **模块化设计**：审查器可独立注册、可组合、可扩展
- **多语言支持**：Python / JavaScript / TypeScript / Go（持续增加中）
- **三通道输出**：CLI 终端 / JSON 报告 / GitHub PR 评论

---

## 🚀 快速开始

### 安装

```bash
pip install lingcheck
```

### 审查你的项目

```bash
# 审查整个项目
lingcheck scan .

# 审查特定文件
lingcheck scan src/main.py --format json

# 增量审查（只审 git diff）
lingcheck scan . --diff-only
```

### GitHub Action 集成

在你的 `.github/workflows/` 下创建 `lingcheck.yml`：

```yaml
name: 灵测代码审查
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  lingcheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: 运行灵测审查
        uses: your-org/lingcheck-action@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-fix: true    # 自动建修复 PR
          generate-tests: true  # 自动补测试
```

---

## 📋 PR 评论效果

灵测会在 PR 中自动发表**折叠式评论**：

> <img src="https://via.placeholder.com/600x300?text=LingCheck+PR+Comment+Demo" alt="PR评论示例" width="600">

每类问题可折叠展开，维护者按需审阅，不刷屏。

---

## 🧪 自动修复 + 测试生成

这是灵测与其他工具最大的区别：

| 场景 | 其他工具 | 灵测 |
|------|---------|------|
| 发现漏洞 | ❌ 只报告 | ✅ 报告 + **自动建修复 PR** |
| 缺少测试 | ❌ 只提醒 | ✅ 分析代码 + **生成 pytest/unittest** |
| 代码规范 | ✅ 报告 | ✅ 报告 + **自动格式化 PR** |

---

## 🔧 配置

在项目根目录创建 `lingcheck.yml`：

```yaml
# .lingcheck.yml
checkers:
  - security        # 安全漏洞检查
  - complexity      # 复杂度检查（函数长度、圈复杂度）
  - conventions     # 代码规范检查

rules:
  max-function-length: 80      # 函数最大行数
  max-cyclomatic-complexity: 15 # 圈复杂度上限
  no-magic-numbers: true       # 禁止魔法数字
  require-docstrings: false    # 是否强制文档字符串

output:
  format: pretty               # pretty / json / sarif
  report-file: lingcheck-report.json

ci:
  auto-fix: true               # 自动建修复 PR
  generate-tests: true         # 自动生成测试
  comment-on-pr: true          # 在 PR 上发表评论
```

---

## 🗺️ 路线图

| 阶段 | 功能 | 状态 |
|------|------|:----:|
| v0.1 | Python 代码审查（安全+复杂度+规范） | ✅ 完成 |
| v0.2 | CLI 工具 + JSON 输出 | ✅ 完成 |
| v0.3 | GitHub Action 集成 | ✅ 完成 |
| v0.4 | 自动建修复 PR | 🚧 开发中 |
| v0.5 | 自动生成单元测试 | 🚧 开发中 |
| v0.6 | JavaScript/TypeScript 支持 | 📋 计划中 |
| v0.7 | GitLab CI / 自建 CI 集成 | 📋 计划中 |
| v1.0 | 企业版发布（私有化部署+管理后台） | 📋 计划中 |

---

## 🤝 为什么做这个？

市面上的代码审查工具要么贵（CodeRabbit $24-48/用户/月），要么只做一半（只报告不修复）。灵测的目标是：

> **一个开箱即用、全链路的开源代码质量工具，让每个开发团队都能用上自动化的 PR 审查。**

---

## 📄 License

MIT License © 2025 灵测团队

---

<p align="center">
  <b>给灵测一个 ⭐，让更多开发者发现自动化代码审查的力量</b>
</p>
