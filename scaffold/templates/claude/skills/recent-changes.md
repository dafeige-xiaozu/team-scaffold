---
name: "recent-changes"
description: "查看最近代码变更"
disable-model-invocation: true
---

# /recent-changes

查看最近的代码变更，帮助王重阳了解项目当前状态。

## 执行
```bash
echo "===== 最近 10 次提交 =====" && git log --oneline -10 && echo "" && echo "===== 未提交的改动 =====" && git status --short && echo "" && echo "===== 最近一次提交的详细变更 =====" && git diff HEAD~1 --stat
```
