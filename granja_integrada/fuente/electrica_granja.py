"""Instalación eléctrica, instrumentación y automatización de la granja integrada (Fases 7 y 8 de la consigna).

Alcance (consigna, punto 8): la planta de secado y sus equipos auxiliares, y de los galpones solo las conexiones del
transporte de guano (CCM de cada galpón). Lo del galpón que no es guano (ventilación, comederos, huevos, luz) lo define
el integrador del galpón; acá entra solo como carga preliminar (P) para dimensionar el transformador.

Criterio de cálculo, igual al de la Rev. F (fuente/calculos/calculos_memoria.py del proyecto anterior):
- Corriente de diseño de cada motor: I = P / (√3 · U · η · cos φ) (los valores de η y cos φ salen de calculos.json).
- Iz de la IEC 60364-5-52 (base de la AEA 90364-7-771) con factor de temperatura y de agrupamiento:
  bandeja (método E) 40 °C → 0,87 y agrupamiento 0,80; enterrado (método D1) 25 °C → 0,95.
- Ib ≤ In ≤ Iz e I2 ≤ 1,45 · Iz (interruptores termomagnéticos: I2 = 1,45 · In; guardamotores: regulados a In del motor).
- Caída de tensión ΔU = √3 · I · L · (R · cos φ + X · sen φ) con R a 70 °C. Límites: alimentadores ≤ 3 % y del origen
  al motor ≤ 5 % (AEA 90364-7-771).
- Cortocircuito: método de las impedancias (IEC 60909) con c = 1,05 para el máximo y c = 0,95 para el mínimo al final de
  cada línea; red de MT de 250 MVA y transformador de 315 kVA con ucc 4 % (ambos preliminares, P).
- Esquema de conexión a tierra TT, como en la Rev. F: diferenciales en todos los circuitos (tipo B en los variadores).

Los largos de cable salen de las canalizaciones del modelo 3D (fuente/modelo/electrica.py · red()): camino más corto
por bandejas y caños desde el tablero hasta el punto de la red más cercano al equipo, más el tramo final en caño, 1 m
por cada extremo y 5 % de reserva. Las ubicaciones de motores e instrumentos se leen del mismo modelo.

    python electrica_granja.py        # escribe datos/electrica.json
"""
from __future__ import annotations

import heapq
import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI / "modelo"))
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
K = json.loads((RAIZ / "datos" / "calculos.json").read_text(encoding="utf-8"))
L_REVF = json.loads((RAIZ / "datos" / "base" / "layout_planta_revF.json").read_text(encoding="utf-8"))
R_REVF = json.loads((RAIZ / "datos" / "base" / "resultados_revF.json").read_text(encoding="utf-8"))
SALIDA = RAIZ / "datos" / "electrica.json"

# ===================================================================================== criterio
U, UF = 380.0, 220.0
R3 = math.sqrt(3)
RHO20, ALFA = 0.0172, 0.00393
RHO70 = RHO20 * (1 + ALFA * 50)
X_CABLE = 0.08e-3                       # Ω/m
IZ = {"E": {1.5: 18.5, 2.5: 25, 4: 34, 6: 43, 10: 60, 16: 80, 25: 101, 35: 126, 50: 153, 70: 196, 95: 238, 120: 276},
      "D1": {1.5: 18, 2.5: 24, 4: 30, 6: 38, 10: 50, 16: 64, 25: 82, 35: 98, 50: 116, 70: 143, 95: 169, 120: 192}}
F_TEMP = {"E": 0.87, "D1": 0.95}
F_AGRUP = {"E": 0.80, "D1": 1.0}
IN_NORMAL = [2, 4, 6, 10, 13, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400]
GUARDAMOTOR = [(0.7, 1.0), (0.9, 1.25), (1.1, 1.6), (1.4, 2.0), (1.8, 2.5), (2.2, 3.2), (2.8, 4.0), (3.5, 5.0),
               (4.5, 6.3), (5.5, 8.0), (7.0, 10.0), (9.0, 12.5), (11.0, 16.0)]           # rangos tipo 3RV2011 (S00)
VFD_KW = [0.55, 0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5]
LIM_DU = {"motor": 5.0, "alimentador": 3.0}
RESERVA, TERMINAL, F_CANO = 1.05, 1.0, 1.3
# fuente y transformador (P: confirmar con la distribuidora y el fabricante)
S_RED_MVA, S_TR_KVA, UCC, PCU_KW = 250.0, 315.0, 0.04, 3.9
U0 = 400.0                               # tensión de vacío del secundario
DU_GALPON_MAX = 3.0                      # ΔU admitida del TGBT al CCM de cada galpón (alimentadores del integrador, P)
DU_TG2_MAX = 2.0                         # alimentador del TG2: deja margen a los circuitos de la Rev. F (≤ 2,17 % propios)
DU_TSG_MAX = 1.5                         # alimentador del TS de cada galpón (integrador, P)


def iz(s, metodo="E"):
    return IZ[metodo][s] * F_TEMP[metodo] * F_AGRUP[metodo]


def caida(i, largo, s, cos=0.85):
    sen = math.sqrt(1 - cos ** 2)
    du = R3 * i * largo * (RHO70 / s * cos + X_CABLE * sen)
    return du, 100 * du / U


def seccion(ib, largo, cos, lim, metodo="E", s_min=1.5, du_previo=0.0, i_prot=None):
    """Menor sección que cumple Iz ≥ max(Ib, protección) y la caída acumulada."""
    for s in IZ[metodo]:
        if s < s_min or iz(s, metodo) < max(ib, i_prot or 0):
            continue
        du, pct = caida(ib, largo, s, cos)
        if pct + du_previo <= lim:
            return s, round(iz(s, metodo), 1), round(pct, 2)
    raise ValueError(f"sin sección para Ib {ib} A y {largo} m")


def normal(i, minimo=6):
    return next(v for v in IN_NORMAL if v >= max(i, minimo))


def guardamotor(i):
    return next(f"{a}–{b} A" for a, b in GUARDAMOTOR if a <= i <= b)


def vfd_kw(kw):
    return next(v for v in VFD_KW if v >= kw - 1e-9)


# ===================================================================================== cortocircuito (IEC 60909)
def z_fuente():
    zq = 1.1 * U0 ** 2 / (S_RED_MVA * 1e6)
    xq, rq = 0.995 * zq, 0.0995 * zq
    zt = UCC * U0 ** 2 / (S_TR_KVA * 1e3)
    rt = PCU_KW * 1e3 * U0 ** 2 / (S_TR_KVA * 1e3) ** 2
    xt = math.sqrt(zt ** 2 - rt ** 2)
    return rq + rt, xq + xt


def z_linea(largo, s, temp=20):
    rho = RHO20 if temp == 20 else RHO70
    return rho * largo / s, X_CABLE * largo


def icc3(r, x, c=1.05):
    return c * U0 / (R3 * math.hypot(r, x)) / 1000           # kA


def icc_min_fin(r_up, x_up, largo, s):
    """Cortocircuito bifásico mínimo al final de la línea (c = 0,95, conductor a 70 °C), en A."""
    r, x = z_linea(largo, s, temp=70)
    return 0.95 * U0 / (2 * math.hypot(r_up + r, x_up + x))


# ===================================================================================== modelo 3D: posiciones y red
def escanear_modelo():
    import cad
    import electrica
    import galpon
    import planta
    import sitio
    import transporte
    e = cad.Escena("granja")
    sitio.construir(e)
    galpon.construir(e)
    planta.construir(e)
    transporte.construir(e)
    electrica.construir(e)
    tipos = {"Termorresistencia": "temperatura", "Transmisor de humedad": "humedad", "Transmisor de presión": "presión",
             "Medidor de nivel por radar": "nivel continuo", "Interruptor de nivel vibratorio": "nivel puntual",
             "Sensor de velocidad cero": "velocidad", "Interruptor de desvío de banda": "desvío de banda",
             "Interruptor de parada por cable": "parada de emergencia por cable", "Detector de atascamiento": "atasco",
             "Celda de carga": "peso", "Detector de llama": "llama", "Sensor de vibración": "vibración",
             "Final de carrera": "posición", "Baliza y sirena de prearranque": "señalización",
             "Botonera local con parada de emergencia": "parada de emergencia (botonera)",
             "Seccionador de seguridad bloqueable": "seccionador (contacto auxiliar)"}
    motores, instrumentos, tableros = {}, defaultdict(list), {}
    for i in e.inst:
        cod, nom, grupo = i["cod"], i["nom"], i["grupo"]
        if not cod or not nom:
            continue
        pos = tuple(round(float(v) / 1000, 2) for v in i["M"][:3, 3])
        if nom.startswith(("Motor ", "Motorreductor ")):
            motores.setdefault(cod, {"pos": pos, "grupo": grupo, "desc3d": nom})
        elif nom.startswith(("Tablero", "CCM-")):
            tableros.setdefault(cod, {"pos": pos, "nom": nom})
        else:
            for pref, tipo in tipos.items():
                if nom.startswith(pref):
                    instrumentos[cod].append({"pos": pos, "tipo": tipo, "grupo": grupo})
                    break
    # motores sin tag (ventiladores, carros): cuentan para la carga de cada galpón
    sin_tag = defaultdict(float)
    for i in e.inst:
        m = re.match(r"Motor\s+([\d.]+) kW", i["nom"])
        g = re.search(r" (G\d)$", i["grupo"])
        if m and g and not i["cod"]:
            sin_tag[g.group(1)] += float(m.group(1))
    return motores, instrumentos, tableros, electrica.red(), sin_tag


class Red:
    """Grafo de canalizaciones: polilíneas cortadas donde otra polilínea arranca o termina sobre ellas."""

    def __init__(self, polis):
        segs = []
        for nom, tipo, pts, r in polis:
            for a, b in zip(pts, pts[1:]):
                segs.append((tuple(a), tuple(b), nom, tipo))
        puntos = {tuple(p) for _, _, pts, _ in polis for p in pts}
        self.ady = defaultdict(list)
        self.segs = []
        for a, b, nom, tipo in segs:
            corte = [a, b]
            for p in puntos:
                if p in (a, b):
                    continue
                t, d = self._proy(p, a, b)
                if 1e-6 < t < 1 - 1e-6 and d < 0.03:
                    corte.append(p)
            corte.sort(key=lambda p: math.dist(a, p))
            for p, q in zip(corte, corte[1:]):
                w = math.dist(p, q)
                if w < 1e-9:
                    continue
                kp, kq = self._k(p), self._k(q)
                self.ady[kp].append((kq, w))
                self.ady[kq].append((kp, w))
                self.segs.append((p, q, nom, tipo))

    @staticmethod
    def _k(p):
        return tuple(round(v, 2) for v in p)

    @staticmethod
    def _proy(p, a, b):
        ab = [b[i] - a[i] for i in range(3)]
        L2 = sum(v * v for v in ab)
        if L2 == 0:
            return 0.0, math.dist(p, a)
        t = sum((p[i] - a[i]) * ab[i] for i in range(3)) / L2
        t = min(1.0, max(0.0, t))
        q = [a[i] + t * ab[i] for i in range(3)]
        return t, math.dist(p, q)

    def unir(self, p, q, w=None):
        kp, kq = self._k(p), self._k(q)
        w = math.dist(p, q) if w is None else w
        self.ady[kp].append((kq, w))
        self.ady[kq].append((kp, w))

    def distancias(self, origen):
        d = {self._k(origen): 0.0}
        cola = [(0.0, self._k(origen))]
        while cola:
            dd, u = heapq.heappop(cola)
            if dd > d.get(u, 1e18):
                continue
            for v, w in self.ady[u]:
                nd = dd + w
                if nd < d.get(v, 1e18):
                    d[v] = nd
                    heapq.heappush(cola, (nd, v))
        return d

    def a_equipo(self, dist, p, excluir=("subterraneo",)):
        """(largo por la red, largo del tramo final en caño) desde el origen de `dist` hasta el equipo en p."""
        cands = []
        for a, b, nom, tipo in self.segs:
            if tipo in excluir:
                continue
            ka, kb = self._k(a), self._k(b)
            if ka not in dist and kb not in dist:
                continue
            t, dfin = self._proy(p, a, b)
            q = [a[i] + t * (b[i] - a[i]) for i in range(3)]
            dred = min(dist.get(ka, 1e18) + math.dist(a, q), dist.get(kb, 1e18) + math.dist(b, q))
            cands.append((dfin, dred))
        # el cable sale de la canalización más cercana al equipo (no se tiende "por el aire" desde lejos)
        dmin = min(c[0] for c in cands)
        dfin, dred = min((c for c in cands if c[0] <= dmin + 0.5), key=lambda c: c[1] + c[0] * F_CANO)
        return dred, dfin * F_CANO


def largo_cable(red_, dist, p):
    dred, dfin = red_.a_equipo(dist, p)
    return round((dred + dfin + 2 * TERMINAL) * RESERVA, 1), round(dred, 1), round(dfin, 1)


def largo_polilinea(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


# ===================================================================================== motores
def describir(m, gid=None):
    """Función, ubicación y vínculo mecánico de un motor nuevo, en palabras."""
    nom = m["nom"]
    trans = {t["id"]: t for t in K["transportadores"]}
    if nom.startswith("Cinta de guano"):
        mm = re.search(r"piso (\d) fila (\w)", nom)
        return ("Mueve la cinta de polipropileno bajo las jaulas y descarga el guano de la fila en la cabecera Sur",
                f"cabecera Sur del {gid}, fila {mm.group(2)}, piso {mm.group(1)}",
                "motorreductor ortogonal de eje hueco sobre el rodillo motriz de la cinta (≈ 10 m/min)")
    cid = nom.split()[-1]
    if cid in ("G1", "G2", "G3", "G4"):
        cid = ("CT-" if "transversal" in nom else "CI-") + cid[1]
    t = trans.get(cid)
    if t:
        mec = (f"motorreductor ortogonal de eje hueco i ≈ {t['relacion_reductor']:.0f} sobre el tambor motriz "
               f"Ø{t['tambor_D_m'] * 1000:.0f} mm ({t['rpm_tambor']:.0f} rpm, banda a {t['v_m_s']} m/s), con brazo de reacción")
        if cid.startswith("CT"):
            return ("Junta el guano de las 4 filas en el canal de la cabecera y lo lleva al pie de la inclinada",
                    f"canal de H° de la cabecera Sur del {gid}", mec)
        if cid.startswith("CI"):
            return ("Sube el guano desde el foso de la cabecera hasta la colectora (+7,1 m)",
                    f"cabezal sobre la colectora, al Sur del {gid}", mec)
        if cid.startswith("CE"):
            return (f"Colectora del lado {cid[-1]}: recibe las inclinadas de los dos galpones y descarga en la torre",
                    f"cabezal dentro de la torre TT-{cid[-1]}", mec)
        if cid.startswith("CP"):
            return (f"Principal del lado {cid[-1]}: lleva el guano de la torre a la tapa de la tolva pulmón TP-01",
                    "cabezal en el pórtico PC-01 sobre la TP-01", mec)
    if "Sinfín" in nom:
        return ("Dosifica el guano del fondo vivo de la TP-01 a la cinta de alimentación del secador",
                "lado Norte de la TP-01, en el extremo de cada sinfín",
                "motorreductor coaxial con patas y acople elástico al eje del sinfín Ø400")
    if "desviadora" in nom:
        dv = nom.split()[-1]
        return (f"Mueve la clapeta de la desviadora {dv}: posición A a la planta, B al contenedor de emergencia",
                f"sobre la desviadora, dentro de la torre TT-{dv[-1]}",
                "actuador eléctrico de cuarto de vuelta con finales de carrera ZSA/ZSB, acoplado al eje de la clapeta")
    return ("", "", "")


def motores_lista(pos3d, red_planta, dist_gu, redes_g, dist_ccm, du_gu, du_ccm):
    lista = []
    # ---------------------------------------------------------------- Rev. F: tablero TGF (M1 a M15)
    vinculo_rf = {"M1": "acople directo (ventilador centrífugo)", "M2": "acople directo (ventilador centrífugo)",
                  "M3": "acople directo (extractor centrífugo)", "M4": "acople directo (ventilador de combustión)",
                  "M5": "reductor doble sinfín 1:300 + cadena ASA 60 Z15/Z75 al tambor motriz",
                  "M6": "reductor doble sinfín 1:300 + cadena ASA 60 Z15/Z75 al tambor motriz",
                  "M7": "reductor doble sinfín 1:300 + cadena ASA 60 Z15/Z75 al tambor motriz",
                  "M8": "motorreductor al tambor motriz de la cinta de alimentación (3)",
                  "M9": "motorreductor al rodillo esparcidor de paletas", "M10": "motorreductor al eje del sinfín",
                  "M11": "motorreductor al tambor de cabeza del elevador", "M12": "motorreductor al sinfín de cáscara",
                  "M13": "motorreductor al sinfín de cenizas", "M14": "acople directo (bomba centrífuga del lavador)",
                  "M15": "vibrador de masa excéntrica"}
    for m in L_REVF["motores"]:
        quitado = m["tag"] == "M15"
        lista.append({"tag": m["tag"], "funcion": m["nom"], "ubicacion": "planta (Rev. F)", "tablero": "TGF",
                      "kW": m["P"], "origen_kW": "R", "In_A": round(m["In"], 2), "arranque": m["arr"],
                      "vinculo": vinculo_rf.get(m["tag"], ""),
                      "proteccion": "interruptor + variador" if m["arr"] == "VFD" else f"guardamotor {m['gm'][0]}–{m['gm'][1]} A + contactor",
                      "mando": "PLC-02 (S7-1200 del SC-4)", "S_mm2": m["sec"], "L_m": m["L"], "dU_pct": round(m["dU"], 2),
                      "estado": "se quita (vibrador de la tolva vieja de 3,1 m³)" if quitado else "sin cambios (Rev. F)",
                      "pos": None})
    # ---------------------------------------------------------------- Rev. F: TG2 y subtableros (M16 a M40)
    for m in R_REVF["tg2"]["motores"]:
        estado = "sin cambios (Rev. F)"
        if m["tablero"].startswith("TS-BIO"):
            estado = "se quita (biogás)"
        elif m["tablero"] == "TS-LAV":
            estado = "se quita (ya no entran camiones de guano)"
        elif m["tag"] == "M23":
            estado = "se mantiene: ahora aspira la tapa de la tolva pulmón TP-01 hacia el biofiltro"
        lista.append({"tag": m["tag"], "funcion": m["nom"] if m["tag"] != "M23" else "Extractor de aspiración de la TP-01 al biofiltro",
                      "ubicacion": "planta (Rev. F)", "tablero": m["tablero"], "kW": m["kW"], "origen_kW": "R",
                      "In_A": m["In"], "arranque": m["arranque"], "vinculo": "según Rev. F",
                      "proteccion": "según Rev. F", "mando": "PLC-01 (permisivo de las rutas)" if m["tag"] == "M23" else "local / PLC-02",
                      "S_mm2": None, "L_m": None, "dU_pct": None, "estado": estado, "pos": None})
    # ---------------------------------------------------------------- nuevos: TS-GU y CCM de cada galpón
    for m in K["motores_nuevos"]:
        tag, kw, ib = m["tag"], m["kW"], m["In"]
        cid = m["nom"].split()[-1]
        t = next((x for x in K["transportadores"] if x["id"] == cid), None)
        cos = t["cosf"] if t else (0.81 if kw >= 3 else (0.77 if kw >= 1.1 else 0.72))
        p = pos3d.get(tag, {}).get("pos")
        if m["tablero"] == "TS-GU":
            tablero, gid = "TS-GU", None
            L, Lred, Lfin = largo_cable(red_planta, dist_gu, p)
            du_prev = du_gu
            if m["arranque"] == "inversor":
                arr, prot = "inversor de marcha (2 contactores enclavados)", f"guardamotor {guardamotor(ib)} + 2 contactores"
            else:
                arr = f"variador SINAMICS G120 {vfd_kw(kw)} kW (PM240-2 + CU240E-2 PN-F)"
                prot = f"interruptor C{normal(2 * ib)} + diferencial tipo B 300 mA + protección electrónica del variador"
            mando = "PLC-01 por PROFINET, STO por PROFIsafe" if "variador" in arr else "PLC-01 (salidas del RIO de la torre)"
            secc = f"Q-{tag} bloqueable junto al motor"
        else:
            gid = m["tablero"].replace("TS-", "")
            tablero = f"CCM-{gid}"
            L, Lred, Lfin = largo_cable(redes_g[gid], dist_ccm[gid], p)
            du_prev = du_ccm[gid]
            if m["arranque"] == "VFD":
                arr = f"variador SINAMICS G120C PN {vfd_kw(kw)} kW"
                prot = f"interruptor C{normal(2 * ib)} + diferencial tipo B 300 mA + protección electrónica del variador"
                mando = f"PLC-01 por PROFINET (CCM-{gid}), STO por PROFIsafe"
            else:
                arr = "directo (contactor)"
                prot = f"guardamotor {guardamotor(ib)} regulado a {ib:.2f} A + contactor"
                mando = f"PLC-01 por RIO-{gid} (ET 200SP del CCM-{gid})"
            secc = f"interruptor del CCM-{gid} bloqueable con candado (a la vista de la cabecera)"
        vfd = "variador" in arr
        s, izz, du = seccion(ib, L, cos, LIM_DU["motor"], s_min=2.5 if vfd else 1.5, du_previo=du_prev)
        funcion, ubic, vinc = describir(m, gid)
        lista.append({"tag": tag, "funcion": funcion, "nombre": m["nom"], "ubicacion": ubic, "pos": p, "tablero": tablero,
                      "kW": kw, "origen_kW": "P", "nota_kW": m.get("nota", ""), "In_A": ib, "cos_phi": cos, "arranque": arr,
                      "vinculo": vinc, "proteccion": prot, "seccionador": secc, "mando": mando,
                      "cable": f"{'apantallado ' if vfd else ''}4G{s} mm² Cu/PVC 1 kV",
                      "S_mm2": s, "Iz_A": izz, "L_m": L, "L_bandeja_m": Lred, "L_cano_m": Lfin, "dU_pct": du,
                      "dU_aguas_arriba_pct": round(du_prev, 2), "dU_total_pct": round(du + du_prev, 2), "estado": "nuevo"})
    return lista


# ===================================================================================== balance de potencia y transformador
def balance(mot, sin_tag, motores_3d):
    """Demanda de la granja por tablero (P para lo que no es alcance de la planta)."""
    gal = defaultdict(float, sin_tag)
    for tag, v in motores_3d.items():          # huevos y silos (con tag), sin los de guano
        m = re.search(r"([\d.]+) kW", v["desc3d"])
        if not m:
            continue
        if re.match(r"MH\d\d$", tag):                         # elevadores de huevos: MH<galpón><fila>
            gal[f"G{tag[2]}"] += float(m.group(1))
        elif tag.startswith("MS-") and re.search(r"G(\d)", tag):
            gal[f"G{re.search(r'G(\d)', tag).group(1)}"] += float(m.group(1))
    filas = [("TGF (secador SC-4, Rev. F)", "R", 59.0, 1.0, "balance de la Rev. F: 54 a 59 kW; se toma el máximo")]
    tg2 = R_REVF["tg2"]
    quedan = [c for c in tg2["circuitos"] if c["Q"] not in ("Q22", "Q23")]
    kw_tg2_rf = sum(c["kW"] for c in quedan)
    kw_gu = sum(m["kW"] for m in mot if m.get("tablero") == "TS-GU")
    filas.append(("TG2 sin biogás ni lavadero (Rev. F)", "R", round(kw_tg2_rf, 2), 0.75, "Q21, Q24, Q25, Q26, Q27"))
    filas.append(("TS-GU (en TG2 · Q23): cintas principales, colectoras, desviadoras y sinfines", "P", round(kw_gu, 2), 0.80,
                  "los dos lados vaciando y los 4 sinfines dosificando"))
    for g in ("G1", "G2", "G3", "G4"):
        kw_ccm = sum(m["kW"] for m in mot if m.get("tablero") == f"CCM-{g}")
        filas.append((f"TS-{g}: equipos del galpón contados en el 3D (ventiladores, carros, huevos, silos)", "P", round(gal[g], 2),
                      0.85, "ventilación de verano a pleno"))
        filas.append((f"TS-{g}: alumbrado LED, bombas de los paneles, controlador y varios", "P", 4.0, 0.80, "estimado"))
        if kw_ccm:
            filas.append((f"CCM-{g}: cintas de guano (un piso por vez: 4 cintas + CT + CI)", "P", round(kw_ccm, 2),
                          round((4 * 1.1 + 0.55 + 1.1) / kw_ccm, 3), "secuencia del PLC: 6,05 kW en marcha"))
    filas.append(("Depósitos DH-O y DH-E (transelevador, mesas, cintas, luz)", "P", 20.0, 0.60, "estimado"))
    filas.append(("Servicios: bombeo de agua, alumbrado exterior, bioseguridad y garita", "P", 10.0, 0.70, "estimado"))
    tot_inst = sum(f[2] for f in filas)
    tot_dem = sum(f[2] * f[3] for f in filas)
    simult, cos_g = 0.90, 0.90
    s_kva = tot_dem * simult / cos_g
    return {"filas": [{"carga": a, "tipo": b, "kW_instalados": c, "factor": d, "kW_demanda": round(c * d, 2), "nota": e}
                      for a, b, c, d, e in filas],
            "kW_instalados": round(tot_inst, 1), "kW_demanda": round(tot_dem, 1), "simultaneidad_tableros": simult,
            "cos_phi_global": cos_g, "kVA_demanda": round(s_kva, 1), "transformador_kVA": S_TR_KVA,
            "carga_transformador_pct": round(100 * s_kva / S_TR_KVA, 1),
            "nota": "315 kVA (P) deja lugar para la ampliación (2 galpones más ≈ 50 kVA) y para los arranques",
            "kW_TS_GU": round(kw_gu, 2), "kW_TG2_RevF": round(kw_tg2_rf, 2)}


# ===================================================================================== alimentadores y cortocircuito
def alimentadores(polis, bal, tableros3d):
    rf, xf = z_fuente()
    pol = {n: p for n, _, p, _ in polis}
    out = []

    def linea(nombre, desde, hasta, kw, cos, largo, metodo, lim, du_prev, r_up, x_up, s_min=4, i_extra=0.0, tipo="P"):
        ib = kw * 1000 / (R3 * U * cos) + i_extra
        inn = normal(ib, 10)
        s, izz, du = seccion(ib, largo, cos, lim, metodo=metodo, s_min=s_min, du_previo=du_prev, i_prot=inn)
        r, x = z_linea(largo, s)
        fila = {"circuito": nombre, "desde": desde, "hasta": hasta, "tipo": tipo, "kW_demanda": round(kw, 2),
                "Ib_A": round(ib, 1), "In_A": inn, "S_mm2": s, "metodo": metodo, "Iz_A": izz, "L_m": round(largo, 1),
                "dU_pct": du, "dU_total_pct": round(du + du_prev, 2), "I2_A": round(1.45 * inn, 1),
                "lim_I2_A": round(1.45 * izz, 1), "verifica": ib <= inn <= izz and du + du_prev <= lim,
                "Icc3_fin_kA": round(icc3(r_up + r, x_up + x), 2)}
        out.append(fila)
        return fila, r_up + r, x_up + x

    filas = {f["carga"]: f for f in bal["filas"]}
    L = {k: largo_polilinea(pol[f"Alimentador TGBT → {k} (enterrado)"]) * RESERVA + 2 * TERMINAL for k in ("TG2", "TGF")}
    f_tgf, r_tgf, x_tgf = linea("QF1 · alimentador del TGF", "TGBT", "TGF", 59.0, 0.85, L["TGF"], "D1",
                                LIM_DU["alimentador"], 0, rf, xf, tipo="R (cargas) / P (línea)")
    k_gu = "TS-GU (en TG2 · Q23): cintas principales, colectoras, desviadoras y sinfines"
    dem_tg2 = filas["TG2 sin biogás ni lavadero (Rev. F)"]["kW_demanda"] + filas[k_gu]["kW_demanda"]
    f_tg2, r_tg2, x_tg2 = linea("QF2 · alimentador del TG2", "TGBT", "TG2", dem_tg2, 0.85, L["TG2"], "D1",
                                DU_TG2_MAX, 0, rf, xf)
    L_gu = largo_polilinea(pol["Bandeja de la sala de control TG2 → TS-GU"]) * RESERVA + 2 * TERMINAL
    f_gu, r_gu, x_gu = linea("TG2 · Q23 → TS-GU (salida que era del TS-BIO)", "TG2", "TS-GU", filas[k_gu]["kW_demanda"],
                             0.80, L_gu, "E", LIM_DU["alimentador"], f_tg2["dU_pct"], r_tg2, x_tg2, s_min=6, i_extra=3.0)
    ccm = {}
    for g in D["galpones"]:
        gid = g["id"]
        ts = tableros3d.get(f"TS-{gid}", {}).get("pos") or (g["x"], g["y1"] + 3.0, 0.0)
        L_ts = (abs(ts[0] - (-7.4)) + abs(ts[1] - (-74.4)) + 2) * 1.10 + 2 * TERMINAL
        kw_g = sum(f["kW_demanda"] for f in bal["filas"] if f"TS-{gid}" in f["carga"] or f"CCM-{gid}" in f["carga"])
        f_ts, r_ts, x_ts = linea(f"QF{2 + int(gid[1])} · alimentador del TS-{gid} (integrador del galpón)", "TGBT",
                                 f"TS-{gid}", kw_g, 0.85, L_ts, "D1", DU_TSG_MAX, 0, rf, xf, s_min=16)
        L_c = largo_polilinea(pol[f"Alimentador TS-{gid} → CCM-{gid} (enterrado)"]) * RESERVA + 2 * TERMINAL
        kw_c = filas[f"CCM-{gid}: cintas de guano (un piso por vez: 4 cintas + CT + CI)"]["kW_demanda"]
        f_c, r_c, x_c = linea(f"TS-{gid} → CCM-{gid}", f"TS-{gid}", f"CCM-{gid}", kw_c, 0.78, L_c, "D1", DU_GALPON_MAX,
                              f_ts["dU_pct"], r_ts, x_ts, s_min=6, i_extra=2.0)
        ccm[gid] = (r_c, x_c, f_c["dU_total_pct"])
    imp = {"TGF": (r_tgf, x_tgf, f_tgf["dU_pct"]), "TG2": (r_tg2, x_tg2, f_tg2["dU_pct"]),
           "TS-GU": (r_gu, x_gu, f_gu["dU_total_pct"])}
    return out, imp, ccm


def poder_de_corte(i_tgbt, i_tab, i_ccm):
    """Poder de corte pedido a cada tablero según su Icc máxima (la Rev. F eligió los del TG2 para 4,5 kA)."""
    def pc(i):
        return next(v for v in (4.5, 6, 10, 15, 25, 36) if v >= i * 1.0)
    txt = [f"TGBT: Icc {i_tgbt:.1f} kA → interruptores de {pc(i_tgbt):g} kA o más"]
    for k, i in i_tab.items():
        nota = ""
        if k in ("TGF", "TG2") and i > 4.5:
            nota = " (subió respecto de la Rev. F: verificar que sus interruptores sean de 6 kA o más y cambiar los de 4,5 kA)"
        elif k in ("TGF", "TG2"):
            nota = " (los de la Rev. F alcanzan)"
        txt.append(f"{k}: Icc {i:.2f} kA → {max(pc(i), 4.5):g} kA o más{nota}")
    txt.append("CCM: Icc " + ", ".join(f"{g} {i:.2f} kA" for g, i in i_ccm.items()) + " → 6 kA (guardamotores y variadores con su protección)")
    return txt


def tg2_circuitos(du_alim):
    """Circuitos del TG2 de la Rev. F con su nueva caída total (alimentador nuevo desde el TGBT)."""
    out = []
    for c in R_REVF["tg2"]["circuitos"]:
        estado = {"Q22": "queda de reserva (lavadero quitado)", "Q23": "ahora alimenta al TS-GU (ver alimentadores)",
                  "Q25": "sin los 4 proyectores Ex de la zona de biogás"}.get(c["Q"], "sin cambios")
        out.append({"Q": c["Q"], "destino": c["destino"], "kW": c["kW"], "In_A": c["In"], "S_mm2": c["S"], "L_m": c["L"],
                    "dU_circuito_pct": c["dU_pct"], "dU_total_nuevo_pct": round(c["dU_pct"] + du_alim, 2),
                    "estado": estado})
    return out


# ===================================================================================== instrumentos y E/S
SENAL = {"velocidad": ("DI", 1, "sensor inductivo frente a la maza del tambor de cola (PNP, 24 V)"),
         "desvío de banda": ("DI", 2, "rodillo vertical a 15° del borde: 1.er contacto alarma, 2.º parada"),
         "parada de emergencia por cable": ("F-DI", 2, "cable a lo largo de la pasarela, interruptor con 2 contactos NC"),
         "parada de emergencia (botonera)": ("F-DI", 2, "hongo con enclavamiento, 2 contactos NC"),
         "atasco": ("DI", 1, "péndulo en el chute (contacto NA)"),
         "nivel continuo": ("AI", 1, "radar de 80 GHz, 4-20 mA HART"),
         "nivel puntual": ("F-DI", 2, "horquilla vibratoria con salida de seguridad (SIL 2)"),
         "peso": ("SIWAREX", 1, "celda de compresión C3 bajo cada columna, caja sumadora"),
         "posición": ("DI", 1, "final de carrera del actuador"),
         "señalización": ("DQ", 2, "baliza (luz) y sirena de prearranque"),
         "temperatura": ("AI", 1, "Pt100 a 4 hilos"), "llama": ("DI", 1, ""), "vibración": ("AI", 1, ""),
         "seccionador (contacto auxiliar)": ("DI", 1, "contacto auxiliar del seccionador junto al motor")}


def periferia(tag, pos):
    m = re.search(r"-(?:CT|CI)-(\d)$", tag) or re.match(r"(?:SS|HS)-M?(\d)\d\d$", tag) or re.match(r"HS-G(\d)-", tag)
    if m:
        return f"RIO-G{m.group(1)}"
    x = pos[0]
    if 0.0 <= x <= 33.0:
        return "RIO-TP"
    return "RIO-O" if x < 0 else "RIO-E"


def nodo_rio(polis, rio):
    if rio == "RIO-TP":
        return next(p for n, _, p, _ in polis if n.startswith("Bajada de la CP-E al RIO-TP"))[-1]
    if rio in ("RIO-O", "RIO-E"):
        return next(p for n, _, p, _ in polis if n == f"Bajada al {rio}")[-1]
    gid = rio[-2:]
    return next(p for n, _, p, _ in polis if n == f"Bandeja de la cabecera de guano del {gid}")[0]


def instrumentos_lista(ins3d, polis, red_planta, redes_g):
    dist_rio = {}
    lista = []
    for tag, usos in sorted(ins3d.items()):
        tipo = usos[0]["tipo"]
        grupo = usos[0]["grupo"]
        fuera = tag.startswith(("TH-", "PDT-", "WT-SA", "SS-CH")) or "silos" in grupo or "huevos" in grupo
        if fuera:
            lista.append({"tag": tag, "tipo": tipo, "cantidad": len(usos), "senal": "—", "periferia": "—",
                          "alcance": "galpón / depósito (controlador del galpón, fuera de alcance)", "pos": usos[0]["pos"]})
            continue
        sig, canales, montaje = SENAL.get(tipo, ("DI", 1, ""))
        if tag.startswith("ZS-REG"):
            tipo, sig, canales, montaje = ("enclavamiento de registro", "F-DI", 2,
                                           "interruptor de seguridad con lengüeta codificada en el registro de la tapa")
        elif tipo.startswith("seccionador") and tag in ("Q-M85", "Q-M86", "Q-M87", "Q-M88"):
            sig, canales, montaje = "F-DI", 2, "contacto auxiliar de seguridad de la estación de bloqueo de los sinfines"
        unidades = []
        for u in usos:
            rio = periferia(tag, u["pos"])
            red_ = red_planta if rio in ("RIO-TP", "RIO-O", "RIO-E") else redes_g[rio[-2:]]
            if rio not in dist_rio:
                dist_rio[rio] = red_.distancias(nodo_rio(polis, rio))
            L, _, _ = largo_cable(red_, dist_rio[rio], u["pos"])
            unidades.append({"pos": u["pos"], "periferia": rio, "L_m": L})
        lista.append({"tag": tag, "tipo": tipo, "cantidad": len(usos), "senal": sig, "canales_por_unidad": canales,
                      "montaje": montaje, "periferia": " / ".join(sorted({u["periferia"] for u in unidades})),
                      "alcance": "planta / transporte",
                      "cable": "4 × 1 mm² apantallado" if sig in ("AI", "SIWAREX") else ("4 × 1,5 mm²" if canales == 2 else "3 × 1,5 mm²"),
                      "L_total_m": round(sum(u["L_m"] for u in unidades), 1), "unidades": unidades})
    return lista


def io_resumen(instr, mot):
    io = defaultdict(lambda: defaultdict(int))
    for i in instr:
        if i["alcance"] != "planta / transporte":
            continue
        for u in i["unidades"]:
            io[u["periferia"]][i["senal"]] += i["canales_por_unidad"]
    # motores: marcha y falla de los arranques directos e inversores (DI) y orden (DQ); variadores por PROFINET
    for m in mot:
        if m.get("estado") != "nuevo":
            continue
        if m["tablero"].startswith("CCM"):
            rio = "RIO-" + m["tablero"][4:]
        else:
            x = m["pos"][0]
            rio = "RIO-TP" if 0 <= x <= 33 else ("RIO-O" if x < 0 else "RIO-E")
        if "variador" in m["arranque"]:
            io[rio]["PROFINET (variadores)"] += 1
        elif "inversor" in m["arranque"]:
            io[rio]["DQ"] += 2
            io[rio]["DI"] += 1
        else:
            io[rio]["DQ"] += 1
            io[rio]["DI"] += 2
    canales = {"DI": 16, "F-DI": 8, "DQ": 8, "AI": 4}
    res = {}
    for rio, s in sorted(io.items()):
        res[rio] = {"señales": dict(s),
                    "modulos_ET200SP_con_20pct_reserva": {k: math.ceil(v * 1.2 / canales[k]) for k, v in s.items() if k in canales},
                    "SIWAREX_WP231": 1 if s.get("SIWAREX") else 0}
    return res


# ===================================================================================== automatización
SECUENCIA = [
    {"n": 1, "etapa": "Detección de disponibilidad de guano",
     "acciones": ["cada galpón pide el vaciado de sus cintas de piso según su programa (una vez por día y por piso, en ventanas horarias que fija el encargado)",
                  "el PLC-01 acepta el pedido si la TP-01 tiene lugar para todo el galpón: LT-101 < 80 % y peso de WT-101 a 104 < 32 t"],
     "transicion": "pedido aceptado (un galpón por vez en cada lado; los lados Oeste y Este pueden correr juntos)"},
    {"n": 2, "etapa": "Activación del sistema de transporte",
     "acciones": ["prearranque: baliza y sirena XA de toda la ruta durante 10 s", "desviadora DV-x a la posición A (planta)",
                  "arranque de aguas abajo hacia aguas arriba: CP-x → CE-x → CI-g → CT-g, con rampa de 5 s en los variadores"],
     "transicion": "cada cinta confirma velocidad (SSL) antes de que arranque la siguiente"},
    {"n": 3, "etapa": "Verificación de transportadores",
     "acciones": ["velocidad confirmada en ≤ 5 s (SSL)", "sin desvío de banda (ZS)", "sin chute lleno (LSH)",
                  "variadores listos y sin falla", "desviadora en A confirmada por ZSA"],
     "transicion": "ruta completa en marcha y verificada"},
    {"n": 4, "etapa": "Verificación de condiciones de seguridad (permisivos)",
     "acciones": ["ninguna parada de emergencia, botonera de fila ni cable de parada accionado (F-DI por PROFIsafe sano)",
                  "registros de la TP-01 cerrados y estación de bloqueo de los sinfines liberada",
                  "extractor M23 en marcha (aspiración de la TP-01 al biofiltro)", "central de incendio sin alarma",
                  "comunicación sana con todas las periferias de la ruta"],
     "transicion": "si falta un permisivo la ruta no arranca y la pantalla dice cuál: la planta no arranca con condiciones inseguras"},
    {"n": 5, "etapa": "Alimentación de la tolva",
     "acciones": ["arrancan las 4 cintas de piso de un piso por vez (9,4 min por piso, 5 pisos por galpón)",
                  "el guano entra a la TP-01 por las bocas de la tapa; el PLC sigue el nivel (LT-101) y el peso (WT-101 a 104)"],
     "transicion": "galpón vaciado o TP-01 alta-alta (LSHH-101)"},
    {"n": 6, "etapa": "Dosificación",
     "acciones": ["sinfines M85 a M88 con variador: dosificación por pérdida de peso (FIC-101) a la consigna del secador",
                  "la cinta de alimentación (M8) acompaña con su variador", "consigna de régimen 1.260 kg/h de guano húmedo"],
     "transicion": "caudal estable ± 5 % durante 2 min"},
    {"n": 7, "etapa": "Inicio del proceso de secado",
     "acciones": ["secuencia del SC-4 de la Rev. F en el PLC-02: extractor M3, impulsión M1 y M2, barrido del hogar",
                  "encendido con el piloto a GLP, detección de llama y alimentación de cáscara (M12)",
                  "bandas M5 a M7 y esparcidor M9 cuando el aire llega a la consigna"],
     "transicion": "aire ≥ consigna − 10 °C: habilita la dosificación del paso 6"},
    {"n": 8, "etapa": "Regulación de variables",
     "acciones": ["TIC-01: temperatura del aire con la cáscara (M12) y el aire de combustión (M4) (Rev. F)",
                  "MIC-01: humedad del producto al 15 % en cascada sobre TIC-01 (Rev. F)",
                  "FIC-101: caudal de guano con la velocidad de los sinfines", "PIC: depresión de la cámara con M3"],
     "transicion": "régimen"},
    {"n": 9, "etapa": "Monitoreo",
     "acciones": ["alarmas, tendencias e historial en el TP1200 de la sala de control y acceso remoto por VPN",
                  "reserva de la TP-01 en horas, vaciado de cada galpón, horas de marcha, consumos y fallas"],
     "transicion": "continuo"},
    {"n": 10, "etapa": "Descarga",
     "acciones": ["sinfín de descarga M10 → elevador M11 → tolva de retención F1 (1 h a ≥ 70 °C) → enfriador M40",
                  "desviadora M35: acopio o envasado"],
     "transicion": "producto frío (< 40 °C)"},
    {"n": 11, "etapa": "Transporte del producto procesado",
     "acciones": ["zaranda M18 → ensacadora (M19 a M22, M24) → palets al depósito de expedición E7",
                  "despacho a granel por el portón P2"],
     "transicion": "continuo"},
    {"n": 12, "etapa": "Parada controlada",
     "acciones": ["transporte: primero las cintas de piso y después CT → CI → CE → CP, cada una con su tiempo de vaciado (largo / velocidad + 30 s)",
                  "secador: corta la dosificación, las bandas siguen hasta vaciar la cámara, el hogar se apaga con post-barrido y los ventiladores enfrían hasta < 60 °C"],
     "transicion": "planta detenida y vacía"},
    {"n": 13, "etapa": "Manejo de fallas",
     "acciones": ["parada de emergencia o cable: parada categoría 0 de la zona por PROFIsafe (STO en los variadores, contactores abiertos)",
                  "falla de una cinta (velocidad, desvío, atasco, sobrecarga): se para esa cinta y todo lo de aguas arriba; lo de aguas abajo se vacía y para",
                  "TP-01 llena (LSHH-101): se cortan las rutas; con el secador parado el operador puede mandar la desviadora a B (contenedor de emergencia)",
                  "disparo del secador: se corta la dosificación y la TP-01 acumula (2,3 días de reserva)",
                  "pérdida de comunicación con una periferia: estado seguro de su zona",
                  "corte de energía: rearranque solo con reconocimiento del operador (UPS en PLC, pantallas y red)"],
     "transicion": "reconocimiento y vuelta al paso 1"},
]

ENCLAVAMIENTOS = [
    ("Parada de emergencia, botonera de fila o cable de parada de la ruta", "para toda la ruta del lado (categoría 0, STO)", "F-DI → F-CPU"),
    ("Cinta de aguas abajo detenida o sin velocidad (SSL)", "no arranca / para la de aguas arriba", "lógica de cascada"),
    ("Desvío de banda (ZS, 2.º contacto)", "para la cinta y las de aguas arriba", "DI"),
    ("Chute lleno (LSH)", "para la cinta que descarga en ese chute y las de aguas arriba", "DI"),
    ("TP-01 alta-alta (LSHH-101)", "para CP-O y CP-E y todo lo de aguas arriba", "F-DI"),
    ("TP-01 baja (LSL-101)", "para los sinfines M85 a M88 y avisa al secador", "F-DI"),
    ("Estación de bloqueo de los sinfines o registro de la TP-01 abierto", "sinfines y cintas principales bloqueados", "F-DI"),
    ("Extractor M23 detenido", "no se permite arrancar rutas hacia la TP-01", "estado del variador"),
    ("Desviadora sin posición confirmada (ZSA/ZSB)", "no arranca la colectora del lado", "DI"),
    ("Aire del secador bajo la consigna o falla del hogar", "no se dosifica (sinfines detenidos)", "PLC-02 → PLC-01"),
    ("Alarma de la central de incendio", "para transporte y secador; M23 sigue según la matriz de incendio de la Rev. F", "DI"),
    ("Sobrecarga del motor o falla del variador", "para el equipo y lo de aguas arriba", "PROFINET / DI"),
]

FALLAS = [
    ("Falta de velocidad (SSL) con orden de marcha", "banda patinando, rota o motor sin tensión", "parada de la cinta y aguas arriba; alarma", "revisar tensión de banda, tambor y motor"),
    ("Desvío de banda (1.er contacto)", "banda corrida", "alarma", "centrar la banda en la próxima parada"),
    ("Desvío de banda (2.º contacto)", "banda muy corrida", "parada de la cinta y aguas arriba", "centrar la banda y revisar rodillos"),
    ("Chute lleno (LSH)", "atasco en la transferencia", "parada de la cinta que descarga y aguas arriba", "limpiar el chute con el motor bloqueado"),
    ("Sobrecarga del guardamotor o falla del variador", "material pesado, rodamiento trabado o falla eléctrica", "parada del equipo y aguas arriba", "revisar el equipo y reponer"),
    ("TP-01 alta-alta", "secador parado con galpones vaciando", "corte de rutas", "esperar o desviar al contenedor (solo con el secador parado)"),
    ("TP-01 baja", "falta de guano", "parada de sinfines; secador a mínimo o parada controlada", "programar vaciados"),
    ("Desviadora sin posición", "actuador trabado o final de carrera", "no arranca la colectora", "revisar la clapeta y los finales"),
    ("Pérdida de comunicación con una periferia", "fibra cortada o switch", "estado seguro de esa zona", "el anillo MRP mantiene el resto"),
    ("Parada de emergencia", "accionada por una persona", "parada categoría 0 de la zona", "reponer el pulsador y reconocer en la pantalla"),
    ("Celdas de carga fuera de rango", "celda dañada o sobrecarga", "dosificación volumétrica (velocidad fija de los sinfines)", "revisar SIWAREX y celdas"),
]

LAZOS = [
    {"tag": "FIC-101", "variable": "caudal de guano al secador (kg/h)", "medicion": "pérdida de peso de la TP-01 (WT-101 a 104)",
     "actuador": "velocidad de los sinfines M85 a M88 (variadores)", "consigna": "1.260 kg/h en régimen (la ajusta MIC-01)", "controlador": "PLC-01"},
    {"tag": "LIC-101", "variable": "nivel de la TP-01", "medicion": "radar LT-101", "actuador": "permiso de vaciado de los galpones",
     "consigna": "entre 20 y 80 %", "controlador": "PLC-01 (lógica de turnos)"},
    {"tag": "TIC-01", "variable": "temperatura del aire de secado", "medicion": "Pt100 de la Rev. F", "actuador": "cáscara (M12) y aire de combustión (M4)",
     "consigna": "100 a 135 °C", "controlador": "PLC-02 (Rev. F)"},
    {"tag": "MIC-01", "variable": "humedad del producto", "medicion": "transmisor de la Rev. F", "actuador": "consigna de TIC-01 y de FIC-101",
     "consigna": "15 %", "controlador": "PLC-02 → PLC-01"},
    {"tag": "SIC-CE/CP", "variable": "velocidad de colectoras y principales", "medicion": "variador", "actuador": "variador G120",
     "consigna": "100 % en vaciado", "controlador": "PLC-01"},
]


def main():
    mot3d, ins3d, tab3d, polis, sin_tag = escanear_modelo()
    red_planta = Red([p for p in polis if p[3] == "planta"])
    dist_gu = red_planta.distancias(next(p for n, _, p, _ in polis if n.startswith("Troncal"))[0])
    redes_g, dist_ccm = {}, {}
    for g in D["galpones"]:
        gid = g["id"]
        pg = [p for p in polis if p[3] == gid]
        rg = Red(pg)
        top = next(p for n, _, p, _ in pg if n.startswith("Bandeja de la cabecera"))[0]
        rg.unir(top, (top[0], top[1], 0.20), 1.0)                 # dentro del CCM: salida de arriba y de abajo
        redes_g[gid] = rg
        dist_ccm[gid] = rg.distancias(top)
    # 1.ª pasada con caídas aguas arriba supuestas, para el balance; 2.ª con las calculadas
    mot0 = motores_lista(mot3d, red_planta, dist_gu, redes_g, dist_ccm, 1.5, {g["id"]: DU_GALPON_MAX for g in D["galpones"]})
    bal = balance(mot0, sin_tag, mot3d)
    alim, imp, ccm = alimentadores(polis, bal, tab3d)
    mot = motores_lista(mot3d, red_planta, dist_gu, redes_g, dist_ccm, imp["TS-GU"][2], {g: v[2] for g, v in ccm.items()})
    for m in mot:
        if m.get("estado") != "nuevo":
            continue
        r_up, x_up = imp["TS-GU"][:2] if m["tablero"] == "TS-GU" else ccm[m["tablero"][4:]][:2]
        m["Icc_min_fin_A"] = round(icc_min_fin(r_up, x_up, m["L_m"], m["S_mm2"]))
        rango = re.search(r"guardamotor ([\d.]+)–([\d.]+) A", m["proteccion"])
        if rango:
            m["disparo_magnetico_A"] = round(13 * float(rango.group(2)), 1)
            m["verifica_Icc_min"] = m["Icc_min_fin_A"] > m["disparo_magnetico_A"]
        m["verifica_dU"] = m["dU_total_pct"] <= LIM_DU["motor"]
    ins = instrumentos_lista(ins3d, polis, red_planta, redes_g)
    io = io_resumen(ins, mot)
    rf, xf = z_fuente()
    nuevos = [m for m in mot if m.get("estado") == "nuevo"]
    peor = max(nuevos, key=lambda m: m["dU_total_pct"])
    out = {
        "criterio": {"norma": "AEA 90364-7-771 (Iz de la IEC 60364-5-52), IEC 60909 para cortocircuito, ECT TT como en la Rev. F",
                     "lim_dU_pct": LIM_DU, "U_V": U, "reserva_largo": RESERVA, "terminales_m": TERMINAL,
                     "factor_tramo_final": F_CANO, "dU_TGBT_a_CCM_max_pct": DU_GALPON_MAX,
                     "fuente": {"S_red_MVA": S_RED_MVA, "S_tr_kVA": S_TR_KVA, "ucc": UCC, "Pcu_kW": PCU_KW, "tipo": "P"}},
        "balance": bal,
        "cortocircuito": {"TGBT_kA": round(icc3(rf, xf), 2), "TGF_kA": round(icc3(*imp["TGF"][:2]), 2),
                          "TG2_kA": round(icc3(*imp["TG2"][:2]), 2), "TS-GU_kA": round(icc3(*imp["TS-GU"][:2]), 2),
                          "CCM_kA": {g: round(icc3(*v[:2]), 2) for g, v in ccm.items()},
                          "poder_de_corte": poder_de_corte(icc3(rf, xf), {k: icc3(*v[:2]) for k, v in imp.items()},
                                                           {g: icc3(*v[:2]) for g, v in ccm.items()})},
        "TG2_circuitos": tg2_circuitos(imp["TG2"][2]),
        "alimentadores": alim,
        "tableros": {
            "TGBT": {"ubicacion": "subestación, afuera del cerco (preliminar)", "origen": "P",
                     "salidas": ["QF0 TBI (bombas de incendio, antes del interruptor general)", "QF1 TGF", "QF2 TG2",
                                 "QF3 a QF6 TS-G1 a TS-G4", "QF7 y QF8 depósitos DH-O y DH-E", "QF9 servicios"]},
            "TGF": {"origen": "R", "cambios": ["se quita M15 (vibrador de la tolva vieja)", "se alimenta del TGBT (QF1) en vez del pilar viejo"]},
            "TG2": {"origen": "R (modificado)",
                    "cambios": ["Q22 (TS-LAV) queda de reserva", "Q23 (TS-BIO de 22,85 kW) pasa a alimentar al TS-GU",
                                "Q24 (variador de M23) sigue: el extractor ahora aspira la TP-01",
                                "Q25: se sacan los 4 proyectores Ex de la zona de biogás",
                                "se alimenta del TGBT (QF2) en vez del pilar viejo"]},
            "TS-GU": {"ubicacion": "sala de control, muro Este (junto al TG2 y al TGF de la Rev. F)", "origen": "P",
                      "alimentado_desde": "TG2 · Q23 (salida que era del TS-BIO)",
                      "contenido": ["interruptor general 4P con bloqueo y diferencial tipo B 300 mA para los variadores",
                                    "8 variadores SINAMICS G120 (PM240-2 + CU240E-2 PN-F) para CE-O, CE-E, CP-O, CP-E y los 4 sinfines",
                                    "2 inversores de marcha para los actuadores de las desviadoras DV-O y DV-E",
                                    "PLC-01 S7-1500F (CPU 1515F-2 PN); el SIWAREX WP231 va en el RIO-TP",
                                    "fuente SITOP 24 V 20 A con módulo de respaldo y UPS de 1 kVA (PLC, pantallas y red)",
                                    "switch SCALANCE XC208 con puertos de fibra para los dos anillos MRP",
                                    "circuitos de alumbrado de galerías y torres y tomacorrientes con diferencial de 30 mA",
                                    "panel de operador TP1200 Comfort en la puerta"]},
            "RIO": [{"id": "RIO-TP", "ubicacion": "al Este de la TP-01, bajo la bandeja de la CP-E", "pantalla": "KTP700"},
                    {"id": "RIO-O", "ubicacion": "plataforma de la TT-O, esquina Sudeste", "pantalla": "KTP400"},
                    {"id": "RIO-E", "ubicacion": "plataforma de la TT-E, esquina Sudoeste", "pantalla": "KTP400"}],
            "CCM": [{"id": f"CCM-{g['id']}", "ubicacion": f"afuera del muro del lado de la planta del {g['id']}, cabecera Sur, con alero",
                     "contenido": "interruptor general bloqueable, 20 guardamotores + contactores de las cintas de piso, "
                                  "guardamotor + contactor de la CT, variador G120C de la CI, RIO ET 200SP con F-DI, "
                                  "switch de fibra, fuente de 24 V y panel KTP400"} for g in D["galpones"]]},
        "motores": mot,
        "puesta_a_tierra": {
            "esquema": "TT (como en la Rev. F): neutro a tierra en la subestación y masas de cada sector a su propia puesta a tierra",
            "objetivo": "RA ≤ 10 Ω en cada jabalina (con diferencial de 300 mA alcanzaría RA ≤ 83 Ω para 25 V en locales con animales; "
                        "se piden 10 Ω por el pararrayos)",
            "elementos": ["anillo y jabalinas de la nave (D16 de la Rev. F)",
                          "jabalina y cámara en cada torre, unida a la barra equipotencial de la plataforma",
                          "puntas captoras Franklin en el techo de cada torre con bajada de Cu desnudo de 50 mm² (IRAM 2184)",
                          "galerías unidas a la tierra de la torre y de la nave en cada extremo y en cada caballete con Cu de 16 mm²",
                          "jabalina y cámara en cada CCM de galpón, unida a la tierra del galpón",
                          "bandejas con conductor de protección continuo de 16 mm²"],
            "diferenciales": "tipo B 300 mA en los circuitos con variador; tipo A 30 mA en tomacorrientes y alumbrado de galerías"},
        "instrumentos": ins,
        "io": io,
        "automatizacion": {
            "arquitectura": ["PLC-01 S7-1500F (CPU 1515F-2 PN) en el TS-GU: transporte, recepción, dosificación y enclavamientos de seguridad por PROFIsafe",
                             "PLC-02 S7-1200 (CPU 1214C) del SC-4 de la Rev. F: sigue controlando el secador y se acopla al PLC-01 como I-device",
                             "periferias ET 200SP con módulos F-DI: RIO-TP (recepción), RIO-O y RIO-E (torres) y RIO-G1 a RIO-G4 (CCM de los galpones)",
                             "red PROFINET por fibra óptica multimodo en dos anillos MRP (Oeste: TS-GU, RIO-TP, RIO-O, RIO-G2, RIO-G1; Este: TS-GU, RIO-TP, RIO-E, RIO-G3, RIO-G4); la vuelta de cada anillo va por un cable separado",
                             "switches SCALANCE XC208 en el TS-GU, las torres y los CCM",
                             "pantallas: TP1200 Comfort en el TS-GU (sala de control), KTP700 en el RIO-TP, KTP400 en cada torre y en cada CCM, más el KTP700 del SC-4 (Rev. F)",
                             "supervisión WinCC con alarmas, tendencias e informes; acceso remoto por router VPN SCALANCE M",
                             "variadores SINAMICS con PROFINET y STO por PROFIsafe; pesaje SIWAREX WP231 de las 4 celdas de la TP-01"],
            "lazos": LAZOS, "secuencia": SECUENCIA,
            "enclavamientos": [{"condicion": a, "efecto": b, "senal": c} for a, b, c in ENCLAVAMIENTOS],
            "fallas": [{"falla": a, "causa": b, "accion_automatica": c, "accion_del_operador": d} for a, b, c, d in FALLAS]},
        "resumen": {"motores_nuevos": len(nuevos), "kW_nuevos": round(sum(m["kW"] for m in nuevos), 2),
                    "motores_quitados": [m["tag"] for m in mot if str(m["estado"]).startswith("se quita")],
                    "instrumentos_nuevos": sum(i["cantidad"] for i in ins if i["alcance"] == "planta / transporte"),
                    "peor_caida_total": {"tag": peor["tag"], "dU_total_pct": peor["dU_total_pct"], "L_m": peor["L_m"], "S_mm2": peor["S_mm2"]},
                    "todos_verifican_dU": all(m["verifica_dU"] for m in nuevos),
                    "todos_verifican_Icc_min": all(m.get("verifica_Icc_min", True) for m in nuevos),
                    "alimentadores_verifican": all(a["verifica"] for a in alim),
                    "motores_sin_ubicacion_3d": [m["tag"] for m in nuevos if not m["pos"]]}}
    SALIDA.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    r = out["resumen"]
    print(f"motores nuevos {r['motores_nuevos']} ({r['kW_nuevos']} kW); quitados {r['motores_quitados']}")
    print(f"balance: {bal['kW_instalados']} kW instalados, {bal['kW_demanda']} kW de demanda, {bal['kVA_demanda']} kVA "
          f"({bal['carga_transformador_pct']} % del transformador de {S_TR_KVA:.0f} kVA)")
    for a in alim:
        print(f"  {a['circuito']}: Ib {a['Ib_A']} A, In {a['In_A']} A, {a['S_mm2']} mm² ({a['metodo']}), {a['L_m']} m, "
              f"ΔU {a['dU_pct']} % (total {a['dU_total_pct']} %), Icc {a['Icc3_fin_kA']} kA, {'OK' if a['verifica'] else 'NO VERIFICA'}")
    cc = out["cortocircuito"]
    print(f"Icc: TGBT {cc['TGBT_kA']} kA, TGF {cc['TGF_kA']}, TG2 {cc['TG2_kA']}, TS-GU {cc['TS-GU_kA']}, CCM {cc['CCM_kA']}")
    print(f"peor caída total: {r['peor_caida_total']}; ΔU ok {r['todos_verifican_dU']}; Icc mín ok {r['todos_verifican_Icc_min']}; "
          f"alimentadores ok {r['alimentadores_verifican']}; sin ubicación {r['motores_sin_ubicacion_3d']}")
    print(f"instrumentos nuevos: {r['instrumentos_nuevos']}")
    for k, v in io.items():
        print(f"  {k}: {v['señales']} → módulos {v['modulos_ET200SP_con_20pct_reserva']}")


if __name__ == "__main__":
    main()
