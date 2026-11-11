"""Estilo común de las figuras (paleta validada, coma decimal, tipografía) y ayudas de dibujo.

Paleta: la de referencia del método de visualización usado en el proyecto (categórica en orden
fijo, rampa secuencial azul y divergente azul-rojo con gris en el medio). Los colores identifican
series; los textos van siempre en tinta neutra.
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

# ------------------------------------------------------------------ colores
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
TINTA_3 = "#898781"
GRILLA = "#e1e0d9"
EJE = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
AZUL, NARANJA, AGUA, AMARILLO, MAGENTA, VERDE, VIOLETA, ROJO = SERIES
ESTADO = dict(bien="#0ca30c", alerta="#fab219", serio="#ec835a", critico="#d03b3b")
RAMPA_AZUL = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5",
              "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
NEUTRO = "#f0efec"
# divergente: rojo (seco) - gris - azul (húmedo)
_ROJOS = ["#7f1d1d", "#b42828", "#e34948", "#f09a99", NEUTRO]
_AZULES = [NEUTRO, "#9ec5f4", "#3987e5", "#1c5cab", "#0d366b"]
DIVERGENTE = LinearSegmentedColormap.from_list("seco_humedo", _ROJOS + _AZULES[1:], N=256)
SECUENCIAL = LinearSegmentedColormap.from_list("azul", RAMPA_AZUL, N=256)

PISOS = {1: AZUL, 2: NARANJA, 3: AGUA}


def _fuente():
    nombres = {f.name for f in font_manager.fontManager.ttflist}
    for n in ("Inter", "DejaVu Sans"):
        if n in nombres:
            return n
    return "sans-serif"


def estilo():
    plt.rcParams.update({
        "figure.facecolor": SUPERFICIE, "axes.facecolor": SUPERFICIE, "savefig.facecolor": SUPERFICIE,
        "font.family": _fuente(), "font.size": 9.5,
        "axes.edgecolor": EJE, "axes.linewidth": 0.8, "axes.labelcolor": TINTA_2,
        "axes.titlecolor": TINTA, "axes.titlesize": 11, "axes.titleweight": "semibold",
        "axes.titlelocation": "left", "axes.titlepad": 10,
        "axes.grid": True, "grid.color": GRILLA, "grid.linewidth": 0.6, "grid.linestyle": "-",
        "axes.axisbelow": True, "axes.spines.top": False, "axes.spines.right": False,
        "xtick.color": TINTA_3, "ytick.color": TINTA_3, "xtick.labelcolor": TINTA_2,
        "ytick.labelcolor": TINTA_2, "xtick.major.size": 0, "ytick.major.size": 0,
        "xtick.major.pad": 5, "ytick.major.pad": 5,
        "lines.linewidth": 1.8, "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
        "legend.frameon": False, "legend.fontsize": 8.5, "legend.labelcolor": TINTA_2,
        "figure.dpi": 100, "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.15,
        "axes.prop_cycle": matplotlib.cycler(color=SERIES),
    })


# ------------------------------------------------------------------ números en castellano
def num(x, dec=0, miles=True):
    """Formatea con coma decimal y punto de miles: num(1234.5, 1) -> '1.234,5'."""
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "—"
    s = f"{x:,.{dec}f}" if miles else f"{x:.{dec}f}"
    s = s.replace(",", "§").replace(".", ",").replace("§", ".")
    if s.startswith("-"):
        s = "−" + s[1:] if s.strip("-0,.") else s[1:]
    return s


def _fmt_eje(x, pos=None):
    if abs(x) >= 1000:
        return num(x, 0)
    if float(x).is_integer():
        return num(x, 0)
    d = 1 if abs(x * 10 - round(x * 10)) < 1e-9 else 2
    return num(x, d, miles=False)


def coma(ax, ejes="xy"):
    f = FuncFormatter(_fmt_eje)
    if "x" in ejes:
        ax.xaxis.set_major_formatter(f)
    if "y" in ejes:
        ax.yaxis.set_major_formatter(f)


def pct(ax, ejes="y", dec=0):
    f = FuncFormatter(lambda x, p: num(100 * x, dec, miles=False) + " %")
    if "x" in ejes:
        ax.xaxis.set_major_formatter(f)
    if "y" in ejes:
        ax.yaxis.set_major_formatter(f)


# ------------------------------------------------------------------ ayudas
def titulo(fig, texto, sub=None, y=1.0):
    """Título que dice el hallazgo y, debajo, qué se grafica (se corta en líneas al ancho de la figura)."""
    import textwrap
    ancho = fig.get_size_inches()[0]
    n_sub = int(ancho * 15.5)
    n_tit = int(ancho * 11.2)
    lineas_sub = textwrap.wrap(sub, n_sub) if sub else []
    alto_linea = 0.16 / fig.get_size_inches()[1]          # ~0,16 pulgadas por línea de 9 pt
    y_sub = y + 0.02
    if lineas_sub:
        fig.text(0.0, y_sub, "\n".join(lineas_sub), ha="left", va="bottom", fontsize=9.2, color=TINTA_2,
                 transform=fig.transFigure, linespacing=1.35)
    y_tit = y_sub + alto_linea * 1.35 * len(lineas_sub) + 0.012
    fig.text(0.0, y_tit, "\n".join(textwrap.wrap(texto, n_tit)), ha="left", va="bottom", fontsize=12.5,
             fontweight="semibold", color=TINTA, transform=fig.transFigure, linespacing=1.2)


def nota(fig, texto, y=-0.02):
    fig.text(0.0, y, texto, ha="left", va="top", fontsize=7.8, color=TINTA_3, transform=fig.transFigure)


def linea_ref(ax, valor, texto, eje="y", lado="derecha", color=TINTA_3, va="bottom"):
    """Línea de referencia (límite, objetivo) con su rótulo en tinta neutra."""
    if eje == "y":
        ax.axhline(valor, color=color, lw=0.9, zorder=1.5)
        xl = ax.get_xlim()
        x = xl[1] if lado == "derecha" else xl[0]
        ax.text(x, valor, " " + texto + " ", ha="right" if lado == "derecha" else "left", va=va,
                fontsize=7.8, color=TINTA_2, zorder=5)
    else:
        ax.axvline(valor, color=color, lw=0.9, zorder=1.5)
        yl = ax.get_ylim()
        ax.text(valor, yl[1], " " + texto, ha="left", va="top", fontsize=7.8, color=TINTA_2,
                rotation=90, zorder=5)


def rotulo_fin(ax, x, y, texto, color_marca, dx=4, dy=0, ha="left"):
    """Rótulo directo al final de una serie: punto con anillo + texto neutro."""
    ax.plot([x], [y], "o", ms=5.5, color=color_marca, mec=SUPERFICIE, mew=1.6, zorder=6, clip_on=False)
    ax.annotate(texto, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center",
                fontsize=8, color=TINTA_2, zorder=6, annotation_clip=False)


def marcar_pisos(ax, L=12.0, ymax=None, rotulo=True):
    """Separadores verticales de los tres pisos sobre un eje x de recorrido (0-36 m)."""
    for k in (1, 2):
        ax.axvline(k * L, color=EJE, lw=0.8, zorder=1)
    if rotulo:
        y = ax.get_ylim()[1] if ymax is None else ymax
        for k in range(3):
            ax.text((k + 0.5) * L, y, f"piso {k + 1}", ha="center", va="bottom", fontsize=8,
                    color=TINTA_3)


def guardar(fig, ruta):
    fig.savefig(ruta)
    plt.close(fig)
