# DRRR API通信模块
import asyncio
import aiohttp
import json
from urllib.parse import urlparse
from http.cookies import SimpleCookie
from yarl import URL

class DRRRAPI:
    """DRRR API通信类"""
    
    def __init__(self):
        self.base_url = "https://drrr.com"
        self.session = None
        self.cookie_jar = None
        self.user_agent = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
        self.room_id = None
        self.room_info = None
        self.timeout = 30  # 请求超时时间（秒）
        
    async def create_session(self):
        """创建HTTP会话"""
        if not self.session:
            self.cookie_jar = aiohttp.CookieJar()
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                cookie_jar=self.cookie_jar,
                headers={
                    'User-Agent': self.user_agent,
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
                },
                timeout=timeout
            )
        return self.session
        
    async def set_cookie(self, cookie_string):
        """设置cookie"""
        if not self.session:
            await self.create_session()
            
        try:
            # 手动解析cookie字符串
            cookie = SimpleCookie()
            # 分割cookie字符串并逐个处理
            for cookie_part in cookie_string.split(';'):
                cookie_part = cookie_part.strip()
                if '=' in cookie_part:
                    key, value = cookie_part.split('=', 1)
                    cookie[key] = value
            
            # 使用正确的URL格式
            url = URL(self.base_url)
            self.cookie_jar.update_cookies(cookie, url)
        except Exception as e:
            print(f"设置cookie时出错: {e}")
        
    async def get_lounge(self):
        """获取休息室信息"""
        session = await self.create_session()
        try:
            async with session.get(f"{self.base_url}/lounge?api=json") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"获取休息室信息失败: {resp.status}")
                    return None
        except asyncio.TimeoutError:
            print("获取休息室信息超时")
            return None
        except Exception as e:
            print(f"获取休息室信息失败: {e}")
            return None
            
    async def join_room(self, room_id):
        """加入房间"""
        session = await self.create_session()
        try:
            # 首先尝试直接访问房间API
            print(f"尝试直接访问房间API: {self.base_url}/room/?id={room_id}&api=json")
            async with session.get(f"{self.base_url}/room/?id={room_id}&api=json") as resp:
                print(f"房间API响应状态: {resp.status}")
                if resp.status == 403:
                    text = await resp.text()
                    print(f"403响应内容: {text}")
                    # 解析授权信息
                    try:
                        error_data = json.loads(text)
                        if "authorization" in error_data and "id" in error_data:
                            # 使用POST请求加入房间
                            post_data = {
                                'id': error_data['id'],
                                'authorization': error_data['authorization']
                            }
                            print(f"发送加入房间POST请求，数据: {post_data}")
                            async with session.post(f"{self.base_url}/room/", data=post_data) as post_resp:
                                print(f"加入房间POST响应状态: {post_resp.status}")
                                post_text = await post_resp.text()
                                print(f"加入房间POST响应内容前200字符: {post_text[:200]}...")
                                
                                # 检查是否是重定向页面
                                if "正在加入房间" in post_text or "You are joining room" in post_text:
                                    print("检测到房间加入页面，可能需要等待重定向完成")
                                    # 等待服务器处理并重定向
                                    await asyncio.sleep(3)
                        else:
                            return {"success": False, "message": "缺少授权信息"}
                    except json.JSONDecodeError:
                        return {"success": False, "message": "解析授权信息失败: 无效的JSON格式"}
                    except Exception as e:
                        return {"success": False, "message": f"解析授权信息时出错: {e}"}
                elif resp.status != 200:
                    return {"success": False, "message": f"访问房间API失败: {resp.status}"}
            
            # 多次尝试获取房间信息
            for attempt in range(3):
                await asyncio.sleep(2)  # 等待服务器处理
                print(f"第{attempt+1}次尝试获取房间信息...")
                room_info = await self.get_room_info(room_id)
                if room_info:
                    self.room_id = room_id
                    self.room_info = room_info
                    return {"success": True, "message": "成功加入房间"}
                else:
                    print(f"第{attempt+1}次尝试获取房间信息失败")
            
            # 如果还是失败，尝试不带ID的API调用
            print("尝试不带ID的房间API调用...")
            async with session.get(f"{self.base_url}/room/?api=json") as resp:
                print(f"不带ID的房间API响应状态: {resp.status}")
                if resp.status == 200:
                    try:
                        data = await resp.json()
                        self.room_id = room_id
                        self.room_info = data
                        return {"success": True, "message": "成功加入房间"}
                    except Exception as e:
                        print(f"解析房间信息失败: {e}")
                else:
                    text = await resp.text()
                    print(f"不带ID的房间API响应内容: {text[:100]}...")
            
            return {"success": False, "message": "加入房间失败: 无法获取房间信息"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "加入房间超时"}
        except Exception as e:
            return {"success": False, "message": f"加入房间时出错: {e}"}
            
    async def send_message(self, message, url=None, to=None):
        """发送消息"""
        session = await self.create_session()
        try:
            message_data = {'message': message}
            if url:
                message_data['url'] = url
            if to:
                message_data['to'] = to
                
            print(f"发送消息请求数据: {message_data}")
                
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=message_data) as resp:
                print(f"消息发送响应状态: {resp.status}")
                if resp.status == 200:
                    response_text = await resp.text()
                    print(f"消息发送响应内容: {response_text}")
                    # 检查是否被重定向到休息室
                    try:
                        response_data = json.loads(response_text)
                        if response_data.get("redirect") == "lounge":
                            print("警告: 消息发送被重定向到休息室，可能未真正发送到房间")
                            return {"success": True, "message": "消息发送成功（但可能被重定向）"}
                        else:
                            return {"success": True, "message": "消息发送成功"}
                    except json.JSONDecodeError:
                        # 如果不是JSON，可能是HTML页面
                        if "lounge" in response_text or "休息室" in response_text:
                            print("警告: 消息发送返回了休息室页面，可能未真正发送到房间")
                            return {"success": True, "message": "消息发送成功（但可能被重定向到休息室）"}
                        else:
                            return {"success": True, "message": "消息发送成功"}
                else:
                    response_text = await resp.text()
                    print(f"消息发送响应内容: {response_text}")
                    return {"success": False, "message": f"消息发送失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "消息发送超时"}
        except Exception as e:
            return {"success": False, "message": f"发送消息时出错: {e}"}
            
    async def send_music(self, title, url):
        """发送音乐"""
        session = await self.create_session()
        try:
            music_data = {
                'music': 'music',
                'name': title,
                'url': url
            }
                
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=music_data) as resp:
                if resp.status == 200:
                    return {"success": True, "message": "音乐发送成功"}
                else:
                    return {"success": False, "message": f"音乐发送失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "音乐发送超时"}
        except Exception as e:
            return {"success": False, "message": f"发送音乐时出错: {e}"}
            
    async def get_room_info(self, room_id=None):
        """获取房间信息"""
        session = await self.create_session()
        try:
            # 如果提供了房间ID，使用带ID的URL
            if room_id:
                url = f"{self.base_url}/room/?id={room_id}&api=json"
            else:
                url = f"{self.base_url}/room/?api=json"
                
            print(f"获取房间信息URL: {url}")
            async with session.get(url) as resp:
                print(f"获取房间信息响应状态: {resp.status}")
                if resp.status == 200:
                    text = await resp.text()
                    print(f"获取房间信息响应内容: {text[:200]}...")
                    try:
                        data = json.loads(text)
                        self.room_info = data
                        return data
                    except json.JSONDecodeError as e:
                        print(f"解析房间信息JSON失败: {e}")
                        return None
                else:
                    text = await resp.text()
                    print(f"获取房间信息失败: {resp.status}, 响应内容: {text[:100]}...")
                    return None
        except asyncio.TimeoutError:
            print("获取房间信息超时")
            return None
        except Exception as e:
            print(f"获取房间信息失败: {e}")
            return None
            
    async def leave_room(self):
        """离开房间"""
        session = await self.create_session()
        try:
            leave_data = {'leave': 'leave'}
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=leave_data) as resp:
                if resp.status == 200:
                    self.room_id = None
                    self.room_info = None
                    return {"success": True, "message": "成功离开房间"}
                else:
                    return {"success": False, "message": f"离开房间失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "离开房间超时"}
        except Exception as e:
            return {"success": False, "message": f"离开房间时出错: {e}"}
            
    async def kick_user(self, user_id):
        """踢出用户"""
        session = await self.create_session()
        try:
            kick_data = {'kick': user_id}
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=kick_data) as resp:
                if resp.status == 200:
                    return {"success": True, "message": "用户已踢出"}
                else:
                    return {"success": False, "message": f"踢出用户失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "踢出用户超时"}
        except Exception as e:
            return {"success": False, "message": f"踢出用户时出错: {e}"}
            
    async def ban_user(self, user_id):
        """封禁用户"""
        session = await self.create_session()
        try:
            ban_data = {'ban': user_id}
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=ban_data) as resp:
                if resp.status == 200:
                    return {"success": True, "message": "用户已封禁"}
                else:
                    return {"success": False, "message": f"封禁用户失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "封禁用户超时"}
        except Exception as e:
            return {"success": False, "message": f"封禁用户时出错: {e}"}
            
    async def unban_user(self, user_id, user_name):
        """解封用户"""
        session = await self.create_session()
        try:
            unban_data = {
                'unban': user_id,
                'userName': user_name
            }
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=unban_data) as resp:
                if resp.status == 200:
                    return {"success": True, "message": "用户已解封"}
                else:
                    return {"success": False, "message": f"解封用户失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "解封用户超时"}
        except Exception as e:
            return {"success": False, "message": f"解封用户时出错: {e}"}
            
    async def set_host(self, user_id):
        """转让房主"""
        session = await self.create_session()
        try:
            host_data = {'new_host': user_id}
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=host_data) as resp:
                if resp.status == 200:
                    return {"success": True, "message": "房主已转让"}
                else:
                    return {"success": False, "message": f"转让房主失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "转让房主超时"}
        except Exception as e:
            return {"success": False, "message": f"转让房主时出错: {e}"}
            
    async def set_dj_mode(self, is_dj_mode):
        """设置DJ模式"""
        session = await self.create_session()
        try:
            dj_data = {'dj_mode': str(is_dj_mode).lower()}
            async with session.post(f"{self.base_url}/room/?ajax=1&api=json", data=dj_data) as resp:
                if resp.status == 200:
                    return {"success": True, "message": "DJ模式已设置"}
                else:
                    return {"success": False, "message": f"设置DJ模式失败: {resp.status}"}
        except asyncio.TimeoutError:
            return {"success": False, "message": "设置DJ模式超时"}
        except Exception as e:
            return {"success": False, "message": f"设置DJ模式时出错: {e}"}
            
    async def close(self):
        """关闭会话"""
        if self.session:
            try:
                await self.session.close()
            except Exception as e:
                print(f"关闭会话时出错: {e}")
            self.session = None