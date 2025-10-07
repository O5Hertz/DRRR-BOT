package com.drrr.bot;

import android.content.Context;
import android.content.Intent;
import android.util.Log;

public class BotServiceManager {
    private static final String TAG = "BotServiceManager";
    
    private Context context;
    
    public BotServiceManager(Context context) {
        this.context = context;
    }
    
    /**
     * 启动机器人服务
     */
    public void startBotService() {
        try {
            Intent serviceIntent = new Intent(context, BotService.class);
            context.startService(serviceIntent);
            Log.d(TAG, "Bot service started");
        } catch (Exception e) {
            Log.e(TAG, "Failed to start bot service", e);
        }
    }
    
    /**
     * 停止机器人服务
     */
    public void stopBotService() {
        try {
            Intent serviceIntent = new Intent(context, BotService.class);
            context.stopService(serviceIntent);
            Log.d(TAG, "Bot service stopped");
        } catch (Exception e) {
            Log.e(TAG, "Failed to stop bot service", e);
        }
    }
    
    /**
     * 检查机器人服务是否正在运行
     * @return true if running, false otherwise
     */
    public boolean isBotServiceRunning() {
        // TODO: 实现检查服务运行状态的逻辑
        // 由于Android 5.0之后无法直接查询服务状态，需要通过其他方式实现
        // 比如使用SharedPreferences或数据库记录状态
        return false;
    }
}