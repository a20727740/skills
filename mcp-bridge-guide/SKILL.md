---
name: MCP Bridge Guide
description: 桥接管理器 MCP 使用指南 - 多供应商协作、任务分配、内部执行、外部审核
version: 1.0.0
tags: [mcp, bridge, ai, proxy, multi-provider]
---

# 桥接管理器 MCP 使用指南

## 概述

桥接管理器（Bridge Manager）是一个 macOS 状态栏应用，将多个 AI 供应商（DeepSeek、Kimi、智谱等）统一为本地 OpenAI 兼容 API。外部 AI 应用可通过 MCP 端口连接，实现**任务分配 → 内部执行 → 整理结果 → 外部审核**的完整工作流。

## 架构

```
┌─────────────────────────────────────────────────────────┐
│                    外部 AI 应用                          │
│          （架构师 / 审核者角色）                          │
│         通过 MCP 端口 5200 连接                          │
└──────────┬──────────────────────────┬───────────────────┘
           │ 分配任务                  │ 审核结果
           ▼                          │
┌──────────────────────────────────────┴──────────────────┐
│              桥接管理器 (MCP 服务)                        │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ DeepSeek    │  │ Kimi K2.6   │  │ 智谱 GLM-5  │     │
│  │ :5100       │  │ :5100       │  │ :5100       │     │
│  │ (执行者)     │  │ (审核者)     │  │ (执行者)     │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┴────────────────┘             │
│                     │                                   │
│              整理数据 & 通知外部 AI                       │
└─────────────────────────────────────────────────────────┘
```

## 工作流程

### 1. 内部执行任务
- 外部 AI 通过 MCP 端口下达任务到指定供应商
- 供应商（执行者角色）独立完成任务
- 桥接自动记录所有输入/输出到终端日志

### 2. 整理数据
- 任务完成后，桥接自动整理执行结果
- 汇总关键信息：输入摘要、输出内容、耗时、token 用量
- 生成结构化的审核报告

### 3. 通知外部 AI 审核
- 整理好的数据通过 MCP 推送给外部 AI
- 外部 AI 以审核者角色评估工作质量
- 审核结果可反馈给执行者进行修正

## 配置文件

### providers.json — 供应商配置

位于桥接目录下，定义可用的 AI 供应商：

```json
{
  "providers": [
    {
      "id": "deepseek",
      "name": "DeepSeek",
      "apiKey": "sk-xxx",
      "baseUrl": "https://api.deepseek.com",
      "defaultModel": "deepseek-v4-pro",
      "port": 5100,
      "protocol": "openai",
      "models": [
        { "id": "deepseek-v4-pro", "name": "DeepSeek V4 Pro", "description": "高性能推理模型" }
      ],
      "capabilities": {
        "thinking": true,
        "reasoningEffort": true,
        "reasoningContent": true
      }
    }
  ]
}
```

**关键字段说明：**
- `protocol`: `openai` 或 `anthropic`，决定请求转换格式
- `port`: 本地监听端口，同一供应商复用端口
- `capabilities.thinking`: 是否支持深度思考
- `capabilities.reasoningEffort`: 是否支持调节推理强度

### mcp-config.json — MCP 服务配置

```json
{
  "allowExternalReview": true,
  "isEnabled": false,
  "monitorAllIO": true,
  "port": 5200,
  "providerAssignments": [
    {
      "id": "uuid",
      "providerId": "deepseek",
      "taskRole": "worker",
      "taskDescription": "代码编写和实现",
      "isEnabled": true
    }
  ]
}
```

**角色类型：**
- `worker`（执行者）— 接收任务并执行实际工作
- `reviewer`（审核者）— 审核其他供应商的工作成果
- `architect`（架构师）— 规划任务分解和分配策略

## 本地 API 端点

每个供应商启动后，在 `127.0.0.1:{port}` 提供 OpenAI 兼容接口：

| 端点 | 说明 |
|------|------|
| `GET /v1/models` | 获取可用模型列表 |
| `POST /v1/chat/completions` | Chat Completions API（支持流式） |
| `POST /v1/responses` | Responses API（支持流式 + 工具调用） |

### 请求示例

```bash
# Chat Completions
curl http://127.0.0.1:5100/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "messages": [{"role": "user", "content": "写一个排序算法"}],
    "stream": true
  }'

# Responses API
curl http://127.0.0.1:5100/v1/responses \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-pro",
    "input": "实现二叉树遍历",
    "stream": true
  }'
```

## 使用方式

### 启动桥接

1. 点击状态栏「桥接管理」→「打开管理窗口」
2. 左侧选择供应商，右侧点击「启动」
3. 桥接在指定端口启动，终端实时显示日志

### MCP 管理

1. 底部齿轮菜单 →「MCP 管理」进入全屏管理界面
2. 配置 MCP 端口（默认 5200）
3. 添加协作任务，指定供应商和角色
4. 启动 MCP 服务

### 监控与审核

- **终端面板**：实时显示所有供应商的输入/输出
- **外部审核**：开启后外部 AI 可读取执行结果并给出评审意见
- **I/O 监控**：完整记录请求和响应，支持回溯排查

## 供应商协议差异

桥接自动处理 OpenAI 和 Anthropic 两种协议的转换：

| 特性 | OpenAI (`openai`) | Anthropic (`anthropic`) |
|------|-------------------|------------------------|
| API 格式 | Chat Completions | Messages API |
| 思考模式 | `reasoning_effort` 参数 | `thinking` 内容块 |
| 工具调用 | function calling | tool_use 内容块 |
| 流式响应 | SSE delta | SSE event blocks |

Kimi 系列供应商使用 Anthropic 协议，桥接会自动转换请求格式。

## 视觉能力

供应商配置 `visionModel` 后，桥接自动启用视觉预处理：
- 检测消息中的图片内容
- 调用视觉模型生成文字描述
- 将描述传给主模型处理
- 自动缓存已处理图片

## 导入导出

- **导出**：底部工具栏「导出配置」→ 保存为 `models.json` 兼容格式
- **导入**：支持两种格式：
  - `providers.json`：`{"providers": [...]}` 格式
  - `models.json`：模型管理器/CodeIDE 导出的纯数组格式

导入时自动分配不冲突的端口，支持「替换全部」或「合并到现有」两种模式。

## 提问与审核规范

在使用 MCP 桥接将任务下发给 Worker 供应商时，作为调度者（提问者/外部 AI），必须严格遵循以下上下文与审核规则：

### 1. 提问规范：全面上下文传递 (Context Injection)
内部 Worker 运行在隔离环境中，并不知晓外部 AI 所在的目录结构、项目背景以及当前激活的技能（Skill）。因此，在通过 `assign_task` 等方式分配任务时，**提问者（外部 AI）必须在 prompt 中完整注入以下四大要素**：

- **[必选] 绝对路径与环境**：显式提供当前项目的绝对物理路径（例如 `/Users/mo/Documents/...`）、操作系统环境、框架语言与版本信息。
- **[必选] 技能（Skill）透传**：如果外部 AI 当前正在应用某项 Skill（如 `ui-ux-pro-max`、`locale-sync` 或本项目规约），**必须将该 Skill 的核心规则甚至完整内容**作为文本附加在 Prompt 中一并发送给 Worker，以保证“干活的人”和“调度的人”遵循相同的标准和审美要求。
- **[必选] 角色与能力边界告知**：必须明确告知 Worker 它自己**没有直接修改文件或执行命令的能力**（除非独立为其配置了工具）。Worker 的职责是**输出完整的代码或分析结果**，再由提问者（外部 AI）在收到回复后去代为执行写入或运行测试。
- **[必选] 相关文件与代码**：不能仅提供文件名！必须将需要修改或参考的核心代码内容、依赖文件（如 `package.json` 等）以代码块的形式完整传给 Worker，以供其分析。
- **[可选] 额外限制与目标**：如果是写代码任务，必须告知是否有安装新依赖的允许、测试运行要求以及最终的成功验收标准。

### 2. 外部审核与循环优化规则
1. **角色定义**：外部 AI（即“提问者”或 Orchestrator）自动充当“审核者”角色。
2. **评估标准**：每次 Worker 返回执行结果或代码修改后，审核者必须仔细阅读并评估其是否完全达标（逻辑是否正确、是否符合规范）。
3. **循环打回（最多 5 次）**：如果 Worker 返回的内容未达标或有明显错误，审核者应通过 `review_checkpoint(reject)` 或者继续使用 `assign_task` 指出不足并要求 Worker 重新修改。对于同一个问题，这种打回与优化循环**最多可进行 5 次**。
4. **终止条件**：在重试 5 次后，审核者需根据效果评估是否值得继续针对当前问题进行优化；若判定效果不佳或陷入死循环，应立即停止循环，向人工汇报或改变解决策略。

---

## 文件结构

```
nodejs桥接/
├── providers.json          # 供应商配置
├── mcp-config.json         # MCP 服务配置（自动生成）
├── model-catalog.json      # 模型目录
├── universal-bridge.js     # 桥接核心（OpenAI 兼容代理）
├── vision-mcp.js           # 视觉理解 MCP Server
├── bridge.js               # 旧版桥接
├── Sources/
│   ├── BridgeManagerApp.swift    # 应用入口 + 状态栏
│   └── BridgeToolWindow.swift    # 主界面 + 设置 + MCP 管理
├── skills/
│   └── 使用桥接mcp.md      # 本文档
└── bridge-{id}.log         # 各供应商运行日志
```
