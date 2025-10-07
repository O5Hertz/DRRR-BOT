#!/bin/bash
# 增强版Bot监控脚本

BOT_DIR="/storage/self/primary/壹号工作区/drrr_bot_standalone_drrr机器人"
BOT_SCRIPT="enhanced_ai_bot.py"
LOGIN_SCRIPT="smart_login_bot.py"
DECISION_SCRIPT="intelligent_decision.py"
MONITOR_LOG="$BOT_DIR/monitor.log"
CHECK_INTERVAL=30  # 检查间隔(秒)

# 记录日志函数
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$MONITOR_LOG"
}

# 检查Bot进程是否运行
is_bot_running() {
    pgrep -f "$BOT_SCRIPT" > /dev/null
    return $?
}

# 启动Bot
start_bot() {
    cd "$BOT_DIR"
    nohup PYTHONPATH=/data/data/com.termux/files/usr/lib/python3.12/site-packages python3 "$BOT_SCRIPT" >> "$BOT_DIR/bot.log" 2>&1 &
    BOT_PID=$!
    log_message "Bot已启动，PID: $BOT_PID"
    echo $BOT_PID > "$BOT_DIR/bot.pid"
}

log_message "增强版Bot监控脚本已启动"

# 主循环
while true; do
    log_message "执行智能决策检查..."
    
    # 运行智能决策脚本
    cd "$BOT_DIR"
    python3 "$DECISION_SCRIPT"
    
    # 确保Bot进程在运行
    if ! is_bot_running; then
        log_message "检测到Bot未运行，正在启动..."
        start_bot
    fi
    
    sleep $CHECK_INTERVAL
done