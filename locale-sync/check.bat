@echo off
REM 多语言文件检查脚本 - Windows 版本
REM 使用 locale-sync skill 中的工具

set SKILL_DIR=%~dp0

REM 默认执行完整检查
if "%1"=="" (
    python "%SKILL_DIR%locale_manager.py" --dir . full
) else (
    python "%SKILL_DIR%locale_manager.py" --dir . %*
)
