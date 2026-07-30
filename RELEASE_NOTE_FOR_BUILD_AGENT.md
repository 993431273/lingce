# LingCheck v0.1.0 Release

## 打包说明
- 此版本为 CLI 工具 + GitHub Action，不需要打包为桌面应用
- Linux/Mac/Windows 用户可通过 pip install -e . 安装
- 已推送到 GitHub: https://github.com/993431273/lingce

## 发布内容
- 核心引擎：代码审查 + 测试生成
- CLI 工具：lingcheck scan/check/test 三个子命令
- GitHub Action：自动 PR 审查
- 问题模板：Bug Report + Feature Request

## 验证
- 实测通过：Flask 源码 18 个文件扫描出 346 个问题
- 引擎 292 行，完整可运行
