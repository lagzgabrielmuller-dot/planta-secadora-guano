"""Gráficos del análisis económico (PNG para el informe), a partir de economia.json.

    python figuras_economia.py      # -> analisis_economico/figuras/*.png

Estilo: superficie blanca, una sola escala por gráfico (nunca dos ejes Y), líneas de 2 px, barras finas, grilla
fina y clara, leyenda cuando hay dos series o más y rótulos directos sólo donde cuentan la historia. Colores
categóricos en orden fijo (azul, naranja, aguamarina, amarillo, magenta, verde, violeta), validados para
daltonismo; el positivo/negativo del puente usa el par divergente azul/rojo con gris neutro para los totales.
"""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.ticker import FuncFormatter, MultipleLocator  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
SALIDA = os.path.join(RAIZ, "analisis_economico", "figuras")
E = json.load(open(os.path.join(AQUI, "economia.json"), encoding="utf-8"))
D = E["dolar"]
M = 1e6

SERIE = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
TINTA, TINTA2, MUDA = "#0b0b0b", "#52514e", "#898781"
GRILLA, BASE = "#e1e0d9", "#c3c2b7"
POS, NEG, NEUTRO = "#2a78d6", "#e34948", "#898781"
ESC = {"realista": ("Realista", SERIE[0]), "conservador": ("Conservador", SERIE[1]),
       "optimista": ("Optimista", SERIE[2])}

for f in ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
          "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
    if os.path.exists(f):
        font_manager.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": ["Liberation Sans", "DejaVu Sans"], "font.size": 9.5, "axes.edgecolor": BASE,
    "axes.labelcolor": TINTA2, "xtick.color": TINTA2, "ytick.color": TINTA2, "axes.titlecolor": TINTA,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRILLA,
    "grid.linewidth": 0.6, "grid.linestyle": "-", "axes.axisbelow": True, "figure.facecolor": "white",
    "axes.facecolor": "white", "legend.frameon": False, "legend.fontsize": 9, "axes.titlesize": 11,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "savefig.dpi": 200,
})


def ar(x, d=0):
    """Número con coma decimal, punto de miles y signo menos tipográfico."""
    t = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" + t) if x < 0 and t.strip("0,") else t


FMT = FuncFormatter(lambda v, _p: ar(v, 0))


def guardar(fig, nombre):
    os.makedirs(SALIDA, exist_ok=True)
    ruta = os.path.join(SALIDA, nombre)
    fig.savefig(ruta, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return ruta


def produccion():
    """Guano húmedo procesado, producto seco obtenido y producto vendido (t/año, año de régimen)."""
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    nombres = ["conservador", "realista", "optimista"]
    series = [("Guano húmedo procesado", "humedo_t"), ("Producto seco al 15 % obtenido", "seco_t"),
              ("Producto vendido", "vendido_t")]
    ancho = 0.22
    for j, (rot, k) in enumerate(series):
        xs = [i + (j - 1) * (ancho + 0.03) for i in range(3)]
        vals = [E["escenarios"][n]["anio2"][k] for n in nombres]
        ax.bar(xs, vals, ancho, color=SERIE[j], label=rot, zorder=2)
        for x, v in zip(xs, vals):
            ax.text(x, v + 25, ar(v), ha="center", va="bottom", fontsize=8, color=TINTA2)
    ax.set_xticks(range(3), [ESC[n][0] for n in nombres])
    ax.tick_params(axis="x", length=0, labelsize=10, labelcolor=TINTA)
    ax.yaxis.set_major_formatter(FMT)
    ax.set_ylabel("t/año")
    ax.grid(axis="x", visible=False)
    ax.set_title("Producción anual por escenario (1 turno, año de régimen)")
    ax.legend(loc="upper left", ncol=3, bbox_to_anchor=(0, -0.1))
    return guardar(fig, "f1_produccion.png")


GRUPOS = [("Mano de obra y administración", ("mano_obra", "administracion")),
          ("Energía eléctrica", ("energia_var", "energia_fija")),
          ("Cáscara de arroz", ("cascara",)),
          ("Flete del guano húmedo", ("flete_guano",)),
          ("Mantenimiento", ("mantenimiento",)),
          ("Envases, insumos, seguros, comercialización e impuestos",
           ("envases", "otros_insumos", "seguros_tasas", "comercializacion", "iibb", "deb_cred"))]


def ingresos_costos():
    """Ventas y costos mensuales de régimen (M$/mes), costos apilados por rubro."""
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    nombres = ["conservador", "realista", "optimista"]
    ancho = 0.32
    for i, n in enumerate(nombres):
        a = E["escenarios"][n]["anio2"]
        v = a["ventas"] / 12 / M
        ax.bar(i - 0.19, v, ancho, color=SERIE[0], zorder=2, label="Ventas" if i == 0 else None)
        ax.text(i - 0.19, v + 0.4, ar(v, 1), ha="center", va="bottom", fontsize=8, color=TINTA2)
        base = 0.0
        for j, (rot, claves) in enumerate(GRUPOS):
            h = sum(a["costos"][k] for k in claves) / 12 / M
            ax.bar(i + 0.19, h, ancho, bottom=base, color=SERIE[j + 1], zorder=2, edgecolor="white", linewidth=1,
                   label=rot if i == 0 else None)
            base += h
        ax.text(i + 0.19, base + 0.4, ar(base, 1), ha="center", va="bottom", fontsize=8, color=TINTA2)
    ax.set_xticks(range(3), [f"{ESC[n][0]}\nventas · costos" for n in nombres])
    ax.tick_params(axis="x", length=0, labelcolor=TINTA)
    ax.set_ylabel("millones de pesos por mes")
    ax.grid(axis="x", visible=False)
    ax.set_title("Ventas y costos de un mes de régimen ($ de noviembre de 2026)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8)
    return guardar(fig, "f2_ingresos_costos.png")


def curva_referencia():
    """Curva de recuperación mes a mes del caso que recupera: 2 turnos a 1.440 kg/h con precios del proyecto."""
    ref = E["referencia"]
    fm = ref["flujo_mensual"]
    meses = [f["mes"] for f in fm][:73]
    acum = [f["acumulado"] / M for f in fm][:73]
    inv_acum = [-(ref["inv_total"] + max(f.get("capital_trabajo") or 0.0, 0.0)) / M for f in fm][:73]
    flujo = [f["flujo"] / M for f in fm][1:73]
    pb = ref["payback_meses"]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.4, 5.6), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]})
    a1.plot(meses, inv_acum, color=SERIE[1], lw=2, label="Inversión inicial acumulada (activo fijo + capital de trabajo)",
            drawstyle="steps-post")
    a1.plot(meses, acum, color=SERIE[0], lw=2, label="Flujo de caja acumulado")
    a1.axhline(0, color=BASE, lw=1)
    a1.plot([pb], [0], "o", ms=8, color=SERIE[0], mec="white", mew=2, zorder=5)
    a1.annotate(f"Mes {ar(pb, 1)}: el flujo acumulado\nllega a cero y se recupera la inversión",
                (pb, 0), xytext=(pb + 3, -600), fontsize=8.5, color=TINTA,
                arrowprops={"arrowstyle": "-", "color": MUDA, "lw": 0.8})
    a1.yaxis.set_major_formatter(FMT)
    a1.set_ylabel("millones de $")
    a1.set_title("Recuperación de la inversión: 2 turnos a 1.440 kg/h, precios del proyecto")
    a1.legend(loc="upper left", fontsize=8)
    a2.bar(meses[1:], flujo, 0.7, color=SERIE[0], zorder=2)
    a2.axhline(0, color=BASE, lw=1)
    a2.set_ylabel("flujo mensual\n(millones de $)")
    a2.set_xlabel("mes desde el arranque de la planta")
    a2.xaxis.set_major_locator(MultipleLocator(12))
    a2.grid(axis="x", visible=False)
    a2.text(8, min(flujo) * 0.7, "meses 1 a 6: puesta en marcha (50 % y 80 % del caudal) y capital de trabajo",
            fontsize=7.5, color=TINTA2, va="center")
    a2.yaxis.set_major_formatter(FMT)
    return guardar(fig, "f3_recuperacion_referencia.png")


def curva_escenarios():
    """Flujo acumulado de los tres escenarios en 15 años (no recuperan) y de la referencia."""
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    series = [("realista", "Realista"), ("conservador", "Conservador"), ("optimista", "Optimista")]
    for j, (n, rot) in enumerate(series):
        fm = E["escenarios"][n]["flujo_mensual"][:180]
        xs = [f["mes"] for f in fm]
        ys = [f["acumulado"] / M for f in fm]
        ax.plot(xs, ys, color=SERIE[j], lw=2, label=f"{rot}: 1 turno, 1.000 kg/h")
        ax.text(xs[-1] + 2, ys[-1], rot, va="center", fontsize=8, color=TINTA2)
    fm = E["referencia"]["flujo_mensual"][:180]
    xs, ys = [f["mes"] for f in fm], [f["acumulado"] / M for f in fm]
    ax.plot(xs, ys, color=SERIE[3], lw=2, label="Referencia: 2 turnos a 1.440 kg/h, precios del proyecto")
    ax.text(xs[-1] + 2, ys[-1], "Referencia", va="center", fontsize=8, color=TINTA2)
    ax.axhline(0, color=BASE, lw=1)
    ax.yaxis.set_major_formatter(FMT)
    ax.xaxis.set_major_locator(MultipleLocator(24))
    ax.set_xlim(0, 196)
    ax.set_xlabel("mes desde el arranque de la planta")
    ax.set_ylabel("flujo de caja acumulado (millones de $)")
    ax.set_title("Flujo de caja acumulado en 15 años (sin valor residual)")
    ax.legend(loc="upper left", fontsize=8)
    return guardar(fig, "f4_recuperacion_escenarios.png")


def tornado():
    """Payback del caso de referencia cuando cambia una variable por vez."""
    s = E["sensibilidad"]["referencia"]
    base = s["base"]["payback"]
    tope = 180.0
    filas = []
    for f in s["filas"]:
        lo = f["bajo"]["payback"] if f["bajo"]["payback"] is not None else tope
        hi = f["alto"]["payback"] if f["alto"]["payback"] is not None else tope
        (vd, td), (vf, tf) = sorted(((lo, f["txt_bajo"]), (hi, f["txt_alto"])), key=lambda t: -t[0])
        filas.append((f"{f['nombre']}: {td} / {tf}", vd, vf, max(abs(lo - base), abs(hi - base))))
    filas.sort(key=lambda t: t[3])
    fig, ax = plt.subplots(figsize=(7.4, 4.6))
    leyenda = set()
    for i, (_desc, vd, vf, _r) in enumerate(filas):
        for v, col, rot in ((vd, NEG, "Valor desfavorable (primero en el rótulo)"),
                            (vf, POS, "Valor favorable (segundo en el rótulo)")):
            if abs(v - base) < 0.05:
                continue
            ax.barh(i, v - base, 0.36, left=base, color=col, zorder=2, label=None if rot in leyenda else rot)
            leyenda.add(rot)
            ax.text(v + (1.2 if v > base else -1.2), i, ar(v, 0), va="center", ha="left" if v > base else "right",
                    fontsize=7.5, color=TINTA2)
    ax.axvline(base, color=TINTA2, lw=1)
    ax.set_yticks(range(len(filas)), [t[0] for t in filas], fontsize=8)
    ax.tick_params(axis="y", length=0, labelcolor=TINTA)
    ax.set_xlabel("meses hasta recuperar la inversión")
    ax.grid(axis="y", visible=False)
    ax.set_title(f"Sensibilidad del payback (base: {ar(base, 1)} meses, 2 turnos a 1.440 kg/h)")
    ax.legend(loc="lower right", fontsize=8)
    return guardar(fig, "f5_tornado.png")


def precio_payback():
    """Payback en función del precio medio para cuatro configuraciones (demás supuestos del realista)."""
    c = E["curva_precio"]
    pr = c["precios_usd_t"]
    nombres = {"Actual": "1 turno, 1.000 kg/h (actual)", "B": "1 turno, 1.440 kg/h",
               "A1+B": "2 turnos, 1.440 kg/h", "A2+B": "3 turnos, 1.440 kg/h"}
    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for j, (k, rot) in enumerate(nombres.items()):
        ys = [v if v is not None and v <= 180 else None for v in c["payback"][k]]
        xs = [x for x, y in zip(pr, ys) if y is not None]
        ys2 = [y for y in ys if y is not None]
        ax.plot(xs, ys2, color=SERIE[j], lw=2, label=rot)
    ax.axhline(60, color=TINTA2, lw=1)
    ax.text(805, 60, "60 meses", va="center", fontsize=8, color=TINTA2)
    for x, rot in ((E["escenarios"]["realista"]["precio_t"] / D, "precio realista"),
                   (E["datos"]["PRECIO_PROY"], "precio del proyecto")):
        ax.axvline(x, color=MUDA, lw=0.8)
        ax.text(x + 6, 172, rot, fontsize=8, color=TINTA2, rotation=90, va="top")
    ax.set_xlim(100, 800)
    ax.set_ylim(0, 180)
    ax.xaxis.set_major_formatter(FMT)
    ax.set_xlabel("precio medio de venta ex planta (USD/t, sin IVA)")
    ax.set_ylabel("meses hasta recuperar la inversión")
    ax.set_title("¿A qué precio se recupera la inversión? (demás supuestos del escenario realista)")
    ax.legend(loc="upper right", fontsize=8)
    return guardar(fig, "f6_precio_payback.png")


def capacidad_necesaria():
    """Caudal de guano húmedo necesario para recuperar en 24 a 60 meses (precios del proyecto)."""
    mins = E["inverso"]["optimista"]["minimos"]
    fig, ax = plt.subplots(figsize=(7.4, 4.0))
    plazos = [24, 36, 48, 60]
    for j, (cfg, rot) in enumerate((("1T", "1 turno (8 h/día)"), ("2T", "2 turnos (16 h/día)"),
                                    ("3T", "3 turnos (24 h/día)"))):
        ys = [mins[f"{cfg}_{N}"]["m_in"] if mins[f"{cfg}_{N}"] else None for N in plazos]
        ax.plot(plazos, ys, color=SERIE[j], lw=2, marker="o", ms=6, mec="white", mew=1.5, label=rot)
        ax.text(61.2, ys[-1], ar(ys[-1]) + " kg/h", va="center", fontsize=8, color=TINTA2)
    for y, x, rot in ((1440, 49.0, "límite del secador a 135 °C: 1.440 kg/h"),
                      (1000, 24.3, "diseño actual: 1.000 kg/h")):
        ax.axhline(y, color=MUDA, lw=0.9)
        ax.text(x, y + 50, rot, fontsize=8, color=TINTA2)
    ax.set_xticks(plazos, [f"{n} meses\n({n // 12} años)" for n in plazos])
    ax.yaxis.set_major_formatter(FMT)
    ax.set_xlim(23, 66)
    ax.set_ylabel("guano húmedo por secadora (kg/h)")
    ax.set_title("Caudal necesario para recuperar la inversión (precios del proyecto)")
    ax.legend(loc="upper right", fontsize=8)
    return guardar(fig, "f7_capacidad_necesaria.png")


def puente():
    """Del beneficio anual del proyecto al flujo del escenario realista (USD/año)."""
    pasos = E["puente"]["pasos"]
    cortos = ["Proyecto (sin biogás, 1 turno)", "Sin «ahorros» de la granja", "Sin venta de sulfato",
              "Disponibilidad, mermas y venta parcial", "Precio medio realista", "Cáscara puesta en planta",
              "Flete del guano húmedo", "Energía recalculada", "Mano de obra UOM", "Envases según el canal",
              "Mantenimiento y otros insumos", "Seguros y tasas", "Administración y honorarios",
              "Comercialización e impuestos", "Ganancias y capital de trabajo"]
    fig, ax = plt.subplots(figsize=(7.4, 5.2))
    acum = 0.0
    n = len(pasos)
    for i, (_t, v) in enumerate(pasos):
        y = n - i
        if i == 0:
            ax.barh(y, v, 0.55, color=NEUTRO, zorder=2)
            acum = v
            ax.text(v + 2000, y, ar(v), va="center", fontsize=7.5, color=TINTA2)
        else:
            ax.barh(y, v, 0.55, left=acum, color=POS if v >= 0 else NEG, zorder=2)
            txt = "0" if abs(v) < 0.5 else (("+" if v > 0 else "−") + ar(abs(v)))
            ax.text(max(acum, acum + v) + 2000, y, txt, va="center", ha="left", fontsize=7.5, color=TINTA2)
            acum += v
    ax.barh(0, acum, 0.55, color=NEUTRO, zorder=2)
    ax.text(max(acum, 0) + 2000, 0, ar(acum), va="center", ha="left", fontsize=7.5, color=TINTA2)
    ax.set_xlim(min(acum, 0) - 6000, None)
    ax.set_yticks(list(range(n, -1, -1)), cortos + ["Escenario realista (flujo de un año)"], fontsize=8)
    ax.tick_params(axis="y", length=0, labelcolor=TINTA)
    ax.axvline(0, color=BASE, lw=1)
    ax.xaxis.set_major_formatter(FMT)
    ax.set_xlabel("USD por año (año de régimen)")
    ax.grid(axis="y", visible=False)
    ax.set_title("Del beneficio del proyecto al flujo del escenario realista")
    return guardar(fig, "f8_puente.png")


def main():
    rutas = [produccion(), ingresos_costos(), curva_referencia(), curva_escenarios(), tornado(), precio_payback(),
             capacidad_necesaria(), puente()]
    for r in rutas:
        print(r)


if __name__ == "__main__":
    main()
