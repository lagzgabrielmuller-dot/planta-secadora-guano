"""Ajuste de la difusividad efectiva del agua en el guano a los ensayos de estufa publicados.

Ajusta D_ref, b y Ea de  D = D_ref·exp(b·(X − 0,5))·exp(−Ea/R·(1/T − 1/333,15 K))  y el coeficiente
de convección de la estufa de Liška y Kic (no informado), minimizando el error logarítmico en:
  - el tiempo hasta peso constante y la velocidad de las primeras 2 h de los 9 ensayos de
    Ghaly y MacDonald (2012), y
  - la humedad a 4,5 h (70 °C) y a 3 h (110 °C) y la velocidad inicial a 70 °C de Liška y Kic (2011).

Los valores de parametros.py (D_ref = 5,2·10⁻⁹ m²/s, b = 3,4, Ea = 27 kJ/mol) salieron de este ajuste
con la masa promedio de cada espesor. Con la masa de cada ensayo, como está ahora, el mínimo se corre a
D_ref = 1,03·10⁻⁸ m²/s, b = 5,4 y Ea = 22,4 kJ/mol, pero el error casi no cambia (suma 0,738 contra
0,741 con los valores adoptados): los ensayos dejan un valle largo en el que D_ref y b se compensan.
En el secador las dos combinaciones piden 102,2 y 101,5 °C para el 15 %, así que se dejaron los adoptados.

Uso:  python ajustar_cinetica.py      (unos 15 minutos)
"""
import time

import numpy as np
from scipy.optimize import minimize

from secado import parametros as pa
from secado.nucleo import secar_losa_horno
from validar import (GHALY_RHO, GHALY_TIEMPO, GHALY_VEL0, GHALY_X0, H_GHALY, LISKA_L0, LISKA_PUNTOS,
                     LISKA_VEL0_70, LISKA_X0, espesor_ghaly)

P = pa.P_ATM


def errores(th):
    dref, b, ea, hL = np.exp(th[0]), th[1], th[2] * 1e3, th[3]
    e = []
    prmG = pa.vector_parametros(dref=dref, db=b, ea=ea, x0=GHALY_X0, rhop0=GHALY_RHO)
    for (T, cm), t_med in GHALY_TIEMPO.items():
        r = secar_losa_horno(espesor_ghaly(T, cm), GHALY_X0, 22.0, float(T), 0.009, H_GHALY, P, prmG,
                             250 * 3600.0, 30.0, 1)
        t05 = float(np.interp(-0.05, -r[:, 1], r[:, 0]))
        vel = (GHALY_X0 - float(np.interp(2.0, r[:, 0], r[:, 1]))) / 2.0
        e += [np.log(t05 / t_med), np.log(vel / GHALY_VEL0[(T, cm)])]
    prmL = pa.vector_parametros(dref=dref, db=b, ea=ea, x0=LISKA_X0, rhop0=1000.0)
    for (T, t_h, xmin, xmax) in LISKA_PUNTOS:
        r = secar_losa_horno(LISKA_L0, LISKA_X0, 22.0, T, 0.010, hL, P, prmL, 9 * 3600.0, 10.0, 1)
        x = float(np.interp(t_h, r[:, 0], r[:, 1]))
        e.append(2.0 * np.log(x / np.sqrt(xmin * xmax)))          # al centro (geométrico) del rango
        if T == 70.0:
            v70 = (LISKA_X0 - float(np.interp(1.5, r[:, 0], r[:, 1]))) / 1.5
            e.append(np.log(v70 / np.mean(LISKA_VEL0_70)))
    return np.array(e)


def main():
    t0 = time.time()
    mejor = None
    for th0 in ([np.log(4e-10), 0.8, 40, 12], [np.log(1e-9), 2.0, 30, 10], [np.log(5e-9), 3.4, 27, 7.3]):
        r = minimize(lambda th: float(np.sum(errores(th) ** 2)), th0, method="Nelder-Mead",
                     options=dict(maxiter=500, xatol=1e-3, fatol=1e-5))
        print(f"desde {th0}: suma {r.fun:.4f}  D_ref {np.exp(r.x[0]):.3g}  b {r.x[1]:.3f}  "
              f"Ea {r.x[2]:.1f} kJ/mol  h {r.x[3]:.2f}  ({time.time() - t0:.0f} s)", flush=True)
        if mejor is None or r.fun < mejor.fun:
            mejor = r
    print(f"\nMEJOR: D_ref = {np.exp(mejor.x[0]):.3g} m²/s, b = {mejor.x[1]:.3f}, Ea = {mejor.x[2]:.1f} kJ/mol, "
          f"h estufa Liška = {mejor.x[3]:.2f} W/m²·K")
    print("adoptado en parametros.py:", pa.D_REF, pa.D_B, pa.EA_DIFUSION / 1e3)


if __name__ == "__main__":
    main()
