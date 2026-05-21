---
name: html-output
description: Use lightweight HTML only when complex information needs higher density, faster scanning, or visual structure.
---

# HTML Output Skill

## 核心原则

复杂内容优先使用 HTML，而不是长篇 Markdown。

目标：

- 提高信息密度
- 降低阅读疲劳
- 提高扫描与决策效率

优先使用：

- 对比表格
- 并排卡片
- 状态面板
- 流程图
- 架构图
- 分栏布局

避免：

- 大段连续文字
- 超长 Markdown
- 重复解释

## 内容优先，保持极简

HTML 的目标是提高沟通效率，不是做网页设计。

生成 HTML 时：

- 使用原生 HTML
- 使用简单 CSS
- 使用朴素 SVG
- 使用系统字体
- 使用极简布局

禁止：

- 花哨动画
- 炫技样式
- 重 UI 设计
- 无意义装饰

原则：内容第一，样式服务阅读效率。

## 什么时候使用 HTML

简单问题直接命令行回答。

以下情况才使用 HTML：

- 包含多个表格、章节或多层级内容
- 同时包含现状、改动、测试、风险、下一步等多维信息
- 存在多个待决策方案
- 涉及流程、架构、模块关系、数据流等空间信息
- 纯文字已经难以快速理解

## 技术规范

优先：

- 单文件 HTML
- 简单 CSS
- 内联 SVG

避免：

- React / Vue
- Tailwind CDN
- 重型依赖
- 复杂构建

## 一句话原则

信息密度优先。  
内容优先。  
能不用 HTML 就不用。  
一旦用了，就让复杂信息变得可扫描、可定位、可决策。