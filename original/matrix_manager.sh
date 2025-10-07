#!/bin/bash
# DRRR Bot维持矩阵系统管理脚本

case "$1" in
    start)
        echo "启动DRRR Bot维持矩阵系统..."
        cd /storage/emulated/0/壹号工作区/drrr_bot_standalone
        bash start_matrix.sh
        ;;
    stop)
        echo "停止DRRR Bot维持矩阵系统..."
        cd /storage/emulated/0/壹号工作区/drrr_bot_standalone
        bash stop_matrix.sh
        ;;
    status)
        echo "检查DRRR Bot维持矩阵系统状态..."
        echo "矩阵节点进程:"
        ps aux | grep matrix_node.py | grep -v grep
        echo ""
        echo "Bot进程:"
        ps aux | grep enhanced_ai_bot.py | grep -v grep
        echo ""
        echo "心跳文件:"
        ls -la /storage/emulated/0/壹号工作区/drrr_bot_standalone/node_*.json
        ;;
    logs)
        echo "查看矩阵节点日志..."
        echo "=== 节点A日志 ==="
        tail -10 /storage/emulated/0/壹号工作区/drrr_bot_standalone/matrix_node_A.log
        echo ""
        echo "=== 节点B日志 ==="
        tail -10 /storage/emulated/0/壹号工作区/drrr_bot_standalone/matrix_node_B.log
        echo ""
        echo "=== 节点C日志 ==="
        tail -10 /storage/emulated/0/壹号工作区/drrr_bot_standalone/matrix_node_C.log
        ;;
    bot-logs)
        echo "查看Bot日志..."
        tail -20 /storage/emulated/0/壹号工作区/drrr_bot_standalone/bot.log
        ;;
    restart-bot)
        echo "重启Bot程序..."
        cd /storage/emulated/0/壹号工作区/drrr_bot_standalone
        pkill -f enhanced_ai_bot.py
        sleep 3
        nohup python3 enhanced_ai_bot.py >> bot.log 2>&1 &
        echo "Bot程序已重启"
        ;;
    *)
        echo "用法: $0 {start|stop|status|logs|bot-logs|restart-bot}"
        echo ""
        echo "  start       启动维持矩阵系统"
        echo "  stop        停止维持矩阵系统"
        echo "  status      查看系统状态"
        echo "  logs        查看矩阵节点日志"
        echo "  bot-logs    查看Bot日志"
        echo "  restart-bot 重启Bot程序"
        exit 1
        ;;
esac