"""Figuras del estudio (PNG en figuras/), a partir de resultados/*.json.

Cada figura lleva como título el hallazgo y, debajo, qué se grafica y en qué condiciones.
"""
import json
import os

import numpy as np
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from secado import graficos as gr
from secado import parametros as pa

plt = gr.plt
AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "resultados")
FIG = os.path.join(AQUI, "figuras")
os.makedirs(FIG, exist_ok=True)
N = gr.num

RAMPA_NARANJA = LinearSegmentedColormap.from_list(
    "naranja", ["#fdeee6", "#fbd3bf", "#f7b394", "#f28f63", "#eb6834", "#c9501f", "#9c3c15", "#6e2a0e"])


def cargar(nombre):
    p = os.path.join(RES, f"{nombre}.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def ruta(nombre):
    return os.path.join(FIG, nombre)


def _tramos(d, clave_hum="hum_med"):
    """Une los tres pisos en un solo recorrido, con el punto de entrada de cada piso."""
    s = d["resumen"]
    xs, hs, hmin, hmax, Tm, Tmin, Tmax, Ta = [], [], [], [], [], [], [], []
    h_prev = s["humedad_entrada"]
    T_prev = s["T_amb"] + pa.DT_NAVE
    for k, p in enumerate(d["pisos"]):
        x0 = 12.0 * k
        xs.append(np.r_[x0, p["x"]])
        hs.append(np.r_[h_prev, p["hum_med"]])
        hmin.append(np.r_[h_prev, p["hum_min"]])
        hmax.append(np.r_[h_prev, p["hum_max"]])
        Tm.append(np.r_[T_prev, p["T_med"]])
        Tmin.append(np.r_[T_prev, p["T_min"]])
        Tmax.append(np.r_[T_prev, p["T_max"]])
        Ta.append(np.r_[p["T_aire_sal"][0], p["T_aire_sal"]])
        h_prev = p["hum_med"][-1]
        cap = pa.CP_SOLIDO + 4186.0 * np.array(p["capas_hum"])[:, -1] / (1 - np.array(p["capas_hum"])[:, -1])
        T_prev = float((cap * np.array(p["capas_T"])[:, -1]).sum() / cap.sum())
    return xs, hs, hmin, hmax, Tm, Tmin, Tmax, Ta


# =============================================================================== 01 perfiles
def fig_perfiles(P):
    fig, axs = plt.subplots(2, 2, figsize=(11.5, 6.8), sharex=True, sharey="row",
                            gridspec_kw=dict(hspace=0.16, wspace=0.08))
    casos = [("diseno", f"Diseño Rev. E: aire a {N(P['diseno']['resumen']['T_aire'])} °C"),
             ("ajustado", f"Aire a {N(P['T15'])} °C: sale al 15 %")]
    for col, (clave, nombre) in enumerate(casos):
        d = P[clave]
        s = d["resumen"]
        xs, hs, hmin, hmax, Tm, Tmin, Tmax, Ta = _tramos(d)
        ax = axs[0, col]
        for k in range(3):
            ax.fill_between(xs[k], 100 * hmin[k], 100 * hmax[k], color=gr.AZUL, alpha=0.13, lw=0)
            ax.plot(xs[k], 100 * hs[k], color=gr.AZUL)
        ax.set_ylim(0, 80)
        ax.set_xlim(0, 36)
        ax.axhline(15, color=gr.TINTA_3, lw=0.9, zorder=1.5)
        ax.text(0.4, 15.6, "objetivo 15 %", ha="left", va="bottom", fontsize=7.8, color=gr.TINTA_2)
        ax.set_title(nombre, fontsize=10.5)
        gr.marcar_pisos(ax, ymax=80)
        txt_sal = (f"sale al {N(100 * s['hum_out'], 1)} %" if s["hum_out"] >= 0.02 else "sale casi seco (< 2 %)")
        gr.rotulo_fin(ax, 36, 100 * s["hum_out"], txt_sal, gr.AZUL, dx=-8, dy=10, ha="right")
        ax2 = axs[1, col]
        for k in range(3):
            ax2.fill_between(xs[k], Tmin[k], Tmax[k], color=gr.AZUL, alpha=0.13, lw=0)
            ax2.plot(xs[k], Tm[k], color=gr.AZUL)
            ax2.plot(xs[k], Ta[k], color=gr.NARANJA)
            ax2.plot([12 * k, 12 * (k + 1)], [s["Tin"][k]] * 2, color=gr.TINTA_3, lw=1.1)
        ax2.set_ylim(0, 150)
        ax2.set_xlabel("recorrido del producto en el secador [m]")
        gr.coma(ax2)
        gr.coma(ax)
        ax2.annotate(f"producto a la salida: {N(s['T_prod'])} °C", (36, s["T_prod"]), xytext=(-4, -14),
                     textcoords="offset points", ha="right", fontsize=8.2, color=gr.TINTA)
    axs[0, 0].set_ylabel("humedad del guano [% b.h.]")
    axs[1, 0].set_ylabel("temperatura [°C]")
    h = [Line2D([], [], color=gr.AZUL, label="guano (media de las capas)"),
         Patch(color=gr.AZUL, alpha=0.13, label="rango entre capas"),
         Line2D([], [], color=gr.NARANJA, label="aire que sale del lecho"),
         Line2D([], [], color=gr.TINTA_3, lw=1.1, label="aire que entra bajo la banda")]
    axs[1, 1].legend(handles=h, loc="lower right", ncol=2, fontsize=8)
    sd = P["diseno"]["resumen"]
    gr.titulo(fig, "A 135 °C el guano se seca del todo antes del piso 3; con "
                   f"{N(P['T15'])} °C sale justo al 15 %",
              f"1.000 kg/h de guano al 72 %, bandas a {N(sd['vel'], 2)} m/min (capa de {N(sd['capa_mm'])} mm, "
              f"{N(sd['t_res'])} min de residencia), 25 % de recirculación, ambiente 18 °C y 60 %.", y=0.93)
    gr.guardar(fig, ruta("01_perfiles_diseno.png"))


# =============================================================================== 02 capas
def fig_capas(P):
    d = P["ajustado"]
    nz = d["nz"]
    H = np.hstack([np.array(p["capas_hum"]) for p in d["pisos"]]) * 100
    T = np.hstack([np.array(p["capas_T"]) for p in d["pisos"]])
    fig, axs = plt.subplots(2, 1, figsize=(11.5, 5.6), sharex=True, gridspec_kw=dict(hspace=0.32))
    ext = [0, 36, 0, nz]
    im = axs[0].imshow(H, origin="lower", aspect="auto", extent=ext, cmap=gr.DIVERGENTE,
                       norm=TwoSlopeNorm(vmin=0, vcenter=15, vmax=72), interpolation="nearest")
    axs[0].contour(np.linspace(0, 36, H.shape[1]), np.arange(nz) + 0.5, H, levels=[15],
                        colors=[gr.TINTA_2], linewidths=0.9)
    cb = fig.colorbar(im, ax=axs[0], pad=0.01, fraction=0.03)
    cb.set_label("humedad [% b.h.]", color=gr.TINTA_2)
    cb.set_ticks([0, 5, 10, 15, 30, 45, 60, 72])
    cb.outline.set_visible(False)
    axs[0].set_title("Humedad de cada capa (rojo: más seca que el 15 %; azul: más húmeda)", fontsize=10, pad=16)
    im2 = axs[1].imshow(T, origin="lower", aspect="auto", extent=ext, cmap=RAMPA_NARANJA, vmin=20,
                        vmax=105, interpolation="nearest")
    axs[1].contour(np.linspace(0, 36, T.shape[1]), np.arange(nz) + 0.5, T, levels=[55, 70],
                   colors=[gr.TINTA_2], linewidths=0.9)
    cb2 = fig.colorbar(im2, ax=axs[1], pad=0.01, fraction=0.03)
    cb2.set_label("temperatura [°C]", color=gr.TINTA_2)
    cb2.outline.set_visible(False)
    axs[1].set_title("Temperatura de cada capa (líneas: 55 y 70 °C)", fontsize=10, pad=16)
    for ax in axs:
        ax.grid(False)
        for k in (1, 2):
            ax.axvline(12 * k, color=gr.SUPERFICIE, lw=2)
        ax.set_yticks([0.5, nz - 0.5])
        ax.set_yticklabels(["abajo\n(entra el aire)", "arriba"], fontsize=8)
        for k in range(3):
            ax.text(12 * k + 6, nz + 0.1, f"piso {k + 1}", ha="center", va="bottom", fontsize=8, color=gr.TINTA_3)
        gr.coma(ax, "x")
    axs[1].set_xlabel("recorrido del producto en el secador [m]")
    gr.titulo(fig, "Al 15 % casi todo el secado pasa en el piso 3: abajo el guano queda sobresecado y "
                   "caliente, arriba sigue húmedo",
              f"Punto con aire a {N(P['T15'])} °C. Al piso 1 el aire llega casi saturado y solo calienta el guano. "
              f"El lecho se dibuja en {nz} capas de igual masa; al caer de un piso a otro el guano se mezcla.", y=0.93)
    gr.guardar(fig, ruta("02_capas_del_lecho.png"))


# =============================================================================== 03 ventana
def _malla(V, clave, f=lambda x: x):
    T = np.array(V["T"], float)
    v = np.array(V["v"], float)
    Z = np.zeros((len(T), len(v)))
    for i, fila in enumerate(V["filas"]):
        for j, r in enumerate(fila):
            Z[i, j] = f(r[clave])
    return v, T, Z


def fig_ventana(V, P):
    v, T, H = _malla(V, "hum_out", lambda x: 100 * x)
    _, _, HR = _malla(V, "HR_exh", lambda x: 100 * x)
    _, _, t55 = _malla(V, "t55_med")
    fig, ax = plt.subplots(figsize=(10.5, 6.0))
    # tres zonas suaves: sobresecado, en rango (12-17 %) y húmedo
    zonas = ["#f5d5d4", "#e9ece8", "#d6e6f8"]
    ax.contourf(v, T, H, levels=[-1, 12, 17, 100], colors=zonas)
    finas = ax.contour(v, T, H, levels=[2, 5, 10, 20, 25, 30], colors=[gr.TINTA_3], linewidths=0.6)
    ax.clabel(finas, fmt=lambda x: f"{N(x)} %", fontsize=7.4, inline_spacing=3)
    c15 = ax.contour(v, T, H, levels=[15], colors=[gr.TINTA], linewidths=1.6)
    ax.clabel(c15, fmt=lambda x: "15 %", fontsize=8, inline_spacing=3)
    chr_ = ax.contour(v, T, HR, levels=[90], colors=[gr.NARANJA], linewidths=1.6)
    ax.clabel(chr_, fmt=lambda x: "escape con HR 90 %", fontsize=7.6, inline_spacing=2)
    c55 = ax.contour(v, T, t55, levels=[60], colors=[gr.AZUL], linewidths=1.6)
    ax.clabel(c55, fmt=lambda x: "60 min > 55 °C (promedio)", fontsize=7.6, inline_spacing=2)
    for x0, x1 in ((0.2, V["v_capa_40"]), (V["v_capa_20"], 0.9)):
        ax.fill_betweenx([96, 150], x0, x1, facecolor="none", edgecolor=gr.EJE, hatch="////", lw=0, zorder=1.2)
    ax.text(0.5 * (0.2 + V["v_capa_40"]), 148.5, "capa\n> 40 mm", ha="center", va="top", fontsize=7.8,
            color=gr.TINTA_2, zorder=5)
    ax.text(0.5 * (V["v_capa_20"] + 0.9), 148.5, "capa < 20 mm", ha="center", va="top", fontsize=7.8,
            color=gr.TINTA_2, zorder=5)
    ax.text(0.71, 136, "producto sobresecado (< 12 %)", fontsize=9, color=gr.TINTA, ha="center", zorder=5,
            bbox=dict(boxstyle="square,pad=0.3", fc=zonas[0], ec="none"))
    ax.text(0.86, 98.5, "producto húmedo (> 17 %)", fontsize=9, color=gr.TINTA, ha="right", zorder=5,
            bbox=dict(boxstyle="square,pad=0.3", fc=zonas[2], ec="none"))
    sd = P["diseno"]["resumen"]
    ax.plot(sd["vel"], sd["T_aire"], "o", ms=9, color=gr.TINTA, mec=gr.SUPERFICIE, mew=2, zorder=6)
    ax.annotate(f"diseño Rev. E: {N(sd['T_aire'])} °C y {N(sd['vel'], 2)} m/min\n"
                f"→ sale casi seco (< 2 %)", (sd["vel"], sd["T_aire"]), xytext=(12, -4),
                textcoords="offset points", fontsize=8.2, color=gr.TINTA, va="top", zorder=6)
    sa = P["ajustado"]["resumen"]
    ax.plot(sa["vel"], sa["T_aire"], "o", ms=9, color=gr.TINTA, mec=gr.SUPERFICIE, mew=2, zorder=6)
    ax.annotate(f"15 % con {N(sa['T_aire'])} °C", (sa["vel"], sa["T_aire"]), xytext=(-12, -14),
                textcoords="offset points", fontsize=8.2, color=gr.TINTA, ha="right", zorder=6)
    ax.set_xlim(0.2, 0.9)
    ax.set_ylim(96, 150)
    ax.set_xlabel("velocidad de las bandas [m/min]")
    ax.set_ylabel("temperatura del aire a la entrada (TT-01) [°C]")
    ax.grid(False)
    gr.coma(ax)
    gr.titulo(fig, "La humedad de salida la fija la temperatura del aire; la velocidad de las bandas casi no la mueve",
              "1.000 kg/h al 72 %, 25 % de recirculación, 18 °C. Líneas grises: humedad de salida. Debajo de la línea "
              "naranja el escape sale con HR > 90 %; a la izquierda de la azul el guano pasa, en promedio, 1 h sobre "
              "55 °C. "
              "Rayado: capa fuera de 20-40 mm.", y=0.93)
    gr.guardar(fig, ruta("03_ventana_de_operacion.png"))


# =============================================================================== 04 autoridad
def fig_autoridad(V, P):
    v, T, H = _malla(V, "hum_out", lambda x: 100 * x)
    fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.4), gridspec_kw=dict(wspace=0.22))
    ax = axs[0]
    sel = [(100, gr.AZUL), (105, gr.NARANJA), (110, gr.AGUA), (135, gr.AMARILLO)]
    ax.axhspan(12, 17, color=gr.GRILLA, alpha=0.7, lw=0)
    ax.text(0.205, 17.4, "rango aceptado 12-17 %", fontsize=7.8, color=gr.TINTA_2)
    for Tv, col in sel:
        i = list(T).index(Tv)
        ax.plot(v, H[i], color=col, marker="o", ms=4, mec=gr.SUPERFICIE, mew=1)
        gr.rotulo_fin(ax, v[-1], H[i][-1], f"{Tv} °C", col)
    ax.axvspan(V["v_capa_40"], V["v_capa_20"], color=gr.AZUL, alpha=0.05, lw=0)
    ax.text(0.5 * (V["v_capa_40"] + V["v_capa_20"]), 29, "capa 20-40 mm", ha="center", fontsize=7.8,
            color=gr.TINTA_2)
    ax.set_xlim(0.2, 0.9)
    ax.set_ylim(0, 30)
    ax.set_xlabel("velocidad de las bandas [m/min]")
    ax.set_ylabel("humedad a la salida [% b.h.]")
    ax.set_title("Lo que hace el lazo MIC-01 del informe (mueve las bandas)", fontsize=10)
    gr.coma(ax)
    ax = axs[1]
    int(np.argmin(np.abs(v - 0.37))) if 0.37 in v else None
    Hm = np.array([np.interp(0.37, v, H[i]) for i in range(len(T))])
    ax.axhspan(12, 17, color=gr.GRILLA, alpha=0.7, lw=0)
    ax.plot(T, Hm, color=gr.AZUL, marker="o", ms=4, mec=gr.SUPERFICIE, mew=1)
    ax.set_xlim(95, 150)
    ax.set_ylim(0, 30)
    ax.set_xlabel("temperatura del aire a la entrada [°C]")
    ax.set_title("Lo que pasa si se mueve la temperatura del aire (bandas a 0,37 m/min)", fontsize=10)
    gr.coma(ax)
    T15 = P["T15"]
    ax.axvline(T15, color=gr.TINTA_3, lw=0.9)
    ax.text(T15 + 0.8, 26, f"{N(T15)} °C → 15 %", fontsize=8, color=gr.TINTA_2)
    ax.axvline(135, color=gr.TINTA_3, lw=0.9)
    ax.text(135.8, 26, "diseño 135 °C", fontsize=8, color=gr.TINTA_2)
    # pendiente cerca del 15 %
    i0 = np.searchsorted(T, T15)
    pend = (Hm[i0] - Hm[i0 - 1]) / (T[i0] - T[i0 - 1])
    ax.text(T15 + 0.8, 21, f"pendiente ≈ {N(pend, 1)} puntos/°C", fontsize=8, color=gr.TINTA_2)
    gr.titulo(fig, "Cerca del 15 %, mover las bandas casi no cambia la humedad; 1 °C de aire la cambia unos 2 puntos",
              "Humedad del guano a la salida en régimen. 1.000 kg/h al 72 %, 25 % de recirculación, 18 °C.", y=0.95)
    gr.guardar(fig, ruta("04_que_controla_la_humedad.png"))


# =============================================================================== 05 temperatura necesaria
def fig_temperatura(TN, P):
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 4.2), gridspec_kw=dict(wspace=0.3))
    ph = TN["por_humedad"]
    hum = [100 * r["humedad_entrada"] for r in ph]
    Tn = [r["T_aire"] for r in ph]
    ax = axs[0]
    ax.plot(hum, Tn, color=gr.AZUL, marker="o", ms=5, mec=gr.SUPERFICIE, mew=1.2)
    ax.axhline(135, color=gr.TINTA_3, lw=0.9)
    ax.text(hum[0], 136, "diseño 135 °C", fontsize=7.8, color=gr.TINTA_2, va="bottom")
    ax.axhline(150, color=gr.TINTA_3, lw=0.9)
    ax.text(hum[0], 151, "máximo 150 °C", fontsize=7.8, color=gr.TINTA_2, va="bottom")
    ax.set_ylim(70, 160)
    ax.set_xticks(hum)
    ax.set_xlabel("humedad del guano fresco [% b.h.]")
    ax.set_ylabel("temperatura del aire necesaria [°C]")
    ax.set_title("Según la humedad del guano", fontsize=10)
    for x, y in zip(hum, Tn):
        if x in (65.0, 72.0, 78.0):
            ax.annotate(f"{N(y)} °C", (x, y), xytext=(0, 8), textcoords="offset points", ha="center",
                        fontsize=8, color=gr.TINTA_2)
    gr.coma(ax)
    pa_ = TN["por_alimentacion"]
    al = [r["alimentacion"] for r in pa_]
    Ta = [r["T_aire"] for r in pa_]
    ax = axs[1]
    ax.plot(al, Ta, color=gr.AZUL)
    for x, y, r in zip(al, Ta, pa_):
        cerr = r.get("cd03") in ("cerrada", "cicla")
        ax.plot([x], [y], marker="o", ms=5.5, color=gr.SUPERFICIE if cerr else gr.AZUL, mec=gr.AZUL, mew=1.3)
    if any(r.get("cd03") in ("cerrada", "cicla") for r in pa_):
        x0 = min(r["alimentacion"] for r in pa_ if r.get("cd03") in ("cerrada", "cicla"))
        ax.text(x0 - 20, 80, "huecos: CD-03 cerrada\npor su regla (> 45 g/kg)", fontsize=7.6, color=gr.TINTA_2,
                ha="right", va="bottom")
    ax.axhline(135, color=gr.TINTA_3, lw=0.9)
    ax.axhline(150, color=gr.TINTA_3, lw=0.9)
    ax.set_ylim(70, 160)
    ax.set_xlabel("caudal de guano [kg/h] (bandas a 0,37 m/min)")
    ax.set_title("Según el caudal de guano", fontsize=10)
    for x, y in zip(al, Ta):
        if x in (700.0, 1000.0, 1400.0):
            ax.annotate(f"{N(y)} °C", (x, y), xytext=(0, 8), textcoords="offset points", ha="center",
                        fontsize=8, color=gr.TINTA_2)
    gr.coma(ax)
    ax = axs[2]
    c15 = [r["comb"] for r in ph]
    ax.plot(hum, c15, color=gr.AZUL, marker="o", ms=5, mec=gr.SUPERFICIE, mew=1.2)
    c135 = P["diseno"]["resumen"]["comb"]
    ax.axhline(c135, color=gr.TINTA_3, lw=0.9)
    ax.text(hum[0], c135 + 3, f"a 135 °C: {N(c135)} kg/h", fontsize=7.8, color=gr.TINTA_2, va="bottom")
    ax.axhline(314, color=gr.TINTA_3, lw=0.9)
    ax.text(hum[0], 317, "informe sin recirculación: 314 kg/h", fontsize=7.8, color=gr.TINTA_2, va="bottom")
    ax.set_ylim(150, 340)
    ax.set_xticks(hum)
    ax.set_xlabel("humedad del guano fresco [% b.h.]")
    ax.set_ylabel("cáscara de arroz [kg/h]")
    ax.set_title("Cáscara que se quema para dejarlo al 15 %", fontsize=10)
    gr.coma(ax)
    gr.titulo(fig, "Para dejar el guano al 15 % alcanza con aire a 90-115 °C; los 135 °C del diseño solo hacen "
                   "falta con mucho más guano",
              "Temperatura de entrada (TT-01) que deja 15 % a la salida, con 25 % de recirculación (la CD-03 se cierra "
              "por su regla del plano 18 cuando el escape pasa de 45 g/kg) y 18 °C. Salvo indicación, 1.000 kg/h al "
              "72 % y bandas a 0,37 m/min.", y=0.95)
    gr.guardar(fig, ruta("05_temperatura_necesaria.png"))


# =============================================================================== 06 capacidad
def fig_capacidad(C, P):
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    T = C["T"]
    a1 = [r["alimentacion"] for r in C["vel_fija"]]
    a2 = [r["alimentacion"] for r in C["capa_30"]]
    ax.plot(T, a1, color=gr.AZUL)
    for x, y, r in zip(T, a1, C["vel_fija"]):
        cerr = r.get("cd03") in ("cerrada", "cicla")
        ax.plot([x], [y], marker="o", ms=6, color=gr.SUPERFICIE if cerr else gr.AZUL, mec=gr.AZUL, mew=1.4)
    t_cierre = min([x for x, r in zip(T, C["vel_fija"]) if r.get("cd03") in ("cerrada", "cicla")] or [None])
    if t_cierre:
        ax.annotate("desde acá el escape pasa de 45 g/kg y la CD-03 se cierra\n(puntos huecos): más aire fresco, "
                    "más secado", (t_cierre, a1[T.index(t_cierre)]), xytext=(10, -8), textcoords="offset points",
                    fontsize=7.8, color=gr.TINTA_2, va="top")
    ax.axhline(1000, color=gr.TINTA_3, lw=0.9)
    ax.text(T[-1], 988, "pedido: 1.000 kg/h (8 t en un turno de 8 h)", fontsize=7.8, color=gr.TINTA_2, va="top",
            ha="right")
    # la cinta de alimentación del plano 12 (Rev. D) llega a 2.590 kg/h a 0,10 m/s: no limita la capacidad
    ax.text(T[-1], 1012, "cinta de alimentación (M8): 1.000 kg/h a 3,9 cm/s; máx. 2.590 kg/h a 0,10 m/s",
            fontsize=7.8, color=gr.TINTA_2, va="bottom", ha="right")
    i135 = T.index(135.0)
    ax.annotate(f"{N(a1[i135])} kg/h", (135, a1[i135]), xytext=(-8, 8), textcoords="offset points",
                ha="right", fontsize=8.4, color=gr.TINTA)
    abiertos = [(x, y) for x, y, r in zip(T, a1, C["vel_fija"]) if r.get("cd03") not in ("cerrada", "cicla")]
    cerrados = [(x, y) for x, y, r in zip(T, a1, C["vel_fija"]) if r.get("cd03") in ("cerrada", "cicla")]
    tramo = cerrados if len(cerrados) >= 2 else abiertos
    pend = (tramo[-1][1] - tramo[0][1]) / (tramo[-1][0] - tramo[0][0])
    ax.text(0.03, 0.93, f"≈ {N(pend)} kg/h más por cada grado de aire", transform=ax.transAxes, fontsize=8.4,
            color=gr.TINTA_2, va="top")
    ax.set_xlim(T[0] - 2, T[-1] + 2)
    ax.set_ylim(900, 1700)
    ax.set_xlabel("temperatura del aire a la entrada [°C]")
    ax.set_ylabel("guano al 72 % que sale al 15 % [kg/h]")
    gr.coma(ax)
    dif = max(abs(x - y) for x, y in zip(a1, a2))
    B = cargar("bordes")
    cap10 = next((c["capacidad"]["alimentacion"] for c in B["casos"] if abs(c["bypass_pila"] - 0.10) < 1e-9), None) \
        if B else None
    extra = (f" Si un 10 % del aire sube por los bordes sin tocar el guano, baja a {N(round(cap10, -1))} kg/h."
             if cap10 else "")
    gr.titulo(fig, f"A 135 °C el SC-4 puede secar unos {N(round(a1[i135], -1))} kg/h al 15 %: "
                   f"{N(100 * (a1[i135] / 1000 - 1))} % más de lo pedido",
              "Máximo caudal de guano que sale al 15 %, con 26.600 kg/h de aire, 18 °C y la CD-03 al 25 % con su "
              "regla. Da lo mismo con las bandas fijas a 0,37 m/min o siguiendo al caudal con capa de 30 mm "
              f"(diferencia < {N(max(dif, 1))} kg/h).{extra}", y=0.93)
    gr.guardar(fig, ruta("06_capacidad.png"))


# =============================================================================== 07 recirculación
def fig_recirculacion(R):
    fig, axs = plt.subplots(1, 3, figsize=(12.5, 4.2), gridspec_kw=dict(wspace=0.3))
    rec = [100 * x for x in R["recirc"]]
    series = [("diseno", "18 °C (diseño)", gr.AZUL), ("invierno", "julio", gr.NARANJA),
              ("verano", "enero", gr.AGUA)]
    for clave, _nombre, col in series:
        d = R[clave]
        axs[0].plot(rec, [x["a15"]["comb"] for x in d], color=col, marker="o", ms=4, mec=gr.SUPERFICIE, mew=1)
        axs[1].plot(rec, [100 * x["a15"]["HR_mix"] for x in d], color=col)
        for r_, x in zip(rec, d):
            niebla = x["a15"]["niebla_mix"] > 1e-5 or x["a15"]["HR_mix"] >= 0.995
            axs[1].plot([r_], [100 * x["a15"]["HR_mix"]], marker="o", ms=4.5, color=gr.SUPERFICIE if niebla else col,
                        mec=col, mew=1.2)
        axs[2].plot(rec, [x["a135"]["comb"] for x in d], color=col, marker="o", ms=4, mec=gr.SUPERFICIE, mew=1)
    axs[0].set_title("Cáscara al 15 % (aire ajustado)", fontsize=10)
    axs[0].set_ylabel("cáscara de arroz [kg/h]")
    axs[1].set_title("Humedad relativa en la cámara de mezcla", fontsize=10)
    axs[1].set_ylabel("HR de la mezcla aire fresco + recirculado [%]")
    axs[1].axhline(100, color=gr.TINTA_3, lw=0.9)
    axs[1].text(0, 101, "saturada (huecos: niebla y condensado)", fontsize=7.8, color=gr.TINTA_2, va="bottom")
    axs[1].set_ylim(40, 108)
    axs[2].set_title("Cáscara con aire a 135 °C (producto sobresecado)", fontsize=10)
    axs[2].set_ylabel("cáscara de arroz [kg/h]")
    for ax in axs:
        ax.set_xlabel("recirculación (compuerta CD-03) [%]")
        ax.axvline(25, color=gr.TINTA_3, lw=0.9)
        gr.coma(ax)
    axs[0].set_ylim(180, 335)
    axs[2].set_ylim(180, 335)
    axs[0].text(25.6, axs[0].get_ylim()[1], "25 %\n(plano 18)", fontsize=7.8, color=gr.TINTA_2, va="top")
    h = [Line2D([], [], color=c, marker="o", ms=4, label=n) for _, n, c in series]
    axs[2].legend(handles=h, loc="upper right")
    i25 = R["recirc"].index(0.25)
    ah = lambda clave, caso: 100 * (1 - R[clave][i25][caso]["comb"] / R[clave][0][caso]["comb"])
    gr.titulo(fig, f"Al 15 % recircular casi no ahorra: el 25 % de la CD-03 ahorra {N(ah('diseno', 'a15'), 1)} % de "
                   f"cáscara a 18 °C, {N(ah('invierno', 'a15'), 1)} % en julio con la cámara saturada y en enero gasta "
                   f"{N(-ah('verano', 'a15'), 1)} % más; solo rinde a 135 °C ({N(ah('diseno', 'a135'))} %)",
              "1.000 kg/h al 72 %, bandas a 0,37 m/min, la CD-03 fija en cada valor. Clima del turno de Crespo "
              "(estación Paraná Aero). Los dos paneles de cáscara usan la misma escala.", y=0.97)
    gr.guardar(fig, ruta("07_recirculacion.png"))


# =============================================================================== 08 sensibilidad
def fig_sensibilidad(S, P):
    base = S["base"]["T15"]
    filas = sorted(S["filas"], key=lambda f: abs(f["a"]["T15"] - f["b"]["T15"]))
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 5.0), gridspec_kw=dict(width_ratios=[1.45, 1], wspace=0.35))
    ax = axs[0]
    for i, f in enumerate(filas):
        da = f["a"]["T15"] - base
        db = f["b"]["T15"] - base
        for dv, lab, col in ((da, f["etiqueta_a"], gr.NARANJA), (db, f["etiqueta_b"], gr.AZUL)):
            if abs(dv) < 0.05 and abs(da if dv is db else db) >= 0.05:
                continue            # es el caso base de esa fila
            ax.barh(i, dv, height=0.55, color=col, edgecolor=gr.SUPERFICIE, lw=1.2)
            ha = "left" if dv >= 0 else "right"
            ax.text(dv + (0.4 if dv >= 0 else -0.4), i, f"{lab}: {'+' if dv >= 0 else '−'}{N(abs(dv), 1)} K",
                    va="center", ha=ha, fontsize=7.8, color=gr.TINTA_2)
    ax.set_yticks(range(len(filas)))
    cortos = {"Aire que sube por los bordes de los tres pisos": "Aire por los bordes (no toca ningún piso)",
              "Aire que esquiva cada banda (se mezcla entre pisos)": "Aire que esquiva cada banda"}
    ax.set_yticklabels([cortos.get(f["nombre"], f["nombre"]) for f in filas], fontsize=8.5)
    ax.axvline(0, color=gr.TINTA_3, lw=0.9)
    lim = max(abs(f["a"]["T15"] - base) for f in filas)
    lim = max(lim, max(abs(f["b"]["T15"] - base) for f in filas)) + 6
    ax.set_xlim(-lim, lim)
    ax.set_xlabel(f"cambio de la temperatura de aire necesaria para el 15 % [K] (base {N(base, 1)} °C)")
    ax.grid(axis="y", visible=False)
    gr.coma(ax, "x")
    ax.set_title("Qué mueve el punto de operación", fontsize=10)
    ax = axs[1]
    g = S["grumos"]
    d0 = [x["d0_mm"] for x in g]
    h = [100 * x["hum135"] for x in g]
    ax.plot(d0, h, color=gr.AZUL, marker="o", ms=5, mec=gr.SUPERFICIE, mew=1.2)
    ax.axhline(15, color=gr.TINTA_3, lw=0.9)
    ax.text(d0[0], 15.6, "objetivo 15 %", fontsize=7.8, color=gr.TINTA_2, va="bottom")
    ax.set_xlabel("tamaño de grumo que deja el esparcidor [mm]")
    ax.set_ylabel("humedad a la salida [% b.h.]")
    ax.set_title("Diseño a 135 °C: solo falla si los grumos son grandes", fontsize=10)
    gr.coma(ax)
    gr.titulo(fig, "La temperatura necesaria la mueven los caudales, el aire que se escapa por los bordes, el grumo "
                   "y la humedad del guano; la cinética casi no la cambia",
              "Izquierda: cuánto cambia la temperatura de aire que deja 15 % al mover un dato por vez (base: 1.000 kg/h "
              "al 72 %, 26.600 kg/h de aire, grumo de 10 mm, CD-03 fija al 25 %). Derecha: humedad de salida en el "
              "punto de diseño (135 °C) según el tamaño de grumo.", y=0.95)
    gr.guardar(fig, ruta("08_sensibilidad.png"))


# =============================================================================== 09 clima
def fig_clima(CL):
    M = CL["meses"]
    fig, axs = plt.subplots(1, 2, figsize=(12.5, 4.4), gridspec_kw=dict(wspace=0.25))
    x = np.arange(12)
    nombres = [m["nombre"] for m in M]
    ax = axs[0]
    hr15 = [100 * m["a15"]["HR_mix"] for m in M]
    ax.plot(x, hr15, color=gr.AZUL)
    for xi, m in zip(x, M):
        cerr = m["a15"].get("cd03") in ("cerrada", "cicla")
        sat = m["a15"]["niebla_mix"] > 1e-5 or m["a15"]["HR_mix"] >= 0.995
        ax.plot([xi], [100 * m["a15"]["HR_mix"]], marker="s" if cerr else "o", ms=5.5,
                color=gr.SUPERFICIE if (cerr or sat) else gr.AZUL, mec=gr.AZUL, mew=1.3)
    ax.axhline(100, color=gr.TINTA_3, lw=0.9)
    ax.text(-0.3, 101, "saturada: niebla y condensado antes del intercambiador", fontsize=7.8, color=gr.TINTA_2,
            va="bottom")
    ax.text(11.3, 42, "cuadrados: la CD-03 se cierra por su regla\n(escape > 45 g/kg) y entra solo aire de afuera",
            fontsize=7.6, color=gr.TINTA_2, va="bottom", ha="right")
    ax.set_xticks(x)
    ax.set_xticklabels(nombres)
    ax.set_ylim(40, 110)
    ax.set_ylabel("humedad relativa de la mezcla [%]")
    ax.set_title("Cámara de mezcla con la CD-03 al 25 % y su regla (al 15 %)", fontsize=10)
    gr.coma(ax, "y")
    ax = axs[1]
    w = 0.38
    a = [m["a135"]["cascara_t_mes"] for m in M]
    b = [m["a15"]["cascara_t_mes"] for m in M]
    ax.bar(x - w / 2 - 0.01, a, width=w, color=gr.NARANJA, edgecolor=gr.SUPERFICIE, lw=1, label="a 135 °C (diseño)")
    ax.bar(x + w / 2 + 0.01, b, width=w, color=gr.AZUL, edgecolor=gr.SUPERFICIE, lw=1, label="aire ajustado al 15 %")
    ax.set_xticks(x)
    ax.set_xticklabels(nombres)
    ax.set_ylabel("cáscara de arroz [t/mes]")
    ax.set_title("Cáscara por mes (250 días de 8 h al año)", fontsize=10)
    ax.legend(loc="upper center", ncol=2)
    ax.set_ylim(0, max(a) * 1.18)
    gr.coma(ax, "y")
    ta, tb = sum(a), sum(b)
    t15 = [m["a15"]["T_aire"] for m in M]
    B = cargar("bordes")
    extra = ""
    if B:
        a10 = B["anual"].get("0.10")
        if a10:
            extra = (f" Si un 10 % del aire sube por los bordes sin tocar el guano, el ahorro baja a "
                     f"{N(a10['t135'] - a10['t15'])} t.")
    LARGO = dict(Ene="enero", Feb="febrero", Mar="marzo", Abr="abril", May="mayo", Jun="junio", Jul="julio",
                 Ago="agosto", Sep="septiembre", Oct="octubre", Nov="noviembre", Dic="diciembre")
    sat = [LARGO.get(m["nombre"], m["nombre"]) for m in M
           if m["a15"]["niebla_mix"] > 1e-5 or m["a15"]["HR_mix"] >= 0.995]
    txt_sat = (f"; en {' y '.join(sat)} la recirculación satura la cámara de mezcla" if sat else "")
    gr.titulo(fig, f"Ajustando el aire al 15 % se queman {N(ta - tb)} t menos de cáscara por año "
                   f"({N(100 * (1 - tb / ta))} %){txt_sat}",
              f"Total anual: {N(ta)} t a 135 °C contra {N(tb)} t ajustando el aire (el informe estima 575 t con "
              f"recirculación). La temperatura de aire que deja 15 % casi no cambia en el año ({N(min(t15), 1)} a "
              f"{N(max(t15), 1)} °C). Clima del turno de 8 h de Crespo, 1.000 kg/h al 72 %.{extra}", y=0.95)
    gr.guardar(fig, ruta("09_clima_anual.png"))


# =============================================================================== 10 guías
def fig_guias(P):
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    casos = [("diseno", "diseño: 135 °C, 1.000 kg/h", gr.NARANJA),
             ("ajustado", f"{N(P['T15'])} °C, 1.000 kg/h (sale al 15 %)", gr.AZUL),
             ("capacidad", f"135 °C, {N(round(P['A_cap'], -1))} kg/h (sale al 15 %)", gr.AGUA)]
    w = 0.26
    x = np.arange(3)
    for i, (clave, nombre, col) in enumerate(casos):
        Tin = P[clave]["resumen"]["Tin"]
        pos = x + (i - 1) * (w + 0.02)
        ax.bar(pos, Tin, width=w, color=col, edgecolor=gr.SUPERFICIE, lw=1, label=nombre)
        for p_, t_ in zip(pos, Tin):
            ax.text(p_, t_ + 2, N(t_), ha="center", va="bottom", fontsize=7.8, color=gr.TINTA_2)
    ax.axhline(pa.UHMW_SERVICIO_CONTINUO, color=gr.TINTA_3, lw=0.9)
    ax.text(2.52, pa.UHMW_SERVICIO_CONTINUO, "UHMW-PE:\n80 °C en uso continuo", ha="left",
            fontsize=7.8, color=gr.TINTA_2, va="center")
    ax.axhline(pa.UHMW_FUSION, color=gr.TINTA_3, lw=0.9)
    ax.text(2.52, pa.UHMW_FUSION, "UHMW-PE:\nfunde a 130-135 °C", ha="left", fontsize=7.8,
            color=gr.TINTA_2, va="center")
    ax.set_xticks(x)
    ax.set_xticklabels(["piso 1 (arriba)", "piso 2", "piso 3 (abajo)"])
    ax.set_ylabel("aire debajo de la banda [°C]")
    ax.set_ylim(0, 160)
    ax.set_xlim(-0.5, 3.15)
    ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.1), fontsize=8)
    ax.grid(axis="x", visible=False)
    gr.coma(ax, "y")
    gr.titulo(fig, "Las guías de UHMW-PE quedan en el aire que entra a cada piso: en el piso 3, a 100-135 °C",
              "Temperatura del aire bajo cada banda, donde van las guías. El informe (7.2.5) supone que la guía "
              "queda en la zona de aire más frío.", y=0.93)
    gr.guardar(fig, ruta("10_guias_uhmw.png"))


# =============================================================================== 11 higiene
def fig_higiene(P):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True, gridspec_kw=dict(wspace=0.08))
    hd = P["diseno"]["resumen"]["hum_out"]
    casos = [("diseno", f"Diseño: aire a {N(P['diseno']['resumen']['T_aire'])} °C (sale "
                        + (f"al {N(100 * hd, 1)} %)" if hd >= 0.02 else "casi seco)")),
             ("ajustado", f"Aire a {N(P['T15'])} °C (sale al 15 %)")]
    for ax, (clave, nombre) in zip(axs, casos):
        d = P[clave]
        s = d["resumen"]
        for p in d["pisos"]:
            t = np.array(p["t_min"])
            Tc = np.array(p["capas_T"])
            ax.plot(t, Tc[0], color=gr.NARANJA)
            ax.plot(t, Tc[-1], color=gr.AZUL)
            ax.plot(t, np.array(p["T_med"]), color=gr.TINTA_3, lw=1.2)
        for lim in (55, 70):
            ax.axhline(lim, color=gr.TINTA_3, lw=0.9)
            ax.text(0.5, lim + 1, f"{lim} °C", fontsize=7.8, color=gr.TINTA_2, va="bottom")
        tr = s["t_res"]
        for k in (1, 2):
            ax.axvline(tr * k / 3, color=gr.EJE, lw=0.8)
        for k in range(3):
            ax.text(tr * (k + 0.5) / 3, 152, f"piso {k + 1}", ha="center", fontsize=8, color=gr.TINTA_3)
        ax.set_xlim(0, tr)
        ax.set_ylim(0, 150)
        ax.set_xlabel("tiempo desde la entrada [min]")
        ax.set_title(nombre, fontsize=10, pad=18)
        gr.coma(ax)
        txt = (f"tiempo sobre 55 °C: promedio {N(s['t55_med'])} min · capa de arriba {N(s['t55_peor'])} min\n"
               f"tiempo sobre 70 °C: promedio {N(s['t70_med'])} min · capa de arriba {N(s['t70_peor'])} min")
        ax.text(0.98, 0.03, txt, transform=ax.transAxes, va="bottom", ha="right", fontsize=8, color=gr.TINTA,
                bbox=dict(boxstyle="square,pad=0.4", fc=gr.SUPERFICIE, ec="none", alpha=0.92), zorder=7)
    axs[0].set_ylabel("temperatura del guano [°C]")
    h = [Line2D([], [], color=gr.NARANJA, label="capa de abajo (le llega el aire primero)"),
         Line2D([], [], color=gr.AZUL, label="capa de arriba (peor caso)"),
         Line2D([], [], color=gr.TINTA_3, lw=1.2, label="promedio de las capas")]
    fig.legend(handles=h, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 0.0), fontsize=8.2)
    HG = cargar("higiene")
    extra = ""
    if HG:
        f3 = next(f for f in HG["filas"] if f["nz"] == 3)
        extra = (f" Con capas de un grumo, los de arriba llegan a {N(f3['Tmax_arriba'][2])} °C; al salir tienen "
                 f"{N(100 * f3['hum_arriba'])}-{N(100 * max(f['hum_arriba'] for f in HG['filas']))} % de humedad y "
                 f"los de abajo {N(100 * min(f['hum_abajo'] for f in HG['filas']), 1)}-"
                 f"{N(100 * f3['hum_abajo'], 1)} %: el 15 % es un promedio.")
    sa = P["ajustado"]["resumen"]
    gr.titulo(fig, f"Al 15 % el guano pasa unos {N(sa['t55_med'])} min sobre 55 °C y los grumos de arriba no llegan "
                   "a 60 °C: la higienización del informe (> 55 °C durante 1 h) solo se cumple sobresecando",
              "Historia de temperatura del guano dentro del secador, con el lecho en 8 capas de igual masa (un tercio "
              "de grumo cada una). Al caer de un piso a otro las capas se mezclan; la capa de arriba es el guano que "
              f"siempre queda arriba (caso más desfavorable).{extra}", y=0.99)
    gr.guardar(fig, ruta("11_higiene.png"))


# =============================================================================== 12 dinámica
def fig_dinamica(DY):
    casos = DY["casos"]
    colores = [gr.TINTA_3, gr.NARANJA, gr.AZUL, gr.AGUA]
    fig, axs = plt.subplots(3, 1, figsize=(11.5, 8.0), sharex=True,
                            gridspec_kw=dict(height_ratios=[1.6, 1, 1], hspace=0.22))
    for c, col in zip(casos, colores):
        t = np.array(c["t"])
        axs[0].plot(t, 100 * np.array(c["hum_real"]), color=col, lw=1.6 if col != gr.TINTA_3 else 1.2)
    axs[0].axhspan(12, 17, color=gr.GRILLA, alpha=0.6, lw=0)
    axs[0].axhline(20, color=gr.TINTA_3, lw=0.9)
    axs[0].text(8, 20.4, "alarma > 20 % durante 15 min (para el dosificador)", ha="right", fontsize=7.8,
                color=gr.TINTA_2, va="bottom")
    axs[0].set_ylabel("humedad a la salida [% b.h.]")
    axs[0].set_ylim(0, 46)
    axs[0].axvline(1, color=gr.EJE, lw=0.8)
    axs[0].text(1.04, 44.5, "a la hora 1 el guano pasa de 72 a 76 %", fontsize=7.8, color=gr.TINTA_2, va="top")
    axs[0].text(0.05, 12.4, "rango aceptado 12-17 %", fontsize=7.8, color=gr.TINTA_2, va="bottom")
    h = [Line2D([], [], color=col, label=c["nombre"]) for c, col in zip(casos, colores)]
    fig.legend(handles=h, loc="upper center", fontsize=8.2, ncol=2, bbox_to_anchor=(0.5, 0.0))
    c_inf = casos[1]
    axs[1].plot(np.array(c_inf["t"]), c_inf["v"], color=gr.NARANJA)
    axs[1].set_ylabel("bandas [m/min]")
    axs[1].set_ylim(0.15, 0.95)
    axs[1].axhline(0.2, color=gr.TINTA_3, lw=0.9)
    axs[1].axhline(0.9, color=gr.TINTA_3, lw=0.9)
    for c, col in zip(casos[2:], colores[2:]):
        axs[2].plot(np.array(c["t"]), c["T_aire"], color=col)
    axs[2].plot(np.array(casos[0]["t"]), casos[0]["T_aire"], color=gr.TINTA_3, lw=1.2)
    axs[2].set_ylabel("aire TT-01 [°C]")
    axs[2].set_xlabel("tiempo [h]")
    axs[2].set_xlim(0, 8)
    for ax in axs:
        gr.coma(ax)
    gr.titulo(fig, "Si el guano llega más húmedo, mover las bandas no alcanza; corregir la temperatura del aire sí",
              "Simulación en el tiempo (celdas que avanzan con la banda) con el lazo MIC-01: sensor de humedad en el "
              "sinfín de descarga, PLC cada 30 s. El lazo del informe va sin el ajuste anticipado por TT-04 (con él "
              "fue peor). El primer pico no lo evita ningún lazo que mida a la salida: el guano húmedo tarda 1,6 h en "
              "llegar.", y=0.95)
    gr.guardar(fig, ruta("12_control_dinamico.png"))


# =============================================================================== 14 energía
def fig_energia(E, P):
    filas = [("informe", "Memoria del informe (sin recirculación)"),
             ("diseno", "Modelo: diseño, 135 °C"),
             ("ajustado", f"Modelo: aire a {N(P['T15'])} °C (15 %)"),
             ("capacidad", f"Modelo: 135 °C con {N(round(P['A_cap'], -1))} kg/h")]
    partes = [("evaporar", "evaporar el agua", gr.AZUL),
              ("escape", "escape: aire y vapor calientes", gr.NARANJA),
              ("paredes", "paredes y ducto", gr.AGUA),
              ("sorcion", "agua ligada (sorción)", gr.AMARILLO),
              ("producto", "calentar el guano", gr.MAGENTA)]
    orden = ["evaporar", "producto", "sorcion", "paredes", "escape"]
    fig, ax = plt.subplots(figsize=(11.5, 4.1))
    for i, (clave, _nombre) in enumerate(filas):
        e = E[clave]
        x0 = 0.0
        y = len(filas) - 1 - i
        for p in orden:
            _, _, col = next(q for q in partes if q[0] == p)
            v = e[p]
            if v <= 0.05:
                continue
            ax.barh(y, v, left=x0, height=0.55, color=col, edgecolor=gr.SUPERFICIE, lw=1.5)
            if v > 60:
                ax.text(x0 + v / 2, y, N(v), ha="center", va="center", fontsize=8,
                        color=gr.TINTA if col in (gr.AMARILLO, gr.MAGENTA) else "#ffffff")
            x0 += v
        ax.text(x0 + 8, y, f"{N(e['Q_gen'])} kW · {N(100 * e['rendimiento'])} % para el guano", va="center",
                fontsize=8.2, color=gr.TINTA_2)
    ax.set_yticks(range(len(filas)))
    ax.set_yticklabels([n for _, n in filas][::-1], fontsize=8.5)
    ax.set_xlim(0, 1120)
    ax.set_xlabel("calor que entrega el generador al aire [kW]")
    ax.grid(axis="y", visible=False)
    gr.coma(ax, "x")
    h = [Patch(color=c, label=n) for p in orden for (q, n, c) in partes if q == p]
    ax.legend(handles=h, loc="upper center", ncol=5, bbox_to_anchor=(0.5, -0.2), fontsize=8)
    r = [100 * E[k]["rendimiento"] for k in ("diseno", "ajustado", "capacidad")]
    rm = [100 * E[k]["rendimiento_memoria"] for k in ("diseno", "ajustado", "capacidad")]
    gr.titulo(fig, f"El aire sale mucho más frío que lo que supone la memoria: el secador usa {N(min(r))}-{N(max(r))} % "
                   f"del calor para evaporar y calentar el guano, no {N(100 * E['informe']['rendimiento'])} %",
              "Destino del calor del generador. La memoria supone el escape a 65 °C; en el modelo el aire sale casi "
              "saturado mientras el guano tiene agua. El agua evaporada se cuenta desde la temperatura del guano; con la "
              f"cuenta de la memoria (cap. 6.3, el agua calentada como líquido hasta la salida) daría {N(min(rm))}-"
              f"{N(max(rm))} % y la memoria {N(100 * E['informe']['rendimiento_memoria'])} %.", y=0.95)
    gr.guardar(fig, ruta("14_balance_de_energia.png"))


# =============================================================================== todas
def todas():
    gr.estilo()
    P = cargar("perfiles")
    hechas = []
    if P:
        fig_perfiles(P)
        fig_capas(P)
        fig_guias(P)
        fig_higiene(P)
        hechas += ["01", "02", "10", "11"]
    V = cargar("ventana")
    if V and P:
        fig_ventana(V, P)
        fig_autoridad(V, P)
        hechas += ["03", "04"]
    TN = cargar("temperatura")
    if TN and P:
        fig_temperatura(TN, P)
        hechas.append("05")
    C = cargar("capacidad")
    if C and P:
        fig_capacidad(C, P)
        hechas.append("06")
    R = cargar("recirculacion")
    if R:
        fig_recirculacion(R)
        hechas.append("07")
    S = cargar("sensibilidad")
    if S and P:
        fig_sensibilidad(S, P)
        hechas.append("08")
    CL = cargar("clima")
    if CL:
        fig_clima(CL)
        hechas.append("09")
    DY = cargar("dinamica")
    if DY:
        fig_dinamica(DY)
        hechas.append("12")
    E = cargar("energia")
    if E and P:
        fig_energia(E, P)
        hechas.append("14")
    print("figuras:", ", ".join(hechas))


if __name__ == "__main__":
    todas()
