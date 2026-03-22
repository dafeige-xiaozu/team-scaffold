FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app

# 拷贝国内镜像配置
COPY pip.conf /etc/pip.conf

# 只拷贝 backend 的依赖文件
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 只拷贝 backend 代码（不会包含 frontend/、.git/ 等）
COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
