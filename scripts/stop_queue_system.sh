#!/bin/bash

# 队列系统停止脚本

echo "停止队列管理系统..."

# 停止Celery Workers
echo "停止Celery Workers..."
pkill -f "celery.*worker"

# 停止Celery Beat
echo "停止Celery Beat..."
pkill -f "celery.*beat"

# 停止Flower
echo "停止Flower..."
pkill -f "celery.*flower"

# 停止调度器
echo "停止调度器..."
pkill -f "scheduler.start"

# 可选：停止Redis
read -p "是否停止Redis? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "停止Redis..."
    redis-cli shutdown
fi

echo ""
echo "队列管理系统已停止"