package com.drrr.bot;

import android.util.Log;
import java.util.List;
import java.util.ArrayList;

public class RoomManager {
    private static final String TAG = "RoomManager";
    
    // 管理员列表
    private List<String> admins;
    
    // 封禁用户列表
    private List<String> bannedUsers;
    
    // 白名单用户列表
    private List<String> whitelist;
    
    // 黑名单用户列表
    private List<String> blacklist;
    
    // 房间设置
    private boolean allowDM = true;
    private boolean allowMusic = true;
    private int maxUsers = 0; // 0表示无限制
    
    public RoomManager() {
        admins = new ArrayList<>();
        bannedUsers = new ArrayList<>();
        whitelist = new ArrayList<>();
        blacklist = new ArrayList<>();
        
        // 添加默认管理员
        admins.add("52Hertz");
        
        Log.d(TAG, "RoomManager initialized");
    }
    
    /**
     * 添加管理员
     * @param tripcode 用户标识
     * @return 结果消息
     */
    public String addAdmin(String tripcode) {
        if (!admins.contains(tripcode)) {
            admins.add(tripcode);
            return "已添加管理员: " + tripcode;
        } else {
            return "用户已经是管理员: " + tripcode;
        }
    }
    
    /**
     * 移除管理员
     * @param tripcode 用户标识
     * @return 结果消息
     */
    public String removeAdmin(String tripcode) {
        if (admins.contains(tripcode)) {
            admins.remove(tripcode);
            return "已移除管理员: " + tripcode;
        } else {
            return "用户不是管理员: " + tripcode;
        }
    }
    
    /**
     * 检查是否为管理员
     * @param tripcode 用户标识
     * @return true if admin, false otherwise
     */
    public boolean isAdmin(String tripcode) {
        return admins.contains(tripcode);
    }
    
    /**
     * 封禁用户
     * @param userId 用户ID
     * @param tripcode 用户标识
     * @return 结果消息
     */
    public String banUser(String userId, String tripcode) {
        if (!bannedUsers.contains(userId)) {
            bannedUsers.add(userId);
            return "已封禁用户: " + userId;
        } else {
            return "用户已被封禁: " + userId;
        }
    }
    
    /**
     * 解封用户
     * @param userId 用户ID
     * @return 结果消息
     */
    public String unbanUser(String userId) {
        if (bannedUsers.contains(userId)) {
            bannedUsers.remove(userId);
            return "已解封用户: " + userId;
        } else {
            return "用户未被封禁: " + userId;
        }
    }
    
    /**
     * 检查用户是否被封禁
     * @param userId 用户ID
     * @return true if banned, false otherwise
     */
    public boolean isBanned(String userId) {
        return bannedUsers.contains(userId);
    }
    
    // Getter和Setter方法
    public boolean isAllowDM() {
        return allowDM;
    }
    
    public void setAllowDM(boolean allowDM) {
        this.allowDM = allowDM;
    }
    
    public boolean isAllowMusic() {
        return allowMusic;
    }
    
    public void setAllowMusic(boolean allowMusic) {
        this.allowMusic = allowMusic;
    }
    
    public int getMaxUsers() {
        return maxUsers;
    }
    
    public void setMaxUsers(int maxUsers) {
        this.maxUsers = maxUsers;
    }
}