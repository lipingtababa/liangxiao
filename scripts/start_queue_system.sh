#!/bin/bash

# 队列系统启动脚本

echo "启动队列管理系统..."

# 检查依赖
echo "检查依赖..."

# 检查Redis
if ! command -v redis-cli &> /dev/null; then
    echo "错误: Redis未安装"
    echo "请运行: brew install redis (macOS) 或 apt-get install redis-server (Linux)"
    exit 1
fi

# 检查PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "错误: PostgreSQL未安装"
    echo "请运行: brew install postgresql (macOS) 或 apt-get install postgresql (Linux)"
    exit 1
fi

# 启动Redis
echo "启动Redis..."
if ! pgrep -x "redis-server" > /dev/null; then
    redis-server --daemonize yes
    echo "Redis已启动"
else
    echo "Redis已在运行"
fi

# 创建数据库（如果不存在）
echo "初始化数据库..."
python -c "
from scripts.queue.models import DatabaseManager
DatabaseManager.create_tables()
print('数据库表已创建')
"

# 启动Celery Worker
echo "启动Celery Worker..."

# 启动高优先级Worker
celery -A scripts.queue.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --hostname=worker-high@%h \
    --queues=high_priority \
    --pool=prefork \
    --logfile=logs/celery-high.log \
    --detach &

# 启动中优先级Worker
celery -A scripts.queue.celery_app worker \
    --loglevel=info \
    --concurrency=8 \
    --hostname=worker-medium@%h \
    --queues=medium_priority \
    --pool=prefork \
    --logfile=logs/celery-medium.log \
    --detach &

# 启动低优先级Worker
celery -A scripts.queue.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --hostname=worker-low@%h \
    --queues=low_priority \
    --pool=prefork \
    --logfile=logs/celery-low.log \
    --detach &

# 启动调度Worker
celery -A scripts.queue.celery_app worker \
    --loglevel=info \
    --concurrency=2 \
    --hostname=worker-scheduled@%h \
    --queues=scheduled \
    --pool=prefork \
    --logfile=logs/celery-scheduled.log \
    --detach &

echo "Celery Workers已启动"

# 启动Celery Beat（调度器）
echo "启动Celery Beat..."
celery -A scripts.queue.celery_app beat \
    --loglevel=info \
    --logfile=logs/celery-beat.log \
    --detach &

echo "Celery Beat已启动"

# 启动Flower（监控界面）
if [ "$1" != "--no-flower" ]; then
    echo "启动Flower监控界面..."
    celery -A scripts.queue.celery_app flower \
        --port=5555 \
        --basic_auth=admin:password \
        --logfile=logs/flower.log \
        --detach &
    echo "Flower已启动，访问: http://localhost:5555"
fi

# 启动调度器
echo "启动文章调度器..."
python -c "
from scripts.queue.scheduler import get_scheduler
scheduler = get_scheduler()
scheduler.start()
print('调度器已启动')
" &

echo ""
echo "队列管理系统启动完成!"
echo ""
echo "管理命令:"
echo "  查看状态: python scripts/queue/manager.py status"
echo "  提交任务: python scripts/queue/manager.py submit <url>"
echo "  查看健康: python scripts/queue/manager.py health"
echo ""
echo "监控界面:"
echo "  Flower: http://localhost:5555 (用户名: admin, 密码: password)"
echo ""
echo "日志文件:"
echo "  logs/celery-*.log"
echo ""