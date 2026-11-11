"""P05 - Esquema unifilar del tablero general (TGF), Rev. D (redibujo vectorial de la Rev. C).

Transcripción fiel de la lámina PNG original (Rev. C): acometida, QG, barras, 15 circuitos
de motores (Q1-Q15), batería de capacitores, fuente, TS-1 y TIT, tabla de circuitos y notas.
Símbolos IEC 60617.
"""
from lamina_secadora import (FECHA, circulo, exportar_lamina, lamina, linea, notas, poli, rect,
                             subtitulo, t, tabla, titulo_vista, tn)


def caja_disparo(msp, x, y, s=2.4):
    """Recuadro con el símbolo 'I>' (disparo magnético) junto al interruptor."""
    rect(msp, x - s / 2, y - s / 2, x + s / 2, y + s / 2, "CONTORNO")
    t(msp, "I>", (x, y), 1.4, "MIDDLE_CENTER")


def interruptor(msp, x, y, largo=8.5, cruz=True):
    """Interruptor (IEC 60617): línea, cuchilla inclinada y cruz en el borne fijo. Devuelve la y de salida."""
    y1 = y - 7.3
    linea(msp, (x, y), (x, y1))
    if cruz:
        linea(msp, (x - 1.2, y1 + 1.2), (x + 1.2, y1 - 1.2))
        linea(msp, (x - 1.2, y1 - 1.2), (x + 1.2, y1 + 1.2))
    linea(msp, (x, y1), (x + 2.6, y1 - 4.2))
    return y1 - 5.5


def contacto_na(msp, x, y):
    """Contacto normal abierto del contactor KM (cuchilla abierta)."""
    linea(msp, (x, y), (x + 2.6, y - 4.4))
    return y - 6.0


def reactancia(msp, x, y, n=3, r=0.75):
    """Bobina (reactancia de línea): semicírculos en serie. Devuelve la y inferior."""
    for i in range(n):
        c = (x, y - r - 2 * r * i)
        msp.add_arc(c, r, -90, 90, dxfattribs={"layer": "CONTORNO"})
    return y - 2 * r * n


def variador(msp, x, ytop, lado=10.0):
    """Convertidor de frecuencia: cuadrado con diagonal y '~' arriba a la izquierda y abajo a la derecha."""
    x0, x1, y0 = x - lado / 2, x + lado / 2, ytop - lado
    rect(msp, x0, y0, x1, ytop)
    linea(msp, (x0, y0), (x1, ytop), "FINO")
    t(msp, "~", (x0 + 2.0, ytop - 2.2), 2.2, "MIDDLE_CENTER")
    t(msp, "~", (x1 - 2.0, y0 + 2.2), 2.2, "MIDDLE_CENTER")
    return y0


def motor(msp, x, yc, r=4.6):
    circulo(msp, (x, yc), r)
    tn(msp, "M", (x, yc + 1.0), 3.0, "MIDDLE_CENTER")
    t(msp, "3~", (x, yc - 2.3), 1.9, "MIDDLE_CENTER")


def tierra(msp, x, y):
    """Símbolo de puesta a tierra con el extremo superior en (x, y)."""
    linea(msp, (x, y), (x, y - 1.6))
    for i, w in enumerate((2.2, 1.5, 0.8)):
        linea(msp, (x - w, y - 1.6 - i * 0.7), (x + w, y - 1.6 - i * 0.7))


def diferencial(msp, x, y):
    """Bloque diferencial 'ID' sobre la línea; y = centro."""
    rect(msp, x - 1.3, y - 2.1, x + 1.3, y + 2.1)
    t(msp, "ID", (x, y), 1.2, "MIDDLE_CENTER")
    t(msp, "30 mA", (x + 2.0, y), 1.6, "MIDDLE_LEFT")


# ------------------------------------------------------------------ datos (del original Rev. C)
# Q, motor, kW, In, rango GM, KM, tipo (V = VFD con RL, v = VFD, d = directo), cable, etiqueta
CIRC = [
    ("Q1", "M1", "15 kW", "29,5 A", "24-32 A", "", "V", "4x6 mm² apant."),
    ("Q2", "M2", "15 kW", "29,5 A", "24-32 A", "", "V", "4x6 mm² apant."),
    ("Q3", "M3", "22 kW", "42,8 A", "37-50 A", "", "V", "4x10 mm² apant."),
    ("Q4", "M4", "4,0 kW", "8,4 A", "6,0-10 A", "", "V", "4x1,5 mm² apant."),
    ("Q5", "M5", "0,75 kW", "1,8 A", "1,6-2,5 A", "", "v", "4x1,5 mm² apant."),
    ("Q6", "M6", "0,75 kW", "1,8 A", "1,6-2,5 A", "", "v", "4x1,5 mm² apant."),
    ("Q7", "M7", "0,75 kW", "1,8 A", "1,6-2,5 A", "", "v", "4x1,5 mm² apant."),
    ("Q8", "M8", "0,75 kW", "1,8 A", "1,6-2,5 A", "", "v", "4x1,5 mm² apant."),
    ("Q9", "M9", "0,75 kW", "1,8 A", "1,6-2,5 A", "KM9", "d", "4x1,5 mm²"),
    ("Q10", "M10", "1,1 kW", "2,6 A", "2,5-4,0 A", "KM10", "d", "4x1,5 mm²"),
    ("Q11", "M11", "1,5 kW", "3,4 A", "2,5-4,0 A", "KM11", "d", "4x1,5 mm²"),
    ("Q12", "M12", "0,75 kW", "1,8 A", "1,6-2,5 A", "", "v", "4x1,5 mm² apant."),
    ("Q13", "M13", "0,55 kW", "1,4 A", "1,0-1,6 A", "KM13", "d", "4x1,5 mm²"),
    ("Q14", "M14", "3,0 kW", "6,4 A", "6,0-10 A", "KM14", "d", "4x1,5 mm²"),
    ("Q15", "M15", "0,25 kW", "0,8 A", "0,6-1,0 A", "KM15", "d", "4x1,5 mm²"),
]

TABLA = [
    ["Circ.", "Motor", "Accionamiento", "P kW", "η", "cos φ", "In A", "Arranque", "Protección (rango / ajuste)",
     "Cable Cu IRAM 2178", "L m", "ΔU"],
    ["Q1", "M1", "Ventilador impulsión 1", "15,00", "92,1 %", "0,84", "29,46", "VFD + RL 3 %", "GM 24,0-32,0 A / Ir 29,5 A", "4x6 mm² apant.", "28", "1,18 %"],
    ["Q2", "M2", "Ventilador impulsión 2", "15,00", "92,1 %", "0,84", "29,46", "VFD + RL 3 %", "GM 24,0-32,0 A / Ir 29,5 A", "4x6 mm² apant.", "30", "1,27 %"],
    ["Q3", "M3", "Extractor de gases", "22,00", "93,0 %", "0,84", "42,79", "VFD + RL 3 %", "GM 37,0-50,0 A / Ir 42,8 A", "4x10 mm² apant.", "33", "1,22 %"],
    ["Q4", "M4", "Ventilador de combustión", "4,00", "88,6 %", "0,82", "8,37", "VFD + RL 3 %", "GM 6,0-10,0 A / Ir 8,4 A", "4x1,5 mm² apant.", "33", "1,53 %"],
    ["Q5", "M5", "Cinta piso 1", "0,75", "82,5 %", "0,75", "1,84", "VFD", "GM 1,6-2,5 A / Ir 1,8 A", "4x1,5 mm² apant.", "15", "0,14 %"],
    ["Q6", "M6", "Cinta piso 2", "0,75", "82,5 %", "0,75", "1,84", "VFD", "GM 1,6-2,5 A / Ir 1,8 A", "4x1,5 mm² apant.", "28", "0,26 %"],
    ["Q7", "M7", "Cinta piso 3", "0,75", "82,5 %", "0,75", "1,84", "VFD", "GM 1,6-2,5 A / Ir 1,8 A", "4x1,5 mm² apant.", "15", "0,14 %"],
    ["Q8", "M8", "Cinta de alimentación", "0,75", "82,5 %", "0,75", "1,84", "VFD", "GM 1,6-2,5 A / Ir 1,8 A", "4x1,5 mm² apant.", "27", "0,25 %"],
    ["Q9", "M9", "Esparcidor", "0,75", "82,5 %", "0,75", "1,84", "directo (KM)", "GM 1,6-2,5 A / Ir 1,8 A", "4x1,5 mm²", "26", "0,24 %"],
    ["Q10", "M10", "Sinfín de descarga", "1,10", "84,1 %", "0,77", "2,58", "directo (KM)", "GM 2,5-4,0 A / Ir 2,6 A", "4x1,5 mm²", "17", "0,23 %"],
    ["Q11", "M11", "Elevador de cangilones", "1,50", "85,3 %", "0,79", "3,38", "directo (KM)", "GM 2,5-4,0 A / Ir 3,4 A", "4x1,5 mm²", "17", "0,31 %"],
    ["Q12", "M12", "Sinfín de cáscara", "0,75", "82,5 %", "0,75", "1,84", "VFD", "GM 1,6-2,5 A / Ir 1,8 A", "4x1,5 mm² apant.", "35", "0,33 %"],
    ["Q13", "M13", "Sinfín de cenizas", "0,55", "80,0 %", "0,73", "1,43", "directo (KM)", "GM 1,0-1,6 A / Ir 1,4 A", "4x1,5 mm²", "33", "0,23 %"],
    ["Q14", "M14", "Bomba del lavador", "3,00", "87,7 %", "0,81", "6,42", "directo (KM)", "GM 6,0-10,0 A / Ir 6,4 A", "4x1,5 mm²", "40", "1,41 %"],
    ["Q15", "M15", "Vibrador de tolva", "0,25", "73,0 %", "0,68", "0,77", "directo (KM)", "GM 0,63-1,0 A / Ir 0,8 A", "4x1,5 mm²", "35", "0,12 %"],
    ["", "", "TOTAL INSTALADO / DEMANDA (fs 0,8)", "66,90", "", "", "135,7", "", "demanda 109 A - QG 125 A", "", "", ""],
]

NOTAS = [
    "1. ECT TT según AEA 90364; masas a barra PE; diferenciales 30 mA en circuitos de tomas e iluminación.",
    "2. Guardamotores regulados a la corriente nominal del motor (Ir = In); en circuitos con VFD protegen la entrada del variador según su fabricante.",
    "3. cos φ sin batería ≈ 0,95 (los VFD tienen cos φ1 ≈ 0,97): batería de 10 kVAr con reactancia de desintonía 7 % (evita resonancia con armónicas).",
    "4. Cables de salida de VFD apantallados, malla a tierra en ambos extremos; bandeja de potencia separada 300 mm de señales.",
    "5. Caída de tensión máxima en motores 1,5 % + acometida < 1 % (límite AEA: 5 %).",
    "6. Parada de emergencia con relé de seguridad cat. 3: abre la bobina de mínima de QG y la alimentación de los VFD (STO).",
    "7. Pilar: fusibles NH00 160 A gG aguas arriba del QG 125 A (selectividad por corriente); el cable 3x50+25 mm² enterrado "
    "debe tener Iz ≥ 178 A (In ≤ 0,9 Iz).",
]


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "ECT TT; GM a In; η y cos φ de catálogo; batería desintonizada; cables VFD"),
            ("C", "09/2026", "Pilar: medición ENERSA 3 TI; secc. NH00 3x160 A gG protege cable 40 m, selectivo"),
            ("D", "10/2026", "Redibujo vectorial (DXF y PDF A3); numeración de hojas x/24"),
            ("E", FECHA, "Distribuidora LAR (no ENERSA); tarifa T3, 100 kW contratados (plano 23)")]
    for r in revs:
        assert len(r[2]) <= 80, (r[0], len(r[2]))
    doc, msp, z = lamina(5, "ESQUEMA UNIFILAR - TABLERO GENERAL (TGF)" + " " * 9, "S/E", revs)
    titulo_vista(msp, "ESQUEMA UNIFILAR TGF  -  3 x 380/220 V  -  50 Hz  -  ECT: TT  -  Icc presunta en barras: 6 kA",
                 25, 281.5, 3.6)

    X = 43.9  # línea principal
    # ---------------- pilar de acometida
    rect(msp, 26, 265.5, 205, 278.0)
    tn(msp, "PILAR DE ACOMETIDA (línea municipal - plano 11)", (203, 276.4), 2.0, "MIDDLE_RIGHT")
    t(msp, "Red BT Coop. La Agrícola Regional (LAR) 3x380/220 V", (203, 273.9), 1.8, "MIDDLE_RIGHT")
    for a, b in ((278.0, 276.9), (273.5, 272.0), (268.4, 258.0), (250.4, 245.8), (242.4, 228.3)):
        linea(msp, (X, a), (X, b))
    # medición de la distribuidora
    circulo(msp, (X, 275.2), 1.7)
    t(msp, "3 TI 150/5 A", (X - 2.4, 275.2), 1.8, "MIDDLE_RIGHT")
    linea(msp, (X + 1.7, 275.2), (49.1, 275.2))
    rect(msp, 49.1, 273.2, 57.8, 277.2)
    tn(msp, "kWh", (53.45, 275.2), 2.2, "MIDDLE_CENTER")
    t(msp, "medidor LAR - tarifa T3 grandes demandas BT (100 kW, plano 23)", (59.4, 275.2), 1.8)
    # seccionador bajo carga con fusibles
    linea(msp, (X - 1.0, 272.0), (X + 1.0, 272.0))          # borne del seccionador
    poli(msp, [(X - 0.4, 268.4), (X + 1.9, 271.8), (X + 1.0, 272.3), (X - 1.3, 268.9)], cerrada=True)  # fusible-cuchilla
    linea(msp, (X - 1.6, 267.6), (X + 0.6, 269.0), "FINO")
    tn(msp, "seccionador bajo carga con fusibles NH00 - 3 x 160 A gG (Icu 100 kA)", (48.9, 269.9), 1.9)
    t(msp, "protege el cable de 40 m y es selectivo con el QG de 125 A (curva gG por encima de la del QG)", (48.9, 267.5), 1.7)
    t(msp, "3x50+25 mm² Cu (IRAM 2178) - 40 m", (46.0, 263.6), 1.9)
    # QG
    yq = 258.0
    linea(msp, (X - 1.3, yq + 1.3), (X + 1.3, yq - 1.3))
    linea(msp, (X - 1.3, yq - 1.3), (X + 1.3, yq + 1.3))
    linea(msp, (X, yq), (X + 3.4, yq - 7.2))
    caja_disparo(msp, 48.8, 254.8)
    tn(msp, "QG", (51.7, 257.7), 2.6)
    t(msp, "4P 125 A - Icu 25 kA", (51.7, 254.6), 1.9)
    t(msp, "bobina de mínima + P.E.", (51.7, 251.9), 1.9)
    # multimedidor
    circulo(msp, (X, 244.1), 1.7)
    t(msp, "3 TI 150/5 A", (X - 2.4, 244.1), 1.8, "MIDDLE_RIGHT")
    linea(msp, (X + 1.7, 244.1), (49.1, 244.1))
    rect(msp, 49.1, 241.8, 57.8, 246.5)
    tn(msp, "MM", (53.45, 244.15), 2.2, "MIDDLE_CENTER")
    t(msp, "multimedidor V-A-kW-cosφ-THD", (59.2, 244.1), 1.8)
    # DPS
    poli(msp, [(X, 238.2), (35.9, 238.2), (35.9, 236.8)])
    rect(msp, 33.0, 231.7, 38.8, 236.8)
    t(msp, "DPS", (35.9, 234.25), 1.8, "MIDDLE_CENTER")
    t(msp, "T2", (32.0, 234.25), 1.8, "MIDDLE_RIGHT")
    tierra(msp, 35.9, 231.7)

    # ---------------- barras
    linea(msp, (24, 228.3), (405, 228.3), lw=100)
    tn(msp, "BARRAS Cu 30x5 - 3F+N+PE - 160 A", (50.0, 231.0), 2.2)
    t(msp, "PE -> barra de tierra -> 4 jabalinas Cu 3 m (RT < 5 Ω)", (249.9, 231.0), 1.9)

    paso = 17.85
    ym = 166.0        # centro de los motores
    for i, (q, m, kw, inn, gm, km, tipo, cable) in enumerate(CIRC):
        x = 59.9 + paso * i
        tn(msp, q, (x + 1.2, 223.8), 2.0)
        y = interruptor(msp, x, 228.3)
        caja_disparo(msp, x + 4.8, 218.9)
        # rango del guardamotor (+ contactor)
        t(msp, gm, (x + 1.3, 211.7), 1.6)
        if km:
            t(msp, km, (x + 1.3, 209.2), 1.6)
        linea(msp, (x, y), (x, 213.0))
        ycur = 213.0
        if tipo == "V":
            linea(msp, (x, ycur), (x, 209.0))
            ycur = reactancia(msp, x, 209.0)
            t(msp, "RL 3 %", (x + 1.4, 207.0), 1.6)
            linea(msp, (x, ycur), (x, 202.1))
            ycur = variador(msp, x, 202.1)
        elif tipo == "v":
            linea(msp, (x, ycur), (x, 208.2))
            ycur = variador(msp, x, 208.2)
        else:
            linea(msp, (x, ycur), (x, 205.0))
            contacto_na(msp, x, 205.0)
            ycur = 199.0
        linea(msp, (x, ycur), (x, ym + 4.6))
        yc = (ycur + ym + 4.6) / 2
        t(msp, cable, (x - 1.0, yc), 1.6, "BOTTOM_CENTER", rotacion=90)
        motor(msp, x, ym)
        tn(msp, m, (x, 159.0), 2.2, "MIDDLE_CENTER")
        t(msp, kw, (x, 156.2), 1.6, "MIDDLE_CENTER")
        t(msp, inn, (x, 153.9), 1.6, "MIDDLE_CENTER")

    # QC batería de capacitores
    x = 59.9 + paso * 15
    tn(msp, "QC", (x + 1.2, 223.8), 2.0)
    y = interruptor(msp, x, 228.3)
    t(msp, "3x32 A", (x + 1.3, 211.2), 1.6)
    linea(msp, (x, y), (x, 207.0))
    yb = reactancia(msp, x, 207.0)
    linea(msp, (x, yb), (x, 200.0))
    linea(msp, (x - 3.2, 200.0), (x + 3.2, 200.0), lw=50)
    linea(msp, (x - 3.2, 198.2), (x + 3.2, 198.2), lw=50)
    linea(msp, (x, 198.2), (x, 196.4))
    tierra(msp, x, 196.4)
    tn(msp, "BATERÍA", (x, 177.6), 2.0, "MIDDLE_CENTER")
    t(msp, "10 kVAr\np = 7 %\nregulador", (x, 175.8), 1.7, "TOP_CENTER")

    # QA, QTS, QL
    salidas = [("QA", "2x10 A", False, "FUENTE", "24 Vcc 10 A\nPLC + HMI"),
               ("QTS", "4x25 A", True, "TS-1", "tablero sec.\njunto secador"),
               ("QL", "4x32 A", True, "TIT", "iluminación\ny tomas")]
    for j, (q, dato, dif, nom, desc) in enumerate(salidas):
        x = 59.9 + paso * (16 + j)
        tn(msp, q, (x + 1.2, 223.8), 2.0)
        y = interruptor(msp, x, 228.3)
        t(msp, dato, (x + 1.3, 211.2), 1.6)
        if dif:
            linea(msp, (x, y), (x, 210.0))
            diferencial(msp, x, 207.9)
            linea(msp, (x, 205.8), (x, 192.2))
        else:
            linea(msp, (x, y), (x, 192.2))
        rect(msp, x - 7.15, 178.1, x + 7.15, 192.2)
        tn(msp, nom, (x, 188.6), 2.1, "MIDDLE_CENTER")
        t(msp, desc, (x, 186.0), 1.6, "TOP_CENTER")

    # ---------------- tabla de circuitos
    subtitulo(msp, "TABLA DE CIRCUITOS DE MOTORES (motores IE3 - 4 polos - IP55 - 380 V)", 25, 147.6, 2.8)
    anchos = [10.9, 11.1, 50.0, 13.0, 13.9, 12.2, 13.0, 27.9, 50.0, 34.2, 9.7, 14.1]
    y = tabla(msp, 25, 146.4, anchos, TABLA, h_fila=3.7, altura=1.85,
              alin=["C", "C", "L", "R", "R", "R", "R", "L", "L", "L", "R", "R"], negrita_ultima=True)
    assert y > 80.5, y

    notas(msp, NOTAS, 25, 64.0, altura=1.85, interlineado=1.65, titulo="NOTAS")
    exportar_lamina(doc, 5)


if __name__ == "__main__":
    main()
