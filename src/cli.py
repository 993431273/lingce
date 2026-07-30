#!/usr/bin/env python3
"""
灵测 (LingCheck) CLI — AI Code Review + Test Generation Tool
核心引擎入口
"""

import os
import sys
import json
import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

VERSION = "0.1.0"

class LingCheckEngine:
    """灵测核心引擎：代码审查 + 测试生成"""
    
    def __init__(self, repo_path: str, verbose: bool = False):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        self.results = {
            "summary": {"total_issues": 0, "critical": 0, "warning": 0, "info": 0},
            "issues": [],
            "tests_generated": [],
            "stats": {}
        }
    
    def log(self, msg: str):
        if self.verbose:
            print(f"[灵测] {msg}")
    
    def analyze_structure(self) -> Dict:
        """分析项目结构"""
        self.log("分析项目结构中...")
        files = list(self.repo_path.rglob("*.py")) + list(self.repo_path.rglob("*.js")) + \
                list(self.repo_path.rglob("*.ts")) + list(self.repo_path.rglob("*.java"))
        
        return {
            "total_files": len(files),
            "languages": self._detect_languages(files),
            "file_list": [str(f.relative_to(self.repo_path)) for f in files[:50]]
        }
    
    def _detect_languages(self, files: List[Path]) -> Dict[str, int]:
        langs = {}
        for f in files:
            ext = f.suffix
            lang_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".java": "Java"}
            lang = lang_map.get(ext, "Other")
            langs[lang] = langs.get(lang, 0) + 1
        return langs
    
    def scan_for_security_issues(self) -> List[Dict]:
        """扫描安全漏洞"""
        self.log("扫描安全漏洞中...")
        issues = []
        
        patterns = {
            "hardcoded_password": (r"(password|pwd|secret|api_key|apikey)\s*=\s*['\"][^'\"]+['\"]", "高危"),
            "sql_injection": (r"execute\(.*f['\"]", "高危"),
            "eval_usage": (r"\beval\s*\(", "高危"),
            "insecure_deserialize": (r"pickle\.loads?\s*\(", "中危"),
            "debug_print": (r"print\(.*(password|token|secret)", "低危"),
        }
        
        for file_path in self.repo_path.rglob("*.py"):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                rel_path = str(file_path.relative_to(self.repo_path))
                
                for pattern_name, (pattern, severity) in patterns.items():
                    import re
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_no = content[:match.start()].count("\n") + 1
                        issues.append({
                            "type": "security",
                            "severity": severity,
                            "file": rel_path,
                            "line": line_no,
                            "message": f"发现{severity}安全问题: {pattern_name}",
                            "snippet": content[max(0, match.start()-20):match.end()+20].strip()
                        })
            except Exception as e:
                self.log(f"  跳过 {file_path}: {e}")
        
        return issues
    
    def scan_for_code_smells(self) -> List[Dict]:
        """扫描代码坏味道"""
        self.log("扫描代码坏味道中...")
        issues = []
        
        for file_path in self.repo_path.rglob("*.py"):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                lines = content.split("\n")
                rel_path = str(file_path.relative_to(self.repo_path))
                
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    
                    # 函数过长（超过50行）
                    if stripped.startswith("def ") and i < len(lines):
                        end_line = self._find_function_end(lines, i)
                        func_length = end_line - i
                        if func_length > 50:
                            issues.append({
                                "type": "code_smell",
                                "severity": "warning",
                                "file": rel_path,
                                "line": i,
                                "message": f"函数过长 ({func_length} 行)，建议拆分为小函数"
                            })
                    
                    # 魔法数字
                    import re
                    magic_numbers = re.findall(r'(?<!= )\b(?:[2-9]|[1-9]\d{2,})(?![.\w])', line)
                    if magic_numbers and not line.strip().startswith("#"):
                        issues.append({
                            "type": "code_smell",
                            "severity": "info",
                            "file": rel_path,
                            "line": i,
                            "message": f"发现魔法数字: {', '.join(magic_numbers[:3])}，建议定义为常量"
                        })
                    
                    # 空的 except
                    if "except:" in stripped:
                        issues.append({
                            "type": "code_smell",
                            "severity": "warning",
                            "file": rel_path,
                            "line": i,
                            "message": "裸 except 捕获所有异常，建议指定具体异常类型"
                        })
                    
                    # TODO/FIXME
                    if "TODO" in stripped.upper() or "FIXME" in stripped.upper():
                        issues.append({
                            "type": "code_smell",
                            "severity": "info",
                            "file": rel_path,
                            "line": i,
                            "message": f"存在待办事项: {stripped.strip()}"
                        })
                        
            except Exception:
                continue
        
        return issues
    
    def _find_function_end(self, lines: List[str], start: int) -> int:
        indent = len(lines[start]) - len(lines[start].lstrip())
        for i in range(start + 1, len(lines)):
            if lines[i].strip() and not lines[i].startswith(" ") and not lines[i].startswith("\t"):
                if len(lines[i]) - len(lines[i].lstrip()) <= indent:
                    return i
        return len(lines)
    
    def generate_test_suggestions(self) -> List[Dict]:
        """分析代码并生成测试建议"""
        self.log("分析测试覆盖情况...")
        suggestions = []
        
        for file_path in self.repo_path.rglob("*.py"):
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                rel_path = str(file_path.relative_to(self.repo_path))
                
                # 查找函数定义
                import re
                functions = re.findall(r'def (\w+)\s*\(', content)
                
                if functions:
                    # 检查是否存在对应测试文件
                    test_path = self.repo_path / "tests" / f"test_{file_path.name}"
                    if not test_path.exists():
                        test_path = file_path.parent / f"test_{file_path.name}"
                    
                    if not test_path.exists():
                        suggestions.append({
                            "file": rel_path,
                            "functions": functions[:10],
                            "missing_test_file": True,
                            "message": f"缺少测试文件，发现 {len(functions)} 个待测函数"
                        })
                    else:
                        test_content = test_path.read_text(encoding="utf-8", errors="ignore")
                        untested = [f for f in functions if f"def test_{f}" not in test_content 
                                    and f not in test_content]
                        if untested:
                            suggestions.append({
                                "file": rel_path,
                                "functions": untested[:10],
                                "missing_test_file": False,
                                "message": f"以下函数缺少测试: {', '.join(untested[:5])}"
                            })
            except Exception:
                continue
        
        return suggestions
    
    def run(self) -> Dict:
        """执行完整扫描"""
        print("=" * 50)
        print("  灵测 LingCheck v%s" % VERSION)
        print("  AI 自主代码审查引擎")
        print("=" * 50)
        
        # 1. 分析结构
        self.results["stats"] = self.analyze_structure()
        print("\n📁 项目概况:")
        print(f"  - 文件数: {self.results['stats']['total_files']}")
        print(f"  - 语言: {self.results['stats']['languages']}")
        
        # 2. 安全扫描
        sec_issues = self.scan_for_security_issues()
        self.results["issues"].extend(sec_issues)
        
        # 3. 代码坏味道
        smell_issues = self.scan_for_code_smells()
        self.results["issues"].extend(smell_issues)
        
        # 4. 统计数据
        severity_map = {"高危": "critical", "中危": "warning", "低危": "info", "warning": "warning", "info": "info"}
        for issue in self.results["issues"]:
            sev = severity_map.get(issue["severity"], "info")
            self.results["summary"][sev] += 1
        self.results["summary"]["total_issues"] = len(self.results["issues"])
        
        # 5. 测试建议
        self.results["tests_generated"] = self.generate_test_suggestions()
        
        # 打印报告
        self._print_report()
        
        return self.results
    
    def _print_report(self):
        s = self.results["summary"]
        print(f"\n📊 审查报告")
        print(f"  - 总问题数: {s['total_issues']}")
        print(f"  - 🔴 高风险: {s['critical']}")
        print(f"  - 🟡 中风险: {s['warning']}")
        print(f"  - 🔵 低风险: {s['info']}")
        print(f"  - 测试建议: {len(self.results['tests_generated'])} 条")
        
        if self.results["issues"]:
            print(f"\n📋 问题详情 (前10条):")
            for issue in self.results["issues"][:10]:
                icon = {"高危": "🔴", "中危": "🟡", "低危": "🔵", "warning": "🟡", "info": "🔵"}
                print(f"  {icon.get(issue['severity'], '⚪')} [{issue['severity']}] {issue['file']}:{issue['line']}")
                print(f"     {issue['message']}")
        
        if self.results["tests_generated"]:
            print(f"\n🧪 测试生成建议 (前5条):")
            for t in self.results["tests_generated"][:5]:
                print(f"  📝 {t['file']}: {t['message']}")


def main():
    parser = argparse.ArgumentParser(description="灵测 LingCheck - AI 代码审查 & 测试生成工具")
    parser.add_argument("path", nargs="?", default=".", help="目标项目路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式报告")
    parser.add_argument("--version", action="store_true", help="显示版本号")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"灵测 LingCheck v{VERSION}")
        return
    
    if not os.path.exists(args.path):
        print(f"❌ 路径不存在: {args.path}")
        sys.exit(1)
    
    engine = LingCheckEngine(args.path, args.verbose)
    results = engine.run()
    
    if args.json:
        print("\n\n--- JSON 输出 ---")
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
