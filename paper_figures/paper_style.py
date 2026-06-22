"""Shared house style for the publication figure set (one figure per study).
Consistent palette, typography, a stats-annotation box, significance stars, and a PNG+PDF saver."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

COORD="#2E7D8C"   # coordination pole / team A
DELIB="#d95f02"   # deliberation pole / team B
NEUTRAL="#6b7280"
INK="#1f2937"
GRID="#e5e7eb"
TEAM={"startup_a":COORD,"startup_b":DELIB}

def setup():
    plt.rcParams.update({
        "font.family":"DejaVu Sans","font.size":10.5,"axes.edgecolor":"#9aa0a6",
        "axes.linewidth":.8,"axes.titlesize":11.5,"axes.titleweight":"bold","axes.labelsize":10.5,
        "axes.grid":True,"grid.color":GRID,"grid.linewidth":.7,"xtick.color":INK,"ytick.color":INK,
        "xtick.labelsize":9.5,"ytick.labelsize":9.5,
        "axes.axisbelow":True,"figure.dpi":150,"savefig.dpi":600,"legend.frameon":False,
        "axes.spines.top":False,"axes.spines.right":False,
        # crisp, selectable text in vector outputs (embed TrueType; keep SVG text as text)
        "pdf.fonttype":42,"ps.fonttype":42,"svg.fonttype":"none"})

def stars(p):
    return "***" if p<.001 else "**" if p<.01 else "*" if p<.05 else "n.s."

def statbox(ax,text,loc="upper left",fc="#f8fafc",ec="#cbd5e1",fontsize=8.4):
    xy={"upper left":(.025,.975,"left","top"),"upper right":(.975,.975,"right","top"),
        "lower left":(.025,.03,"left","bottom"),"lower right":(.975,.03,"right","bottom")}[loc]
    ax.text(xy[0],xy[1],text,transform=ax.transAxes,ha=xy[2],va=xy[3],fontsize=fontsize,color=INK,
            bbox=dict(boxstyle="round,pad=0.45",fc=fc,ec=ec,lw=.8),zorder=10,linespacing=1.35)

def caption(fig,text,y=0.005,fontsize=8):
    fig.text(0.5,y,text,ha="center",va="bottom",fontsize=fontsize,color=NEUTRAL,style="italic",wrap=True)

def save(fig,name):
    import os; d=os.path.dirname(__file__)
    fig.savefig(os.path.join(d,f"{name}.png"),bbox_inches="tight",facecolor="white",dpi=600)
    fig.savefig(os.path.join(d,f"{name}.pdf"),bbox_inches="tight",facecolor="white")   # vector
    fig.savefig(os.path.join(d,f"{name}.svg"),bbox_inches="tight",facecolor="white")   # vector
    print(f"wrote {name}.png (600dpi) / .pdf / .svg")
