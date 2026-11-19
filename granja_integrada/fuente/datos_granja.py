"""Datos únicos de la granja avícola integrada con planta central de secado de guano.

Es la única fuente de medidas del proyecto nuevo: el modelo 3D, los planos, los renders y los cálculos leen
`datos/granja.json`, que se genera con este programa. Si cambia una medida, se cambia acá y se regenera todo.

Distribución (pedido de Gabriel, 19/11/2026): en una fila de Oeste a Este, galpón G1, galpón G2, planta de secado,
galpón G3 y galpón G4. Los galpones van uno al lado del otro (paralelos, eje Norte-Sur, como el par de San Jorge) y
las cintas de guano están conectadas: una cinta colectora por lado pasa por la cabecera Sur de los dos galpones y
entra a la planta. Los huevos y el alimento quedan del lado Norte (zona limpia); el guano y la planta, del lado Sur
(zona sucia).

Coordenadas en metros. Origen en el vértice Sudoeste de la nave de proceso, igual que el proyecto anterior
(`layout_planta.json`), para usar sin cambios las posiciones de la planta Rev. F. x al Este, y al Norte, z arriba.

Tipo de dato (ver docs/01_auditoria.md): R proyecto de la secadora Rev. F, S TP San Jorge o dato de Gabriel,
V verificado con fuente, P preliminar de este rediseño, H hipótesis.

    python datos_granja.py          # -> ../datos/granja.json
"""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BASE = json.loads((RAIZ / "datos" / "base" / "layout_planta_revF.json").read_text(encoding="utf-8"))
SALIDA = RAIZ / "datos" / "granja.json"

# =============================================================================== galpones de postura
GALPON = {
    "L": 100.0,                                 # S: 100 m de largo (San Jorge)
    "A": 10.5,                                  # P: con 36.000 gallinas no entran en 6 m (dato satelital de San Jorge)
    "eje_par": 31.0,                            # S: ejes de los galpones de un par a unos 31 m
    "e_muro": 0.10, "zocalo": 0.50,             # P: zócalo de H°A° y panel sándwich
    "h_alero": 4.20, "pendiente_deg": 20.0,     # P: 5 pisos de jaulas + carro de alimentación
    "paso_porticos": 5.0,                       # P: pórticos de perfil C en cajón cada 5 m
    "cabecera_huevos": 2.80,                    # P: recolectores de huevos y pasillo de servicio (Norte)
    "cabecera_guano": 2.60,                     # P: accionamientos de las cintas y cinta transversal (Sur)
    "aves": 36000,                              # S: dato de Gabriel (19/11/2026)
}
JAULAS = {                                      # P (celda de referencia: Big Dutchman SuperTripleDeck, V)
    "filas": 4, "pisos": 5,
    "celda_ancho": 0.610, "celda_prof": 0.483, "celda_alto": 0.460,
    "aves_por_celda": 6,                        # 490 cm² por ave (V: ficha del fabricante)
    "celdas_por_modulo": 5, "modulos_por_fila": 30,
    "paso_pisos": 0.620, "z_piso1": 0.35,
    "ancho_fila": 1.30,                         # 2 × 0,483 de jaula + comederos + separador
    "cinta_guano_ancho": 1.25, "cinta_guano_v_m_min": 10.0,   # V (rango 10-12 m/min de proveedores)
    "cinta_huevos_ancho": 0.10,
}
JAULAS["modulo"] = round(JAULAS["celda_ancho"] * JAULAS["celdas_por_modulo"], 3)        # 3,05 m
JAULAS["largo_fila"] = round(JAULAS["modulo"] * JAULAS["modulos_por_fila"], 2)          # 91,5 m
JAULAS["celdas_por_lado"] = JAULAS["celdas_por_modulo"] * JAULAS["modulos_por_fila"]    # 150
JAULAS["aves_por_fila"] = JAULAS["celdas_por_lado"] * 2 * JAULAS["pisos"] * JAULAS["aves_por_celda"]
JAULAS["aves_por_galpon"] = JAULAS["aves_por_fila"] * JAULAS["filas"]                   # 36.000
_int = GALPON["A"] - 2 * GALPON["e_muro"]
JAULAS["pasillo"] = round((_int - JAULAS["filas"] * JAULAS["ancho_fila"]) / (JAULAS["filas"] + 1), 3)
assert JAULAS["aves_por_galpon"] == GALPON["aves"]

# ------------------------------------------------------------------------------- ubicación (P)
SEP_NAVE = 30.0                       # m libres entre la nave y el galpón más cercano (camino, playón e incendio)
Y_COLECTORA = 14.6                    # eje de las cintas colectoras: entran a la nave sobre la tolva pulmón
Z_COLECTORA = 6.20                    # plano de banda de las colectoras (5,6 m libres sobre los caminos)
CI_TRAMO = 9.20                       # recorrido horizontal de la cinta inclinada desde la cinta transversal
Y_SUR_GALPONES = Y_COLECTORA + CI_TRAMO - 1.15   # cabecera Sur de los galpones
_A2 = GALPON["A"] / 2
EJES_X = {"G2": -SEP_NAVE - _A2, "G1": -SEP_NAVE - _A2 - GALPON["eje_par"],
          "G3": 33.0 + SEP_NAVE + _A2, "G4": 33.0 + SEP_NAVE + _A2 + GALPON["eje_par"]}


def _galpones():
    g = []
    for gid in ("G1", "G2", "G3", "G4"):
        x = EJES_X[gid]
        lado = "O" if x < 16.5 else "E"
        g.append({"id": gid, "lado": lado, "x": round(x, 3), "x0": round(x - _A2, 3), "x1": round(x + _A2, 3),
                  "y0": round(Y_SUR_GALPONES, 3), "y1": round(Y_SUR_GALPONES + GALPON["L"], 3),
                  "cab_guano": "S", "cab_huevos": "N",
                  "posicion": "exterior" if gid in ("G1", "G4") else "interior",
                  "hacia_planta": 1 if lado == "O" else -1})
    return g


# =============================================================================== depósitos de huevos (copia del de San Jorge)
DEPOSITO = {"L": 21.8, "A": 16.0, "h_libre": 5.0, "e_muro": 0.20,      # S: 21,8 × 16,0 por fuera, alto libre 5,0 m
            "riel": 17.0, "lugares": 24, "estaciones_x": [7.5, 10.1],   # S: transelevador, 24 lugares, E1 y E2
            "muelle_h": 1.25, "palets_dia": 7.2}                        # S: 7,2 palets por día por par de galpones


def _depositos(galpones):
    d = []
    for lado in ("O", "E"):
        par = [g for g in galpones if g["lado"] == lado]
        xm = sum(g["x"] for g in par) / 2
        y0 = par[0]["y1"] + 4.0                                         # P: paso de las cintas de huevos
        # S: el depósito de San Jorge tiene el portón en un lado corto (16 m) y el pasillo del transelevador a lo largo
        # (21,8 m); acá se gira para que el portón mire al camino Norte (limpio) y el pasillo vaya de Norte a Sur
        d.append({"id": "DH-" + lado, "lado": lado, "x0": round(xm - DEPOSITO["A"] / 2, 3),
                  "x1": round(xm + DEPOSITO["A"] / 2, 3), "y0": round(y0, 3), "y1": round(y0 + DEPOSITO["L"], 3),
                  "porton": "N", "galpones": [g["id"] for g in par]})
    return d


# =============================================================================== transporte de guano (P)
Z_CT = -0.30          # cinta transversal en canal de H° (piso del canal -0,95): la cinta del piso 1 de las jaulas
                      # descarga a +0,27, así que la transversal tiene que quedar bajo el nivel del piso
Z_CI_COLA = -0.95     # tramo horizontal de carga de la cinta inclinada (en L), en el foso (piso -1,65): pasa 0,17 m
                      # bajo el tambor de cabeza de la transversal y dobla hacia arriba en el muro Sur
DZ_CI_CE = 0.90       # la cabeza de la inclinada queda 0,90 m sobre la banda de la colectora (chute y faldones)
DY_DESCARGA = 0.35    # los cabezales terminan 0,35 m antes del eje de la cinta que reciben (la parábola cae al centro)
Z_CP_COLA = 4.40      # cola de las cintas principales en las torres (bajo la compuerta desviadora)
Z_CP_O = 5.40         # cabezales sobre la tapa de la tolva pulmón (+4,55): 0,85 m para el chute
Z_CP_E = 5.40         # la principal Este cruza la nave a +4,8/+5,1: sobre el ducto caliente (+3,8), la baranda de la
                      # zaranda (+4,1) y por debajo del ducto de aire agotado (+6,05)
X_TT = {"O": -10.0, "E": 43.0}
X_DESCARGA = {"O": 2.0, "E": 4.2}     # cabezales sobre la tolva pulmón


def _transporte(galpones):
    t = []
    for g in galpones:
        n = int(g["id"][1])
        sig = g["hacia_planta"]
        x_ci = g["x"] + sig * (_A2 - 0.90)                  # la cinta transversal descarga del lado de la planta
        y_ct = g["y0"] + 2.15                               # 0,45 m antes del extremo de las filas de jaulas
        x_ct0 = g["x"] - sig * (_A2 - 0.85)                 # el tensor de cola queda adentro del muro
        t.append({"id": f"CT-{n}", "tipo": "transversal", "galpon": g["id"], "ancho": 0.65,
                  "p0": [round(x_ct0, 3), y_ct, Z_CT], "p1": [round(x_ci - sig * DY_DESCARGA, 3), y_ct, Z_CT],
                  "nota": "dentro del galpón, en canal de H° con rejilla bajo el extremo de las 20 cintas de las jaulas"})
        y_cab = Y_COLECTORA + DY_DESCARGA
        z_cab = Z_COLECTORA + DZ_CI_CE
        y_cola, y_quiebre = y_ct + 0.80, g["y0"] + 0.05                 # tramo horizontal de carga de 2,9 m
        ang = round(math.degrees(math.atan2(z_cab - Z_CI_COLA, y_quiebre - y_cab)), 1)
        p0 = [round(x_ci, 3), round(y_cola, 3), Z_CI_COLA]
        pq = [round(x_ci, 3), round(y_quiebre, 3), Z_CI_COLA]
        p1 = [round(x_ci, 3), round(y_cab, 3), round(z_cab, 3)]
        t.append({"id": f"CI-{n}", "tipo": "inclinada", "galpon": g["id"], "ancho": 0.50, "ang": ang,
                  "p0": p0, "p1": p1, "trazado": [p0, pq, p1],
                  "foso": {"z_fondo": -1.65, "y0": round(g["y0"] - 1.30, 3), "y1": round(y_cola + 0.60, 3),
                           "x0": round(min(x_ci - sig * 1.10, x_ci + sig * 0.65), 3),
                           "x1": round(max(x_ci - sig * 1.10, x_ci + sig * 0.65), 3)},
                  "banda": "goma EP 400/3 con bordes ondulados de 80 mm y tacos (como la cinta 3 de la Rev. F)"})
    for lado in ("O", "E"):
        par = sorted([g for g in galpones if g["lado"] == lado], key=lambda g: abs(g["x"] - 16.5), reverse=True)
        ext = par[0]
        sig = ext["hacia_planta"]
        x_cola = ext["x"] + sig * (_A2 - 0.90) - sig * 1.2
        num = "1" if lado == "O" else "2"
        t.append({"id": f"CE-{lado}", "tipo": "colectora", "ancho": 0.65,
                  "p0": [round(x_cola, 3), Y_COLECTORA, Z_COLECTORA], "p1": [X_TT[lado] - sig * 0.9, Y_COLECTORA, Z_COLECTORA],
                  "recibe": [g["id"] for g in par],
                  "nota": f"colectora {num}: recibe las cintas inclinadas de los dos galpones; artesa a 20°, cubierta, pasarela"})
        if lado == "O":
            t.append({"id": "CP-O", "tipo": "principal", "ancho": 0.65, "p0": [X_TT["O"] - 1.0, Y_COLECTORA, Z_CP_COLA],
                      "p1": [X_DESCARGA["O"], Y_COLECTORA, Z_CP_O], "nota": "entra por el muro Oeste sobre la tolva pulmón"})
        else:
            t.append({"id": "CP-E", "tipo": "principal", "ancho": 0.65, "p0": [X_TT["E"] + 1.0, Y_COLECTORA, Z_CP_COLA],
                      "p1": [X_DESCARGA["E"], Y_COLECTORA, Z_CP_E],
                      "nota": "entra por el muro Este y cruza la nave a +4,8/+5,4 m hasta la tolva pulmón (sin capota bajo techo)"})
    return t


# P: contenedor roll-off de 20 m³ (6,0 × 2,35 × 1,9 m) bajo la boca de emergencia: lo levanta y lo lleva el camión
# portacontenedor, sin pala cargadora. 20 m³ × 0,95 t/m³ = 19 t ≈ 2 días de guano de un lado (2 galpones).
CONTENEDOR = {"L": 6.0, "A": 2.35, "H": 1.90, "cap_m3": 20, "dy": -3.0}
TORRES = [  # P: torres de transferencia con compuerta desviadora (pantalón) a la boca de emergencia
    {"id": "TT-O", "x": X_TT["O"], "y": Y_COLECTORA, "lado": "O", "z_plataforma": 4.80, "A": 3.2, "B": 3.2,
     "desviadora": "DV-O", "boca_emergencia_z": 2.20, "chute_ang": 50,
     "contenedor": {**CONTENEDOR, "id": "CR-O", "x": X_TT["O"], "y": Y_COLECTORA + CONTENEDOR["dy"]}},
    {"id": "TT-E", "x": X_TT["E"], "y": Y_COLECTORA, "lado": "E", "z_plataforma": 4.80, "A": 3.2, "B": 3.2,
     "desviadora": "DV-E", "boca_emergencia_z": 2.20, "chute_ang": 50,
     "contenedor": {**CONTENEDOR, "id": "CR-E", "x": X_TT["E"], "y": Y_COLECTORA + CONTENEDOR["dy"]}},
]

TOLVA_PULMON = {  # P: reemplaza la pila de guano, la pala cargadora y la tolva de 3,1 m³ de la Rev. F
    "id": "TP-01", "x0": 0.60, "x1": 5.00, "y0": 10.20, "y1": 16.20,
    "z_fondo": 2.20, "z_borde": 4.40, "z_tapa": 4.55,
    # fondo en W: 4 artesas en U con lomos a 60° entre ellas; los ejes a +1,42 y el vértice de los lomos a z_fondo
    "sinfines": {"n": 4, "D": 0.40, "sentido": "Sur", "z_eje": 1.42, "y_sur": 8.95, "y_norte": 16.40, "largo": 7.45,
                 "bocas_y": 9.30},
    "celdas_carga": 4, "plataforma_z": 4.55,
    "nota": "fondo vivo de 4 sinfines con variador que descargan sobre la cola de la cinta de alimentación (3); "
            "tapa cerrada con aspiración al extractor M23 y al biofiltro",
}
_tp = TOLVA_PULMON
TOLVA_PULMON["volumen_util_m3"] = round((_tp["x1"] - _tp["x0"]) * (_tp["y1"] - _tp["y0"]) *
                                        (_tp["z_borde"] - _tp["z_fondo"] - 0.15) * 0.85, 1)

# =============================================================================== predio, caminos y servicios (P)
X_MIN = EJES_X["G1"] - _A2 - 50.0
X_MAX = EJES_X["G4"] + _A2 + 50.0
_Y_DEP1 = Y_SUR_GALPONES + GALPON["L"] + 4.0 + DEPOSITO["L"]       # muro Norte (portón) de los depósitos
_yn = _Y_DEP1 + 15.0                                                # playón de 15 m frente al muelle
Y_MAX = _yn + 7.0 + 20.0
PREDIO = {"x0": round(X_MIN, 1), "x1": round(X_MAX, 1), "y0": -70.0, "y1": round(Y_MAX, 1),
          "nota": "cerco a ≥ 50 m de los galpones (criterio de la Res. SENASA anterior; verificar con la 1699/2019)"}
CALLE = {"y0": -85.0, "y1": -78.0, "nom": "Camino rural público"}
_xo, _xe = EJES_X["G1"] - _A2 - 38.0, EJES_X["G4"] + _A2 + 38.0   # dejan lugar para un galpón más por lado
CAMINOS = [
    {"id": "C1", "zona": "sucia", "x0": 13.0, "x1": 20.0, "y0": -55.0, "y1": -22.0, "nom": "acceso a la planta"},
    {"id": "C2", "zona": "sucia", "x0": -20.0, "x1": -13.0, "y0": -22.0, "y1": 39.0, "nom": "camino Oeste de la planta"},
    {"id": "C3", "zona": "sucia", "x0": 46.0, "x1": 53.0, "y0": -22.0, "y1": 39.0, "nom": "camino Este de la planta"},
    {"id": "C4", "zona": "sucia", "x0": -20.0, "x1": 53.0, "y0": 32.0, "y1": 39.0, "nom": "camino Norte de la planta (cáscara y bomberos)"},
    {"id": "C5", "zona": "sucia", "x0": -20.0, "x1": 53.0, "y0": -22.0, "y1": -15.0, "nom": "camino Sur de la planta"},
    {"id": "C6", "zona": "limpia", "x0": round(_xo - 7, 1), "x1": round(_xe + 7, 1), "y0": -62.0, "y1": -55.0,
     "nom": "camino perimetral Sur (limpio)"},
    {"id": "C7", "zona": "limpia", "x0": round(_xo - 7, 1), "x1": round(_xo, 1), "y0": -62.0, "y1": round(_yn + 7, 1),
     "nom": "camino perimetral Oeste (limpio)"},
    {"id": "C8", "zona": "limpia", "x0": round(_xe, 1), "x1": round(_xe + 7, 1), "y0": -62.0, "y1": round(_yn + 7, 1),
     "nom": "camino perimetral Este (limpio)"},
    {"id": "C9", "zona": "limpia", "x0": round(_xo - 7, 1), "x1": round(_xe + 7, 1), "y0": round(_yn, 1),
     "y1": round(_yn + 7, 1), "nom": "camino Norte de los depósitos y silos (limpio)"},
]
PLAYONES = [
    {"id": "PY1", "x0": 24.0, "x1": 37.0, "y0": -7.0, "y1": 0.0, "nom": "playón de despacho de producto (P2)"},
    {"id": "PY2", "x0": 34.0, "x1": 41.0, "y0": 17.0, "y1": 32.0, "nom": "dársena de descarga de cáscara (empieza "
                                                                          "0,7 m al Norte de la galería de la CP-E)"},
    {"id": "PY3", "x0": -13.0, "x1": 0.0, "y0": 2.0, "y1": 24.0, "nom": "playón Oeste: boca de emergencia de la TT-O"},
    {"id": "PY4", "x0": 33.0, "x1": 46.0, "y0": 2.0, "y1": 13.0, "nom": "playón Este: boca de emergencia de la TT-E"},
    {"id": "PY5", "x0": round(EJES_X["G2"] - GALPON["eje_par"] / 2 - 11.0, 1), "x1": round(EJES_X["G2"] - GALPON["eje_par"] / 2 + 11.0, 1),
     "y0": round(_Y_DEP1, 2), "y1": round(_yn, 2), "nom": "playón de carga de huevos del DH-O (camión al muelle)"},
    {"id": "PY6", "x0": round(EJES_X["G3"] + GALPON["eje_par"] / 2 - 11.0, 1), "x1": round(EJES_X["G3"] + GALPON["eje_par"] / 2 + 11.0, 1),
     "y0": round(_Y_DEP1, 2), "y1": round(_yn, 2), "nom": "playón de carga de huevos del DH-E (camión al muelle)"},
]
ACCESO = {  # P: todos los vehículos cruzan el vado; el personal entra por los vestuarios con ducha
    "porton": {"x0": 11.0, "x1": 22.0, "y": -70.0},
    "garita": {"x0": 4.0, "x1": 8.0, "y0": -69.0, "y1": -65.0, "h": 2.8},
    "vado": {"x0": 13.0, "x1": 20.0, "y0": -69.0, "y1": -64.0, "nota": "vado sanitario (E1 de la Rev. D)"},
    "bascula": {"x0": 14.75, "x1": 18.25, "y0": -50.0, "y1": -34.0, "cap_t": 40,
                "nota": "sobre el acceso a la planta: pesan los camiones de cáscara y de producto"},
    "bioseguridad": {"x0": 26.0, "x1": 38.0, "y0": -74.0, "y1": -66.0, "h": 3.2,
                     "nom": "vestuarios con ducha: se entra desde afuera del cerco y se sale adentro"},
    "estacionamiento": {"x0": 40.0, "x1": 62.0, "y0": -77.0, "y1": -71.0, "nota": "afuera del cerco"},
    "set": {"x0": -12.0, "x1": -4.0, "y0": -77.0, "y1": -71.0, "nom": "subestación 13,2/0,4 kV (preliminar), afuera del cerco"},
}

SILOS_ALIMENTO = []
for _gid in ("G1", "G2", "G3", "G4"):
    _x = EJES_X[_gid]
    _afuera = -1 if _gid in ("G1", "G3") else 1           # cada galpón tiene sus silos del lado contrario a la colectora
    _xs = _x + _afuera * (_A2 + 2.6)
    for _k in range(2):
        SILOS_ALIMENTO.append({"id": f"SA-{_gid}-{_k + 1}", "galpon": _gid, "x": round(_xs, 2),
                               "y": round(Y_SUR_GALPONES + GALPON["L"] - 6.0 - 3.6 * _k, 2),
                               "D": 2.75, "h_cil": 5.5, "h_cono": 2.3, "h_patas": 1.2, "cap_t": 15})

SERVICIOS = [
    {"id": "TQ-AGUA", "x": 16.5, "y": 95.0, "D": 8.0, "h": 3.0, "nom": "tanque de agua de la granja (preliminar)"},
    {"id": "TQ-EF", "x": -6.5, "y": -3.0, "D": 2.6, "h": 3.0, "nom": "tanque de efluentes de 15 m³ (reemplaza al biodigestor)"},
    {"id": "GLP", "x": 31.5, "y": 27.0, "D": 0.9, "L": 2.0, "nom": "tanque de GLP del piloto del hogar"},
    {"id": "MORT", "x0": 56.0, "x1": 62.0, "y0": 26.0, "y1": 32.0, "nom": "compostera de mortandad (preliminar)"},
]
AMPLIACION = [  # P: lugar para un galpón más por lado; la secadora llega a 1.440 kg/h
    {"id": "G0 (futuro)", "x": EJES_X["G1"] - GALPON["eje_par"]},
    {"id": "G5 (futuro)", "x": EJES_X["G4"] + GALPON["eje_par"]},
]

# =============================================================================== planta central (copia de la Rev. F)
QUITAR = ["pila_guano", "muro_contencion", "tolva", "rutas", "camion", "operarios", "predio", "calle",
          "porton_predio", "garita", "bascula", "caminos", "playones", "estacionamiento", "senda", "pavimento",
          "entrada_vehicular", "arboles", "farolas", "pilar_acometida"]


def _planta():
    p = copy.deepcopy(BASE["G"])
    for k in QUITAR:
        p.pop(k, None)
    p["zonas"] = [dict(z) for z in p["zonas"]]
    for z in p["zonas"]:
        if z["n"] == 1:
            z["nom"] = "RECEPCIÓN AUTOMÁTICA DE GUANO (TOLVA PULMÓN TP-01)"
    # el portón P1 (camiones de guano) se cierra: ahí va la tolva pulmón y entra la cinta CP-O
    p["portones"] = [dict(x) for x in p["portones"] if x["id"] != "P1"]
    # el tanque de incendio y su casilla de bombas quedaban sobre el camino Oeste nuevo (C2): se corren 5,5 m al Oeste
    for k in ("tanque_incendio", "casilla_bomba"):
        p[k] = dict(p[k], x=round(p[k]["x"] - 5.5, 2), nota="corrido 5,5 m al Oeste (camino C2 de la granja)")
    return p


def construir():
    galpones = _galpones()
    return {
        "titulo": "Granja avícola integrada con planta central de secado de guano",
        "lugar": "Crespo, Entre Ríos",
        "origen": "vértice Sudoeste de la nave de proceso (igual que el proyecto de la secadora)",
        "distribucion": "en fila de Oeste a Este: G1, G2, planta de secado, G3, G4",
        "galpon": GALPON, "jaulas": JAULAS, "galpones": galpones, "depositos": _depositos(galpones),
        "deposito": DEPOSITO, "transporte": _transporte(galpones), "torres": TORRES, "tolva_pulmon": TOLVA_PULMON,
        "predio": PREDIO, "calle": CALLE, "caminos": CAMINOS, "playones": PLAYONES, "acceso": ACCESO,
        "silos_alimento": SILOS_ALIMENTO, "servicios": SERVICIOS, "ampliacion": AMPLIACION,
        "planta": _planta(), "quitado_de_la_planta": QUITAR + ["portón P1"],
        "cotas": {"Y_COLECTORA": Y_COLECTORA, "Z_COLECTORA": Z_COLECTORA, "Y_SUR_GALPONES": Y_SUR_GALPONES,
                  "Z_CP_COLA": Z_CP_COLA, "Z_CP_O": Z_CP_O, "Z_CP_E": Z_CP_E, "SEP_NAVE": SEP_NAVE},
    }


def main():
    d = construir()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    j = d["jaulas"]
    print(f"granja.json: {len(d['galpones'])} galpones de {j['aves_por_galpon']} gallinas "
          f"({j['aves_por_galpon'] * 4} en total; {j['filas']} filas × {j['pisos']} pisos, pasillos de {j['pasillo']} m), "
          f"{len(d['transporte'])} transportadores, tolva pulmón de {d['tolva_pulmon']['volumen_util_m3']} m³")


if __name__ == "__main__":
    main()
