# WebSocket连接模块
import asyncio
import json
import time
from typing import Callable, Dict, Any
import websockets
from urllib.parse import urlparse

class DRRRWebSocketClient:
    """DRRR WebSocket客户端"""
    
    def __init__(self, base_url: str = "https://drrr.com"):
        self.base_url = base_url
        self.websocket = None
        self.message_handlers: Dict[str, Callable] = {}
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # seconds
        self.should_reconnect = True
        self.cookie_string = None
        self.room_id = None
        
    def register_message_handler(self, message_type: str, handler: Callable):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
        
    async def connect(self, cookie_string: str = None, room_id: str = None):
        """连接WebSocket"""
        self.cookie_string = cookie_string
        self.room_id = room_id
        self.should_reconnect = True
        
        while self.should_reconnect and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                # 构建WebSocket URL
                # DRRR使用长轮询而不是WebSocket，所以我们需要模拟浏览器的行为
                # 这里我们暂时禁用WebSocket连接，改为使用API轮询
                print("DRRR平台不支持标准WebSocket，使用API轮询替代")
                return
                
                # 如果平台确实支持WebSocket，URL可能如下：
                # ws_url = self.base_url.replace("http://", "ws://").replace("https://", "wss://")
                # if self.room_id:
                #     ws_url += f"/ws/room/{self.room_id}"
                # else:
                #     ws_url += "/ws"
                    
                # print(f"尝试连接WebSocket: {ws_url}")
                
                # headers = {}
                # if self.cookie_string:
                #     headers["Cookie"] = self.cookie_string
                    
                # # 设置连接超时
                # self.websocket = await websockets.connect(
                #     ws_url,
                #     extra_headers=headers,
                #     timeout=10
                # )
                
                self.is_connected = True
                self.reconnect_attempts = 0
                print("WebSocket连接成功")
                
                # 开始监听消息
                await self._listen()
                
            except asyncio.TimeoutError:
                print("WebSocket连接超时")
                await self._reconnect()
            except websockets.exceptions.InvalidStatusCode as e:
                print(f"WebSocket连接状态码错误: {e}")
                await self._reconnect()
            except websockets.exceptions.InvalidHandshake as e:
                print(f"WebSocket握手失败: {e}")
                await self._reconnect()
            except Exception as e:
                print(f"WebSocket连接失败: {e}")
                await self._reconnect()
                
    async def _listen(self):
        """监听WebSocket消息"""
        try:
            while self.is_connected and self.websocket and self.should_reconnect:
                try:
                    # 设置接收超时
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=30.0)
                    await self._handle_message(message)
                except asyncio.TimeoutError:
                    # 心跳检测或保持连接
                    print("WebSocket接收超时，发送心跳")
                    await self._send_heartbeat()
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket连接已关闭")
            await self._reconnect()
        except Exception as e:
            print(f"WebSocket监听出错: {e}")
            await self._reconnect()
            
    async def _send_heartbeat(self):
        """发送心跳包"""
        try:
            if self.websocket and self.is_connected:
                # 发送心跳消息（根据实际API调整）
                heartbeat_msg = json.dumps({"type": "ping"})
                await self.websocket.send(heartbeat_msg)
        except Exception as e:
            print(f"发送心跳包失败: {e}")
            
    async def _handle_message(self, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            message_type = data.get("type", "unknown")
            
            # 调用相应的消息处理器
            if message_type in self.message_handlers:
                await self.message_handlers[message_type](data)
            else:
                # 默认处理程序
                await self._default_message_handler(data)
                
        except json.JSONDecodeError:
            print(f"无法解析JSON消息: {message}")
        except Exception as e:
            print(f"处理消息时出错: {e}")
            
    async def _default_message_handler(self, data: Dict[str, Any]):
        """默认消息处理器"""
        print(f"收到消息: {data}")
        
    async def _reconnect(self):
        """重新连接"""
        if not self.should_reconnect:
            return
            
        self.is_connected = False
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            print("达到最大重连次数，停止重连")
            return
            
        print(f"尝试重新连接 ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
        await asyncio.sleep(self.reconnect_delay)
        
        # 重新连接
        # 注意：这里会重新调用connect方法
        
    async def send_message(self, message: str):
        """发送消息"""
        if self.websocket and self.is_connected:
            try:
                await self.websocket.send(message)
                return True
            except Exception as e:
                print(f"发送消息失败: {e}")
                return False
        else:
            print("WebSocket未连接")
            return False
            
    async def close(self):
        """关闭连接"""
        self.should_reconnect = False
        self.is_connected = False
        if self.websocket:
            try:
                await self.websocket.close()
            except Exception as e:
                print(f"关闭WebSocket时出错: {e}")
            self.websocket = None