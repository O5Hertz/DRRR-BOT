# 事件处理模块
import re
import json
from typing import Dict, List, Callable, Any

class EventHandler:
    """事件处理类"""
    
    def __init__(self):
        self.event_handlers: Dict[str, List[Callable]] = {
            'join': [],
            'leave': [],
            'message': [],
            'dm': [],
            'music': [],
            'new_host': []
        }
        self.command_handlers: Dict[str, Callable] = {}
        self.regex_handlers: List[tuple] = []  # (pattern, handler)
        
    def register_event_handler(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            
    def register_command_handler(self, command: str, handler: Callable):
        """注册命令处理器"""
        self.command_handlers[command.lower()] = handler
        
    def register_regex_handler(self, pattern: str, handler: Callable):
        """注册正则表达式处理器"""
        self.regex_handlers.append((re.compile(pattern), handler))
        
    async def handle_event(self, event_type: str, data: Dict[str, Any]):
        """处理事件"""
        # 处理事件处理器
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(data)
                except Exception as e:
                    print(f"事件处理器出错: {e}")
                    
    async def handle_message(self, message: str, user: Dict[str, Any]):
        """处理消息"""
        # 检查是否为命令
        if message.startswith('/'):
            await self.handle_command(message, user)
        else:
            # 检查正则表达式处理器
            for pattern, handler in self.regex_handlers:
                match = pattern.match(message)
                if match:
                    try:
                        await handler(message, user, match)
                    except Exception as e:
                        print(f"正则表达式处理器出错: {e}")
                        
    async def handle_command(self, command: str, user: Dict[str, Any]):
        """处理命令"""
        command_parts = command[1:].split()
        if not command_parts:
            return
            
        cmd = command_parts[0].lower()
        args = command_parts[1:] if len(command_parts) > 1 else []
        
        # 查找命令处理器
        if cmd in self.command_handlers:
            try:
                await self.command_handlers[cmd](cmd, args, user)
            except Exception as e:
                print(f"命令处理器出错: {e}")