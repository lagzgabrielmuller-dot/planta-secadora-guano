"""Psicrometría del aire húmedo y propiedades de transporte (funciones compiladas con numba).

Referencias:
  - Presión de saturación sobre agua líquida: ASHRAE Handbook Fundamentals (Hyland y Wexler),
    válida de 0 a 200 °C.
  - Viscosidad: ley de Sutherland. Difusividad vapor-aire: Marrero y Mason (1972).
Unidades: T en °C, presiones en Pa, Y en kg de vapor / kg de aire seco, entalpías en J/kg a.s.
"""
import math

from numba import njit

CPA = 1006.0        # J/kg·K, aire seco
CPV = 1860.0        # J/kg·K, vapor
CPW = 4186.0        # J/kg·K, agua líquida
LAMBDA0 = 2.501e6   # J/kg, calor latente a 0 °C
MW = 0.621945       # relación de masas molares agua/aire


@njit(cache=True)
def psat(T):
    """Presión de saturación del agua [Pa] a T [°C] (ASHRAE, Hyland-Wexler)."""
    Tk = T + 273.15
    if Tk < 273.16:
        Tk = 273.16
    ln = (-5.8002206e3 / Tk + 1.3914993 - 4.8640239e-2 * Tk + 4.1764768e-5 * Tk * Tk
          - 1.4452093e-8 * Tk * Tk * Tk + 6.5459673 * math.log(Tk))
    return math.exp(ln)


@njit(cache=True)
def Y_de_pv(pv, P):
    if pv >= 0.999 * P:
        pv = 0.999 * P
    return MW * pv / (P - pv)


@njit(cache=True)
def pv_de_Y(Y, P):
    return P * Y / (MW + Y)


@njit(cache=True)
def Ysat(T, P):
    return Y_de_pv(psat(T), P)


@njit(cache=True)
def hr(T, Y, P):
    """Humedad relativa (0-1)."""
    return pv_de_Y(Y, P) / psat(T)


@njit(cache=True)
def entalpia(T, Y):
    """Entalpía del aire húmedo [J/kg aire seco]."""
    return CPA * T + Y * (LAMBDA0 + CPV * T)


@njit(cache=True)
def temp_de_entalpia(h, Y):
    return (h - LAMBDA0 * Y) / (CPA + CPV * Y)


@njit(cache=True)
def hfg(T):
    """Calor latente de vaporización del agua [J/kg] a T, coherente con las entalpías de arriba."""
    return LAMBDA0 + (CPV - CPW) * T


@njit(cache=True)
def bulbo_humedo(T, Y, P):
    """Temperatura de saturación adiabática (≈ bulbo húmedo) [°C]."""
    h = entalpia(T, Y)
    lo, hi = -10.0, T
    if hi > 99.0:
        hi = 99.0
    for _ in range(60):
        tw = 0.5 * (lo + hi)
        ys = Ysat(tw, P)
        g = entalpia(tw, ys) - (ys - Y) * CPW * tw - h
        if g > 0.0:
            hi = tw
        else:
            lo = tw
    return 0.5 * (lo + hi)


@njit(cache=True)
def saturar(T, Y, P):
    """Estado real de un aire con más agua que la de saturación (p. ej. al mezclar dos corrientes
    casi saturadas): el exceso condensa como niebla con la misma entalpía total, y el calor latente
    que libera calienta un poco la mezcla.
    Devuelve (T, Y del vapor, niebla) con la niebla en kg de agua líquida por kg de aire seco."""
    if Y <= Ysat(T, P):
        return T, Y, 0.0
    h = entalpia(T, Y)
    lo, hi = T, T + 40.0
    for _ in range(60):
        t = 0.5 * (lo + hi)
        ys = Ysat(t, P)
        g = entalpia(t, ys) + (Y - ys) * CPW * t - h
        if g > 0.0:
            hi = t
        else:
            lo = t
    t = 0.5 * (lo + hi)
    ys = Ysat(t, P)
    return t, ys, Y - ys


@njit(cache=True)
def punto_rocio(Y, P):
    pv = pv_de_Y(Y, P)
    lo, hi = 0.01, 150.0
    for _ in range(60):
        t = 0.5 * (lo + hi)
        if psat(t) > pv:
            hi = t
        else:
            lo = t
    return 0.5 * (lo + hi)


@njit(cache=True)
def rho_aire(T, Y, P):
    """Densidad del aire húmedo [kg/m³]."""
    return P / (287.055 * (T + 273.15)) * (1.0 + Y) / (1.0 + 1.6078 * Y)


@njit(cache=True)
def mu_aire(T):
    Tk = T + 273.15
    return 1.716e-5 * (Tk / 273.15) ** 1.5 * (273.15 + 110.4) / (Tk + 110.4)


@njit(cache=True)
def k_aire(T):
    return 0.0241 * ((T + 273.15) / 273.15) ** 0.81


@njit(cache=True)
def difusividad_vapor(T, P):
    """Difusividad del vapor de agua en aire [m²/s] (Marrero y Mason)."""
    Tk = T + 273.15
    return 1.87e-10 * Tk ** 2.072 / (P / 101325.0)
