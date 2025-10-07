# 工具函数模块
import re

def validate_room_id(room_id):
    """验证房间ID格式"""
    return re.match(r'^[a-zA-Z0-9]+$', room_id) is not None

def format_message(message):
    """格式化消息"""
    return message.strip()

def is_command(message):
    """检查是否为命令"""
    return message.startswith('/')

def truncate_message(message, max_length=140):
    """截断消息到指定长度"""
    if len(message) <= max_length:
        return message
    else:
        return message[:max_length-3] + "..."

def is_valid_guess(guess):
    """验证猜数字输入"""
    return (len(guess) == 4 and 
            guess.isdigit() and 
            len(set(guess)) == 4)