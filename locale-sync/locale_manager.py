#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言文件管理工具集
统一管理所有 locale 相关的工具和脚本
"""

import os
import sys
import re
import argparse
from pathlib import Path


class LocaleManager:
    """多语言文件管理器"""

    def __init__(self, locale_dir=None):
        """初始化管理器

        Args:
            locale_dir: locale 目录路径，默认为当前目录的父目录
        """
        if locale_dir is None:
            self.locale_dir = Path(__file__).parent.parent
        else:
            self.locale_dir = Path(locale_dir)

        self.master_file = self.locale_dir / 'zh-CN.js'

    def get_all_locale_files(self):
        """获取所有 locale 文件列表"""
        files = [f for f in self.locale_dir.glob('*.js')
                 if f.name != 'check_keys.py' and not f.name.startswith('.')]
        return sorted(files)

    def extract_keys_from_file(self, filepath):
        """从 locale 文件中提取所有的 key

        Args:
            filepath: 文件路径

        Returns:
            list: [(行号, key), ...] 的列表
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        keys = []
        for i, line in enumerate(lines, 1):
            # 跳过注释行
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
                continue

            # 匹配 key: value 或 key: { 格式
            match = re.match(r'^\s*(["\']?)([a-zA-Z_][a-zA-Z0-9_]*)\1\s*:\s*', line)
            if match:
                key = match.group(2)
                keys.append((i, key))

        return keys

    def compare_with_master(self, target_file):
        """比较目标文件与主文件的 key 差异

        Args:
            target_file: 目标文件路径

        Returns:
            dict: {
                'missing': 缺失的 keys,
                'extra': 多余的 keys,
                'master_count': 主文件 key 数量,
                'target_count': 目标文件 key 数量
            }
        """
        master_keys = self.extract_keys_from_file(self.master_file)
        target_keys = self.extract_keys_from_file(target_file)

        master_key_list = [k[1] for k in master_keys]
        target_key_list = [k[1] for k in target_keys]

        master_set = set(master_key_list)
        target_set = set(target_key_list)

        missing_in_target = master_set - target_set
        extra_in_target = target_set - master_set

        return {
            'missing': sorted(list(missing_in_target)),
            'extra': sorted(list(extra_in_target)),
            'master_count': len(master_key_list),
            'target_count': len(target_key_list)
        }

    def check_consistency(self):
        """检查所有文件的 key 一致性"""
        print("=" * 80)
        print("多语言文件 Key 一致性检查")
        print("=" * 80)
        print(f"\n主文件: {self.master_file.name}")
        print(f"检查文件数量: {len(self.get_all_locale_files())}\n")

        results = {}
        all_ok = True

        for filepath in self.get_all_locale_files():
            if filepath.name == self.master_file.name:
                continue

            result = self.compare_with_master(filepath)
            results[filepath.name] = result

            # 输出结果
            if result['missing'] or result['extra']:
                all_ok = False
                status = "⚠️ "
            else:
                status = "✅"

            print(f"{status} {filepath.name:20s} | Keys: {result['target_count']:4d} | ", end='')

            if result['missing']:
                print(f"缺失 {len(result['missing'])} 个: {result['missing'][:3]}...", end='')
            if result['extra']:
                print(f"多余 {len(result['extra'])} 个: {result['extra'][:3]}...", end='')
            if not result['missing'] and not result['extra']:
                print("完全一致", end='')
            print()

        if not all_ok:
            print("\n" + "=" * 80)
            print("详细差异报告")
            print("=" * 80)

            for filename, result in results.items():
                if result['missing'] or result['extra']:
                    print(f"\n【{filename}】")
                    if result['missing']:
                        print(f"  缺失的 keys ({len(result['missing'])} 个):")
                        for key in result['missing']:
                            print(f"    - {key}")
                    if result['extra']:
                        print(f"  多余的 keys ({len(result['extra'])} 个):")
                        for key in result['extra']:
                            print(f"    - {key}")

        return all_ok

    def check_line_counts(self):
        """检查所有文件的行数统计"""
        print("\n" + "=" * 80)
        print("文件行数统计")
        print("=" * 80)

        line_counts = []
        for filepath in self.get_all_locale_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                line_count = len(f.readlines())
            line_counts.append((filepath.name, line_count))

        # 按行数排序
        line_counts.sort(key=lambda x: x[1])

        for filename, count in line_counts:
            print(f"  {filename:20s}: {count:4d} 行")

        # 检查是否所有文件行数相同
        unique_counts = set(count for _, count in line_counts)
        if len(unique_counts) == 1:
            print(f"\n✅ 所有文件行数一致: {unique_counts.pop()} 行")
            return True
        else:
            print(f"\n⚠️  文件行数不一致，共有 {len(unique_counts)} 种不同的行数")
            return False

    def check_syntax(self):
        """检查所有文件的 JavaScript 语法"""
        print("\n" + "=" * 80)
        print("JavaScript 语法检查")
        print("=" * 80)

        import subprocess

        all_ok = True
        for filepath in self.get_all_locale_files():
            result = subprocess.run(
                ['node', '--check', str(filepath)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"  ✅ {filepath.name}")
            else:
                print(f"  ❌ {filepath.name}")
                print(f"     {result.stderr}")
                all_ok = False

        return all_ok

    def fix_trailing_newlines(self):
        """统一所有文件的末尾换行符格式"""
        print("\n" + "=" * 80)
        print("统一文件末尾格式")
        print("=" * 80)

        for filepath in self.get_all_locale_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 移除末尾所有空白字符和换行符
            content = content.rstrip()

            # 确保以换行符结束
            if not content.endswith('\n'):
                content += '\n'

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"  ✅ {filepath.name}: 已统一末尾格式")

        return True

    def remove_extra_blank_lines(self):
        """移除 explore 部分后的多余空行"""
        print("\n" + "=" * 80)
        print("移除 explore 部分后的多余空行")
        print("=" * 80)

        for filepath in self.get_all_locale_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 查找 explore 部分
            new_lines = []
            skip_next_blank = False

            for i, line in enumerate(lines):
                # 如果当前行是 fortune_trends 的最后一行
                if "fortune_trends" in line and ':' in line:
                    new_lines.append(line)
                    # 检查下一行是否是空行
                    if i + 1 < len(lines) and not lines[i + 1].strip():
                        skip_next_blank = True
                    continue

                # 如果应该跳过这个空行
                if skip_next_blank and not line.strip():
                    skip_next_blank = False
                    continue

                new_lines.append(line)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            print(f"  ✅ {filepath.name}: 已移除多余空行")

        return True

    def add_blank_line_before_composite(self):
        """在 composite 部分前添加空行（如果缺失）"""
        print("\n" + "=" * 80)
        print("添加 composite 部分前的空行")
        print("=" * 80)

        for filepath in self.get_all_locale_files():
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否需要添加空行
            pattern = r"\bretry:\s*'[^\']+'\s*\}\s*\n\s*//\s*专业合盘"
            if re.search(pattern, content):
                # 添加空行
                content = re.sub(
                    r"\b(retry:\s*'[^\']+'\s*\})\s*\n\s*//(.*?合盘)",
                    r"\1\n\n\t// \2",
                    content
                )

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)

                print(f"  ✅ {filepath.name}: 已添加空行")
            else:
                print(f"  ⏭️  {filepath.name}: 无需修改")

        return True

    def full_check(self):
        """执行完整的检查流程"""
        print("\n" + "🔍" * 40)
        print("开始完整检查...")
        print("🔍" * 40 + "\n")

        results = {
            'syntax': self.check_syntax(),
            'line_counts': self.check_line_counts(),
            'consistency': self.check_consistency()
        }

        print("\n" + "=" * 80)
        print("检查结果汇总")
        print("=" * 80)
        print(f"  语法检查:     {'✅ 通过' if results['syntax'] else '❌ 失败'}")
        print(f"  行数检查:     {'✅ 通过' if results['line_counts'] else '❌ 失败'}")
        print(f"  一致性检查:   {'✅ 通过' if results['consistency'] else '❌ 失败'}")

        all_ok = all(results.values())
        if all_ok:
            print("\n🎉 所有检查通过！")
        else:
            print("\n⚠️  部分检查未通过，请查看详细信息")

        return all_ok


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='多语言文件管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 检查 key 一致性
  python locale_manager.py check

  # 检查文件行数
  python locale_manager.py lines

  # 检查 JavaScript 语法
  python locale_manager.py syntax

  # 执行完整检查
  python locale_manager.py full

  # 修复文件末尾格式
  python locale_manager.py fix-trailing

  # 移除多余空行
  python locale_manager.py fix-blanks
        """
    )

    parser.add_argument(
        'command',
        choices=['check', 'lines', 'syntax', 'full', 'fix-trailing', 'fix-blanks', 'fix-composite'],
        help='要执行的命令'
    )

    parser.add_argument(
        '--dir',
        default=None,
        help='locale 目录路径（默认为当前目录）'
    )

    args = parser.parse_args()

    # 创建管理器
    manager = LocaleManager(locale_dir=args.dir)

    # 执行命令
    if args.command == 'check':
        result = manager.check_consistency()
        sys.exit(0 if result else 1)

    elif args.command == 'lines':
        result = manager.check_line_counts()
        sys.exit(0 if result else 1)

    elif args.command == 'syntax':
        result = manager.check_syntax()
        sys.exit(0 if result else 1)

    elif args.command == 'full':
        result = manager.full_check()
        sys.exit(0 if result else 1)

    elif args.command == 'fix-trailing':
        result = manager.fix_trailing_newlines()
        sys.exit(0 if result else 1)

    elif args.command == 'fix-blanks':
        result = manager.remove_extra_blank_lines()
        sys.exit(0 if result else 1)

    elif args.command == 'fix-composite':
        result = manager.add_blank_line_before_composite()
        sys.exit(0 if result else 1)


if __name__ == '__main__':
    main()
