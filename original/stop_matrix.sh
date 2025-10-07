#!/bin/bash
# 停止所有矩阵节点的脚本

echo "正在停止DRRR Bot维持矩阵系统..."

# 停止节点A
if [ -f matrix_node_A.pid ]; then
    NODE_A_PID=$(cat matrix_node_A.pid)
    echo "正在停止矩阵节点A (PID: $NODE_A_PID)..."
    kill $NODE_A_PID 2>/dev/null
    rm -f matrix_node_A.pid
fi

# 停止节点B
if [ -f matrix_node_B.pid ]; then
    NODE_B_PID=$(cat matrix_node_B.pid)
    echo "正在停止矩阵节点B (PID: $NODE_B_PID)..."
    kill $NODE_B_PID 2>/dev/null
    rm -f matrix_node_B.pid
fi

# 停止节点C
if [ -f matrix_node_C.pid ]; then
    NODE_C_PID=$(cat matrix_node_C.pid)
    echo "正在停止矩阵节点C (PID: $NODE_C_PID)..."
    kill $NODE_C_PID 2>/dev/null
    rm -f matrix_node_C.pid
fi

# 强制停止所有矩阵节点进程
echo "正在强制停止所有矩阵节点进程..."
pkill -f "matrix_node.py" 2>/dev/null

echo "所有矩阵节点已停止"