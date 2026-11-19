"""Transporte automático de guano (Fases 4 y 5).

Cintas transversales en canal (CT), inclinadas con bordes y tramo de carga horizontal (CI, en L), colectoras (CE) y
principales (CP) con sus galerías y caballetes; torres de transferencia TT-O y TT-E con compuerta desviadora tipo
pantalón y boca de emergencia a contenedor roll-off; tolva pulmón TP-01 con fondo vivo de 4 sinfines, celdas de carga y
pórtico de cabezales PC-01.

Todo sale de datos/granja.json y datos/calculos.json. Medidas en mm (los datos están en m).
Marco local de cada tramo de cinta: s a lo largo de la banda (de la cola a la cabeza), t lateral (a la izquierda
mirando a la cabeza) y n normal a la banda (hacia arriba). La cara superior del ramal de carga está en n = 0.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
import numpy as np

import componentes as C
from cad import T, Rx, Ry, Rz, alinear, caja0, proto, wp

RAIZ = Path(__file__).resolve().parents[2]
D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
K = json.loads((RAIZ / "datos" / "calculos.json").read_text(encoding="utf-8"))
TR = {t["id"]: t for t in D["transporte"]}
CALC = {t["id"]: t for t in K["transportadores"]}
NAVE = D["planta"]["nave"]
CINTA3 = D["planta"]["cinta"]
GRUPO = "Transporte de guano"
FLUJO = "Flujo de guano"
ESP = 8.0                      # espesor de banda


def mm(p):
    return np.asarray(p, float) * 1000.0


def tag_motor(cid):
    for m in K["motores_nuevos"]:
        if m["nom"].endswith(" " + cid):
            return m["tag"]
    g = TR[cid].get("galpon")
    pref = {"CT": "Cinta transversal ", "CI": "Cinta inclinada "}.get(cid[:2])
    for m in K["motores_nuevos"]:
        if g and pref and m["nom"] == pref + g:
            return m["tag"]
    return ""


def d_cab(B):
    return 400 if B >= 600 else 320


def d_cola(B):
    return 320 if B >= 600 else 250


class Marco:
    """Marco local (s, t, n) de un tramo recto de cinta (n siempre con componente hacia arriba)."""

    def __init__(self, p0, p1):
        self.p0, self.p1 = mm(p0), mm(p1)
        d = self.p1 - self.p0
        self.L = float(np.linalg.norm(d))
        self.u = d / self.L
        uh = np.array([d[0], d[1], 0.0])
        self.uh = uh / np.linalg.norm(uh)
        self.v = np.array([-self.uh[1], self.uh[0], 0.0])
        self.w = np.cross(self.u, self.v)
        R = np.eye(4)
        R[:3, 0], R[:3, 1], R[:3, 2], R[:3, 3] = self.u, self.v, self.w, self.p0
        self.M = R
        self.ang = math.degrees(math.asin(max(-1.0, min(1.0, self.u[2]))))

    def p(self, s, t=0.0, n=0.0):
        return self.p0 + self.u * s + self.v * t + self.w * n

    def at(self, s, t=0.0, n=0.0):
        return self.M @ T(s, t, n)

    def s_de_x(self, x):
        """s del punto de la banda que está en la abscisa x (tramos paralelos al eje x en planta)."""
        return float((x - self.p0[0]) / self.u[0])


# ===================================================================================== chutes de transferencia
def _rect_w(x0, x1, y0, y1, z):
    return cq.Wire.makePolygon([cq.Vector(x0, y0, z), cq.Vector(x1, y0, z), cq.Vector(x1, y1, z), cq.Vector(x0, y1, z)],
                               close=True)


def _chute0(tdx, tdy, h_recta, bdx, bdy, ox, oy, h_tolva, t):
    """Chute abierto abajo: caja recta (planta tdx × tdy, z de 0 a h_recta) y transición de alto h_tolva hasta la boca
    bdx × bdy corrida (ox, oy). Origen: centro de la caja recta en su base."""
    recta = cq.Workplane("XY").box(tdx, tdy, h_recta, centered=(True, True, False)).faces("<Z").shell(-t)
    if h_tolva < 30:
        return recta
    sol = cq.Solid.makeLoft([_rect_w(ox - bdx / 2, ox + bdx / 2, oy - bdy / 2, oy + bdy / 2, -h_tolva),
                             _rect_w(-tdx / 2, tdx / 2, -tdy / 2, tdy / 2, 0)], True)
    try:
        tol = cq.Workplane("XY").add(sol).faces(">Z or <Z").shell(-t)
        if not tol.val().isValid():
            raise ValueError("vaciado inválido")
    except Exception:            # si el vaciado falla queda la transición maciza (solo cambia el interior)
        tol = cq.Workplane("XY").add(sol)
    return [recta, tol]


def chute(e, c_top, top, z_top, z_mid, c_bot, bot, z_bot, tag, nom, t=5.0, mat="galv"):
    """Chute en coordenadas absolutas (mm): caja recta con planta `top` (dx, dy) centrada en c_top entre z_mid y z_top,
    y transición hasta la boca `bot` (dx, dy) centrada en c_bot, en z_bot."""
    ox, oy = c_bot[0] - c_top[0], c_bot[1] - c_top[1]
    h_r, h_t = z_top - z_mid, z_mid - z_bot
    clave = ("chute",) + tuple(int(round(v)) for v in (top[0], top[1], h_r, bot[0], bot[1], ox, oy, h_t, t))
    k = proto(clave, lambda: _chute0(top[0], top[1], h_r, bot[0], bot[1], ox, oy, h_t, t))
    e.add(k, mat, T(c_top[0], c_top[1], z_mid), tag, nom)


# ===================================================================================== cinta genérica
def cinta(e, cid, lado_motor=1, capota=True, capota_hasta=None, guano=True, bordes=False, cargas=(), chute_a=None,
          sensores=True):
    """Cinta completa. `cargas`: s de los puntos de carga del primer tramo (faldones y rodillos de impacto).
    `chute_a`: (x, y, z, dx, dy) en mm de la boca inferior del chute de cabeza. Devuelve la lista de tramos."""
    t = TR[cid]
    c = CALC[cid]
    B = t["ancho"] * 1000
    Dh, Dt = d_cab(B), d_cola(B)
    pts = t.get("trazado", [t["p0"], t["p1"]])
    tramos = [Marco(a, b) for a, b in zip(pts, pts[1:])]
    m0, mf = tramos[0], tramos[-1]
    e.en(GRUPO)
    nombre = {"transversal": "cinta transversal", "inclinada": "cinta inclinada", "colectora": "cinta colectora",
              "principal": "cinta principal"}[t["tipo"]]
    n_larg = -Dh / 2 - 170
    t_borde = B / 2 - 45                       # bordes ondulados: 40 mm de borde libre para las ruedas de retención
    for k_tr, m in enumerate(tramos):
        L = m.L
        primero, ultimo = k_tr == 0, k_tr == len(tramos) - 1
        s_a = 0.0 if primero else -60.0
        s_b = L if ultimo else L + 60.0
        # ------------------------------------------------------------- banda (ramal de carga y de retorno)
        if bordes:
            e.caja(s_a, -B / 2, -ESP, s_b, B / 2, 0, "banda", M=m.M, cod=cid,
                   nom=f"Banda EP 400/3 de {B:.0f} mm con bordes ondulados ({nombre} {cid})")
            for sg in (-1, 1):
                e.caja(s_a, sg * t_borde - 5, 0, s_b, sg * t_borde + 5, 80, "banda", M=m.M, cod=cid,
                       nom="Borde ondulado de 80 mm")
            k_taco = proto(("taco", B), lambda: caja0(12, 2 * t_borde - 20, 70).translate((-6, -(t_borde - 10), 0)))
            for s in np.arange(150 if primero else 100, L - 80, 250):
                e.add(k_taco, "banda", m.at(s, 0, 0), cid, "")
        else:
            l3 = B / 3
            e.caja(s_a, -l3 / 2, -ESP, s_b, l3 / 2, 0, "banda", M=m.M, cod=cid,
                   nom=f"Banda EP 400/3 de {B:.0f} mm en artesa de 20° ({nombre} {cid})")
            for sg in (-1, 1):
                G = m.M @ T(0, sg * l3 / 2, 0) @ Rx(sg * 20) @ T(0, 0 if sg > 0 else -l3, 0)
                e.caja(s_a, 0, -ESP, s_b, l3, 0, "banda", M=G, cod=cid, nom="")
        n_ret_a = -(Dt if primero else Dh) - ESP / 2
        Gr = m.M @ alinear((s_a, 0, n_ret_a), (s_b, 0, -Dh - ESP / 2), up=(0, 0, 1))
        e.caja(-ESP / 2, -B / 2, 0, ESP / 2, B / 2, s_b - s_a, "banda", M=Gr, cod=cid, nom="Ramal de retorno")
        if guano:
            e.en(FLUJO)
            s_ini = (min(cargas) - 250) if (primero and cargas) else (250 if primero else 0)
            hg = 55 if bordes else 45
            e.caja(s_ini, -B / 4, 0, L - (150 if ultimo else 0), B / 4, hg, "guano", M=m.M, cod=cid,
                   nom=f"Guano fresco sobre la {cid}")
            e.en(GRUPO)
        # ------------------------------------------------------------- largueros, rodillos de carga y de retorno
        for sg in (-1, 1):
            y = sg * (B / 2 + 170)
            e.barra(m.p(-350 if primero else -30, y, n_larg), m.p(L + 150 if ultimo else L + 30, y, n_larg), "UPN 120",
                    "estructura", up=tuple(-sg * m.v), cod=cid, nom="Larguero UPN 120")
        paso = 1000 if bordes else 1200
        cargas_tr = cargas if primero else ()
        for s in np.arange(700, L - 500, paso):
            if any(abs(s - sc) < 1000 for sc in cargas_tr):
                continue
            if bordes:
                C.rodillo_retorno(e, B - 50, m.at(s, 0, -ESP), tag=cid)
            else:
                C.terna(e, B, m.at(s, 0, 0), tag=cid)
            e.barra(m.p(s, -(B / 2 + 170), n_larg - 60), m.p(s, B / 2 + 170, n_larg - 60), "L 63", "estructura",
                    up=tuple(m.w), cod=cid, nom="Travesaño L 63")
        for s in np.arange(1500, L - 700, 3000):
            C.rodillo_retorno(e, B + 190, m.at(s, 0, -Dh - ESP), tag=cid)
        # ------------------------------------------------------------- carga: rodillos de impacto y faldones
        for sc in cargas_tr:
            for k in range(4):
                s = sc - 450 + 300 * k
                if bordes:
                    C.rodillo_retorno(e, B - 50, m.at(s, 0, -ESP), tag=cid)
                else:
                    C.terna(e, B, m.at(s, 0, 0), tag=cid)
            if not bordes:
                n_s = (B / 2 - 70 - B / 6) * math.tan(math.radians(20))
                for sg in (-1, 1):
                    e.caja(sc - 900, sg * (B / 2 - 60) - 4, n_s + 20, sc + 900, sg * (B / 2 - 60) + 4, n_s + 420,
                           "acero_pintado", M=m.M, cod=cid, nom="Faldón de chapa 4 mm")
                    e.caja(sc - 900, sg * (B / 2 - 70) - 6, n_s, sc + 900, sg * (B / 2 - 70) + 6, n_s + 60, "goma", M=m.M,
                           cod=cid, nom="Goma de sello del faldón 12 mm")
                e.caja(sc - 904, -(B / 2 - 56), n_s + 20, sc - 900, B / 2 - 56, n_s + 420, "acero_pintado", M=m.M,
                       cod=cid, nom="Cierre trasero del faldón")
        # ------------------------------------------------------------- capota (al aire libre, sin tapar las cargas)
        if capota and (k_tr > 0 or len(tramos) == 1):
            R = B / 2 + 140 if not bordes else B / 2 + 90
            fin = (L - 500 if ultimo else L)
            if capota_hasta is not None:
                fin = min(fin, capota_hasta)
            tramos_cap = [(400.0 if primero else 0.0, fin)]
            for sc in cargas_tr:
                nuevo = []
                for a, b in tramos_cap:
                    if sc + 1000 <= a or sc - 1000 >= b:
                        nuevo.append((a, b))
                    else:
                        nuevo += [(a, sc - 1000), (sc + 1000, b)]
                tramos_cap = nuevo
            for a, b in tramos_cap:
                lc = b - a
                if lc < 600:
                    continue
                k_cap = proto(("capota", round(R), round(lc)),
                              lambda R=R, lc=lc: wp().moveTo(R, 0).threePointArc((0, R), (-R, 0)).lineTo(-R + 2, 0)
                              .threePointArc((0, R - 2), (R - 2, 0)).close().extrude(lc))
                h0 = 40 if not bordes else 100
                e.add(k_cap, "galv", m.M @ T(a, 0, h0) @ Ry(90) @ Rz(90), cid, "Capota semicircular de chapa galvanizada")
                for s in np.arange(a + 100, b, 1200):
                    e.caja(s - 15, -R - 10, h0 - 15, s + 15, R + 10, h0 + 5, "galv", M=m.M, cod=cid,
                           nom="Abrazadera de la capota")
    # ----------------------------------------------------------------- quiebre en L: ruedas de retención de los bordes
    for mb in tramos[1:]:
        for sg in (-1, 1):
            e.cil(mb.p(0, sg * (B / 2 - 35), 150), mb.p(0, sg * (B / 2 + 5), 150), 150, "acero_pintado", cod=cid,
                  nom="Rueda de retención de los bordes Ø300 (curva cóncava)")
            e.barra(mb.p(0, sg * (B / 2 + 170), n_larg), mb.p(0, sg * (B / 2 + 25), 150), "FB 50x6",
                    "estructura", cod=cid, nom="Brazo de la rueda de retención")
    # ----------------------------------------------------------------- tambores, rodamientos, tensor y accionamiento
    L = mf.L
    d_eje = 60 if B >= 600 else 50
    L_eje = B + 520
    C.tambor(e, Dh, B + 100, L_eje, d_eje, mf.at(L, 0, -Dh / 2), cid, goma=True)
    C.tambor(e, Dt, B + 100, L_eje - 120, d_eje - 10, m0.at(0, 0, -Dt / 2), cid)
    for sg in (-1, 1):
        C.chumacera_ucp(e, d_eje, mf.at(L, sg * (B / 2 + 160), -Dh / 2), cid)
        y = sg * (B / 2 + 140)
        for dz in (-75, 75):
            e.caja(-330, y - 30, -Dt / 2 + dz - 8, 170, y + 30, -Dt / 2 + dz + 8, "estructura", M=m0.M, cod=cid,
                   nom="Guía del tensor")
        e.caja(-60, y - 32, -Dt / 2 - 62, 60, y + 32, -Dt / 2 + 62, "gris_motor", M=m0.M, cod=cid,
               nom="Rodamiento tensor UCT")
        e.barra(m0.p(-560, y, -Dt / 2), m0.p(-60, y, -Dt / 2), "RB 20", "galv", cod=cid,
                nom="Tornillo tensor M20 (carrera 300 mm)")
        e.caja(-350, y - 45, -Dt / 2 - 95, -330, y + 45, -Dt / 2 + 95, "estructura", M=m0.M, cod=cid,
               nom="Placa de reacción del tensor")
    kw = c["motor_kW"]
    tg = tag_motor(cid)
    b_red = 190 * (max(kw, 0.37) / 1.1) ** (1 / 3)
    C.motorreductor_ortogonal(e, kw, mf.at(L, lado_motor * (B / 2 + 205 + b_red / 2), -Dh / 2) @ Rz(180), tg,
                              d_salida=d_eje)
    e.cil(mf.p(L, -lado_motor * (L_eje / 2 - 60), -Dh / 2), mf.p(L, -lado_motor * (L_eje / 2 + 25), -Dh / 2),
          d_eje / 2 + 30, "amarillo", cod=cid, nom="Tapa protectora del extremo de eje")
    C.placa(e, mf.p(L - 300, lado_motor * (B / 2 + 232), n_larg), tuple(lado_motor * mf.v), 220, 110, tag=cid,
            nom=f"Placa {cid}: {nombre}, {kw} kW, {c['v_m_s']} m/s, {c['Q_diseno_t_h']} t/h")
    # ----------------------------------------------------------------- rascadores y arado
    e.barra(mf.p(L + Dh * 0.12, -B / 2 - 60, -Dh * 0.95), mf.p(L + Dh * 0.12, B / 2 + 60, -Dh * 0.95), "CHS 60",
            "acero_pintado", cod=cid, nom="Rascador primario de poliuretano")
    e.caja(L + Dh * 0.10, -B / 2 + 20, -Dh * 0.80, L + Dh * 0.28, B / 2 - 20, -Dh * 0.62, "naranja", M=mf.M, cod=cid,
           nom="Hoja de poliuretano del rascador primario")
    e.barra(mf.p(L - 260, -B / 2 - 60, -Dh - 70), mf.p(L - 260, B / 2 + 60, -Dh - 70), "CHS 48", "acero_pintado",
            cod=cid, nom="Rascador secundario de láminas")
    k_v = proto(("arado", B), lambda: wp().polyline([(0, 0), (B * 0.45, -B * 0.42), (B * 0.45, B * 0.42)]).close().extrude(80))
    e.add(k_v, "naranja", m0.at(450, 0, -Dt - ESP - 80), cid, "Rascador en V del ramal de retorno")
    # ----------------------------------------------------------------- chute de cabeza con puerta de inspección
    if chute_a is not None:
        xb, yb, zb, bdx, bdy = chute_a
        c0 = mf.p(L, 0, 0)
        a, b = -(Dh / 2 + 150), Dh / 2 + 350
        ca = c0[:2] + mf.uh[:2] * (a + b) / 2
        ext_u, ext_v = b - a, B + 260
        en_x = abs(mf.uh[0]) > 0.5
        tdx, tdy = (ext_u, ext_v) if en_x else (ext_v, ext_u)
        z_top = c0[2] + 0.7 * Dh
        z_mid = max(zb + 150, c0[2] - Dh - 150)
        chute(e, ca, (tdx, tdy), z_top, z_mid, (xb, yb), (bdx, bdy), zb, cid, f"Chute de cabeza de la {cid}")
        fr = np.array([ca[0], ca[1]]) + mf.uh[:2] * (ext_u / 2 + 6)
        zc = (z_mid + z_top) / 2
        e.caja_rot((fr[0], fr[1], zc), (12 if en_x else 380, 380 if en_x else 12, min(300, z_top - z_mid - 60)), 0,
                   "amarillo", cid, "Puerta de inspección abisagrada del chute")
        if sensores:
            C.sensor(e, "atasco", (fr[0] + mf.uh[0] * 8, fr[1] + mf.uh[1] * 8, z_top - 90), (mf.uh[0], mf.uh[1], 0),
                     tag=f"LSH-{cid}")
    # ----------------------------------------------------------------- instrumentos de la cinta
    if sensores:
        C.sensor(e, "velocidad", m0.p(-60, -(B / 2 + 210), -Dt / 2 + 60), tuple(-m0.v), tag=f"SSL-{cid}")
        for m in tramos:
            if m.L < 2500:
                continue
            for s in ([700, m.L - 900] if m.L < 25000 else [700, m.L / 2, m.L - 900]):
                for sg in (-1, 1):
                    C.sensor(e, "desvio", m.p(s, sg * (B / 2 + 230), n_larg + 70), tuple(m.w), tag=f"ZS-{cid}")
        C.sensor(e, "baliza", mf.p(L - 350, lado_motor * (B / 2 + 260), n_larg + 300), tuple(mf.w), tag=f"XA-{cid}")
    return tramos


# ===================================================================================== soportes simples
def patas(e, m, s_lista, B, cid, z_suelo=0.0, z_min=600.0, riostras=True):
    """Pórticos de caño cuadrado desde los largueros hasta el piso, con cruces y riostras longitudinales."""
    n_larg = -d_cab(B) / 2 - 170
    previos = None
    for s in s_lista:
        a = m.p(s, -(B / 2 + 170), n_larg - 70)
        b = m.p(s, B / 2 + 170, n_larg - 70)
        if min(a[2], b[2]) - z_suelo < z_min:
            continue
        for p in (a, b):
            C.columna(e, p[0], p[1], z_suelo, p[2], "RHS 100", tag=f"SOP-{cid}", placa=(240, 240, 12), d_anclaje=12)
        e.barra(a, b, "UPN 100", "estructura", up=(0, 0, 1), cod=f"SOP-{cid}", nom="Travesaño de apoyo UPN 100")
        if a[2] - z_suelo > 1500:
            e.barra((a[0], a[1], z_suelo + 300), (b[0], b[1], a[2] - 300), "L 50", "estructura", cod=f"SOP-{cid}",
                    nom="Cruz de San Andrés L 50")
            e.barra((b[0], b[1], z_suelo + 300), (a[0], a[1], a[2] - 300), "L 50", "estructura", cod=f"SOP-{cid}",
                    nom="Cruz de San Andrés L 50")
        if riostras and previos is not None:
            for p_prev, p in zip(previos, (a, b)):
                e.barra((p_prev[0], p_prev[1], z_suelo + 300), (p[0], p[1], min(p[2], p_prev[2] + 3000) - 200), "L 50",
                        "estructura", cod=f"SOP-{cid}", nom="Riostra longitudinal L 50")
        previos = (a, b)


# ===================================================================================== galería elevada
def apoyos_galeria(s0, s1, prohibidos, vano=11000.0):
    """Posiciones de los caballetes: desde s0, con vanos ≤ `vano`, fuera de los intervalos prohibidos."""
    def libre(s):
        return all(not (a <= s <= b) for a, b in prohibidos)
    res = [s0] if libre(s0) else []
    s = s0
    while s1 - s > vano:
        cand = s + vano
        while cand > s + 2500 and not libre(cand):
            cand -= 100
        res.append(cand)
        s = cand
    return res


def galeria(e, m, s0, s1, B, cid, apoyos, lado_pasarela=1, aberturas=(), escalera_cola=False, z_suelo=0.0):
    """Galería reticulada de 1,65 m de alto con pasarela de 0,8 m del lado `lado_pasarela`, caballetes en `apoyos` (s) y
    aberturas (s_a, s_b) en el reticulado del otro lado para la entrada de las cintas inclinadas."""
    Dh = d_cab(B)
    t_int = -lado_pasarela * (B / 2 + 380)
    t_ext = lado_pasarela * (B / 2 + 1250)
    n_inf = -Dh / 2 - 650
    n_sup = n_inf + 1650
    n_pas = n_inf + 120
    tag = f"GAL-{cid}"

    def en_abertura(s, margen=50):
        return any(a - margen <= s <= b + margen for a, b in aberturas)
    # cordones
    for t_ in (t_int, t_ext):
        e.barra(m.p(s0, t_, n_inf), m.p(s1, t_, n_inf), "L 80", "estructura", up=tuple(m.w), cod=tag, nom="Cordón inferior L 80")
    a_prev = s0
    for a, b in sorted(aberturas) + [(s1, s1)]:
        if a - a_prev > 100:
            e.barra(m.p(a_prev, t_int, n_sup), m.p(a, t_int, n_sup), "L 80", "estructura", up=tuple(-m.w), cod=tag,
                    nom="Cordón superior L 80")
        a_prev = b
    e.barra(m.p(s0, t_ext, n_sup), m.p(s1, t_ext, n_sup), "L 80", "estructura", up=tuple(-m.w), cod=tag,
            nom="Cordón superior L 80")
    paso = 1500.0
    n = max(2, int(round((s1 - s0) / paso)))
    paso = (s1 - s0) / n
    for i in range(n + 1):
        s = s0 + i * paso
        for t_ in (t_int, t_ext):
            if t_ == t_int and en_abertura(s):
                continue
            e.barra(m.p(s, t_, n_inf), m.p(s, t_, n_sup), "L 50", "estructura", up=tuple(m.u), cod=tag, nom="Montante L 50")
        e.barra(m.p(s, t_int, n_inf), m.p(s, t_ext, n_inf), "L 63", "estructura", up=tuple(m.w), cod=tag, nom="Viga de piso L 63")
        if i < n:
            for t_ in (t_int, t_ext):
                if t_ == t_int and any(not (b + 50 < s or a - 50 > s + paso) for a, b in aberturas):
                    continue
                a_, b_ = (n_inf, n_sup) if i % 2 == 0 else (n_sup, n_inf)
                e.barra(m.p(s, t_, a_), m.p(s + paso, t_, b_), "L 50", "estructura", up=tuple(m.u), cod=tag, nom="Diagonal L 50")
            e.barra(m.p(s, t_int, n_inf), m.p(s + paso, t_ext, n_inf), "L 50", "estructura", up=tuple(m.w), cod=tag,
                    nom="Arriostramiento de piso")
    # pórticos de las aberturas: montantes más altos y dintel por encima de la cinta que entra
    for a, b in aberturas:
        for s in (a, b):
            e.barra(m.p(s, t_int, n_inf), m.p(s, t_int, n_sup + 700), "L 80", "estructura", up=tuple(m.u), cod=tag,
                    nom="Montante del pórtico de entrada L 80")
            e.barra(m.p(s, t_int, n_sup + 700), m.p(s, t_ext, n_sup), "L 50", "estructura", cod=tag, nom="Puntal del pórtico")
        e.barra(m.p(a, t_int, n_sup + 700), m.p(b, t_int, n_sup + 700), "UPN 100", "estructura", up=tuple(m.w), cod=tag,
                nom="Dintel del pórtico de entrada UPN 100")
    # pasarela de rejilla, baranda y rodapié del lado de afuera
    tp0, tp1 = sorted((lado_pasarela * (B / 2 + 400), lado_pasarela * (B / 2 + 1200)))
    e.caja(s0, tp0, n_pas, s1, tp1, n_pas + 30, "rejilla", M=m.M, cod=tag, nom="Pasarela de rejilla electrosoldada 0,8 m")
    e.barra(m.p(s0, t_ext, n_pas + 580), m.p(s1, t_ext, n_pas + 580), "CHS 33", "amarillo", cod=tag, nom="Travesaño de baranda")
    e.barra(m.p(s0, t_ext, n_pas + 1100), m.p(s1, t_ext, n_pas + 1100), "CHS 42", "amarillo", cod=tag, nom="Pasamanos")
    e.caja(s0, t_ext - lado_pasarela * 10 - 3, n_pas, s1, t_ext - lado_pasarela * 10 + 3, n_pas + 150, "amarillo",
           M=m.M, cod=tag, nom="Rodapié")
    # cable de parada de emergencia a lo largo de la pasarela, con sus interruptores
    tc = t_ext - lado_pasarela * 60
    e.cil(m.p(s0 + 300, tc, n_pas + 1000), m.p(s1 - 300, tc, n_pas + 1000), 3, "rojo", cod=tag,
          nom="Cable de parada de emergencia")
    for s in list(np.arange(s0 + 400, s1 - 1000, 25000)) + [s1 - 400]:
        C.sensor(e, "tiron", m.p(s, tc, n_pas + 700), tuple(-lado_pasarela * m.v), tag=f"HS-{cid}")
    # bandeja portacables por fuera
    tb = t_ext + lado_pasarela * 220
    C.bandeja(e, m.p(s0, tb, n_inf + 300), m.p(s1, tb, n_inf + 300), 200, tag=f"BC-{cid}")
    C.cables_en_bandeja(e, m.p(s0, tb, n_inf + 300), m.p(s1, tb, n_inf + 300), 3, 200, tag=f"BC-{cid}")
    # luminarias estancas cada 6 m sobre la pasarela
    rz = math.degrees(math.atan2(m.u[1], m.u[0]))
    for s in np.arange(s0 + 1500, s1, 6000):
        e.caja_rot(tuple(m.p(s, t_ext - lado_pasarela * 150, n_sup - 60)), (1300, 120, 80), rz, "plastico_blanco",
                   f"IL-{cid}", "Luminaria LED estanca IP66 2 × 18 W")
    # caballetes
    for s in apoyos:
        a = m.p(s, t_int - lado_pasarela * 150, n_inf)
        b = m.p(s, t_ext + lado_pasarela * 150, n_inf)
        for p in (a, b):
            C.columna(e, p[0], p[1], z_suelo, p[2] - 160, "HEB 160", tag=f"CAB-{cid}", placa=(320, 320, 16), d_anclaje=20)
        e.barra(np.subtract(a, (0, 0, 80)), np.subtract(b, (0, 0, 80)), "UPN 160", "estructura", up=(0, 0, 1),
                cod=f"CAB-{cid}", nom="Viga del caballete UPN 160")
        e.barra((a[0], a[1], z_suelo + 300), (b[0], b[1], a[2] - 400), "L 63", "estructura", cod=f"CAB-{cid}",
                nom="Cruz de San Andrés L 63")
        e.barra((b[0], b[1], z_suelo + 300), (a[0], a[1], a[2] - 400), "L 63", "estructura", cod=f"CAB-{cid}",
                nom="Cruz de San Andrés L 63")
    # escalera marinera con jaula en la cola (segunda salida de la pasarela)
    if escalera_cola:
        tm = (tp0 + tp1) / 2
        pie = m.p(s0 - 450, tm, 0)
        alto = m.p(s0, tm, n_pas)[2] - z_suelo
        pie[2] = z_suelo
        C.escalera_marinera(e, pie, alto, tag=tag, frente=tuple(m.uh))
    return {"n_inf": n_inf, "n_pas": n_pas, "t_ext": t_ext, "t_int": t_int, "tp": (tp0, tp1)}


# ===================================================================================== torres de transferencia
def torre(e, tt):
    e.en("Torres de transferencia")
    x, y = tt["x"] * 1000, tt["y"] * 1000
    A, B_ = tt["A"] * 1000, tt["B"] * 1000
    zp = tt["z_plataforma"] * 1000
    techo = 8200.0
    tag = tt["id"]
    sig = 1 if tt["lado"] == "O" else -1                 # sentido hacia la planta
    ce = TR["CE-" + tt["lado"]]
    cp = TR["CP-" + tt["lado"]]
    B = ce["ancho"] * 1000
    Dh = d_cab(B)
    x0, x1, y0, y1 = x - A / 2, x + A / 2, y - B_ / 2, y + B_ / 2
    x_ce, x_cp = (x0, x1) if sig > 0 else (x1, x0)       # cara por donde entra la colectora y por donde sale la principal
    mce, mcp = Marco(ce["p0"], ce["p1"]), Marco(cp["p0"], cp["p1"])
    # ------------------------------------------------------------------ columnas, vigas y arriostramientos
    for xx in (x0, x1):
        for yy in (y0, y1):
            C.columna(e, xx, yy, 0, techo, "HEB 160", tag=tag, placa=(340, 340, 18), d_anclaje=20)
    for z in (zp - 100, techo - 100):
        for (a, b) in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
            e.barra((a[0], a[1], z), (b[0], b[1], z), "UPN 160", "estructura", up=(0, 0, 1), cod=tag,
                    nom="Viga perimetral UPN 160")
    e.barra((x0, y1, 400), (x1, y1, zp - 300), "L 80", "estructura", cod=tag, nom="Cruz de San Andrés L 80")
    e.barra((x1, y1, 400), (x0, y1, zp - 300), "L 80", "estructura", cod=tag, nom="Cruz de San Andrés L 80")
    for xx in (x0, x1):                                                  # caras Este y Oeste: cruz bajo las cintas
        e.barra((xx, y0, 400), (xx, y1, 3200), "L 80", "estructura", cod=tag, nom="Cruz de San Andrés L 80")
        e.barra((xx, y1, 400), (xx, y0, 3200), "L 80", "estructura", cod=tag, nom="Cruz de San Andrés L 80")
        e.barra((xx, y0, 3300), (xx, y1, 3300), "UPN 120", "estructura", up=(0, 0, 1), cod=tag, nom="Viga intermedia UPN 120")
    for xx, d in ((x0, 1), (x1, -1)):                                    # cara Sur: puntales de esquina (paso del chute)
        e.barra((xx, y0, 2500), (xx + d * 800, y0, zp - 180), "L 80", "estructura", cod=tag, nom="Puntal de esquina L 80")
    e.barra((x0, y0, 3300), (x1, y0, 3300), "UPN 160", "estructura", up=(0, 0, 1), cod=tag,
            nom="Viga soporte del chute de emergencia UPN 160")
    # vigas donde apoyan los extremos de las galerías
    z_gce = ce["p1"][2] * 1000 - Dh / 2 - 650 - 120
    s_cp = mcp.s_de_x(x_cp)
    z_gcp = mcp.p(s_cp)[2] - Dh / 2 - 650 - 120
    for xx, zz, nom in ((x_ce, z_gce, "colectora"), (x_cp, z_gcp, "principal")):
        e.barra((xx, y0, zz), (xx, y1, zz), "UPN 160", "estructura", up=(0, 0, 1), cod=tag,
                nom=f"Viga de apoyo de la galería de la {nom} UPN 160")
    # cabezal de la colectora colgado de vigas de techo; cola de la principal sobre patas
    s_h = mce.L + 150
    p_h = mce.p(s_h + 200)
    for yy in (y - 650, y + 650):
        e.barra((x0, yy, techo - 100), (x1, yy, techo - 100), "UPN 160", "estructura", up=(0, 0, 1), cod=tag,
                nom="Viga de techo para colgar el cabezal UPN 160")
        e.barra((p_h[0] + sig * 0, yy, techo - 180), (p_h[0], yy, ce["p1"][2] * 1000 - Dh / 2 - 170 - 140), "L 63",
                "estructura", cod=tag, nom="Colgador del cabezal L 63")
    e.barra((p_h[0], y - 700, ce["p1"][2] * 1000 - Dh / 2 - 170 - 140), (p_h[0], y + 700, ce["p1"][2] * 1000 - Dh / 2 - 170 - 140),
            "UPN 100", "estructura", up=(0, 0, 1), cod=tag, nom="Travesaño colgado del cabezal UPN 100")
    patas(e, mcp, [300.0, 1700.0], cp["ancho"] * 1000, cp["id"], riostras=False)
    # ------------------------------------------------------------------ plataforma con abertura sobre la cola de la CP
    xa0, xa1 = sorted((cp["p0"][0] * 1000 - sig * 500, cp["p0"][0] * 1000 + sig * 1700))
    xa0, xa1 = max(xa0, x0), min(xa1, x1)
    ya0, ya1 = y - 600, y + 600
    for (a0, b0, a1, b1) in ((x0, y0, x1, ya0), (x0, ya1, x1, y1), (x0, ya0, xa0, ya1), (xa1, ya0, x1, ya1)):
        if a1 - a0 > 50 and b1 - b0 > 50:
            e.caja(a0, b0, zp - 30, a1, b1, zp, "rejilla", cod=tag, nom="Piso de rejilla electrosoldada")
    for yy in (ya0, ya1):
        e.barra((x0, yy, zp - 100), (x1, yy, zp - 100), "UPN 120", "estructura", up=(0, 0, 1), cod=tag,
                nom="Brochal de la abertura UPN 120")
    x_lib = xa1 if sig > 0 else xa0
    C.baranda(e, [(xa0, ya0, zp), (xa1, ya0, zp)], tag=tag)
    C.baranda(e, [(xa0, ya1, zp), (xa1, ya1, zp)], tag=tag)
    C.baranda(e, [(x_lib, ya0, zp), (x_lib, ya1, zp)], tag=tag)
    # barandas perimetrales: llegadas de la escalera (Norte) y de las pasarelas de la CE (Sur) y de la CP (Norte)
    ce_tp = (y - 1525, y - 725)
    cp_tp = (y + 725, y + 1525)
    C.baranda(e, [(x0, y0, zp), (x1, y0, zp)], tag=tag)
    C.baranda(e, [(x0, y1, zp), (x - 450, y1, zp)], tag=tag)
    C.baranda(e, [(x + 450, y1, zp), (x1, y1, zp)], tag=tag)
    for xx, (ya, yb) in ((x_ce, ce_tp), (x_cp, cp_tp)):
        if ya - y0 > 300:
            C.baranda(e, [(xx, y0, zp), (xx, ya, zp)], tag=tag)
        if y1 - yb > 300:
            C.baranda(e, [(xx, yb, zp), (xx, y1, zp)], tag=tag)
    # escalones a las pasarelas (CE más arriba que la plataforma, CP más abajo) y escalera principal a 42°
    z_ce = ce["p1"][2] * 1000 - Dh / 2 - 650 + 150
    z_cp = mcp.p(s_cp)[2] - Dh / 2 - 650 + 150
    ym = sum(ce_tp) / 2
    C.escalera(e, (x_ce + sig * 950, ym, zp), (x_ce + sig * 150, ym, z_ce), 760, tag=tag)
    ym = sum(cp_tp) / 2
    C.escalera(e, (x_cp + sig * 1400, ym, z_cp), (x_cp - sig * 150, ym, zp), 760, tag=tag)
    run = zp / math.tan(math.radians(42))
    C.escalera(e, (x, y1 + 150 + run, 0), (x, y1 + 150, zp), 800, tag=tag)
    # ------------------------------------------------------------------ techo, correas, cerramientos y luminarias
    e.caja(x0 - 400, y0 - 400, techo, x1 + 400, y1 + 400, techo + 60, "chapa_techo", cod=tag, nom="Techo de chapa trapezoidal")
    for xx in np.linspace(x0, x1, 4):
        e.barra((xx, y0 - 400, techo - 50), (xx, y1 + 400, techo - 50), "C 100", "estructura", cod=tag, nom="Correa C 100")
    for yy in (y0, y1):
        e.caja(x0, yy - 25, zp + 1500, x1, yy + 25, techo, "chapa_trap", cod=tag, nom="Cerramiento lateral")
    for xx in (x0, x1):
        z_inf = 7150 if xx == x_ce else zp + 1500
        e.caja(xx - 25, y0, z_inf, xx + 25, y1, techo, "chapa_trap", cod=tag, nom="Cerramiento lateral")
    for xx in (x0 + 700, x1 - 700):
        e.caja_rot((xx, y, techo - 200), (1300, 120, 80), 0, "plastico_blanco", tag, "Luminaria LED estanca IP66 2 × 18 W")
    # ------------------------------------------------------------------ compuerta desviadora tipo pantalón
    dv = tt["desviadora"]
    xd = x - sig * 300
    z_falda = cp["p0"][2] * 1000 + 420
    zd0, zd1 = z_falda + 230, z_falda + 830
    e.caja(xd - 450, y - 450, zd0, xd + 450, y + 450, zd1, "galv", cod=dv, nom=f"Cuerpo de la desviadora {dv} (pantalón)")
    for zz in (zd0, zd1 - 10):
        e.caja(xd - 480, y - 480, zz, xd + 480, y + 480, zz + 10, "galv", cod=dv, nom="Brida")
    e.caja(xd - 250, y - 225, z_falda, xd + 250, y + 225, zd0, "galv", cod=dv, nom="Pierna A hacia la cinta principal")
    zc = (zd0 + zd1) / 2
    xa = xd + sig * 450
    e.cil((xd - sig * 520, y - 150, zc), (xa + sig * 40, y - 150, zc), 25, "acero", cod=dv, nom="Eje de la clapeta")
    e.cil((xa + sig * 40, y - 150, zc), (xa + sig * 300, y - 150, zc), 115, "plastico_gris", cod=dv,
          nom="Actuador eléctrico de cuarto de vuelta")
    C.motor(e, 0.37, T(xa + sig * 170, y - 150, zc + 120) @ Rz(90), "M89" if tt["lado"] == "O" else "M90", patas=False)
    for k, nom in ((1, "A"), (-1, "B")):
        C.sensor(e, "final", (xa + sig * 170, y - 150 + k * 120, zc - 60), (0, k, 0), tag=f"ZS{nom}-{dv}")
    C.placa(e, (xd, y + 455, zc), (0, 1, 0), 380, 160, "amarillo", tag=dv,
            nom=f"{dv}: A = a la planta / B = a la boca de emergencia")
    # pierna B: chute de emergencia a 50° hacia el Sur, apoyado en la viga de la cara Sur
    ang = math.radians(tt["chute_ang"])
    zb = tt["boca_emergencia_z"] * 1000
    pB0 = np.array([xd, y - 450, zd0 + 220])
    dz = pB0[2] - (zb + 300)
    pB1 = pB0 + np.array([0, -dz / math.tan(ang), -dz])
    Gb = alinear(pB0, pB1, up=(0, 0, 1))
    Lb = float(np.linalg.norm(pB1 - pB0))
    e.caja(-225, -225, 0, 225, 225, Lb, "galv", M=Gb, cod=dv, nom="Chute de emergencia 450 × 450 a 50° (pierna B)")
    for s in np.arange(300, Lb, 900):
        e.caja(-250, -250, s, 250, 250, s + 12, "galv", M=Gb, cod=dv, nom="Brida del chute")
    e.caja(-240, -240, Lb * 0.45, 240, 240, Lb * 0.45 + 300, "amarillo", M=Gb, cod=dv, nom="Tapa de inspección del chute")
    e.caja(pB1[0] - 275, pB1[1] - 275, zb, pB1[0] + 275, pB1[1] + 275, zb + 320, "galv", cod=dv,
           nom="Boca de carga de emergencia")
    e.cil((pB1[0], pB1[1], zb), (pB1[0], pB1[1], zb - 200), 230, "goma", cod=dv, nom="Manga de goma antipolvo")
    C.sensor(e, "atasco", (pB1[0] + 280, pB1[1], zb + 160), (1, 0, 0), tag=f"LSH-{dv}")
    # ------------------------------------------------------------------ contenedor roll-off de 20 m³
    cr = tt["contenedor"]
    cx, cy = cr["x"] * 1000, cr["y"] * 1000
    Lc, Ac, Hc = cr["L"] * 1000, cr["A"] * 1000, cr["H"] * 1000
    e.en("Contenedores de emergencia")
    ct = cr["id"]
    for (a0, b0, a1, b1) in ((cx - Lc / 2, cy - Ac / 2, cx + Lc / 2, cy - Ac / 2 + 5),
                             (cx - Lc / 2, cy + Ac / 2 - 5, cx + Lc / 2, cy + Ac / 2),
                             (cx - Lc / 2, cy - Ac / 2, cx - Lc / 2 + 5, cy + Ac / 2),
                             (cx + Lc / 2 - 5, cy - Ac / 2, cx + Lc / 2, cy + Ac / 2)):
        e.caja(a0, b0, 250, a1, b1, Hc, "verde", cod=ct, nom=f"Contenedor roll-off {ct} de {cr['cap_m3']} m³")
    e.caja(cx - Lc / 2, cy - Ac / 2, 250, cx + Lc / 2, cy + Ac / 2, 260, "verde", cod=ct, nom="Piso del contenedor")
    for xx in np.arange(cx - Lc / 2 + 600, cx + Lc / 2, 600):
        for yy in (cy - Ac / 2 - 40, cy + Ac / 2):
            e.caja(xx - 30, yy, 250, xx + 30, yy + 40, Hc, "verde", cod=ct, nom="Nervio vertical")
    for yy in (cy - Ac / 2 - 50, cy + Ac / 2 - 50):
        e.caja(cx - Lc / 2, yy, Hc - 100, cx + Lc / 2, yy + 100, Hc, "verde", cod=ct, nom="Borde superior")
    for yy in (cy - 500, cy + 500):
        e.barra((cx - Lc / 2, yy, 125), (cx + Lc / 2, yy, 125), "IPN 200", "verde", up=(1, 0, 0), cod=ct,
                nom="Larguero de deslizamiento IPN 200")
    xr = cx + sig * (Lc / 2 - 150)
    for yy in (cy - 650, cy + 650):
        e.cil((xr, yy - 80, 140), (xr, yy + 80, 140), 130, "negro", cod=ct, nom="Rodillo trasero")
    xg = cx - sig * Lc / 2
    for yy in (cy - 600, cy + 600):
        e.barra((xg, yy, 300), (xg - sig * 450, cy, 1550), "RHS 100", "verde", cod=ct, nom="Bastidor del gancho")
    e.cil((xg - sig * 450, cy - 120, 1550), (xg - sig * 450, cy + 120, 1550), 30, "acero", cod=ct, nom="Barra del gancho")
    for yy in (cy - 700, cy + 700):
        e.caja(xr + sig * 250 - 150, yy - 200, 0, xr + sig * 250 + 150, yy + 200, 150, "amarillo", cod=ct,
               nom="Tope de posicionamiento del contenedor")
    e.en("Torres de transferencia")
    # ------------------------------------------------------------------ periferia remota, botonera y cartel
    C.tablero(e, x_cp - sig * 700, y1 - 260, zp, 800, 1000, 300, rotz=180, tag=f"RIO-{tt['lado']}",
              nombre=f"Tablero de periferia remota RIO-{tt['lado']} (ET 200SP, PROFINET)")
    C.botonera(e, (x - 600, y0 + 60, zp + 1200), (0, 1, 0), tag=tag)
    C.placa(e, (x, y1 + 30, zp + 1600), (0, 1, 0), 900, 300, "amarillo", tag=tag,
            nom=f"{tag} · TORRE DE TRANSFERENCIA · USAR ARNÉS EN LA ABERTURA")


# ===================================================================================== tolva pulmón TP-01
def _offset(pts, d):
    """Desplaza la polilínea abierta `pts` (x, z) una distancia d hacia su derecha (abajo, si se recorre en +x)."""
    P = np.asarray(pts, float)
    nrm = []
    for a, b in zip(P, P[1:]):
        t = (b - a) / np.linalg.norm(b - a)
        nrm.append(np.array([t[1], -t[0]]))
    out = []
    for i in range(len(P)):
        if i == 0:
            out.append(P[i] + nrm[0] * d)
        elif i == len(P) - 1:
            out.append(P[i] + nrm[-1] * d)
        else:
            n = nrm[i - 1] + nrm[i]
            ln = np.linalg.norm(n)
            if ln < 1e-6:
                out.append(P[i] + nrm[i] * d)
            else:
                n /= ln
                out.append(P[i] + n * d / max(0.3, float(np.dot(n, nrm[i]))))
    return [tuple(p) for p in out]


def _perfil_w(x0, x1, n, za, r, h_rect, z_apex, seg=12):
    """Cara interior del fondo en W (x, z): artesas en U de radio r con lados rectos de h_rect y lomos hasta z_apex."""
    w = (x1 - x0) / n
    pts = [(x0, z_apex)]
    for i in range(n):
        xc = x0 + w * (i + 0.5)
        pts += [(xc - r, za + h_rect), (xc - r, za)]
        for k in range(1, seg):
            a = math.pi + math.pi * k / seg
            pts.append((xc + r * math.cos(a), za + r * math.sin(a)))
        pts += [(xc + r, za), (xc + r, za + h_rect), (x0 + w * (i + 1), z_apex)]
    return pts


def _prisma_xz(pts, largo):
    """Prisma de sección `pts` (x, z) extruido de y = 0 a y = largo."""
    s = cq.Workplane("XZ").polyline(pts).close().extrude(-largo)
    bb = s.val().BoundingBox()
    if bb.ymin < -1:                 # por si la normal del plano XZ apunta al revés en esta versión
        s = s.translate((0, -bb.ymin, 0))
    return s


def tolva_pulmon(e):
    tp = D["tolva_pulmon"]
    sf = tp["sinfines"]
    e.en("Recepción - tolva pulmón TP-01")
    x0, x1, y0, y1 = (tp[k] * 1000 for k in ("x0", "x1", "y0", "y1"))
    zf, zb, zt = tp["z_fondo"] * 1000, tp["z_borde"] * 1000, tp["z_tapa"] * 1000
    tag = tp["id"]
    n, Ds = sf["n"], sf["D"] * 1000
    za, r, hr = sf["z_eje"] * 1000, Ds / 2 + 15, 200.0
    w = (x1 - x0) / n
    xs = [x0 + w * (i + 0.5) for i in range(n)]
    e_ch = 8.0
    # ------------------------------------------------------------------ cuerpo: paredes y rigidizadores
    for (a0, b0, a1, b1) in ((x0 - e_ch, y0 - e_ch, x1 + e_ch, y0), (x0 - e_ch, y1, x1 + e_ch, y1 + e_ch),
                             (x0 - e_ch, y0, x0, y1), (x1, y0, x1 + e_ch, y1)):
        e.caja(a0, b0, zf, a1, b1, zb, "acero_pintado", cod=tag, nom="Pared de chapa 8 mm F-24")
    for z in np.arange(zf + 350, zb - 100, 550):
        e.barra((x0 - 60, y0 - 60, z), (x1 + 60, y0 - 60, z), "UPN 100", "acero_pintado", up=(0, -1, 0), cod=tag, nom="Rigidizador UPN 100")
        e.barra((x0 - 60, y1 + 60, z), (x1 + 60, y1 + 60, z), "UPN 100", "acero_pintado", up=(0, 1, 0), cod=tag, nom="Rigidizador UPN 100")
        e.barra((x0 - 60, y0 - 60, z), (x0 - 60, y1 + 60, z), "UPN 100", "acero_pintado", up=(-1, 0, 0), cod=tag, nom="Rigidizador UPN 100")
        e.barra((x1 + 60, y0 - 60, z), (x1 + 60, y1 + 60, z), "UPN 100", "acero_pintado", up=(1, 0, 0), cod=tag, nom="Rigidizador UPN 100")
    for xx in np.linspace(x0, x1, 5)[1:-1]:
        for yy, d in ((y0 - 50, -1), (y1 + 50, 1)):
            e.barra((xx, yy, zf), (xx, yy, zb), "UPN 100", "acero_pintado", up=(0, d, 0), cod=tag, nom="Montante rigidizador UPN 100")
    # ------------------------------------------------------------------ fondo en W con 4 artesas y lomos a 60°
    sup = _perfil_w(x0, x1, n, za, r, hr, zf)
    inf = _offset(sup, e_ch)
    k_w = proto(("fondo_w", round(x1 - x0), round(y1 - y0), round(za), n), lambda: _prisma_xz(sup + inf[::-1], y1 - y0))
    e.add(k_w, "acero_pintado", T(0, y0, 0), tag, "Fondo en W de chapa 8 mm con 4 artesas")
    k_tes = proto(("valles_w", round(x1 - x0), round(za), n), lambda: _prisma_xz(sup, e_ch))
    e.add(k_tes, "acero_pintado", T(0, y0 - e_ch, 0), tag, "Testero inferior Sur")
    e.add(k_tes, "acero_pintado", T(0, y1, 0), tag, "Testero inferior Norte")
    costilla = _offset(sup, e_ch) + _offset(sup, e_ch + 160)[::-1]
    k_cost = proto(("costilla_w", round(x1 - x0), round(za), n), lambda: _prisma_xz(costilla, 12))
    for yy in np.linspace(y0, y1, 5)[1:-1]:
        e.add(k_cost, "estructura", T(0, yy - 6, 0), tag, "Costilla transversal 12 mm bajo el fondo")
    # ------------------------------------------------------------------ artesas fuera de la tolva, sinfines y accionamientos
    u_sup = [(-r, hr)] + [(r * math.cos(math.pi + math.pi * k / 12), r * math.sin(math.pi + math.pi * k / 12))
                          for k in range(13)] + [(r, hr)]
    u_inf = _offset(u_sup, 6)
    ys0, ys1 = sf["y_sur"] * 1000, sf["y_norte"] * 1000
    yboca = sf["bocas_y"] * 1000
    z_c3 = CINTA3["z_carga"] * 1000
    s_red = (3.0 / 1.1) ** (1 / 3)
    zc_red = 210 * s_red / 2 + 20
    for i, xc in enumerate(xs):
        for (ya, yb_) in ((ys0, y0 - e_ch), (y1 + e_ch, ys1)):
            k_u = proto(("artesa_u", round(r), round(yb_ - ya)), lambda ya=ya, yb_=yb_: _prisma_xz(u_sup + u_inf[::-1], yb_ - ya))
            e.add(k_u, "acero_pintado", T(xc, ya, za), tag, "Artesa en U de chapa 6 mm")
            e.caja(xc - r - 30, ya, za + hr, xc + r + 30, yb_, za + hr + 5, "galv", cod=tag, nom="Tapa abulonada de la artesa")
            for sg in (-1, 1):
                e.barra((xc + sg * (r + 15), ya, za + hr - 20), (xc + sg * (r + 15), yb_, za + hr - 20), "L 50",
                        "acero_pintado", up=(sg, 0, 0), cod=tag, nom="Ala de la artesa L 50")
        e.caja(xc - r - 40, ys0 - 10, za - r - 40, xc + r + 40, ys0, za + hr + 20, "acero_pintado", cod=tag,
               nom="Placa de cabeza de la artesa")
        e.caja(xc - r - 40, ys1, za - r - 40, xc + r + 40, ys1 + 10, za + hr + 20, "acero_pintado", cod=tag,
               nom="Placa de cabeza de la artesa")
        C.chumacera_ucf(e, 60, T(xc, ys0 - 28, za) @ Rz(180), tag)
        e.tubo((xc, ys0 + 30, za), (xc, ys1 - 30, za), 57, 50, "acero", cod=tag, nom="Tubo central del sinfín Ø114")
        k_esp = proto(("espira", Ds), lambda: wp().circle(Ds / 2).circle(57).extrude(8))
        for yy in np.arange(ys0 + 120, ys1 - 80, Ds * 0.8):
            e.add(k_esp, "galv", T(xc, yy, za) @ Rx(-90) @ Rx(14), tag, f"Espira del sinfín Ø{Ds:.0f} paso {Ds * 0.8:.0f}")
        C.motorreductor_coaxial(e, 3.0, T(xc, ys1 + 70, za - zc_red) @ Rz(-90), tag=f"M{85 + i}", patas=True)
        e.caja(xc - 180, ys1 + 10, za - zc_red - 20, xc + 180, ys1 + 760, za - zc_red, "acero_pintado", cod=tag,
               nom="Ménsula del motorreductor")
        e.barra((xc, ys1 + 10, za - r - 40), (xc, ys1 + 700, za - zc_red - 20), "L 50", "acero_pintado", cod=tag,
                nom="Pie de amigo de la ménsula")
        C.sensor(e, "velocidad", (xc - r - 60, ys0 - 10, za), (0, -1, 0), tag=f"SSL-M{85 + i}")
        # boca de descarga sobre la cinta 3, con manga y detector de atascamiento
        e.caja(xc - 210, yboca - 210, z_c3 + 280, xc + 210, yboca + 210, za - r, "galv", cod=tag,
               nom="Boca de descarga del sinfín a la cinta 3")
        e.cil((xc, yboca, z_c3 + 280), (xc, yboca, z_c3 + 120), 190, "goma", cod=tag, nom="Manga de goma")
        C.sensor(e, "atasco", (xc + 215, yboca, za - r - 120), (1, 0, 0), tag=f"LSH-{102 + i}")
    # ------------------------------------------------------------------ tapa transitable, bocas, registros y aspiración
    e.caja(x0 - 30, y0 - 30, zb, x1 + 30, y1 + 30, zb + 10, "estructura", cod=tag, nom="Aro superior L 80")
    for yy in np.arange(y0 + 600, y1, 1200):
        e.barra((x0, yy, zt - 85), (x1, yy, zt - 85), "UPN 140", "estructura", up=(0, 0, 1), cod=tag, nom="Viga de la tapa UPN 140")
    e.caja(x0 - 30, y0 - 30, zt - 6, x1 + 30, y1 + 30, zt, "galv", cod=tag, nom="Tapa de chapa semilla de melón 6,35 mm")
    for (cx, cy) in ((1700, 11300), (3900, 11300)):
        e.caja(cx - 400, cy - 350, zt, cx + 400, cy + 350, zt + 50, "amarillo", cod=tag,
               nom="Registro de inspección 800 × 700 con bisagras y traba")
        e.caja(cx - 420, cy + 330, zt + 30, cx + 420, cy + 360, zt + 80, "negro", cod=tag, nom="Bisagra")
    e.tubo((1200, 15900, zt), (1200, 15900, 6000), 300, 296, "galv", cod=tag, nom="Boca de aspiración Ø600 (a M23 y biofiltro)")
    C.cano(e, [(1200, 15900, 6000), (1200, 18300, 6000)], d=600, tag=tag, mat="galv")
    e.caja(1500, 15850, 5050, 1620, 15950, 5250, "amarillo", cod=tag, nom="Compuerta mariposa con palanca")
    C.sensor(e, "radar", (3100, 12600, zt + 10), (0, 0, 1), tag="LT-101")
    C.sensor(e, "horquilla", (x0 - 10, 13000, zb - 450), (-1, 0, 0), tag="LSHH-101")
    C.sensor(e, "horquilla", (x0 - 10, 12000, zf + 250), (-1, 0, 0), tag="LSL-101")
    # ------------------------------------------------------------------ apoyos con 4 celdas de carga
    z_aro = zf - 80
    for yy in (y0 - 80, y1 + 80):
        e.barra((x0 - 160, yy, z_aro), (x1 + 160, yy, z_aro), "HEB 160", "estructura", up=(0, 0, 1), cod=tag, nom="Viga de apoyo HEB 160")
    for xx in (x0 - 80, x1 + 80):
        e.barra((xx, y0 - 160, z_aro), (xx, y1 + 160, z_aro), "HEB 160", "estructura", up=(0, 0, 1), cod=tag, nom="Viga de apoyo HEB 160")
    z_col = z_aro - 80 - 130
    esquinas = [(x0 - 80, y0 - 80), (x1 + 80, y0 - 80), (x0 - 80, y1 + 80), (x1 + 80, y1 + 80)]
    for i, (xx, yy) in enumerate(esquinas):
        C.columna(e, xx, yy, 0, z_col, "HEB 160", tag=tag, placa=(360, 360, 20), d_anclaje=20)
        e.caja(xx - 120, yy - 120, z_col, xx + 120, yy + 120, z_col + 20, "estructura", cod=tag, nom="Placa de apoyo de la celda")
        C.sensor(e, "celda", (xx, yy, z_col + 20), (0, 0, 1), tag=f"WT-10{i + 1}")
    for xx in (x0 - 80, x1 + 80):
        e.barra((xx, y0 - 80, 350), (xx, y1 + 80, z_col - 250), "L 80", "estructura", cod=tag, nom="Cruz de San Andrés L 80")
        e.barra((xx, y1 + 80, 350), (xx, y0 - 80, z_col - 250), "L 80", "estructura", cod=tag, nom="Cruz de San Andrés L 80")
    for yy in (y0 - 80, y1 + 80):
        e.barra((x0 - 80, yy, 300), (x1 + 80, yy, 300), "UPN 120", "estructura", up=(0, 0, 1), cod=tag, nom="Riostra baja UPN 120")
    # ------------------------------------------------------------------ barandas, descanso y escalera de acceso
    C.baranda(e, [(x0 - 30, y0 - 30, zt), (x0 - 30, y1 + 30, zt), (x1 + 30, y1 + 30, zt)], tag=tag)
    C.baranda(e, [(x0 - 30, y0 - 30, zt), (x1 + 30, y0 - 30, zt)], tag=tag)
    C.baranda(e, [(x1 + 30, y0 + 1100, zt), (x1 + 30, 13800, zt)], tag=tag)
    C.baranda(e, [(x1 + 30, 15850, zt), (x1 + 30, y1 + 30, zt)], tag=tag)
    xd0, xd1 = x1 + 100, x1 + 1100
    e.caja(xd0, y0 - 100, zt - 30, xd1, y0 + 1000, zt, "rejilla", cod=tag, nom="Descanso de rejilla")
    for (a, b) in (((xd0, y0 - 100), (xd1, y0 - 100)), ((xd1, y0 - 100), (xd1, y0 + 1000)), ((xd0, y0 + 1000), (xd1, y0 + 1000))):
        e.barra((a[0], a[1], zt - 100), (b[0], b[1], zt - 100), "UPN 140", "estructura", up=(0, 0, 1), cod=tag, nom="Marco del descanso")
    for yy in (y0 - 50, y0 + 950):
        C.columna(e, xd1 - 50, yy, 0, zt - 170, "RHS 100", tag=tag, placa=(220, 220, 12), d_anclaje=12)
    C.baranda(e, [(xd1, y0 - 100 + 900, zt), (xd1, y0 + 1000, zt), (xd0, y0 + 1000, zt)], tag=tag)
    run = zt / math.tan(math.radians(42))
    xm = (xd0 + xd1) / 2
    C.escalera(e, (xm, y0 - 100 - run, 0), (xm, y0 - 100, zt), 800, tag=tag)
    C.placa(e, ((x0 + x1) / 2, y0 - 70, zb - 350), (0, -1, 0), 1200, 320, "amarillo", tag=tag,
            nom="TP-01 TOLVA PULMÓN 46 m³ · PELIGRO: ATRAPAMIENTO Y ESPACIO CONFINADO · BLOQUEAR M85 A M88 ANTES DE ENTRAR")
    e.en(GRUPO)


# ===================================================================================== pórtico de cabezales PC-01
def portico_cabezales(e):
    """Pórtico que sostiene los cabezales de CP-O y CP-E sobre la tolva sin cargarla (la tolva pesa en celdas)."""
    e.en("Recepción - tolva pulmón TP-01")
    tp = D["tolva_pulmon"]
    tag = "PC-01"
    ya, yb = (CINTA3["y"] + 0.62) * 1000, (tp["y1"] + 0.45) * 1000
    z_v = 6250.0
    for xx in (1700.0, 3800.0):
        for yy in (ya, yb):
            C.columna(e, xx, yy, 0, z_v - 80, "HEB 140", tag=tag, placa=(300, 300, 16), d_anclaje=16)
        e.barra((xx, ya - 100, z_v), (xx, yb + 100, z_v), "HEB 160", "estructura", up=(0, 0, 1), cod=tag,
                nom="Viga del pórtico de cabezales HEB 160")
        e.barra((xx, ya, 5000), (xx, ya + 1200, z_v - 80), "L 63", "estructura", cod=tag, nom="Cartela L 63")
        e.barra((xx, yb, 5000), (xx, yb - 1200, z_v - 80), "L 63", "estructura", cod=tag, nom="Cartela L 63")
    for yy in (ya, yb):
        e.barra((1700, yy, z_v - 400), (3800, yy, z_v - 400), "UPN 120", "estructura", up=(0, 0, 1), cod=tag, nom="Riostra UPN 120")
    for cid, xx in (("CP-O", 1700.0), ("CP-E", 3800.0)):
        m = Marco(TR[cid]["p0"], TR[cid]["p1"])
        B = TR[cid]["ancho"] * 1000
        s = m.s_de_x(xx)
        z_tr = m.p(s)[2] - d_cab(B) / 2 - 170 - 120
        for sg in (-1, 1):
            p = m.p(s, sg * (B / 2 + 220))
            e.barra((p[0], p[1], z_v - 80), (p[0], p[1], z_tr), "L 63", "estructura", cod=tag, nom=f"Colgador del cabezal de la {cid}")
        p0 = m.p(s, -(B / 2 + 260))
        p1 = m.p(s, B / 2 + 260)
        e.barra((p0[0], p0[1], z_tr), (p1[0], p1[1], z_tr), "UPN 100", "estructura", up=(0, 0, 1), cod=tag,
                nom=f"Travesaño del cabezal de la {cid}")


# ===================================================================================== cinta principal Este dentro de la nave
def colgadores_cp_e(e, x_porticos=(5.5, 11.0, 16.5, 22.0, 27.5)):
    """La CP-E cruza la nave colgada de las cerchas (cordón inferior a h_alero) con pasarela de 0,6 m del lado Norte."""
    cid = "CP-E"
    m = Marco(TR[cid]["p0"], TR[cid]["p1"])
    B = TR[cid]["ancho"] * 1000
    tag = f"COL-{cid}"
    z_cercha = NAVE["h_alero"] * 1000
    n_inf = -d_cab(B) / 2 - 250
    t_pas0, t_pas1 = -(B / 2 + 250), -(B / 2 + 850)            # −t de la CP-E es el Norte
    for xp in x_porticos:
        s = m.s_de_x(xp * 1000)
        a = m.p(s, B / 2 + 220, n_inf)
        b = m.p(s, t_pas1 - 60, n_inf)
        e.barra(a, b, "UPN 100", "estructura", up=(0, 0, 1), cod=tag, nom="Travesaño colgado UPN 100")
        for p in (a, b):
            e.barra(p, (p[0], p[1], z_cercha), "L 63", "estructura", cod=tag, nom="Colgador L 63 a la cercha")
        e.barra((a[0], a[1], z_cercha - 300), (b[0], b[1], a[2] + 300), "L 50", "estructura", cod=tag,
                nom="Diagonal de rigidez L 50")
    s0 = m.s_de_x(NAVE["L"] * 1000 - 100)
    s1 = m.s_de_x(5050)
    e.caja(s0, t_pas1, n_inf + 70, s1, t_pas0, n_inf + 100, "rejilla", M=m.M, cod=tag, nom="Pasarela interior de rejilla 0,6 m")
    e.barra(m.p(s0, t_pas1, n_inf + 1200), m.p(s1, t_pas1, n_inf + 1200), "CHS 42", "amarillo", cod=tag, nom="Pasamanos")
    e.barra(m.p(s0, t_pas1, n_inf + 650), m.p(s1, t_pas1, n_inf + 650), "CHS 33", "amarillo", cod=tag, nom="Travesaño de baranda")
    e.caja(s0, t_pas1 - 3, n_inf + 100, s1, t_pas1 + 3, n_inf + 250, "amarillo", M=m.M, cod=tag, nom="Rodapié")
    for s in np.arange(s0, s1, 1500):
        e.barra(m.p(s, t_pas1, n_inf + 100), m.p(s, t_pas1, n_inf + 1200), "CHS 42", "amarillo", cod=tag, nom="Parante")
    tc = t_pas1 + 60
    e.cil(m.p(s0 + 300, tc, n_inf + 1050), m.p(s1 - 300, tc, n_inf + 1050), 3, "rojo", cod=tag, nom="Cable de parada de emergencia")
    for s in (s0 + 300, (s0 + s1) / 2, s1 - 300):
        C.sensor(e, "tiron", m.p(s, tc, n_inf + 800), (0, 1, 0), tag=f"HS-{cid}")
    C.bandeja(e, m.p(s0, B / 2 + 300, n_inf + 50), m.p(s1, B / 2 + 300, n_inf + 50), 200, tag=f"BC-{cid}")
    # escalones de la pasarela a la tapa de la tolva
    p_a = m.p(s1, (t_pas0 + t_pas1) / 2, n_inf + 100)
    zt = D["tolva_pulmon"]["z_tapa"] * 1000
    C.escalera(e, (p_a[0] - 650, p_a[1], zt), (p_a[0] + 50, p_a[1], p_a[2]), 560, tag=tag)


# ===================================================================================== canal y foso de las cintas de los galpones
def canal_y_foso(e, ct, ci):
    """Canal de H° de la cinta transversal y foso de la inclinada, con rejillas y barandas en la parte abierta."""
    e.en("Transporte de guano - obra civil")
    tag = f"FOSO-{ci['id']}"
    y_ct = ct["p0"][1] * 1000
    xa, xb = sorted((ct["p0"][0] * 1000, ct["p1"][0] * 1000))
    xa, xb = xa - 650, xb + 350
    e.caja(xa, y_ct - 700, -1100, xb, y_ct + 700, -950, "hormigon", cod=tag, nom="Losa de fondo del canal")
    for yy in (y_ct - 850, y_ct + 700):
        e.caja(xa, yy, -1100, xb, yy + 150, 0, "hormigon", cod=tag, nom="Tabique del canal")
    e.caja(xa, y_ct - 700, -25, xb, y_ct + 700, 0, "rejilla", cod=tag, nom="Rejilla transitable del canal (30 × 100)")
    B = ct["ancho"] * 1000
    m = Marco(ct["p0"], ct["p1"])
    for s in np.arange(600, m.L, 2400):
        p = m.p(s)
        e.barra((p[0], y_ct - 760, -790), (p[0], y_ct + 760, -790), "UPN 100", "estructura", up=(0, 0, 1), cod=tag,
                nom="Apoyo de la cinta en el canal UPN 100")
    f = ci["foso"]
    fx0, fx1 = f["x0"] * 1000, f["x1"] * 1000
    fa, fb = f["y0"] * 1000, f["y1"] * 1000
    zf = f["z_fondo"] * 1000
    e.caja(fx0, fa, zf - 200, fx1, fb, zf, "hormigon", cod=tag, nom="Losa del foso de la cinta inclinada")
    for xx in (fx0 - 200, fx1):
        e.caja(xx, fa - 200, zf - 200, xx + 200, fb + 200, 0, "hormigon", cod=tag, nom="Tabique del foso")
    for yy in (fa - 200, fb):
        e.caja(fx0, yy, zf - 200, fx1, yy + 200, 0, "hormigon", cod=tag, nom="Tabique del foso")
    x_ci = ci["p0"][0] * 1000
    e.caja(x_ci - 250, fb - 600, zf - 120, x_ci + 250, fb - 200, zf, "hormigon_piso", cod=tag,
           nom="Sumidero con rejilla al tanque de efluentes")
    y_muro = D["galpones"][0]["y0"] * 1000
    e.caja(fx0, y_muro, -25, fx1, fb, 0, "rejilla", cod=tag, nom="Rejilla del foso (dentro del galpón)")
    C.baranda(e, [(fx0 - 100, y_muro - 200, 0), (fx0 - 100, fa - 100, 0), (fx1 + 100, fa - 100, 0),
                  (fx1 + 100, y_muro - 200, 0)], tag=tag)
    e.en(GRUPO)


# ===================================================================================== conjunto
def construir(e):
    tt = {t["lado"]: t for t in D["torres"]}
    ce_marco = {l: Marco(TR["CE-" + l]["p0"], TR["CE-" + l]["p1"]) for l in ("O", "E")}
    for g in D["galpones"]:
        k = g["id"][1]
        ct, ci = TR[f"CT-{k}"], TR[f"CI-{k}"]
        sig = g["hacia_planta"]
        # CT: el chute de cabeza la lleva al centro del tramo horizontal de la CI
        z_ci = ci["p0"][2] * 1000
        cinta(e, ct["id"], lado_motor=-1, capota=False,
              chute_a=(ci["p0"][0] * 1000, ct["p0"][1] * 1000, z_ci + 80 + 60, 380, 420))
        # CI: carga en el tramo horizontal; el chute de cabeza termina sobre los faldones de la colectora
        mce = ce_marco[g["lado"]]
        Bce = TR["CE-" + g["lado"]]["ancho"] * 1000
        n_s = (Bce / 2 - 70 - Bce / 6) * math.tan(math.radians(20))
        y_carga = (ci["p0"][1] - ct["p0"][1]) * 1000
        tr = cinta(e, ci["id"], bordes=True, cargas=(y_carga,), lado_motor=sig,
                   chute_a=(ci["p1"][0] * 1000, mce.p0[1], mce.p0[2] + n_s + 420, 420, Bce - 140))
        patas(e, tr[0], [500.0, 1500.0, 2500.0], ci["ancho"] * 1000, ci["id"], z_suelo=ci["foso"]["z_fondo"] * 1000,
              z_min=120, riostras=False)
        patas(e, tr[1], [400.0], ci["ancho"] * 1000, ci["id"], z_suelo=ci["foso"]["z_fondo"] * 1000, z_min=120,
              riostras=False)
        patas(e, tr[1], list(np.arange(1800, tr[1].L - 600, 2300)), ci["ancho"] * 1000, ci["id"])
        canal_y_foso(e, ct, ci)
    for lado in ("O", "E"):
        ce, cp, t = TR["CE-" + lado], TR["CP-" + lado], tt[lado]
        sig = 1 if lado == "O" else -1
        mce = ce_marco[lado]
        B = ce["ancho"] * 1000
        # colectora: cargas donde caen las inclinadas; el chute de cabeza entra a la desviadora
        cargas = sorted(mce.s_de_x(TR["CI-" + g[1]]["p1"][0] * 1000) for g in ce["recibe"])
        xd = t["x"] * 1000 - sig * 300
        zd1 = cp["p0"][2] * 1000 + 420 + 830
        cinta(e, ce["id"], lado_motor=sig, cargas=tuple(cargas), chute_a=(xd, t["y"] * 1000, zd1, 820, 820))
        s_torre = mce.s_de_x(t["x"] * 1000 - sig * t["A"] * 500) - 40
        prohib = [(s - 1600, s + 1600) for s in cargas]
        for cam in D["caminos"]:
            if cam["y0"] * 1000 <= mce.p0[1] <= cam["y1"] * 1000 and cam["x1"] - cam["x0"] < 10:
                sa, sb = sorted((mce.s_de_x(cam["x0"] * 1000), mce.s_de_x(cam["x1"] * 1000)))
                prohib.append((sa - 1200, sb + 1200))
        apoyos = apoyos_galeria(-450.0, s_torre, prohib)
        abert = [(s - 750, s + 750) for s in cargas]
        galeria(e, mce, -600.0, s_torre, B, ce["id"], apoyos, lado_pasarela=-sig, aberturas=abert, escalera_cola=True)
        # principal: carga bajo la pierna A; chute de cabeza a la boca de la tapa de la tolva
        mcp = Marco(cp["p0"], cp["p1"])
        x_boca = (cp["p1"][0] + sig * 0.35) * 1000
        zt = D["tolva_pulmon"]["z_tapa"] * 1000
        x_muro = 0.0 if lado == "O" else NAVE["L"] * 1000
        s_m = mcp.s_de_x(x_muro - sig * 150)
        cinta(e, cp["id"], lado_motor=-sig, cargas=(700.0,), capota=True, capota_hasta=s_m,
              chute_a=(x_boca, cp["p1"][1] * 1000, zt, 560, 560))
        s_t = mcp.s_de_x(t["x"] * 1000 + sig * t["A"] * 500) + 40
        galeria(e, mcp, s_t, s_m, B, cp["id"], [mcp.s_de_x(x_muro - sig * 650)], lado_pasarela=sig)
        torre(e, t)
    tolva_pulmon(e)
    portico_cabezales(e)
    colgadores_cp_e(e)
