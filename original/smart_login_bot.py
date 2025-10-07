#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能登录机器人
用于在账号掉线时重新登录并进入指定房间
"""

import requests
import json
import time
import os
import sys

class SmartLoginBot:
    """智能登录机器人"""
    
    def __init__(self, config_file="login_config.json"):
        self.session = requests.Session()
        self.base_url = "https://drrr.com"
        self.config = self.load_config(config_file)
        
        # 设置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://drrr.com/',
            'DNT': '1',
            'Accept-Charset': 'utf-8'
        })
        
    def load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件 {config_file} 未找到，请创建配置文件")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"配置文件 {config_file} 格式错误")
            sys.exit(1)
            
    def set_cookie(self, cookie_string):
        """设置Cookie"""
        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
        self.session.cookies.update(cookies)
        print("Cookie设置成功")
        
    def check_login_status(self):
        """检查登录状态"""
        try:
            response = self.session.get(f"{self.base_url}/lounge?api=json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'profile' in data and data['profile']:
                    print(f"已登录账号: {data['profile'].get('name', 'Unknown')}")
                    return True
            return False
        except Exception as e:
            print(f"检查登录状态失败: {e}")
            return False
            
    def join_room(self, room_id):
        """加入房间"""
        try:
            # 首先尝试直接访问房间API
            response = self.session.get(f"{self.base_url}/room/?id={room_id}&api=json", timeout=10)
            if response.status_code == 200:
                print(f"成功加入房间: {room_id}")
                return True
            elif response.status_code == 403:
                # 需要授权加入房间
                error_data = response.json()
                if "authorization" in error_data and "id" in error_data:
                    post_data = {
                        'id': error_data['id'],
                        'authorization': error_data['authorization']
                    }
                    post_response = self.session.post(f"{self.base_url}/room/", data=post_data, timeout=10)
                    if post_response.status_code == 200:
                        print(f"成功加入房间: {room_id}")
                        return True
            return False
        except Exception as e:
            print(f"加入房间失败: {e}")
            return False
            
    def search_and_join_room(self, room_name):
        """搜索并加入房间"""
        try:
            response = self.session.get(f"{self.base_url}/lounge?api=json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                rooms = data.get('rooms', [])
                for room in rooms:
                    if room.get('name') == room_name:
                        room_id = room.get('id')
                        return self.join_room(room_id)
            return False
        except Exception as e:
            print(f"搜索房间失败: {e}")
            return False
            
    def send_message(self, message):
        """发送消息测试连接"""
        try:
            post_data = {
                'message': message,
                'id': self.config['room_id']
            }
            response = self.session.post(f"{self.base_url}/room/?ajax=1&api=json", data=post_data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
            
    def run(self):
        """运行登录机器人"""
        print("智能登录机器人启动")
        
        # 设置Cookie
        self.set_cookie(self.config['cookie'])
        
        # 检查登录状态
        if not self.check_login_status():
            print("账号未登录或Cookie已过期")
            return False
            
        # 尝试加入指定房间
        room_id = self.config['room_id']
        room_name = self.config['room_name']
        
        # 优先使用房间ID加入
        if self.join_room(room_id):
            print(f"成功加入房间 {room_name} ({room_id})")
            # 发送测试消息确认连接正常
            if self.send_message("登录机器人已上线"):
                print("连接状态正常")
                return True
        else:
            # 如果通过ID加入失败，尝试通过房间名称搜索
            print("通过房间ID加入失败，尝试通过房间名称搜索...")
            if self.search_and_join_room(room_name):
                print(f"成功通过名称加入房间 {room_name}")
                return True
                
        print("无法加入指定房间")
        return False

def main():
    """主函数"""
    bot = SmartLoginBot()
    if bot.run():
        print("智能登录成功")
        # 这里可以添加通知机制，比如发送邮件或短信通知
    else:
        print("智能登录失败")
        sys.exit(1)

if __name__ == "__main__":
    main()