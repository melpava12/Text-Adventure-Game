import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(20, 28))
ax.set_xlim(0, 20)
ax.set_ylim(0, 28)
ax.axis('off')
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#1a1a2e')

C_GREY   = '#7f8c8d'
C_GREEN  = '#27ae60'
C_PURPLE = '#8e44ad'
C_ORANGE = '#e67e22'
C_DARK   = '#2c3e50'
C_RED    = '#e74c3c'
C_TEXT   = 'white'

NW, NH = 3.0, 0.52   # standard node
SW, SH = 2.4, 0.50   # small node

def node(x, y, w, h, label, color, fs=9):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle="round,pad=0.06",
                         facecolor=color, edgecolor='white',
                         linewidth=1.4, zorder=5)
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center',
            fontsize=fs, color='white', fontweight='bold',
            multialignment='center', zorder=6)

def arr(x1, y1, x2, y2, color='#bdc3c7', lw=1.5,
        ls='solid', label='', lo=(0, 0), lfs=7.5, rad=0.0):
    style = f'arc3,rad={rad}'
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw,
                                linestyle=ls,
                                connectionstyle=style), zorder=4)
    if label:
        mx = (x1+x2)/2 + lo[0]
        my = (y1+y2)/2 + lo[1]
        ax.text(mx, my, label, fontsize=lfs, color=color,
                ha='center', va='center', fontstyle='italic',
                bbox=dict(facecolor='#1a1a2e', edgecolor='none', alpha=0.75, pad=1),
                zorder=7)

# ── TITLE ────────────────────────────────────────────────────────────────
ax.text(10, 27.5, 'THE PINES: A HAUNTED GETAWAY', ha='center', va='center',
        fontsize=19, color='white', fontweight='bold', fontfamily='serif')
ax.text(10, 27.05, 'Story Flowchart', ha='center', va='center',
        fontsize=11, color='#bdc3c7', fontstyle='italic')

# ── LEGEND ───────────────────────────────────────────────────────────────
legend = [(C_GREY,'Intro / Neutral'), (C_GREEN,'Friendly Path'),
          (C_PURPLE,'Skeptic Path'), (C_ORANGE,'Escape Path')]
for i,(c,lbl) in enumerate(legend):
    lx = 0.8 + i*4.6
    ax.add_patch(FancyBboxPatch((lx,26.35),1.1,0.40,
                 boxstyle="round,pad=0.04",
                 facecolor=c, edgecolor='white', linewidth=1, zorder=5))
    ax.text(lx+1.25, 26.55, lbl, fontsize=8, color='white', va='center')
# dashed crossover in legend
ax.plot([17.3,18.0],[26.55,26.55], color=C_RED, lw=1.5, linestyle='dashed')
ax.text(18.15, 26.55, 'Crossover', fontsize=8, color=C_RED, va='center')

# ══════════════════════════════════════════════════════════════════════════
# LAYOUT  (y: 25.8 top → endings ~4.5)
# x columns: Friendly=3.8  Skeptic=10.0  Escape=16.2
# ══════════════════════════════════════════════════════════════════════════
XF, XS, XE = 3.8, 10.0, 16.2

# INTRO / ACT1
node(10, 25.6, NW+0.4, NH, 'INTRO\n(Arrive at The Pines)', C_GREY, fs=8)
node(10, 24.5, NW+0.6, NH+0.05, 'ACT 1: Victor\'s Welcome', C_DARK, fs=9)

# branch labels
ax.text(XF,  23.8, 'A: Play along',       fontsize=7.5, color=C_GREEN,  ha='center', fontstyle='italic')
ax.text(XS,  23.8, 'B: Ask about WiFi',   fontsize=7.5, color=C_PURPLE, ha='center', fontstyle='italic')
ax.text(XE,  23.8, 'C: Pretend to leave', fontsize=7.5, color=C_ORANGE, ha='center', fontstyle='italic')

# ── FRIENDLY PATH ────────────────────────────────────────────────────────
F2 = (XF, 23.2);  node(*F2, NW, NH, 'ACT 2: Meet Dot', C_GREEN)
F3 = (XF, 21.7);  node(*F3, NW, NH, 'ACT 3: The Incident', C_GREEN)
F4 = (XF, 20.2);  node(*F4, NW, NH, 'ACT 4: Help with Inn', C_GREEN)
E1 = (XF,  6.0);  node(*E1, NW+0.2, NH+0.1, 'ENDING 1: Five Stars [*]', C_GREEN, fs=9)

ax.text(XF, 21.05, 'FRIENDLY PATH', fontsize=8, color=C_GREEN,
        ha='center', fontweight='bold', alpha=0.7)

# ── SKEPTIC PATH ─────────────────────────────────────────────────────────
S2 = (XS, 23.2);  node(*S2, NW, NH, 'ACT 2: Room Investigation', C_PURPLE)
S3 = (XS, 21.7);  node(*S3, NW, NH, 'ACT 3: The Incident', C_PURPLE)
S4 = (XS, 20.2);  node(*S4, NW, NH, 'ACT 4: Confront Victor', C_PURPLE)
SI = (XS, 18.95); node(*SI, NW-0.2, SH, 'Player types response', '#5d2a7e', fs=8)
VT = (XS-1.6, 17.8); node(*VT, SW-0.1, SH, 'Victor tells you', '#7b3fa0', fs=8)
VR = (XS+1.6, 17.8); node(*VR, SW-0.1, SH, 'Victor refuses', '#7b3fa0', fs=8)
SK = (XS, 16.65); node(*SK, NW, NH, 'Knock mini-game', C_PURPLE)
SB = (XS, 15.4);  node(*SB, NW, NH, 'Barry interaction', C_PURPLE)
E3 = (XS,  6.0);  node(*E3, NW+0.6, NH+0.1, 'ENDING 3: Permanent Guest [ghost]', C_PURPLE, fs=8)

ax.text(XS, 21.05, 'SKEPTIC PATH', fontsize=8, color=C_PURPLE,
        ha='center', fontweight='bold', alpha=0.7)

# ── ESCAPE PATH ──────────────────────────────────────────────────────────
EA2 = (XE,    23.2);  node(*EA2, NW,   NH,   'ACT 2: Dot Negotiation', C_ORANGE)
ELV = (XE-1.6,22.0);  node(*ELV, SW,   SH,   'Leave tonight', '#b35900', fs=8)
EST = (XE+1.6,22.0);  node(*EST, SW,   SH,   'Stay for breakfast', '#b35900', fs=8)
EWT = (XE-1.6,20.8);  node(*EWT, SW,   SH,   'Grab watch\naccidentally', C_ORANGE, fs=7.5)
EA3 = (XE+1.6,20.8);  node(*EA3, SW,   SH,   'ACT 3: The Incident', C_ORANGE, fs=8)
EA4 = (XE+1.6,19.6);  node(*EA4, SW,   SH,   'ACT 4: Kitchen scene', C_ORANGE, fs=8)
ESW = (XE+1.6,18.4);  node(*ESW, SW,   SH,   'A: Stay for weekend', C_ORANGE, fs=8)
EPL = (XE+0.2,18.4);  node(*EPL, SW-0.4,SH,  'B: Stick to plan', C_ORANGE, fs=8)
E2E = (XE-1.6, 6.0);  node(*E2E, NW+0.2, NH+0.1, 'ENDING 2:\nCheck Out Early [run]', C_ORANGE, fs=8)
E2L = (XE+0.2, 6.0);  node(*E2L, NW+0.2, NH+0.1, 'ENDING 2:\nCheck Out Early [run]', C_ORANGE, fs=8)

ax.text(XE, 21.05, 'ESCAPE PATH', fontsize=8, color=C_ORANGE,
        ha='center', fontweight='bold', alpha=0.7)

# ═══════════════════════════════════
# ARROWS
# ═══════════════════════════════════

# intro → act1 → branches
arr(10, 25.6-NH/2, 10, 24.5+NH/2, color='white')
arr(10, 24.5-NH/2, XF, F2[1]+NH/2, color=C_GREEN, lw=1.6)
arr(10, 24.5-NH/2, XS, S2[1]+NH/2, color=C_PURPLE, lw=1.6)
arr(10, 24.5-NH/2, XE, EA2[1]+NH/2, color=C_ORANGE, lw=1.6)

# FRIENDLY chain
arr(F2[0], F2[1]-NH/2, F3[0], F3[1]+NH/2, color=C_GREEN)
arr(F3[0], F3[1]-NH/2, F4[0], F4[1]+NH/2, color=C_GREEN)
arr(F4[0], F4[1]-NH/2, E1[0], E1[1]+NH/2, color=C_GREEN)

# SKEPTIC chain
arr(S2[0], S2[1]-NH/2, S3[0], S3[1]+NH/2, color=C_PURPLE)
arr(S3[0], S3[1]-NH/2, S4[0], S4[1]+NH/2, color=C_PURPLE)
arr(S4[0], S4[1]-NH/2, SI[0], SI[1]+SH/2, color=C_PURPLE)
arr(SI[0], SI[1]-SH/2, VT[0], VT[1]+SH/2, color=C_PURPLE)
arr(SI[0], SI[1]-SH/2, VR[0], VR[1]+SH/2, color=C_PURPLE)
arr(VT[0], VT[1]-SH/2, SK[0], SK[1]+NH/2, color=C_PURPLE)
arr(VR[0], VR[1]-SH/2, SK[0], SK[1]+NH/2, color=C_PURPLE)
arr(SK[0], SK[1]-NH/2, SB[0], SB[1]+NH/2, color=C_PURPLE)
arr(SB[0], SB[1]-NH/2, E3[0], E3[1]+NH/2, color=C_PURPLE)

# ESCAPE chain
arr(EA2[0], EA2[1]-NH/2, ELV[0], ELV[1]+SH/2, color=C_ORANGE)
arr(EA2[0], EA2[1]-NH/2, EST[0], EST[1]+SH/2, color=C_ORANGE)
arr(ELV[0], ELV[1]-SH/2, EWT[0], EWT[1]+SH/2, color=C_ORANGE)
arr(EWT[0], EWT[1]-SH/2, E2E[0], E2E[1]+NH/2, color=C_ORANGE)
arr(EST[0], EST[1]-SH/2, EA3[0], EA3[1]+SH/2, color=C_ORANGE)
arr(EA3[0], EA3[1]-SH/2, EA4[0], EA4[1]+SH/2, color=C_ORANGE)
arr(EA4[0], EA4[1]-SH/2, ESW[0], ESW[1]+SH/2, color=C_ORANGE)
arr(EA4[0], EA4[1]-SH/2, EPL[0], EPL[1]+SH/2, color=C_ORANGE)
arr(EPL[0], EPL[1]-SH/2, E2L[0], E2L[1]+NH/2, color=C_ORANGE)

# ── CROSSOVER DASHED ARROWS ───────────────────────────────────────────────
# Friendly ACT2 "Are you a ghost? B" → Skeptic ACT3
arr(F2[0]+NW/2, F2[1], S3[0]-NW/2, S3[1],
    color=C_RED, lw=1.6, ls='dashed', rad=-0.2,
    label='Are you a ghost? (B)', lo=(0, 0.35), lfs=7)

# Escape ACT4 "A: Stay for weekend" → Friendly ACT4
arr(ESW[0]-SW/2, ESW[1], F4[0]+NW/2, F4[1],
    color=C_RED, lw=1.6, ls='dashed', rad=0.35,
    label='merges to Friendly ACT 4', lo=(0, -0.35), lfs=7)

# ── ENDINGS BANNER ───────────────────────────────────────────────────────
ax.add_patch(FancyBboxPatch((0.3, 4.8), 19.4, 0.35,
             boxstyle="round,pad=0.05",
             facecolor='#2c3e50', edgecolor='#7f8c8d',
             linewidth=1, zorder=3))
ax.text(10, 4.975, 'E N D I N G S', ha='center', va='center',
        fontsize=10, color='#bdc3c7', fontweight='bold')

plt.tight_layout(pad=0.4)
plt.savefig(r'C:\Users\mellissa.pava\Downloads\Claude Code Practice\flowchart.png',
            dpi=100, bbox_inches='tight', facecolor=fig.get_facecolor())
print('Saved flowchart.png')
