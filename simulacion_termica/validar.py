"""Validación del modelo.

1. Cinética de secado contra ensayos publicados de guano de ponedora en capa fina:
   - Ghaly y MacDonald (2012), Am. J. Biochem. Biotechnol. 8(2):128-142: estufa de tiro forzado a
     40, 50 y 60 °C, bandejas de 1, 2 y 3 cm, guano al 78,45 % b.h. (Tabla 3: tiempo hasta peso
     constante; Tabla 4: velocidad de secado de las primeras 2 h).
   - Liška y Kic (2011), Sci. Agric. Bohem. 42(2):79-86: estufa a 70 y 110 °C, muestras de 5 a 20 g
     (curvas de la Fig. 2 y velocidad inicial 0,85-1,00 g/g·h a 70 °C). El espesor de muestra no
     está informado: se supone 3 mm.
2. Cierre de los balances de masa y energía en varios puntos de operación.
3. Independencia de la malla (nx posiciones a lo largo de la banda × nz capas en el espesor).
4. Comparación con los números de la memoria de cálculo (informe Rev. E, cap. 6 y 15).

Uso:  python validar.py            (escribe resultados/validacion.json y figuras/13_validacion_cinetica.png)
"""
import json
import os
import time

import numpy as np

from secado import graficos as gr
from secado import parametros as pa
from secado import secador as sc
from secado.nucleo import secar_losa_horno

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "resultados")
FIG = os.path.join(AQUI, "figuras")
os.makedirs(RES, exist_ok=True)
os.makedirs(FIG, exist_ok=True)

P = pa.P_ATM
# ------------------------------------------------------------------ datos publicados
GHALY_X0 = 0.7845 / (1 - 0.7845)                      # 3,64 kg/kg b.s.
GHALY_RHO = 960.0                                     # kg/m³ (Tabla 1)
# Tabla 3: tiempo de secado [h] hasta peso constante y masa inicial de guano [g]
# (bandejas de 100 cm² de superficie, sección 2.1 del trabajo)
GHALY_TIEMPO = {(40, 1): 55, (40, 2): 106, (40, 3): 120, (50, 1): 44, (50, 2): 84, (50, 3): 90,
                (60, 1): 28, (60, 2): 52, (60, 3): 60}
GHALY_MASA_G = {(40, 1): 125.95, (40, 2): 224.70, (40, 3): 312.72, (50, 1): 129.16, (50, 2): 226.21,
                (50, 3): 314.28, (60, 1): 127.18, (60, 2): 227.86, (60, 3): 322.57}
GHALY_AREA = 0.01                                     # m²
# Tabla 4 evaluada en el primer intervalo (t = 2 h): velocidad media de las primeras 2 h [g/g s.s.·h]
GHALY_VEL0 = {(40, 1): 0.1184, (40, 2): 0.0591, (40, 3): 0.0456, (50, 1): 0.1512, (50, 2): 0.0783,
              (50, 3): 0.0516, (60, 1): 0.2194, (60, 2): 0.1159, (60, 3): 0.0810}


def espesor_ghaly(T, cm):
    """Espesor equivalente de la pasta [m] a partir de la masa cargada en la bandeja."""
    m_ss = GHALY_MASA_G[(T, cm)] / 1000.0 * (1 - 0.7845) / GHALY_AREA      # kg s.s./m²
    return m_ss * (1 + GHALY_X0) / GHALY_RHO
H_GHALY = 11.5          # W/m²·K, estufa de tiro forzado (supuesto)
H_LISKA = 7.3           # W/m²·K, estufa de convección natural (ajustado junto con la cinética)
LISKA_X0 = 3.2
LISKA_L0 = 0.003
LISKA_PUNTOS = [  # (T, t [h], X mínimo, X máximo) leídos de la Fig. 2 (tres muestras)
    (70.0, 4.5, 0.30, 0.64),
    (110.0, 3.0, 0.035, 0.074),
]
LISKA_VEL0_70 = (0.85, 1.00)


def cinetica():
    prmG = pa.vector_parametros(x0=GHALY_X0, rhop0=GHALY_RHO)
    filas = []
    curvas = {}
    for (T, cm), t_med in GHALY_TIEMPO.items():
        L0 = espesor_ghaly(T, cm)
        r = secar_losa_horno(L0, GHALY_X0, 22.0, float(T), 0.009, H_GHALY, P, prmG, 250 * 3600.0, 30.0, 1)
        t05 = float(np.interp(-0.05, -r[:, 1], r[:, 0]))
        vel = (GHALY_X0 - float(np.interp(2.0, r[:, 0], r[:, 1]))) / 2.0
        filas.append(dict(T=T, cm=cm, t_medido_h=t_med, t_modelo_h=t05,
                          vel0_medida=GHALY_VEL0[(T, cm)], vel0_modelo=vel))
        sel = r[:: max(1, len(r) // 400)]
        curvas[f"ghaly_{T}_{cm}"] = dict(t=sel[:, 0].tolist(), X=sel[:, 1].tolist())
    prmL = pa.vector_parametros(x0=LISKA_X0, rhop0=1000.0)
    liska = []
    for T in (70.0, 110.0):
        r = secar_losa_horno(LISKA_L0, LISKA_X0, 22.0, T, 0.010, H_LISKA, P, prmL, 9 * 3600.0, 10.0, 1)
        sel = r[:: max(1, len(r) // 400)]
        curvas[f"liska_{int(T)}"] = dict(t=sel[:, 0].tolist(), X=sel[:, 1].tolist())
        for (Tp, tp, xmin, xmax) in LISKA_PUNTOS:
            if Tp == T:
                liska.append(dict(T=T, t_h=tp, X_min=xmin, X_max=xmax,
                                  X_modelo=float(np.interp(tp, r[:, 0], r[:, 1]))))
        if T == 70.0:
            vel70 = (LISKA_X0 - float(np.interp(1.5, r[:, 0], r[:, 1]))) / 1.5
    err_t = [np.log(f["t_modelo_h"] / f["t_medido_h"]) for f in filas]
    err_v = [np.log(f["vel0_modelo"] / f["vel0_medida"]) for f in filas]
    return dict(ghaly=filas, liska=liska, liska_vel0_70=dict(medida=LISKA_VEL0_70, modelo=vel70),
                rms_log_tiempo=float(np.sqrt(np.mean(np.square(err_t)))),
                rms_log_vel0=float(np.sqrt(np.mean(np.square(err_v)))),
                curvas=curvas)


def balances():
    casos = [
        ("diseño Rev. E (135 °C, 0,37 m/min, 25 % recirc.)", {}),
        ("aire 102 °C", dict(T_aire=102.0)),
        ("alimentación 1.400 kg/h", dict(alimentacion=1400.0)),
        ("sin recirculación", dict(recirc=0.0)),
        ("invierno (11 °C, 80 %)", dict(T_amb=11.0, HR_amb=0.80)),
        ("aire en paralelo a los 3 pisos", dict(modo_aire="paralelo")),
        ("guano al 78 %", dict(humedad_entrada=0.78)),
    ]
    filas = []
    for nombre, kw in casos:
        r = sc.resolver(sc.config(**kw))
        filas.append(dict(caso=nombre, hum_out=r["hum_out"], err_masa=r["err_masa"],
                          err_energia=r["err_energia"], iteraciones=r["iteraciones"],
                          convergio=r["convergio"]))
        print(f"  {nombre:50s} hum {100 * r['hum_out']:5.1f} %  masa {100 * r['err_masa']:+.3f} %  "
              f"energía {100 * r['err_energia']:+.3f} %  ({r['iteraciones']} it.)", flush=True)
    return filas


def malla():
    mallas = [(60, 4), (80, 6), (120, 8), (160, 10), (240, 14), (320, 20)]
    filas = []
    for T in (135.0, 102.0):
        for nx, nz in mallas:
            t0 = time.time()
            r = sc.resolver(sc.config(T_aire=T, nx=nx, nz=nz), inicial=None)
            filas.append(dict(T_aire=T, nx=nx, nz=nz, hum_out=r["hum_out"], T_exh=r["T_exh"],
                              comb=r["comb_kg_h"], T_prod=r["T_prod_out"], seg=time.time() - t0))
            print(f"  T {T:.0f} nx {nx:3d} nz {nz:2d}: hum {100 * r['hum_out']:6.2f} %  "
                  f"escape {r['T_exh']:5.2f} °C  cáscara {r['comb_kg_h']:6.1f}  ({time.time() - t0:4.1f} s)",
                  flush=True)
    return filas


def memoria():
    """Números del informe Rev. E (cap. 1, 6, 15, 19, 26) contra el modelo."""
    d = sc.resolver(sc.config())
    s = sc.resolver(sc.config(recirc=0.0))
    return dict(
        informe=dict(T_aire_salida=65.0, Y_salida=0.033, T_producto=60.0, Q_gen_kW=882.0,
                     cascara_kg_h=314.0, cascara_recirc_t_dia=2.3, rendimiento=0.54,
                     consumo_MJ_kg=4.7, perdidas_kW=48.0, perdidas_cap19_kW=6.1, W_kg_h=670.6,
                     hum_out=0.15),
        modelo_diseno=dict(hum_out=d["hum_out"], T_exh=d["T_exh"], Y_exh=d["Y_exh"], HR_exh=d["HR_exh"],
                           T_prod=d["T_prod_out"], Q_gen_kW=d["Q_gen_kW"], cascara_kg_h=d["comb_kg_h"],
                           rendimiento=d["rendimiento"], consumo_MJ_kg=d["consumo_MJ_kg"],
                           perdidas_kW=d["Q_paredes_kW"], W_kg_h=d["W_kg_h"], Tin=d["Tin"]),
        modelo_sin_recirc=dict(hum_out=s["hum_out"], T_exh=s["T_exh"], Q_gen_kW=s["Q_gen_kW"],
                               cascara_kg_h=s["comb_kg_h"]),
    )


def figura_cinetica(cin, ruta):
    gr.estilo()
    fig, axs = gr.plt.subplots(1, 3, figsize=(12.5, 4.1), gridspec_kw=dict(wspace=0.32))
    colores = {40: gr.AZUL, 50: gr.NARANJA, 60: gr.AGUA}
    marcas = {1: "o", 2: "s", 3: "^"}
    # (a) tiempo de secado
    ax = axs[0]
    lo, hi = 15, 260
    ax.fill_between([lo, hi], [lo / 1.3, hi / 1.3], [lo * 1.3, hi * 1.3], color=gr.GRILLA, alpha=0.6, lw=0)
    ax.plot([lo, hi], [lo, hi], color=gr.TINTA_3, lw=0.9)
    for f in cin["ghaly"]:
        ax.plot(f["t_medido_h"], f["t_modelo_h"], marcas[f["cm"]], color=colores[f["T"]], ms=7,
                mec=gr.SUPERFICIE, mew=1.4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ticks = [20, 30, 50, 100, 200]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    gr.coma(ax)
    ax.minorticks_off()
    ax.set_xlabel("medido: horas hasta peso constante")
    ax.set_ylabel("modelo: horas hasta X = 0,05")
    ax.set_title("Tiempo de secado en estufa")
    ax.text(lo * 1.08, hi * 0.80, "banda ±30 %", fontsize=7.8, color=gr.TINTA_3)
    # (b) velocidad inicial
    ax = axs[1]
    lo, hi = 0.03, 0.3
    ax.fill_between([lo, hi], [lo / 1.3, hi / 1.3], [lo * 1.3, hi * 1.3], color=gr.GRILLA, alpha=0.6, lw=0)
    ax.plot([lo, hi], [lo, hi], color=gr.TINTA_3, lw=0.9)
    for f in cin["ghaly"]:
        ax.plot(f["vel0_medida"], f["vel0_modelo"], marcas[f["cm"]], color=colores[f["T"]], ms=7,
                mec=gr.SUPERFICIE, mew=1.4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ticks = [0.04, 0.06, 0.1, 0.2]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    gr.coma(ax)
    ax.minorticks_off()
    ax.set_xlabel("medida [kg agua / kg s.s. · h]")
    ax.set_ylabel("modelo [kg agua / kg s.s. · h]")
    ax.set_title("Velocidad de las primeras 2 h")
    # leyenda compartida
    from matplotlib.lines import Line2D
    h = [Line2D([], [], ls="", marker="o", color=colores[T], ms=7, label=f"{T} °C") for T in (40, 50, 60)]
    h += [Line2D([], [], ls="", marker=marcas[c], color=gr.TINTA_3, ms=7, label=f"{c} cm") for c in (1, 2, 3)]
    axs[1].legend(handles=h, loc="lower right", ncol=2, columnspacing=0.8, handletextpad=0.2)
    # (c) Liška y Kic
    ax = axs[2]
    for T, col in ((70, gr.AZUL), (110, gr.NARANJA)):
        c = cin["curvas"][f"liska_{T}"]
        ax.plot(c["t"], c["X"], color=col, lw=1.8)
    for p, col in zip(cin["liska"], (gr.AZUL, gr.NARANJA)):
        ax.errorbar([p["t_h"]], [0.5 * (p["X_min"] + p["X_max"])], yerr=[[0.5 * (p["X_max"] - p["X_min"])]],
                    fmt="none", ecolor=col, elinewidth=1.4, capsize=4, alpha=0.8)
        ax.plot([p["t_h"]], [p["X_modelo"]], "o", color=col, ms=6, mec=gr.SUPERFICIE, mew=1.4, zorder=5)
    ax.set_xlim(0, 9)
    ax.set_ylim(0, 3.4)
    gr.coma(ax)
    ax.set_xlabel("tiempo [h]")
    ax.set_ylabel("humedad X [kg agua / kg s.s.]")
    ax.set_title("Estufa a 70 y 110 °C (espesor supuesto 3 mm)")
    c70 = cin["curvas"]["liska_70"]
    c110 = cin["curvas"]["liska_110"]
    ax.annotate("70 °C", (3.2, float(np.interp(3.2, c70["t"], c70["X"]))), xytext=(8, 4),
                textcoords="offset points", fontsize=8, color=gr.TINTA_2)
    ax.annotate("110 °C", (2.4, float(np.interp(2.4, c110["t"], c110["X"]))), xytext=(7, 2),
                textcoords="offset points", fontsize=8, color=gr.TINTA_2, ha="left", va="bottom")
    ax.text(4.6, 2.9, "barras: rango de las 3 muestras medidas\npuntos: modelo", fontsize=7.8,
            color=gr.TINTA_3, va="top")
    gr.titulo(fig, "Con la difusividad ajustada, el modelo sigue los ensayos de estufa con un error típico de ±25 %",
              "Guano de ponedora en capa fina: Ghaly y MacDonald (2012) a 40-60 °C y Liška y Kic (2011) "
              "a 70-110 °C. Mismos parámetros para todos los casos; son los ensayos con los que se ajustaron, así que "
              "esto muestra la calidad del ajuste, no una prueba independiente.", y=0.93)
    gr.nota(fig, f"Error cuadrático medio (en logaritmo): tiempo {100 * cin['rms_log_tiempo']:.0f} %, "
                 f"velocidad inicial {100 * cin['rms_log_vel0']:.0f} %. Velocidad inicial a 70 °C (Liška): medida "
                 f"0,85-1,00, modelo {gr.num(cin['liska_vel0_70']['modelo'], 2)} kg/kg·h.", y=-0.03)
    gr.guardar(fig, ruta)


def main():
    t0 = time.time()
    print("1) cinética", flush=True)
    cin = cinetica()
    for f in cin["ghaly"]:
        print(f"  Ghaly {f['T']} °C {f['cm']} cm: tiempo {f['t_medido_h']} h vs {f['t_modelo_h']:.0f} h | "
              f"vel0 {f['vel0_medida']:.3f} vs {f['vel0_modelo']:.3f}")
    for p in cin["liska"]:
        print(f"  Liška {p['T']:.0f} °C a {p['t_h']} h: X medido {p['X_min']}-{p['X_max']}, modelo {p['X_modelo']:.3f}")
    print(f"  RMS log tiempo {cin['rms_log_tiempo']:.3f}, vel0 {cin['rms_log_vel0']:.3f}")
    figura_cinetica(cin, os.path.join(FIG, "13_validacion_cinetica.png"))
    print("2) balances", flush=True)
    bal = balances()
    print("3) malla", flush=True)
    mal = malla()
    print("4) memoria", flush=True)
    mem = memoria()
    out = dict(cinetica={k: v for k, v in cin.items() if k != "curvas"}, curvas=cin["curvas"],
               balances=bal, malla=mal, memoria=mem)
    with open(os.path.join(RES, "validacion.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, default=float)
    print(f"listo en {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
