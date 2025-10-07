package com.drrr.bot;

import android.util.Log;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

public class EventHandler {
    private static final String TAG = "EventHandler";
    
    // 事件处理器映射
    private Map<String, List<EventHandlerCallback>> eventHandlers;
    
    // 命令处理器映射
    private Map<String, EventHandlerCallback> commandHandlers;
    
    public EventHandler() {
        eventHandlers = new HashMap<>();
        commandHandlers = new HashMap<>();
        
        // 初始化事件类型
        eventHandlers.put("join", new ArrayList<EventHandlerCallback>());
        eventHandlers.put("leave", new ArrayList<EventHandlerCallback>());
        eventHandlers.put("message", new ArrayList<EventHandlerCallback>());
        eventHandlers.put("dm", new ArrayList<EventHandlerCallback>());
        eventHandlers.put("music", new ArrayList<EventHandlerCallback>());
        eventHandlers.put("new_host", new ArrayList<EventHandlerCallback>());
        
        Log.d(TAG, "EventHandler initialized");
    }
    
    /**
     * 注册事件处理器
     * @param eventType 事件类型
     * @param handler 处理器回调
     */
    public void registerEventHandler(String eventType, EventHandlerCallback handler) {
        if (eventHandlers.containsKey(eventType)) {
            eventHandlers.get(eventType).add(handler);
            Log.d(TAG, "Registered event handler for: " + eventType);
        } else {
            Log.w(TAG, "Unknown event type: " + eventType);
        }
    }
    
    /**
     * 注册命令处理器
     * @param command 命令
     * @param handler 处理器回调
     */
    public void registerCommandHandler(String command, EventHandlerCallback handler) {
        commandHandlers.put(command.toLowerCase(), handler);
        Log.d(TAG, "Registered command handler for: " + command);
    }
    
    /**
     * 处理事件
     * @param eventType 事件类型
     * @param data 事件数据
     */
    public void handleEvent(String eventType, Map<String, Object> data) {
        if (eventHandlers.containsKey(eventType)) {
            for (EventHandlerCallback handler : eventHandlers.get(eventType)) {
                try {
                    handler.onEvent(data);
                } catch (Exception e) {
                    Log.e(TAG, "Error in event handler for: " + eventType, e);
                }
            }
        }
    }
    
    /**
     * 处理消息
     * @param message 消息内容
     * @param user 用户信息
     */
    public void handleMessage(String message, Map<String, Object> user) {
        // 检查是否为命令
        if (message.startsWith("/")) {
            handleCommand(message, user);
        } else {
            // 处理普通消息事件
            Map<String, Object> data = new HashMap<>();
            data.put("message", message);
            data.put("user", user);
            handleEvent("message", data);
        }
    }
    
    /**
     * 处理命令
     * @param message 命令消息
     * @param user 用户信息
     */
    private void handleCommand(String message, Map<String, Object> user) {
        // 解析命令
        String[] parts = message.substring(1).split(" ", 2);
        String command = parts[0].toLowerCase();
        String args = parts.length > 1 ? parts[1] : "";
        
        // 查找命令处理器
        if (commandHandlers.containsKey(command)) {
            Map<String, Object> data = new HashMap<>();
            data.put("command", command);
            data.put("args", args);
            data.put("user", user);
            
            try {
                commandHandlers.get(command).onEvent(data);
            } catch (Exception e) {
                Log.e(TAG, "Error in command handler for: " + command, e);
            }
        } else {
            // 未找到命令处理器
            Log.d(TAG, "No handler found for command: " + command);
        }
    }
    
    /**
     * 事件处理器回调接口
     */
    public interface EventHandlerCallback {
        void onEvent(Map<String, Object> data);
    }
}