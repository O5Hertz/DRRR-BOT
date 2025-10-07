# 音乐播放模块
import asyncio
import random
from typing import List, Dict, Any

class MusicPlayer:
    """音乐播放器类"""
    
    def __init__(self):
        self.playlist: List[Dict[str, str]] = []  # 播放列表
        self.current_song = None
        self.play_mode = "album"  # album, single, repeat, loop
        self.is_playing = False
        
    def add_to_playlist(self, title: str, url: str, singer: str = ""):
        """添加到播放列表"""
        song = {
            "title": title,
            "url": url,
            "singer": singer
        }
        self.playlist.append(song)
        return f"已添加到播放列表: {self.format_song_title(song)}"
        
    def remove_from_playlist(self, index: int):
        """从播放列表移除"""
        if 0 <= index < len(self.playlist):
            song = self.playlist.pop(index)
            return f"已从播放列表移除: {self.format_song_title(song)}"
        else:
            return "索引超出范围"
            
    def list_playlist(self):
        """列出播放列表"""
        if not self.playlist:
            return "播放列表为空"
            
        result = "播放列表:\n"
        for i, song in enumerate(self.playlist):
            result += f"{i+1}. {self.format_song_title(song)}\n"
        return result.strip()
        
    def format_song_title(self, song: Dict[str, str]):
        """格式化歌曲标题"""
        title = song["title"]
        if song["singer"]:
            title = f"{title} - {song['singer']}"
        return title
        
    def set_play_mode(self, mode: str):
        """设置播放模式"""
        valid_modes = ["album", "single", "repeat", "loop"]
        if mode in valid_modes:
            self.play_mode = mode
            return f"播放模式已设置为: {mode}"
        else:
            return f"无效的播放模式。可用模式: {', '.join(valid_modes)}"
            
    def get_next_song(self):
        """获取下一首歌曲"""
        if not self.playlist:
            return None
            
        if self.play_mode == "single":
            # 单曲播放，不自动播放下一首
            return None
        elif self.play_mode == "repeat":
            # 单曲循环，返回当前歌曲
            return self.current_song
        elif self.play_mode == "loop":
            # 列表循环，返回第一首
            return self.playlist[0]
        else:
            # 专辑模式，按顺序播放
            if self.current_song and self.current_song in self.playlist:
                current_index = self.playlist.index(self.current_song)
                if current_index + 1 < len(self.playlist):
                    return self.playlist[current_index + 1]
                else:
                    return None  # 播放完毕
            else:
                return self.playlist[0]  # 从第一首开始
                
    def play_next(self):
        """播放下一首"""
        next_song = self.get_next_song()
        if next_song:
            self.current_song = next_song
            self.is_playing = True
            # 从播放列表移除（如果不是循环模式）
            if self.play_mode != "repeat" and self.play_mode != "loop":
                if next_song in self.playlist:
                    self.playlist.remove(next_song)
            return next_song
        else:
            self.is_playing = False
            return None
            
    def shuffle_playlist(self):
        """随机播放列表"""
        if self.playlist:
            random.shuffle(self.playlist)
            return "播放列表已随机排序"
        else:
            return "播放列表为空"
            
    def clear_playlist(self):
        """清空播放列表"""
        self.playlist.clear()
        self.current_song = None
        self.is_playing = False
        return "播放列表已清空"