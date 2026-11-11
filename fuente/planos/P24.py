"""P24 - Ventilación general de la nave: extractores con campana y ventiladores móviles (E10), 1:200.

Geometría: fuente/datos/layout_planta.json (clave G) y bloque E10 de visor.html (Rev. D).
Números de las tablas: fuente/calculos/resultados.json -> ventilacion.
"""
import json
import math
import os

from lamina_secadora import (fuente_pil, COL, FECHA, circulo, exportar_lamina, factor, flecha, lamina, linea,
                             notas, poli, rect, relleno, relleno_circulo, relleno_rect, t, tabla,
                             tn)
from lamina_a3 import cota

AQUI = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(AQUI, "..", "datos", "layout_planta.json"), encoding="utf-8"))["G"]
V = json.load(open(os.path.join(AQUI, "..", "calculos", "resultados.json"), encoding="utf-8"))["ventilacion"]

K = factor("1:200")          # mm de papel por mm real
M = K * 1000.0               # mm de papel por metro real (5 mm)
OX, OY = 34.0, 147.0         # vértice SO de la nave en la planta

AZUL = COL["azul"]
VERDE = COL["aire_agotado"]


def miles(x, d=0):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def P(x, y):
    """Coordenadas de la nave (m) -> papel (mm) en la planta."""
    return (OX + x * M, OY + y * M)


def rect_m(x0, y0, x1, y1, capa="CONTORNO", color=None, lw=None, fill=None, tipo=None):
    a, b = P(x0, y0), P(x1, y1)
    if fill:
        relleno_rect(None or MSP, a[0], a[1], b[0], b[1], fill)
    return rect(MSP, a[0], a[1], b[0], b[1], capa, color, lw, tipo)


def circ_m(x, y, r, fill=None, capa="CONTORNO", color=None, lw=None):
    c = P(x, y)
    if fill:
        relleno_circulo(MSP, c, r * M, fill)
    return circulo(MSP, c, r * M, capa, color, lw)


# ---------------------------------------------------------------- helpers propios de la lámina

def ancho_texto(texto, h, negrita=True):
    """Ancho real (mm) de un texto Arial de altura h (altura de mayúscula = h)."""
    return fuente_pil(negrita).getlength(texto) / 1000.0 * h / 0.716


def titulo(msp, texto, x, y, h=3.5):
    """Título de vista en negrita con subrayado doble del largo real del texto."""
    tn(msp, texto, (x, y), h, "BOTTOM_LEFT")
    largo = ancho_texto(texto, h)
    linea(msp, (x, y - 1.0), (x + largo, y - 1.0), "CONTORNO")
    linea(msp, (x, y - 1.8), (x + largo, y - 1.8), "FINO")


def globo2(msp, etiqueta, centro, apunta_a=None, radio=2.6, h=None, relleno_rgb=(255, 255, 255)):
    """Globo de referencia con el texto ajustado al diámetro."""
    h = h or min(radio * 0.95, 1.55 * radio / max(ancho_texto(etiqueta, 1.0), 0.1))
    if relleno_rgb:
        relleno_circulo(msp, centro, radio, relleno_rgb)
    circulo(msp, centro, radio, "COTAS")
    tn(msp, etiqueta, centro, h, "MIDDLE_CENTER", capa="COTAS")
    if apunta_a:
        dx, dy = apunta_a[0] - centro[0], apunta_a[1] - centro[1]
        d = math.hypot(dx, dy)
        if d > radio:
            linea(msp, (centro[0] + dx / d * radio, centro[1] + dy / d * radio), apunta_a, "COTAS")
            p = msp.add_hatch(dxfattribs={"layer": "COTAS"})
            p.paths.add_edge_path().add_arc(apunta_a, 0.55, 0, 360)


def trazos(msp, pts, capa="OCULTAS", color=None, lw=None, largo=1.6, hueco=0.9):
    """Línea de trazos explícita (el PDF no aplica tipos de línea): cada trazo es una LINE."""
    resto, dibujar = largo, True
    for a, b in zip(pts[:-1], pts[1:]):
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        if d == 0:
            continue
        ux, uy = (b[0] - a[0]) / d, (b[1] - a[1]) / d
        s0 = 0.0
        while s0 < d:
            s1 = min(d, s0 + resto)
            if dibujar:
                linea(msp, (a[0] + ux * s0, a[1] + uy * s0), (a[0] + ux * s1, a[1] + uy * s1), capa, color, lw)
            resto -= s1 - s0
            s0 = s1
            if resto <= 1e-9:
                dibujar = not dibujar
                resto = largo if dibujar else hueco


MSP = None


def planta(msp):
    nave = G["nave"]
    L, A = nave["L"], nave["A"]
    # ---- zonas (rellenos primero)
    rect_m(0, 0, 9.5, 18, "FINO", fill=COL["zona_recepcion"])
    rect_m(26, 0, 33, 9, "FINO", fill=COL["zona_recepcion"])
    rect_m(26, 9, 33, 18, "FINO", fill=(228, 233, 238))
    for lo in G["locales"]:
        rect_m(lo["x0"], lo["y0"], lo["x1"], lo["y1"], "FINO", fill=(248, 248, 248))
        tn(msp, str(lo["n"]), P((lo["x0"] + lo["x1"]) / 2, 2.4), 2.2, "MIDDLE_CENTER")
    # pila de guano (E3) y pila de producto seco
    pg, ps = G["pila_guano"], G["pila_seca"]
    circ_m(pg["x"], pg["y"], pg["r"], fill=(210, 180, 140), capa="FINO")
    circ_m(ps["x"], ps["y"], ps["r"], fill=(222, 200, 160), capa="FINO")
    # muro de contención de la recepción
    linea(msp, P(9.5, G["muro_contencion"]["y0"]), P(9.5, 18), "CONTORNO", lw=50)
    # cinta, tolva, secador, sinfín y elevador
    ci, tv, se = G["cinta"], G["tolva"], G["secador"]
    rect_m(ci["x_cola"], ci["y"] - 0.4, ci["x_cabeza"] + 0.2, ci["y"] + 0.4, "FINO", fill=(232, 224, 212))
    rect_m(tv["x0"], tv["y0"], tv["x1"], tv["y1"], "CONTORNO", fill=(215, 197, 165))
    rect_m(se["x0"], se["y0"], se["x0"] + se["L"], se["y0"] + se["A"], "CONTORNO", fill=(243, 243, 243))
    for yy in (se["y0"] + 0.3, se["y0"] + se["A"] - 0.3):
        trazos(msp, [P(se["x0"] + 0.3, yy), P(se["x0"] + se["L"] - 0.3, yy)], color=(90, 90, 90))
    sd, el = G["sinfin_desc"], G["elevador"]
    rect_m(sd["x0"], sd["y"] - 0.08, sd["x1"] - 0.45, sd["y"] + 0.08, "FINO", fill=(225, 225, 225))
    rect_m(el["x"] - 0.45, el["y"] - 0.5, el["x"] + 0.45, el["y"] + 0.5, "CONTORNO", fill=(200, 200, 200))
    # ductos: aire agotado al ciclón (verde) y aire caliente desde el anexo (rojo)
    rect_m(14.1, 9.3, 14.9, 20.2, "FINO", color=VERDE, fill=(234, 244, 236))
    dc = G["ducto_caliente"]
    rect_m(dc["x0"], 11.2, dc["x1"], 18.0, "FINO", color=COL["aire_caliente"], fill=(248, 222, 222))

    # ---- exterior Norte: ciclón, lavador, tanque, extractor, anexo y silo
    cy, sc, tq, ex = G["ciclon"], G["scrubber"], G["tanque_sol"], G["extractor"]
    circ_m(cy["x"], cy["y"], cy["D"] / 2, fill=(236, 241, 241))
    circ_m(sc["x"], sc["y"], sc["D"] / 2, fill=(228, 238, 226))
    circ_m(tq["x"], tq["y"], tq["D"] / 2, fill=(222, 232, 242))
    circ_m(ex["x"], ex["y"], 0.62, fill=(255, 255, 255))
    circ_m(ex["chim_x"], ex["chim_y"], ex["chim_D"] / 2, fill=(165, 165, 165))
    an = G["anexo"]
    rect_m(an["x0"], an["y0"], an["x1"], an["y1"], "CONTORNO", fill=(240, 224, 214), lw=70)
    ic, ho = an["intercambiador"], an["hogar"]
    rect_m(ic["x0"], ic["y0"], ic["x1"], ic["y1"], "FINO", fill=(226, 226, 226))
    rect_m(ho["x0"], ho["y0"], ho["x1"], ho["y1"], "CONTORNO", fill=(225, 165, 120))
    for v in an["ventiladores"]:
        circ_m(v["x"], v["y"], 0.6, fill=(255, 255, 255))
    ch = an["ciclon_humos"]
    circ_m(ch["x"], ch["y"], ch["D"] / 2, capa="FINO")
    cz = an["cenizas"]
    rect_m(cz["x"] - 0.5, cz["y"] - 0.5, cz["x"] + 0.5, cz["y"] + 0.5, "FINO")
    chm = an["chimenea"]
    circ_m(chm["x"], chm["y"], chm["D"] / 2, fill=(165, 165, 165))
    si = G["silo"]
    circ_m(si["x"], si["y"], si["D"] / 2, fill=(230, 230, 230))
    linea(msp, P(ho["x1"], si["y"]), P(si["x"], si["y"]), "FINO")

    # ---- muros de la nave con aberturas
    lw = 100
    tramos = {
        "S": [(0, 19), (20, 28), (32, 33)],          # PP1 19-20, P2 28-32
        "N": [(0, 26.2), (27.2, 33)],                 # PC1 RF-60 al anexo
        "O": [(0, 2.0), (3.2, 12.6), (16.6, 18)],     # SE2 y portón P1
        "E": [(0, 12.4), (14.9, 15.0), (16.2, 18)],   # portón P3 y SE1
    }
    for a, b in tramos["S"]:
        linea(msp, P(a, 0), P(b, 0), lw=lw)
    for a, b in tramos["N"]:
        linea(msp, P(a, A), P(b, A), lw=lw)
    for a, b in tramos["O"]:
        linea(msp, P(0, a), P(0, b), lw=lw)
    for a, b in tramos["E"]:
        linea(msp, P(L, a), P(L, b), lw=lw)
    for x in nave["porticos"]:
        for y in (0, A):
            c = P(x, y)
            relleno_rect(msp, c[0] - 0.8, c[1] - 0.8, c[0] + 0.8, c[1] + 0.8, (0, 0, 0))

    # ---- termostato TH en el muro Este
    th = P(32.9, 7.32)
    relleno_rect(msp, th[0] - 0.5, th[1] - 0.7, th[0] + 0.3, th[1] + 0.7, (255, 255, 255))
    rect(msp, th[0] - 0.5, th[1] - 0.7, th[0] + 0.3, th[1] + 0.7, "FINO")
    tn(msp, "TH", (th[0] - 1.5, th[1]), 1.8, "MIDDLE_RIGHT")

    # ---- extractores EX1, EX2 (marco 1,40 m + campana) en el muro Este
    for i, yc in enumerate((4.6, 9.9), start=1):
        relleno(msp, [P(33.0, yc - 0.7), P(33.35, yc - 0.7), P(33.35, yc + 0.7), P(33.0, yc + 0.7)], (160, 175, 190))
        rect_m(33.0, yc - 0.7, 33.35, yc + 0.7, "FINO")
        cono = [P(33.35, yc - 0.6), P(34.35, yc - 0.86), P(34.35, yc + 0.86), P(33.35, yc + 0.6)]
        relleno(msp, cono, (215, 220, 225))
        poli(msp, cono, "CONTORNO", cerrada=True)
        flecha(msp, P(34.45, yc), P(35.6, yc), "CONTORNO", color=VERDE, tam=1.8, lw=50)
        globo2(msp, f"EX{i}", P(31.2, yc + 1.5), apunta_a=P(34.0, yc), radio=2.5)
    t(msp, "salida", P(33.2, 12.1), 1.8, "BOTTOM_LEFT", color=VERDE)

    # ---- ventiladores móviles VM1, VM2
    for tag, (x, y), gl in (("VM1", (24.6, 14.0), (26.6, 15.6)), ("VM2", (6.0, 5.5), (8.0, 7.1))):
        rect_m(x - 0.65, y - 0.25, x + 0.65, y + 0.25, "FINO", fill=(205, 214, 222))
        globo2(msp, tag, P(*gl), apunta_a=P(x, y), radio=2.5)
    # campana de la recepción E3
    globo2(msp, "E3", P(pg["x"], 17.0), apunta_a=P(pg["x"], pg["y"]), radio=2.3, relleno_rgb=(255, 243, 190))

    # ---- barrido de aire: entra por el Oeste, sale por el Este
    for y in (15.5, 9.3, 3.5):
        flecha(msp, P(-2.6, y), P(0.5, y), "CONTORNO", color=AZUL, tam=1.8, lw=35)
    t(msp, "entrada\nde aire", P(-2.6, 17.9), 1.8, "BOTTOM_LEFT", color=AZUL)
    for y in (13.0, 7.5, 3.0):
        flecha(msp, P(10.0, y), P(31.5, y), "CONTORNO", color=AZUL, tam=1.8, lw=25)

    # ---- notas de la planta
    notas(msp, [
        "EX1, EX2: extractores Campagnoni AirTEC 1215 con campana (cono) de descarga, a +4,60 / +6,00 m en el muro Este.",
        "VM1, VM2: ventiladores móviles 50\" (confort de los operarios, no cuentan como renovación).",
        "E3: campana de captación de la recepción (existente Rev. D) · TH: termostato de comando EX1/EX2.",
        "El aire entra por el portón P1 y las aberturas del Oeste y sale por el muro Este, barriendo la nave a lo largo.",
        "EX1, EX2 (M36, M37) y VM1, VM2 (M38, M39) se alimentan desde el TS-VEN (circuito Q27 del TG2, plano 23).",
    ], 30, 137.5, altura=1.8, interlineado=1.6)


def elevacion(msp):
    """Muro Este visto desde afuera: el Sur queda a la izquierda."""
    x0, y0 = 40.0, 65.0
    E = lambda y, z: (x0 + y * M, y0 + z * M)
    nave = G["nave"]
    A = nave["A"]
    contorno = [E(0, 0), E(0, nave["h_alero"]), E(A / 2, nave["h_cumbrera"]), E(A, nave["h_alero"]), E(A, 0)]
    relleno(msp, contorno, (242, 242, 238))
    poli(msp, contorno, "CONTORNO", lw=50)
    linea(msp, (x0 - 3.5, y0), (x0 + A * M + 1.5, y0), "CONTORNO", lw=50)
    # portón P3 y salida de emergencia SE1
    for (a, b, h, tag, arriba) in ((12.4, 14.9, 3.1, "P3", False), (15.0, 16.2, 2.1, "SE1", True)):
        p, q = E(a, 0), E(b, h)
        relleno_rect(msp, p[0], p[1], q[0], q[1], (228, 228, 228))
        rect(msp, p[0], p[1], q[0], q[1], "CONTORNO")
        if arriba:
            t(msp, tag, ((p[0] + q[0]) / 2, q[1] + 0.8), 1.8, "BOTTOM_CENTER")
        else:
            t(msp, tag, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2), 1.8, "MIDDLE_CENTER")
    # extractores: marco 1,40 × 1,40, campana Ø1,72 y maza
    for i, yc in enumerate((4.6, 9.9), start=1):
        c = E(yc, 5.3)
        relleno_rect(msp, c[0] - 3.5, c[1] - 3.5, c[0] + 3.5, c[1] + 3.5, (60, 60, 60))
        relleno_circulo(msp, c, 0.86 * M, (215, 220, 225))
        circulo(msp, c, 0.86 * M, "CONTORNO", lw=50)
        relleno_circulo(msp, c, 0.32 * M, (85, 100, 98))
        circulo(msp, c, 0.32 * M, "CONTORNO")
        tn(msp, f"EX{i}", (c[0], c[1] + 6.2), 1.8, "BOTTOM_CENTER")
    # cotas de altura del marco (en m)
    xc = x0 + A * M + 6.0
    cota(msp, (xc, y0), (xc, y0 + 4.6 * M), distancia=0, escala=K, valor="4,60")
    cota(msp, (xc + 4.0, y0 + 4.6 * M), (xc + 4.0, y0 + 6.0 * M), distancia=0, escala=K, valor="1,40")
    linea(msp, E(A, 4.6), (xc + 5.0, y0 + 4.6 * M), "FINO")
    linea(msp, E(A, 6.0), (xc + 5.0, y0 + 6.0 * M), "FINO")


def tablas(msp):
    x = 214.0
    h, a = 3.3, 1.8
    Vv = V
    # 1. volumen
    y = tabla(msp, x, 263.0, [104, 70], [
        ["1. Volumen de la nave", "Valor"],
        ["Largo × ancho × altura al alero: 33 × 18 × 7,00 m", f"{miles(Vv['V_nave'])} m³"],
        ["Techo a dos aguas: ½ × 18 × 1,35 × 33", f"{miles(Vv['V_techo'])} m³"],
        ["Volumen total V", f"{miles(Vv['V'])} m³"],
    ], h_fila=h, altura=a, alin=["L", "R"], negrita_ultima=True)
    # 2. renovaciones
    y = tabla(msp, x, y - 4.0, [74, 34, 66], [
        ["2. Caudal por renovaciones (Q = V × N)", "N (R/H)", "Q"],
        ["Invierno: ventilación mínima", str(Vv["n_inv"]), f"{miles(Vv['Q_inv'])} m³/h"],
        ["Verano: calor, olor, amoníaco y polvo", str(Vv["n_ver"]), f"{miles(Vv['Q_ver'])} m³/h"],
    ], h_fila=h, altura=a, alin=["L", "C", "R"])
    # 3. balance térmico
    filas = [["3. Balance térmico de verano (comprobación)", "kW"]]
    for nom, kw in Vv["cargas"].items():
        filas.append([nom.replace("→", "→"), miles(kw, 1)])
    filas.append(["Total H → Q = H / (ρ·cp·ΔT), ΔT = 3 °C, 35 °C exterior",
                  f"{miles(Vv['H_kW'], 1)} → {miles(Vv['Q_termico'])} m³/h"])
    y = tabla(msp, x, y - 4.0, [130, 44], filas, h_fila=h, altura=a, alin=["L", "R"], negrita_ultima=True)
    # 4. selección (Rev. E: alimentación desde el TS-VEN)
    y = tabla(msp, x, y - 4.0, [104, 70], [
        ["4. Selección", "Valor"],
        ["Caudal de diseño (manda el método 1)", f"{miles(Vv['Q_ex'])} m³/h"],
        [f"EX1, EX2: AirTEC 1215 con campana, {miles(Vv['Q_ex'])} m³/h c/u", f"{miles(Vv['Q_ex'] * Vv['n_ex'])} m³/h"],
        [f"Real: curva AirTEC (pmáx 24 Pa) → {round(Vv['punto']['frac_calc'] * 100, 1):.1f} %; se adopta 85 %".replace(".", ","),
         f"≈ {miles(round(Vv['Q_real'], -3))} m³/h ({round(Vv['ren_real']):d} R/H)"],
        ["Con un solo extractor (invierno o falla)",
         f"≈ {miles(round(Vv['Q_un_extractor'], -2))} m³/h ({round(Vv['ren_un_extractor']):d} R/H)"],
        ["Potencia EX1 + EX2 (1,5 HP trifásico c/u)", f"{miles(Vv['P_ex_kW'], 1)} kW · TG2, Q27 TS-VEN (plano 23)"],
        ["Tomas de aire necesarias (a 2 m/s)", "≈ 15 m² (P1 + aberturas)"],
        ["VM1, VM2 ventiladores móviles 50\" (1 HP c/u)", "51.480 m³/h c/u"],
        ["VM1, VM2 alimentación", "tomas 2P+T 16 A del TS-VEN (0,75 kW c/u)"],
    ], h_fila=h, altura=a, alin=["L", "R"])
    # 5. por qué cada equipo
    y = tabla(msp, x, y - 4.0, [44, 130], [
        ["5. Por qué cada equipo", ""],
        ["AirTEC 1215", "mucho caudal con poca potencia; persianas que se cierran solas; hecho para galpones con amoníaco y polvo"],
        ["Campana (cono)", "recupera presión a la salida: pierde menos caudal con persianas y tomas, menos kWh por m³"],
        ["Ventilador móvil 50\"", "mueve el aire en el puesto de trabajo (recepción, zaranda); refresca al operario"],
        ["Campana E3", "capta el olor en la recepción y lo manda al biofiltro (6.000 m³/h, existente)"],
    ], h_fila=h, altura=a)
    # 6. dónde comprar
    tabla(msp, x, y - 4.0, [44, 130], [
        ["6. Dónde comprar (Argentina)", ""],
        ["Campagnoni", "fábrica en el Parque Industrial de Crespo · campagnoni.com.ar/ventilacion · tienda MercadoLibre"],
        ["Grantec", "extractor 50\" de cono con persiana (alternativa con cono de fábrica) · grantecsa.com"],
        ["Atenas Ventilación", "extractores avícolas 120 cm 380 V · atenasventilacion.com.ar"],
        ["Agrofy", "extractores 50\" 1,5 CV (Colón, Entre Ríos) · agrofy.com.ar"],
    ], h_fila=h, altura=a)


def main():
    global MSP
    revs = [("D", "09/2026", "Emisión orig.: extractores Campagnoni AirTEC 1215 c/ campana y vent. móviles 50\""),
            ("E", "10/2026", "Extractores en circuito Q27 TS-VEN del TG2 (plano 23); VM en tomas 2P+T"),
            ("F", FECHA, "Punto de funcionamiento calculado con la curva de catálogo (el 85 % deja de ser supuesto)")]
    doc, msp, z = lamina(24, "VENTILACIÓN GENERAL DE LA NAVE\nEXTRACTORES Y VENTILADORES", "1:200", revs)
    MSP = msp
    titulo(msp, "VENTILACIÓN GENERAL DE LA NAVE: EXTRACTORES CON CAMPANA Y VENTILADORES MÓVILES - ESC. 1:200",
                 26, 277.5, 3.4)
    titulo(msp, "A - PLANTA DE LA NAVE - ESC. 1:200", 26, 267.5, 2.6)
    planta(msp)
    titulo(msp, "B - ELEVACIÓN MURO ESTE (VISTA DESDE AFUERA) - ESC. 1:200", 26, 113.5, 2.6)
    elevacion(msp)
    tablas(msp)
    exportar_lamina(doc, 24)


if __name__ == "__main__":
    main()
