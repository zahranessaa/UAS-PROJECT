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
F24 = mkfont(int(H*0.045)) # Tambahan font lebih besar untuk cinematic
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
        self.mode = "VN" 
        self.pages = []
        self.curr_page = 0

    def set(self, spk, text):
        self.spk = spk
        self.ci = 0
        self.done = False
        
        if spk == "CINEMATIC":
            self.mode = "CINEMATIC"
            self.pages = text # text berupa list untuk pindah halaman
            self.curr_page = 0
            self._load_page()
        else:
            self.mode = "VN"
            self._wrap(text)

    def _load_page(self):
        if self.curr_page < len(self.pages):
            self._wrap(self.pages[self.curr_page])
            self.ci = 0
        else:
            self.done = True

    def _wrap(self, text):
        words = text.split(); lines = []; line = ""
        font_dipakai = F24 if self.mode == "CINEMATIC" else F18
        for w in words:
            if font_dipakai.size(line + " " + w)[0] < W*0.8: line += (" " if line else "") + w
            else: lines.append(line); line = w
        if line: lines.append(line)
        self.lines = lines

    def next_page(self):
        # Dipanggil saat spasi / mouse diklik
        if self.ci >= sum(len(l) for l in self.lines):
            if self.mode == "CINEMATIC":
                self.curr_page += 1
                self._load_page()
            else:
                self.done = True
        else:
            self.ci = 999 # Skip animasi ketik agar teks langsung full

    def update(self):
        if not self.done:
            self.ci += 0.5

    def draw(self, surf):
        if self.mode == "CINEMATIC":
            surf.fill((0, 0, 0)) # Background full hitam
            drawn = 0
            tot_y = len(self.lines) * (H * 0.08)
            sy = (H - tot_y) // 2
            
            for i, line in enumerate(self.lines):
                rem = max(0, int(self.ci) - drawn)
                if rem > 0:
                    txt(surf, line[:rem], F24, WH, W//2, sy + i*(H*0.08), cx=True, cy=True)
                drawn += len(line)
                
            if self.ci >= sum(len(l) for l in self.lines):
                txt(surf, "▼ Space / Klik untuk lanjut", F14, YL, W//2, H*0.9, cx=True)
        else:
            bx, by, bw, bh = W*0.1, H*0.7, W*0.8, H*0.25
            pygame.draw.rect(surf, (20, 20, 40), (bx, by, bw, bh)); pygame.draw.rect(surf, WH, (bx, by, bw, bh), 3)
            if self.spk:
                pygame.draw.rect(surf, (40, 40, 80), (bx+20, by-30, F18.size(self.spk)[0]+20, 35)); txt(surf, self.spk, F18, YL, bx+30, by-25)
            drawn = 0
            for i, line in enumerate(self.lines):
                rem = max(0, int(self.ci) - drawn)
                txt(surf, line[:rem], F18, WH, bx+30, by+20 + i*(H*0.04))
                drawn += len(line)
            if self.ci >= sum(len(l) for l in self.lines):
                txt(surf, "▼ Enter / Klik", F14, YL, bx+bw-140, by+bh-30)

STORY = {
    # Teks intro dipecah menjadi array agar muncul bergantian per halaman
    "intro": ("CINEMATIC", [
        "Negeri yang dijaga oleh kekuatan yang tak boleh jatuh ke tangan yang salah.",
        "Hingga seseorang memastikan ia jatuh.",
        "Kini hanya tersisa saya, Kael.",
        "Satu kesempatan dan satu pertanyaan yang belum terjawab",
        "Apakah AurenVeil masih bisa diselamatkan?",
    ]),
    "start": ("KAEL", "Pohon dan bebatuan tidak bisa ditembus. Manfaatkan alam untuk bersembunyi dari musuh! Tahan 90 Detik untuk memanggil Side Boss."),
    "hutan_masuk": ("KAEL", "Ini Hutan Pinus. Dimana tempat bersembunyinya monster berelemen listrik."),
    "gurun_masuk": ("KAEL", "Gurun Wild West. Hati-hati dengan ledakan monster api itu"),
    "rawa_masuk": ("KAEL", "Rawa Gelap... Pohon mati ini sangat keras, aku bisa menggunakannya sebagai tembok."),
    "salju_masuk": ("KAEL", "Lembah Salju. Bersembunyilah dari golem tanah itu."),
    "hutan_clear": ("KAEL", "Monster elemen sudah berhasil saya dapatkan, Dan sekarang dia menjadi temanku"),
    "boss_masuk": ("CINEMATIC", [
        "Pertarungan sengit terjadi antara sang penjaga melawan kegelapan"
    ]),
    "boss_win": ("CINEMATIC",[
        "Kekuatanku berhasil menaklukkan kegelapan...",
        "Bukan sorak sorai. Bukan kejayaan",
        "Hanya... cahaya. perlahan kembali, menyentuh tanah yang sudah gelap",
        "Aku berdiri di sini, ditanah yang belum pernah kuinjak, tapi selalu kurindukan",
        "Bukan sebagai raja, Tapi sebagai penjaga",
        "Seperti yang harus yang saya lakukan."
    ]),
    "boss_lose": ("CINEMATIC", [
        "Serangan terakhir datang seperti langit jatuh, kael jatuh terlentang.",
        "AurenVeil kehilangan penjaganya..."
    ]),
}

BASE_UPGRADES = [
    {"id": "hp", "name": "Max HP +20", "desc": "Menambah batas HP dan memulihkan 20 HP."},
    {"id": "dmg", "name": "Damage Tebasan +10", "desc": "Tebasan pedang lebih menyakitkan."},
    {"id": "spd", "name": "Kecepatan +10%", "desc": "Lari dari musuh lebih kencang."},
    {"id": "cd", "name": "Attack Speed+", "desc": "Cooldown tebasan lebih cepat."},
    {"id": "rad", "name": "Radius Tebasan+", "desc": "Jangkauan tebasan pedang membesar."},
    {"id": "mag", "name": "Magnet EXP+", "desc": "Mengambil EXP dari jarak lebih jauh."}
]