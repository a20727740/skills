---
name: init-memory
description: 为当前项目生成 CLAUDE.md、.claude/rules/ 规则文件和自动记忆 MEMORY.md，一次调用全部搞定
argument-hint: [--force]
disable-model-invocation: true
---

# init-memory: 项目记忆初始化

为当前项目一次性生成三层记忆文件。生成的文件包含结构化的占位模板，用户后续可自行补充内容。

## 执行步骤

### 第一步：探测项目环境

扫描当前工作目录，收集以下信息（不要输出，内部使用）：

1. **当前工作目录**：使用 Claude Code 的当前工作目录（`cwd`），不要向上查找 git 根目录
2. **项目名称**：取当前工作目录名
3. **技术栈**：检查当前工作目录及子目录中是否存在以下文件，推断技术栈
   - `package.json` → Node.js / 前端项目，读取 scripts 字段
   - `Podfile` / `*.xcodeproj` / `*.xcworkspace` → iOS / Swift 项目
   - `build.gradle` / `build.gradle.kts` → Android / Kotlin 项目
   - `Cargo.toml` → Rust 项目
   - `go.mod` → Go 项目
   - `requirements.txt` / `pyproject.toml` / `setup.py` → Python 项目
   - `Gemfile` → Ruby 项目
   - `pom.xml` → Java / Maven 项目
   - `*.sln` / `*.csproj` → .NET 项目
   - `pubspec.yaml` → Flutter / Dart 项目
   - `manifest.json` / `pages.json` → uni-app / 小程序项目
   - `Package.swift` → Swift Package Manager 项目
4. **已有文件**：检查当前工作目录是否已存在 `CLAUDE.md`、`.claude/`、`README.md`
5. **项目结构**：扫描当前工作目录，自动生成目录树。使用 Bash 工具执行：
   ```bash
   # 获取项目目录结构（排除隐藏文件、构建产物、node_modules 等）
   find {当前工作目录} -maxdepth 3 \
     -not -path '*/.*' \
     -not -path '*/node_modules/*' \
     -not -path '*/build/*' \
     -not -path '*/DerivedData/*' \
     -not -path '*/.build/*' \
     -not -path '*/CodeIDE.app/*' \
     -not -path '*/design-system/*' \
     | sort | head -100
   ```
   然后根据扫描结果，用 `tree` 格式手动构建目录树，为每个文件/目录添加 `# 注释` 说明其用途。注释规则：
   - 目录：简述该目录的职责
   - 源文件：从文件名和内容推断功能，如 `FileManagerApp.swift → # App 入口、生命周期管理`
   - 资源/配置文件：简述用途
   - 忽略编译产物（`.app`、`.build`、`DerivedData`）、隐藏目录、`node_modules`

### 第二步：生成或更新 CLAUDE.md

在**当前工作目录**下生成或更新 `CLAUDE.md` 文件。

**每次调用都必须更新「目录结构」**，无论文件是否已存在。

**情况 A：文件不存在或传入了 `--force`** → 用 Write 工具创建完整文件（模板如下）

**情况 B：文件已存在且无 `--force`** → 用 Read 工具读取现有内容，然后用 Edit 工具**仅替换**「目录结构」部分的代码块（即 `## 目录结构` 到下一个 `##` 之间的内容）。其他章节保持不变。

**定位目录结构的规则**：找到 `## 目录结构`（或 `## 项目结构`）标题，替换其下方紧跟的 ``` 代码块直到下一个 `##` 标题。如果旧文件中没有此章节，在「技术栈」章节之后插入。

生成模板如下（根据技术栈替换对应内容）：

```markdown
# {项目名称}

## 项目概述

<!-- TODO: 补充项目简要描述 -->

## 技术栈

{根据探测结果列出，例如：}
- 语言：Swift / TypeScript / Python
- 框架：{框架名称和版本}
- 包管理：CocoaPods / npm / pip

## 目录结构

{根据第一步扫描结果，自动生成如下格式的目录树，每个条目带 # 注释：}

```
{项目名}/
├── Package.swift                  # SPM 包定义
├── build.sh                       # 多架构构建脚本 (arm64/x86_64/universal)
├── Sources/                       # 源代码目录
│   ├── FileManagerApp.swift       # App 入口、生命周期管理、菜单命令
│   ├── IDEState.swift             # 全局状态管理（核心）
│   ├── Models.swift               # 数据模型
│   ├── Services.swift             # 服务层
│   ├── Views/                     # UI 视图目录
│   │   ├── Welcome/               # 欢迎页
│   │   ├── Editor/                # 编辑器视图
│   │   ├── Settings/              # 设置页面
│   │   └── Components/            # 通用组件
│   └── MemoryManagement/          # 内存管理
├── Resources/                     # 资源文件
├── Tests/                         # 测试目录
└── ...
```

注意：只列出项目自身文件，排除编译产物、隐藏目录、第三方依赖目录。注释要简洁准确，从文件名和内容推断用途。

## 常用命令

{根据 package.json scripts 或其他配置推断，无法推断则留占位符}
<!-- TODO: 补充或修正命令 -->
- 构建：`<!-- TODO -->`
- 测试：`<!-- TODO -->`
- 运行：`<!-- TODO -->`

## 编码规范

<!-- TODO: 补充项目编码规范，例如：
- 缩进：2 空格 / 4 空格
- 命名风格：camelCase / snake_case
- 最大行宽：120
-->

## 架构说明

<!-- TODO: 补充架构要点，例如：
- 数据流方向
- 核心模块职责
- 第三方依赖及用途
-->

## 注意事项

<!-- TODO: 补充开发注意事项，例如：
- 已知问题和 workaround
- 需要特别关注的文件
- 环境配置要求
-->
```

### 第三步：生成 .claude/rules/ 规则文件

在**当前工作目录**的 `.claude/rules/` 目录下生成规则文件。注意：是当前工作目录，不是 git 仓库根目录。

**如果文件已存在且没有 `--force`**：跳过该文件

使用 Bash 工具执行 `mkdir -p {当前工作目录}/.claude/rules` 创建目录，然后用 Write 工具写入以下文件：

#### 文件 1: `.claude/rules/code-style.md`

```markdown
---
paths:
  - "**/*.swift"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/*.py"
  - "**/*.go"
  - "**/*.kt"
  - "**/*.java"
---

# 代码风格

<!-- TODO: 根据项目实际情况补充 -->

## 通用规则

- 代码注释使用中文
- TODO 标记格式：`// TODO: [描述]`

## 命名规范

<!-- TODO: 补充命名规则 -->

## 格式化

<!-- TODO: 补充格式化工具和配置，如 SwiftLint, ESLint, Prettier 等 -->
```

#### 文件 2: `.claude/rules/bug-fix.md`

```markdown
# Bug 修复规范

## 修复流程

1. 先理解问题根因，不要只修表面症状
2. 检查调用链和相关代码，发现关联问题一并修复
3. 修复后验证：
   - 类型检查通过
   - Lint 检查通过
   - 无明显运行时错误

## 注意事项

<!-- TODO: 补充项目特有的调试技巧和常见问题 -->
```

#### 文件 3: `.claude/rules/git-workflow.md`

```markdown
# Git 工作流

## 提交规范

<!-- TODO: 补充 commit message 格式要求 -->

## 分支策略

<!-- TODO: 补充分支命名和合并策略 -->
```

### 第四步：生成自动记忆 MEMORY.md

确定项目的自动记忆目录路径：

- 如果是 git 仓库：`~/.claude/projects/<编码后的项目路径>/memory/`
- 如果不是 git 仓库：`~/.claude/projects/<编码后的项目路径>/memory/`

使用 Bash 工具获取实际路径：
```bash
# 获取当前工作目录的绝对路径（去掉 / 替换为 -）
PROJECT_PATH=$(pwd)
ENCODED_PATH=$(echo "$PROJECT_PATH" | sed 's|/|-|g')
echo "~/.claude/projects/${ENCODED_PATH}/memory/"
```

用 Bash 创建目录 `mkdir -p`，然后用 Write 工具写入 `MEMORY.md`：

```markdown
# {项目名称} - 记忆索引

## 项目基本信息

- 项目路径：{项目根目录}
- 技术栈：{探测到的技术栈}
- 初始化时间：{当前日期}

## 构建和运行

<!-- Claude 会在此自动积累：构建命令、运行方式、部署步骤 -->

## 调试记录

<!-- Claude 会在此自动积累：调试发现、问题模式 -->

## 用户偏好

<!-- Claude 会在此自动积累：从对话中学习到的用户偏好 -->

## 重要发现

<!-- Claude 会在此自动积累：架构洞察、代码模式、依赖关系 -->
```

### 第五步：输出结果摘要

完成所有文件生成后，输出简洁的摘要表格：

```
✅ 记忆文件初始化完成！

| 文件 | 路径 | 状态 |
|------|------|------|
| 项目 CLAUDE.md | {当前工作目录}/CLAUDE.md | ✅ 已创建 / 🔄 已更新目录结构 |
| 代码风格规则 | {当前工作目录}/.claude/rules/code-style.md | ✅ 已创建 / ⏭ 已跳过 |
| Bug修复规范 | {当前工作目录}/.claude/rules/bug-fix.md | ✅ 已创建 / ⏭ 已跳过 |
| Git工作流 | {当前工作目录}/.claude/rules/git-workflow.md | ✅ 已创建 / ⏭ 已跳过 |
| 自动记忆 | ~/.claude/projects/.../memory/MEMORY.md | ✅ 已创建 / ⏭ 已跳过 |

所有文件包含 <!-- TODO --> 占位符，请根据项目实际情况补充内容。
运行 /memory 可随时查看和编辑这些文件。
```

如果某些文件被跳过，对应行显示 `⏭ 已跳过（已存在）`。

## 重要规则

- **「目录结构」每次都更新**：CLAUDE.md 中的目录结构章节在每次调用时都必须重新扫描并更新，反映最新文件变化
- 不要覆盖已有文件的其他章节（除非 `--force`）
- 生成的文件是模板，包含 `<!-- TODO -->` 占位符供用户后续补充
- 根据探测到的技术栈调整模板内容（如 Swift 项目不需要 Python 相关的 paths）
- rules 文件的 `paths` 字段根据实际技术栈只保留匹配的 glob 模式
- 保持生成的文件简洁，每个文件控制在 50 行以内
