"""Verificación a fatiga de las piezas del secador que trabajan con cargas variables.

Método: Budynas y Nisbett, «Diseño en ingeniería mecánica de Shigley», 8.ª ed., McGraw-Hill:
  cap. 6 (fatiga: límite de resistencia, factores de Marin, concentración de tensiones,
  sensibilidad a la muesca, Goodman, vida finita), cap. 7 (ejes: criterio DE-Goodman, ec. 7-8),
  cap. 8 (uniones abulonadas a fatiga) y cap. 11 (vida de rodamientos).
Ensayos de referencia (curva de Wöhler, flexión rotativa): D. H. Ruiz, «Fundamentos y ensayos en
materiales metálicos», INET, 2006 (apunte de cátedra); A. y C. E. González Arias, «Laboratorio de ensayos
industriales. Metales», 14.ª ed., Litenia, 1999 (cap. IX, fatiga), y las clases de Laboratorio de la escuela
(tracción, flexión y dureza Brinell, Rockwell y Vickers). Perfiles y barras disponibles: catálogo «Tablas y
equivalencias» de Acindar.

Cada verificación devuelve los datos, el reemplazo y el resultado para que la memoria (Word) y los
planos usen los mismos números. Lo llama calculos_memoria.py y queda en resultados.json["fatiga"].

    python fatiga.py      # imprime el resumen
"""
from __future__ import annotations

import json
import math
import os

KPSI = 6.894757  # MPa por kpsi
MM_IN = 25.4

# ------------------------------------------------------------------------------------------ materiales
# Shigley 8.ª ed., tabla A-20 (aceros laminados en caliente HR y estirados en frío CD), MPa
MATERIALES = {
    "SAE 1045 HR": {"Sut": 570, "Sy": 310, "HB": 163, "fuente": "Shigley tabla A-20"},
    "SAE 1045 CD": {"Sut": 630, "Sy": 530, "HB": 179, "fuente": "Shigley tabla A-20"},
    "SAE 1020 HR": {"Sut": 380, "Sy": 210, "HB": 111, "fuente": "Shigley tabla A-20"},
    "F-24 (IRAM-IAS U 500-503)": {"Sut": 370, "Sy": 240, "HB": 110, "fuente": "IRAM-IAS U 500-503"},
}
# Bulones y varillas roscadas (rosca laminada): Shigley tabla 8-11 (clases ISO) y tabla 8-17 (Se corregido)
BULONES = {
    "5.8": {"Sp": 380, "Sut": 520, "Sy": 420, "Se": 56},
    "8.8": {"Sp": 600, "Sut": 830, "Sy": 660, "Se": 129},
}

# Factores de concentración de tensiones de primera iteración (Shigley tabla 7-1) y leídos de las
# figuras A-15-8 y A-15-9 para el escalón del eje motriz (D/d = 1,2; r/d = 0,04)
KT = {
    "escalón bien redondeado (r/d = 0,1)": (1.7, 1.5),
    "escalón Ø60/Ø50, r = 2 mm (fig. A-15-8/9)": (1.95, 1.55),
    "chavetero fresado (r/d = 0,02)": (2.14, 3.0),
    "asiento de cubo con buje cónico (se asimila a escalón redondeado)": (1.7, 1.5),
    "asiento de rodamiento con prisioneros": (1.5, 1.3),
}


# ------------------------------------------------------------------------------------------ Shigley cap. 6
def se_prima(sut):
    """Límite de resistencia a la fatiga de la probeta rotativa (ec. 6-8)."""
    return 0.5 * sut if sut <= 1400 else 700.0


def ka(sut, acabado="maquinado"):
    """Factor de superficie (ec. 6-19, tabla 6-2), Sut en MPa."""
    a, b = {"rectificado": (1.58, -0.085), "maquinado": (4.51, -0.265),
            "laminado en caliente": (57.7, -0.718), "forjado": (272.0, -0.995)}[acabado]
    return a * sut ** b


def kb(d, carga="flexion"):
    """Factor de tamaño (ec. 6-20) para ejes rotativos en flexión o torsión; 1 en carga axial."""
    if carga == "axial":
        return 1.0
    if d <= 51:
        return 1.24 * d ** -0.107
    return 1.51 * d ** -0.157


KD_TEMP = {20: 1.000, 50: 1.010, 100: 1.020, 150: 1.025, 200: 1.020}  # tabla 6-4
KE_CONF = {50: 1.000, 90: 0.897, 95: 0.868, 99: 0.814, 99.9: 0.753}   # tabla 6-5


def q_neuber(sut, r_mm, torsion=False):
    """Sensibilidad a la muesca (ec. 6-35a y 6-35b, constante de Neuber con Sut en kpsi y r en pulgadas)."""
    s = sut / KPSI
    if torsion:
        raiz_a = 0.190 - 2.51e-3 * s + 1.35e-5 * s ** 2 - 2.67e-8 * s ** 3
    else:
        raiz_a = 0.246 - 3.08e-3 * s + 1.51e-5 * s ** 2 - 2.67e-8 * s ** 3
    return 1.0 / (1.0 + raiz_a / math.sqrt(r_mm / MM_IN))


def f_vida(sut):
    """Fracción f de Sut a 10³ ciclos (fig. 6-18; ajuste para 70 < Sut < 200 kpsi)."""
    s = sut / KPSI
    if s < 70:
        return 0.9
    return 1.06 - 2.8e-3 * s + 6.9e-6 * s ** 2


def marin(sut, d, acabado="maquinado", temp=20, conf=99, kf_varios=1.0, carga="flexion"):
    k = {"ka": ka(sut, acabado), "kb": kb(d, carga), "kc": 1.0 if carga != "axial" else 0.85,
         "kd": KD_TEMP.get(temp, 1.0), "ke": KE_CONF[conf], "kf": kf_varios}
    se = se_prima(sut)
    for v in k.values():
        se *= v
    return se, k


def eje_de_goodman(d, kf, kfs, ma, mm, ta, tm, se, sut, sy):
    """Ejes: criterio DE-Goodman (ec. 7-8), DE-Gerber (7-7) y fluencia de primer ciclo (7-15/7-16).
    d en mm, momentos en N·m. Devuelve tensiones (MPa) y coeficientes."""
    d_m = d / 1000
    c_b = 32 / (math.pi * d_m ** 3) / 1e6      # MPa por N·m (flexión)
    c_t = 16 / (math.pi * d_m ** 3) / 1e6      # MPa por N·m (torsión)
    sa = kf * ma * c_b
    sm = kf * mm * c_b
    ta_ = kfs * ta * c_t
    tm_ = kfs * tm * c_t
    s_a = math.sqrt(sa ** 2 + 3 * ta_ ** 2)       # von Mises alternante
    s_m = math.sqrt(sm ** 2 + 3 * tm_ ** 2)       # von Mises medio
    n_goodman = 1 / (s_a / se + s_m / sut)
    # DE-Gerber (ec. 7-7)
    A = math.sqrt(4 * (kf * ma) ** 2 + 3 * (kfs * ta) ** 2)
    B = math.sqrt(4 * (kf * mm) ** 2 + 3 * (kfs * tm) ** 2)
    if B > 0:
        n_gerber = 1 / ((8 * A / (math.pi * d_m ** 3 * se * 1e6)) * (1 + math.sqrt(1 + (2 * B * se / (A * sut)) ** 2)))
    else:
        n_gerber = se / s_a
    s_max = math.sqrt((sa + sm) ** 2 + 3 * (ta_ + tm_) ** 2)
    n_y = sy / s_max
    return {"sigma_a": sa, "sigma_m": sm, "tau_a": ta_, "tau_m": tm_, "vm_a": s_a, "vm_m": s_m,
            "vm_max": s_max, "n_goodman": n_goodman, "n_gerber": n_gerber, "n_fluencia": n_y}


def vida_finita(sigma_a, sigma_m, se, sut):
    """Ciclos hasta la falla con Basquin (ec. 6-13 a 6-16) y la tensión equivalente de Goodman.
    Devuelve math.inf si la tensión equivalente no supera Se (vida infinita)."""
    s_ar = sigma_a / (1 - sigma_m / sut) if sigma_m < sut else math.inf
    if s_ar <= se:
        return math.inf, s_ar
    f = f_vida(sut)
    a = (f * sut) ** 2 / se
    b = -math.log10(f * sut / se) / 3
    return (s_ar / a) ** (1 / b), s_ar


def ciclos(rpm, horas_dia, dias_anio, anios):
    return rpm * 60 * horas_dia * dias_anio * anios


# ------------------------------------------------------------------------------------------ datos de servicio
SERVICIO = {"horas_dia": 9.0, "dias_anio": 250, "anios": 20}   # 8 h de turno + calentamiento y vaciado
CONFIABILIDAD = 99   # %
N_ADM = 1.5          # coeficiente de seguridad mínimo adoptado a fatiga (cargas conocidas, material normal)
N_ADM_Y = 1.5        # a la fluencia del primer ciclo


def propiedades(mat, hb=None):
    """Sut y Sy del material; con hb, Sut estimada por la dureza Brinell (Sut ≈ 3,45·HB, clase de dureza
    y Shigley ec. 2-17) y Sy en la misma proporción Sy/Sut del material de tabla."""
    sut, sy = MATERIALES[mat]["Sut"], MATERIALES[mat]["Sy"]
    if hb is None:
        return sut, sy
    return 3.45 * hb, 3.45 * hb * sy / sut


def eje_motriz(mat="SAE 1045 HR", hb=None):
    """Eje del tambor motriz (4.2 y plano 03): SAE 1045 HR torneado, Ø60 con Ø50 en la corona Z75."""
    sut, sy = propiedades(mat, hb)
    rpm = 0.373                                   # tambor (plano 03)
    T = 471.0                                     # N·m, par de servicio (Fe·r = 2.978 N × 0,158 m)
    fluct = 0.15                                  # ±15 % de par por espesor de capa irregular
    P_H, P_V = 3489.0, 225.0                      # N por cubo: (T1+T2)/2 y medio peso del tambor
    Fc = 2069.0                                   # N, tiro de la cadena en la corona (plano V)
    u_ap, u_cubo, u_esc, u_cor = 1.370, 1.044, 1.455, 1.505   # m desde el centro del tambor
    # flector en cada sección (plano H: cargas simétricas de los cubos; plano V: peso + cadena en voladizo)
    def momento(u):
        """Flector combinado en la sección u (m desde el centro del tambor, lado Sur > 0).
        Plano H: los dos cubos con P_H, simétricos -> constante entre cubos, lineal hasta 0 en el apoyo.
        Plano V: peso en los cubos (flexión positiva) menos el voladizo de la cadena hacia abajo
        (flexión negativa, lineal desde 0 en A hasta Fc·(u_cor - u_ap) en B)."""
        if abs(u) <= u_cubo:
            mh, mw = P_H * (u_ap - u_cubo), P_V * (u_ap - u_cubo)
        elif abs(u) <= u_ap:
            mh, mw = P_H * (u_ap - abs(u)), P_V * (u_ap - abs(u))
        else:
            mh, mw = 0.0, 0.0
        if u <= u_ap:
            mc = -Fc * (u_cor - u_ap) * (u + u_ap) / (2 * u_ap)
        else:
            mc = -Fc * (u_cor - u)
        return math.hypot(mh, mw + mc)
    secciones = [
        ("S1", "asiento del cubo Sur (borde del buje cónico)", u_cubo, 60, "asiento de cubo con buje cónico (se asimila a escalón redondeado)", 3.0, T, 100, "rectificado"),
        ("S2", "asiento del rodamiento B (UCF 212)", u_ap, 60, "asiento de rodamiento con prisioneros", 3.0, T, 50, "maquinado"),
        ("S3", "escalón Ø60/Ø50, radio de acuerdo 2 mm", u_esc, 50, "escalón Ø60/Ø50, r = 2 mm (fig. A-15-8/9)", 2.0, T, 50, "maquinado"),
        ("S4", "chavetero de la corona Z75 (14×9, fresado)", u_esc + 0.014, 50, "chavetero fresado (r/d = 0,02)", 1.0, T, 50, "maquinado"),
    ]
    # S1 con terminación de torneado común, para mostrar por qué se pide rectificar el asiento del cubo
    se_t, _ = marin(sut, 60, "maquinado", temp=100, conf=CONFIABILIDAD, kf_varios=0.85)
    res = []
    for cod, nom, u, d, tipo, r, t, temp, acab in secciones:
        M = momento(u)
        kt, kts = KT[tipo]
        q, qs = q_neuber(sut, r), q_neuber(sut, r, torsion=True)
        kf, kfs = 1 + q * (kt - 1), 1 + qs * (kts - 1)
        se, k = marin(sut, d, acab, temp=temp, conf=CONFIABILIDAD, kf_varios=0.85)
        g = eje_de_goodman(d, kf, kfs, ma=M, mm=0.0, ta=fluct * t, tm=t, se=se, sut=sut, sy=sy)
        N, s_ar = vida_finita(g["vm_a"], g["vm_m"], se, sut)
        res.append({"cod": cod, "seccion": nom, "u_mm": round(u * 1000), "d": d, "M": round(M, 1), "T": t,
                    "temp": temp, "acabado": acab,
                    "Kt": kt, "Kts": kts, "r": r, "q": round(q, 3), "qs": round(qs, 3), "Kf": round(kf, 3),
                    "Kfs": round(kfs, 3), "Se": round(se, 1), "marin": {a: round(b, 3) for a, b in k.items()},
                    **{a: round(b, 2) for a, b in g.items()},
                    "N_falla": "infinita" if N == math.inf else f"{N:.3g}", "s_ar": round(s_ar, 1)})
    critica = min(res, key=lambda x: x["n_goodman"])
    n_ciclos = ciclos(rpm, **SERVICIO)
    # caso de atascamiento: el motor entrega su par máximo limitado por el variador
    t_motor = 0.75e3 / (2 * math.pi * 1400 / 60)          # N·m nominal del motor
    i_total, eta_red, eta_cad = 1500, 0.40, 0.95           # reductor doble sinfín-corona 1:300 y cadena 1:5
    t_atasco = 1.5 * t_motor * i_total * eta_red * eta_cad  # 150 % de corriente en el VFD
    tau_atasco = 16 * t_atasco / (math.pi * 0.050 ** 3) / 1e6   # Ø50, sin Kt: fluencia estática de un material dúctil
    sy_corte = 0.577 * sy
    t_limite = 1.5 * T                                       # límite de par a programar en el VFD
    tau_lim = 16 * t_limite / (math.pi * 0.050 ** 3) / 1e6
    # S1 torneado (comparación)
    s1 = res[0]
    g_t = eje_de_goodman(60, s1["Kf"], s1["Kfs"], ma=s1["M"], mm=0, ta=fluct * T, tm=T, se=se_t, sut=sut, sy=sy)
    return {"material": mat, "Sut": sut, "Sy": sy, "rpm": rpm, "T": T, "fluct": fluct, "P_H": P_H, "P_V": P_V,
            "Fc": Fc, "Se_prima": se_prima(sut), "secciones": res, "critica": critica["cod"],
            "n_min": critica["n_goodman"], "ciclos_vida": round(n_ciclos), "anios": SERVICIO["anios"],
            "atasco": {"T_motor": round(t_motor, 2), "i": i_total, "eta": eta_red * eta_cad,
                       "T_atasco": round(t_atasco), "tau": round(tau_atasco, 1), "Sys": round(sy_corte, 1),
                       "n": round(sy_corte / tau_atasco, 2), "T_limite_VFD": round(t_limite),
                       "tau_limite": round(tau_lim, 1), "n_limite": round(sy_corte / tau_lim, 1)},
            "S1_torneado": {"Se": round(se_t, 1), "n_goodman": round(g_t["n_goodman"], 2)},
            "verifica": critica["n_goodman"] >= N_ADM and all(s["n_fluencia"] >= N_ADM_Y for s in res)
                        and sy_corte / tau_lim >= 2}


def eje_reenvio(mat="SAE 1045 HR", hb=None):
    """Eje del tambor de reenvío (4.3): no transmite par; flexión rotativa por las dos ramas de la banda.
    Se compara la ejecución actual Ø50 constante con la propuesta Ø60 entre cubos y muñones Ø50."""
    sut, sy = propiedades(mat, hb)
    t2 = 2000.0                                       # N, tensión del ramal flojo (Fe = 2.978 N actúa en el motriz)
    f_ret = 0.25 * 9.81 * 288 * 1.15                 # fricción del ramal de retorno (tabla 8 de la memoria)
    t_cola = t2 + f_ret                               # tensión en la cola (ambas ramas)
    P_H = t_cola                                      # N por cubo (2·t_cola repartido en 2 discos)
    P_V = 175.0                                       # medio peso del tambor Ø250
    brazo = 1.370 - 1.044
    M = math.hypot(P_H, P_V) * brazo
    casos = []
    for nombre, d, tipo, r in (("Ø50 constante (actual)", 50, "asiento de cubo con buje cónico (se asimila a escalón redondeado)", 3.0),
                               ("Ø60 en cubos, muñones Ø50 (propuesto)", 60, "asiento de cubo con buje cónico (se asimila a escalón redondeado)", 3.0)):
        kt, kts = KT[tipo]
        q = q_neuber(sut, r)
        kf = 1 + q * (kt - 1)
        se, k = marin(sut, d, "maquinado", temp=50, conf=CONFIABILIDAD, kf_varios=0.85)
        g = eje_de_goodman(d, kf, 1.0, ma=M, mm=0, ta=0, tm=0, se=se, sut=sut, sy=sy)
        N, _ = vida_finita(g["vm_a"], 0, se, sut)
        casos.append({"caso": nombre, "d": d, "Kf": round(kf, 3), "Se": round(se, 1), "sigma_a": round(g["sigma_a"], 1),
                      "n": round(g["n_goodman"], 2), "N_falla": "infinita" if N == math.inf else f"{N:.3g}"})
    # muñón Ø50 del eje propuesto, en el escalón junto al rodamiento (M pequeño: brazo 30 mm)
    m_mun = math.hypot(P_H, P_V) * 0.030
    q = q_neuber(sut, 2.0)
    kf = 1 + q * (1.95 - 1)
    se, _ = marin(sut, 50, "maquinado", temp=50, conf=CONFIABILIDAD, kf_varios=0.85)
    n_mun = se / (kf * 32 * m_mun / (math.pi * 0.05 ** 3) / 1e6)
    return {"t_cola": round(t_cola), "f_ret": round(f_ret), "P_H": round(P_H), "brazo": brazo, "M": round(M, 1),
            "casos": casos, "n_munon": round(n_mun, 1), "rpm": 0.0062 * 60 / (math.pi * 0.25)}


def chaveta():
    """Chaveta paralela 14×9×63 DIN 6885 A (acero C45) de la corona Z75 sobre el eje Ø50."""
    T, fluct = 471.0, 0.15
    d, b, h, L, t1 = 50, 14, 9, 63, 5.5
    l_ef = L - b                                      # forma A: extremos redondeados
    F = T / (d / 2000)
    tau_m = F / (b * l_ef)                            # MPa
    tau_a = fluct * tau_m
    sigma_ap = F / ((h - t1) * l_ef)
    mat = MATERIALES["SAE 1045 HR"]
    se, _ = marin(mat["Sut"], 14, "maquinado", conf=CONFIABILIDAD, carga="flexion")
    se_s = 0.577 * se
    sus = 0.67 * mat["Sut"]
    n_f = 1 / (tau_a / se_s + tau_m / sus)
    return {"F": round(F), "tau_m": round(tau_m, 1), "tau_a": round(tau_a, 1), "sigma_ap": round(sigma_ap, 1),
            "Se_corte": round(se_s, 1), "Sus": round(sus), "n_fatiga": round(n_f, 1),
            "n_aplast": round(mat["Sy"] / sigma_ap, 1), "l_ef": l_ef}


def cadena():
    """Cadena ASA 60 (RS60) simple: tiro de servicio frente a la carga máxima admisible por fatiga del
    fabricante (Tsubaki: 1.980 lb = 8,81 kN, basada en la resistencia a la fatiga de las placas) y a la
    rotura mínima ANSI B29.1 (7.030 lb = 31,3 kN)."""
    Fc = 2069.0
    k_choque = 1.3                                    # arranques con VFD (rampa) y capa irregular
    f_adm_fatiga = 1980 * 4.448
    f_rot = 7030 * 4.448
    f_serv = Fc * k_choque
    return {"Fc": Fc, "k": k_choque, "F_servicio": round(f_serv), "F_adm_fatiga": round(f_adm_fatiga),
            "F_rotura_min": round(f_rot), "n_fatiga": round(f_adm_fatiga / f_serv, 2),
            "n_rotura": round(f_rot / Fc, 1)}


def rodamientos():
    """Vida a fatiga de rodadura L10 (Shigley cap. 11): rodamientos de bolas, exponente 3."""
    filas = []
    for nom, C, C0, P, rpm in (("UCF 212 - apoyo B del tambor motriz", 52.5, 36.0, 4.364, 0.373),
                               ("UCF 212 - apoyo A del tambor motriz", 52.5, 36.0, 3.506, 0.373),
                               ("UCT 210 - tambor de reenvío", 35.0, 23.2, 2.818, 0.47)):
        l10 = (C / P) ** 3                               # millones de revoluciones
        horas = l10 * 1e6 / (60 * rpm)
        filas.append({"rodamiento": nom, "C": C, "C0": C0, "P": P, "rpm": round(rpm, 3), "L10_Mrev": round(l10),
                      "L10_h": f"{horas:.2e}", "s0": round(C0 / P, 1)})
    return {"filas": filas, "nota": "a tan baja velocidad la vida a fatiga es prácticamente ilimitada; manda la "
                                    "capacidad estática (s0 ≥ 2 para cargas con choques leves, catálogo NTN/SKF)."}


def masa_secador():
    """Masa del secador SC-4 por componentes (pesos de catálogo de perfiles y chapas; ver memoria 7.6)."""
    g = 9.81
    filas = [
        ("Columnas UPN 120 (10 × 3,4 m × 13,4 kg/m)", 10 * 3.4 * 13.4),
        ("Vigas longitudinales IPN 140 (4 × 13 m × 14,3 kg/m)", 4 * 13 * 14.3),
        ("Travesaños L 50×50×5 (39 × 2,6 m × 3,77 kg/m)", 39 * 2.6 * 3.77),
        ("Placas base 200×200×12 (10 × 3,8 kg)", 10 * 0.2 * 0.2 * 0.012 * 7850),
        ("Paneles sándwich 80 mm (161 m² × 17 kg/m²)", 161 * 17),
        ("Bandas de malla AISI 304 (3 × 25 m × 2 m × 12 kg/m²)", 3 * 25 * 2 * 12),
        ("Tambores motrices con eje (3 × 145 kg)", 3 * 145),
        ("Tambores de reenvío con eje y tensores (3 × 115 kg)", 3 * 115),
        ("Motorreductores 0,75 kW 1:300 con base y cadena (3 × 65 kg)", 3 * 65),
        # Rev. F: guías de PTFE en los pisos 2 y 3 (densidad 2,17 contra 0,94 del UHMW-PE: +113 kg) y faldones
        ("Guías (PTFE pisos 2-3, UHMW-PE piso 1), guías laterales inox, tolvas de caída", 820 + 113),
        ("Faldones de sellado de bordes AISI 304 1,5 mm (6 × 11,6 m × 0,32 m)", 6 * 11.6 * 0.32 * 0.0015 * 7930),
        ("Plenum, campana de salida y bridas de ductos", 640),
        ("Pasarela superior 4.13 con barandas y escalera", 600),
        ("Rodillos de retorno Ø89 (15 × 9 kg)", 15 * 9),
    ]
    total = sum(m for _, m in filas)
    res = {"filas": [(n, round(m)) for n, m in filas], "total_kg": round(total), "peso_kN": round(total * g / 1000, 1)}
    # control cruzado con el modelo 3D (secadora/modelo_3d/piezas.json, masas pieza por pieza del CadQuery)
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "secadora", "modelo_3d", "piezas.json")
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as fh:
            cad = sum(p["masa_kg"] for p in json.load(fh)["piezas"])
        res["modelo_cad_kg"] = round(cad)
        res["dif_cad_pct"] = round((cad - total) / total * 100, 1)
        # para los anclajes se toma la mayor de las dos estimaciones (del lado de la seguridad)
        res["total_kg"] = round(max(total, cad))
        res["peso_kN"] = round(res["total_kg"] * g / 1000, 1)
    return res


def anclajes():
    """Anclajes químicos de las placas base (Shigley cap. 8 a fatiga + resistencia de catálogo del anclaje).
    a) Secador SC-4: 10 placas 200×200×12 con 4 varillas M16 clase 5.8 en resina epoxi (h_ef 125 mm).
    b) Base de un ventilador de impulsión M1/M2 (15 kW): 4 varillas M16 8.8, desbalanceo G 6,3."""
    g = 9.81
    ms = masa_secador()
    m_producto = 1080.0                               # kg de guano en proceso (memoria 6.6)
    n_placas, n_var = 10, 4
    peso = (ms["total_kg"] + m_producto) * g
    v_por_placa = peso / n_placas
    # horizontal: el tiro de las tres cadenas se cierra dentro del bastidor salvo la componente que pasa
    # por la base del motorreductor (se toma la mitad), más una fricción de arranque de las bandas
    h_total = 3 * 2069.0 * 0.5 + 0.05 * peso
    h_por_varilla = h_total / (n_placas * n_var)
    a_s = 157.0                                        # mm², área resistente M16
    tau = h_por_varilla / a_s
    # sismo: Crespo está en zona sísmica 0 (INPRES-CIRSOC 103) -> no se considera; dentro de la nave no hay viento
    # resistencias de diseño típicas de catálogo para varilla M16 5.8 en epoxi, hormigón H-21 no fisurado,
    # h_ef = 125 mm (orden de magnitud Hilti HIT-RE 500 / Fischer FIS EM): verificar con el producto elegido
    n_rd, v_rd = 26.0, 15.0
    util_v = h_por_varilla / 1000 / v_rd
    # par de apriete de la varilla M16 (catálogo de anclajes químicos) y precarga resultante
    t_inst = 80.0                                      # N·m
    k_rosca = 0.2
    f_pre = t_inst / (k_rosca * 0.016) / 1000         # kN (ec. 8-27)
    # b) ventilador de impulsión: desbalanceo residual ISO 21940-11 grado G 6,3 y caso de polvo adherido (10×)
    rpm_v, m_rot = 1450, 70.0
    w = 2 * math.pi * rpm_v / 60
    e_per = 6.3 / w / 1000
    f_unb = m_rot * e_per * w ** 2
    f_unb_falla = f_unb * 10
    p_bul = 4
    b8 = BULONES["8.8"]
    at = 157.0
    fp = b8["Sp"] * at / 1000
    fi = 0.75 * fp                                     # precarga recomendada (ec. 8-31)
    C = 0.25                                           # rigidez relativa de la unión (bancada sobre amortiguadores)
    p_a = f_unb_falla / p_bul / 1000
    sigma_a = C * p_a * 1000 / (2 * at)
    sigma_i = fi * 1000 / at
    sigma_m = sigma_a + sigma_i
    nf = b8["Se"] * (b8["Sut"] - sigma_i) / (b8["Sut"] * sigma_a + b8["Se"] * (sigma_m - sigma_i))   # ec. 8-38
    return {"masa": ms, "secador": {"m_kg": round(ms["total_kg"] + m_producto), "V_placa_kN": round(v_por_placa / 1000, 1),
                                    "H_total_N": round(h_total), "H_var_N": round(h_por_varilla), "tau_MPa": round(tau, 1),
                                    "N_Rd": n_rd, "V_Rd": v_rd, "uso_V_pct": round(100 * util_v, 1), "placas": n_placas,
                                    "varillas": n_var, "T_inst": t_inst, "F_pre_kN": round(f_pre, 1),
                                    "sigma_apoyo_MPa": round(v_por_placa / (200 * 200), 2)},
            "ventilador": {"rpm": rpm_v, "m_rotor": m_rot, "e_um": round(e_per * 1e6, 1), "F_unb_N": round(f_unb, 1),
                           "F_falla_N": round(f_unb_falla), "Fi_kN": round(fi, 1), "sigma_a": round(sigma_a, 2),
                           "sigma_i": round(sigma_i), "n_f": round(nf, 1)}}


def mensula():
    """Ménsula PL 12 soldada a la columna UPN 120 que sostiene el UCF 212 del apoyo B (plano 03).
    Dos cordones de filete de 6 mm × 370 mm; reacción R con ±15 % de fluctuación, brazo 150 mm."""
    R, fl, e = 4364.0, 0.15, 0.150
    h, l = 6.0, 370.0
    t = 0.707 * h
    area = 2 * t * l
    I = 2 * t * l ** 3 / 12
    sigma = R * e * 1000 * (l / 2) / I           # MPa (flexión del grupo de soldadura)
    tau = R / area
    s_m = math.hypot(sigma, tau)
    s_a = fl * s_m
    kfs = 2.7                                     # extremo de filete paralelo (Shigley tabla 9-5)
    sut_e60 = 427.0                               # electrodo E60xx (Shigley tabla 9-3)
    se, _ = marin(sut_e60, 12, "forjado", conf=CONFIABILIDAD)   # cordón en bruto de soldadura
    sse = 0.59 * se                               # kc = 0,59 para corte (Shigley ec. 6-26, ejemplo 9-6)
    ssu = 0.67 * sut_e60                          # Ssu = 0,67·Sut (Shigley ec. 6-54)
    n = 1 / (kfs * s_a / sse + kfs * s_m / ssu)
    return {"R": R, "e": e, "h": h, "l": l, "sigma": round(sigma, 2), "tau": round(tau, 2), "s_a": round(s_a, 2),
            "s_m": round(s_m, 2), "Kfs": kfs, "Sse": round(sse, 1), "n": round(n, 1)}


def ensayo_wohler():
    """Plan del ensayo de flexión rotativa (apunte INET) con 12 probetas del mismo lote de SAE 1045 de los
    ejes: niveles de tensión y vida esperada por Basquin con Se' = 0,5 Sut (probeta pulida de 7,5 mm)."""
    sut = MATERIALES["SAE 1045 HR"]["Sut"]
    se = se_prima(sut)
    f = f_vida(sut)
    a = (f * sut) ** 2 / se
    b = -math.log10(f * sut / se) / 3
    niveles = []
    for frac in (0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.56, 0.53, 0.51, 0.50, 0.48, 0.46):
        s = frac * sut
        n = (s / a) ** (1 / b) if s > se else math.inf
        niveles.append({"S": round(s), "frac": frac, "N": "> 10⁶ (no rompe)" if n == math.inf or n > 1e6 else f"{n:.2e}"})
    return {"Sut": sut, "Se_prima": se, "f": round(f, 3), "a": round(a, 1), "b": round(b, 4), "niveles": niveles,
            "probetas": len(niveles)}


def d_impronta(hb, P=3000.0, D=10.0):
    """Diámetro de la impronta Brinell (mm) para una dureza dada: HB = 2P / (π·D·(D − √(D² − d²)))."""
    h = 2 * P / (math.pi * D * hb)
    return math.sqrt(D ** 2 - (D - h) ** 2)


def recepcion_material():
    """Material de los ejes y control de recepción por dureza Brinell.
    Acindar lamina barras redondas en grados 1008 a 1020 y el 1045 solo a pedido: se verifica qué pasa si el
    eje se hace con el acero de stock (SAE 1020) y cuál es la dureza mínima que asegura n ≥ N_ADM."""
    stock = "SAE 1020 HR"
    m20, r20 = eje_motriz(stock), eje_reenvio(stock)
    hb_min = None
    for hb in range(140, 191):
        if (eje_motriz(hb=hb)["n_min"] >= N_ADM
                and eje_reenvio(hb=hb)["casos"][1]["n"] >= N_ADM):
            hb_min = hb
            break
    hb_adop = 5 * math.ceil(hb_min / 5)          # criterio de aceptación redondeado hacia arriba
    hb_max = 190                                 # por encima, colada fuera de lo normal para un 1045 HR
    m_min = eje_motriz(hb=hb_min)
    return {
        "stock": stock, "n_motriz_stock": round(m20["n_min"], 2), "n_reenvio_stock": r20["casos"][1]["n"],
        "hb_min": hb_min, "hb_adop": hb_adop, "hb_max": hb_max, "sut_hb_min": round(3.45 * hb_min), "n_hb_min": round(m_min["n_min"], 2),
        "d_max": round(d_impronta(hb_adop), 2), "d_min": round(d_impronta(hb_max), 2),
        "brinell": {"designacion": "HB 10/3000/15", "D": 10, "P": 3000, "C": 30, "t": "10 a 15 s",
                    "d_D": "0,25 a 0,50", "borde": "2,5·d", "entre_centros": "4·d", "espesor": "10·h"},
        "probetas_wohler_min": 12, "probetas_wohler_rigurosa": 50,
    }


def calc_fatiga():
    return {"servicio": SERVICIO, "confiabilidad": CONFIABILIDAD, "n_adm": N_ADM,
            "materiales": MATERIALES, "eje_motriz": eje_motriz(), "eje_reenvio": eje_reenvio(),
            "chaveta": chaveta(), "cadena": cadena(), "rodamientos": rodamientos(),
            "anclajes": anclajes(), "mensula": mensula(),
            "wohler": ensayo_wohler(), "recepcion": recepcion_material()}


if __name__ == "__main__":
    import json
    r = calc_fatiga()
    em = r["eje_motriz"]
    print("EJE MOTRIZ  Se'", em["Se_prima"], "ciclos en", em["anios"], "años:", em["ciclos_vida"])
    for s in em["secciones"]:
        print(f"  {s['cod']} {s['seccion'][:40]:40s} d{s['d']} M {s['M']:7.1f} Kf {s['Kf']} Kfs {s['Kfs']} Se {s['Se']} "
              f"σa {s['sigma_a']:.1f} τm {s['tau_m']:.1f} nG {s['n_goodman']:.2f} nGe {s['n_gerber']:.2f} ny {s['n_fluencia']:.2f} N {s['N_falla']}")
    print("  atasco", em["atasco"], "verifica", em["verifica"])
    print("REENVIO", json.dumps(r["eje_reenvio"], ensure_ascii=False))
    print("CHAVETA", r["chaveta"])
    print("CADENA", r["cadena"])
    print("RODAMIENTOS", r["rodamientos"]["filas"])
    print("ANCLAJES", json.dumps(r["anclajes"], ensure_ascii=False))
    print("MENSULA", r["mensula"])
    print("WOHLER", r["wohler"]["a"], r["wohler"]["b"], [(x["S"], x["N"]) for x in r["wohler"]["niveles"]])
