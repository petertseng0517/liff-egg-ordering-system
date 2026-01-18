#!/bin/bash

# 測試運行腳本
# 使用方式: ./run_tests.sh [option]
# Options:
#   all          - 運行所有測試
#   unit         - 運行單元測試
#   integration  - 運行整合測試
#   coverage     - 運行測試並生成覆蓋率報告
#   quick        - 快速測試（不含覆蓋率報告）

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 配置顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印帶顏色的訊息
print_info() {
    echo -e "${BLUE}ℹ ${1}${NC}"
}

print_success() {
    echo -e "${GREEN}✓ ${1}${NC}"
}

print_warn() {
    echo -e "${YELLOW}⚠ ${1}${NC}"
}

print_error() {
    echo -e "${RED}✗ ${1}${NC}"
}

# 檢查 Python 環境
check_environment() {
    print_info "檢查 Python 環境..."
    
    if [ ! -d ".venv" ]; then
        print_error "虛擬環境不存在，請先運行: python -m venv .venv"
        exit 1
    fi
    
    source .venv/bin/activate
    
    if ! command -v pytest &> /dev/null; then
        print_warn "pytest 未安裝，正在安裝..."
        pip install pytest pytest-cov
    fi
    
    if ! command -v python &> /dev/null; then
        print_error "Python 未找到"
        exit 1
    fi
    
    print_success "環境檢查完成"
}

# 運行所有測試
run_all_tests() {
    print_info "運行所有測試..."
    pytest tests/ -v --tb=short
}

# 運行單元測試
run_unit_tests() {
    print_info "運行單元測試..."
    pytest tests/test_*.py -v -m "unit or (not integration)" --tb=short
}

# 運行整合測試
run_integration_tests() {
    print_info "運行整合測試..."
    pytest tests/test_*_routes.py -v -m "integration" --tb=short
}

# 運行測試並生成覆蓋率報告
run_with_coverage() {
    print_info "運行測試並生成覆蓋率報告..."
    pytest tests/ \
        -v \
        --cov=. \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-report=xml \
        --cov-exclude=tests \
        --cov-exclude=.venv \
        --cov-exclude=__pycache__ \
        --tb=short
    
    print_success "覆蓋率報告已生成在 htmlcov/index.html"
}

# 快速測試
run_quick_tests() {
    print_info "運行快速測試（不含覆蓋率報告）..."
    pytest tests/ -v --tb=short
}

# 運行特定測試文件
run_specific_test() {
    local test_file=$1
    print_info "運行測試: $test_file"
    
    if [ ! -f "tests/$test_file" ]; then
        print_error "測試文件不存在: tests/$test_file"
        exit 1
    fi
    
    pytest "tests/$test_file" -v --tb=short
}

# 清理生成的文件
cleanup() {
    print_info "清理測試生成的文件..."
    rm -rf htmlcov/
    rm -rf .coverage
    rm -rf .pytest_cache/
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    print_success "清理完成"
}

# 顯示幫助信息
show_help() {
    cat << EOF
單元測試運行腳本

使用方式: $0 [command] [options]

指令:
  all           - 運行所有測試
  unit          - 運行單元測試
  integration   - 運行整合測試
  coverage      - 運行測試並生成覆蓋率報告
  quick         - 快速測試（不含覆蓋率報告）
  specific      - 運行特定測試文件 (usage: $0 specific test_file.py)
  cleanup       - 清理測試生成的文件
  help          - 顯示此幫助信息

範例:
  $0 all
  $0 coverage
  $0 specific test_app.py

覆蓋率目標:
  - 整體覆蓋率: >= 80%
  - 服務層覆蓋率: >= 85%
  - 路由層覆蓋率: >= 75%
EOF
}

# 主程序
main() {
    local command=${1:-help}
    
    case "$command" in
        all)
            check_environment
            run_all_tests
            ;;
        unit)
            check_environment
            run_unit_tests
            ;;
        integration)
            check_environment
            run_integration_tests
            ;;
        coverage)
            check_environment
            run_with_coverage
            ;;
        quick)
            check_environment
            run_quick_tests
            ;;
        specific)
            if [ -z "$2" ]; then
                print_error "請指定測試文件名"
                exit 1
            fi
            check_environment
            run_specific_test "$2"
            ;;
        cleanup)
            cleanup
            ;;
        help)
            show_help
            ;;
        *)
            print_error "未知指令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 執行主程序
main "$@"
