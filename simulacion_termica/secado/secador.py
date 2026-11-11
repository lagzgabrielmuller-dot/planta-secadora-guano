"""Solución estacionaria del secador SC-4 y de su circuito de aire (generador, recirculación).

Configuración de la Rev. D/E: tres pisos de 2,0 × 12 m en cascada. El guano entra al piso 1
(arriba), cae al 2 y luego al 3 (abajo). El aire caliente entra por el plenum inferior y atraviesa
los tres pisos en serie de abajo hacia arriba (contracorriente). Entre pisos el aire se mezcla
(hay 850 mm libres entre bandas) y pierde calor por las paredes de la cámara.

La función principal es `resolver(cfg)`. `buscar_velocidad(cfg)` reproduce el lazo MIC-01: busca
la velocidad de las bandas que deja el producto en la humedad objetivo.
"""
import copy
import math

import numpy as np

from . import parametros as pa
from .guano import humedad_equilibrio, volumen_lecho
from .nucleo import C_AERG, C_BERG, NOUT, avanzar_piso
from .psicrometria import CPA, CPV, Y_de_pv, bulbo_humedo, entalpia, hfg, hr, psat, punto_rocio, \
    rho_aire, saturar, temp_de_entalpia

AREA_PISO = pa.ANCHO_BANDA * pa.LARGO_BANDA
_PERIM = 2.0 * (pa.CAMARA_L + pa.CAMARA_A)
_TAPA = pa.CAMARA_L * pa.CAMARA_A
# superficie de paredes por zona de aire (plenum, entre 3 y 2, entre 2 y 1, campana)
AREA_ZONAS = np.array([
    _PERIM * (pa.Z_PISO3 - pa.Z_PISO_CAMARA) + _TAPA,
    _PERIM * (pa.Z_PISO2 - pa.Z_PISO3),
    _PERIM * (pa.Z_PISO1 - pa.Z_PISO2),
    _PERIM * (pa.Z_TECHO - pa.Z_PISO1) + _TAPA,
])


def config(**kw):
    """Configuración por defecto = punto de diseño de la Rev. D/E."""
    c = dict(
        alimentacion=pa.ALIMENTACION_KG_H,      # kg/h de guano húmedo
        humedad_entrada=pa.HUMEDAD_ENTRADA_BH,  # base húmeda
        humedad_objetivo=pa.HUMEDAD_SALIDA_BH,
        T_guano=None,                           # °C; None = temperatura de la nave
        T_aire=pa.T_AIRE_ENTRADA,               # °C a la entrada del secador (TT-01)
        aire_seco=pa.AIRE_SECO_KG_H,            # kg/h
        recirc=pa.RECIRCULACION,                # fracción
        T_amb=pa.T_AMBIENTE_DISENO,
        HR_amb=pa.HR_AMBIENTE_DISENO,
        vel=pa.VEL_BANDA_DISENO,                # m/s
        factores_vel=(1.0, 1.0, 1.0),           # piso 1, 2, 3
        modo_aire="contracorriente",            # o "paralelo"
        distribuir=True,                        # reparto del aire según la pérdida de carga local
        transferencia="mezcla",                 # o "inversion"
        U_panel=pa.U_PANEL,
        perdida_extra=0.0,                      # fracción extra del calor del aire (fugas), 0 = sin
        bypass_pila=0.0,                        # fracción del aire que sube del plenum a la campana
                                                # por las rendijas entre bandas y paredes, sin tocar
                                                # ningún piso (el 5 % de prm["byp"] es aparte)
        nx=160, nz=10,
        prm={},                                 # cambios a parametros.vector_parametros
        tol=0.01, maxit=80, relajacion=0.9,
    )
    for k, v in kw.items():
        if k not in c:
            raise KeyError(f"opción desconocida: {k}")
        c[k] = v
    return c


def _distribucion(A, B, u_media):
    """Reparte el aire entre las posiciones con la misma ΔP (caminos en paralelo, Ergun)."""
    A = np.maximum(A, 1e-9)
    B = np.maximum(B, 1e-12)

    def u_de_dp(dp):
        return (-A + np.sqrt(A * A + 4.0 * B * dp)) / (2.0 * B)

    hi = float(np.max(A * u_media + B * u_media ** 2)) * 4.0 + 1.0
    lo = 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if u_de_dp(mid).mean() > u_media:
            hi = mid
        else:
            lo = mid
    dp = 0.5 * (lo + hi)
    u = u_de_dp(dp)
    return u / u.mean(), dp


def _T(h, Y):
    return temp_de_entalpia(h, Y)


def resolver(cfg, inicial=None):
    """Resuelve el secador en régimen. Devuelve un diccionario con perfiles y balances."""
    prm = pa.vector_parametros(**cfg["prm"])
    P = prm[pa.I_P]
    nx, nz = int(cfg["nx"]), int(cfg["nz"])
    T_amb = cfg["T_amb"]
    T_nave = T_amb + pa.DT_NAVE
    Y_amb = Y_de_pv(cfg["HR_amb"] * psat(T_amb), P)
    h_amb = entalpia(T_amb, Y_amb)
    T_guano = T_nave if cfg["T_guano"] is None else cfg["T_guano"]

    hum = cfg["humedad_entrada"]
    X_feed = hum / (1.0 - hum)
    mdm = cfg["alimentacion"] * (1.0 - hum) / 3600.0          # kg s.s./s
    m_air = cfg["aire_seco"] / 3600.0                          # kg a.s./s
    vel = np.array(cfg["factores_vel"], float) * cfg["vel"]
    w_dm = mdm / (pa.ANCHO_BANDA * vel)                        # kg s.s./m² en cada piso
    paralelo = cfg["modo_aire"] == "paralelo"
    fp = float(cfg["bypass_pila"])
    m_pila = (1.0 - fp) * m_air                                # aire que atraviesa los pisos
    G_piso = m_pila / AREA_PISO / (3.0 if paralelo else 1.0)
    r = float(cfg["recirc"])
    UA = cfg["U_panel"] * AREA_ZONAS                           # W/K por zona

    # estimaciones iniciales
    X_obj = cfg["humedad_objetivo"] / (1 - cfg["humedad_objetivo"])
    dY = max(mdm * (X_feed - X_obj), 1e-6) / m_air
    if inicial is not None:
        st = copy.deepcopy(inicial)
    else:
        st = dict(T_exh=70.0, Y_exh=Y_amb + dY / (1.0 - r),
                  Tin=[75.0, 100.0, cfg["T_aire"]], Yin=[Y_amb + dY, Y_amb + 0.5 * dY, Y_amb],
                  g=[np.ones(nx) for _ in range(3)])

    outs = [np.zeros((nx, NOUT)) for _ in range(3)]
    capX = [np.zeros((nx, nz)) for _ in range(3)]
    capT = [np.zeros((nx, nz)) for _ in range(3)]
    historia = []
    convergio = False
    for it in range(int(cfg["maxit"])):
        # --- cámara de mezcla: aire fresco + recirculación (salida del ciclón)
        h_exh = entalpia(st["T_exh"], st["Y_exh"])
        Y_mix = (1.0 - r) * Y_amb + r * st["Y_exh"]
        h_mix = (1.0 - r) * h_amb + r * h_exh
        T_mix = _T(h_mix, Y_mix)
        cs_mix = 1006.0 + 1860.0 * Y_mix
        # --- plenum: el aire llega a T_aire (TT-01) y pierde por el piso y las paredes bajas
        q_pl = UA[0] * (cfg["T_aire"] - T_nave)
        T3 = cfg["T_aire"] - q_pl / (m_air * cs_mix)
        if paralelo:
            st["Tin"] = [T3, T3, T3]
            st["Yin"] = [Y_mix, Y_mix, Y_mix]
        else:
            st["Tin"][2] = T3
            st["Yin"][2] = Y_mix

        # --- producto: piso 1 → 2 → 3
        Xp = np.full(nz, X_feed)
        Tp = np.full(nz, T_guano)
        hig_c = np.zeros((nz, 4))
        hig_m = np.zeros((nz, 4))
        salida = []
        for k in range(3):
            inc = np.zeros((nz, 4))
            h_o, Y_o, Qm, Em, Sm = avanzar_piso(Xp, Tp, inc, st["Tin"][k], st["Yin"][k], st["g"][k],
                                                w_dm[k], G_piso, pa.LARGO_BANDA, vel[k], nx, prm,
                                                outs[k], capX[k], capT[k])
            salida.append((h_o, Y_o, Qm, Em, Sm))
            hig_c += inc
            hig_m += inc
            if k < 2:
                if cfg["transferencia"] == "inversion":
                    Xp = Xp[::-1].copy()
                    Tp = Tp[::-1].copy()
                    hig_c = hig_c[::-1].copy()
                    hig_m = hig_m[::-1].copy()
                else:
                    cap = pa.CP_SOLIDO + 4186.0 * Xp
                    Tmix = float((cap * Tp).sum() / cap.sum())
                    Xp = np.full(nz, Xp.mean())
                    Tp = np.full(nz, Tmix)
                    hig_c = np.tile(hig_c.min(axis=0), (nz, 1))
                    hig_m = np.tile(hig_m.mean(axis=0), (nz, 1))

        # --- aire: salidas de cada piso, pérdidas por zona y nuevas entradas
        Tout = [_T(s[0], s[1]) for s in salida]
        Yout = [s[1] for s in salida]
        h_byp = entalpia(T3, Y_mix)              # aire que sube por los bordes sin tocar el guano
        if paralelo:
            # cada piso descarga en su propia campana; se mezclan a la salida
            Yx = (1.0 - fp) * float(np.mean(Yout)) + fp * Y_mix
            hx = (1.0 - fp) * float(np.mean([s[0] for s in salida])) + fp * h_byp
            Tx = _T(hx, Yx)
            q_zonas = [UA[1] * (Tout[2] - T_nave), UA[2] * (Tout[1] - T_nave), UA[3] * (Tout[0] - T_nave)]
            T_exh_new = Tx - sum(q_zonas) / (m_air * (1006.0 + 1860.0 * Yx))
            Y_exh_new = Yx
            nuevos = None
        else:
            cs3 = 1006.0 + 1860.0 * Yout[2]
            q32 = UA[1] * (Tout[2] - T_nave)
            Tin2 = Tout[2] - q32 / (m_pila * cs3)
            cs2 = 1006.0 + 1860.0 * Yout[1]
            q21 = UA[2] * (Tout[1] - T_nave)
            Tin1 = Tout[1] - q21 / (m_pila * cs2)
            # campana: el aire del piso 1 se junta con el que subió por los bordes
            Yc = (1.0 - fp) * Yout[0] + fp * Y_mix
            Tc = _T((1.0 - fp) * salida[0][0] + fp * h_byp, Yc)
            cs1 = 1006.0 + 1860.0 * Yc
            q1 = UA[3] * (Tc - T_nave)
            T_exh_new = Tc - q1 / (m_air * cs1)
            Y_exh_new = Yc
            q_zonas = [q32, q21, q1]
            nuevos = (Tin1, Yout[1], Tin2, Yout[2])
        q_extra = 0.0
        if cfg["perdida_extra"] > 0:
            # fugas no modeladas, como fracción del calor que entrega el aire
            q_extra = cfg["perdida_extra"] * m_air * cs_mix * (cfg["T_aire"] - T_exh_new)
            T_exh_new -= q_extra / (m_air * cs_mix)

        # --- relajación y convergencia
        w = cfg["relajacion"]
        err = abs(T_exh_new - st["T_exh"]) + 1e4 * abs(Y_exh_new - st["Y_exh"])
        st["T_exh"] = (1 - w) * st["T_exh"] + w * T_exh_new
        st["Y_exh"] = (1 - w) * st["Y_exh"] + w * Y_exh_new
        if nuevos is not None:
            Tin1, Yin1, Tin2, Yin2 = nuevos
            err += abs(Tin1 - st["Tin"][0]) + abs(Tin2 - st["Tin"][1])
            err += 1e4 * (abs(Yin1 - st["Yin"][0]) + abs(Yin2 - st["Yin"][1]))
            st["Tin"][0] = (1 - w) * st["Tin"][0] + w * Tin1
            st["Tin"][1] = (1 - w) * st["Tin"][1] + w * Tin2
            st["Yin"][0] = (1 - w) * st["Yin"][0] + w * Yin1
            st["Yin"][1] = (1 - w) * st["Yin"][1] + w * Yin2
        # --- reparto del aire según la permeabilidad del lecho
        dps = []
        for k in range(3):
            rho = rho_aire(st["Tin"][k], st["Yin"][k], P)
            u_med = (1.0 - prm[pa.I_BYP]) * G_piso * (1 + st["Yin"][k]) / rho
            gk, dp = _distribucion(outs[k][:, C_AERG], outs[k][:, C_BERG], u_med)
            dps.append(dp)
            if cfg["distribuir"]:
                st["g"][k] = (1 - w) * st["g"][k] + w * gk
        historia.append(err)
        if err < cfg["tol"] and it > 2:
            convergio = True
            break

    # ---------------------------------------------------------------- resultados
    X_out = float(Xp.mean())
    cap = pa.CP_SOLIDO + 4186.0 * Xp
    T_out = float((cap * Tp).sum() / cap.sum())
    W = mdm * (X_feed - X_out)                                 # kg/s de agua evaporada
    T_exh, Y_exh = st["T_exh"], st["Y_exh"]
    h_in = entalpia(cfg["T_aire"], Y_mix)
    # generador: calienta la mezcla de T_mix a T_aire, más el ducto dentro de la nave
    Q_gen = m_air * (h_in - h_mix) + pa.Q_DUCTO_W
    comb = Q_gen / (pa.PCI_CASCARA * pa.REND_GENERADOR)        # kg/s de cáscara
    Q_paredes = q_pl + sum(q_zonas)
    # balances de control
    agua_aire = m_air * (Y_exh - Y_mix)
    err_masa = (agua_aire - W) / max(W, 1e-9)
    H_aire_in = m_air * h_in
    H_aire_out = m_air * entalpia(T_exh, Y_exh)
    Hp_in = mdm * (pa.CP_SOLIDO + 4186.0 * X_feed) * T_guano
    Hp_out = mdm * (pa.CP_SOLIDO + 4186.0 * X_out) * T_out
    S_sorc = sum(s[4] for s in salida) * AREA_PISO              # calor de sorción [W]
    resid = H_aire_in + Hp_in - H_aire_out - Hp_out - Q_paredes - S_sorc - q_extra
    err_energia = resid / max(Q_gen, 1.0)
    # destino del calor del generador (cierra con el balance de arriba):
    #   Q_gen = ducto + evaporar + calentar el producto + sorción + paredes + escape
    # evaporar: el agua sale del guano como vapor a la temperatura de entrada del guano;
    # escape: calor sensible del aire y del vapor que se van por la chimenea
    Q_evap = W * hfg(T_guano)
    Q_prod = mdm * (pa.CP_SOLIDO + 4186.0 * X_out) * (T_out - T_guano)
    Q_util = Q_evap + Q_prod
    Q_escape = ((1.0 - r) * m_air * (CPA + CPV * Y_amb) * (T_exh - T_amb)
                + W * CPV * (T_exh - T_guano))
    # calor útil con la definición de la memoria (cap. 6.3): cuenta el agua evaporada como líquido
    # calentado hasta la temperatura de salida del producto
    dTp = T_out - T_guano
    Q_util_memoria = W * (4186.0 * dTp + 2.36e6) + mdm * pa.CP_SOLIDO * dTp + mdm * X_out * 4186.0 * dTp
    # estados reales: si una mezcla queda sobresaturada, el exceso es niebla
    Tm_r, Ym_v, niebla_mix = saturar(T_mix, Y_mix, P)
    Te_r, Ye_v, niebla_exh = saturar(T_exh, Y_exh, P)
    # pérdida de carga de cada piso (con el reparto calculado)
    dp_pisos = []
    for k in range(3):
        rho = rho_aire(st["Tin"][k], st["Yin"][k], P)
        u = (1.0 - prm[pa.I_BYP]) * G_piso * (1 + st["Yin"][k]) / rho * st["g"][k]
        dp_pisos.append(float(np.mean(outs[k][:, C_AERG] * u + outs[k][:, C_BERG] * u ** 2)))
    V_vent = m_air * (1 + Y_mix) / rho_aire(Tm_r, Ym_v, P) * 3600.0     # m³/h en los ventiladores
    P_vent = V_vent / 3600.0 * pa.VENTILADORES_PRESION / pa.VENTILADORES_REND
    # higienización (camino más desfavorable y promedio)
    hig_peor = hig_c.min(axis=0)
    hig_med = hig_m.mean(axis=0)
    # capa de entrada en el piso 1
    capa0 = w_dm[0] * volumen_lecho(X_feed, prm) * 1000.0
    t_res = [pa.LARGO_BANDA / v for v in vel]
    res = dict(
        cfg=cfg, convergio=convergio, iteraciones=len(historia), historia=historia,
        X_feed=X_feed, X_out=X_out, hum_out=X_out / (1 + X_out), T_prod_out=T_out,
        T_guano=T_guano, T_nave=T_nave, Y_amb=Y_amb,
        # Y_mix y Y_exh: agua total por kg de aire seco (vapor + niebla, si hay)
        T_mix=Tm_r, Y_mix=Y_mix, HR_mix=hr(Tm_r, Ym_v, P), niebla_mix=niebla_mix,
        T_exh=Te_r, Y_exh=Y_exh, HR_exh=hr(Te_r, Ye_v, P), niebla_exh=niebla_exh,
        T_rocio_exh=punto_rocio(Ye_v, P),
        T_bh_entrada=bulbo_humedo(cfg["T_aire"], Y_mix, P),
        Tin=list(st["Tin"]), Yin=list(st["Yin"]), Tout=Tout, Yout=Yout,
        W_kg_h=W * 3600.0, prod_kg_h=mdm * (1 + X_out) * 3600.0,
        Q_gen_kW=Q_gen / 1e3, comb_kg_h=comb * 3600.0, cenizas_kg_h=comb * pa.CENIZAS * 3600.0,
        Q_paredes_kW=Q_paredes / 1e3, Q_zonas_kW=[q_pl / 1e3] + [q / 1e3 for q in q_zonas],
        consumo_MJ_kg=Q_gen / max(W, 1e-9) / 1e6,
        Q_util_kW=Q_util / 1e3, Q_evap_kW=Q_evap / 1e3, Q_producto_kW=Q_prod / 1e3,
        Q_escape_kW=Q_escape / 1e3, Q_ducto_kW=pa.Q_DUCTO_W / 1e3, Q_fugas_kW=q_extra / 1e3,
        Q_sorcion_kW=S_sorc / 1e3, Q_util_memoria_kW=Q_util_memoria / 1e3,
        rendimiento=Q_util / Q_gen if Q_gen > 0 else 0.0,
        rendimiento_memoria=Q_util_memoria / Q_gen if Q_gen > 0 else 0.0,
        err_masa=err_masa, err_energia=err_energia,
        dp_pisos=dp_pisos, V_vent_m3h=V_vent, P_vent_kW=P_vent / 1e3,
        hig_peor=hig_peor, hig_med=hig_med, capa_mm=capa0, t_res_min=[t / 60 for t in t_res],
        vel=vel, w_dm=w_dm,
        perfiles=[o.copy() for o in outs], capasX=[c.copy() for c in capX], capasT=[c.copy() for c in capT],
        g=[gg.copy() for gg in st["g"]],
        estado=dict(T_exh=st["T_exh"], Y_exh=st["Y_exh"], Tin=list(st["Tin"]), Yin=list(st["Yin"]),
                    g=[gg.copy() for gg in st["g"]]),
        Xe_salida=humedad_equilibrio(hr(Te_r, Ye_v, P), Te_r, prm),
        cd03="fija",
    )
    return res


def con_regla_cd03(calculo, cfg):
    """Regla de la CD-03 del plano 18: la recirculación se cierra si el escape pasa de 45 g/kg.

    `calculo(cfg)` es `resolver` o una búsqueda que devuelve (resultado, estado). Si con la CD-03
    abierta el escape supera el límite, repite el cálculo con la CD-03 cerrada. En el resultado,
    "cd03" queda en "abierta", "cerrada" o "cicla" (cerrada, pero así el escape baja del límite y
    la regla la volvería a abrir: en la planta la compuerta abriría y cerraría).
    """
    sal = calculo(cfg)
    r = sal[0] if isinstance(sal, tuple) else sal
    if cfg["recirc"] <= 0.0 or r["Y_exh"] <= pa.Y_MAX_RECIRC:
        r["cd03"] = "abierta" if cfg["recirc"] > 0.0 else "cerrada"
        return sal
    Y_abierta = r["Y_exh"]
    sal2 = calculo(dict(cfg, recirc=0.0))
    r2 = sal2[0] if isinstance(sal2, tuple) else sal2
    r2["cd03"] = "cerrada" if r2["Y_exh"] > pa.Y_MAX_RECIRC else "cicla"
    r2["Y_exh_cd03_abierta"] = Y_abierta
    return sal2


def buscar_velocidad(cfg, objetivo=None, v_min=pa.VEL_BANDA_MIN, v_max=pa.VEL_BANDA_MAX, tol=2e-4):
    """Lazo MIC-01 en régimen: velocidad de banda que deja la humedad de salida en el objetivo.

    Devuelve (resultado, estado) con estado = "ok", "sobra" (aun a la velocidad máxima el producto
    sale más seco que el objetivo) o "falta" (a la velocidad mínima sale más húmedo).
    """
    obj = cfg["humedad_objetivo"] if objetivo is None else objetivo
    c = dict(cfg)
    c["vel"] = v_max
    r_hi = resolver(c)
    if r_hi["hum_out"] <= obj:
        return r_hi, "sobra"
    c["vel"] = v_min
    r_lo = resolver(c, inicial=r_hi["estado"])
    if r_lo["hum_out"] >= obj:
        return r_lo, "falta"
    lo, hi = math.log(v_min), math.log(v_max)
    f_lo, f_hi = r_lo["hum_out"] - obj, r_hi["hum_out"] - obj
    best = r_lo
    estado_prev = r_lo["estado"]
    for _ in range(30):
        # regula falsi con bisección de resguardo (en log v)
        x = hi - f_hi * (hi - lo) / (f_hi - f_lo)
        if not (lo + 0.05 * (hi - lo) < x < hi - 0.05 * (hi - lo)):
            x = 0.5 * (lo + hi)
        c["vel"] = math.exp(x)
        r = resolver(c, inicial=estado_prev)
        estado_prev = r["estado"]
        f = r["hum_out"] - obj
        best = r
        if abs(f) < tol:
            break
        if f > 0:
            hi, f_hi = x, f
        else:
            lo, f_lo = x, f
    return best, "ok"


def _biseccion(cfg, clave, lo, hi, objetivo, creciente, tol=2e-4, maxit=30):
    """Busca el valor de cfg[clave] en [lo, hi] que deja la humedad de salida en `objetivo`.

    `creciente`: True si la humedad de salida sube cuando sube el valor (p. ej. la alimentación).
    Devuelve (resultado, estado) con estado "ok", "bajo" (no se llega ni en el extremo favorable)
    o "alto" (se pasa aun en el extremo desfavorable).
    """
    c = dict(cfg)
    c[clave] = lo
    r_lo = resolver(c)
    c[clave] = hi
    r_hi = resolver(c, inicial=r_lo["estado"])
    f_lo, f_hi = r_lo["hum_out"] - objetivo, r_hi["hum_out"] - objetivo
    if creciente:
        if f_lo > 0:
            return r_lo, "falta"
        if f_hi < 0:
            return r_hi, "sobra"
    else:
        if f_lo < 0:
            return r_lo, "sobra"
        if f_hi > 0:
            return r_hi, "falta"
    est = r_hi["estado"]
    best = r_hi
    for _ in range(maxit):
        x = hi - f_hi * (hi - lo) / (f_hi - f_lo)
        if not (lo + 0.05 * (hi - lo) < x < hi - 0.05 * (hi - lo)):
            x = 0.5 * (lo + hi)
        c[clave] = x
        r = resolver(c, inicial=est)
        est = r["estado"]
        f = r["hum_out"] - objetivo
        best = r
        if abs(f) < tol:
            break
        if (f > 0) == creciente:
            hi, f_hi = x, f
        else:
            lo, f_lo = x, f
    return best, "ok"


def buscar_temperatura(cfg, T_min=70.0, T_max=pa.T_AIRE_MAX, objetivo=None):
    """Temperatura de entrada del aire que deja el producto en la humedad objetivo (banda fija)."""
    obj = cfg["humedad_objetivo"] if objetivo is None else objetivo
    return _biseccion(cfg, "T_aire", T_min, T_max, obj, creciente=False)


def capacidad(cfg, objetivo=None, a_min=300.0, a_max=3000.0):
    """Máxima alimentación [kg/h] que el secador lleva a la humedad objetivo (banda y aire fijos)."""
    obj = cfg["humedad_objetivo"] if objetivo is None else objetivo
    return _biseccion(cfg, "alimentacion", a_min, a_max, obj, creciente=True)


def resumen(r):
    """Texto corto con los números principales de una solución."""
    lin = [
        f"velocidad bandas      : {r['vel'][0] * 60:.3f} m/min  (capa {r['capa_mm']:.1f} mm, "
        f"residencia {sum(r['t_res_min']):.0f} min)",
        f"humedad salida        : {100 * r['hum_out']:.1f} % b.h.  (X = {r['X_out']:.3f})",
        f"temperatura producto  : {r['T_prod_out']:.1f} °C",
        f"agua evaporada        : {r['W_kg_h']:.1f} kg/h",
        f"aire mezcla / entrada : {r['T_mix']:.1f} °C, {1e3 * r['Y_mix']:.1f} g/kg",
        "aire bajo pisos 3/2/1 : " + " / ".join(f"{t:.1f}" for t in r['Tin'][::-1]) + " °C",
        f"escape                : {r['T_exh']:.1f} °C, {1e3 * r['Y_exh']:.1f} g/kg, HR {100 * r['HR_exh']:.0f} %, "
        f"rocío {r['T_rocio_exh']:.1f} °C",
        f"generador             : {r['Q_gen_kW']:.0f} kW  → cáscara {r['comb_kg_h']:.0f} kg/h",
        f"consumo específico    : {r['consumo_MJ_kg']:.2f} MJ/kg agua (rend. {100 * r['rendimiento']:.0f} %)",
        f"pérdidas por paredes  : {r['Q_paredes_kW']:.1f} kW",
        "ΔP lechos 1/2/3       : " + " / ".join(f"{d:.0f}" for d in r['dp_pisos']) + " Pa",
        f"higiene (peor camino) : {r['hig_peor'][0] / 60:.0f} min > 55 °C, {r['hig_peor'][1] / 60:.0f} min > 70 °C, "
        f"Salmonella −{r['hig_peor'][3]:.0f} log",
        f"balances              : masa {100 * r['err_masa']:+.3f} %, energía {100 * r['err_energia']:+.3f} %  "
        f"({r['iteraciones']} iteraciones, {'convergió' if r['convergio'] else 'NO convergió'})",
    ]
    return "\n".join(lin)
