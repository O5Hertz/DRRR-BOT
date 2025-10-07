package com.drrr.bot;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

public class MainActivity extends Activity {
    private static final String TAG = "MainActivity";
    
    private Button startButton;
    private Button stopButton;
    private Button settingsButton;
    private TextView statusText;
    private TextView logText;
    
    // 机器人服务管理器
    private BotServiceManager botServiceManager;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // 初始化UI组件
        initUI();
        
        // 初始化机器人服务管理器
        botServiceManager = new BotServiceManager(this);
        
        // 设置事件监听器
        setupEventListeners();
        
        // 更新UI状态
        updateUI();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // 每次回到界面时更新状态
        updateUI();
    }
    
    private void initUI() {
        startButton = findViewById(R.id.startButton);
        stopButton = findViewById(R.id.stopButton);
        settingsButton = findViewById(R.id.settingsButton);
        statusText = findViewById(R.id.statusText);
        logText = findViewById(R.id.logText);
    }
    
    private void setupEventListeners() {
        startButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startBot();
            }
        });
        
        stopButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                stopBot();
            }
        });
        
        settingsButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openSettings();
            }
        });
    }
    
    private void startBot() {
        // 启动机器人服务
        botServiceManager.startBotService();
        updateUI();
    }
    
    private void stopBot() {
        // 停止机器人服务
        botServiceManager.stopBotService();
        updateUI();
    }
    
    private void openSettings() {
        // 打开设置界面
        // TODO: 实现设置界面跳转
    }
    
    private void updateUI() {
        // 检查机器人服务状态并更新UI
        boolean isRunning = botServiceManager.isBotServiceRunning();
        
        // 更新状态文本
        statusText.setText(isRunning ? R.string.bot_running : R.string.bot_stopped);
        statusText.setTextColor(getResources().getColor(
            isRunning ? android.R.color.holo_green_dark : android.R.color.darker_gray));
        
        // 更新按钮状态
        startButton.setEnabled(!isRunning);
        stopButton.setEnabled(isRunning);
        
        // 更新日志显示
        updateLogDisplay();
    }
    
    private void updateLogDisplay() {
        // TODO: 实现日志显示逻辑
        // 这里可以显示机器人的运行日志
        logText.setText("日志信息将在此显示...");
    }
}