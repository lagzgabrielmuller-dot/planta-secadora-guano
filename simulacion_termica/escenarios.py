"""Escenarios de cálculo del secador SC-4 (resultados en resultados/*.json).

Cada función calcula un grupo de casos y devuelve un diccionario serializable. `correr_todo.py`
las llama, guarda los JSON y después dibuja las figuras con `figuras.py`.

Malla de trabajo: nx = 120 posiciones por piso y nz = 8 capas (difiere menos de 0,1 punto de
humedad de la malla fina de 320 × 20, ver validar.py).
"""
import time
from multiprocessing import get_context

import numpy as np

from secado import clima
from secado import dinamica as dn
from secado import parametros as pa
from secado import secador as sc

NX, NZ = 120, 8
OBJ = pa.HUMEDAD_SALIDA_BH


def cfg(**kw):
    kw.setdefault("nx", NX)
    kw.setdefault("nz", NZ)
    return sc.config(**kw)


def resumen(r):
    """Escalares de una solución (todo en unidades de uso: °C, %, kg/h, kW, min, m/min, mm)."""
    c = r["cfg"]
    return dict(
        T_aire=c["T_aire"], vel=float(r["vel"][0] * 60), alimentacion=c["alimentacion"],
        humedad_entrada=c["humedad_entrada"], recirc=c["recirc"], T_amb=c["T_amb"], HR_amb=c["HR_amb"],
        hum_out=r["hum_out"], X_out=r["X_out"], T_prod=r["T_prod_out"], T_exh=r["T_exh"],
        Y_exh=r["Y_exh"], HR_exh=r["HR_exh"], T_rocio_exh=r["T_rocio_exh"], T_mix=r["T_mix"],
        Y_mix=r["Y_mix"], HR_mix=r["HR_mix"], niebla_exh=r["niebla_exh"], niebla_mix=r["niebla_mix"],
        Tin=[float(x) for x in r["Tin"]], Tout=[float(x) for x in r["Tout"]],
        W=r["W_kg_h"], prod=r["prod_kg_h"], comb=r["comb_kg_h"], Q_gen=r["Q_gen_kW"],
        Q_util=r["Q_util_kW"], Q_sorcion=r["Q_sorcion_kW"], Q_paredes=r["Q_paredes_kW"],
        Q_evap=r["Q_evap_kW"], Q_producto=r["Q_producto_kW"], Q_escape=r["Q_escape_kW"],
        Q_ducto=r["Q_ducto_kW"], Q_util_memoria=r["Q_util_memoria_kW"],
        rendimiento=r["rendimiento"], rendimiento_memoria=r["rendimiento_memoria"],
        consumo_MJ_kg=r["consumo_MJ_kg"], cd03=r.get("cd03", "fija"),
        Y_exh_cd03_abierta=r.get("Y_exh_cd03_abierta"), bypass_pila=c["bypass_pila"],
        dp=[float(x) for x in r["dp_pisos"]], capa_mm=r["capa_mm"], t_res=float(sum(r["t_res_min"])),
        t55_peor=float(r["hig_peor"][0] / 60), t70_peor=float(r["hig_peor"][1] / 60),
        t55_med=float(r["hig_med"][0] / 60), t70_med=float(r["hig_med"][1] / 60),
        P_vent=r["P_vent_kW"], convergio=bool(r["convergio"]), err_masa=r["err_masa"],
        err_energia=r["err_energia"],
    )


def regla(calculo, c):
    """`calculo` con la regla de la CD-03 del plano 18 (cierra si el escape pasa de 45 g/kg)."""
    return sc.con_regla_cd03(calculo, c)


def pmap(f, args, procesos=2):
    with get_context("fork").Pool(procesos) as p:
        return p.map(f, args, chunksize=1)


def capa_a_vel(alimentacion, capa_mm, humedad=pa.HUMEDAD_ENTRADA_BH):
    """Velocidad de banda [m/s] que deja una capa de `capa_mm` en el piso 1."""
    from secado.guano import volumen_lecho
    prm = pa.vector_parametros()
    X = humedad / (1 - humedad)
    mdm = alimentacion * (1 - humedad) / 3600.0
    return mdm * volumen_lecho(X, prm) / (pa.ANCHO_BANDA * capa_mm / 1000.0)


def T_para_objetivo(c, T_min=80.0, T_max=pa.T_AIRE_MAX):
    r, est = sc.buscar_temperatura(c, T_min=T_min, T_max=T_max)
    return r, est


# ------------------------------------------------------------------ 1. perfiles
def _perfil(r):
    nz = r["capasX"][0].shape[1]
    v = r["vel"][0]
    pisos = []
    for k in range(3):
        o = r["perfiles"][k]
        X = r["capasX"][k]
        T = r["capasT"][k]
        x = o[:, 0] + 12.0 * k
        pisos.append(dict(
            x=x.tolist(), t_min=((o[:, 0] + 12.0 * k) / v / 60).tolist(),
            hum_med=(o[:, 2] / (1 + o[:, 2])).tolist(), hum_min=(o[:, 3] / (1 + o[:, 3])).tolist(),
            hum_max=(o[:, 4] / (1 + o[:, 4])).tolist(), T_med=o[:, 5].tolist(), T_min=o[:, 6].tolist(),
            T_max=o[:, 7].tolist(), T_aire_sal=o[:, 8].tolist(), Y_aire_sal=o[:, 9].tolist(),
            g=(o[:, 10] / o[:, 10].mean()).tolist(), altura_mm=(o[:, 14] * 1000).tolist(),
            capas_hum=(X / (1 + X)).T.tolist(), capas_T=T.T.tolist(),
        ))
    return dict(resumen=resumen(r), pisos=pisos, nz=nz)


def perfiles():
    out = {}
    r = regla(sc.resolver, cfg())
    out["diseno"] = _perfil(r)
    r15, est = regla(T_para_objetivo, cfg())
    out["ajustado"] = _perfil(r15)
    out["T15"] = r15["cfg"]["T_aire"]
    rc, est = regla(lambda c: sc.capacidad(c, a_min=600.0, a_max=2500.0), cfg())
    out["capacidad"] = _perfil(rc)
    out["A_cap"] = rc["cfg"]["alimentacion"]
    return out


# ------------------------------------------------------------------ 2. ventana de operación
VENT_T = [96, 98, 100, 101, 102, 103, 104, 105, 106, 108, 110, 112.5, 115, 117.5, 120, 125, 130, 135,
          140, 145, 150]
VENT_V = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90]


def _fila_ventana(T):
    est = None
    filas = []
    for v in VENT_V:
        r = sc.resolver(cfg(T_aire=float(T), vel=v / 60.0), inicial=est)
        est = r["estado"]
        filas.append(resumen(r))
    return filas


def ventana():
    filas = pmap(_fila_ventana, VENT_T)
    return dict(T=VENT_T, v=VENT_V, filas=filas,
                v_capa_20=capa_a_vel(1000.0, 20.0) * 60, v_capa_40=capa_a_vel(1000.0, 40.0) * 60)


# ------------------------------------------------------------------ 3. temperatura necesaria
HUMS = [0.65, 0.68, 0.70, 0.72, 0.74, 0.76, 0.78]
ALIMS = [700.0, 800.0, 900.0, 1000.0, 1100.0, 1200.0, 1300.0, 1400.0]


def _T_hum(h):
    r, est = regla(lambda c: T_para_objetivo(c, T_min=70.0), cfg(humedad_entrada=h))
    d = resumen(r)
    d["estado"] = est
    return d


def _T_alim(a):
    r, est = regla(lambda c: T_para_objetivo(c, T_min=70.0), cfg(alimentacion=a))
    d = resumen(r)
    d["estado"] = est
    return d


def temperatura():
    return dict(por_humedad=pmap(_T_hum, HUMS), por_alimentacion=pmap(_T_alim, ALIMS))


# ------------------------------------------------------------------ 4. capacidad
CAP_T = [105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0, 145.0, 150.0]


def _cap_vfija(T):
    r, est = regla(lambda c: sc.capacidad(c, a_min=300.0, a_max=3000.0), cfg(T_aire=T))
    d = resumen(r)
    d["estado"] = est
    return d


def _cap_capa(T, capa_mm=30.0):
    """Capacidad con la velocidad atada al caudal para mantener la capa en `capa_mm` (con la regla
    de la CD-03: si el escape pasa de 45 g/kg se repite con la recirculación cerrada)."""
    d = _cap_capa_r(T, capa_mm, pa.RECIRCULACION)
    if d["Y_exh"] > pa.Y_MAX_RECIRC:
        Y_ab = d["Y_exh"]
        d = _cap_capa_r(T, capa_mm, 0.0)
        d["cd03"] = "cerrada" if d["Y_exh"] > pa.Y_MAX_RECIRC else "cicla"
        d["Y_exh_cd03_abierta"] = Y_ab
    else:
        d["cd03"] = "abierta"
    return d


def _cap_capa_r(T, capa_mm, recirc):
    def hum(a, ini=None):
        c = cfg(T_aire=T, alimentacion=a, vel=capa_a_vel(a, capa_mm), recirc=recirc)
        return sc.resolver(c, inicial=ini)
    lo, hi = 300.0, 3000.0
    r_lo = hum(lo)
    r_hi = hum(hi, r_lo["estado"])
    if r_hi["hum_out"] <= OBJ:
        d = resumen(r_hi)
        d["estado"] = "sobra"
        return d
    est = r_hi["estado"]
    f_lo, f_hi = r_lo["hum_out"] - OBJ, r_hi["hum_out"] - OBJ
    best = r_hi
    for _ in range(30):
        x = hi - f_hi * (hi - lo) / (f_hi - f_lo)
        if not (lo + 0.05 * (hi - lo) < x < hi - 0.05 * (hi - lo)):
            x = 0.5 * (lo + hi)
        r = hum(x, est)
        est = r["estado"]
        f = r["hum_out"] - OBJ
        best = r
        if abs(f) < 2e-4:
            break
        if f > 0:
            hi, f_hi = x, f
        else:
            lo, f_lo = x, f
    d = resumen(best)
    d["estado"] = "ok"
    return d


def capacidad():
    return dict(T=CAP_T, vel_fija=pmap(_cap_vfija, CAP_T), capa_30=pmap(_cap_capa, CAP_T))


# ------------------------------------------------------------------ 5. recirculación
RECS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
MES_INV, MES_VER = 6, 0        # julio y enero


def _rec(args):
    r_, mes = args
    if mes is None:
        T_amb, HR_amb = pa.T_AMBIENTE_DISENO, pa.HR_AMBIENTE_DISENO
    else:
        T_amb, HR_amb = clima.condiciones_turno(mes)
    r15, est = T_para_objetivo(cfg(recirc=r_, T_amb=T_amb, HR_amb=HR_amb), T_min=70.0)
    d15 = resumen(r15)
    d15["estado"] = est
    d135 = resumen(sc.resolver(cfg(recirc=r_, T_amb=T_amb, HR_amb=HR_amb)))
    return dict(recirc=r_, mes=mes, a15=d15, a135=d135)


def recirculacion():
    args = [(r_, m) for m in (None, MES_INV, MES_VER) for r_ in RECS]
    res = pmap(_rec, args)
    return dict(recirc=RECS, diseno=[x for x in res if x["mes"] is None],
                invierno=[x for x in res if x["mes"] == MES_INV],
                verano=[x for x in res if x["mes"] == MES_VER])


# ------------------------------------------------------------------ 6. sensibilidad
def _sens_casos():
    Tj, Hj = clima.condiciones_turno(MES_INV)
    Te, He = clima.condiciones_turno(MES_VER)
    return [
        ("Difusividad del agua en el grumo", "× 0,5", dict(prm=dict(dref=pa.D_REF * 0.5)),
         "× 2", dict(prm=dict(dref=pa.D_REF * 2.0))),
        ("Tamaño de grumo del esparcidor", "20 mm", dict(prm=dict(d0=0.020)),
         "6 mm", dict(prm=dict(d0=0.006))),
        ("Aire que sube por los bordes de los tres pisos", "10 %", dict(bypass_pila=0.10),
         "0 %", dict(bypass_pila=0.0)),
        ("Aire que esquiva cada banda (se mezcla entre pisos)", "20 %", dict(prm=dict(byp=0.20)),
         "0 %", dict(prm=dict(byp=0.0))),
        ("Humedad del guano fresco", "76 %", dict(humedad_entrada=0.76),
         "68 %", dict(humedad_entrada=0.68)),
        ("Caudal de guano", "1.100 kg/h", dict(alimentacion=1100.0),
         "900 kg/h", dict(alimentacion=900.0)),
        ("Clima del turno", "julio", dict(T_amb=Tj, HR_amb=Hj), "enero", dict(T_amb=Te, HR_amb=He)),
        ("Caudal de aire", "− 10 %", dict(aire_seco=pa.AIRE_SECO_KG_H * 0.9),
         "+ 10 %", dict(aire_seco=pa.AIRE_SECO_KG_H * 1.1)),
        ("Recirculación (CD-03)", "35 %", dict(recirc=0.35), "0 %", dict(recirc=0.0)),
        ("Aislación de la cámara (U)", "× 2", dict(U_panel=pa.U_PANEL * 2), "× 0,5",
         dict(U_panel=pa.U_PANEL * 0.5)),
        ("Isoterma (monocapa GAB)", "× 1,3", dict(prm=dict(xm25=pa.GAB_XM_25 * 1.3)),
         "× 0,7", dict(prm=dict(xm25=pa.GAB_XM_25 * 0.7))),
    ]


def _sens(kw):
    r15, est = T_para_objetivo(cfg(**kw), T_min=70.0)
    d = dict(T15=r15["cfg"]["T_aire"], estado=est, comb15=r15["comb_kg_h"])
    r135 = sc.resolver(cfg(**kw))
    d["hum135"] = r135["hum_out"]
    d["Tprod135"] = r135["T_prod_out"]
    return d


def sensibilidad():
    casos = _sens_casos()
    args = [{}]
    for _, _, kw_a, _, kw_b in casos:
        args += [kw_a, kw_b]
    res = pmap(_sens, args)
    base = res[0]
    filas = []
    for i, (nombre, la, _, lb, _) in enumerate(casos):
        filas.append(dict(nombre=nombre, etiqueta_a=la, a=res[1 + 2 * i], etiqueta_b=lb, b=res[2 + 2 * i]))
    # grumos más grandes, a la temperatura de diseño (lo único que hace fallar el diseño)
    grumos = []
    for d0 in (0.006, 0.010, 0.015, 0.020, 0.025, 0.030, 0.035, 0.040):
        r = sc.resolver(cfg(prm=dict(d0=d0)))
        grumos.append(dict(d0_mm=d0 * 1000, hum135=r["hum_out"], T_exh=r["T_exh"]))
    return dict(base=base, filas=filas, grumos=grumos)


# ------------------------------------------------------------------ 7. clima mes a mes
def _mes(m):
    T_amb, HR_amb = clima.condiciones_turno(m)
    r15, est = regla(lambda c: T_para_objetivo(c, T_min=70.0), cfg(T_amb=T_amb, HR_amb=HR_amb))
    d15 = resumen(r15)
    d15["estado"] = est
    d135 = resumen(regla(sc.resolver, cfg(T_amb=T_amb, HR_amb=HR_amb)))
    d0 = resumen(sc.resolver(cfg(T_amb=T_amb, HR_amb=HR_amb, recirc=0.0)))
    return dict(mes=m, nombre=pa.MESES[m], T_amb=T_amb, HR_amb=HR_amb, a15=d15, a135=d135, a135_sin_recirc=d0)


def clima_anual():
    meses = pmap(_mes, list(range(12)))
    dias = clima.dias_operacion_mes()
    for m, d in zip(meses, dias):
        d_op = float(d)
        m["dias_operacion"] = d_op
        for k in ("a15", "a135", "a135_sin_recirc"):
            m[k]["cascara_t_mes"] = m[k]["comb"] * pa.HORAS_TURNO * d_op / 1000.0
    return dict(meses=meses)


# ------------------------------------------------------------------ 8. variantes de configuración
def variantes():
    out = {}
    for nombre, kw in (("contracorriente", {}), ("paralelo", dict(modo_aire="paralelo")),
                       ("inversion", dict(transferencia="inversion"))):
        r15, est = T_para_objetivo(cfg(**kw), T_min=70.0)
        d = resumen(r15)
        d["estado"] = est
        out[nombre] = dict(a15=d, a135=resumen(sc.resolver(cfg(**kw))), perfil15=_perfil(r15))
    return out


# ------------------------------------------------------------------ 9. dinámica del lazo de humedad
def _sim(args):
    nombre, control, T0, horas, perturbacion = args
    c = cfg(T_aire=T0)
    r0 = sc.resolver(c)

    def ent(t):
        d = dict(humedad_entrada=0.72, alimentacion=1000.0, T_amb=pa.T_AMBIENTE_DISENO,
                 HR_amb=pa.HR_AMBIENTE_DISENO, T_aire=T0)
        if t >= 3600.0:
            d.update(perturbacion)
        return d

    t0 = time.time()
    s = dn.simular(c, horas, ent, control=control, nc=96, dt=10.0, inicial=r0)
    paso = 6        # cada minuto
    out = {k: (v[::paso].tolist() if isinstance(v, np.ndarray) else v) for k, v in s.items()}
    out["nombre"] = nombre
    out["seg"] = time.time() - t0
    return out


def dinamica_lazos(T15, sintonia):
    """Escalón de humedad del guano 72 → 76 % a la hora 1, con tres estrategias de control."""
    pert = dict(humedad_entrada=0.76)
    h = 8.0
    casos = [
        ("sin control", None, T15, h, pert),
        ("informe: MIC-01 mueve las bandas", dict(variable="vel", ff="T_out3", **sintonia["vel"]), T15, h, pert),
        ("propuesto: MIC-01 corrige la consigna de TIC-01", dict(variable="T_aire", **sintonia["T"]), T15, h, pert),
        ("propuesto + humedad de entrada medida",
         dict(variable="T_aire", ff="humedad_entrada", **sintonia["T_ff"]), T15, h, pert),
    ]
    return dict(T15=T15, casos=pmap(_sim, casos))


# ------------------------------------------------------------------ 10. balance de energía
def energia(perf):
    """Destino del calor del generador en los tres puntos (desde perfiles()) y en la memoria.

    Q_gen = evaporar el agua (a la temperatura de entrada del guano) + calentar el producto
            + calor de sorción del agua ligada + paredes y ducto + escape (calor sensible del aire
            y del vapor que se van por la chimenea).
    La memoria (cap. 6.3) cuenta el agua evaporada como líquido calentado hasta la salida del producto;
    su caso se recalcula acá con la misma definición que el modelo.
    """
    from secado.psicrometria import hfg
    out = {}
    for k in ("diseno", "ajustado", "capacidad"):
        s = perf[k]["resumen"]
        out[k] = dict(Q_gen=s["Q_gen"], evaporar=s["Q_evap"], producto=s["Q_producto"], sorcion=s["Q_sorcion"],
                      paredes=s["Q_paredes"] + s["Q_ducto"], escape=s["Q_escape"],
                      util=s["Q_util"], rendimiento=s["rendimiento"],
                      util_memoria=s["Q_util_memoria"], rendimiento_memoria=s["rendimiento_memoria"])
    # memoria, cap. 6.3: 882 kW; 1.000 kg/h del 72 al 15 %; guano de 18 a 60 °C; paredes 48 kW (10 %)
    mdm = 1000.0 * (1 - 0.72) / 3600.0
    X_out = 0.15 / 0.85
    W = mdm * (0.72 / 0.28 - X_out)
    T_feed, T_out = 18.0, 60.0
    evap = W * hfg(T_feed) / 1e3
    prod = mdm * (pa.CP_SOLIDO + 4186.0 * X_out) * (T_out - T_feed) / 1e3
    out["informe"] = dict(Q_gen=882.0, evaporar=evap, producto=prod, sorcion=0.0, paredes=48.0,
                          escape=882.0 - evap - prod - 48.0, util=evap + prod, rendimiento=(evap + prod) / 882.0,
                          util_memoria=480.0, rendimiento_memoria=480.0 / 882.0)
    return out


# ------------------------------------------------------------------ 11. aire por los bordes
BORDES = [0.0, 0.05, 0.10, 0.20]


def _borde(fp):
    r15, est = regla(lambda c: T_para_objetivo(c, T_min=70.0), cfg(bypass_pila=fp))
    d15 = resumen(r15)
    d15["estado"] = est
    d135 = resumen(regla(sc.resolver, cfg(bypass_pila=fp)))
    rc, estc = regla(lambda c: sc.capacidad(c, a_min=600.0, a_max=3000.0), cfg(bypass_pila=fp))
    dc = resumen(rc)
    dc["estado"] = estc
    return dict(bypass_pila=fp, a15=d15, a135=d135, capacidad=dc)


def _borde_mes(args):
    fp, m = args
    T_amb, HR_amb = clima.condiciones_turno(m)
    r15, est = regla(lambda c: T_para_objetivo(c, T_min=70.0), cfg(T_amb=T_amb, HR_amb=HR_amb, bypass_pila=fp))
    r135 = regla(sc.resolver, cfg(T_amb=T_amb, HR_amb=HR_amb, bypass_pila=fp))
    return dict(bypass_pila=fp, mes=m, T15=r15["cfg"]["T_aire"], comb15=r15["comb_kg_h"], estado=est,
                comb135=r135["comb_kg_h"], cd03_15=r15["cd03"], cd03_135=r135["cd03"])


def bordes():
    """Aire que sube del plenum a la campana por las rendijas entre bandas y paredes, sin tocar
    ningún piso. El modelo base supone bordes sellados (solo el 5 % que esquiva cada banda y se
    mezcla antes del piso siguiente); esto da las cotas si las rendijas quedan alineadas."""
    casos = pmap(_borde, BORDES)
    dias = clima.dias_operacion_mes()
    meses = pmap(_borde_mes, [(fp, m) for fp in (0.05, 0.10) for m in range(12)])
    anual = {}
    for fp in (0.05, 0.10):
        ms = [x for x in meses if x["bypass_pila"] == fp]
        t15 = sum(x["comb15"] * pa.HORAS_TURNO * float(d) / 1000.0 for x, d in zip(ms, dias))
        t135 = sum(x["comb135"] * pa.HORAS_TURNO * float(d) / 1000.0 for x, d in zip(ms, dias))
        anual[f"{fp:.2f}"] = dict(t15=t15, t135=t135, meses=ms)
    return dict(casos=casos, anual=anual)


# ------------------------------------------------------------------ 12. higiene según la malla
def higiene_malla(T15):
    """Temperatura y tiempo sobre 55 °C de la capa de arriba según en cuántas capas se divide el
    lecho (con 3 capas, cada una es de un grumo; con 8, de un tercio de grumo)."""
    filas = []
    for nz in (3, 4, 6, 8, 16, 32):
        r = sc.resolver(cfg(T_aire=T15, nz=nz))
        top = [float(r["capasT"][k][:, nz - 1].max()) for k in range(3)]
        Xs = r["capasX"][2][-1, :]
        filas.append(dict(nz=nz, hum_out=r["hum_out"], T_prod=r["T_prod_out"],
                          Tmax_arriba=top, Tmax_abajo=[float(r["capasT"][k][:, 0].max()) for k in range(3)],
                          t55_peor=float(r["hig_peor"][0] / 60), t55_med=float(r["hig_med"][0] / 60),
                          t70_peor=float(r["hig_peor"][1] / 60), t70_med=float(r["hig_med"][1] / 60),
                          hum_arriba=float(Xs[-1] / (1 + Xs[-1])), hum_abajo=float(Xs[0] / (1 + Xs[0]))))
    return dict(T15=T15, filas=filas)


# ------------------------------------------------------------------ 13. pruebas de sintonía
def _prueba(args):
    nombre, control, T15 = args
    c = cfg(T_aire=T15)
    r0 = sc.resolver(c)

    def ent(t):
        return dict(humedad_entrada=0.76 if t >= 3600.0 else 0.72, alimentacion=1000.0,
                    T_amb=pa.T_AMBIENTE_DISENO, HR_amb=pa.HR_AMBIENTE_DISENO, T_aire=T15)

    s = dn.simular(c, 8.0, ent, control=control, nc=96, dt=10.0, inicial=r0)
    t = s["t"]
    h = 100 * s["hum_real"]
    m = t >= 1.0
    e = h[m] - 100 * OBJ
    var = control.get("variable")
    return dict(nombre=nombre, iae=float(np.trapezoid(np.abs(e), t[m])), max=float(h[m].max()),
                min=float(h[m].min()), final=float(h[-60:].mean()),
                t_sobre20=float((h[m] > 20).sum() * 10 / 60),
                u_final=float(s["T_aire_sp"][-1] if var == "T_aire" else s["v"][-1]),
                alarma=float(s["alarma"].max()))


def sintonia(T15):
    """Escalón 72 → 76 % a la hora 1 con varias sintonías de los dos lazos (8 h simuladas)."""
    r76, _ = T_para_objetivo(cfg(humedad_entrada=0.76))
    T76 = r76["cfg"]["T_aire"]
    Kff = (T76 - T15) / 4.0          # ganancia estática: K de aire por punto de humedad de entrada
    casos = []
    for Kc, Ti in [(0.3, 30), (0.5, 30), (0.5, 60), (0.8, 45), (1.0, 60), (0.3, 60)]:
        casos.append((f"T PI Kc={Kc} Ti={Ti}", dict(variable="T_aire", Kc=Kc, Ti_min=Ti, rampa=2.0)))
    for ret in [0, 30, 40, 50, 70]:
        casos.append((f"T PI 0.8/45 + FF ret={ret}", dict(variable="T_aire", Kc=0.8, Ti_min=45, rampa=2.0,
                                                         ff="humedad_entrada", Kff=Kff, ff_retardo_s=ret * 60.0)))
    for Kc, Ti, Kff_v in [(0.003, 120, 0.0), (0.005, 97, 0.002), (0.01, 60, 0.0), (0.01, 60, 0.005),
                          (0.02, 97, 0.0)]:
        casos.append((f"v PI Kc={Kc} Ti={Ti} Kff={Kff_v}", dict(variable="vel", Kc=Kc, Ti_min=Ti, ff="T_out3",
                                                               Kff=Kff_v, rampa=0.05)))
    pruebas = pmap(_prueba, [(n, c, T15) for n, c in casos])
    return dict(nota="Escalón de humedad del guano 72 → 76 % a la hora 1, 8 h simuladas. IAE en puntos·h "
                     "desde la hora 1. Kff de las bandas: (m/min) por K de la salida de aire del piso 3 (TT-04).",
                T15_72=T15, T15_76=T76, Kff_estatico=Kff, pruebas=pruebas)
