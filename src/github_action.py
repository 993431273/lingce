#!/usr/bin/env python3
"""
灵测 GitHub Action 集成模块
将代码审查结果自动评论到 PR 中
"""

import os
import json
import sys
from typing import Dict, List, Optional

# GitHub CLI 路径
GH_CLI = "gh"


def format_pr_comment(results: Dict) -> str:
    """将审查结果格式化为 PR 评论（Markdown）"""
    s = results.get("summary", {})
    
    # 生成徽章
    critical = s.get("critical", 0)
    warning = s.get("warning", 0)
    info = s.get("info", 0)
    
    badge_color = "brightgreen" if critical == 0 else "red"
    
    comment = f"""## 🤖 灵测 (LingCheck) 代码审查报告

[![灵测](https://img.shields.io/badge/灵测-审查完成-{badge_color})](https://github.com)

### 📊 总览
| 指标 | 数值 |
|------|------|
| 🔴 高风险问题 | {critical} |
| 🟡 中风险问题 | {warning} |
| 🔵 低风险/建议 | {info} |
| 🧪 测试生成建议 | {len(results.get('tests_generated', []))} 条 |

"""
    
    # 按文件分组显示问题
    issues = results.get("issues", [])
    if issues:
        comment += "### 📋 发现的问题\n\n"
        
        # 按文件分组
        by_file: Dict[str, List] = {}
        for issue in issues:
            file = issue.get("file", "unknown")
            if file not in by_file:
                by_file[file] = []
            by_file[file].append(issue)
        
        for file, file_issues in sorted(by_file.items()):
            comment += f"<details>\n<summary><b>{file}</b> ({len(file_issues)} 个问题)</summary>\n\n"
            for iss in file_issues[:20]:  # 每个文件最多显示20条
                icon = {"高危": "🔴", "中危": "🟡", "低危": "🔵", 
                       "warning": "🟡", "info": "🔵", "critical": "🔴"}
                line = iss.get("line", "?")
                sev = iss.get("severity", "info")
                msg = iss.get("message", "")
                comment += f"- {icon.get(sev, '⚪')} **L{line}**: {msg}\n"
            
            if len(file_issues) > 20:
                comment += f"\n*...还有 {len(file_issues) - 20} 个问题未显示*\n"
            
            comment += "</details>\n\n"
    
    # 测试建议
    tests = results.get("tests_generated", [])
    if tests:
        comment += "### 🧪 自动测试生成建议\n\n"
        for t in tests[:10]:
            comment += f"- **{t['file']}**: {t['message']}\n"
        comment += "\n"
    
    # 统计信息
    stats = results.get("stats", {})
    if stats:
        comment += "### 📈 项目统计\n\n"
        comment += f"- 分析文件数: {stats.get('total_files', 0)}\n"
        langs = stats.get("languages", {})
        for lang, count in langs.items():
            comment += f"- {lang}: {count} 个文件\n"
    
    comment += "\n---\n"
    comment += "> 🤖 本报告由 [灵测 LingCheck](https://github.com) 自动生成 | 如有问题请联系我们\n"
    
    return comment


def post_to_pr(comment: str, repo: str, pr_number: int):
    """通过 GitHub CLI 将评论发布到 PR"""
    import subprocess
    
    cmd = [
        GH_CLI, "pr", "comment", str(pr_number),
        "--repo", repo,
        "--body", comment
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ 评论已发布到 {repo}#{pr_number}")
        else:
            print(f"⚠️ 发布失败: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 发布异常: {e}")
        return False


def simulate_pr_analysis(results_path: str, output_path: str = None):
    """从结果文件生成 PR 评论预览"""
    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)
    
    comment = format_pr_comment(results)
    
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(comment)
        print(f"✅ 评论预览已保存到 {output_path}")
    else:
        print(comment)
    
    return comment


if __name__ == "__main__":
    # 测试模式：从 JSON 结果生成 PR 评论预览
    if len(sys.argv) > 1:
        simulate_pr_analysis(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    else:
        print("用法: python github_action.py <results.json> [output.md]")
