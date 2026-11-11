"""Memoria de cálculo (entrega final): TG2 y conductores, iluminación del Sector Este, ventilación de la nave,
biogás, carga de fuego y fatiga de las piezas del secador (fatiga.py).

Cada bloque sigue el método de la memoria: datos (con su fuente), fórmula, reemplazo, resultado,
valor adoptado y verificación. Los resultados se guardan en resultados.json, que leen el plano
P23 (unifilar TG2) y el armado de la memoria (memoria_docx.py), así planos e informe usan los
mismos números.

    python calculos_memoria.py
"""
from __future__ import annotations

import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fatiga import calc_fatiga  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
R3 = math.sqrt(3)

# =====================================================================================
# 1. Datos eléctricos
# =====================================================================================
U, UF = 380.0, 220.0                       # V, red 3 × 380/220 V 50 Hz (plano 05)
RHO20, ALFA = 0.0172, 0.00393              # Ω·mm²/m y 1/°C del cobre
RHO70 = RHO20 * (1 + ALFA * 50)            # conductor en servicio a 70 °C (PVC)
X_CABLE = 0.08e-3                          # Ω/m, reactancia típica de cable multipolar BT
K_PVC = 115                                # A·s^0,5/mm², Cu con aislación de PVC (IEC 60364-4-43)

# Corriente admisible Iz (A), cobre/PVC, 3 conductores cargados (IEC 60364-5-52, base de la
# AEA 90364-7-771). E: multipolar en bandeja perforada a 30 °C; D1: multipolar en caño enterrado a 20 °C.
IZ = {
    "E": {1.5: 18.5, 2.5: 25, 4: 34, 6: 43, 10: 60, 16: 80, 25: 101, 35: 126, 50: 153},
    "D1": {1.5: 18, 2.5: 24, 4: 30, 6: 38, 10: 50, 16: 64, 25: 82, 35: 98, 50: 116},
}
IZ_2C = {"E": {1.5: 22, 2.5: 30, 4: 40, 6: 51}}       # 2 conductores cargados (monofásico)
F_TEMP = {"E": 0.87, "D1": 0.95}           # aire a 40 °C (nave en verano) / suelo a 25 °C
F_AGRUP = {"E": 0.80, "D1": 1.0}           # bandeja compartida por varios circuitos

# Motores de la Rev. D (plano 23 Rev. D) + agregados de esta revisión (E10, plano 24)
# tag, accionamiento, kW, In (A), arranque, tablero, fases
MOTORES = [
    ("M16", "Hidrolavadora de camiones (lavadero P1)", 4.00, 8.2, "directo", "TS-LAV", 3),
    ("M17", "Bomba del arco de desinfección", 1.10, 2.5, "directo", "TS-LAV", 3),
    ("M18", "Zaranda rotativa (trommel)", 1.10, 2.5, "VFD", "TS-ENS", 3),
    ("M19", "Alimentador de la ensacadora 25 kg", 0.75, 1.9, "VFD", "TS-ENS", 3),
    ("M20", "Cosedora de bolsas", 0.37, 0.9, "directo", "TS-ENS", 3),
    ("M21", "Cinta de salida de bolsas", 0.55, 1.4, "directo", "TS-ENS", 3),
    ("M22", "Envasadora vertical de bolsas chicas", 2.20, 4.9, "propio", "TS-ENS", 3),
    ("M23", "Extractor de la campana de recepción", 4.00, 8.2, "VFD", "TG2", 3),
    ("M24", "Transportador flexible a la envasadora", 0.55, 1.4, "directo", "TS-ENS", 3),
    ("M25", "Bomba de incendio", 7.50, 15.4, "directo", "TBI", 3),
    ("M26", "Bomba jockey de incendio", 0.75, 1.9, "directo", "TBI", 3),
    ("M27", "Bomba trituradora de alimentación a digestores", 4.00, 8.2, "directo", "TS-BIO", 3),
    ("M28", "Agitador sumergible biodigestor BD-1", 4.00, 8.2, "directo", "TS-BIO", 3),
    ("M29", "Agitador sumergible biodigestor BD-2", 4.00, 8.2, "directo", "TS-BIO", 3),
    ("M30", "Agitador del tanque de digestato", 4.00, 8.2, "directo", "TS-BIO", 3),
    ("M31", "Bomba de digestato y recirculación", 3.00, 6.2, "directo", "TS-BIO", 3),
    ("M32", "Separador sólido-líquido (tornillo prensa)", 2.20, 4.9, "directo", "TS-BIO", 3),
    ("M33", "Soplante de biogás", 1.10, 2.5, "directo", "TS-BIO (Ex)", 3),
    ("M34", "Bomba de agua caliente (calefacción de digestores)", 0.55, 1.4, "directo", "TS-BIO", 3),
    ("M35", "Actuador de la válvula desviadora del elevador", 0.12, 0.3, "directo", "TS-ENS", 3),
]
# Nuevos (E10, plano 24): extractores Campagnoni AirTEC 1215 de 1,5 HP trifásicos (motor IE3 de
# 1,1 kW, 4 polos: η y cos φ como el M10 del plano 05) y ventiladores móviles de 50" de 1 HP
# (motor monofásico 0,75 kW con capacitor permanente; η y cos φ supuestos: verificar con la placa).
ETA_EX, COS_EX = 0.841, 0.77
ETA_VM, COS_VM = 0.72, 0.92


def i_trif(p_kw, eta, cos):
    return p_kw * 1000 / (R3 * U * eta * cos)


def i_mono(p_kw, eta, cos):
    return p_kw * 1000 / (UF * eta * cos)


I_EX = i_trif(1.1, ETA_EX, COS_EX)
I_VM = i_mono(0.75, ETA_VM, COS_VM)
NUEVOS = [
    ("M36", "Extractor EX-01 Campagnoni AirTEC 1215 (1,5 HP)", 1.10, round(I_EX, 1), "directo", "TS-VEN", 3),
    ("M37", "Extractor EX-02 Campagnoni AirTEC 1215 (1,5 HP)", 1.10, round(I_EX, 1), "directo", "TS-VEN", 3),
    ("M38", "Ventilador móvil VM-1 50\" (1 HP, 220 V, toma 2P+T)", 0.75, round(I_VM, 1), "toma", "TS-VEN", 1),
    ("M39", "Ventilador móvil VM-2 50\" (1 HP, 220 V, toma 2P+T)", 0.75, round(I_VM, 1), "toma", "TS-VEN", 1),
    # Rev. F: enfriador de producto bajo la tolva de retención (900 m³/h a ≈ 1.000 Pa); In como los 0,55 kW de la lista
    ("M40", "Ventilador del enfriador de producto (Rev. F)", 0.55, 1.4, "directo", "TS-ENS", 3),
]
TODOS = MOTORES + NUEVOS
INCENDIO = {"M25", "M26"}

FS_TG2 = 0.55                             # simultaneidad del TG2 (criterio del plano 23 Rev. D)
DEMANDA_TGF = (54, 59)                    # kW, plano 05 (fs 0,8 sobre 66,9 kW)
G1_KW = 25.0                              # cogeneración a biogás
P_CONTRATAR_ANTERIOR = 100                # kW, plano 23 Rev. D

# Circuitos de salida del TG2: (Q, destino, cargas, sección mm², largo m, método)
# Largos medidos sobre el recorrido real de bandejas y zanjas (layout del visor, ver RECORRIDOS):
# Q22 y Q25 dejan de ser "medidos sobre el plano 13" (dato supuesto de la Rev. D) y salen de RECORRIDOS.
# Q25 (TL2) y Q26 (CI) tienen potencia del cálculo luminotécnico y de la central (calc_iluminacion).
# Posiciones (m, origen vértice SO de la nave): TG2 en la sala de control (24,8; 0,45); TS-LAV sobre el muro
# Oeste junto al portón P1 (-0,4; 17,5); TL2 dentro del depósito de expedición (61,0; 1,0).
RECORRIDOS = {
    "Q22": [("TG2 → bandeja (subida)", 2.6), ("bandeja muro Sur, x 24,8 → 0,3", 24.5),
            ("bandeja muro Oeste, y 0,45 → 17,5", 17.1), ("bajada y paso de muro a TS-LAV", 3.2), ("reserva 5 %", 2.4)],
    "Q25": [("TG2 → salida de la nave por la sala de control", 3.0), ("zanja junto al playón P2, x 26 → 60", 34.0),
            ("subidas y bajadas en cámaras", 3.0), ("dentro del depósito hasta TL2", 2.5), ("reserva 5 %", 2.1)],
}
CIRCUITOS = [
    ("Q21", "TS-ENS zaranda, envasado y enfriador", ["M18", "M19", "M20", "M21", "M22", "M24", "M35", "M40"], 4, 25, "E"),
    ("Q22", "TS-LAV limpieza de vehículos", ["M16", "M17"], 4, None, "E"),
    ("Q23", "TS-BIO biogás + G1 25 kWe", ["M27", "M28", "M29", "M30", "M31", "M32", "M33", "M34"], 16, 105, "D1"),
    ("Q24", "VFD M23 extractor de recepción", ["M23"], 2.5, 30, "E"),
    ("Q25", "TL2 iluminación del Sector Este", ["ILUM"], 4, None, "D1"),
    ("Q26", "CI central de incendio", ["CI"], 2.5, 5, "E"),
    ("Q27", "TS-VEN ventilación de la nave (E10)", ["M36", "M37", "M38", "M39"], 2.5, 28, "E"),
]
IN_NORMAL = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125]
# Acometida pilar → TG2: pasa de 4 × 25 a 4 × 35 mm² (cierra la incoherencia 4 y la decisión pendiente 4:
# el fusible NH00 de 80 A y el QG2 de 80 A quedan por debajo de Iz; el QG2 se regula en Ir = 63 A para
# selectividad con el fusible).
ACOMETIDA_TG2 = {"seccion": 35, "largo": 40, "metodo": "D1", "In_QG2": 80, "Ir_QG2": 63, "fusible": 80}
ICC_PILAR_KA = 6.0                        # Icc presunta en el pilar (plano 05)
TIEMPO_DISPARO = 0.1                      # s, disparo magnético
LIM_DU = {"iluminacion": 3.0, "fuerza": 5.0}   # % de caída admisible desde el origen (AEA 90364-7-771)


def iz(seccion, metodo, fases=3):
    base = (IZ if fases == 3 else IZ_2C)[metodo][seccion]
    return base * F_TEMP[metodo] * F_AGRUP[metodo]


def caida(i, largo, seccion, cos=0.85, fases=3):
    r = RHO70 / seccion
    sen = math.sqrt(1 - cos ** 2)
    k = R3 if fases == 3 else 2
    du = k * i * largo * (r * cos + X_CABLE * sen)
    return du, 100 * du / (U if fases == 3 else UF)


def norm_sup(x):
    return next(v for v in IN_NORMAL if v >= x)


def calc_tg2(ilum):
    motores = {m[0]: m for m in TODOS}
    # cargas que no son motores: iluminación del Sector Este (trifásica repartida) y central de incendio
    i_ilum = ilum["P_Q25_kW"] * 1000 / (R3 * U * 0.95)
    i_ci = ilum["P_Q26_kW"] * 1000 / (UF * 0.9)
    motores["ILUM"] = ("ILUM", "Iluminación Sector Este (TL2)", ilum["P_Q25_kW"], round(i_ilum, 1), "—", "TL2", 3)
    motores["CI"] = ("CI", "Central de incendio y sirenas", ilum["P_Q26_kW"], round(i_ci, 1), "—", "CI", 1)
    filas, circ = [], []
    for q, dest, cargas, s, largo, met in CIRCUITOS:
        if largo is None:
            largo = round(sum(t for _, t in RECORRIDOS[q]))
        fases = 1 if cargas == ["CI"] else 3
        kw = sum(motores[c][2] for c in cargas)
        # corriente por fase: trifásicos suman directo; los monofásicos van repartidos en L1 y L2
        i3 = sum(motores[c][3] for c in cargas if motores[c][6] == 3)
        i1 = max([motores[c][3] for c in cargas if motores[c][6] == 1] or [0])
        ib = i3 + i1
        nota = ""
        if q == "Q23":
            # TS-BIO: con fs 0,7 los agitadores y bombas no arrancan todos juntos; cuando G1 genera
            # su corriente vuelve por el mismo cable: se toma el mayor de los dos casos.
            ib_carga = ib * 0.7
            ib_gen = G1_KW * 1000 / (R3 * U * 0.95)
            ib = max(ib_carga, ib_gen)
            nota = f"mayor entre carga (fs 0,7: {ib_carga:.1f} A) y G1 a plena potencia ({ib_gen:.1f} A)"
        in_ = norm_sup(ib * 1.15)  # margen: In ≥ 1,15·Ib
        cos = 0.95 if cargas in (["ILUM"], ["CI"]) else 0.85
        s_proy = s
        while True:   # Ib ≤ In ≤ Iz (AEA 90364-7-771); si no verifica, se sube a la sección comercial siguiente
            izz = iz(s, met, fases=2 if fases == 1 else 3)
            verif = ib <= in_ <= izz
            mayores = [x for x in (IZ if fases == 3 else IZ_2C)[met] if x > s]
            if verif or not mayores:
                break
            s = min(mayores)
        du, du_pct = caida(ib, largo, s, cos=cos, fases=fases)
        if s != s_proy:
            nota += f" · sección aumentada de {s_proy} a {s} mm² para que In ≤ Iz"
        circ.append({"Q": q, "destino": dest, "cargas": cargas, "kW": round(kw, 2), "Ib": round(ib, 1),
                     "In": in_, "S": s, "L": largo, "metodo": met, "Iz": round(izz, 1), "fases": fases,
                     "dU_V": round(du, 2), "dU_pct": round(du_pct, 2), "verifica": verif, "nota": nota.strip()})
    for m in TODOS:
        filas.append({"tag": m[0], "nom": m[1], "kW": m[2], "In": m[3], "arranque": m[4], "tablero": m[5], "fases": m[6]})
    total_anterior = sum(m[2] for m in MOTORES)
    total = sum(m[2] for m in TODOS)
    sin_inc = sum(m[2] for m in TODOS if m[0] not in INCENDIO)
    sin_inc_ant = sum(m[2] for m in MOTORES if m[0] not in INCENDIO)
    p_ilum = ilum["P_Q25_kW"] + ilum["P_Q26_kW"]          # iluminación y central: simultaneidad 1
    demanda = FS_TG2 * sin_inc + p_ilum
    i_dem = demanda * 1000 / (R3 * U * 0.85)
    i_inst = (sin_inc + p_ilum) * 1000 / (R3 * U * 0.85)
    # acometida del TG2
    ac = ACOMETIDA_TG2
    iz_ac = iz(ac["seccion"], ac["metodo"])
    du_ac, du_ac_pct = caida(i_dem, ac["largo"], ac["seccion"])
    for c in circ:   # caída total desde el pilar: acometida + circuito (AEA 90364-7-771: 3 % iluminación, 5 % fuerza)
        c["dU_total_pct"] = round(du_ac_pct + c["dU_pct"], 2)
        c["lim_dU_pct"] = LIM_DU["iluminacion" if c["cargas"] == ["ILUM"] else "fuerza"]
        c["verifica"] = c["verifica"] and c["dU_total_pct"] <= c["lim_dU_pct"]
    # cortocircuito en barras del TG2 (máximo, conductor a 20 °C)
    z_red = U / (R3 * ICC_PILAR_KA * 1000)
    r_red, x_red = z_red * 0.3, z_red * 0.95
    r_ac = RHO20 * ac["largo"] / ac["seccion"]
    x_ac = X_CABLE * ac["largo"]
    z_tg2 = math.hypot(r_red + r_ac, x_red + x_ac)
    icc_tg2 = U / (R3 * z_tg2) / 1000
    s_min_cc = icc_tg2 * 1000 * math.sqrt(TIEMPO_DISPARO) / K_PVC
    # balance de potencia
    tgf_max = DEMANDA_TGF[1]
    p_sin_g1 = tgf_max + demanda + 7.5
    p_con_g1 = p_sin_g1 - G1_KW
    p_adopt = P_CONTRATAR_ANTERIOR
    return {
        "motores": filas, "circuitos": circ,
        "total_anterior_kW": round(total_anterior, 2), "total_kW": round(total, 2),
        "agregado_kW": round(total - total_anterior, 2),
        "base_fs_anterior_kW": round(sin_inc_ant, 2), "base_fs_kW": round(sin_inc, 2),
        "fs": FS_TG2, "demanda_tg2_kW": round(demanda, 1), "demanda_tg2_anterior_kW": round(FS_TG2 * sin_inc_ant, 1),
        "I_demanda_A": round(i_dem, 1), "I_instalada_A": round(i_inst, 1),
        "acometida": {"S": ac["seccion"], "L": ac["largo"], "Iz": round(iz_ac, 1), "In": ac["In_QG2"], "Ir": ac["Ir_QG2"],
                      "fusible": ac["fusible"],
                      "verifica": (i_dem <= ac["Ir_QG2"] <= iz_ac and ac["fusible"] <= iz_ac and ac["In_QG2"] <= iz_ac
                                   and 1.6 * ac["fusible"] <= 1.45 * iz_ac),   # I2 del fusible gG ≤ 1,45·Iz
                      "I2_fusible": round(1.6 * ac["fusible"], 1), "lim_I2": round(1.45 * iz_ac, 1),
                      "dU_pct": round(du_ac_pct, 2), "In_recomendada": max(v for v in IN_NORMAL if v <= iz_ac)},
        "P_ilum_kW": round(p_ilum, 2), "recorridos": {q: [(a, b) for a, b in v] for q, v in RECORRIDOS.items()},
        "Icc_TG2_kA": round(icc_tg2, 2), "S_min_cc_mm2": round(s_min_cc, 1),
        "balance": {"TGF_kW": f"{DEMANDA_TGF[0]} - {DEMANDA_TGF[1]}", "TG2_kW": round(demanda, 1),
                    "incendio_kW": 7.5, "G1_kW": -G1_KW, "sin_G1_kW": round(p_sin_g1, 1),
                    "con_G1_kW": round(p_con_g1, 1), "adoptada_kW": p_adopt,
                    "margen_sin_G1_pct": round(100 * (p_adopt - p_sin_g1) / p_adopt, 1)},
        "I_EX": round(I_EX, 2), "I_VM": round(I_VM, 2),
    }



# =====================================================================================
# 1 bis. Iluminación del Sector Este (Q25 → TL2) y central de incendio (Q26)
# =====================================================================================
def calc_iluminacion():
    """Método de los lúmenes (IRAM-AADL J 20-06) para el depósito de expedición E7 y potencia de las
    farolas, proyectores Ex de la zona de biogás y luces de emergencia del Sector Este."""
    a, b = 20.0, 12.0                         # m, depósito E7
    h_lum, h_trab = 5.6, 0.85                 # m, montaje de las campanas y plano de trabajo
    h = h_lum - h_trab
    k = a * b / (h * (a + b))                 # índice del local
    E = 200.0                                 # lx: depósito con movimiento de pallets (IRAM-AADL J 20-06)
    cu, fm = 0.62, 0.70                       # CU (reflectancias 0,5/0,3/0,2; k ≈ 1,6) y mantenimiento (polvo)
    phi_lum, p_lum = 19500.0, 150.0           # campana LED industrial 150 W, 130 lm/W
    phi_t = E * a * b / (cu * fm)
    n_calc = phi_t / phi_lum
    n = 6                                     # 2 filas de 3: separación 6,7 × 6 m ≤ 1,5·h = 7,1 m
    e_real = n * phi_lum * cu * fm / (a * b)
    cargas = [("Depósito E7: campanas LED 150 W", n, p_lum),
              ("Farolas del Sector Este (calles R6, R7, R8): LED 100 W", 5, 100.0),
              ("Zona de biogás: proyectores LED Ex 60 W", 4, 60.0),
              ("Dársena y portón del depósito: reflectores LED 100 W", 2, 100.0),
              ("Luces de emergencia autónomas (carga de baterías)", 8, 6.0)]
    p_q25 = sum(c * w for _, c, w in cargas) / 1000
    p_q26 = 0.15                              # kW: central de incendio 24 V con cargador y sirenas
    return {"a": a, "b": b, "h": round(h, 2), "k": round(k, 2), "E": E, "CU": cu, "fm": fm, "phi_lum": phi_lum,
            "p_lum": p_lum, "phi_t": round(phi_t), "n_calc": round(n_calc, 2), "n": n, "E_real": round(e_real),
            "sep_max": round(1.5 * h, 1), "cargas": [(t, c, w) for t, c, w in cargas],
            "P_Q25_kW": round(p_q25, 2), "P_Q26_kW": p_q26}

# =====================================================================================
# 2. Ventilación general de la nave (E10, plano 24)
# =====================================================================================
def calc_ventilacion():
    L, A, H_alero, flecha = 33.0, 18.0, 7.0, 1.35          # m (planos 01 y 08)
    v_nave = L * A * H_alero
    v_techo = 0.5 * A * flecha * L
    V = v_nave + v_techo
    n_inv, n_ver = 6, 12                                    # renovaciones por hora
    # balance térmico de verano (plano 24): kW
    cargas = {"Paredes del secador (lana de roca 80 mm)": 6.1, "Ductos calientes dentro de la nave": 3.0,
              "Motores M5 a M11 (20 % de 6,35 kW)": 1.3, "Producto que se enfría (329 kg/h, 60 → 35 °C)": 3.4,
              "Personas (7) e iluminación (18 LED)": 3.8, "Sol sobre la cubierta (594 m² × 25 W/m²)": 14.9}
    # comprobación del producto: m·cp·ΔT con cp del guano seco ≈ 1,5 kJ/kg·K
    q_prod = 329 / 3600 * 1.5 * (60 - 35)
    H = sum(cargas.values())
    rho, cp, dT = 1.15, 1.005, 3.0                          # aire a 35 °C, kJ/kg·K, salto admitido
    q_term = H / (rho * cp * dT) * 3600                     # m³/h
    q_ren = V * n_ver
    q_dis = max(q_ren, q_term)
    q_ex_cat = 54700                                        # m³/h por extractor (Campagnoni AirTEC 1215, con persianas)
    p_max = 24.0                                            # Pa, depresión máxima de catálogo
    n_ex = math.ceil(q_dis / q_ex_cat)
    # punto de funcionamiento: curva del ventilador p = p_max·(1 − (Q/Q0)²) contra la resistencia de las
    # tomas de aire (K = 2,5 rejas + persianas fijas) y de la nave (1 Pa); se itera porque v depende de Q
    a_tomas_dis, k_toma, rho_a = 15.0, 2.5, 1.15
    q1 = q_ex_cat
    for _ in range(60):
        v = n_ex * q1 / 3600 / a_tomas_dis
        dp = k_toma * 0.5 * rho_a * v ** 2 + 1.0
        q1 = 0.5 * q1 + 0.5 * q_ex_cat * math.sqrt(max(0.0, 1 - dp / p_max))
    frac_calc = q1 / q_ex_cat
    frac = min(0.85, frac_calc)                             # se mantiene 85 % del lado de la seguridad
    q_real = n_ex * q_ex_cat * frac
    v_toma = 2.0                                            # m/s en las aberturas de entrada
    a_tomas = q_real / 3600 / v_toma
    # biofiltro de la recepción (E3)
    q_bio, a_bio, h_lecho = 6000, 8.5 * 4.5, 1.2
    carga_bio = q_bio / a_bio
    t_contacto = h_lecho / (carga_bio / 3600)
    return {"V_nave": round(v_nave), "V_techo": round(v_techo), "V": round(V), "n_inv": n_inv, "n_ver": n_ver,
            "Q_inv": round(V * n_inv), "Q_ver": round(q_ren), "cargas": cargas, "H_kW": round(H, 1),
            "q_prod_kW": round(q_prod, 1), "Q_termico": round(q_term), "Q_diseno": round(q_dis),
            "Q_ex": q_ex_cat, "n_ex": n_ex, "Q_real": round(q_real), "ren_real": round(q_real / V, 1),
            "Q_un_extractor": round(q_ex_cat * 0.85), "ren_un_extractor": round(q_ex_cat * 0.85 / V, 1),
            "A_tomas": round(a_tomas, 1), "P_ex_kW": 2 * 1.1, "p_max": p_max,
            "punto": {"frac_calc": round(frac_calc, 3), "dp_Pa": round(dp, 1), "v_toma": round(v, 2),
                      "frac_adoptada": frac},
            "biofiltro": {"Q": q_bio, "A": round(a_bio, 1), "h": h_lecho, "carga": round(carga_bio),
                          "t_contacto": round(t_contacto, 1)}}


# =====================================================================================
# 3. Biogás (E8, plano 20)
# =====================================================================================
def calc_biogas():
    guano_anio = 920.0                       # t/año que la secadora no procesa (fines de semana y feriados)
    guano = guano_anio / 365                 # t/día promedio
    st = 1 - 0.72                            # sólidos totales: humedad 72 % (plano 06)
    sv_st = 0.746                            # sólidos volátiles / ST (guano de ponedoras)
    m_st = guano * 1000 * st                 # kg ST/día
    m_sv = m_st * sv_st
    st_obj = 0.08                            # alimentación al 8 % de ST
    q_alim = m_st / st_obj / 1000            # m³/día (densidad ≈ 1 t/m³)
    # el plano 20 adopta 9,40 m³/día: suma ≈ 0,6 m³/día de lixiviados y agua de lavado que entran
    # con sus propios sólidos; se toma ese valor para el volumen
    q_adop = 9.40
    trh = 30
    v_util = q_adop * trh
    n_dig, d_dig = 2, 6.5
    a_dig = math.pi / 4 * d_dig ** 2
    h_util = v_util / n_dig / a_dig
    carga = m_sv / v_util
    y_biogas = 0.35                          # m³ biogás / kg SV (guano de gallina, mesofílico)
    biogas = m_sv * y_biogas
    ch4, pci = 0.58, 20.8                    # fracción de metano y PCI del biogás (MJ/m³)
    e_dia = biogas * pci
    piloto = 12.1                            # m³/día al quemador piloto del hogar
    e_chp = (biogas - piloto) * pci / 3.6    # kWh/día de combustible al CHP
    eta_el, eta_th, p_chp = 0.32, 0.48, 25.0
    e_el = e_chp * eta_el
    horas = e_el / p_chp
    calor = e_chp * eta_th
    # calor que piden los digestores: calentar la alimentación + pérdidas por la envolvente
    cp_agua = 4.18
    # coeficientes U por capas (ISO 6946): resistencias en m²K/W
    capas_pared = [("Rsi (digestato → pared)", 0.13), ("acero vitrificado 5 mm (λ 50)", 0.005 / 50),
                   ("lana mineral 80 mm (λ 0,040)", 0.080 / 0.040), ("chapa trapezoidal de protección", 0.0),
                   ("Rse (exterior, viento)", 0.04)]
    capas_techo = [("Rsi ascendente (superficie del digestato → biogás)", 0.10),
                   ("capa de biogás no ventilada (domo, flujo ascendente)", 0.16),
                   ("Rsi ascendente (biogás → membrana interior)", 0.10),
                   ("membranas de PVC-poliéster 2 × 1,2 mm (λ 0,16)", 2 * 0.0012 / 0.16),
                   ("cámara de aire inflada por el soplante (ventilada: se toma Rsi)", 0.10)]
    capas_piso = [("Rsi", 0.17), ("losa de H°A° 300 mm (λ 1,6)", 0.30 / 1.6), ("XPS 50 mm bajo losa (λ 0,035)", 0.05 / 0.035)]
    u_paredes = 1 / sum(r for _, r in capas_pared)
    u_techo = 1 / sum(r for _, r in capas_techo)
    u_piso = 1 / sum(r for _, r in capas_piso)
    # la alimentación es una mezcla: guano y líquidos fríos + 4,6 m³/día de líquido recirculado del T3 a ≈ 30 °C
    recirc_v, t_recirc = 4.6, 30.0
    def calor_dig(t_frio, t_ext, t_suelo):
        t_alim = (recirc_v * t_recirc + (q_adop - recirc_v) * t_frio) / q_adop
        q_alim_kwh = q_adop * 1000 * cp_agua * (38 - t_alim) / 3600
        a_par = n_dig * math.pi * d_dig * 5.0
        a_tec = n_dig * a_dig * 1.25          # casquete del domo ≈ 1,25 × área del círculo
        a_piso = n_dig * a_dig
        perd = ((u_paredes * a_par + u_techo * a_tec) * (38 - t_ext) + u_piso * a_piso * (38 - t_suelo)) * 24 / 1000
        return round(t_alim, 1), q_alim_kwh, perd, q_alim_kwh + perd
    med = calor_dig(17, 18, 18)
    inv = calor_dig(10, 8, 12)
    almacen = 2 * 37 + 31                    # m³: 2 domos + techo del tanque T3
    h_almacen = almacen / biogas * 24
    gas_masa = biogas * 1.15 / 1000          # t/día que salen como gas
    solido = 1.8                             # t/día del separador (plano 20)
    recirc = 4.6                             # m³/día que vuelven a la mezcla
    liquido = q_adop - gas_masa - solido - recirc
    v_t3 = math.pi / 4 * 8.0 ** 2 * 4.0
    dias_t3 = v_t3 / liquido
    return {"guano_t_dia": round(guano, 2), "ST_kg": round(m_st), "SV_kg": round(m_sv), "Q_alim_calc": round(q_alim, 2),
            "Q_alim": q_adop, "TRH": trh, "V_util": round(v_util), "h_util": round(h_util, 2), "A_dig": round(a_dig, 1),
            "V_dig_c_u": round(v_util / 2), "carga": round(carga, 2), "biogas": round(biogas), "CH4": ch4,
            "PCI": pci, "E_MJ": round(e_dia), "piloto": piloto, "E_chp_kWh": round(e_chp), "E_el": round(e_el),
            "horas": round(horas, 1), "calor": round(calor), "calor_med": [round(x) for x in med],
            "calor_inv": [round(x) for x in inv], "almacen": almacen, "h_almacen": round(h_almacen, 1),
            "U": {"paredes": round(u_paredes, 2), "techo": round(u_techo, 2), "piso": round(u_piso, 2)},
            "capas": {"paredes": capas_pared, "techo": capas_techo, "piso": capas_piso},
            "balance_calor": {"med": round(calor - med[3]), "inv": round(calor - inv[3])},
            "liquido": round(liquido, 2), "V_T3": round(v_t3), "dias_T3": round(dias_t3),
            "solido": solido, "recirc": recirc}


# =====================================================================================
# 4. Carga de fuego (Dec. 351/79, Anexo VII; plano 16)
# =====================================================================================
PCI_MADERA = 18.41  # MJ/kg (Anexo VII, 1.2)
S1 = [  # material, kg, PCI MJ/kg
    ("Guano seco en pila de acopio (21,7 m³ × 500 kg/m³)", 10840, 10.5),
    ("Guano en proceso dentro del secador (equivalente seco)", 600, 10.5),
    ("Guano húmedo en playa de recepción (8 m³ × 800 kg/m³)", 6400, 2.0),
    ("Producto embolsado en zona 28 (104 bolsas × 25 kg)", 2600, 10.5),
    ("Bolsas vacías de PE (stock de línea)", 102, 46.0),
    ("Rechazo de zaranda (plumas y cáscara de huevo)", 300, 8.0),
    ("Pallets de madera (10 u × 22 kg)", 220, 18.4),
    ("Bandas y recubrimientos de goma", 180, 32.0),
    ("Guías UHMW-PE del secador (15 × 12 m)", 135, 46.0),
    ("Aislación de cables (PVC/XLPE)", 250, 20.0),
    ("Aceites y grasas en taller y depósito (200 l)", 176, 43.0),
    ("Gasoil en tanque de la pala cargadora (150 l)", 126, 43.0),
    ("Mobiliario, papeles y ropa (oficina, vestuario, sala de control)", 800, 18.4),
    ("Repuestos embalados (cartón y plásticos)", 150, 17.0),
]
SECTORES = [  # sector, superficie m², energía MJ (plano 16), riesgo
    ("S1 Nave de proceso", 594, None, "R3"),
    ("S2 Anexo del generador", 52, 2274, "R3"),
    ("S3 Silo de cáscara (al aire libre)", 72, 103950, "R3"),
    ("S4 Depósito de expedición (nuevo)", 240, 173991, "R3"),
    ("S5 Zona de biogás (al aire libre)", 864, 10451, "R2"),
]


def _rango(q):
    for lim, txt in ((15, "hasta 15"), (30, "16 a 30"), (60, "31 a 60"), (100, "61 a 100")):
        if q <= lim:
            return txt
    return "más de 100"


RES_FUEGO = {"R2": {"hasta 15": "F 60", "16 a 30": "F 90", "31 a 60": "F 120", "61 a 100": "F 180", "más de 100": "F 180"},
             "R3": {"hasta 15": "F 30", "16 a 30": "F 60", "31 a 60": "F 90", "61 a 100": "F 120", "más de 100": "F 180"}}
POT_A = {"R3": {"hasta 15": "1 A", "16 a 30": "2 A", "31 a 60": "3 A", "61 a 100": "6 A"}}
POT_B = {"R2": {"hasta 15": "6 B", "16 a 30": "8 B", "31 a 60": "10 B", "61 a 100": "20 B"},
         "R3": {"hasta 15": "4 B", "16 a 30": "6 B", "31 a 60": "8 B", "61 a 100": "10 B"}}


def calc_fuego():
    filas = [(m, kg, pci, kg * pci) for m, kg, pci in S1]
    e_s1 = sum(f[3] for f in filas)
    sectores = []
    for nom, sup, e, riesgo in SECTORES:
        e = e_s1 if e is None else e
        q = e / PCI_MADERA / sup
        r = _rango(q)
        sectores.append({"sector": nom, "sup": sup, "E": round(e), "q": round(q, 1), "rango": r, "riesgo": riesgo,
                         "F": RES_FUEGO[riesgo][r], "A": POT_A.get(riesgo, {}).get(r, "—"),
                         "B": POT_B[riesgo].get(r, "a det.")})
    # servicio de agua: bomba M25 24 m³/h a 45 m c.a.
    q_b, h_b, eta_b = 24 / 3600, 45, 0.60
    p_eje = 1000 * 9.81 * q_b * h_b / eta_b / 1000
    reserva = max(10.0, 10 / 1000 * 901)
    hidrantes = 2 * 200 * 30 / 1000
    return {"S1": [{"material": m, "kg": kg, "PCI": pci, "MJ": round(e)} for m, kg, pci, e in filas],
            "E_S1": round(e_s1), "madera_S1": round(e_s1 / PCI_MADERA), "sectores": sectores,
            "bomba_kW_eje": round(p_eje, 1), "reserva_m3": reserva, "hidrantes_m3": hidrantes, "tanque_m3": 20}


def main():
    ilum = calc_iluminacion()
    res = {"tg2": calc_tg2(ilum), "iluminacion": ilum, "ventilacion": calc_ventilacion(), "biogas": calc_biogas(),
           "fuego": calc_fuego(), "fatiga": calc_fatiga()}
    with open(os.path.join(AQUI, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    tg = res["tg2"]
    print(f"TG2: total {tg['total_anterior_kW']} -> {tg['total_kW']} kW (+{tg['agregado_kW']}); base fs "
          f"{tg['base_fs_anterior_kW']} -> {tg['base_fs_kW']} kW; demanda {tg['demanda_tg2_anterior_kW']} -> "
          f"{tg['demanda_tg2_kW']} kW; I dem {tg['I_demanda_A']} A, inst {tg['I_instalada_A']} A")
    for c in tg["circuitos"]:
        print(f"  {c['Q']} {c['destino'][:28]:28s} {c['kW']:6.2f} kW Ib {c['Ib']:5.1f} In {c['In']:3d} "
              f"Iz {c['Iz']:5.1f} {c['S']} mm² {c['L']} m dU {c['dU_pct']} % {'OK' if c['verifica'] else 'NO'} {c['nota']}")
    print("  acometida:", tg["acometida"], "Icc TG2", tg["Icc_TG2_kA"], "kA; Smin cc", tg["S_min_cc_mm2"])
    print("  balance:", tg["balance"], "I_EX", tg["I_EX"], "I_VM", tg["I_VM"])
    v = res["ventilacion"]
    print(f"Ventilación: V {v['V']} m³; Q ver {v['Q_ver']}; térmico {v['Q_termico']}; {v['n_ex']} ex -> real "
          f"{v['Q_real']} ({v['ren_real']} R/h); tomas {v['A_tomas']} m²; biofiltro {v['biofiltro']}")
    b = res["biogas"]
    print("Biogás:", {k: b[k] for k in ("guano_t_dia", "ST_kg", "SV_kg", "Q_alim_calc", "V_util", "h_util", "carga",
                                         "biogas", "E_MJ", "E_el", "horas", "calor", "calor_med", "calor_inv",
                                         "h_almacen", "liquido", "dias_T3")})
    fu = res["fuego"]
    print("Fuego: E_S1", fu["E_S1"], [(s["sector"][:3], s["q"], s["F"], s["A"], s["B"]) for s in fu["sectores"]],
          "bomba", fu["bomba_kW_eje"])


if __name__ == "__main__":
    main()

