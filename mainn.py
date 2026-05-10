"""
DEMON KING QUEST v5
pip install pygame  →  python demon_king_quest_v5.py

KONTROL UMUM:
  WASD / Arrow  = Gerak
  ENTER / Z     = Konfirmasi / Lanjut dialog
  X             = Kembali ke World Map (+ konfirmasi)

BERBURU MONSTER KECIL (hutan):
  WASD          = Gerak player
  J             = Tebas pedang  (area kecil, CD pendek)
  K             = Ultimate pedang  (area besar, CD panjang)
  Sentuh monster = +1 monster (setelah kena sword)

GUA MONSTER BESAR (dungeon labirin bergambar):
  WASD          = Gerak player di dalam dungeon
  J             = Tebas pedang  (jangkauan pendek)
  K             = Ultimate pedang  (area besar, CD panjang)
  M             = Tembak monster kecil sebagai proyektil
  Monster besar ada di TENGAH ruangan, serang saat masuk kamar!
  Kabut perang menghalangi pandangan di luar jangkauan cahaya!

LAWAN RAJA IBLIS (battle box):
  Phase Explore : WASD  cari monster, SPASI = mulai lawan
  Phase Battle  :
    WASD        = Gerak soul (dodge peluru musuh)
    J           = Lempar 1 monster kecil (ammo)
    K           = Ultimate: lempar 5 sekaligus (pakai 5 ammo)
"""

import pygame, sys, json, os, random, math
pygame.init()

SW, SH = 800, 600
FPS    = 60
SAVE_FILE = "save_data.json"

C = {
    "black":(0,0,0),"white":(255,255,255),"red":(220,50,50),"darkred":(140,20,20),
    "green":(60,160,60),"dkgreen":(30,90,30),"blue":(60,100,200),"dkblue":(20,40,120),
    "yellow":(240,200,40),"orange":(220,130,40),"purple":(130,50,180),"dkpurple":(60,20,100),
    "cyan":(80,200,200),"gray":(120,120,120),"dkgray":(60,60,60),"ltgray":(200,200,200),
    "sky":(100,180,240),"ground":(60,140,60),"brown":(120,80,40),"pink":(255,120,150),
    "cream":(255,240,210),"gold":(255,215,0),
    "cave":(22,16,12),"cavewall":(55,40,30),"cavefloor":(42,32,24),"cavetorch":(200,120,40),
    "fog":(8,5,3),"stone":(70,60,50),"darkstone":(35,26,18),
    "roomfloor":(55,42,30),"corridor":(38,28,20),"walledge":(80,58,40),
    "doorcolor":(90,55,25),"doorframe":(110,75,40),
}

screen = pygame.display.set_mode((SW,SH))
pygame.display.set_caption("Demon King Quest v5")
clock  = pygame.time.Clock()

def mkf(s): return pygame.font.SysFont("couriernew",s,bold=True)
F_SM=mkf(14);F_MD=mkf(18);F_LG=mkf(26);F_XL=mkf(36);F_TTL=mkf(52)

def pxr(s,c,r,bw=0,bc=(0,0,0)):
    pygame.draw.rect(s,c,r)
    if bw: pygame.draw.rect(s,bc,r,bw)

def pxt(s,txt,f,c,x,y,center=False,shadow=True):
    if shadow:
        sh=f.render(txt,False,(0,0,0));r=sh.get_rect()
        if center: r.center=(x+2,y+2)
        else: r.topleft=(x+2,y+2)
        s.blit(sh,r)
    t=f.render(txt,False,c);r=t.get_rect()
    if center: r.center=(x,y)
    else: r.topleft=(x,y)
    s.blit(t,r);return r

def hpbar(s,x,y,w,h,cur,mx,col=(80,200,80)):
    pxr(s,C["dkgray"],(x,y,w,h))
    fw=int(w*max(0,cur)/max(1,mx))
    if fw>0: pxr(s,col,(x,y,fw,h))
    pxr(s,C["black"],(x,y,w,h),2)

# ── sprites ───────────────────────────────────────────────────────────────────
def draw_player(s,x,y,frame=0,sword=False,ult=False):
    bx,by=int(x),int(y)
    pxr(s,C["blue"],(bx-8,by-20,16,18))
    pxr(s,C["cream"],(bx-7,by-34,14,14))
    pxr(s,C["black"],(bx-4,by-30,3,3));pxr(s,C["black"],(bx+2,by-30,3,3))
    pxr(s,C["dkblue"],(bx-8,by-2,7,14));pxr(s,C["dkblue"],(bx+1,by-2,7,14))
    pxr(s,C["blue"],(bx-14,by-18,6,12));pxr(s,C["blue"],(bx+8,by-18,6,12))
    if ult:
        col=C["gold"]
        pygame.draw.line(s,col,(bx+8,by-18),(bx+50,by-60),4)
        pygame.draw.line(s,(255,255,180),(bx+8,by-18),(bx+55,by-55),2)
        pygame.draw.circle(s,C["yellow"],(bx+14,by-14),14,0)
        for ang in range(0,360,45):
            r=math.radians(ang+frame*10)
            pygame.draw.line(s,C["yellow"],(bx+14,by-14),
                (int(bx+14+math.cos(r)*22),int(by-14+math.sin(r)*22)),2)
    elif sword:
        pygame.draw.line(s,C["ltgray"],(bx+8,by-18),(bx+36,by-46),3)
        pygame.draw.line(s,C["yellow"],(bx+10,by-16),(bx+16,by-22),3)
    else:
        pygame.draw.line(s,C["gray"],(bx+6,by-34),(bx+12,by-2),2)

def draw_friend_a(s,x,y,frame=0):
    bx,by=int(x),int(y)
    pxr(s,C["orange"],(bx-8,by-20,16,18))
    pxr(s,C["yellow"],(bx-7,by-34,14,14))
    pxr(s,C["black"],(bx-4,by-30,3,3));pxr(s,C["black"],(bx+2,by-30,3,3))
    for i in range(-6,8,4):
        pygame.draw.polygon(s,C["orange"],[(bx+i,by-34),(bx+i+2,by-44),(bx+i+4,by-34)])
    pxr(s,C["brown"],(bx-8,by-2,7,14));pxr(s,C["brown"],(bx+1,by-2,7,14))
    pxr(s,C["orange"],(bx-14,by-18,6,12));pxr(s,C["orange"],(bx+8,by-18,6,12))
    pygame.draw.line(s,C["brown"],(bx-14,by-18),(bx-20,by-50),2)
    pygame.draw.circle(s,C["orange"],(bx-20,by-50),4)

def draw_friend_b(s,x,y,frame=0):
    bx,by=int(x),int(y)
    pxr(s,C["purple"],(bx-8,by-20,16,18))
    pxr(s,C["pink"],(bx-7,by-34,14,14))
    pxr(s,C["black"],(bx-4,by-30,3,3));pxr(s,C["black"],(bx+2,by-30,3,3))
    pygame.draw.polygon(s,C["purple"],[(bx-7,by-34),(bx-12,by-46),(bx-1,by-34)])
    pygame.draw.polygon(s,C["purple"],[(bx+7,by-34),(bx+12,by-46),(bx+1,by-34)])
    pxr(s,C["dkpurple"],(bx-8,by-2,7,14));pxr(s,C["dkpurple"],(bx+1,by-2,7,14))
    pxr(s,C["purple"],(bx-14,by-18,6,12));pxr(s,C["purple"],(bx+8,by-18,6,12))
    pygame.draw.line(s,C["ltgray"],(bx+8,by-18),(bx+18,by-10),2)
    pygame.draw.line(s,C["ltgray"],(bx+8,by-18),(bx+20,by-18),2)

def draw_small_monster(s,x,y,variant=0,scale=1.0):
    bx,by=int(x),int(y)
    r=int(10*scale)
    cols=[(180,60,60),(60,60,180),(60,180,60),(180,120,60),(120,60,180)]
    c=cols[variant%len(cols)]
    pygame.draw.ellipse(s,c,(bx-r,by-int(14*scale),r*2,int(16*scale)))
    pygame.draw.ellipse(s,(0,0,0),(bx-r,by-int(14*scale),r*2,int(16*scale)),1)
    ew=max(2,int(4*scale));eh=max(2,int(4*scale))
    pxr(s,C["white"],(bx-int(5*scale),by-int(12*scale),ew,eh))
    pxr(s,C["white"],(bx+int(2*scale),by-int(12*scale),ew,eh))
    pxr(s,C["black"],(bx-int(4*scale),by-int(11*scale),max(1,int(2*scale)),max(1,int(2*scale))))
    pxr(s,C["black"],(bx+int(3*scale),by-int(11*scale),max(1,int(2*scale)),max(1,int(2*scale))))
    pygame.draw.polygon(s,C["darkred"],[(bx-int(6*scale),by-int(14*scale)),
        (bx-int(8*scale),by-int(20*scale)),(bx-int(3*scale),by-int(14*scale))])
    pygame.draw.polygon(s,C["darkred"],[(bx+int(6*scale),by-int(14*scale)),
        (bx+int(8*scale),by-int(20*scale)),(bx+int(3*scale),by-int(14*scale))])

def draw_big_monster_centered(s, x, y, color=(140,40,40), scale=1.8, frame=0, hp_ratio=1.0):
    """Monster besar di tengah ruangan - ukuran besar dan detail"""
    bx, by = int(x), int(y)
    sc = scale
    # Animasi mengambang
    bob = math.sin(frame * 0.04) * 5
    by = by + int(bob)

    # Aura efek
    pulse = abs(math.sin(frame * 0.06)) * 15
    aura_col = (min(255,color[0]+60), min(255,color[1]+20), min(255,color[2]+20), 60)
    aura_surf = pygame.Surface((int(100*sc), int(100*sc)), pygame.SRCALPHA)
    pygame.draw.ellipse(aura_surf, aura_col,
        (0, 0, int(100*sc), int(80*sc)))
    s.blit(aura_surf, (bx - int(50*sc), by - int(40*sc)))

    # Kaki
    pxr(s, C["dkgray"], (bx-int(22*sc), by, int(18*sc), int(28*sc)), 2, C["black"])
    pxr(s, C["dkgray"], (bx+int(4*sc), by, int(18*sc), int(28*sc)), 2, C["black"])

    # Badan utama
    body_col = color
    pxr(s, body_col, (bx-int(26*sc), by-int(50*sc), int(52*sc), int(52*sc)), 2, C["black"])

    # Kepala
    head_col = (min(255,color[0]+20), min(255,color[1]+10), min(255,color[2]+10))
    pxr(s, head_col, (bx-int(24*sc), by-int(90*sc), int(48*sc), int(42*sc)), 2, C["black"])

    # Tanduk - lebih besar
    pygame.draw.polygon(s, C["darkred"], [
        (bx-int(24*sc), by-int(90*sc)),
        (bx-int(38*sc), by-int(120*sc)),
        (bx-int(8*sc),  by-int(90*sc))])
    pygame.draw.polygon(s, C["darkred"], [
        (bx+int(24*sc), by-int(90*sc)),
        (bx+int(38*sc), by-int(120*sc)),
        (bx+int(8*sc),  by-int(90*sc))])
    # Glow di tanduk
    pygame.draw.polygon(s, C["red"], [
        (bx-int(24*sc), by-int(90*sc)),
        (bx-int(35*sc), by-int(115*sc)),
        (bx-int(10*sc), by-int(90*sc))])
    pygame.draw.polygon(s, C["red"], [
        (bx+int(24*sc), by-int(90*sc)),
        (bx+int(35*sc), by-int(115*sc)),
        (bx+int(10*sc), by-int(90*sc))])

    # Mata bercahaya
    eye_glow = int(abs(math.sin(frame*0.08))*40+180)
    pxr(s, (eye_glow, eye_glow//3, 0), (bx-int(16*sc), by-int(80*sc), int(10*sc), int(10*sc)))
    pxr(s, (eye_glow, eye_glow//3, 0), (bx+int(6*sc), by-int(80*sc), int(10*sc), int(10*sc)))
    pxr(s, C["black"], (bx-int(14*sc), by-int(78*sc), int(6*sc), int(6*sc)))
    pxr(s, C["black"], (bx+int(8*sc), by-int(78*sc), int(6*sc), int(6*sc)))

    # Mulut gerigi
    pxr(s, C["black"], (bx-int(12*sc), by-int(64*sc), int(24*sc), int(8*sc)))
    for i in range(4):
        tx = bx-int(11*sc)+i*int(6*sc)
        pygame.draw.polygon(s, C["white"], [
            (tx, by-int(64*sc)),
            (tx+int(3*sc), by-int(64*sc)),
            (tx+int(1.5*sc), by-int(70*sc))])

    # Lengan
    pxr(s, body_col, (bx-int(50*sc), by-int(48*sc), int(26*sc), int(18*sc)), 2, C["black"])
    pxr(s, body_col, (bx+int(24*sc), by-int(48*sc), int(26*sc), int(18*sc)), 2, C["black"])
    # Cakar
    for ci in range(3):
        pygame.draw.line(s, C["dkgray"],
            (bx-int(26*sc)+ci*int(6*sc), by-int(30*sc)),
            (bx-int(28*sc)+ci*int(6*sc), by-int(22*sc)), int(2*sc))
        pygame.draw.line(s, C["dkgray"],
            (bx+int(24*sc)+ci*int(6*sc), by-int(30*sc)),
            (bx+int(22*sc)+ci*int(6*sc), by-int(22*sc)), int(2*sc))

    # HP bar besar di atas monster
    bar_w = int(120*sc)
    bar_h = 10
    hpbar(s, bx-bar_w//2, by-int(140*sc), bar_w, bar_h, hp_ratio, 1.0, (220,50,50))
    pxt(s, "BOSS", F_SM, C["red"], bx, by-int(155*sc), center=True)

def draw_demon_king(s,x,y,frame=0):
    bx,by=int(x),int(y)
    pulse=abs(math.sin(frame*0.05))*10
    pygame.draw.circle(s,(80,0,80),(bx,by-40),int(60+pulse))
    pygame.draw.polygon(s,C["dkpurple"],[(bx-30,by-50),(bx+30,by-50),(bx+40,by+10),(bx-40,by+10)])
    pxr(s,C["darkred"],(bx-22,by-50,44,50),2,C["black"])
    pxr(s,(160,60,60),(bx-20,by-84,40,36),2,C["black"])
    for i in[-16,-6,4,14]:
        pygame.draw.polygon(s,C["yellow"],[(bx+i,by-84),(bx+i+3,by-98),(bx+i+7,by-84)])
    pxr(s,C["red"],(bx-14,by-76,10,10));pxr(s,C["red"],(bx+4,by-76,10,10))
    pxr(s,(255,200,0),(bx-12,by-74,6,6));pxr(s,(255,200,0),(bx+6,by-74,6,6))
    pxr(s,C["black"],(bx-10,by-60,20,8))
    pxr(s,C["white"],(bx-8,by-60,4,6));pxr(s,C["white"],(bx+4,by-60,4,6))
    pxr(s,C["darkred"],(bx-44,by-48,22,16),2,C["black"])
    pxr(s,C["darkred"],(bx+22,by-48,22,16),2,C["black"])
    pygame.draw.line(s,C["ltgray"],(bx+44,by-48),(bx+70,by-80),4)
    pxr(s,C["dkpurple"],(bx-20,by,18,24),2,C["black"])
    pxr(s,C["dkpurple"],(bx+2,by,18,24),2,C["black"])

# ── particles ──────────────────────────────────────────────────────────────
class Particles:
    def __init__(self): self.p=[]
    def emit(self,x,y,n=10,color=(255,200,0),spd=3,life=40,sz=4,grav=0.1,spread=360):
        for _ in range(n):
            a=math.radians(random.uniform(0,spread)); sp=spd*random.uniform(0.5,1.5)
            col=random.choice(color) if isinstance(color,list) else color
            self.p.append({"x":float(x),"y":float(y),"vx":math.cos(a)*sp,"vy":math.sin(a)*sp,
                           "l":life,"ml":life,"sz":sz,"col":col,"g":grav})
    def update(self):
        for p in self.p[:]:
            p["x"]+=p["vx"];p["y"]+=p["vy"];p["vy"]+=p["g"];p["l"]-=1
            if p["l"]<=0: self.p.remove(p)
    def draw(self,s,ox=0,oy=0):
        for p in self.p:
            a=p["l"]/p["ml"]; sz=max(1,int(p["sz"]*a))
            pygame.draw.circle(s,tuple(min(255,int(c*a)) for c in p["col"]),
                (int(p["x"]+ox),int(p["y"]+oy)),sz)

# ── transition ──────────────────────────────────────────────────────────────
class Transition:
    def __init__(self):
        self._s=pygame.Surface((SW,SH));self._s.fill((0,0,0))
        self.alpha=0;self.state="idle";self.spd=8;self._cb=None
    def fade_to(self,cb,spd=8):
        self.state="out";self.alpha=0;self.spd=spd;self._cb=cb
    def update(self):
        if self.state=="out":
            self.alpha=min(255,self.alpha+self.spd)
            if self.alpha>=255 and self._cb: self._cb();self._cb=None;self.state="in"
        elif self.state=="in":
            self.alpha=max(0,self.alpha-self.spd)
            if self.alpha<=0: self.state="idle"
    def draw(self,s):
        if self.state=="idle" and self.alpha==0: return
        self._s.set_alpha(self.alpha);s.blit(self._s,(0,0))
    @property
    def busy(self): return self.state!="idle"

# ── dialog ──────────────────────────────────────────────────────────────────
class Dialog:
    def __init__(self):
        self.lines=[];self.speaker="";self.visible=False
        self.ci=0;self.timer=0;self.spd=2
        self.choices=[];self.csel=0;self.await_c=False;self.done=False
    def show(self,sp,txt,choices=None):
        self.speaker=sp;self.lines=self._wrap(txt,60)
        self.visible=True;self.ci=0;self.timer=0;self.done=False
        self.choices=choices or[];self.csel=0;self.await_c=bool(choices)
    def _wrap(self,t,w):
        words=t.split();lines=[];cur=""
        for wd in words:
            if len(cur)+len(wd)+1<=w: cur+=("" if not cur else " ")+wd
            else: lines.append(cur);cur=wd
        if cur: lines.append(cur)
        return lines
    def update(self):
        if not self.visible or self.done: return
        self.timer+=1
        if self.timer>=self.spd:
            self.timer=0;self.ci+=1
            tot=sum(len(l) for l in self.lines)+len(self.lines)
            if self.ci>=tot:
                self.ci=tot
                if not self.await_c: self.done=True
    def key(self,k):
        if not self.visible: return None
        tot=sum(len(l) for l in self.lines)+len(self.lines)
        if not self.done and self.ci<tot:
            self.ci=tot
            if not self.await_c: self.done=True
            return None
        if self.await_c:
            if k==pygame.K_UP:   self.csel=(self.csel-1)%len(self.choices)
            if k==pygame.K_DOWN: self.csel=(self.csel+1)%len(self.choices)
            if k in(pygame.K_RETURN,pygame.K_z):
                sel=self.csel;self.visible=False;return sel
        else:
            if k in(pygame.K_RETURN,pygame.K_z,pygame.K_SPACE):
                self.visible=False;return -1
        return None
    def draw(self,s):
        if not self.visible: return
        bx,by,bw,bh=30,SH-180,SW-60,160
        pxr(s,C["black"],(bx-2,by-2,bw+4,bh+4))
        pxr(s,C["dkgray"],(bx,by,bw,bh))
        pxr(s,C["dkpurple"],(bx,by,bw,bh),3)
        if self.speaker:
            tw=F_MD.size(self.speaker)[0]+16
            pxr(s,C["dkgray"],(bx+8,by-22,tw,24))
            pxr(s,C["white"],(bx+8,by-22,tw,24),2)
            pxt(s,self.speaker,F_MD,C["yellow"],bx+16,by-20)
        rendered=0
        for i,line in enumerate(self.lines):
            ch=min(max(0,self.ci-rendered),len(line))
            pxt(s,line[:ch],F_SM,C["white"],bx+16,by+14+i*22,shadow=False)
            rendered+=len(line)+1
        if self.await_c and self.ci>=sum(len(l) for l in self.lines)+len(self.lines):
            for i,ch in enumerate(self.choices):
                cy=by+bh-20-(len(self.choices)-i)*26
                col=C["yellow"] if i==self.csel else C["ltgray"]
                pxt(s,("> " if i==self.csel else "  ")+ch,F_SM,col,bx+30,cy,shadow=False)
        elif self.done and not self.await_c:
            if(pygame.time.get_ticks()//400)%2==0:
                pxt(s,"▼",F_SM,C["yellow"],bx+bw-30,by+bh-28,shadow=False)

# ── back confirm ────────────────────────────────────────────────────────────
class BackConfirm:
    def __init__(self): self.visible=False;self.sel=1;self._cb=None
    def show(self,cb): self.visible=True;self.sel=1;self._cb=cb
    def key(self,k):
        if not self.visible: return False
        if k==pygame.K_LEFT: self.sel=0
        if k==pygame.K_RIGHT: self.sel=1
        if k in(pygame.K_RETURN,pygame.K_z):
            self.visible=False
            if self.sel==0 and self._cb: self._cb()
            return True
        if k==pygame.K_ESCAPE: self.visible=False;return True
        return True
    def draw(self,s):
        if not self.visible: return
        dim=pygame.Surface((SW,SH),pygame.SRCALPHA);dim.fill((0,0,0,160));s.blit(dim,(0,0))
        bx,by,bw,bh=SW//2-220,SH//2-80,440,160
        pxr(s,C["black"],(bx-3,by-3,bw+6,bh+6))
        pxr(s,C["dkgray"],(bx,by,bw,bh));pxr(s,C["orange"],(bx,by,bw,bh),3)
        pxt(s,"Kembali ke World Map?",F_MD,C["yellow"],SW//2,by+18,center=True)
        pxt(s,"Progress di lokasi ini TIDAK tersimpan!",F_SM,C["orange"],SW//2,by+44,center=True)
        for i,(lbl,col) in enumerate(zip(["YA, Kembali","TIDAK, Lanjut"],
                [C["red"] if self.sel==0 else C["gray"],C["green"] if self.sel==1 else C["gray"]])):
            bxb=bx+30+i*210;byb=by+90
            pxr(s,col,(bxb,byb,180,36),3,C["black"])
            pxt(s,("> " if i==self.sel else "  ")+lbl,F_SM,C["white"],bxb+90,byb+18,center=True)
        pxt(s,"← → pilih  ENTER konfirmasi",F_SM,C["ltgray"],SW//2,by+bh-18,center=True)

# ── save/load ────────────────────────────────────────────────────────────────
def save_game(st):
    with open(SAVE_FILE,"w") as f: json.dump(st,f)
def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f: return json.load(f)
    return None
def default_state():
    return{"scene":"intro","small_monsters":0,"big_monsters":0,
           "has_friend_a":False,"has_friend_b":False,"defeated_king":False,"flags":{}}

# ════════════════════════════════════════════════════════════════════════════
#  SMALL MONSTER HUNT  – sword-based, touch = capture after sword contact
# ════════════════════════════════════════════════════════════════════════════
class SmallHunt:
    SWORD_R  = 55
    ULT_R    = 110
    SWORD_CD = 18
    ULT_CD   = 120
    PHP_MAX  = 60

    def __init__(self,state):
        self.state=state
        self.px=float(SW//2);self.py=float(SH//2)
        self.frame=0;self.phase="hunt";self.result=None
        self.monsters=self._spawn(30)
        self.sword_cd=0;self.ult_cd=0
        self.sword_anim=0;self.ult_anim=0
        self.shake=0
        self.ax=self.px-50;self.ay=self.py
        self.bx=self.px+50;self.by_=self.py
        self.particles=Particles()
        self.php=self.PHP_MAX
        self.inv=0
        self.enemy_bullets=[]

    def _spawn(self,n):
        ms=[]
        for _ in range(n):
            while True:
                x=float(random.randint(40,SW-40));y=float(random.randint(40,SH-80))
                if math.hypot(x-SW//2,y-SH//2)>80: break
            ms.append({
                "x":x,"y":y,
                "vx":random.uniform(-1,1),"vy":random.uniform(-1,1),
                "variant":random.randint(0,4),"alive":True,"stunned":0,
                "atk_cd":random.randint(60,140),
            })
        return ms

    def handle_key(self,k):
        if self.phase!="hunt": return
        if k==pygame.K_j and self.sword_cd<=0:
            self._slash(self.SWORD_R,dmg=1);self.sword_cd=self.SWORD_CD;self.sword_anim=12
        if k==pygame.K_k and self.ult_cd<=0:
            self._slash(self.ULT_R,dmg=3);self.ult_cd=self.ULT_CD;self.ult_anim=24

    def _slash(self,radius,dmg):
        for m in self.monsters:
            if not m["alive"]: continue
            if math.hypot(m["x"]-self.px,m["y"]-self.py)<=radius:
                m["stunned"]=40
                self.particles.emit(m["x"],m["y"],n=8,
                    color=[(255,200,0),(255,255,100)],spd=3,life=20,sz=4,grav=0)

    def _monster_shoot(self,m):
        dx=self.px-m["x"]; dy=self.py-m["y"]
        d=max(1,math.hypot(dx,dy))
        spd=3.2+random.uniform(-0.4,0.4)
        spread=random.uniform(-0.18,0.18)
        cols=[(220,80,80),(80,80,220),(80,200,80),(200,140,60),(160,80,220)]
        col=cols[m["variant"]%len(cols)]
        self.enemy_bullets.append({
            "x":float(m["x"]),"y":float(m["y"]),
            "vx":(dx/d+spread)*spd,"vy":(dy/d+spread)*spd,
            "r":5,"col":col,"life":70,
        })

    def update(self):
        if self.phase!="hunt": return
        self.frame+=1
        if self.shake>0: self.shake-=1
        if self.inv>0:   self.inv-=1
        if self.sword_cd>0: self.sword_cd-=1
        if self.ult_cd>0:   self.ult_cd-=1
        if self.sword_anim>0: self.sword_anim-=1
        if self.ult_anim>0:   self.ult_anim-=1
        self.particles.update()

        keys=pygame.key.get_pressed()
        spd=3.5
        if keys[pygame.K_LEFT]:  self.px=max(16,self.px-spd)
        if keys[pygame.K_RIGHT]: self.px=min(SW-16,self.px+spd)
        if keys[pygame.K_UP]:    self.py=max(16,self.py-spd)
        if keys[pygame.K_DOWN]:  self.py=min(SH-80,self.py+spd)

        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha:
            self.ax+=(self.px-55-self.ax)*0.12
            self.ay+=(self.py-self.ay)*0.12
        if hb:
            self.bx+=(self.px+55-self.bx)*0.12
            self.by_+=(self.py-self.by_)*0.12

        for m in self.monsters:
            if not m["alive"]: continue
            if m["stunned"]>0:
                m["stunned"]-=1
                if math.hypot(m["x"]-self.px,m["y"]-self.py)<24:
                    m["alive"]=False
                    self.state["small_monsters"]=min(50,self.state["small_monsters"]+1)
                    self.particles.emit(m["x"],m["y"],n=12,
                        color=[(100,220,255),(200,255,200)],spd=4,life=30,sz=5,grav=-0.05)
                    self.shake=4
                    if self.state["small_monsters"]>=50:
                        self.phase="full";self.result="full"
                continue
            m["x"]+=m["vx"];m["y"]+=m["vy"]
            if m["x"]<20 or m["x"]>SW-20: m["vx"]*=-1
            if m["y"]<20 or m["y"]>SH-80: m["vy"]*=-1
            dist=math.hypot(m["x"]-self.px,m["y"]-self.py)
            m["atk_cd"]-=1
            if m["atk_cd"]<=0 and dist<260:
                m["atk_cd"]=random.randint(70,130)
                self._monster_shoot(m)

        for b in self.enemy_bullets[:]:
            b["x"]+=b["vx"]; b["y"]+=b["vy"]; b["life"]-=1
            if b["life"]<=0 or b["x"]<0 or b["x"]>SW or b["y"]<0 or b["y"]>SH:
                self.enemy_bullets.remove(b); continue
            if self.inv<=0 and math.hypot(b["x"]-self.px,b["y"]-self.py)<b["r"]+8:
                self.php-=6; self.inv=30; self.shake=5
                self.particles.emit(self.px,self.py,n=6,
                    color=[(255,80,80),(255,160,0)],spd=2,life=14,sz=3,grav=0)
                self.enemy_bullets.remove(b)
                if self.php<=0:
                    self.php=0; self.phase="lost"; self.result="lost"
                continue

        alive=[m for m in self.monsters if m["alive"]]
        if not alive and self.phase=="hunt":
            self.phase="done";self.result="cleared"

    def draw(self,s):
        ox=random.randint(-3,3) if self.shake else 0
        s.fill(C["dkgreen"])
        for gx in range(0,SW,32): pygame.draw.line(s,(40,110,40),(gx,0),(gx,SH))
        for gy in range(0,SH,32): pygame.draw.line(s,(40,110,40),(0,gy),(SW,gy))

        if self.sword_anim>0:
            pygame.draw.circle(s,(255,220,0),(int(self.px+ox),int(self.py)),self.SWORD_R,2)
        if self.ult_anim>0:
            surf2=pygame.Surface((SW,SH),pygame.SRCALPHA)
            pygame.draw.circle(surf2,(255,200,0,60),(int(self.px+ox),int(self.py)),self.ULT_R)
            s.blit(surf2,(0,0))
            pygame.draw.circle(s,(255,220,80),(int(self.px+ox),int(self.py)),self.ULT_R,3)

        for b in self.enemy_bullets:
            pygame.draw.circle(s,b["col"],(int(b["x"]+ox),int(b["y"])),b["r"])
            pygame.draw.circle(s,C["white"],(int(b["x"]+ox),int(b["y"])),b["r"],1)

        for m in self.monsters:
            if m["alive"]:
                draw_small_monster(s,m["x"]+ox,m["y"],m["variant"])
                if m["stunned"]>0:
                    pygame.draw.circle(s,C["yellow"],(int(m["x"]+ox),int(m["y"]-18)),6,2)

        self.particles.draw(s)

        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha: draw_friend_a(s,self.ax+ox,self.ay,self.frame)
        if hb: draw_friend_b(s,self.bx+ox,self.by_,self.frame)

        if self.inv<=0 or (self.frame//4)%2==0:
            draw_player(s,self.px+ox,self.py,frame=self.frame,
                        sword=self.sword_anim>0,ult=self.ult_anim>0)

        sm=self.state["small_monsters"]
        hpbar(s,10,10,140,14,self.php,self.PHP_MAX,(80,200,80))
        pxt(s,f"HP: {self.php}/{self.PHP_MAX}",F_SM,C["white"],10,28)
        hpbar(s,10,46,180,12,sm,50,(80,180,220))
        pxt(s,f"Tangkap: {sm}/50",F_SM,C["white"],10,62)
        pxt(s,f"[J]=Tebas(CD:{self.sword_cd}) [K]=Ult(CD:{self.ult_cd})",F_SM,C["yellow"],10,78)
        pxt(s,"Dodge peluru! Tebas lalu sentuh monster kuning!",F_SM,C["cyan"],10,94)
        pxt(s,"[X]=Kembali",F_SM,C["orange"],SW-150,10)
        alive_cnt=sum(1 for m in self.monsters if m["alive"])
        pxt(s,f"Sisa: {alive_cnt}",F_SM,C["white"],SW-150,30)

        if self.phase in("done","full","lost"):
            pxr(s,C["black"],(SW//2-210,SH//2-30,420,90))
            if self.result=="full":
                pxt(s,"MONSTER SUDAH CUKUP! (50/50)",F_LG,C["yellow"],SW//2,SH//2,center=True)
                pxt(s,"Kembali ke Map Dunia...",F_MD,C["white"],SW//2,SH//2+44,center=True)
            elif self.result=="lost":
                pxt(s,"KAU PINGSAN! Kembali ke Map...",F_LG,C["red"],SW//2,SH//2,center=True)
                pxt(s,"ENTER lanjut",F_MD,C["white"],SW//2,SH//2+44,center=True)
            else:
                pxt(s,f"Area Bersih! +{sm} monster",F_LG,C["cyan"],SW//2,SH//2,center=True)
                pxt(s,"ENTER lanjut",F_MD,C["white"],SW//2,SH//2+44,center=True)


# ════════════════════════════════════════════════════════════════════════════
#  DUNGEON CAVE v2  – RPG-style top-down dungeon, labirin nyata
#  Setiap ruangan punya monster BESAR di TENGAH, gelap dengan fog of war
# ════════════════════════════════════════════════════════════════════════════

TS = 32  # tile size pixel - lebih kecil untuk dungeon lebih detail

# Tile types
T_WALL    = 0
T_FLOOR   = 1
T_DOOR    = 2
T_ENTRY   = 3
T_CHEST   = 4
T_PILLAR  = 5

class DungeonRoom:
    def __init__(self, x, y, w, h, room_id):
        self.x=x; self.y=y; self.w=w; self.h=h; self.id=room_id
        self.cx = x + w//2; self.cy = y + h//2
        self.monster = None  # satu boss per ruangan
        self.cleared = False
        self.visited = False

class DungeonCave:
    """
    Dungeon labirin bergaya RPG Maker:
    - Setiap ruangan punya satu monster BESAR di tengah
    - Labirin dengan banyak cabang dan koridor
    - Fog of war gelap, cahaya torch sekitar player
    - Monster besar menembak peluru BESAR dan cepat
    - Player bisa dodge dengan WASD, serang J/K/M
    """

    MAP_W = 80   # tiles wide
    MAP_H = 60   # tiles tall
    LIGHT_R = 5.5  # radius cahaya dalam tiles
    SWORD_R  = 70
    ULT_R    = 130
    SWORD_CD = 20
    ULT_CD   = 150
    SHOOT_CD = 25
    PHP_MAX  = 80

    def __init__(self, state):
        self.state = state
        self.frame = 0
        self.shake = 0
        self.result = None
        self.particles = Particles()
        self.shoot_cd = 0
        self.sword_cd = 0
        self.ult_cd   = 0
        self.sword_anim = 0
        self.ult_anim   = 0
        self.projectiles = []
        self.big_killed  = 0
        self.php = self.PHP_MAX
        self.inv = 0

        # fog surfaces cache
        self._fog_surf = pygame.Surface((SW+TS*2, SH+TS*2), pygame.SRCALPHA)

        # generate dungeon
        self.tiles = [[T_WALL]*self.MAP_H for _ in range(self.MAP_W)]
        self.explored = [[False]*self.MAP_H for _ in range(self.MAP_W)]
        self.rooms = []
        self._gen_dungeon()

        # spawn player di entry room (room 0) - tengah ruangan
        r0 = self.rooms[0]
        self.px = float(r0.cx * TS + TS//2)
        self.py = float(r0.cy * TS + TS//2)

        # camera
        self.cam_x = 0.0; self.cam_y = 0.0

        # torch positions untuk dekorasi
        self.torches = self._place_torches()
        self.torch_tick = 0

    # ── dungeon generation ──────────────────────────────────────────────
    def _gen_dungeon(self):
        W, H = self.MAP_W, self.MAP_H

        # Layout ruangan seperti RPG Maker - banyak ruangan terhubung
        # Entry room di kiri tengah, boss rooms di kanan
        room_templates = [
            # (x_tile, y_tile, width_tile, height_tile) - entry room
            (2, H//2-4, 10, 8),           # 0: Entry Hall
            # cabang utama
            (16, H//2-4, 9, 8),           # 1: Hall Tengah
            (29, H//2-4, 8, 8),           # 2: Junction
            # cabang atas
            (16, H//2-16, 8, 8),          # 3: Ruang Atas Kiri
            (28, H//2-18, 9, 9),          # 4: Ruang Atas Kanan
            (40, H//2-18, 8, 8),          # 5: Far Top
            # cabang bawah
            (16, H//2+10, 8, 8),          # 6: Ruang Bawah Kiri
            (28, H//2+12, 9, 9),          # 7: Ruang Bawah Kanan
            (40, H//2+12, 8, 8),          # 8: Far Bottom
            # ruang tengah & boss
            (40, H//2-4, 10, 8),          # 9: Ruang Center
            (54, H//2-6, 11, 12),         # 10: Ruang Besar
            (54, H//2-20, 9, 10),         # 11: Ruang Kiri Boss
            (54, H//2+10, 9, 10),         # 12: Ruang Kanan Boss
            (68, H//2-4, 8, 8),           # 13: Boss Lobby
        ]

        for i, (rx, ry, rw, rh) in enumerate(room_templates):
            rx = max(1, min(W-rw-1, rx))
            ry = max(1, min(H-rh-1, ry))
            room = DungeonRoom(rx, ry, rw, rh, i)
            self.rooms.append(room)
            for x in range(rx, rx+rw):
                for y in range(ry, ry+rh):
                    self.tiles[x][y] = T_FLOOR
            # Tandai entry
            if i == 0:
                self.tiles[room.cx][room.cy] = T_ENTRY

        # Tambahkan pilar di dalam ruangan besar
        for room in self.rooms:
            if room.w >= 9 and room.h >= 9:
                offsets = [(2, 2), (room.w-3, 2), (2, room.h-3), (room.w-3, room.h-3)]
                for ox, oy in offsets:
                    px_ = room.x + ox
                    py_ = room.y + oy
                    if 0 < px_ < W-1 and 0 < py_ < H-1:
                        self.tiles[px_][py_] = T_PILLAR

        # Koneksi antar ruangan dengan koridor
        connections = [
            (0,1),(1,2),(1,3),(3,4),(4,5),(1,6),(6,7),(7,8),
            (2,9),(5,9),(8,9),(9,10),(10,11),(10,12),(10,13)
        ]
        for a_id, b_id in connections:
            if a_id < len(self.rooms) and b_id < len(self.rooms):
                self._connect_rooms(self.rooms[a_id], self.rooms[b_id])

        # Tambah beberapa ruangan kecil tambahan (secret rooms)
        self._add_secret_corridors()

        # Spawn monster boss di setiap ruangan kecuali entry (room 0)
        boss_colors = [
            (160, 40, 40),    # merah
            (40, 40, 160),    # biru
            (40, 140, 40),    # hijau
            (160, 80, 20),    # coklat
            (100, 40, 160),   # ungu
            (160, 40, 100),   # pink
            (100, 100, 20),   # kuning gelap
            (20, 100, 120),   # teal
            (160, 60, 0),     # oranye
            (80, 0, 80),      # magenta
            (0, 80, 40),      # hijau tua
            (120, 0, 0),      # merah tua
            (0, 0, 120),      # biru tua
        ]
        for i, room in enumerate(self.rooms[1:], 1):
            col = boss_colors[(i-1) % len(boss_colors)]
            scale = random.uniform(1.4, 2.0)
            hp_base = int(80 * scale)
            # Boss lobby punya boss paling kuat
            if i == 13:
                scale = 2.2; hp_base = 200
            room.monster = {
                "x": float(room.cx * TS + TS//2),
                "y": float(room.cy * TS + TS//2),
                "color": col,
                "scale": scale,
                "hp": hp_base,
                "maxhp": hp_base,
                "alive": True,
                "stun": 0,
                "atk_cd": random.randint(60, 120),
                "bullets": [],
                "aggro": False,
                "pattern": i % 4,  # pola serangan berbeda
                "atk_phase": 0,
                "variant": (i-1) % 5,
            }

    def _connect_rooms(self, ra, rb):
        """Buat koridor L-shape antara dua ruangan"""
        W, H = self.MAP_W, self.MAP_H
        ax, ay = ra.cx, ra.cy
        bx, by = rb.cx, rb.cy
        # Horizontal dulu
        for x in range(min(ax, bx), max(ax, bx)+1):
            x = max(1, min(W-2, x))
            self.tiles[x][max(1,min(H-2,ay))] = T_FLOOR
            self.tiles[x][max(1,min(H-2,ay+1))] = T_FLOOR
        # Lalu vertical
        for y in range(min(ay, by), max(ay, by)+1):
            y_c = max(1, min(H-2, y))
            self.tiles[max(1,min(W-2,bx))][y_c] = T_FLOOR
            self.tiles[max(1,min(W-2,bx+1))][y_c] = T_FLOOR

    def _add_secret_corridors(self):
        """Tambah koridor lebar untuk nuansa labirin lebih dalam"""
        W, H = self.MAP_W, self.MAP_H
        # Beberapa segmen koridor pendek
        extra = [
            (12, H//2-10, 4, 6),    # koridor kiri atas
            (12, H//2+4,  4, 6),    # koridor kiri bawah
            (24, H//2-2,  5, 4),    # koridor tengah
            (36, H//2-10, 4, 5),
            (36, H//2+6,  4, 5),
            (48, H//2-12, 5, 4),
            (48, H//2+8,  5, 4),
            (62, H//2-4,  4, 8),
        ]
        for rx, ry, rw, rh in extra:
            rx = max(1, min(W-rw-1, rx)); ry = max(1, min(H-rh-1, ry))
            for x in range(rx, rx+rw):
                for y in range(ry, ry+rh):
                    if 0 < x < W-1 and 0 < y < H-1:
                        self.tiles[x][y] = T_FLOOR

    def _place_torches(self):
        """Tempatkan obor di dinding dekat ruangan"""
        torches = []
        for room in self.rooms:
            # Obor di tengah dinding tiap sisi ruangan
            cx_w = (room.cx) * TS + TS//2
            cy_w = (room.cy) * TS + TS//2
            room_w_px = room.w * TS
            room_h_px = room.h * TS
            rx_w = room.x * TS
            ry_w = room.y * TS
            # Atas, bawah, kiri, kanan dinding dalam ruangan
            torches.append((cx_w, ry_w + 4))
            torches.append((cx_w, ry_w + room_h_px - 8))
            torches.append((rx_w + 4, cy_w))
            torches.append((rx_w + room_w_px - 8, cy_w))
        return torches

    # ── tile helpers ────────────────────────────────────────────────────
    def _walkable(self, wx, wy):
        margin = 8
        for dx, dy in [(-margin,-margin),(margin,-margin),(-margin,margin),(margin,margin)]:
            tx = int((wx+dx) // TS); ty = int((wy+dy) // TS)
            if tx < 0 or ty < 0 or tx >= self.MAP_W or ty >= self.MAP_H: return False
            t = self.tiles[tx][ty]
            if t == T_WALL or t == T_PILLAR: return False
        return True

    # ── key handler ──────────────────────────────────────────────────────
    def handle_key(self, k):
        if self.result: return
        if k == pygame.K_j and self.sword_cd <= 0:
            self._sword_attack(self.SWORD_R, 25)
            self.sword_cd = self.SWORD_CD; self.sword_anim = 16
        if k == pygame.K_k and self.ult_cd <= 0:
            self._sword_attack(self.ULT_R, 55)
            self.ult_cd = self.ULT_CD; self.ult_anim = 32
        if k == pygame.K_m and self.shoot_cd <= 0:
            self._shoot_projectile()

    def _sword_attack(self, radius, dmg):
        hit = False
        for room in self.rooms:
            m = room.monster
            if not m or not m["alive"]: continue
            d = math.hypot(m["x"]-self.px, m["y"]-self.py)
            if d <= radius:
                m["hp"] -= dmg; m["stun"] = 25
                self.particles.emit(m["x"], m["y"], n=14,
                    color=[(255,220,0),(255,100,0),(255,50,50)], spd=5, life=28, sz=6, grav=0)
                hit = True
                if m["hp"] <= 0:
                    m["alive"] = False; m["hp"] = 0
                    self._on_monster_die(m, room)
        if hit: self.shake = 7

    def _on_monster_die(self, m, room):
        self.big_killed += 1
        self.state["big_monsters"] = min(5, self.state["big_monsters"]+1)
        room.cleared = True
        self.particles.emit(m["x"], m["y"], n=30,
            color=[(255,200,0),(200,50,50),(100,200,255),(255,255,100)],
            spd=7, life=50, sz=8, grav=-0.08)

    def _shoot_projectile(self):
        ammo = self.state["small_monsters"]
        if ammo <= 0: return
        self.state["small_monsters"] -= 1
        self.shoot_cd = self.SHOOT_CD

        nearest = None; nd = 99999
        for room in self.rooms:
            m = room.monster
            if m and m["alive"]:
                d = math.hypot(m["x"]-self.px, m["y"]-self.py)
                if d < nd: nd = d; nearest = m

        if nearest:
            dx = nearest["x"]-self.px; dy = nearest["y"]-self.py
            d = max(1, math.hypot(dx, dy))
            self.projectiles.append({
                "x": self.px, "y": self.py,
                "vx": dx/d*10, "vy": dy/d*10,
                "variant": random.randint(0,4), "dmg": 28, "r": 9, "life": 90
            })
        else:
            # Tembak ke depan
            self.projectiles.append({
                "x": self.px, "y": self.py,
                "vx": 0, "vy": -10,
                "variant": 0, "dmg": 28, "r": 9, "life": 90
            })
        self.particles.emit(self.px, self.py, n=6,
            color=[(255,180,0),(255,100,50)], spd=3, life=12, sz=4, grav=0)

    # ── update ──────────────────────────────────────────────────────────
    def update(self):
        self.frame += 1
        self.torch_tick = (self.torch_tick + 1) % 20
        if self.shake > 0: self.shake -= 1
        if self.inv > 0: self.inv -= 1
        if self.sword_cd > 0: self.sword_cd -= 1
        if self.ult_cd > 0: self.ult_cd -= 1
        if self.shoot_cd > 0: self.shoot_cd -= 1
        if self.sword_anim > 0: self.sword_anim -= 1
        if self.ult_anim > 0: self.ult_anim -= 1
        self.particles.update()

        if self.result: return

        # Player movement
        keys = pygame.key.get_pressed(); spd = 3.4
        dx = 0.0; dy = 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: dx -= spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]: dy -= spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: dy += spd
        if dx != 0 and dy != 0: dx *= 0.707; dy *= 0.707

        nx = self.px + dx; ny = self.py + dy
        if self._walkable(nx, self.py): self.px = nx
        if self._walkable(self.px, ny): self.py = ny

        # Update explored tiles
        ptx = int(self.px // TS); pty = int(self.py // TS)
        for fx in range(ptx-8, ptx+9):
            for fy in range(pty-8, pty+9):
                if 0 <= fx < self.MAP_W and 0 <= fy < self.MAP_H:
                    if math.hypot(fx-ptx, fy-pty) <= 7:
                        self.explored[fx][fy] = True

        # Camera smooth follow
        target_cx = self.px - SW//2
        target_cy = self.py - SH//2
        self.cam_x += (target_cx - self.cam_x) * 0.15
        self.cam_y += (target_cy - self.cam_y) * 0.15

        # Tandai room visited
        for room in self.rooms:
            if self.explored[room.cx][room.cy]:
                room.visited = True

        # Update monsters
        for room in self.rooms:
            m = room.monster
            if not m or not m["alive"]: continue
            if m["stun"] > 0: m["stun"] -= 1; continue

            dist = math.hypot(m["x"]-self.px, m["y"]-self.py)
            if dist < 200: m["aggro"] = True

            if m["aggro"]:
                # Monster bergerak perlahan ke player (tetap di sekitar tengah ruangan)
                center_x = float(room.cx * TS + TS//2)
                center_y = float(room.cy * TS + TS//2)
                dist_center = math.hypot(m["x"]-center_x, m["y"]-center_y)
                # Tarik ke tengah ruangan jika terlalu jauh
                if dist_center > 60:
                    m["x"] += (center_x - m["x"]) * 0.03
                    m["y"] += (center_y - m["y"]) * 0.03
                else:
                    # Gerakan osilasi mengancam
                    osc = math.sin(self.frame * 0.04 + room.id) * 20
                    m["x"] = center_x + osc
                    m["y"] = center_y + math.cos(self.frame * 0.03 + room.id) * 15

                # Tembak ke player
                m["atk_cd"] -= 1
                if m["atk_cd"] <= 0 and dist < 350:
                    m["atk_cd"] = max(40, int(80/m["scale"]))
                    self._boss_shoot(m, dist)

            # Update peluru boss
            for b in m["bullets"][:]:
                b["x"] += b["vx"]; b["y"] += b["vy"]
                b["life"] -= 1
                if b["life"] <= 0:
                    m["bullets"].remove(b); continue
                tx_ = int(b["x"]//TS); ty_ = int(b["y"]//TS)
                if tx_ < 0 or ty_ < 0 or tx_ >= self.MAP_W or ty_ >= self.MAP_H:
                    m["bullets"].remove(b); continue
                if self.tiles[tx_][ty_] in (T_WALL, T_PILLAR):
                    self.particles.emit(b["x"], b["y"], n=5,
                        color=[(200,100,50),(150,50,50)], spd=2, life=10, sz=3, grav=0)
                    m["bullets"].remove(b); continue
                # Hit player
                if self.inv <= 0 and math.hypot(b["x"]-self.px, b["y"]-self.py) < b["r"] + 10:
                    dmg = b.get("dmg", 12)
                    self.php -= dmg; self.inv = 35; self.shake = 8
                    self.particles.emit(self.px, self.py, n=10,
                        color=[(255,80,80),(255,160,0)], spd=3, life=18, sz=4, grav=0)
                    m["bullets"].remove(b)
                    if self.php <= 0:
                        self.php = 0; self.result = "lose"
                    continue

        # Update player projectiles
        for proj in self.projectiles[:]:
            proj["x"] += proj["vx"]; proj["y"] += proj["vy"]; proj["life"] -= 1
            if proj["life"] <= 0:
                self.projectiles.remove(proj); continue
            tx_ = int(proj["x"]//TS); ty_ = int(proj["y"]//TS)
            if tx_ < 0 or ty_ < 0 or tx_ >= self.MAP_W or ty_ >= self.MAP_H:
                self.projectiles.remove(proj); continue
            if self.tiles[tx_][ty_] in (T_WALL, T_PILLAR):
                self.projectiles.remove(proj); continue
            hit = False
            for room in self.rooms:
                m = room.monster
                if not m or not m["alive"]: continue
                if math.hypot(proj["x"]-m["x"], proj["y"]-m["y"]) < m["scale"]*22+proj["r"]:
                    m["hp"] -= proj["dmg"]; m["stun"] = 18
                    self.particles.emit(m["x"], m["y"], n=10,
                        color=[(255,150,50),(200,50,50)], spd=4, life=20, sz=5, grav=0)
                    hit = True
                    if m["hp"] <= 0:
                        m["alive"] = False; m["hp"] = 0
                        self._on_monster_die(m, room)
                    break
            if hit: self.projectiles.remove(proj)

        # Cek menang
        if self.state["big_monsters"] >= 5:
            self.result = "win"
        elif all(not room.monster or not room.monster["alive"] for room in self.rooms[1:]):
            if self.big_killed > 0:
                self.result = "win"

    def _boss_shoot(self, m, dist):
        """Pola tembak berbeda tiap boss"""
        pattern = m["pattern"]
        bspd = 4.0 + m["scale"] * 1.5
        dmg = int(10 * m["scale"])
        col = tuple(min(255, c+80) for c in m["color"])

        dx = self.px - m["x"]; dy = self.py - m["y"]
        d = max(1, math.hypot(dx, dy))
        base_angle = math.atan2(dy, dx)

        if pattern == 0:
            # Pola: 3 peluru menyebar
            for spread in [-0.25, 0, 0.25]:
                ang = base_angle + spread
                m["bullets"].append({
                    "x": m["x"], "y": m["y"],
                    "vx": math.cos(ang)*bspd, "vy": math.sin(ang)*bspd,
                    "r": 10, "dmg": dmg, "life": 100,
                    "col": col
                })
        elif pattern == 1:
            # Pola: spiral 8 arah
            m["atk_phase"] += 1
            base = math.radians(m["atk_phase"] * 45)
            for i in range(8):
                ang = base + math.radians(i * 45)
                m["bullets"].append({
                    "x": m["x"], "y": m["y"],
                    "vx": math.cos(ang)*bspd*0.8, "vy": math.sin(ang)*bspd*0.8,
                    "r": 9, "dmg": dmg-2, "life": 90,
                    "col": col
                })
        elif pattern == 2:
            # Pola: 5 peluru lurus ke player
            for i in range(5):
                delay_ang = base_angle + random.uniform(-0.15, 0.15)
                spd2 = bspd + random.uniform(-1, 1)
                m["bullets"].append({
                    "x": m["x"], "y": m["y"],
                    "vx": math.cos(delay_ang)*spd2, "vy": math.sin(delay_ang)*spd2,
                    "r": 11, "dmg": dmg+3, "life": 110,
                    "col": col
                })
        else:
            # Pola: ring peluru kecil
            for i in range(12):
                ang = math.radians(i * 30 + self.frame * 2)
                m["bullets"].append({
                    "x": m["x"], "y": m["y"],
                    "vx": math.cos(ang)*bspd*0.6, "vy": math.sin(ang)*bspd*0.6,
                    "r": 7, "dmg": dmg//2, "life": 80,
                    "col": col
                })

    # ── drawing ──────────────────────────────────────────────────────────
    def draw(self, s):
        self._draw_world(s)
        if self.result:
            self._draw_result(s)

    def _draw_world(self, s):
        ox = random.randint(-2,2) if self.shake else 0
        oy = random.randint(-2,2) if self.shake else 0
        cam_x = int(self.cam_x) + ox
        cam_y = int(self.cam_y) + oy

        s.fill(C["cave"])

        # Hitung tile range yang terlihat
        start_tx = max(0, cam_x//TS - 1)
        start_ty = max(0, cam_y//TS - 1)
        end_tx   = min(self.MAP_W, start_tx + SW//TS + 3)
        end_ty   = min(self.MAP_H, start_ty + SH//TS + 3)

        ptx = int(self.px // TS); pty = int(self.py // TS)

        # Gambar tile
        for tx in range(start_tx, end_tx):
            for ty in range(start_ty, end_ty):
                sx = tx*TS - cam_x
                sy = ty*TS - cam_y
                if sx < -TS or sx > SW+TS or sy < -TS or sy > SH+TS: continue

                tile = self.tiles[tx][ty]
                exp  = self.explored[tx][ty]

                if not exp:
                    pxr(s, C["fog"], (sx, sy, TS, TS))
                    continue

                # Gambar tile sesuai tipe
                if tile == T_WALL:
                    self._draw_wall_tile(s, sx, sy, tx, ty)
                elif tile == T_PILLAR:
                    self._draw_pillar_tile(s, sx, sy)
                elif tile in (T_FLOOR, T_ENTRY, T_CHEST):
                    self._draw_floor_tile(s, sx, sy, tx, ty, tile)

        # Gambar obor dekorasi
        tf = math.sin(self.frame * 0.15) * 3
        for (twx, twy) in self.torches:
            tsx = int(twx - cam_x)
            tsy = int(twy - cam_y)
            if -20 < tsx < SW+20 and -20 < tsy < SH+20:
                ttx = int(twx // TS); tty = int(twy // TS)
                if 0 <= ttx < self.MAP_W and 0 <= tty < self.MAP_H and self.explored[ttx][tty]:
                    # Glow obor
                    glow_sz = int(24 + tf)
                    glow = pygame.Surface((glow_sz*2, glow_sz*2), pygame.SRCALPHA)
                    pygame.draw.circle(glow, (180,100,30,50), (glow_sz,glow_sz), glow_sz)
                    s.blit(glow, (tsx-glow_sz, tsy-glow_sz))
                    # Obor stick
                    pxr(s, C["brown"], (tsx-2, tsy, 4, 8))
                    # Api
                    flame_col = (255, int(140+tf*20), 0)
                    pygame.draw.polygon(s, flame_col, [
                        (tsx-3, tsy), (tsx+3, tsy),
                        (tsx+1, tsy-int(8+tf)), (tsx-1, tsy-int(8+tf))
                    ])

        # Gambar monster besar di tengah ruangan
        for room in self.rooms[1:]:
            m = room.monster
            if not m or not m["alive"]: continue
            if not self.explored[room.cx][room.cy]: continue
            mx = int(m["x"] - cam_x)
            my = int(m["y"] - cam_y)
            if -100 < mx < SW+100 and -150 < my < SH+150:
                hp_ratio = m["hp"] / m["maxhp"]
                draw_big_monster_centered(s, mx, my, m["color"], m["scale"], self.frame, hp_ratio)
                if m["stun"] > 0:
                    pxt(s, "★STUN★", F_SM, C["yellow"], mx, my-int(170*m["scale"]),
                        center=True, shadow=True)
            # Gambar peluru boss
            for b in m["bullets"]:
                bsx = int(b["x"] - cam_x)
                bsy = int(b["y"] - cam_y)
                if 0 < bsx < SW and 0 < bsy < SH:
                    r = b["r"]
                    col = b.get("col", (220,60,60))
                    # Bullet dengan glow
                    glow_s = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_s, (*col, 80), (r*2, r*2), r*2)
                    s.blit(glow_s, (bsx-r*2, bsy-r*2))
                    pygame.draw.circle(s, col, (bsx, bsy), r)
                    pygame.draw.circle(s, (255,200,100), (bsx, bsy), r//2)
                    pygame.draw.circle(s, C["white"], (bsx, bsy), r, 1)

        # Gambar player projectiles
        for proj in self.projectiles:
            px_ = int(proj["x"] - cam_x)
            py_ = int(proj["y"] - cam_y)
            if 0 < px_ < SW and 0 < py_ < SH:
                draw_small_monster(s, px_, py_, proj["variant"], 0.8)

        # Gambar particles
        self.particles.draw(s, -cam_x, -cam_y)

        # Gambar teman
        ha = self.state.get("has_friend_a"); hb = self.state.get("has_friend_b")
        if ha: draw_friend_a(s, self.px-cam_x-38, self.py-cam_y, self.frame)
        if hb: draw_friend_b(s, self.px-cam_x+38, self.py-cam_y, self.frame)

        # Gambar player (berkedip saat invincible)
        sx_ = int(self.px - cam_x); sy_ = int(self.py - cam_y)
        if self.inv <= 0 or (self.frame//4) % 2 == 0:
            draw_player(s, sx_, sy_, frame=self.frame,
                       sword=self.sword_anim > 0, ult=self.ult_anim > 0)

        # Sword range visual
        if self.sword_anim > 0:
            pygame.draw.circle(s, (255,220,0), (sx_, sy_), self.SWORD_R, 2)
        if self.ult_anim > 0:
            ult_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
            pygame.draw.circle(ult_surf, (255,200,0,45), (sx_, sy_), self.ULT_R)
            s.blit(ult_surf, (0,0))
            pygame.draw.circle(s, (255,220,80), (sx_, sy_), self.ULT_R, 3)

        # ── FOG OF WAR overlay ──────────────────────────────────────────
        # Buat efek kabut gelap nyata dengan gradient melingkar
        fog_surf = pygame.Surface((SW, SH), pygame.SRCALPHA)
        fog_surf.fill((0, 0, 0, 255))  # Mulai dari gelap total

        # Potong cahaya di sekitar player
        light_radius = int(self.LIGHT_R * TS)
        # Inner bright zone
        for ring in range(light_radius, 0, -4):
            alpha = max(0, int(200 * (1 - ring/light_radius) * (ring/light_radius)**0.4))
            alpha = 255 - alpha
            if alpha < 0: alpha = 0
            pygame.draw.circle(fog_surf, (0,0,0,alpha), (sx_, sy_), ring)

        # Buat tepi gradient lebih halus
        for i in range(12):
            r2 = light_radius - i*6
            if r2 <= 0: break
            a = min(255, int(i * 20))
            pygame.draw.circle(fog_surf, (0,0,0,a), (sx_, sy_), r2)

        # Tambah cahaya obor sekitar
        for (twx, twy) in self.torches:
            tsx2 = int(twx - cam_x); tsy2 = int(twy - cam_y)
            if -80 < tsx2 < SW+80 and -80 < tsy2 < SH+80:
                ttx2 = int(twx // TS); tty2 = int(twy // TS)
                if 0 <= ttx2 < self.MAP_W and 0 <= tty2 < self.MAP_H and self.explored[ttx2][tty2]:
                    torch_r = int(TS * 2.5)
                    for tr in range(torch_r, 0, -6):
                        a2 = max(0, 255 - int(220 * (1-tr/torch_r)**0.5))
                        pygame.draw.circle(fog_surf, (0,0,0,a2), (tsx2, tsy2), tr)

        s.blit(fog_surf, (0,0))

        # ── HUD ─────────────────────────────────────────────────────────
        pxr(s, (10,6,3,220), (0,0,SW,58))
        pxr(s, (50,35,15), (0,58,SW,2))

        bm = self.state["big_monsters"]
        am = self.state["small_monsters"]
        killed = sum(1 for r in self.rooms[1:] if r.monster and not r.monster["alive"])
        total_rooms = len([r for r in self.rooms[1:] if r.monster])

        # HP Player bar
        hpbar(s, 10, 8, 150, 12, self.php, self.PHP_MAX, (80,200,80))
        pxt(s, f"HP: {self.php}/{self.PHP_MAX}", F_SM, C["white"], 10, 24)

        # Progress bar
        hpbar(s, 170, 8, 130, 12, bm, 5, (200,80,80))
        pxt(s, f"Boss: {bm}/5  ({killed}/{total_rooms} ruangan)", F_SM, C["cyan"], 170, 24)

        pxt(s, f"Ammo:{am} [J]Pedang({self.sword_cd}) [K]Ult({self.ult_cd}) [M]Tembak({self.shoot_cd})",
            F_SM, C["yellow"], 10, 42)
        pxt(s, "[X]=Kembali", F_SM, C["orange"], SW-130, 8)

        # Minimap kecil
        self._draw_minimap(s)

        # Indikator ruangan
        current_room = None
        for room in self.rooms:
            if abs(self.px - room.cx*TS) < room.w*TS//2+10 and \
               abs(self.py - room.cy*TS) < room.h*TS//2+10:
                current_room = room
                break
        if current_room and current_room.id > 0:
            m = current_room.monster
            if m and m["alive"]:
                # Boss HP bar besar di atas layar
                bw2 = 300; bh2 = 16
                bx2 = SW//2 - bw2//2; by2 = 62
                pxr(s, (30,10,10), (bx2-2, by2-2, bw2+4, bh2+4))
                hpbar(s, bx2, by2, bw2, bh2, m["hp"], m["maxhp"], (220,40,40))
                pxr(s, (200,50,50), (bx2, by2, bw2, bh2), 2)
                pxt(s, f"BOSS HP: {m['hp']}/{m['maxhp']}", F_SM, C["red"],
                    SW//2, by2+bh2+4, center=True)
            elif current_room.cleared:
                pxt(s, "✓ RUANGAN BERSIH", F_SM, C["green"], SW//2, 66, center=True)

    def _draw_wall_tile(self, s, sx, sy, tx, ty):
        """Gambar dinding dengan tekstur bata gaya RPG"""
        # Warna bata bergradien
        base = C["cavewall"]
        pxr(s, base, (sx, sy, TS, TS))
        # Garis bata horizontal
        brick_y = sy + TS//3
        brick_y2 = sy + 2*TS//3
        pygame.draw.line(s, C["darkstone"], (sx, brick_y), (sx+TS, brick_y), 1)
        pygame.draw.line(s, C["darkstone"], (sx, brick_y2), (sx+TS, brick_y2), 1)
        # Garis bata vertikal (verseting tiap baris)
        mid_x = sx + TS//2 + ((tx+ty)%2) * (TS//4)
        pygame.draw.line(s, C["darkstone"], (mid_x, sy), (mid_x, brick_y), 1)
        pygame.draw.line(s, C["darkstone"],
            (sx + (TS//4 if (tx+ty)%2==0 else 3*TS//4), brick_y),
            (sx + (TS//4 if (tx+ty)%2==0 else 3*TS//4), brick_y2), 1)
        # Shadow tepi bawah dan kanan
        pygame.draw.line(s, C["darkstone"], (sx, sy+TS-1), (sx+TS, sy+TS-1), 2)
        pygame.draw.line(s, C["darkstone"], (sx+TS-1, sy), (sx+TS-1, sy+TS), 2)
        # Highlight tepi atas dan kiri
        pygame.draw.line(s, C["walledge"], (sx, sy), (sx+TS, sy), 1)
        pygame.draw.line(s, C["walledge"], (sx, sy), (sx, sy+TS), 1)

    def _draw_floor_tile(self, s, sx, sy, tx, ty, tile):
        """Gambar lantai dengan tekstur kayu/batu"""
        # Warna lantai dengan variasi subtle
        rng = ((tx*5+ty*11)%7) * 2
        col = (C["roomfloor"][0]+rng, C["roomfloor"][1]+rng//2, C["roomfloor"][2])
        pxr(s, col, (sx, sy, TS, TS))

        # Garis kayu horizontal
        if (ty)%2 == 0:
            pygame.draw.line(s, C["darkstone"], (sx, sy+TS-1), (sx+TS, sy+TS-1), 1)
        # Grain kayu vertikal tipis
        if (tx*3+ty*7)%8 == 0:
            pygame.draw.line(s, C["darkstone"], (sx+TS//3, sy), (sx+TS//3+2, sy+TS), 1)

        if tile == T_ENTRY:
            # Tanda bintang entry
            pxr(s, (50,80,50), (sx+4, sy+4, TS-8, TS-8))
            pxt(s, "◉", F_SM, C["green"], sx+TS//2, sy+TS//2, center=True, shadow=False)
        elif tile == T_CHEST:
            pxr(s, C["brown"], (sx+4, sy+8, TS-8, TS-12))
            pxr(s, C["gold"], (sx+4, sy+8, TS-8, TS-12), 2)

    def _draw_pillar_tile(self, s, sx, sy):
        """Gambar pilar"""
        pxr(s, C["stone"], (sx, sy, TS, TS))
        pxr(s, C["dkgray"], (sx+4, sy+4, TS-8, TS-8))
        pxr(s, C["darkstone"], (sx+4, sy+4, TS-8, TS-8), 2)
        # Detail pilar
        pygame.draw.line(s, C["ltgray"], (sx+TS//2, sy+4), (sx+TS//2, sy+TS-4), 1)

    def _draw_minimap(self, s):
        mm = 2  # pixel per tile
        mmw = self.MAP_W * mm; mmh = self.MAP_H * mm
        mmx = SW - mmw - 6; mmy = SH - mmh - 6

        surf = pygame.Surface((mmw, mmh))
        surf.fill((4,2,1))
        for tx in range(self.MAP_W):
            for ty in range(self.MAP_H):
                if not self.explored[tx][ty]: continue
                t = self.tiles[tx][ty]
                col = (4,2,1) if t == T_WALL else \
                      (55,42,30) if t in (T_FLOOR,T_ENTRY,T_CHEST) else (30,25,20)
                pygame.draw.rect(surf, col, (tx*mm, ty*mm, mm, mm))
        # Monster dots
        for room in self.rooms[1:]:
            if room.monster and room.monster["alive"] and room.visited:
                rx = room.cx * mm; ry = room.cy * mm
                pygame.draw.rect(surf, (220,50,50), (rx, ry, mm+1, mm+1))
        # Player dot
        px2 = int(self.px // TS) * mm
        py2 = int(self.py // TS) * mm
        pygame.draw.rect(surf, (100,220,255), (px2, py2, mm+1, mm+1))

        pxr(s, (15,10,5), (mmx-2, mmy-2, mmw+4, mmh+4))
        s.blit(surf, (mmx, mmy))
        pygame.draw.rect(s, (80,55,30), (mmx-2, mmy-2, mmw+4, mmh+4), 2)
        pxt(s, "PETA", F_SM, C["orange"], mmx+mmw//2, mmy-16, center=True)

    def _draw_result(self, s):
        dim = pygame.Surface((SW,SH), pygame.SRCALPHA); dim.fill((0,0,0,160)); s.blit(dim,(0,0))
        if self.result == "win":
            pxt(s, "SEMUA BOSS TAKLUK!", F_XL, C["yellow"], SW//2, SH//2-30, center=True)
            pxt(s, f"Monster besar: {self.state['big_monsters']}/5", F_MD, C["white"], SW//2, SH//2+20, center=True)
        else:
            pxt(s, "KAU JATUH...", F_XL, C["red"], SW//2, SH//2-20, center=True)
        pxt(s, "ENTER untuk lanjut", F_MD, C["ltgray"], SW//2, SH//2+70, center=True)


# ════════════════════════════════════════════════════════════════════════════
#  BIG MONSTER / BOSS FINAL  – explore + battle-box duel
# ════════════════════════════════════════════════════════════════════════════
class BigBattle:
    def __init__(self,state,is_dk=False):
        self.state=state;self.is_dk=is_dk
        self.phase="explore";self.frame=0
        self.px=0.0;self.pz=5.0
        self.mx=random.uniform(-8,8);self.mz=random.uniform(-20,-8)
        self.found=False
        self.box=pygame.Rect(140,100,SW-280,SH-200)
        self.sx=float(self.box.centerx);self.sy=float(self.box.centery)
        self.mhp_max=350;self.mhp=self.mhp_max
        self.php=100;self.php_max=100
        self.enemy_bullets=[];self.ammo_bullets=[]
        self.atk_timer=0;self.atk_phase=0
        self.bf=0;self.result=None;self.shake=0
        self.turn="enemy";self.turn_timer=0
        self.shoot_cd=0;self.ult_cd=0
        self.sword_anim=0;self.ult_anim=0
        self.particles=Particles()
        self.fax=0.0;self.faz=6.0
        self.fbx=0.0;self.fbz=6.0

    def handle_key(self,k):
        if self.phase=="explore":
            if k==pygame.K_SPACE and self.found: self.phase="battle"
        elif self.phase=="battle":
            if k==pygame.K_j and self.shoot_cd<=0:
                self._fire(1);self.shoot_cd=14;self.sword_anim=12
            if k==pygame.K_k and self.ult_cd<=0:
                self._fire(5);self.ult_cd=100;self.ult_anim=20

    def _fire(self,n):
        ammo=self.state["small_monsters"]
        n=min(n,ammo)
        if n<=0: return
        self.state["small_monsters"]-=n
        for i in range(n):
            spread=(n-1)*14
            angle=-90+(-spread//2+i*(spread//(max(n-1,1)))) if n>1 else -90
            rad=math.radians(angle)
            v=random.randint(0,4)
            self.ammo_bullets.append({"x":self.sx,"y":self.sy-12,
                "vx":math.cos(rad)*9,"vy":math.sin(rad)*9,
                "variant":v,"r":10,"dmg":8 if n==1 else 12})
        self.particles.emit(self.sx,self.sy-10,n=8,
            color=[(255,200,0),(255,100,50)],spd=4,life=16,sz=5,grav=0)

    def update(self):
        self.frame+=1
        if self.phase=="explore": self._upd_ex()
        elif self.phase=="battle": self._upd_bt()

    def _upd_ex(self):
        keys=pygame.key.get_pressed();spd=0.08
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.px-=spd
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.px+=spd
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.pz-=spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.pz+=spd
        self.px=max(-15,min(15,self.px));self.pz=max(-25,min(10,self.pz))
        if abs(self.px-self.mx)<3 and abs(self.pz-self.mz)<3: self.found=True
        self.fax+=(self.px-self.fax)*0.08;self.faz+=(self.pz+1.5-self.faz)*0.08
        self.fbx+=(self.px-self.fbx)*0.08;self.fbz+=(self.pz+2.5-self.fbz)*0.08

    def _proj(self,wx,wz,base_y=400):
        fov=200;rz=wz-(self.pz-2)
        if rz>=-0.1: rz=-0.1
        sc=fov/(-rz)
        return int(SW//2+(wx-self.px)*sc),int(base_y-rz*8),max(0.1,sc)

    def _draw_ex(self,s):
        s.fill(C["sky"])
        pygame.draw.rect(s,C["ground"],(0,SH//2,SW,SH//2))
        pygame.draw.line(s,C["dkgreen"],(0,SH//2),(SW,SH//2),2)
        for tx,tz in[(-5,-8),(-8,-15),(3,-10),(6,-18),(-2,-20),(9,-12)]:
            ex,ey,sc=self._proj(tx,tz)
            if sc<0.01 or not(0<ex<SW and 0<ey<SH): continue
            h=int(80*sc);w=int(24*sc)
            pxr(s,C["brown"],(ex-w//2,ey-h,w,h))
            pygame.draw.ellipse(s,C["dkgreen"],(ex-w,ey-h-int(w*1.2),w*2,int(w*1.4)))
        ex,ey,sc=self._proj(self.mx,self.mz)
        if 0<ex<SW and 0<ey<SH and sc>0.05:
            draw_demon_king(s,ex,ey,self.frame)
            if self.found: pxt(s,"! DITEMUKAN !",F_MD,C["yellow"],ex,ey-90,center=True)
        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha:
            fx,fy,fsc=self._proj(self.fax-1,self.faz)
            if 0<fx<SW and 0<fy<SH: draw_friend_a(s,fx,fy,self.frame)
        if hb:
            fx,fy,fsc=self._proj(self.fbx+1,self.fbz)
            if 0<fx<SW and 0<fy<SH: draw_friend_b(s,fx,fy,self.frame)
        pxr(s,C["red"],(SW//2-6,SH//2+20,12,16))
        pxr(s,C["cream"],(SW//2-5,SH//2+6,10,12))
        pxt(s,"Eksplorasi – Cari RAJA IBLIS",F_SM,C["white"],8,8)
        pxt(s,"WASD=gerak | SPASI=lawan (setelah ditemukan)",F_SM,C["ltgray"],8,28)
        pxt(s,"[X]=Kembali",F_SM,C["orange"],SW-150,8)
        if self.found: pxt(s,"[SPASI] Mulai Pertarungan!",F_MD,C["yellow"],SW//2,SH-40,center=True)

    def _upd_bt(self):
        if self.result: return
        self.bf+=1
        if self.shake>0: self.shake-=1
        if self.sword_cd>0: self.sword_cd-=1
        if self.ult_cd>0:   self.ult_cd-=1
        if self.sword_anim>0: self.sword_anim-=1
        if self.ult_anim>0:   self.ult_anim-=1
        self.particles.update()

        if self.turn=="enemy":
            keys=pygame.key.get_pressed();spd=3.5
            if keys[pygame.K_LEFT]:  self.sx=max(self.box.left+6,self.sx-spd)
            if keys[pygame.K_RIGHT]: self.sx=min(self.box.right-6,self.sx+spd)
            if keys[pygame.K_UP]:    self.sy=max(self.box.top+6,self.sy-spd)
            if keys[pygame.K_DOWN]:  self.sy=min(self.box.bottom-6,self.sy+spd)
            self.atk_timer+=1
            if self.atk_timer>=28:
                self.atk_timer=0;self._spawn_ebullets()
            for b in self.enemy_bullets[:]:
                b["x"]+=b["vx"];b["y"]+=b["vy"]
                if not self.box.inflate(20,20).collidepoint(b["x"],b["y"]):
                    self.enemy_bullets.remove(b);continue
                if math.hypot(b["x"]-self.sx,b["y"]-self.sy)<b["r"]+5:
                    self.php-=b.get("dmg",10);self.shake=6;self.enemy_bullets.remove(b)
            mcx=SW//2;mcy=120
            for b in self.ammo_bullets[:]:
                b["x"]+=b["vx"];b["y"]+=b["vy"]
                if not pygame.Rect(0,0,SW,SH).collidepoint(b["x"],b["y"]):
                    self.ammo_bullets.remove(b);continue
                if math.hypot(b["x"]-mcx,b["y"]-mcy)<55:
                    self.mhp-=b["dmg"]
                    self.particles.emit(b["x"],b["y"],n=6,
                        color=[(255,150,50),(255,100,100)],spd=3,life=18,sz=4,grav=0)
                    self.ammo_bullets.remove(b)
            if self.bf%300==0:
                self.turn="player_turn";self.turn_timer=100;self.enemy_bullets.clear()
        elif self.turn=="player_turn":
            self.turn_timer-=1
            if self.turn_timer<=0:
                dmg=random.randint(15,30)
                if self.state.get("has_friend_a"): dmg+=random.randint(5,12)
                if self.state.get("has_friend_b"): dmg+=random.randint(5,12)
                dmg+=self.state["big_monsters"]*8
                self.mhp-=dmg;self.turn="enemy";self.bf=0

        if self.php<=0: self.php=0;self.result="lose"
        if self.mhp<=0: self.mhp=0;self.result="win"

    def _spawn_ebullets(self):
        cx,cy=self.box.centerx,self.box.centery
        ap=self.atk_phase%4;self.atk_phase+=1
        for ang in range(0,360,30):
            r=math.radians(ang+self.bf*3)
            self.enemy_bullets.append({"x":float(cx),"y":float(cy),
                "vx":math.cos(r)*4,"vy":math.sin(r)*4,"r":7,"color":C["red"],"dmg":12})
        dx=self.sx-cx;dy=self.sy-cy;d=max(1,math.hypot(dx,dy))
        for off in[-0.2,0,0.2]:
            self.enemy_bullets.append({"x":float(cx),"y":float(cy),
                "vx":(dx/d+off)*5,"vy":(dy/d+off)*5,"r":8,"color":C["purple"],"dmg":14})

    def _draw_bt(self,s):
        s.fill((10,10,20))
        ox=random.randint(-3,3) if self.shake else 0
        pxr(s,C["black"],self.box.inflate(6,6));pxr(s,C["white"],self.box,3)
        mcx=SW//2+ox
        draw_demon_king(s,mcx,120,self.bf)
        hpbar(s,self.box.left,self.box.top-22,self.box.width,14,self.mhp,self.mhp_max,(200,60,60))
        pxt(s,"RAJA IBLIS HP",F_SM,C["white"],self.box.left,self.box.top-38)
        for b in self.enemy_bullets:
            pygame.draw.circle(s,b["color"],(int(b["x"]+ox),int(b["y"])),b["r"])
            pygame.draw.circle(s,C["white"],(int(b["x"]+ox),int(b["y"])),b["r"],1)
        for b in self.ammo_bullets:
            draw_small_monster(s,b["x"]+ox,b["y"],b["variant"])
        self.particles.draw(s)
        if self.ult_anim>0:
            surf2=pygame.Surface((SW,SH),pygame.SRCALPHA)
            pygame.draw.circle(surf2,(255,200,0,60),(int(self.sx+ox),int(self.sy)),50)
            s.blit(surf2,(0,0))
        pygame.draw.polygon(s,C["red"],
            [(int(self.sx+ox),int(self.sy-8)),
             (int(self.sx-7+ox),int(self.sy+6)),
             (int(self.sx+7+ox),int(self.sy+6))])
        draw_player(s,self.sx+ox,self.sy+30,sword=self.sword_anim>0,ult=self.ult_anim>0,frame=self.bf)
        ha=self.state.get("has_friend_a");hb=self.state.get("has_friend_b")
        if ha: draw_friend_a(s,self.box.left-30,self.box.centery,self.bf)
        if hb: draw_friend_b(s,self.box.right+30,self.box.centery,self.bf)
        hpbar(s,self.box.left,self.box.bottom+8,self.box.width,14,self.php,self.php_max,(80,200,80))
        pxt(s,f"HP: {self.php}",F_SM,C["white"],self.box.left,self.box.bottom+26)
        ammo=self.state["small_monsters"]
        pxt(s,f"Ammo (monster kecil): {ammo}",F_SM,C["cyan"],self.box.left,self.box.bottom+46)
        pxt(s,f"[J]=Lempar 1 (CD:{self.shoot_cd})  [K]=Lempar 5 (CD:{self.ult_cd})",
            F_SM,C["yellow"],self.box.left,self.box.bottom+62)
        if self.turn=="player_turn":
            pxt(s,f"GILIRAN SERANG! ({self.turn_timer//60+1}s)",F_MD,C["yellow"],SW//2,self.box.bottom+82,center=True)
        else:
            pxt(s,"DODGE! WASD=gerak | J/K=lempar monster",F_SM,C["ltgray"],SW//2,self.box.bottom+82,center=True)
        pxt(s,"[X]=Kembali",F_SM,C["orange"],SW-150,10)
        if ammo<=0 and self.turn=="enemy":
            pxt(s,"AMMO HABIS! Survive sampai giliran auto-attack",F_SM,C["red"],SW//2,self.box.top-56,center=True)
        if self.result:
            msg="MENANG!" if self.result=="win" else "KALAH..."
            col=C["yellow"] if self.result=="win" else C["red"]
            pxr(s,C["black"],(SW//2-120,SH//2-30,240,60))
            pxt(s,msg,F_XL,col,SW//2,SH//2,center=True)
            pxt(s,"ENTER lanjut",F_SM,C["white"],SW//2,SH//2+40,center=True)

    def draw(self,s):
        if self.phase=="explore": self._draw_ex(s)
        else: self._draw_bt(s)


# ════════════════════════════════════════════════════════════════════════════
#  MAIN GAME
# ════════════════════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        self.state=default_state()
        self.dialog=Dialog()
        self.back_confirm=BackConfirm()
        self.sub=None
        self.particles=Particles()
        self.transition=Transition()
        self.menu_sel=0;self.prologue_step=0
        self.wx=float(SW//2);self.wy=float(SH//2);self.wframe=0
        self._near=None
        self._smap={
            "intro":self._s_intro,"title":self._s_title,"prologue":self._s_prologue,
            "world":self._s_world,"meet_a":self._s_meet_a,
            "meet_b_setup":self._s_meet_b_setup,"meet_b":self._s_meet_b,
            "hunting_small":self._s_hunt_sm,"hunting_big":self._s_hunt_big,
            "pre_final":self._s_pre_final,"final_battle":self._s_final,
            "ending_good":self._s_end_good,"ending_no_friends":self._s_end_nof,
            "ending_weak":self._s_end_weak,"ending_lost":self._s_end_lost,
        }

    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit();sys.exit()
                if ev.type==pygame.KEYDOWN and not self.transition.busy:
                    self._key(ev.key)
            screen.fill(C["black"])
            fn=self._smap.get(self.state["scene"],self._s_world);fn()
            self.particles.update();self.particles.draw(screen)
            self.transition.update();self.transition.draw(screen)
            self.back_confirm.draw(screen)
            pygame.display.flip();clock.tick(FPS)

    def _key(self,k):
        if self.back_confirm.visible: self.back_confirm.key(k);return
        scene=self.state["scene"]
        if k==pygame.K_x and scene not in("title","intro","world","prologue",
            "ending_good","ending_no_friends","ending_weak","ending_lost"):
            self.back_confirm.show(self._go_world);return

        if self.sub:
            if isinstance(self.sub,SmallHunt):
                self.sub.handle_key(k)
                if self.sub.phase in("done","full"):
                    if k in(pygame.K_RETURN,pygame.K_z) or self.sub.result=="full":
                        self._end_sub()
                elif self.sub.phase == "lost":
                    if k in(pygame.K_RETURN,pygame.K_z):
                        self._end_sub()
            elif isinstance(self.sub,DungeonCave):
                self.sub.handle_key(k)
                if self.sub.result and k in(pygame.K_RETURN,pygame.K_z):
                    self._end_sub()
            elif isinstance(self.sub,BigBattle):
                self.sub.handle_key(k)
                if self.sub.result and k in(pygame.K_RETURN,pygame.K_z):
                    self._end_sub()
            return

        if self.dialog.visible:
            res=self.dialog.key(k)
            if res is not None: self._on_dlg(res)
            return

        if scene=="title":
            if k in(pygame.K_UP,pygame.K_w):   self.menu_sel=(self.menu_sel-1)%3
            if k in(pygame.K_DOWN,pygame.K_s):  self.menu_sel=(self.menu_sel+1)%3
            if k in(pygame.K_RETURN,pygame.K_z):
                if self.menu_sel==0:
                    self.state=default_state();self.prologue_step=0
                    self.state["scene"]="prologue";self._dlg_prolog()
                elif self.menu_sel==1:
                    sv=load_game()
                    if sv: self.state=sv
                    else: self.dialog.show("System","Tidak ada save ditemukan!")
                elif self.menu_sel==2: pygame.quit();sys.exit()
        elif scene=="world":
            if k==pygame.K_s: save_game(self.state);self.dialog.show("System","✓ Game tersimpan!")
            elif k in(pygame.K_RETURN,pygame.K_z):
                if self._near: self._enter(self._near[7])
                else: self._wadv()
        elif scene in("hunting_small","hunting_big","final_battle"):
            if k in(pygame.K_RETURN,pygame.K_z) and not self.sub: self._start(scene)

    def _go_world(self):
        self.sub=None
        def do(): self.state["scene"]="world"
        self.transition.fade_to(do,8)

    def _on_dlg(self,res):
        sc=self.state["scene"]
        if sc=="intro": self.state["scene"]="title"
        elif sc=="prologue":
            if self.prologue_step==0:
                self.prologue_step=1
                self.dialog.show("Kael","Aku akan mengumpulkan teman-teman dan monster-monster terkuat! Perjalanan menuju kastil Raja Iblis dimulai!")
            else: self.transition.fade_to(lambda:self.state.update({"scene":"world"}),6)
        elif sc=="meet_a":
            if not self.state["flags"].get("a_cd"):
                self.state["flags"]["a_cd"]=True
                if res==0: self.state["has_friend_a"]=True;self.dialog.show("A","Sip! Petualangan seru. Ayo!")
                else: self.dialog.show("A","Oh... baiklah. Hati-hati.")
            else: self.state["scene"]="world"
        elif sc=="meet_b_setup":
            if res==0: self.state["flags"]["b_bs"]=True;self.sub=SmallHunt(self.state)
            else: self.state["scene"]="world"
        elif sc=="meet_b":
            if not self.state["flags"].get("b_cd"):
                self.state["flags"]["b_cd"]=True
                if res==0: self.state["has_friend_b"]=True;self.dialog.show("B","Haah... baiklah. Tapi jangan harap aku jadi lemah!")
                else: self.dialog.show("B","Hmph. Aku tidak mau ikut orang lemah.")
            else: self.state["scene"]="world"
        elif sc=="pre_final": self._chk_final()
        elif sc in("ending_good","ending_no_friends","ending_weak","ending_lost"):
            self.state["scene"]="title";save_game(self.state)
        if res==-1 and self.state["flags"].get("_bw"):
            self.state["flags"].pop("_bw")
            self.transition.fade_to(lambda:self.state.update({"scene":"world"}),8)

    def _end_sub(self):
        sc=self.sub;self.sub=None;scene=self.state["scene"]
        if isinstance(sc,SmallHunt):
            sm=self.state["small_monsters"]
            if scene=="meet_b_setup":
                self.state["scene"]="meet_b";self.state["flags"]["b_cd"]=False;self._dlg()
            elif scene=="hunting_small":
                if sc.result=="full":
                    self.dialog.show("System","Monster sudah 50/50! Cukup untuk melawan Raja Iblis. Kembali ke Map.")
                elif sc.result=="lost":
                    self.dialog.show("System",f"Kau pingsan! Tetap semangat! Total: {sm}/50")
                else:
                    self.dialog.show("System",f"Area bersih! Total: {sm}/50")
                self.state["flags"]["_bw"]=True
        elif isinstance(sc,DungeonCave):
            bm=self.state["big_monsters"]
            if sc.result=="win":
                self.dialog.show("System",
                    f"Dungeon bersih! Monster besar: {bm}/5"+
                    (" — SEMUA TERKUMPUL!" if bm>=5 else ""))
            else:
                self.dialog.show("System","Kembali dari dungeon.")
            self.state["flags"]["_bw"]=True
        elif isinstance(sc,BigBattle):
            if scene=="final_battle":
                if sc.result=="win":
                    self.state["defeated_king"]=True
                    for _ in range(6):
                        self.particles.emit(random.randint(100,700),random.randint(100,400),
                            n=30,color=[(255,200,0),(255,100,100),(100,200,255)],
                            spd=6,life=90,sz=7,grav=-0.05)
                    def gg(): self.state["scene"]="ending_good";save_game(self.state);self._dlg()
                    self.transition.fade_to(gg,5)
                else:
                    def gl(): self.state["scene"]="ending_lost";save_game(self.state);self._dlg()
                    self.transition.fade_to(gl,5)

    def _start(self,scene):
        if scene=="hunting_small": self.sub=SmallHunt(self.state)
        elif scene=="hunting_big":  self.sub=DungeonCave(self.state)
        elif scene=="final_battle": self.sub=BigBattle(self.state,True)

    def _wadv(self):
        fl=self.state["flags"];sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        if not fl.get("met_a"): fl["met_a"]=True;fl["a_cd"]=False;self.state["scene"]="meet_a";self._dlg()
        elif not fl.get("met_b"): fl["met_b"]=True;self.state["scene"]="meet_b_setup";self._dlg()
        elif sm<50: self.state["scene"]="hunting_small";self._dlg()
        elif bm<5:  self.state["scene"]="hunting_big";self._dlg()
        else: self.state["scene"]="pre_final";self._dlg()

    def _enter(self,skey):
        fl=self.state["flags"];sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        if skey=="meet_a":
            if not fl.get("met_a"): fl["met_a"]=True;fl["a_cd"]=False;self.state["scene"]="meet_a";self._dlg()
            else: self.dialog.show("A","Hei! Tetap semangat!" if self.state["has_friend_a"] else "Kamu tidak mengajakku...")
        elif skey=="meet_b_setup":
            if not fl.get("met_b"): fl["met_b"]=True;self.state["scene"]="meet_b_setup";self._dlg()
            else: self.dialog.show("B","Sudah siap?" if self.state["has_friend_b"] else "Kau tidak layak.")
        elif skey=="hunting_small": self.state["scene"]="hunting_small";self._dlg()
        elif skey=="hunting_big":   self.state["scene"]="hunting_big";self._dlg()
        elif skey=="pre_final":
            if sm<50 or bm<5: self.dialog.show("Kael",f"Belum siap! {sm}/50 kecil, {bm}/5 besar.")
            else: self.state["scene"]="pre_final";self._dlg()

    def _chk_final(self):
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        if not ha and not hb: self.state["scene"]="ending_no_friends"
        elif sm<50 or bm<5:   self.state["scene"]="ending_weak"
        else:                  self.state["scene"]="final_battle"
        self._dlg()

    def _dlg_prolog(self):
        self.dialog.show("Narator","Di dunia Arathos, Raja Iblis Malachar telah bangkit kembali. Seorang pemuda bernama Kael memutuskan untuk menghentikannya. Ia tahu ia butuh teman-teman terbaik dan monster-monster kuat di sisinya.")

    def _dlg(self):
        sc=self.state["scene"]
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        D={
            "meet_a":("Kael","Itu A! Petualang terkenal yang selalu ingin mencoba hal baru. Mungkin dia mau ikut?",["Ajak A bergabung","Lewati saja"]),
            "meet_b_setup":("Narator","Di arena kota ada B – monster tamer terkuat. Kalahkan dia dalam pertandingan untuk mengajaknya!",["Mulai pertandingan!","Nanti saja"]),
            "meet_b":("B","Hmph... Kau cukup kuat. Mengapa kau melawanku?",["Ajak B – kalahkan Raja Iblis!","Tidak perlu"]),
            "hunting_small":("Narator",f"Hutan monster kecil! Saat ini: {sm}/50. Tebas dengan pedang [J/K] lalu sentuh monster kuning untuk menangkapnya! [ENTER] Mulai | [X] Kembali"),
            "hunting_big":("Narator",f"Gua Kastil Monster Besar! Saat ini: {bm}/5. Jelajahi dungeon labirin gelap, setiap ruangan ada BOSS di tengah! WASD=gerak J=Pedang K=Ultimate M=Tembak monster. [ENTER] Masuk | [X] Kembali"),
            "pre_final":("Kael",f"A: {'Bersama' if ha else 'Tidak ada'}. B: {'Bersama' if hb else 'Tidak ada'}. Monster: {sm}/50 kecil, {bm}/5 besar. Kastil Raja Iblis ada di depan!"),
            "final_battle":("Narator","RAJA IBLIS MALACHAR! Di battle: dodge peluru, lempar monster kecil [J/K] untuk menyerang! [ENTER] Mulai | [X] Kembali"),
            "ending_good":("Narator","LUAR BIASA! Raja Iblis Malachar jatuh! Dunia Arathos damai. Kael dan sahabat-sahabatnya menjadi pahlawan legendaris! ★ ENDING TERBAIK ★"),
            "ending_no_friends":("Narator","Kael berdiri sendiri. Tanpa teman ia memutuskan mundur. ENDING: Sendirian..."),
            "ending_weak":("Narator",f"Monster tidak cukup! ({sm}/50 kecil, {bm}/5 besar). Raja Iblis terlalu kuat. ENDING: Berlatih lebih keras..."),
            "ending_lost":("Narator","Raja Iblis terlalu kuat! Kael mundur. Semangat tidak padam. ENDING: Perjuangan belum berakhir!"),
        }
        if sc in D:
            d=D[sc];self.dialog.show(d[0],d[1],d[2] if len(d)>2 else None)

    # ── scene renderers ──────────────────────────────────────────────────
    def _s_intro(self):
        screen.fill(C["black"])
        pxt(screen,"DEMON KING QUEST v5",F_TTL,C["red"],SW//2,SH//2-40,center=True)
        pxt(screen,"Tekan ENTER untuk mulai",F_MD,C["white"],SW//2,SH//2+40,center=True)
        if not self.dialog.visible: self.dialog.show("","Selamat datang di Demon King Quest v5!")
        self.dialog.update();self.dialog.draw(screen)

    def _s_title(self):
        screen.fill((10,5,20))
        random.seed(42)
        for _ in range(80): pygame.draw.circle(screen,C["white"],(random.randint(0,SW),random.randint(0,SH//2)),random.randint(1,2))
        random.seed()
        pxt(screen,"DEMON KING QUEST",F_TTL,C["red"],SW//2,80,center=True)
        pxt(screen,"～ Quest of Legends v5 ～",F_MD,C["orange"],SW//2,130,center=True)
        draw_player(screen,SW//2-120,300);draw_friend_a(screen,SW//2,300);draw_friend_b(screen,SW//2+120,300)
        draw_demon_king(screen,SW//2,490)
        for i,lbl in enumerate(["New Game","Load Game","Quit"]):
            col=C["yellow"] if i==self.menu_sel else C["ltgray"]
            pxt(screen,("> " if i==self.menu_sel else "  ")+lbl,F_LG,col,SW//2,360+i*42,center=True)
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        pxt(screen,f"Save: SM={sm}/50 BM={bm}/5 A={'v'if ha else'x'} B={'v'if hb else'x'}",F_SM,C["gray"],SW//2,SH-30,center=True)
        self.dialog.update();self.dialog.draw(screen)

    def _s_prologue(self):
        screen.fill((20,10,40))
        for i in range(5): pygame.draw.line(screen,(40,20,60),(0,80+i*60),(SW,80+i*60),2)
        pxt(screen,"PROLOG",F_XL,C["yellow"],SW//2,30,center=True)
        draw_player(screen,SW//2,SH//2-40)
        if not self.dialog.visible and self.prologue_step==0: self._dlg_prolog()
        self.dialog.update();self.dialog.draw(screen)

    def _s_world(self):
        self.wframe+=1
        keys=pygame.key.get_pressed();spd=3.0
        if not self.dialog.visible and not self.back_confirm.visible:
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.wx=max(20,self.wx-spd)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.wx=min(SW-20,self.wx+spd)
            if keys[pygame.K_UP]    or keys[pygame.K_w]: self.wy=max(50,self.wy-spd)
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.wy=min(SH-50,self.wy+spd)
        screen.fill(C["dkgreen"])
        for gx in range(0,SW,40): pygame.draw.line(screen,(40,110,40),(gx,0),(gx,SH))
        for gy in range(0,SH,40): pygame.draw.line(screen,(40,110,40),(0,gy),(SW,gy))
        sm=self.state["small_monsters"];bm=self.state["big_monsters"]
        ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
        locs=[
            (120,100,80,60,C["brown"],"Desa A","Temui Teman A","meet_a"),
            (580,120,80,60,C["purple"],"Arena B","Temui Teman B","meet_b_setup"),
            (200,380,90,60,C["darkred"],"Hutan Monster",f"Berburu Kecil {sm}/50","hunting_small"),
            (560,380,90,60,C["dkgray"],"Gua Monster",f"Dungeon Besar {bm}/5","hunting_big"),
            (SW//2,80,100,55,(80,0,80),"Kastil Iblis","Pertarungan Final","pre_final"),
        ]
        path=[(120,130),(200,410),(560,410),(580,150),(SW//2,107)]
        for i in range(len(path)-1): pygame.draw.line(screen,(80,150,80),path[i],path[i+1],6)
        near=None
        for lx,ly,lw,lh,col,label,hint,skey in locs:
            rect=pygame.Rect(lx-lw//2,ly-lh//2,lw,lh)
            dist=math.hypot(self.wx-lx,self.wy-ly)
            if dist<70:
                near=(lx,ly,lw,lh,col,label,hint,skey)
                pulse=int(abs(math.sin(pygame.time.get_ticks()/300))*6)
                pygame.draw.rect(screen,C["yellow"],rect.inflate(pulse*2,pulse*2),3)
            pxr(screen,col,rect,2,C["black"])
            pxr(screen,tuple(min(c+40,255) for c in col),rect.inflate(-20,-20))
            pxt(screen,label,F_SM,C["white"],lx,ly-lh//2-16,center=True)
        if ha: draw_friend_a(screen,self.wx-40,self.wy+4,self.wframe)
        if hb: draw_friend_b(screen,self.wx+40,self.wy+4,self.wframe)
        draw_player(screen,self.wx,self.wy,frame=self.wframe)
        if near and not self.dialog.visible:
            lx,ly,lw,lh,col,label,hint,skey=near
            bw2=310;bh2=44
            pxr(screen,C["black"],(SW//2-bw2//2,SH-100,bw2,bh2))
            pxr(screen,col,(SW//2-bw2//2,SH-100,bw2,bh2),3)
            pxt(screen,f"[ENTER] {hint}",F_SM,C["yellow"],SW//2,SH-78,center=True)
        pxt(screen,"PETA DUNIA",F_LG,C["yellow"],SW//2,14,center=True)
        pxt(screen,f"Monster: {sm}/50 kecil | {bm}/5 besar",F_SM,C["white"],8,8)
        pxt(screen,f"Teman: {'A✓'if ha else'A✗'} {'B✓'if hb else'B✗'}",F_SM,C["cyan"],8,28)
        pxt(screen,"WASD=gerak  ENTER=masuk lokasi  S=simpan",F_SM,C["yellow"],8,SH-28)
        self._near=near;self.dialog.update();self.dialog.draw(screen)

    def _s_meet_a(self):
        screen.fill((80,120,60));pygame.draw.rect(screen,C["dkgreen"],(0,SH-100,SW,100))
        draw_player(screen,SW//2-80,SH//2+20);draw_friend_a(screen,SW//2+80,SH//2+20)
        pxt(screen,"BERTEMU TEMAN A",F_LG,C["yellow"],SW//2,20,center=True)
        pxt(screen,"A – Si Petualang Sejati",F_MD,C["orange"],SW//2+80,SH//2-60,center=True)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("a_is"): self.state["flags"]["a_is"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_meet_b_setup(self):
        screen.fill((40,40,80));pygame.draw.rect(screen,(60,60,100),(100,100,SW-200,SH-200),4)
        draw_player(screen,SW//2-120,SH//2+40);draw_friend_b(screen,SW//2+120,SH//2+40)
        pxt(screen,"ARENA PERTANDINGAN",F_LG,C["yellow"],SW//2,20,center=True)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("b_ss"): self.state["flags"]["b_ss"]=True;self._dlg()
        if self.sub: self.sub.update();self.sub.draw(screen)
        self.dialog.update();self.dialog.draw(screen)

    def _s_meet_b(self):
        screen.fill((40,40,80))
        draw_player(screen,SW//2-120,SH//2+40);draw_friend_b(screen,SW//2+120,SH//2+40)
        pxt(screen,"BERTEMU TEMAN B",F_LG,C["yellow"],SW//2,20,center=True)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("b_ms"): self.state["flags"]["b_ms"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_hunt_sm(self):
        if self.sub: self.sub.update();self.sub.draw(screen)
        else:
            screen.fill(C["dkgreen"])
            pxt(screen,"HUTAN MONSTER KECIL",F_LG,C["yellow"],SW//2,30,center=True)
            pxt(screen,f"Total: {self.state['small_monsters']}/50",F_MD,C["white"],SW//2,80,center=True)
            pxt(screen,"[ENTER] Mulai berburu!",F_LG,C["cyan"],SW//2,SH//2,center=True)
            pxt(screen,"[J]=Tebas [K]=Ultimate — sentuh monster kuning untuk tangkap!",F_SM,C["yellow"],SW//2,SH//2+50,center=True)
            pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
            for i in range(8):
                a=i*45;draw_small_monster(screen,SW//2+math.cos(math.radians(a))*120,SH//2+80+math.sin(math.radians(a))*60,i)
            ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
            if ha: draw_friend_a(screen,SW//2-70,SH//2+80)
            if hb: draw_friend_b(screen,SW//2+70,SH//2+80)
            draw_player(screen,SW//2,SH//2+80,sword=True)
        self.dialog.update();self.dialog.draw(screen)

    def _s_hunt_big(self):
        if self.sub: self.sub.update();self.sub.draw(screen)
        else:
            screen.fill(C["cave"])
            # Cave entrance screen dengan visual gaya RPG
            for gx in range(0,SW,32):
                for gy in range(0,SH,32):
                    t_x = gx//32; t_y = gy//32
                    if (t_x+t_y)%3 != 0:
                        pxr(screen,C["cavewall"],(gx,gy,32,32))
                    # Bata lines
                    pygame.draw.line(screen,C["darkstone"],(gx,gy+16),(gx+32,gy+16),1)
                    pygame.draw.rect(screen,C["darkstone"],(gx,gy,32,32),1)
            # Obor dekorasi
            for tx in [80,240,400,560,720]:
                tf2 = math.sin(pygame.time.get_ticks()/200)*3
                pxr(screen,C["brown"],(tx-2,SH//2-50,4,20))
                fl_col=(255,int(140+tf2*15),0)
                pygame.draw.polygon(screen,fl_col,[(tx-4,SH//2-50),(tx+4,SH//2-50),(tx,SH//2-int(68+tf2))])
                glow=pygame.Surface((50,50),pygame.SRCALPHA)
                pygame.draw.circle(glow,(200,120,40,50),(25,25),22)
                screen.blit(glow,(tx-25,SH//2-70))
            pxt(screen,"GUA KASTIL – DUNGEON LABIRIN",F_LG,C["orange"],SW//2,30,center=True)
            pxt(screen,f"Monster Besar Terkumpul: {self.state['big_monsters']}/5",F_MD,C["white"],SW//2,70,center=True)
            pxt(screen,"[ENTER] Masuk Dungeon Labirin!",F_LG,C["cyan"],SW//2,SH//2-30,center=True)
            pxt(screen,"Setiap ruangan punya BOSS di tengah!",F_SM,C["yellow"],SW//2,SH//2+10,center=True)
            pxt(screen,"WASD=gerak | J=Pedang | K=Ultimate | M=Tembak",F_SM,C["ltgray"],SW//2,SH//2+34,center=True)
            pxt(screen,f"Ammo: {self.state['small_monsters']} monster kecil",F_SM,C["cyan"],SW//2,SH//2+58,center=True)
            pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
            draw_big_monster_centered(screen,SW//2,SH//2+160,scale=1.2,frame=pygame.time.get_ticks()//16)
            ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
            if ha: draw_friend_a(screen,SW//2-100,SH//2+140)
            if hb: draw_friend_b(screen,SW//2+100,SH//2+140)
            draw_player(screen,SW//2-140,SH//2+140,sword=True)
        self.dialog.update();self.dialog.draw(screen)

    def _s_pre_final(self):
        screen.fill((30,10,50))
        pxt(screen,"SEBELUM PERTEMPURAN FINAL",F_LG,C["red"],SW//2,20,center=True)
        draw_player(screen,SW//2,SH//2-20,sword=True)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2-90,SH//2-20)
        if self.state["has_friend_b"]: draw_friend_b(screen,SW//2+90,SH//2-20)
        draw_demon_king(screen,SW//2,100)
        pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        if not self.dialog.visible and not self.state["flags"].get("pf_s"): self.state["flags"]["pf_s"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_final(self):
        if self.sub: self.sub.update();self.sub.draw(screen)
        else:
            screen.fill((20,0,30))
            pxt(screen,"PERTEMPURAN FINAL!",F_XL,C["red"],SW//2,30,center=True)
            draw_demon_king(screen,SW//2,200,pygame.time.get_ticks()//16)
            ha=self.state["has_friend_a"];hb=self.state["has_friend_b"]
            if ha: draw_friend_a(screen,SW//2-120,280)
            if hb: draw_friend_b(screen,SW//2+120,280)
            draw_player(screen,SW//2,280,sword=True)
            pxt(screen,"[ENTER] Mulai pertempuran!",F_MD,C["yellow"],SW//2,SH-60,center=True)
            pxt(screen,"[X] Kembali ke Map",F_SM,C["orange"],8,SH-28)
        self.dialog.update();self.dialog.draw(screen)

    def _bg(self,col):
        screen.fill(col)
        for i in range(0,SW,16): pygame.draw.line(screen,(max(0,col[0]-20),max(0,col[1]-20),max(0,col[2]-20)),(i,0),(i,SH))

    def _s_end_good(self):
        self._bg((10,30,60))
        t=pygame.time.get_ticks()
        for i in range(5):
            cx=100+i*140;cy=100+math.sin(t/500+i)*40
            for a in range(0,360,30):
                r=math.radians(a+t//10);d=30+math.sin(t/200+i)*10
                pygame.draw.circle(screen,[(255,200,0),(255,100,100),(100,200,255),(200,100,255),(100,255,100)][i%5],(int(cx+math.cos(r)*d),int(cy+math.sin(r)*d)),3)
        draw_player(screen,SW//2-120,SH//2+60)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2,SH//2+60)
        if self.state["has_friend_b"]: draw_friend_b(screen,SW//2+120,SH//2+60)
        pxt(screen,"★ ENDING TERBAIK ★",F_XL,C["yellow"],SW//2,40,center=True)
        pxt(screen,"Raja Iblis Malachar telah dikalahkan!",F_LG,C["white"],SW//2,110,center=True)
        if not self.dialog.visible and not self.state["flags"].get("eg_d"): self.state["flags"]["eg_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_end_nof(self):
        self._bg((30,20,10));draw_player(screen,SW//2,SH//2)
        pxt(screen,"ENDING: Sendirian",F_XL,C["orange"],SW//2,40,center=True)
        if not self.dialog.visible and not self.state["flags"].get("en_d"): self.state["flags"]["en_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_end_weak(self):
        self._bg((20,10,10));draw_player(screen,SW//2-60,SH//2)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2+60,SH//2)
        pxt(screen,"ENDING: Kurang Kuat",F_XL,C["red"],SW//2,40,center=True)
        if not self.dialog.visible and not self.state["flags"].get("ew_d"): self.state["flags"]["ew_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

    def _s_end_lost(self):
        self._bg((10,5,5))
        pxt(screen,"ENDING: Dikalahkan",F_XL,C["red"],SW//2,40,center=True)
        draw_player(screen,SW//2,SH//2+20)
        if self.state["has_friend_a"]: draw_friend_a(screen,SW//2-80,SH//2+20)
        if self.state["has_friend_b"]: draw_friend_b(screen,SW//2+80,SH//2+20)
        draw_demon_king(screen,SW//2,SH//2-100)
        if not self.dialog.visible and not self.state["flags"].get("el_d"): self.state["flags"]["el_d"]=True;self._dlg()
        self.dialog.update();self.dialog.draw(screen)

if __name__=="__main__":
    Game().run()