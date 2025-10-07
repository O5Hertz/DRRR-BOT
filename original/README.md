# DRRR 聊天室机器人

## 概述

DRRR聊天室机器人是一个增强版AI机器人，具有用户欢迎、指令权限控制、AI对话和音乐点播功能。

## 功能特性

- 增强版AI机器人，具有用户欢迎、指令权限控制、AI对话和音乐点播功能
- 只有管理员"52Hertz"可以执行管理命令
- 支持AI对话功能，通过指定API进行智能对话
- 音乐点播功能，支持添加、播放和管理音乐播放列表
- 所有命令以"/"开头，便于识别和管理
- 智能监控系统：自动监控机器人状态并进行智能决策
- 维持矩阵系统：分布式高可用监控，确保机器人稳定运行
- QQ音乐搜索：支持搜索QQ音乐并直接输出链接
- 文本转语音：支持将文本转换为语音并直接输出链接

## 项目结构

```
drrr_bot_standalone_drrr机器人/
├── api/                     # API模块
├── modules/                 # 功能模块
├── success_versions/        # 成功版本备份
├── utils/                   # 工具模块
├── enhanced_ai_bot.py       # 增强版AI机器人主程序
├── bot_user_manual.md       # 用户手册
├── bot_ctl.sh               # 便捷启动脚本
├── bot-ctl                  # 便捷控制脚本
├── drrr_browser_proxy.js    # 浏览器代理脚本
├── unified_launcher.py      # 统一启动程序
├── matrix_node.py           # 维持矩阵节点
├── start_matrix.sh          # 启动矩阵系统
├── stop_matrix.sh           # 停止矩阵系统
├── enhanced_monitor.sh      # 增强监控脚本
├── requirements.txt         # 依赖包列表
└── README.md                # 本文件
```

## 依赖包

- requests>=2.25.1
- aiohttp>=3.7.4
- websockets>=9.1

## 统一管理

```bash
# 启动完整系统
bash bot_ctl.sh start

# 停止完整系统
bash bot_ctl.sh stop

# 重启完整系统
bash bot_ctl.sh restart

# 查看系统状态
bash bot_ctl.sh status
```