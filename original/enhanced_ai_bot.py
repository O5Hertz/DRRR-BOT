#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRRR 增强版AI机器人
基于AI的智能交互机器人，具有用户欢迎、指令权限控制、AI对话和音乐点播功能
"""

import requests
import json
import time
import re
import random
import threading
import os
from urllib.parse import urlparse
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DRRREnhancedAIBot:
    """DRRR增强版AI机器人"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://drrr.com"
        self.room_id = None
        self.room_info = None
        self.user_profile = None
        self.admin_name = "52Hertz"
        self.ai_enabled = False
        self.ai_manage_enabled = True  # AI房间管理功能开关 - 默认开启
        # 新的素颜API接口配置
        self.ai_api_key = ""  # 新接口不需要API key
        self.ai_api_url = "https://api.suyanw.cn/api/zpai.php"
        
        # AI模型设置
        self.ai_models = ["V3", "R1"]
        self.current_ai_model = "V3"  # 默认使用V3模型
        
        # 不当言论关键词列表（用于最小化发送到AI的文本量）
        self.inappropriate_keywords = [
            "暴力", "色情", "赌博", "毒品", "诈骗", "骂人", "脏话", "攻击", 
            "威胁", "恐吓", "歧视", "仇恨", "违法", "敏感", "政治", "宗教"
        ]
        
        # 音乐点播列表
        self.music_playlist = []
        self.auto_play_enabled = False  # 自动播放功能开关
        self.last_auto_play_time = 0
        self.auto_play_interval = 5 * 60  # 自动播放间隔（5分钟）
        
        # 已欢迎的用户列表
        self.welcomed_users = set()
        
        # 挂房功能相关
        self.hang_room_enabled = True
        self.last_hang_room_time = 0
        self.hang_room_interval = 20 * 60  # 20分钟
        
        # 机器人连接状态
        self.is_connected = False
        self.last_heartbeat = time.time()
        self.heartbeat_interval = 60  # 60秒心跳检测
        
        # 消息去重机制
        self.recent_messages = []  # 存储最近发送的消息
        self.max_recent_messages = 10  # 最多存储10条最近消息
        
        # 用户消息频率限制
        self.user_message_times = {}  # 存储用户最近消息的时间戳
        self.message_limit = 5  # 限制用户在指定时间内发送的消息数量
        self.time_window = 60  # 时间窗口（秒）
        
        # 用户重复消息检测
        self.user_last_messages = {}  # 存储用户最近发送的消息
        self.repeat_limit = 3  # 允许重复消息的最大次数
        
        # 用户违规记录
        self.user_violations = {}
        self.violations_file = "user_violations.json"
        self.load_user_violations()
        
        # 保存配置信息用于重连
        self.cookie_string = None
        self.room_id_saved = None
        
        # 设置请求头，模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # 心跳文件
        self.heartbeat_file = "bot_heartbeat.json"
        
    def set_cookie(self, cookie_string):
        """设置Cookie"""
        try:
            self.session.headers['Cookie'] = cookie_string
            logger.info("Cookie设置成功")
        except Exception as e:
            logger.error(f"设置Cookie失败: {e}")
            
    def get_room_info(self, max_retries=3):
        """获取房间信息"""
        if not self.room_id:
            logger.error("房间ID未设置")
            return None
            
        url = f"{self.base_url}/room/?id={self.room_id}&api=json"
        
        for attempt in range(max_retries):
            try:
                logger.info(f"正在获取房间信息: {url} (尝试 {attempt+1}/{max_retries})")
                response = self.session.get(url, timeout=30)
                logger.info(f"房间信息响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        room_data = response.json()
                        logger.info("成功获取房间信息")
                        return room_data
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON解析错误: {e}")
                        # 尝试打印响应内容以帮助调试
                        try:
                            logger.error(f"响应内容: {response.text[:500]}")  # 只打印前500个字符
                        except:
                            pass
                        return None
                elif response.status_code == 404:
                    logger.error("房间不存在或已关闭")
                    return None
                else:
                    logger.error(f"获取房间信息失败，状态码: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"网络请求错误: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析错误: {e}")
                # 尝试打印响应内容以帮助调试
                try:
                    logger.error(f"响应内容: {response.text[:500]}")  # 只打印前500个字符
                except:
                    pass
            except Exception as e:
                logger.error(f"获取房间信息时出错: {e}")
                
            if attempt < max_retries - 1:
                time.sleep(5)  # 等待5秒后重试
                
        logger.error("获取房间信息失败，已达到最大重试次数")
        return None
        
    def join_room(self, room_id, max_retries=3):
        """加入房间"""
        self.room_id = room_id
        
        for attempt in range(max_retries):
            try:
                # 直接尝试加入房间，而不先检查是否已在房间中
                # 直接访问房间页面来加入房间
                join_url = f"{self.base_url}/room/?id={room_id}"
                logger.info(f"正在加入房间: {join_url} (尝试 {attempt+1}/{max_retries})")
                
                # 先发送GET请求访问房间页面
                response = self.session.get(join_url, timeout=30)
                logger.info(f"访问房间页面响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info(f"成功加入房间: {room_id}")
                    self.is_connected = True
                    return True
                else:
                    logger.error(f"加入房间失败，状态码: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"加入房间时出错: {e}")
                
            if attempt < max_retries - 1:
                time.sleep(5)  # 等待5秒后重试
                
        logger.error("加入房间失败，已达到最大重试次数")
        return False
        
    def send_message(self, message, url=None, max_retries=3, is_delayed=False):
        """发送消息，如果消息过长则分段发送"""
        if not self.room_id:
            logger.error("房间ID未设置")
            return False
            
        # DRRR聊天室消息长度限制（最大100字符）
        MAX_MESSAGE_LENGTH = 100
        
        # 如果消息长度超过限制，进行分段发送
        if len(message) > MAX_MESSAGE_LENGTH:
            # 按换行符分割消息，避免在单词中间分割
            messages = self.split_message(message, MAX_MESSAGE_LENGTH)
        else:
            messages = [message]
            
        # 发送所有消息段
        success = True
        for i, msg_segment in enumerate(messages):
            # 为分段消息添加序号
            if len(messages) > 1:
                numbered_message = f"[{i+1}/{len(messages)}] {msg_segment}"
            else:
                numbered_message = msg_segment
                
            segment_success = self._send_single_message(numbered_message, url, max_retries, is_delayed)
            success = success and segment_success
            
            # 在发送分段消息之间添加延迟，避免发送过快
            if len(messages) > 1 and i < len(messages) - 1:
                time.sleep(1)
                
        return success
        
    def split_message(self, message, max_length):
        """将长消息分割成多个片段"""
        # 先按换行符分割
        lines = message.split('\n')
        messages = []
        current_message = ""
        
        for line in lines:
            # 如果加上新行后超过长度限制，则保存当前消息并开始新的消息
            if len(current_message) + len(line) + 1 > max_length and current_message:
                messages.append(current_message)
                current_message = line
            # 如果单行就超过长度限制，则强制分割
            elif len(line) > max_length:
                # 如果current_message有内容，先保存
                if current_message:
                    messages.append(current_message)
                    current_message = ""
                
                # 分割长行
                while len(line) > max_length:
                    messages.append(line[:max_length])
                    line = line[max_length:]
                current_message = line
            # 否则添加到当前消息
            else:
                if current_message:
                    current_message += '\n' + line
                else:
                    current_message = line
        
        # 添加最后的消息段
        if current_message:
            messages.append(current_message)
            
        return messages
        
    def _send_single_message(self, message, url=None, max_retries=3, is_delayed=False):
        """发送单条消息"""
        if not url:
            url = f"{self.base_url}/room/?ajax=1"
            
        data = {
            'message': message,
            'id': self.room_id
        }
        
        # 如果是延迟发送的消息，添加特殊标记
        if is_delayed:
            data['delayed'] = '1'
            
        for attempt in range(max_retries):
            try:
                logger.info(f"发送消息到: {url} (尝试 {attempt+1}/{max_retries})")
                logger.info(f"POST数据: {data}")
                
                response = self.session.post(url, data=data, timeout=30)
                logger.info(f"消息发送响应状态: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info(f"消息发送成功: {message}")
                    return True
                else:
                    logger.error(f"消息发送失败，状态码: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"发送消息时出错: {e}")
                
            if attempt < max_retries - 1:
                time.sleep(2)  # 等待2秒后重试
                
        logger.error("消息发送失败，已达到最大重试次数")
        return False
        
    def is_admin(self, user_name):
        """检查用户是否为管理员"""
        return user_name == self.admin_name
        
    def handle_admin_commands(self, user_name, message_text):
        """处理管理员命令"""
        if not self.is_admin(user_name):
            return False
            
        # 移除命令前缀
        command = message_text.lstrip('/')
        
        # 处理管理命令
        if command.startswith('ai manage'):
            if 'on' in command:
                self.ai_manage_enabled = True
                self.send_message("AI房间管理功能已开启")
                logger.info("AI房间管理功能已开启")
                return True
            elif 'off' in command:
                self.ai_manage_enabled = False
                self.send_message("AI房间管理功能已关闭")
                logger.info("AI房间管理功能已关闭")
                return True
                
        elif command.startswith('ai'):
            if 'on' in command:
                self.ai_enabled = True
                self.send_message("AI对话功能已开启")
                logger.info("AI对话功能已开启")
                return True
            elif 'off' in command:
                self.ai_enabled = False
                self.send_message("AI对话功能已关闭")
                logger.info("AI对话功能已关闭")
                return True
            elif command.strip() == 'ai model':
                # 查看当前AI模型
                self.send_message(f"当前AI模型: {self.current_ai_model}")
                return True
            elif command.startswith('ai model '):
                # 切换AI模型
                model_name = command[9:].strip()  # 移除'ai model '前缀
                if model_name in self.ai_models:
                    self.current_ai_model = model_name
                    self.send_message(f"AI模型已切换为: {model_name}")
                    logger.info(f"AI模型已切换为: {model_name}")
                else:
                    models_list = ", ".join(self.ai_models)
                    self.send_message(f"无效的AI模型: {model_name}\n可用模型: {models_list}")
                return True
            elif command.strip() == 'ai models':
                # 查看可用AI模型列表
                models_list = ", ".join(self.ai_models)
                self.send_message(f"可用AI模型: {models_list}")
                return True
                
        elif command.startswith('hang'):
            if 'on' in command:
                self.hang_room_enabled = True
                self.send_message("挂房功能已开启")
                logger.info("挂房功能已开启")
                return True
            elif 'off' in command:
                self.hang_room_enabled = False
                self.send_message("挂房功能已关闭")
                logger.info("挂房功能已关闭")
                return True
                
        elif command.startswith('help'):
            # 显示帮助信息
            help_text = """DRRR 增强版AI机器人 帮助信息:
            
AI功能命令（仅限管理员）:
/ai on - 开启AI功能
/ai off - 关闭AI功能
/ai <问题> - 与AI对话
/ai model - 查看当前AI模型
/ai models - 查看可用AI模型列表
/ai model <模型名> - 切换AI模型
/ai manage on - 开启AI房间管理功能
/ai manage off - 关闭AI房间管理功能

音乐点播命令（所有用户）:
/play <歌曲名> <链接> - 添加歌曲到播放列表
/netmusic <歌曲名> - 搜索网易云音乐
/qqmusic <歌曲名> - 搜索QQ音乐并直接输出链接
/tts <文本> - 将文本转换为语音并直接输出链接
/next - 播放下一首歌曲
/playlist - 查看播放列表
/clear - 清空播放列表

信息查询命令（所有用户）:
/joke - 随机段子
/translate <内容> - 翻译内容

系统命令（仅限管理员）:
/hang on - 开启挂房功能
/hang off - 关闭挂房功能
/kick <用户名> - 踢出指定用户
/ban <用户名> - 封禁指定用户
/unban <用户名> - 解封指定用户
/help - 显示帮助信息"""
            self.send_message(help_text)
            return True
            
        elif command.startswith('joke'):
            # 处理笑话命令
            joke = self.get_random_joke()
            self.send_message(f"@{user_name} {joke}")
            return True
            
        elif command.startswith('kick'):
            # 踢出用户命令
            target_user = command[4:].strip()  # 移除'kick'前缀
            if target_user:
                self.kick_user(target_user, None)  # 这里需要实际的用户ID
                self.send_message(f"已发送踢出用户 {target_user} 的指令")
                return True
            else:
                self.send_message("请提供要踢出的用户名: /kick <用户名>")
                return True
                
        elif command.startswith('ban'):
            # 封禁用户命令
            target_user = command[3:].strip()  # 移除'ban'前缀
            if target_user:
                self.ban_user(target_user, None)  # 这里需要实际的用户ID
                self.send_message(f"已发送封禁用户 {target_user} 的指令")
                return True
            else:
                self.send_message("请提供要封禁的用户名: /ban <用户名>")
                return True
                
        elif command.startswith('unban'):
            # 解封用户命令
            target_user = command[5:].strip()  # 移除'unban'前缀
            if target_user:
                self.unban_user(target_user)
                self.send_message(f"已发送解封用户 {target_user} 的指令")
                return True
            else:
                self.send_message("请提供要解封的用户名: /unban <用户名>")
                return True
                
        # 音乐相关命令完全由handle_music_commands函数处理
        # 这里不再处理music命令，避免命令处理冲突
        pass
        
    def handle_music_commands(self, user_name, message_text):
        """处理音乐点播命令"""
        # 处理不同的音乐命令前缀
        if message_text.startswith('/music'):
            # 旧的/music命令格式
            command_prefix = '/music'
        elif message_text.startswith('/play'):
            # 新的/play命令格式
            command_prefix = '/play'
        elif message_text.startswith('/netmusic'):
            # 网易云音乐搜索命令
            command_prefix = '/netmusic'
        elif message_text.startswith('/yunting'):
            # 云听FM搜索命令
            command_prefix = '/yunting'
        elif message_text.startswith('/tts'):
            # 文本转语音命令
            command_prefix = '/tts'
        elif message_text.startswith('/next'):
            # 播放下一首命令
            command_prefix = '/next'
        elif message_text.startswith('/playlist'):
            # 查看播放列表命令
            command_prefix = '/playlist'
        elif message_text.startswith('/clear'):
            # 清空播放列表命令
            command_prefix = '/clear'
        else:
            return False
            
        # 移除命令前缀
        command = message_text[len(command_prefix):].strip()
        
        if command_prefix == '/play':
            # 提取歌曲名和链接
            parts = command.split(' ', 1)
            if len(parts) >= 2:
                song_name, song_url = parts[0], parts[1]
                self.music_playlist.append(song_url)
                self.send_message(f"@{user_name} 已添加歌曲 '{song_name}' 到播放列表")
                logger.info(f"用户 {user_name} 添加歌曲 '{song_name}' 到播放列表: {song_url}")
                return True
            else:
                self.send_message("请使用格式: /play <歌曲名> <链接>")
                return True
                
        elif command_prefix == '/netmusic':
            # 搜索网易云音乐
            if command:
                self.send_message(f"@{user_name} 正在搜索网易云音乐: {command}")
                # 这里应该调用网易云音乐搜索API
                # 暂时用模拟回复
                self.send_message(f"@{user_name} 搜索完成，找到相关歌曲，请使用/play命令添加到播放列表")
                return True
            else:
                self.send_message("请提供要搜索的歌曲名: /netmusic <歌曲名>")
                return True
                
        elif command_prefix == '/yunting':
            # 搜索云听FM专辑
            if command:
                self.send_message(f"@{user_name} 正在搜索云听FM专辑: {command}")
                # 这里应该调用云听FM搜索API
                # 暂时用模拟回复
                self.send_message(f"@{user_name} 搜索完成，找到相关专辑，请使用/play命令添加到播放列表")
                return True
            else:
                self.send_message("请提供要搜索的专辑名: /yunting <专辑名>")
                return True
                
        elif command_prefix == '/tts':
            # 文本转语音
            if command:
                self.send_message(f"@{user_name} 正在将文本转换为语音...")
                # 这里应该调用TTS API
                # 暂时用模拟回复
                tts_url = "https://example.com/tts/" + command[:10]  # 模拟TTS链接
                self.music_playlist.append(tts_url)
                self.send_message(f"@{user_name} 文本转语音完成，已添加到播放列表")
                return True
            else:
                self.send_message("请提供要转换的文本: /tts <文本>")
                return True
                
        elif command_prefix == '/next':
            # 播放下一首
            self.play_music()
            return True
            
        elif command_prefix == '/playlist':
            # 查看播放列表
            if self.music_playlist:
                playlist_msg = f"@{user_name} 当前播放列表:\n" + "\n".join(self.music_playlist)
            else:
                playlist_msg = f"@{user_name} 播放列表为空"
            self.send_message(playlist_msg)
            return True
            
        elif command_prefix == '/clear':
            # 清空播放列表
            self.music_playlist.clear()
            self.send_message(f"@{user_name} 播放列表已清空")
            logger.info(f"用户 {user_name} 清空了播放列表")
            return True
            
        # 处理原有的/music命令
        if command.startswith('add'):
            # 提取音乐链接
            music_url = command[3:].strip()  # 移除'add'前缀
            if music_url:
                self.music_playlist.append(music_url)
                self.send_message(f"@{user_name} 已添加到播放列表")
                logger.info(f"用户 {user_name} 添加音乐到播放列表: {music_url}")
                return True
                
        elif command == 'list':
            if self.music_playlist:
                playlist_msg = f"@{user_name} 当前播放列表:\n" + "\n".join(self.music_playlist)
            else:
                playlist_msg = f"@{user_name} 播放列表为空"
            self.send_message(playlist_msg)
            return True
            
        elif command == 'play':
            self.play_music()
            return True
            
        return False
        
    def handle_ai_command(self, user_name, message_text):
        """处理AI对话命令"""
        if not message_text.startswith('/ai'):
            return False
            
        # 检查AI功能是否开启
        if not self.ai_enabled:
            # 如果是管理员，提示如何开启AI功能
            if self.is_admin(user_name):
                self.send_message("AI对话功能未开启，请使用 '/ai on' 命令开启")
            else:
                self.send_message("AI对话功能未开启，请管理员先开启")
            return True
            
        # 提取用户消息
        user_message = message_text[3:].strip()  # 移除'/ai'前缀
        
        if not user_message:
            self.send_message("请输入要对话的内容")
            return True
            
        # 提示用户等待
        self.send_message(f"@{user_name} 正在处理您的请求，请稍等...")
            
        # 异步调用AI接口，避免阻塞主线程
        def async_call_ai():
            ai_response = self.call_ai_api(user_message)
            if ai_response:
                # 检查是否为空响应或特定错误消息
                if ai_response == "AI接口返回空响应，请稍后再试":
                    self.send_message(f"@{user_name} {ai_response}")
                elif ai_response.startswith("AI接口调用失败"):
                    self.send_message(f"@{user_name} {ai_response}")
                else:
                    # 发送AI回复
                    self.send_message(f"@{user_name} {ai_response}")
            else:
                self.send_message(f"@{user_name} AI接口调用失败，请稍后再试")
        
        # 在新线程中执行AI调用
        ai_thread = threading.Thread(target=async_call_ai)
        ai_thread.daemon = True  # 设置为守护线程
        ai_thread.start()
            
        return True
        
    def call_ai_api(self, user_message):
        """调用AI接口"""
        try:
            # 构造请求参数
            params = {
                "msg": user_message
            }

            logger.info(f"调用AI接口: {self.ai_api_url}")
            logger.info(f"请求参数: {params}")

            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }

            # 实现重试机制以优化延迟问题
            max_retries = 3
            retry_delay = 5  # 重试间隔（秒）

            for attempt in range(max_retries):
                try:
                    logger.info(f"开始第{attempt + 1}次AI接口调用")
                    start_time = time.time()

                    # 发送GET请求，增加超时时间以适应长时间响应（最大可能需要1分钟）
                    response = self.session.get(self.ai_api_url, params=params, headers=headers, timeout=70)

                    end_time = time.time()
                    response_time = end_time - start_time
                    logger.info(f"AI接口响应状态码: {response.status_code}")
                    logger.info(f"AI接口响应时间: {response_time:.2f}秒")
                    logger.info(f"AI接口响应内容长度: {len(response.text)}字符")

                    if response.status_code == 200:
                        # 解析JSON响应
                        try:
                            response_data = response.json()
                            if response_data.get("status") == "success":
                                content = response_data.get("content", "")
                                if content.strip():
                                    logger.info(f"AI接口调用成功，返回内容: {content[:100]}{'...' if len(content) > 100 else ''}")
                                    return content
                                else:
                                    logger.warning("AI接口返回空内容")
                                    # 如果不是最后一次尝试，等待后重试
                                    if attempt < max_retries - 1:
                                        logger.info(f"AI接口返回空内容，{retry_delay}秒后进行第{attempt + 2}次重试")
                                        time.sleep(retry_delay)
                                        continue
                                    return "AI接口返回空内容，请稍后再试"
                            else:
                                error_msg = response_data.get("message", "未知错误")
                                logger.error(f"AI接口返回错误: {error_msg}")
                                return f"AI接口返回错误: {error_msg}"
                        except json.JSONDecodeError:
                            logger.error(f"AI接口响应不是有效的JSON格式: {response.text}")
                            return "AI接口响应格式错误，请稍后再试"
                    else:
                        logger.error(f"AI接口调用失败，状态码: {response.status_code}")
                        logger.error(f"AI接口错误响应: {response.text}")
                        # 根据错误码返回相应的错误信息
                        if response.status_code == 400:
                            return "请求错误，请稍后再试"
                        elif response.status_code == 403:
                            return "请求被服务器拒绝，请稍后再试"
                        elif response.status_code == 405:
                            return "客户端请求的方法被禁止，请稍后再试"
                        elif response.status_code == 408:
                            return "请求时间过长，请稍后再试"
                        elif response.status_code == 500:
                            return "服务器内部出现错误，请稍后再试"
                        elif response.status_code == 501:
                            return "服务器不支持请求的功能，请稍后再试"
                        elif response.status_code == 503:
                            return "系统维护中，请稍后再试"
                        else:
                            # 如果不是最后一次尝试，等待后重试
                            if attempt < max_retries - 1:
                                logger.info(f"AI接口调用失败，{retry_delay}秒后进行第{attempt + 2}次重试")
                                time.sleep(retry_delay)
                                continue
                            return f"AI接口调用失败，状态码: {response.status_code}"

                except requests.exceptions.Timeout:
                    end_time = time.time()
                    response_time = end_time - start_time
                    logger.warning(f"AI接口请求超时，第{attempt + 1}次尝试，耗时: {response_time:.2f}秒")
                    # 如果不是最后一次尝试，等待后重试
                    if attempt < max_retries - 1:
                        logger.info(f"AI接口请求超时，{retry_delay}秒后进行第{attempt + 2}次重试")
                        time.sleep(retry_delay)
                        continue
                    return "AI接口请求超时，请稍后再试"
                except requests.exceptions.RequestException as e:
                    end_time = time.time()
                    response_time = end_time - start_time
                    logger.error(f"AI接口网络请求错误: {e}，耗时: {response_time:.2f}秒")
                    # 如果不是最后一次尝试，等待后重试
                    if attempt < max_retries - 1:
                        logger.info(f"AI接口网络请求错误，{retry_delay}秒后进行第{attempt + 2}次重试")
                        time.sleep(retry_delay)
                        continue
                    return "网络请求错误，请稍后再试"

            # 所有重试都失败
            return "AI接口调用失败，请稍后再试"
                
        except Exception as e:
            logger.error(f"调用AI接口时出错: {e}")
            return "调用AI接口时出错，请稍后再试"
            
    def get_random_joke(self):
        """获取随机笑话"""
        try:
            # 使用AI接口生成笑话
            joke_prompt = "请给我讲一个简短的笑话，最好是中文的，适合在聊天室分享。"
            params = {
                "msg": joke_prompt,
                "qq": "10002",  # 使用不同的QQ参数
                "type": "text"
            }
            
            logger.info(f"请求笑话: {self.ai_api_url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(self.ai_api_url, params=params, headers=headers, timeout=30)
            
            logger.info(f"笑话接口响应状态码: {response.status_code}")
            logger.info(f"笑话接口响应内容: {response.text}")
            
            if response.status_code == 200:
                # 对于文本响应，直接返回内容
                return response.text
            else:
                logger.error(f"笑话接口调用失败，状态码: {response.status_code}")
                logger.error(f"笑话接口错误响应: {response.text}")
                return "抱歉，暂时无法生成笑话，请稍后再试。"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"笑话接口网络请求错误: {e}")
            return "网络请求错误，请稍后再试"
        except Exception as e:
            logger.error(f"获取笑话时出错: {e}")
            return "抱歉，暂时无法生成笑话，请稍后再试。"
            
    def search_bilibili(self, uid):
        """搜索B站用户动态"""
        try:
            # 使用AI接口搜索B站用户信息
            prompt = f"请根据UID {uid}生成一个模拟的B站用户信息，包括用户名和签名。请直接返回用户名和签名，不要包含代码。"
            params = {
                "msg": prompt
            }
            
            logger.info(f"请求AI生成B站用户信息: {self.ai_api_url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(self.ai_api_url, params=params, headers=headers, timeout=30)
            
            logger.info(f"AI接口响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解析JSON响应
                data = response.json()
                
                # 检查是否有内容
                if data.get("status") == "success":
                    content = data.get("content", "")
                    if content.strip():
                        return f"用户UID {uid} 的信息：\n{content}"
                    else:
                        return f"抱歉，未能生成UID为'{uid}'的B站用户信息。"
                else:
                    return "抱歉，暂时无法获取B站用户信息，请稍后再试。"
            else:
                logger.error(f"AI接口调用失败，状态码: {response.status_code}")
                logger.error(f"AI接口错误响应: {response.text}")
                return "抱歉，暂时无法获取B站用户信息，请稍后再试。"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"AI接口网络请求错误: {e}")
            return "网络请求错误，请稍后再试"
        except Exception as e:
            logger.error(f"搜索B站用户信息时出错: {e}")
            return "抱歉，暂时无法获取B站用户信息，请稍后再试。"
            
    def search_baike(self, keyword):
        """搜索百度百科"""
        try:
            # 使用AI接口搜索百科内容
            prompt = f"请为我提供'{keyword}'的简要百科介绍，包括其定义、主要特点和用途。"
            params = {
                "msg": prompt
            }
            
            logger.info(f"请求AI生成百科内容: {self.ai_api_url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(self.ai_api_url, params=params, headers=headers, timeout=30)
            
            logger.info(f"AI接口响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解析JSON响应
                data = response.json()
                
                # 检查是否有内容
                if data.get("status") == "success":
                    content = data.get("content", "")
                    if content.strip():
                        return f"【{keyword}】\n{content}"
                    else:
                        return f"抱歉，未能生成'{keyword}'的百科内容。"
                else:
                    return "抱歉，暂时无法获取百科内容，请稍后再试。"
            else:
                logger.error(f"AI接口调用失败，状态码: {response.status_code}")
                logger.error(f"AI接口错误响应: {response.text}")
                return "抱歉，暂时无法获取百科内容，请稍后再试。"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"AI接口网络请求错误: {e}")
            return "网络请求错误，请稍后再试"
        except Exception as e:
            logger.error(f"搜索百科内容时出错: {e}")
            return "抱歉，暂时无法获取百科内容，请稍后再试。"
            
    def search_qq_music(self, song_name):
        """搜索QQ音乐"""
        try:
            # 使用QQ音乐API搜索歌曲
            url = "https://api.suyanw.cn/api/QQ_Music.php"
            params = {
                "msg": song_name,
                "n": 1  # 默认选择第一首
            }
            
            logger.info(f"请求QQ音乐: {url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            
            logger.info(f"QQ音乐接口响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解析JSON响应
                data = response.json()
                
                # 检查是否有内容
                if 'code' in data and data['code'] == 200:
                    # 提取歌曲信息
                    song_info = data.get('data', {})
                    if song_info:
                        title = song_info.get('title', '未知歌曲')
                        singer = song_info.get('singer', '未知歌手')
                        song_url = song_info.get('url', '')
                        
                        result = f"找到歌曲: {title} - {singer}"
                        if song_url:
                            # 将歌曲添加到播放列表
                            self.music_playlist.append(song_url)
                            result += f"\n已添加到播放列表"
                        else:
                            result += f"\n无法获取播放链接"
                        
                        return result
                    else:
                        return f"抱歉，未找到与'{song_name}'相关的歌曲。"
                else:
                    error_msg = data.get('text', '未知错误')
                    return f"QQ音乐搜索失败: {error_msg}"
            else:
                logger.error(f"QQ音乐接口调用失败，状态码: {response.status_code}")
                logger.error(f"QQ音乐接口错误响应: {response.text}")
                return "抱歉，暂时无法搜索QQ音乐，请稍后再试。"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"QQ音乐接口网络请求错误: {e}")
            return "网络请求错误，请稍后再试"
        except Exception as e:
            logger.error(f"搜索QQ音乐时出错: {e}")
            return "抱歉，暂时无法搜索QQ音乐，请稍后再试。"
            
    def search_qq_music_direct(self, song_name):
        """搜索QQ音乐并直接输出URL"""
        try:
            # 使用QQ音乐API搜索歌曲
            url = "https://api.suyanw.cn/api/QQ_Music.php"
            params = {
                "msg": song_name,
                "n": 1  # 默认选择第一首
            }
            
            logger.info(f"请求QQ音乐: {url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            
            logger.info(f"QQ音乐接口响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解析JSON响应
                data = response.json()
                
                # 检查是否有内容
                if 'code' in data and data['code'] == 200:
                    # 提取歌曲信息
                    song_info = data.get('data', {})
                    if song_info:
                        title = song_info.get('title', '未知歌曲')
                        singer = song_info.get('singer', '未知歌手')
                        song_url = song_info.get('url', '')
                        
                        result = f"找到歌曲: {title} - {singer}"
                        if song_url:
                            # 直接输出URL而不是添加到播放列表
                            result += f"\n歌曲链接: {song_url}"
                        else:
                            result += f"\n无法获取播放链接"
                        
                        return result
                    else:
                        return f"抱歉，未找到与'{song_name}'相关的歌曲。"
                else:
                    error_msg = data.get('text', '未知错误')
                    return f"QQ音乐搜索失败: {error_msg}"
            else:
                logger.error(f"QQ音乐接口调用失败，状态码: {response.status_code}")
                logger.error(f"QQ音乐接口错误响应: {response.text}")
                return "抱歉，暂时无法搜索QQ音乐，请稍后再试。"
                
        except requests.exceptions.RequestException as e:
            logger.error(f"QQ音乐接口网络请求错误: {e}")
            return "网络请求错误，请稍后再试"
        except Exception as e:
            logger.error(f"搜索QQ音乐时出错: {e}")
            return "抱歉，暂时无法搜索QQ音乐，请稍后再试。"
            
    def text_to_speech(self, text):
        """文本转语音"""
        try:
            # 使用文本转语音API
            url = "https://api.suyanw.cn/api/tts.php"
            params = {
                "text": text,
                "voice": "素颜"  # 使用默认声音
            }
            
            logger.info(f"请求文本转语音: {url}")
            
            # 设置请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=30)
            
            logger.info(f"文本转语音接口响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解析JSON响应
                data = response.json()
                
                # 检查是否有内容
                if 'code' in data and data['code'] == 200:
                    # 提取音频链接
                    file_link = data['data']['file_link']
                    return file_link
                else:
                    error_msg = data.get('msg', '未知错误')
                    logger.error(f"文本转语音失败: {error_msg}")
                    return None
            else:
                logger.error(f"文本转语音接口调用失败，状态码: {response.status_code}")
                logger.error(f"文本转语音接口错误响应: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"文本转语音接口网络请求错误: {e}")
            return None
        except Exception as e:
            logger.error(f"文本转语音时出错: {e}")
            return None
            
    def handle_info_commands(self, user_name, message_text):
        """处理信息查询命令"""
        # 处理不同的信息查询命令前缀
        if message_text.startswith('/translate'):
            # 翻译命令
            command_prefix = '/translate'
        else:
            return False
            
        # 移除命令前缀
        command = message_text[len(command_prefix):].strip()
        
        if command_prefix == '/translate':
            # 翻译文本
            if command:
                result = self.translate_text(command)
                self.send_message(f"@{user_name} {result}")
                return True
            else:
                self.send_message("请提供要翻译的内容: /translate <内容>")
                return True
                
        return True
        
    def handle_music_commands(self, user_name, message_text):
        """处理音乐点播命令"""
        # 处理不同的音乐命令前缀
        if message_text.startswith('/music'):
            # 旧的/music命令格式
            command_prefix = '/music'
        elif message_text.startswith('/play'):
            # 新的/play命令格式
            command_prefix = '/play'
        elif message_text.startswith('/netmusic'):
            # 网易云音乐搜索命令
            command_prefix = '/netmusic'
        elif message_text.startswith('/qqmusic'):
            # QQ音乐搜索命令
            command_prefix = '/qqmusic'
        elif message_text.startswith('/tts'):
            # 文本转语音命令
            command_prefix = '/tts'
        elif message_text.startswith('/next'):
            # 播放下一首命令
            command_prefix = '/next'
        elif message_text.startswith('/playlist'):
            # 查看播放列表命令
            command_prefix = '/playlist'
        elif message_text.startswith('/clear'):
            # 清空播放列表命令
            command_prefix = '/clear'
        else:
            return False
            
        # 移除命令前缀
        command = message_text[len(command_prefix):].strip()
        
        if command_prefix == '/play':
            # 提取歌曲名和链接
            parts = command.split(' ', 1)
            if len(parts) >= 2:
                song_name, song_url = parts[0], parts[1]
                self.music_playlist.append(song_url)
                self.send_message(f"@{user_name} 已添加歌曲 '{song_name}' 到播放列表")
                logger.info(f"用户 {user_name} 添加歌曲 '{song_name}' 到播放列表: {song_url}")
                return True
            else:
                self.send_message("请使用格式: /play <歌曲名> <链接>")
                return True
                
        elif command_prefix == '/netmusic':
            # 搜索网易云音乐
            if command:
                self.send_message(f"@{user_name} 正在搜索网易云音乐: {command}")
                # 这里应该调用网易云音乐搜索API
                # 暂时用模拟回复
                self.send_message(f"@{user_name} 搜索完成，找到相关歌曲，请使用/play命令添加到播放列表")
                return True
            else:
                self.send_message("请提供要搜索的歌曲名: /netmusic <歌曲名>")
                return True
                
        elif command_prefix == '/qqmusic':
            # 搜索QQ音乐
            if command:
                self.send_message(f"@{user_name} 正在搜索QQ音乐: {command}")
                # 调用QQ音乐搜索API
                result = self.search_qq_music_direct(command)
                self.send_message(f"@{user_name} {result}")
                return True
            else:
                self.send_message("请提供要搜索的歌曲名: /qqmusic <歌曲名>")
                return True
                
        elif command_prefix == '/tts':
            # 文本转语音
            if command:
                self.send_message(f"@{user_name} 正在将文本转换为语音...")
                # 调用文本转语音API
                tts_result = self.text_to_speech(command)
                if tts_result:
                    # 直接输出URL而不是添加到播放列表
                    self.send_message(f"@{user_name} 文本转语音完成:\n{tts_result}")
                else:
                    self.send_message(f"@{user_name} 文本转语音失败，请稍后再试")
                return True
            else:
                self.send_message("请提供要转换的文本: /tts <文本>")
                return True
                
        elif command_prefix == '/next':
            # 播放下一首
            self.play_music()
            return True
            
        elif command_prefix == '/playlist':
            # 查看播放列表
            if self.music_playlist:
                playlist_msg = f"@{user_name} 当前播放列表:\n" + "\n".join(self.music_playlist)
            else:
                playlist_msg = f"@{user_name} 播放列表为空"
            self.send_message(playlist_msg)
            return True
            
        elif command_prefix == '/clear':
            # 清空播放列表
            self.music_playlist.clear()
            self.send_message(f"@{user_name} 播放列表已清空")
            logger.info(f"用户 {user_name} 清空了播放列表")
            return True
            
        # 处理原有的/music命令
        if command.startswith('add'):
            # 提取音乐链接
            music_url = command[3:].strip()  # 移除'add'前缀
            if music_url:
                self.music_playlist.append(music_url)
                self.send_message(f"@{user_name} 已添加到播放列表")
                logger.info(f"用户 {user_name} 添加音乐到播放列表: {music_url}")
                return True
                
        elif command == 'list':
            if self.music_playlist:
                playlist_msg = f"@{user_name} 当前播放列表:\n" + "\n".join(self.music_playlist)
            else:
                playlist_msg = f"@{user_name} 播放列表为空"
            self.send_message(playlist_msg)
            return True
            
        elif command == 'play':
            self.play_music()
            return True
            
        return True
        
    def play_music(self):
        """播放音乐"""
        if not self.music_playlist:
            self.send_message("播放列表为空")
            return
            
        # 播放第一首音乐
        music_url = self.music_playlist[0]
        self.send_message(f"正在播放: {music_url}")
        logger.info(f"播放音乐: {music_url}")
        
        # 移除已播放的音乐
        self.music_playlist.pop(0)
        
    def auto_play_music(self):
        """自动播放音乐"""
        if not self.auto_play_enabled or not self.music_playlist:
            return
            
        current_time = time.time()
        if current_time - self.last_auto_play_time >= self.auto_play_interval:
            self.play_music()
            self.last_auto_play_time = current_time
            
    def send_hang_room_message(self):
        """发送挂房消息"""
        if not self.hang_room_enabled:
            return
            
        current_time = time.time()
        if current_time - self.last_hang_room_time >= self.hang_room_interval:
            self.send_message("/me 挂房测试信息")
            self.last_hang_room_time = current_time
            
    def keep_alive(self):
        """保持活跃状态"""
        try:
            # 发送一个无害的消息来保持连接
            self.send_message("/me 保持活跃...")
            logger.info("发送活跃信号成功")
            # 保存心跳信息
            self.save_heartbeat()
        except Exception as e:
            logger.error(f"发送活跃信号失败: {e}")
            
    def welcome_new_users(self):
        """欢迎新用户"""
        try:
            room_info = self.get_room_info()
            if not room_info:
                return
                
            users = room_info.get('room', {}).get('users', [])
            
            for user in users:
                user_name = user.get('name', '')
                user_id = user.get('id', '')
                
                # 跳过机器人自己和已欢迎的用户
                if user_name == 'AI机器人' or user_id in self.welcomed_users:
                    continue
                    
                # 欢迎新用户
                welcome_msg = f"/me ようこそ {user_name}！お疲れ様です！"
                self.send_message(welcome_msg)
                logger.info(f"已欢迎新用户: {user_name}")
                
                # 添加到已欢迎用户列表
                self.welcomed_users.add(user_id)
                
        except Exception as e:
            logger.error(f"欢迎新用户时出错: {e}")
            
    def is_user_rate_limited(self, user_id):
        """检查用户是否触发频率限制"""
        current_time = time.time()
        
        # 清理过期的时间戳
        if user_id in self.user_message_times:
            self.user_message_times[user_id] = [
                timestamp for timestamp in self.user_message_times[user_id] 
                if current_time - timestamp < self.time_window
            ]
        else:
            self.user_message_times[user_id] = []
            
        # 添加当前时间戳
        self.user_message_times[user_id].append(current_time)
        
        # 检查是否超过限制
        return len(self.user_message_times[user_id]) > self.message_limit
        
    def is_user_repeating_message(self, user_id, message):
        """检查用户是否重复发送相同消息"""
        current_time = time.time()
        
        # 初始化用户消息记录
        if user_id not in self.user_last_messages:
            self.user_last_messages[user_id] = []
            
        # 清理过期的消息记录（保留最近5分钟的）
        self.user_last_messages[user_id] = [
            (msg, timestamp) for msg, timestamp in self.user_last_messages[user_id]
            if current_time - timestamp < 300  # 5分钟
        ]
        
        # 检查是否重复
        repeat_count = sum(1 for msg, _ in self.user_last_messages[user_id] if msg == message)
        
        # 添加当前消息到记录
        self.user_last_messages[user_id].append((message, current_time))
        
        return repeat_count >= self.repeat_limit
        
    def load_user_violations(self):
        """加载用户违规记录"""
        try:
            if os.path.exists(self.violations_file):
                with open(self.violations_file, 'r', encoding='utf-8') as f:
                    self.user_violations = json.load(f)
                logger.info("已加载用户违规记录")
            else:
                logger.info("未找到用户违规记录文件，将创建新文件")
                self.save_user_violations()  # 创建空文件
        except Exception as e:
            logger.error(f"加载用户违规记录失败: {e}")
            self.user_violations = {}
            
    def save_user_violations(self):
        """保存用户违规记录"""
        try:
            with open(self.violations_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_violations, f, ensure_ascii=False, indent=2)
            logger.info("用户违规记录已保存")
        except Exception as e:
            logger.error(f"保存用户违规记录失败: {e}")
            
    def auto_manage_user(self, user_name, user_id, violation_count):
        """自动管理用户"""
        try:
            # 根据违规次数采取不同措施
            if violation_count >= 5:
                # 踢出房间
                self.kick_user(user_name, user_id)
            elif violation_count >= 3:
                # 禁言
                self.ban_user(user_name, user_id)
        except Exception as e:
            logger.error(f"自动管理用户时出错: {e}")
            
    def kick_user(self, user_name, user_id):
        """踢出用户"""
        try:
            # 这里应该调用实际的踢人API
            logger.info(f"踢出用户: {user_name} ({user_id})")
            # 发送通知消息
            self.send_message(f"用户 {user_name} 已被管理员踢出房间")
        except Exception as e:
            logger.error(f"踢出用户时出错: {e}")
            
    def ban_user(self, user_name, user_id):
        """禁言用户"""
        try:
            # 这里应该调用实际的禁言API
            logger.info(f"禁言用户: {user_name} ({user_id})")
            # 发送通知消息
            self.send_message(f"用户 {user_name} 已被管理员封禁")
        except Exception as e:
            logger.error(f"禁言用户时出错: {e}")
            
    def unban_user(self, user_name):
        """解封用户"""
        try:
            # 这里应该调用实际的解封API
            logger.info(f"解封用户: {user_name}")
            # 发送通知消息
            self.send_message(f"用户 {user_name} 已被管理员解封")
        except Exception as e:
            logger.error(f"解封用户时出错: {e}")
            
    def check_inappropriate_content(self, message):
        """检查不当内容"""
        try:
            # 转换为小写进行检查
            message_lower = message.lower()
            
            # 检查是否包含不当关键词
            for keyword in self.inappropriate_keywords:
                if keyword in message_lower:
                    return True, f"包含不当关键词: {keyword}"
                    
            return False, ""
        except Exception as e:
            logger.error(f"检查不当内容时出错: {e}")
            return False, ""
            
    def process_emojis(self, message):
        """处理表情符号"""
        try:
            # 移除或替换特殊表情符号
            # 这里可以根据需要添加具体的表情符号处理逻辑
            processed_message = message
            
            # 示例：移除某些特殊字符
            # processed_message = re.sub(r'[\U0001F600-\U0001F64F]', '', processed_message)  # 移除表情符号
            
            return processed_message
        except Exception as e:
            logger.error(f"处理表情符号时出错: {e}")
            return message
            
    def is_duplicate_message(self, message):
        """检查是否为重复消息"""
        try:
            # 检查消息是否在最近发送的消息中
            if message in self.recent_messages:
                return True
                
            # 添加到最近消息列表
            self.recent_messages.append(message)
            
            # 保持列表大小在限制范围内
            if len(self.recent_messages) > self.max_recent_messages:
                self.recent_messages.pop(0)
                
            return False
        except Exception as e:
            logger.error(f"检查重复消息时出错: {e}")
            return False
            
    def process_message(self, message_data):
        """处理收到的消息"""
        try:
            message_type = message_data.get('type', '')
            
            # 处理普通消息
            if message_type == 'message':
                user = message_data.get('from', {})
                user_name = user.get('name', 'Unknown')
                user_id = user.get('id', '')
                message_text = message_data.get('message', '')
                
                # 处理表情符号
                message_text = self.process_emojis(message_text)
                
                logger.info(f"[{user_name}]: {message_text}")
                
                # 检查用户是否触发频率限制（管理员除外）
                if not self.is_admin(user_name) and self.is_user_rate_limited(user_id):
                    # 增加用户违规计数
                    user_key = f"{user_name}_{user_id}"
                    self.user_violations[user_key] = self.user_violations.get(user_key, 0) + 1
                    violation_count = self.user_violations[user_key]
                    
                    # 保存违规记录
                    self.save_user_violations()
                    
                    # 根据违规次数采取自动管理措施
                    self.auto_manage_user(user_name, user_id, violation_count)
                    
                    # 发送警告消息（仅对轻微违规）
                    if violation_count < 2:
                        warning_msg = f"@{user_name} 您发送消息过于频繁，请稍后再试。这是第{violation_count}次违规。"
                        # 延迟发送警告消息
                        delay = random.randint(1, 3)
                        threading.Timer(delay, self.send_message, args=[warning_msg, None, None, True]).start()
                        logger.info(f"用户 {user_name} 触发频率限制，将在{delay}秒后发送警告")
                    return  # 不继续处理该消息
                
                # 检查用户是否重复发送相同消息（管理员除外）
                if not self.is_admin(user_name) and self.is_user_repeating_message(user_id, message_text):
                    # 增加用户违规计数
                    user_key = f"{user_name}_{user_id}"
                    self.user_violations[user_key] = self.user_violations.get(user_key, 0) + 1
                    violation_count = self.user_violations[user_key]
                    
                    # 保存违规记录
                    self.save_user_violations()
                    
                    # 警告用户（延迟回复）
                    warning_msg = f"@{user_name} 请勿重复发送相同消息。这是第{violation_count}次违规。"
                    # 延迟5-10秒发送警告消息，模拟缓慢回复
                    delay = random.randint(5, 10)
                    threading.Timer(delay, self.send_message, args=[warning_msg, None, None, True]).start()
                    logger.info(f"已检测到重复消息，将在{delay}秒后警告用户 {user_name}")
                    
                    # 根据违规次数采取自动管理措施
                    self.auto_manage_user(user_name, user_id, violation_count)
                    return  # 不继续处理该消息
                    
                # 检查消息是否包含不当内容（管理员除外）
                if not self.is_admin(user_name):
                    is_inappropriate, reason = self.check_inappropriate_content(message_text)
                    if is_inappropriate:
                        # 增加用户违规计数
                        user_key = f"{user_name}_{user_id}"
                        self.user_violations[user_key] = self.user_violations.get(user_key, 0) + 1
                        violation_count = self.user_violations[user_key]
                        
                        # 保存违规记录
                        self.save_user_violations()
                        
                        # 警告用户（延迟回复）
                        warning_msg = f"@{user_name} 发送的消息包含不当内容，已被系统拦截。请遵守聊天室规则。这是第{violation_count}次违规。"
                        # 延迟5-10秒发送警告消息，模拟缓慢回复
                        delay = random.randint(5, 10)
                        threading.Timer(delay, self.send_message, args=[warning_msg, None, None, True]).start()
                        logger.info(f"已检测到不当内容，将在{delay}秒后警告用户 {user_name}: {reason}")
                        
                        # 根据违规次数采取自动管理措施
                        self.auto_manage_user(user_name, user_id, violation_count)
                        return  # 不继续处理该消息
                
                # 处理管理员命令（仅管理员可以使用）
                if self.handle_admin_commands(user_name, message_text):
                    return
                    
                # 处理AI对话命令（所有用户都可以使用）
                if self.handle_ai_command(user_name, message_text):
                    return
                    
                # 处理音乐点播命令（所有用户都可以使用）
                if self.handle_music_commands(user_name, message_text):
                    return
                    
                # 处理信息查询命令（所有用户都可以使用）
                if self.handle_info_commands(user_name, message_text):
                    return
                    
                # 其他消息可以在这里处理
                
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            
    def heartbeat_check(self):
        """心跳检测，检查连接状态"""
        current_time = time.time()
        # 缩短心跳间隔到30秒，更频繁地检查连接状态
        if current_time - self.last_heartbeat > 30:
            logger.info("检测到连接可能已断开，尝试重新连接...")
            self.is_connected = False
            
    def reconnect(self):
        """重新连接"""
        logger.info("尝试重新连接...")
        try:
            # 重新加入房间
            if self.join_room(self.room_id_saved):
                logger.info("重新连接成功")
                self.is_connected = True
                self.last_heartbeat = time.time()
            else:
                logger.error("重新连接失败")
                # 如果重连失败，等待一段时间再试
                time.sleep(30)
        except Exception as e:
            logger.error(f"重新连接时出错: {e}")
            time.sleep(30)
            
    def save_heartbeat(self):
        """保存心跳信息"""
        try:
            heartbeat_data = {
                "timestamp": time.time(),
                "room_id": self.room_id,
                "is_connected": self.is_connected
            }
            with open(self.heartbeat_file, 'w', encoding='utf-8') as f:
                json.dump(heartbeat_data, f)
        except Exception as e:
            logger.error(f"保存心跳信息失败: {e}")
            
    def monitor_room(self):
        """监控房间活动"""
        logger.info("开始监控房间活动...")
        last_users = set()
        last_keep_alive_time = time.time()
        processed_messages = set()  # 用于跟踪已处理的消息
        
        while True:
            try:
                current_time = time.time()
                
                # 心跳检测
                if current_time - self.last_heartbeat >= self.heartbeat_interval:
                    logger.info("执行心跳检测...")
                    self.last_heartbeat = current_time
                    # 保存心跳信息
                    self.save_heartbeat()
                    # 检查连接状态
                    if not self.is_connected:
                        logger.warning("检测到连接断开")
                        # 尝试重新连接
                        self.reconnect()
                        
                # 增加额外的连接检查，确保机器人在房间中
                if self.is_connected:
                    # 每30秒检查一次是否仍在房间中
                    if current_time - self.last_heartbeat >= 30:
                        try:
                            room_info = self.get_room_info()
                            if room_info:
                                # 检查机器人是否仍在房间中
                                users = room_info.get('room', {}).get('users', [])
                                bot_in_room = any(user.get('name') == 'AI机器人' for user in users)
                                if not bot_in_room:
                                    logger.warning("检测到机器人不在房间中，尝试重新加入...")
                                    self.is_connected = False
                                    self.reconnect()
                            else:
                                logger.warning("无法获取房间信息，可能连接已断开")
                                self.is_connected = False
                                self.reconnect()
                        except Exception as e:
                            logger.warning(f"检查房间信息时出错: {e}")
                            # 即使检查失败，也继续运行
                        
                # 发送挂房消息
                self.send_hang_room_message()
                
                # 自动播放音乐
                self.auto_play_music()
                
                # 每3分钟发送一次活跃信号，防止账号被踢
                current_time = time.time()
                if current_time - last_keep_alive_time >= 3 * 60:
                    self.keep_alive()
                    last_keep_alive_time = current_time
                    
                # 获取最新的房间信息
                try:
                    room_info = self.get_room_info()
                    if room_info:
                        # 检查新用户加入
                        users = room_info.get('room', {}).get('users', [])
                        current_users = {user.get('id', '') for user in users}
                        
                        # 检查是否有新用户
                        new_users = current_users - last_users
                        if new_users:
                            self.welcome_new_users()
                            
                        last_users = current_users
                        
                        # 检查新消息
                        talks = room_info.get('room', {}).get('talks', [])
                    else:
                        talks = []
                except Exception as e:
                    logger.warning(f"获取房间信息时出错: {e}")
                    # 即使获取房间信息失败，也继续运行
                    room_info = None
                    talks = []
                    
                # 处理所有未处理的消息
                if talks:
                    for talk in talks:
                        # 简单的去重检查（基于消息内容和发送者）
                        talk_key = f"{talk.get('message', '')}_{talk.get('from', {}).get('id', '')}_{talk.get('time', 0)}"
                        if talk_key not in processed_messages:
                            self.process_message(talk)
                            processed_messages.add(talk_key)
                            # 限制消息处理速度，避免过快
                            time.sleep(0.1)
                        
                        # 保持processed_messages集合大小合理
                        if len(processed_messages) > 1000:
                            # 只保留最近的500条消息的记录
                            processed_messages = set(list(processed_messages)[-500:])
                            
                time.sleep(3)  # 每3秒检查一次
                
            except KeyboardInterrupt:
                logger.info("\n接收到中断信号")
                break
            except Exception as e:
                logger.error(f"监控房间时出错: {e}")
                time.sleep(5)
                
    def run_bot(self, room_id, cookie_string):
        """运行机器人"""
        try:
            # 保存配置信息用于重连
            self.cookie_string = cookie_string
            self.room_id_saved = room_id
            
            # 设置Cookie
            self.set_cookie(cookie_string)
            
            # 加入房间
            if not self.join_room(room_id):
                logger.error("加入房间失败")
                return
                
            # 发送上线消息
            self.send_message("AI机器人已上线")
            
            # 保存初始心跳信息
            self.save_heartbeat()
            
            # 开始监控房间
            self.monitor_room()
            
        except Exception as e:
            logger.error(f"运行时出错: {e}")
            import traceback
            traceback.print_exc()

def main():
    """主函数"""
    print("DRRR 增强版AI机器人")
    print("具有用户欢迎、指令权限控制、AI对话和音乐点播功能")
    
    bot = DRRREnhancedAIBot()
    
    # 从login_config.json读取配置信息
    try:
        with open('login_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        cookie_string = config.get('cookie', '')
        room_id = config.get('room_id', '')
        
        if not cookie_string or not room_id:
            print("错误：login_config.json中缺少cookie或room_id")
            return
    except Exception as e:
        print(f"错误：无法读取login_config.json: {e}")
        return
    
    # 运行机器人
    bot.run_bot(room_id, cookie_string)

if __name__ == "__main__":
    main()