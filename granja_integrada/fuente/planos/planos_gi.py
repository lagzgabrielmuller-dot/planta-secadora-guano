"""Láminas GI de la granja integrada (A3 IRAM, DXF + PDF vectorial + PNG).

    python planos_gi.py            # todas
    python planos_gi.py 1 4 12     # algunas

Todo sale de los datos del proyecto (datos/granja.json, calculos.json, electrica.json) y de las mismas funciones
con que se arma el 3D, así planos, modelo y memoria dicen lo mismo.
"""
from __future__ import annotations

import math
import sys
import zipfile

from lamina_gi import (C, CARPETA, D, E, K, TOTAL, Vista, arco, caja_texto, circulo, cota_h, cota_v, escala_grafica, exportar,
                       flecha, flecha_poli, fmt, globo, hoja, imagen, linea, nivel, norte, notas, poli, rayado, rect,
                       relleno, relleno_circulo, relleno_rect, subtitulo, suelo, t, tabla, titulo_vista, tn, unir_pdfs)

sys.path.insert(0, str(CARPETA.parent / "fuente" / "modelo"))
import galpon as GP  # noqa: E402

TR = {x["id"]: x for x in D["transporte"]}
GAL = {g["id"]: g for g in D["galpones"]}
LAMINAS = {}


def lamina(n):
    def deco(f):
        LAMINAS[n] = f
        return f
    return deco


def trazado(c):
    return c.get("trazado") or [c["p0"], c["p1"]]


def rutas_huevos():
    """Recorrido en planta de las cintas de huevos de cada galpón a su estación de armado (igual que galpon.py)."""
    out = []
    for dep in D["depositos"]:
        x0, x1, y0, y1 = (dep[k] for k in ("x0", "x1", "y0", "y1"))
        xm = (x0 + x1) / 2
        sx = 1 if dep["lado"] == "O" else -1
        yi = y1 - D["deposito"]["e_muro"]
        x_muro = x0 if sx > 0 else x1
        orden = sorted(dep["galpones"], key=lambda g: abs(GAL[g]["x"] - xm), reverse=True)
        for gid, est in zip(orden, ("E1", "E2")):
            g = GAL[gid]
            lado_dep = 1 if xm > g["x"] else -1
            x_sal = g["x"] + lado_dep * 4.6
            y_est = yi - GP.SJ[est] / 1000
            x_est = xm + sx * GP.SJ["l_est"] / 1000
            x_carril = x_muro - sx * (1.4 if est == "E1" else 2.95)
            if est == "E1":
                pts = [(x_sal, g["y1"] + 0.3), (x_sal, y_est), (x_muro, y_est), (x_est - sx * 0.6, y_est)]
            else:
                pts = [(x_sal, g["y1"] + 0.3), (x_sal, g["y1"] + 2.0), (x_carril, g["y1"] + 2.0), (x_carril, y_est),
                       (x_muro, y_est), (x_est - sx * 0.6, y_est)]
            out.append((gid, pts))
    return out


def leyenda(msp, x, y, items, ancho=7.0, h=4.2, alto_txt=2.0):
    """Referencias: (tipo, rgb o None, texto); tipo 'r' recuadro lleno, 'l' línea, 'c' círculo, 'd' recuadro de trazos."""
    for tipo, rgb, txt in items:
        if tipo == "r":
            relleno_rect(msp, x, y - 1.6, x + ancho, y + 1.6, rgb)
            rect(msp, x, y - 1.6, x + ancho, y + 1.6, "FINO")
        elif tipo == "l":
            linea(msp, (x, y), (x + ancho, y), "CONTORNO", color=rgb, lw=60)
        elif tipo == "c":
            relleno_circulo(msp, (x + ancho / 2, y), 1.4, rgb)
            circulo(msp, (x + ancho / 2, y), 1.4, "FINO")
        elif tipo == "d":
            rect(msp, x, y - 1.6, x + ancho, y + 1.6, "OCULTAS", color=rgb)
        t(msp, txt, (x + ancho + 2.0, y), alto_txt, "MIDDLE_LEFT")
        y -= h
    return y


# ===================================================================================== GI-01 implantación
@lamina(1)
def gi01():
    doc, msp, z = hoja(1, "IMPLANTACIÓN GENERAL\nDE LA GRANJA", "1:1500")
    v = Vista(27.0, 58.0, -125.0, -88.0, 1500)
    pr, ac = D["predio"], D["acceso"]
    titulo_vista(msp, "PLANTA GENERAL - ESC. 1:1500", 27, 274)
    # calle pública
    c = D["calle"]
    v.relleno_rect(msp, -125, c["y0"], 160, c["y1"], C["pavimento"])
    t(msp, c["nom"], v(105, (c["y0"] + c["y1"]) / 2), 1.9, "MIDDLE_CENTER")
    # zona limpia (todo el predio) y zona sucia (cerco sanitario de la planta)
    v.relleno_rect(msp, pr["x0"], pr["y0"], pr["x1"], pr["y1"], C["limpia"])
    zs = (-21.0, 54.0, -23.0, 40.0)
    v.relleno_rect(msp, zs[0], zs[2], zs[1], zs[3], C["sucia"])
    for cm in D["caminos"]:
        v.relleno_rect(msp, cm["x0"], cm["y0"], cm["x1"], cm["y1"], C["camino"])
        v.rect(msp, cm["x0"], cm["y0"], cm["x1"], cm["y1"], "FINO")
    for p in D["playones"]:
        v.relleno_rect(msp, p["x0"], p["y0"], p["x1"], p["y1"], C["pavimento"])
        v.rect(msp, p["x0"], p["y0"], p["x1"], p["y1"], "FINO")
    # cerco perimetral con portón y cerco sanitario
    hueco = (ac["porton"]["x0"], ac["porton"]["x1"])
    bio = (ac["bioseguridad"]["x0"], ac["bioseguridad"]["x1"])
    for a, b in (((pr["x0"], pr["y0"]), (hueco[0], pr["y0"])), ((hueco[1], pr["y0"]), (bio[0], pr["y0"])),
                 ((bio[1], pr["y0"]), (pr["x1"], pr["y0"])), ((pr["x1"], pr["y0"]), (pr["x1"], pr["y1"])),
                 ((pr["x1"], pr["y1"]), (pr["x0"], pr["y1"])), ((pr["x0"], pr["y1"]), (pr["x0"], pr["y0"]))):
        linea(msp, v(*a), v(*b), "CONTORNO", color=(47, 93, 47), lw=50)
    c1 = next(cm for cm in D["caminos"] if cm["id"] == "C1")
    for a, b in (((zs[0], zs[2]), (c1["x0"], zs[2])), ((c1["x1"], zs[2]), (zs[1], zs[2])), ((zs[1], zs[2]), (zs[1], zs[3])),
                 ((zs[1], zs[3]), (zs[0], zs[3])), ((zs[0], zs[3]), (zs[0], zs[2]))):
        e_ = linea(msp, v(*a), v(*b), "CONTORNO", color=(138, 90, 36), lw=35)
        e_.dxf.linetype = "DASHDOT" if "DASHDOT" in doc.linetypes else "DASHED"
    # forestación (cortina de casuarinas, igual que el 3D)
    arboles = [(x, pr["y1"] - 8) for x in _rango(pr["x0"] + 8, pr["x1"] - 7, 7)]
    for y in _rango(pr["y0"] + 30, pr["y1"] - 7, 7):
        arboles += [(pr["x0"] + 8, y), (pr["x1"] - 8, y)]
    for p in arboles:
        relleno_circulo(msp, v(*p), v.L(2.2), C["arbol"])
    # ampliación futura
    g1 = D["galpones"][0]
    for a in D["ampliacion"]:
        x0, x1 = a["x"] - D["galpon"]["A"] / 2, a["x"] + D["galpon"]["A"] / 2
        v.rect(msp, x0, g1["y0"], x1, g1["y1"], "OCULTAS", color=C["ampl"])
        t(msp, a["id"], v(a["x"], 72), 2.0, "MIDDLE_CENTER", rotacion=90, color=C["ampl"])
    # galpones con sus filas de jaulas
    for g in D["galpones"]:
        v.relleno_rect(msp, g["x0"], g["y0"], g["x1"], g["y1"], C["galpon"])
        for xf in GP.x_filas(g["x"] * 1000):
            a, b = v(xf / 1000, g["y0"] + D["galpon"]["cabecera_guano"]), v(xf / 1000, g["y1"] - D["galpon"]["cabecera_huevos"])
            linea(msp, a, b, "FINO", color=(120, 140, 160))
        v.rect(msp, g["x0"], g["y0"], g["x1"], g["y1"], "CONTORNO", color=C["galpon_borde"])
        tn(msp, f"{g['id']} · 36.000 gallinas", v(g["x"] - 3.2 * g["hacia_planta"], (g["y0"] + g["y1"]) / 2), 2.2,
           "MIDDLE_CENTER", rotacion=90)
    for s in D["silos_alimento"]:
        relleno_circulo(msp, v(s["x"], s["y"]), v.L(s["D"] / 2), (176, 166, 142))
        circulo(msp, v(s["x"], s["y"]), v.L(s["D"] / 2), "FINO")
    for dpo in D["depositos"]:
        v.relleno_rect(msp, dpo["x0"], dpo["y0"], dpo["x1"], dpo["y1"], C["deposito"])
        v.rect(msp, dpo["x0"], dpo["y0"], dpo["x1"], dpo["y1"], "CONTORNO")
        t(msp, f"{dpo['id']}\nhuevos", v((dpo["x0"] + dpo["x1"]) / 2, (dpo["y0"] + dpo["y1"]) / 2), 1.9, "MIDDLE_CENTER")
    for gid, pts in rutas_huevos():
        v.poli(msp, pts, "CONTORNO", color=(47, 120, 47), lw=30)
    # planta de secado
    p = D["planta"]
    n = p["nave"]
    an = p["anexo"]
    v.relleno_rect(msp, n["x0"], n["y0"], n["x0"] + n["L"], n["y0"] + n["A"], C["planta"])
    v.relleno_rect(msp, an["x0"], an["y0"], an["x1"], an["y1"], (190, 176, 160))
    v.rect(msp, n["x0"], n["y0"], n["x0"] + n["L"], n["y0"] + n["A"], "CONTORNO")
    v.rect(msp, an["x0"], an["y0"], an["x1"], an["y1"], "CONTORNO")
    for k_ in ("silo", "ciclon", "scrubber"):
        e_ = p[k_]
        relleno_circulo(msp, v(e_["x"], e_["y"]), v.L(e_["D"] / 2), (160, 160, 160))
        circulo(msp, v(e_["x"], e_["y"]), v.L(e_["D"] / 2), "FINO")
    tp = D["tolva_pulmon"]
    v.relleno_rect(msp, tp["x0"], tp["y0"], tp["x1"], tp["y1"], C["tp"])
    tn(msp, "PLANTA DE SECADO", v(16.5, 9.0), 2.0, "MIDDLE_CENTER")
    # transporte de guano
    for tr in D["transporte"]:
        pts = [(q[0], q[1]) for q in trazado(tr)]
        col = C["transporte"] if tr["tipo"] in ("principal", "interior", "exterior", "colectora") else C["inclinada"]
        v.poli(msp, pts, "CONTORNO", color=col, lw=70 if tr["id"][:2] in ("CE", "CP") else 45)
    for tt in D["torres"]:
        v.relleno_rect(msp, tt["x"] - tt["A"] / 2, tt["y"] - tt["B"] / 2, tt["x"] + tt["A"] / 2, tt["y"] + tt["B"] / 2, C["torre"])
        cr = tt["contenedor"]
        v.rect(msp, cr["x"] - cr["A"] / 2, cr["y"] - cr["L"] / 2, cr["x"] + cr["A"] / 2, cr["y"] + cr["L"] / 2, "FINO")
        t(msp, tt["id"], v(tt["x"], tt["y"] + 4.5), 1.8, "BOTTOM_CENTER")
    # accesos y servicios
    for k_, nom in (("garita", "garita"), ("bascula", "báscula"), ("vado", "vado"), ("bioseguridad", "bioseguridad"),
                    ("set", "SET 315 kVA"), ("estacionamiento", "estacionamiento")):
        e_ = ac[k_]
        v.relleno_rect(msp, e_["x0"], e_["y0"], e_["x1"], e_["y1"], (207, 207, 232))
        v.rect(msp, e_["x0"], e_["y0"], e_["x1"], e_["y1"], "FINO")
        pos = v((e_["x0"] + e_["x1"]) / 2, (e_["y0"] + e_["y1"]) / 2)
        if k_ in ("bascula",):
            t(msp, nom, (pos[0] + 3.5, pos[1]), 1.7, "MIDDLE_LEFT")
        elif k_ in ("set", "estacionamiento"):
            t(msp, "SET" if k_ == "set" else nom, pos, 1.3, "MIDDLE_CENTER")
        elif k_ == "bioseguridad":
            t(msp, nom, (pos[0], pos[1] - 3.0), 1.5, "TOP_CENTER")
        else:
            t(msp, nom, (pos[0], pos[1] + 2.5), 1.7, "BOTTOM_CENTER")
    for s in D["servicios"]:
        if s.get("x") is None:
            continue
        if "D" in s:
            relleno_circulo(msp, v(s["x"], s["y"]), v.L(s["D"] / 2), C["agua_c"] if "AGUA" in s["id"] else (150, 130, 110))
        t(msp, s["id"], v(s["x"] + 5, s["y"]), 1.7, "MIDDLE_LEFT")
    # zonas y circulaciones
    t(msp, "ZONA SUCIA (cerco sanitario)", v(16.5, 28.5), 1.7, "MIDDLE_CENTER", color=(138, 90, 36))
    t(msp, "ZONA LIMPIA: galpones, huevos y alimento", v(16.5, 150), 2.2, "MIDDLE_CENTER", color=(47, 93, 47))
    flecha(msp, v(16.5, -95), v(16.5, -72), "CONTORNO", tam=2.0)
    t(msp, "ingreso único", v(19, -93.5), 1.7, "MIDDLE_LEFT")
    # nombres de los caminos (al final, para que no los tapen los árboles)
    pos_c = {"C1": (16.5, -27), "C2": (-16.5, -6), "C3": (49.5, -6), "C4": (-5, 35.5), "C5": (-5, -18.5),
             "C6": (100, -58.5), "C7": (-113, 60), "C8": (146, 60), "C9": (100, 167)}
    for cm in D["caminos"]:
        horiz = (cm["x1"] - cm["x0"]) > (cm["y1"] - cm["y0"])
        t(msp, cm["id"], v(*pos_c.get(cm["id"], ((cm["x0"] + cm["x1"]) / 2, (cm["y0"] + cm["y1"]) / 2))), 1.8,
          "MIDDLE_CENTER", rotacion=0 if horiz else 90)
    norte(msp, 210, 262, 6.0)
    escala_grafica(msp, 30, 40, "1:1500", 50, 10)
    # ---------------------------------------------------------------- columna derecha
    x = 228
    subtitulo(msp, "REFERENCIAS", x, 276)
    leyenda(msp, x, 271, [
        ("r", C["galpon"], "Galpón de ponedoras (jaulas en 4 filas × 5 pisos)"),
        ("r", C["deposito"], "Depósito de huevos (estaciones de armado y almacén)"),
        ("r", C["planta"], "Planta de secado de guano (nave de la Rev. F)"),
        ("r", C["tp"], "Tolva pulmón TP-01 (recepción automática)"),
        ("r", C["limpia"], "Zona limpia (huevos, alimento y personal)"),
        ("r", C["sucia"], "Zona sucia: planta, dentro del cerco sanitario"),
        ("r", C["camino"], "Caminos internos y playones"),
        ("l", C["transporte"], "Cintas colectoras CE y principales CP (en galería)"),
        ("l", C["inclinada"], "Cintas transversales CT e inclinadas CI"),
        ("r", C["torre"], "Torre de transferencia con desviadora"),
        ("l", (47, 120, 47), "Cintas de huevos a los depósitos"),
        ("c", C["arbol"], "Cortina forestal de casuarinas"),
        ("d", C["ampl"], "Ampliación futura (G0 y G5)"),
    ])
    filas = [["Edificio", "Medidas (m)", "Sup. (m²)"]]
    ga = D["galpon"]
    filas.append(["Galpones G1 a G4 (×4)", f"{fmt(ga['L'], 0)} × {fmt(ga['A'], 1)}", fmt(4 * ga["L"] * ga["A"], 0)])
    dpo = D["depositos"][0]
    dl, da = dpo["x1"] - dpo["x0"], dpo["y1"] - dpo["y0"]
    filas.append(["Depósitos DH-O y DH-E (×2)", f"{fmt(dl, 1)} × {fmt(da, 1)}", fmt(2 * dl * da, 0)])
    filas.append(["Nave de proceso (Rev. F)", f"{fmt(n['L'], 0)} × {fmt(n['A'], 0)}", fmt(n["L"] * n["A"], 0)])
    filas.append(["Anexo del hogar", f"{fmt(an['x1'] - an['x0'], 1)} × {fmt(an['y1'] - an['y0'], 1)}",
                  fmt((an["x1"] - an["x0"]) * (an["y1"] - an["y0"]), 0)])
    filas.append(["Torres TT-O y TT-E (×2)", "3,2 × 3,2", fmt(2 * 3.2 * 3.2, 1)])
    b = ac["bioseguridad"]
    filas.append(["Bioseguridad (vestuarios)", f"{fmt(b['x1'] - b['x0'], 0)} × {fmt(b['y1'] - b['y0'], 0)}",
                  fmt((b["x1"] - b["x0"]) * (b["y1"] - b["y0"]), 0)])
    filas.append(["Predio dentro del cerco", f"{fmt(pr['x1'] - pr['x0'], 0)} × {fmt(pr['y1'] - pr['y0'], 1)}",
                  fmt((pr["x1"] - pr["x0"]) * (pr["y1"] - pr["y0"]), 0)])
    subtitulo(msp, "EDIFICIOS Y SUPERFICIES", x, 212)
    yb = tabla(msp, x, 209, [78, 52, 47], filas, h_fila=4.6, altura=2.1, alin=["L", "C", "R"])
    B = K["balance"]
    subtitulo(msp, "DATOS DE LA GRANJA", x, yb - 7)
    yb = tabla(msp, x, yb - 10, [118, 59], [
        ["Dato", "Valor"],
        ["Gallinas (4 galpones)", f"{fmt(B['aves_total'], 0)}"],
        ["Guano fresco (72 % de humedad)", f"{fmt(B['guano_total_kg_dia'] / 1000, 1)} t/día"],
        ["Producto seco (15 % de humedad)", f"{fmt(B['producto_seco_kg_dia'] / 1000, 1)} t/día"],
        ["Huevos", f"{fmt(B['huevos_dia'], 0)} por día"],
        ["Reserva de la tolva pulmón TP-01", f"{fmt(B['tolva_pulmon_dias'], 1)} días"],
    ], h_fila=4.6, altura=2.1, alin=["L", "R"])
    notas(msp, ["1. Coordenadas en m; origen en el vértice Sudoeste de la nave (igual que la Rev. F).",
                "2. Fila de Oeste a Este: G1, G2, planta, G3, G4; las cabeceras de guano miran al Sur.",
                "3. Cerco a ≥ 50 m de los galpones (verificar con la Res. SENASA 1699/2019).",
                "4. Subestación y estacionamiento afuera del cerco; ingreso único con vado y duchas."],
          x, yb - 7, altura=2.0, titulo="NOTAS")
    return doc


def _rango(a, b, paso):
    out, v = [], a
    while v < b:
        out.append(v)
        v += paso
    return out


# ===================================================================================== ayudas de cortes
def cd(msp, eje, valor, region, vista, recorte, filtro=None, color=None, lw=None, capa="CONTORNO", mallas=True):
    """Corta el modelo y dibuja: devuelve la cantidad de líneas."""
    import cortes
    segs = cortes.corte(eje, valor, region=region, filtro=filtro, mallas=mallas)
    return cortes.dibujar(msp, segs, vista, capa=capa, color=color, lw=lw, recorte=recorte)


def sin_jaula(i):
    return i["mat"] not in ("gallina", "malla")


def norte_derecha(msp, x, y, r=5.0):
    """Norte hacia la derecha (plantas giradas 90°)."""
    circulo(msp, (x, y), r, "CONTORNO")
    flecha(msp, (x - r * 0.8, y), (x + r * 0.85, y), "CONTORNO", tam=2.6)
    tn(msp, "N", (x + r + 1.5, y), 3.5, "MIDDLE_LEFT")


def etiqueta(msp, texto, punto, pos, h=2.0, alin="MIDDLE_LEFT"):
    """Texto con línea de referencia al punto señalado."""
    linea(msp, punto, pos, "COTAS")
    relleno_circulo(msp, punto, 0.45, (0, 0, 0))
    t(msp, texto, (pos[0] + (1.0 if "LEFT" in alin else -1.0), pos[1]), h, alin)


# ===================================================================================== GI-02 galpón: planta
@lamina(2)
def gi02():
    doc, msp, z = hoja(2, "GALPÓN TIPO G1\nPLANTA Y CABECERA DE GUANO", "1:300 · 1:75")
    g = GAL["G1"]
    ga = D["galpon"]
    # ---------------------------------------------------------------- planta general girada (Norte a la derecha)
    titulo_vista(msp, "PLANTA GENERAL DEL GALPÓN G1 (CORTE A +1,00 m) - ESC. 1:300", 27, 274)
    v = Vista(27.0, 196.0, 14.0, 56.0, 300, eje="yx")
    rec = (25, 405, 190, 268)
    cd(msp, "z", 1.0, (-77, -54.5, 13.5, 127.5, None, None), v, rec, filtro=sin_jaula, mallas=False)
    # cotas y nombres
    y0, y1 = g["y0"], g["y1"]
    a, b = v.p3((g["x1"], y0, 0)), v.p3((g["x1"], y1, 0))
    cota_h(msp, a[0], b[0], 190.5, f"{fmt(ga['L'], 2)} m (largo del galpón)")
    c0, c1 = v.p3((g["x0"], y0 - 3.5, 0)), v.p3((g["x1"], y0 - 3.5, 0))
    cota_v(msp, c0[0], c1[1], c0[1], f"{fmt(ga['A'], 2)} m")
    for k, xf in enumerate(GP.x_filas(g["x"] * 1000)):
        pt = v.p3((xf / 1000, 70.0, 0))
        t(msp, f"FILA {'ABCD'[k]}", (pt[0], pt[1]), 1.8, "MIDDLE_CENTER", fondo=True)
    pa = v.p3((g["x0"], y0 + 1.3, 0))
    etiqueta(msp, "CABECERA DE GUANO (Sur)", pa, (pa[0] + 8, 262.0), 1.8)
    pb = v.p3((g["x0"], y1 - 1.4, 0))
    etiqueta(msp, "CABECERA DE HUEVOS (Norte)", pb, (pb[0] - 40, 262.0), 1.8)
    q = v.p3((g["x"] + 3.1, y1 + 1.5, 0))
    etiqueta(msp, "SALA DE SERVICIO (TS-G1)", q, (q[0] - 30, 200.0), 1.7, "MIDDLE_RIGHT")
    q = v.p3((-61.9, 18.5, 0))
    t(msp, "CI-1 a la\ncolectora CE-O", (q[0], q[1] - 6), 1.6, "TOP_CENTER")
    q = v.p3((-60.63, 24.15, 0))
    etiqueta(msp, "CCM-G1", q, (q[0] + 6, 186.0), 1.8)
    q = v.p3((-74.1, 114.85, 0))
    etiqueta(msp, "silos SA-G1-1/2", q, (q[0] - 14, 270.5), 1.7, "MIDDLE_RIGHT")
    norte_derecha(msp, 392, 276, 4.0)
    # ---------------------------------------------------------------- detalle de la cabecera de guano
    titulo_vista(msp, "DETALLE DE LA CABECERA DE GUANO (VISTA DESDE +3,60 m) - ESC. 1:75", 27, 177, 3.0)
    proy_d, caja_d = vista_img(doc, msp, "T02_cabecera", 28, 80, 75)
    yc0 = g["y0"] + ga["cabecera_guano"]
    refs = [
        ("1", (GP.x_filas(g["x"] * 1000)[0] / 1000 + 0.76, yc0 - 0.15), "Motorreductor de la cinta de piso (20 por galpón, 1,1 kW)"),
        ("2", (-66.5, D["transporte"][0]["p0"][1]), "Canal de H° con la cinta transversal CT-1 (0,55 kW)"),
        ("3", (-61.9, 21.0), "Cinta inclinada CI-1 hacia la colectora CE-O"),
        ("4", (-60.63, 24.15), "CCM-G1 (IP65) con alero, afuera del muro"),
        ("5", (-64.6, g["y0"] + 1.5), "Bandeja de cabecera a +3,45 m"),
        ("6", (-71.5, g["y0"] + 1.95), "Puerta de la cabecera de guano"),
        ("7", (GP.x_filas(g["x"] * 1000)[1] / 1000 + 1.01, yc0 - 0.80), "Botonera de fila con parada de emergencia"),
    ]
    globos_borde(msp, [(n_, (pt[0], pt[1], 0.5)) for n_, pt, txt in refs], proy_d, caja_d, ("abajo",), sep=7.0, radio=2.6, dist=8.0)
    subtitulo(msp, "REFERENCIAS DEL DETALLE", 232, 177)
    yb = tabla(msp, 232, 174, [9, 166], [["N°", "Elemento"]] + [[r[0], r[2]] for r in refs], h_fila=4.3, altura=2.0, alin=["C", "L"])
    # ---------------------------------------------------------------- datos del galpón
    V = K["ventilacion"]
    J = D["jaulas"]
    B = K["balance"]
    subtitulo(msp, "DATOS DEL GALPÓN (SAN JORGE, ADAPTADO)", 232, yb - 7)
    tabla(msp, 232, yb - 10, [112, 63], [
        ["Dato", "Valor"],
        ["Gallinas / jaulas", f"{fmt(J['aves_por_galpon'], 0)} / {fmt(J['aves_por_galpon'] / J['aves_por_celda'], 0)}"],
        ["Filas × pisos × módulos", f"{J['filas']} × {J['pisos']} × {J['modulos_por_fila']}"],
        ["Cinta de guano (ancho, velocidad)", f"{fmt(J['cinta_guano_ancho'], 2)} m · {fmt(J['cinta_guano_v_m_min'], 0)} m/min"],
        ["Guano por día", f"{fmt(B['guano_galpon_kg_dia'] / 1000, 2)} t"],
        ["Ventilación de verano", f"{fmt(V['caudal_verano_m3h'], 0)} m³/h"],
        ["Ventiladores 50\" / 36\"", f"{V['ventiladores_50']} / {V['ventiladores_36']}"],
        ["Velocidad en el túnel", f"{fmt(V['velocidad_tunel_m_s'], 2)} m/s"],
        ["Panel evaporativo", f"{fmt(V['panel_evaporativo_m2'], 1)} m²"],
    ], h_fila=4.3, altura=2.0, alin=["L", "R"])
    return doc


# ===================================================================================== GI-03 galpón: corte transversal
@lamina(3)
def gi03():
    doc, msp, z = hoja(3, "GALPÓN TIPO G1\nCORTE TRANSVERSAL", "1:50")
    g = GAL["G1"]
    ga, J = D["galpon"], D["jaulas"]
    titulo_vista(msp, "CORTE A-A (MÓDULO TÍPICO, MIRANDO AL NORTE) - ESC. 1:50", 27, 274)
    v = Vista(42.0, 100.0, g["x0"], 0.0, 50, eje="xz")
    rec = (27, 300, 85, 262)
    cd(msp, "y", g["y0"] + 30.0, (g["x0"] - 1, g["x1"] + 1, None, None, -1.0, 8.0), v, rec, mallas=False)
    suelo(msp, v(g["x0"] - 0.6, 0)[0], v(g["x1"] + 0.6, 0)[0], v(0, -0.15)[1])
    # cotas horizontales: filas y pasillos
    xs = GP.x_filas(g["x"] * 1000)
    yb = v(0, -0.6)[1]
    bordes = [g["x0"] + ga["e_muro"]]
    for xf in xs:
        bordes += [xf / 1000 - J["ancho_fila"] / 2, xf / 1000 + J["ancho_fila"] / 2]
    bordes.append(g["x1"] - ga["e_muro"])
    for a_, b_ in zip(bordes, bordes[1:]):
        cota_h(msp, v(a_, 0)[0], v(b_, 0)[0], yb - 4, fmt(b_ - a_, 2), h=1.8)
    cota_h(msp, v(g["x0"], 0)[0], v(g["x1"], 0)[0], yb - 11, f"{fmt(ga['A'], 2)} m", h=2.2)
    # niveles
    xn = v(g["x1"] + 0.9, 0)[0]
    hc = ga["h_alero"] + ga["A"] / 2 * math.tan(math.radians(ga["pendiente_deg"]))
    for zz, txt in ((0.0, "±0,00 piso"), (J["z_piso1"], "+0,35 piso 1 de jaulas"),
                    (J["z_piso1"] + 4 * J["paso_pisos"], f"+{fmt(J['z_piso1'] + 4 * J['paso_pisos'], 2)} piso 5"),
                    (ga["h_alero"], f"+{fmt(ga['h_alero'], 2)} alero"), (hc, f"+{fmt(hc, 2)} cumbrera")):
        nivel(msp, xn, v(0, zz)[1], txt)
    # referencias
    xa = xs[0] / 1000
    zt = J["z_piso1"] + 4 * J["paso_pisos"]
    pas = xa + J["ancho_fila"] / 2 + J["pasillo"] / 2            # eje del pasillo entre las filas A y B
    refs = [
        ("1", (xa + 0.30, zt + 0.25), (pas, 3.05), "Jaula de 6 gallinas (0,61 × 0,483 m), 5 pisos"),
        ("2", (xa + 0.45, J["z_piso1"] + 3 * J["paso_pisos"] - 0.03), (pas, 2.25), "Cinta de guano de polipropileno de 1,25 m bajo cada piso"),
        ("3", (xa + 0.62, J["z_piso1"] + 2 * J["paso_pisos"] + 0.06), (pas, 1.45), "Comedero y bandeja de huevos (cinta de huevos de 0,10 m)"),
        ("4", (g["x0"] + 0.08, 3.3), (g["x0"] + 0.55, 3.75), "Muro de panel con correas C 80 y zócalo de H° de 0,50 m"),
        ("5", (g["x"] - 2.0, hc - 0.72), (g["x"] - 2.6, hc + 0.55), "Panel sándwich de techo PIR 50 mm sobre correas C 100"),
        ("6", (g["x"], 2.1), (g["x"] + 0.0, 1.0), "Luminaria LED de pasillo (luz de postura regulable)"),
    ]
    for n_, punto, pos, txt in refs:
        globo(msp, n_, v(*pos), v(*punto), radio=2.6)
    subtitulo(msp, "REFERENCIAS", 305, 274)
    tabla(msp, 305, 271, [9, 91], [["N°", "Elemento"]] + [[r[0], r[3]] for r in refs], h_fila=4.6, altura=1.9, alin=["C", "L"])
    notas(msp, ["1. Corte obtenido del modelo 3D (mismas medidas).",
                "2. Jaulas tipo San Jorge (proveedor del galpón",
                "   existente); medidas a confirmar con el fabricante.",
                "3. Piso con pendiente a los canales de limpieza.",
                "4. Cotas en m."], 305, 228, altura=2.0, titulo="NOTAS")
    return doc


# ===================================================================================== vistas técnicas a escala
IMG = CARPETA / "img_tecnicas"


def _recorte(nombre, margen_px=12):
    """(meta, imagen RGBA, caja de recorte en px) de la vista técnica: lo dibujado más un margen."""
    import json as _json
    from PIL import Image
    meta = _json.loads((IMG / f"{nombre}.json").read_text(encoding="utf-8"))
    im = Image.open(IMG / f"{nombre}.png").convert("RGBA")
    W, H = im.size
    bx0, by0, bx1, by1 = im.getchannel("A").getbbox() or (0, 0, W, H)
    return meta, im, (max(0, bx0 - margen_px), max(0, by0 - margen_px), min(W, bx1 + margen_px), min(H, by1 + margen_px))


def tam_vista(nombre, den, margen_px=12):
    """Ancho y alto en la lámina (mm) de la vista recortada a escala 1:den."""
    meta, im, (bx0, by0, bx1, by1) = _recorte(nombre, margen_px)
    k = meta["ancho_m"] / im.size[0] * 1000.0 / den
    return (bx1 - bx0) * k, (by1 - by0) * k


def vista_img(doc, msp, nombre, x, y, den, margen_px=12, fondo=(255, 255, 255), atenuar=0.0, gris=False):
    """Ubica la vista técnica `nombre` (PNG + JSON de render_tecnico.py) con su esquina inferior izquierda en (x, y), a
    escala 1:den. Recorta lo transparente y la pone sobre fondo blanco. Devuelve (proyector, (x0, y0, x1, y1)): el
    proyector lleva un punto 3D (m) al papel (mm)."""
    from PIL import Image
    meta, im, (bx0, by0, bx1, by1) = _recorte(nombre, margen_px)
    W, H = im.size
    rec = im.crop((bx0, by0, bx1, by1))
    blanco = Image.new("RGB", rec.size, fondo)
    blanco.paste(rec, mask=rec.getchannel("A"))
    sufijo = ""
    if gris:
        blanco = blanco.convert("L").convert("RGB")
        sufijo += "_gris"
    if atenuar:
        blanco = Image.blend(blanco, Image.new("RGB", blanco.size, (255, 255, 255)), atenuar)
        sufijo += f"_{int(atenuar * 100)}"
    destino = CARPETA / "dxf" / "img"
    destino.mkdir(parents=True, exist_ok=True)
    ruta = destino / f"{nombre}{sufijo}.png"
    blanco.save(ruta, optimize=True)
    m_px = meta["ancho_m"] / W
    k = 1000.0 / den
    ancho = (bx1 - bx0) * m_px * k
    alto = (by1 - by0) * m_px * k
    imagen(doc, msp, str(ruta), x, y, ancho, alto, carpeta_planos=str(CARPETA))
    import numpy as _np
    c, der, arr = (_np.array(meta[q], float) for q in ("centro", "derecha", "arriba"))

    def proy(P):
        d = _np.array(P, float) - c
        px = W / 2 + d.dot(der) / m_px
        py = H / 2 - d.dot(arr) / m_px
        return (x + (px - bx0) * m_px * k, y + (by1 - py) * m_px * k)
    return proy, (x, y, x + ancho, y + alto)


def globos_lado(msp, items, proy, caja, lado="izq", sep=7.5, radio=3.0):
    """Globos alineados a un costado de la vista, con su línea al punto 3D de cada ítem (n, punto)."""
    x0, y0, x1, y1 = caja
    pts = sorted(((n, proy(pt)) for n, pt in items), key=lambda r: -r[1][1])
    if not pts:
        return
    ys = []
    for n, (u, v) in pts:
        yy = min(v, ys[-1] - sep) if ys else v
        ys.append(yy)
    # si se pasan del borde de abajo, se corren todos hacia arriba
    falta = (y0 + radio) - ys[-1]
    if falta > 0:
        ys = [yy + falta for yy in ys]
    xg = x0 - 9 if lado == "izq" else x1 + 9
    for (n, (u, v)), yy in zip(pts, ys):
        globo(msp, str(n), (xg, yy), (u, v), radio=radio, relleno_rgb=(255, 255, 255))


# ===================================================================================== GI-04 transporte: planta
def _galeria_ancho(cid):
    return 2.8 if cid[:2] in ("CE", "CP") else 1.2


K_T = {x["id"]: x for x in K["transportadores"]}


@lamina(4)
def gi04():
    doc, msp, z = hoja(4, "TRANSPORTE DE GUANO\nPLANTA GENERAL Y DETALLES", "1:500 · 1:200")
    titulo_vista(msp, "PLANTA GENERAL DEL TRANSPORTE DE GUANO - ESC. 1:500", 27, 274)
    v = Vista(28.0, 214.0, -77.0, 8.0, 500)
    for g in D["galpones"]:
        v.relleno_rect(msp, g["x0"], g["y0"], g["x1"], 30.0, C["galpon"])
        v.poli(msp, [(g["x0"], 30.0), (g["x0"], g["y0"]), (g["x1"], g["y0"]), (g["x1"], 30.0)], "CONTORNO")
        tn(msp, g["id"], v(g["x"], 27.5), 2.4, "MIDDLE_CENTER")
    n = D["planta"]["nave"]
    v.relleno_rect(msp, 0, 8.0, n["L"], n["A"], C["planta"])
    v.poli(msp, [(0, 8.0), (0, n["A"]), (n["L"], n["A"]), (n["L"], 8.0)], "CONTORNO")
    t(msp, "NAVE DE PROCESO", v(20.0, 10.0), 1.9, "MIDDLE_CENTER")
    tp = D["tolva_pulmon"]
    v.relleno_rect(msp, tp["x0"], tp["y0"], tp["x1"], tp["y1"], C["tp"])
    t(msp, "TP-01", v((tp["x0"] + tp["x1"]) / 2, tp["y0"] - 1.0), 1.7, "TOP_CENTER")
    for tt in D["torres"]:
        v.relleno_rect(msp, tt["x"] - tt["A"] / 2, tt["y"] - tt["B"] / 2, tt["x"] + tt["A"] / 2, tt["y"] + tt["B"] / 2, C["torre"])
        cr = tt["contenedor"]
        v.rect(msp, cr["x"] - cr["A"] / 2, cr["y"] - cr["L"] / 2, cr["x"] + cr["A"] / 2, cr["y"] + cr["L"] / 2, "FINO")
        t(msp, tt["id"], v(tt["x"], tt["y"] - 3.0), 1.8, "TOP_CENTER")
    for tr in D["transporte"]:
        pts = [(q[0], q[1]) for q in trazado(tr)]
        col = C["transporte"] if tr["id"][:2] in ("CE", "CP") else C["inclinada"]
        if tr["id"][:2] in ("CE", "CP"):
            for sg in (-1, 1):
                v.poli(msp, [(x, y + sg * _galeria_ancho(tr["id"]) / 2) for x, y in pts], "FINO")
        v.poli(msp, pts, "CONTORNO", color=col, lw=60)
        xm = (pts[0][0] + pts[-1][0]) / 2
        ym = (pts[0][1] + pts[-1][1]) / 2
        if tr["id"][:2] in ("CE", "CP"):
            t(msp, f"{tr['id']} · {fmt(K_T[tr['id']]['L_m'], 1)} m", v(xm, ym + 2.2), 1.8, "BOTTOM_CENTER")
        elif tr["id"].startswith("CI"):
            t(msp, tr["id"], v(pts[-1][0] + 1.6, 18.5), 1.7, "MIDDLE_LEFT", rotacion=90)
    flecha(msp, v(-40, 9.6), v(-20, 9.6), "CONTORNO", tam=2.0)
    t(msp, "sentido del guano", v(-30, 9.0), 1.7, "TOP_CENTER")
    flecha(msp, v(80, 9.6), v(60, 9.6), "CONTORNO", tam=2.0)
    t(msp, "sentido del guano", v(70, 9.0), 1.7, "TOP_CENTER")
    for k, (x0, y0, ancho, alto) in enumerate(((-72.8, 11.5, 17, 16), (-14.25, 9.6, 9, 10), (-1.0, 7.5, 9, 11.5))):
        a, b = v(x0, y0), v(x0 + ancho, y0 + alto)
        rect(msp, a[0], a[1], b[0], b[1], "OCULTAS")
        t(msp, f"D{k + 1}", (b[0] + 0.8, b[1]), 1.8, "TOP_LEFT")
    norte(msp, 398, 262, 4.0)
    # detalles 1:200 (vistas desde arriba con la cámara a la altura indicada)
    import electrica as EL
    geo1 = EL._galpon_geo(GAL["G1"])
    tt_o = D["torres"][0]
    tp_ = D["tolva_pulmon"]
    rot = {"T04_D1_G1_CI": [("CI-1", (-61.9, 18.5, 3.0), (14, 4)), ("CE-O (+6,20)", (-57.5, 14.6, 6.2), (-6, -9)),
                            ("CCM-G1", (geo1["ccm"][0], geo1["ccm"][1], 1.0), (14, -3)),
                            ("CT-1 (canal)", (-67.0, 24.8, -0.3), (-6, 9))],
           "T04_D2_TT-O": [("DV-O", (-10.3, 14.3, 5.4), (-14, 9)),
                           ("CR-O", (tt_o["contenedor"]["x"], tt_o["contenedor"]["y"], 1.9), (-12, -6)),
                           ("CE-O", (-13.0, 14.6, 6.2), (-4, 12)), ("CP-O", (-7.2, 14.6, 4.6), (6, 10))],
           "T04_D3_TP01": [("TP-01", ((tp_["x0"] + tp_["x1"]) / 2, (tp_["y0"] + tp_["y1"]) / 2, 4.5), (10, -12)),
                           ("PC-01", (3.1, 14.6, 5.5), (12, 12)), ("RIO-TP", (7.0, 14.2, 1.5), (8, -16))]}
    for nombre, tit, x, w_det in (("T04_D1_G1_CI", "D1 · G1, CI-1 Y CE-O (vista desde +9,5 m, sin techo del galpón)", 28, 85),
                                  ("T04_D2_TT-O", "D2 · TORRE TT-O (corte a +7,90 m)", 122, 45),
                                  ("T04_D3_TP01", "D3 · TP-01 Y CABEZALES (corte a +6,05 m)", 176, 45)):
        try:
            proy, caja = vista_img(doc, msp, nombre, x, 98, 200)
            tn(msp, tit, (x, caja[3] + 2.5), 1.8, "BOTTOM_LEFT")
            for txt, P, (dx, dy) in rot.get(nombre, []):
                q = proy(P)
                etiqueta(msp, txt, q, (q[0] + dx, q[1] + dy), 1.7, "MIDDLE_RIGHT" if dx < 0 else "MIDDLE_LEFT")
        except FileNotFoundError:
            t(msp, f"(falta la vista {nombre})", (x, 120), 2.0, "MIDDLE_LEFT")
    t(msp, "Detalles a escala 1:200", (28, 93), 2.0, "TOP_LEFT")
    filas = [["Cinta", "Tipo", "L (m)", "B (mm)", "v (m/s)", "Q dis./cap. (t/h)", "P req./motor (kW)", "Motor"]]
    for tr_ in K["transportadores"]:
        motor = next((m["tag"] for m in K["motores_nuevos"] if m["nom"].endswith(" " + tr_["id"]) or
                      (tr_["id"][:2] in ("CT", "CI") and m["nom"].endswith(f"G{tr_['id'][-1]}") and
                       (("transversal" in m["nom"]) == (tr_["id"][:2] == "CT")))), "")
        filas.append([tr_["id"], tr_["tipo"], fmt(tr_["L_m"], 1), f"{tr_['B_m'] * 1000:.0f}", fmt(tr_["v_m_s"], 2),
                      f"{fmt(tr_['Q_diseno_t_h'], 1)} / {fmt(tr_['Q_capacidad_t_h'], 1)}",
                      f"{fmt(tr_['P_requerida_kW'], 2)} / {fmt(tr_['motor_kW'], 2)}", motor])
    subtitulo(msp, "TRANSPORTADORES (DIN 22101, preliminares P)", 232, 200)
    tabla(msp, 232, 197, [14, 20, 13, 13, 13, 28, 28, 14], filas, h_fila=4.3, altura=1.9,
          alin=["C", "L", "R", "R", "R", "C", "C", "C"])
    return doc


# ===================================================================================== GI-05 transporte: perfiles
@lamina(5)
def gi05():
    doc, msp, z = hoja(5, "TRANSPORTE DE GUANO\nELEVACIONES Y PERFIL DE LA CI", "1:250 · 1:100")
    cotas = D["cotas"]
    for nombre, tit, y in (("T05_oeste", "ELEVACIÓN LADO OESTE (desde el Sur): CE-O, TT-O, CP-O Y NAVE - ESC. 1:250", 220),
                           ("T05_este", "ELEVACIÓN LADO ESTE (desde el Sur): NAVE, CP-E, TT-E Y CE-E - ESC. 1:250", 158)):
        titulo_vista(msp, tit, 27, y + 50)
        try:
            proy, caja = vista_img(doc, msp, nombre, 30, y, 250)
        except FileNotFoundError:
            continue
        lado = "O" if "oeste" in nombre else "E"
        tt = next(t_ for t_ in D["torres"] if t_["lado"] == lado)
        xn = caja[2] + 2
        for zz, txt in ((0.0, "±0,00"), (cotas["Z_COLECTORA"], "+6,20 colectora"), (tt["z_plataforma"], "+4,80 plataforma"),
                        (8.2, "+8,20 techo de la torre")):
            nivel(msp, xn, proy((tt["x"], 12.3, zz))[1], txt)
    titulo_vista(msp, "CORTE POR EL EJE DE LA CI-1 (x = -61,85, mirando al Oeste) - ESC. 1:100", 27, 147)
    try:
        proy, caja = vista_img(doc, msp, "T05_CI", 30, 40, 100)
        for zz, txt, yy in ((-0.95, "-0,95 tramo en el foso", 26.0), (cotas["Z_COLECTORA"], "+6,20 CE-O", 13.0),
                            (7.1, "+7,10 cabezal de la CI", 15.3)):
            q = proy((-61.85, yy, zz))
            nivel(msp, q[0], q[1], txt)
    except FileNotFoundError:
        pass
    notas(msp, ["1. Vistas a escala obtenidas del modelo 3D con la cámara",
                "   en el plano indicado (lo de adelante no se ve).",
                "2. Las galerías apoyan en caballetes cada ≤ 11 m, fuera",
                "   de los caminos internos.",
                "3. La CP-E cuelga de las cerchas dentro de la nave (carga a verificar en la estructura de la Rev. F); la",
                "   CP-O entra por el muro Oeste hasta el pórtico PC-01.",
                "4. Niveles en m respecto del piso de la nave (±0,00)."], 232, 140, altura=2.0, titulo="NOTAS")
    return doc


# ===================================================================================== GI-06 torre
@lamina(6)
def gi06():
    doc, msp, z = hoja(6, "TORRE DE TRANSFERENCIA TT-O\nPLANTA Y CORTES", "1:75 · 1:100")
    tt = D["torres"][0]
    titulo_vista(msp, "PLANTA (corte a +7,90 m) - ESC. 1:75", 27, 274, 2.6)
    proy_p, caja_p = vista_img(doc, msp, "T06_planta", 36, 116, 75)
    titulo_vista(msp, "CORTE A-A (y = 13,05; mira al Norte) - ESC. 1:75", 150, 274, 2.6)
    proy_a, caja_a = vista_img(doc, msp, "T06_A", 156, 112, 75)
    for zz, txt in ((0, "±0,00"), (tt["z_plataforma"], "+4,80 plataforma"), (6.2, "+6,20 colectora"), (8.2, "+8,20 techo"),
                    (tt["boca_emergencia_z"], "+2,20 boca de emergencia")):
        nivel(msp, caja_a[2] + 2, proy_a((-10, 13.05, zz))[1], txt)
    titulo_vista(msp, "CORTE B-B (x = -9,95; mira al Oeste) - ESC. 1:100", 272, 274, 2.6)
    proy_b, caja_b = vista_img(doc, msp, "T06_B", 276, 150, 100)
    items = [("1", (-9.68, 14.44, 5.47)), ("2", (-10.9, 15.24, 6.0)), ("3", (-11.0, 14.6, 4.4)), ("4", (-10.0, 12.2, 3.0)),
             ("6", (-8.57, 13.5, 5.4)), ("7", (-9.0, 14.0, 4.8))]
    globos_lado(msp, items, proy_p, caja_p, "izq", radio=2.4)
    items_b = [("4", (-9.95, 11.9, 3.0)), ("5", (-9.95, 11.6, 1.0)), ("8", (-9.95, 14.6, 9.6))]
    globos_lado(msp, items_b, proy_b, caja_b, "der", radio=2.4)
    refs = [["1", "Desviadora DV-O con actuador M89 de 0,37 kW y finales ZSA/ZSB"],
            ["2", "Cabezal de la colectora CE-O (motorreductor M81, 1,5 kW)"],
            ["3", "Cola de la principal CP-O"],
            ["4", "Chute de emergencia a 50° con tapa de inspección"],
            ["5", "Contenedor volquete de emergencia CR-O de 20 m³"],
            ["6", "Periferia RIO-O con panel KTP400"],
            ["7", "Plataforma de rejilla +4,80 con barandas y escalera a 42°"],
            ["8", "Punta captora Franklin y bajada de Cu 50 mm²"]]
    subtitulo(msp, "REFERENCIAS", 110, 98)
    tabla(msp, 110, 95, [8, 110], [["N°", "Elemento"]] + refs, h_fila=4.3, altura=1.8, alin=["C", "L"])
    notas(msp, ["1. Vistas a escala del modelo 3D.",
                "   La TT-E es simétrica.",
                "2. Columnas HEB 160 con placas y",
                "   anclajes; vigas UPN 160.",
                "3. La desviadora pasa a B (contenedor)",
                "   solo con el secador parado y por",
                "   orden del operador."], 28, 98, altura=1.9, titulo="NOTAS")
    return doc


# ===================================================================================== GI-07 tolva pulmón
@lamina(7)
def gi07():
    doc, msp, z = hoja(7, "TOLVA PULMÓN TP-01\nPLANTA Y CORTES", "1:75 · 1:100")
    tp = D["tolva_pulmon"]
    titulo_vista(msp, "PLANTA (bajo la tapa, +4,45 m) - ESC. 1:75", 27, 274, 2.6)
    proy_p, caja_p = vista_img(doc, msp, "T07_planta", 36, 100, 75)
    titulo_vista(msp, "CORTE A-A (x = 2,25; mira al Oeste) - ESC. 1:100", 156, 274, 2.6)
    proy_a, caja_a = vista_img(doc, msp, "T07_A", 160, 172, 100)
    for zz, txt in ((0, "±0,00"), (tp["z_tapa"], f"+{fmt(tp['z_tapa'], 2)} tapa"), (1.42, "+1,42 eje de los sinfines")):
        nivel(msp, caja_a[2] + 2, proy_a((2.25, 12.7, zz))[1], txt)
    titulo_vista(msp, "CORTE B-B (y = 12,60; mira al Norte) - ESC. 1:100", 300, 274, 2.6)
    proy_b, caja_b = vista_img(doc, msp, "T07_B", 306, 172, 100)
    globos_borde(msp, [("1", (1.15, 16.6, 1.42))], proy_p, caja_p, ("izq",), radio=2.4)
    globos_borde(msp, [("3", (0.52, 10.12, 1.93))], proy_a, caja_a, ("abajo",), radio=2.4, dist=6.0)
    globos_borde(msp, [("2", (2.25, 12.7, 1.42)), ("4", (3.1, 12.6, 4.5)), ("5", (0.59, 13.0, 3.95))], proy_b, caja_b,
                 ("abajo",), radio=2.4, dist=6.0)
    sf = tp["sinfines"]
    filas = [["N°", "Dato", "Valor"],
             ["", "Volumen útil", f"{fmt(tp['volumen_util_m3'], 0)} m³ ({fmt(K['balance']['tolva_pulmon_dias'], 1)} días de reserva)"],
             ["", "Medidas en planta", f"{fmt(tp['x1'] - tp['x0'], 2)} × {fmt(tp['y1'] - tp['y0'], 2)} m"],
             ["1", "Motorreductores", "M85 a M88, coaxiales de 3 kW con variador"],
             ["2", "Fondo vivo", f"{sf['n']} sinfines Ø400 × {fmt(sf['largo'], 2)} m en artesas"],
             ["3", "Pesaje", "4 celdas de compresión C3 + SIWAREX WP231"],
             ["4", "Nivel continuo", "radar LT-101 de 80 GHz en la tapa"],
             ["5", "Niveles puntuales", "horquillas LSHH-101 y LSL-101"],
             ["", "Registros", "2 de 800 × 700 con interruptor ZS-REG"],
             ["", "Aspiración", "boca Ø600 al extractor M23 y al biofiltro"]]
    subtitulo(msp, "DATOS Y REFERENCIAS DE LA TP-01", 156, 150)
    tabla(msp, 156, 147, [8, 34, 102], filas, h_fila=4.3, altura=1.9, alin=["C", "L", "L"])
    notas(msp, ["1. Vistas a escala del modelo 3D con la cámara en el plano del corte.",
                "2. Los sinfines descargan en la cinta de alimentación M8 del secador",
                "   (Rev. F) por bocas con manga de goma."], 156, 98, altura=1.9, titulo="NOTAS")
    return doc


# ===================================================================================== GI-08 nave: planta
@lamina(8)
def gi08():
    import planta as PL
    doc, msp, z = hoja(8, "NAVE DE PROCESO\nPLANTA DE EQUIPOS", "1:150")
    titulo_vista(msp, "PLANTA DE EQUIPOS (vista desde +6,15 m, bajo las cerchas) - ESC. 1:150", 27, 274)
    proy, caja = vista_img(doc, msp, "T08_planta_nave", 30, 78, 150)
    lista = [(k, nom, c) for k, (nom, c) in centros_revF().items()
             if not (k in PL.EXCLUIR or k.startswith(("4.", "D", "OP", "N")) or k in ("terreno", "TGF", "AN"))
             and -2 <= c[0] <= 35.5 and -1.5 <= c[1] <= 26.5]
    lista.sort(key=lambda r: (len(r[0]), r[0]))
    for k, nom, c in lista:
        globo(msp, k, proy((c[0], c[1], 6.15)), None, radio=2.1, relleno_rgb=(255, 255, 255))
    nuevos = [("TP-01", (2.8, 12.6), "Tolva pulmón con 4 sinfines"), ("PC-01", (2.75, 16.9), "Pórtico de cabezales CP-O y CP-E"),
              ("RIO-TP", (7.6, 14.2), "Periferia de la recepción y KTP700"), ("TS-GU", (25.65, 3.1), "Tablero del transporte y PLC-01")]
    for k, xy, nom in nuevos:
        q = proy((xy[0], xy[1], 6.15))
        relleno_rect(msp, q[0] - 6, q[1] - 1.6, q[0] + 6, q[1] + 1.6, (255, 236, 200))
        rect(msp, q[0] - 6, q[1] - 1.6, q[0] + 6, q[1] + 1.6, "FINO")
        tn(msp, k, q, 1.7, "MIDDLE_CENTER")
    filas = [["N°", "Equipo de la Rev. F que sigue"]] + [[k, nom.replace(" (scrubber)", "")[:46]] for k, nom, c in lista[:34]]
    subtitulo(msp, "EQUIPOS", 288, 274)
    yb = tabla(msp, 288, 271, [12, 105], filas, h_fila=3.9, altura=1.7, alin=["C", "L"])
    subtitulo(msp, "NUEVO EN LA GRANJA INTEGRADA", 288, yb - 7)
    tabla(msp, 288, yb - 10, [16, 101], [["Tag", "Equipo"]] + [[k, nom] for k, xy, nom in nuevos], h_fila=3.9, altura=1.7,
          alin=["C", "L"])
    norte(msp, 276, 254, 4.0)
    return doc


# ===================================================================================== GI-09 nave: cortes
@lamina(9)
def gi09():
    doc, msp, z = hoja(9, "NAVE DE PROCESO\nCORTES", "1:150 · 1:200")
    n = D["planta"]["nave"]
    titulo_vista(msp, "CORTE A-A (y = 9,30, por el secador y la descarga de la TP-01, mirando al Norte) - ESC. 1:150", 27, 274)
    proy_a, caja_a = vista_img(doc, msp, "T09_A", 32, 150, 150)
    for zz, txt in ((0, "±0,00"), (n["h_alero"], "+7,00 alero"), (n["h_cumbrera"], "+8,35 cumbrera")):
        nivel(msp, caja_a[2] + 2, proy_a((16.75, 9.3, zz))[1], txt)
    titulo_vista(msp, "CORTE B-B (x = 3,00, por la TP-01 y los cabezales, mirando al Oeste) - ESC. 1:200", 27, 140)
    proy_b, caja_b = vista_img(doc, msp, "T09_B", 32, 40, 200)
    for zz, txt in ((0, "±0,00"), (D["tolva_pulmon"]["z_tapa"], "+4,55 tapa de la TP-01"), (n["h_alero"], "+7,00 alero"),
                    (n["h_cumbrera"], "+8,35 cumbrera")):
        nivel(msp, caja_b[2] + 2, proy_b((3.0, 12.5, zz))[1], txt)
    notas(msp, ["1. Vistas a escala del modelo 3D (nave de la Rev. F,",
                "   secador SC-4 y equipos nuevos), con la cámara en el",
                "   plano del corte.",
                "2. La nave, el secador y los equipos de la Rev. F no",
                "   cambian salvo lo indicado en la GI-08.",
                "3. Niveles en m."], 300, 140, altura=2.0, titulo="NOTAS")
    return doc


# ===================================================================================== ayudas de vistas y globos
_CENTROS = None


def centros_revF():
    """{clave: (nombre, centro 3D en m)} de las partes de la Rev. F (geometría del visor, con los corrimientos de planta.py)."""
    global _CENTROS
    if _CENTROS is None:
        import gzip
        import json as _json
        import numpy as _np
        import planta as PL
        geo = _json.loads(gzip.open(PL.GEO, "rt", encoding="utf-8").read())
        nombres = geo.get("nombres", {})
        _CENTROS = {}
        for k, items in geo["partes"].items():
            pts = []
            for it in items:
                if not it.get("tri"):
                    continue
                m = _np.array(it["m"], float).reshape(4, 4).T
                vv = _np.array(it["tri"], float).reshape(-1, 3)
                w_ = (m @ _np.c_[vv, _np.ones(len(vv))].T).T[:, :3]
                p_ = _np.c_[w_[:, 0], -w_[:, 2], w_[:, 1]]
                ok, dxyz = PL._filtro_item(k, p_.min(0), p_.max(0))
                if ok:
                    pts.append(p_.mean(0) + (dxyz if dxyz is not None else 0))
            if pts:
                _CENTROS[k] = (nombres.get(k, ""), _np.mean(pts, axis=0))
    return _CENTROS


def escala_para(nombre, ancho_mm, alto_mm, escalas=(5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 125, 150, 200, 250, 300, 400, 500),
                normal=True):
    """La escala normal más grande con la que la vista `nombre` (recortada a lo dibujado) entra en ancho_mm × alto_mm.
    Con normal=False devuelve el denominador justo (vistas sin escala: isométricas y despieces)."""
    meta, im, (bx0, by0, bx1, by1) = _recorte(nombre)
    m_px = meta["ancho_m"] / im.size[0]
    w_m, h_m = (bx1 - bx0) * m_px, (by1 - by0) * m_px
    if not normal:
        return max(w_m * 1000 / ancho_mm, h_m * 1000 / alto_mm)
    for den in escalas:
        if w_m * 1000 / den <= ancho_mm and h_m * 1000 / den <= alto_mm:
            return den
    return escalas[-1]


def _repartir(pos, sep, a, b):
    """Corre las posiciones (ordenadas) para que queden separadas al menos `sep` y dentro de [a, b]."""
    out = []
    for p in pos:
        out.append(max(p, out[-1] + sep) if out else max(p, a))
    if out and out[-1] > b:
        out[-1] = b
        for i in range(len(out) - 2, -1, -1):
            out[i] = min(out[i], out[i + 1] - sep)
    return out


def globos_borde(msp, items, proy, caja, bordes=("arriba", "abajo"), sep=6.6, radio=2.6, dist=7.0):
    """Globos en fila sobre los bordes de la vista, cada uno con su línea al punto 3D del ítem (n, punto).
    Cada ítem va al borde más cercano de los indicados; dentro de cada fila se ordenan para que las líneas no se crucen."""
    x0, y0, x1, y1 = caja
    grupos = {b: [] for b in bordes}
    for n, pt in items:
        u, v = proy(pt)
        d = {"arriba": y1 - v, "abajo": v - y0, "izq": u - x0, "der": x1 - u}
        grupos[min(bordes, key=lambda k: d[k])].append((n, (u, v)))
    for b, lst in grupos.items():
        if not lst:
            continue
        if b in ("arriba", "abajo"):
            lst.sort(key=lambda r: r[1][0])
            pos = _repartir([q[0] for _, q in lst], sep, x0 + radio, x1 - radio)
            yy = y1 + dist if b == "arriba" else y0 - dist
            for (n, q), xx in zip(lst, pos):
                globo(msp, str(n), (xx, yy), q, radio=radio, relleno_rgb=(255, 255, 255))
        else:
            lst.sort(key=lambda r: -r[1][1])
            pos = _repartir([-q[1] for _, q in lst], sep, -(y1 - radio), -(y0 + radio))
            xx = x0 - dist if b == "izq" else x1 + dist
            for (n, q), yy in zip(lst, pos):
                globo(msp, str(n), (xx, -yy), q, radio=radio, relleno_rgb=(255, 255, 255))


def _mot(tag):
    return next((m for m in E["motores"] if m["tag"] == tag), None)


def _kw(tag):
    m = _mot(tag)
    return f"{fmt(m['kW'], 2)} kW" if m else "(completar)"


# ===================================================================================== GI-10 secador SC-4 integrado
@lamina(10)
def gi10():
    doc, msp, z = hoja(10, "SECADOR SC-4 (REV. F)\nINTEGRACIÓN A LA GRANJA", "S/E")
    B = K["balance"]
    tp = D["tolva_pulmon"]
    S_ = D["planta"]["secador"]
    glp = next(x for x in D["servicios"] if x["id"] == "GLP")
    titulo_vista(msp, "LÍNEA DE SECADO DEL MODELO 3D: TP-01 → CINTA M8 → SC-4 → DESCARGA (ISOMÉTRICA, S/E)", 27, 274, 2.8)
    den = escala_para("T10_SC4", 190, 112, normal=False)
    proy, caja = vista_img(doc, msp, "T10_SC4", 32, 146, den)
    cen = centros_revF()
    refs = [
        ("—", ((tp["x0"] + tp["x1"]) / 2, (tp["y0"] + tp["y1"]) / 2, tp["z_tapa"]),
         f"Tolva pulmón TP-01 ({fmt(tp['volumen_util_m3'], 0)} m³) con los sinfines M85 a M88 (nuevo)"),
        ("—", (1.2, 17.4, 6.45), "Aspiración Ø600 de la TP-01 al extractor M23 y al biofiltro (nuevo)"),
        ("3.1", None, f"Cinta de alimentación M8 ({_kw('M8')}) con bordes y tacos"),
        ("5", None, f"Esparcidor de paletas M9 ({_kw('M9')})"),
        ("4.8", None, f"Cámara de {fmt(S_['L'], 1)} × {fmt(S_['A'], 1)} × {fmt(S_['H'], 1)} m con panel sándwich de 80 mm"),
        ("4.5", None, f"Motorreductores de los 3 pisos M5 a M7 ({_kw('M5')} c/u)"),
        ("4.13", None, "Pasarela superior con baranda"),
        ("9", None, "Hogar de parrilla escalonada a cáscara de arroz"),
        ("10", None, "Intercambiador humos-aire"),
        ("11", None, f"Ventiladores de impulsión M1 y M2 ({_kw('M1')} c/u)"),
        ("12", None, "Ducto de aire caliente al secador"),
        ("13", None, f"Silo de cáscara de 70 m³ con sinfín M12 ({_kw('M12')})"),
        ("15", None, "Chimenea de humos"),
        ("—", (glp["x"], glp["y"], 0.8 + glp["D"] / 2), "Tanque de GLP de 0,5 m³ del piloto del hogar (reemplaza al biogás)"),
        ("17", None, "Ducto de aire agotado (escape aislado, Rev. F)"),
        ("18", None, "Ciclón separador"),
        ("19", None, f"Lavador de gases con bomba M14 ({_kw('M14')})"),
        ("20", None, f"Extractor M3 ({_kw('M3')}) y chimenea de aire tratado"),
        ("6", None, f"Sinfín de descarga M10 ({_kw('M10')})"),
        ("7", None, f"Elevador de cangilones M11 ({_kw('M11')})"),
        ("F1", None, "Tolva de retención de 1 h y enfriador del producto (Rev. F)"),
        ("8", None, "Acopio de producto seco"),
    ]
    items, filas = [], [["N°", "Equipo", "Ref. Rev. F"]]
    for k, pt, desc in refs:
        if pt is None:
            if k not in cen:
                continue
            pt = tuple(cen[k][1])
        n = len(items) + 1
        items.append((n, pt))
        filas.append([str(n), desc, k])
    globos_borde(msp, items, proy, caja, ("arriba", "abajo"), sep=6.4, radio=2.5, dist=7.5)
    # ---------------------------------------------------------------- interfaces con la granja
    subtitulo(msp, "INTERFACES DEL SC-4 CON LA GRANJA INTEGRADA", 28, 124)
    tabla(msp, 28, 121, [36, 72, 92], [
        ["Interfaz", "Rev. F (planta sola)", "Granja integrada"],
        ["Ingreso del guano", "camión, playa y pala a la tolva de 3,1 m³", "galpones → cintas → TP-01 (sin pala ni camión)"],
        ["Alimentación del SC-4", "cinta M8 desde la tolva de recepción", "cinta M8 desde la descarga de los sinfines de la TP-01"],
        ["Caudal de guano", "velocidad de la M8 (operador)", f"FIC-101 en el PLC-01: {fmt(B['secador_kg_h_regimen'], 0)} kg/h en régimen"],
        ["Control del secado", "PLC-02: TIC-01 y MIC-01", "sin cambios; MIC-01 corrige TIC-01 y la consigna de FIC-101"],
        ["Comunicación", "PLC-02 solo, con KTP700", "PLC-02 como I-device del PLC-01 (PROFINET)"],
        ["Energía", "TGF y TG2 de la Rev. F", "sin cambios; el Q23 del TG2 (ex TS-BIO) alimenta el TS-GU"],
        ["Piloto del hogar", "biogás de la planta vecina (E8)", "GLP con tanque de 0,5 m³; el biogás se elimina"],
        ["Producto seco", "retención 0,7 m³, enfriador 900 m³/h, zaranda", "F1 de 1,0 m³ y enfriador de 1.200 m³/h (P)"],
    ], h_fila=4.3, altura=1.75, alin=["L", "L", "L"])
    # ---------------------------------------------------------------- datos y referencias
    h_reg = D["planta"]["secador"]
    horas = B["guano_total_kg_dia"] / B["secador_kg_h_regimen"]
    subtitulo(msp, "DATOS DEL SC-4 EN LA GRANJA", 236, 271)
    yb = tabla(msp, 236, 268, [82, 88], [
        ["Dato", "Valor"],
        ["Tipo", "secador de cinta de 3 pisos, malla AISI 304"],
        ["Banda y cámara", f"{fmt(h_reg['banda_ancho'], 1)} m · {fmt(h_reg['L'], 1)} × {fmt(h_reg['A'], 1)} × {fmt(h_reg['H'], 1)} m"],
        ["Guano húmedo de los 4 galpones", f"{fmt(B['guano_total_kg_dia'], 0)} kg/día"],
        ["Humedad de entrada → salida", "72 % → 15 % (Rev. F)"],
        ["Régimen adoptado", f"{fmt(B['secador_kg_h_regimen'], 0)} kg/h con aire a {fmt(B['T_aire_regimen_C'], 0)} °C"],
        ["Horas de secado por día", f"{fmt(horas, 1)} h ({B['secador_turnos']} turnos)"],
        ["Capacidad máxima (Rev. F)", "1.440 kg/h con aire a 135 °C"],
        ["Reserva de capacidad", f"{fmt(B['reserva_secador_pct'], 1)} %"],
        ["Producto seco", f"{fmt(B['producto_seco_kg_dia'], 0)} kg/día"],
        ["Agua evaporada", f"{fmt(B['agua_evaporada_kg_dia'], 0)} kg/día"],
        ["Reserva de la TP-01", f"{fmt(B['tolva_pulmon_dias'], 2)} días de guano"],
    ], h_fila=4.0, altura=1.8, alin=["L", "L"])
    subtitulo(msp, "REFERENCIAS DE LA VISTA", 236, yb - 7)
    yb = tabla(msp, 236, yb - 10, [9, 144, 17], filas, h_fila=3.55, altura=1.6, alin=["C", "L", "C"])
    notas(msp, ["Detalle del SC-4 en el juego aparte (Rev. F): SC-01 conjunto general, SC-02 despiece y lista de piezas,",
                "SC-03 ejes, SC-04 fatiga, SC-05 bastidor y fijación, SC-06 montaje; manual de armado, STEP y visor.",
                "La forma y las medidas del secador no cambian: se conserva el diseño original."],
          236, yb - 3, altura=1.7, interlineado=1.5)
    return doc


# ===================================================================================== GI-14 canalizaciones
def _estilo_ruta(tipo, red):
    if red == "fibra":
        return C["fibra"], 35, "CONTORNO"
    return {"bandeja": (C["electrica"], 70, "CONTORNO"), "caño": (C["electrica"], 25, "CONTORNO"),
            "existente": ((120, 120, 120), 50, "CONTORNO"), "subterraneo": ((139, 90, 43), 35, "OCULTAS")}[tipo]


def _largo(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


@lamina(14)
def gi14():
    import cortes
    import electrica as EL
    doc, msp, z = hoja(14, "INSTALACIÓN ELÉCTRICA\nCANALIZACIONES Y TENDIDOS", "1:200 · 1:2000")
    rutas = EL.red()
    # ---------------------------------------------------------------- nave
    titulo_vista(msp, "NAVE DE PROCESO: BANDEJAS, CAÑOS Y TABLEROS SOBRE LA PLANTA DE EQUIPOS - ESC. 1:200", 27, 274, 2.8)
    proy, caja = vista_img(doc, msp, "T08_planta_nave", 30, 128, 200, atenuar=0.6, gris=True)
    rec = (caja[0], caja[2], caja[1], caja[3])
    for nom, tipo, pts, red in rutas:
        rgb, lw, capa = _estilo_ruta(tipo, red)
        q = [proy(p) for p in pts]
        dibujado = []
        for a, b in zip(q, q[1:]):
            if math.dist(a, b) < 0.05:
                continue
            c_ = cortes._recortar(a, b, rec)
            if c_ is None:
                continue
            linea(msp, c_[0], c_[1], capa, color=rgb, lw=lw)
            dibujado.append(c_)
        if tipo == "bandeja" and dibujado:
            a, b = max(dibujado, key=lambda s: math.dist(*s))
            if math.dist(a, b) > 6:
                ancho, tag, _ = EL.clase_bandeja(nom)
                ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
                if ang > 90 or ang < -90:
                    ang += 180
                t(msp, f"{tag} ({ancho})", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + 1.2), 1.6, "BOTTOM_CENTER", rotacion=ang,
                  color=C["electrica"])
    tableros = [("TS-GU", (EL.TS_GU["x"], EL.TS_GU["y"]), (-16, 10)), ("TG2", EL.TG2, (-22, -4)), ("TGF", EL.TGF, (10, -4)),
                ("RIO-TP", (EL.RIO_TP["x"], EL.RIO_TP["y"]), (12, 9))]
    for nom, xy, off in tableros:
        q = proy((xy[0], xy[1], 1.0))
        relleno_rect(msp, q[0] - 1.6, q[1] - 1.0, q[0] + 1.6, q[1] + 1.0, C["electrica"])
        etiqueta(msp, nom, q, (q[0] + off[0], q[1] + off[1]), 1.9, "MIDDLE_RIGHT" if off[0] < 0 else "MIDDLE_LEFT")
    leyenda(msp, 32, 121, [("l", C["electrica"], "bandeja nueva tipo escalera (tag y ancho en mm)"),
                           ("l", (120, 120, 120), "bandeja de las galerías de las cintas (BC, 200 mm)")], ancho=8, h=3.6, alto_txt=1.8)
    leyenda(msp, 132, 121, [("l", C["fibra"], "fibra óptica (anillos PROFINET)"),
                            ("d", (139, 90, 43), "caño enterrado a -0,70 m (en trazos)")], ancho=8, h=3.6, alto_txt=1.8)
    # ---------------------------------------------------------------- tabla de canalizaciones
    grupos = {}
    for nom, tipo, pts, red in rutas:
        L = _largo(pts)
        if tipo == "bandeja":
            ancho, tag, _ = EL.clase_bandeja(nom)
            if tag[:4] in ("BT-G", "BT-C") and tag[-1].isdigit():
                tag = tag[:-1] + "1 a " + tag[:-1] + "4"
            clave = (tag, f"bandeja escalera {ancho} mm")
        elif tipo == "existente":
            clave = ("BC-…", "bandeja escalera 200 mm (galerías)")
        elif tipo == "caño":
            d_, tag = EL.clase_cano(nom)
            clave = (tag, f"caño de acero galv. Ø{d_} mm" if tag != "FO" else f"caño para fibra Ø{d_} mm")
        else:
            clave = ("SUB", "TGBT → TGF y TG2" if red == "acometida" else
                     ("TS-G → CCM (4 galpones)" if red.endswith("-alim") else "CCM → pie de la CI (4 galpones)"))
        grupos.setdefault(clave, [0.0, 0, set()])
        grupos[clave][0] += L
        grupos[clave][1] += 1
        grupos[clave][2].add(nom.split(" (")[0])
    desc = {"BT-SC": "sala de control: TG2 → TS-GU", "BT-01": "troncal TS-GU → recepción (+5,60, colgada de las correas)",
            "BT-PC01": "pórtico de cabezales PC-01", "BT-TP": "recepción: RIO-TP y motores de los sinfines",
            "BT-TT-O": "torre TT-O (+7,40) y bajada al RIO-O", "BT-TT-E": "torre TT-E (+7,40) y bajada al RIO-E",
            "BT-G1 a BT-G4": "cabeceras de guano de los galpones (+3,45)", "BT-CI-1 a BT-CI-4": "cintas inclinadas CI-1 a CI-4",
            "BC-…": "galerías de CE-O, CE-E, CP-O y CP-E", "CÑ": "bajadas a motores, sensores y botoneras",
            "CT": "cintas transversales CT-1 a CT-4", "FO": "cruces de la fibra óptica"}
    filas = [["Tag", "Recorrido", "Tipo y medida", "Tramos", "Largo (m)"]]
    orden = ["BT-SC", "BT-01", "BT-PC01", "BT-TP", "BT-TT-O", "BT-TT-E", "BT-G1 a BT-G4", "BT-CI-1 a BT-CI-4", "BC-…", "CÑ", "CT", "FO", "SUB"]
    for (tag, tipo_), (L, n, noms) in sorted(grupos.items(), key=lambda kv: (orden.index(kv[0][0]) if kv[0][0] in orden else 99, kv[0][1])):
        d_txt = "cruces de muro hacia las galerías" if (tag == "CÑ" and "Ø50" in tipo_) else desc.get(tag, tipo_ if tag == "SUB" else "")
        filas.append([tag if tag != "SUB" else "—", d_txt,
                      tipo_ if tag != "SUB" else "enterrado, cámaras 40 × 40", str(n), fmt(L, 1)])
    subtitulo(msp, "CANALIZACIONES NUEVAS (largos medidos en el modelo 3D)", 28, 108)
    tabla(msp, 28, 105, [24, 76, 50, 14, 20], filas, h_fila=3.75, altura=1.65, alin=["C", "L", "L", "R", "R"])
    # ---------------------------------------------------------------- granja: tendidos entre edificios
    titulo_vista(msp, "GRANJA: TENDIDOS ENTRE EDIFICIOS - ESC. 1:2000", 236, 274, 2.8)
    gx0 = min(g["x0"] for g in D["galpones"]) - 4
    gy1 = max(g["y1"] for g in D["galpones"]) + 4
    alto_plano = (gy1 + 82.0) / 2.0
    vf = Vista(240.0, 266.0 - alto_plano, gx0, -82.0, 2000)
    y_pie = 266.0 - alto_plano
    for g in D["galpones"]:
        vf.relleno_rect(msp, g["x0"], g["y0"], g["x1"], g["y1"], C["galpon"])
        vf.rect(msp, g["x0"], g["y0"], g["x1"], g["y1"], "FINO")
        tn(msp, g["id"], vf(g["x"], (g["y0"] + g["y1"]) / 2), 1.8, "MIDDLE_CENTER")
    n_ = D["planta"]["nave"]
    vf.relleno_rect(msp, 0, 0, n_["L"], n_["A"], C["planta"])
    vf.rect(msp, 0, 0, n_["L"], n_["A"], "FINO")
    for tt in D["torres"]:
        vf.rect(msp, tt["x"] - tt["A"] / 2, tt["y"] - tt["B"] / 2, tt["x"] + tt["A"] / 2, tt["y"] + tt["B"] / 2, "FINO")
    for tr in D["transporte"]:
        vf.poli(msp, [(q[0], q[1]) for q in trazado(tr)], "FINO", color=(170, 170, 170))
    for nom, tipo, pts, red in rutas:
        rgb, lw, capa = _estilo_ruta(tipo, red)
        vf.poli(msp, [(p[0], p[1]) for p in pts], capa, color=rgb, lw=lw)
    q = vf(*EL.TGBT)
    relleno_rect(msp, q[0] - 1.5, q[1] - 1.5, q[0] + 1.5, q[1] + 1.5, (60, 60, 60))
    etiqueta(msp, "TGBT (subestación 315 kVA)", q, (q[0] + 6, q[1] + 3), 1.7)
    q = vf(12.0, 9.0)
    etiqueta(msp, "nave (TGF, TG2, TS-GU)", q, (q[0] + 18, q[1] - 10), 1.7)
    t(msp, "QF3 a QF6 (TGBT → TS-G1 a TS-G4) van por los caminos: largo de cálculo en la memoria; esquema en GI-12.",
      (236, y_pie - 3), 1.55, "TOP_LEFT")
    norte(msp, 404, 262, 3.2)
    # ---------------------------------------------------------------- alimentadores
    filas = [["Circuito", "Desde → hasta", "S (mm²)", "Mét.", "L (m)", "ΔU (%)", "ΔU tot. (%)"]]
    for a in E["alimentadores"]:
        filas.append([a["circuito"].split(" · ")[0].replace("TG2", "Q23") if a["circuito"].startswith("TG2") else a["circuito"].split(" · ")[0],
                      f"{a['desde']} → {a['hasta']}", fmt(a["S_mm2"], 0), a["metodo"], fmt(a["L_m"], 1),
                      fmt(a["dU_pct"], 2), fmt(a["dU_total_pct"], 2)])
    subtitulo(msp, "ALIMENTADORES (Cu, AEA 90364; ΔU ≤ 3 % hasta cada CCM)", 236, y_pie - 11)
    yb = tabla(msp, 236, y_pie - 14, [24, 44, 16, 12, 18, 18, 22], filas, h_fila=3.7, altura=1.65,
               alin=["L", "L", "R", "C", "R", "R", "R"])
    notas(msp, ["1. Bandejas escalera galvanizadas con conductor de protección de Cu 16 mm² continuo.",
                "2. Caños de PEAD a -0,70 m con malla de advertencia (AEA 95101): Ø110 para 70 a 120 mm², Ø63 para",
                "   10 y 25 mm², Ø40 señales y fibra (P); dos caños por zanja separados 0,5 m (factor 0,95);",
                "   cámaras de 40 × 40 cm en cambios de dirección y cada 30 m.",
                "3. La fibra de cada anillo vuelve por un cable separado (otro lado de la galería)."],
          236, yb - 3, altura=1.65, interlineado=1.45)
    return doc


# ===================================================================================== GI-18 a GI-20 despieces
DESP = CARPETA.parent / "modelo_3d" / "despieces"


def _ancla(it, der, arr):
    """Punto del globo: de las piezas de la categoría que están más cerca de la cámara (el 30 % de adelante), la más
    cercana al centro de la categoría en la imagen; así la línea no termina sobre una pieza tapada."""
    import numpy as _np
    P = _np.array(it.get("candidatos") or [it["punto"]], float)
    der, arr = _np.array(der, float), _np.array(arr, float)
    adelante = -_np.cross(der, arr)                 # la cámara mira hacia su -Z local = -(X × Y)
    prof = P @ adelante
    sel = P[prof <= prof.min() + 0.3 * (prof.max() - prof.min()) + 0.05]
    c = _np.c_[P @ der, P @ arr].mean(0)
    return sel[_np.argmin(_np.linalg.norm(_np.c_[sel @ der, sel @ arr] - c, axis=1))].tolist()


def _despiece(doc, msp, nombre, img, x, y, ancho_mm, alto_mm, bordes=("izq", "der")):
    import json as _json
    meta = _json.loads((DESP / f"{nombre}.json").read_text(encoding="utf-8"))
    vis = _json.loads((IMG / f"{img}.json").read_text(encoding="utf-8"))
    den = escala_para(img, ancho_mm, alto_mm, normal=False)
    w, h = tam_vista(img, den)
    proy, caja = vista_img(doc, msp, img, x + (ancho_mm - w) / 2, y + (alto_mm - h) / 2, den)
    items = [(it["n"], _ancla(it, vis["derecha"], vis["arriba"])) for it in meta["items"]]
    globos_borde(msp, items, proy, caja, bordes, sep=7.2, radio=3.0, dist=9.0)
    return meta, caja


CANT = {"TP01": {1: "1 conj.", 2: "2", 3: "1", 4: "1", 5: "1", 6: "1", 7: "4", 8: "4", 9: "4", 10: "1 conj.", 11: "1"},
        "CPO": {1: "1", 2: "2", 3: "1", 4: "1", 5: "1", 6: "1", 7: "1", 8: "1 + 1", 9: "1", 10: "1", 11: "1", 12: "1"},
        "DVO": {1: "1", 2: "1", 3: "1", 4: "2", 5: "1", 6: "1", 7: "1", 8: "1", 9: "2", 10: "1"},
        "TSGU": {1: "1", 2: "1", 3: "1", 4: "1", 5: "1", 6: "1", 7: "10", 8: "8", 9: "2 + 4", 10: "1", 11: "1", 12: "1",
                 13: "1", 14: "40", 15: "5"}}
MAT_TSGU = {1: "chapa de acero 1,5 mm, RAL 7035", 2: "chapa de acero 1,5 mm, RAL 7035", 4: "chapa galvanizada 2 mm",
            14: "poliamida", 15: "PVC"}


def _lista_piezas(msp, nombre, meta, x, y, anchos=(9, 98, 15, 46)):
    filas = [["N°", "Descripción (medidas)", "Cant.", "Material"]]
    for it in meta["items"]:
        mat = it["material"] or MAT_TSGU.get(it["n"], "equipo comercial")
        filas.append([str(it["n"]), it["descripcion"], CANT.get(nombre, {}).get(it["n"], "1"), mat])
    return tabla(msp, x, y, list(anchos), filas, h_fila=4.3, altura=1.8, alin=["C", "L", "C", "L"])


@lamina(18)
def gi18():
    doc, msp, z = hoja(18, "TOLVA PULMÓN TP-01\nDESPIECE Y LISTA DE PIEZAS", "S/E")
    tp = D["tolva_pulmon"]
    titulo_vista(msp, "VISTA EXPLOTADA DE LA TP-01 (MODELO 3D, S/E)", 27, 274, 3.0)
    meta, caja = _despiece(doc, msp, "TP01", "X_TP01", 44, 32, 170, 228)
    subtitulo(msp, "LISTA DE PIEZAS", 236, 271)
    yb = _lista_piezas(msp, "TP01", meta, 236, 268, (9, 98, 15, 46))
    subtitulo(msp, "MEDIDAS DEL CONJUNTO", 236, yb - 7)
    yb = tabla(msp, 236, yb - 10, [80, 88], [
        ["Dato", "Valor"],
        ["Planta (exterior del cuerpo)", f"{fmt(tp['x1'] - tp['x0'], 2)} × {fmt(tp['y1'] - tp['y0'], 2)} m"],
        ["Cota de la tapa", f"+{fmt(tp['z_tapa'], 2)} m"],
        ["Volumen útil", f"{fmt(tp['volumen_util_m3'], 0)} m³"],
        ["Sinfines", f"{tp['sinfines']['n']} × Ø400 × {fmt(tp['sinfines']['largo'], 2)} m"],
        ["Piezas del modelo 3D", f"{meta['piezas']}"],
    ], h_fila=4.0, altura=1.8, alin=["L", "L"])
    notas(msp, ["1. Desarme: tapa (1) y equipos de la tapa (2 a 4); cuerpo (5) por",
                "   paneles abulonados; sinfines (7) por el testero del lado de los",
                "   motores después de sacar el motorreductor (8) y la tapa del fondo (6).",
                "2. Antes de abrir un registro (2): bloqueo y etiquetado en la estación de los",
                "   seccionadores Q-M85 a Q-M88 (los ZS-REG cortan por PROFIsafe).",
                "3. Pesaje: las celdas (9) se cambian de a una con gatos bajo las vigas."],
          236, yb - 7, altura=1.75, interlineado=1.45, titulo="NOTAS DE MONTAJE")
    return doc


@lamina(19)
def gi19():
    doc, msp, z = hoja(19, "CABEZAL CP-O Y DESVIADORA DV-O\nDESPIECES Y LISTAS DE PIEZAS", "S/E")
    titulo_vista(msp, "A - CABEZAL MOTRIZ DE LA CP-O (S/E)", 27, 274, 2.6)
    meta_a, caja_a = _despiece(doc, msp, "CPO", "X_CPO", 38, 60, 82, 190)
    titulo_vista(msp, "B - DESVIADORA DV-O DE LA TT-O (S/E)", 136, 274, 2.6)
    meta_b, caja_b = _despiece(doc, msp, "DVO", "X_DVO", 144, 34, 70, 226)
    subtitulo(msp, "A - LISTA DE PIEZAS DEL CABEZAL CP-O", 236, 271)
    yb = _lista_piezas(msp, "CPO", meta_a, 236, 268, (9, 98, 15, 46))
    cp = K_T.get("CP-O", {})
    t(msp, f"Banda de {fmt(cp.get('B_m', 0) * 1000, 0)} mm a {fmt(cp.get('v_m_s', 0), 2)} m/s · motor M82 {_kw('M82')}",
      (236, yb - 3), 1.7, "TOP_LEFT")
    subtitulo(msp, "B - LISTA DE PIEZAS DE LA DESVIADORA DV-O", 236, yb - 13)
    yb = _lista_piezas(msp, "DVO", meta_b, 236, yb - 16, (9, 98, 15, 46))
    notas(msp, ["Posición A: a la cinta principal (normal). Posición B: al contenedor",
                "de emergencia CR-O, solo con el secador parado y por orden del operador.",
                "La DV-E es simétrica."], 236, yb - 4, altura=1.75, interlineado=1.45)
    return doc


@lamina(20)
def gi20():
    doc, msp, z = hoja(20, "TABLERO TS-GU\nDESPIECE Y LISTA DE EQUIPOS", "S/E")
    titulo_vista(msp, "VISTA EXPLOTADA DEL TS-GU (PUERTA CORRIDA, EQUIPOS ADELANTE DE LA PLACA, S/E)", 27, 274, 2.8)
    meta, caja = _despiece(doc, msp, "TSGU", "X_TSGU", 40, 40, 180, 215)
    subtitulo(msp, "LISTA DE EQUIPOS", 236, 271)
    yb = _lista_piezas(msp, "TSGU", meta, 236, 268, (9, 98, 15, 46))
    bal = E["balance"]
    tsgu = next((a for a in E["alimentadores"] if a["hasta"] == "TS-GU"), {})
    subtitulo(msp, "DATOS DEL TABLERO", 236, yb - 7)
    yb = tabla(msp, 236, yb - 10, [80, 88], [
        ["Dato", "Valor"],
        ["Gabinete", "1200 × 2000 × 400 mm, IP54, con zócalo de 100 mm"],
        ["Ubicación", "sala de control, muro Este (x = 25,65 m)"],
        ["Alimentación", f"Q23 del TG2, {fmt(tsgu.get('S_mm2', 0), 0)} mm², {fmt(tsgu.get('L_m', 0), 1)} m"],
        ["Potencia instalada", f"{fmt(bal['kW_TS_GU'], 2)} kW"],
        ["Corriente de cortocircuito", f"{fmt(E['cortocircuito']['TS-GU_kA'], 2)} kA"],
    ], h_fila=4.0, altura=1.8, alin=["L", "L"])
    notas(msp, ["1. Distribución: arriba entrada y protecciones, al medio variadores,",
                "   abajo mando, PLC, red y borneras; canaletas entre filas.",
                "2. Medidas de los equipos según catálogo (P); verificar con el",
                "   proveedor del tablero el calentamiento (IEC 61439)."],
          236, yb - 7, altura=1.75, interlineado=1.45, titulo="NOTAS")
    return doc


# ===================================================================================== símbolos eléctricos (IEC 60617 simplificados)
def s_interruptor(msp, x, y, rotulo="", h=7.0, diferencial=False):
    """Interruptor termomagnético en una línea vertical que baja (y = borne superior)."""
    linea(msp, (x, y), (x, y - h * 0.3))
    linea(msp, (x, y - h * 0.3), (x + h * 0.32, y - h * 0.72))
    linea(msp, (x, y - h * 0.72), (x, y - h))
    linea(msp, (x - 0.9, y - h * 0.3 - 0.9), (x + 0.9, y - h * 0.3 + 0.9), "FINO")
    linea(msp, (x - 0.9, y - h * 0.3 + 0.9), (x + 0.9, y - h * 0.3 - 0.9), "FINO")
    if diferencial:
        rect(msp, x + 1.6, y - h * 0.65, x + 5.2, y - h * 0.35, "FINO")
        t(msp, "ΔI", (x + 3.4, y - h * 0.5), 1.4, "MIDDLE_CENTER")
    if rotulo:
        t(msp, rotulo, (x - 1.2, y - h * 0.5), 1.7, "MIDDLE_RIGHT")
    return y - h


def s_motor(msp, x, y, tag, kw, r=3.2):
    circulo(msp, (x, y - r), r, "CONTORNO")
    t(msp, "M", (x, y - r + 0.8), 1.8, "MIDDLE_CENTER")
    t(msp, "3~", (x, y - r - 1.2), 1.3, "MIDDLE_CENTER")
    t(msp, f"{tag}\n{fmt(kw, 2)} kW", (x, y - 2 * r - 1.0), 1.5, "TOP_CENTER")


def s_vfd(msp, x, y, w=6.0):
    rect(msp, x - w / 2, y - w, x + w / 2, y, "CONTORNO")
    linea(msp, (x - w / 2, y - w), (x + w / 2, y), "FINO")
    t(msp, "~", (x - w / 4, y - w / 4), 1.6, "MIDDLE_CENTER")
    t(msp, "~", (x + w / 4, y - 3 * w / 4), 1.6, "MIDDLE_CENTER")
    return y - w


def s_contactor(msp, x, y, h=6.0):
    linea(msp, (x, y), (x, y - h * 0.3))
    linea(msp, (x, y - h * 0.3), (x + h * 0.32, y - h * 0.72))
    arco(msp, (x, y - h * 0.3), 0.9, 180, 360)
    linea(msp, (x, y - h * 0.72), (x, y - h))
    return y - h


def s_trafo(msp, x, y, r=5.0):
    circulo(msp, (x, y - r), r)
    circulo(msp, (x, y - 2.6 * r), r)
    return y - 3.6 * r


def barra(msp, x0, x1, y, nombre, h=2.6):
    linea(msp, (x0, y), (x1, y), "CONTORNO", lw=100)
    tn(msp, nombre, (x0 - 1.5, y), h, "MIDDLE_RIGHT")


# ===================================================================================== GI-11 PFD
@lamina(11)
def gi11():
    doc, msp, z = hoja(11, "DIAGRAMA DE FLUJO DEL PROCESO\n(PFD) Y BALANCE", "S/E")
    titulo_vista(msp, "RECORRIDO DEL GUANO, DEL AIRE Y DEL PRODUCTO", 27, 274)
    B = K["balance"]
    g = (139, 90, 43)
    caja = lambda x0, y0, w, h, tit, ren, rgb=None: caja_texto(msp, x0, y0, x0 + w, y0 + h, tit, ren, h=1.8, rgb=rgb)
    # fila del guano
    caja(28, 222, 40, 36, "GALPONES G1 A G4", ["4 × 36.000 gallinas", "20 cintas de piso c/u", "vaciado 1 vez/día"], (196, 214, 230))
    caja(78, 230, 28, 20, "CT-1 a CT-4", ["transversales", "0,55 kW"])
    caja(114, 230, 28, 20, "CI-1 a CI-4", ["inclinadas", "1,1 kW"])
    caja(150, 230, 30, 20, "CE-O / CE-E", ["colectoras", "52,2 m · 1,5 kW"])
    caja(188, 226, 32, 28, "TT-O / TT-E", ["torres con", "desviadora DV", "(A planta / B contenedor)"], (220, 220, 220))
    caja(228, 230, 30, 20, "CP-O / CP-E", ["principales", "13 y 39,8 m"])
    caja(266, 222, 36, 36, "TOLVA PULMÓN TP-01", [f"{fmt(D['tolva_pulmon']['volumen_util_m3'], 0)} m³ útiles", f"{fmt(B['tolva_pulmon_dias'], 1)} días de reserva",
                                                 "4 celdas de carga", "radar LT-101"], (230, 200, 180))
    caja(310, 230, 34, 20, "4 SINFINES", ["M85 a M88, 3 kW", "dosificación FIC-101"])
    caja(352, 230, 40, 20, "CINTA DE ALIMENT. (3)", ["M8 con variador", "al esparcidor M9"])
    for (a, b_) in ((68, 78), (106, 114), (142, 150), (180, 188), (220, 228), (258, 266), (302, 310), (344, 352)):
        flecha(msp, (a, 240), (b_, 240), "CONTORNO", color=g, tam=2.0)
    caja(188, 196, 32, 18, "CONTENEDOR CR", ["20 m³ (solo con el", "secador parado)"])
    flecha(msp, (204, 226), (204, 214), "CONTORNO", color=g, tam=1.8)
    # secador y aire
    caja(300, 150, 92, 52, "SECADOR SC-4 (Rev. F)", ["cinta de 3 pisos de malla AISI 304", "bandas M5, M6 y M7 (1:300)", "aire 100 a 135 °C (TIC-01)",
                                                   "humedad final 15 % (MIC-01)", f"régimen {fmt(B['secador_kg_h_regimen'], 0)} kg/h de guano"], (205, 220, 240))
    flecha_poli(msp, [(372, 230), (372, 210), (372, 202)], "CONTORNO", color=g, tam=2.0)
    caja(212, 150, 40, 28, "HOGAR E INTERCAMB.", ["cáscara de arroz", "parrilla escalonada", "humos → chimenea"], (250, 225, 210))
    caja(212, 116, 40, 20, "SILO DE CÁSCARA", ["70 m³ · sinfín M12"])
    caja(262, 150, 30, 28, "VENTILADORES", ["M1 y M2 (15 kW)", "impulsión de", "aire caliente"])
    flecha(msp, (232, 136), (232, 150), "CONTORNO", color=(200, 130, 40), tam=1.8)
    flecha(msp, (252, 164), (262, 164), "CONTORNO", color=(214, 40, 40), tam=1.8)
    flecha(msp, (292, 164), (300, 164), "CONTORNO", color=(214, 40, 40), tam=1.8)
    caja(300, 100, 30, 24, "CICLÓN", ["separa el polvo", "del aire agotado"])
    caja(338, 100, 26, 24, "LAVADOR", ["de gases", "(Rev. F)"])
    caja(370, 100, 26, 24, "EXTRACTOR", ["M3 (22 kW)", "a la chimenea"])
    flecha(msp, (315, 150), (315, 124), "CONTORNO", color=(46, 139, 87), tam=1.8)
    flecha(msp, (330, 112), (338, 112), "CONTORNO", color=(46, 139, 87), tam=1.8)
    flecha(msp, (364, 112), (370, 112), "CONTORNO", color=(46, 139, 87), tam=1.8)
    # producto
    caja(28, 150, 36, 28, "DESCARGA", ["sinfín M10", "elevador M11"], (220, 238, 214))
    caja(72, 150, 36, 28, "RETENCIÓN F1", ["1 h a ≥ 70 °C", "(sanitización)"], (220, 238, 214))
    caja(116, 150, 36, 28, "ENFRIADOR", ["M40", "< 40 °C"], (220, 238, 214))
    caja(160, 150, 40, 28, "ZARANDA Y ENVASADO", ["M18 a M22, M24", "bolsas y palets"], (220, 238, 214))
    flecha_poli(msp, [(306, 150), (306, 140), (46, 140), (46, 150)], "CONTORNO", color=(11, 138, 67), tam=2.0)
    for a, b_ in ((64, 72), (108, 116), (152, 160)):
        flecha(msp, (a, 164), (b_, 164), "CONTORNO", color=(11, 138, 67), tam=1.8)
    caja(160, 112, 40, 20, "DEPÓSITO E7", ["expedición por P3", "granel por P2"], (220, 238, 214))
    flecha(msp, (180, 150), (180, 132), "CONTORNO", color=(11, 138, 67), tam=1.8)
    # aspiración de la TP-01
    caja(262, 196, 36, 18, "EXTRACTOR M23", ["aspira la tapa de la", "TP-01 al biofiltro"])
    flecha(msp, (284, 222), (284, 214), "CONTORNO", color=(46, 139, 87), tam=1.6)
    # números de corriente
    corrientes = [("1", (73, 240)), ("2", (262, 240)), ("3", (347, 240)), ("4", (296, 164)), ("5", (315, 138)), ("6", (306, 144)),
                  ("7", (204, 220)), ("8", (232, 143)), ("9", (284, 218))]
    for n_, xy in corrientes:
        globo(msp, n_, (xy[0], xy[1] + 4.5), xy, radio=2.2, relleno_rgb=(255, 255, 255))
    m_s = B["secador_kg_h_regimen"] * (1 - K["entradas"]["X_in"]["valor"])
    prod = m_s / (1 - K["entradas"]["X_out"]["valor"])
    filas = [["N°", "Corriente", "Caudal", "Humedad / temp.", "Origen"],
             ["1", "Guano fresco de los galpones", f"{fmt(B['guano_total_kg_dia'] / 1000, 2)} t/día", "72 %", "R"],
             ["2", "Guano a la TP-01 (vaciado de un lado)", f"{fmt(B['flujo_lado_simultaneo_t_h'], 2)} t/h", "72 %", "P"],
             ["3", "Guano dosificado al secador", f"{fmt(B['secador_kg_h_regimen'], 0)} kg/h", "72 %", "P"],
             ["4", "Aire caliente al SC-4", "Rev. F", "100 a 135 °C", "R"],
             ["5", "Aire agotado a tratamiento", "Rev. F", "—", "R"],
             ["6", "Producto seco", f"{fmt(prod, 0)} kg/h · {fmt(B['producto_seco_kg_dia'] / 1000, 2)} t/día", "15 %", "R/P"],
             ["7", "Guano al contenedor de emergencia", "eventual", "72 %", "P"],
             ["8", "Cáscara de arroz al hogar", "Rev. F", "—", "R"],
             ["9", "Aire aspirado de la TP-01", "Rev. F (M23)", "—", "R"],
             ["—", "Agua evaporada", f"{fmt(B['secador_kg_h_regimen'] - prod, 0)} kg/h · {fmt(B['agua_evaporada_kg_dia'] / 1000, 2)} t/día", "—", "R/P"]]
    subtitulo(msp, "CORRIENTES Y BALANCE DE MASA", 28, 98)
    tabla(msp, 28, 95, [8, 66, 52, 30, 14], filas, h_fila=4.2, altura=1.9, alin=["C", "L", "R", "C", "C"])
    leyenda(msp, 232, 95, [("l", g, "Guano húmedo"), ("l", (214, 40, 40), "Aire caliente"), ("l", (46, 139, 87), "Aire agotado / aspiración"),
                          ("l", (11, 138, 67), "Producto seco"), ("l", (200, 130, 40), "Cáscara de arroz")], ancho=8, h=3.8)
    return doc


# ===================================================================================== GI-12 unifilar general
@lamina(12)
def gi12():
    doc, msp, z = hoja(12, "ESQUEMA UNIFILAR GENERAL\nTGBT, TG2 Y ALIMENTADORES", "S/E")
    titulo_vista(msp, "ESQUEMA UNIFILAR GENERAL (3 × 380/220 V · 50 Hz · ECT TT)", 27, 274)
    cc = E["cortocircuito"]
    al = {a["hasta"]: a for a in E["alimentadores"]}
    # MT y transformador
    linea(msp, (40, 268), (40, 258))
    t(msp, "Red de MT 13,2 kV (distribuidora)\nScc 250 MVA (P)", (44, 264), 1.8, "MIDDLE_LEFT")
    y = s_trafo(msp, 40, 256, 4.0)
    t(msp, "Transformador 315 kVA (P)\n13,2/0,4 kV · Dyn11 · ucc 4 %", (48, 248), 1.8, "MIDDLE_LEFT")
    linea(msp, (40, y), (40, 226))
    barra(msp, 40, 402, 226, "TGBT")
    t(msp, f"Icc {fmt(cc['TGBT_kA'], 1)} kA · interruptores ≥ 15 kA", (300, 229), 1.8, "BOTTOM_LEFT")
    salidas = [("QF0", "TBI", "bombas de incendio\n(Rev. F, antes del general)", None),
               ("QF1", "TGF", "secador SC-4\n(Rev. F)", al.get("TGF")),
               ("QF2", "TG2", "auxiliares de la\nplanta (Rev. F mod.)", al.get("TG2"))]
    for k in (1, 2, 3, 4):
        salidas.append((f"QF{2 + k}", f"TS-G{k}", f"galpón G{k}\n(integrador, P)", al.get(f"TS-G{k}")))
    salidas += [("QF7", "DH-O", "depósito de\nhuevos (P)", None), ("QF8", "DH-E", "depósito de\nhuevos (P)", None),
                ("QF9", "SERV.", "agua, alumbrado,\nbioseguridad (P)", None)]
    xs = [52 + 35 * i for i in range(len(salidas))]
    for x, (q, dest, desc, a) in zip(xs, salidas):
        linea(msp, (x, 226), (x, 222))
        yy = s_interruptor(msp, x, 222, q, diferencial=dest not in ("TBI",))
        linea(msp, (x, yy), (x, 190))
        if a:
            t(msp, f"{a['In_A']} A\n{a['S_mm2']} mm² {a['metodo']}\n{fmt(a['L_m'], 0)} m\nΔU {fmt(a['dU_pct'], 2)} %",
              (x + 1.0, 203), 1.5, "MIDDLE_LEFT")
        caja_texto(msp, x - 15, 172, x + 15, 190, dest, desc.split("\n"), h=1.6)
    # TG2 abierto
    xt = xs[2]
    linea(msp, (xt, 172), (xt, 125))
    barra(msp, 34, 150, 125, "TG2")
    t(msp, f"Icc {fmt(cc['TG2_kA'], 2)} kA", (36, 127.5), 1.7, "BOTTOM_LEFT")
    circ = {c["Q"]: c for c in E["TG2_circuitos"]}
    gu = al.get("TS-GU")
    destinos = [("Q21", "TS-ENS", "zaranda, envasado\ny enfriador"), ("Q22", "RESERVA", "(era el lavadero)"),
                ("Q23", "TS-GU", "transporte de guano\n(ver GI-13)"), ("Q24", "VFD M23", "aspiración de\nla TP-01"),
                ("Q25", "TL2", "iluminación del\nsector Este"), ("Q26", "CI", "central de\nincendio"), ("Q27", "TS-VEN", "ventilación\nde la nave")]
    for i, (q, dest, desc) in enumerate(destinos):
        x = 40 + 18.0 * i
        linea(msp, (x, 125), (x, 121))
        yy = s_interruptor(msp, x, 121, q, h=6.0, diferencial=True)
        linea(msp, (x, yy), (x, 96))
        c = circ.get(q)
        if q == "Q23" and gu:
            txt = f"{gu['In_A']} A\n{gu['S_mm2']} mm²\n{fmt(gu['L_m'], 1)} m"
        elif c and q != "Q22":
            txt = f"{c['In_A']} A\n{c['S_mm2']} mm²\n{c['L_m']} m"
        else:
            txt = ""
        if txt:
            t(msp, txt, (x + 1.0, 104), 1.3, "MIDDLE_LEFT")
        caja_texto(msp, x - 8.6, 80, x + 8.6, 96, dest, desc.split("\n"), h=1.25,
                   rgb=(255, 236, 200) if q == "Q23" else None)
    # CCM de los galpones
    for k, x in zip((1, 2, 3, 4), xs[3:7]):
        a = al.get(f"CCM-G{k}")
        linea(msp, (x, 172), (x, 152))
        if a:
            t(msp, f"{a['In_A']} A · {a['S_mm2']} mm² {a['metodo']}\n{fmt(a['L_m'], 0)} m · ΔU {fmt(a['dU_total_pct'], 2)} % total",
              (x + 1, 160), 1.3, "MIDDLE_LEFT")
        caja_texto(msp, x - 13, 134, x + 13, 152, f"CCM-G{k}", ["20 cintas de piso", "CT + CI (VFD)", "ver GI-13"], h=1.4,
                   rgb=(255, 236, 200))
    notas(msp, ["1. ECT TT como en la Rev. F: diferencial en cada salida (tipo B 300 mA donde hay variadores).",
                "2. Los alimentadores de los galpones, depósitos y servicios son del integrador (P): se dan para el balance y la Icc.",
                f"3. Icc: TGF {fmt(cc['TGF_kA'], 2)} kA, TG2 {fmt(cc['TG2_kA'], 2)} kA, TS-GU {fmt(cc['TS-GU_kA'], 2)} kA; "
                "los interruptores del TGF tienen que ser de 6 kA o más.",
                f"4. Demanda: {fmt(E['balance']['kW_demanda'], 1)} kW × {fmt(E['balance']['simultaneidad_tableros'], 2)} (simultaneidad) ÷ "
                f"cos φ {fmt(E['balance']['cos_phi_global'], 2)} = {fmt(E['balance']['kVA_demanda'], 0)} kVA "
                f"({fmt(E['balance']['carga_transformador_pct'], 0)} % del transformador)."],
          232, 128, altura=1.6, titulo="NOTAS")
    return doc


# ===================================================================================== GI-13 unifilar TS-GU y CCM tipo
@lamina(13)
def gi13():
    doc, msp, z = hoja(13, "ESQUEMAS UNIFILARES\nTS-GU Y CCM-G1 (TIPO)", "S/E")
    mot = {m["tag"]: m for m in E["motores"] if m.get("estado") == "nuevo"}
    gu = next(a for a in E["alimentadores"] if a["hasta"] == "TS-GU")
    titulo_vista(msp, "TS-GU - TABLERO DEL TRANSPORTE DE GUANO (sala de control)", 27, 274)
    linea(msp, (40, 268), (40, 262))
    t(msp, f"desde TG2 · Q23: {gu['In_A']} A, 4 × {gu['S_mm2']} mm², {fmt(gu['L_m'], 1)} m", (43, 266), 1.8, "MIDDLE_LEFT")
    yy = s_interruptor(msp, 40, 262, "QG 4P 40 A", diferencial=True)
    t(msp, "diferencial tipo B 300 mA", (47, 257), 1.6, "MIDDLE_LEFT")
    linea(msp, (40, yy), (40, 248))
    barra(msp, 40, 222, 248, "")
    tags = ["M81", "M82", "M83", "M84", "M85", "M86", "M87", "M88", "M89", "M90"]
    for i, tg in enumerate(tags):
        m = mot[tg]
        x = 48 + 17.5 * i
        linea(msp, (x, 248), (x, 244))
        prot = m["proteccion"].split(" ")[1] if m["proteccion"].startswith("interruptor") else "GM"
        yy = s_interruptor(msp, x, 244, h=6.0)
        t(msp, prot if prot != "GM" else m["proteccion"].split(" + ")[0].replace("guardamotor ", "GM "), (x + 1.2, 241), 1.3, "MIDDLE_LEFT")
        if "variador" in m["arranque"]:
            yy = s_vfd(msp, x, yy - 1)
            t(msp, f"G120\n{m['arranque'].split()[3]} kW", (x + 3.5, yy + 3), 1.2, "MIDDLE_LEFT")   # 1,5 kW (coma desde electrica.json)
        else:
            yy = s_contactor(msp, x - 1.2, yy, 5.0)
            s_contactor(msp, x + 1.2, yy + 5.0, 5.0)
            t(msp, "inv.", (x + 3, yy + 2.5), 1.2, "MIDDLE_LEFT")
        linea(msp, (x, yy), (x, 200))
        t(msp, f"4G{fmt(m['S_mm2'], 1 if m['S_mm2'] < 10 else 0)}\n{fmt(m['L_m'], 0)} m\nΔU {fmt(m['dU_total_pct'], 1)} %", (x + 1, 210), 1.25, "MIDDLE_LEFT")
        s_motor(msp, x, 200, tg, m["kW"])
    # auxiliares
    caja_texto(msp, 226, 220, 270, 250, "AUXILIARES", ["SITOP 24 V 20 A + respaldo", "UPS 1 kVA", "PLC-01 S7-1500F",
                                                      "switch XC208 (fibra)", "luz de galerías y torres", "tomas con ΔI 30 mA"], h=1.6)
    linea(msp, (222, 248), (248, 248))
    linea(msp, (248, 248), (248, 250))
    # CCM tipo
    titulo_vista(msp, "CCM-G1 - CENTRO DE CONTROL DE MOTORES DEL GALPÓN (tipo para G1 a G4)", 27, 172)
    a = next(x for x in E["alimentadores"] if x["hasta"] == "CCM-G1")
    linea(msp, (40, 166), (40, 160))
    t(msp, f"desde TS-G1: {a['In_A']} A, 4 × {a['S_mm2']} mm² enterrado, {fmt(a['L_m'], 0)} m", (43, 164), 1.8, "MIDDLE_LEFT")
    yy = s_interruptor(msp, 40, 160, "QG bloqueable", diferencial=True)
    linea(msp, (40, yy), (40, 146))
    barra(msp, 40, 222, 146, "")
    grupos = [("M101 a M120", "20 cintas de piso", 1.1, "GM 2,2–3,2 A", "directo"), ("M121", "cinta transversal CT-1", 0.55, "GM 1,1–1,6 A", "directo"),
              ("M122", "cinta inclinada CI-1", 1.1, "C6 + ΔI tipo B", "G120C 1,1 kW")]
    for i, (tg, nom, kw, prot, arr) in enumerate(grupos):
        x = 60 + 50 * i
        linea(msp, (x, 146), (x, 142))
        yy = s_interruptor(msp, x, 142, h=6.0)
        t(msp, prot, (x + 1.2, 139), 1.4, "MIDDLE_LEFT")
        if arr == "directo":
            yy = s_contactor(msp, x, yy, 6.0)
        else:
            yy = s_vfd(msp, x, yy - 1)
            t(msp, arr, (x + 3.5, yy + 3), 1.3, "MIDDLE_LEFT")
        linea(msp, (x, yy), (x, 112))
        m = mot[tg.split()[0]]
        t(msp, f"4G{fmt(m['S_mm2'], 1 if m['S_mm2'] < 10 else 0)} · {fmt(m['L_m'], 0)} m\nΔU {fmt(m['dU_total_pct'], 2)} % total", (x + 1, 120), 1.35, "MIDDLE_LEFT")
        s_motor(msp, x, 112, tg if "a" not in tg else "×20", kw)
        t(msp, nom, (x, 96), 1.5, "TOP_CENTER")
    caja_texto(msp, 210, 120, 270, 144, "RIO-G1", ["ET 200SP con F-DI", "20 SS + 4 botoneras", "switch de fibra", "KTP400 en la puerta"], h=1.6)
    # planilla de circuitos del TS-GU
    filas = [["Motor", "Equipo", "kW", "In (A)", "Arranque", "Cable", "L (m)", "ΔU tot. %"]]
    for tg in tags:
        m = mot[tg]
        filas.append([tg, m["nombre"].replace("Actuador de la compuerta desviadora", "Actuador").replace(" de la TP-01", ""),
                      fmt(m["kW"], 2), fmt(m["In_A"], 2), "VFD" if "variador" in m["arranque"] else "inversor",
                      f"4G{fmt(m['S_mm2'], 1)}" + (" apant." if "apantallado" in m["cable"] else ""),
                      fmt(m["L_m"], 1), fmt(m["dU_total_pct"], 2)])
    subtitulo(msp, "CIRCUITOS DEL TS-GU", 276, 274)
    tabla(msp, 276, 271, [11, 40, 9, 11, 13, 20, 11, 15], filas, h_fila=4.0, altura=1.7, alin=["C", "L", "R", "R", "C", "L", "R", "R"])
    return doc


# ===================================================================================== GI-15 arquitectura de automatización
@lamina(15)
def gi15():
    doc, msp, z = hoja(15, "ARQUITECTURA DE\nAUTOMATIZACIÓN Y RED", "S/E")
    titulo_vista(msp, "PLC, PERIFERIAS, VARIADORES, PANTALLAS Y RED PROFINET", 27, 274)
    io = E["io"]
    fo, cu = (230, 120, 30), (40, 140, 60)

    def nodo(x0, y0, w, h, tit, ren, rgb=None):
        return caja_texto(msp, x0, y0, x0 + w, y0 + h, tit, ren, h=1.6, rgb=rgb)
    nodo(150, 226, 70, 40, "SALA DE CONTROL · TS-GU", ["PLC-01 S7-1500F (CPU 1515F-2 PN)", "switch SCALANCE XC208 (MRP)",
                                                      "TP1200 Comfort · WinCC", "router VPN SCALANCE M", "UPS 1 kVA"], (226, 232, 238))
    nodo(232, 236, 54, 26, "PLC-02 SECADOR SC-4", ["S7-1200 CPU 1214C (Rev. F)", "I-device del PLC-01", "KTP700 (Rev. F)"], (226, 232, 238))
    linea(msp, (220, 249), (232, 249), "CONTORNO", color=cu, lw=50)
    nodo(100, 226, 42, 26, "8 VARIADORES G120", ["CE-O, CE-E, CP-O, CP-E", "sinfines M85 a M88", "STO por PROFIsafe"])
    linea(msp, (142, 239), (150, 239), "CONTORNO", color=cu, lw=50)
    y1_, y2_, y3_ = 180, 134, 88                       # filas de periferias (cajas de 30 mm de alto)
    rios = [("RIO-TP", 160, y1_, "recepción TP-01", "KTP700 · SIWAREX"), ("RIO-O", 60, y1_, "torre TT-O", "KTP400"),
            ("RIO-E", 260, y1_, "torre TT-E", "KTP400"), ("RIO-G2", 60, y2_, "CCM-G2", "KTP400 · G120C"),
            ("RIO-G1", 60, y3_, "CCM-G1", "KTP400 · G120C"), ("RIO-G3", 260, y2_, "CCM-G3", "KTP400 · G120C"),
            ("RIO-G4", 260, y3_, "CCM-G4", "KTP400 · G120C")]
    pos = {}
    for rid, x, y, ubic, hmi in rios:
        s_ = io.get(rid, {}).get("señales", {})
        ren = [ubic, hmi, f"DI {s_.get('DI', 0)} · F-DI {s_.get('F-DI', 0)}", f"DQ {s_.get('DQ', 0)} · AI {s_.get('AI', 0)}"]
        nodo(x, y, 48, 30, rid + " (ET 200SP)", ren, (255, 244, 220))
        pos[rid] = (x, y)

    def via(pts):
        poli(msp, pts, "CONTORNO", color=fo, lw=60)
    via([(185, 226), (185, y1_ + 30)])
    via([(160, y1_ + 15), (108, y1_ + 15)])
    via([(84, y1_), (84, y2_ + 30)])
    via([(84, y2_), (84, y3_ + 30)])
    via([(60, y3_ + 15), (40, y3_ + 15), (40, 259), (150, 259)])          # pasa sobre la caja de los variadores
    via([(208, y1_ + 15), (260, y1_ + 15)])
    via([(284, y1_), (284, y2_ + 30)])
    via([(284, y2_), (284, y3_ + 30)])
    via([(308, y3_ + 15), (330, y3_ + 15), (330, 232), (220, 232)])
    t(msp, "anillo Oeste (MRP)", (42, 165), 1.8, "MIDDLE_LEFT", rotacion=90, color=fo)
    t(msp, "anillo Este (MRP)", (328, 165), 1.8, "MIDDLE_RIGHT", rotacion=90, color=fo)
    t(msp, "las vueltas de los anillos van por un cable separado (otro lado de la galería)", (185, 126), 1.8, "MIDDLE_CENTER")
    leyenda(msp, 120, 110, [("l", fo, "fibra óptica multimodo (PROFINET, anillo MRP)"), ("l", cu, "PROFINET cobre"),
                           ("r", (255, 244, 220), "periferia ET 200SP con módulos F-DI"), ("r", (226, 232, 238), "controladores y supervisión")], ancho=8, h=3.9)
    notas(msp, ["1. Seguridad: paradas de emergencia, cables de parada, registros y estación de bloqueo por F-DI y PROFIsafe (SIL 2 / PL d).",
                "2. Pérdida de comunicación con una periferia: su zona pasa a estado seguro; el anillo mantiene el resto.",
                "3. El PLC-02 de la Rev. F sigue controlando el SC-4 (TIC-01, MIC-01) y recibe la dosificación del PLC-01."],
          28, 40, altura=1.8)
    return doc


# ===================================================================================== GI-16 GRAFCET y enclavamientos
@lamina(16)
def gi16():
    doc, msp, z = hoja(16, "SECUENCIA (GRAFCET)\nY ENCLAVAMIENTOS", "S/E")
    titulo_vista(msp, "GRAFCET (IEC 60848) CON LOS 13 PASOS DE LA CONSIGNA", 27, 274, 3.0)
    sec = {sp["n"]: sp for sp in E["automatizacion"]["secuencia"]}
    W = 8.0                                                    # lado del recuadro de cada etapa

    def etapa(x, y, num, texto, accion=None, inicial=False, ancho=96):
        """Etapa con su número y, a la derecha, la acción asociada. (x, y) = vértice superior izquierdo."""
        if inicial:
            rect(msp, x - 0.9, y - W - 0.9, x + W + 0.9, y + 0.9, "CONTORNO")
        rect(msp, x, y - W, x + W, y, "CONTORNO")
        tn(msp, str(num), (x + W / 2, y - W / 2), 2.4 if len(str(num)) < 3 else 1.9, "MIDDLE_CENTER")
        linea(msp, (x + W, y - W / 2), (x + W + 2, y - W / 2))
        rect(msp, x + W + 2, y - W, x + W + 2 + ancho, y, "FINO")
        tn(msp, texto, (x + W + 3, y - 1.0), 1.35, "TOP_LEFT")
        if accion:
            t(msp, accion, (x + W + 3, y - 3.9), 1.05, "TOP_LEFT", ancho=ancho - 2)

    def transicion(x, y, texto):
        """Receptividad: trazo horizontal sobre la línea de enlace, con la condición a la derecha."""
        linea(msp, (x + W / 2 - 2.6, y), (x + W / 2 + 2.6, y), "CONTORNO", lw=50)
        t(msp, texto, (x + W / 2 + 4, y), 1.15, "MIDDLE_LEFT", ancho=98)

    def cadena(x, y, pasos, paso_y=13.2):
        """pasos: [(num, nombre, acción, receptividad de salida, inicial)]; devuelve la y final de la última receptividad."""
        for k, (num, nom, acc, rec, ini_) in enumerate(pasos):
            yy = y - k * paso_y
            etapa(x, yy, num, nom, acc, ini_)
            linea(msp, (x + W / 2, yy - W), (x + W / 2, yy - paso_y))
            transicion(x, yy - W - (paso_y - W) / 2, rec)
        return y - len(pasos) * paso_y

    def retorno(x, y_bajo, y_alto, dx=6.0):
        """Enlace de vuelta a la etapa inicial, por la izquierda, con flecha hacia arriba."""
        xl = x - dx
        poli(msp, [(x + W / 2, y_bajo), (xl, y_bajo), (xl, y_alto + 2.5), (x + W / 2, y_alto + 2.5)], "CONTORNO")
        flecha(msp, (xl, y_alto - 6), (xl, y_alto - 1), "CONTORNO", tam=1.6)
        linea(msp, (x + W / 2, y_alto + 2.5), (x + W / 2, y_alto))

    # G1: transporte y recepción
    subtitulo(msp, "G1 · TRANSPORTE Y RECEPCIÓN (un galpón por vez en cada lado)", 28, 263, 2.2)
    x1, y1 = 40.0, 257.0
    g1 = [(0, "Reposo", "planta del lado sin pedidos ni fallas", "pedido de vaciado de un galpón (horario o manual) · LIC-101 < 80 %", True),
          (1, sec[1]["etapa"], "el PLC-01 acepta el pedido si la TP-01 tiene lugar (LT-101, WT-101 a 104)", "pedido aceptado", False),
          (4, sec[4]["etapa"], "F-DI sanos, registros cerrados, M23 en marcha, DV en A, comunicación sana", "todos los permisivos cumplidos", False),
          (2, sec[2]["etapa"], "prearranque 10 s; arranque de aguas abajo hacia aguas arriba: CP → CE → CI → CT", "todas las cintas de la ruta con velocidad (SSL)", False),
          (3, sec[3]["etapa"], "velocidad, desvío (ZS), chute (LSH) y variadores sin falla durante 5 s", "ruta verificada", False),
          (5, sec[5]["etapa"], "cintas de piso de un piso por vez (4 filas); el guano entra a la TP-01", "galpón vaciado o LSHH-101 (TP-01 alta-alta)", False),
          ("12a", "Parada controlada de la ruta", "se paran las cintas de aguas arriba hacia aguas abajo con su tiempo de vaciado", "ruta detenida y vacía", False)]
    y_fin = cadena(x1, y1, g1)
    retorno(x1, y_fin, y1)

    # G2: secado (el PLC-02 de la Rev. F conduce el secador; el PLC-01 dosifica)
    subtitulo(msp, "G2 · SECADO Y PRODUCTO (pasos 8 a 11 en paralelo)", 28, 157, 2.2)
    x2, y2 = 40.0, 151.0
    g2 = [("S0", "Secador en reposo", "PLC-02 sin fallas, hogar apagado", "orden de secado · TP-01 por encima de LSL-101", True),
          (7, sec[7]["etapa"], "extractor M3, ventiladores M1-M2, barrido, piloto a GLP, llama (BE-01), cáscara M12", "aire ≥ consigna − 10 °C", False),
          (6, sec[6]["etapa"], "sinfines M85 a M88: FIC-101 a la consigna (pérdida de peso; volumétrico mientras se llena la TP-01)", "caudal estable ± 5 % durante 2 min", False)]
    y_fin2 = cadena(x2, y2, g2)
    # divergencia en Y (doble trazo) con las etapas 8 a 11
    yd = y_fin2 - 1.5                                         # debajo de la receptividad del paso 6
    linea(msp, (x2 + W / 2, y_fin2), (x2 + W / 2, yd))
    linea(msp, (x2 - 2, yd), (x2 + 132, yd), "CONTORNO")
    linea(msp, (x2 - 2, yd - 1.0), (x2 + 132, yd - 1.0), "CONTORNO")
    par = [(8, "Regulación", "TIC-01, MIC-01, FIC-101, presión de cámara"), (9, "Monitoreo", "alarmas, tendencias, VPN"),
           (10, "Descarga", "M10, M11, F1 ≥ 70 °C 1 h, enfriador"), (11, "Producto", "zaranda M18, ensacado, granel")]
    for k, (num, nom, acc) in enumerate(par):
        xx = x2 + k * 34.0
        linea(msp, (xx + W / 2, yd - 1.0), (xx + W / 2, yd - 3.0))
        rect(msp, xx, yd - 3.0 - W, xx + W, yd - 3.0, "CONTORNO")
        tn(msp, str(num), (xx + W / 2, yd - 3.0 - W / 2), 2.4, "MIDDLE_CENTER")
        tn(msp, nom, (xx + W + 1.2, yd - 4.0), 1.25, "TOP_LEFT")
        t(msp, acc, (xx + W + 1.2, yd - 6.4), 0.95, "TOP_LEFT", ancho=23)
        linea(msp, (xx + W / 2, yd - 3.0 - W), (xx + W / 2, yd - 3.0 - W - 4.0))
    yc = yd - 3.0 - W - 4.0
    linea(msp, (x2 - 2, yc), (x2 + 132, yc), "CONTORNO")
    linea(msp, (x2 - 2, yc - 1.0), (x2 + 132, yc - 1.0), "CONTORNO")
    linea(msp, (x2 + W / 2, yc - 1.0), (x2 + W / 2, yc - 5.0))
    transicion(x2, yc - 3.0, "orden de parada del secado o LSL-101 (TP-01 baja)")
    g2b = [("12b", "Parada controlada del secado", "corta la dosificación; las bandas vacían la cámara; hogar apagado con post-barrido; ventiladores hasta < 60 °C",
            "cámara vacía y aire < 60 °C", False)]
    y_fin3 = cadena(x2, yc - 5.0, g2b)
    retorno(x2, y_fin3, y2)

    # G3: seguridad con forzado (manejo de fallas)
    subtitulo(msp, "G3 · SEGURIDAD (forzado de G1 y G2)", 28, 52, 2.2)
    g3 = [("13R", "Vigilancia", "PLC-01 F y PROFIsafe sanos", "falla de categoría 0, parada de emergencia, cable de parada o pérdida de comunicación", True),
          (13, sec[13]["etapa"], "F/G1:\\{0\\} y F/G2:\\{12b\\}; STO en los variadores; alarma y registro; la causa en pantalla",
           "falla eliminada y reconocida por el operador", False)]
    y_fin4 = cadena(40.0, 46.0, g3, paso_y=12.0)
    retorno(40.0, y_fin4, 46.0)
    # matriz de enclavamientos
    filas = [["Condición", "Efecto", "Señal"]]
    for r in E["automatizacion"]["enclavamientos"]:
        filas.append([r["condicion"], r["efecto"], r["senal"]])
    subtitulo(msp, "MATRIZ DE ENCLAVAMIENTOS (la planta no arranca con condiciones inseguras)", 186, 274)
    yb = tabla(msp, 186, 271, [92, 92, 34], filas, h_fila=4.6, altura=1.6, alin=["L", "L", "C"])
    filas = [["Falla", "Acción automática", "Acción del operador"]]
    for r in E["automatizacion"]["fallas"]:
        filas.append([r["falla"], r["accion_automatica"], r["accion_del_operador"]])
    subtitulo(msp, "TABLA DE FALLAS", 186, yb - 7)
    yb = tabla(msp, 186, yb - 10, [64, 78, 76], filas, h_fila=4.3, altura=1.5, alin=["L", "L", "L"])
    filas = [["Lazo", "Variable", "Actuador", "Consigna"]]
    for r in E["automatizacion"]["lazos"]:
        filas.append([r["tag"], r["variable"], r["actuador"], r["consigna"]])
    subtitulo(msp, "LAZOS DE CONTROL", 186, yb - 7)
    tabla(msp, 186, yb - 10, [20, 62, 84, 52], filas, h_fila=4.3, altura=1.5, alin=["C", "L", "L", "L"])
    return doc


# ===================================================================================== GI-17 instrumentación y E/S
@lamina(17)
def gi17():
    import re
    doc, msp, z = hoja(17, "INSTRUMENTACIÓN\nLISTA DE E/S POR PERIFERIA", "S/E")
    titulo_vista(msp, "INSTRUMENTOS DEL TRANSPORTE Y LA RECEPCIÓN", 27, 274, 2.8)
    ins = [i for i in E["instrumentos"] if i["alcance"] == "planta / transporte"]
    grupos = {}
    for i in ins:
        pref = re.match(r"[A-Z]+", i["tag"]).group(0)
        grupos.setdefault((i["periferia"], pref, i["tipo"], i["senal"]), []).append(i)
    orden_rio = ["RIO-TP", "RIO-O", "RIO-O / RIO-TP", "RIO-E", "RIO-E / RIO-TP", "RIO-G1", "RIO-G2", "RIO-G3", "RIO-G4"]
    filas = []
    for (rio, pref, tipo, senal), lst in sorted(grupos.items(), key=lambda kv: (orden_rio.index(kv[0][0]) if kv[0][0] in orden_rio
                                                                                else 99, kv[0][1], kv[0][2])):
        tags = sorted((i["tag"] for i in lst), key=lambda x: [int(c) if c.isdigit() else c for c in re.split(r"(\d+)", x)])
        txt = ", ".join(tags) if len(tags) <= 2 else f"{tags[0]} … {tags[-1]} ({len(tags)})"
        filas.append([txt, tipo[:44], sum(int(i["cantidad"]) for i in lst), senal, rio, fmt(sum(i["L_total_m"] for i in lst), 0)])
    enc = ["Tags", "Tipo", "Cant.", "Señal", "Periferia", "Cable (m)"]
    anchos, alin = [36, 50, 9, 12, 19, 14], ["L", "L", "R", "C", "C", "R"]
    h = 3.65
    n1 = min(len(filas), int((271 - 27) / h) - 1)              # la primera columna baja hasta el pie de la hoja
    yb = tabla(msp, 28, 271, anchos, [enc] + filas[:n1], h_fila=h, altura=1.5, alin=alin)
    if filas[n1:]:
        yb = tabla(msp, 172, 271, anchos, [enc] + filas[n1:], h_fila=h, altura=1.5, alin=alin)
    tot = sum(int(i["cantidad"]) for i in ins)
    t(msp, f"Total: {tot} instrumentos en {len(ins)} tags de la planta y el transporte; los de los galpones y depósitos "
           f"son del controlador de cada galpón.", (28, yb - 3), 1.6, "TOP_LEFT")
    if not filas[n1:]:
        por_tipo = {}
        for i in ins:
            k = (i["tipo"], i["senal"])
            a_ = por_tipo.setdefault(k, [0, 0, 0.0])
            a_[0] += int(i["cantidad"])
            a_[1] += 1
            a_[2] += i["L_total_m"]
        res = [["Tipo", "Señal", "Tags", "Cant.", "Cable (m)"]] + [
            [tp_[:40], sn_, n_t, n_c, fmt(L_, 0)] for (tp_, sn_), (n_c, n_t, L_) in sorted(por_tipo.items(), key=lambda kv: -kv[1][0])]
        res.append(["Total", "", len(ins), tot, fmt(sum(i["L_total_m"] for i in ins), 0)])
        subtitulo(msp, "RESUMEN POR TIPO", 176, 271)
        tabla(msp, 176, 268, [58, 14, 12, 12, 18], res, h_fila=3.9, altura=1.5, alin=["L", "C", "R", "R", "R"], negrita_ultima=True)
    io = E["io"]
    filas = [["Periferia", "DI", "F-DI", "DQ", "AI", "SIWAR.", "Var. TS-GU", "Módulos (+20 % reserva)"]]
    for rid, v in io.items():
        s_ = v["señales"]
        mods = ", ".join(f"{k} {n}" for k, n in v["modulos_ET200SP_con_20pct_reserva"].items())
        filas.append([rid, s_.get("DI", 0), s_.get("F-DI", 0), s_.get("DQ", 0), s_.get("AI", 0), s_.get("SIWAREX", 0),
                      s_.get("PROFINET (variadores)", 0), mods])
    subtitulo(msp, "ENTRADAS Y SALIDAS POR PERIFERIA", 300, 271)
    yb = tabla(msp, 300, 268, [16, 8, 9, 8, 7, 11, 11, 36], filas, h_fila=4.2, altura=1.5,
               alin=["C", "R", "R", "R", "R", "R", "R", "L"])
    notas(msp, ["SSL: velocidad cero · ZS: desvío de banda",
                "LSH: chute lleno · HS: cable de parada",
                "XA: baliza y sirena de prearranque",
                "LT-101: radar · LSHH/LSL-101: horquillas",
                "WT-101 a 104: celdas de carga (SIWAREX)",
                "ZSA/ZSB: posición de la desviadora",
                "ZS-REG: registros de la TP-01",
                "Q-M: seccionadores · TT: botoneras de torre",
                "P: pulsadores de parada de la nave",
                "SS-Mxxx: velocidad de las cintas de piso"], 300, yb - 7, altura=1.75, interlineado=1.5, titulo="REFERENCIAS")
    return doc


# ===================================================================================== ejecución
def main(nums=None):
    nums = nums or sorted(LAMINAS)
    pdfs = []
    for n in nums:
        doc = LAMINAS[n]()
        pdfs.append(exportar(doc, n))
    if set(nums) == set(LAMINAS):
        unir_pdfs([str(CARPETA / "pdf" / f"GI-{n:02d}.pdf") for n in sorted(LAMINAS)], str(CARPETA / "Planos_GI.pdf"))
        with zipfile.ZipFile(CARPETA / "dxf" / "Planos_DXF_GI.zip", "w", zipfile.ZIP_DEFLATED) as z:
            for n in sorted(LAMINAS):
                z.write(CARPETA / "dxf" / f"GI-{n:02d}.dxf", f"GI-{n:02d}.dxf")
            for img in (CARPETA / "dxf" / "img").glob("*") if (CARPETA / "dxf" / "img").exists() else []:
                z.write(img, f"img/{img.name}")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or None)
