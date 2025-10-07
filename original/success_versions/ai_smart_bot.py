#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRRR AI智能机器人
基于AI的智能交互机器人，能够自动加入房间并发送消息
"""

import requests
import json
import time
import re
import random

class DRRRAISmartBot:
    """DRRR AI智能机器人"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://drrr.com"
        self.room_id = None
        self.room_info = None
        self.user_profile = None
        
        # 设置请求头，模拟真实浏览器
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
        
    def set_cookie(self, cookie_string):
        """设置Cookie"""
        # 解析并设置Cookie
        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
        self.session.cookies.update(cookies)
        print("Cookie设置成功")
        
    def join_room(self, room_id):
        """加入房间"""
        try:
            self.room_id = room_id
            
            # 首先获取房间信息
            room_info = self.get_room_info(room_id)
            if not room_info:
                print("无法获取房间信息")
                return False
                
            print(f"成功加入房间: {room_info.get('room', {}).get('name', 'N/A')}")
            return True
            
        except Exception as e:
            print(f"加入房间失败: {e}")
            return False
            
    def get_room_info(self, room_id):
        """获取房间信息"""
        try:
            # 获取房间信息
            room_url = f"{self.base_url}/room/?id={room_id}&api=json"
            print(f"正在获取房间信息: {room_url}")
            
            response = self.session.get(room_url)
            print(f"房间信息响应状态: {response.status_code}")
            
            if response.status_code == 200:
                room_data = response.json()
                # 保存房间信息
                self.room_info = room_data.get('room', {})
                self.user_profile = room_data.get('profile', {})
                print("成功获取房间信息")
                return room_data
            else:
                print(f"获取房间信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"获取房间信息失败: {e}")
            return None
            
    def send_message(self, message, url=None, to=None):
        """发送消息"""
        if not self.room_id:
            print("未加入房间，请先调用join_room方法")
            return False
            
        try:
            # 使用正确的API端点发送消息
            post_url = f"{self.base_url}/room/?ajax=1"
            print(f"发送消息到: {post_url}")
            
            # 构造POST数据
            post_data = {
                'message': message,
                'id': self.room_id
            }
            
            if url:
                post_data['url'] = url
            if to:
                post_data['to'] = to
                
            print(f"POST数据: {post_data}")
            
            response = self.session.post(post_url, data=post_data)
            print(f"消息发送响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print(f"消息发送成功: {message}")
                return True
            else:
                print(f"消息发送失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"发送消息失败: {e}")
            return False
            
    def send_music(self, title, music_url):
        """发送音乐"""
        if not self.room_id:
            print("未加入房间，请先调用join_room方法")
            return False
            
        try:
            # 使用正确的API端点发送音乐
            post_url = f"{self.base_url}/room/?ajax=1"
            print(f"发送音乐到: {post_url}")
            
            # 构造POST数据
            post_data = {
                'music': 'music',
                'name': title,
                'url': music_url,
                'id': self.room_id
            }
                
            print(f"POST数据: {post_data}")
            
            response = self.session.post(post_url, data=post_data)
            print(f"音乐发送响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print(f"音乐发送成功: {title}")
                return True
            else:
                print(f"音乐发送失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"发送音乐失败: {e}")
            return False
            
    def send_smart_message(self, content):
        """发送智能消息（根据内容类型自动选择发送方式）"""
        if not self.room_id:
            print("未加入房间，请先调用join_room方法")
            return False
            
        try:
            # 检查内容是否包含音乐链接
            music_patterns = [
                r'(https?://.*\.(mp3|wav|flac|m4a|aac))',
                r'(music\.apple\.com)',
                r'(spotify\.com)',
                r'(youtube\.com/watch)',
                r'(youtu\.be)'
            ]
            
            for pattern in music_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # 提取音乐标题和URL
                    url_match = re.search(r'https?://[^\s]+', content)
                    if url_match:
                        music_url = url_match.group(0)
                        title = content.replace(music_url, '').strip() or "分享的音乐"
                        return self.send_music(title, music_url)
            
            # 检查是否包含普通链接
            url_patterns = [
                r'https?://[^\s]+',
                r'www\.[^\s]+'
            ]
            
            for pattern in url_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    # 提取URL
                    url_match = re.search(r'https?://[^\s]+|www\.[^\s]+', content)
                    if url_match:
                        url = url_match.group(0)
                        # 如果URL前面有文字，则作为消息发送
                        message = content.replace(url, '').strip()
                        if message:
                            return self.send_message(message, url)
                        else:
                            return self.send_message("分享链接", url)
            
            # 普通消息
            return self.send_message(content)
            
        except Exception as e:
            print(f"发送智能消息失败: {e}")
            return False
            
    def send_random_greeting(self):
        """发送随机问候语"""
        greetings = [
            "大家好！我是AI机器人，很高兴加入这个房间！",
            "Hello everyone! 我是一个AI助手，希望能和大家愉快交流！",
            "こんにちは！AIボットです。よろしくお願いします！",
            "机器人报道！请大家多多关照~",
            "AI智能体已上线，随时准备为大家服务！"
        ]
        
        greeting = random.choice(greetings)
        return self.send_message(greeting)
        
    def send_random_emoji(self):
        """发送随机表情"""
        emojis = [
            "😊", "😂", "😍", "🥰", "😎", 
            "🤩", "🥳", "🤗", "🤔", "🙄",
            "👍", "👏", "🙌", "🎉", "✨"
        ]
        
        emoji = random.choice(emojis)
        return self.send_message(emoji)
        
    def monitor_room(self, duration=60):
        """监控房间活动（简化版）"""
        print(f"开始监控房间活动 {duration} 秒...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            try:
                # 获取最新的房间信息
                room_info = self.get_room_info(self.room_id)
                if room_info:
                    # 检查是否有新用户加入
                    users = room_info.get('room', {}).get('users', [])
                    print(f"当前在线用户数: {len(users)}")
                    
                    # 检查是否有新消息（简化版）
                    talks = room_info.get('room', {}).get('talks', [])
                    if talks:
                        latest_message = talks[-1] if talks else None
                        if latest_message and latest_message.get('type') == 'message':
                            user_name = latest_message.get('from', {}).get('name', 'Unknown')
                            message_text = latest_message.get('message', '')
                            print(f"最新消息: [{user_name}]: {message_text}")
                            
                time.sleep(5)  # 每5秒检查一次
                
            except Exception as e:
                print(f"监控房间时出错: {e}")
                time.sleep(5)
                
        print("房间监控结束")

def main():
    """主函数"""
    print("DRRR AI智能机器人")
    print("基于AI的智能交互机器人，能够自动加入房间并发送消息")
    
    bot = DRRRAISmartBot()
    
    try:
        # 1. 设置Cookie
        print("\n步骤1: 设置Cookie")
        cookie_string = "_ga=GA1.2.1299878145.1757816979; drrr-session-1=iq32ndq8g7ph7far3vqbjldg8m; _gid=GA1.2.713627936.1759452430; _gat=1; drrr-session-1=e7581u36sfumh61bn5hg6h179q"
        bot.set_cookie(cookie_string)
        
        # 2. 加入房间
        print("\n步骤2: 加入房间")
        room_id = "UrXoZHQCyg"
        if bot.join_room(room_id):
            print("成功加入房间")
        else:
            print("加入房间失败")
            return
            
        # 3. 发送欢迎消息
        print("\n步骤3: 发送欢迎消息")
        if bot.send_random_greeting():
            print("✓ 欢迎消息发送成功")
        else:
            print("✗ 欢迎消息发送失败")
            
        # 4. 发送智能消息测试
        print("\n步骤4: 发送智能消息测试")
        test_messages = [
            "这是一个普通的测试消息",
            "请查看这个链接 https://www.google.com",
            "分享一首音乐 https://example.com/song.mp3",
            "你好世界！😊",
            "今天的天气真不错呢"
        ]
        
        for message in test_messages:
            print(f"\n发送: {message}")
            if bot.send_smart_message(message):
                print("✓ 消息发送成功")
            else:
                print("✗ 消息发送失败")
            time.sleep(2)  # 避免发送过快
            
        # 5. 发送随机表情
        print("\n步骤5: 发送随机表情")
        if bot.send_random_emoji():
            print("✓ 表情发送成功")
        else:
            print("✗ 表情发送失败")
            
        # 6. 监控房间活动
        print("\n步骤6: 监控房间活动")
        bot.monitor_room(30)  # 监控30秒
            
        print("\nAI智能机器人任务完成！")
        
    except KeyboardInterrupt:
        print("\n接收到中断信号")
    except Exception as e:
        print(f"运行时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()