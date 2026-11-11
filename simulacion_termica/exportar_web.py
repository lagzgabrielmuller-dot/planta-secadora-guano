"""Exporta los datos de planta para el modelo JavaScript (web/datos.js) y casos de referencia
para comprobar que JavaScript y Python dan lo mismo (web/referencia.json, ver web/probar_js.js).

Uso:  python exportar_web.py
"""
import json
import os
import time

from secado import parametros as pa
from secado import secador as sc

AQUI = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(AQUI, "web")
ORDEN = ["P", "cps", "rhop0", "d0", "betap", "rhob0", "rhobf", "xf_ref", "dref", "ea", "tref", "xm25",
         "xmdt", "c25", "ch", "k", "sa", "sb", "x0", "byp", "d70", "z", "db", "xdref"]


def datos_planta():
    prm = pa.vector_parametros()
    return dict(
        prm={k: float(v) for k, v in zip(ORDEN, prm)},
        dt_nave=pa.DT_NAVE, ancho=pa.ANCHO_BANDA, largo=pa.LARGO_BANDA,
        area_zonas=[float(a) for a in sc.AREA_ZONAS], vel_min=pa.VEL_BANDA_MIN, vel_max=pa.VEL_BANDA_MAX,
        q_ducto=pa.Q_DUCTO_W, pci=pa.PCI_CASCARA, rend_gen=pa.REND_GENERADOR, cenizas=pa.CENIZAS,
        vent_presion=pa.VENTILADORES_PRESION, vent_rend=pa.VENTILADORES_REND,
        uhmw_continuo=pa.UHMW_SERVICIO_CONTINUO, uhmw_fusion=pa.UHMW_FUSION,
        t_aire_max=pa.T_AIRE_MAX, y_max_recirc=pa.Y_MAX_RECIRC,
        meses=pa.MESES, clima=[dict(zip(("T", "HR"), c)) for c in (
            __import__("secado.clima", fromlist=["x"]).condiciones_turno(m) for m in range(12))],
        defecto=dict(alimentacion=pa.ALIMENTACION_KG_H, humedad_entrada=pa.HUMEDAD_ENTRADA_BH,
                     humedad_objetivo=pa.HUMEDAD_SALIDA_BH, T_aire=pa.T_AIRE_ENTRADA,
                     aire_seco=pa.AIRE_SECO_KG_H, recirc=pa.RECIRCULACION, T_amb=pa.T_AMBIENTE_DISENO,
                     HR_amb=pa.HR_AMBIENTE_DISENO, vel=pa.VEL_BANDA_DISENO, factores_vel=[1.0, 1.0, 1.0],
                     modo_aire="contracorriente", distribuir=True, transferencia="mezcla",
                     U_panel=pa.U_PANEL, bypass_pila=0.0, nx=60, nz=6, tol=0.02, maxit=60, relajacion=0.9,
                     nbis=40),
    )


CASOS = [
    ("diseño", {}),
    ("aire 102 °C", dict(T_aire=102.24)),
    ("1.400 kg/h", dict(alimentacion=1400.0)),
    ("paralelo", dict(modo_aire="paralelo")),
    ("inversión", dict(transferencia="inversion", T_aire=104.0)),
    ("sin recirculación, invierno", dict(recirc=0.0, T_amb=11.0, HR_amb=0.8, T_aire=100.0)),
    ("grumo 20 mm", dict(prm=dict(d0=0.020))),
    ("bandas 0,6 m/min", dict(vel=0.6 / 60, T_aire=110.0)),
    ("10 % por los bordes", dict(bypass_pila=0.10, T_aire=111.0)),
]


def referencia(nx=60, nz=6):
    out = []
    for nombre, kw in CASOS:
        t0 = time.time()
        r = sc.resolver(sc.config(nx=nx, nz=nz, tol=1e-4, maxit=200, **kw))
        out.append(dict(nombre=nombre, cfg=kw, seg=time.time() - t0, hum_out=r["hum_out"], T_exh=r["T_exh"],
                        Y_exh=r["Y_exh"], T_prod=r["T_prod_out"], comb=r["comb_kg_h"], Tin=list(r["Tin"]),
                        HR_exh=r["HR_exh"], HR_mix=r["HR_mix"], Q_util=r["Q_util_kW"], Q_escape=r["Q_escape_kW"],
                        t55_peor=float(r["hig_peor"][0]), t70_med=float(r["hig_med"][1]),
                        iteraciones=r["iteraciones"], convergio=r["convergio"]))
        print(f"  {nombre:28s} hum {100 * r['hum_out']:6.2f} %  escape {r['T_exh']:6.2f} °C  "
              f"({r['iteraciones']} it., {time.time() - t0:.1f} s)", flush=True)
    return out


def main():
    D = datos_planta()
    with open(os.path.join(WEB, "datos.js"), "w", encoding="utf-8") as f:
        f.write("/* Datos de planta del SC-4 (Rev. D/E) exportados desde Python: exportar_web.py */\n")
        f.write("const DATOS_SC4 = " + json.dumps(D, ensure_ascii=False, indent=1) + ";\n")
        f.write('if (typeof module !== "undefined") module.exports = DATOS_SC4;\n')
    ref = referencia()
    with open(os.path.join(WEB, "referencia.json"), "w", encoding="utf-8") as f:
        json.dump(dict(nx=60, nz=6, casos=ref), f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
