---
name: mcp-bridge-guide
description: 简单桥接 MCP 使用指南 - 架构AI只做分析与拆解，所有实现必须分发给Worker执行
version: 4.0.0
tags: [mcp, bridge, ai, proxy, multi-provider, multimodal]
---

# 简单桥接 MCP 使用指南

## 概述

简单桥接（Bridge Manager）是一个 macOS 状态栏应用，将多个 AI 供应商统一为本地 API。外部 AI 应用（如 Claude Code）通过 **5200 端口**的 MCP Server 连接，用极简别名（`"1号"`、`"2号"`）调度内部 Worker。

## ⛔ 强制自检（最高优先级）

收到任何用户请求后，在执行任何操作前，必须先完成以下自检：

1. **判断请求类型**：
   - 纯信息查询（解释概念、回答问题） → 可自行回答，标注 `[Worker: 未派任务]`
   - 涉及代码修改/文件操作/功能实现 → **必须走 Worker 流程，禁止自己动手**

2. **代码修改任务的强制流程**：
   - ❌ 禁止调用 write_to_file / replace_file_content / multi_replace_file_content / run_command
   - ✅ 只允许用 read 类工具收集上下文
   - ✅ 分析 + 拆解 + assign_task 分发

3. **违规检测口诀**：
   > 如果我下一步要「改文件」或「跑命令」，那我就违规了。停下来，走 assign_task。

---

## 核心原则（铁律）

> **架构AI只做分析和拆解，绝不动手实现。所有编码、修改、实现工作必须分发给 Worker。**

```
用户需求
    │
    ▼
架构AI ──── 分析方向 + 拆解任务 + 注入上下文 ────→ Worker 执行
                                                      │
                                                      ▼
架构AI ◀──────────────── 审核结果 ──────────────── Worker 返回
    │
    ▼
 合格 → 落地应用代码
 不合格 → 打回重做（最多5次）
```

**架构AI（Claude Code 自身）禁止行为**：
- 禁止自己写代码实现
- 禁止自己修改文件
- 禁止自己执行终端命令

**架构AI唯一职责**：
- 分析用户需求（含图片识别）
- 拆解为原子任务
- 为每个任务注入完整上下文（项目路径、相关代码、规范）
- 调用 `assign_task` 分发给 Worker
- 审核 Worker 返回结果，决定通过或打回

## 架构

```
┌──────────────────────────────────────────────────────────────┐
│         架构AI (Claude Code) — 分析者 / 调度者 / 审核者       │
│                                                               │
│  ① 接收用户输入（文字 + 截图/图片）                            │
│  ② 多模态识别：用自身视觉能力分析截图，提取为文字              │
│  ③ 任务拆解：拆分为独立原子任务                                │
│  ④ 调用 assign_task 分发给 Worker（禁止自己实现）              │
│  ⑤ 审核 Worker 返回结果                                       │
└───────────────────────────┬──────────────────────────────────┘
                            │ assign_task（含 project_path + context_files）
                            │ (stdio / HTTP SSE @ 5200)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│           MCP Server Orchestrator (:5200)                     │
│             (解析 1号、2号 等协作别名)                          │
└─────┬─────────────────────┬─────────────────────┬────────────┘
      │                     │                     │
      ▼ (1号 @ :5100)       ▼ (2号 @ :5101)       ▼ (3号 @ :5102)
┌───────────┐         ┌───────────┐         ┌───────────┐
│ [权]      │         │ [权]      │         │ [权]      │
│ glm-5.1   │         │ glm-5-turb│         │ glm-5     │
│ :5100     │         │ :5101     │         │ :5102     │
│ 执行者    │         │ 执行者    │         │ 执行者    │
└─────┬─────┘         └─────┬─────┘         └─────┬─────┘
      │                     │                     │
      ▼                     ▼                     ▼
  智谱 GLM              智谱 GLM              智谱 GLM
```

## 工作流程

### 第一步：分析（架构AI）

1. **多模态识别**
   - 用户附带截图/图片时，架构AI用自身视觉能力分析
   - 提取为结构化文字描述
   - **不把图片传给 Worker**，只传文字分析结果

2. **需求拆解**
   - 将复杂需求拆为独立的原子任务
   - 每个任务目标单一、边界清晰
   - 判断任务依赖关系和执行顺序

3. **上下文收集**
   - 用 `context_files` 收集需要修改的文件路径
   - 确认 `project_path`（当前项目绝对路径）
   - 确认 `project_language`（语言/框架）

### 第二步：分发（架构AI → Worker）

调用 `assign_task` 分发任务，**所有实现工作都由 Worker 完成**：

```json
{
  "provider_id": "1号",
  "task": "在 LoginForm.tsx 的密码框下方添加'记住我'复选框...",
  "project_path": "/Users/mo/projects/my-app",
  "project_language": "TypeScript/React",
  "context_files": ["src/components/LoginForm.tsx"],
  "auto_checkpoint": true
}
```

**并行优化**：无依赖的多个任务可同时分发给不同 Worker。

### 第三步：审核（架构AI）

Worker 返回结果后，架构AI审核：
- 合格 → 架构AI将代码落地应用（这是唯一允许架构AI操作代码的时刻）
- 不合格 → 打回重做（最多 5 次）

### 图片识别降级策略

仅当架构AI自身无法识别时（极模糊、专业图表、手写体），才降级让 Worker（如 8号 Kimi）尝试。

---

## 协作别名与端口映射表

| 别名 | 供应商名称 | 默认模型 | 端口 | 擅长领域 |
|:---:|:---|:---|:---:|:---|
| **1号** | `[权] glm-5.1` | `glm-5.1` | **5100** | 复杂逻辑、算法、架构代码 |
| **2号** | `[权] glm-5-turbo` | `glm-5-turbo` | **5101** | 快速修复、简单代码、格式化 |
| **3号** | `[权] glm-5` | `glm-5` | **5102** | 常规任务、文档、测试 |
| **4号** | `[权] glm-4.7` | `glm-4.7` | **5103** | 简单问答、轻量脚本 |
| **5号** | `[权] deepseek-v4-pro[1m]` | `deepseek-v4-pro[1m]` | **5104** | 复杂推理、数学、长链逻辑 |
| **6号** | `[权] deepseek-v4-flash` | `deepseek-v4-flash` | **5105** | 极简任务、快速验证 |
| **7号** | `[权-联通] glm-5` | `glm-5` | **5106** | 3号繁忙时的替代 |
| **8号** | `[伟] kimi-for-2.6` | `kimi-for-2.6` | **5107** | 长文档、多模态降级备选 |
| **9号** | `[伟] kimi-for-2.5` | `kimi-for-2.5` | **5108** | 常规任务 |

> 用户未指定 Worker 时，**默认使用 `"1号"`**。

---

## MCP 工具列表

### bridge_status — 查看运行状态

```json
// 输入: {}
// 输出示例:
🟢 运行中  [权] glm-5.1 (export_02aaa593)  端口:5100 PID:12345
⚪ 已停止  [权] glm-5-turbo (export_47545d61)  端口:5101
```

### bridge_start — 启动桥接

```json
{ "provider_id": "1号" }
```

### bridge_stop — 停止桥接

```json
{ "provider_id": "1号" }
```

### assign_task — 分配执行任务（核心工具）

向 Worker 发送任务。**架构AI的所有实现工作都必须通过此工具完成。**

```json
{
  "provider_id": "1号",
  "task": "[架构AI已拆解好的、包含完整上下文的纯文本任务描述]",
  "project_path": "/Users/mo/Documents/mac/data/CodeIDE",
  "project_language": "Swift/SwiftUI",
  "context_files": ["Sources/Views.swift"],
  "skills": ["coding-style"],
  "model": "glm-5.1",
  "auto_checkpoint": true
}
```

| 参数 | 必填 | 说明 |
|------|:---:|------|
| `provider_id` | 是 | Worker 别名（如 `"1号"`） |
| `task` | 是 | 已分析好的纯文本任务描述 |
| `project_path` | 是 | 调用者所在项目绝对路径 |
| `project_language` | 推荐 | 语言/框架（如 `Swift/SwiftUI`） |
| `context_files` | 可选 | 相对或绝对路径，系统自动读取注入 |
| `skills` | 可选 | 技能规范文件路径 |
| `model` | 可选 | 覆盖默认模型 |
| `auto_checkpoint` | 可选 | 自动创建审核点（默认 true） |

### create_checkpoint — 手动创建审核点

```json
{ "alias": "1号", "summary": "任务摘要", "detail": "[代码或日志]" }
```

### list_checkpoints — 列出审核点

```json
{ "status": "pending", "limit": 10 }
```

### get_checkpoint_detail — 获取审核点详情

```json
{ "checkpoint_id": "..." }
```

### review_checkpoint — 审核里程碑

```json
{ "checkpoint_id": "...", "action": "approve", "feedback": "驳回原因" }
```

---

## 完整工作流示例

### 场景：用户说"登录页加个记住我复选框"

```
═══ 架构AI 分析阶段（禁止自己写代码） ═══

架构AI:
  1. 读取 LoginForm.tsx → 收集上下文
  2. 拆解任务：在密码框下方添加"记住我"复选框
  3. 选择 Worker：1号（常规 UI 任务）

═══ Worker 执行阶段 ═══

架构AI → 1号: assign_task({
  task: "在 LoginForm.tsx 的密码框下方添加'记住我'复选框。
         样式：Tailwind，与输入框左对齐，文字'记住我'，checkbox 前置。
         输出完整修改后的文件。",
  project_path: "/Users/mo/projects/my-app",
  project_language: "TypeScript/React",
  context_files: ["src/components/LoginForm.tsx"]
})

═══ 架构AI 审核阶段 ═══

1号 返回代码 → 架构AI审核：
  ✅ 组件位置正确、样式符合要求 → approve → 落地应用
```

### 场景：用户发截图说"按照这个改"

```
═══ 架构AI 分析阶段 ═══

架构AI:
  1. 视觉识别截图 → 提取为文字：
     - 蓝色主题 (#2563EB)
     - 缺少"记住我"复选框
     - 按钮不是 full width
     - 颜色不匹配

  2. 拆解为 3 个独立任务（可并行）：
     任务A → 1号：添加复选框
     任务B → 2号：按钮改 full width
     任务C → 2号：修正颜色

═══ Worker 并行执行 ═══

架构AI → 1号: assign_task({ task: "添加复选框...", context_files: [...] })
架构AI → 2号: assign_task({ task: "按钮改 w-full...", context_files: [...] })
架构AI → 2号: assign_task({ task: "颜色改 #2563EB...", context_files: [...] })

═══ 架构AI 审核阶段 ═══

逐个审核 → 全部 approve → 按顺序落地应用
```

---

## 调度规范

### 架构AI 必须遵守

1. **只分析不分发 = 失职**：分析完方向后，必须调用 `assign_task` 让 Worker 实现
2. **`project_path` 必填**：传入当前项目绝对路径
3. **`context_files` 必传**：Worker 运行在隔离环境，看不到项目文件，必须通过此参数注入
4. **`project_language` 推荐**：帮助 Worker 选择正确语法和 API
5. **默认 1 号**：用户未指定 Worker 时使用 `"1号"`

### Worker 调度规范

- Worker 是纯执行者，只接收架构AI已消化的纯文本指令
- Worker 没有修改文件能力，职责是输出完整代码或分析结果
- 由架构AI代为落地应用 Worker 返回的代码

### 审核循环

1. Worker 返回结果 → 架构AI审核
2. 不合格 → `review_checkpoint(reject)` 或重新 `assign_task` 打回
3. **同一问题最多循环 5 次**
4. 5 次仍未解决 → 停止循环，向用户汇报

---

## 技巧

1. **并行分发**：无依赖的任务同时发给不同 Worker，提升效率
2. **图片不传 Worker**：架构AI视觉识别是零成本的，传给 Worker 增加消耗且可能格式不兼容
3. **上下文越完整越好**：Worker 看不到项目，`context_files` 尽可能传全
4. **轻量审核**：用 checkpoint 机制，架构AI只看摘要，无需挂流式输出

---

## 响应规范

每次回复必须在开头标注 Worker 调度情况：

```
[Worker: 已派任务]  → 本回复涉及了 Worker 分发
[Worker: 未派任务]  → 本回复仅由架构AI自身完成（仅限纯信息查询）
```

**注意**：涉及任何代码修改、功能实现的需求，`[Worker: 未派任务]` 是违规的——必须分发。
