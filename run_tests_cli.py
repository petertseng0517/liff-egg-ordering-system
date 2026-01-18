#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試運行工具 - Python 版本
使用方式: python run_tests_cli.py [command]
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


class Colors:
    """ANSI 顏色代碼"""
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color


class TestRunner:
    """測試運行工具"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.tests_dir = self.project_root / 'tests'
        
    def print_info(self, message):
        """打印信息訊息"""
        print(f"{Colors.BLUE}ℹ {message}{Colors.NC}")
    
    def print_success(self, message):
        """打印成功訊息"""
        print(f"{Colors.GREEN}✓ {message}{Colors.NC}")
    
    def print_warn(self, message):
        """打印警告訊息"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.NC}")
    
    def print_error(self, message):
        """打印錯誤訊息"""
        print(f"{Colors.RED}✗ {message}{Colors.NC}")
    
    def check_environment(self):
        """檢查 Python 環境"""
        self.print_info("檢查 Python 環境...")
        
        venv_path = self.project_root / '.venv'
        if not venv_path.exists():
            self.print_error("虛擬環境不存在，請先運行: python -m venv .venv")
            sys.exit(1)
        
        # 檢查 pytest
        try:
            import pytest
            self.print_success(f"pytest 版本: {pytest.__version__}")
        except ImportError:
            self.print_warn("pytest 未安裝，正在安裝...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-cov'])
        
        self.print_success("環境檢查完成")
    
    def run_command(self, cmd, description=""):
        """運行命令"""
        if description:
            self.print_info(description)
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            self.print_error(f"命令執行失敗: {e}")
            return False
    
    def run_all_tests(self):
        """運行所有測試"""
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.tests_dir),
            '-v',
            '--tb=short'
        ]
        return self.run_command(cmd, "運行所有測試...")
    
    def run_unit_tests(self):
        """運行單元測試"""
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.tests_dir),
            '-v',
            '--tb=short',
            '-k', 'not routes'
        ]
        return self.run_command(cmd, "運行單元測試...")
    
    def run_integration_tests(self):
        """運行整合測試"""
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.tests_dir),
            '-v',
            '--tb=short',
            '-k', 'routes'
        ]
        return self.run_command(cmd, "運行整合測試...")
    
    def run_with_coverage(self):
        """運行測試並生成覆蓋率報告"""
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.tests_dir),
            '-v',
            '--cov=.',
            '--cov-report=html:htmlcov',
            '--cov-report=term-missing',
            '--cov-report=xml',
            '--cov-exclude=tests',
            '--cov-exclude=.venv',
            '--cov-exclude=__pycache__',
            '--tb=short'
        ]
        
        success = self.run_command(cmd, "運行測試並生成覆蓋率報告...")
        
        if success:
            htmlcov_path = self.project_root / 'htmlcov' / 'index.html'
            self.print_success(f"覆蓋率報告已生成: {htmlcov_path}")
        
        return success
    
    def run_quick_tests(self):
        """運行快速測試"""
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.tests_dir),
            '-v',
            '--tb=short',
            '-x'  # 首次失敗時停止
        ]
        return self.run_command(cmd, "運行快速測試...")
    
    def run_specific_test(self, test_file):
        """運行特定測試文件"""
        test_path = self.tests_dir / test_file
        
        if not test_path.exists():
            self.print_error(f"測試文件不存在: {test_path}")
            return False
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(test_path),
            '-v',
            '--tb=short'
        ]
        return self.run_command(cmd, f"運行測試: {test_file}")
    
    def cleanup(self):
        """清理測試生成的文件"""
        self.print_info("清理測試生成的文件...")
        
        dirs_to_remove = [
            self.project_root / 'htmlcov',
            self.project_root / '.pytest_cache'
        ]
        
        files_to_remove = [
            self.project_root / '.coverage'
        ]
        
        for dir_path in dirs_to_remove:
            if dir_path.exists():
                import shutil
                shutil.rmtree(dir_path)
        
        for file_path in files_to_remove:
            if file_path.exists():
                file_path.unlink()
        
        # 清理 __pycache__
        for pycache in self.project_root.rglob('__pycache__'):
            import shutil
            shutil.rmtree(pycache)
        
        self.print_success("清理完成")
    
    def run(self, command):
        """運行指定命令"""
        self.check_environment()
        
        commands = {
            'all': self.run_all_tests,
            'unit': self.run_unit_tests,
            'integration': self.run_integration_tests,
            'coverage': self.run_with_coverage,
            'quick': self.run_quick_tests,
            'cleanup': self.cleanup
        }
        
        if command in commands:
            return commands[command]()
        else:
            self.print_error(f"未知指令: {command}")
            return False


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='單元測試運行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python run_tests_cli.py all
  python run_tests_cli.py coverage
  python run_tests_cli.py specific test_app.py
  python run_tests_cli.py cleanup

覆蓋率目標:
  - 整體覆蓋率: >= 80%
  - 服務層覆蓋率: >= 85%
  - 路由層覆蓋率: >= 75%
        """
    )
    
    parser.add_argument(
        'command',
        nargs='?',
        default='help',
        choices=['all', 'unit', 'integration', 'coverage', 'quick', 'specific', 'cleanup', 'help'],
        help='要執行的命令'
    )
    
    parser.add_argument(
        'test_file',
        nargs='?',
        help='特定測試文件名 (用於 specific 命令)'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.command == 'help':
        parser.print_help()
        return 0
    
    if args.command == 'specific':
        if not args.test_file:
            print("錯誤: specific 命令需要指定測試文件名")
            return 1
        success = runner.run_specific_test(args.test_file)
    else:
        success = runner.run(args.command)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
