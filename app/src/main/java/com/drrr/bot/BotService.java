package com.drrr.bot;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;

public class BotService extends Service {
    private static final String TAG = "BotService";
    
    // 机器人核心逻辑实例
    private DRRRBotCore botCore;
    
    // 服务运行状态
    private boolean isRunning = false;
    
    @Override
    public void onCreate() {
        super.onCreate();
        Log.d(TAG, "BotService created");
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.d(TAG, "BotService started");
        
        // 如果服务已经在运行，则不重复启动
        if (!isRunning) {
            startBot();
        }
        
        // 返回START_STICKY以确保服务在被杀死后会重启
        return START_STICKY;
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "BotService destroyed");
        stopBot();
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        // 不支持绑定服务
        return null;
    }
    
    /**
     * 启动机器人核心逻辑
     */
    private void startBot() {
        Log.d(TAG, "Starting bot core logic");
        
        try {
            // 初始化机器人核心逻辑
            botCore = new DRRRBotCore();
            
            // 启动机器人
            botCore.start();
            
            // 更新运行状态
            isRunning = true;
            
            Log.d(TAG, "Bot core logic started successfully");
        } catch (Exception e) {
            Log.e(TAG, "Failed to start bot core logic", e);
        }
    }
    
    /**
     * 停止机器人核心逻辑
     */
    private void stopBot() {
        Log.d(TAG, "Stopping bot core logic");
        
        try {
            // 停止机器人
            if (botCore != null) {
                botCore.stop();
                botCore = null;
            }
            
            // 更新运行状态
            isRunning = false;
            
            Log.d(TAG, "Bot core logic stopped successfully");
        } catch (Exception e) {
            Log.e(TAG, "Failed to stop bot core logic", e);
        }
    }
    
    /**
     * 检查机器人是否正在运行
     * @return true if running, false otherwise
     */
    public boolean isBotRunning() {
        return isRunning && botCore != null && botCore.isRunning();
    }
}