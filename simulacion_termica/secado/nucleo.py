"""Núcleo numérico: avance del producto a lo largo de un piso del secador (compilado con numba).

Modelo de lecho atravesado por aire (through-circulation), en régimen estacionario:
  - El producto avanza con la banda (x = v·t). En cada posición el lecho se divide en `nz` capas
    de igual masa de sólido seco; el aire las atraviesa de abajo hacia arriba.
  - Cada capa es un conjunto de grumos esféricos de diámetro d(X) que se achican al secarse.
  - Transferencia externa de calor y masa: correlación de Wakao y Kaguei para lechos rellenos
    (Nu, Sh = 2 + 1,1·Re^0,6·Pr^(1/3), Sc^(1/3)), con eficiencia de capa 1 − e^(−NTU).
  - Resistencia interna: aproximación de fuerza impulsora lineal (LDF) para una esfera,
    dX/dt = −15·D/R²·(X − Xs), con difusividad de Arrhenius.
  - La superficie del grumo está en equilibrio con su humedad superficial Xs a través de la
    isoterma GAB: mientras Xs es alta, aw = 1 (período de velocidad constante); cuando la
    difusión interna no alcanza, Xs baja, aw < 1 y aparece el período de velocidad decreciente.
    Xs se obtiene igualando el flujo interno con el que se lleva el aire.
  - Balance de energía de cada capa con calor latente más calor de desorción. Si el producto está
    más frío que el punto de rocío del aire, condensa (precalentamiento del guano fresco).
  - Pérdida de carga de cada capa por Ergun (coeficientes A y B), para repartir el aire.
"""
import math

import numpy as np
from numba import njit

from . import parametros as pa
from .guano import actividad_agua, diametro, difusividad, factor_sorcion, porosidad, volumen_lecho, \
    volumen_particula
from .psicrometria import CPV, CPW, LAMBDA0, Y_de_pv, Ysat, difusividad_vapor, entalpia, hfg, k_aire, \
    mu_aire, psat, rho_aire

NOUT = 17
# columnas de `out`
C_X, C_T, C_XMED, C_XMIN, C_XMAX, C_TMED, C_TMIN, C_TMAX, C_TAOUT, C_YAOUT, C_G, C_EVAP, C_AERG, \
    C_BERG, C_ALTURA, C_QCONV, C_XS = range(NOUT)


@njit(cache=True)
def capa(Xj, Tj, m, Ta, Ya, G, dts, prm, P):
    """Intercambio de una capa durante dts. Devuelve (E, Tout, Yout, Qconv, dTdt, Xs, tau, A, B, H).

    E: evaporación [kg/(m²·s)] por m² de banda (negativa = condensación)
    Qconv: calor sensible del aire al producto [W/m²]
    tau: constante de tiempo térmica de la capa [s] (para elegir el subpaso)
    A, B: coeficientes de Ergun de la capa (ΔP = A·u + B·u²); H: altura de la capa [m]
    """
    vp = volumen_particula(Xj, prm)
    d = diametro(Xj, prm)
    eps = porosidad(Xj, prm)
    vb = volumen_lecho(Xj, prm)
    As = 6.0 * vp / d                     # m² de superficie por kg s.s.
    Acapa = m * As                        # m² por m² de banda
    H = m * vb
    rho = rho_aire(Ta, Ya, P)
    mu = mu_aire(Ta)
    ka = k_aire(Ta)
    Dva = difusividad_vapor(Ta, P)
    u = G * (1.0 + Ya) / rho
    Re = rho * u * d / mu
    Pr = 1006.0 * mu / ka
    Sc = mu / (rho * Dva)
    f06 = 1.1 * Re ** 0.6
    Nu = 2.0 + f06 * Pr ** (1.0 / 3.0)
    Sh = 2.0 + f06 * Sc ** (1.0 / 3.0)
    h = Nu * ka / d
    ky = Sh * Dva / d * rho / (1.0 + Ya)  # kg/(m²·s) por unidad de ΔY
    cs = 1006.0 + 1860.0 * Ya
    NTUh = h * Acapa / (G * cs)
    NTUm = ky * Acapa / G
    phih = 1.0 - math.exp(-NTUh)
    phim = 1.0 - math.exp(-NTUm)
    R = 0.5 * d
    kL = 15.0 * difusividad(Tj, Xj, prm) / (R * R)

    ps = psat(Tj)
    pvmax = 0.95 * P
    ysat_s = Y_de_pv(min(ps, pvmax), P)
    if ysat_s <= Ya:
        # condensación sobre el producto frío
        E = G * phim * (ysat_s - Ya)
        Xs = Xj
    else:
        lo = 0.0
        hi = Xj + 50.0
        for _ in range(48):
            mid = 0.5 * (lo + hi)
            aw = actividad_agua(mid, Tj, prm)
            ys = Y_de_pv(min(aw * ps, pvmax), P)
            f = m * kL * (Xj - mid) - G * phim * (ys - Ya)
            if f > 0.0:
                lo = mid
            else:
                hi = mid
        Xs = 0.5 * (lo + hi)
        E = m * kL * (Xj - Xs)

    Tout = Tj + (Ta - Tj) * math.exp(-NTUh)
    Yout = Ya + E / G
    ylim = Ysat(Tout, P)
    if Yout > ylim and E > 0.0:          # no puede salir sobresaturado
        Yout = max(ylim, Ya)
        E = G * (Yout - Ya)
    if Yout < 0.0:
        Yout = 0.0
    Qconv = G * (entalpia(Ta, Ya) - entalpia(Tout, Yout)) + E * (LAMBDA0 + CPV * Tj)
    cap = m * (prm[pa.I_CPS] + CPW * Xj)
    # con el agua del grumo (desorción o adsorción) va el calor de sorción; el agua que condensa
    # sobre un grumo más frío que el rocío es agua libre y solo entrega el latente
    lat = hfg(Tj) * factor_sorcion(Xs, prm) if ysat_s > Ya else hfg(Tj)
    S = E * (lat - hfg(Tj))               # calor de sorción por encima del latente [W/m²]
    dTdt = (Qconv - E * lat) / cap
    # constante de tiempo térmica de la capa: realimentación sensible + evaporativa.
    # dE/dT combina la resistencia externa con la interna (en el período decreciente la
    # evaporación casi no depende de T porque la limita la difusión).
    dlnps = hfg(Tj) / (461.5 * (Tj + 273.15) ** 2)
    awm = actividad_agua(Xs, Tj, prm)
    pvs = awm * ps
    if pvs < pvmax:
        fac = 0.621945 * P / ((P - pvs) * (P - pvs))
        dYdT = fac * pvs * dlnps
        dX = 1e-3 + 1e-3 * Xs
        dYdX = fac * ps * (actividad_agua(Xs + dX, Tj, prm) - awm) / dX
    else:
        dYdT = 0.0
        dYdX = 0.0
    ext = G * phim
    dEdT = m * kL * ext * dYdT / (m * kL + ext * dYdX + 1e-30)
    tau = cap / (G * cs * phih + hfg(Tj) * dEdT + 1e-12)
    # Ergun
    e3 = eps * eps * eps
    A = H * 150.0 * mu * (1.0 - eps) ** 2 / (e3 * d * d)
    B = H * 1.75 * rho * (1.0 - eps) / (e3 * d)
    return E, Tout, Yout, Qconv, dTdt, Xs, tau, A, B, H, S


@njit(cache=True)
def avanzar_piso(X, Tp, hig, Ta_in, Ya_in, g, w_dm, G_media, L, v, nx, prm, out, capasX, capasT):
    """Recorre un piso. X, Tp (nz,) y hig (nz, 4) se actualizan in situ.

    hig[:, 0] tiempo sobre 55 °C [s]; hig[:, 1] tiempo sobre 70 °C [s];
    hig[:, 2] F70 con z = 10 °C [min]; hig[:, 3] reducción logarítmica estimada de Salmonella.
    Devuelve (h_salida, Y_salida, Q_medio, E_medio, S_medio): entalpía y humedad del aire
    mezclado a la salida del piso (incluye el bypass) y, por m² de banda, el calor convectivo,
    la evaporación y el calor de desorción medios.
    """
    nz = X.shape[0]
    P = prm[pa.I_P]
    byp = prm[pa.I_BYP]
    d70 = prm[pa.I_D70]
    zs = prm[pa.I_Z]
    dt = L / (v * nx)
    dx = L / nx
    m = w_dm / nz
    h_in = entalpia(Ta_in, Ya_in)
    sumG = 0.0
    sumGh = 0.0
    sumGY = 0.0
    sumE = 0.0
    sumQ = 0.0
    sumS = 0.0
    nsub = 25
    t = 0.0
    for i in range(nx):
        Gloc = G_media * g[i]
        G = (1.0 - byp) * Gloc
        dts = dt / nsub
        acc_h = 0.0
        acc_Y = 0.0
        acc_E = 0.0
        acc_Q = 0.0
        acc_S = 0.0
        acc_xs = 0.0
        tau_min = 1e30
        Aerg = 0.0
        Berg = 0.0
        Htot = 0.0
        for s in range(nsub):
            Ta = Ta_in
            Ya = Ya_in
            Ecol = 0.0
            Qcol = 0.0
            Scol = 0.0
            for j in range(nz):
                E, Tout, Yout, Qc, dTdt, Xs, tau, A, B, H, S = capa(X[j], Tp[j], m, Ta, Ya, G, dts, prm, P)
                Scol += S
                X[j] = X[j] - E * dts / m
                if X[j] < 0.0:
                    X[j] = 0.0
                Tp[j] = Tp[j] + dTdt * dts
                Tj = Tp[j]
                if Tj >= 55.0:
                    hig[j, 0] += dts
                if Tj >= 70.0:
                    hig[j, 1] += dts
                hig[j, 2] += dts / 60.0 * 10.0 ** ((Tj - 70.0) / 10.0)
                if Tj >= 50.0:
                    hig[j, 3] += dts / 60.0 / (d70 * 10.0 ** ((70.0 - Tj) / zs))
                if tau < tau_min:
                    tau_min = tau
                if s == 0:
                    Aerg += A
                    Berg += B
                    Htot += H
                acc_xs += Xs
                Ecol += E
                Qcol += Qc
                Ta = Tout
                Ya = Yout
            acc_h += entalpia(Ta, Ya)
            acc_Y += Ya
            acc_E += Ecol
            acc_Q += Qcol
            acc_S += Scol
        t += dt
        h_tr = acc_h / nsub
        Y_tr = acc_Y / nsub
        # mezcla con el aire que se escapó por el bypass
        h_mix = (1.0 - byp) * h_tr + byp * h_in
        Y_mix = (1.0 - byp) * Y_tr + byp * Ya_in
        sumG += Gloc
        sumGh += Gloc * h_mix
        sumGY += Gloc * Y_mix
        sumE += acc_E / nsub
        sumQ += acc_Q / nsub
        sumS += acc_S / nsub
        # estadísticos del producto
        xm = 0.0
        tm = 0.0
        xmn = 1e9
        xmx = -1e9
        tmn = 1e9
        tmx = -1e9
        for j in range(nz):
            xm += X[j]
            tm += Tp[j]
            if X[j] < xmn:
                xmn = X[j]
            if X[j] > xmx:
                xmx = X[j]
            if Tp[j] < tmn:
                tmn = Tp[j]
            if Tp[j] > tmx:
                tmx = Tp[j]
            capasX[i, j] = X[j]
            capasT[i, j] = Tp[j]
        out[i, C_X] = (i + 1) * dx
        out[i, C_T] = t
        out[i, C_XMED] = xm / nz
        out[i, C_XMIN] = xmn
        out[i, C_XMAX] = xmx
        out[i, C_TMED] = tm / nz
        out[i, C_TMIN] = tmn
        out[i, C_TMAX] = tmx
        out[i, C_TAOUT] = (h_tr - LAMBDA0 * Y_tr) / (1006.0 + 1860.0 * Y_tr)
        out[i, C_YAOUT] = Y_tr
        out[i, C_G] = G
        out[i, C_EVAP] = acc_E / nsub
        out[i, C_AERG] = Aerg
        out[i, C_BERG] = Berg
        out[i, C_ALTURA] = Htot
        out[i, C_QCONV] = acc_Q / nsub
        out[i, C_XS] = acc_xs / (nsub * nz)
        # subpasos para el próximo tramo: dts ≤ 0,3·tau
        ns = int(math.ceil(dt / (0.3 * tau_min)))
        if ns < 1:
            ns = 1
        if ns > 400:
            ns = 400
        nsub = ns
    return sumGh / sumG, sumGY / sumG, sumQ / nx, sumE / nx, sumS / nx


@njit(cache=True)
def secar_losa_horno(L0, Xi, Ti, Taire, Yaire, h, P, prm, t_fin, dt, nz):
    """Prueba de capa fina en estufa (Ghaly y MacDonald 2012): pasta de espesor L0 en bandeja
    abierta arriba, aire que pasa por encima con coeficiente h. Modelo LDF de una losa con una
    cara sellada (dX/dt = −3·D/L²·(X − Xs)); el espesor se achica con el volumen.
    Devuelve una matriz (n, 3): tiempo [h], X medio, T.
    """
    n = int(t_fin / dt) + 1
    res = np.zeros((n, 3))
    X = Xi
    T = Ti
    x0 = prm[pa.I_X0]
    vp0 = (1.0 + x0) / prm[pa.I_RHOP0]
    m = L0 / vp0                           # kg s.s. por m² de bandeja
    cs = 1006.0 + 1860.0 * Yaire
    rho_aire(Taire, Yaire, P)
    ky = h / (cs * 0.89 ** (2.0 / 3.0)) * 1.0   # analogía de Chilton-Colburn (Le ≈ 0,89)
    for k in range(n):
        res[k, 0] = k * dt / 3600.0
        res[k, 1] = X
        res[k, 2] = T
        L = L0 * volumen_particula(X, prm) / vp0
        kL = 3.0 * difusividad(T, X, prm) / (L * L)
        ps = psat(T)
        lo = 0.0
        hi = X + 50.0
        for _ in range(48):
            mid = 0.5 * (lo + hi)
            ys = Y_de_pv(min(actividad_agua(mid, T, prm) * ps, 0.95 * P), P)
            f = m * kL * (X - mid) - ky * (ys - Yaire)
            if f > 0.0:
                lo = mid
            else:
                hi = mid
        Xs = 0.5 * (lo + hi)
        E = m * kL * (X - Xs)
        Q = h * (Taire - T)
        cap = m * (prm[pa.I_CPS] + CPW * X)
        T += (Q - E * hfg(T) * factor_sorcion(Xs, prm)) / cap * dt
        X -= E * dt / m
        if X < 0.0:
            X = 0.0
    return res
