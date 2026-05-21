#!/bin/bash
# 多语言文件检查脚本
# 使用 locale-sync skill 中的工具

# 获取脚本所在目录
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 默认执行完整检查
if [ -z "$1" ]; then
    python3 "$SKILL_DIR/locale_manager.py" --dir . full
else
    python3 "$SKILL_DIR/locale_manager.py" --dir . "$@"
fi
