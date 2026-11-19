"""Cálculos de la granja integrada: balance de guano y huevos, ventilación de los galpones, transportadores de
guano (capacidad y potencia), tolva pulmón y corrientes de los motores nuevos.

Todos los resultados van a `datos/calculos.json` y de ahí a los planos, el 3D y la memoria. Cada valor lleva su
tipo (R, S, V, P, H) como en docs/01_auditoria.md. Los resultados de potencia son **preliminares (P)**: alcanzan para
dimensionar la instalación eléctrica, pero se confirman con el fabricante de cada transportador.

Fórmulas:
- Guano: m = N · g, con g = 0,133 kg por gallina y día (R: 8 t/día para 60.000 aves del proyecto).
- Balance de masa del secado: m_s = m_in · (1 − X_in); m_out = m_s / (1 − X_out) (R).
- Capacidad de una cinta plana con sobrecarga (DIN 22101 simplificada): A = b² · tg(θ) / 6, b = 0,9 · B − 0,05;
  Q_v = A · v · k_incl · 3.600.
- Potencia (DIN 22101, método del coeficiente C): F_H = C · f · L · g · [q_RO + q_RU + (2 · q_B + q_G) · cos δ];
  F_St = q_G · H · g; P = (F_H + F_St + F_S) · v / η.
- Corriente de un motor trifásico: I = P / (√3 · U · η · cos φ).

    python calculos_granja.py       # -> ../datos/calculos.json
"""
from __future__ import annotations

import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
SALIDA = RAIZ / "datos" / "calculos.json"
g = 9.81

# ---------------------------------------------------------------------------------------- datos de entrada
ENT = {
    "guano_kg_ave_dia": (0.133, "R", "8 t/día de guano fresco para 60.000 aves (proyecto de la secadora)"),
    "X_in": (0.72, "R", "humedad del guano fresco"),
    "X_out": (0.15, "R", "humedad del producto"),
    "m_secador_kg_h": (1000.0, "R", "alimentación de diseño del SC-4"),
    "m_secador_max_kg_h": (1440.0, "R", "máximo con aire a 135 °C (Rev. F)"),
    "T_aire_diseno": (100.0, "R", "aire de secado a la alimentación de diseño (lámina SC-01)"),
    "T_aire_max": (135.0, "R", "aire de secado a 1.440 kg/h (Rev. F)"),
    "horas_secador": (16.0, "P", "dos turnos de 8 h"),
    "disponibilidad": (0.95, "P", "paradas de limpieza y mantenimiento"),
    "postura": (0.90, "S", "San Jorge: 64.800 huevos por día con 72.000 gallinas (2 galpones de 36.000)"),
    "huevos_cajon": (360, "S", "12 maples de 30 huevos"),
    "cajones_palet": (25, "S", "palet de 25 cajones"),
    "rho_guano": (950.0, "H", "densidad aparente del guano fresco, kg/m³ (a medir)"),
    "vent_m3h_ave": (9.5, "V", "ventilación de túnel en verano, 9 a 10 m³/h por gallina"),
    "vent_min_m3h_ave": (1.0, "V", "ventilación mínima, más de 1 m³/h por gallina"),
    "ventilador_50_m3h": (36000.0, "P", "ventilador de túnel de 50\" a 25 Pa (valor típico de catálogo)"),
    "ventilador_36_m3h": (17000.0, "P", "ventilador de 36\" para la ventilación mínima (valor típico)"),
    "v_panel_m_s": (1.8, "P", "velocidad frontal en el panel evaporativo de 150 mm"),
    "U": (380.0, "R", "tensión de línea"),
}
E = {k: v[0] for k, v in ENT.items()}

# IE3 4 polos 50 Hz: rendimiento mínimo (IEC 60034-30-1, V) y cos φ típico (P)
MOTORES_STD = [(0.37, 0.770, 0.70), (0.55, 0.808, 0.72), (0.75, 0.825, 0.75), (1.1, 0.841, 0.77), (1.5, 0.853, 0.79),
               (2.2, 0.867, 0.81), (3.0, 0.877, 0.81), (4.0, 0.886, 0.82), (5.5, 0.896, 0.83), (7.5, 0.904, 0.84),
               (11.0, 0.914, 0.84), (15.0, 0.921, 0.84)]


def motor_std(p_req, margen=1.15):
    for kw, eta, cosf in MOTORES_STD:
        if kw >= p_req * margen:
            return kw, eta, cosf
    return MOTORES_STD[-1]


def corriente(kw, eta, cosf):
    return kw * 1000 / (math.sqrt(3) * E["U"] * eta * cosf)


# ---------------------------------------------------------------------------------------- balance
def balance():
    j = D["jaulas"]
    aves_g = j["aves_por_galpon"]
    aves = aves_g * len(D["galpones"])
    guano_g = aves_g * E["guano_kg_ave_dia"]
    guano = guano_g * len(D["galpones"])
    por_cinta = guano_g / (j["filas"] * j["pisos"])
    kg_m = por_cinta / j["largo_fila"]
    v = j["cinta_guano_v_m_min"] / 60
    flujo_cinta = kg_m * v * 3600 / 1000                    # t/h de una cinta de jaula
    flujo_piso = flujo_cinta * j["filas"]                   # las 4 filas de un mismo piso a la vez
    t_piso_min = (j["largo_fila"] + 3.0) / j["cinta_guano_v_m_min"]
    seco = guano * (1 - E["X_in"]) / (1 - E["X_out"])
    h_secador = guano / E["m_secador_kg_h"]
    m_reg = guano / (E["horas_secador"] * E["disponibilidad"])
    T_aire = E["T_aire_diseno"] + (m_reg - E["m_secador_kg_h"]) / (E["m_secador_max_kg_h"] - E["m_secador_kg_h"]) * (
        E["T_aire_max"] - E["T_aire_diseno"])
    tp = D["tolva_pulmon"]
    dias_tolva = tp["volumen_util_m3"] * E["rho_guano"] / guano
    huevos = aves * E["postura"]
    cajones = huevos / E["huevos_cajon"]
    return {
        "aves_por_galpon": aves_g, "aves_total": aves,
        "densidad_cm2_ave": round(j["celda_ancho"] * j["celda_prof"] * 1e4 / j["aves_por_celda"], 0),
        "guano_galpon_kg_dia": round(guano_g, 0), "guano_total_kg_dia": round(guano, 0),
        "guano_por_cinta_kg": round(por_cinta, 1), "guano_kg_por_m_de_cinta": round(kg_m, 2),
        "flujo_cinta_jaula_t_h": round(flujo_cinta, 2), "flujo_por_piso_t_h": round(flujo_piso, 2),
        "tiempo_por_piso_min": round(t_piso_min, 1), 
        "flujo_lado_simultaneo_t_h": round(2 * flujo_piso, 2),
        "tiempo_por_galpon_min": round(j["pisos"] * (t_piso_min + 1.0), 0),
        "producto_seco_kg_dia": round(seco, 0), "agua_evaporada_kg_dia": round(guano - seco, 0),
        "horas_secador_dia": round(h_secador, 2),
        "horas_secador_dia_max": round(guano / E["m_secador_max_kg_h"], 2),
        "secador_kg_h_regimen": round(m_reg, 0), "secador_turnos": round(E["horas_secador"] / 8),
        "T_aire_regimen_C": round(T_aire, 0),
        "reserva_secador_pct": round((1 - m_reg / E["m_secador_max_kg_h"]) * 100, 1),
        "tolva_pulmon_m3": tp["volumen_util_m3"], "tolva_pulmon_dias": round(dias_tolva, 2),
        "huevos_dia": round(huevos, 0), "cajones_dia": round(cajones, 1),
        "palets_dia": round(cajones / E["cajones_palet"], 2),
        "palets_dia_por_deposito": round(cajones / E["cajones_palet"] / 2, 2),
        "alimento_t_dia_galpon": round(aves_g * 0.110 / 1000, 2),
    }


# ---------------------------------------------------------------------------------------- ventilación
def ventilacion():
    j, gp = D["jaulas"], D["galpon"]
    aves = j["aves_por_galpon"]
    q = aves * E["vent_m3h_ave"]
    n50 = math.ceil(q / E["ventilador_50_m3h"])
    q_inst = n50 * E["ventilador_50_m3h"]
    ancho_int = gp["A"] - 2 * gp["e_muro"]
    h_media = gp["h_alero"] + (gp["A"] / 2) * math.tan(math.radians(gp["pendiente_deg"])) / 2
    seccion = ancho_int * h_media
    v = q_inst / 3600 / seccion
    q_min = aves * E["vent_min_m3h_ave"]
    n36 = math.ceil(q_min / E["ventilador_36_m3h"])
    panel = q_inst / 3600 / E["v_panel_m_s"]
    n_cab = min(n50, 4)
    return {"caudal_verano_m3h": round(q, 0), "ventiladores_50": n50, "caudal_instalado_m3h": q_inst,
            "seccion_m2": round(seccion, 2), "velocidad_tunel_m_s": round(v, 2),
            "verifica_velocidad": 1.0 <= v <= 2.5, "caudal_minimo_m3h": round(q_min, 0), "ventiladores_36": n36,
            "panel_evaporativo_m2": round(panel, 1), "panel_por_lado_m": round(panel / 2 / 1.8, 1),
            "panel_alto_m": 1.8, "ventiladores_cabecera": n_cab, "ventiladores_laterales_por_lado": math.ceil((n50 - n_cab) / 2)}


# ---------------------------------------------------------------------------------------- transportadores
BANDAS = {  # q_B en kg/m (P: valores típicos de catálogo)
    0.50: {"lisa": 3.6, "bordes": 6.5},
    0.60: {"lisa": 4.3, "bordes": 7.5},
}


def coef_C(L):
    """Coeficiente de resistencias secundarias de DIN 22101 (tabla), interpolado; para L < 10 m se toma 4,5."""
    tabla = [(10, 4.5), (20, 3.2), (40, 2.4), (60, 2.0), (80, 1.92), (100, 1.78), (150, 1.58)]
    if L <= tabla[0][0]:
        return tabla[0][1]
    for (l0, c0), (l1, c1) in zip(tabla, tabla[1:]):
        if L <= l1:
            return c0 + (c1 - c0) * (L - l0) / (l1 - l0)
    return tabla[-1][1]


def cinta(t, Q_t_h, v=0.40, eta=0.85, f=0.025, theta_sob=20.0):
    p0, p1 = t["p0"], t["p1"]
    L = math.dist(p0, p1)
    H = p1[2] - p0[2]
    delta = math.degrees(math.asin(max(-1, min(1, H / L)))) if L else 0
    B = t["ancho"]
    tipo_banda = "bordes" if t["tipo"] in ("inclinada",) else "lisa"
    qB = BANDAS.get(B, BANDAS[0.50])[tipo_banda]
    b = 0.9 * B - 0.05
    A = b * b * math.tan(math.radians(theta_sob)) / 6
    if t["tipo"] == "inclinada":
        A *= 1.6                          # bordes de 80 mm y tacos: la sección útil crece (P)
    k = max(0.4, 1 - 0.012 * abs(delta)) if t["tipo"] != "inclinada" else 1.0
    Qv = A * v * k * 3600
    Qm = Qv * E["rho_guano"] / 1000
    qG = Q_t_h / (3.6 * v)
    qRO, qRU = 4.5, 1.1
    C = coef_C(L)
    FH = C * f * L * g * (qRO + qRU + (2 * qB + qG) * math.cos(math.radians(delta)))
    FSt = qG * H * g
    FS = 2 * 300 + 150 * min(L, 3.0)      # 2 rascadores + faldones en la carga (P)
    P = (FH + FSt + FS) * v / eta / 1000
    kw, e_m, cf = motor_std(P)
    D_tambor = 0.32
    rpm = v / (math.pi * D_tambor) * 60
    return {"id": t["id"], "tipo": t["tipo"], "L_m": round(L, 2), "H_m": round(H, 2), "inclinacion_deg": round(delta, 1),
            "B_m": B, "v_m_s": v, "Q_diseno_t_h": Q_t_h, "Q_capacidad_t_h": round(Qm, 1),
            "verifica_capacidad": Qm >= Q_t_h, "P_requerida_kW": round(P, 2), "motor_kW": kw,
            "eta": e_m, "cosf": cf, "In_A": round(corriente(kw, e_m, cf), 2), "tambor_D_m": D_tambor,
            "rpm_tambor": round(rpm, 1), "relacion_reductor": round(1440 / rpm, 0), "C": round(C, 2)}


def transportadores(bal):
    # caudales de diseño (P): en cada galpón corre un piso por vez (las 4 filas juntas); en cada lado pueden
    # correr los 2 galpones a la vez, y en la tolva pulmón pueden llegar los dos lados juntos.
    q_piso = bal["flujo_por_piso_t_h"]
    Q = {"transversal": math.ceil(q_piso * 1.25), "inclinada": math.ceil(q_piso * 1.25),
         "colectora": math.ceil(2 * q_piso * 1.25), "principal": math.ceil(2 * q_piso * 1.25)}
    res = []
    for t in D["transporte"]:
        v = {"transversal": 0.30, "inclinada": 0.40}.get(t["tipo"], 0.50)
        res.append(cinta(t, Q[t["tipo"]], v=v))
    return res


def motores_nuevos(trans):
    """Motores del transporte de guano y de la recepción (P). Tags: M1xx a M4xx en cada galpón (el primer dígito
    es el galpón) y M81 a M90 afuera de los galpones."""
    m = []
    porid = {t["id"]: t for t in trans}
    j = D["jaulas"]
    for gp in D["galpones"]:
        k = int(gp["id"][1])
        n = 1
        for piso in range(1, j["pisos"] + 1):
            for fila in "ABCD"[: j["filas"]]:
                kw, eta, cf = 1.1, 0.841, 0.77
                m.append({"tag": f"M{k}{n:02d}", "nom": f"Cinta de guano {gp['id']} piso {piso} fila {fila}",
                          "kW": kw, "In": round(corriente(kw, eta, cf), 2), "arranque": "directo",
                          "tablero": f"TS-{gp['id']}", "tipo": "P", "nota": "1 a 1,5 kW hasta 100 m (proveedores)"})
                n += 1
        for cod, nom, arr in ((f"CT-{k}", "Cinta transversal ", "directo"), (f"CI-{k}", "Cinta inclinada ", "VFD")):
            c = porid[cod]
            m.append({"tag": f"M{k}{n:02d}", "nom": nom + gp["id"], "kW": c["motor_kW"], "In": c["In_A"], "arranque": arr,
                      "tablero": f"TS-{gp['id']}", "tipo": "P", "nota": f"P req. {c['P_requerida_kW']} kW"})
            n += 1
    for cod, tag in (("CE-O", "M81"), ("CP-O", "M82"), ("CE-E", "M83"), ("CP-E", "M84")):
        c = porid[cod]
        m.append({"tag": tag, "nom": ("Cinta colectora " if cod.startswith("CE") else "Cinta principal ") + cod,
                  "kW": c["motor_kW"], "In": c["In_A"], "arranque": "VFD", "tablero": "TS-GU", "tipo": "P",
                  "nota": f"P req. {c['P_requerida_kW']} kW"})
    for i in range(D["tolva_pulmon"]["sinfines"]["n"]):
        kw, eta, cf = 3.0, 0.877, 0.81
        m.append({"tag": f"M{85 + i}", "nom": f"Sinfín dosificador {i + 1} de la TP-01", "kW": kw,
                  "In": round(corriente(kw, eta, cf), 2), "arranque": "VFD", "tablero": "TS-GU", "tipo": "P",
                  "nota": "Ø400 × 6 m bajo la tolva llena; confirmar con el fabricante"})
    for tag, nom in (("M89", "Actuador de la compuerta desviadora DV-O"), ("M90", "Actuador de la compuerta desviadora DV-E")):
        kw, eta, cf = 0.37, 0.77, 0.70
        m.append({"tag": tag, "nom": nom, "kW": kw, "In": round(corriente(kw, eta, cf), 2), "arranque": "inversor",
                  "tablero": "TS-GU", "tipo": "P", "nota": "actuador eléctrico de cuarto de vuelta con finales de carrera"})
    return m


def main():
    bal = balance()
    ven = ventilacion()
    tr = transportadores(bal)
    mot = motores_nuevos(tr)
    out = {"entradas": {k: {"valor": v[0], "tipo": v[1], "fuente": v[2]} for k, v in ENT.items()},
           "balance": bal, "ventilacion": ven, "transportadores": tr, "motores_nuevos": mot,
           "potencia_nueva_kW": round(sum(x["kW"] for x in mot), 2)}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"aves {bal['aves_total']}, guano {bal['guano_total_kg_dia']} kg/día, secador {bal['secador_kg_h_regimen']} kg/h "
          f"en {bal['secador_turnos']} turnos (aire ≈ {bal['T_aire_regimen_C']} °C), "
          f"tolva {bal['tolva_pulmon_dias']} días, huevos {bal['huevos_dia']}/día ({bal['palets_dia']} palets)")
    print(f"ventilación: {ven['ventiladores_50']} × 50\" por galpón, túnel {ven['velocidad_tunel_m_s']} m/s, "
          f"panel {ven['panel_evaporativo_m2']} m²")
    for t in tr:
        print(f"  {t['id']:5s} L {t['L_m']:5.1f} H {t['H_m']:5.2f} Q {t['Q_diseno_t_h']}/{t['Q_capacidad_t_h']} t/h "
              f"P {t['P_requerida_kW']:.2f} → {t['motor_kW']} kW")
    print(f"motores nuevos: {len(mot)}, {out['potencia_nueva_kW']} kW instalados")


if __name__ == "__main__":
    main()
