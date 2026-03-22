---
name: "decision"
description: "记录新决策"
disable-model-invocation: true
---

# /decision

记录一条新的架构/技术决策。

## 执行
用户提供标题和提议人后执行：
```bash
python scripts/state_cli.py decision-propose --title "决策标题" --proposed-by "角色名"
```
