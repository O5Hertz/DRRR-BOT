#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DRRR Bot统一启动程序
一键启动所有相关服务：主Bot、监控程序、维持矩阵
"""

import subprocess
import time
import os
import sys
import signal
import json

class UnifiedLauncher:
    """统一启动器"""
    
    def __init__(self):
        self.bot_dir = "/storage/self/primary/壹号工作区/drrr_bot_standalone_drrr机器人"
        self.pids = {}
        self.is_running = True
        
    def setup_environment(self):
        """设置运行环境"""
        print("正在设置运行环境...")
        try:
            # 确保所有脚本具有执行权限
            scripts = [
                'enhanced_monitor.sh',
                'start_matrix.sh',
                'stop_matrix.sh',
                'matrix_manager.sh'
            ]
            
            for script in scripts:
                script_path = os.path.join(self.bot_dir, script)
                if os.path.exists(script_path):
                    subprocess.run(['chmod', '+x', script_path], 
                                 cwd=self.bot_dir, check=True)
                    
            print("脚本权限设置完成")
        except Exception as e:
            print(f"设置脚本权限时出错: {e}")
            
    def stop_existing_services(self):
        """停止已存在的服务"""
        print("正在停止已存在的相关服务...")
        
        # 停止主Bot进程
        try:
            subprocess.run(['pkill', '-f', 'enhanced_ai_bot.py'], 
                         capture_output=True)
            time.sleep(2)
        except:
            pass
            
        # 停止监控进程
        try:
            subprocess.run(['pkill', '-f', 'enhanced_monitor.sh'], 
                         capture_output=True)
            time.sleep(2)
        except:
            pass
            
        # 停止矩阵节点进程
        try:
            subprocess.run(['pkill', '-f', 'matrix_node.py'], 
                         capture_output=True)
            time.sleep(2)
        except:
            pass
            
        print("已停止所有相关服务")
        
    def start_main_bot(self):
        """启动主Bot程序"""
        print("正在启动主Bot程序...")
        try:
            os.chdir(self.bot_dir)
            
            # 打开日志文件
            bot_log = open('bot.log', 'a')
            
            # 启动Bot程序
            env = os.environ.copy()
            env['PYTHONPATH'] = '/data/data/com.termux/files/usr/lib/python3.12/site-packages'
            process = subprocess.Popen(['nohup', 'python3', 'enhanced_ai_bot.py'], 
                                     stdout=bot_log, 
                                     stderr=bot_log,
                                     preexec_fn=os.setsid,
                                     env=env)
            
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
            os.chdir(self.bot_dir)
            
            # 打开监控日志文件
            monitor_log = open('monitor_output.log', 'a')
            
            # 启动监控程序
            process = subprocess.Popen(['nohup', 'bash', 'enhanced_monitor.sh'], 
                                     stdout=monitor_log, 
                                     stderr=monitor_log,
                                     preexec_fn=os.setsid)
            
            self.pids['monitor'] = process.pid
            print(f"监控服务已启动，PID: {process.pid}")
            return True
        except Exception as e:
            print(f"启动监控服务失败: {e}")
            return False
            
    def start_matrix_system(self):
        """启动维持矩阵系统"""
        print("正在启动维持矩阵系统...")
        try:
            os.chdir(self.bot_dir)
            
            # 使用管理脚本启动矩阵系统
            result = subprocess.run(['bash', 'start_matrix.sh'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("维持矩阵系统启动完成")
                # 读取PID文件获取进程ID
                try:
                    if os.path.exists('matrix_node_A.pid'):
                        with open('matrix_node_A.pid', 'r') as f:
                            self.pids['matrix_A'] = int(f.read().strip())
                    if os.path.exists('matrix_node_B.pid'):
                        with open('matrix_node_B.pid', 'r') as f:
                            self.pids['matrix_B'] = int(f.read().strip())
                    if os.path.exists('matrix_node_C.pid'):
                        with open('matrix_node_C.pid', 'r') as f:
                            self.pids['matrix_C'] = int(f.read().strip())
                except:
                    pass
                return True
            else:
                print(f"启动维持矩阵系统失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"启动维持矩阵系统失败: {e}")
            return False
            
    def save_pids(self):
        """保存进程ID到文件"""
        try:
            pid_info = {
                'timestamp': time.time(),
                'pids': self.pids
            }
            
            with open(os.path.join(self.bot_dir, 'unified_launcher.pid'), 'w') as f:
                json.dump(pid_info, f)
                
            print("进程ID已保存到文件")
        except Exception as e:
            print(f"保存进程ID时出错: {e}")
            
    def check_services_status(self):
        """检查服务状态"""
        print("\n正在检查服务状态...")
        
        bot_running = self.is_process_running('enhanced_ai_bot.py')
        monitor_running = self.is_process_running('enhanced_monitor.sh')
        matrix_running = self.is_process_running('matrix_node.py')
        
        print(f"主Bot程序状态: {'运行中' if bot_running else '未运行'}")
        print(f"监控服务状态: {'运行中' if monitor_running else '未运行'}")
        print(f"维持矩阵状态: {'运行中' if matrix_running else '未运行'}")
        
        return bot_running and monitor_running and matrix_running
        
    def is_process_running(self, process_name):
        """检查进程是否正在运行"""
        try:
            result = subprocess.run(['pgrep', '-f', process_name], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
            
    def start_all_services(self):
        """启动所有服务"""
        print("=" * 50)
        print("DRRR Bot统一启动程序")
        print("=" * 50)
        
        try:
            # 设置环境
            self.setup_environment()
            
            # 停止已存在的服务
            self.stop_existing_services()
            
            # 启动主Bot程序
            print("\n[1/3] 启动主Bot程序...")
            if not self.start_main_bot():
                print("启动主Bot程序失败")
                return False
                
            # 等待一段时间确保Bot启动
            time.sleep(3)
            
            # 启动监控服务
            print("\n[2/3] 启动监控服务...")
            if not self.start_monitor_service():
                print("启动监控服务失败")
                return False
                
            # 等待一段时间
            time.sleep(3)
            
            # 启动维持矩阵系统
            print("\n[3/3] 启动维持矩阵系统...")
            if not self.start_matrix_system():
                print("启动维持矩阵系统失败")
                return False
                
            # 保存进程ID
            self.save_pids()
            
            # 检查服务状态
            time.sleep(5)
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
        
        # 停止矩阵系统
        try:
            os.chdir(self.bot_dir)
            subprocess.run(['bash', 'stop_matrix.sh'], 
                         capture_output=True)
            time.sleep(2)
        except:
            pass
            
        # 停止监控服务
        try:
            subprocess.run(['pkill', '-f', 'enhanced_monitor.sh'], 
                         capture_output=True)
            time.sleep(2)
        except:
            pass
            
        # 停止主Bot程序
        try:
            subprocess.run(['pkill', '-f', 'enhanced_ai_bot.py'], 
                         capture_output=True)
            time.sleep(2)
        except:
            pass
            
        # 删除PID文件
        try:
            pid_files = [
                'bot.pid', 'monitor.pid', 
                'matrix_node_A.pid', 'matrix_node_B.pid', 'matrix_node_C.pid',
                'unified_launcher.pid'
            ]
            
            for pid_file in pid_files:
                pid_path = os.path.join(self.bot_dir, pid_file)
                if os.path.exists(pid_path):
                    os.remove(pid_path)
        except:
            pass
            
        print("所有服务已停止")

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == 'stop':
        # 停止服务
        launcher = UnifiedLauncher()
        launcher.stop_all_services()
        print("所有服务已停止")
    else:
        # 启动服务
        launcher = UnifiedLauncher()
        success = launcher.start_all_services()
        
        if success:
            print("\n启动完成！所有服务正在后台运行。")
            print("您可以使用 'python3 unified_launcher.py stop' 来停止所有服务。")
        else:
            print("\n启动失败！请检查日志文件以获取更多信息。")
            sys.exit(1)

if __name__ == "__main__":
    main()