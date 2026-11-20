"""Despieces (vistas explotadas) de los conjuntos principales, armados con las piezas del modelo 3D.

Cada conjunto toma las piezas reales del modelo (mismo prototipo, misma ubicación), las agrupa por categoría según su
nombre y separa cada categoría con un desplazamiento. Sale un GLB por conjunto (para renderizar) y un JSON con la lista
de piezas numerada (descripción, cantidad, material) y el punto 3D de cada globo.

    python despieces.py      # -> modelo_3d/despieces/*.glb y *.json
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI / "modelo"))

import cad            # noqa: E402
import componentes as CMP  # noqa: E402
import electrica      # noqa: E402
import transporte     # noqa: E402
from cad import T     # noqa: E402

SALIDA = RAIZ / "modelo_3d" / "despieces"

MATERIAL = {"estructura": "acero F-24 pintado", "galv": "acero galvanizado", "inox": "acero inoxidable AISI 304",
            "acero": "acero SAE 1045", "acero_pintado": "acero pintado", "reductor": "fundición gris pintada",
            "azul_motor": "motor IE3 (carcasa de aluminio)", "gris_motor": "fundición gris", "goma": "caucho",
            "uhmw": "polietileno UHMW", "amarillo": "acero pintado amarillo", "rejilla": "rejilla electrosoldada galvanizada",
            "negro": "acero pintado / caucho", "rojo": "acero pintado rojo", "sensor": "acero inoxidable / plástico",
            "sensor_amarillo": "fundición de aluminio", "tablero": "chapa de acero pintada RAL 7035",
            "tablero_int": "chapa galvanizada", "plastico_gris": "PVC / policarbonato", "plastico_blanco": "PVC",
            "aluminio": "aluminio", "cobre": "cobre", "cable": "Cu/PVC", "naranja": "plástico", "verde": "plástico",
            "vidrio": "vidrio templado", "hormigon": "hormigón H-21", "banda": "banda EP de caucho"}

# ===================================================================================== conjuntos
CONJUNTOS = {
    "TP01": {
        "titulo": "TOLVA PULMÓN TP-01",
        "elegir": lambda i, p: i["cod"] in ("TP-01", "M85", "M86", "M87", "M88", "WT-101", "WT-102",
                                                                               "WT-103", "WT-104", "LT-101", "LSHH-101", "LSL-101",
                                                                               "ZS-REG1", "ZS-REG2", "SSL-M85", "SSL-M86", "SSL-M87",
                                                                               "SSL-M88", "LSH-102", "LSH-103", "LSH-104", "LSH-105"),
        "mira": [0.55, -1.0, -0.62],
        # barandas y rodapiés: los que están sobre la tolva van con la tapa; los del descanso (x > 5,1 m), con la escalera
        "reasignar": lambda n, c: ((1 if c[0] <= 5.1 else 11) if any(k in n for k in ("Baranda", "Rodapié")) else None),
        "categorias": [
            (1, ["Tapa de chapa", "Viga de la tapa", "Aro superior", "Baranda"], (0, 0, 5.2),
             "Tapa transitable de chapa semilla de melón 6,35 mm sobre vigas UPN 140, con baranda perimetral"),
            (2, ["Registro de inspección", "Bisagra", "ZS-REG"], (0, 0, 5.6), "Registro 800 × 700 con bisagras, traba e interruptor de seguridad ZS-REG"),
            (3, ["LT-101", "Medidor de nivel"], (0, 0, 6.3), "Medidor de nivel por radar LT-101 (80 GHz)"),
            (4, ["Boca de aspiración", "Compuerta mariposa", "Caño rígido"], (0, 0, 5.2), "Boca de aspiración Ø600 con compuerta mariposa (a M23)"),
            (5, ["Pared de chapa", "Rigidizador", "Montante rigidizador", "TP-01 TOLVA", "LSHH", "LSL", "Interruptor de nivel"], (0, 0, 2.6),
             "Cuerpo de chapa 8 mm F-24 con rigidizadores UPN 100 y niveles LSHH/LSL-101"),
            (6, ["Fondo en W", "Testero", "Costilla", "Placa de cabeza", "Tapa abulonada", "Soporte de brida", "Manga de goma",
                 "Detector de atascamiento", "LSH-10", "Artesa", "Ala de la artesa", "Boca de descarga"], (0, 0, 1.3),
             "Fondo en W con 4 artesas de chapa 6 mm, testeros, tapas abulonadas y bocas de descarga con manga"),
            (7, ["Espira", "Tubo central", "SSL-M8", "Sensor de velocidad"], (0, 6.5, 1.3), "Sinfín Ø400 paso 320 con tubo Ø114 (4 unidades)"),
            (8, ["Motorreductor coaxial", "Motor M8", "Ménsula del motorreductor", "Pie de amigo"], (0, 9.0, 1.3),
             "Motorreductor coaxial 3 kW M85 a M88 con ménsula (4 unidades)"),
            (9, ["Celda de carga", "Placa de apoyo de la celda"], (0, 0, 0.55), "Celda de carga de compresión WT-101 a 104 con placas"),
            (10, ["Viga de apoyo", "Columna HEB", "Cruz de San Andrés", "Riostra baja", "Placa base 360", "Dado", "Mortero"], (0, 0, 0),
             "Estructura de apoyo: columnas y vigas HEB 160, cruces L 80"),
            (11, ["Zanca", "Peldaño", "Pasamanos", "Parante", "Rodapié", "Descanso", "Marco del descanso", "Columna RHS", "Placa base 220"],
             (3.0, 0, 0), "Escalera a 42° con descanso, barandas y rodapié"),
        ]},
    "CPO": {
        "titulo": "CABEZAL DE LA CINTA PRINCIPAL CP-O",
        "elegir": lambda i, p: (i["cod"] in ("CP-O", "M82", "LSH-CP-O", "XA-CP-O", "Q-M82") and p[0] > 0.4 and p[1] > 12.9),
        "mira": [-0.7, 1.0, -0.6],
        "categorias": [
            (1, ["Tambor", "Revestimiento de goma", "Eje Ø"], (0, 0, 0), "Tambor motriz Ø400 con revestimiento de goma romboidal 8 mm y eje SAE 1045"),
            (2, ["Soporte UCP"], (0, 0, 0.5), "Soporte de pie UCP 212 (2 unidades)"),
            (3, ["Motorreductor ortogonal", "Motor M82"], (0, -1.3, 0), "Motorreductor ortogonal M82 1,1 kW de eje hueco con brazo de reacción"),
            (4, ["Tapa protectora"], (0, 1.2, 0), "Tapa protectora del extremo del eje"),
            (5, ["Rascador primario", "Hoja de poliuretano"], (0.9, 0, -0.6), "Rascador primario de poliuretano"),
            (6, ["Rascador secundario"], (0.6, 0, -1.1), "Rascador secundario de láminas"),
            (7, ["Chute de cabeza", "Puerta de inspección"], (0.9, 0, -1.9), "Chute de cabeza con puerta de inspección abisagrada"),
            (8, ["Rodillo", "Bastidor de terna", "Travesaño"], (-0.9, 0, 0.5), "Terna de rodillos Ø89 y rodillo de retorno"),
            (9, ["Detector de atascamiento"], (0, -0.4, 0.9), "Detector de atascamiento LSH-CP-O (interruptor de inclinación)"),
            (10, ["Baliza"], (0, -0.4, 0.9), "Baliza y sirena de prearranque XA-CP-O"),
            (11, ["Placa CP-O"], (0, -0.4, 0.9), "Placa de identificación de la CP-O"),
            (12, ["Seccionador de seguridad"], (0, 0.3, 0.3), "Seccionador de seguridad bloqueable Q-M82 (en el pórtico PC-01)"),
        ]},
    "DVO": {
        "titulo": "DESVIADORA DV-O DE LA TORRE TT-O",
        "elegir": lambda i, p: ("DV-O" in (i["cod"] or "")) or i["cod"] in ("M89", "Q-M89"),
        "mira": [-0.85, 1.0, -0.55],
        "categorias": [
            (1, ["Cuerpo de la desviadora", "DV-O: A"], (0, 0, 0), "Cuerpo pantalón de la desviadora (chapa 4 mm)"),
            (2, ["Eje de la clapeta"], (0, -0.7, 0.4), "Clapeta con eje y bujes"),
            (3, ["Actuador eléctrico", "Motor M89"], (0, -1.4, 0.4), "Actuador eléctrico de cuarto de vuelta M89 0,37 kW"),
            (4, ["Final de carrera"], (0, -1.9, 0.9), "Finales de carrera ZSA y ZSB"),
            (5, ["Pierna A"], (0.6, 0, -0.5), "Pierna A hacia la cinta principal"),
            (6, ["Chute de emergencia", "Tapa de inspección", "Brida del chute"], (-0.6, 0, -0.9), "Chute de emergencia 450 × 450 a 50° (pierna B) con tapa de inspección"),
            (7, ["Boca de carga de emergencia", "Manga de goma"], (-0.6, -0.6, -1.6),
             "Boca de emergencia al contenedor CR-O (+2,20) con manga de goma"),
            (8, ["Detector de atascamiento"], (-0.6, -0.6, -1.0), "Detector de atascamiento LSH-DV-O de la boca de emergencia"),
            (9, ["Brida"], (0, 0, 0.9), "Bridas de entrada (de la CE-O) y de unión del cuerpo"),
            (10, ["Seccionador de seguridad"], (0, -0.3, 0.3), "Seccionador de seguridad bloqueable Q-M89 (en la baranda de la plataforma)"),
        ]},
}


def _nombre_heredado(inst):
    """Las piezas de un mismo componente vienen seguidas con el mismo código: la que no tiene nombre hereda el del anterior."""
    out, ult = [], {}
    for i in inst:
        n = i["nom"] or ult.get(i["cod"], "")
        if i["nom"]:
            ult[i["cod"]] = i["nom"]
        out.append(n)
    return out


def armar(nombre, conf, e):
    sel = [(i, n) for i, n in zip(e.inst, _nombre_heredado(e.inst)) if conf["elegir"](i, i["M"][:3, 3] / 1000)]
    nuevo = cad.Escena(nombre)
    puntos = defaultdict(list)
    cantidad = defaultdict(set)
    mats = defaultdict(lambda: defaultdict(int))
    for i, n in sel:
        cat = None
        c_mundo = (i["M"] @ np.r_[np.array(_centro_caja(i)), 1.0])[:3] / 1000
        forzada = conf.get("reasignar", lambda n_, c_: None)(n, c_mundo)
        for num, claves, off, desc in conf["categorias"]:
            if (forzada is not None and num == forzada) or (forzada is None and any(k in n or k in (i["cod"] or "") for k in claves)):
                cat = (num, off)
                break
        off = np.array(cat[1] if cat else (0, 0, 0), float) * 1000
        M = T(*off) @ i["M"]
        nuevo.inst.append({**i, "M": M})
        if cat:
            puntos[cat[0]].append((M @ np.r_[np.array(_centro_caja(i)), 1.0])[:3] / 1000)
            cantidad[cat[0]].add((i["cod"], n) if cat[0] in (7, 8) and nombre == "TP01" else (i["cod"], n))
            mats[cat[0]][i["mat"]] += 1
    SALIDA.mkdir(parents=True, exist_ok=True)
    nuevo.exportar_glb(SALIDA / f"{nombre}.glb")
    items = []
    for num, claves, off, desc in conf["categorias"]:
        if num not in puntos:
            continue
        P = np.array(puntos[num])
        c = P[np.argmin(np.linalg.norm(P - P.mean(0), axis=1))]           # pieza más cercana al centro de la categoría
        mat = max(mats[num].items(), key=lambda kv: kv[1])[0]
        items.append({"n": num, "descripcion": desc, "material": MATERIAL.get(mat, mat), "punto": [round(float(v), 3) for v in c],
                      "candidatos": _candidatos(P)})
    todos = np.array([s[0]["M"][:3, 3] / 1000 for s in sel] + [p for v in puntos.values() for p in v])
    meta = {"titulo": conf["titulo"], "mira": conf["mira"], "piezas": len(sel), "items": items,
            "caja": [todos.min(0).round(2).tolist(), todos.max(0).round(2).tolist()]}
    (SALIDA / f"{nombre}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nombre}: {len(sel)} piezas en {len(items)} categorías")
    return meta


# ===================================================================================== interior del TS-GU (para su despiece)
def tablero_ts_gu():
    """Tablero TS-GU de 1200 × 2000 × 400 mm con su placa de montaje y equipos (medidas de catálogo aproximadas, P)."""
    e = cad.Escena("TSGU")
    e.en("TS-GU")
    W, H, P = 1200.0, 2000.0, 400.0
    items = []

    def caja(x0, y0, z0, x1, y1, z1, mat, cod, nom, off=(0, 0, 0)):
        e.caja(x0, y0, z0, x1, y1, z1, mat, cod, nom, M=T(*off))

    # gabinete (abierto adelante), techo y zócalo
    for (a, b, c, d, f, g) in ((-W / 2, 0, 100, -W / 2 + 15, P, H + 100), (W / 2 - 15, 0, 100, W / 2, P, H + 100),
                               (-W / 2, P - 15, 100, W / 2, P, H + 100), (-W / 2, 0, H + 85, W / 2, P, H + 100)):
        caja(a, b, c, d, f, g, "tablero", "GAB", "Gabinete de chapa 1,5 mm RAL 7035 (1200 × 2000 × 400)")
    caja(-W / 2, 0, 0, W / 2, P, 100, "negro", "GAB", "Zócalo de 100 mm")
    caja(-W / 2 + 10, -20, 110, W / 2 - 10, 0, H + 90, "tablero", "PUERTA", "Puerta con burlete, manija con llave y bisagras", off=(1700, -350, 0))
    caja(-260, -45, 1300, 70, -20, 1540, "negro", "HMI", "Panel de operador TP1200 Comfort (en la puerta)", off=(1700, -350, 0))
    caja(-W / 2 + 60, P - 40, 160, W / 2 - 60, P - 30, H + 40, "tablero_int", "PLACA", "Placa de montaje galvanizada 2 mm", off=(0, -350, 0))
    off = (0, -620, 0)
    y0 = P - 30

    def equipo(x, z, w, h, d, mat, cod, nom):
        caja(x, y0 - d, z, x + w, y0, z + h, mat, cod, nom, off=off)

    # canaletas y rieles
    for zz in (1880.0, 1500.0, 1080.0, 640.0, 260.0):
        caja(-W / 2 + 70, y0 - 60, zz, W / 2 - 70, y0, zz + 60, "plastico_gris", "CAN", "Canaleta ranurada 60 × 60 mm", off=off)
    equipo(-520, 1580, 110, 240, 130, "plastico_gris", "QG", "Interruptor general 4P 40 A con mando rotativo bloqueable")
    equipo(-400, 1580, 70, 200, 80, "plastico_gris", "ΔI-B", "Diferencial tipo B 300 mA 4P")
    for k in range(10):
        equipo(-310 + 34 * k, 1600, 18, 90, 75, "plastico_gris", "QC", "Interruptores C para variadores y guardamotores (10)")
    for k in range(8):
        equipo(-520 + 125 * k, 1130, 73, 330, 230, "plastico_gris" if k % 2 else "tablero", "VFD",
               "Variador SINAMICS G120: PM240-2 + CU240E-2 PN-F (8)")
    for k in range(2):
        equipo(-520 + 140 * k, 700, 45, 95, 90, "plastico_gris", "GM", "Guardamotores de los actuadores de las desviadoras (2)")
        for j in range(2):
            equipo(-470 + 140 * k + 45 * j, 700, 45, 85, 100, "plastico_gris", "KM", "Contactores del inversor de marcha (4)")
    equipo(-200, 700, 70, 130, 120, "plastico_gris", "SITOP", "Fuente SITOP 24 V 20 A con módulo de respaldo")
    equipo(-110, 700, 147, 147, 130, "negro", "PLC", "PLC-01 S7-1500F: CPU 1515F-2 PN con fuente y módulos")
    equipo(60, 700, 60, 147, 125, "negro", "SW", "Switch SCALANCE XC208 con puertos de fibra")
    equipo(150, 700, 300, 180, 150, "negro", "UPS", "UPS de 1 kVA para PLC, pantallas y red")
    for k in range(40):
        equipo(-520 + 26 * k, 320, 6, 60, 50, "plastico_gris" if k % 5 else "naranja", "BORN", "Borneras de salida a motores e instrumentos")
    caja(-W / 2 + 20, -10, 300, -W / 2 + 140, 0, 420, "plastico_gris", "VENT", "Ventilador con filtro (abajo) y rejilla de salida (arriba)", off=(1700, -350, 0))
    SALIDA.mkdir(parents=True, exist_ok=True)
    e.exportar_glb(SALIDA / "TSGU.glb")
    grupos = [("1", "GAB", "Gabinete RAL 7035 de 1200 × 2000 × 400 mm con zócalo (IP54)"),
              ("2", "PUERTA", "Puerta con manija con llave, burlete y ventilación con filtro"),
              ("3", "HMI", "Panel de operador TP1200 Comfort en la puerta"),
              ("4", "PLACA", "Placa de montaje galvanizada de 2 mm"),
              ("5", "QG", "Interruptor general 4P 40 A bloqueable"), ("6", "ΔI-B", "Diferencial tipo B 300 mA"),
              ("7", "QC", "Interruptores C de los variadores y guardamotores"), ("8", "VFD", "Variadores SINAMICS G120 (8)"),
              ("9", "KM", "Inversores de marcha de las desviadoras"), ("10", "SITOP", "Fuente SITOP 24 V 20 A con respaldo"),
              ("11", "PLC", "PLC-01 S7-1500F (CPU 1515F-2 PN)"), ("12", "SW", "Switch SCALANCE XC208 (anillos MRP)"),
              ("13", "UPS", "UPS de 1 kVA"), ("14", "BORN", "Borneras de salida"), ("15", "CAN", "Canaletas ranuradas")]
    pos = defaultdict(list)
    for i in e.inst:
        pos[i["cod"]].append(i["M"][:3, 3] / 1000 + np.array(_centro_caja(i)) / 1000)
    for n, cod, desc in grupos:
        P_ = np.array(pos[cod])
        c = P_[np.argmin(np.linalg.norm(P_ - P_.mean(0), axis=1))]
        items.append({"n": int(n), "descripcion": desc, "material": "", "punto": [round(float(v), 3) for v in c],
                      "candidatos": _candidatos(P_)})
    todos = np.array([p for v in pos.values() for p in v])
    meta = {"titulo": "TABLERO TS-GU (TRANSPORTE DE GUANO Y PLC-01)", "mira": [0.75, 1.0, -0.45], "piezas": len(e.inst),
            "items": items, "caja": [todos.min(0).round(2).tolist(), todos.max(0).round(2).tolist()]}
    (SALIDA / "TSGU.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"TSGU: {len(e.inst)} piezas")


def _candidatos(P, n_max=80):
    """Puntos de las piezas de una categoría (hasta n_max, repartidos) para elegir en la lámina el más visible."""
    P = np.asarray(P, float)
    if len(P) > n_max:
        P = P[np.linspace(0, len(P) - 1, n_max).round().astype(int)]
    return [[round(float(v), 3) for v in p] for p in P]


def _centro_caja(i):
    bb = cad.forma(i["key"]).BoundingBox()
    return ((bb.xmin + bb.xmax) / 2, (bb.ymin + bb.ymax) / 2, (bb.zmin + bb.zmax) / 2)


def main():
    e = cad.Escena("transporte")
    transporte.construir(e)
    electrica.construir(e)
    for nombre, conf in CONJUNTOS.items():
        armar(nombre, conf, e)
    tablero_ts_gu()


if __name__ == "__main__":
    main()
