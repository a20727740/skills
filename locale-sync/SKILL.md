---
name: locale-sync
description: 使用主文件（默认 zh-CN-GJ）同步多语言 locale 文件，确保 key 一致性，翻译缺失 key，并对齐文件结构。
---

# i18n 多语言同步技能

本技能用于基于一个"主文件"同步 `utils/locale/` 目录下的多个语言文件。

## 配置

- **默认主文件**：`utils/locale/zh-CN-GJ.js`（国产版本，使用"占卜断事"等术语）
- **目标目录**：`utils/locale/`
- **目标语言**：全部 28 个 locale 文件（见下方完整列表）
- **项目路径**：`/Users/mo/Documents/uniapp/guojisuansuan/`

### 完整 locale 文件列表（28 个）

| 文件 | 语言 | 文件 | 语言 |
|------|------|------|------|
| `zh-CN-GJ.js` | 简体中文（主文件/国产版） | `zh-CN.js` | 简体中文（国际版） |
| `zh-TW.js` | 繁體中文 | `en-US.js` | English |
| `ja-JP.js` | 日本語 | `ko-KR.js` | 한국어 |
| `es-ES.js` | Español | `fr-FR.js` | Français |
| `de-DE.js` | Deutsch | `de-AT.js` | Österreichisches Deutsch |
| `it-IT.js` | Italiano | `pt-BR.js` | Português (BR) |
| `pt-PT.js` | Português (PT) | `ru-RU.js` | Русский |
| `tr-TR.js` | Türkçe | `id-ID.js` | Bahasa Indonesia |
| `es-CL.js` | Español (Chile) | `fil-PH.js` | Filipino |
| `ms-MY.js` | Bahasa Melayu | `th-TH.js` | ไทย |
| `hu-HU.js` | Magyar | `pl-PL.js` | Polski |
| `cs-CZ.js` | Čeština | `sk-SK.js` | Slovenčina |
| `ro-RO.js` | Română | `bg-BG.js` | Български |
| `el-GR.js` | Ελληνικά | `ga-IE.js` | Gaeilge |

### zh-CN vs zh-CN-GJ 术语差异

`zh-CN-GJ.js` 是国产版本，与 `zh-CN.js`（国际版）key 结构完全一致，但存在术语差异：

| 场景 | zh-CN（国际版） | zh-CN-GJ（国产版/主文件） |
|------|-----------------|--------------------------|
| 应用名 | 算了么 | 算算玄学 |
| 功能名称 | 探索 | 占卜解惑/断事 |
| 操作按钮 | 探索 | 起卦断事 |
| 状态描述 | 测算中 | 起卦中 |
| 次数用完 | 探索次数已用完 | 占卜解惑次数已用完 |

## 核心原则：必须分批处理

> **重要**：28 个 locale 文件每个约 1600+ 行，全部读取会超出上下文限制。
> **必须**按以下策略分批处理，每批 2-3 个文件，不可一次性读取所有文件。

### 推荐批次划分

| 批次 | 文件 | 说明 |
|------|------|------|
| 第 1 批 | `zh-TW.js`, `zh-CN.js` | 中文类 |
| 第 2 批 | `ja-JP.js`, `ko-KR.js` | 中日韩 |
| 第 3 批 | `en-US.js`, `id-ID.js`, `ms-MY.js` | 英语系+东南亚 |
| 第 4 批 | `es-ES.js`, `es-CL.js`, `pt-BR.js`, `pt-PT.js` | 西葡语系 |
| 第 5 批 | `fr-FR.js`, `de-DE.js`, `de-AT.js`, `it-IT.js` | 西欧语言 |
| 第 6 批 | `ru-RU.js`, `tr-TR.js`, `pl-PL.js`, `cs-CZ.js`, `sk-SK.js` | 中东欧语言 |
| 第 7 批 | `ro-RO.js`, `bg-BG.js`, `el-GR.js`, `hu-HU.js` | 东欧/巴尔干语言 |
| 第 8 批 | `th-TH.js`, `fil-PH.js`, `ga-IE.js` | 亚洲/特殊语言 |

### 每批次的处理流程

对每个文件：
1. 用 Grep 定位缺失 key 附近的上下文（如 `suggestPage:` 的行号）
2. 用 Read 读取该位置前后 5-10 行（不要读整个文件）
3. 用 Edit 精准插入缺失的翻译内容
4. 已存在的 key **不要动**

### 避免上下文溢出的技巧

- **不要** `Read` 整个 locale 文件（1600+ 行）
- **不要** 一次读取多个完整文件
- **用 Grep** 先定位行号，再用 `Read` + `offset/limit` 读局部
- **用并行工具调用** 在同一批次中同时处理多个文件（Grep 并行、Edit 并行）
- **先分析再动手**：先用 Python 脚本一次性检查所有文件的 key 差异，确定哪些文件需要修改

## Agent 执行步骤

### 步骤 1：全局差异检测（一次性）

先运行内联 Python 脚本检测所有文件的 key 差异，**不要逐个读取文件**：

```bash
cd utils/locale && python3 -c "
import re, os
def extract_keys(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    keys = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            continue
        match = re.match(r'^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', line)
        if match:
            keys.append(match.group(1))
    return keys
master_keys = set(extract_keys('zh-CN-GJ.js'))
print(f'zh-CN-GJ.js 总 key 数: {len(master_keys)}\n')
for fn in sorted(os.listdir('.')):
    if not fn.endswith('.js') or fn == 'zh-CN-GJ.js':
        continue
    target_keys = set(extract_keys(fn))
    missing = master_keys - target_keys
    extra = target_keys - master_keys
    if missing or extra:
        print(f'⚠️  {fn:20s} | 缺失 {len(missing):2d} 个, 多余 {len(extra):2d} 个 | 缺失: {sorted(missing)[:5]}')
    else:
        print(f'✅ {fn:20s} | 完全一致')
"
```

根据输出结果，确定哪些文件需要修改、缺失了哪些 key。

### 步骤 2：读取主文件中缺失 key 的内容

只读取主文件中缺失部分的内容（用 Grep 定位行号 + Read 局部读取）。

例如缺失 `suggest` 对象：
```bash
# 先定位
grep -n "^suggest:" zh-CN-GJ.js
# 再局部读取
# Read zh-CN-GJ.js offset=行号 limit=20
```

### 步骤 3：按批次补充缺失 key

对每个需要修改的文件：
1. **Grep** 定位插入点（如 `suggestPage:` 的行号）
2. **Read** 插入点前后 5 行确认上下文
3. **Edit** 精准插入翻译后的内容

**翻译要求**：
- 从文件名推断目标语言（如 `ja-JP.js` -> 日语）
- 占位符（`{0}`、`%s`）必须保持不变
- 技术术语保持一致

### 步骤 4：验证

```bash
# 1. 重新运行差异检测脚本，确认所有文件 key 一致
# 2. JS 语法检查
for f in *.js; do node --check "$f" && echo "✅ $f" || echo "❌ $f"; done

# 3. 行数检查
wc -l *.js | sort -n
```

## 文件头注释对照表

```javascript
zh-CN-GJ: /**\n * 简体中文语言包\n */
zh-CN:    /**\n * 简体中文语言包\n */
zh-TW:    /**\n * 繁體中文語言包\n */
en-US:    /**\n * English Language Pack\n */
ja-JP:    /**\n * 日本語言語パック\n */
ko-KR:    /**\n * 한국어 언어 팩\n */
es-ES:    /**\n * Paquete de idioma español\n */
fr-FR:    /**\n * Paquet de langue française\n */
de-DE:    /**\n * Deutsches Sprachpaket\n */
de-AT:    /**\n * Österreichisches Deutsch Sprachpaket\n */
tr-TR:    /**\n * Türkçe dil paketi\n */
ru-RU:    /**\n * Пакет русского языка\n */
pt-BR:    /**\n * Pacote de idioma português\n */
pt-PT:    /**\n * Pacote de idioma português (Portugal)\n */
it-IT:    /**\n * Pacchetto di lingua italiana\n */
id-ID:    /**\n * Paket bahasa Indonesia\n */
es-CL:    /**\n * Paquete de idioma español (Chile)\n */
fil-PH:   /**\n * Paket ng wikang Filipino\n */
ms-MY:    /**\n * Pakej bahasa Melayu\n */
th-TH:    /**\n * ชุดภาษาไทย\n */
hu-HU:    /**\n * Magyar nyelvi csomag\n */
pl-PL:    /**\n * Polski pakiet językowy\n */
cs-CZ:    /**\n * Český jazykový balíček\n */
sk-SK:    /**\n * Slovenský jazykový balíček\n */
ro-RO:    /**\n * Pachet de limbă română\n */
bg-BG:    /**\n * Български езиков пакет\n */
el-GR:    /**\n * Ελληνικό γλωσσικό πακέτο\n */
ga-IE:    /**\n * Pacáiste Gaeilge\n */
```

## 常见问题速查

| 问题 | 检测方法 | 修复方式 |
|------|----------|----------|
| 缺失 key | 运行步骤 1 的 Python 脚本 | 按批次 Edit 补充 |
| 多余 key | 运行步骤 1 的 Python 脚本 | Edit 删除对应行 |
| JS 语法错误 | `node --check file.js` | 检查大括号数量 |
| 行数不一致 | `wc -l *.js \| sort -n` | 检查文件末尾换行符、空行 |
| 文件头语言错误 | 打开文件检查前 3 行 | Edit 替换为正确语言注释 |

### 大括号检查

```bash
# 检查所有文件的大括号数量
for f in *.js; do
  echo "$f: $(python3 -c "with open('$f', 'r') as c: print(f'{c.read().count(\"{\")}/{c.read().count(\"}\")}')")"
done
```

### 文件末尾格式统一

标准末尾格式：`内容 + \n\t}\n\n}\n`

```python
# 统一所有文件末尾
for filename in [f for f in os.listdir('.') if f.endswith('.js')]:
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.rstrip()
    if not content.endswith('}'):
        content += '\n}'
    content += '\n'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
```

## 工具集

本 skill 目录包含辅助 Python 工具（详见 `TOOLS.md`）：

| 工具 | 说明 |
|------|------|
| `locale_manager.py` | 统一管理工具（推荐，已改用 zh-CN-GJ.js 为主文件） |
| `check_keys.py` | Key 一致性检查工具（已改用 zh-CN-GJ.js 为主文件） |
| `translate_ga.py` | 爱尔兰语翻译辅助工具 |

```bash
# 完整检查（推荐）
python3 /path/to/skills/locale-sync/locale_manager.py full

# 只检查 key 一致性
python3 /path/to/skills/locale-sync/locale_manager.py check

# 修复文件末尾格式
python3 /path/to/skills/locale-sync/locale_manager.py fix-trailing
```

## 验证清单

- [ ] 所有 28 个 locale 文件存在
- [ ] Key 与 zh-CN-GJ.js 完全一致（运行步骤 1 脚本）
- [ ] 所有文件 `node --check` 语法通过
- [ ] 文件头与各自语言匹配
