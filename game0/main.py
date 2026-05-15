"""
╔══════════════════════════════════════════════════════════╗
║        DEMON KING QUEST  ─  Pixel Chronicle              ║
║   Visual Novel RPG with Multi-Ending System              ║
╚══════════════════════════════════════════════════════════╝
Controls:
  Arrow keys / WASD  ─ Navigate
  Z / Enter          ─ Confirm / Advance dialog
  X / Escape         ─ Cancel / Back
"""

import pygame, sys, json, os, math, random, array as arr
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    _AUDIO = True
except Exception:
    _AUDIO = False

# ─────────────────────────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────────────────────────
W, H   = 800, 600
FPS    = 60
SAVE   = "dkq_save.json"

BK  = (0,   0,   0)
WH  = (255,255,255)
GR  = (80, 80, 80)
LGR = (160,160,160)
DGR = (20, 20, 20)
RD  = (210, 40, 40)
DRD = (120, 10, 10)
GN  = (50, 190, 80)
DGN = (20,100, 40)
BL  = (60, 130,230)
YL  = (240,200, 40)
OR  = (230,120, 30)
PU  = (160, 70,220)
DPU = (70,  20,120)
CY  = (50, 210,210)
PK  = (230,100,160)
TL  = (30,  10, 50)   # title bg
NB  = (10,  10, 25)   # night blue

scr   = pygame.display.set_mode((W, H))
pygame.display.set_caption("DEMON KING QUEST  ─  Pixel Chronicle")
clk   = pygame.time.Clock()

# ─────────────────────────────────────────────────────────────────
#  FONTS  (pixel/monospace)
# ─────────────────────────────────────────────────────────────────
def mkfont(sz, bold=True):
    for nm in ("Courier New","Courier","Lucida Console","monospace"):
        try: return pygame.font.SysFont(nm, sz, bold=bold)
        except: pass
    return pygame.font.Font(None, sz)

F10 = mkfont(13); F14 = mkfont(16); F18 = mkfont(20)
F24 = mkfont(26); F32 = mkfont(34); F48 = mkfont(52)

# ─────────────────────────────────────────────────────────────────
#  SYNTH SFX
# ─────────────────────────────────────────────────────────────────
def _tone(freq, ms, vol=0.25, wave="sq", sr=22050):
    """Generate synth tone — no numpy, no sndarray, pure bytes."""
    if not _AUDIO: return None
    try:
        n = int(sr * ms / 1000)
        # stereo 16-bit signed PCM: 4 bytes per frame (L+R)
        buf = bytearray(n * 4)
        for i in range(n):
            t = i / sr
            if   wave == "sq": v = vol if math.sin(2*math.pi*freq*t) > 0 else -vol
            elif wave == "si": v = vol * math.sin(2*math.pi*freq*t)
            elif wave == "tr":
                p = (t*freq) % 1.0
                v = vol * (4*p - 1 if p < .5 else 3 - 4*p)
            else:              v = vol * (random.random()*2 - 1)
            s = max(-32767, min(32767, int(v * 32767)))
            lo, hi = s & 0xFF, (s >> 8) & 0xFF
            b = i * 4
            buf[b], buf[b+1], buf[b+2], buf[b+3] = lo, hi, lo, hi
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None

class SFX:
    def __init__(self):
        self.vol = 0.7; self.mute = False
        self._c = {}
    def _get(self,k,fn):
        if k not in self._c:
            try: self._c[k]=fn()
            except: self._c[k]=None
        return self._c[k]
    def _p(self,s):
        if self.mute or s is None: return
        try: s.set_volume(self.vol); s.play()
        except: pass
    def cursor(self):  self._p(self._get("cu",lambda:_tone(440, 50,.12,"sq")))
    def confirm(self): self._p(self._get("co",lambda:_tone(660,120,.18,"si")))
    def cancel(self):  self._p(self._get("ca",lambda:_tone(220,100,.18,"sq")))
    def blip(self):
        f=random.choice([320,360,400,450])
        self._p(_tone(f,28,.07,"sq"))
    def hit(self):     self._p(self._get("hi",lambda:_tone(160,160,.28,"no")))
    def magic(self):   self._p(self._get("ma",lambda:_tone(880,200,.18,"si")))
    def heal(self):    self._p(self._get("he",lambda:_tone(523,150,.18,"tr")))
    def victory(self): self._p(self._get("vi",lambda:_tone(784,400,.22,"si")))
    def defeat(self):  self._p(self._get("de",lambda:_tone(110,600,.25,"sq")))
    def save(self):    self._p(self._get("sv",lambda:_tone(1047,300,.20,"si")))

sfx = SFX()

# ─────────────────────────────────────────────────────────────────
#  PIXEL-ART HELPERS
# ─────────────────────────────────────────────────────────────────
def box(surf, bg, rect, border=WH, bw=2, fill=True):
    r = pygame.Rect(rect)
    if fill: pygame.draw.rect(surf, bg, r)
    pygame.draw.rect(surf, border, r, bw)

def txt(surf, s, font, col, x, y, shadow=True, cx=False, cy=False):
    ren = font.render(s, False, col)
    bx = x - ren.get_width()//2  if cx else x
    by = y - ren.get_height()//2 if cy else y
    if shadow:
        sh = font.render(s, False, (0,0,0))
        surf.blit(sh,(bx+2,by+2))
    surf.blit(ren,(bx,by))

def hp_bar(surf, val, mx, x, y, w=160, h=14):
    ratio = max(0,val/mx)
    col = GN if ratio>.5 else YL if ratio>.25 else RD
    pygame.draw.rect(surf,(15,15,15),(x,y,w,h))
    pygame.draw.rect(surf, col, (x,y,int(w*ratio),h))
    pygame.draw.rect(surf, WH,  (x,y,w,h), 2)
    label = f"{val}/{mx}"
    txt(surf, label, F10, WH, x+w//2, y+2, shadow=False, cx=True)

# ─────────────────────────────────────────────────────────────────
#  PIXEL SPRITES  (drawn with colored rectangles)
# ─────────────────────────────────────────────────────────────────
PATTERNS = {
"player": (
"  XXX  ","XXXXXXX"," XXXXX ","  X X  "," X   X ","X     X",),
"ally_a": (
"  AAA  ","AAAAAAA"," AAAAA ","  A A  "," A   A ","A     A",),
"ally_b": (
" BBBBB ","BBBBBBB","BBBBBBB"," B   B ","BB   BB","B     B",),
"slime": (
" SSSSS ","SSSSSSS","SSSSSSS"," S S S ","       ",),
"wolf": (
"WW   WW"," WWWWW ","WWWWWWW","WWWWWWW"," WW WW ",),
"golem": (
"GGGGGGG","GGGGGGG","GGGGGGG","G GGG G","GG   GG",),
"dragon": (
"D  D  D","DDDDDDD","DDDDDDD"," DDDDD ","DD   DD","D     D",),
"king": (
"K KKK K","KKKKKKK","KKKKKKK","KKKKKKK","KKKKKKK"," K   K ","KK   KK",),
}
PCOLS = {
"X":(100,180,255),"A":(255,180, 60),"B":(170, 90,240),
"S":( 60,210,100),"W":(200,150, 60),"G":(130,130,140),
"D":(220, 80, 30),"K":(210, 30, 30),
}

class Sprite:
    def __init__(self, key, ps=8):
        self.pat = PATTERNS.get(key, PATTERNS["player"])
        self.ps  = ps; self.tick = 0
    def draw(self, surf, cx, cy, scale=1.0, shake=False):
        ps = max(1,int(self.ps*scale))
        ox = 2 if (shake and self.tick%4<2) else 0
        W2 = len(self.pat[0])*ps; H2 = len(self.pat)*ps
        sx, sy = cx-W2//2+ox, cy-H2//2
        for r, row in enumerate(self.pat):
            for c, ch in enumerate(row):
                if ch!=" ":
                    col = PCOLS.get(ch, WH)
                    pygame.draw.rect(surf, col,(sx+c*ps,sy+r*ps,ps-1,ps-1))
        self.tick+=1

# ─────────────────────────────────────────────────────────────────
#  TYPEWRITER DIALOG BOX
# ─────────────────────────────────────────────────────────────────
class Dialog:
    def __init__(self):
        self.lines=[]; self.speaker=""; self.ci=0
        self.done=False; self.tick=0; self.spd=2
        self.portrait=None
    def set(self, spk, text, portrait=None):
        words=text.split()
        lines,line=[],""
        for w in words:
            test=(line+" "+w).strip()
            if F18.size(test)[0]<540: line=test
            else: lines.append(line); line=w
        if line: lines.append(line)
        self.lines=lines; self.speaker=spk
        self.ci=0; self.done=False; self.tick=0
        self.portrait=portrait
    def update(self):
        if self.done: return
        self.tick+=1
        rate = max(1, 4-self.spd)
        if self.tick%rate==0:
            total=sum(len(l) for l in self.lines)
            if self.ci<total:
                self.ci+=1
                if random.random()<.35: sfx.blip()
            else: self.done=True
    def skip(self):
        self.ci=sum(len(l) for l in self.lines); self.done=True
    def draw(self, surf):
        bx,by,bw,bh = 20, H-180, W-40, 162
        box(surf,(8,8,22),(bx,by,bw,bh),WH,3)
        tx = bx+110 if self.portrait else bx+18
        if self.portrait:
            self.portrait.draw(surf, bx+55, by+bh//2, scale=1.5)
            pygame.draw.line(surf, GR,(bx+100,by+10),(bx+100,by+bh-10),2)
        if self.speaker:
            box(surf,(25,25,55),(tx,by-30,max(160,F18.size(self.speaker)[0]+20),30),(YL),2)
            txt(surf,self.speaker,F18,YL,tx+8,by-27)
        drawn=0
        for i,line in enumerate(self.lines):
            rem=self.ci-drawn
            vis=line[:max(0,rem)]
            drawn+=len(line)
            r=pygame.Rect(tx,by+12+i*28,bw-tx+bx-10,26)
            pygame.draw.rect(surf,(8,8,22),r)
            txt(surf,vis,F18,WH,tx,by+12+i*28,shadow=False)
        if self.done:
            p=int(abs(math.sin(pygame.time.get_ticks()*.005))*220)
            txt(surf,"▼",F18,(p,p,40),bx+bw-28,by+bh-30,shadow=False)

dlg = Dialog()

# ─────────────────────────────────────────────────────────────────
#  BATTLE ENTITY
# ─────────────────────────────────────────────────────────────────
class Entity:
    def __init__(self, name, hp, atk, dfn, spk, col):
        self.name=name; self.maxhp=hp; self.hp=hp
        self.atk=atk; self.dfn=dfn
        self.spr=Sprite(spk); self.col=col
        self.shake=False; self.flash=0; self._dx=0
    def dmg(self, d):
        d=max(1,d-self.dfn); self.hp=max(0,self.hp-d)
        self.shake=True; self.flash=8; sfx.hit(); return d
    def alive(self): return self.hp>0

# ─────────────────────────────────────────────────────────────────
#  BATTLE SCENE
# ─────────────────────────────────────────────────────────────────
class Battle:
    ACTS = ["SERANG","SIHIR","ITEM","KABUR"]
    def __init__(self, party, enemy, flee_ok=True):
        self.party=[e for e in party if e.alive()]
        self.enemy=enemy; self.flee_ok=flee_ok
        self.state="player"   # player|enemy|result
        self.log=[]; self.ai=0
        self.result=None      # win|lose|flee
        self.tick=0; self.wave=0
        self.popups=[]        # [x,y,txt,col,ttl]
        self.items=3
    def log_add(self,m):
        self.log.append(m)
        if len(self.log)>5: self.log.pop(0)
    def do(self, act):
        hero=self.party[0]
        if act=="SERANG":
            d=self.enemy.dmg(hero.atk+random.randint(-3,6))
            self.log_add(f"{hero.name} menyerang! -{d}HP")
            self.popups.append([580,230,f"-{d}",RD,60])
        elif act=="SIHIR":
            d=self.enemy.dmg(int(hero.atk*1.8)+random.randint(0,12))
            self.log_add(f"Sihir! -{d}HP")
            self.popups.append([580,230,f"✦-{d}",CY,70]); sfx.magic()
        elif act=="ITEM":
            if self.items>0:
                hl=random.randint(25,45); hero.hp=min(hero.maxhp,hero.hp+hl)
                self.items-=1
                self.log_add(f"Item! +{hl}HP ({self.items} sisa)")
                self.popups.append([200,370,f"+{hl}HP",GN,60]); sfx.heal()
            else:
                self.log_add("Item habis!")
        elif act=="KABUR":
            if not self.flee_ok:
                self.log_add("Tidak bisa kabur dari pertarungan ini!")
                self.state="enemy"; pygame.time.set_timer(pygame.USEREVENT+1,1000)
                return
            if random.random()<.5:
                self.log_add("Berhasil kabur!"); self.result="flee"; self.state="result"; return
            else:
                self.log_add("Gagal kabur!")
        if not self.enemy.alive():
            self.result="win"; self.state="result"; sfx.victory(); return
        self.state="enemy"; pygame.time.set_timer(pygame.USEREVENT+1,1100)
    def enemy_turn(self):
        alive=[p for p in self.party if p.alive()]
        if not alive: self.result="lose"; self.state="result"; sfx.defeat(); return
        tgt=random.choice(alive)
        d=tgt.dmg(self.enemy.atk+random.randint(-3,5))
        self.log_add(f"{self.enemy.name} menyerang {tgt.name}! -{d}HP")
        self.popups.append([getattr(tgt,'_dx',200),360,f"-{d}",OR,60])
        if not any(p.alive() for p in self.party):
            self.result="lose"; self.state="result"; sfx.defeat()
        else: self.state="player"
    def update(self):
        self.tick+=1; self.wave=math.sin(self.tick*.05)
        for e in self.party+[self.enemy]:
            if e.flash>0:
                e.flash-=1
                if e.flash==0: e.shake=False
        self.popups=[[x,y-1,t,c,ttl-1] for x,y,t,c,ttl in self.popups if ttl>0]
    def draw(self, surf):
        # BG grid
        surf.fill((12,4,20))
        for i in range(0,W,36): pygame.draw.line(surf,(22,10,36),(i,0),(i,H),1)
        for j in range(0,H,36): pygame.draw.line(surf,(22,10,36),(0,j),(W,j),1)
        # Enemy
        ex,ey=560, int(220+self.wave*10)
        self.enemy.spr.draw(surf,ex,ey,scale=3.5,shake=self.enemy.shake)
        hp_bar(surf,self.enemy.hp,self.enemy.maxhp,ex-90,ey-115,180,16)
        txt(surf,self.enemy.name,F24,self.enemy.col,ex,ey-138,cx=True)
        # Party
        alive=[p for p in self.party if p.alive()]
        for i,p in enumerate(alive):
            px=100+i*160; p._dx=px
            p.spr.draw(surf,px,360,scale=2.4,shake=p.shake)
            txt(surf,p.name,F10,p.col,px,315,cx=True)
            hp_bar(surf,p.hp,p.maxhp,px-65,322,130,12)
        # Action box
        if self.state=="player":
            bx,by=20,H-175
            box(surf,(8,8,22),(bx,by,360,145),WH,2)
            txt(surf,"AKSI",F14,YL,bx+10,by+6)
            for i,a in enumerate(self.ACTS):
                ax=bx+15+(i%2)*165; ay=by+32+(i//2)*50
                sel=(i==self.ai)
                box(surf,(35,35,75) if sel else (15,15,35),(ax-4,ay-4,148,38),YL if sel else GR,2)
                txt(surf,("► " if sel else "  ")+a,F18,YL if sel else LGR,ax,ay)
            txt(surf,f"ITEM x{self.items}",F10,CY,bx+260,by+128)
        # Log
        lx,ly=392,H-175
        box(surf,(8,8,22),(lx,ly,W-lx-20,145),LGR,2)
        txt(surf,"LOG PERTEMPURAN",F10,LGR,lx+8,ly+5)
        for i,m in enumerate(self.log[-5:]):
            txt(surf,m,F10,WH,lx+6,ly+22+i*22,shadow=False)
        # Popups
        for x,y,t,c,ttl in self.popups:
            txt(surf,t,F24,c,int(x),int(y),cx=True)
        # Result overlay
        if self.state=="result":
            ov=pygame.Surface((W,H),pygame.SRCALPHA)
            ov.fill((0,0,0,170)); surf.blit(ov,(0,0))
            if self.result=="win":
                txt(surf,"⚔  MENANG!",F48,YL,W//2,190,cx=True)
                txt(surf,"Tekan ENTER untuk lanjut",F18,WH,W//2,270,cx=True)
            elif self.result=="lose":
                txt(surf,"✖  KALAH...",F48,RD,W//2,190,cx=True)
                txt(surf,"Tekan ENTER untuk lanjut",F18,WH,W//2,270,cx=True)
            elif self.result=="flee":
                txt(surf,"➤  KABUR!",F48,CY,W//2,190,cx=True)
                txt(surf,"Tekan ENTER untuk lanjut",F18,WH,W//2,270,cx=True)
    def input(self,ev):
        if ev.type==pygame.KEYDOWN:
            if self.state=="player":
                if ev.key in(pygame.K_LEFT,pygame.K_a):   self.ai=(self.ai-1)%4; sfx.cursor()
                elif ev.key in(pygame.K_RIGHT,pygame.K_d):self.ai=(self.ai+1)%4; sfx.cursor()
                elif ev.key in(pygame.K_UP,pygame.K_w):   self.ai=(self.ai-2)%4; sfx.cursor()
                elif ev.key in(pygame.K_DOWN,pygame.K_s): self.ai=(self.ai+2)%4; sfx.cursor()
                elif ev.key in(pygame.K_RETURN,pygame.K_z):
                    sfx.confirm(); self.do(self.ACTS[self.ai])
        elif ev.type==pygame.USEREVENT+1:
            pygame.time.set_timer(pygame.USEREVENT+1,0)
            if self.state=="enemy": self.enemy_turn()

# ─────────────────────────────────────────────────────────────────
#  SAVE PLACE SCREEN
# ─────────────────────────────────────────────────────────────────
class SavePlace:
    def __init__(self, location_name, on_done):
        self.loc=location_name; self.done_cb=on_done
        self.tick=0; self.confirmed=False; self.timer=0
    def draw(self, surf):
        self.tick+=1
        ov=pygame.Surface((W,H),pygame.SRCALPHA)
        ov.fill((0,0,0,200)); surf.blit(ov,(0,0))
        # star
        cx,cy=W//2,H//2-30
        for i in range(12):
            a=math.radians(i*30+self.tick*2)
            r=40+10*math.sin(self.tick*.08)
            x2,y2=cx+r*math.cos(a),cy+r*math.sin(a)
            pygame.draw.line(surf,YL,(cx,cy),(int(x2),int(y2)),2)
        pygame.draw.circle(surf,YL,(cx,cy),18)
        pygame.draw.circle(surf,(255,240,100),(cx,cy),14)
        box(surf,(15,15,40),(W//2-200,H//2+10,400,130),YL,3)
        txt(surf,"✦ TITIK SIMPAN ✦",F24,YL,W//2,H//2+18,cx=True)
        txt(surf,self.loc,F18,WH,W//2,H//2+50,cx=True)
        if not self.confirmed:
            txt(surf,"Tekan Z / Enter untuk Simpan",F14,CY,W//2,H//2+85,cx=True)
        else:
            p=int(abs(math.sin(self.tick*.15))*200)
            txt(surf,"Data Tersimpan!",F18,(p,255,p),W//2,H//2+85,cx=True)
            self.timer+=1
            if self.timer>90: self.done_cb()
    def input(self,ev):
        if ev.type==pygame.KEYDOWN and not self.confirmed:
            if ev.key in(pygame.K_z,pygame.K_RETURN):
                self.confirmed=True; sfx.save()

# ─────────────────────────────────────────────────────────────────
#  SETTINGS SCREEN
# ─────────────────────────────────────────────────────────────────
class Settings:
    def __init__(self):
        self.idx=0
    def draw(self,surf):
        surf.fill((8,8,20))
        txt(surf,"⚙  PENGATURAN",F48,YL,W//2,50,cx=True)
        pygame.draw.line(surf,YL,(80,110),(W-80,110),2)
        spd_lbl=["LAMBAT","SEDANG","CEPAT"][min(2,dlg.spd-1)]
        items=[
            f"Volume: {'[MUTE]' if sfx.mute else str(int(sfx.vol*100))+'%'}",
            f"Kecepatan Teks: {spd_lbl}",
            "Kembali ke Menu",
        ]
        for i,item in enumerate(items):
            sel=(i==self.idx)
            by=170+i*80
            box(surf,(35,30,65) if sel else (15,12,30),(W//2-210,by,420,56),YL if sel else GR,2)
            txt(surf,("► " if sel else "  ")+item,F24,YL if sel else LGR,W//2-195,by+14)
        txt(surf,"↑↓ Pilih   ←→ Ubah   Enter Konfirmasi",F10,GR,W//2,H-30,cx=True)
    def input(self,ev):
        if ev.type!=pygame.KEYDOWN: return None
        k=ev.key
        if k in(pygame.K_UP,pygame.K_w):   self.idx=(self.idx-1)%3; sfx.cursor()
        elif k in(pygame.K_DOWN,pygame.K_s):self.idx=(self.idx+1)%3; sfx.cursor()
        elif k in(pygame.K_LEFT,pygame.K_a): self._adj(-1)
        elif k in(pygame.K_RIGHT,pygame.K_d):self._adj(1)
        elif k in(pygame.K_RETURN,pygame.K_z):
            if self.idx==2: sfx.confirm(); return "back"
        return None
    def _adj(self,d):
        sfx.cursor()
        if self.idx==0:
            if d>0: sfx.vol=min(1.0,sfx.vol+.1); sfx.mute=False
            else:
                sfx.vol=max(0.0,sfx.vol-.1)
                if sfx.vol<=0: sfx.mute=True
        elif self.idx==1:
            dlg.spd=max(1,min(3,dlg.spd+d))

settings = Settings()

# ─────────────────────────────────────────────────────────────────
#  PORTRAIT SPRITES  (singleton)
# ─────────────────────────────────────────────────────────────────
SPR = {k:Sprite(k) for k in PATTERNS}

# ─────────────────────────────────────────────────────────────────
#  STORY DATA
# ─────────────────────────────────────────────────────────────────
# Each entry: (id, speaker, text, portrait_key, next_id)
STORY = [
# ═══════════ PROLOG ═══════════
("s00","NARATOR",
 "Di Kerajaan Valoria, bayang-bayang kegelapan menyelimuti langit. Raja Iblis MALACHAR bangkit dari tidurnya yang panjang dan mulai menghancurkan kota demi kota.",
 None,"s01"),
("s01","ARION",
 "Aku tidak bisa tinggal diam. Tidak ada ksatria yang berani maju... maka akulah yang harus pergi.",
 "player","s02"),
("s02","NARATOR",
 "Arion, seorang petualang muda, memulai perjalanannya sendirian. Ia tahu butuh kawan — dan monster-monster yang kuat — untuk menghadapi Sang Raja Iblis.",
 None,"s03"),
# ═══════════ MONSTER PERTAMA — SLIME ═══════════
("s03","NARATOR",
 "Di Hutan Elmwood, seekor Slime Kristal menghadang jalan. Arion menggenggam tongkatnya erat-erat.",
 None,"BATTLE_slime"),
("post_slime","ARION",
 "Kau pemberani juga, Slime kecil. Ikutlah bersamaku — perjalanan ini masih panjang.",
 "player","s04"),
("s04","NARATOR",
 "Slime Kristal bergabung! Party monster: [Slime Kristal].",
 None,"s05"),
# ═══════════ PERTEMUAN ELARA (ALLY A) ═══════════
("s05","NARATOR",
 "Di tepi hutan, seorang gadis berambut api sedang bermain lempar batu sambil menguap.",
 None,"s06"),
("s06","ELARA",
 "Hei hei hei! Kamu mau ke mana sih seserius itu? Wajahmu seperti orang mau bayar pajak.",
 "ally_a","s07"),
("s07","ARION",
 "Aku ingin mengalahkan Raja Iblis Malachar.",
 "player","s08"),
("s08","ELARA",
 "Malachar?! Wah, akhirnya ada yang nekat! Hidupku bosan sekali belakangan ini. Boleh aku ikut? Sekedar mencoba hal baru~",
 "ally_a","s09"),
("s09","ARION",
 "Tentu saja! Sihir apimu pasti sangat berguna.",
 "player","SAVE_hutan_elmwood"),
# === SAVE POINT ===
("post_save_hutan_elmwood","NARATOR","Kamu menyentuh Titik Simpan. Perjalanan berlanjut ke Kota Karveth...",None,"s10"),
# ═══════════ MONSTER SERIGALA ═══════════
("s10","NARATOR",
 "Di jalan menuju kota, Serigala Besi menghadang rombongan dengan auman yang mengguncang tanah.",
 None,"BATTLE_wolf"),
("post_wolf","ELARA",
 "Wah, Serigala Besi! Lucu juga ya kalau sudah dijinakkan~",
 "ally_a","s11"),
("s11","NARATOR",
 "Serigala Besi bergabung! Party monster: [Slime Kristal, Serigala Besi].",
 None,"s12"),
# ═══════════ PERTEMUAN BRATH (ALLY B) ═══════════
("s12","NARATOR",
 "Di gerbang Kota Karveth, seorang ksatria bertubuh besar menghalangi jalan dengan pedang terhunus.",
 None,"s13"),
("s13","BRATH",
 "BERHENTI. Tidak ada yang masuk tanpa mengalahkanku lebih dulu. Aku Brath, Penjaga Gerbang.",
 "ally_b","s14"),
("s14","ELARA",
 "Arion... mau kita lawan dia? Atau kita cari jalan lain?",
 "ally_a","CHOICE_brath"),
# === CHOICE: tantang brath atau hindari ===
# CHOICE_brath handled specially in code
("choice_brath_yes","ARION",
 "Akan kuterima tantanganmu, Brath. Ini pertarungan persahabatan — monster terbaik kita akan bertarung!",
 "player","BATTLE_brath"),
("choice_brath_no","ARION",
 "Maaf, kami tidak punya waktu untuk ini. Ada jalan lain yang harus kami tempuh.",
 "player","SOLO_no_brath"),
# Path: tanpa Brath
("solo_no_brath_1","NARATOR",
 "Tanpa bergabungnya Brath, party hanya terdiri dari Arion dan Elara. Perjalanan berlanjut...",
 None,"s15"),
# Path: dengan Brath
("post_brath","BRATH",
 "... Kau mengalahkanku. Pertama kalinya dalam dua belas tahun. Aku tidak bisa membiarkan ini berlalu begitu saja.",
 "ally_b","s_brath2"),
("s_brath2","BRATH",
 "Aku ikut bersamamu. Bukan karena kawan — tapi karena aku perlu membuktikan kekalahan ini bukan kebetulan.",
 "ally_b","s15"),
("s15","NARATOR",
 "Rombongan tiba di Kota Karveth. Pedagang tua memberikan kabar mengejutkan.",
 None,"s16"),
("s16","PEDAGANG",
 "Untuk menembus Kastil Malachar, kalian butuh setidaknya tiga monster yang sudah terlatih. Golem Batu menjaga gerbang kastil!",
 None,"SAVE_kota_karveth"),
# === SAVE POINT ===
("post_save_kota_karveth","NARATOR","Titik Simpan tersimpan. Menuju Dataran Kelabu...",None,"s17"),
# ═══════════ MONSTER GOLEM ═══════════
("s17","NARATOR",
 "Di Dataran Kelabu, Golem Batu raksasa menghalangi jalan menuju kastil.",
 None,"BATTLE_golem"),
("post_golem","ELARA",
 "YES! Golem ikut kita! Sekarang kita punya tiga monster!",
 "ally_a","s18"),
("s18","NARATOR",
 "Golem Batu bergabung! Party monster: [Slime Kristal, Serigala Besi, Golem Batu].",
 None,"s19"),
# ═══════════ GERBANG KASTIL ═══════════
("s19","NARATOR",
 "Kastil Kegelapan Malachar berdiri di depan mereka. Menara-menaranya mencakar langit merah.",
 None,"s20"),
("s20","ARION",
 "Ini dia. Tidak ada jalan kembali. Apapun yang menunggu di dalam — kita hadapi bersama.",
 "player","s21"),
("s21","ELARA",
 "Jangan khawatir! Selama aku ada, tidak ada yang bisa memadamkan semangat kita!",
 "ally_a","s21b"),
# Brath hanya muncul kalau bergabung — handled in code
("s21b","NARATOR","Rombongan memasuki kastil. Kegelapan menyambut mereka...",None,"BOSS_check"),
# ═══════════ KONFRONTASI MALACHAR ═══════════
("boss_intro1","NARATOR",
 "Di singgasana hitam, sosok berjiwa kegelapan menatap mereka dengan mata menyala.",
 None,"boss_intro2"),
("boss_intro2","MALACHAR",
 "HAHAHA... manusia-manusia kecil datang ke istanaku? Sungguh menggelikan.",
 "king","boss_intro3"),
("boss_intro3","ARION",
 "Malachar! Akhiri kekejamanmu sekarang. Valoria bukan milikmu!",
 "player","boss_intro4"),
("boss_intro4","MALACHAR",
 "Kau... berani sekali. Tapi keberanian tanpa kekuatan hanyalah kebodohan.",
 "king","BATTLE_king"),
# BATTLE MALACHAR — handled specially
# ═══════════ ENDINGS ═══════════
# (handled in code based on flags)
]

# ─────────────────────────────────────────────────────────────────
#  BATTLE TEMPLATES
# ─────────────────────────────────────────────────────────────────
BATTLE_CFG = {
"slime": dict(name="Slime Kristal",    hp=45,  atk=8,  dfn=1,  spk="slime", col=GN,   flee_ok=True,  post="post_slime",  reward="Slime Kristal bergabung ke party monster!"),
"wolf":  dict(name="Serigala Besi",    hp=80,  atk=13, dfn=3,  spk="wolf",  col=OR,   flee_ok=True,  post="post_wolf",   reward="Serigala Besi bergabung ke party monster!"),
"brath": dict(name="BRATH (Persahabatan)",hp=90,atk=11,dfn=5,  spk="ally_b",col=PU,   flee_ok=False, post="post_brath",  reward="Brath bergabung sebagai Ally!"),
"golem": dict(name="Golem Batu",       hp=110, atk=15, dfn=7,  spk="golem", col=LGR,  flee_ok=True,  post="post_golem",  reward="Golem Batu bergabung ke party monster!"),
"king":  dict(name="Raja Iblis MALACHAR",hp=220,atk=22,dfn=9,  spk="king",  col=RD,   flee_ok=False, post="ENDING_dispatch",reward=""),
}

# ─────────────────────────────────────────────────────────────────
#  GAME STATE
# ─────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.reset()
        self.hsave = os.path.exists(SAVE)

    def reset(self):
        self.mode        = "title"   # title|story|battle|choice|save_place|settings|ending
        self.prev_mode   = None
        self.story_id    = "s00"
        self.battle      = None
        self.battle_key  = None
        self.choice_data = None      # {prompt, options:[(label,next_id)], idx}
        self.save_place  = None
        self.ending_id   = None      # which ending
        self.tick        = 0
        self.particles   = []
        self.title_idx   = 0         # 0=mulai,1=lanjut,2=setting,3=keluar
        self.reward_msg  = ""
        self.reward_timer= 0
        # flags
        self.has_elara   = False
        self.has_brath   = False
        self.monsters    = []        # list of monster names
        # entities (recreated on reset)
        self._mk_party()

    def _mk_party(self):
        self.e_arion = Entity("Arion",  130,18,5,"player",CY)
        self.e_elara = Entity("Elara",  110,20,3,"ally_a",YL)
        self.e_brath = Entity("Brath",  150,16,9,"ally_b",PU)
        self.party   = [self.e_arion]

    def _cur_party(self):
        p=[self.e_arion]
        if self.has_elara: p.append(self.e_elara)
        if self.has_brath: p.append(self.e_brath)
        return p

    # ── STORY NAVIGATION ──────────────────────────────────────────
    def _find(self, sid):
        for i,s in enumerate(STORY):
            if s[0]==sid: return i
        return 0

    def goto(self, sid):
        # specials
        if sid.startswith("BATTLE_"):
            self._start_battle(sid[7:])
        elif sid.startswith("SAVE_"):
            loc=sid[5:].replace("_"," ").title()
            self.save_place=SavePlace(loc, lambda:self.goto("post_save_"+sid[5:]))
            self.mode="save_place"
        elif sid=="CHOICE_brath":
            self.choice_data={
                "prompt":"Tantang Brath atau hindari?",
                "options":[("Tantang Brath!","choice_brath_yes"),
                           ("Cari jalan lain","choice_brath_no")],
                "idx":0}
            self.mode="choice"
        elif sid=="SOLO_no_brath":
            self.goto("solo_no_brath_1")
        elif sid=="BOSS_check":
            # inject brath dialog if he's in party
            if self.has_brath:
                self._set_story_by_id("boss_brath_line")
            else:
                self.goto("boss_intro1")
        elif sid=="ENDING_dispatch":
            self._dispatch_ending()
        else:
            idx=self._find(sid)
            if idx>=0:
                self.story_id=STORY[idx][0]
                self.mode="story"
                self._load_story(idx)

    def _load_story(self, idx):
        _,spk,text,port,_=STORY[idx]
        portrait=SPR.get(port) if port else None
        dlg.set(spk,text,portrait)

    def _set_story_by_id(self, sid):
        idx=self._find(sid)
        if idx>=0: self.story_id=sid; self._load_story(idx)

    def _advance(self):
        idx=self._find(self.story_id)
        if idx<0: return
        nxt=STORY[idx][4]
        # update party members based on story progress
        if self.story_id in("s09","post_save_hutan_elmwood") and not self.has_elara:
            self.has_elara=True; self.party=self._cur_party()
        self.goto(nxt)

    # ── BATTLE ────────────────────────────────────────────────────
    def _start_battle(self, key):
        cfg=BATTLE_CFG[key]
        # heal party slightly before boss
        if key=="king":
            for e in self._cur_party():
                e.hp=max(e.hp, e.maxhp//2)
        enemy=Entity(cfg["name"],cfg["hp"],cfg["atk"],cfg["dfn"],cfg["spk"],cfg["col"])
        self.battle=Battle(self._cur_party(), enemy, flee_ok=cfg["flee_ok"])
        self.battle_key=key; self.mode="battle"

    def _after_battle(self, result):
        key=self.battle_key
        cfg=BATTLE_CFG[key]
        if result=="win":
            if key=="slime": self.monsters.append("Slime Kristal")
            elif key=="wolf": self.monsters.append("Serigala Besi")
            elif key=="brath":
                self.has_brath=True; self.party=self._cur_party()
            elif key=="golem": self.monsters.append("Golem Batu")
            self.reward_msg=cfg["reward"]
            self.reward_timer=200
            self._save_progress()
            self.goto(cfg["post"])
        elif result=="lose":
            self.ending_id="ending_lose_battle"
            self.mode="ending"
        else:  # flee
            idx=self._find(self.story_id)
            self.mode="story"
            self._load_story(idx)

    # ── ENDING DISPATCH ───────────────────────────────────────────
    def _dispatch_ending(self):
        # Good ending: has both allies + ≥3 monsters
        allies_ok = self.has_elara and self.has_brath
        monsters_ok = len(self.monsters) >= 3
        if allies_ok and monsters_ok:
            self.ending_id = "ending_good"
        elif not allies_ok and monsters_ok:
            self.ending_id = "ending_no_ally"
        elif allies_ok and not monsters_ok:
            self.ending_id = "ending_no_monster"
        elif not self.has_elara and not self.has_brath:
            self.ending_id = "ending_solo"
        else:
            self.ending_id = "ending_weak"
        self.mode = "ending"

    # ── SAVE / LOAD ───────────────────────────────────────────────
    def _save_progress(self):
        d={"story_id":self.story_id,"has_elara":self.has_elara,
           "has_brath":self.has_brath,"monsters":self.monsters}
        try:
            with open(SAVE,"w") as f: json.dump(d,f)
            self.hsave=True
        except: pass

    def load_progress(self):
        try:
            with open(SAVE) as f: d=json.load(f)
            self.story_id=d.get("story_id","s00")
            self.has_elara=d.get("has_elara",False)
            self.has_brath=d.get("has_brath",False)
            self.monsters=d.get("monsters",[])
            self.party=self._cur_party()
            idx=self._find(self.story_id)
            self.mode="story"; self._load_story(idx)
        except: pass

    # ── PARTICLES ─────────────────────────────────────────────────
    def _spawn_pts(self):
        if random.random()<.3:
            self.particles.append({"x":random.randint(0,W),"y":H+5,
                "vy":random.uniform(-0.6,-0.2),"s":random.randint(1,3),
                "c":random.choice([YL,CY,PU,WH,PK])})
        self.particles=[p for p in self.particles if p["y"]>-10]
        for p in self.particles: p["y"]+=p["vy"]

    def _draw_pts(self,surf):
        for p in self.particles:
            pygame.draw.rect(surf,p["c"],(int(p["x"]),int(p["y"]),p["s"],p["s"]))

    # ── TITLE SCREEN ──────────────────────────────────────────────
    def _draw_title(self, surf):
        surf.fill(TL); self._spawn_pts(); self._draw_pts(surf)
        t=pygame.time.get_ticks()/1000
        # castle silhouette
        for cx2,cy2,w2,h2 in [(400,430,80,160),(310,470,45,90),(490,470,45,90),(230,500,32,65),(570,500,32,65)]:
            pygame.draw.rect(surf,(18,8,32),(cx2-w2//2,cy2,w2,h2))
        for bx2 in range(360,445,18): pygame.draw.rect(surf,(18,8,32),(bx2,425,12,12))
        # moon
        pygame.draw.circle(surf,(255,255,180),(650,80),45)
        pygame.draw.circle(surf,TL,(665,70),38)
        # title
        pulse=int(abs(math.sin(t))*25)
        txt(surf,"DEMON KING",F48,(200+pulse,30+pulse,30),W//2,75,cx=True)
        txt(surf,"QUEST",F48,(230+pulse,60+pulse,30),W//2,133,cx=True)
        txt(surf,"─── Pixel Chronicle ───",F18,PU,W//2,190,cx=True)
        # menu
        has_save=os.path.exists(SAVE)
        menu=[("▶  MULAI BARU",True),("▶  LANJUTKAN",has_save),
              ("▶  PENGATURAN",True),("▶  KELUAR",True)]
        for i,(label,enabled) in enumerate(menu):
            sel=(i==self.title_idx)
            col=YL if (sel and enabled) else (GR if not enabled else LGR)
            bg=(40,28,72) if sel else (18,14,32)
            by=240+i*68
            box(surf,bg,(W//2-185,by,370,52),col if sel else GR,2)
            txt(surf,label,F24,col,W//2,by+13,cx=True)
        txt(surf,"↑↓ Navgasi   Enter Pilih",F10,GR,W//2,H-22,cx=True)

    def _title_input(self,ev):
        if ev.type!=pygame.KEYDOWN: return
        k=ev.key
        if k in(pygame.K_UP,pygame.K_w):   self.title_idx=(self.title_idx-1)%4; sfx.cursor()
        elif k in(pygame.K_DOWN,pygame.K_s):self.title_idx=(self.title_idx+1)%4; sfx.cursor()
        elif k in(pygame.K_RETURN,pygame.K_z):
            sfx.confirm()
            if self.title_idx==0:
                delete_save(); self.reset(); self.goto("s00")
            elif self.title_idx==1:
                if os.path.exists(SAVE): self.load_progress()
            elif self.title_idx==2:
                self.prev_mode="title"; self.mode="settings"
            elif self.title_idx==3:
                pygame.quit(); sys.exit()

    # ── STORY DRAW ────────────────────────────────────────────────
    def _draw_story(self, surf):
        # dynamic bg
        sid=self.story_id
        if any(x in sid for x in ("s19","s20","s21","boss","king","MALACHAR")):
            bg=(18,4,4); gc=(35,8,8)
        elif any(x in sid for x in ("s05","s06","s07","s08","s03","s04","slime")):
            bg=(4,18,8); gc=(8,32,12)
        elif any(x in sid for x in ("s12","s13","s14","brath","karveth")):
            bg=(8,8,22); gc=(15,15,40)
        elif any(x in sid for x in ("golem","s17","s18","kelabu")):
            bg=(16,14,10); gc=(28,24,18)
        else:
            bg=(8,10,22); gc=(16,18,40)
        surf.fill(bg)
        for i in range(0,W,32): pygame.draw.line(surf,gc,(i,0),(i,H),1)
        for j in range(0,H,32): pygame.draw.line(surf,gc,(0,j),(W,j),1)
        # current portrait big
        idx=self._find(sid)
        if 0<=idx<len(STORY):
            pkey=STORY[idx][3]
            if pkey and pkey in SPR:
                SPR[pkey].draw(surf,W//2,H//2-80,scale=4.5)
        # party status strip
        self._draw_party_strip(surf)
        # dialog
        dlg.update(); dlg.draw(surf)
        # reward popup
        if self.reward_timer>0:
            self.reward_timer-=1
            a=min(255,self.reward_timer*4)
            s2=pygame.Surface((W,50),pygame.SRCALPHA)
            s2.fill((20,80,20,min(200,a)))
            surf.blit(s2,(0,H-235))
            txt(surf,self.reward_msg,F18,GN,W//2,H-225,cx=True)
        # controls hint
        txt(surf,"Z/Enter: Lanjut",F10,GR,W-110,H-195,shadow=False)

    def _draw_party_strip(self,surf):
        sx=10
        txt(surf,"PARTY:",F10,LGR,sx,12)
        members=self._cur_party()
        for i,e in enumerate(members):
            bx=sx+65+i*145
            box(surf,(15,15,35),(bx,6,138,30),e.col,1)
            e.spr.draw(surf,bx+16,21,scale=0.9)
            txt(surf,e.name,F10,e.col,bx+28,10,shadow=False)
            hp_bar(surf,e.hp,e.maxhp,bx+28,24,96,10)
        # monsters
        if self.monsters:
            mx=W-200
            txt(surf,"MONSTER:",F10,LGR,mx,12)
            for i,m in enumerate(self.monsters[:3]):
                txt(surf,f"[{m[:10]}]",F10,GN,mx,24+i*13,shadow=False)

    # ── CHOICE SCREEN ─────────────────────────────────────────────
    def _draw_choice(self,surf):
        self._draw_story(surf)  # story bg
        cd=self.choice_data
        bw,bh=440,160
        bx,by=W//2-bw//2, H//2-bh//2-20
        box(surf,(10,10,30),(bx,by,bw,bh),YL,3)
        txt(surf,cd["prompt"],F18,YL,W//2,by+14,cx=True)
        for i,(label,_) in enumerate(cd["options"]):
            sel=(i==cd["idx"])
            ob=(bx+20,by+52+i*52,bw-40,44)
            box(surf,(35,30,70) if sel else (15,14,32),ob,YL if sel else GR,2)
            txt(surf,("► " if sel else "  ")+label,F24,YL if sel else LGR,
                bx+40,by+62+i*52)

    def _choice_input(self,ev):
        if ev.type!=pygame.KEYDOWN: return
        cd=self.choice_data; k=ev.key
        if k in(pygame.K_UP,pygame.K_w):   cd["idx"]=(cd["idx"]-1)%len(cd["options"]); sfx.cursor()
        elif k in(pygame.K_DOWN,pygame.K_s):cd["idx"]=(cd["idx"]+1)%len(cd["options"]); sfx.cursor()
        elif k in(pygame.K_RETURN,pygame.K_z):
            sfx.confirm()
            _,nxt=cd["options"][cd["idx"]]
            self.choice_data=None; self.goto(nxt)

    # ── ENDING SCREEN ─────────────────────────────────────────────
    ENDING_DATA = {
"ending_good": {
    "title":"✦ AKHIR SEMPURNA ✦",
    "color":YL,
    "lines":[
        "Malachar jatuh. Cahaya kembali menyelimuti Valoria.",
        "Arion, Elara, dan Brath berdiri bersama di reruntuhan singgasana.",
        "Monster-monster setia mereka meraung kegirangan.",
        "","ELARA:  'Kukatakan kan? Petualangan ini seru banget!'",
        "BRATH:  '...Tidak buruk. Kau tidak seburuk yang kukira, Arion.'",
        "ARION:  'Tanpa kalian semua, ini tidak akan mungkin.'",
        "","Kerajaan Valoria kembali bersinar.",
        "                    ─── TAMAT ───",
    ],
},
"ending_no_ally": {
    "title":"⚔  AKHIR KESEPIAN",
    "color":OR,
    "lines":[
        "Malachar tumbang. Tapi keheningan terasa berat.",
        "Arion berdiri sendirian di antara serpihan kegelapan.",
        "Monster-monster setia mengelilinginya dalam diam.",
        "","ARION:  'Aku menang... tapi kenapa rasanya sepi?'",
        "","Tanpa kawan sejati di sisi, kemenangan terasa hampa.",
        "Valoria bebas, tapi hati Arion tetap bertanya:",
        "'Mungkinkah aku meminta mereka untuk ikut?'",
        "","         ─── Berakhir dengan Kemenangan Sunyi ───",
    ],
},
"ending_no_monster": {
    "title":"⚠  AKHIR PERJUANGAN BERAT",
    "color":RD,
    "lines":[
        "Monster penjaga gerbang terlalu kuat.",
        "Tanpa monster yang cukup, rombongan terpaksa mundur.",
        "","BRATH:  'Kita butuh kekuatan lebih dari ini.'",
        "ELARA:  'Mundur bukan kalah — kita kumpulkan lebih banyak kawan!'",
        "ARION:  'Kau benar. Kita kembali, dan kita persiapkan diri.'",
        "","Malachar masih berdiri. Tapi Arion tidak menyerah.",
        "Perjalanan dimulai kembali dari awal — kali ini dengan lebih banyak monster.",
        "","      ─── Berakhir dengan Harapan yang Tersisa ───",
    ],
},
"ending_solo": {
    "title":"✖  AKHIR JALAN SUNYI",
    "color":LGR,
    "lines":[
        "Arion melangkah ke kastil sendirian.",
        "Tanpa Elara. Tanpa Brath.",
        "Monster-monsternya berjuang keras — tapi jumlahnya tak cukup.",
        "","Gerbang kastil terkunci. Tidak ada yang bisa membobolnya.",
        "","ARION:  'Aku terlalu sombong. Seharusnya aku meminta bantuan.'",
        "","Kadang keberanian saja tidak cukup.",
        "Kebersamaan adalah kunci yang sesungguhnya.",
        "","            ─── Berakhir dengan Pelajaran Berharga ───",
    ],
},
"ending_weak": {
    "title":"⚠  AKHIR KEKUATAN KURANG",
    "color":OR,
    "lines":[
        "Rombongan tiba di hadapan Malachar.",
        "Tapi monster penjaga gerbang menghentikan mereka.",
        "","MALACHAR:  'Hanya segini kekuatan yang kau bawa?'",
        "ELARA:  'Arion... sepertinya kita kurang persiapan...'",
        "","Dengan monster yang tidak cukup, gerbang kastil tak terbuka.",
        "Rombongan terpaksa mundur untuk mengumpulkan lebih banyak kekuatan.",
        "","   ─── Berakhir dengan Kembali Mempersiapkan Diri ───",
    ],
},
"ending_lose_battle": {
    "title":"✖  KEKALAHAN",
    "color":RD,
    "lines":[
        "Kekuatan Malachar terlalu besar.",
        "Arion dan kawan-kawannya jatuh satu per satu.",
        "","MALACHAR:  'Sungguh lemah. Itulah batas kekuatan manusia.'",
        "","Kegelapan kembali menguasai Valoria...",
        "","        ─── Berakhir dengan Kekalahan ───",
        "","        Coba lagi? Tekan R untuk Restart.",
    ],
},
    }

    def _draw_ending(self,surf):
        surf.fill((5,2,12))
        self._spawn_pts(); self._draw_pts(surf)
        ed=self.ENDING_DATA.get(self.ending_id,{})
        title=ed.get("title","TAMAT"); col=ed.get("color",YL)
        lines=ed.get("lines",[])
        t=pygame.time.get_ticks()/1000
        pulse=int(abs(math.sin(t*1.5))*20)
        txt(surf,title,F32,( min(255,col[0]+pulse),
                              min(255,col[1]+pulse),
                              min(255,col[2]+pulse)),W//2,38,cx=True)
        pygame.draw.line(surf,col,(60,82),(W-60,82),2)
        for i,line in enumerate(lines):
            if not line: continue
            c2=YL if line.startswith("ARION") else \
               GN  if line.startswith("ELARA") else \
               PU  if line.startswith("BRATH") else \
               RD  if line.startswith("MALACHAR") else WH
            txt(surf,line,F14,c2,W//2,96+i*28,cx=True)
        # buttons
        by2=H-68
        box(surf,(30,28,60),(W//2-180,by2,160,44),YL,2)
        txt(surf,"R  Restart",F18,YL,W//2-100,by2+12,cx=True)
        box(surf,(20,18,40),(W//2+20,by2,160,44),LGR,2)
        txt(surf,"Q  Keluar",F18,LGR,W//2+100,by2+12,cx=True)

    def _ending_input(self,ev):
        if ev.type!=pygame.KEYDOWN: return
        if ev.key==pygame.K_r:
            delete_save(); self.reset(); self.goto("s00"); sfx.confirm()
        elif ev.key==pygame.K_q:
            pygame.quit(); sys.exit()

    # ── MAIN LOOP ─────────────────────────────────────────────────
    def run(self):
        while True:
            self.tick+=1
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT:
                    pygame.quit(); sys.exit()
                self._handle_event(ev)
            self._draw()
            pygame.display.flip()
            clk.tick(FPS)

    def _handle_event(self, ev):
        m=self.mode
        if m=="title":      self._title_input(ev)
        elif m=="story":    self._story_input(ev)
        elif m=="battle":
            if self.battle: self.battle.input(ev)
            if ev.type==pygame.KEYDOWN and ev.key in(pygame.K_RETURN,pygame.K_z):
                if self.battle and self.battle.state=="result":
                    sfx.confirm(); self._after_battle(self.battle.result)
        elif m=="choice":   self._choice_input(ev)
        elif m=="save_place":
            if self.save_place: self.save_place.input(ev)
        elif m=="settings":
            res=settings.input(ev)
            if res=="back": self.mode=self.prev_mode or "title"
        elif m=="ending":   self._ending_input(ev)

    def _story_input(self,ev):
        if ev.type!=pygame.KEYDOWN: return
        k=ev.key
        if k in(pygame.K_RETURN,pygame.K_z):
            if dlg.done: sfx.confirm(); self._advance()
            else: dlg.skip()
        elif k==pygame.K_ESCAPE:
            self.prev_mode="story"; self.mode="settings"; sfx.cancel()

    def _draw(self):
        m=self.mode
        if m=="title":      self._draw_title(scr)
        elif m=="story":    self._draw_story(scr)
        elif m=="battle":
            if self.battle: self.battle.update(); self.battle.draw(scr)
        elif m=="choice":   self._draw_choice(scr)
        elif m=="save_place":
            self._draw_story(scr)
            if self.save_place: self.save_place.draw(scr)
        elif m=="settings": settings.draw(scr)
        elif m=="ending":   self._draw_ending(scr)

# ─────────────────────────────────────────────────────────────────
#  EXTRA STORY NODES  (injected dynamically)
# ─────────────────────────────────────────────────────────────────
STORY += [
("boss_brath_line","BRATH",
 "Tidak ada kata menyerah. Aku Brath — dan aku tidak mundur sebelum Malachar tumbang!",
 "ally_b","boss_intro1"),
]

def delete_save():
    if os.path.exists(SAVE):
        try: os.remove(SAVE)
        except: pass

# ─────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    g = Game()
    g.run()