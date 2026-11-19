"""Componentes normalizados para la granja integrada (se agregan a una Escena con una matriz de colocación M).

Medidas en mm. Cada función documenta su sistema local. Las medidas de carcasa de los motores son las de
IEC 60072-1 (altura de eje H, separación de patas A y B, eje d × E); el resto son proporciones típicas de catálogo
y quedan como representativas (P).
"""
from __future__ import annotations

import math

import numpy as np

from cad import (I4, T, Rx, Ry, Rz, alinear, caja0, cil0, cono0, hex0, proto, tubo0, wp)

# ===================================================================================== motores IEC
#        kW: (carcasa, H, D cuerpo, L cuerpo, d eje, E eje, A, B)
CARCASAS = [
    (0.55, ("71", 71, 140, 235, 14, 30, 112, 90)), (1.1, ("80", 80, 160, 275, 19, 40, 125, 100)),
    (2.2, ("90", 90, 180, 320, 24, 50, 140, 125)), (3.0, ("100", 100, 200, 370, 28, 60, 160, 140)),
    (4.0, ("112", 112, 225, 395, 28, 60, 190, 140)), (7.5, ("132", 132, 265, 470, 38, 80, 216, 178)),
    (15.0, ("160", 160, 320, 610, 42, 110, 254, 254)), (22.0, ("180", 180, 360, 690, 48, 110, 279, 279)),
    (37.0, ("225", 225, 440, 810, 60, 140, 356, 311)),
]


def carcasa(kw):
    for lim, c in CARCASAS:
        if kw <= lim + 1e-6:
            return c
    return CARCASAS[-1][1]


def _cuerpo_aletado(D, L, n=28):
    r1, r2 = D / 2, D / 2 - 7
    pts = []
    for i in range(2 * n):
        a = math.pi * i / n
        r = r1 if i % 2 == 0 else r2
        pts.append((r * math.cos(a), r * math.sin(a)))
    return wp().polyline(pts).close().extrude(L)


def motor(e, kw, M=I4, tag="", patas=True, color="azul_motor"):
    """Motor trifásico IEC. Local: eje del motor según +X, punta del eje desde x = 0 hacia +X; cuerpo hacia −X;
    plano de apoyo de las patas en z = 0 (patas=True) o brida en x = 0 (patas=False, eje a z = 0)."""
    fr, H, D, L, d, E, A, B = carcasa(kw)
    zc = H if patas else 0.0
    base = M @ T(0, 0, zc)
    k_cuerpo = proto(("motor_cuerpo", fr), lambda: _cuerpo_aletado(D, L * 0.72))
    e.add(k_cuerpo, color, base @ Ry(-90) @ T(0, 0, L * 0.06), tag, f"Motor {tag} {kw} kW (carcasa {fr})")
    k_tapa = proto(("motor_tapa", fr), lambda: cil0(D / 2 - 2, L * 0.06))
    e.add(k_tapa, color, base @ Ry(-90), tag, "")
    k_vent = proto(("motor_cubrevent", fr), lambda: [tubo0(D / 2 + 3, D / 2 - 2, L * 0.20),
                                                     cil0(D / 2 - 2, 3).translate((0, 0, L * 0.20 - 3))])
    e.add(k_vent, color, base @ Ry(-90) @ T(0, 0, L * 0.78), tag, "")
    k_eje = proto(("motor_eje", fr), lambda: cil0(d / 2, E + 12))
    e.add(k_eje, "acero", base @ Ry(90) @ T(0, 0, -12), tag, "")
    tb = (0.46 * D, 0.40 * D, 0.30 * D)
    k_bornera = proto(("motor_bornera", fr), lambda: caja0(*tb))
    e.add(k_bornera, color, base @ T(-0.42 * L - tb[0] / 2, -tb[1] / 2, D / 2 - 6), tag, "")
    k_prensa = proto(("prensacable", round(0.08 * D)), lambda: [cil0(0.045 * D, 0.10 * D), hex0(0.11 * D, 0.03 * D)])
    e.add(k_prensa, "negro", base @ T(-0.42 * L, -tb[1] / 2, D / 2 - 6 + tb[2] / 2) @ Rx(90), tag, "")
    k_chapa = proto(("chapa_caract", fr), lambda: caja0(0.32 * D, 1.0, 0.18 * D))
    e.add(k_chapa, "aluminio", base @ T(-0.62 * L, -D / 2 - 4, -0.05 * D), tag, "")
    if patas:
        k_pata = proto(("motor_pata", fr), lambda: caja0(0.20 * D, A + 0.12 * D, 0.10 * H))
        for x in (-0.12 * L, -0.12 * L - B):
            e.add(k_pata, color, M @ T(x - 0.10 * D, -(A + 0.12 * D) / 2, 0), tag, "")
        k_alma = proto(("motor_alma", fr), lambda: caja0(B + 0.2 * D, 0.5 * A, H - D / 2 + 8))
        e.add(k_alma, color, M @ T(-0.12 * L - B - 0.1 * D, -0.25 * A, 0.08 * H), tag, "")
    else:
        k_brida = proto(("motor_brida", fr), lambda: cil0(0.62 * D + 25, 12))
        e.add(k_brida, color, base @ Ry(-90) @ T(0, 0, -2), tag, "")
    return {"L": L, "D": D, "H": H, "fr": fr}


# ===================================================================================== reductores
def motorreductor_ortogonal(e, kw, M=I4, tag="", d_salida=50, brazo=True):
    """Motorreductor de ejes ortogonales (cónico-helicoidal) con eje hueco y brazo de reacción.
    Local: eje de salida (hueco) según +Y centrado en el origen; carcasa hacia +X; motor sobre la carcasa,
    con su eje paralelo a −X... (sale hacia atrás del tambor) y brazo de reacción hacia −Z."""
    s = (max(kw, 0.37) / 1.1) ** (1 / 3)
    a, b, c = 230 * s, 190 * s, 250 * s                  # largo (X), ancho (Y), alto (Z)
    k = proto(("red_ort_caja", round(s, 2)), lambda: [caja0(a, b, c).translate((-0.18 * a, -b / 2, -0.42 * c)),
                                                       cil0(0.42 * b, b + 24).translate((0, 0, -(b + 24) / 2))
                                                       .rotate((0, 0, 0), (1, 0, 0), 90)])
    e.add(k, "reductor", M, tag, f"Motorreductor ortogonal {tag} {kw} kW")
    k_aleta = proto(("red_ort_aleta", round(s, 2)), lambda: caja0(0.65 * a, 6, 0.55 * c))
    for yy in (-b / 2 - 6, b / 2):
        e.add(k_aleta, "reductor", M @ T(0.05 * a, yy, -0.30 * c), tag, "")
    k_tapon = proto(("tapon_aceite",), lambda: [cil0(9, 10), hex0(16, 6).translate((0, 0, 10))])
    e.add(k_tapon, "rojo", M @ T(0.35 * a, 0, 0.58 * c), tag, "")
    k_tapon_b = proto(("tapon_purga",), lambda: [cil0(8, 8), hex0(14, 5).translate((0, 0, 8))])
    e.add(k_tapon_b, "negro", M @ T(0.35 * a, 0, -0.42 * c) @ Rx(180), tag, "")
    # motor montado sobre la brida de entrada, eje según −X
    mot = motor(e, kw, M @ T(0.82 * a + 4, 0, 0.08 * c) @ Rz(180), tag, patas=False)
    if brazo:
        k_br = proto(("brazo_reac", round(s, 2)), lambda: caja0(30, 18, 0.9 * c))
        e.add(k_br, "acero_pintado", M @ T(0.55 * a, -9, -0.42 * c - 0.9 * c), tag, "")
        k_buje = proto(("buje_goma", round(s, 2)), lambda: cil0(22, 34))
        e.add(k_buje, "goma", M @ T(0.55 * a + 15, -17, -0.42 * c - 0.85 * c) @ Rx(-90), tag, "")
    return {"a": a, "b": b, "c": c, "motor": mot}


def motorreductor_coaxial(e, kw, M=I4, tag="", patas=True):
    """Motorreductor coaxial (helicoidal) con patas. Local: eje de salida según +X desde x = 0; motor hacia −X."""
    s = (max(kw, 0.37) / 1.1) ** (1 / 3)
    a, b, c = 200 * s, 170 * s, 210 * s
    k = proto(("red_coax", round(s, 2)), lambda: [caja0(a, b, c).translate((-a, -b / 2, -c / 2)),
                                                   cil0(0.32 * b, 60 * s).rotate((0, 0, 0), (0, 1, 0), 90)])
    zc = c / 2 + 20 if patas else 0
    e.add(k, "reductor", M @ T(0, 0, zc), tag, f"Motorreductor coaxial {tag} {kw} kW")
    if patas:
        k_p = proto(("red_coax_pata", round(s, 2)), lambda: caja0(0.8 * a, b + 50, 22))
        e.add(k_p, "reductor", M @ T(-0.9 * a, -(b + 50) / 2, 0), tag, "")
    motor(e, kw, M @ T(-a, 0, zc) , tag, patas=False)
    return {"a": a, "b": b, "c": c}


# ===================================================================================== rodamientos y transmisión
UCP = {25: (36.5, 140, 38, 105), 30: (42.9, 165, 48, 121), 35: (47.6, 167, 48, 127), 40: (49.2, 184, 54, 137),
       50: (57.2, 206, 60, 159), 60: (69.8, 241, 70, 184)}


def chumacera_ucp(e, d, M=I4, tag=""):
    """Soporte de pie UCP. Local: eje según +Y por el origen; base en z = −H."""
    H, Lb, Wb, J = UCP.get(d, UCP[50])
    k_base = proto(("ucp_base", d), lambda: caja0(Lb, Wb, 0.42 * H).translate((-Lb / 2, -Wb / 2, -H)))
    e.add(k_base, "gris_motor", M, tag, f"Soporte UCP 2{d // 5:02d}")
    k_cuerpo = proto(("ucp_cuerpo", d), lambda: cil0(0.95 * H, Wb * 0.9).translate((0, 0, -Wb * 0.45)).rotate((0, 0, 0), (1, 0, 0), 90))
    e.add(k_cuerpo, "gris_motor", M, tag, "")
    k_alma = proto(("ucp_alma", d), lambda: caja0(0.9 * H, Wb * 0.8, 0.7 * H).translate((-0.45 * H, -0.4 * Wb, -H * 0.62)))
    e.add(k_alma, "gris_motor", M, tag, "")
    for x in (-J / 2, J / 2):
        e.bulon((x, 0, -H + 0.42 * H), (0, 0, 1), 14 if d <= 40 else 16, 50, M=M)
    k_grasa = proto(("engrasador",), lambda: [cil0(4, 10), hex0(10, 4).translate((0, 0, 10)), wp().sphere(5).translate((0, 0, 18))])
    e.add(k_grasa, "amarillo", M @ T(0, 0, 0.95 * H), tag, "")


def chumacera_ucf(e, d, M=I4, tag=""):
    """Soporte de brida cuadrada UCF. Local: eje según +Y; la brida apoya en el plano y = 0 del lado −Y."""
    A = 3.4 * d + 30
    J = 0.72 * A
    k_br = proto(("ucf_brida", d), lambda: caja0(A, 18, A).translate((-A / 2, -18, -A / 2)))
    e.add(k_br, "gris_motor", M, tag, f"Soporte de brida UCF 2{d // 5:02d}")
    k_c = proto(("ucf_cubo", d), lambda: cil0(0.32 * A, 0.45 * d + 20).rotate((0, 0, 0), (1, 0, 0), -90))
    e.add(k_c, "gris_motor", M, tag, "")
    for sx in (-1, 1):
        for sz in (-1, 1):
            e.bulon((sx * J / 2, 0, sz * J / 2), (0, 1, 0), 16, 40, M=M)


def tambor(e, D, ancho, L_eje, d_eje, M=I4, tag="", goma=False):
    """Tambor de cinta. Local: eje según +Y centrado en el origen."""
    k = proto(("tambor", D, ancho), lambda: tubo0(D / 2, D / 2 - 8, ancho).translate((0, 0, -ancho / 2)).rotate((0, 0, 0), (1, 0, 0), 90))
    e.add(k, "acero_pintado", M, tag, f"Tambor Ø{D} × {ancho}")
    k_disco = proto(("tambor_disco", D), lambda: cil0(D / 2 - 8, 12).rotate((0, 0, 0), (1, 0, 0), 90))
    for y in (-ancho / 2 + 20, ancho / 2 - 8):
        e.add(k_disco, "acero_pintado", M @ T(0, y, 0), tag, "")
    if goma:
        k_g = proto(("tambor_goma", D, ancho), lambda: tubo0(D / 2 + 8, D / 2, ancho - 20).translate((0, 0, -(ancho - 20) / 2)).rotate((0, 0, 0), (1, 0, 0), 90))
        e.add(k_g, "goma", M, tag, "Revestimiento de goma romboidal 8 mm")
    k_eje = proto(("eje", d_eje, L_eje), lambda: cil0(d_eje / 2, L_eje).translate((0, 0, -L_eje / 2)).rotate((0, 0, 0), (1, 0, 0), 90))
    e.add(k_eje, "acero", M, tag, f"Eje Ø{d_eje} SAE 1045")


def terna(e, B, M=I4, D=89, ang=20.0, tag=""):
    """Terna de rodillos portantes. Local: banda según +X, centro de la banda en el origen (z = parte superior del
    rodillo central); base en z = −(D/2 + 120)."""
    l = round((B + 100) / 3)
    k_r = proto(("rodillo", D, l), lambda: [tubo0(D / 2, D / 2 - 3.5, l - 16).translate((0, 0, 8)), cil0(10, l)])
    e.add(k_r, "galv", M @ T(0, -l / 2, -D / 2) @ Rx(-90), tag, f"Rodillo Ø{D} × {l}")
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    for s_ in (-1, 1):
        p0 = np.array([0.0, s_ * (l / 2 + 10), -D / 2 + 4])
        p1 = p0 + l * np.array([0.0, s_ * ca, sa])
        e.add(k_r, "galv", M @ alinear(p0, p1), tag, "")
    ancho = B + 260
    k_base = proto(("terna_base", B), lambda: caja0(60, ancho, 6).translate((-30, -ancho / 2, 0)))
    e.add(k_base, "galv", M @ T(0, 0, -D / 2 - 130), tag, "Bastidor de terna")
    k_sop = proto(("terna_sop", B), lambda: caja0(50, 6, 130))
    for y in (-l / 2 - 6, l / 2):
        e.add(k_sop, "galv", M @ T(-25, y, -D / 2 - 124), tag, "")
    k_ext = proto(("terna_ext", B), lambda: caja0(50, 6, 130 + l * math.sin(math.radians(ang)) + 20))
    for y in (-ancho / 2 + 4, ancho / 2 - 10):
        e.add(k_ext, "galv", M @ T(-25, y, -D / 2 - 124), tag, "")


def rodillo_retorno(e, B, M=I4, D=89, tag=""):
    """Rodillo de retorno colgado. Local: banda según +X; parte superior del rodillo en z = 0."""
    l = B + 150
    k = proto(("rodillo_ret", D, l), lambda: [tubo0(D / 2, D / 2 - 3.5, l - 16).translate((0, 0, 8)), cil0(10, l)])
    e.add(k, "galv", M @ T(0, -l / 2, -D / 2) @ Rx(-90), tag, f"Rodillo de retorno Ø{D} × {l}")
    k_s = proto(("ret_sop", D), lambda: caja0(40, 6, 110))
    for y in (-l / 2 - 8, l / 2 + 2):
        e.add(k_s, "galv", M @ T(-20, y, -D / 2 - 5), tag, "")


# ===================================================================================== estructura auxiliar
def baranda(e, pts, M=I4, alto=1100, tag="", paso=1500, rodapie=True, color="amarillo"):
    """Baranda reglamentaria (Dec. 351/79): pasamanos a 1,10 m, travesaño intermedio, rodapié de 0,15 m y parantes
    cada 1,5 m como máximo. `pts` son puntos (mm) del borde, a la altura del piso."""
    pts = [np.asarray(p, float) for p in pts]
    for a, b in zip(pts, pts[1:]):
        L = np.linalg.norm(b - a)
        n = max(1, math.ceil(L / paso))
        for i in range(n + 1):
            p = a + (b - a) * i / n
            e.barra(p, p + (0, 0, alto), "CHS 42", color, cod=tag, nom="Baranda", M=M)
        e.barra(a + (0, 0, alto), b + (0, 0, alto), "CHS 42", color, cod=tag, nom="Baranda", M=M)
        e.barra(a + (0, 0, alto / 2), b + (0, 0, alto / 2), "CHS 33", color, cod=tag, nom="Baranda", M=M)
        if rodapie:
            d = (b - a) / L
            nrm = np.array([-d[1], d[0], 0])
            e.barra(a + (0, 0, 75), b + (0, 0, 75), "FB 150x6", color, up=tuple(nrm), cod=tag, nom="Rodapié", M=M)


def plataforma(e, x0, y0, x1, y1, z, M=I4, tag="", perfil="UPN 140", baranda_lados="NSEO", color="amarillo",
               abertura=None):
    """Plataforma con piso de rejilla electrosoldada 30 × 100 (ESR 25 mm) sobre marco de UPN. z = nivel de piso.
    `abertura`: (lado, desde, hasta) sin baranda para la llegada de la escalera."""
    e.caja(x0, y0, z - 30, x1, y1, z, "rejilla", tag, "Piso de rejilla electrosoldada", M=M)
    h = 140
    for (a, b) in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
        e.barra((a[0], a[1], z - 30 - h / 2), (b[0], b[1], z - 30 - h / 2), perfil, "estructura", up=(0, 0, 1), cod=tag,
                nom="Marco de plataforma", M=M)
    lados = {"S": [(x0, y0, z), (x1, y0, z)], "N": [(x0, y1, z), (x1, y1, z)], "O": [(x0, y0, z), (x0, y1, z)],
             "E": [(x1, y0, z), (x1, y1, z)]}
    for l in baranda_lados:
        p = lados[l]
        if abertura and abertura[0] == l:
            a, b = np.asarray(p[0], float), np.asarray(p[1], float)
            Lt = np.linalg.norm(b - a)
            u = (b - a) / Lt
            if abertura[1] > 50:
                baranda(e, [a, a + u * abertura[1]], M, tag=tag, color=color)
            if Lt - abertura[2] > 50:
                baranda(e, [a + u * abertura[2], b], M, tag=tag, color=color)
        else:
            baranda(e, p, M, tag=tag, color=color)


def escalera(e, p_pie, p_llegada, ancho=800, M=I4, tag="", color="amarillo"):
    """Escalera de servicio (ángulo ≤ 45°): zancas UPN 160, peldaños de rejilla cada ≤ 200 mm y pasamanos a ambos lados.
    p_pie y p_llegada son los puntos medios del arranque y la llegada (mm)."""
    p0, p1 = np.asarray(p_pie, float), np.asarray(p_llegada, float)
    dh = p1[2] - p0[2]
    n = max(2, math.ceil(dh / 190))
    d = p1 - p0
    dir_h = np.array([d[0], d[1], 0.0])
    Lh = np.linalg.norm(dir_h)
    u = dir_h / Lh
    v = np.array([-u[1], u[0], 0.0])
    for s in (-1, 1):
        a = p0 + v * s * ancho / 2
        b = p1 + v * s * ancho / 2
        e.barra(a, b, "UPN 160", "estructura", up=tuple(v * s), cod=tag, nom="Zanca de escalera", M=M)
        e.barra(a + (0, 0, 900), b + (0, 0, 900), "CHS 42", color, cod=tag, nom="Pasamanos", M=M)
        for t in (0.0, 0.5, 1.0):
            p = a + (b - a) * t
            e.barra(p, p + (0, 0, 900), "CHS 42", color, cod=tag, nom="Parante", M=M)
    for i in range(1, n):
        c = p0 + d * i / n
        e.caja_rot((c[0], c[1], c[2] - 15), (240, ancho - 40, 30), math.degrees(math.atan2(u[1], u[0])), "rejilla", tag,
                   "Peldaño de rejilla", M=M)


def escalera_marinera(e, p_pie, alto, M=I4, tag="", jaula=True, frente=(1, 0, 0)):
    """Escalera marinera con jaula desde 2,2 m (Dec. 351/79). p_pie al pie, `frente` hacia donde se sube mirando."""
    p0 = np.asarray(p_pie, float)
    f = np.asarray(frente, float) / np.linalg.norm(frente)
    v = np.array([-f[1], f[0], 0])
    for s in (-1, 1):
        a = p0 + v * s * 225
        e.barra(a, a + (0, 0, alto + 1000), "FB 50x6", "amarillo", up=tuple(f), cod=tag, nom="Larguero de escalera", M=M)
    for k in range(1, int(alto / 300) + 1):
        c = p0 + (0, 0, k * 300)
        e.barra(c - v * 225, c + v * 225, "RB 20", "amarillo", cod=tag, nom="Peldaño", M=M)
    if jaula and alto > 2500:
        for z in np.arange(2200, alto + 900, 900):
            for ang in range(0, 181, 30):
                pass
            c = p0 + (0, 0, z) - f * 350
            arco = [c + 350 * (math.cos(math.radians(t)) * v + math.sin(math.radians(t)) * (-f)) for t in range(0, 181, 30)]
            for a, b in zip(arco, arco[1:]):
                e.barra(a, b, "FB 50x6", "amarillo", up=(0, 0, 1), cod=tag, nom="Aro de jaula", M=M)
        for t in (0, 60, 120, 180):
            c = p0 - f * 350
            a = c + 350 * (math.cos(math.radians(t)) * v + math.sin(math.radians(t)) * (-f))
            e.barra(a + (0, 0, 2200), a + (0, 0, alto + 900), "FB 30x5", "amarillo", up=tuple(f), cod=tag, nom="Fleje de jaula", M=M)


def columna(e, x, y, z0, z1, perfil, M=I4, tag="", placa=(300, 300, 16), anclajes=4, d_anclaje=20, dado=True,
            rot=0.0, color="estructura"):
    """Columna con placa base, anclajes con tuerca y arandela, y dado de hormigón (fundación representativa)."""
    px, py, pt = placa
    if dado:
        e.caja(x - px / 2 - 100, y - py / 2 - 100, z0 - 600, x + px / 2 + 100, y + py / 2 + 100, z0 - 20, "hormigon",
               tag, "Dado de fundación (representativo)", M=M)
        e.caja(x - px / 2 - 20, y - py / 2 - 20, z0 - 20, x + px / 2 + 20, y + py / 2 + 20, z0, "revoque", tag,
               "Mortero de nivelación", M=M)
    e.caja_rot((x, y, z0 + pt / 2), (px, py, pt), rot, "estructura", tag, f"Placa base {px}×{py}×{pt}", M=M)
    e.barra((x, y, z0 + pt), (x, y, z1), perfil, color, up=(math.cos(math.radians(rot)), math.sin(math.radians(rot)), 0),
            cod=tag, nom=f"Columna {perfil}", M=M)
    if anclajes:
        c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for (ax, ay) in ((-1, -1), (1, -1), (1, 1), (-1, 1))[:anclajes]:
            ox, oy = ax * (px / 2 - 40), ay * (py / 2 - 40)
            e.bulon((x + ox * c - oy * s, y + ox * s + oy * c, z0 + pt), (0, 0, 1), d_anclaje, 300, M=M, nom="Anclaje químico")
    # cartelas
    k = proto(("cartela", px), lambda: wp().polyline([(0, 0), (px * 0.38, 0), (0, px * 0.38)]).close().extrude(10)
              .rotate((0, 0, 0), (1, 0, 0), 90))
    for ang in (0, 90, 180, 270):
        e.add(k, "estructura", M @ T(x, y, z0 + pt) @ Rz(ang + rot) @ T(30, 5, 0), tag, "")


def bandeja(e, p0, p1, ancho=300, M=I4, tag="", alto_ala=60, paso=300):
    """Bandeja portacables tipo escalera (chapa galvanizada): alas laterales y travesaños. Local de colocación:
    de p0 a p1, horizontal o vertical."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    if L < 50:
        return
    u = d / L
    up = np.array([0, 0, 1.0]) if abs(u[2]) < 0.9 else np.array([1.0, 0, 0])
    v = np.cross(up, u)
    v /= np.linalg.norm(v)
    for s in (-1, 1):
        a = p0 + v * s * ancho / 2
        e.barra(a, a + d, "C 80" if alto_ala >= 80 else "L 50", "galv", up=tuple(-v * s), cod=tag, nom="Ala de bandeja", M=M)
    n = int(L // paso)
    for i in range(1, n):
        c = p0 + u * i * paso
        e.barra(c - v * ancho / 2, c + v * ancho / 2, "L 30", "galv", up=tuple(up), cod=tag, nom="Travesaño de bandeja", M=M)


def cables_en_bandeja(e, p0, p1, n=4, ancho=300, M=I4, tag=""):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    d = p1 - p0
    L = np.linalg.norm(d)
    if L < 50:
        return
    u = d / L
    up = np.array([0, 0, 1.0]) if abs(u[2]) < 0.9 else np.array([1.0, 0, 0])
    v = np.cross(up, u)
    v /= np.linalg.norm(v)
    for i in range(n):
        off = (i - (n - 1) / 2) * min(40, (ancho - 60) / max(1, n))
        a = p0 + v * off + up * 18
        e.cil(a, a + d, 9 + (i % 3) * 3, "cable", tag, "Cable", M=M)


def cano(e, pts, d=25, M=I4, tag="", mat="galv"):
    """Caño rígido de acero galvanizado (conducto) por una poligonal, con curvas representadas por esferas."""
    e.polilinea([np.asarray(p, float) for p in pts], d / 2, mat, tag, "Caño rígido", M=M)


def caja_paso(e, c, n=(1, 0, 0), dims=(200, 200, 120), M=I4, tag=""):
    a, b, h = dims
    k = proto(("caja_paso", a, b, h), lambda: [caja0(a, b, h).translate((-a / 2, -b / 2, 0)),
                                              caja0(a + 10, b + 10, 8).translate((-a / 2 - 5, -b / 2 - 5, h))])
    e.add(k, "plastico_gris", M @ alinear(c, np.add(c, n)), tag, "Caja de paso IP65")


def tablero(e, x, y, z, ancho, alto, prof, rotz=0.0, M=I4, tag="", nombre="", zocalo=100, color="tablero"):
    """Gabinete de tablero (tipo Rittal VX) con zócalo, puerta, manija y bisagras. Local: frente hacia −Y antes de rotar."""
    G = M @ T(x, y, z) @ Rz(rotz)
    e.caja(-ancho / 2, -prof / 2, 0, ancho / 2, prof / 2, zocalo, "negro", tag, "Zócalo", M=G)
    e.caja(-ancho / 2, -prof / 2, zocalo, ancho / 2, prof / 2, zocalo + alto, color, tag, nombre or f"Tablero {tag}", M=G)
    e.caja(-ancho / 2 + 15, -prof / 2 - 18, zocalo + 15, ancho / 2 - 15, -prof / 2, zocalo + alto - 15, color, tag,
           "Puerta", M=G)
    e.caja(ancho / 2 - 70, -prof / 2 - 45, zocalo + alto * 0.48, ancho / 2 - 45, -prof / 2 - 18, zocalo + alto * 0.62,
           "negro", tag, "Manija", M=G)
    for zz in (0.12, 0.88):
        e.caja(-ancho / 2 + 5, -prof / 2 - 25, zocalo + alto * zz, -ancho / 2 + 20, -prof / 2 - 10, zocalo + alto * zz + 60,
               "negro", tag, "Bisagra", M=G)
    e.caja(-ancho / 2 + 60, -prof / 2 - 20, zocalo + alto - 140, -ancho / 2 + 260, -prof / 2 - 18, zocalo + alto - 60,
           "aluminio", tag, "Chapa de identificación", M=G)
    e.caja(-80, -prof / 2 - 21, zocalo + alto - 330, 80, -prof / 2 - 18, zocalo + alto - 170, "amarillo", tag,
           "Cartel de riesgo eléctrico", M=G)
    return G


def botonera(e, c, n=(0, -1, 0), M=I4, tag="", paro=True):
    """Botonera local de comando con parada de emergencia (hongo rojo) en caja amarilla."""
    G = M @ alinear(c, np.add(c, n))
    k = proto(("botonera",), lambda: caja0(110, 180, 90).translate((-55, -90, 0)))
    e.add(k, "sensor_amarillo", G, tag, "Botonera local con parada de emergencia")
    if paro:
        k_h = proto(("hongo",), lambda: [cil0(14, 20), wp().sphere(22).translate((0, 0, 24))])
        e.add(k_h, "rojo", G @ T(0, 40, 90), tag, "")
        k_b = proto(("pulsador",), lambda: cil0(14, 14))
        e.add(k_b, "verde", G @ T(0, -10, 90), tag, "")
        e.add(k_b, "negro", G @ T(0, -55, 90), tag, "")


def seccionador(e, c, n=(0, -1, 0), M=I4, tag=""):
    """Interruptor-seccionador de seguridad junto al motor (bloqueable con candado)."""
    G = M @ alinear(c, np.add(c, n))
    k = proto(("seccionador",), lambda: caja0(150, 200, 110).translate((-75, -100, 0)))
    e.add(k, "plastico_gris", G, tag, "Seccionador de seguridad bloqueable")
    k_m = proto(("secc_manija",), lambda: [cil0(30, 20), caja0(20, 90, 22).translate((-10, -20, 20))])
    e.add(k_m, "rojo", G @ T(0, 0, 110), tag, "")
    k_f = proto(("secc_fondo",), lambda: cil0(46, 4))
    e.add(k_f, "amarillo", G @ T(0, 0, 108), tag, "")


# ===================================================================================== instrumentos
def sensor(e, tipo, c, n=(0, 0, 1), M=I4, tag=""):
    """Instrumentos de campo. c: punto de montaje, n: normal saliente (hacia afuera del equipo)."""
    G = M @ alinear(c, np.add(c, n))
    if tipo == "rtd":           # termorresistencia con vaina y cabezal
        k = proto(("rtd",), lambda: [cil0(6, 220).translate((0, 0, -220)), cil0(11, 70), cil0(28, 55).translate((0, 0, 70)),
                                      cil0(30, 10).translate((0, 0, 125))])
        e.add(k, "aluminio", G, tag, f"Termorresistencia Pt100 {tag}")
    elif tipo == "humedad":     # transmisor de humedad y temperatura
        k = proto(("hum",), lambda: [cil0(9, 200).translate((0, 0, -200)), caja0(90, 70, 130).translate((-45, -35, 0))])
        e.add(k, "plastico_blanco", G, tag, f"Transmisor de humedad {tag}")
    elif tipo == "presion":
        k = proto(("pres",), lambda: [cil0(10, 60), cil0(40, 80).translate((0, 0, 60)), cil0(42, 12).translate((0, 0, 140))])
        e.add(k, "inox", G, tag, f"Transmisor de presión {tag}")
    elif tipo == "radar":       # medidor de nivel por radar con antena de bocina
        k = proto(("radar",), lambda: [cono0(70, 30, 160).translate((0, 0, -160)), cil0(55, 40), cil0(60, 140).translate((0, 0, 40)),
                                       cil0(64, 12).translate((0, 0, 180))])
        e.add(k, "aluminio", G, tag, f"Medidor de nivel por radar {tag}")
    elif tipo == "horquilla":   # interruptor de nivel vibratorio
        k = proto(("horq",), lambda: [cil0(12, 140).translate((-14, 0, -140)), cil0(12, 140).translate((14, 0, -140)),
                                      cil0(24, 60), cil0(40, 70).translate((0, 0, 60))])
        e.add(k, "inox", G, tag, f"Interruptor de nivel vibratorio {tag}")
    elif tipo == "velocidad":   # sensor inductivo de velocidad cero con soporte
        k = proto(("vel",), lambda: [cil0(15, 110), hex0(36, 8).translate((0, 0, 30)), caja0(60, 8, 120).translate((-30, -4, -120))])
        e.add(k, "sensor", G, tag, f"Sensor de velocidad cero {tag}")
    elif tipo == "desvio":      # interruptor de desvío de banda (rodillo vertical)
        k = proto(("desv",), lambda: [caja0(140, 110, 170).translate((-70, -55, 0)), cil0(14, 200).translate((0, 0, 170))])
        e.add(k, "sensor_amarillo", G, tag, f"Interruptor de desvío de banda {tag}")
    elif tipo == "tiron":       # interruptor de parada de emergencia por cable
        k = proto(("tiron",), lambda: [caja0(160, 120, 200).translate((-80, -60, 0)), cil0(30, 30).translate((0, 0, 200)),
                                       caja0(200, 14, 30).translate((-100, -7, 210))])
        e.add(k, "sensor_amarillo", G, tag, f"Interruptor de parada por cable {tag}")
    elif tipo == "atasco":      # interruptor de atascamiento de chute (péndulo)
        k = proto(("atasco",), lambda: [cil0(40, 120), cil0(14, 380).translate((0, 0, -380)), cil0(30, 90).translate((0, 0, -470))])
        e.add(k, "sensor", G, tag, f"Detector de atascamiento {tag}")
    elif tipo == "celda":       # celda de carga
        k = proto(("celda",), lambda: [caja0(160, 160, 30).translate((-80, -80, 0)), cil0(45, 70).translate((0, 0, 30)),
                                       caja0(160, 160, 30).translate((-80, -80, 100))])
        e.add(k, "inox", G, tag, f"Celda de carga {tag}")
    elif tipo == "llama":       # detector de llama UV/IR
        k = proto(("llama",), lambda: [cil0(20, 80), cil0(38, 120).translate((0, 0, 80)), cil0(26, 8).translate((0, 0, 200))])
        e.add(k, "rojo", G, tag, f"Detector de llama {tag}")
    elif tipo == "vibracion":
        k = proto(("vib",), lambda: [hex0(28, 12), cil0(12, 60).translate((0, 0, 12))])
        e.add(k, "inox", G, tag, f"Sensor de vibración {tag}")
    elif tipo == "final":       # final de carrera
        k = proto(("final",), lambda: [caja0(60, 40, 90).translate((-30, -20, 0)), cil0(5, 60).translate((0, 0, 90))])
        e.add(k, "sensor", G, tag, f"Final de carrera {tag}")
    elif tipo == "baliza":      # baliza luminosa y sirena de arranque
        k = proto(("baliza",), lambda: [cil0(35, 60), cil0(30, 70).translate((0, 0, 60))])
        e.add(k, "naranja", G, tag, f"Baliza y sirena de prearranque {tag}")
    else:
        raise ValueError(tipo)


def placa(e, c, n, ancho, alto, mat="aluminio", M=I4, tag="", nom="Placa de identificación"):
    G = M @ alinear(c, np.add(c, n))
    e.caja(-ancho / 2, -alto / 2, 0, ancho / 2, alto / 2, 2, mat, tag, nom, M=G)
