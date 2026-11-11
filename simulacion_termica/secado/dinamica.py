"""Simulación en el tiempo del secador con el lazo de humedad MIC-01 (PI + ajuste anticipado).

Cada piso se divide en `nc` celdas a lo largo de la banda; cada celda guarda la carga de sólido y
el estado de sus `nz` capas. En cada paso de tiempo:
  1. las bandas avanzan v·dt; cuando una banda recorre una celda, el producto de la última celda
     cae al piso siguiente (se mezcla) y entra producto nuevo en la primera;
  2. el aire atraviesa los pisos 3 → 2 → 1 (cuasi estacionario: el aire tarda menos de 1 s);
  3. el sensor de humedad MT-01 del sinfín de descarga mide con retardo de transporte y de primer
     orden;
  4. cada 30 s el PLC corrige la variable manipulada: la velocidad de las tres bandas (como en el
     informe) o la consigna de temperatura del aire (cascada sobre TIC-01).
"""
import math

import numpy as np
from numba import njit

from . import parametros as pa
from .nucleo import capa
from .psicrometria import Y_de_pv, entalpia, psat, rho_aire, temp_de_entalpia
from .secador import AREA_PISO, AREA_ZONAS, buscar_velocidad


@njit(cache=True)
def distribuir_aire(A, B, u_media, g):
    """Reparte el aire entre las celdas de un piso con la misma ΔP (caminos en paralelo, Ergun).
    Escribe en g (media 1) la fracción relativa de caudal de cada celda."""
    nc = A.shape[0]
    hi = 0.0
    for c in range(nc):
        a = max(A[c], 1e-9)
        b = max(B[c], 1e-12)
        v = a * u_media + b * u_media * u_media
        if v > hi:
            hi = v
    hi = hi * 4.0 + 1.0
    lo = 0.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        s = 0.0
        for c in range(nc):
            a = max(A[c], 1e-9)
            b = max(B[c], 1e-12)
            s += (-a + math.sqrt(a * a + 4.0 * b * mid)) / (2.0 * b)
        if s / nc > u_media:
            hi = mid
        else:
            lo = mid
    dp = 0.5 * (lo + hi)
    s = 0.0
    for c in range(nc):
        a = max(A[c], 1e-9)
        b = max(B[c], 1e-12)
        g[c] = (-a + math.sqrt(a * a + 4.0 * b * dp)) / (2.0 * b)
        s += g[c]
    for c in range(nc):
        g[c] = g[c] * nc / s
    return dp


@njit(cache=True)
def paso_piso(Xc, Tc, wc, tauc, g, Ac, Bc, Ta_in, Ya_in, G_media, dt, prm):
    """Un paso de tiempo de un piso completo.

    g: reparto relativo del aire por celda (media 1). Ac, Bc: salida, coeficientes de Ergun de
    cada celda (para el reparto del paso siguiente).
    Devuelve (h_salida, Y_salida, evaporación media por m² de banda).
    """
    nc, nz = Xc.shape
    P = prm[pa.I_P]
    byp = prm[pa.I_BYP]
    h_in = entalpia(Ta_in, Ya_in)
    sG = 0.0
    sh = 0.0
    sY = 0.0
    sE = 0.0
    for c in range(nc):
        Gloc = G_media * g[c]
        if wc[c] <= 1e-6:
            sG += Gloc
            sh += Gloc * h_in
            sY += Gloc * Ya_in
            Ac[c] = 0.0
            Bc[c] = 0.0
            continue
        G = (1.0 - byp) * Gloc
        m = wc[c] / nz
        nsub = int(math.ceil(dt / (0.3 * tauc[c])))
        if nsub < 1:
            nsub = 1
        if nsub > 200:
            nsub = 200
        dts = dt / nsub
        acc_h = 0.0
        acc_Y = 0.0
        acc_E = 0.0
        tmin = 1e30
        Aa = 0.0
        Bb = 0.0
        for s in range(nsub):
            Ta = Ta_in
            Ya = Ya_in
            for j in range(nz):
                E, Tout, Yout, Qc, dTdt, Xs, tau, A, B, H, S = capa(Xc[c, j], Tc[c, j], m, Ta, Ya, G, dts, prm, P)
                Xc[c, j] = max(Xc[c, j] - E * dts / m, 0.0)
                Tc[c, j] = Tc[c, j] + dTdt * dts
                acc_E += E
                if tau < tmin:
                    tmin = tau
                if s == 0:
                    Aa += A
                    Bb += B
                Ta = Tout
                Ya = Yout
            acc_h += entalpia(Ta, Ya)
            acc_Y += Ya
        tauc[c] = tmin
        Ac[c] = Aa
        Bc[c] = Bb
        sG += Gloc
        sh += Gloc * ((1.0 - byp) * acc_h / nsub + byp * h_in)
        sY += Gloc * ((1.0 - byp) * acc_Y / nsub + byp * Ya_in)
        sE += acc_E / nsub
    return sh / sG, sY / sG, sE / nc


class SecadorDinamico:
    """Secador SC-4 en el tiempo, inicializado desde la solución estacionaria."""

    def __init__(self, cfg, nc=120, dt=10.0):
        if len(set(cfg["factores_vel"])) != 1:
            raise ValueError("la simulación dinámica supone la misma velocidad en los tres pisos")
        self.cfg = dict(cfg)
        self.nz = int(cfg["nz"])
        self.nc = nc
        self.dt = dt
        self.prm = pa.vector_parametros(**cfg["prm"])
        self.dx = pa.LARGO_BANDA / nc
        self.UA = cfg["U_panel"] * AREA_ZONAS
        self.m_air = cfg["aire_seco"] / 3600.0
        self.G = self.m_air / AREA_PISO

    def inicializar(self, res):
        """Copia el estado de una solución estacionaria (perfiles a lo largo de cada piso)."""
        nz, nc = self.nz, self.nc
        self.X = np.zeros((3, nc, nz))
        self.T = np.zeros((3, nc, nz))
        self.w = np.zeros((3, nc))
        self.tau = np.full((3, nc), 5.0)
        self.g = np.ones((3, nc))
        self.A = np.zeros((3, nc))
        self.B = np.zeros((3, nc))
        xc = (np.arange(nc) + 0.5) * self.dx
        for k in range(3):
            xs = res["perfiles"][k][:, 0]
            for j in range(nz):
                self.X[k, :, j] = np.interp(xc, xs, res["capasX"][k][:, j])
                self.T[k, :, j] = np.interp(xc, xs, res["capasT"][k][:, j])
            self.w[k, :] = res["w_dm"][k]
            if self.cfg.get("distribuir", True):
                self.g[k, :] = np.interp(xc, xs, res["g"][k])
                self.g[k, :] /= self.g[k, :].mean()
        self.vel = float(res["vel"][0])
        self.fact = np.array(self.cfg["factores_vel"], float)
        self.avance = np.zeros(3)
        self.T_exh = res["T_exh"]
        self.Y_exh = res["Y_exh"]
        self.salida = []                 # producto que sale del piso 3: (X, T, w)
        self.res0 = res

    def _desplazar(self, k, entrada):
        """Corre el piso k una celda. Devuelve el estado (X, T, w) que cae del extremo."""
        sale = (self.X[k, -1].copy(), self.T[k, -1].copy(), float(self.w[k, -1]))
        self.X[k, 1:] = self.X[k, :-1]
        self.T[k, 1:] = self.T[k, :-1]
        self.w[k, 1:] = self.w[k, :-1]
        self.tau[k, 1:] = self.tau[k, :-1]
        self.g[k, 1:] = self.g[k, :-1]
        self.g[k, 0] = 1.0
        X, T, w = entrada
        self.X[k, 0] = X
        self.T[k, 0] = T
        self.w[k, 0] = w
        self.tau[k, 0] = 5.0
        return sale

    @staticmethod
    def _mezclar(estado, w_nuevo):
        X, T, w = estado
        cap = pa.CP_SOLIDO + 4186.0 * X
        Tm = float((cap * T).sum() / cap.sum())
        return np.full_like(X, X.mean()), np.full_like(T, Tm), w_nuevo

    def paso(self, entradas):
        """Avanza un dt. `entradas`: humedad_entrada, alimentacion, T_aire, T_amb, HR_amb."""
        cfg = self.cfg
        P = self.prm[pa.I_P]
        dt = self.dt
        hum = entradas["humedad_entrada"]
        Xf = hum / (1 - hum)
        mdm = entradas["alimentacion"] * (1 - hum) / 3600.0
        T_amb = entradas["T_amb"]
        T_nave = T_amb + pa.DT_NAVE
        vk = self.vel * self.fact
        # 1) avance de las bandas (el piso 1 recibe guano fresco, los otros lo que cae del anterior)
        for k in range(3):
            self.avance[k] += vk[k] * dt
        while self.avance.min() >= self.dx:
            entrada = (np.full(self.nz, Xf), np.full(self.nz, T_nave), mdm / (pa.ANCHO_BANDA * vk[0]))
            for k in range(3):
                cae = self._desplazar(k, entrada)
                if k < 2:
                    w_sig = cae[2] * vk[k] / vk[k + 1]
                    entrada = self._mezclar(cae, w_sig)
                else:
                    self.salida.append(cae)
                self.avance[k] -= self.dx
        # 2) aire
        Y_amb = Y_de_pv(entradas["HR_amb"] * psat(T_amb), P)
        r = cfg["recirc"]
        Y_mix = (1 - r) * Y_amb + r * self.Y_exh
        h_mix = (1 - r) * entalpia(T_amb, Y_amb) + r * entalpia(self.T_exh, self.Y_exh)
        cs = 1006.0 + 1860.0 * Y_mix
        Ta = entradas["T_aire"] - self.UA[0] * (entradas["T_aire"] - T_nave) / (self.m_air * cs)
        Ya = Y_mix
        T_salida_pisos = [0.0, 0.0, 0.0]
        evap = 0.0
        for idx, k in enumerate((2, 1, 0)):
            h_o, Y_o, E = paso_piso(self.X[k], self.T[k], self.w[k], self.tau[k], self.g[k], self.A[k],
                                    self.B[k], Ta, Ya, self.G, dt, self.prm)
            if cfg.get("distribuir", True) and self.w[k].min() > 1e-6:
                u_med = (1.0 - self.prm[pa.I_BYP]) * self.G * (1.0 + Ya) / rho_aire(Ta, Ya, P)
                gk = np.empty(self.nc)
                distribuir_aire(self.A[k], self.B[k], u_med, gk)
                self.g[k, :] = gk
            evap += E * AREA_PISO
            To = temp_de_entalpia(h_o, Y_o)
            T_salida_pisos[k] = To
            Ta = To - self.UA[idx + 1] * (To - T_nave) / (self.m_air * (1006.0 + 1860.0 * Y_o))
            Ya = Y_o
        self.T_exh, self.Y_exh = Ta, Ya
        Q_gen = self.m_air * (entalpia(entradas["T_aire"], Y_mix) - h_mix) + pa.Q_DUCTO_W
        return dict(T_out=T_salida_pisos, evap=evap, Q_gen=Q_gen, Y_mix=Y_mix)


def simular(cfg, horas, entradas_fn, control=None, nc=120, dt=10.0, inicial=None,
            tau_gen_min=5.0, rampa_gen=3.0):
    """Simula `horas` de operación del secador con el lazo de humedad MIC-01.

    entradas_fn(t_s) -> dict con humedad_entrada, alimentacion, T_amb, HR_amb y T_aire (consigna de
    TIC-01; si el lazo de humedad mueve la temperatura, este valor se usa solo al inicio).
    La temperatura real del aire sigue a su consigna con un primer orden de `tau_gen_min` minutos y
    una rampa máxima de `rampa_gen` K/min (hogar de cáscara + intercambiador + lazo TIC-01).

    control: None (lazo abierto) o dict con
      variable   "vel" (como el informe: MIC-01 mueve la velocidad de las bandas) o "T_aire"
                 (cascada: MIC-01 corrige la consigna de TIC-01; las bandas quedan fijas)
      Kc, Ti_min ganancia [(m/min) o K por punto de humedad] y tiempo integral [min]
      sp         consigna de humedad (fracción); por defecto cfg["humedad_objetivo"]
      Ts         período del PLC [s] (30); tau_sensor [s] (60); retardo_s [s] (120, transporte
                 por el sinfín de descarga hasta el MT-01)
      rampa      límite de cambio de la salida por minuto; lim (mín, máx)
      ff         None, "T_out3" (ajuste anticipado del informe con TT-04, Kff en (m/min)/K o K/K)
                 o "humedad_entrada" (sensor en el dosificador, Kff en K o (m/min) por punto,
                 aplicado con un retardo ff_retardo_s)
    """
    if inicial is None:
        inicial, _ = buscar_velocidad(cfg)
    sim = SecadorDinamico(cfg, nc=nc, dt=dt)
    sim.inicializar(inicial)
    v0 = sim.vel * 60.0
    e0 = entradas_fn(0.0)
    T_sp0 = float(e0.get("T_aire", cfg["T_aire"]))
    T_real = T_sp0
    T_sp = T_sp0
    n = int(horas * 3600 / dt)
    claves = ("t", "v", "T_aire", "T_aire_sp", "hum_real", "hum_medida", "T_prod", "T_exh", "Y_exh",
              "HR_exh", "T_out3", "comb", "hum_entrada", "capa_mm", "alarma", "alimentacion")
    serie = {k: np.zeros(n) for k in claves}
    hum_real = inicial["hum_out"]
    h_med = hum_real
    T_prod = inicial["T_prod_out"]
    integ = 0.0
    t_ctrl = 0.0
    alarma_t = 0.0
    var = control.get("variable", "vel") if control else None
    u0 = v0 if var == "vel" else T_sp0
    u_prev = u0
    n_ret = max(1, int(round((control or {}).get("retardo_s", 120.0) / dt)))
    buf = [hum_real] * n_ret
    n_ff = max(1, int(round((control or {}).get("ff_retardo_s", 0.0) / dt)) + 1)
    buf_ff = [e0["humedad_entrada"]] * n_ff
    hum_ref = e0["humedad_entrada"]
    T3_ref = None
    from .guano import volumen_lecho
    from .psicrometria import hr as _hr, saturar
    P = sim.prm[pa.I_P]
    for i in range(n):
        t = i * dt
        e = dict(entradas_fn(t))
        if var != "T_aire":
            T_sp = float(e.get("T_aire", T_sp))
        # lazo TIC-01: primer orden + rampa
        dT = (T_sp - T_real) * dt / (tau_gen_min * 60.0)
        lim_r = rampa_gen * dt / 60.0
        T_real += min(max(dT, -lim_r), lim_r)
        e["T_aire"] = T_real
        out = sim.paso(e)
        if sim.salida:
            Xs = np.array([s[0].mean() for s in sim.salida])
            ws = np.array([s[2] for s in sim.salida])
            caps = [(pa.CP_SOLIDO + 4186.0 * s[0]) for s in sim.salida]
            Ts_ = np.array([(c * s[1]).sum() / c.sum() for c, s in zip(caps, sim.salida)])
            Xm = float((Xs * ws).sum() / ws.sum())
            hum_real = Xm / (1 + Xm)
            T_prod = float((Ts_ * ws).sum() / ws.sum())
            sim.salida.clear()
        buf.append(hum_real)
        hum_sensor = buf.pop(0)
        buf_ff.append(e["humedad_entrada"])
        hum_in_ff = buf_ff.pop(0)
        if control is not None:
            tau_s = control.get("tau_sensor", 60.0)
            h_med += (hum_sensor - h_med) * dt / tau_s
            if T3_ref is None:
                T3_ref = control.get("T3_ref", out["T_out"][2])
            t_ctrl += dt
            if t_ctrl >= control.get("Ts", 30.0):
                err = 100.0 * (h_med - control.get("sp", cfg["humedad_objetivo"]))
                integ += err * t_ctrl / 60.0
                signo = -1.0 if var == "vel" else 1.0
                u = u0 + signo * control["Kc"] * (err + integ / control["Ti_min"])
                ff = control.get("ff")
                if ff == "T_out3":
                    # la salida de aire del piso 3 baja cuando llega producto más húmedo
                    u += -signo * control.get("Kff", 0.0) * (out["T_out"][2] - T3_ref)
                elif ff == "humedad_entrada":
                    u += signo * control.get("Kff", 0.0) * 100.0 * (hum_in_ff - hum_ref)
                rampa = control.get("rampa", 0.05 if var == "vel" else 2.0) * t_ctrl / 60.0
                u_pi = u
                u = min(max(u, u_prev - rampa), u_prev + rampa)
                if var == "vel":
                    lo, hi = control.get("lim", (pa.VEL_BANDA_MIN * 60, pa.VEL_BANDA_MAX * 60))
                else:
                    lo, hi = control.get("lim", (90.0, pa.T_AIRE_MAX))
                u_lim = min(max(u, lo), hi)
                if abs(u_lim - u_pi) > 1e-9:
                    # anti-windup: no integrar mientras la salida está recortada por los límites
                    # o por la rampa
                    integ -= err * t_ctrl / 60.0
                if var == "vel":
                    sim.vel = u_lim / 60.0
                else:
                    T_sp = u_lim
                u_prev = u_lim
                t_ctrl = 0.0
        else:
            h_med = hum_sensor
        if hum_real > 0.20:
            alarma_t += dt
        else:
            alarma_t = 0.0
        hum = e["humedad_entrada"]
        Xf = hum / (1 - hum)
        mdm = e["alimentacion"] * (1 - hum) / 3600.0
        serie["t"][i] = t / 3600.0
        serie["v"][i] = sim.vel * 60.0
        serie["T_aire"][i] = T_real
        serie["T_aire_sp"][i] = T_sp
        serie["hum_real"][i] = hum_real
        serie["hum_medida"][i] = h_med
        serie["T_prod"][i] = T_prod
        serie["T_exh"][i] = sim.T_exh
        serie["Y_exh"][i] = sim.Y_exh
        Te_r, Ye_v, _ = saturar(sim.T_exh, sim.Y_exh, P)
        serie["HR_exh"][i] = _hr(Te_r, Ye_v, P)
        serie["T_out3"][i] = out["T_out"][2]
        serie["comb"][i] = out["Q_gen"] / (pa.PCI_CASCARA * pa.REND_GENERADOR) * 3600.0
        serie["hum_entrada"][i] = hum
        serie["alimentacion"][i] = e["alimentacion"]
        serie["capa_mm"][i] = mdm / (pa.ANCHO_BANDA * sim.vel * sim.fact[0]) * volumen_lecho(Xf, sim.prm) * 1e3
        serie["alarma"][i] = 1.0 if alarma_t >= 900 else 0.0
    serie["T3_ref"] = T3_ref
    return serie
