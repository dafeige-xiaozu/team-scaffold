---
description: "踩坑 Top 10 — 全局常驻加载，避免重复踩坑"
globs: "**"
---

# 踩坑 Top 10

1. **deploy.sh 禁止 --no-cache** — 3 分钟变 22 分钟
2. **requirements.txt 禁止手动编辑** — 用 pip freeze 生成
3. **presigned URL 有效期至少 6 小时** — 大文件+排队会超时
4. **Celery soft_time_limit 至少 7200s** — 大文件处理需要时间
5. **docker-compose 必须 stop_grace_period** — 防止强杀丢任务
6. **API 时间一律 UTC+Z** — 前端转本地时间
7. **部署后必须 md5 校验** — 确认文件同步一致
8. **pip/npm 配国内镜像** — pip.conf + .npmrc
9. **.env 必须有 .env.example** — 新人能快速配置
10. **改接口必须先更新契约文档** — contracts/CONTRACTS.md
