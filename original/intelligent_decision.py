#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能决策脚本
用于判断是程序掉线还是账号掉线，并采取相应措施
"""

import subprocess
import time
import json
import os
import re

class IntelligentDecision:
    """智能决策类"""
    
    def __init__(self, log_file="bot.log", config_file="login_config.json"):
        self.log_file = log_file
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
            
    def is_process_running(self):
        """检查bot进程是否运行"""
        try:
            result = subprocess.run(['pgrep', '-f', 'enhanced_ai_bot.py'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def check_log_for_disconnect(self):
        """检查日志中是否有掉线信息"""
        try:
            with open(self.log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[-100:]  # 只检查最后100行
                
            # 检查是否有连接断开的信息
            for line in reversed(lines):
                if "检测到连接可能已断开" in line or "重新连接失败" in line:
                    return True
                if "成功加入房间" in line:
                    # 如果最近有成功加入房间的信息，说明连接是正常的
                    return False
            return False
        except Exception as e:
            print(f"检查日志失败: {e}")
            return False
            
    def check_account_status(self):
        """检查账号状态（通过简单的API调用）"""
        # 这里可以实现更复杂的账号状态检查逻辑
        # 比如检查是否能访问用户个人页面等
        return True
            
    def restart_main_bot(self):
        """重启主bot程序"""
        try:
            # 停止现有bot进程
            subprocess.run(['pkill', '-f', 'enhanced_ai_bot.py'], 
                          capture_output=True)
            time.sleep(2)
            
            # 启动bot程序
            bot_dir = "/storage/emulated/0/壹号工作区/drrr_bot_standalone"
            subprocess.Popen(['nohup', 'python3', 'enhanced_ai_bot.py'], 
                           cwd=bot_dir, stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            print("主bot程序已重启")
            return True
        except Exception as e:
            print(f"重启主bot程序失败: {e}")
            return False
            
    def run_login_bot(self):
        """运行登录机器人"""
        try:
            login_dir = "/storage/emulated/0/壹号工作区/drrr_bot_standalone"
            result = subprocess.run(['python3', 'smart_login_bot.py'], 
                                  cwd=login_dir, capture_output=True, 
                                  text=True)
            if result.returncode == 0:
                print("登录机器人执行成功")
                return True
            else:
                print(f"登录机器人执行失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"运行登录机器人失败: {e}")
            return False
            
    def make_decision(self):
        """做出智能决策"""
        print("开始智能决策...")
        
        # 检查进程状态
        process_running = self.is_process_running()
        print(f"进程运行状态: {process_running}")
        
        # 检查连接状态
        connection_lost = self.check_log_for_disconnect()
        print(f"连接状态: {'已断开' if connection_lost else '正常'}")
        
        # 决策逻辑
        if not process_running:
            print("检测到程序掉线，正在重启主bot程序...")
            return self.restart_main_bot()
        elif connection_lost:
            print("检测到账号掉线，正在运行登录机器人...")
            if self.run_login_bot():
                # 登录成功后重启主bot程序
                time.sleep(5)  # 等待登录完成
                print("登录成功，正在重启主bot程序...")
                return self.restart_main_bot()
            else:
                print("登录机器人执行失败")
                return False
        else:
            print("程序运行正常，无需操作")
            return True

def main():
    """主函数"""
    decision = IntelligentDecision()
    decision.make_decision()

if __name__ == "__main__":
    main()