#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键启动所有DRRR Bot相关服务的Python程序
"""

import subprocess
import time
import os
import signal
import sys

class DRRRBotLauncher:
    """DRRR机器人服务启动器"""
    
    def __init__(self):
        self.bot_dir = "/storage/emulated/0/壹号工作区/drrr_bot_standalone"
        self.bot_script = "enhanced_ai_bot.py"
        self.monitor_script = "enhanced_monitor.sh"
        self.pids = {}
        
    def setup_environment(self):
        """设置运行环境"""
        print("正在设置运行环境...")
        # 确保脚本具有执行权限
        try:
            subprocess.run(['chmod', '+x', os.path.join(self.bot_dir, self.monitor_script)], 
                          cwd=self.bot_dir, check=True)
            print("脚本权限设置完成")
        except subprocess.CalledProcessError as e:
            print(f"设置脚本权限时出错: {e}")
            
    def is_process_running(self, process_name):
        """检查进程是否正在运行"""
        try:
            result = subprocess.run(['pgrep', '-f', process_name], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def stop_existing_processes(self):
        """停止已存在的相关进程"""
        print("正在停止已存在的相关进程...")
        
        # 停止主Bot进程
        if self.is_process_running(self.bot_script):
            print("停止主Bot进程...")
            subprocess.run(['pkill', '-f', self.bot_script], capture_output=True)
            time.sleep(2)
            
        # 停止监控进程
        if self.is_process_running(self.monitor_script):
            print("停止监控进程...")
            subprocess.run(['pkill', '-f', self.monitor_script], capture_output=True)
            time.sleep(2)
            
        print("已停止所有相关进程")
        
    def start_main_bot(self):
        """启动主Bot程序"""
        print("正在启动主Bot程序...")
        try:
            # 切换到Bot目录
            os.chdir(self.bot_dir)
            
            # 打开日志文件
            bot_log = open('bot.log', 'a')
            
            # 启动Bot程序，将输出重定向到日志文件
            process = subprocess.Popen(['nohup', 'python3', self.bot_script], 
                                     stdout=bot_log, 
                                     stderr=bot_log,
                                     preexec_fn=os.setsid)
            
            self.pids['bot'] = process.pid
            print(f"主Bot程序已启动，PID: {process.pid}")
            return True
        except Exception as e:
            print(f"启动主Bot程序失败: {e}")
            return False
            
    def start_monitor_service(self):
        """启动监控服务"""
        print("正在启动监控服务...")
        try:
            # 切换到Bot目录
            os.chdir(self.bot_dir)
            
            # 打开监控日志文件
            monitor_log = open('monitor_output.log', 'a')
            
            # 启动监控程序，将输出重定向到日志文件
            process = subprocess.Popen(['nohup', 'bash', self.monitor_script], 
                                     stdout=monitor_log, 
                                     stderr=monitor_log,
                                     preexec_fn=os.setsid)
            
            self.pids['monitor'] = process.pid
            print(f"监控服务已启动，PID: {process.pid}")
            return True
        except Exception as e:
            print(f"启动监控服务失败: {e}")
            return False
            
    def save_pids(self):
        """保存进程ID到文件"""
        try:
            with open(os.path.join(self.bot_dir, 'bot.pid'), 'w') as f:
                f.write(str(self.pids.get('bot', '')))
                
            with open(os.path.join(self.bot_dir, 'monitor.pid'), 'w') as f:
                f.write(str(self.pids.get('monitor', '')))
                
            print("进程ID已保存到文件")
        except Exception as e:
            print(f"保存进程ID时出错: {e}")
            
    def check_services_status(self):
        """检查服务状态"""
        print("\n正在检查服务状态...")
        
        bot_running = self.is_process_running(self.bot_script)
        monitor_running = self.is_process_running(self.monitor_script)
        
        print(f"主Bot程序状态: {'运行中' if bot_running else '未运行'}")
        print(f"监控服务状态: {'运行中' if monitor_running else '未运行'}")
        
        return bot_running and monitor_running
        
    def start_all_services(self):
        """启动所有服务"""
        print("=" * 50)
        print("DRRR Bot一键启动程序")
        print("=" * 50)
        
        try:
            # 设置环境
            self.setup_environment()
            
            # 停止已存在的进程
            self.stop_existing_processes()
            
            # 启动主Bot程序
            if not self.start_main_bot():
                print("启动主Bot程序失败")
                return False
                
            # 等待一段时间确保Bot启动
            time.sleep(3)
            
            # 启动监控服务
            if not self.start_monitor_service():
                print("启动监控服务失败")
                return False
                
            # 保存进程ID
            self.save_pids()
            
            # 检查服务状态
            time.sleep(2)
            if self.check_services_status():
                print("\n所有服务已成功启动！")
                return True
            else:
                print("\n部分服务启动失败！")
                return False
                
        except KeyboardInterrupt:
            print("\n用户中断启动过程")
            return False
        except Exception as e:
            print(f"\n启动过程中发生错误: {e}")
            return False
            
    def stop_all_services(self):
        """停止所有服务"""
        print("正在停止所有服务...")
        self.stop_existing_processes()
        print("所有服务已停止")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'stop':
        # 停止服务
        launcher = DRRRBotLauncher()
        launcher.stop_all_services()
    else:
        # 启动服务
        launcher = DRRRBotLauncher()
        success = launcher.start_all_services()
        
        if success:
            print("\n启动完成！机器人和监控服务正在后台运行。")
            print("您可以使用 'python3 start_all_services.py stop' 来停止所有服务。")
        else:
            print("\n启动失败！请检查日志文件以获取更多信息。")
            sys.exit(1)

if __name__ == "__main__":
    main()