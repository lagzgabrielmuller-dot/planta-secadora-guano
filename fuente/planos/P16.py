"""P16 - Estudio de carga de fuego (Ley 19.587, Dec. 351/79, cap. 18 y Anexo VII).

Redibujo vectorial de la lámina Rev. D. Los valores se transcriben tal cual la lámina
original (ver fuente/calculos/resultados.json -> "fuego" para el cálculo).
"""
from lamina_secadora import (exportar_lamina, lamina, relleno_rect, subtitulo, t, tabla,
                             titulo_vista, tn)

SOMBRA = (250, 234, 183)          # celda sombreada = caso del proyecto


def texto(msp, renglones, x, y, altura=1.9, paso=2.6):
    for r in renglones:
        t(msp, r, (x, y), altura, "TOP_LEFT")
        y -= paso
    return y


def celdas(msp, x, y, anchos, h, marcadas):
    """Sombrea celdas (fila, columna) de una tabla con esquina superior izquierda (x, y)."""
    xs = [x]
    for w in anchos:
        xs.append(xs[-1] + w)
    for i, j in marcadas:
        relleno_rect(msp, xs[j], y - (i + 1) * h, xs[j + 1], y - i * h, SOMBRA)


def main():
    revs = [("D", "09/2026", "Emisión original: carga de fuego, riesgo, resistencia, pot. extintor y escape")]
    doc, msp, z = lamina(16, "ESTUDIO DE CARGA DE FUEGO\n(DEC. 351/79)", "S/E", revs)
    titulo_vista(msp, "ESTUDIO DE CARGA DE FUEGO - LEY 19.587, DEC. 351/79, CAP. 18 Y ANEXO VII", 26, 278, 3.5)

    # ------------------------------------------------ 1. carga de fuego del sector S1
    subtitulo(msp, "1. CARGA DE FUEGO DEL SECTOR S1 (materiales y cantidades máximas)", 26, 266.5, 2.6)
    filas = [["Material (sector S1: nave de proceso, 594 m²)", "kg", "PCI MJ/kg", "Energía MJ", "Clasificación (1.5)"],
             ["Guano seco en pila de acopio (21,7 m³ × 500 kg/m³)", "10.840", "10,5", "113.820", "muy combustible"],
             ["Guano en proceso dentro del secador (equivalente seco)", "600", "10,5", "6.300", "muy combustible"],
             ["Guano húmedo en playa de recepción (8 m³ × 800 kg/m³)", "6.400", "2,0", "12.800", "poco combustible"],
             ["Producto embolsado en zona 28 (1 turno: 104 bolsas × 25 kg)", "2.600", "10,5", "27.300", "muy combustible"],
             ["Bolsas vacías de PE (stock de línea)", "102", "46,0", "4.692", "muy combustible"],
             ["Rechazo de zaranda (plumas y cáscara de huevo)", "300", "8,0", "2.400", "combustible"],
             ["Pallets de madera (10 u × 22 kg)", "220", "18,4", "4.050", "muy combustible"],
             ["Bandas y recubrimientos de goma", "180", "32,0", "5.760", "combustible"],
             ["Guías UHMW-PE del secador (15 × 12 m)", "135", "46,0", "6.210", "combustible"],
             ["Aislación de cables (PVC/XLPE)", "250", "20,0", "5.000", "combustible"],
             ["Aceites y grasas en taller y depósito (200 l)", "176", "43,0", "7.568", "combustible"],
             ["Gasoil en tanque de la pala cargadora (150 l)", "126", "43,0", "5.418", "inflamable 2ª cat."],
             ["Mobiliario, papeles y ropa (oficina, vestuario, sala de control)", "800", "18,4", "14.728", "muy combustible"],
             ["Repuestos embalados (cartón y plásticos)", "150", "17,0", "2.550", "combustible"],
             ["TOTAL S1", "", "", "218.596", ""]]
    y = tabla(msp, 26, 265, [104, 14, 17, 20, 30], filas, h_fila=3.27, altura=1.65,
              alin=["L", "R", "R", "R", "L"], negrita_ultima=True, sombras={15: (241, 242, 244)})
    texto(msp, ["Carga de fuego = Σ(m · PCI) / (18,41 MJ/kg × superficie) [kg de madera equivalente por m², Anexo VII punto 1.2]",
                "S1: 218.596 MJ / 18,41 = 11.874 kg de madera → q = 11.874 / 594 m² = 20,0 kg/m² → rango 16 a 30 kg/m²"],
          26, y - 2.6, 1.85, 3.0)

    # ------------------------------------------------ 2. resumen por sector
    subtitulo(msp, "2. RESUMEN POR SECTOR DE INCENDIO", 26, 196.3, 2.6)
    filas = [["Sector", "Superficie m²", "Energía MJ", "q kg/m²", "Rango", "Riesgo", "Resist. al fuego", "Pot. A", "Pot. B"],
             ["S1 Nave de proceso", "594", "218.596", "20,0", "16 a 30", "R3", "F 60", "2 A", "6 B"],
             ["S2 Anexo del generador", "52", "2.274", "2,4", "≤ 15", "R3", "F 30", "1 A", "4 B"],
             ["S3 Silo de cáscara (al aire libre)", "72", "103.950", "78,0", "61 a 100", "R3", "F 120", "6 A", "10 B"],
             ["S4 Depósito de expedición (nuevo)", "240", "173.991", "39,4", "31 a 60", "R3", "F 90", "3 A", "8 B"],
             ["S5 Zona de biogás (al aire libre)", "864", "10.451", "0,7", "≤ 15", "R2", "F 60", "—", "6 B"]]
    y = tabla(msp, 26, 194.5, [74.2, 16.8, 17, 13, 13.2, 10.3, 19.1, 9.5, 11.9], filas, h_fila=3.36, altura=1.65,
              alin=["L", "R", "R", "R", "C", "C", "C", "C", "C"])
    texto(msp, ["Riesgo: R3 «muy combustible» en S1 a S4 (guano seco, cáscara, polietileno, madera); R2 «inflamable» en S5 (biogás ≈ 58 % CH4).",
                "S3 (silo): carga concentrada > 60 kg/m² → protección especial: rociadores con válvula de diluvio, sensor de temperatura TS-01,",
                "válvula rotativa cortafuego y guillotina de corte (el silo es de chapa al aire libre; se protege con agua, no con resistencia F).",
                "S4 (depósito nuevo): muros de ladrillo macizo 0,20 m (≥ F 120) y columnas de H°A° (F 90); a 27 m de la nave (sector independiente).",
                "S1: estructura metálica existente; exigencia F 60 → pintura intumescente en columnas y cabriadas del sector del acopio y la zaranda,",
                "o reducir el acopio a granel (con la pila máxima de 10,8 t se obtuvo 20 kg/m², dentro del rango 16 a 30)."],
          26, y - 3.0, 1.75, 2.6)

    # ------------------------------------------------ 6. matafuegos
    subtitulo(msp, "6. MATAFUEGOS", 26, 148.4, 2.6)
    filas = [["Verificación de matafuegos (art. 176 y Anexo VII)", "Resultado"],
             ["S1: 1 cada 200 m² → 594/200 = 3 mín.; se disponen", "10 (8 existentes + 2 nuevos)"],
             ["Recorrido máximo al matafuego: 20 m clase A / 15 m clase B", "cumple (plano 15)"],
             ["Art. 178: equipos eléctricos energizados", "CO2 5 kg junto al TGF"],
             ["S4 depósito 240 m² (3 A mín.)", "3 ABC 10 kg + 1 agua 10 l"],
             ["S5 biogás (6 B mín.)", "ABC 50 kg rodante + CO2 + gabinete"],
             ["Control, carga y recarga", "IRAM 3517 · tarjeta y marbete anual"]]
    tabla(msp, 26, 146.6, [92.2, 57.8], filas, h_fila=3.33, altura=1.65)

    # ------------------------------------------------ 7. artículos del capítulo 18
    subtitulo(msp, "7. ARTÍCULOS DEL CAPÍTULO 18 APLICADOS", 26, 115.2, 2.6)
    texto(msp, ["Art. 160: se cumplen los 5 objetivos: dificultar la iniciación (limpieza de polvo, prohibido fumar, sensores), evitar la",
                "propagación (sectores S1 a S5, muro RF-120, separación de 27 m), evacuación (salidas señalizadas), acceso de bomberos",
                "(portón y calle R8) e instalaciones de detección y extinción (detectores, central, hidrantes, rociadores).",
                "Art. 172: medios de escape libres, señalizados y de ancho reglamentario. Art. 176/178: cantidad y clase de matafuegos.",
                "Art. 187: brigada entrenada, capacitación anual, plan de emergencias con simulacro semestral y registro del personal."],
          26, 112.0, 1.8, 2.6)

    # ------------------------------------------------ 3. cuadros del Anexo VII
    subtitulo(msp, "3. CUADROS DEL ANEXO VII APLICADOS (sombreado = caso del proyecto)", 232, 266.5, 2.6)
    rangos = ["hasta 15", "16 a 30", "31 a 60", "61 a 100", "más de 100"]
    h = 3.2
    # 2.2.1 resistencia al fuego
    a1 = [26, 18, 18, 18, 18]
    celdas(msp, 232, 261, a1, h, [(1, 1), (1, 2), (2, 2), (3, 2), (4, 2)])
    filas = [["Carga kg/m²", "R2", "R3", "R4", "R5"]] + [[r] + v for r, v in zip(rangos, [
        ["F 60", "F 30", "F 30", "—"], ["F 90", "F 60", "F 30", "F 30"], ["F 120", "F 90", "F 60", "F 30"],
        ["F 180", "F 120", "F 90", "F 60"], ["F 180", "F 180", "F 120", "F 90"]])]
    tabla(msp, 232, 261, a1, filas, h_fila=h, altura=1.65, alin=["L", "C", "C", "C", "C"])
    tn(msp, "2.2.1 Resistencia al fuego", (334, 259.4), 1.85, "MIDDLE_LEFT")
    texto(msp, ["(locales con ventilación natural)", "S1 → F 60 · S2 → F 30", "S3 → F 120 · S4 → F 90", "S5 → F 60"],
          334, 256.4, 1.7, 2.35)
    # 4.1 potencial extintor clase A
    a2 = [26, 18, 18, 18]
    celdas(msp, 232, 237, a2, h, [(2, 1), (3, 1), (4, 1)])
    filas = [["Carga kg/m²", "R3", "R4", "R5"]] + [[r] + v for r, v in zip(rangos, [
        ["1 A", "1 A", "1 A"], ["2 A", "1 A", "1 A"], ["3 A", "2 A", "1 A"], ["6 A", "4 A", "3 A"],
        ["a det.", "a det.", "a det."]])]
    tabla(msp, 232, 237, a2, filas, h_fila=h, altura=1.65, alin=["L", "C", "C", "C"])
    tn(msp, "4.1 Potencial extintor", (316, 235.4), 1.85, "MIDDLE_LEFT")
    texto(msp, ["mínimo, fuegos clase A", "S1 → 2 A por matafuego", "S4 → 3 A · S3 → 6 A"], 316, 232.4, 1.7, 2.35)
    # 4.2 potencial extintor clase B
    a3 = [26, 18, 18]
    celdas(msp, 232, 213, a3, h, [(1, 1), (2, 2)])
    filas = [["Carga kg/m²", "R2", "R3"]] + [[r] + v for r, v in zip(rangos, [
        ["6 B", "4 B"], ["8 B", "6 B"], ["10 B", "8 B"], ["20 B", "10 B"], ["a det.", "a det."]])]
    tabla(msp, 232, 213, a3, filas, h_fila=h, altura=1.65, alin=["L", "C", "C"])
    tn(msp, "4.2 Potencial extintor", (298, 211.4), 1.85, "MIDDLE_LEFT")
    texto(msp, ["mínimo, fuegos clase B (gasoil de la pala,", "aceites del taller, biogás)", "S1 → 6 B · S5 → 6 B"],
          298, 208.4, 1.7, 2.35)

    # ------------------------------------------------ 4. medios de escape
    subtitulo(msp, "4. MEDIOS DE ESCAPE (Anexo VII, cap. 3)", 232, 187.3, 2.6)
    filas = [["Sector", "Sup. m²", "Factor ocup.", "N personas", "n = N/100", "UAS mín.", "Ancho mín.", "Salidas previstas"],
             ["S1", "594", "16 m²/p", "38", "0,38", "2", "1,10 m", "SE1 1,20, SE2 1,20, P1 4,00, P2 4,00, P3 2,50"],
             ["S4", "240", "30 m²/p", "8", "0,08", "2", "1,10 m", "Portón 4,00, SE3 1,20"]]
    y = tabla(msp, 232, 185.5, [11, 13, 17, 16, 15, 13, 15, 73], filas, h_fila=3.43, altura=1.65,
              alin=["L", "R", "C", "C", "C", "C", "C", "L"])
    texto(msp, ["Recorrido máximo medido en planta hasta una salida: 20 m en la nave (plano 15). Puertas de egreso con",
                "apertura hacia afuera, barra antipánico, cartel SALIDA con luz autónoma (art. 172 inc. 2 y 5)."],
          232, y - 2.0, 1.75, 2.5)

    # ------------------------------------------------ 5. servicio de agua contra incendio
    subtitulo(msp, "5. SERVICIO DE AGUA CONTRA INCENDIO", 232, 164.0, 2.6)
    filas = [["Concepto", "Valor"],
             ["Superficie cubierta total (nave + anexo + depósito + sala CHP)", "901 m²"],
             ["Reserva mínima adoptada (10 l/m², mín. 10 m³)", "10,0 m³"],
             ["2 hidrantes de 45 mm × 200 l/min × 30 min", "12,0 m³"],
             ["Tanque existente (27)", "20 m³ (verifica)"],
             ["Bomba M25: 24 m³/h a 45 m c.a. (η 0,60)", "4,9 kW eje → 7,5 kW"],
             ["Rociadores del silo: 8 boquillas × 40 l/min", "320 l/min (diluvio)"]]
    tabla(msp, 232, 162.2, [120, 53], filas, h_fila=3.36, altura=1.65)

    exportar_lamina(doc, 16)


if __name__ == "__main__":
    main()
