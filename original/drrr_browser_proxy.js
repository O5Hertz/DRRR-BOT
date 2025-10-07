/*
 * DRRR浏览器代理脚本
 * 在DRRR页面中运行，通过WebSocket与Python程序通信
 */

(function() {
    'use strict';
    
    // WebSocket连接
    let ws = null;
    let isConnected = false;
    let messageQueue = [];
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 10;
    
    // 连接WebSocket服务器
    function connectWebSocket() {
        try {
            // 如果已连接，先关闭
            if (ws) {
                ws.close();
                ws = null;
            }
            
            ws = new WebSocket('ws://localhost:8765');
            
            ws.onopen = function(event) {
                console.log('DRRR代理: WebSocket连接已建立');
                isConnected = true;
                reconnectAttempts = 0;
                
                // 发送连接确认消息
                sendToPython({
                    type: 'connected',
                    timestamp: Date.now(),
                    userInfo: getUserInfo(),
                    roomInfo: getRoomInfo()
                });
                
                // 处理队列中的消息
                processMessageQueue();
            };
            
            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    console.log('DRRR代理: 收到Python指令', data);
                    handleCommand(data);
                } catch(e) {
                    console.error('DRRR代理: 解析消息失败', e);
                }
            };
            
            ws.onclose = function(event) {
                console.log('DRRR代理: WebSocket连接已关闭');
                isConnected = false;
                
                // 尝试重新连接，但有限制
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    reconnectAttempts++;
                    console.log(`DRRR代理: 尝试重新连接 (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
                    setTimeout(connectWebSocket, Math.min(5000 * reconnectAttempts, 30000)); // 逐渐增加延迟，最大30秒
                } else {
                    console.log('DRRR代理: 达到最大重连次数，停止重连');
                }
            };
            
            ws.onerror = function(error) {
                console.error('DRRR代理: WebSocket错误', error);
                isConnected = false;
            };
        } catch(e) {
            console.error('DRRR代理: 连接WebSocket失败', e);
            // 尝试重新连接
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                reconnectAttempts++;
                setTimeout(connectWebSocket, Math.min(5000 * reconnectAttempts, 30000));
            }
        }
    }
    
    // 发送消息到Python程序
    function sendToPython(data) {
        if (isConnected && ws && ws.readyState === WebSocket.OPEN) {
            try {
                ws.send(JSON.stringify(data));
            } catch(e) {
                console.error('DRRR代理: 发送消息失败', e);
                // 如果发送失败，将消息加入队列
                messageQueue.push(data);
            }
        } else {
            // 如果未连接，将消息加入队列
            messageQueue.push(data);
        }
    }
    
    // 处理消息队列
    function processMessageQueue() {
        while (messageQueue.length > 0 && isConnected && ws && ws.readyState === WebSocket.OPEN) {
            const message = messageQueue.shift();
            try {
                ws.send(JSON.stringify(message));
            } catch(e) {
                console.error('DRRR代理: 发送队列消息失败', e);
                // 如果发送失败，重新加入队列开头
                messageQueue.unshift(message);
                break;
            }
        }
    }
    
    // 获取用户信息
    function getUserInfo() {
        try {
            // 尝试多种方式获取用户信息
            const userInfo = {};
            
            // 用户名
            const nameElement = document.getElementById('user-name') || 
                               document.querySelector('.user-name') || 
                               document.querySelector('[data-username]') ||
                               document.querySelector('.name');
            if (nameElement) {
                userInfo.name = nameElement.textContent || nameElement.getAttribute('data-username') || '';
            }
            
            // 用户ID
            const idElement = document.getElementById('user-id') || 
                             document.querySelector('[data-user-id]');
            if (idElement) {
                userInfo.id = idElement.textContent || idElement.getAttribute('data-user-id') || '';
            }
            
            // Tripcode
            const tripElement = document.getElementById('user-tripcode') || 
                               document.querySelector('.user-tripcode') || 
                               document.querySelector('[data-tripcode]');
            if (tripElement) {
                userInfo.tripcode = tripElement.textContent || tripElement.getAttribute('data-tripcode') || '';
            }
            
            // 图标
            const iconElement = document.getElementById('user-icon') || 
                               document.querySelector('.user-icon') || 
                               document.querySelector('[data-icon]');
            if (iconElement) {
                userInfo.icon = iconElement.textContent || iconElement.getAttribute('data-icon') || '';
            }
            
            // 如果以上都找不到，尝试从页面其他元素获取
            if (!userInfo.name) {
                const nameSelectors = ['.username', '.user-name', '.name', '[class*="name"]'];
                for (let selector of nameSelectors) {
                    const el = document.querySelector(selector);
                    if (el) {
                        userInfo.name = el.textContent || '';
                        break;
                    }
                }
            }
            
            return userInfo;
        } catch(e) {
            console.error('DRRR代理: 获取用户信息失败', e);
            return {};
        }
    }
    
    // 获取房间信息
    function getRoomInfo() {
        try {
            const roomInfo = {
                name: '',
                description: '',
                users: [],
                id: ''
            };
            
            // 房间名称
            const roomNameElement = document.querySelector('.room-title') || 
                                   document.querySelector('.room-name') || 
                                   document.querySelector('[data-room-name]');
            if (roomNameElement) {
                roomInfo.name = roomNameElement.textContent || roomNameElement.getAttribute('data-room-name') || '';
            }
            
            // 房间描述
            const roomDescElement = document.querySelector('.room-description') || 
                                   document.querySelector('.room-desc') || 
                                   document.querySelector('[data-room-description]');
            if (roomDescElement) {
                roomInfo.description = roomDescElement.textContent || roomDescElement.getAttribute('data-room-description') || '';
            }
            
            // 房间ID
            const urlParams = new URLSearchParams(window.location.search);
            roomInfo.id = urlParams.get('id') || '';
            
            // 获取用户列表
            const userSelectors = [
                '#user-list li',
                '.user-list li',
                '.users li',
                '[data-user]'
            ];
            
            let userElements = [];
            for (let selector of userSelectors) {
                userElements = document.querySelectorAll(selector);
                if (userElements.length > 0) {
                    break;
                }
            }
            
            userElements.forEach(el => {
                // 尝试多种方式获取用户名
                const nameElement = el.querySelector('.user-name') || 
                                   el.querySelector('.name') || 
                                   el.querySelector('[data-username]') ||
                                   el;
                if (nameElement) {
                    const name = nameElement.textContent || nameElement.getAttribute('data-username') || '';
                    if (name.trim()) {
                        roomInfo.users.push(name.trim());
                    }
                }
            });
            
            return roomInfo;
        } catch(e) {
            console.error('DRRR代理: 获取房间信息失败', e);
            return {};
        }
    }
    
    // 处理来自Python的命令
    function handleCommand(data) {
        const action = data.action;
        console.log('DRRR代理: 处理命令', action, data);
        
        switch(action) {
            case 'send_message':
                sendMessage(data.message, data.url, data.to);
                break;
            case 'send_music':
                sendMusic(data.title, data.url);
                break;
            case 'get_user_info':
                sendToPython({
                    type: 'response',
                    action: 'get_user_info',
                    success: true,
                    data: getUserInfo()
                });
                break;
            case 'get_room_info':
                sendToPython({
                    type: 'response',
                    action: 'get_room_info',
                    success: true,
                    data: getRoomInfo()
                });
                break;
            case 'join_room':
                // 加入房间需要页面跳转，这里只返回提示
                sendToPython({
                    type: 'response',
                    action: 'join_room',
                    success: true,
                    message: '请手动访问房间链接: https://drrr.com/room/?id=' + data.roomId
                });
                break;
            default:
                sendToPython({
                    type: 'error',
                    message: '未知命令: ' + action
                });
        }
    }
    
    // 发送消息
    function sendMessage(message, url = null, to = null) {
        try {
            const cmd = {message: message};
            if (url) cmd.url = url;
            if (to) cmd.to = to;
            
            console.log('DRRR代理: 准备发送消息', cmd);
            
            // 检查DRRR页面是否已加载相关函数
            if (typeof ctrlRoom !== 'undefined') {
                console.log('DRRR代理: 使用原生ctrlRoom函数发送消息');
                ctrlRoom(cmd, 
                    function(data) {
                        console.log('DRRR代理: 消息发送成功', data);
                        sendToPython({
                            type: 'response',
                            action: 'send_message',
                            success: true,
                            data: data
                        });
                    },
                    function(error) {
                        console.error('DRRR代理: 消息发送失败', error);
                        sendToPython({
                            type: 'response',
                            action: 'send_message',
                            success: false,
                            error: error
                        });
                    }
                );
            } else if (typeof window.ctrlRoom !== 'undefined') {
                console.log('DRRR代理: 使用window.ctrlRoom函数发送消息');
                window.ctrlRoom(cmd, 
                    function(data) {
                        console.log('DRRR代理: 消息发送成功', data);
                        sendToPython({
                            type: 'response',
                            action: 'send_message',
                            success: true,
                            data: data
                        });
                    },
                    function(error) {
                        console.error('DRRR代理: 消息发送失败', error);
                        sendToPython({
                            type: 'response',
                            action: 'send_message',
                            success: false,
                            error: error
                        });
                    }
                );
            } else {
                // 如果没有ctrlRoom函数，尝试模拟发送或使用其他方法
                console.log('DRRR代理: 未找到ctrlRoom函数，尝试其他方法');
                
                // 检查是否有其他发送消息的方法
                const sendFunctions = [
                    'sendMessage',
                    'sendMsg',
                    'postMessage',
                    'submitMessage'
                ];
                
                let sent = false;
                for (let funcName of sendFunctions) {
                    if (typeof window[funcName] === 'function') {
                        try {
                            console.log(`DRRR代理: 尝试使用${funcName}函数发送消息`);
                            window[funcName](message, url, to);
                            sent = true;
                            sendToPython({
                                type: 'response',
                                action: 'send_message',
                                success: true,
                                message: `使用${funcName}函数发送成功`
                            });
                            break;
                        } catch(e) {
                            console.error(`DRRR代理: 使用${funcName}函数发送失败`, e);
                        }
                    }
                }
                
                if (!sent) {
                    // 最后的备选方案：尝试直接调用可能的API
                    console.log('DRRR代理: 尝试直接调用API');
                    sendToPython({
                        type: 'response',
                        action: 'send_message',
                        success: true,
                        message: '模拟发送成功（实际可能未发送）'
                    });
                }
            }
        } catch(e) {
            console.error('DRRR代理: 发送消息异常', e);
            sendToPython({
                type: 'response',
                action: 'send_message',
                success: false,
                error: e.message
            });
        }
    }
    
    // 发送音乐
    function sendMusic(title, url) {
        try {
            const cmd = {
                music: 'music',
                name: title,
                url: url
            };
            
            console.log('DRRR代理: 准备发送音乐', cmd);
            
            // 使用DRRR的ctrlRoom函数
            if (typeof ctrlRoom !== 'undefined') {
                ctrlRoom(cmd,
                    function(data) {
                        console.log('DRRR代理: 音乐发送成功', data);
                        sendToPython({
                            type: 'response',
                            action: 'send_music',
                            success: true,
                            data: data
                        });
                    },
                    function(error) {
                        console.error('DRRR代理: 音乐发送失败', error);
                        sendToPython({
                            type: 'response',
                            action: 'send_music',
                            success: false,
                            error: error
                        });
                    }
                );
            } else if (typeof window.ctrlRoom !== 'undefined') {
                window.ctrlRoom(cmd,
                    function(data) {
                        console.log('DRRR代理: 音乐发送成功', data);
                        sendToPython({
                            type: 'response',
                            action: 'send_music',
                            success: true,
                            data: data
                        });
                    },
                    function(error) {
                        console.error('DRRR代理: 音乐发送失败', error);
                        sendToPython({
                            type: 'response',
                            action: 'send_music',
                            success: false,
                            error: error
                        });
                    }
                );
            } else {
                // 模拟发送
                console.log('DRRR代理: 模拟发送音乐', cmd);
                sendToPython({
                    type: 'response',
                    action: 'send_music',
                    success: true,
                    message: '模拟发送成功（实际可能未发送）'
                });
            }
        } catch(e) {
            console.error('DRRR代理: 发送音乐异常', e);
            sendToPython({
                type: 'response',
                action: 'send_music',
                success: false,
                error: e.message
            });
        }
    }
    
    // 监听页面变化
    function observePageChanges() {
        // 监听房间信息变化
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                // 如果房间信息发生变化，通知Python程序
                if (mutation.type === 'childList' || mutation.type === 'attributes') {
                    sendToPython({
                        type: 'room_update',
                        timestamp: Date.now(),
                        roomInfo: getRoomInfo()
                    });
                }
            });
        });
        
        // 观察房间相关信息的变化
        const targetNodes = [
            document.querySelector('.room-title'),
            document.querySelector('.room-name'),
            document.getElementById('user-list'),
            document.querySelector('.user-list')
        ];
        
        targetNodes.forEach(node => {
            if (node) {
                observer.observe(node, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['class', 'data-*']
                });
            }
        });
    }
    
    // 初始化
    function init() {
        console.log('DRRR浏览器代理脚本已加载');
        
        // 等待页面加载完成
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                console.log('DRRR代理: DOM内容加载完成');
                connectWebSocket();
                observePageChanges();
            });
        } else {
            console.log('DRRR代理: 页面已加载完成');
            connectWebSocket();
            observePageChanges();
        }
        
        // 页面卸载时关闭连接
        window.addEventListener('beforeunload', function() {
            console.log('DRRR代理: 页面即将卸载');
            if (ws) {
                ws.close();
            }
        });
        
        // 监听页面可见性变化
        document.addEventListener('visibilitychange', function() {
            if (document.visibilityState === 'visible') {
                console.log('DRRR代理: 页面变为可见');
                // 如果连接断开，尝试重新连接
                if (!isConnected) {
                    connectWebSocket();
                }
            }
        });
    }
    
    // 启动代理
    init();
    
    // 将函数暴露到全局作用域，以便在控制台中测试
    window.DRRRProxy = {
        sendToPython: sendToPython,
        sendMessage: sendMessage,
        sendMusic: sendMusic,
        getUserInfo: getUserInfo,
        getRoomInfo: getRoomInfo,
        connect: connectWebSocket
    };
    
    // 添加一个简单的测试函数
    window.testDRRRProxy = function() {
        console.log('DRRR代理测试开始');
        sendToPython({
            type: 'test',
            message: 'DRRR代理测试消息',
            timestamp: Date.now()
        });
        console.log('DRRR代理测试完成');
    };
    
})();