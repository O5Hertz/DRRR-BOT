#!/bin/bash
# 便捷启动脚本

cd /storage/self/primary/壹号工作区/drrr_bot_standalone_drrr机器人

case "$1" in
    start)
        echo "正在启动DRRR Bot完整系统..."
        PYTHONPATH=/data/data/com.termux/files/usr/lib/python3.12/site-packages python3 unified_launcher.py
        ;;
    stop)
        echo "正在停止DRRR Bot完整系统..."
        PYTHONPATH=/data/data/com.termux/files/usr/lib/python3.12/site-packages python3 unified_launcher.py stop
        ;;
    restart)
        echo "正在重启DRRR Bot完整系统..."
        PYTHONPATH=/data/data/com.termux/files/usr/lib/python3.12/site-packages python3 unified_launcher.py stop
        sleep 3
        PYTHONPATH=/data/data/com.termux/files/usr/lib/python3.12/site-packages python3 unified_launcher.py
        ;;
    status)
        echo "DRRR Bot系统状态:"
        echo "=================="
        ps aux | grep -E "(enhanced_ai_bot|enhanced_monitor|matrix_node)" | grep -v grep
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        echo ""
        echo "  start   启动完整系统"
        echo "  stop    停止完整系统"
        echo "  restart 重启完整系统"
        echo "  status  查看系统状态"
        ;;
esac