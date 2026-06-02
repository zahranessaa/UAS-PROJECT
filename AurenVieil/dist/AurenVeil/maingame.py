import pygame, sys, os, math, random, json
from datetime import datetime
from abc import ABC, abstractmethod 
from dialog import Dialog, STORY, BASE_UPGRADES
import sys

pygame.init()
try:
    pygame.mixer.init()
    _AUDIO = True
except:
    _AUDIO = False


# SETUP LAYAR 

W, H = 1280, 720 
flags = pygame.FULLSCREEN | pygame.SCALED
scr = pygame.display.set_mode((W, H), flags)
pygame.display.set_caption("AurenVeil")
clk = pygame.time.Clock()
FPS = 60

SAVE_FILE = "dkq_save.json"
LEADERBOARD_FILE = "dkq_leaderboard.json"


# WARNA & FONT

BK = (0, 0, 0); WH = (255, 255, 255); GR = (80, 80, 80); LGR = (160, 160, 160)
RD = (210, 40, 40); GN = (50, 190, 80); BL = (60, 130, 230); YL = (240, 200, 40)
OR = (230, 120, 30); TL = (20, 10, 30); CY = (50, 210, 210); EXP_COL = (100, 200, 255)
PU = (180, 50, 200); MAP_BG = (210, 200, 180)

def mkfont(sz):
    try: return pygame.font.SysFont("Courier New", sz, bold=True)
    except: return pygame.font.Font(None, sz)

F14 = mkfont(int(H*0.025)); F18 = mkfont(int(H*0.035))
F24 = mkfont(int(H*0.045)); F48 = mkfont(int(H*0.08))


# PENGATURAN & AUDIO

class Config:
    SFX_VOL = 0.5
    BGM_VOL = 0.5
    FULLSCREEN = True

cfg = Config()

def play_tone(freq, ms):
    if not _AUDIO or cfg.SFX_VOL <= 0: return
    n = int(22050 * ms / 1000)
    buf = bytearray(n * 4)
    for i in range(n):
        v = cfg.SFX_VOL * 0.3 * (1 if math.sin(2*math.pi*freq*(i/22050)) > 0 else -1)
        s = max(-32767, min(32767, int(v * 32767)))
        buf[i*4], buf[i*4+1], buf[i*4+2], buf[i*4+3] = s&0xFF, (s>>8)&0xFF, s&0xFF, (s>>8)&0xFF
    snd = pygame.mixer.Sound(buffer=bytes(buf))
    snd.play()

def play_bgm(filename=None):
    if _AUDIO:
        pygame.mixer.music.stop()
        if filename:
            try:
                pygame.mixer.music.load(filename)
                pygame.mixer.music.set_volume(cfg.BGM_VOL)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"Musik gagal dimuat: {e}")

def update_bgm_vol():
    if _AUDIO: pygame.mixer.music.set_volume(cfg.BGM_VOL)


# GAMBAR

if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def load_img(name, size, fallback_col):
    path = os.path.join(BASE_PATH, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception as e:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, fallback_col, (0, 0, size[0], size[1]), border_radius=8)
        return surf

def tint_image(image, color):
    tinted = image.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

sz_p = int(H*0.06); sz_m = int(H*0.05); sz_b = int(H*0.2); sz_sb = int(H*0.15)
img_player = load_img("karaktermc.png", (120, 120), BL)
img_monster = load_img("monster.png", (sz_m, sz_m), WH)
img_boss = load_img("lastboss.png", (200,200), RD)

img_sb_hutan = load_img("boss_hutan.png", (sz_sb, sz_sb), PU)
img_sb_gurun = load_img("boss_gurun.png", (sz_sb, sz_sb), YL)
img_sb_rawa  = load_img("boss_rawa.png", (sz_sb, sz_sb), (139, 69, 19))
img_sb_salju = load_img("boss_salju.png", (sz_sb, sz_sb), CY)
list_img_sideboss = [img_sb_hutan, img_sb_gurun, img_sb_rawa, img_sb_salju]


sz_ally = (int(H*0.06), int(H*0.06))
img_ally_hutan = load_img("boss_hutan.png", sz_ally, PU)
img_ally_gurun = load_img("boss_gurun.png", sz_ally, YL)
img_ally_rawa  = load_img("boss_rawa.png", sz_ally, (139, 69, 19))
img_ally_salju = load_img("boss_salju.png", sz_ally, CY)
list_img_ally = [img_ally_hutan, img_ally_gurun, img_ally_rawa, img_ally_salju]

sz_peluru = (int(H*0.04), int(H*0.015))
try:
    img_peluru = pygame.image.load(os.path.join(BASE_PATH, "peluru.png")).convert_alpha()
    img_peluru = pygame.transform.scale(img_peluru, sz_peluru)
except:
    img_peluru = pygame.Surface(sz_peluru, pygame.SRCALPHA)
    pygame.draw.ellipse(img_peluru, OR, (0, 0, sz_peluru[0], sz_peluru[1]))
    pygame.draw.ellipse(img_peluru, WH, (0, 0, sz_peluru[0], sz_peluru[1]), 1)

# Monster kecil
img_m_normal = load_img("monster_hijau.png", (sz_m, sz_m), YL)  
img_m_tank   = load_img("monster_biru.png", (sz_m, sz_m), BL)  
img_m_fast   = load_img("monster_merah.png", (sz_m, sz_m), RD) 

sz_tree = (int(H*0.12), int(H*0.18)); sz_flower = (int(H*0.04), int(H*0.04))
img_pohon = load_img("pohon.png", (120, 120), (20, 100, 20))
img_bunga = load_img("flower.png", sz_flower, (255, 100, 200))
img_kaktus = load_img("kaktus.png", sz_tree, (46, 139, 87))
img_saloon = load_img("Saloon.png", (300,300), (46, 139, 87))
img_batu = load_img("batu.png", (30,30), (100, 100, 100))
img_pohonmati = load_img("pohonmati.png", sz_tree, (60, 50, 40))
img_jamur = load_img("jamur.png", sz_flower, (0, 255, 255))
img_pohonsalju = load_img("pohonsalju.png", sz_tree, (200, 220, 230))
img_lava = load_img("pohonmati1.png", (120, 120), (200, 60, 0))
img_tengkorak = load_img("flowermerah.png", sz_flower, (180, 180, 180))
img_bg_map = load_img("map-bg.png", (W, H), MAP_BG)

sz_node = (int(H*0.1), int(H*0.1))
img_node = {
    0: load_img("hutanpinus.png",  sz_node, GN),
    1: load_img("gurun.png",       sz_node, YL),
    2: load_img("rawa.png",        sz_node, (25, 20, 40)),
    3: load_img("salju.png",       sz_node, (200, 220, 230)),
    4: load_img("castiliblis.png", sz_node, RD),
}

try:
    img_bg_menu = pygame.image.load(os.path.join(BASE_PATH, "backgroundmenu.png")).convert()
    img_bg_menu = pygame.transform.scale(img_bg_menu, (W, H))
except:
    img_bg_menu = None 

def draw_dashed_line(surf, color, start_pos, end_pos, width=3, dash_length=15):
    x1, y1 = start_pos; x2, y2 = end_pos
    dl = math.hypot(x2 - x1, y2 - y1)
    if dl == 0: return
    dx = (x2 - x1) / dl; dy = (y2 - y1) / dl
    for i in range(int(dl / dash_length)):
        if i % 2 == 0:
            sx = x1 + dx * (i * dash_length); sy = y1 + dy * (i * dash_length)
            ex = x1 + dx * ((i + 1) * dash_length); ey = y1 + dy * ((i + 1) * dash_length)
            pygame.draw.line(surf, color, (sx, sy), (ex, ey), width)


# Abstraksi

class Entitas(ABC):
    def __init__(self, x, y, img):
        self.x, self.y = x, y; self.img = img
        self.rect = self.img.get_rect(center=(self.x, self.y))
        self.facing_right = True

    def update_hitbox(self):
        self.rect.center = (self.x, self.y)

    def draw(self, surf, cx=0, cy=0):
        img = self.img if self.facing_right else pygame.transform.flip(self.img, True, False)
        draw_rect = img.get_rect(center=(self.x - cx, self.y - cy))
        surf.blit(img, draw_rect)

    @abstractmethod
    def update(self, *args, **kwargs):
        pass 

class ObjekMap(Entitas):
    def __init__(self, x, y, img, is_solid=False):
        super().__init__(x, y, img)
        self.is_solid = is_solid
    def get_hitbox(self):
        w = self.rect.width * 0.4; h = self.rect.height * 0.3
        return pygame.Rect(self.x - w/2, self.y + self.rect.height*0.2 - h/2, w, h)
    def update(self, *args, **kwargs): pass

class BossObj(Entitas):
    def __init__(self, x, y):
        super().__init__(x, y, img_boss)
        self.hp = 10000; self.max_hp = 10000
    def update(self, *args, **kwargs): pass


# INHERITANCE & ENCAPSULATION

class Player(Entitas):
    def __init__(self, x, y):
        super().__init__(x, y, img_player)
        self.__hp = 100       
        self.__max_hp = 100   
        self.hp_regen = 0.04 
        self.base_speed = H * 0.007; self.speed_mult = 1.0
        self.slash_dmg = 10; self.slash_cd_max = 25
        self.slash_radius = H * 0.15
        self.magnet_radius = H * 0.15
        self.level = 1; self.exp = 0; self.max_exp = 50
        
        self.skills = {"listrik": 0, "api": 0, "air": 0, "tanah": 0}
        self.cd_skills = {"listrik": 0, "api": 0, "air": 0, "tanah": 0}
        
        self.invuln = 0
        self.cd_slash = 0
        self.cd_dash = 0
        self.anim_slash = 0; self.slash_angle = 0
        self.last_tap = {pygame.K_w: 0, pygame.K_a: 0, pygame.K_s: 0, pygame.K_d: 0}
        self.dash_timer = 0; self.dash_dir = (0, 0)

    def get_hp(self): return self.__hp
    def get_max_hp(self): return self.__max_hp
    def take_damage(self, amount):
        self.__hp -= amount
        if self.__hp < 0: self.__hp = 0
    def heal(self, amount):
        self.__hp = min(self.__max_hp, self.__hp + amount)
    def add_max_hp(self, amount):
        self.__max_hp += amount
        self.__hp += amount
    def set_loaded_hp(self, max_hp):
        self.__max_hp = max_hp
        self.__hp = max_hp
    
    def handle_dash(self, key):
        if self.cd_dash > 0:
            return
            
        now = pygame.time.get_ticks()
        if key in self.last_tap:
            if now - self.last_tap[key] < 250:
                self.dash_timer = 12; play_tone(600, 50)
                
                self.cd_dash = 20
                
                if key == pygame.K_w: self.dash_dir = (0, -1)
                elif key == pygame.K_s: self.dash_dir = (0, 1)
                elif key == pygame.K_a: self.dash_dir = (-1, 0)
                elif key == pygame.K_d: self.dash_dir = (1, 0)
            self.last_tap[key] = now

    def bergerak(self, keys, bounds, obstacles):
        speed = self.base_speed * self.speed_mult
        speed = speed * 3.5 if self.dash_timer > 0 else speed
        if self.dash_timer > 0:
            self.dash_timer -= 1
            dx, dy = self.dash_dir[0] * speed, self.dash_dir[1] * speed
        else:
            dx = dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= speed; self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += speed; self.facing_right = True
            if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += speed
            if dx != 0 and dy != 0: dx *= 0.707; dy *= 0.707

        self.x += dx
        ph_x = pygame.Rect(self.x - sz_p*0.2, self.y - sz_p*0.1, sz_p*0.4, sz_p*0.4) 
        for obs in obstacles:
            if ph_x.colliderect(obs.get_hitbox()): self.x -= dx; break

        self.y += dy
        ph_y = pygame.Rect(self.x - sz_p*0.2, self.y - sz_p*0.1, sz_p*0.4, sz_p*0.4)
        for obs in obstacles:
            if ph_y.colliderect(obs.get_hitbox()): self.y -= dy; break

        self.x = max(sz_p, min(bounds[0]-sz_p, self.x))
        self.y = max(sz_p, min(bounds[1]-sz_p, self.y))
        self.update_hitbox()
    
    def update(self, *args, **kwargs):
        if self.cd_slash > 0: self.cd_slash -= 1
        if self.cd_dash > 0: self.cd_dash -= 1
        if self.anim_slash > 0: self.anim_slash -= 1
        if self.invuln > 0: self.invuln -= 1
        if 0 < self.__hp < self.__max_hp: self.heal(self.hp_regen)
        
        for k in self.cd_skills:
            if self.cd_skills[k] > 0: self.cd_skills[k] -= 1

    def draw(self, surf, cx=0, cy=0):
        img = self.img if self.facing_right else pygame.transform.flip(self.img, True, False)
        if self.invuln > 0 and (self.invuln // 4) % 2 == 0: img.set_alpha(100)
        else: img.set_alpha(255)
        draw_rect = img.get_rect(center=(self.x - cx, self.y - cy))
        surf.blit(img, draw_rect)

    def draw_slash(self, surf, cx=0, cy=0):
        if self.anim_slash > 0:
            px = self.x - cx; py = self.y - cy
            prog = 1.0 - (self.anim_slash / 8.0) 
            r = self.slash_radius * (0.6 + 0.4 * prog)
            start_ang = self.slash_angle - math.radians(70)
            end_ang = self.slash_angle + math.radians(70)
            points = []
            for i in range(11):
                f = i / 10.0; ang = start_ang + (end_ang - start_ang) * f
                points.append((px + math.cos(ang) * r, py + math.sin(ang) * r))
            for i in range(10, -1, -1):
                f = i / 10.0; ang = start_ang + (end_ang - start_ang) * f
                thickness = math.sin(f * math.pi) * (25 * (1.0 - prog))
                inner_r = r - thickness
                points.append((px + math.cos(ang) * inner_r, py + math.sin(ang) * inner_r))
            pygame.draw.polygon(surf, WH, points)

class Monster(Entitas):
    def __init__(self, x, y, stage_diff=1):
        self.m_type = random.choice([0, 0, 0, 1, 2])
        spd_mult = 1 + (stage_diff - 1) * 0.1 
        if self.m_type == 0:
            super().__init__(x, y, img_m_normal)
            self.max_hp = 20 * stage_diff; self.speed = H * 0.003 * spd_mult
        elif self.m_type == 1:
            super().__init__(x, y, img_m_tank)
            self.max_hp = 50 * stage_diff; self.speed = H * 0.0015 * spd_mult
        else:
            super().__init__(x, y, img_m_fast)
            self.max_hp = 10 * stage_diff; self.speed = H * 0.005 * spd_mult
            
        self.hp = self.max_hp; self.stun = 0
        self.cd_shoot = random.randint(60, 180)
        self.vx = random.choice([-2, 2, -3, 3]); self.vy = random.choice([-2, 2, -3, 3])

    def update(self, *args, **kwargs): pass

    def draw(self, surf, cx=0, cy=0):
        super().draw(surf, cx, cy)
        hp_pct = max(0, self.hp) / self.max_hp
        if getattr(self, "m_type", 0) == 99:
            bar_w = int(H*0.15)
            pygame.draw.rect(surf, RD, (self.x - cx - bar_w//2, self.y - cy - int(H*0.1), bar_w, 8))
            pygame.draw.rect(surf, GN, (self.x - cx - bar_w//2, self.y - cy - int(H*0.1), bar_w * hp_pct, 8))
        else:
            bar_w = sz_m
            pygame.draw.rect(surf, RD, (self.x - cx - bar_w//2, self.y - cy - sz_m//2 - 10, bar_w, 5))
            pygame.draw.rect(surf, GN, (self.x - cx - bar_w//2, self.y - cy - sz_m//2 - 10, bar_w * hp_pct, 5))

class Peluru(Entitas):
    def __init__(self, x, y, img, vx, vy, is_player):
        super().__init__(x, y, img)
        self.vx, self.vy = vx, vy; self.is_player = is_player
        angle = math.degrees(math.atan2(-vy, vx))
        self.rotated_img = pygame.transform.rotate(self.img, angle)
        
    def gerak(self):
        self.x += self.vx; self.y += self.vy
        self.update_hitbox()

    def update(self, *args, **kwargs): pass

    def draw(self, surf, cx=0, cy=0):
        draw_rect = self.rotated_img.get_rect(center=(self.x - cx, self.y - cy))
        surf.blit(self.rotated_img, draw_rect)

class ExpGem(Entitas):
    def __init__(self, x, y, amt):
        super().__init__(x, y, pygame.Surface((0,0)))
        self.amt = amt
    def update(self, *args, **kwargs): pass
    def draw(self, surf, cx, cy):
        pygame.draw.circle(surf, EXP_COL, (int(self.x - cx), int(self.y - cy)), 6)
        pygame.draw.circle(surf, WH, (int(self.x - cx), int(self.y - cy)), 3)

class Companion(Entitas):
    def __init__(self, type_id):
        super().__init__(0, 0, list_img_ally[type_id % 4])
        self.type_id = type_id; self.cd_atk = 0; self.angle_offset = type_id * (math.pi / 2)

    def update(self, px, py, game_obj):
        self.angle_offset += 0.05
        target_x = px + math.cos(self.angle_offset) * (H * 0.1)
        target_y = py + math.sin(self.angle_offset) * (H * 0.1)
        self.x += (target_x - self.x) * 0.1; self.y += (target_y - self.y) * 0.1
        self.update_hitbox()
        
        self.facing_right = (px > self.x)
        
        if self.cd_atk > 0: self.cd_atk -= 1
        targets = game_obj.get_valid_targets()
        
        if self.cd_atk <= 0 and targets:
            terdekat = min(targets, key=lambda m: math.hypot(m.x - self.x, m.y - self.y))
            if math.hypot(terdekat.x - self.x, terdekat.y - self.y) < H * 0.6:
                lvl_bonus = game_obj.player.level * 2
                self.facing_right = (terdekat.x > self.x)
                
                if self.type_id == 0: 
                    game_obj.active_lightnings.append({"source": self, "target": terdekat, "timer": 15})
                    terdekat.hp -= 20 + lvl_bonus
                    if hasattr(terdekat, 'stun'): terdekat.stun = 30
                    play_tone(1500, 100); self.cd_atk = 60
                
                elif self.type_id == 1: 
                    ang = math.atan2(terdekat.y - self.y, terdekat.x - self.x)
                    game_obj.peluru_api.append({"x": self.x, "y": self.y, "vx": math.cos(ang)*H*0.015, "vy": math.sin(ang)*H*0.015, "timer": 60})
                    play_tone(1200, 100); self.cd_atk = 60
                
                elif self.type_id == 2: 
                    game_obj.efek_tanah.append({"x": terdekat.x, "y": terdekat.y, "timer": 30})
                    terdekat.hp -= 30 + lvl_bonus
                    if hasattr(terdekat, 'stun'): terdekat.stun = 60
                    play_tone(200, 200); self.cd_atk = 90
                
                elif self.type_id == 3: 
                    game_obj.efek_air.append({"x": self.x, "y": self.y, "r": 0, "max_r": H*0.2, "timer": 20})
                    play_tone(800, 150)
                    for m in targets:
                        if math.hypot(m.x - self.x, m.y - self.y) < H*0.2:
                            m.hp -= 15 + lvl_bonus
                            if hasattr(m, 'stun'): m.stun = 20
                            if m.hp <= 0: game_obj.kill_monster(m)
                    self.cd_atk = 120
                
                if terdekat.hp <= 0: game_obj.kill_monster(terdekat)

def txt(surf, s, font, col, x, y, cx=False, cy=False):
    ren = font.render(s, False, col); sh = font.render(s, False, BK)
    bx = x - ren.get_width()//2 if cx else x; by = y - ren.get_height()//2 if cy else y
    surf.blit(sh, (bx+2, by+2)); surf.blit(ren, (bx, by))


# MAIN

class Main:
    def __init__(self):
        play_bgm("mainmenu.mp3")
        self.state = "TITLE"; self.prev_state = "TITLE"; self.sel = 0
        self.return_from_options = "TITLE"
        self.player = Player(W//2, H//2); self.dlg = Dialog()
        self.score = 0
        self.cam_x = 0; self.cam_y = 0
        self.world_w = W * 3; self.world_h = H * 3
        self.active_story_key = ""
        
        self.stage_timer = 0; self.side_boss_spawned = False; self.side_boss = None
        self.gems = []; self.companions = []; self.upgrade_choices = []
        self.peluru_hutan = []; self.peluru = []
        self.monsters = []
        
        self.peluru_api = []
        self.ledakan_api = []
        self.efek_air = []
        self.efek_tanah = []
        self.active_lightnings = [] 
        self.bom_waktu = []
        
        self.decos = []; self.obstacles = []
        self.bg_surface = None 
        self.bg_color = GN
        
        self.map_nodes = [
            {"id": 0, "name": "Hutan Pinus", "x": W*0.5, "y": H*0.8, "type": "HUNT", "story": "hutan_masuk"},
            {"id": 1, "name": "Gurun Wild West", "x": W*0.35, "y": H*0.6, "type": "HUNT", "story": "gurun_masuk"},
            {"id": 2, "name": "Rawa Gelap", "x": W*0.65, "y": H*0.6, "type": "HUNT", "story": "rawa_masuk"},
            {"id": 3, "name": "Lembah Salju", "x": W*0.5, "y": H*0.4, "type": "HUNT", "story": "salju_masuk"},
            {"id": 4, "name": "Kastil Raja Iblis", "x": W*0.5, "y": H*0.15, "type": "BOSS", "story": "boss_masuk"}
        ]
        self.map_links = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
        self.cleared_nodes = []; self.current_node_id = -1; self.target_node_id = -1

    def generate_map_objects(self, node_id):
        self.decos = []; self.obstacles = []
        ww, wh = self.world_w, self.world_h
        
        if node_id == 4: self.bg_color = (60, 10, 10) 
        elif node_id == 1: self.bg_color = (210, 180, 140)
        elif node_id == 2: self.bg_color = (25, 20, 40)
        elif node_id == 3: self.bg_color = (230, 240, 255)
        else: self.bg_color = (34, 139, 34) 
        
        self.bg_surface = pygame.Surface((ww, wh))
        try:
            map_img = pygame.image.load(os.path.join(BASE_PATH, f"map_{node_id}.jpg")).convert()
            self.bg_surface = pygame.transform.scale(map_img, (ww, wh))
        except:
            tiles = []
            
            try:
                t1 = pygame.image.load(os.path.join(BASE_PATH, f"tile_{node_id}_1.png")).convert()
                t2 = pygame.image.load(os.path.join(BASE_PATH, f"tile_{node_id}_2.png")).convert()
                t3 = pygame.image.load(os.path.join(BASE_PATH, f"tile_{node_id}_3.png")).convert()
                
                tiles.append(pygame.transform.scale(t1, (16, 16)))
                tiles.append(pygame.transform.scale(t2, (16, 16)))
                tiles.append(pygame.transform.scale(t3, (16, 16)))
            except:
                for _ in range(4):
                    tsurf = pygame.Surface((16, 16))
                    offset = random.randint(-15, 15)
                    r = max(0, min(255, self.bg_color[0] + offset))
                    g = max(0, min(255, self.bg_color[1] + offset))
                    b = max(0, min(255, self.bg_color[2] + offset))
                    tsurf.fill((r, g, b))
                    tiles.append(tsurf)
                    
            for tx in range(0, ww, 16):
                for ty in range(0, wh, 16):
                    self.bg_surface.blit(random.choice(tiles), (tx, ty))

        if node_id == 4:
            for _ in range(80): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_tengkorak, False))
            for _ in range(30): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_lava, True))
        elif node_id == 1:
            for _ in range(30): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_batu, False))
            for _ in range(80): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_kaktus, True))
        elif node_id == 2:
            for _ in range(150): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_jamur, False))
            for _ in range(100): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_pohonmati, True))
        elif node_id == 3:
            for _ in range(100): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_pohonsalju, True))
        else:
            for _ in range(150): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_bunga, False))
            for _ in range(120): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_pohon, True))
            
        self.obstacles = [o for o in self.obstacles if math.hypot(o.x - ww//2, o.y - wh//2) > H*0.2]

    def save_game(self):
        data = {
            "cleared_nodes": self.cleared_nodes, "current_node_id": self.current_node_id, "score": self.score,
            "level": self.player.level, "max_hp": self.player.get_max_hp(),
            "speed_mult": self.player.speed_mult, "slash_dmg": self.player.slash_dmg,
            "slash_cd_max": self.player.slash_cd_max, "slash_radius": self.player.slash_radius, 
            "magnet_radius": self.player.magnet_radius, "skills": self.player.skills
        }
        with open(SAVE_FILE, "w") as f: json.dump(data, f)

    def load_game(self):
        try:
            with open(SAVE_FILE, "r") as f:
                d = json.load(f)
                self.cleared_nodes = d.get("cleared_nodes", [])
                self.current_node_id = d.get("current_node_id", -1)
                self.score = d.get("score", 0); self.player.level = d.get("level", 1)
                self.player.set_loaded_hp(d.get("max_hp", 100))
                self.player.speed_mult = d.get("speed_mult", 1.0); self.player.slash_dmg = d.get("slash_dmg", 10)
                self.player.slash_cd_max = d.get("slash_cd_max", 25)
                self.player.slash_radius = d.get("slash_radius", H*0.15); self.player.magnet_radius = d.get("magnet_radius", H*0.15)
                self.player.skills = d.get("skills", {"listrik": 0, "api": 0, "air": 0, "tanah": 0})
                self.companions = [Companion(n) for n in self.cleared_nodes]
                self.state = "MAP"
                return True
        except: return False

    def save_to_leaderboard(self):
        try:
            with open(LEADERBOARD_FILE, "r") as f: lb = json.load(f)
        except: lb = []
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        lb.append({"score": int(self.score), "date": date_str, "level": self.player.level})
        lb.sort(key=lambda x: x["score"], reverse=True)
        with open(LEADERBOARD_FILE, "w") as f: json.dump(lb[:5], f)

    def is_node_available(self, node_id):
        if node_id == 0: return True
        if node_id in self.cleared_nodes: return True 
        
        for (n1, n2) in self.map_links:
            if n1 in self.cleared_nodes and n2 == node_id: return True
            if n2 in self.cleared_nodes and n1 == node_id: return True 
        return False

    def set_story(self, key):
        self.active_story_key = key; self.dlg.set(*STORY[key]); self.state = "STORY"

    def trigger_level_up(self):
        self.player.level += 1; self.player.exp -= self.player.max_exp
        self.player.max_exp = int(self.player.max_exp * 1.5)
        
        pool = BASE_UPGRADES[:]
        for sk, name in [("listrik", "Petir"), ("api", "Bola Api"), ("air", "Nova Air"), ("tanah", "Paku Tanah")]:
            lvl = self.player.skills[sk]
            if lvl < 5: 
                desc = f"Membuka elemen {name} otomatis." if lvl == 0 else f"Meningkatkan {name} menjadi Level {lvl+1}."
                pool.append({"id": sk, "name": f"{name} Lv.{lvl+1}", "desc": desc})

        self.upgrade_choices = random.sample(pool, min(3, len(pool)))
        self.prev_state = self.state; self.state = "LEVEL_UP"; self.sel = 0; play_tone(1000, 200)

    def apply_upgrade(self, upg_id):
        if upg_id == "hp": self.player.add_max_hp(20)
        elif upg_id == "dmg": self.player.slash_dmg += 10
        elif upg_id == "spd": self.player.speed_mult += 0.1
        elif upg_id == "cd": self.player.slash_cd_max = max(5, self.player.slash_cd_max - 4)
        elif upg_id == "rad": self.player.slash_radius += H * 0.03
        elif upg_id == "mag": self.player.magnet_radius += H * 0.05
        elif upg_id in self.player.skills: self.player.skills[upg_id] += 1 
        self.state = self.prev_state

    def kill_monster(self, m):
        if m in self.monsters:
            self.score += int(getattr(m, "max_hp", 10)) 
            if getattr(m, "m_type", 0) == 99:
                self.side_boss = None
            else:
                self.gems.append(ExpGem(m.x, m.y, 10))
                if getattr(m, "m_type", 0) == 1:
                    self.bom_waktu.append({"x": m.x, "y": m.y, "timer": 90})
            self.monsters.remove(m)

    def get_valid_targets(self):
        targets = self.monsters[:]
        if self.state == "BOSS" and hasattr(self, 'boss') and self.boss.hp > 0:
            targets.append(self.boss)
        return targets

    def teleport_to_map(self, node_id):
        bgm_map = {
            0: "bgm-hutan.mp3",
            4: "bgm_boss.mp3",
        }
        play_bgm(bgm_map.get(node_id, "gameplay_music.mp3"))

        node = self.map_nodes[node_id]
        self.generate_map_objects(node['id'])
        self.peluru_api = []; self.ledakan_api = []
        self.efek_air = []; self.efek_tanah = []; self.active_lightnings = []
        self.bom_waktu = []
        
        if node['type'] == 'HUNT':
            self.state = "HUNT"
            self.player.x, self.player.y = self.world_w // 2, self.world_h // 2
            self.peluru_hutan = []; self.gems = []; self.monsters = []
            self.stage_timer = 0; self.side_boss_spawned = False; self.side_boss = None
        elif node['type'] == 'BOSS':
            self.state = "BOSS"
            self.boss = BossObj(self.world_w//2, self.world_h//2) 
            self.boss.max_hp = int(20000 + (self.player.level * 500))
            self.boss.hp = self.boss.max_hp
            self.monsters = [] 
            self.boss_timer = 0
            self.player.x, self.player.y = self.world_w//2, self.world_h - H//2

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
                self.handle_input(ev)
            self.update()
            self.draw()
            pygame.display.flip()
            clk.tick(FPS)

    def handle_input(self, ev):
        global scr  
        has_save = os.path.exists(SAVE_FILE)
        title_opts = ["Mulai Baru", "Lanjutkan", "Leaderboard", "Developer Mode", "Pengaturan", "Keluar"] if has_save else ["Mulai Baru", "Leaderboard", "Developer Mode", "Pengaturan", "Keluar"]
        
        if ev.type == pygame.MOUSEMOTION:
            mx, my = ev.pos
            if self.state == "TITLE":
                for i in range(len(title_opts)):
                    if pygame.Rect(W*0.02, H*0.35 + i*(H*0.08) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i
            elif self.state == "DEV_MODE":
                for i in range(6):
                    if pygame.Rect(W//2 - W*0.2, H*0.3 + i*50 - 20, W*0.4, 40).collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i
            elif self.state == "OPTIONS":
                for i in range(4):
                    if pygame.Rect(W//2 - W*0.2, H*0.4 + i*(H*0.08) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i
            elif self.state == "PAUSE":
                for i in range(3):
                    if pygame.Rect(W//2 - W*0.2, H*0.5 + i*(H*0.1) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = pygame.mouse.get_pos()
            
            if self.state == "TITLE":
                for i in range(len(title_opts)):
                    if pygame.Rect(W*0.02, H*0.35 + i*(H*0.08) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        self.sel = i; play_tone(600, 100)
                        act = title_opts[i]
                        if act == "Mulai Baru": 
                            self.player = Player(W//2, H//2)
                            self.cleared_nodes = []; self.current_node_id = -1; self.companions = []
                            self.score = 0
                            self.set_story("intro") 
                        elif act == "Lanjutkan": self.load_game()
                        elif act == "Leaderboard": self.state = "LEADERBOARD"
                        elif act == "Developer Mode": self.sel = 0; self.state = "DEV_MODE"
                        elif act == "Pengaturan": self.sel = 0; self.return_from_options = "TITLE"; self.state = "OPTIONS"
                        else: pygame.quit(); sys.exit()
                        break
            
            elif self.state == "DEV_MODE":
                for i in range(6):
                    if pygame.Rect(W//2 - W*0.2, H*0.3 + i*50 - 20, W*0.4, 40).collidepoint(mx, my):
                        self.sel = i; play_tone(600, 100)
                        if self.sel < 5:
                            self.player = Player(W//2, H//2)
                            self.player.add_max_hp(900); self.player.slash_dmg = 200
                            self.player.skills = {"listrik": 5, "api": 5, "air": 5, "tanah": 5}
                            self.target_node_id = self.sel
                            self.current_node_id = self.sel 
                            self.teleport_to_map(self.sel) 
                        else:
                            self.state = "TITLE"; self.sel = 0
                        break
                        
            elif self.state == "OPTIONS":
                for i in range(4):
                    if pygame.Rect(W//2 - W*0.2, H*0.4 + i*(H*0.08) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        self.sel = i; play_tone(600, 100)
                        if self.sel == 3: 
                            self.sel = 0; self.state = getattr(self, 'return_from_options', 'TITLE')
                            if self.state == "PAUSE": self.sel = 1
                        elif self.sel == 0: 
                            if mx < W//2: cfg.SFX_VOL = max(0.0, round(cfg.SFX_VOL - 0.1, 1))
                            else: cfg.SFX_VOL = min(1.0, round(cfg.SFX_VOL + 0.1, 1))
                            play_tone(400, 50)
                        elif self.sel == 1: 
                            if mx < W//2: cfg.BGM_VOL = max(0.0, round(cfg.BGM_VOL - 0.1, 1))
                            else: cfg.BGM_VOL = min(1.0, round(cfg.BGM_VOL + 0.1, 1))
                            update_bgm_vol()
                        elif self.sel == 2:
                            cfg.FULLSCREEN = not cfg.FULLSCREEN
                            scr = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED if cfg.FULLSCREEN else pygame.SCALED)
                        break
            
            elif self.state == "PAUSE":
                for i in range(3):
                    if pygame.Rect(W//2 - W*0.2, H*0.5 + i*(H*0.1) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        self.sel = i; play_tone(600, 100)
                        if self.sel == 0: pygame.mixer.music.unpause(); self.state = self.prev_state
                        elif self.sel == 1: self.return_from_options = "PAUSE"; self.state = "OPTIONS"; self.sel = 0
                        else: pygame.mixer.music.stop(); self.state = "TITLE"; self.sel = 0
                        break

            elif self.state == "STORY":
                self.dlg.next_page()
                if self.dlg.done: self.finish_dialog()
            
            elif self.state == "LEVEL_UP":
                box_w, box_h = W*0.25, H*0.3; by = H*0.4
                for i, upg in enumerate(self.upgrade_choices):
                    if pygame.Rect(W*0.1 + i * (box_w + W*0.05), by, box_w, box_h).collidepoint(mx, my):
                        play_tone(800, 100); self.apply_upgrade(upg["id"]); break

            elif self.state == "MAP":
                for node in self.map_nodes:
                    if self.is_node_available(node['id']):
                        if math.hypot(node['x'] - mx, node['y'] - my) < H*0.05:
                            self.target_node_id = node['id']
                            self.set_story(node['story']); play_tone(600, 100)
                            break

        elif ev.type == pygame.KEYDOWN:
            k = ev.key
            if self.state in ["HUNT", "BOSS"]: self.player.handle_dash(k)

            if self.state == "TITLE":
                if k in (pygame.K_w, pygame.K_UP): self.sel = (self.sel - 1) % len(title_opts); play_tone(400, 50)
                if k in (pygame.K_s, pygame.K_DOWN): self.sel = (self.sel + 1) % len(title_opts); play_tone(400, 50)
                if k == pygame.K_RETURN:
                    play_tone(600, 100); act = title_opts[self.sel]
                    if act == "Mulai Baru": 
                        self.player = Player(W//2, H//2)
                        self.cleared_nodes = []; self.current_node_id = -1; self.companions = []
                        self.score = 0
                        self.set_story("intro")
                    elif act == "Lanjutkan": self.load_game()
                    elif act == "Leaderboard": self.state = "LEADERBOARD"
                    elif act == "Developer Mode": self.sel = 0; self.state = "DEV_MODE"
                    elif act == "Pengaturan": self.sel = 0; self.return_from_options = "TITLE"; self.state = "OPTIONS"
                    else: pygame.quit(); sys.exit()
                        
            elif self.state == "DEV_MODE":
                if k in (pygame.K_w, pygame.K_UP): self.sel = (self.sel - 1) % 6; play_tone(400, 50)
                if k in (pygame.K_s, pygame.K_DOWN): self.sel = (self.sel + 1) % 6; play_tone(400, 50)
                if k == pygame.K_RETURN:
                    play_tone(800, 100)
                    if self.sel < 5:
                        self.player = Player(W//2, H//2)
                        self.player.add_max_hp(900); self.player.slash_dmg = 200 
                        self.player.skills = {"listrik": 5, "api": 5, "air": 5, "tanah": 5}
                        self.target_node_id = self.sel
                        self.current_node_id = self.sel 
                        self.teleport_to_map(self.sel)
                    else:
                        self.state = "TITLE"; self.sel = 0

            elif self.state == "OPTIONS":
                if k in (pygame.K_w, pygame.K_UP): self.sel = (self.sel - 1) % 4; play_tone(400, 50)
                if k in (pygame.K_s, pygame.K_DOWN): self.sel = (self.sel + 1) % 4; play_tone(400, 50)
                if k in (pygame.K_a, pygame.K_LEFT):
                    if self.sel == 0: cfg.SFX_VOL = max(0.0, round(cfg.SFX_VOL - 0.1, 1)); play_tone(400, 50)
                    elif self.sel == 1: cfg.BGM_VOL = max(0.0, round(cfg.BGM_VOL - 0.1, 1)); update_bgm_vol()
                if k in (pygame.K_d, pygame.K_RIGHT):
                    if self.sel == 0: cfg.SFX_VOL = min(1.0, round(cfg.SFX_VOL + 0.1, 1)); play_tone(400, 50)
                    elif self.sel == 1: cfg.BGM_VOL = min(1.0, round(cfg.BGM_VOL + 0.1, 1)); update_bgm_vol()
                if k == pygame.K_RETURN and self.sel == 2:
                    cfg.FULLSCREEN = not cfg.FULLSCREEN
                    scr = pygame.display.set_mode((W, H), pygame.FULLSCREEN | pygame.SCALED if cfg.FULLSCREEN else pygame.SCALED)
                    play_tone(400, 50)
                if k == pygame.K_RETURN and self.sel == 3: 
                    self.sel = 0; self.state = getattr(self, 'return_from_options', 'TITLE')
                    if self.state == "PAUSE": self.sel = 1

            elif self.state == "LEADERBOARD":
                if k in (pygame.K_RETURN, pygame.K_ESCAPE): self.state = "TITLE"; self.sel = 0; play_tone(400, 50)

            elif self.state == "LEVEL_UP":
                if k in (pygame.K_a, pygame.K_LEFT): self.sel = max(0, self.sel - 1); play_tone(400, 50)
                if k in (pygame.K_d, pygame.K_RIGHT): self.sel = min(2, self.sel + 1); play_tone(400, 50)
                if k == pygame.K_RETURN: play_tone(800, 100); self.apply_upgrade(self.upgrade_choices[self.sel]["id"])

            elif self.state == "PAUSE":
                if k in (pygame.K_w, pygame.K_UP): self.sel = (self.sel - 1) % 3; play_tone(400, 50)
                if k in (pygame.K_s, pygame.K_DOWN): self.sel = (self.sel + 1) % 3; play_tone(400, 50)
                if k == pygame.K_RETURN:
                    play_tone(600, 100)
                    if self.sel == 0: pygame.mixer.music.unpause(); self.state = self.prev_state
                    elif self.sel == 1: self.return_from_options = "PAUSE"; self.state = "OPTIONS"; self.sel = 0
                    else: pygame.mixer.music.stop(); self.state = "TITLE"; self.sel = 0

            elif self.state == "STORY":
                if k in (pygame.K_RETURN, pygame.K_SPACE):
                    self.dlg.next_page()
                    if self.dlg.done: self.finish_dialog()
            
            if k == pygame.K_ESCAPE:
                if self.state in ["MAP", "HUNT", "BOSS"]: self.prev_state = self.state; self.state = "PAUSE"; self.sel = 0
                pygame.mixer.music.pause()

    def finish_dialog(self):
        if self.active_story_key == "intro":
            play_bgm("gameplay_music.mp3")
            self.state = "MAP"
        elif self.active_story_key in ["boss_win", "boss_lose"]: 
            self.save_to_leaderboard()
            play_bgm("mainmenu.mp3")
            self.state = "TITLE"; self.sel = 0
        elif self.target_node_id != -1 and self.state != "MAP":
            self.current_node_id = self.target_node_id 
            self.teleport_to_map(self.target_node_id)
            self.target_node_id = -1
        else:
            self.state = "MAP"

    def update(self):
        keys = pygame.key.get_pressed()
        if self.state not in ["PAUSE", "TITLE", "OPTIONS", "LEVEL_UP", "LEADERBOARD", "DEV_MODE"]:
            self.player.update()

        if self.state == "STORY": self.dlg.update()

        elif self.state == "HUNT" or self.state == "BOSS":
            
            # --- SISTEM AUTO ATTACK (DENGAN JEDA) ---
            if self.player.cd_slash <= 0:
                mx, my = pygame.mouse.get_pos()
                wmx, wmy = mx + self.cam_x, my + self.cam_y
                self.player.slash_angle = math.atan2(wmy - self.player.y, wmx - self.player.x)
                
                # JEDA SERANGAN: 45 frame = 0.75 detik (karena game berjalan di 60 FPS)
                self.player.cd_slash = 45 
                
                self.player.anim_slash = 8; play_tone(800, 50)
                slash_r = self.player.slash_radius
                
                if self.state == "HUNT":
                    for m in self.monsters[:]:
                        if math.hypot(m.x - self.player.x, m.y - self.player.y) < slash_r:
                            m_ang = math.atan2(m.y - self.player.y, m.x - self.player.x)
                            if abs(math.remainder(m_ang - self.player.slash_angle, math.tau)) < math.radians(60):
                                m.hp -= self.player.slash_dmg; m.stun = 20; play_tone(150, 50)
                                if m.hp <= 0: self.kill_monster(m); play_tone(900, 50)
                elif self.state == "BOSS":
                    if hasattr(self, 'boss') and self.boss.hp > 0:
                        if math.hypot(self.boss.x - self.player.x, self.boss.y - self.player.y) < slash_r:
                            b_ang = math.atan2(self.boss.y - self.player.y, self.boss.x - self.player.x)
                            if abs(math.remainder(b_ang - self.player.slash_angle, math.tau)) < math.radians(60):
                                self.boss.hp -= self.player.slash_dmg; play_tone(150, 50)
            
            targets = self.get_valid_targets()
            
            # --- LOGIKA BOM WAKTU MONSTER BIRU ---
            for b in getattr(self, "bom_waktu", [])[:]:
                b["timer"] -= 1
                if b["timer"] <= 0:
                    self.ledakan_api.append({"x": b["x"], "y": b["y"], "r": 0, "max_r": H*0.12, "timer": 15})
                    play_tone(300, 150)
                    if math.hypot(self.player.x - b["x"], self.player.y - b["y"]) < H*0.12:
                        if self.player.invuln <= 0:
                            self.player.take_damage(20)
                            self.player.invuln = 45; play_tone(100, 100)
                    self.bom_waktu.remove(b)
            
            for p in self.peluru_api[:]:
                p["x"] += p["vx"]; p["y"] += p["vy"]; p["timer"] -= 1
                hit = False
                for m in targets:
                    if math.hypot(p["x"] - m.x, p["y"] - m.y) < H*0.05:
                        hit = True; break
                if hit or p["timer"] <= 0:
                    self.ledakan_api.append({"x": p["x"], "y": p["y"], "r": 0, "max_r": H*0.1 + self.player.skills["api"]*H*0.02, "timer": 15})
                    self.peluru_api.remove(p); play_tone(300, 100)

            for e in self.ledakan_api[:]:
                if e["r"] == 0: 
                    for m in targets:
                        if math.hypot(m.x - e["x"], m.y - e["y"]) < e["max_r"]:
                            m.hp -= 30 + 15 * self.player.skills["api"]
                            if m.hp <= 0: self.kill_monster(m)
                e["r"] += e["max_r"] / 15
                e["timer"] -= 1
                if e["timer"] <= 0: self.ledakan_api.remove(e)

            for e in self.efek_air[:]:
                e["r"] += e["max_r"] / 20
                e["timer"] -= 1
                if e["timer"] <= 0: self.efek_air.remove(e)

            for e in self.efek_tanah[:]:
                e["timer"] -= 1
                if e["timer"] <= 0: self.efek_tanah.remove(e)
                
            for l in self.active_lightnings[:]:
                l["timer"] -= 1
                if l["timer"] <= 0: self.active_lightnings.remove(l)

            if targets:
                if self.player.skills["listrik"] > 0 and self.player.cd_skills["listrik"] <= 0:
                    self.player.cd_skills["listrik"] = max(30, 120 - self.player.skills["listrik"]*15)
                    nearest = sorted(targets, key=lambda m: math.hypot(m.x-self.player.x, m.y-self.player.y))
                    hit_targets = nearest[:self.player.skills["listrik"]]
                    if hit_targets:
                        play_tone(1500, 150)
                        for t in hit_targets:
                            self.active_lightnings.append({"source": self.player, "target": t, "timer": 15})
                            t.hp -= 30 + 15 * self.player.skills["listrik"]
                            if hasattr(t, 'stun'): t.stun = 40
                            if t.hp <= 0: self.kill_monster(t)

                if self.player.skills["api"] > 0 and self.player.cd_skills["api"] <= 0:
                    self.player.cd_skills["api"] = max(30, 90 - self.player.skills["api"]*10)
                    nearest = sorted(targets, key=lambda m: math.hypot(m.x-self.player.x, m.y-self.player.y))
                    for i in range(min(self.player.skills["api"], len(nearest))):
                        ang = math.atan2(nearest[i].y - self.player.y, nearest[i].x - self.player.x)
                        self.peluru_api.append({"x": self.player.x, "y": self.player.y, "vx": math.cos(ang)*H*0.015, "vy": math.sin(ang)*H*0.015, "timer": 60})
                    play_tone(1200, 100)

                if self.player.skills["air"] > 0 and self.player.cd_skills["air"] <= 0:
                    self.player.cd_skills["air"] = max(60, 150 - self.player.skills["air"]*15)
                    max_r = H * 0.15 + self.player.skills["air"] * (H * 0.05)
                    self.efek_air.append({"x": self.player.x, "y": self.player.y, "r": 0, "max_r": max_r, "timer": 20})
                    play_tone(800, 200)
                    for m in targets:
                        if math.hypot(m.x - self.player.x, m.y - self.player.y) < max_r:
                            m.hp -= 20 + 10 * self.player.skills["air"]
                            ang = math.atan2(m.y - self.player.y, m.x - self.player.x)
                            m.x += math.cos(ang) * H * 0.1
                            m.y += math.sin(ang) * H * 0.1
                            if hasattr(m, 'stun'): m.stun = 30
                            if m.hp <= 0: self.kill_monster(m)

                if self.player.skills["tanah"] > 0 and self.player.cd_skills["tanah"] <= 0:
                    self.player.cd_skills["tanah"] = max(80, 180 - self.player.skills["tanah"]*15)
                    num_targets = min(self.player.skills["tanah"] * 2, len(targets))
                    hit_targets = random.sample(targets, num_targets)
                    if hit_targets: play_tone(200, 300)
                    for t in hit_targets:
                        self.efek_tanah.append({"x": t.x, "y": t.y, "timer": 30})
                        t.hp -= 50 + 20 * self.player.skills["tanah"]
                        if hasattr(t, 'stun'): t.stun = 60
                        if t.hp <= 0: self.kill_monster(t)

            if self.state == "HUNT":
                self.player.bergerak(keys, (self.world_w, self.world_h), self.obstacles)
                self.cam_x = max(0, min(self.player.x - W//2, self.world_w - W))
                self.cam_y = max(0, min(self.player.y - H//2, self.world_h - H))

                for c in self.companions:
                    c.update(self.player.x, self.player.y, self)

                self.stage_timer += 1
                max_timer = 60 * 90 
                
                # Tingkat Kesulitan
                
                if self.current_node_id == 1: map_mult = 1.2
                elif self.current_node_id == 2: map_mult = 1.3
                elif self.current_node_id == 3: map_mult = 1.5
                else: map_mult = 1.0
                
                level_mult = 1.0 + (self.player.level * 0.1) 
                
                if self.stage_timer < max_timer:
                    max_monsters = int(60 + (self.player.level * 5)) 
                    
                    spawn_rate = max(5, 60 - int((self.stage_timer / max_timer) * 50) - self.player.level)
                    if self.stage_timer % spawn_rate == 0 and len(self.monsters) < max_monsters:
                        spawn_x = self.cam_x + random.choice([-100, W+100])
                        spawn_y = self.cam_y + random.choice([-100, H+100])
                        diff = (1 + (self.stage_timer / max_timer)) * level_mult * map_mult
                        self.monsters.append(Monster(spawn_x, spawn_y, stage_diff=diff))
                elif not self.side_boss_spawned:
                    self.side_boss_spawned = True
                    spawn_x = self.player.x + random.choice([-W//3, W//3])
                    spawn_y = self.player.y + random.choice([-H//3, H//3])
                    
                    sb_diff = 3 * map_mult + (self.player.level * 0.2)
                    sb = Monster(spawn_x, spawn_y, stage_diff=sb_diff)
                    sb.img = list_img_sideboss[self.current_node_id % 4] 
                    sb.rect = sb.img.get_rect(center=(sb.x, sb.y))
                    sb.max_hp = 500 * map_mult + (self.player.level * 50)
                    sb.hp = sb.max_hp; sb.speed = H * 0.002; sb.m_type = 99
                    self.monsters.append(sb); self.side_boss = sb
                    play_tone(200, 1000)

                for m in self.monsters[:]:
                    m.update()
                    if m.stun > 0: m.stun -= 1
                    else:
                        dist = math.hypot(self.player.x - m.x, self.player.y - m.y)
                        if dist < H * 0.05 and self.player.invuln <= 0:
                            dmg = 15 if m.m_type == 1 else 5
                            if getattr(m, "m_type", 0) == 99: dmg = 25 
                            self.player.take_damage(int(dmg * map_mult)); self.player.invuln = 45; play_tone(100, 100)

                        if dist < H * 0.8:
                            ang = math.atan2(self.player.y - m.y, self.player.x - m.x)
                            m.x += math.cos(ang) * m.speed; m.y += math.sin(ang) * m.speed
                            m.facing_right = self.player.x < m.x 
                            
                            if getattr(m, "m_type", 0) != 1:
                                m.cd_shoot -= 1
                                if m.cd_shoot <= 0 and dist < H * 0.5:
                                    m.cd_shoot = random.randint(100, 200)
                                    vx, vy = math.cos(ang) * (H*0.008), math.sin(ang) * (H*0.008)
                                    self.peluru_hutan.append(Peluru(m.x, m.y, img_peluru, vx, vy, False))
                        else:
                            m.x += m.vx; m.y += m.vy
                            m.facing_right = m.vx < 0
                            
                            if m.x < 0 or m.x > self.world_w: m.vx *= -1
                            if m.y < 0 or m.y > self.world_h: m.vy *= -1
                    m.update_hitbox()

                for g in self.gems[:]:
                    dist = math.hypot(self.player.x - g.x, self.player.y - g.y)
                    if dist < self.player.magnet_radius:
                        g.x += (self.player.x - g.x) * 0.1; g.y += (self.player.y - g.y) * 0.1
                    if dist < H * 0.05:
                        self.player.exp += g.amt; self.gems.remove(g); play_tone(1200, 20)
                        if self.player.exp >= self.player.max_exp: self.trigger_level_up()

                for p in self.peluru_hutan[:]:
                    p.gerak()
                    if p.is_player:
                        for m in self.monsters[:]:
                            if math.hypot(p.x - m.x, p.y - m.y) < H*0.05:
                                m.hp -= self.player.slash_dmg
                                if p in self.peluru_hutan: self.peluru_hutan.remove(p)
                                if m.hp <= 0: self.kill_monster(m)
                                break
                    else:
                        if math.hypot(p.x - self.player.x, p.y - self.player.y) < H*0.03 and self.player.invuln <= 0:
                            self.player.take_damage(int(5 * map_mult)); self.player.invuln = 45; self.peluru_hutan.remove(p); play_tone(100, 100)
                    if p.x < 0 or p.x > self.world_w or p.y < 0 or p.y > self.world_h:
                        if p in self.peluru_hutan: self.peluru_hutan.remove(p)

                if self.player.get_hp() <= 0: self.set_story("boss_lose")
                
                if self.side_boss_spawned and self.side_boss not in self.monsters:
                    if self.current_node_id not in self.cleared_nodes:
                        self.cleared_nodes.append(self.current_node_id)
                        self.companions.append(Companion(self.current_node_id))
                    self.save_game(); self.set_story("hutan_clear")

            elif self.state == "BOSS":
                self.player.bergerak(keys, (self.world_w, self.world_h), self.obstacles)
                self.cam_x = max(0, min(self.player.x - W//2, self.world_w - W))
                self.cam_y = max(0, min(self.player.y - H//2, self.world_h - H))

                for c in self.companions: c.update(self.player.x, self.player.y, self)

                dist_boss = math.hypot(self.player.x - self.boss.x, self.player.y - self.boss.y)
                ang_boss = math.atan2(self.player.y - self.boss.y, self.player.x - self.boss.x)
                
                self.boss.facing_right = self.player.x < self.boss.x
                
                self.boss_timer += 1
                cycle = self.boss_timer % 800
                
                if cycle < 200 or 600 <= cycle < 800:
                    if cycle % 40 == 0:
                        self.boss_dash_ang = ang_boss 
                        play_tone(400, 100)
                    
                    if hasattr(self, 'boss_dash_ang'):
                        if cycle % 40 < 15: 
                            self.boss.x += math.cos(self.boss_dash_ang) * (H * 0.02)
                            self.boss.y += math.sin(self.boss_dash_ang) * (H * 0.02)
                        else: 
                            self.boss.x += math.cos(ang_boss + math.pi/2) * (H * 0.003)
                            self.boss.y += math.sin(ang_boss + math.pi/2) * (H * 0.003)
                
                elif 200 <= cycle < 400:
                    if cycle == 200:
                        self.boss_laser_angles = [ang_boss, ang_boss + math.pi/2, ang_boss + math.pi, ang_boss - math.pi/2]
                        play_tone(1000, 500)
                    if cycle > 280: 
                        dx = self.player.x - self.boss.x
                        dy = self.player.y - self.boss.y
                        for a in self.boss_laser_angles:
                            dot_prod = dx * math.cos(a) + dy * math.sin(a)
                            dist_to_laser = abs(dy * math.cos(a) - dx * math.sin(a))
                            if dot_prod > 0 and dist_to_laser < 35 and self.player.invuln <= 0:
                                self.player.take_damage(40 + (self.player.level * 2)) 
                                self.player.invuln = 45; play_tone(100, 100)
                                
                elif 400 <= cycle < 600:
                    if cycle < 450: 
                        self.boss_target_ang = ang_boss 
                        if cycle % 20 == 0: play_tone(1200, 100)
                    elif 450 <= cycle < 500:
                        pass 
                    elif 500 <= cycle < 530: 
                        dx = self.player.x - self.boss.x
                        dy = self.player.y - self.boss.y
                        dot_prod = dx * math.cos(self.boss_target_ang) + dy * math.sin(self.boss_target_ang)
                        dist_to_laser = abs(dy * math.cos(self.boss_target_ang) - dx * math.sin(self.boss_target_ang))
                        
                        if dot_prod > 0 and dist_to_laser < 45 and self.player.invuln <= 0:
                            self.player.take_damage(50 + (self.player.level * 2)) 
                            self.player.invuln = 45; play_tone(100, 100)

                self.boss.x = max(sz_b, min(self.world_w - sz_b, self.boss.x))
                self.boss.y = max(sz_b, min(self.world_h - sz_b, self.boss.y))
                self.boss.update_hitbox()

                if dist_boss < H * 0.12 and self.player.invuln <= 0:
                    self.player.take_damage(20)
                    self.player.invuln = 45
                    play_tone(100, 100)

                if self.boss.hp <= 0: 
                 self.score += 10000
                 self.set_story("boss_win")
                 play_bgm("mainmenu.mp3")  
                
                if self.player.get_hp() <= 0: 
                 self.set_story("boss_lose")
                 pygame.mixer.music.stop()  

    def draw_lightning(self, start, end, cx=0, cy=0):
        points = [(start[0]-cx, start[1]-cy)]
        dist = math.hypot(end[0]-start[0], end[1]-start[1])
        segments = max(1, int(dist / 20))
        for i in range(1, segments):
            px = start[0] + (end[0]-start[0]) * (i/segments) + random.randint(-15, 15)
            py = start[1] + (end[1]-start[1]) * (i/segments) + random.randint(-15, 15)
            points.append((px-cx, py-cy))
        points.append((end[0]-cx, end[1]-cy))
        pygame.draw.lines(scr, CY, False, points, 5)
        pygame.draw.lines(scr, WH, False, points, 2)

    def draw(self):
        if self.state == "TITLE":
            if img_bg_menu:
                scr.blit(img_bg_menu, (0, 0)) 
            else:
                scr.fill(TL) 

            ov = pygame.Surface((W, H), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 70)) 
            scr.blit(ov, (0, 0))

            has_save = os.path.exists(SAVE_FILE)
            opts = ["Mulai Baru", "Lanjutkan", "Leaderboard", "Developer Mode", "Pengaturan", "Keluar"] if has_save else ["Mulai Baru", "Leaderboard", "Developer Mode", "Pengaturan", "Keluar"]
            for i, opt in enumerate(opts):
                col = WH if i == self.sel else GR
                
                txt(scr, ("> " if i == self.sel else "") + opt, F24, col, W*0.22, H*0.35 + i*(H*0.08), cx=True)

        elif self.state == "DEV_MODE":
            scr.fill(TL)
            txt(scr, "DEVELOPER MODE (TEST MAP)", F48, YL, W//2, H*0.15, cx=True)
            for i, node in enumerate(self.map_nodes):
                col = YL if self.sel == i else WH
                txt(scr, ("> " if self.sel == i else "") + node['name'], F24, col, W//2, H*0.3 + i*50, cx=True)
            col = YL if self.sel == 5 else GR
            txt(scr, ("> " if self.sel == 5 else "") + "Kembali", F24, col, W//2, H*0.3 + 5*50 + 20, cx=True)

        elif self.state == "LEADERBOARD":
            scr.fill(TL)
            txt(scr, "LEADERBOARD SKOR TERKUAT", F48, YL, W//2, H*0.15, cx=True)
            try:
                with open(LEADERBOARD_FILE, "r") as f: lb = json.load(f)
            except: lb = []
            
            if not lb: txt(scr, "Belum ada pahlawan yang tercatat.", F24, GR, W//2, H*0.4, cx=True)
            else:
                for i, r in enumerate(lb):
                    baris = f"Rank {i+1}: Skor {r['score']} | Lv.{r['level']} | {r['date']}"
                    txt(scr, baris, F24, WH, W//2, H*0.3 + i*(H*0.08), cx=True)
            txt(scr, "Ketik ESC / ENTER untuk kembali", F18, GR, W//2, H*0.85, cx=True)
                
        elif self.state == "OPTIONS":
            scr.fill(TL)
            txt(scr, "PENGATURAN", F48, WH, W//2, H*0.2, cx=True)
            fs_txt = "ON" if cfg.FULLSCREEN else "OFF"
            opts = [f"SFX Vol: < {int(round(cfg.SFX_VOL*10))} >", f"BGM Vol: < {int(round(cfg.BGM_VOL*10))} >", f"Fullscreen: < {fs_txt} >", "Kembali"]
            for i, opt in enumerate(opts):
                col = YL if i == self.sel else GR
                txt(scr, ("> " if i == self.sel else "") + opt, F24, col, W//2, H*0.4 + i*(H*0.08), cx=True)

        elif self.state == "STORY":
            scr.fill((15, 10, 20)); self.dlg.draw(scr)

        elif self.state == "MAP":
            scr.blit(img_bg_map, (0, 0))
            for (n1, n2) in self.map_links:
                x1, y1 = self.map_nodes[n1]['x'], self.map_nodes[n1]['y']
                x2, y2 = self.map_nodes[n2]['x'], self.map_nodes[n2]['y']
                draw_dashed_line(scr, (100, 90, 80), (x1, y1), (x2, y2))
                
            for node in self.map_nodes:
                nx, ny = node['x'], node['y'];
                color = GR
                if node['id'] in self.cleared_nodes:
                    color = GN
                elif self.is_node_available(node['id']):
                    color = YL
                    pulse = int(H * 0.045 + math.sin(pygame.time.get_ticks() * 0.005) * 5)
                    pygame.draw.circle(scr, WH, (int(nx), int(ny)), pulse)

                icon = img_node[node['id']]
                scr.blit(icon, icon.get_rect(center=(int(nx), int(ny))))
                txt(scr, node['name'], F14, BK, nx, ny + H * 0.06, cx=True)

            if self.current_node_id != -1:
                cx, cy = self.map_nodes[self.current_node_id]['x'], self.map_nodes[self.current_node_id]['y']
                scr.blit(img_player, img_player.get_rect(center=(cx, cy)))
            else:
                scr.blit(img_player, img_player.get_rect(center=(W*0.5, H*0.95)))
                
            txt(scr, f"Lv: {self.player.level} | Skor: {int(self.score)} | ESC: Pause", F18, BK, 20, 20)

        elif self.state in ["HUNT", "BOSS"] or (self.state in ["PAUSE", "LEVEL_UP"] and self.prev_state in ["HUNT", "BOSS"]):
            if hasattr(self, 'bg_surface') and self.bg_surface is not None:
                scr.blit(self.bg_surface, (-self.cam_x, -self.cam_y))
            else:
                scr.fill(self.bg_color)

            if self.state == "BOSS" or self.prev_state == "BOSS":
                if hasattr(self, 'boss_timer'):
                    cycle = self.boss_timer % 800
                    cx, cy = self.cam_x, self.cam_y
                    
                    if 200 <= cycle < 400 and hasattr(self, 'boss_laser_angles'):
                        for a in self.boss_laser_angles:
                            end_x = self.boss.x + math.cos(a) * self.world_w
                            end_y = self.boss.y + math.sin(a) * self.world_w
                            if cycle < 280: 
                                pygame.draw.line(scr, (255, 100, 100), (self.boss.x - cx, self.boss.y - cy), (end_x - cx, end_y - cy), 4)
                            else: 
                                pygame.draw.line(scr, RD, (self.boss.x - cx, self.boss.y - cy), (end_x - cx, end_y - cy), 60)
                                pygame.draw.line(scr, WH, (self.boss.x - cx, self.boss.y - cy), (end_x - cx, end_y - cy), 20)
                    
                    if 400 <= cycle < 600 and hasattr(self, 'boss_target_ang'):
                        end_x = self.boss.x + math.cos(self.boss_target_ang) * self.world_w
                        end_y = self.boss.y + math.sin(self.boss_target_ang) * self.world_w
                        if cycle < 450: 
                            pygame.draw.line(scr, (255, 150, 0), (self.boss.x - cx, self.boss.y - cy), (end_x - cx, end_y - cy), 2)
                        elif 450 <= cycle < 500: 
                            pygame.draw.line(scr, (255, 50, 50), (self.boss.x - cx, self.boss.y - cy), (end_x - cx, end_y - cy), 8)
                        elif 500 <= cycle < 530: 
                            pygame.draw.line(scr, OR, (self.boss.x - cx, self.boss.y - cy), (end_x - cx, end_y - cy), 80)
                            pygame.draw.line(scr, YL, (self.boss.x - cx, self.boss.y - cy), (end_x - cx, end_y - cy), 30)

            for e in self.efek_tanah:
                pygame.draw.polygon(scr, (139, 69, 19), [
                    (e["x"] - self.cam_x, e["y"] - self.cam_y - H*0.05),
                    (e["x"] - self.cam_x - H*0.03, e["y"] - self.cam_y + H*0.02),
                    (e["x"] - self.cam_x + H*0.03, e["y"] - self.cam_y + H*0.02)
                ])

            vis_objs = []
            if self.prev_state == "HUNT" or self.state == "HUNT":
                vis_objs = [o for o in self.decos + self.obstacles + self.monsters + self.companions + [self.player]
                            if self.cam_x - H < o.x < self.cam_x + W + H and self.cam_y - H < o.y < self.cam_y + H + H]
                vis_objs.sort(key=lambda o: o.y)
                
                for g in self.gems: g.draw(scr, self.cam_x, self.cam_y)
                for obj in vis_objs: obj.draw(scr, self.cam_x, self.cam_y)
                for p in self.peluru_hutan: p.draw(scr, self.cam_x, self.cam_y)
                
            elif self.prev_state == "BOSS" or self.state == "BOSS":
                vis_objs = [o for o in self.decos + self.obstacles + self.companions + [self.boss, self.player]
                            if self.cam_x - H < o.x < self.cam_x + W + H and self.cam_y - H < o.y < self.cam_y + H + H]
                vis_objs.sort(key=lambda o: o.y)
                
                for obj in vis_objs:
                    if obj == self.boss:
                        pygame.draw.rect(scr, RD, (self.boss.x - self.cam_x - H*0.4, self.boss.y - self.cam_y - H*0.15, H*0.8, H*0.02))
                        pygame.draw.rect(scr, GN, (self.boss.x - self.cam_x - H*0.4, self.boss.y - self.cam_y - H*0.15, H*0.8 * (max(0, self.boss.hp)/self.boss.max_hp), H*0.02))
                    obj.draw(scr, self.cam_x, self.cam_y)
            
            for e in self.efek_air: pygame.draw.circle(scr, CY, (int(e["x"] - self.cam_x), int(e["y"] - self.cam_y)), int(e["r"]), 3)
            
            for b in getattr(self, "bom_waktu", []):
                if (b["timer"] // 10) % 2 == 0:
                    pygame.draw.circle(scr, RD, (int(b["x"] - self.cam_x), int(b["y"] - self.cam_y)), int(H*0.12), 2)
                    pygame.draw.circle(scr, WH, (int(b["x"] - self.cam_x), int(b["y"] - self.cam_y)), 10)

            for e in self.ledakan_api:
                pygame.draw.circle(scr, OR, (int(e["x"] - self.cam_x), int(e["y"] - self.cam_y)), int(e["r"]))
                pygame.draw.circle(scr, YL, (int(e["x"] - self.cam_x), int(e["y"] - self.cam_y)), int(e["r"]*0.7))
            for p in self.peluru_api:
                pygame.draw.circle(scr, RD, (int(p["x"] - self.cam_x), int(p["y"] - self.cam_y)), int(H*0.015))
                pygame.draw.circle(scr, YL, (int(p["x"] - self.cam_x), int(p["y"] - self.cam_y)), int(H*0.008))

            self.player.draw_slash(scr, self.cam_x, self.cam_y)
            
            if self.active_lightnings:
                for l in self.active_lightnings:
                    if hasattr(l["target"], 'x') and hasattr(l["source"], 'x'):
                        self.draw_lightning((l["source"].x, l["source"].y), (l["target"].x, l["target"].y), self.cam_x, self.cam_y)
            
            # --- HUD ---
            if self.state == "HUNT" or (self.state in ["PAUSE", "LEVEL_UP"] and self.prev_state == "HUNT"):
                if not self.side_boss_spawned:
                    sisa_waktu = max(0, 90 - (self.stage_timer // 60))
                    txt(scr, f"WAKTU: {sisa_waktu}s", F24, YL, W//2, 35, cx=True)
                else:
                    txt(scr, f"", F48, RD, W//2, 50, cx=True)
            elif self.state == "BOSS" or (self.state in ["PAUSE", "LEVEL_UP"] and self.prev_state == "BOSS"):
                txt(scr, f"", F48, RD, W//2, 50, cx=True)

            pygame.draw.rect(scr, GR, (0, 0, W, 10))
            pygame.draw.rect(scr, EXP_COL, (0, 0, W * (self.player.exp / self.player.max_exp), 10))
            txt(scr, f"Lv {self.player.level}", F18, WH, 20, 25)
            
            hp_w = H*0.3; hp_h = H*0.025
            hp_pct = max(0, self.player.get_hp()) / self.player.get_max_hp()
            pygame.draw.rect(scr, RD, (20, 45, hp_w, hp_h))
            pygame.draw.rect(scr, GN, (20, 45, hp_w * hp_pct, hp_h))
            pygame.draw.rect(scr, WH, (20, 45, hp_w, hp_h), 2)
            txt(scr, f"{int(self.player.get_hp())} / {self.player.get_max_hp()}", F14, WH, 20 + hp_w/2, 45 + hp_h/2, cx=True, cy=True)
            
            sk_text = []
            for k, v in self.player.skills.items():
                if v > 0: sk_text.append(f"{k.capitalize()} Lv{v}")
            teks_skill = "Elemen: " + (", ".join(sk_text) if sk_text else "Belum Ada")
            txt(scr, f"{teks_skill} | Skor: {int(self.score)}", F14, WH, 20, 85)

        if self.state == "PAUSE":
            ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((0, 0, 0, 180)); scr.blit(ov, (0, 0))
            txt(scr, "GAME PAUSED", F48, WH, W//2, H*0.3, cx=True)
            for i, opt in enumerate(["Lanjutkan", "Pengaturan", "Kembali ke Menu Utama"]):
                col = YL if i == self.sel else GR
                txt(scr, ("> " if i == self.sel else "") + opt, F24, col, W//2, H*0.5 + i*(H*0.1), cx=True)

        if self.state == "LEVEL_UP":
            ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((0, 0, 0, 180)); scr.blit(ov, (0, 0))
            txt(scr, "LEVEL UP!", F48, YL, W//2, H*0.2, cx=True)
            txt(scr, "Pilih satu upgrade (A/D untuk geser, Mouse Klik / Enter untuk pilih)", F18, WH, W//2, H*0.3, cx=True)
            
            box_w, box_h = W*0.25, H*0.3
            for i, upg in enumerate(self.upgrade_choices):
                bx = W*0.1 + i * (box_w + W*0.05); by = H*0.4
                color = YL if i == self.sel else GR
                pygame.draw.rect(scr, (30, 30, 50), (bx, by, box_w, box_h))
                pygame.draw.rect(scr, color, (bx, by, box_w, box_h), 4)
                txt(scr, upg["name"], F24, color, bx + box_w//2, by + 30, cx=True)
                
                words = upg["desc"].split(); line = ""; y_off = 80
                for w in words:
                    if F14.size(line + " " + w)[0] < box_w - 20: line += (" " if line else "") + w
                    else: txt(scr, line, F14, WH, bx + box_w//2, by + y_off, cx=True); line = w; y_off += 25
                txt(scr, line, F14, WH, bx + box_w//2, by + y_off, cx=True)