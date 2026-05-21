# Locale 工具集

多语言文件管理工具的统一管理目录。

## 目录结构

```
utils/locale/
├── tools/
│   ├── locale_manager.py    # 主工具脚本（推荐使用）
│   ├── check_keys.py        # Key 一致性检查工具
│   └── README.md            # 本文档
├── zh-CN-GJ.js              # 简体中文国产版（主文件）
├── zh-CN.js                 # 简体中文国际版
├── zh-TW.js                 # 繁體中文
├── en-US.js                 # 英语
├── ja-JP.js                 # 日语
├── ko-KR.js                 # 韩语
├── es-ES.js                 # 西班牙语
├── es-CL.js                 # 西班牙语（智利）
├── fr-FR.js                 # 法语
├── de-DE.js                 # 德语
├── de-AT.js                 # 德语（奥地利）
├── it-IT.js                 # 意大利语
├── pt-BR.js                 # 葡萄牙语（巴西）
├── pt-PT.js                 # 葡萄牙语（葡萄牙）
├── ru-RU.js                 # 俄语
├── tr-TR.js                 # 土耳其语
├── id-ID.js                 # 印尼语
├── fil-PH.js                # 菲律宾语
├── ms-MY.js                 # 马来语
├── th-TH.js                 # 泰语
├── hu-HU.js                 # 匈牙利语
├── pl-PL.js                 # 波兰语
├── cs-CZ.js                 # 捷克语
├── sk-SK.js                 # 斯洛伐克语
├── ro-RO.js                 # 罗马尼亚语
├── bg-BG.js                 # 保加利亚语
├── el-GR.js                 # 希腊语
└── ga-IE.js                 # 爱尔兰语
```

工具脚本目录：

```
.agents/skills/locale-sync/
├── SKILL.md              # 技能文档
├── TOOLS.md              # 本文档
├── locale_manager.py     # 主工具脚本（推荐使用）
├── check_keys.py         # Key 一致性检查工具
├── translate_ga.py       # 爱尔兰语翻译辅助工具
├── check.sh              # Shell 检查入口
└── check.bat             # Windows 检查入口
```

## 快速开始

### 使用 locale_manager.py（推荐）

`locale_manager.py` 是统一的管理工具，集成了所有功能：

```bash
# 进入 locale 目录
cd utils/locale

# 执行完整检查（推荐）
python tools/locale_manager.py full

# 只检查 key 一致性
python tools/locale_manager.py check

# 只检查行数
python tools/locale_manager.py lines

# 只检查 JavaScript 语法
python tools/locale_manager.py syntax

# 修复文件末尾格式
python tools/locale_manager.py fix-trailing

# 移除多余空行
python tools/locale_manager.py fix-blanks

# 添加 composite 部分前的空行
python tools/locale_manager.py fix-composite
```

### 使用 check_keys.py

`check_keys.py` 是独立的 key 一致性检查工具：

```bash
# 进入 locale 目录
cd utils/locale

# 运行检查
python tools/check_keys.py
```

## 命令详解

### locale_manager.py 命令

| 命令 | 说明 | 输出 |
|------|------|------|
| `full` | 执行完整检查 | 语法、行数、key 一致性 |
| `check` | 检查 key 一致性 | 所有文件的 key 对比 |
| `lines` | 检查行数统计 | 所有文件的行数 |
| `syntax` | 检查 JavaScript 语法 | Node.js 语法验证 |
| `fix-trailing` | 修复末尾格式 | 统一文件末尾换行符 |
| `fix-blanks` | 移除多余空行 | 清理 explore 部分后的空行 |
| `fix-composite` | 添加缺失空行 | 在 composite 部分前添加空行 |

## 检查报告示例

### 完整检查输出

```
开始完整检查...

================================================================================
JavaScript 语法检查
================================================================================
  ✅ de-DE.js
  ✅ en-US.js
  ...

================================================================================
文件行数统计
================================================================================
  de-DE.js             : 1636 行
  en-US.js             : 1636 行
  ...

✅ 所有文件行数一致: 1636 行

================================================================================
多语言文件 Key 一致性检查
================================================================================

主文件: zh-CN-GJ.js
检查文件数量: 27

✅ de-DE.js             | Keys: 1092 | 完全一致
✅ en-US.js             | Keys: 1092 | 完全一致
  ...

================================================================================
检查结果汇总
================================================================================
  语法检查:     ✅ 通过
  行数检查:     ✅ 通过
  一致性检查:   ✅ 通过

🎉 所有检查通过！
```

## 常见问题修复

### 问题 1: 行数不一致

**症状**: 不同文件的行数不同

**解决**:
```bash
python tools/locale_manager.py fix-blanks
python tools/locale_manager.py fix-trailing
```

### 问题 2: JavaScript 语法错误

**症状**: `node --check` 报错

**解决**:
1. 查看具体错误信息
2. 检查大括号是否匹配
3. 使用 `python tools/locale_manager.py syntax` 查看哪个文件有问题

### 问题 3: Key 不一致

**症状**: 某些文件缺失或有多余的 key

**解决**:
1. 运行 `python tools/locale_manager.py check` 查看详情
2. 手动添加缺失的 key 或删除多余的 key
3. 重新运行检查验证

## 最佳实践

### 提交前检查

在提交代码前，建议运行完整检查：

```bash
cd utils/locale
python tools/locale_manager.py full
```

### Git Hook

在 `.git/hooks/pre-commit` 中添加：

```bash
#!/bin/bash
cd utils/locale
python tools/locale_manager.py full
if [ $? -ne 0 ]; then
    echo "❌ 多语言文件检查失败，请修复后再提交"
    exit 1
fi
```

### CI/CD 集成

在 GitHub Actions 中添加检查步骤：

```yaml
name: Locale Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check locale files
        run: |
          cd utils/locale
          python tools/locale_manager.py full
```

## 文件格式规范

### 标准格式

所有 locale 文件应遵循以下格式规范：

1. **编码**: UTF-8
2. **行结束符**: LF (`\n`)
3. **文件末尾**: `\n\t}\n}\n`
4. **缩进**: Tab
5. **对象格式**: `key: 'value'`（冒号后有空格）

### explore 部分格式

```javascript
explore: {
    life_blueprint: '...',
    love_compatibility: '...',
    work_compatibility: '...',
    decision_oracle: '...',
    fortune_trends: '...',
}
```

### composite 部分格式

```javascript
    // 前面的内容
    retry: 'Retry'
},

// 专业合盘
composite: {
    ...
}
```

## 相关文档

- [locale-sync 技能文档](./SKILL.md)
- [项目主 README](../../../README.md)

---

**最后更新**: 2026-05-21
**版本**: 2.0.0
**变更**: 主文件从 zh-CN.js 切换为 zh-CN-GJ.js，locale 文件从 14 个扩展至 28 个
