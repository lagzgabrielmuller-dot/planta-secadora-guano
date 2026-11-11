"""P23 - Esquema unifilar TG2 (consumos Rev. D), con los extractores y ventiladores de E10.

Lee los números de fuente/calculos/resultados.json (calculos_memoria.py).
"""
import json
import os

from lamina_secadora import (COL, FECHA, circulo, exportar_lamina, lamina, linea, rect,
                             relleno_rect, subtitulo, t, tabla, titulo_vista, tn)

AQUI = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(AQUI, "..", "calculos", "resultados.json"), encoding="utf-8"))["tg2"]
ILU = json.load(open(os.path.join(AQUI, "..", "calculos", "resultados.json"), encoding="utf-8"))["iluminacion"]


def coma(x, d=2):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def interruptor(msp, x, y, etiqueta, dato):
    """Interruptor termomagnético (IEC 60617): contacto inclinado con cruz en el borne fijo."""
    linea(msp, (x, y), (x, y - 2))
    linea(msp, (x, y - 2), (x + 2.6, y - 7.0))
    linea(msp, (x - 1.0, y - 1.0), (x + 1.0, y - 3.0), "CONTORNO")
    linea(msp, (x - 1.0, y - 3.0), (x + 1.0, y - 1.0), "CONTORNO")
    linea(msp, (x, y - 7.6), (x, y - 9))
    tn(msp, etiqueta, (x - 1.6, y - 4.0), 2.4, "MIDDLE_RIGHT")
    t(msp, dato, (x + 3.4, y - 5.0), 2.0, "MIDDLE_LEFT")
    return y - 9


def fusible(msp, x, y, texto, h=8):
    linea(msp, (x, y), (x, y - 1.5))
    rect(msp, x - 1.4, y - 1.5, x + 1.4, y - 1.5 - h * 0.55)
    linea(msp, (x, y - 1.5), (x, y - 1.5 - h * 0.55), "FINO")
    linea(msp, (x, y - 1.5 - h * 0.55), (x, y - h))
    t(msp, texto, (x + 2.6, y - h / 2), 2.1, "MIDDLE_LEFT")
    return y - h


def main():
    revs = [("D", "09/2026", "Emisión original: TG2, tableros seccionales, bomba de incendio y cogeneración"),
            ("E", "10/2026", "EX1-EX2 y VM1-VM2 en Q27 (TS-VEN); potencia recalculada; QG2 Ir = 63 A"),
            ("F", FECHA, "Acometida 4×35 mm²; Q25 y Q26 con potencia (cálculo luminotécnico); largos reales"),
            ("G", "11/2026", "Ventilador M40 del enfriador de producto (Rev. F) en Q21; potencia recalculada")]
    doc, msp, z = lamina(23, "ESQUEMA UNIFILAR TG2\n(CONSUMOS NUEVOS REV. D)", "S/E", revs)
    titulo_vista(msp, "ESQUEMA UNIFILAR TG2 - 3 × 380/220 V - 50 Hz - ECT TT (el TGF de la Rev. C no se modifica)", 26, 276, 3.3)

    # ---------------- pilar de acometida
    relleno_rect(msp, 28, 238, 226, 264, (245, 245, 245))
    rect(msp, 28, 238, 226, 264)
    tn(msp, "PILAR DE ACOMETIDA EXISTENTE (plano 05): medidor 3 TI 150/5 A - seccionador NH00 160 A → TGF", (30, 261.5), 2.1)
    linea(msp, (40, 256), (205, 256), "CONTORNO", lw=70)
    salidas = [(62, "salida existente", "NH00 3 × 160 A → TGF"), (118, "salida nueva", "NH00 3 × 80 A → TG2"),
               (190, "alimentación exclusiva", "NH00 3 × 25 A → TBI")]
    for x, a, b in salidas:
        fusible(msp, x, 256, "", 10)
        t(msp, a, (x + 2.8, 251.5), 2.0)
        tn(msp, b, (x + 2.8, 248.0), 2.0)
    linea(msp, (62, 246), (62, 230))
    tn(msp, "TGF (Rev. C, sin cambios)", (62, 227.5), 2.4, "MIDDLE_CENTER")
    # acometida al TG2
    linea(msp, (118, 246), (118, 228))
    t(msp, f"4 × {R['acometida']['S']} mm² Cu IRAM 2178 enterrado · {R['acometida']['L']} m", (120, 236), 2.0)
    rect(msp, 113, 220, 123, 226)
    linea(msp, (118, 220), (118, 211))
    tn(msp, "QG2 4P 80 A · Icu 10 kA · Ir regulado a 63 A", (125, 224.5), 2.1)
    t(msp, "DPS T2 · multimedidor V-A-kW-cos φ", (125, 221.0), 2.0)
    # alimentación de las bombas de incendio (sin pasar por el QG2)
    linea(msp, (190, 246), (190, 236))
    t(msp, "4 × 6 mm² · 55 m", (192, 240), 2.0)
    linea(msp, (190, 236), (214, 236))
    linea(msp, (214, 236), (214, 152))

    # ---------------- barras del TG2
    tn(msp, "TG2 - BARRAS Cu 3F+N+PE 100 A (sala de control 22)", (30, 212.5), 2.3)
    linea(msp, (30, 210), (206, 210), "CONTORNO", lw=140)
    linea(msp, (118, 211), (118, 210))
    circ = {c["Q"]: c for c in R["circuitos"]}
    salidas_tg2 = [
        ("Q21", "TS-ENS", "zaranda y envasado", "M18 M19 M20 M21\nM22 M24 M35"),
        ("Q22", "TS-LAV", "limpieza de vehículos", "M16 M17"),
        ("Q23", "TS-BIO", "biogás + G1 25 kWe", "M27 a M34 · G1"),
        ("Q24", "VFD M23", "extractor recepción", "M23 4 kW"),
        ("Q25", "TL2", "iluminación Sector Este", "farolas y depósito"),
        ("Q26", "CI", "central de incendio", "detectores y sirenas"),
        ("Q27", "TS-VEN", "ventilación nave (E10)", "M36 M37 (EX1 EX2)\nM38 M39 (VM1 VM2)"),
    ]
    otros = {"Q25": ("4P 16 A", "4 × 4 mm² · 90 m"), "Q26": ("2P 6 A", "2 × 2,5 mm² · 5 m")}
    xs = [36, 61, 86, 111, 136, 161, 188]
    for x, (q, tab, desc, cargas) in zip(xs, salidas_tg2):
        if q in circ:
            c = circ[q]
            dato = f"{'4P' if q != 'Q26' else '2P'} {c['In']} A"
            cable = f"{'2' if c.get('fases') == 1 else '4'} × {coma(c['S'], 1).replace(',0', '')} mm² · {c['L']} m"
        else:
            dato, cable = otros[q]
        y = interruptor(msp, x, 210, q, dato)
        linea(msp, (x, y), (x, 166))
        t(msp, cable, (x - 1.2, 186), 1.9, "MIDDLE_CENTER", rotacion=90)
        nuevo = q == "Q27"
        relleno_rect(msp, x - 10, 159, x + 10, 166, (255, 243, 205) if q == "Q23" else (225, 240, 228) if nuevo else (235, 241, 245))
        rect(msp, x - 10, 159, x + 10, 166)
        tn(msp, tab, (x, 162.5), 2.4, "MIDDLE_CENTER")
        t(msp, desc, (x, 157.2), 1.6, "TOP_CENTER")
        t(msp, cargas, (x, 154.2), 1.6, "TOP_CENTER")
        if nuevo:
            tn(msp, "NUEVO", (x, 168.5), 1.8, "BOTTOM_CENTER", color=COL["salida"])
    # G1 en paralelo
    linea(msp, (86, 150.5), (86, 146.5))
    circulo(msp, (86, 143), 3.5)
    tn(msp, "G1", (86, 143), 2.4, "MIDDLE_CENTER")
    t(msp, "motogenerador a biogás 25 kWe\nrelé de interconexión 27/59/81 + 32\n(paralelo sujeto a la distribuidora)", (91, 145.5), 1.7, "TOP_LEFT")
    # tablero de bombas de incendio
    relleno_rect(msp, 202, 140, 226, 152, (248, 220, 222))
    rect(msp, 202, 140, 226, 152)
    tn(msp, "TBI", (214, 149.5), 2.4, "MIDDLE_CENTER")
    t(msp, "bombas de incendio\nM25 7,5 kW (solo magn.)\nM26 jockey 0,75 kW", (214, 147.0), 1.45, "TOP_CENTER")
    # comando de los extractores
    t(msp, "EX1/EX2 por termostato TH\n(arranque escalonado)", (171, 147.5), 1.6, "TOP_LEFT")

    # ---------------- tabla de consumos
    subtitulo(msp, "CONSUMOS NUEVOS REV. D (TG2 y TBI)", 232, 268)
    filas = [["Tag", "Accionamiento", "kW", "In A", "Arranque", "Tablero"]]
    sombras = {}
    for i, m in enumerate(R["motores"], start=1):
        filas.append([m["tag"], m["nom"], coma(m["kW"]), coma(m["In"], 1), m["arranque"], m["tablero"]])
        if m["tag"] in ("M36", "M37", "M38", "M39"):
            sombras[i] = (225, 240, 228)
    filas.append(["", "TOTAL NUEVO (incluye incendio)", coma(R["total_kW"]), "", "", ""])
    y = tabla(msp, 232, 266, [12, 84, 13, 13, 18, 36], filas, h_fila=3.25, altura=2.0,
              alin=["L", "L", "R", "R", "C", "L"], negrita_ultima=True, sombras=sombras)
    t(msp, f"Sombreado: agregados de esta revisión (E10, plano 24). Total anterior {coma(R['total_anterior_kW'])} kW "
           f"+ {coma(R['agregado_kW'])} kW.", (232, y - 2.0), 1.9, "TOP_LEFT")

    # ---------------- verificación de circuitos
    subtitulo(msp, "VERIFICACIÓN DE LOS CIRCUITOS (Ib ≤ In ≤ Iz; ΔU; memoria 2.4)", 26, 129)
    filas = [["Circ.", "Destino", "kW", "Ib A", "In A", "Cable Cu", "L m", "Iz A", "ΔU %"]]
    for c in R["circuitos"]:
        filas.append([c["Q"], c["destino"], coma(c["kW"]), coma(c["Ib"], 1), c["In"],
                      f"{'2' if c.get('fases') == 1 else '4'} × {coma(c['S'], 1).replace(',0', '')} mm² ({c['metodo']})", c["L"], coma(c["Iz"], 1), coma(c["dU_pct"])])
    ac = R["acometida"]
    filas.append(["QG2", "Acometida pilar → TG2 (demanda)", coma(R["demanda_tg2_kW"], 1), coma(R["I_demanda_A"], 1),
                  "63*", f"4 × {ac['S']} mm² (D1)", ac["L"], coma(ac["Iz"], 1), coma(ac["dU_pct"])])
    y = tabla(msp, 26, 127, [11, 55, 12, 12, 11, 32, 10, 13, 12], filas, h_fila=3.4, altura=2.0,
              alin=["L", "L", "R", "R", "R", "L", "R", "R", "R"])
    t(msp, f"* Acometida 4 × {ac['S']} mm² enterrada (Iz = {coma(ac['Iz'], 1)} A): fusible NH00 {ac['fusible']} A y QG2 "
           f"{ac['In']} A verifican In ≤ Iz; Ir = {ac['Ir']} A por selectividad. E: bandeja, D1: enterrado.",
      (26, y - 1.5), 1.8, "TOP_LEFT")

    # ---------------- balance de potencia
    b = R["balance"]
    subtitulo(msp, "BALANCE Y POTENCIA A CONTRATAR", 26, 86)
    filas = [["Balance de potencia", "kW"],
             ["Demanda TGF existente (Rev. C, fs 0,8)", b["TGF_kW"].replace("-", "-")],
             [f"Demanda nueva TG2 (fs {coma(R['fs'])} sobre {coma(R['base_fs_kW'], 1)} kW)", coma(b["TG2_kW"], 1)],
             ["Bomba de incendio (no simultánea, se suma igual)", "7,5"],
             ["Total sin cogeneración (G1 parada)", coma(b["sin_G1_kW"], 1)],
             ["Aporte de la cogeneración G1 (12,7 h/día)", "−25"],
             ["Potencia a contratar recomendada", str(b["adoptada_kW"])]]
    tabla(msp, 26, 84, [96, 22], filas, h_fila=3.6, altura=2.1, alin=["L", "R"], negrita_ultima=True)
    t(msp, f"Margen con G1 parada: {coma(b['margen_sin_G1_pct'], 1)} %", (26, 57.5), 1.9, "TOP_LEFT")

    subtitulo(msp, "NOTAS", 150, 86)
    t(msp, "\n".join([
        "1. El TGF, sus 15 circuitos y el unifilar del plano 05 no se modifican: todas las cargas nuevas van al TG2.",
        "2. La bomba de incendio se alimenta desde el pilar antes del QG (no la corta la parada general); sin relé térmico.",
        "3. TS-BIO y los equipos en zona clasificada: motores y cajas Ex (IEC 60079), cables armados, puesta a tierra.",
        "4. Caída de tensión máxima: 3 % en alimentadores y 5 % en motores (AEA 90364). Diferenciales 30 mA en tomas.",
        "5. Distribuidora: Cooperativa La Agrícola Regional (LAR); confirmar potencia y conexión en paralelo de G1.",
        "6. TS-VEN: EX1/EX2 con contactor y guardamotor 2,5-4 A comandados por termostato; VM1/VM2 en tomas 2P+T 16 A "
        "con diferencial 30 mA, uno en L1 y otro en L2.",
        f"7. Q25 (TL2): {coma(ILU['n'], 0)} campanas LED 150 W en el depósito ({ILU['E_real']} lx), farolas, proyectores Ex y "
        f"reflectores = {coma(ILU['P_Q25_kW'], 2)} kW. Q26 (CI) = {coma(ILU['P_Q26_kW'], 2)} kW. Interruptores IEC 60898-1 "
        "clase de limitación 3.",
    ]), (150, 83), 1.85, "TOP_LEFT", ancho=77)
    exportar_lamina(doc, 23)


if __name__ == "__main__":
    main()
