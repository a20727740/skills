#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多语言文件 key 一致性检查脚本
检查所有 locale 文件的 key 是否与 zh-CN.js 一致
"""

import os
import re
from collections import OrderedDict

def extract_keys_from_file(filepath):
    """从 locale 文件中提取所有的 key"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    keys = []
    lines = content.split('\n')

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

def compare_with_master(master_file, target_file):
    """比较目标文件与主文件的 key 差异"""
    master_keys = extract_keys_from_file(master_file)
    target_keys = extract_keys_from_file(target_file)

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

def main():
    locale_dir = os.path.dirname(os.path.abspath(__file__))
    master_file = os.path.join(locale_dir, 'zh-CN-GJ.js')

    # 获取所有 .js 文件
    all_files = [f for f in os.listdir(locale_dir)
                 if f.endswith('.js') and f != 'check_keys.py']

    print("=" * 80)
    print("多语言文件 Key 一致性检查")
    print("=" * 80)
    print(f"\n主文件: zh-CN-GJ.js")
    print(f"检查文件数量: {len(all_files)}\n")

    results = {}

    for filename in sorted(all_files):
        if filename == 'zh-CN.js':
            continue

        filepath = os.path.join(locale_dir, filename)
        result = compare_with_master(master_file, filepath)
        results[filename] = result

        # 输出结果
        status = "✅" if not result['missing'] and not result['extra'] else "⚠️ "
        print(f"{status} {filename:20s} | Keys: {result['target_count']:4d} | ", end='')

        if result['missing']:
            print(f"缺失 {len(result['missing'])} 个: {result['missing'][:3]}...", end='')
        if result['extra']:
            print(f"多余 {len(result['extra'])} 个: {result['extra'][:3]}...", end='')
        if not result['missing'] and not result['extra']:
            print("完全一致", end='')
        print()

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

if __name__ == '__main__':
    main()
