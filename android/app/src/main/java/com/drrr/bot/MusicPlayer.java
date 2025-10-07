package com.drrr.bot;

import android.util.Log;
import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;

public class MusicPlayer {
    private static final String TAG = "MusicPlayer";
    
    // 播放列表
    private List<Map<String, String>> playlist;
    
    // 当前播放的歌曲
    private Map<String, String> currentSong;
    
    // 播放模式 (album, single, repeat, loop)
    private String playMode = "album";
    
    // 播放状态
    private boolean isPlaying = false;
    
    public MusicPlayer() {
        playlist = new ArrayList<>();
        Log.d(TAG, "MusicPlayer initialized");
    }
    
    /**
     * 添加歌曲到播放列表
     * @param title 歌曲标题
     * @param url 歌曲链接
     * @param singer 歌手（可选）
     * @return 结果消息
     */
    public String addToPlaylist(String title, String url, String singer) {
        Map<String, String> song = new HashMap<>();
        song.put("title", title);
        song.put("url", url);
        song.put("singer", singer != null ? singer : "");
        
        playlist.add(song);
        return "已添加到播放列表: " + formatSongTitle(song);
    }
    
    /**
     * 从播放列表移除歌曲
     * @param index 歌曲索引
     * @return 结果消息
     */
    public String removeFromPlaylist(int index) {
        if (index >= 0 && index < playlist.size()) {
            Map<String, String> song = playlist.remove(index);
            return "已从播放列表移除: " + formatSongTitle(song);
        } else {
            return "索引超出范围";
        }
    }
    
    /**
     * 列出播放列表
     * @return 播放列表内容
     */
    public String listPlaylist() {
        if (playlist.isEmpty()) {
            return "播放列表为空";
        }
        
        StringBuilder result = new StringBuilder("播放列表:\n");
        for (int i = 0; i < playlist.size(); i++) {
            result.append(i + 1).append(". ").append(formatSongTitle(playlist.get(i))).append("\n");
        }
        return result.toString().trim();
    }
    
    /**
     * 格式化歌曲标题
     * @param song 歌曲信息
     * @return 格式化后的标题
     */
    private String formatSongTitle(Map<String, String> song) {
        String title = song.get("title");
        String singer = song.get("singer");
        
        if (singer != null && !singer.isEmpty()) {
            title = title + " - " + singer;
        }
        return title;
    }
    
    /**
     * 设置播放模式
     * @param mode 播放模式
     * @return 结果消息
     */
    public String setPlayMode(String mode) {
        if (isValidPlayMode(mode)) {
            this.playMode = mode;
            return "播放模式已设置为: " + mode;
        } else {
            return "无效的播放模式: " + mode;
        }
    }
    
    /**
     * 检查播放模式是否有效
     * @param mode 播放模式
     * @return true if valid, false otherwise
     */
    private boolean isValidPlayMode(String mode) {
        return "album".equals(mode) || "single".equals(mode) || 
               "repeat".equals(mode) || "loop".equals(mode);
    }
    
    /**
     * 播放下一首歌曲
     * @return 结果消息
     */
    public String playNext() {
        if (playlist.isEmpty()) {
            return "播放列表为空";
        }
        
        // 简单实现：播放第一首歌曲
        currentSong = playlist.get(0);
        isPlaying = true;
        return "正在播放: " + formatSongTitle(currentSong);
    }
    
    /**
     * 停止播放
     * @return 结果消息
     */
    public String stop() {
        currentSong = null;
        isPlaying = false;
        return "已停止播放";
    }
    
    /**
     * 清空播放列表
     * @return 结果消息
     */
    public String clearPlaylist() {
        playlist.clear();
        currentSong = null;
        isPlaying = false;
        return "播放列表已清空";
    }
    
    // Getter方法
    public boolean isPlaying() {
        return isPlaying;
    }
    
    public Map<String, String> getCurrentSong() {
        return currentSong;
    }
    
    public String getPlayMode() {
        return playMode;
    }
    
    public int getPlaylistSize() {
        return playlist.size();
    }
}