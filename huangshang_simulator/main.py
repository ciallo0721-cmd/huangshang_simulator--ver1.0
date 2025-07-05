#2025/6/23梦开始的地方
import pygame
import sys
import random
from datetime import datetime, timedelta
import os
import time
import json

# 初始化pygame
pygame.init()
pygame.mixer.init()  # 初始化音频系统

# 全局变量声明
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1280
screen = None

# 获取屏幕尺寸 - 适配Android全屏
try:
    info = pygame.display.Info()
    SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
    print(f"检测到屏幕尺寸: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    # 在PC上测试时使用固定大小
    SCREEN_WIDTH, SCREEN_HEIGHT = 720, 1280
    print(f"使用默认屏幕尺寸: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 如果屏幕未创建，安全回退
if screen is None:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("皇上模拟器")

# 颜色定义
BACKGROUND = (230, 220, 200)
GOLD = (212, 175, 55)
RED = (180, 30, 30)
DARK_RED = (120, 20, 20)
LIGHT_GOLD = (240, 220, 130)
BLACK = (30, 30, 30)
WHITE = (240, 240, 240)
GRAY = (180, 180, 180)
LIGHT_BLUE = (200, 220, 240)
IMPERIAL_YELLOW = (255, 204, 0)
BUTTON_HIGHLIGHT = (255, 255, 200, 150)  # 半透明高亮效果
START_BG = (20, 30, 60)  # 开始菜单背景色
SETTINGS_BG = (40, 40, 60, 220)  # 设置菜单背景色（半透明）

# 分辨率选项
RESOLUTIONS = [
    (720, 1280),    # 手机竖屏
    (1280, 720),    # 手机横屏/小屏
    (1920, 1080),   # 全高清
    (2560, 1440),   # 2K
    (3840, 2160)    # 4K
]

# 存档目录
SAVE_DIR = "huangshang_simulator/dangan"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# 字体处理 - 适配Android
def load_font(size):
    try:
        # 尝试加载字体文件
        base_path = os.path.dirname(os.path.abspath(__file__))
        font_dir = os.path.join(base_path, 'fonts')
        font_path = os.path.join(font_dir, 'simhei.ttf')
        
        # 确保目录存在
        if not os.path.exists(font_dir):
            os.makedirs(font_dir)
            print(f"创建字体目录: {font_dir}")
        
        # 如果字体文件存在，使用它
        if os.path.exists(font_path):
            print(f"加载字体文件: {font_path}")
            return pygame.font.Font(font_path, size)
        
        # 尝试系统字体作为后备
        try:
            print("尝试加载系统字体: simhei")
            return pygame.font.SysFont('simhei', size)
        except:
            print("使用默认系统字体")
            return pygame.font.SysFont(None, size)
    except Exception as e:
        print(f"加载字体出错: {e}")
        # 备用字体
        return pygame.font.SysFont(None, size)

# 创建字体对象
title_font = load_font(64)  # 增大开始菜单标题
header_font = load_font(36)
main_font = load_font(28)
small_font = load_font(24)

# 反外挂系统
class AntiCheatSystem:
    def __init__(self):
        self.cheat_detected = False
        self.last_check_time = time.time()
        self.speed_checks = []
        self.max_allowed_speed = 0.01  # 允许的最小帧间隔（100FPS）
        self.max_allowed_checks = 10  # 连续检测次数
        
    def check_speed(self):
        """检测游戏速度是否异常"""
        current_time = time.time()
        delta = current_time - self.last_check_time
        self.last_check_time = current_time
        
        # 如果游戏速度异常快（小于0.01秒一帧）
        if delta < self.max_allowed_speed:
            self.speed_checks.append(True)
            if len(self.speed_checks) > self.max_allowed_checks:
                self.speed_checks.pop(0)
            
            # 如果连续多次检测到高速
            if len(self.speed_checks) == self.max_allowed_checks and all(self.speed_checks):
                self.trigger_anti_cheat("游戏速度异常")
        else:
            self.speed_checks = []
    
    def trigger_anti_cheat(self, reason):
        """触发反外挂措施"""
        self.cheat_detected = True
        print(f"反外挂系统已触发: {reason}")
        
        # 显示警告
        cheat_popup = {
            "title": "反外挂警告",
            "message": f"检测到异常行为: {reason}\n请停止使用任何外挂程序！",
            "duration": 5  # 显示5秒
        }
        return cheat_popup

# 存档管理器
class SaveManager:
    def __init__(self):
        self.save_slots = 5
        self.save_dir = SAVE_DIR
        self.current_save = None
        
        # 创建存档目录
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def get_save_path(self, slot):
        """获取存档路径"""
        return os.path.join(self.save_dir, f"save_{slot}.json")
    
    def save_game(self, slot, game_state):
        """保存游戏"""
        try:
            save_path = self.get_save_path(slot)
            
            # 准备存档数据
            save_data = {
                "day": game_state.day,
                "year": game_state.year,
                "date": game_state.date.strftime("%Y-%m-%d"),
                "health": game_state.health,
                "mood": game_state.mood,
                "authority": game_state.authority,
                "treasury": game_state.treasury,
                "concubines": game_state.concubines,
                "events": game_state.events,
                "reports": game_state.reports,
                "audience_requests": game_state.audience_requests,
                "difficulty": game_state.difficulty,
                "save_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            self.current_save = slot
            return True
        except Exception as e:
            print(f"存档失败: {e}")
            return False
    
    def load_game(self, slot, game_state):
        """加载游戏"""
        try:
            save_path = self.get_save_path(slot)
            if os.path.exists(save_path):
                with open(save_path, 'r') as f:
                    save_data = json.load(f)
                
                # 恢复游戏状态
                game_state.day = save_data["day"]
                game_state.year = save_data["year"]
                game_state.date = datetime.strptime(save_data["date"], "%Y-%m-%d")
                game_state.health = save_data["health"]
                game_state.mood = save_data["mood"]
                game_state.authority = save_data["authority"]
                game_state.treasury = save_data["treasury"]
                game_state.concubines = save_data["concubines"]
                game_state.events = save_data["events"]
                game_state.reports = save_data["reports"]
                game_state.audience_requests = save_data["audience_requests"]
                game_state.difficulty = save_data["difficulty"]
                
                return True
            return False
        except Exception as e:
            print(f"读档失败: {e}")
            return False
    
    def get_save_info(self, slot):
        """获取存档信息"""
        save_path = self.get_save_path(slot)
        if os.path.exists(save_path):
            try:
                with open(save_path, 'r') as f:
                    save_data = json.load(f)
                save_time = save_data.get("save_time", "未知时间")
                day = save_data.get("day", 1)
                return f"第{day}天 {save_time}"
            except:
                return "存档损坏"
        return "空存档"

# 游戏状态
class GameState:
    def __init__(self):
        self.current_view = "start_menu"  # start_menu, main, concubines, reports, audience, settings, save_load
        self.day = 1
        self.year = 1722  # 雍正元年
        self.date = datetime(self.year, 1, 1)
        self.health = 90
        self.mood = 80
        self.authority = 85
        self.treasury = 5000000  # 国库银两
        self.concubines = [
            {"name": "皇后", "favor": 75, "status": "健康", "pregnant": False, "days_pregnant": 0, "personality": "端庄"},
            {"name": "华妃", "favor": 90, "status": "健康", "pregnant": False, "days_pregnant": 0, "personality": "骄纵"},
            {"name": "甄嬛", "favor": 85, "status": "健康", "pregnant": False, "days_pregnant": 0, "personality": "聪慧"},
            {"name": "安陵容", "favor": 65, "status": "健康", "pregnant": False, "days_pregnant": 0, "personality": "敏感"},
            {"name": "沈眉庄", "favor": 70, "status": "健康", "pregnant": False, "days_pregnant": 0, "personality": "温婉"},
            {"name": "祺嫔", "favor": 60, "status": "健康", "pregnant": False, "days_pregnant": 0, "personality": "张扬"},
        ]
        self.events = []
        self.reports = []
        self.audience_requests = []
        self.selected_concubine = None
        self.last_button_click_time = 0  # 防止快速多次点击
        
        # 设置选项
        self.sound_enabled = True
        self.music_enabled = True
        self.difficulty = "中等"  # 简单、中等、困难
        self.settings_open = False  # 设置菜单是否打开
        self.fullscreen = False  # 全屏模式
        self.current_resolution = 0  # 当前分辨率索引
        
        # 音乐状态
        self.current_music = None
        self.music_playing = False
        
        # 关于按钮点击计数器
        self.about_click_count = 0
        self.last_about_click_time = 0
        
        # 开发者模式
        self.developer_mode = False
        
        # 存档管理器
        self.save_manager = SaveManager()
        
        # 反外挂系统
        self.anti_cheat = AntiCheatSystem()
        
        # 警告消息
        self.warning_message = None
        self.warning_display_time = 0
        
        self.generate_initial_requests()
        
    def generate_initial_requests(self):
        # 生成初始奏折
        report_types = [
            "地方水灾请求赈灾拨款",
            "边疆驻军请求粮草补给",
            "科举考试选拔人才",
            "修缮皇宫建筑",
            "外国使节来访接待",
            "地方官员贪污案审理"
        ]
        
        for _ in range(3):
            report = {
                "type": random.choice(report_types),
                "province": random.choice(["江苏", "浙江", "广东", "云南", "四川", "陕西"]),
                "priority": random.randint(1, 3),
                "cost": random.randint(50000, 300000),
                "handled": False
            }
            self.reports.append(report)
        
        # 生成初始觐见请求
        request_types = [
            "大臣奏报边疆军情",
            "内务府汇报宫廷开支",
            "钦天监奏报天象",
            "宗人府汇报皇族事宜",
            "刑部奏报重大案件",
            "工部奏报水利工程"
        ]
        
        for _ in range(2):
            request = {
                "type": random.choice(request_types),
                "official": random.choice(["张廷玉", "年羹尧", "鄂尔泰", "隆科多", "李卫"]),
                "urgency": random.randint(1, 3),
                "handled": False
            }
            self.audience_requests.append(request)
    
    def next_day(self):
        self.day += 1
        self.date += timedelta(days=1)
        self.selected_concubine = None  # 重置选中的嫔妃
        
        # 根据难度调整事件概率
        difficulty_factor = 1.0
        if self.difficulty == "简单":
            difficulty_factor = 0.7
        elif self.difficulty == "困难":
            difficulty_factor = 1.5
        
        # 随机事件
        if random.random() < 0.3 * difficulty_factor:
            events = [
                "华妃在御花园举办赏花宴",
                "皇后召集六宫嫔妃训话",
                "甄嬛在御书房陪皇上读书",
                "安陵容为皇上献唱新曲",
                "祺嫔与其他嫔妃发生争执",
                "沈眉庄照料御花园新植花卉",
                "内务府呈上新进贡的茶叶",
                "御膳房研制出新菜式"
            ]
            self.events.append(random.choice(events))
        
        # 随机健康变化
        if random.random() < 0.15 * difficulty_factor:
            self.health -= random.randint(1, 5)
        elif random.random() < 0.1:
            self.health += random.randint(1, 3)
            self.health = min(100, self.health)
        
        # 随机心情变化
        if random.random() < 0.25 * difficulty_factor:
            mood_change = random.randint(-10, 15)
            if mood_change > 0:
                self.events.append("今日心情愉悦")
            self.mood += mood_change
            self.mood = max(0, min(100, self.mood))
        
        # 处理怀孕状态
        for concubine in self.concubines:
            if concubine["pregnant"]:
                concubine["days_pregnant"] += 1
                if concubine["days_pregnant"] > 270:  # 约9个月
                    concubine["pregnant"] = False
                    concubine["days_pregnant"] = 0
                    self.events.append(f"{concubine['name']}诞下皇子！")
                    self.mood += 10  # 皇子诞生，心情变好
                    self.mood = min(100, self.mood)
        
        # 随机怀孕事件
        if random.random() < 0.05 * difficulty_factor and len(self.events) < 5:
            concubine = random.choice(self.concubines)
            if not concubine["pregnant"]:
                concubine["pregnant"] = True
                self.events.append(f"{concubine['name']}有喜了！")
                self.mood += 5  # 嫔妃有喜，心情变好
                self.mood = min(100, self.mood)
        
        # 随机嫔妃状态变化
        if random.random() < 0.15 * difficulty_factor:
            concubine = random.choice(self.concubines)
            if random.random() < 0.6:
                concubine["favor"] += random.randint(5, 15)
                self.events.append(f"{concubine['name']}近日深得皇上欢心")
            else:
                concubine["favor"] -= random.randint(5, 15)
                self.events.append(f"{concubine['name']}近日触怒皇上")
            concubine["favor"] = max(0, min(100, concubine["favor"]))
            
            # 随机生病
            if random.random() < 0.1 * difficulty_factor:
                concubine["status"] = "染病"
                self.events.append(f"{concubine['name']}身体不适，太医已诊治")
        
        # 恢复生病的嫔妃
        for concubine in self.concubines:
            if concubine["status"] == "染病" and random.random() < 0.3:
                concubine["status"] = "健康"
                self.events.append(f"{concubine['name']}身体康复")
        
        # 随机生成新奏折
        if random.random() < 0.4 * difficulty_factor and len(self.reports) < 8:
            report_types = [
                "地方旱灾请求赈灾拨款",
                "边疆驻军请求粮草补给",
                "科举考试选拔人才",
                "修缮皇宫建筑",
                "外国使节来访接待",
                "地方官员贪污案审理",
                "河道治理工程拨款",
                "粮食丰收税收事宜"
            ]
            report = {
                "type": random.choice(report_types),
                "province": random.choice(["江苏", "浙江", "广东", "云南", "四川", "陕西", "山西", "河南"]),
                "priority": random.randint(1, 3),
                "cost": random.randint(50000, 300000),
                "handled": False
            }
            self.reports.append(report)
        
        # 随机生成新觐见请求
        if random.random() < 0.3 * difficulty_factor and len(self.audience_requests) < 4:
            request_types = [
                "大臣奏报边疆军情",
                "内务府汇报宫廷开支",
                "钦天监奏报天象",
                "宗人府汇报皇族事宜",
                "刑部奏报重大案件",
                "工部奏报水利工程",
                "礼部奏报祭祀事宜",
                "户部奏报税收情况"
            ]
            request = {
                "type": random.choice(request_types),
                "official": random.choice(["张廷玉", "年羹尧", "鄂尔泰", "隆科多", "李卫", "田文镜", "胤祥"]),
                "urgency": random.randint(1, 3),
                "handled": False
            }
            self.audience_requests.append(request)
            
        # 国库收入
        daily_income = random.randint(5000, 20000)
        self.treasury += daily_income
    
    def play_music(self, music_path):
        """播放指定音乐"""
        if not self.music_enabled:
            return
            
        # 检查音乐是否已经在播放
        if self.current_music == music_path and self.music_playing:
            return
            
        try:
            # 确保音乐目录存在
            base_path = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_path, music_path)
            
            if os.path.exists(full_path):
                pygame.mixer.music.load(full_path)
                pygame.mixer.music.play(-1)  # -1表示循环播放
                self.current_music = music_path
                self.music_playing = True
                print(f"播放音乐: {music_path}")
            else:
                print(f"音乐文件不存在: {full_path}")
        except Exception as e:
            print(f"播放音乐出错: {e}")
    
    def stop_music(self):
        """停止播放音乐"""
        pygame.mixer.music.stop()
        self.music_playing = False
        self.current_music = None
    
    def show_about(self, current_time):
        """显示关于信息（带彩蛋）"""
        # 如果是连续点击（1秒内）
        if current_time - self.last_about_click_time < 1:
            self.about_click_count += 1
        else:
            self.about_click_count = 1
        
        self.last_about_click_time = current_time
        
        # 显示普通关于信息
        about_text = "皇帝模拟器 v1.0\n\n由quan于2025/6/26创建"
        
        # 如果连续点击10次，进入开发者模式
        if self.about_click_count >= 10:
            self.developer_mode = True
            self.about_click_count = 0
            return "开发者模式已激活！\n创作时间: 2025/6/26\n创始人: quan"
        
        return about_text

# 创建游戏状态
game_state = GameState()

# 按钮类 - 修复版
class Button:
    def __init__(self, x, y, width, height, text, color=GOLD, hover_color=LIGHT_GOLD, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.text_color = text_color
        self.is_hovered = False
        self.is_pressed = False
        self.press_time = 0
        self.click_cooldown = 0.3  # 防止快速多次点击
        
    def draw(self, surface):
        # 绘制按钮基础
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, DARK_RED, self.rect, 3, border_radius=12)
        
        # 绘制按压效果
        if self.is_pressed:
            highlight = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(highlight, BUTTON_HIGHLIGHT, (0, 0, self.rect.width, self.rect.height), border_radius=12)
            surface.blit(highlight, self.rect)
        
        # 绘制文本
        text_surf = main_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def handle_event(self, event, current_time):
        """处理事件并返回按钮是否被点击"""
        # 处理鼠标事件
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
                self.press_time = current_time
                return True
        
        # 处理触摸事件
        elif event.type == pygame.FINGERDOWN:
            # 将触摸坐标转换为屏幕坐标
            x = event.x * SCREEN_WIDTH
            y = event.y * SCREEN_HEIGHT
            if self.rect.collidepoint((x, y)):
                self.is_pressed = True
                self.press_time = current_time
                return True
        
        # 处理按钮释放
        if event.type == pygame.MOUSEBUTTONUP or event.type == pygame.FINGERUP:
            if self.is_pressed and current_time - self.press_time < self.click_cooldown:
                self.is_pressed = False
                return self.rect.collidepoint(event.pos) if event.type == pygame.MOUSEBUTTONUP else True
            self.is_pressed = False
        
        return False

# 设置开关按钮
class ToggleButton(Button):
    def __init__(self, x, y, width, height, text, initial_state=True):
        super().__init__(x, y, width, height, text)
        self.state = initial_state
        self.update_text()
        
    def update_text(self):
        if self.state:
            self.text = f"{self.text[:self.text.find(':')+1]} 开"
        else:
            self.text = f"{self.text[:self.text.find(':')+1]} 关"
    
    def toggle(self):
        self.state = not self.state
        self.update_text()
        return self.state

# 创建开始菜单按钮
def create_start_menu_buttons():
    buttons = []
    button_width = SCREEN_WIDTH - 200
    button_height = 100
    spacing = 30
    
    # 开始游戏按钮
    y_pos = SCREEN_HEIGHT * 0.6
    buttons.append(Button(100, y_pos, button_width, button_height, "开始游戏", IMPERIAL_YELLOW, (255, 230, 150)))
    
    # 退出游戏按钮
    y_pos += button_height + spacing
    buttons.append(Button(100, y_pos, button_width, button_height, "退出游戏", RED, (220, 100, 100), WHITE))
    
    return buttons

# 创建主界面按钮
def create_main_buttons():
    buttons = []
    button_width = SCREEN_WIDTH - 100
    button_height = 80
    spacing = 20
    
    y_pos = SCREEN_HEIGHT * 0.4
    
    buttons.append(Button(50, y_pos, button_width, button_height, "召见嫔妃", IMPERIAL_YELLOW, (255, 230, 150)))
    
    y_pos += button_height + spacing
    buttons.append(Button(50, y_pos, button_width, button_height, "批阅奏折", LIGHT_BLUE, (180, 220, 255)))
    
    y_pos += button_height + spacing
    buttons.append(Button(50, y_pos, button_width, button_height, "大臣觐见", (200, 230, 180), (220, 255, 200)))
    
    y_pos += button_height + spacing
    buttons.append(Button(50, y_pos, button_width, button_height, "存档/读档", (180, 200, 240), (200, 220, 255)))
    
    y_pos += button_height + spacing
    buttons.append(Button(50, y_pos, button_width, button_height, "就寝（进入下一天）", RED, (220, 100, 100), WHITE))
    
    # 退出到菜单按钮
    y_pos += button_height + spacing + 20
    buttons.append(Button(50, y_pos, button_width, button_height, "退出到菜单", (150, 150, 180), (180, 180, 220)))
    
    return buttons

# 创建设置按钮
def create_settings_button():
    return Button(20, 20, 100, 60, "设置")

# 创建设置菜单
def create_settings_menu():
    buttons = []
    button_width = SCREEN_WIDTH - 100
    button_height = 70
    spacing = 20
    
    # 位置在屏幕左上角
    x_pos = 20
    y_pos = 100
    
    # 音效开关
    buttons.append(ToggleButton(x_pos, y_pos, button_width, button_height, "音效:", game_state.sound_enabled))
    y_pos += button_height + spacing
    
    # 音乐开关
    buttons.append(ToggleButton(x_pos, y_pos, button_width, button_height, "音乐:", game_state.music_enabled))
    y_pos += button_height + spacing
    
    # 难度选择
    buttons.append(Button(x_pos, y_pos, button_width, button_height, f"难度: {game_state.difficulty}", (180, 200, 240), (200, 220, 255)))
    y_pos += button_height + spacing
    
    # 分辨率选择
    res_text = f"分辨率: {RESOLUTIONS[game_state.current_resolution][0]}x{RESOLUTIONS[game_state.current_resolution][1]}"
    buttons.append(Button(x_pos, y_pos, button_width, button_height, res_text, (200, 180, 240), (220, 200, 255)))
    y_pos += button_height + spacing
    
    # 窗口化/全屏切换
    mode_text = "窗口模式" if not game_state.fullscreen else "全屏模式"
    buttons.append(Button(x_pos, y_pos, button_width, button_height, mode_text, (180, 240, 200), (200, 255, 220)))
    y_pos += button_height + spacing
    
    # 关于按钮
    buttons.append(Button(x_pos, y_pos, button_width, button_height, "关于", (200, 180, 240), (220, 200, 255)))
    y_pos += button_height + spacing
    
    # 退出游戏按钮
    buttons.append(Button(x_pos, y_pos, button_width, button_height, "退出游戏", RED, (220, 100, 100), WHITE))
    y_pos += button_height + spacing
    
    # 关闭设置按钮
    buttons.append(Button(x_pos, y_pos, button_width, button_height, "关闭设置", (150, 150, 180), (180, 180, 220)))
    
    return buttons

# 创建存档/读档界面按钮
def create_save_load_buttons():
    buttons = []
    button_width = SCREEN_WIDTH - 100
    button_height = 80
    spacing = 20
    
    y_pos = 300
    
    # 创建存档槽按钮
    for i in range(1, game_state.save_manager.save_slots + 1):
        save_info = game_state.save_manager.get_save_info(i)
        buttons.append(Button(50, y_pos, button_width, button_height, f"存档槽 {i}: {save_info}", (180, 200, 240), (200, 220, 255)))
        y_pos += button_height + spacing
    
    # 返回按钮
    buttons.append(Button(50, y_pos, button_width, button_height, "返回主界面", (150, 150, 180), (180, 180, 220)))
    
    return buttons

# 绘制状态条
def draw_stat_bar(surface, x, y, width, height, value, max_value, color, bg_color=GRAY, text=""):
    """绘制带有文本的状态条"""
    # 绘制背景
    pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=5)
    # 绘制进度条
    bar_width = int(width * value / max_value)
    pygame.draw.rect(surface, color, (x, y, bar_width, height), border_radius=5)
    # 绘制文本
    text_surf = small_font.render(f"{text}{value}/{max_value}", True, WHITE)
    text_rect = text_surf.get_rect(midleft=(x + 10, y + height // 2))
    surface.blit(text_surf, text_rect)

# 显示警告消息
def show_warning(surface, message):
    """在屏幕顶部显示警告消息"""
    if not message:
        return
        
    # 创建半透明背景
    warning_bg = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
    warning_bg.fill((200, 50, 50, 200))
    surface.blit(warning_bg, (0, 0))
    
    # 绘制警告文本
    warning_text = header_font.render(message, True, WHITE)
    surface.blit(warning_text, (SCREEN_WIDTH // 2 - warning_text.get_width() // 2, 15))

# 主游戏循环
def main_game_loop():
    # 声明全局变量
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, start_menu_buttons, main_buttons, settings_button, back_button, interact_button, settings_menu_buttons
    
    clock = pygame.time.Clock()
    running = True
    current_time = time.time()
    last_time = time.time()
    
    # 用于调试的鼠标位置显示
    debug_mouse_pos = (0, 0)
    
    # 播放主菜单音乐
    game_state.play_music("music/bg/bg.mp3")
    
    while running:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time
        
        # 反外挂检测
        game_state.anti_cheat.check_speed()
        
        # 检查警告消息是否过期
        if game_state.warning_message and current_time - game_state.warning_display_time > 5:
            game_state.warning_message = None
        
        mouse_pos = pygame.mouse.get_pos()
        debug_mouse_pos = mouse_pos
        
        # 根据当前视图播放音乐
        if game_state.current_view == "start_menu" or game_state.current_view == "main":
            game_state.play_music("music/bg/bg.mp3")
        else:
            game_state.play_music("music/bg/nb/nb.mp3")
        
        # 检查按钮悬停状态
        if game_state.current_view == "start_menu":
            for button in start_menu_buttons:
                button.check_hover(mouse_pos)
        elif game_state.current_view == "main":
            for button in main_buttons:
                button.check_hover(mouse_pos)
        elif game_state.current_view == "save_load":
            for button in save_load_buttons:
                button.check_hover(mouse_pos)
        
        # 设置按钮总是显示在游戏界面
        if game_state.current_view != "start_menu":
            settings_button.check_hover(mouse_pos)
            back_button.check_hover(mouse_pos)
            interact_button.check_hover(mouse_pos)
            
        # 设置菜单按钮
        if game_state.settings_open:
            for button in settings_menu_buttons:
                button.check_hover(mouse_pos)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 处理Android返回键
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state.settings_open:
                        game_state.settings_open = False
                    elif game_state.current_view != "start_menu" and game_state.current_view != "main":
                        game_state.current_view = "main"
                        game_state.selected_concubine = None
                    elif game_state.current_view == "main":
                        game_state.current_view = "start_menu"
                    else:
                        running = False
            
            # 处理触摸事件
            if event.type == pygame.FINGERDOWN:
                # 将触摸坐标转换为屏幕坐标
                x = event.x * SCREEN_WIDTH
                y = event.y * SCREEN_HEIGHT
                mouse_pos = (x, y)
                # 创建一个模拟鼠标事件
                mouse_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (x, y)})
                pygame.event.post(mouse_event)
            
            # 处理开始菜单按钮
            if game_state.current_view == "start_menu":
                for button in start_menu_buttons:
                    if button.handle_event(event, current_time):
                        if button.text == "开始游戏":
                            game_state.current_view = "main"
                        elif button.text == "退出游戏":
                            running = False
            
            # 处理主界面按钮
            if game_state.current_view == "main":
                for button in main_buttons:
                    if button.handle_event(event, current_time):
                        if button.text == "召见嫔妃":
                            game_state.current_view = "concubines"
                        elif button.text == "批阅奏折":
                            game_state.current_view = "reports"
                        elif button.text == "大臣觐见":
                            game_state.current_view = "audience"
                        elif button.text == "存档/读档":
                            game_state.current_view = "save_load"
                            # 更新存档按钮信息
                            save_load_buttons = create_save_load_buttons()
                        elif button.text == "就寝（进入下一天）":
                            game_state.next_day()
                        elif button.text == "退出到菜单":
                            game_state.current_view = "start_menu"
            
            # 处理存档/读档界面按钮
            if game_state.current_view == "save_load":
                for i, button in enumerate(save_load_buttons):
                    if button.handle_event(event, current_time):
                        if i < game_state.save_manager.save_slots:  # 存档槽按钮
                            slot = i + 1
                            # 保存游戏
                            if game_state.save_manager.save_game(slot, game_state):
                                game_state.events.append(f"游戏已保存到存档槽 {slot}")
                            else:
                                game_state.events.append("存档失败")
                            
                            # 更新存档按钮信息
                            save_load_buttons = create_save_load_buttons()
                        elif button.text == "返回主界面":  # 返回按钮
                            game_state.current_view = "main"
            
            # 处理设置按钮
            if settings_button.handle_event(event, current_time) and game_state.current_view != "start_menu":
                game_state.settings_open = not game_state.settings_open
            
            # 处理返回按钮
            if back_button.handle_event(event, current_time) and game_state.current_view != "start_menu":
                if game_state.current_view != "main":
                    game_state.current_view = "main"
                game_state.selected_concubine = None
            
            # 处理宠幸按钮
            if interact_button.handle_event(event, current_time):
                if game_state.selected_concubine is not None:
                    concubine = game_state.concubines[game_state.selected_concubine]
                    game_state.events.append(f"皇上宠幸了{concubine['name']}")
                    concubine["favor"] = min(100, concubine["favor"] + random.randint(5, 15))
                    game_state.mood = min(100, game_state.mood + random.randint(5, 10))
                    
                    # 有几率怀孕
                    if not concubine["pregnant"] and random.random() < 0.35:
                        concubine["pregnant"] = True
                        game_state.events.append(f"{concubine['name']}有喜了！")
                    
                    game_state.selected_concubine = None
            
            # 处理设置菜单按钮
            if game_state.settings_open:
                for i, button in enumerate(settings_menu_buttons):
                    if button.handle_event(event, current_time):
                        if i == 0:  # 音效开关
                            button.toggle()
                            game_state.sound_enabled = button.state
                        elif i == 1:  # 音乐开关
                            button.toggle()
                            game_state.music_enabled = button.state
                            if not game_state.music_enabled:
                                game_state.stop_music()
                            else:
                                # 重新播放当前视图的音乐
                                if game_state.current_view == "start_menu" or game_state.current_view == "main":
                                    game_state.play_music("music/bg/bg.mp3")
                                else:
                                    game_state.play_music("music/bg/nb/nb.mp3")
                        elif i == 2:  # 难度选择
                            if game_state.difficulty == "简单":
                                game_state.difficulty = "中等"
                            elif game_state.difficulty == "中等":
                                game_state.difficulty = "困难"
                            else:
                                game_state.difficulty = "简单"
                            button.text = f"难度: {game_state.difficulty}"
                        elif i == 3:  # 分辨率选择
                            # 循环到下一个分辨率
                            game_state.current_resolution = (game_state.current_resolution + 1) % len(RESOLUTIONS)
                            
                            # 更新屏幕分辨率
                            new_width, new_height = RESOLUTIONS[game_state.current_resolution]
                            
                            if game_state.fullscreen:
                                screen = pygame.display.set_mode((new_width, new_height), pygame.FULLSCREEN)
                            else:
                                screen = pygame.display.set_mode((new_width, new_height))
                            
                            # 更新全局分辨率变量
                            SCREEN_WIDTH, SCREEN_HEIGHT = new_width, new_height
                            
                            # 重新创建所有按钮以适应新分辨率
                            start_menu_buttons = create_start_menu_buttons()
                            main_buttons = create_main_buttons()
                            settings_button = create_settings_button()
                            back_button = Button(SCREEN_WIDTH - 120, 20, 100, 60, "返回")
                            interact_button = Button(SCREEN_WIDTH - 220, SCREEN_HEIGHT - 100, 200, 70, "宠幸", RED, (220, 100, 100), WHITE)
                            settings_menu_buttons = create_settings_menu()
                            
                            # 更新按钮文本
                            settings_menu_buttons[3].text = f"分辨率: {new_width}x{new_height}"
                        elif i == 4:  # 窗口化/全屏切换
                            game_state.fullscreen = not game_state.fullscreen
                            
                            # 更新屏幕模式
                            if game_state.fullscreen:
                                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                                button.text = "全屏模式"
                            else:
                                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                                button.text = "窗口模式"
                        elif i == 5:  # 关于按钮
                            # 显示关于信息
                            about_text = game_state.show_about(current_time)
                            game_state.warning_message = about_text
                            game_state.warning_display_time = current_time
                        elif i == 6:  # 退出游戏
                            running = False
                        elif i == 7:  # 关闭设置
                            game_state.settings_open = False
            
            # 处理嫔妃选择
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_state.current_view == "concubines" and game_state.selected_concubine is None:
                    for i, concubine in enumerate(game_state.concubines):
                        btn_rect = pygame.Rect(50, 300 + i * 110, SCREEN_WIDTH - 100, 100)
                        if btn_rect.collidepoint(event.pos):
                            game_state.selected_concubine = i
            
            # 处理触摸事件 - 嫔妃选择
            if event.type == pygame.FINGERDOWN:
                # 将触摸坐标转换为屏幕坐标
                x = event.x * SCREEN_WIDTH
                y = event.y * SCREEN_HEIGHT
                if game_state.current_view == "concubines" and game_state.selected_concubine is None:
                    for i, concubine in enumerate(game_state.concubines):
                        btn_rect = pygame.Rect(50, 300 + i * 110, SCREEN_WIDTH - 100, 100)
                        if btn_rect.collidepoint((x, y)):
                            game_state.selected_concubine = i
            
            # 处理批阅奏折界面的按钮
            if game_state.current_view == "reports":
                for i, report in enumerate(game_state.reports):
                    if not report["handled"]:
                        y_pos = 300 + i * 150
                        # 定义批准和驳回按钮的位置
                        approve_btn_rect = pygame.Rect(SCREEN_WIDTH - 240, y_pos + 90, 100, 40)
                        reject_btn_rect = pygame.Rect(SCREEN_WIDTH - 120, y_pos + 90, 100, 40)
                        
                        # 处理鼠标点击
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if approve_btn_rect.collidepoint(event.pos):
                                # 批准奏折
                                report["handled"] = True
                                game_state.treasury -= report["cost"]
                                game_state.authority = min(100, game_state.authority + 5)
                                game_state.events.append(f"已批准: {report['type']} ({report['province']})")
                                
                                # 根据奏折类型增加不同属性
                                if "赈灾" in report["type"]:
                                    game_state.mood = min(100, game_state.mood + 3)
                                    game_state.health = min(100, game_state.health + 2)
                                elif "科举" in report["type"]:
                                    game_state.authority = min(100, game_state.authority + 8)
                                elif "修缮" in report["type"]:
                                    game_state.mood = min(100, game_state.mood + 5)
                                
                            elif reject_btn_rect.collidepoint(event.pos):
                                # 驳回奏折
                                report["handled"] = True
                                game_state.authority = max(0, game_state.authority - 3)
                                game_state.mood = max(0, game_state.mood - 2)
                                game_state.events.append(f"已驳回: {report['type']} ({report['province']})")
                        
                        # 处理触摸事件
                        if event.type == pygame.FINGERDOWN:
                            # 将触摸坐标转换为屏幕坐标
                            x = event.x * SCREEN_WIDTH
                            y = event.y * SCREEN_HEIGHT
                            if approve_btn_rect.collidepoint((x, y)):
                                # 批准奏折
                                report["handled"] = True
                                game_state.treasury -= report["cost"]
                                game_state.authority = min(100, game_state.authority + 5)
                                game_state.events.append(f"已批准: {report['type']} ({report['province']})")
                                
                                # 根据奏折类型增加不同属性
                                if "赈灾" in report["type"]:
                                    game_state.mood = min(100, game_state.mood + 3)
                                    game_state.health = min(100, game_state.health + 2)
                                elif "科举" in report["type"]:
                                    game_state.authority = min(100, game_state.authority + 8)
                                elif "修缮" in report["type"]:
                                    game_state.mood = min(100, game_state.mood + 5)
                                
                            elif reject_btn_rect.collidepoint((x, y)):
                                # 驳回奏折
                                report["handled"] = True
                                game_state.authority = max(0, game_state.authority - 3)
                                game_state.mood = max(0, game_state.mood - 2)
                                game_state.events.append(f"已驳回: {report['type']} ({report['province']})")
            
            # 处理觐见请求界面的按钮
            if game_state.current_view == "audience":
                for i, request in enumerate(game_state.audience_requests):
                    if not request["handled"]:
                        y_pos = 300 + i * 150
                        # 定义接见和推迟按钮的位置
                        accept_btn_rect = pygame.Rect(SCREEN_WIDTH - 240, y_pos + 90, 100, 40)
                        postpone_btn_rect = pygame.Rect(SCREEN_WIDTH - 120, y_pos + 90, 100, 40)
                        
                        # 处理鼠标点击
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            if accept_btn_rect.collidepoint(event.pos):
                                # 接见大臣
                                request["handled"] = True
                                game_state.authority = min(100, game_state.authority + 3)
                                game_state.mood = max(0, game_state.mood - 2)  # 接见可能消耗心情
                                
                                # 根据请求类型增加不同属性
                                if "边疆军情" in request["type"]:
                                    game_state.authority = min(100, game_state.authority + 8)
                                    game_state.mood = max(0, game_state.mood - 5)
                                elif "宫廷开支" in request["type"]:
                                    # 减少开支可能增加国库
                                    savings = random.randint(5000, 20000)
                                    game_state.treasury += savings
                                    game_state.events.append(f"节省开支: {savings}两")
                                elif "天象" in request["type"]:
                                    # 天象可能影响健康
                                    effect = random.choice([-3, -2, -1, 1, 2, 3])
                                    game_state.health = max(0, min(100, game_state.health + effect))
                                    game_state.events.append(f"天象: {'吉' if effect > 0 else '凶'}")
                                
                                game_state.events.append(f"已接见: {request['official']} ({request['type']})")
                            
                            elif postpone_btn_rect.collidepoint(event.pos):
                                # 推迟请求
                                request["handled"] = True
                                game_state.authority = max(0, game_state.authority - 2)
                                game_state.mood = max(0, game_state.mood - 1)
                                game_state.events.append(f"已推迟: {request['official']} ({request['type']})")
                        
                        # 处理触摸事件
                        if event.type == pygame.FINGERDOWN:
                            # 将触摸坐标转换为屏幕坐标
                            x = event.x * SCREEN_WIDTH
                            y = event.y * SCREEN_HEIGHT
                            if accept_btn_rect.collidepoint((x, y)):
                                # 接见大臣
                                request["handled"] = True
                                game_state.authority = min(100, game_state.authority + 3)
                                game_state.mood = max(0, game_state.mood - 2)  # 接见可能消耗心情
                                
                                # 根据请求类型增加不同属性
                                if "边疆军情" in request["type"]:
                                    game_state.authority = min(100, game_state.authority + 8)
                                    game_state.mood = max(0, game_state.mood - 5)
                                elif "宫廷开支" in request["type"]:
                                    # 减少开支可能增加国库
                                    savings = random.randint(5000, 20000)
                                    game_state.treasury += savings
                                    game_state.events.append(f"节省开支: {savings}两")
                                elif "天象" in request["type"]:
                                    # 天象可能影响健康
                                    effect = random.choice([-3, -2, -1, 1, 2, 3])
                                    game_state.health = max(0, min(100, game_state.health + effect))
                                    game_state.events.append(f"天象: {'吉' if effect > 0 else '凶'}")
                                
                                game_state.events.append(f"已接见: {request['official']} ({request['type']})")
                            
                            elif postpone_btn_rect.collidepoint((x, y)):
                                # 推迟请求
                                request["handled"] = True
                                game_state.authority = max(0, game_state.authority - 2)
                                game_state.mood = max(0, game_state.mood - 1)
                                game_state.events.append(f"已推迟: {request['official']} ({request['type']})")
        
        # 绘制界面
        if game_state.current_view == "start_menu":
            # 绘制开始菜单背景
            screen.fill(START_BG)
            
            # 绘制标题
            title_text = title_font.render("皇上模拟器", True, IMPERIAL_YELLOW)
            subtitle_text = header_font.render("体验帝王生活，治理江山社稷", True, LIGHT_GOLD)
            
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT * 0.2))
            screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, SCREEN_HEIGHT * 0.3))
            
            # 绘制装饰性龙纹
            for i in range(0, SCREEN_WIDTH, 80):
                pygame.draw.line(screen, GOLD, (i, SCREEN_HEIGHT * 0.15), (i + 40, SCREEN_HEIGHT * 0.18), 3)
                pygame.draw.line(screen, GOLD, (i + 40, SCREEN_HEIGHT * 0.18), (i + 80, SCREEN_HEIGHT * 0.15), 3)
            
            # 绘制按钮
            for button in start_menu_buttons:
                button.draw(screen)
                
            # 绘制底部信息
            footer_text = small_font.render("大清雍正皇帝御览 - 紫禁城养心殿", True, LIGHT_GOLD)
            screen.blit(footer_text, (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 50))
            
        else:
            # 绘制游戏界面背景
            screen.fill(BACKGROUND)
            
            # 绘制顶部装饰
            pygame.draw.rect(screen, GOLD, (0, 0, SCREEN_WIDTH, 100))
            pygame.draw.rect(screen, DARK_RED, (0, 100, SCREEN_WIDTH, 5))
            
            # 绘制标题
            title_text = title_font.render("皇上模拟器", True, DARK_RED)
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 25))
            
            # 绘制日期和状态
            year_text = f"雍正{game_state.year-1722+1}年" if game_state.year >= 1722 else f"康熙{1722-game_state.year}年"
            date_text = header_font.render(f"{year_text} {game_state.date.strftime('%m月%d日')}", True, BLACK)
            screen.blit(date_text, (30, 110))
            
            # 绘制状态条
            bar_width = SCREEN_WIDTH - 60
            draw_stat_bar(screen, 30, 160, bar_width, 30, game_state.health, 100, (50, 180, 50), text="健康: ")
            draw_stat_bar(screen, 30, 200, bar_width, 30, game_state.mood, 100, (70, 70, 200), text="心情: ")
            draw_stat_bar(screen, 30, 240, bar_width, 30, game_state.authority, 100, (180, 150, 50), text="权威: ")
            
            treasury_text = header_font.render(f"国库: {game_state.treasury:,}两", True, DARK_RED)
            screen.blit(treasury_text, (SCREEN_WIDTH - treasury_text.get_width() - 30, 110))
            
            # 绘制事件框
            pygame.draw.rect(screen, LIGHT_BLUE, (20, 290, SCREEN_WIDTH - 40, 100), border_radius=10)
            pygame.draw.rect(screen, (70, 100, 180), (20, 290, SCREEN_WIDTH - 40, 100), 3, border_radius=10)
            events_title = header_font.render("宫廷记事", True, (70, 100, 180))
            screen.blit(events_title, (SCREEN_WIDTH // 2 - events_title.get_width()//2, 300))
            
            if game_state.events:
                event_text = main_font.render(f"· {game_state.events[-1]}", True, BLACK)
                screen.blit(event_text, (40, 340))
                if len(game_state.events) > 1:
                    event_text2 = main_font.render(f"· {game_state.events[-2]}", True, BLACK)
                    screen.blit(event_text2, (40, 370))
            else:
                no_event_text = main_font.render("今日无大事发生", True, GRAY)
                screen.blit(no_event_text, (SCREEN_WIDTH // 2 - no_event_text.get_width()//2, 340))
            
            # 根据当前视图绘制内容
            if game_state.current_view == "main":
                # 绘制主界面
                title_text = header_font.render("皇上，今日如何安排？", True, BLACK)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 380))
                
                # 绘制按钮
                for button in main_buttons:
                    button.draw(screen)
                
                # 绘制紫禁城简图
                pygame.draw.rect(screen, LIGHT_GOLD, (50, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 100, 200), border_radius=10)
                pygame.draw.rect(screen, DARK_RED, (50, SCREEN_HEIGHT - 250, SCREEN_WIDTH - 100, 200), 3, border_radius=10)
                
                # 绘制宫殿
                palace_width = (SCREEN_WIDTH - 180) // 3
                y_pos = SCREEN_HEIGHT - 230
                pygame.draw.rect(screen, RED, (70, y_pos, palace_width, 50), border_radius=5)  # 太和殿
                pygame.draw.rect(screen, RED, (70 + palace_width + 20, y_pos, palace_width, 50), border_radius=5)  # 中和殿
                pygame.draw.rect(screen, RED, (70, y_pos + 70, palace_width, 50), border_radius=5)   # 乾清宫
                pygame.draw.rect(screen, RED, (70 + palace_width + 20, y_pos + 70, palace_width, 50), border_radius=5)   # 坤宁宫
                
                # 绘制标签
                palace_text = small_font.render("紫禁城", True, DARK_RED)
                screen.blit(palace_text, (SCREEN_WIDTH // 2 - palace_text.get_width()//2, SCREEN_HEIGHT - 240))
            
            elif game_state.current_view == "concubines":
                # 绘制嫔妃界面
                title_text = header_font.render("后宫嫔妃", True, BLACK)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 380))
                
                # 绘制返回按钮
                back_button.draw(screen)
                
                # 绘制宠幸按钮（如果选中了嫔妃）
                if game_state.selected_concubine is not None:
                    interact_button.draw(screen)
                
                # 绘制嫔妃列表
                for i, concubine in enumerate(game_state.concubines):
                    y_pos = 300 + i * 110
                    # 高亮选中的嫔妃
                    if i == game_state.selected_concubine:
                        pygame.draw.rect(screen, (255, 240, 200), (50, y_pos, SCREEN_WIDTH - 100, 100), border_radius=12)
                        pygame.draw.rect(screen, DARK_RED, (50, y_pos, SCREEN_WIDTH - 100, 100), 3, border_radius=12)
                    
                    # 绘制嫔妃卡片
                    pygame.draw.rect(screen, LIGHT_GOLD, (50, y_pos, SCREEN_WIDTH - 100, 100), border_radius=12)
                    pygame.draw.rect(screen, DARK_RED, (50, y_pos, SCREEN_WIDTH - 100, 100), 2, border_radius=12)
                    
                    # 绘制嫔妃信息
                    name_text = main_font.render(concubine["name"], True, BLACK)
                    screen.blit(name_text, (70, y_pos + 15))
                    
                    # 绘制恩宠度
                    favor_text = main_font.render(f"恩宠: {concubine['favor']}/100", True, BLACK)
                    screen.blit(favor_text, (70, y_pos + 50))
                    
                    # 绘制状态
                    status_color = (50, 150, 50) if concubine["status"] == "健康" else (180, 50, 50)
                    status_text = main_font.render(f"状态: {concubine['status']}", True, status_color)
                    screen.blit(status_text, (SCREEN_WIDTH - 200, y_pos + 15))
                    
                    # 绘制怀孕状态
                    if concubine["pregnant"]:
                        pregnant_text = main_font.render(f"怀孕中", True, (200, 50, 120))
                        screen.blit(pregnant_text, (SCREEN_WIDTH - 200, y_pos + 50))
                    
                    # 绘制恩宠条
                    bar_width = SCREEN_WIDTH - 250
                    pygame.draw.rect(screen, GRAY, (200, y_pos + 65, bar_width, 15), border_radius=5)
                    pygame.draw.rect(screen, (200, 50, 120), (200, y_pos + 65, bar_width * concubine["favor"] / 100, 15), border_radius=5)
            
            elif game_state.current_view == "reports":
                # 绘制奏折界面
                title_text = header_font.render("待批阅奏折", True, BLACK)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 380))
                
                # 绘制返回按钮
                back_button.draw(screen)
                
                # 绘制奏折列表
                for i, report in enumerate(game_state.reports):
                    if not report["handled"]:
                        y_pos = 300 + i * 150
                        # 绘制奏折卡片
                        pygame.draw.rect(screen, LIGHT_BLUE, (30, y_pos, SCREEN_WIDTH - 60, 140), border_radius=12)
                        pygame.draw.rect(screen, (70, 100, 180), (30, y_pos, SCREEN_WIDTH - 60, 140), 2, border_radius=12)
                        
                        # 绘制奏折信息
                        type_text = main_font.render(report["type"], True, BLACK)
                        screen.blit(type_text, (50, y_pos + 15))
                        
                        province_text = main_font.render(f"省份: {report['province']}", True, BLACK)
                        screen.blit(province_text, (50, y_pos + 50))
                        
                        priority_text = main_font.render(f"优先级: {'★' * report['priority']}", True, (200, 50, 50))
                        screen.blit(priority_text, (50, y_pos + 85))
                        
                        cost_text = main_font.render(f"所需银两: {report['cost']:,}两", True, (50, 100, 50))
                        screen.blit(cost_text, (SCREEN_WIDTH - 250, y_pos + 50))
                        
                        # 绘制处理按钮
                        approve_btn = Button(SCREEN_WIDTH - 240, y_pos + 90, 100, 40, "批准", (50, 150, 50), (100, 200, 100))
                        reject_btn = Button(SCREEN_WIDTH - 120, y_pos + 90, 100, 40, "驳回", (200, 50, 50), (240, 100, 100))
                        
                        approve_btn.check_hover(mouse_pos)
                        reject_btn.check_hover(mouse_pos)
                        
                        approve_btn.draw(screen)
                        reject_btn.draw(screen)
            
            elif game_state.current_view == "audience":
                # 绘制觐见界面
                title_text = header_font.render("大臣觐见请求", True, BLACK)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 380))
                
                # 绘制返回按钮
                back_button.draw(screen)
                
                # 绘制请求列表
                for i, request in enumerate(game_state.audience_requests):
                    if not request["handled"]:
                        y_pos = 300 + i * 150
                        # 绘制请求卡片
                        pygame.draw.rect(screen, (220, 240, 200), (30, y_pos, SCREEN_WIDTH - 60, 140), border_radius=12)
                        pygame.draw.rect(screen, (100, 120, 50), (30, y_pos, SCREEN_WIDTH - 60, 140), 2, border_radius=12)
                        
                        # 绘制请求信息
                        type_text = main_font.render(request["type"], True, BLACK)
                        screen.blit(type_text, (50, y_pos + 15))
                        
                        official_text = main_font.render(f"大臣: {request['official']}", True, BLACK)
                        screen.blit(official_text, (50, y_pos + 50))
                        
                        urgency_text = main_font.render(f"紧急性: {'⚠' * request['urgency']}", True, (200, 50, 50))
                        screen.blit(urgency_text, (50, y_pos + 85))
                        
                        # 绘制处理按钮
                        accept_btn = Button(SCREEN_WIDTH - 240, y_pos + 90, 100, 40, "接见", (50, 150, 50), (100, 200, 100))
                        postpone_btn = Button(SCREEN_WIDTH - 120, y_pos + 90, 100, 40, "推迟", (200, 50, 50), (240, 100, 100))
                        
                        accept_btn.check_hover(mouse_pos)
                        postpone_btn.check_hover(mouse_pos)
                        
                        accept_btn.draw(screen)
                        postpone_btn.draw(screen)
            
            elif game_state.current_view == "save_load":
                # 绘制存档/读档界面
                title_text = header_font.render("存档/读档", True, BLACK)
                screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 380))
                
                # 绘制提示
                tip_text = main_font.render("点击存档槽保存当前游戏进度", True, BLACK)
                screen.blit(tip_text, (SCREEN_WIDTH // 2 - tip_text.get_width() // 2, 250))
                
                # 绘制按钮
                for button in save_load_buttons:
                    button.draw(screen)
            
            # 绘制底部装饰
            pygame.draw.rect(screen, DARK_RED, (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
            footer_text = small_font.render("大清雍正皇帝御览", True, LIGHT_GOLD)
            screen.blit(footer_text, (SCREEN_WIDTH // 2 - footer_text.get_width() // 2, SCREEN_HEIGHT - 30))
            
            # 绘制龙纹装饰
            for i in range(0, SCREEN_WIDTH, 50):
                pygame.draw.line(screen, GOLD, (i, SCREEN_HEIGHT - 40), (i + 25, SCREEN_HEIGHT - 10), 3)
                pygame.draw.line(screen, GOLD, (i + 25, SCREEN_HEIGHT - 10), (i + 50, SCREEN_HEIGHT - 40), 3)
            
            # 绘制设置按钮和返回按钮
            settings_button.draw(screen)
            back_button.draw(screen)
            
            # 绘制设置菜单（如果打开）
            if game_state.settings_open:
                # 半透明背景
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                # 设置菜单背景
                settings_bg = pygame.Surface((SCREEN_WIDTH - 40, 500), pygame.SRCALPHA)
                settings_bg.fill(SETTINGS_BG)
                screen.blit(settings_bg, (20, 80))
                
                # 设置菜单标题
                settings_title = header_font.render("游戏设置", True, LIGHT_GOLD)
                screen.blit(settings_title, (SCREEN_WIDTH // 2 - settings_title.get_width() // 2, 90))
                
                # 绘制设置菜单按钮
                for button in settings_menu_buttons:
                    button.draw(screen)
        
        # 显示警告消息
        if game_state.warning_message:
            show_warning(screen, game_state.warning_message)
        
        # 显示开发者模式
        if game_state.developer_mode:
            dev_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            dev_bg.fill((0, 0, 0, 150))
            screen.blit(dev_bg, (0, 0))
            
            dev_rect = pygame.Rect(100, 300, SCREEN_WIDTH - 200, 300)
            pygame.draw.rect(screen, (50, 50, 100), dev_rect, border_radius=20)
            pygame.draw.rect(screen, (100, 100, 200), dev_rect, 3, border_radius=20)
            
            title_text = title_font.render("开发者模式", True, LIGHT_GOLD)
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 330))
            
            creator_text = header_font.render("创始人: quan", True, WHITE)
            screen.blit(creator_text, (SCREEN_WIDTH // 2 - creator_text.get_width() // 2, 400))
            
            date_text = header_font.render("创作时间: 2025/6/26", True, WHITE)
            screen.blit(date_text, (SCREEN_WIDTH // 2 - date_text.get_width() // 2, 450))
            
            # 关闭按钮
            close_btn = Button(SCREEN_WIDTH // 2 - 100, 520, 200, 60, "关闭", RED, (220, 100, 100), WHITE)
            close_btn.check_hover(mouse_pos)
            close_btn.draw(screen)
            
            # 处理关闭按钮点击
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if close_btn.rect.collidepoint(event.pos):
                        game_state.developer_mode = False
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

# Android服务初始化
def init_android_service():
    try:
        from android import AndroidService
        service = AndroidService('皇上模拟器', '正在运行')
        service.start('服务已启动')
        print("Android服务已启动")
        return True
    except ImportError:
        print("非Android环境")
        return False

# 应用入口点
def run_app():
    # 尝试初始化Android服务
    is_android = init_android_service()
    
    # 启动主游戏循环
    try:
        # 初始化存档/读档界面按钮
        global save_load_buttons
        save_load_buttons = create_save_load_buttons()
        
        main_game_loop()
    except Exception as e:
        print(f"游戏运行出错: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    print("启动皇上模拟器...")
    run_app()
#老天保佑金山银山前路有
#ciallo
#前后有5个ai参与
