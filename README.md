# team-scaffold

大飞哥无敌战队 — 项目协作框架生成器 v5.0.0

仓库地址：https://github.com/dafeige-xiaozu/team-scaffold

## 安装

```bash
pip install -e .
```

## 用法

```bash
# 交互模式
cd ~/Projects/新项目目录
scaffold init

# 非交互模式
scaffold init --project-name "我的项目" --desc "一句话描述"

# 预览不写入
scaffold init --dry-run --project-name "我的项目" --desc "一句话描述"

# 覆盖已有文件
scaffold init --force --project-name "我的项目" --desc "一句话描述"

# 包含硬件端 + 指定服务器
scaffold init --project-name "我的项目" --desc "一句话描述" --hardware --server 10.0.1.100

# 指定输出目录
scaffold init --project-name "我的项目" --desc "一句话描述" --output-dir /tmp/my-project

# 查看版本
scaffold version
```

## 开发

```bash
pip install -e .
pytest tests/
```
