#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRRR改进版消息发送工具
基于获取到的房间信息，使用正确的参数发送消息
"""

import requests
import json
import time
import re

class DRRRImprovedSender:
    """DRRR改进版消息发送器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://drrr.com"
        self.authorization = None
        self.room_id = None
        
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
                # 保存房间ID和授权信息
                self.room_id = room_id
                print("成功获取房间信息")
                return room_data
            else:
                print(f"获取房间信息失败: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"获取房间信息失败: {e}")
            return None
            
    def send_message_with_auth(self, message, url=None, to=None):
        """使用授权信息发送消息"""
        if not self.room_id:
            print("未获取到房间信息，请先调用get_room_info方法")
            return {'success': False, 'message': '未获取到房间信息'}
            
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
                # 检查响应内容
                try:
                    result = response.json()
                    print(f"消息发送结果: {result}")
                    
                    # 检查是否有重定向
                    if result.get('redirect') == 'lounge':
                        print("警告: 消息被重定向到休息室")
                        # 尝试使用不同的方法发送
                        return self._try_alternative_send(message, url, to)
                    else:
                        return {'success': True, 'message': '消息发送成功', 'data': result}
                except:
                    # 如果不是JSON响应，检查文本内容
                    response_text = response.text
                    print(f"响应内容: {response_text[:200]}...")
                    
                    # 检查是否包含成功标志
                    if 'ok' in response_text.lower() or 'success' in response_text.lower():
                        return {'success': True, 'message': '消息发送成功'}
                    else:
                        return {'success': False, 'message': '消息发送失败', 'response': response_text[:200]}
            else:
                print(f"消息发送失败: {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
                return {'success': False, 'message': f'消息发送失败: {response.status_code}'}
                
        except Exception as e:
            print(f"发送消息失败: {e}")
            return {'success': False, 'message': f'发送消息失败: {e}'}
            
    def _try_alternative_send(self, message, url=None, to=None):
        """尝试替代的消息发送方法"""
        try:
            print("尝试替代的消息发送方法...")
            
            # 方法1: 使用不同的端点
            alt_url = f"{self.base_url}/room/"
            post_data = {
                'message': message,
                'id': self.room_id
            }
            
            if url:
                post_data['url'] = url
            if to:
                post_data['to'] = to
                
            response = self.session.post(alt_url, data=post_data)
            print(f"替代方法响应状态: {response.status_code}")
            
            if response.status_code == 200:
                return {'success': True, 'message': '消息发送成功（替代方法）'}
            else:
                # 方法2: 尝试使用AJAX参数
                ajax_url = f"{self.base_url}/room/?ajax=1&api=json"
                response = self.session.post(ajax_url, data=post_data)
                print(f"AJAX方法响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    return {'success': True, 'message': '消息发送成功（AJAX方法）'}
                else:
                    return {'success': False, 'message': f'所有方法都失败: {response.status_code}'}
                    
        except Exception as e:
            print(f"替代方法失败: {e}")
            return {'success': False, 'message': f'替代方法失败: {e}'}
            
    def send_music_with_auth(self, title, music_url):
        """使用授权信息发送音乐"""
        if not self.room_id:
            print("未获取到房间信息，请先调用get_room_info方法")
            return {'success': False, 'message': '未获取到房间信息'}
            
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
                return {'success': True, 'message': '音乐发送成功'}
            else:
                print(f"音乐发送失败: {response.status_code}")
                print(f"响应内容: {response.text[:200]}...")
                return {'success': False, 'message': f'音乐发送失败: {response.status_code}'}
                
        except Exception as e:
            print(f"发送音乐失败: {e}")
            return {'success': False, 'message': f'发送音乐失败: {e}'}

def main():
    """主函数"""
    print("DRRR改进版消息发送工具")
    print("基于获取到的房间信息，使用正确的参数发送消息")
    
    sender = DRRRImprovedSender()
    
    try:
        # 1. 设置Cookie
        print("\n步骤1: 设置Cookie")
        cookie_string = "_ga=GA1.2.1299878145.1757816979; drrr-session-1=iq32ndq8g7ph7far3vqbjldg8m; _gid=GA1.2.713627936.1759452430; _gat=1; drrr-session-1=e7581u36sfumh61bn5hg6h179q"
        sender.set_cookie(cookie_string)
        
        # 2. 获取房间信息
        print("\n步骤2: 获取房间信息")
        room_id = "UrXoZHQCyg"
        room_info = sender.get_room_info(room_id)
        
        if room_info:
            print("成功获取房间信息")
            print(f"房间名称: {room_info.get('room', {}).get('name', 'N/A')}")
            print(f"房间描述: {room_info.get('room', {}).get('description', 'N/A')}")
            print(f"在线用户数: {len(room_info.get('room', {}).get('users', []))}")
        else:
            print("获取房间信息失败")
            return
            
        # 3. 发送测试消息
        print("\n步骤3: 发送测试消息")
        result = sender.send_message_with_auth("=== 改进版AI测试消息 ===")
        
        if result and result.get('success'):
            print("✓ 消息发送成功")
            print(f"  详细信息: {result.get('message')}")
        else:
            print("✗ 消息发送失败")
            print(f"  错误信息: {result.get('message')}")
            
        # 4. 发送带链接的消息
        print("\n步骤4: 发送带链接的消息")
        result = sender.send_message_with_auth("测试链接消息", "https://www.google.com")
        
        if result and result.get('success'):
            print("✓ 带链接消息发送成功")
            print(f"  详细信息: {result.get('message')}")
        else:
            print("✗ 带链接消息发送失败")
            print(f"  错误信息: {result.get('message')}")
            
        # 5. 发送音乐
        print("\n步骤5: 发送音乐")
        result = sender.send_music_with_auth("测试音乐", "https://example.com/test.mp3")
        
        if result and result.get('success'):
            print("✓ 音乐发送成功")
            print(f"  详细信息: {result.get('message')}")
        else:
            print("✗ 音乐发送失败")
            print(f"  错误信息: {result.get('message')}")
            
    except KeyboardInterrupt:
        print("\n接收到中断信号")
    except Exception as e:
        print(f"运行时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()