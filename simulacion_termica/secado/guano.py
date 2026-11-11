"""Propiedades del guano de ponedora: isoterma, difusividad, contracción y estructura del lecho.

Todas las funciones reciben el vector de parámetros `prm` (ver parametros.vector_parametros).
"""
import math

from numba import njit

from . import parametros as pa

R_GAS = 8.314
RHO_W = 1000.0


@njit(cache=True)
def gab_constantes(T, prm):
    Xm = prm[pa.I_XM25] * math.exp(prm[pa.I_XMDT] * (T - 25.0))
    C = prm[pa.I_C25] * math.exp(prm[pa.I_CH] * (1.0 / (T + 273.15) - 1.0 / 298.15))
    K = prm[pa.I_K]
    return Xm, C, K


@njit(cache=True)
def humedad_equilibrio(aw, T, prm):
    """Humedad de equilibrio X_e [kg agua/kg s.s.] para actividad de agua aw (GAB)."""
    Xm, C, K = gab_constantes(T, prm)
    if aw > 0.999:
        aw = 0.999
    u = K * aw
    return Xm * C * u / ((1.0 - u) * (1.0 - u + C * u))


@njit(cache=True)
def actividad_agua(X, T, prm):
    """Inversa de la GAB: actividad de agua de la superficie con humedad X (recortada a 1)."""
    if X <= 0.0:
        return 0.0
    Xm, C, K = gab_constantes(T, prm)
    a = X * (C - 1.0)
    b = X * (C - 2.0) - Xm * C
    u = (b + math.sqrt(b * b + 4.0 * a * X)) / (2.0 * a)
    aw = u / K
    if aw > 1.0:
        aw = 1.0
    return aw


@njit(cache=True)
def factor_sorcion(X, prm):
    """Calor de desorción por encima del latente del agua libre: h_eff = hfg·(1 + A·e^(−B·X))."""
    if X < 0.0:
        X = 0.0
    return 1.0 + prm[pa.I_SA] * math.exp(-prm[pa.I_SB] * X)


@njit(cache=True)
def difusividad(T, X, prm):
    """Difusividad efectiva del agua en el grumo [m²/s]: Arrhenius en T, exponencial en X."""
    if X < 0.0:
        X = 0.0
    return (prm[pa.I_DREF] * math.exp(prm[pa.I_DB] * (X - prm[pa.I_XDREF]))
            * math.exp(-prm[pa.I_EA] / R_GAS * (1.0 / (T + 273.15) - 1.0 / (prm[pa.I_TREF] + 273.15))))


@njit(cache=True)
def volumen_particula(X, prm):
    """Volumen del grumo por kg de sólido seco [m³/kg s.s.] con contracción lineal en el agua."""
    x0 = prm[pa.I_X0]
    vp0 = (1.0 + x0) / prm[pa.I_RHOP0]
    vp = vp0 - prm[pa.I_BETAP] * (x0 - X) / RHO_W
    vmin = 1.0 / 1500.0 + max(X, 0.0) / RHO_W
    if vp < vmin:
        vp = vmin
    return vp


@njit(cache=True)
def volumen_lecho(X, prm):
    """Volumen aparente del lecho por kg s.s. [m³/kg] (pasa de 800 kg/m³ al 72 % a 500 al 15 %)."""
    x0 = prm[pa.I_X0]
    xf = prm[pa.I_XF_REF]
    vb0 = (1.0 + x0) / prm[pa.I_RHOB0]
    vbf = (1.0 + xf) / prm[pa.I_RHOBF]
    beta_b = (vb0 - vbf) / (x0 - xf)
    vb = vb0 - beta_b * (x0 - X)
    vp = volumen_particula(X, prm)
    if vb < vp / 0.85:
        vb = vp / 0.85
    return vb


@njit(cache=True)
def diametro(X, prm):
    vp0 = (1.0 + prm[pa.I_X0]) / prm[pa.I_RHOP0]
    return prm[pa.I_D0] * (volumen_particula(X, prm) / vp0) ** (1.0 / 3.0)


@njit(cache=True)
def porosidad(X, prm):
    e = 1.0 - volumen_particula(X, prm) / volumen_lecho(X, prm)
    if e < 0.15:
        e = 0.15
    if e > 0.60:
        e = 0.60
    return e
