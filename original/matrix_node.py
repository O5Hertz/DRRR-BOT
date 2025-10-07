#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRRR Bot维持矩阵节点
用于创建分布式维持系统，多个节点互相监控，确保Bot稳定运行
"""

import subprocess
import time
import os
import signal
import sys
import json
import threading
import requests
from datetime import datetime, timedelta
import logging

class MatrixNode:
    """矩阵节点类"""
    
    def __init__(self, node_id, config_file="matrix_config.json"):
        self.node_id = node_id
        self.config_file = config_file
        self.config = self.load_config()
        self.bot_dir = self.config.get('bot_dir', '/storage/emulated/0/壹号工作区/drrr_bot_standalone')
        self.bot_script = self.config.get('bot_script', 'enhanced_ai_bot.py')
        self.heartbeat_file = f"node_{node_id}_heartbeat.json"
        self.status_file = f"node_{node_id}_status.json"
        self.is_running = True
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format=f'%(asctime)s - [Node-{node_id}] - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'matrix_node_{node_id}.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            # 返回默认配置
            return {
                "bot_dir": "/storage/emulated/0/壹号工作区/drrr_bot_standalone",
                "bot_script": "enhanced_ai_bot.py",
                "nodes": [
                    {"id": "A", "heartbeat_file": "node_A_heartbeat.json"},
                    {"id": "B", "heartbeat_file": "node_B_heartbeat.json"},
                    {"id": "C", "heartbeat_file": "node_C_heartbeat.json"}
                ],
                "heartbeat_interval": 30,
                "check_interval": 60,
                "restart_cooldown": 300  # 5分钟冷却时间
            }
            
    def read_json_file_safely(self, file_path):
        """安全读取JSON文件"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:  # 检查文件是否为空
                        return json.loads(content)
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"解析JSON文件 {file_path} 失败: {e}")
            return None
        except Exception as e:
            self.logger.error(f"读取文件 {file_path} 失败: {e}")
            return None
            
    def save_heartbeat(self):
        """保存心跳信息"""
        try:
            heartbeat_data = {
                "node_id": self.node_id,
                "timestamp": time.time(),
                "last_restart": getattr(self, 'last_restart_time', 0)
            }
            with open(self.heartbeat_file, 'w', encoding='utf-8') as f:
                json.dump(heartbeat_data, f)
        except Exception as e:
            self.logger.error(f"保存心跳信息失败: {e}")
            
    def save_status(self, status):
        """保存节点状态"""
        try:
            status_data = {
                "node_id": self.node_id,
                "status": status,
                "timestamp": time.time()
            }
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status_data, f)
        except Exception as e:
            self.logger.error(f"保存状态信息失败: {e}")
            
    def is_bot_running(self):
        """检查Bot进程是否运行"""
        try:
            # 首先检查进程是否存在
            result = subprocess.run(['pgrep', '-f', self.bot_script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            
            # 如果进程不存在，检查统一启动程序
            launcher_result = subprocess.run(['pgrep', '-f', 'unified_launcher.py'], 
                                           capture_output=True, text=True)
            return launcher_result.returncode == 0
        except Exception as e:
            self.logger.error(f"检查Bot进程状态失败: {e}")
            return False
            
    def is_process_running(self, process_name):
        """检查指定进程是否运行"""
        try:
            result = subprocess.run(['pgrep', '-f', process_name], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def stop_bot(self):
        """停止Bot进程"""
        try:
            self.logger.info("正在停止Bot进程...")
            subprocess.run(['pkill', '-f', self.bot_script], capture_output=True)
            time.sleep(2)
            return True
        except Exception as e:
            self.logger.error(f"停止Bot进程失败: {e}")
            return False
            
    def start_bot(self):
        """启动Bot进程"""
        try:
            self.logger.info("正在启动Bot进程...")
            os.chdir(self.bot_dir)
            
            # 打开日志文件
            bot_log = open('bot.log', 'a')
            
            # 启动Bot程序
            process = subprocess.Popen(['nohup', 'python3', self.bot_script], 
                                     stdout=bot_log, 
                                     stderr=bot_log,
                                     preexec_fn=os.setsid)
            
            self.logger.info(f"Bot进程已启动，PID: {process.pid}")
            self.last_restart_time = time.time()
            return True
        except Exception as e:
            self.logger.error(f"启动Bot进程失败: {e}")
            return False
            
    def check_node_status(self, node_info):
        """检查节点状态"""
        try:
            heartbeat_file = node_info['heartbeat_file']
            heartbeat_data = self.read_json_file_safely(heartbeat_file)
            
            if heartbeat_data:
                # 检查心跳是否超时
                last_heartbeat = heartbeat_data.get('timestamp', 0)
                current_time = time.time()
                if current_time - last_heartbeat > 120:  # 2分钟超时
                    return False
                return True
            return False
        except Exception as e:
            self.logger.error(f"检查节点 {node_info['id']} 状态失败: {e}")
            return False
            
    def check_other_nodes(self):
        """检查其他节点状态"""
        try:
            nodes = self.config.get('nodes', [])
            for node_info in nodes:
                # 跳过自己
                if node_info['id'] == self.node_id:
                    continue
                    
                # 检查节点状态
                if not self.check_node_status(node_info):
                    self.logger.warning(f"检测到节点 {node_info['id']} 异常")
                    return True, node_info['id']
                    
            return False, None
        except Exception as e:
            self.logger.error(f"检查其他节点状态失败: {e}")
            return False, None
        
    def should_restart_bot(self):
        """判断是否需要重启Bot"""
        try:
            # 检查Bot进程是否运行
            if not self.is_bot_running():
                self.logger.info("检测到Bot进程未运行")
                return True
                
            # 检查Bot心跳
            bot_heartbeat_file = os.path.join(self.bot_dir, "bot_heartbeat.json")
            heartbeat_data = self.read_json_file_safely(bot_heartbeat_file)
            
            if heartbeat_data:
                last_heartbeat = heartbeat_data.get('timestamp', 0)
                current_time = time.time()
                # 如果5分钟没有心跳，则认为Bot无响应
                if current_time - last_heartbeat > 300:
                    self.logger.info("检测到Bot心跳超时")
                    return True
                    
            # 如果心跳文件不存在，但进程在运行，可能需要检查其他指标
            elif self.is_bot_running():
                # 如果心跳文件不存在但进程在运行，暂时不重启
                self.logger.warning("Bot进程在运行但心跳文件不存在")
                return False
                
            return False
        except Exception as e:
            self.logger.error(f"检查Bot状态失败: {e}")
            return False
            
    def restart_bot_if_needed(self):
        """根据需要重启Bot"""
        try:
            # 检查是否需要重启Bot
            if self.should_restart_bot():
                self.logger.info("检测到Bot需要重启")
                return self.coordinated_restart()
            return False
        except Exception as e:
            self.logger.error(f"重启Bot时出错: {e}")
            return False
        
    def coordinated_restart(self):
        """协调重启Bot"""
        # 检查冷却时间
        if hasattr(self, 'last_restart_time'):
            cooldown = self.config.get('restart_cooldown', 300)
            if time.time() - self.last_restart_time < cooldown:
                self.logger.info("重启冷却中，跳过重启")
                return False
                
        # 停止Bot
        if self.stop_bot():
            time.sleep(5)  # 等待进程完全停止
            
            # 启动Bot
            if self.start_bot():
                self.logger.info("Bot重启成功")
                return True
            else:
                self.logger.error("Bot启动失败")
                return False
        else:
            self.logger.error("Bot停止失败")
            return False
            
    def heartbeat_thread(self):
        """心跳线程"""
        while self.is_running:
            try:
                self.save_heartbeat()
                self.save_status("running")
                time.sleep(self.config.get('heartbeat_interval', 30))
            except Exception as e:
                self.logger.error(f"心跳线程出错: {e}")
                time.sleep(10)
                
    def monitoring_thread(self):
        """监控线程"""
        while self.is_running:
            try:
                self.logger.info("执行监控检查...")
                
                # 检查其他节点
                node_restart_needed, restart_node = self.check_other_nodes()
                
                # 如果需要重启且当前节点是主节点（A节点优先）
                if node_restart_needed and self.node_id == 'A':
                    self.logger.info(f"检测到节点 {restart_node} 异常，执行Bot重启操作...")
                    self.coordinated_restart()
                elif node_restart_needed:
                    self.logger.info(f"检测到节点 {restart_node} 异常，但当前节点不是主节点，等待主节点处理")
                    
                # 检查是否需要重启Bot
                bot_restart_needed = self.should_restart_bot()
                if bot_restart_needed:
                    if self.node_id == 'A':  # 只有主节点执行重启
                        self.logger.info("检测到Bot需要重启，执行重启操作...")
                        self.coordinated_restart()
                    else:
                        self.logger.info("检测到Bot需要重启，但当前节点不是主节点，等待主节点处理")
                        
                time.sleep(self.config.get('check_interval', 60))
            except Exception as e:
                self.logger.error(f"监控线程出错: {e}")
                time.sleep(30)
                
    def start(self):
        """启动节点"""
        self.logger.info(f"矩阵节点 {self.node_id} 启动")
        
        # 启动心跳线程
        heartbeat_t = threading.Thread(target=self.heartbeat_thread, daemon=True)
        heartbeat_t.start()
        
        # 启动监控线程
        monitor_t = threading.Thread(target=self.monitoring_thread, daemon=True)
        monitor_t.start()
        
        # 主线程保持运行
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("接收到中断信号，正在停止...")
            self.is_running = False
            
    def stop(self):
        """停止节点"""
        self.logger.info(f"矩阵节点 {self.node_id} 停止")
        self.is_running = False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 matrix_node.py <node_id>")
        print("例如: python3 matrix_node.py A")
        sys.exit(1)
        
    node_id = sys.argv[1]
    
    # 创建并启动节点
    node = MatrixNode(node_id)
    
    try:
        node.start()
    except KeyboardInterrupt:
        node.stop()
        print(f"节点 {node_id} 已停止")

if __name__ == "__main__":
    main()