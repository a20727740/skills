---
name: chinese-preferences
description: 中文偏好设置：默认使用中文回答，简洁的Markdown格式，MacOS系统，代码添加函数级注释
---

这个技能设置了以下开发偏好：

1. 默认使用中文回答
2. 回答时尽可能简洁、圆洁，无特别说明时优先使用Markdown格式
3. 系统环境为 MacOS
4. 生成代码时添加函数级注释
5. 进入项目先查看是否有 `.md` 格式的文档（如 README.md），通常是项目结构介绍，阅读后再根据需求处理
6. 在 `.vue` 文件中添加 console.log 打印时，必须用 `JSON.stringify()` 包裹对象，例如：`console.log('文件信息获取成功:', JSON.stringify(fileInfo));`

## 使用说明

加载此技能后，所有回答将遵循中文偏好设置，适合中文用户使用。
