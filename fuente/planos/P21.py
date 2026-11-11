"""P21 - Limpieza y desinfección de vehículos y personal (E1, E2).

Redibujo vectorial de la lámina 21 (Rev. D, sin cambios de contenido).
Geometría del modelo 3D Rev. D (visor.html, __revDBuild, partes E1 y E2), en m:
vado sanitario xa..xb = 4,1..7,5 / y = -16,9..-12,2; arco de aspersión en y = -14,6;
IBC y bomba M17 al Oeste del camino; hidrolavadora M16 junto al portón P1 de la nave (x = 0).
"""
import math

from lamina_secadora import (COL, cota, exportar_lamina, factor, flecha, lamina, linea, poli, rayado, rect,
                             relleno, relleno_circulo, relleno_rect, subtitulo, t, tabla, titulo_vista, tn,
                             circulo)

AGUA = (40, 140, 200)
SOLUCION = (168, 213, 198)
VERDE_TERRENO = (232, 241, 224)
PAVIMENTO = (216, 216, 216)
ROJO_INC = (200, 16, 46)


def discontinua(msp, pts, capa="CONTORNO", color=None, lw=None, d=1.6, g=1.0):
    """Polilínea de trazos hecha con segmentos (se ve igual en DXF, PDF y PNG)."""
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        s = 0.0
        while s < L - 1e-6:
            e = min(s + d, L)
            linea(msp, (ax + (bx - ax) * s / L, ay + (by - ay) * s / L),
                  (ax + (bx - ax) * e / L, ay + (by - ay) * e / L), capa, color, lw)
            s = e + g


def cota_txt(msp, p1, p2, distancia, escala, valor, texto_en):
    """Cota alineada (como lamina_a3.cota) con el texto corrido a texto_en (mm de papel)."""
    dim = msp.add_aligned_dim(p1=p1, p2=p2, distance=distancia, dimstyle="IRAM", text=valor,
                              override={"dimlfac": 1.0 / escala}, dxfattribs={"layer": "COTAS"})
    dim.set_location(texto_en, leader=False)
    dim.render()
    return dim


def caja(msp, x0, y0, x1, y1, rgb=None, capa="CONTORNO", lw=None):
    if rgb:
        relleno_rect(msp, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), rgb)
    rect(msp, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), capa, lw=lw)


# ---------------------------------------------------------------- A - planta del acceso 1:100
def planta(msp):
    titulo_vista(msp, "A - PLANTA DEL ACCESO: VADO SANITARIO Y ARCO - ESC. 1:100", 26, 279.2, 2.9)
    k = factor("1:100")

    def P(x, y):
        return (112.14 + (x - 4.1) * 10.0, 260.88 + (y + 12.2) * 10.0)

    def R(x0, y0, x1, y1, rgb=None, capa="CONTORNO", lw=None):
        a, b = P(x0, y0), P(x1, y1)
        caja(msp, a[0], a[1], b[0], b[1], rgb, capa, lw)
        return a, b

    # terreno y calle R1
    a, b = P(-3.53, -18.59), P(9.48, -10.79)
    relleno_rect(msp, a[0], a[1], b[0], b[1], VERDE_TERRENO)
    c0, c1 = P(0.49, -18.59), P(7.5, -10.79)
    relleno_rect(msp, c0[0], c0[1], c1[0], c1[1], PAVIMENTO)
    for x in (0.49, 7.5):
        linea(msp, P(x, -18.59), P(x, -10.79), "CONTORNO", lw=50)
    t(msp, "calle R1 (acceso)", P(0.99, -11.32), 1.8, "MIDDLE_LEFT")
    # báscula 30
    a, b = R(4.25, -18.59, 7.23, -16.99, (150, 166, 166))
    tn(msp, "báscula 30", ((a[0] + b[0]) / 2, a[1] + 1.8), 1.9, "MIDDLE_CENTER")
    # vado sanitario: losa y solución desinfectante
    R(4.1, -16.9, 7.5, -12.2, (226, 226, 226), lw=70)
    R(4.3, -16.0, 7.3, -13.1, SOLUCION, "FINO")
    for yy in (-16.0, -13.1):           # fin de las rampas
        discontinua(msp, [P(4.1, yy), P(4.3, yy)], "FINO", None, 25, 0.8, 0.5)
        discontinua(msp, [P(7.3, yy), P(7.5, yy)], "FINO", None, 25, 0.8, 0.5)
    t(msp, "solución\ndesinfectante", P(6.65, -13.75), 1.8, "MIDDLE_CENTER")
    # sentidos de circulación
    flecha(msp, P(5.19, -11.25), P(5.19, -18.25), "CONTORNO", color=(90, 90, 90), tam=2.4, lw=35)
    flecha(msp, P(5.99, -18.25), P(5.99, -11.25), "CONTORNO", color=(90, 90, 90), tam=2.4, lw=35)
    # tanque de desinfectante (IBC 1 m³) y bomba M17 sobre platea
    R(-2.6, -17.3, -0.6, -15.3, (238, 238, 238))
    R(-2.4, -17.05, -1.4, -16.15, (210, 230, 225), "FINO")
    t(msp, "IBC 1 m³", P(-2.2, -15.75), 1.8, "MIDDLE_LEFT")
    # cañería de la bomba al arco
    poli(msp, [P(-0.9, -16.1), P(-0.9, -14.62), P(3.75, -14.62)], "CONTORNO", color=AGUA, lw=35)
    R(-1.1, -16.3, -0.7, -15.9, (110, 125, 140))
    t(msp, "M17", (P(-0.9, 0)[0] - 1.0, P(0, -14.62)[1] + 0.4), 1.8, "BOTTOM_RIGHT")
    # arco de aspersión (14 boquillas: 7 por lado del caño superior) y sensor de paso
    linea(msp, P(3.75, -14.62), P(7.85, -14.62), "CONTORNO", color=COL["salida"], lw=70)
    for x in (3.75, 7.85):
        a = P(x, -14.62)
        relleno_rect(msp, a[0] - 0.65, a[1] - 0.65, a[0] + 0.65, a[1] + 0.65, (80, 80, 80))
    for i in range(7):
        relleno_circulo(msp, P(4.4 + i * 2.8 / 6, -14.73), 0.32, AGUA)
    a = P(7.95, -14.62)
    relleno_rect(msp, a[0] - 0.1, a[1] - 0.8, a[0] + 0.7, a[1] + 0.8, COL["azul"])
    t(msp, "sensor\nde paso", (a[0] + 1.6, a[1] + 1.0), 1.8, "BOTTOM_LEFT")
    t(msp, "15 cm", P(6.65, -14.98), 1.8, "MIDDLE_CENTER")
    # semáforo existente y matafuego 23
    c = P(3.32, -16.09)
    relleno_circulo(msp, c, 2.1, (45, 45, 45))
    circulo(msp, c, 2.1, "FINO")
    t(msp, "semáforo existente", (c[0] - 4.5, c[1] - 4.0), 1.8, "TOP_CENTER")
    c = P(-1.6, -18.0)
    relleno(msp, [(c[0] - 1.4, c[1] - 1.2), (c[0] + 1.4, c[1] - 1.2), (c[0], c[1] + 1.4)], ROJO_INC)
    tn(msp, "23", (c[0] + 2.0, c[1] - 0.6), 1.8, "MIDDLE_LEFT", color=ROJO_INC)
    # cotas
    cota_txt(msp, P(4.1, -12.2), P(7.5, -12.2), 4.2, k, "3.400", (P(6.75, 0)[0], P(0, -12.2)[1] + 5.6))
    cota_txt(msp, P(7.5, -16.9), P(7.5, -12.2), -18.0, k, "4.700", (P(7.5, 0)[0] + 16.6, P(0, -16.0)[1]))
    cota_txt(msp, P(3.75, -14.62), P(7.85, -14.62), -9.0, k, "4.100", (P(6.65, 0)[0], P(0, -14.62)[1] - 7.6))


# ---------------------------------------------------------------- B - corte longitudinal 1:50 (alturas x 2)
def corte_vado(msp):
    titulo_vista(msp, "B - CORTE LONGITUDINAL DEL VADO - ESC. 1:50 (alturas × 2)", 26, 180, 2.7)

    def P(x, z):
        return (35.91 + x * 20.0, 159.03 + z * 40.0)

    perfil = [(0, 0), (0.9, -0.2), (3.8, -0.2), (4.7, 0)]
    # losa de H°A° (rayado) bajo el perfil
    losa = [P(*p) for p in perfil] + [P(4.7, -0.4), P(0, -0.4)]
    rayado(msp, losa, escala=0.45)
    poli(msp, [P(0, 0), P(0, -0.4), P(4.7, -0.4), P(4.7, 0)], "CONTORNO", lw=35)
    # solución desinfectante (0,15 m)
    agua = [P(0.225, -0.05), P(0.9, -0.2), P(3.8, -0.2), P(4.475, -0.05)]
    relleno(msp, agua, SOLUCION)
    discontinua(msp, [P(0.225, -0.05), P(4.475, -0.05)], "FINO", AGUA, 35, 1.6, 1.0)
    t(msp, "solución desinfectante 0,15 m", P(2.35, -0.125), 1.8, "MIDDLE_CENTER")
    # terreno y perfil del vado
    poli(msp, [P(-0.3, 0)] + [P(*p) for p in perfil] + [P(5.0, 0)], "CONTORNO", lw=70)
    t(msp, "rampa 1:4,5", P(0.45, 0.095), 1.8, "BOTTOM_CENTER")
    t(msp, "rampa 1:4,5", P(4.25, 0.095), 1.8, "BOTTOM_CENTER")
    # sumidero
    c = P(2.35, -0.24)
    relleno_circulo(msp, c, 0.9, (255, 255, 255))
    circulo(msp, c, 0.9, "CONTORNO")
    linea(msp, (c[0] + 0.6, c[1] - 0.7), (c[0] + 4.0, 138.6), "FINO")
    t(msp, "sumidero con válvula de vaciado\n(a bidones, no al biodigestor)", (c[0] + 5.0, 138.6), 1.8, "TOP_LEFT")
    t(msp, "losa H°A° e = 20 cm\nsobre base granular", (35.91, 138.6), 1.8, "TOP_LEFT")
    linea(msp, (40.0, 139.2), (44.0, P(0, -0.33)[1]), "FINO")


# ---------------------------------------------------------------- C - arco de aspersión 1:100
def arco_aspersion(msp):
    titulo_vista(msp, "C - ARCO DE ASPERSIÓN - ESC. 1:100", 166.1, 279.2, 2.9)
    k = factor("1:100")

    def P(x, z):
        return (195.0 + x * 10.0, 219.1 + z * 10.0)

    # pórtico galvanizado
    for s in (-1, 1):
        a, b = P(s * 2.05 - 0.16, 0), P(s * 2.05 + 0.16, 4.84)
        caja(msp, a[0], a[1], b[0], b[1], (190, 190, 190), lw=35)
    a, b = P(-2.21, 4.84), P(2.21, 5.0)
    caja(msp, a[0], a[1], b[0], b[1], (190, 190, 190), lw=35)
    # cañería de aspersión y boquillas
    poli(msp, [P(-1.9, 0.4), P(-1.9, 4.75), P(1.9, 4.75), P(1.9, 0.4)], "CONTORNO", color=AGUA, lw=35)
    for i in range(7):
        x = -1.4 + i * 2.8 / 6
        poli(msp, [P(x, 4.75), P(x - 0.25, 4.2), P(x + 0.25, 4.2)], "FINO", cerrada=True, color=AGUA)
    for s in (-1, 1):
        for z in (0.8, 1.9, 3.0, 4.1):
            poli(msp, [P(s * 1.9, z), P(s * 1.45, z + 0.22), P(s * 1.45, z - 0.22)], "FINO", cerrada=True, color=AGUA)
    # gálibo del camión
    discontinua(msp, [P(-1.4, 0), P(-1.4, 3.3), P(1.4, 3.3), P(1.4, 0)], "FINO", (110, 110, 110), 35, 1.4, 0.9)
    t(msp, "gálibo camión", P(0, 1.6), 1.8, "MIDDLE_CENTER", color=(110, 110, 110))
    linea(msp, P(-2.5, 0), P(2.6, 0), "CONTORNO", lw=70)
    cota(msp, P(2.21, 0), P(2.21, 5.0), distancia=-3.0, escala=k, valor="4.900")
    cota(msp, P(-2.05, 0), P(2.05, 0), distancia=-4.5, escala=k, valor="4.100")


# ---------------------------------------------------------------- D - lavadero en P1 1:200
def lavadero(msp):
    titulo_vista(msp, "D - LAVADERO EN P1 - ESC. 1:200", 148.0, 184.0, 2.9)

    def P(x, y):
        return (199.92 + x * 5.0, 52.3 + y * 5.0)

    def R(x0, y0, x1, y1, rgb=None, capa="CONTORNO", lw=None):
        a, b = P(x0, y0), P(x1, y1)
        caja(msp, a[0], a[1], b[0], b[1], rgb, capa, lw)
        return a, b

    a, b = P(-10, 5.55), P(1.5, 25.0)
    relleno_rect(msp, a[0], a[1], b[0], b[1], VERDE_TERRENO)
    a, b = R(-9.0, 6.05, 0, 24.04, PAVIMENTO, lw=35)
    t(msp, "playón PL1", P(-4.5, 23.15), 1.8, "MIDDLE_CENTER")
    # muro Oeste de la nave con el portón P1 (12,6 a 16,6 m)
    linea(msp, P(0.1, 5.55), P(0.1, 12.6), "CONTORNO", lw=140)
    linea(msp, P(0.1, 16.6), P(0.1, 25.0), "CONTORNO", lw=140)
    tn(msp, "P1", P(0.85, 14.6), 2.0, "MIDDLE_CENTER", rotacion=90)
    # hidrolavadora M16 y manguera
    R(-0.85, 19.3, -0.35, 20.7, COL["azul"], "FINO")
    tn(msp, "M16", P(-2.2, 21.56), 1.9, "MIDDLE_CENTER")
    discontinua(msp, [P(-0.84, 19.33), P(-2.98, 16.6)], "FINO", COL["azul"], 35, 1.0, 0.6)
    # camión lavando
    a, b = P(-7.2, 13.32), P(-0.97, 15.8)
    discontinua(msp, [a, (b[0], a[1]), b, (a[0], b[1]), a], "CONTORNO", None, 35, 1.4, 0.9)
    t(msp, "camión lavando", ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), 1.8, "MIDDLE_CENTER")
    # cámara de lixiviados 26 y rejilla desarenadora
    R(-2.0, 9.88, -0.5, 11.39, (226, 236, 244))
    tn(msp, "26", P(-1.3, 12.15), 1.9, "MIDDLE_CENTER")
    a, b = R(-7.5, 8.6, -1.0, 9.0, (205, 205, 205), "CONTORNO", 25)
    for f in (0.3, 0.55, 0.8):
        linea(msp, (a[0], a[1] + (b[1] - a[1]) * f), (b[0], a[1] + (b[1] - a[1]) * f), "FINO", (120, 120, 120))
    t(msp, "rejilla desarenadora", P(-4.5, 7.73), 1.8, "MIDDLE_CENTER")
    flecha(msp, P(-4.2, 9.25), P(-1.89, 10.21), "CONTORNO", color=AGUA, tam=1.8, lw=35)


# ---------------------------------------------------------------- E - pediluvio y lavabotas 1:50
def pediluvio(msp):
    titulo_vista(msp, "E - PEDILUVIO Y LAVABOTAS (PP1) - ESC. 1:50", 250.1, 279.2, 2.9)
    k = factor("1:50")
    K = k * 1000.0
    cx, cy = 286.0, 240.0
    a, b = (cx - 0.6 * K, cy - 0.45 * K), (cx + 0.6 * K, cy + 0.45 * K)
    caja(msp, a[0], a[1], b[0], b[1], (236, 236, 236), lw=50)
    caja(msp, a[0] + 0.05 * K, a[1] + 0.05 * K, b[0] - 0.05 * K, b[1] - 0.05 * K, SOLUCION, "FINO")
    flecha(msp, (cx, b[1] + 8.0), (cx, b[1] + 0.8), "CONTORNO", color=(90, 90, 90), tam=1.8, lw=35)
    t(msp, "acceso del personal → vestuario (zona sucia / limpia)", (cx + 2.0, b[1] + 6.0), 1.8, "MIDDLE_LEFT")
    cota(msp, a, (b[0], a[1]), distancia=-5.0, escala=k, valor="1.200")
    cota(msp, a, (a[0], b[1]), distancia=5.0, escala=k, valor="900")
    t(msp, "pediluvio 1.200 × 900 × 60 mm", (cx, a[1] - 11.5), 1.8, "MIDDLE_CENTER")
    lx, ly = 335.0, 240.0
    a, b = (lx - 0.3 * K, ly - 0.2 * K), (lx + 0.3 * K, ly + 0.2 * K)
    caja(msp, a[0], a[1], b[0], b[1], (255, 255, 255), lw=50)
    circulo(msp, (lx, ly), 0.1 * K, "CONTORNO")
    cota(msp, a, (b[0], a[1]), distancia=-5.0, escala=k, valor="600")
    cota(msp, (b[0], a[1]), b, distancia=-5.0, escala=k, valor="400")
    t(msp, "lavabotas con cepillos", (lx, a[1] - 11.5), 1.8, "MIDDLE_CENTER")


# ---------------------------------------------------------------- tablas y secuencia
def tablas(msp):
    subtitulo(msp, "DATOS DE DISEÑO Y OPERACIÓN", 232.0, 181.7, 2.6)
    filas = [["Elemento", "Datos de diseño"],
             ["Vado sanitario", "5,0 × 7,0 m útiles; 0,15 m de solución = 1,5 m³"],
             ["Arco de aspersión", "14 boquillas, 28 l/min, ≈ 60 l por camión"],
             ["Bomba del arco M17", "1,1 kW, arranque por sensor de paso, temporizada 20 s"],
             ["Hidrolavadora M16", "150 bar, 15 l/min, ≈ 300 l por camión"],
             ["Desinfectante", "amonio cuaternario o glutaraldehído (dosis del marbete)"],
             ["Renovación del vado", "semanal o según turbidez; registro diario"],
             ["Pediluvio y lavabotas", "en el acceso del personal PP1 (zona sucia / limpia)"]]
    y = tabla(msp, 232.0, 179.0, [40.3, 135.7], filas, h_fila=3.4, altura=1.9)
    subtitulo(msp, "GESTIÓN DE EFLUENTES", 232.0, y - 5.5, 2.6)
    filas = [["Efluente", "Destino"],
             ["Agua del lavadero (guano)", "canaleta → cámara 26 → biodigestor"],
             ["Solución del vado (desinfectante)", "bidones → operador habilitado (no al biodigestor)"],
             ["Barro de la rejilla desarenadora", "a la pila de guano (se seca en la planta)"]]
    y = tabla(msp, 232.0, y - 8.0, [59.9, 116.1], filas, h_fila=3.4, altura=1.9)
    t(msp, "\n".join([
        "SECUENCIA: 1) el camión se pesa; 2) cruza el vado a paso (5 km/h) y el sensor enciende el arco 20 s;",
        "3) descarga en P1 y lava caja y ruedas con la hidrolavadora antes de salir; 4) al salir vuelve a cruzar",
        "el vado. El operario usa botas, guantes de nitrilo, antiparras y protector facial (EPP del lavadero).",
    ]), (232.0, y - 5.0), 1.85, "TOP_LEFT")


def main():
    revs = [("D", "09/2026", "Emisión original: vado sanitario, arco de aspersión, lavadero de camiones, "
                             "pediluvio y lavabotas")]
    doc, msp, z = lamina(21, "LIMPIEZA Y DESINFECCIÓN\nDE VEHÍCULOS Y PERSONAL", "1:100/1:50/1:200", revs)
    planta(msp)
    corte_vado(msp)
    arco_aspersion(msp)
    lavadero(msp)
    pediluvio(msp)
    tablas(msp)
    exportar_lamina(doc, 21)


if __name__ == "__main__":
    main()
