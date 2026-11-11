"""P22 - Ficha técnica completa de la secadora, Rev. E.

Redibujo vectorial de la lámina PNG Rev. D (tablas 1 a 7 y vista lateral esquemática 1:100).
Cambio de contenido de la Rev. E: en la tabla 4 se agregan los extractores EX-01/EX-02 y los
ventiladores móviles VM-1/VM-2 de E10. La tabla 5 sigue siendo la del TGF (sin cambios).
"""
from lamina_secadora import (COL, FECHA, circulo, exportar_lamina, lamina, linea, rect,
                             relleno_circulo, relleno_rect, subtitulo, t, titulo_vista)

ENC = (226, 232, 238)
NUEVO = (225, 240, 228)


def tabla_ajustada(msp, x, y, anchos, filas, h_fila=3.2, altura=1.8, alin=None, sombras=None, negrita_ultima=False):
    """Como tabla() de la biblioteca, pero con un ancho de letra más real (Arial) para achicar el texto."""
    alin = alin or ["L"] * len(anchos)
    xs = [x]
    for w in anchos:
        xs.append(xs[-1] + w)
    sombras = dict(sombras or {})
    sombras.setdefault(0, ENC)
    for i, rgb in sombras.items():
        yy = y - (i + 1) * h_fila
        relleno_rect(msp, x, yy, xs[-1], yy + h_fila, rgb)
    for i, fila in enumerate(filas):
        yy = y - (i + 1) * h_fila
        rect(msp, x, yy, xs[-1], yy + h_fila, "FINO")
        neg = i == 0 or (negrita_ultima and i == len(filas) - 1)
        for j, val in enumerate(fila):
            if not val:
                continue
            ca, cb = xs[j], xs[j + 1]
            fa = 0.80 if neg else 0.72
            hh = max(1.5, min(altura, (cb - ca - 1.6) / (fa * len(val))))
            if alin[j] == "C":
                pos, al = ((ca + cb) / 2, yy + h_fila / 2), "MIDDLE_CENTER"
            elif alin[j] == "R":
                pos, al = (cb - 0.8, yy + h_fila / 2), "MIDDLE_RIGHT"
            else:
                pos, al = (ca + 0.8, yy + h_fila / 2), "MIDDLE_LEFT"
            t(msp, val, pos, hh, al, estilo="NEGRITA" if neg else None)
    for c in xs[1:-1]:
        linea(msp, (c, y), (c, y - len(filas) * h_fila), "FINO")
    rect(msp, x, y - len(filas) * h_fila, xs[-1], y, "CONTORNO")
    return y - len(filas) * h_fila


T1 = [["Dato", "Valor"],
      ["Capacidad", "8 t/día de guano húmedo (1.000 kg/h, 1 turno de 8 h)"],
      ["Humedad entrada / salida", "72 % / 15 % (base húmeda)"],
      ["Producto seco / agua evaporada", "329 kg/h / 671 kg/h"],
      ["Aire de secado", "26.600 kg/h a.s. · ≈ 100 °C (máx. 135) → 33 °C, casi saturado"],
      ["Superficie de secado", "3 pisos × 2,0 × 12 m = 72 m²"],
      ["Cámara", "13,0 × 2,6 × 3,4 m, paneles lana de roca 80 mm"],
      ["Tiempo de residencia", "97 min · capa de 30 mm"],
      ["Velocidad de las bandas", "0,37 m/min (0,2 a 0,9 con VFD)"],
      ["Generador", "882 kW a cáscara de arroz · rend. 75 %"]]

T2 = [["Cinta", "Banda", "Motriz / reenvío", "Accionamiento"],
      ["4.1 piso 1", "malla AISI 304 Ø2 p5, 2.000 mm", "Ø300 goma / Ø250", "M5 0,75 kW · 1:300 · ASA 60 15/75"],
      ["4.1 piso 2", "ídem, guías PTFE 40×20, desarr. ≈ 25 m", "Ø300 goma / Ø250", "M6 0,75 kW · 1:300 · ASA 60 15/75"],
      ["4.1 piso 3", "ídem, guías PTFE 40×20 (piso 1: UHMW-PE)", "Ø300 goma / Ø250", "M7 0,75 kW · 1:300 · ASA 60 15/75"],
      ["3 alimentación", "EP 400/3 500 mm, bordes 60, tacos 50", "Ø320 goma / Ø250", "M8 0,75 kW · VFD · 6 rpm"],
      ["Tensiones", "Fe 2.978 N · T1 4.978 N · malla 2.489 N/m (CS 1,6)", "eje SAE 1045 Ø60", "par 471 N·m · 0,373 rpm"]]

T3 = [["Ubicación", "Rodamiento", "Cant.", "Lubricación"],
      ["Tambores motrices (pisos 1-2-3)", "UCF 212 con brida, fuera de cámara", "6", "grasa de litio alta temp., 2 golpes/mes"],
      ["Tambores de reenvío", "UCT 210 tensor (tornillo M20)", "6", "ídem, desde bloque remoto (Rev. D)"],
      ["Cinta de alimentación", "UCP 210 (motriz) / UCT (cola)", "4", "mensual"],
      ["Rodillos de retorno Ø89", "rodamiento sellado de por vida", "15", "sin mantenimiento"],
      ["Esparcidor, sinfines, elevador", "de catálogo del fabricante", "gl.", "mensual (engraseras)"],
      ["Ventiladores M1-M2-M4, extractor M3", "del fabricante del ventilador", "gl.", "según manual; cambio anual"],
      ["Vida L10 (motriz)", "C = 52,8 kN · carga 5,7 kN", "—", "> 100.000 h"]]

T4 = [["Equipo", "Caudal", "Presión", "Motor"],
      ["M1 / M2 ventiladores de impulsión", "15.400 m³/h c/u", "1.500 Pa", "15 kW c/u · VFD"],
      ["M3 extractor (después del lavador)", "≈ 25.000 m³/h a 39 °C", "≈ 2.000 Pa", "22 kW · VFD"],
      ["M4 ventilador de combustión", "1.685 m³/h", "—", "4 kW · VFD"],
      ["M23 extractor de recepción (Rev. D)", "6.000 m³/h", "≈ 800 Pa", "4 kW · VFD"],
      ["Extractores eólicos (Rev. D)", "6 × Ø600", "natural", "—"],
      # Rev. E: agregados de E10
      ["EX-01, EX-02 extractores de la nave (Rev. D, E10)", "54.700 m³/h c/u (catálogo)", "—",
       "1,1 kW (1,5 HP) · directo · TS-VEN"],
      ['VM-1, VM-2 ventiladores móviles 50" (E10)', "51.480 m³/h c/u", "—", "0,75 kW (1 HP) · toma 2P+T"]]

T5 = [["Tag", "Accionamiento", "kW", "In A", "Arranque", "Cable"],
      ["M1", "Ventilador impulsión 1", "15,00", "29,5", "VFD", "6 mm²"],
      ["M2", "Ventilador impulsión 2", "15,00", "29,5", "VFD", "6 mm²"],
      ["M3", "Extractor de gases", "22,00", "42,8", "VFD", "10 mm²"],
      ["M4", "Ventilador de combustión", "4,00", "8,4", "VFD", "1,5 mm²"],
      ["M5", "Cinta piso 1", "0,75", "1,8", "VFD", "1,5 mm²"],
      ["M6", "Cinta piso 2", "0,75", "1,8", "VFD", "1,5 mm²"],
      ["M7", "Cinta piso 3", "0,75", "1,8", "VFD", "1,5 mm²"],
      ["M8", "Cinta de alimentación", "0,75", "1,8", "VFD", "1,5 mm²"],
      ["M9", "Esparcidor", "0,75", "1,8", "DOL", "1,5 mm²"],
      ["M10", "Sinfín de descarga", "1,10", "2,6", "DOL", "1,5 mm²"],
      ["M11", "Elevador de cangilones", "1,50", "3,4", "DOL", "1,5 mm²"],
      ["M12", "Sinfín de cáscara", "0,75", "1,8", "VFD", "1,5 mm²"],
      ["M13", "Sinfín de cenizas", "0,55", "1,4", "DOL", "1,5 mm²"],
      ["M14", "Bomba del lavador", "3,00", "6,4", "DOL", "1,5 mm²"],
      ["M15", "Vibrador de tolva", "0,25", "0,8", "DOL", "1,5 mm²"],
      ["", "TOTAL INSTALADO Rev. C (TGF)", "66,90", "135,7", "", ""]]

T6 = [["Consumo", "Valor"],
      ["Energía eléctrica", "≈ 54-59 kW de demanda · 432 kWh/turno · 108.000 kWh/año"],
      ["Consumo específico eléctrico", "≈ 164 kWh/t de producto (objetivo < 170)"],
      ["Cáscara de arroz", "314 kg/h (282 kg/h con recirculación) · 2,5 t/día"],
      ["Consumo térmico específico", "4,7 MJ/kg de agua evaporada"],
      ["Agua del lavador", "evaporación 0,31 m³/h ≈ 2,5 m³/turno"],
      ["Ácido sulfúrico", "≈ 1.000 l/año (pH 3)"],
      ["Agua de lavado de bandas", "≈ 1 m³/día (a biodigestor)"],
      ["Cenizas generadas", "56 kg/h ≈ 450 kg/día"],
      ["Aceite de reductores", "sintético, cambio anual o 5.000 h"]]

T7 = [["Tags", "Instrumento"],
      ["TT-01..08", "PT100 (TT-06 termocupla K) en aire, producto y humos"],
      ["MT-01 · PT-01", "humedad NIR del producto · presión diferencial del plenum"],
      ["BE-01 · PS-01", "detector de llama UV · presostato de depresión del hogar"],
      ["LS-01..03 · TS-01", "niveles de tolva, silo y lavador · temperatura del silo"],
      ["SS-01..03 · ZS-10/11", "giro de las cintas · centrado de banda"],
      ["ZS-01..06 · AT-01", "microinterruptores de puertas · pH del lavador"]]


DX = 8.0   # corrimiento de la vista para que los rótulos de la izquierda no toquen el recuadro


def vista_lateral(msp, y_top):
    """Vista lateral sur esquemática del secador SC-4 a 1:100 (13,0 m de largo)."""
    x0, x1 = 30.0 + DX, 160.0 + DX
    yb = y_top - 30.2
    t(msp, "SC-4 · 13,0 m · 3 pisos (motrices: pisos 1 y 3 al Este, piso 2 al Oeste)", (95.0 + DX, y_top + 2.4), 1.8,
      "MIDDLE_CENTER")
    relleno_rect(msp, x0, yb, x1, y_top, (244, 244, 244))
    rect(msp, x0, yb, x1, y_top, lw=50)
    for xp in (30.7 + DX, 62.4 + DX, 94.9 + DX, 127.5 + DX, 159.3 + DX):                        # patas
        relleno_rect(msp, xp - 0.6, yb - 3.8, xp + 0.6, yb, (80, 80, 80))
        rect(msp, xp - 0.6, yb - 3.8, xp + 0.6, yb, "FINO")
    pisos = [y_top - 7.4, y_top - 15.8, y_top - 24.2]
    for y in pisos:                                                    # bandas (trazos marrones)
        x = 33.0 + DX
        while x < 157.5 + DX:
            linea(msp, (x, y), (min(x + 2.6, 157.5 + DX), y), color=COL["guano"], lw=35)
            x += 4.2

    def ucf(x, y):                         # soporte con brida (motriz): círculo
        relleno_circulo(msp, (x, y), 1.5, (220, 230, 242))
        circulo(msp, (x, y), 1.5, lw=50)
        rect(msp, x - 1.05, y - 1.05, x + 1.05, y + 1.05, "FINO")

    def uct(x, y):                         # soporte tensor (reenvío): cuadrado
        relleno_rect(msp, x - 1.3, y - 1.3, x + 1.3, y + 1.3, (220, 230, 242))
        rect(msp, x - 1.3, y - 1.3, x + 1.3, y + 1.3, lw=35)

    # Oeste (izquierda) y Este (derecha); piso 1 arriba
    izq = [(uct, 35.5 + DX, pisos[0] - 1.2, "UCT 210"), (ucf, 35.5 + DX, pisos[1] - 1.5, "UCF 212"),
           (uct, 33.0 + DX, pisos[2] - 1.2, "UCT 210")]
    der = [(ucf, 154.4 + DX, pisos[0] - 1.5, "UCF 212"), (uct, 157.0 + DX, pisos[1] - 1.3, "UCT 210"),
           (ucf, 154.4 + DX, pisos[2] - 1.5, "UCF 212")]
    for f, x, y, n in izq:
        f(x, y)
        t(msp, n, (x0 - 1.6, y), 1.6, "MIDDLE_RIGHT")
    for f, x, y, n in der:
        f(x, y)
        t(msp, n, (x1 + 1.6, y), 1.6, "MIDDLE_LEFT")
    # bloques de engrase remoto (L) con sus líneas a los soportes
    for xb in (40.0 + DX, 150.0 + DX):
        yl = y_top - 21.0
        for ya, yb2 in ((pisos[0] - 1.0, yl + 1.6), (yl - 1.6, pisos[2] - 1.4)):
            y = ya
            while y > yb2:
                linea(msp, (xb, y), (xb, max(y - 0.5, yb2)), "FINO")
                y -= 1.0
        relleno_rect(msp, xb - 1.6, yl - 1.6, xb + 1.6, yl + 1.6, (255, 255, 255))
        rect(msp, xb - 1.6, yl - 1.6, xb + 1.6, yl + 1.6, lw=35)
        t(msp, "L", (xb, yl), 1.8, "MIDDLE_CENTER")
    t(msp, "L = bloque de engrase remoto (ítem 21)", (172.0 + DX, y_top - 21.0), 1.8, "MIDDLE_LEFT")
    return yb - 3.8


def main():
    revs = [("D", "09/2026", "Emisión original: datos, cintas, rodamientos, motores, ventil., consumos, instr."),
            ("E", FECHA, "Se agregan los extractores EX1-EX2 y ventiladores VM1-VM2 (E10) en la tabla 4"),
            ("F", "11/2026", "Estudio térmico: guías PTFE en pisos 2 y 3, faldones, temperaturas de trabajo")]
    for r in revs:
        assert len(r[2]) <= 80, (r[0], len(r[2]))
    doc, msp, z = lamina(22, "FICHA TÉCNICA COMPLETA DE LA SECADORA" + " " * 8, "S/E", revs)
    titulo_vista(msp, "FICHA TÉCNICA COMPLETA DEL SECADOR DE CINTA DE 3 PISOS (SC-4) Y EQUIPOS ASOCIADOS", 26, 278.8, 3.4)

    # ---------------- columna izquierda
    subtitulo(msp, "1. DATOS GENERALES", 26, 269.0, 2.5)
    y = tabla_ajustada(msp, 26, 267.0, [44.4, 87.5], T1, h_fila=3.3)
    subtitulo(msp, "2. CINTAS Y TRANSMISIONES", 26, y - 5.4, 2.5)
    y = tabla_ajustada(msp, 26, y - 7.2, [22.5, 58.0, 29.8, 51.7], T2, h_fila=3.3)
    subtitulo(msp, "3. RODAMIENTOS", 26, y - 5.4, 2.5)
    y = tabla_ajustada(msp, 26, y - 7.2, [46.0, 54.4, 9.9, 51.7], T3, h_fila=3.3)
    subtitulo(msp, "4. VENTILADORES Y EXTRACTORES", 26, y - 5.4, 2.5)
    y = tabla_ajustada(msp, 26, y - 7.2, [62.0, 36.0, 15.0, 49.0], T4, h_fila=3.3,
                       sombras={6: NUEVO, 7: NUEVO})
    t(msp, "Sombreado: agregados de la Rev. E (E10, planos 23 y 24).", (26, y - 1.2), 1.6, "TOP_LEFT")

    # ---------------- vista lateral 1:100
    yv = y - 9.6
    titulo_vista(msp, "VISTA LATERAL SUR ESQUEMÁTICA: RODAMIENTOS Y LUBRICACIÓN - ESC. 1:100", 26, yv, 3.0)
    yfin = vista_lateral(msp, yv - 8.5)
    t(msp, "REPUESTOS CRÍTICOS EN DEPÓSITO: tramo de malla de 2 m, 2 rodamientos UCF 212 y 2 UCT 210, cadena ASA 60 "
           "y piñones Z15,\ncorreas de ventiladores, 2 PT100, un módulo de PLC, un variador de 0,75 kW, paletas del "
           "esparcidor, juego de guías (PTFE y UHMW-PE) y labios de los faldones de sellado.", (26, yfin - 5.0), 1.8, "TOP_LEFT")

    # ---------------- columna derecha
    subtitulo(msp, "5. MOTORES DEL TGF (sin cambios)", 196.1, 269.0, 2.5)
    y = tabla_ajustada(msp, 196.1, 267.0, [11.2, 47.9, 11.9, 12.0, 15.7, 16.2], T5, h_fila=3.1,
                       alin=["L", "L", "R", "R", "C", "C"], negrita_ultima=True, sombras={17: (244, 244, 244)})
    subtitulo(msp, "6. CONSUMOS", 196.1, y - 5.4, 2.5)
    y = tabla_ajustada(msp, 196.1, y - 7.2, [47.9, 98.1], T6, h_fila=3.2)
    subtitulo(msp, "7. INSTRUMENTACIÓN (ver P&ID plano 06)", 196.1, y - 5.4, 2.5)
    y = tabla_ajustada(msp, 196.1, y - 7.2, [30.1, 115.9], T7, h_fila=3.2)
    assert y > z["reservado"][3] + 3, (y, z["reservado"])
    exportar_lamina(doc, 22)


if __name__ == "__main__":
    main()
