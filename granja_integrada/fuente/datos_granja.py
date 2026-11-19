"""Datos únicos de la granja avícola integrada con planta central de secado de guano.

Es la única fuente de medidas del proyecto nuevo: el modelo 3D, los planos, los renders y los cálculos leen
`datos/granja.json`, que se genera con este programa. Si cambia una medida, se cambia acá y se regenera todo.

Coordenadas en metros. Origen en el vértice Sudoeste de la nave de proceso, igual que el proyecto anterior
(`layout_planta.json`), para poder usar sin cambios las posiciones de la planta Rev. F. x al Este, y al Norte, z arriba.

Tipo de dato de cada valor (ver docs/01_auditoria.md): R proyecto de la secadora Rev. F, S TP San Jorge,
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
# Envolvente y separación del TP San Jorge (S); interior propuesto (P).
GALPON = {
    "L": 100.0, "A": 6.0,                       # S: 100 m × 6 m
    "eje_par": 31.0,                            # S: ejes a unos 31 m
    "e_muro": 0.10, "zocalo": 0.50,             # P: zócalo de H°A° y panel sándwich
    "h_alero": 3.60, "pendiente_deg": 20.0,     # P: alero y techo a dos aguas
    "paso_porticos": 5.0,                       # P: pórticos de perfil C en cajón cada 5 m
    "cabecera_huevos": 2.60,                    # P: recolectores de huevos y pasillo de servicio
    "cabecera_guano": 2.20,                     # P: accionamientos de las cintas y cinta transversal
}
JAULAS = {                                      # P (celda de referencia: Big Dutchman SuperTripleDeck, V)
    "filas": 2, "pisos": 4,
    "celda_ancho": 0.610, "celda_prof": 0.483, "celda_alto": 0.460,
    "aves_por_celda": 6,                        # 490 cm² por ave (V: ficha del fabricante)
    "celdas_por_modulo": 4, "modulos_por_fila": 38,
    "paso_pisos": 0.620, "z_piso1": 0.35,       # piso de la jaula 1 sobre el piso del galpón
    "ancho_fila": 1.30,                         # 2 × 0,483 de jaula + comederos + separador
    "cinta_guano_ancho": 1.25, "cinta_guano_v_m_min": 10.0,   # V (rango 10-12 m/min de proveedores)
    "cinta_huevos_ancho": 0.10,
}
JAULAS["modulo"] = JAULAS["celda_ancho"] * JAULAS["celdas_por_modulo"]           # 2,44 m
JAULAS["largo_fila"] = JAULAS["modulo"] * JAULAS["modulos_por_fila"]             # 92,72 m
JAULAS["celdas_por_lado"] = JAULAS["celdas_por_modulo"] * JAULAS["modulos_por_fila"]
JAULAS["aves_por_fila"] = JAULAS["celdas_por_lado"] * 2 * JAULAS["pisos"] * JAULAS["aves_por_celda"]
JAULAS["aves_por_galpon"] = JAULAS["aves_por_fila"] * JAULAS["filas"]

Y_PAR = 9.3                                     # eje de cada par = eje del secador (yc de la Rev. F)
X_CAB_IZQ = -45.0                               # cabecera de guano de los galpones del lado Oeste
X_CAB_DER = 33.0 + 45.0                         # cabecera de guano de los galpones del lado Este (simétrica)


def _galpones():
    g, L, s = [], GALPON["L"], GALPON["eje_par"] / 2
    for gid, lado, y in (("G1", "O", Y_PAR + s), ("G2", "O", Y_PAR - s), ("G3", "E", Y_PAR + s), ("G4", "E", Y_PAR - s)):
        if lado == "O":
            x0, x1, cab_guano, cab_huevos = X_CAB_IZQ - L, X_CAB_IZQ, "E", "O"
        else:
            x0, x1, cab_guano, cab_huevos = X_CAB_DER, X_CAB_DER + L, "O", "E"
        g.append({"id": gid, "lado": lado, "x0": x0, "x1": x1, "y": y, "y0": y - GALPON["A"] / 2,
                  "y1": y + GALPON["A"] / 2, "cab_guano": cab_guano, "cab_huevos": cab_huevos,
                  "posicion": "Norte" if y > Y_PAR else "Sur"})
    return g


# =============================================================================== depósitos de huevos (copia del de San Jorge)
DEPOSITO = {"L": 21.8, "A": 16.0, "h_libre": 5.0, "e_muro": 0.20,      # S: 21,8 × 16,0 por fuera, alto libre 5,0 m
            "riel": 17.0, "lugares": 24, "estaciones_x": [7.5, 10.1],   # S: transelevador, 24 lugares, E1 y E2
            "muelle_h": 1.25}


def _depositos(galpones):
    d = []
    norte = {g["lado"]: g for g in galpones if g["posicion"] == "Norte"}
    for lado, sig in (("O", -1), ("E", 1)):
        gn = norte[lado]
        x_cab = gn["x0"] if lado == "O" else gn["x1"]
        gap = 4.0                                                        # P: paso de las cintas de huevos
        xa = x_cab + sig * gap
        xb = xa + sig * DEPOSITO["L"]
        d.append({"id": "DH-" + lado, "lado": lado, "x0": min(xa, xb), "x1": max(xa, xb),
                  "y0": gn["y"] - DEPOSITO["A"] / 2, "y1": gn["y"] + DEPOSITO["A"] / 2,
                  "porton": "O" if lado == "O" else "E", "galpones": [g["id"] for g in galpones if g["lado"] == lado]})
    return d


# =============================================================================== transporte de guano (P)
# z = altura del plano de la banda (m). Ver docs/03_transporte_guano.md para el criterio de cada tramo.
Z_CE = 6.20          # cintas exteriores a lo largo de las cabeceras
Z_CP_COLA = 5.20     # cola de las cintas principales en las torres de transferencia
Z_CP_IZQ = 6.00      # cinta principal Oeste al entrar por el muro Oeste (pasa sobre la tolva pulmón)
Z_CP_DER = 5.60      # cinta principal Este hasta el muro Este (gálibo de 5,0 m sobre el camino)
Z_CN = 5.00          # cinta interior de la nave (bajo el ducto de agotado, fondo a +6,05 m)
Y_CN = 12.0          # eje de la cinta interior: al Norte del secador y de la descarga (Rev. F)
X_TT_IZQ = -37.0
X_TT_DER = 70.0


def _transporte(galpones):
    t = []
    for g in galpones:
        izq = g["lado"] == "O"
        sig = 1 if izq else -1                     # sentido hacia la planta
        x_cab = g["x1"] if izq else g["x0"]
        x_tt = X_TT_IZQ if izq else X_TT_DER
        hacia_par = -1 if g["posicion"] == "Norte" else 1      # la cinta transversal descarga hacia el eje del par
        y_ci = g["y"] + hacia_par * (GALPON["A"] / 2 - 0.55)
        n = int(g["id"][1])
        # cintas de guano de las jaulas (8 por galpón): solo datos; la geometría sale de JAULAS
        t.append({"id": f"CT-{n}", "tipo": "transversal", "galpon": g["id"], "ancho": 0.60,
                  "p0": [x_cab - sig * 1.15, g["y"] - hacia_par * (GALPON["A"] / 2 - 0.35), 0.30],
                  "p1": [x_cab - sig * 1.15, y_ci, 0.30], "nota": "dentro del galpón, en canal de H°"})
        z_cola = 0.45
        x0_ci = x_cab - sig * 1.15
        ang_ci = round(math.degrees(math.atan2(Z_CE + 0.25 - z_cola, abs(x_tt - x0_ci))), 1)
        t.append({"id": f"CI-{n}", "tipo": "inclinada", "galpon": g["id"], "ancho": 0.50, "ang": ang_ci,
                  "p0": [x0_ci, y_ci, z_cola], "p1": [x_tt, y_ci, Z_CE + 0.25],
                  "banda": "goma EP 400/3 con bordes de 80 mm y tacos (como la cinta 3 de la Rev. F)"})
        y_tt = Y_PAR if izq else Y_CN
        t.append({"id": f"CE-{n}", "tipo": "exterior", "galpon": g["id"], "ancho": 0.50,
                  "p0": [x_tt, y_ci, Z_CE], "p1": [x_tt, y_tt + (0.9 if g["posicion"] == "Norte" else -0.9), Z_CE],
                  "nota": "artesa a 20°, cubierta, pasarela de 0,8 m"})
    t.append({"id": "CP-O", "tipo": "principal", "ancho": 0.50, "p0": [X_TT_IZQ, Y_PAR, Z_CP_COLA],
              "p1": [2.8, Y_PAR, Z_CP_IZQ], "nota": "galería cubierta; cruza el camino Oeste con 5,0 m libres"})
    t.append({"id": "CP-E", "tipo": "principal", "ancho": 0.50, "p0": [X_TT_DER, Y_CN, Z_CP_COLA],
              "p1": [32.2, Y_CN, Z_CP_DER], "nota": "galería cubierta; entra por el muro Este y descarga en la CN-E"})
    t.append({"id": "CN-E", "tipo": "interior", "ancho": 0.50, "p0": [32.6, Y_CN, Z_CN], "p1": [2.8, Y_CN, Z_CN],
              "nota": "sin capota (bajo techo), con guardas laterales; descarga en la tolva pulmón por un chute"})
    return t


TORRES = [  # P: torres de transferencia con compuerta desviadora a la boca de emergencia
    {"id": "TT-O", "x": X_TT_IZQ, "y": Y_PAR, "lado": "O", "z_plataforma": 4.80, "A": 3.2, "B": 3.2,
     "desviadora": "DV-O", "boca_emergencia_z": 3.40},
    {"id": "TT-E", "x": X_TT_DER, "y": Y_CN, "lado": "E", "z_plataforma": 4.80, "A": 3.2, "B": 3.2,
     "desviadora": "DV-E", "boca_emergencia_z": 3.40},
]

TOLVA_PULMON = {  # P: reemplaza a la pila de guano, la pala cargadora y la tolva de 3,1 m³ de la Rev. F
    "id": "TP-01", "x0": 0.60, "x1": 5.00, "y0": 7.80, "y1": 10.80,
    "z_fondo": 2.20, "z_borde": 4.40, "z_tapa": 4.55,
    "volumen_util_m3": None,                 # se calcula abajo
    "sinfines": {"n": 2, "D": 0.40, "sentido": "Oeste", "descarga_x": 1.05},
    "celdas_carga": 4, "plataforma_z": 4.55,
    "nota": "fondo vivo de doble sinfín con variador; descarga sobre la cola de la cinta de alimentación (3)",
}
_tp = TOLVA_PULMON
TOLVA_PULMON["volumen_util_m3"] = round((_tp["x1"] - _tp["x0"]) * (_tp["y1"] - _tp["y0"]) *
                                        (_tp["z_borde"] - _tp["z_fondo"] - 0.15) * 0.85, 1)

# =============================================================================== predio, caminos y servicios (P)
PREDIO = {"x0": -200.0, "x1": 234.0, "y0": -80.0, "y1": 85.0,
          "nota": "cerco a ≥ 50 m de los galpones (criterio de la Res. SENASA anterior; verificar con la 1699/2019)"}
CALLE = {"y0": -95.0, "y1": -88.0, "nom": "Camino rural público"}
CAMINOS = [
    {"id": "C1", "zona": "sucia", "x0": 13.0, "x1": 20.0, "y0": -80.0, "y1": -7.0, "nom": "acceso central a la planta"},
    {"id": "C2", "zona": "sucia", "x0": -28.0, "x1": -21.0, "y0": -40.0, "y1": 47.0, "nom": "camino Oeste de la planta"},
    {"id": "C3", "zona": "sucia", "x0": 54.0, "x1": 61.0, "y0": -40.0, "y1": 47.0, "nom": "camino Este de la planta"},
    {"id": "C4", "zona": "sucia", "x0": -28.0, "x1": 61.0, "y0": 40.0, "y1": 47.0, "nom": "camino Norte (cáscara y bomberos)"},
    {"id": "C5", "zona": "sucia", "x0": -28.0, "x1": 61.0, "y0": -47.0, "y1": -40.0, "nom": "camino Sur de la planta"},
    {"id": "C6", "zona": "limpia", "x0": -185.0, "x1": 219.0, "y0": -62.0, "y1": -55.0, "nom": "camino perimetral Sur (limpio)"},
    {"id": "C7", "zona": "limpia", "x0": -185.0, "x1": -178.0, "y0": -62.0, "y1": 70.0, "nom": "camino de los depósitos Oeste"},
    {"id": "C8", "zona": "limpia", "x0": 212.0, "x1": 219.0, "y0": -62.0, "y1": 70.0, "nom": "camino de los depósitos Este"},
]
PLAYONES = [
    {"id": "PY1", "x0": 24.0, "x1": 37.0, "y0": -7.0, "y1": 0.0, "nom": "playón de despacho de producto (P2)"},
    {"id": "PY2", "x0": 34.0, "x1": 41.0, "y0": 16.0, "y1": 30.0, "nom": "dársena de descarga de cáscara"},
    {"id": "PY3", "x0": -21.0, "x1": 0.0, "y0": 11.0, "y1": 20.0, "nom": "playón de mantenimiento (portón P1)"},
    {"id": "PY-O", "x0": -178.0, "x1": -170.8, "y0": 18.8, "y1": 30.8, "nom": "muelle de huevos Oeste"},
    {"id": "PY-E", "x0": 203.8, "x1": 212.0, "y0": 18.8, "y1": 30.8, "nom": "muelle de huevos Este"},
]
ACCESO = {  # P: todos los vehículos cruzan el vado; el personal entra por los vestuarios con ducha
    "porton": {"x0": 11.0, "x1": 22.0, "y": -80.0},
    "garita": {"x0": 4.0, "x1": 8.0, "y0": -79.0, "y1": -75.0, "h": 2.8},
    "vado": {"x0": 13.0, "x1": 20.0, "y0": -78.0, "y1": -73.0, "nota": "vado sanitario (E1 de la Rev. D)"},
    "bascula": {"x0": 14.75, "x1": 18.25, "y0": -50.0, "y1": -34.0, "cap_t": 40,
                "nota": "sobre el acceso a la planta: pesan los camiones de cáscara y de producto"},
    "bioseguridad": {"x0": 26.0, "x1": 38.0, "y0": -84.0, "y1": -76.0, "h": 3.2,
                     "nom": "vestuarios con ducha: se entra desde afuera del cerco y se sale adentro"},
    "estacionamiento": {"x0": 40.0, "x1": 62.0, "y0": -87.0, "y1": -81.0, "nota": "afuera del cerco"},
    "set": {"x0": -12.0, "x1": -4.0, "y0": -87.0, "y1": -81.0, "nom": "subestación 13,2/0,4 kV (preliminar), afuera del cerco"},
}
SILOS_ALIMENTO = []
for _g in _galpones():
    _x_out = _g["x0"] if _g["lado"] == "O" else _g["x1"]
    _sig = 1 if _g["lado"] == "O" else -1
    _y = _g["y1"] + 2.6 if _g["posicion"] == "Norte" else _g["y0"] - 2.6
    if _g["posicion"] == "Norte":
        _y = _g["y1"] + 2.6
    for _k in range(2):
        SILOS_ALIMENTO.append({"id": f"SA-{_g['id']}-{_k + 1}", "galpon": _g["id"], "x": _x_out + _sig * (8.0 + 3.6 * _k),
                               "y": _y, "D": 2.75, "h_cil": 5.5, "h_cono": 2.3, "h_patas": 1.2, "cap_t": 15})

SERVICIOS = [
    {"id": "TQ-AGUA", "x": 10.0, "y": 60.0, "D": 6.0, "h": 2.5, "nom": "tanque de agua de la granja (preliminar)"},
    {"id": "TQ-EF", "x": -6.5, "y": 5.0, "D": 2.6, "h": 3.0, "nom": "tanque de efluentes de 15 m³ (reemplaza al biodigestor)"},
    {"id": "GLP", "x": 31.5, "y": 27.0, "D": 0.9, "L": 2.0, "nom": "tanque de GLP del piloto del hogar"},
    {"id": "MORT", "x0": 44.0, "x1": 52.0, "y0": 32.0, "y1": 38.0, "nom": "compostera de mortandad (preliminar)"},
]
AMPLIACION = [  # P: lugar reservado para un galpón más por lado (la secadora llega a 1.440 kg/h)
    {"id": "G5 (futuro)", "lado": "O", "x0": X_CAB_IZQ - GALPON["L"], "x1": X_CAB_IZQ, "y": Y_PAR + 1.5 * GALPON["eje_par"]},
    {"id": "G6 (futuro)", "lado": "E", "x0": X_CAB_DER, "x1": X_CAB_DER + GALPON["L"], "y": Y_PAR + 1.5 * GALPON["eje_par"]},
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
    p["portones"] = [dict(x) for x in p["portones"]]
    for x in p["portones"]:
        if x["id"] == "P1":
            x["txt"] = "Portón P1 4,0 m - mantenimiento (ya no entran camiones de guano)"
    return p


def construir():
    galpones = _galpones()
    datos = {
        "titulo": "Granja avícola integrada con planta central de secado de guano",
        "lugar": "Crespo, Entre Ríos",
        "origen": "vértice Sudoeste de la nave de proceso (igual que el proyecto de la secadora)",
        "galpon": GALPON, "jaulas": JAULAS, "galpones": galpones, "depositos": _depositos(galpones),
        "deposito": DEPOSITO, "transporte": _transporte(galpones), "torres": TORRES, "tolva_pulmon": TOLVA_PULMON,
        "predio": PREDIO, "calle": CALLE, "caminos": CAMINOS, "playones": PLAYONES, "acceso": ACCESO,
        "silos_alimento": SILOS_ALIMENTO, "servicios": SERVICIOS, "ampliacion": AMPLIACION,
        "planta": _planta(), "quitado_de_la_planta": QUITAR,
        "cotas": {"Y_PAR": Y_PAR, "X_CAB_IZQ": X_CAB_IZQ, "X_CAB_DER": X_CAB_DER, "Z_CE": Z_CE,
                  "Z_CP_COLA": Z_CP_COLA, "Z_CP_IZQ": Z_CP_IZQ, "Z_CP_DER": Z_CP_DER, "Z_CN": Z_CN, "Y_CN": Y_CN},
    }
    return datos


def main():
    d = construir()
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    j = d["jaulas"]
    print(f"granja.json: {len(d['galpones'])} galpones de {j['aves_por_galpon']} gallinas "
          f"({j['aves_por_galpon'] * 4} en total), {len(d['transporte'])} transportadores, "
          f"tolva pulmón de {d['tolva_pulmon']['volumen_util_m3']} m³")


if __name__ == "__main__":
    main()
