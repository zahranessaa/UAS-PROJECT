import pygame

# Karena class Dialog butuh font F18 dan F14 untuk menggambar teks, 
# kita definisikan ulang setup font-nya di sini agar tidak error.
pygame.font.init()
H = 720 # Sesuaikan dengan tinggi layar standar gamemu
W = 1280

def mkfont(sz):
    try: return pygame.font.SysFont("Courier New", sz, bold=True)
    except: return pygame.font.Font(None, sz)

F14 = mkfont(int(H*0.025))
F18 = mkfont(int(H*0.035))
BK = (0, 0, 0)
WH = (255, 255, 255)
YL = (240, 200, 40)

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
    "intro": ("NARATOR", "TEST!"),
    "start": ("KAEL", "Pohon dan bebatuan tidak bisa ditembus. Manfaatkan alam untuk bersembunyi dari musuh! Tahan 90 Detik untuk memanggil Side Boss."),
    "hutan_masuk": ("KAEL", "Ini Hutan Pinus. Pohon-pohonnya bisa melindungiku dari peluru musuh."),
    "gurun_masuk": ("KAEL", "Gurun Wild West. Hati-hati jangan sampai mentok di kaktus raksasa itu!"),
    "rawa_masuk": ("KAEL", "Rawa Gelap... Pohon mati ini sangat keras, aku bisa menggunakannya sebagai tembok."),
    "salju_masuk": ("KAEL", "Lembah Salju. Bersembunyilah di balik pohon pinus beku!"),
    "hutan_clear": ("KAEL", "Side Boss mati! Temanku bebas. Waktunya melangkah ke area selanjutnya."),
    "boss_masuk": ("KAEL", "Ini akhirnya... Kastil Raja Iblis! Aku harus menghindari serangan mematikan Malachar, cari celah, lalu tebas dia!"),
    "boss_win": ("NARATOR", "MALACHAR BERHASIL DIKALAHKAN! Kedamaian kembali ke Valoria."),
    "boss_lose": ("NARATOR", "Kael telah gugur... Kiamat telah tiba!"),
}

BASE_UPGRADES = [
    {"id": "hp", "name": "Max HP +20", "desc": "Menambah batas HP dan memulihkan 20 HP."},
    {"id": "dmg", "name": "Damage Tebasan +10", "desc": "Tebasan pedang lebih menyakitkan."},
    {"id": "spd", "name": "Kecepatan +10%", "desc": "Lari dari musuh lebih kencang."},
    {"id": "cd", "name": "Attack Speed+", "desc": "Cooldown tebasan lebih cepat."},
    {"id": "rad", "name": "Radius Tebasan+", "desc": "Jangkauan tebasan pedang membesar."},
    {"id": "mag", "name": "Magnet EXP+", "desc": "Mengambil EXP dari jarak lebih jauh."}
]