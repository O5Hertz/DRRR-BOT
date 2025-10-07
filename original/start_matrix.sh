#!/bin/bash
# 启动所有矩阵节点的脚本

echo "正在启动DRRR Bot维持矩阵系统..."

# 确保脚本具有执行权限
chmod +x /storage/self/primary/壹号工作区/drrr_bot_standalone_drrr机器人/matrix_node.py

# 启动节点A
echo "正在启动矩阵节点A..."
cd /storage/self/primary/壹号工作区/drrr_bot_standalone_drrr机器人
nohup python3 matrix_node.py A > matrix_node_A.log 2>&1 &
NODE_A_PID=$!
echo "矩阵节点A已启动，PID: $NODE_A_PID"

# 等待几秒再启动其他节点
sleep 5

# 启动节点B
echo "正在启动矩阵节点B..."
cd /storage/self/primary/壹号工作区/drrr_bot_standalone_drrr机器人
nohup python3 matrix_node.py B > matrix_node_B.log 2>&1 &
NODE_B_PID=$!
echo "矩阵节点B已启动，PID: $NODE_B_PID"

# 等待几秒再启动其他节点
sleep 5

# 启动节点C
echo "正在启动矩阵节点C..."
cd /storage/self/primary/壹号工作区/drrr_bot_standalone_drrr机器人
nohup python3 matrix_node.py C > matrix_node_C.log 2>&1 &
NODE_C_PID=$!
echo "矩阵节点C已启动，PID: $NODE_C_PID"

# 保存PID到文件
echo $NODE_A_PID > matrix_node_A.pid
echo $NODE_B_PID > matrix_node_B.pid
echo $NODE_C_PID > matrix_node_C.pid

echo "所有矩阵节点已启动完成"
echo "节点A PID: $NODE_A_PID"
echo "节点B PID: $NODE_B_PID"
echo "节点C PID: $NODE_C_PID"

echo "维持矩阵系统启动完成"