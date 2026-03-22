"""
{{project_name}} — Celery Worker
"""
import os

from celery import Celery

broker_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("worker", broker=broker_url, backend=broker_url)

app.conf.update(
    task_soft_time_limit=7200,   # 踩坑清单第 4 条
    task_time_limit=7500,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


@app.task
def example_task(name: str) -> str:
    """示例任务 — 实际开发时替换为真正的异步任务。"""
    return f"Hello {name}"
