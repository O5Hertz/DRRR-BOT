# 猜数字游戏模块
import random

class GuessNumberGame:
    def __init__(self):
        self.answer = None
        self.game_active = False
        
    def start_game(self):
        """开始游戏"""
        self.answer = str(random.randint(1000, 9999))
        self.game_active = True
        return "猜数字游戏开始！请输入4位数字进行猜测。"
        
    def judge_guess(self, guess):
        """判断猜测结果"""
        if not self.game_active:
            return "游戏未开始，请先使用 /start 命令开始游戏。"
            
        if len(guess) != 4 or not guess.isdigit():
            return "请输入4位数字！"
            
        if len(set(guess)) != 4:
            return "请输入4个不重复的数字！"
            
        a = sum(1 for i in range(4) if guess[i] == self.answer[i])
        b = sum(1 for digit in guess if digit in self.answer) - a
        
        if a == 4:
            self.game_active = False
            return "恭喜你猜对了！答案就是 " + self.answer
            
        return f"{a}A{b}B"