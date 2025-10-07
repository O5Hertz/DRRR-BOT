# 房间管理模块
import re
from typing import Dict, List, Any

class RoomManager:
    """房间管理类"""
    
    def __init__(self):
        self.admins: List[str] = []  # 管理员tripcode列表
        self.banned_users: List[str] = []  # 被封禁用户ID列表
        self.whitelist: List[str] = []  # 白名单用户tripcode列表
        self.blacklist: List[str] = []  # 黑名单用户tripcode列表
        self.welcome_messages: Dict[str, str] = {}  # 欢迎消息
        self.auto_kick_patterns: List[str] = []  # 自动踢出模式
        self.room_settings: Dict[str, Any] = {
            'allow_dm': True,
            'allow_music': True,
            'max_users': 0,  # 0表示无限制
            'room_name': '',
            'room_description': ''
        }
        
    def add_admin(self, tripcode: str):
        """添加管理员"""
        if tripcode not in self.admins:
            self.admins.append(tripcode)
            return f"已添加管理员: {tripcode}"
        else:
            return f"用户已经是管理员: {tripcode}"
            
    def remove_admin(self, tripcode: str):
        """移除管理员"""
        if tripcode in self.admins:
            self.admins.remove(tripcode)
            return f"已移除管理员: {tripcode}"
        else:
            return f"用户不是管理员: {tripcode}"
            
    def is_admin(self, tripcode: str) -> bool:
        """检查是否为管理员"""
        return tripcode in self.admins
        
    def ban_user(self, user_id: str, tripcode: str = ""):
        """封禁用户"""
        if user_id not in self.banned_users:
            self.banned_users.append(user_id)
            return f"已封禁用户: {user_id}"
        else:
            return f"用户已被封禁: {user_id}"
            
    def unban_user(self, user_id: str):
        """解封用户"""
        if user_id in self.banned_users:
            self.banned_users.remove(user_id)
            return f"已解封用户: {user_id}"
        else:
            return f"用户未被封禁: {user_id}"
            
    def is_banned(self, user_id: str) -> bool:
        """检查用户是否被封禁"""
        return user_id in self.banned_users
        
    def add_to_whitelist(self, tripcode: str):
        """添加到白名单"""
        if tripcode not in self.whitelist:
            self.whitelist.append(tripcode)
            return f"已添加到白名单: {tripcode}"
        else:
            return f"用户已在白名单中: {tripcode}"
            
    def remove_from_whitelist(self, tripcode: str):
        """从白名单移除"""
        if tripcode in self.whitelist:
            self.whitelist.remove(tripcode)
            return f"已从白名单移除: {tripcode}"
        else:
            return f"用户不在白名单中: {tripcode}"
            
    def is_whitelisted(self, tripcode: str) -> bool:
        """检查是否在白名单中"""
        return not self.whitelist or tripcode in self.whitelist  # 空白名单表示无限制
        
    def add_to_blacklist(self, tripcode: str):
        """添加到黑名单"""
        if tripcode not in self.blacklist:
            self.blacklist.append(tripcode)
            return f"已添加到黑名单: {tripcode}"
        else:
            return f"用户已在黑名单中: {tripcode}"
            
    def remove_from_blacklist(self, tripcode: str):
        """从黑名单移除"""
        if tripcode in self.blacklist:
            self.blacklist.remove(tripcode)
            return f"已从黑名单移除: {tripcode}"
        else:
            return f"用户不在黑名单中: {tripcode}"
            
    def is_blacklisted(self, tripcode: str) -> bool:
        """检查是否在黑名单中"""
        return tripcode in self.blacklist
        
    def set_welcome_message(self, pattern: str, message: str):
        """设置欢迎消息"""
        self.welcome_messages[pattern] = message
        return f"已设置欢迎消息: {pattern}"
        
    def get_welcome_message(self, user_name: str, tripcode: str = ""):
        """获取欢迎消息"""
        for pattern, message in self.welcome_messages.items():
            # 检查用户名或tripcode是否匹配模式
            if re.search(pattern, user_name, re.IGNORECASE) or \
               (tripcode and re.search(pattern, tripcode, re.IGNORECASE)):
                return message
        return None
        
    def add_auto_kick_pattern(self, pattern: str):
        """添加自动踢出模式"""
        if pattern not in self.auto_kick_patterns:
            self.auto_kick_patterns.append(pattern)
            return f"已添加自动踢出模式: {pattern}"
        else:
            return f"自动踢出模式已存在: {pattern}"
            
    def remove_auto_kick_pattern(self, pattern: str):
        """移除自动踢出模式"""
        if pattern in self.auto_kick_patterns:
            self.auto_kick_patterns.remove(pattern)
            return f"已移除自动踢出模式: {pattern}"
        else:
            return f"自动踢出模式不存在: {pattern}"
            
    def should_auto_kick(self, user_name: str, tripcode: str = ""):
        """检查是否应该自动踢出用户"""
        for pattern in self.auto_kick_patterns:
            if re.search(pattern, user_name, re.IGNORECASE) or \
               (tripcode and re.search(pattern, tripcode, re.IGNORECASE)):
                return True
        return False
        
    def set_room_setting(self, setting: str, value: Any):
        """设置房间选项"""
        if setting in self.room_settings:
            self.room_settings[setting] = value
            return f"已设置 {setting}: {value}"
        else:
            return f"无效的设置: {setting}"
            
    def get_room_setting(self, setting: str):
        """获取房间选项"""
        return self.room_settings.get(setting)
        
    def list_users(self, users: List[Dict[str, str]]):
        """列出房间用户"""
        if not users:
            return "房间为空"
            
        result = f"房间用户 ({len(users)}人):\n"
        for i, user in enumerate(users):
            user_info = user.get('name', 'Unknown')
            if user.get('tripcode'):
                user_info += f" #{user['tripcode']}"
            if user.get('device') == 'mobile':
                user_info += " 📱"
            result += f"{i+1}. {user_info}\n"
        return result.strip()