import pygame, sys, os, math, random, json

pygame.init()
try:
    pygame.mixer.init()
    _AUDIO = True
except:
    _AUDIO = False

# ==========================================
# SETUP LAYAR FULLSCREEN
# ==========================================
infoObj = pygame.display.Info()
W, H = infoObj.current_w, infoObj.current_h
scr = pygame.display.set_mode((W, H), pygame.FULLSCREEN)
pygame.display.set_caption("Demon King Quest")
clk = pygame.time.Clock()
FPS = 60
SAVE_FILE = "dkq_save.json"

# ==========================================
# WARNA & FONT
# ==========================================
BK = (0, 0, 0); WH = (255, 255, 255); GR = (80, 80, 80); LGR = (160, 160, 160)
RD = (210, 40, 40); GN = (50, 190, 80); BL = (60, 130, 230); YL = (240, 200, 40)
OR = (230, 120, 30); TL = (20, 10, 30); CY = (50, 210, 210); EXP_COL = (100, 200, 255)
PU = (180, 50, 200); MAP_BG = (210, 200, 180)

def mkfont(sz):
    try: return pygame.font.SysFont("Courier New", sz, bold=True)
    except: return pygame.font.Font(None, sz)

F14 = mkfont(int(H*0.025)); F18 = mkfont(int(H*0.035))
F24 = mkfont(int(H*0.045)); F48 = mkfont(int(H*0.08))

# ==========================================
# PENGATURAN & AUDIO
# ==========================================
class Config:
    SFX_VOL = 0.5; BGM_VOL = 0.5
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

def play_bgm():
    if _AUDIO:
        try:
            pygame.mixer.music.load("lagu.mp3")
            pygame.mixer.music.set_volume(cfg.BGM_VOL); pygame.mixer.music.play(-1)
        except: pass

def update_bgm_vol():
    if _AUDIO: pygame.mixer.music.set_volume(cfg.BGM_VOL)

# ==========================================
# LOAD GAMBAR
# ==========================================
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

def load_img(name, size, fallback_col):
    path = os.path.join(BASE_PATH, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, fallback_col, (0, 0, size[0], size[1]), border_radius=8)
        return surf

def tint_image(image, color):
    tinted = image.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

sz_p = int(H*0.06); sz_m = int(H*0.05); sz_b = int(H*0.2); sz_sb = int(H*0.15)
img_player = load_img("karaktermc.png", (120,120), BL)
img_monster = load_img("monster.png", (sz_m, sz_m), WH)
img_boss = load_img("boss.png", (sz_b, sz_b), RD)
img_sideboss = load_img("sideboss.png", (sz_sb, sz_sb), PU)
img_ally = load_img("ally.png", (int(H*0.04), int(H*0.04)), CY)

# Membuat gambar peluru bentuk kapsul lonjong
sz_peluru = (int(H*0.04), int(H*0.015))
try:
    img_peluru = pygame.image.load(os.path.join(BASE_PATH, "peluru.png")).convert_alpha()
    img_peluru = pygame.transform.scale(img_peluru, sz_peluru)
except:
    img_peluru = pygame.Surface(sz_peluru, pygame.SRCALPHA)
    pygame.draw.ellipse(img_peluru, OR, (0, 0, sz_peluru[0], sz_peluru[1]))
    pygame.draw.ellipse(img_peluru, WH, (0, 0, sz_peluru[0], sz_peluru[1]), 1)

img_m_normal = tint_image(img_monster, YL)
img_m_tank = tint_image(img_monster, BL)
img_m_fast = tint_image(img_monster, RD)

# ASET MAP BIOMA
sz_tree = (int(H*0.12), int(H*0.18)); sz_flower = (int(H*0.04), int(H*0.04))
img_pohon = load_img("pohon.png", (120,120), (20, 100, 20))
img_bunga = load_img("bunga.png", sz_flower, (255, 100, 200))
img_kaktus = load_img("kaktus.png", sz_tree, (46, 139, 87))
img_batu = load_img("batu.png", (int(H*0.08), int(H*0.08)), (100, 100, 100))
img_pohonmati = load_img("pohonmati.png", sz_tree, (60, 50, 40))
img_jamur = load_img("jamur.png", sz_flower, (0, 255, 255))
img_pohonsalju = load_img("pohonsalju.png", sz_tree, (200, 220, 230))
img_lava = load_img("lava.png", (int(H*0.15), int(H*0.12)), (200, 60, 0))
img_tengkorak = load_img("tengkorak.png", sz_flower, (180, 180, 180))

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

# ==========================================
# KELAS ENTITAS & SISTEM COMBAT
# ==========================================
class Entitas:
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

class ObjekMap(Entitas):
    def __init__(self, x, y, img, is_solid=False):
        super().__init__(x, y, img)
        self.is_solid = is_solid
    def get_hitbox(self):
        w = self.rect.width * 0.4; h = self.rect.height * 0.3
        return pygame.Rect(self.x - w/2, self.y + self.rect.height*0.2 - h/2, w, h)

class Player(Entitas):
    def __init__(self, x, y):
        super().__init__(x, y, img_player)
        self.max_hp = 100; self.hp = 100
        self.hp_regen = 0.04 # Regen HP (sekitar 2.4 HP per detik)
        self.base_speed = H * 0.007; self.speed_mult = 1.0
        self.slash_dmg = 10; self.slash_cd_max = 25
        self.lightning_cd_max = 120; self.slash_radius = H * 0.15
        self.magnet_radius = H * 0.15
        self.level = 1; self.exp = 0; self.max_exp = 50
        
        self.invuln = 0
        self.cd_slash = 0; self.cd_shoot = 0; self.cd_lightning = 0
        self.anim_slash = 0; self.slash_angle = 0
        self.last_tap = {pygame.K_w: 0, pygame.K_a: 0, pygame.K_s: 0, pygame.K_d: 0}
        self.dash_timer = 0; self.dash_dir = (0, 0)

    def handle_dash(self, key):
        now = pygame.time.get_ticks()
        if key in self.last_tap:
            if now - self.last_tap[key] < 250:
                self.dash_timer = 12; play_tone(600, 50)
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

    def update(self):
        if self.cd_slash > 0: self.cd_slash -= 1
        if self.cd_shoot > 0: self.cd_shoot -= 1
        if self.cd_lightning > 0: self.cd_lightning -= 1
        if self.anim_slash > 0: self.anim_slash -= 1
        if self.invuln > 0: self.invuln -= 1
        
        # SISTEM REGEN HP
        if 0 < self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + self.hp_regen)

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
        if self.m_type == 0:
            super().__init__(x, y, img_m_normal)
            self.max_hp = 20 * stage_diff; self.speed = H * 0.003
        elif self.m_type == 1:
            super().__init__(x, y, img_m_tank)
            self.max_hp = 50 * stage_diff; self.speed = H * 0.0015
        else:
            super().__init__(x, y, img_m_fast)
            self.max_hp = 10 * stage_diff; self.speed = H * 0.005
            
        self.hp = self.max_hp; self.stun = 0
        self.cd_shoot = random.randint(60, 180)
        self.vx = random.choice([-2, 2, -3, 3]); self.vy = random.choice([-2, 2, -3, 3])

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
        # Rotasi Peluru!
        angle = math.degrees(math.atan2(-vy, vx))
        self.rotated_img = pygame.transform.rotate(self.img, angle)
        
    def gerak(self):
        self.x += self.vx; self.y += self.vy
        self.update_hitbox()
        
    def draw(self, surf, cx=0, cy=0):
        draw_rect = self.rotated_img.get_rect(center=(self.x - cx, self.y - cy))
        surf.blit(self.rotated_img, draw_rect)

class ExpGem:
    def __init__(self, x, y, amt):
        self.x, self.y = x, y; self.amt = amt
    def draw(self, surf, cx, cy):
        pygame.draw.circle(surf, EXP_COL, (int(self.x - cx), int(self.y - cy)), 6)
        pygame.draw.circle(surf, WH, (int(self.x - cx), int(self.y - cy)), 3)

class Companion(Entitas):
    def __init__(self, type_id):
        super().__init__(0, 0, tint_image(img_ally, [GN, PU, BL, OR][type_id % 4]))
        self.type_id = type_id; self.cd_atk = 0; self.angle_offset = type_id * (math.pi / 2)

    def update(self, px, py, time_tick, musuh_list, peluru_list):
        self.angle_offset += 0.05
        target_x = px + math.cos(self.angle_offset) * (H * 0.1)
        target_y = py + math.sin(self.angle_offset) * (H * 0.1)
        self.x += (target_x - self.x) * 0.1; self.y += (target_y - self.y) * 0.1
        self.update_hitbox()
        
        if self.cd_atk > 0: self.cd_atk -= 1
        if self.cd_atk <= 0 and musuh_list:
            terdekat = min(musuh_list, key=lambda m: math.hypot(m.x - self.x, m.y - self.y))
            if math.hypot(terdekat.x - self.x, terdekat.y - self.y) < H * 0.6:
                ang = math.atan2(terdekat.y - self.y, terdekat.x - self.x)
                vx, vy = math.cos(ang) * (H*0.015), math.sin(ang) * (H*0.015)
                peluru_list.append(Peluru(self.x, self.y, img_peluru, vx, vy, True))
                self.cd_atk = 60; play_tone(1200, 30)

# ==========================================
# UI & DIALOG
# ==========================================
def txt(surf, s, font, col, x, y, cx=False, cy=False):
    ren = font.render(s, False, col); sh = font.render(s, False, BK)
    bx = x - ren.get_width()//2 if cx else x; by = y - ren.get_height()//2 if cy else y
    surf.blit(sh, (bx+2, by+2)); surf.blit(ren, (bx, by))

class Dialog:
    def __init__(self):
        self.lines = []; self.spk = ""; self.ci = 0; self.done = False
    def set(self, spk, text):
        words = text.split(); lines = []; line = ""
        for w in words:
            if F18.size(line + " " + w)[0] < W*0.7: line += (" " if line else "") + w
            else: lines.append(line); line = w
        if line: lines.append(line)
        self.lines = lines; self.spk = spk; self.ci = 0; self.done = False
    def update(self):
        if not self.done:
            self.ci += 0.5
            if self.ci >= sum(len(l) for l in self.lines): self.done = True
    def draw(self, surf):
        bx, by, bw, bh = W*0.1, H*0.7, W*0.8, H*0.25
        pygame.draw.rect(surf, (20, 20, 40), (bx, by, bw, bh)); pygame.draw.rect(surf, WH, (bx, by, bw, bh), 3)
        if self.spk:
            pygame.draw.rect(surf, (40, 40, 80), (bx+20, by-30, F18.size(self.spk)[0]+20, 35)); txt(surf, self.spk, F18, YL, bx+30, by-25)
        drawn = 0
        for i, line in enumerate(self.lines):
            rem = max(0, int(self.ci) - drawn)
            txt(surf, line[:rem], F18, WH, bx+30, by+20 + i*(H*0.04))
            drawn += len(line)
        if self.done: txt(surf, "▼ Enter/Klik", F14, YL, bx+bw-140, by+bh-30)

STORY = {
    "start": ("KAEL", "Ini petanya. Setiap wilayah memiliki medan yang berbeda. Tahan serangan monster hingga Side Boss muncul dan kalahkan dia!"),
    "hutan_masuk": ("KAEL", "Ini Hutan Pinus. Pohon-pohonnya bisa melindungiku dari peluru musuh."),
    "gurun_masuk": ("KAEL", "Gurun Wild West. Hati-hati jangan sampai mentok di kaktus raksasa itu!"),
    "rawa_masuk": ("KAEL", "Rawa Gelap... Pohon mati ini sangat keras, aku bisa menggunakannya sebagai tembok."),
    "salju_masuk": ("KAEL", "Lembah Salju. Bersembunyilah di balik pohon pinus beku!"),
    "hutan_clear": ("KAEL", "Side Boss mati! Temanku bebas. Waktunya melangkah ke area selanjutnya."),
    "boss_masuk": ("KAEL", "Ini akhirnya... Kastil Raja Iblis! Aku harus menghindari serangan pelurunya, cari posisi yang pas, lalu tembak balik!"),
    "boss_win": ("NARATOR", "MALACHAR BERHASIL DIKALAHKAN! Kedamaian kembali ke Valoria."),
    "boss_lose": ("NARATOR", "Arion telah gugur... Kiamat telah tiba!"),
}

UPGRADES = [
    {"name": "Max HP +20", "desc": "Menambah batas HP dan memulihkan 20 HP.", "id": "hp"},
    {"name": "Damage Tebasan +10", "desc": "Tebasan pedang lebih menyakitkan.", "id": "dmg"},
    {"name": "Kecepatan +10%", "desc": "Lari dari musuh lebih kencang.", "id": "spd"},
    {"name": "Attack Speed+", "desc": "Cooldown tebasan lebih cepat.", "id": "cd"},
    {"name": "Radius Tebasan+", "desc": "Jangkauan tebasan pedang membesar.", "id": "rad"},
    {"name": "CD Listrik Cepat", "desc": "Skill Listrik (1) bisa dipakai lebih sering.", "id": "lcd"},
    {"name": "Magnet EXP+", "desc": "Mengambil EXP dari jarak lebih jauh.", "id": "mag"}
]

# ==========================================
# MAIN GAME
# ==========================================
class Game:
    def __init__(self):
        self.state = "TITLE"; self.prev_state = "TITLE"; self.sel = 0
        self.player = Player(W//2, H//2); self.dlg = Dialog()
        self.ammo = 0; self.cam_x = 0; self.cam_y = 0
        self.world_w = W * 3; self.world_h = H * 3
        self.active_story_key = ""
        
        self.lightning_timer = 0; self.lightning_target = None
        self.stage_timer = 0; self.side_boss_spawned = False; self.side_boss = None
        self.gems = []; self.companions = []; self.upgrade_choices = []
        
        self.decos = []; self.obstacles = []; self.paths = []
        self.bg_color = GN; self.path_color = (100, 80, 40)
        
        self.map_nodes = [
            {"id": 0, "name": "Hutan Pinus", "x": W*0.5, "y": H*0.8, "type": "HUNT", "story": "hutan_masuk"},
            {"id": 1, "name": "Gurun Wild West", "x": W*0.35, "y": H*0.6, "type": "HUNT", "story": "gurun_masuk"},
            {"id": 2, "name": "Rawa Gelap", "x": W*0.65, "y": H*0.6, "type": "HUNT", "story": "rawa_masuk"},
            {"id": 3, "name": "Lembah Salju", "x": W*0.5, "y": H*0.4, "type": "HUNT", "story": "salju_masuk"},
            {"id": 4, "name": "Kastil Raja Iblis", "x": W*0.5, "y": H*0.15, "type": "BOSS", "story": "boss_masuk"}
        ]
        self.map_links = [(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)]
        self.cleared_nodes = []; self.current_node_id = -1; self.target_node_id = -1
        play_bgm()

    def generate_map_objects(self, node_id):
        self.decos = []; self.obstacles = []; self.paths = []
        ww, wh = self.world_w, self.world_h
        
        if node_id == 0:
            self.bg_color = (34, 139, 34); self.path_color = (100, 80, 40)
            for _ in range(150): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_bunga, False))
            for _ in range(120): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_pohon, True))
        elif node_id == 1:
            self.bg_color = (210, 180, 140); self.path_color = (190, 160, 120)
            for _ in range(100): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_batu, False))
            for _ in range(80): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_kaktus, True))
        elif node_id == 2:
            self.bg_color = (25, 20, 40); self.path_color = (35, 25, 50)
            for _ in range(150): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_jamur, False))
            for _ in range(100): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_pohonmati, True))
        elif node_id == 3:
            self.bg_color = (230, 240, 255); self.path_color = (200, 215, 230)
            for _ in range(100): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_pohonsalju, True))
        elif node_id == 4:
            self.bg_color = (60, 10, 10); self.path_color = (80, 20, 20)
            for _ in range(80): self.decos.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_tengkorak, False))
            for _ in range(50): self.obstacles.append(ObjekMap(random.randint(0,ww), random.randint(0,wh), img_lava, True))
            
        for _ in range(8):
            px, py = random.randint(0, ww), random.randint(0, wh)
            for _ in range(40):
                self.paths.append((px, py, random.randint(int(H*0.1), int(H*0.25))))
                px += random.choice([-1, 0, 1]) * H*0.15; py += random.choice([-1, 0, 1]) * H*0.15
            
        self.obstacles = [o for o in self.obstacles if math.hypot(o.x - ww//2, o.y - wh//2) > H*0.2]

    def set_story(self, key):
        self.active_story_key = key
        self.dlg.set(*STORY[key])
        self.state = "STORY"

    def save_game(self):
        data = {
            "cleared_nodes": self.cleared_nodes, "current_node_id": self.current_node_id,
            "ammo": self.ammo, "level": self.player.level, "max_hp": self.player.max_hp,
            "speed_mult": self.player.speed_mult, "slash_dmg": self.player.slash_dmg,
            "slash_cd_max": self.player.slash_cd_max, "lightning_cd_max": self.player.lightning_cd_max,
            "slash_radius": self.player.slash_radius, "magnet_radius": self.player.magnet_radius
        }
        with open(SAVE_FILE, "w") as f: json.dump(data, f)

    def load_game(self):
        try:
            with open(SAVE_FILE, "r") as f:
                d = json.load(f)
                self.cleared_nodes = d.get("cleared_nodes", [])
                self.current_node_id = d.get("current_node_id", -1)
                self.ammo = d.get("ammo", 0); self.player.level = d.get("level", 1)
                self.player.max_hp = d.get("max_hp", 100); self.player.hp = self.player.max_hp
                self.player.speed_mult = d.get("speed_mult", 1.0); self.player.slash_dmg = d.get("slash_dmg", 10)
                self.player.slash_cd_max = d.get("slash_cd_max", 25); self.player.lightning_cd_max = d.get("lightning_cd_max", 120)
                self.player.slash_radius = d.get("slash_radius", H*0.15); self.player.magnet_radius = d.get("magnet_radius", H*0.15)
                self.companions = [Companion(n) for n in self.cleared_nodes]
                self.state = "MAP"
                return True
        except: return False

    def is_node_available(self, node_id):
        if self.current_node_id == -1: return node_id == 0
        if node_id in self.cleared_nodes: return False
        for (n1, n2) in self.map_links:
            if n1 == self.current_node_id and n2 == node_id: return True
        return False

    def trigger_level_up(self):
        self.player.level += 1; self.player.exp -= self.player.max_exp
        self.player.max_exp = int(self.player.max_exp * 1.5)
        self.upgrade_choices = random.sample(UPGRADES, 3)
        self.prev_state = self.state; self.state = "LEVEL_UP"; self.sel = 0; play_tone(1000, 200)

    def apply_upgrade(self, upg_id):
        if upg_id == "hp": self.player.max_hp += 20; self.player.hp += 20
        elif upg_id == "dmg": self.player.slash_dmg += 10
        elif upg_id == "spd": self.player.speed_mult += 0.1
        elif upg_id == "cd": self.player.slash_cd_max = max(5, self.player.slash_cd_max - 4)
        elif upg_id == "rad": self.player.slash_radius += H * 0.03
        elif upg_id == "lcd": self.player.lightning_cd_max = max(30, self.player.lightning_cd_max - 20)
        elif upg_id == "mag": self.player.magnet_radius += H * 0.05
        self.state = self.prev_state

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
        if ev.type == pygame.MOUSEMOTION:
            mx, my = ev.pos
            if self.state == "TITLE":
                has_save = os.path.exists(SAVE_FILE)
                opts = ["Mulai Baru", "Lanjutkan Game", "Pengaturan", "Keluar"] if has_save else ["Mulai Baru", "Pengaturan", "Keluar"]
                for i in range(len(opts)):
                    rect = pygame.Rect(W//2 - W*0.2, H*0.45 + i*(H*0.08) - H*0.03, W*0.4, H*0.06)
                    if rect.collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i
            elif self.state == "OPTIONS":
                for i in range(3):
                    rect = pygame.Rect(W//2 - W*0.2, H*0.4 + i*(H*0.08) - H*0.03, W*0.4, H*0.06)
                    if rect.collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i
            elif self.state == "PAUSE":
                for i in range(2):
                    rect = pygame.Rect(W//2 - W*0.2, H*0.5 + i*(H*0.1) - H*0.03, W*0.4, H*0.06)
                    if rect.collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i
            elif self.state == "LEVEL_UP":
                for i in range(3):
                    box_w, box_h = W*0.25, H*0.3
                    bx = W*0.1 + i * (box_w + W*0.05); by = H*0.4
                    rect = pygame.Rect(bx, by, box_w, box_h)
                    if rect.collidepoint(mx, my):
                        if self.sel != i: play_tone(400, 50)
                        self.sel = i

        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            mx, my = pygame.mouse.get_pos()
            
            if self.state == "TITLE":
                has_save = os.path.exists(SAVE_FILE)
                opts = ["Mulai Baru", "Lanjutkan Game", "Pengaturan", "Keluar"] if has_save else ["Mulai Baru", "Pengaturan", "Keluar"]
                for i in range(len(opts)):
                    if pygame.Rect(W//2 - W*0.2, H*0.45 + i*(H*0.08) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        self.sel = i
                        play_tone(600, 100)
                        if self.sel == 0: 
                            self.ammo = 0; self.player = Player(W//2, H//2)
                            self.cleared_nodes = []; self.current_node_id = -1; self.companions = []
                            self.set_story("start")
                        elif self.sel == 1 and has_save: self.load_game()
                        elif (self.sel == 1 and not has_save) or (self.sel == 2 and has_save): self.sel = 0; self.state = "OPTIONS"
                        else: pygame.quit(); sys.exit()
                        break
            
            elif self.state == "OPTIONS":
                for i in range(3):
                    if pygame.Rect(W//2 - W*0.2, H*0.4 + i*(H*0.08) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        self.sel = i
                        play_tone(600, 100)
                        if self.sel == 2: self.sel = 0; self.state = "TITLE"
                        elif self.sel == 0: cfg.SFX_VOL = min(1.0, cfg.SFX_VOL + 0.1) if cfg.SFX_VOL < 1.0 else 0; play_tone(400, 50)
                        elif self.sel == 1: cfg.BGM_VOL = min(1.0, cfg.BGM_VOL + 0.1) if cfg.BGM_VOL < 1.0 else 0; update_bgm_vol()
                        break
            
            elif self.state == "PAUSE":
                for i in range(2):
                    if pygame.Rect(W//2 - W*0.2, H*0.5 + i*(H*0.1) - H*0.03, W*0.4, H*0.06).collidepoint(mx, my):
                        self.sel = i
                        play_tone(600, 100)
                        if self.sel == 0: self.state = self.prev_state
                        else: self.state = "TITLE"; self.sel = 0
                        break

            elif self.state == "STORY":
                if self.dlg.done: self.finish_dialog()
                else: self.dlg.ci = 999
            
            elif self.state == "LEVEL_UP":
                box_w, box_h = W*0.25, H*0.3; by = H*0.4
                for i, upg in enumerate(self.upgrade_choices):
                    bx = W*0.1 + i * (box_w + W*0.05)
                    if pygame.Rect(bx, by, box_w, box_h).collidepoint(mx, my):
                        play_tone(800, 100)
                        self.apply_upgrade(upg["id"])
                        break

            elif self.state == "MAP":
                for node in self.map_nodes:
                    if self.is_node_available(node['id']):
                        if math.hypot(node['x'] - mx, node['y'] - my) < H*0.05:
                            self.target_node_id = node['id']
                            self.set_story(node['story']); play_tone(600, 100)
                            break
                            
            elif self.state == "HUNT":
                if self.player.cd_slash <= 0:
                    wmx, wmy = mx + self.cam_x, my + self.cam_y
                    self.player.slash_angle = math.atan2(wmy - self.player.y, wmx - self.player.x)
                    self.player.cd_slash = self.player.slash_cd_max; self.player.anim_slash = 8
                    play_tone(800, 50)
                    
                    slash_r = self.player.slash_radius
                    for m in self.monsters[:]:
                        if math.hypot(m.x - self.player.x, m.y - self.player.y) < slash_r:
                            m_ang = math.atan2(m.y - self.player.y, m.x - self.player.x)
                            if abs(math.remainder(m_ang - self.player.slash_angle, math.tau)) < math.radians(60):
                                m.hp -= self.player.slash_dmg; m.stun = 20; play_tone(150, 50)
                                if m.hp <= 0:
                                    if getattr(m, "m_type", 0) == 99: self.side_boss = None
                                    else: self.gems.append(ExpGem(m.x, m.y, 10))
                                    self.monsters.remove(m); self.ammo += (m.m_type + 1)
                                    play_tone(900, 50)
            
            elif self.state == "BOSS":
                wmx, wmy = mx + self.cam_x, my + self.cam_y
                if self.player.cd_shoot <= 0 and self.ammo > 0:
                    ang = math.atan2(wmy - self.player.y, wmx - self.player.x)
                    vx, vy = math.cos(ang) * (H*0.015), math.sin(ang) * (H*0.015)
                    self.peluru.append(Peluru(self.player.x, self.player.y, img_monster, vx, vy, True))
                    self.ammo -= 1; self.player.cd_shoot = 12; play_tone(700, 50)

        elif ev.type == pygame.KEYDOWN:
            k = ev.key
            if self.state in ["HUNT", "BOSS"]: self.player.handle_dash(k)

            if k == pygame.K_1 and self.player.cd_lightning <= 0:
                mx, my = pygame.mouse.get_pos()
                if self.state == "HUNT":
                    wmx, wmy = mx + self.cam_x, my + self.cam_y
                    target = next((m for m in self.monsters if math.hypot(m.x - wmx, m.y - wmy) < H*0.15), None)
                    if target:
                        target.hp -= self.player.slash_dmg * 3; target.stun = 120
                        self.player.cd_lightning = self.player.lightning_cd_max
                        self.lightning_target = target; self.lightning_timer = 15; play_tone(1500, 150)
                        if target.hp <= 0:
                            if getattr(target, "m_type", 0) == 99: self.side_boss = None
                            else: self.gems.append(ExpGem(target.x, target.y, 10))
                            self.monsters.remove(target); self.ammo += (target.m_type + 1)
                elif self.state == "BOSS":
                    wmx, wmy = mx + self.cam_x, my + self.cam_y
                    if math.hypot(self.boss.x - wmx, self.boss.y - wmy) < H*0.3:
                        self.boss.hp -= self.player.slash_dmg * 2
                        self.player.cd_lightning = self.player.lightning_cd_max
                        self.lightning_target = self.boss; self.lightning_timer = 15; play_tone(1500, 150)

            if self.state == "TITLE":
                has_save = os.path.exists(SAVE_FILE)
                max_sel = 3 if has_save else 2
                if k in (pygame.K_w, pygame.K_UP): self.sel = (self.sel - 1) % (max_sel + 1); play_tone(400, 50)
                if k in (pygame.K_s, pygame.K_DOWN): self.sel = (self.sel + 1) % (max_sel + 1); play_tone(400, 50)
                if k == pygame.K_RETURN:
                    play_tone(600, 100)
                    if self.sel == 0: 
                        self.ammo = 0; self.player = Player(W//2, H//2)
                        self.cleared_nodes = []; self.current_node_id = -1; self.companions = []
                        self.set_story("start")
                    elif self.sel == 1 and has_save: self.load_game()
                    elif (self.sel == 1 and not has_save) or (self.sel == 2 and has_save): self.sel = 0; self.state = "OPTIONS"
                    else: pygame.quit(); sys.exit()
                        
            elif self.state == "OPTIONS":
                if k in (pygame.K_w, pygame.K_UP): self.sel = (self.sel - 1) % 3; play_tone(400, 50)
                if k in (pygame.K_s, pygame.K_DOWN): self.sel = (self.sel + 1) % 3; play_tone(400, 50)
                if k in (pygame.K_a, pygame.K_LEFT):
                    if self.sel == 0: cfg.SFX_VOL = max(0, cfg.SFX_VOL - 0.1); play_tone(400, 50)
                    elif self.sel == 1: cfg.BGM_VOL = max(0, cfg.BGM_VOL - 0.1); update_bgm_vol()
                if k in (pygame.K_d, pygame.K_RIGHT):
                    if self.sel == 0: cfg.SFX_VOL = min(1, cfg.SFX_VOL + 0.1); play_tone(400, 50)
                    elif self.sel == 1: cfg.BGM_VOL = min(1, cfg.BGM_VOL + 0.1); update_bgm_vol()
                if k == pygame.K_RETURN and self.sel == 2: self.sel = 0; self.state = "TITLE"

            elif self.state == "LEVEL_UP":
                if k in (pygame.K_a, pygame.K_LEFT): self.sel = max(0, self.sel - 1); play_tone(400, 50)
                if k in (pygame.K_d, pygame.K_RIGHT): self.sel = min(2, self.sel + 1); play_tone(400, 50)
                if k == pygame.K_RETURN: play_tone(800, 100); self.apply_upgrade(self.upgrade_choices[self.sel]["id"])

            elif self.state == "PAUSE":
                if k in (pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN): self.sel = (self.sel + 1) % 2; play_tone(400, 50)
                if k == pygame.K_RETURN:
                    play_tone(600, 100)
                    if self.sel == 0: self.state = self.prev_state
                    else: self.state = "TITLE"; self.sel = 0

            elif self.state == "STORY":
                if k == pygame.K_RETURN:
                    if self.dlg.done: self.finish_dialog()
                    else: self.dlg.ci = 999
            
            if k == pygame.K_ESCAPE:
                if self.state in ["MAP", "HUNT", "BOSS"]: self.prev_state = self.state; self.state = "PAUSE"; self.sel = 0

    def finish_dialog(self):
        if self.active_story_key in ["boss_win", "boss_lose"]: 
            self.state = "TITLE"; self.sel = 0
        elif self.target_node_id != -1 and self.state != "MAP":
            node = self.map_nodes[self.target_node_id]
            self.generate_map_objects(node['id'])
            if node['type'] == 'HUNT':
                self.state = "HUNT"
                self.player.x, self.player.y = self.world_w // 2, self.world_h // 2
                self.peluru_hutan = []; self.gems = []; self.monsters = []
                self.stage_timer = 0; self.side_boss_spawned = False; self.side_boss = None
            elif node['type'] == 'BOSS':
                self.state = "BOSS"
                self.boss = Entitas(self.world_w//2, self.world_h//2, img_boss); self.boss.hp = 5000; self.boss.max_hp = 5000
                self.peluru = []; self.boss_timer = 0
                self.player.x, self.player.y = self.world_w//2, self.world_h - H//2
        else:
            self.state = "MAP"

    def update(self):
        keys = pygame.key.get_pressed()
        if self.state not in ["PAUSE", "TITLE", "OPTIONS", "LEVEL_UP"]:
            self.player.update()
        if self.lightning_timer > 0: self.lightning_timer -= 1

        if self.state == "STORY": self.dlg.update()

        elif self.state == "HUNT":
            self.player.bergerak(keys, (self.world_w, self.world_h), self.obstacles)
            self.cam_x = max(0, min(self.player.x - W//2, self.world_w - W))
            self.cam_y = max(0, min(self.player.y - H//2, self.world_h - H))

            for c in self.companions:
                c.update(self.player.x, self.player.y, pygame.time.get_ticks(), self.monsters, self.peluru_hutan)

            self.stage_timer += 1
            max_timer = 60 * 90 # 90 Detik Survival
            
            if self.stage_timer < max_timer:
                spawn_rate = max(10, 60 - int((self.stage_timer / max_timer) * 50))
                if self.stage_timer % spawn_rate == 0 and len(self.monsters) < 60:
                    spawn_x = self.cam_x + random.choice([-100, W+100])
                    spawn_y = self.cam_y + random.choice([-100, H+100])
                    diff = 1 + (self.stage_timer / max_timer)
                    self.monsters.append(Monster(spawn_x, spawn_y, stage_diff=diff))
            elif not self.side_boss_spawned:
                self.side_boss_spawned = True
                spawn_x = self.player.x + random.choice([-W//3, W//3])
                spawn_y = self.player.y + random.choice([-H//3, H//3])
                sb = Monster(spawn_x, spawn_y, stage_diff=3)
                sb.img = img_sideboss; sb.rect = sb.img.get_rect(center=(sb.x, sb.y))
                sb.max_hp = 500 * (1 + self.current_node_id * 0.5); sb.hp = sb.max_hp
                sb.speed = H * 0.002; sb.m_type = 99
                self.monsters.append(sb); self.side_boss = sb
                play_tone(200, 1000)

            for m in self.monsters[:]:
                if m.stun > 0: m.stun -= 1
                else:
                    dist = math.hypot(self.player.x - m.x, self.player.y - m.y)
                    if dist < H * 0.05 and self.player.invuln <= 0:
                        dmg = 15 if m.m_type == 1 else 5
                        if getattr(m, "m_type", 0) == 99: dmg = 25 
                        self.player.hp -= dmg; self.player.invuln = 45; play_tone(100, 100)

                    if dist < H * 0.8:
                        ang = math.atan2(self.player.y - m.y, self.player.x - m.x)
                        m.x += math.cos(ang) * m.speed; m.y += math.sin(ang) * m.speed
                        m.cd_shoot -= 1
                        if m.cd_shoot <= 0 and dist < H * 0.5:
                            m.cd_shoot = random.randint(100, 200)
                            vx, vy = math.cos(ang) * (H*0.008), math.sin(ang) * (H*0.008)
                            self.peluru_hutan.append(Peluru(m.x, m.y, img_peluru, vx, vy, False))
                    else:
                        m.x += m.vx; m.y += m.vy
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
                            if m.hp <= 0:
                                if getattr(m, "m_type", 0) == 99: self.side_boss = None
                                else: self.gems.append(ExpGem(m.x, m.y, 10))
                                self.monsters.remove(m); self.ammo += (m.m_type + 1)
                            break
                else:
                    if math.hypot(p.x - self.player.x, p.y - self.player.y) < H*0.03 and self.player.invuln <= 0:
                        self.player.hp -= 5; self.player.invuln = 45; self.peluru_hutan.remove(p); play_tone(100, 100)
                if p.x < 0 or p.x > self.world_w or p.y < 0 or p.y > self.world_h:
                    if p in self.peluru_hutan: self.peluru_hutan.remove(p)

            if self.player.hp <= 0: self.set_story("boss_lose")
            
            if self.side_boss_spawned and self.side_boss not in self.monsters:
                self.cleared_nodes.append(self.target_node_id)
                self.companions.append(Companion(self.target_node_id))
                self.current_node_id = self.target_node_id; self.target_node_id = -1
                self.save_game(); self.set_story("hutan_clear")

        elif self.state == "BOSS":
            self.player.bergerak(keys, (self.world_w, self.world_h), self.obstacles)
            self.cam_x = max(0, min(self.player.x - W//2, self.world_w - W))
            self.cam_y = max(0, min(self.player.y - H//2, self.world_h - H))

            for c in self.companions: c.update(self.player.x, self.player.y, pygame.time.get_ticks(), [self.boss], self.peluru)
            
            dist_boss = math.hypot(self.player.x - self.boss.x, self.player.y - self.boss.y)
            if dist_boss > H * 0.2:
                ang_boss = math.atan2(self.player.y - self.boss.y, self.player.x - self.boss.x)
                self.boss.x += math.cos(ang_boss) * (H * 0.002); self.boss.y += math.sin(ang_boss) * (H * 0.002)
            self.boss.update_hitbox()

            self.boss_timer += 1
            if self.boss_timer % 60 == 0:
                for i in range(12):
                    a = math.radians(i * 30 + self.boss_timer)
                    self.peluru.append(Peluru(self.boss.x, self.boss.y, img_peluru, math.cos(a)*(H*0.008), math.sin(a)*(H*0.008), False))
            if self.boss_timer % 150 == 0:
                a = math.atan2(self.player.y - self.boss.y, self.player.x - self.boss.x)
                for i in range(-2, 3):
                    a_off = a + math.radians(i*15)
                    self.peluru.append(Peluru(self.boss.x, self.boss.y, img_peluru, math.cos(a_off)*(H*0.012), math.sin(a_off)*(H*0.012), False))
            
            for p in self.peluru[:]:
                p.gerak()
                if p.is_player:
                    if math.hypot(p.x - self.boss.x, p.y - self.boss.y) < H*0.1:
                        self.boss.hp -= self.player.slash_dmg; self.peluru.remove(p); play_tone(150, 50)
                else:
                    if math.hypot(p.x - self.player.x, p.y - self.player.y) < H*0.03 and self.player.invuln <= 0:
                        self.player.hp -= 15; self.player.invuln = 45; self.peluru.remove(p); play_tone(100, 100)
                if p.x < 0 or p.x > self.world_w or p.y < 0 or p.y > self.world_h:
                    if p in self.peluru: self.peluru.remove(p)

            if dist_boss < H * 0.15 and self.player.invuln <= 0:
                self.player.hp -= 20; self.player.invuln = 45; play_tone(100, 100)

            if self.boss.hp <= 0: self.set_story("boss_win")
            if self.player.hp <= 0: self.set_story("boss_lose")

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
            scr.fill(TL)
            txt(scr, "DEMON KING QUEST", F48, RD, W//2, H*0.2, cx=True)
            txt(scr, "Mouse Menu & Boss Fixed Edition", F24, LGR, W//2, H*0.3, cx=True)
            has_save = os.path.exists(SAVE_FILE)
            opts = ["Mulai Baru", "Lanjutkan Game", "Pengaturan", "Keluar"] if has_save else ["Mulai Baru", "Pengaturan", "Keluar"]
            for i, opt in enumerate(opts):
                col = YL if i == self.sel else GR
                txt(scr, ("> " if i == self.sel else "") + opt, F24, col, W//2, H*0.45 + i*(H*0.08), cx=True)
                
        elif self.state == "OPTIONS":
            scr.fill(TL)
            txt(scr, "PENGATURAN", F48, WH, W//2, H*0.2, cx=True)
            opts = [f"SFX Vol: < {int(cfg.SFX_VOL*10)} >", f"BGM Vol: < {int(cfg.BGM_VOL*10)} >", "Kembali"]
            for i, opt in enumerate(opts):
                col = YL if i == self.sel else GR
                txt(scr, ("> " if i == self.sel else "") + opt, F24, col, W//2, H*0.4 + i*(H*0.08), cx=True)

        elif self.state == "STORY":
            scr.fill((15, 10, 20)); self.dlg.draw(scr)

        elif self.state == "MAP":
            scr.fill(MAP_BG)
            for (n1, n2) in self.map_links:
                x1, y1 = self.map_nodes[n1]['x'], self.map_nodes[n1]['y']
                x2, y2 = self.map_nodes[n2]['x'], self.map_nodes[n2]['y']
                draw_dashed_line(scr, (100, 90, 80), (x1, y1), (x2, y2))
                
            for node in self.map_nodes:
                nx, ny = node['x'], node['y']; color = GR 
                if node['id'] in self.cleared_nodes: color = GN
                elif self.is_node_available(node['id']):
                    color = YL; pulse = int(H*0.045 + math.sin(pygame.time.get_ticks()*0.005)*5)
                    pygame.draw.circle(scr, WH, (nx, ny), pulse)
                
                if node['type'] == 'BOSS': pygame.draw.circle(scr, RD, (nx, ny), int(H*0.05))
                else: pygame.draw.circle(scr, color, (nx, ny), int(H*0.04))
                txt(scr, node['name'], F14, BK, nx, ny + H*0.06, cx=True)

            if self.current_node_id != -1:
                cx, cy = self.map_nodes[self.current_node_id]['x'], self.map_nodes[self.current_node_id]['y']
                scr.blit(img_player, img_player.get_rect(center=(cx, cy)))
            else:
                scr.blit(img_player, img_player.get_rect(center=(W*0.5, H*0.95)))
                
            txt(scr, f"Lv: {self.player.level} | Teman: {len(self.companions)} | ESC: Pause", F18, BK, 20, 20)

        elif self.state in ["HUNT", "BOSS"] or (self.state in ["PAUSE", "LEVEL_UP"] and self.prev_state in ["HUNT", "BOSS"]):
            scr.fill(self.bg_color)
            for px, py, pr in self.paths:
                if self.cam_x - pr < px < self.cam_x + W + pr and self.cam_y - pr < py < self.cam_y + H + pr:
                    pygame.draw.circle(scr, self.path_color, (int(px - self.cam_x), int(py - self.cam_y)), pr)

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
                        pygame.draw.rect(scr, RD, (self.boss.x - self.cam_x - H*0.2, self.boss.y - self.cam_y - H*0.12, H*0.4, H*0.015))
                        pygame.draw.rect(scr, GN, (self.boss.x - self.cam_x - H*0.2, self.boss.y - self.cam_y - H*0.12, H*0.4 * (max(0, self.boss.hp)/5000), H*0.015))
                    obj.draw(scr, self.cam_x, self.cam_y)
                    
                for p in self.peluru: p.draw(scr, self.cam_x, self.cam_y)
            
            self.player.draw_slash(scr, self.cam_x, self.cam_y)
            if self.lightning_timer > 0 and self.lightning_target:
                self.draw_lightning((self.player.x, self.player.y), (self.lightning_target.x, self.lightning_target.y), self.cam_x, self.cam_y)
            
            # --- HUD ---
            if self.state == "HUNT" or (self.state in ["PAUSE", "LEVEL_UP"] and self.prev_state == "HUNT"):
                if not self.side_boss_spawned:
                    sisa_waktu = max(0, 90 - (self.stage_timer // 60))
                    txt(scr, f"WAKTU: {sisa_waktu}s", F24, YL, W//2, 35, cx=True)
                else:
                    txt(scr, f"!! BUNUH SIDE BOSS !!", F48, RD, W//2, 50, cx=True)
            elif self.state == "BOSS" or (self.state in ["PAUSE", "LEVEL_UP"] and self.prev_state == "BOSS"):
                txt(scr, f"!! KALAHKAN MALACHAR !!", F48, RD, W//2, 50, cx=True)

            pygame.draw.rect(scr, GR, (0, 0, W, 10))
            pygame.draw.rect(scr, EXP_COL, (0, 0, W * (self.player.exp / self.player.max_exp), 10))
            txt(scr, f"Lv {self.player.level}", F18, WH, 20, 25)
            
            hp_w = H*0.3; hp_h = H*0.025
            pygame.draw.rect(scr, RD, (20, 45, hp_w, hp_h))
            pygame.draw.rect(scr, GN, (20, 45, hp_w * (max(0, self.player.hp)/self.player.max_hp), hp_h))
            pygame.draw.rect(scr, WH, (20, 45, hp_w, hp_h), 2)
            txt(scr, f"{int(self.player.hp)} / {self.player.max_hp}", F14, WH, 20 + hp_w/2, 45 + hp_h/2, cx=True, cy=True)
            
            stat_cd = "SIAP" if self.player.cd_lightning <= 0 else f"{self.player.cd_lightning//60}s"
            txt(scr, f"Listrik (1): {stat_cd} | Ammo: {self.ammo}", F14, WH, 20, 85)

        if self.state == "PAUSE":
            ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((0, 0, 0, 180)); scr.blit(ov, (0, 0))
            txt(scr, "GAME PAUSED", F48, WH, W//2, H*0.3, cx=True)
            for i, opt in enumerate(["Lanjutkan", "Kembali ke Menu Utama"]):
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

if __name__ == "__main__":
    Game().run()