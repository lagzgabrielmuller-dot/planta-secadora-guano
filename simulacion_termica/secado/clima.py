"""Clima de Crespo (estación Paraná Aero, normales 1991-2020) durante el turno de trabajo.

La planta trabaja un turno diurno de 8 h (≈ 7 a 15 h). Se toma como temperatura del turno la
media diaria más un cuarto de la amplitud térmica (la tarde es más cálida que el promedio del día)
y se supone que la humedad absoluta se mantiene en el día, de modo que la humedad relativa del
turno resulta menor que la media diaria.
"""
import numpy as np

from . import parametros as pa
from .psicrometria import Y_de_pv, hr, psat


def condiciones_turno(mes):
    """(T [°C], HR [0-1]) medias del turno para el mes 0..11."""
    T_med = pa.T_MED_MES[mes]
    amp = pa.T_MAX_MES[mes] - pa.T_MIN_MES[mes]
    T_turno = T_med + 0.25 * amp
    Y = Y_de_pv(pa.HR_MES[mes] * psat(T_med), pa.P_ATM)
    return float(T_turno), float(hr(T_turno, Y, pa.P_ATM))


def tabla_anual():
    filas = []
    for m in range(12):
        T, H = condiciones_turno(m)
        filas.append(dict(mes=pa.MESES[m], dias=int(pa.DIAS_MES[m]), T_media=float(pa.T_MED_MES[m]),
                          HR_media=float(pa.HR_MES[m]), T_turno=T, HR_turno=H))
    return filas


def dias_operacion_mes():
    """Reparte los 250 días de operación del año en proporción a los días de cada mes."""
    return pa.DIAS_MES / pa.DIAS_MES.sum() * pa.DIAS_ANIO


if __name__ == "__main__":
    for f in tabla_anual():
        print(f)
    print(np.round(dias_operacion_mes(), 1))
