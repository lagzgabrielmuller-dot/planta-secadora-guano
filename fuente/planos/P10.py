"""P10 - Conjunto 3D y lista de partes (S/E), Rev. D.

Imágenes: renders del modelo 3D Rev. D (modelo_3d/renders), recortados a fuente/planos/img.
Lista de partes: la de la Rev. C (1 a 34, subconjuntos 3.x y 4.x) + agregados Rev. D
(D1-D24 y E1-E10, de __RD_PARTES en visor.html; denominaciones abreviadas para que entren).
"""
import os

from PIL import Image

from lamina_secadora import (FECHA, exportar_lamina, imagen, lamina, subtitulo, t, tabla, titulo_vista)

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
RENDERS = os.path.join(RAIZ, "modelo_3d", "renders")
IMG = os.path.join(AQUI, "img")

# ---------------------------------------------------------------- lista de partes (Rev. C, plano 10 original)
PARTES = [
    ("1", "Playa de recepción de guano", "01", ""),
    ("2", "Tolva de recepción 3,1 m³", "12", "M15"),
    ("3", "Cinta de alimentación con tacos", "12", "M8"),
    ("4", "Secador de cinta de 3 pisos", "02", "M5, M6, M7"),
    ("5", "Esparcidor de paletas", "02", "M9"),
    ("6", "Sinfín de descarga", "08", "M10"),
    ("7", "Elevador de cangilones", "08", "M11"),
    ("8", "Acopio de producto seco", "01", ""),
    ("9", "Hogar de parrilla escalonada", "04", "M4"),
    ("10", "Intercambiador humos-aire", "04", ""),
    ("11", "Ventiladores de impulsión", "04", "M1, M2"),
    ("12", "Ducto de aire caliente", "02", ""),
    ("13", "Silo de cáscara 70 m³", "04", ""),
    ("14", "Sinfín de cáscara + válvula rotativa", "04", "M12"),
    ("15", "Chimenea de humos", "04", ""),
    ("16", "Tolva de cenizas 1 m³", "04", "M13"),
    ("17", "Ducto de aire agotado", "08", ""),
    ("18", "Ciclón separador", "08", ""),
    ("19", "Lavador de gases (scrubber)", "06", ""),
    ("20", "Extractor y chimenea de aire tratado", "08", "M3"),
    ("21", "Tanque de solución y bomba", "06", "M14"),
    ("22", "Sala de control (TGF)", "07", ""),
    ("23", "Taller de mantenimiento", "01", ""),
    ("24", "Vestuario, baños y oficina", "01", ""),
    ("25", "Depósito de repuestos", "01", ""),
    ("26", "Cámara de lixiviados", "01", ""),
    ("27", "Tanque de agua contra incendio", "01", ""),
    ("28", "Reserva 2ª etapa", "01", ""),
    ("29", "Tablero secundario TS-1", "07", ""),
    ("30", "Báscula para camiones 40 t", "11", ""),
    ("31", "Garita de control y balanza", "11", ""),
    ("32", "Circulación y playones de camiones", "11", ""),
    ("33", "Cerco perimetral y portón de acceso", "11", ""),
    ("34", "Estacionamiento del personal", "11", ""),
]

SUBCONJUNTOS = [
    ("3.1", "Banda con bordes ondulados y tacos", "12", "24,6 m"),
    ("3.2", "Tambor motriz Ø320 con goma", "12", "1"),
    ("3.3", "Tambor de cola Ø250 y tensor a tornillo", "12", "1"),
    ("3.4", "Rodillos portantes y de retorno Ø89", "12", "11 + 12"),
    ("3.5", "Ruedas de desvío en la curva", "12", "8"),
    ("3.6", "Faldones y placa de desgaste bajo la tolva", "12", "1 cj."),
    ("3.7", "Cabezal, capota y bajada al secador", "12", "1"),
    ("3.8", "Estructura y apoyos", "12", "1 cj."),
    ("4.1", "Banda de malla AISI 304", "02", "3"),
    ("4.2", "Tambor motriz Ø300 × 2100", "03", "3"),
    ("4.3", "Tambor de reenvío Ø250 × 2100", "02", "3"),
    ("4.4", "Rodamiento con brida UCF 212", "03", "6"),
    ("4.5", "Motorreductor 0,75 kW i = 1:300", "03", "3"),
    ("4.6", "Rodillo de retorno Ø89", "09", "15"),
    ("4.7", "Guías UHMW-PE 40 × 20", "09", "15"),
    ("4.8", "Panel sándwich 80 mm", "09", "1 cj."),
    ("4.9", "Puerta de inspección 700 × 600", "02", "6"),
    ("4.10", "Tolvas de transferencia", "02", "3"),
    ("4.11", "Estructura UPN 120 / IPN 140", "09", "1 cj."),
    ("4.12", "Campana de salida 800 × 800", "02", "1"),
    ("4.13", "Pasarela superior con baranda", "09", "1"),
]

# agregados Rev. D (__RD_PARTES de visor.html; "abreviado" = nombre acortado para la tabla)
AGREGADOS = [
    ("D1", "Puertas de inspección: manijas y microinterruptores", "17"),
    ("D2", "Protecciones de transmisiones y ejes", "17"),
    ("D3", "Pasarelas, plataformas, escaleras y barandas", "17"),
    ("D4", "Paradas de emergencia tipo hongo", "17"),
    ("D5", "Sensores de instrumentación", "22"),
    ("D6", "Puntos de medición (tomas de presión y temperatura)", "18"),
    ("D7", "Recirculación parcial de aire (retorno a la entrada)", "18"),
    ("D8", "Compuertas de regulación y by-pass de humos", "18"),
    ("D9", "Registros, tapas y bocas de limpieza", "17"),
    ("D10", "Lavador de gases: complementos", "18"),
    ("D11", "Ciclón: complementos", "17"),
    ("D12", "Generador: complementos de seguridad y mantenimiento", "17"),
    ("D13", "Silo de cáscara: seguridad", "15"),
    ("D14", "Sistema de cenizas: descarga y limpieza", "17"),
    ("D15", "Canalizaciones eléctricas", "17"),
    ("D16", "Puesta a tierra, equipotencialidad y pararrayos", "17"),
    ("D17", "Iluminación de emergencia y de zonas de trabajo", "15"),
    ("D18", "Señalización de seguridad (IRAM 10005)", "15"),
    ("D19", "Protección contra incendios", "15"),
    ("D20", "Drenajes y canaletas", "17"),
    ("D21", "Puntos de lubricación", "22"),
    ("D22", "Detalles de mantenimiento: tensores y tapas", "17"),
    ("D23", "Placas de identificación de equipos", "22"),
    ("D24", "Flechas de flujo", "18"),
    ("E1", "Estación de limpieza y desinfección de vehículos", "21"),
    ("E2", "Lavadero de camiones en el playón P1", "21"),
    ("E3", "Ventilación de la recepción: campana, extractor y biofiltro", "18"),
    ("E4", "Separador de cáscara y plumas (zaranda rotativa)", "19"),
    ("E5", "Ensacadora dosificadora de bolsas de 25 kg", "19"),
    ("E6", "Envasadora de bolsas chicas (1, 2 y 5 kg) para viveros", "19"),
    ("E7", "Depósito de producto embolsado y expedición", "13"),
    ("E8.1", "Biogás: recepción y mezcla", "20"),
    ("E8.2", "Biogás: biodigestores BD-1 y BD-2", "20"),
    ("E8.3", "Biogás: tanque de digestato (post-digestor)", "20"),
    ("E8.4", "Biogás: sala de cogeneración y tratamiento", "20"),
    ("E8.5", "Biogás: antorcha de seguridad", "20"),
    ("E8.6", "Biogás: línea al hogar (quemador piloto)", "20"),
    ("E9", "Ampliación del predio: Sector Este", "13"),
    ("E10", "Ventilación general de la nave (extractores y ventiladores)", "24"),
]


def recortes():
    """Recorta los renders Rev. D (cielo y márgenes vacíos) y los guarda en fuente/planos/img."""
    os.makedirs(IMG, exist_ok=True)
    a = os.path.join(IMG, "P10_A_general_RevD.png")
    b = os.path.join(IMG, "P10_B_despiece_RevD.png")
    with Image.open(os.path.join(RENDERS, "P10_A_general.png")) as im:
        im.convert("RGB").crop((0, 200, 2400, 1500)).save(a)
    with Image.open(os.path.join(RENDERS, "P10_B_despiece.png")) as im:
        im.convert("RGB").crop((425, 235, 1805, 1175)).save(b)
    return a, b


def control_textos(anchos, filas, altura):
    """Avisa si alguna celda queda con texto de menos de 1,5 mm (misma regla que tabla())."""
    for f in filas:
        for w, v in zip(anchos, f):
            if v:
                hh = max(1.4, min(altura, (w - 1.8) / (0.64 * len(str(v)))))
                if hh < 1.5:
                    print(f"  AVISO texto {hh:.2f} mm: {v}")


def main():
    revs = [("A", "09/2026", "Emisión original"),
            ("B", "09/2026", "B1: vista con cinta con tacos, camiones y operarios; lista de partes 1 a 34 y "
                             "subconjuntos 3.x (cinta) y 4.x (secador)"),
            ("C", "09/2026", "Imágenes regeneradas con el modelo 3D actual; el ventilador de combustión M4 pasa "
                             "al hogar (9), no a los de impulsión (11)"),
            ("D", FECHA, "Lista de partes Rev. D (D1-D24, E1-E10); imágenes del modelo Rev. D; STEP Rev. D")]
    doc, msp, z = lamina(10, "CONJUNTO 3D Y LISTA DE PARTES", "S/E", revs)
    ruta_a, ruta_b = recortes()

    # ---------------- A - vista general
    titulo_vista(msp, "A - VISTA GENERAL DE LA PLANTA REV. D (desde el Sudoeste)", 26, 278, 3.3)
    with Image.open(ruta_a) as im:
        wa, ha = im.size
    ancho_a = 196.0
    alto_a = ancho_a * ha / wa
    imagen(doc, msp, ruta_a, 26, 272 - alto_a, ancho_a)
    y_b = 272 - alto_a - 9

    # ---------------- B - despiece del secador
    titulo_vista(msp, "B - SECADOR DE CINTA: DESPIECE (paneles laterales y techo retirados)", 26, y_b, 3.3)
    with Image.open(ruta_b) as im:
        wb, hb = im.size
    alto_b = (y_b - 6) - 31
    ancho_b = alto_b * wb / hb
    imagen(doc, msp, ruta_b, 26, 31, ancho_b, alto_b)

    # ---------------- notas
    subtitulo(msp, "NOTAS", 26, 26.0, 2.6)
    t(msp, "\n".join([
        "1. Imágenes del modelo 3D interactivo Rev. D (visor.html), generado con las mismas cotas que los planos.",
        "2. Globos: números de la lista de partes. En B, subconjuntos 4.1 a 4.13 separados (despiece).",
        "3. Modelo para SolidWorks y Fusion 360: modelo_3d/Secadora_guano_RevD.step (ensamble en mm, una pieza por ítem).",
    ]), (26, 24.2), 1.9, "TOP_LEFT")

    # ---------------- lista de partes (columna 1)
    hf, ht = 3.05, 1.7
    xc1, xc2 = 231.0, 321.0
    a1 = [7, 54, 9, 17]
    subtitulo(msp, "LISTA DE PARTES DE LA PLANTA", xc1, 279.5, 3.0)
    filas = [["N°", "Denominación", "Plano", "Motores"]] + [list(p) for p in PARTES]
    control_textos(a1, filas, ht)
    y = tabla(msp, xc1, 278, a1, filas, h_fila=hf, altura=ht, alin=["C", "L", "C", "L"])
    y -= 5.0
    subtitulo(msp, "SUBCONJUNTOS DE LA CINTA (3) Y DEL SECADOR (4)", xc1, y, 2.25)
    filas = [["N°", "Denominación", "Plano", "Cant."]] + [list(p) for p in SUBCONJUNTOS]
    control_textos(a1, filas, ht)
    y = tabla(msp, xc1, y - 1.5, a1, filas, h_fila=hf, altura=ht, alin=["C", "L", "C", "C"])
    assert y > z["reservado"][3] + 2, f"la columna 1 baja hasta {y:.1f}"

    # ---------------- agregados Rev. D (columna 2)
    a2 = [8, 70, 9]
    subtitulo(msp, "AGREGADOS REV. D", xc2, 279.5, 3.0)
    filas = [["N°", "Denominación", "Plano"]] + [list(p) for p in AGREGADOS]
    control_textos(a2, filas, ht)
    sombras = {i: (255, 246, 214) for i, p in enumerate(AGREGADOS, start=1) if p[0].startswith("E8")}
    sombras.update({i: (232, 242, 250) for i, p in enumerate(AGREGADOS, start=1)
                    if p[0].startswith("E") and not p[0].startswith("E8")})
    y2 = tabla(msp, xc2, 278, a2, filas, h_fila=hf, altura=ht, alin=["C", "L", "C"], sombras=sombras)
    t(msp, "\n".join([
        "D1 a D24: seguridad, instrumentación y mantenimiento",
        "(sin fondo). E1 a E10: sectores nuevos de la ampliación",
        "(celeste); E8.x: sistema de biogás (amarillo).",
        "Plano: lámina donde se detalla cada agregado.",
        "Detalle de cada ítem en el modelo 3D (visor.html).",
    ]), (xc2, y2 - 2.0), 1.8, "TOP_LEFT")
    exportar_lamina(doc, 10)


if __name__ == "__main__":
    main()
