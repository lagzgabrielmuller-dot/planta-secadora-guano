"""Presupuesto de la planta (entrega final, 10/2026): inversión, pedido de cotización a la Cooperativa
La Agrícola Regional (LAR), costo de la energía con LAR como distribuidora, costos operativos y
evaluación económica.

Precios: estimaciones de anteproyecto (± 25 %). Se expresan en dólares (USD) y en pesos al tipo de cambio
del Banco Nación del 23/10/2026. Cada precio unitario lleva su fuente o criterio. Los precios de LAR
(corralón, ferretería y electricidad, hormigón elaborado) son de referencia de mercado y se deben
reemplazar por la cotización que entregue LAR con la planilla «Pedido LAR».

    python presupuesto.py      # -> presupuesto.json y presupuesto/Presupuesto_Secadora_Guano.xlsx
"""
from __future__ import annotations

import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
R = json.load(open(os.path.join(AQUI, "resultados.json"), encoding="utf-8"))

DOLAR = 1550.0          # $/USD, BNA vendedor 23/10/2026
FECHA = "23/10/2026"

# ------------------------------------------------------------------------------- fuentes de precios
FUENTES = {
    "BNA": "Banco Nación, cotización vendedor 23/10/2026: $ 1.550 (La Nación, El Destape, 23/10/2026)",
    "H21": "Hormigón elaborado H-21: $ 174.000 a $ 222.000/m³ en planta (Mercado Libre, Hormigonline, ITAR, 10/2026); se toma $ 210.000",
    "UPN": "Perfil UPN 120 × 12 m (161 kg): $ 400.000 a $ 505.000 (Ropelato, Norco, Tubocenter, 10/2026) → ≈ $ 2.900/kg",
    "CEM": "Cemento portland 50 kg: $ 12.000 a $ 15.000 en corralón (servidos.ar, deladrillo.com, 10/2026)",
    "CAB": "Cable subterráneo Cu 4 × 35 mm²: $ 29.500 a $ 32.800/m (Distrielectro, 10/2026); el resto por sección",
    "INOX": "Chapa AISI 304 2 mm 1000 × 2000: $ 360.000 a $ 600.000 (Mercado Libre, Provecom, 10/2026)",
    "MF": "Matafuego ABC 10 kg IRAM: $ 155.400 + IVA (Segucentro, 10/2026)",
    "AIRTEC": "Campagnoni extractor industrial 1,4 m con persianas (AirTEC 1215): $ 1.690.400 (tienda oficial Campagnoni, Mercado Libre)",
    "VM": "Campagnoni ventilador móvil 121,5 cm: $ 1.643.477 (Mercado Libre, 10/2026)",
    "VFD": "Variadores WEG CFW500/CFW300: CFW300 1 HP $ 652.000; CFW500 7,5 HP $ 1.800.000 (Mercado Libre, Indusell)",
    "REVC": "Memoria Rev. C, tabla 19 (consultas a fabricantes nacionales, USD 2026, ± 25 %)",
    "EST": "Estimación de anteproyecto del grupo (costo de materiales + mano de obra de taller local)",
    "TAR": "EPRE Entre Ríos, cuadro tarifario provincial 10/2026 (Res. EPRE 143/26); valores T3 a confirmar con LAR",
    "LDR": "Lana de roca Acuflex 50 mm, rollo de 3 m²: $ 72.760 (Mercado Libre, 11/2026) → ≈ $ 24.250/m²",
    "REVF": "Rev. F (11/2026), estimación con los precios de este presupuesto: chapa AISI 304 ≈ USD 9,8/kg (INOX), lana de "
            "roca (LDR), chapa de protección al precio del acero laminado (UPN), taller USD 11/h; PTFE ≈ USD 25/kg, "
            "perfil de silicona, ventilador centrífugo y sifones a cotizar (no se encontró precio público en Argentina)",
}

ARS = lambda usd: usd * DOLAR
USD = lambda ars: ars / DOLAR
INOX_KG = USD(480000) / (1.0 * 2.0 * 0.002 * 7930)     # chapa AISI 304 2 mm 1 × 2 m (31,7 kg) a $ 480.000 → USD/kg
LANA_M2 = USD(72760 / 3)                                # lana de roca 50 mm, USD/m²
# Rev. F: aislación del ducto de escape Ø800 (14,0 m, layout_planta.json) y del ciclón Ø1,8 (≈ 28 m²) con lana de
# roca 50 mm y chapa de protección de 0,5 mm (3,9 kg/m²); purgas de condensado con sifón
A_AISL = 3.1416 * 0.9 * 14.0 + 30.0                      # m² (diámetro exterior con aislación: 0,9 m)
COSTO_ESCAPE = A_AISL * (LANA_M2 + 3.9 * USD(2900)) + A_AISL * 0.6 * 11 + 150
# Rev. F: tolva de retención aislada 0,7 m³ y enfriador a contracorriente (≈ 135 kg de chapa AISI 304 2 mm), aislación
# de la tolva (4,5 m²), ventilador centrífugo M40 0,55 kW (≈ USD 450, a cotizar), conducto al escape y arranque
COSTO_DESCARGA = 135 * INOX_KG + 4.5 * LANA_M2 + 450 + 150 + 150 + 50 * 11

# ------------------------------------------------------------------------------- 1. inversión
# (código, rubro, descripción, cantidad, unidad, USD unitario, proveedor, fuente)
INVERSION = [
    # --- A. Planta de secado (Rev. C): montos de la memoria Rev. C actualizados con el despiece del secador
    ("A1", "Secador SC-4", "Secador de cinta de 3 pisos completo (ver despiece, planilla «Secador»)", 1, "gl", None, "Taller metalúrgico local + LAR", "EST"),
    ("A2", "Generador", "Generador de aire caliente a cáscara: hogar, refractario, parrilla, intercambiador, chimenea, ciclón de humos", 1, "gl", 45000, "Fabricante nacional", "REVC"),
    ("A3", "Aire", "Ventiladores de impulsión M1-M2, ventilador del hogar M4, ductos aislados", 1, "gl", 14000, "Fabricante nacional", "REVC"),
    ("A4", "Gases", "Ciclón, lavador PRFV, bomba M14, extractor M3 22 kW, chimenea", 1, "gl", 25000, "Fabricante nacional", "REVC"),
    ("A5", "Cáscara", "Silo de cáscara 70 m³, sinfín M12, válvula cortafuego, tolva de cenizas", 1, "gl", 12000, "Fabricante nacional", "REVC"),
    ("A6", "Transporte", "Tolva de recepción, cinta de alimentación (plano 12), esparcidor, sinfín de descarga, elevador", 1, "gl", 10000, "Taller metalúrgico local", "REVC"),
    ("A7", "Control", "Tablero TGF, variadores, PLC S7-1200, HMI, instrumentación, TS-1", 1, "gl", 28000, "Integrador eléctrico", "REVC"),
    ("A8", "Eléctrica", "Instalación eléctrica de planta Rev. C (acometida, bandejas, cables, iluminación)", 1, "gl", 8000, "LAR Electricidad + instalador", "REVC"),
    ("A9", "Obra civil", "Nave de proceso 594 m² y anexo (estructura metálica, pisos, canaleta, locales) USD 330/m²", 594, "m²", 330, "Constructora + LAR (hormigón, hierro, cemento)", "REVC"),
    # --- B. Ampliación Rev. D
    ("B1", "E1-E2 Limpieza", "Vado sanitario H°A° 7 × 5 m, arco de 14 boquillas, bomba M17, tanque, hidrolavadora M16, pediluvio", 1, "gl", 11200, "LAR (hormigón) + proveedores", "EST"),
    ("B2", "E3 Recepción", "Campana 5 × 4 m, ducto Ø600, extractor M23 4 kW con VFD, biofiltro 38 m²", 1, "gl", 14000, "Taller local", "EST"),
    ("B3", "E4 Zaranda", "Trommel Ø0,9 × 3 m con M18, plataforma +3,0 m, desviadora M35, tolva pulmón", 1, "gl", 9500, "Taller local", "EST"),
    ("B4", "E5 Ensacadora", "Ensacadora de boca abierta 25 kg con balanza, cosedora, cinta de salida", 1, "gl", 16000, "Fabricante nacional", "EST"),
    ("B5", "E6 Bolsas chicas", "Envasadora vertical 1-2-5 kg con dosificador volumétrico y sellado", 1, "gl", 18000, "Fabricante nacional", "EST"),
    ("B6", "E7 Depósito", "Depósito de expedición 20 × 12 m (ladrillo macizo F 120, techo de chapa, platea)", 240, "m²", 300, "Constructora + LAR", "EST"),
    ("B7", "E8 Biogás", "Recepción y mezcla, 2 biodigestores 141 m³ con doble membrana, T3 201 m³, separador, tratamiento", 1, "gl", 165000, "Proveedor especializado", "EST"),
    ("B8", "E8 Cogeneración", "Motogenerador a biogás 25 kWe / 40 kWt en contenedor, antorcha, línea al hogar", 1, "gl", 52000, "Proveedor especializado", "EST"),
    ("B9", "E9 Predio", "Ampliación Sector Este: 808 m² de pavimento, cerco, portón R8, cortina forestal, farolas", 1, "gl", 25000, "Constructora + LAR", "EST"),
    ("B10", "E10 Ventilación", "2 extractores Campagnoni AirTEC 1215 con persianas", 2, "u", round(USD(1690400)), "Campagnoni (Crespo)", "AIRTEC"),
    ("B11", "E10 Ventilación", "2 ventiladores móviles Campagnoni 50\"", 2, "u", round(USD(1643477)), "Campagnoni (Crespo)", "VM"),
    ("B12", "Seguridad", "Ítems D1-D24: puertas con enclavamiento, protecciones, pasarelas, hongos, sensores, compuertas, lubricación, placas", 1, "gl", 28000, "Taller local + integrador", "EST"),
    ("B13", "Incendio", "15 matafuegos nuevos, 4 hidrantes, bomba M25 + jockey, central, detectores, rociadores del silo, señalización", 1, "gl", 25000, "Proveedor de incendio + LAR", "EST"),
    ("B14", "TG2", "Tablero TG2, seccionales TS-ENS, TS-LAV, TS-BIO, TS-VEN, TL2, TBI, cables y bandejas (ver Pedido LAR)", 1, "gl", 22000, "LAR Electricidad + integrador", "EST"),
    ("B15", "Puesta a tierra", "Anillo Cu 50 mm², 10 jabalinas, BEP, pararrayos con bajadas (D16)", 1, "gl", 6000, "LAR Electricidad + instalador", "EST"),
    ("B16", "Fatiga (Rev. E)", "Eje de reenvío Ø60 en lugar de Ø50 (3 u), rectificado de asientos, ensayos de material", 1, "gl", 2600, "Taller local + laboratorio", "EST"),
    # --- Rev. F (estudio térmico del secador)
    ("B17", "Descarga (Rev. F)", "Tolva de retención aislada 0,7 m³ con TT-05, enfriador a contracorriente con ventilador M40 0,55 kW, conducto al escape", 1, "gl", round(COSTO_DESCARGA, -1), "Taller local + integrador", "REVF"),
    ("B18", "Escape (Rev. F)", "Aislación lana de roca 50 mm con chapa del ducto Ø800 (14 m) y del ciclón; purgas de condensado con sifón", 1, "gl", round(COSTO_ESCAPE, -1), "Taller local + LAR", "REVF"),
    ("C1", "Ingeniería", "Ingeniería de detalle, habilitaciones (municipio, EIA provincial, Bomberos, SENASA, LAR)", 1, "gl", 18000, "—", "EST"),
]

# ------------------------------------------------------------------------------- 2. despiece del secador SC-4
# precios de materiales (USD) a partir de las referencias; mano de obra de taller USD 11/h (≈ $ 17.000/h)
ACERO_KG = USD(2900)          # perfiles laminados (UPN 120 ≈ $ 2.900/kg)
SECADOR = [
    # (descripción, cantidad, unidad, USD unitario, proveedor, fuente)
    ("Perfiles UPN 120, IPN 140, L 50×5 y placas base (bastidor)", 1620, "kg", round(ACERO_KG, 2), "LAR Corralón / distribuidor siderúrgico", "UPN"),
    ("Paneles sándwich 80 mm lana de roca, cara interior AISI 304", 161, "m²", 85, "Fabricante de paneles", "EST"),
    ("Malla transportadora AISI 304 Ø2 p5, 2.000 mm (3 bandas de 25 m)", 150, "m²", 180, "Fabricante de bandas de malla", "EST"),
    ("Tambor motriz Ø300 × 2.100 con eje SAE 1045 Ø60 y engomado", 3, "u", 1400, "Taller local", "EST"),
    ("Tambor de reenvío Ø250 × 2.100 con eje Ø60/Ø50 y tensores M20", 3, "u", 1050, "Taller local", "EST"),
    ("Rodamientos UCF 212 con brida", 6, "u", 95, "Casa de rodamientos", "EST"),
    ("Unidades tensoras UCT 210", 6, "u", 80, "Casa de rodamientos", "EST"),
    ("Motorreductor 0,75 kW doble sinfín-corona 1:300", 3, "u", 950, "Fabricante nacional", "EST"),
    ("Cadena ASA 60, piñón Z15, corona Z75 y protector", 3, "jgo", 260, "Casa de transmisiones", "EST"),
    ("Guías UHMW-PE 40×20, guías laterales inox, tolvas de caída", 1, "gl", 4500, "Taller local", "INOX"),
    ("Guías de PTFE 40×20 de los pisos 2 y 3 (Rev. F, ≈ 202 kg; no se descuenta el UHMW-PE que reemplazan)", 202, "kg", 25, "Distribuidor de plásticos técnicos (a cotizar)", "REVF"),
    ("Faldones de sellado de bordes (Rev. F): chapa AISI 304 1,5 mm (≈ 265 kg), labio de silicona 200 °C (70 m, ≈ USD 10/m a cotizar) y 40 h de taller", 1, "gl", round(265 * INOX_KG + 70 * 10 + 40 * 11, -1), "Taller local", "REVF"),
    ("Plenum, campana de salida y bridas", 1, "gl", 3800, "Taller local", "EST"),
    ("Pasarela superior con barandas, escalera con jaula", 1, "gl", 3200, "Taller local + LAR", "EST"),
    ("Rodillos de retorno Ø89 (15)", 15, "u", 45, "Casa de transmisiones", "EST"),
    ("Bulonería 8.8 zincada e inoxidable A2, varillas M16 5.8 y resina (40 anclajes)", 1, "gl", 650, "LAR Ferretería", "EST"),
    ("Pintura epoxi y poliuretano (2 manos), electrodos, consumibles", 1, "gl", 1300, "LAR Ferretería", "EST"),
    ("Mano de obra de taller: corte, soldadura, mecanizado, armado", 1900, "h", 11, "Taller metalúrgico de Crespo", "EST"),
    ("Montaje en obra, alineación y puesta en marcha (2 técnicos × 15 días)", 240, "h", 14, "Taller metalúrgico de Crespo", "EST"),
]

# ------------------------------------------------------------------------------- 3. pedido de cotización a LAR
# Cantidades medidas sobre los planos y el visor (rubros que LAR vende: hormigón elaborado, corralón,
# ferretería y electricidad).
PEDIDO_LAR = [
    # (sección LAR, ítem, cantidad, unidad, $ unitario de referencia, de dónde sale la cantidad)
    ("Hormigón elaborado", "Hormigón H-21 asentamiento 10 cm (platea depósito, vado, losas de digestores, bases, pavimentos)", 238, "m³", 210000, "44 depósito + 12 vado + 57 biogás + 4 bases + 121 pavimento"),
    ("Corralón", "Acero ADN 420 en barras Ø6 a Ø16", 14000, "kg", 2300, "≈ 60 kg/m³ en losas y bases"),
    ("Corralón", "Malla sima Q188 (2,15 × 6 m)", 83, "u", 95000, "1.070 m² de pavimento y platea"),
    ("Corralón", "Ladrillo macizo común (muros F 120 del depósito)", 23000, "u", 260, "192 m² × 120 u/m²"),
    ("Corralón", "Cemento portland 50 kg", 250, "bolsa", 13000, "mampostería y revoques del depósito"),
    ("Corralón", "Arena gruesa / cal hidratada", 30, "m³", 38000, "morteros"),
    ("Corralón", "Chapa galvanizada trapezoidal C25 (techo y cierres del depósito)", 465, "m²", 18000, "273 m² techo + 192 m² cierres"),
    ("Corralón", "Perfiles UPN 120 × 12 m (bastidor del secador)", 3, "barra", 470000, "34 m de columnas"),
    ("Corralón", "Perfiles IPN 140 × 12 m (vigas del secador)", 6, "barra", 560000,
     "4 vigas de 13 m = tramo de 9,75 + tramo de 3,25 m, empalmados con cubrejuntas sobre la columna D"),
    ("Corralón", "Ángulo L 50×50×5 × 6 m (travesaños)", 17, "barra", 58000, "101 m"),
    ("Ferretería", "Varilla roscada M16 clase 5.8 × 190 mm con tuerca y arandela", 96, "u", 6200, "40 secador + 16 ventiladores + 40 depósito"),
    ("Ferretería", "Resina epoxi para anclaje químico, cartucho 585 ml", 10, "u", 70000, "≈ 10 anclajes M16 por cartucho"),
    ("Ferretería", "Bulonería 8.8 zincada y A2 surtida", 120, "kg", 9300, "bridas, guías, protecciones"),
    ("Ferretería", "Pintura epoxi antióxido + esmalte poliuretánico", 160, "l", 18600, "650 m² a 2 manos"),
    ("Ferretería", "Electrodos E7018 / E6013", 80, "kg", 9300, "soldadura en obra"),
    ("Electricidad", "Cable subterráneo Cu 4 × 35 mm² IRAM 2178 (acometida TG2)", 45, "m", 32800, "40 m + reserva"),
    ("Electricidad", "Cable subterráneo Cu 4 × 16 mm² (Q23 TS-BIO)", 110, "m", 16300, "105 m + reserva"),
    ("Electricidad", "Cable Cu 4 × 6 mm² (TBI bombas de incendio)", 58, "m", 7100, "55 m + reserva"),
    ("Electricidad", "Cable Cu 4 × 4 mm² (Q21, Q22, Q25)", 130, "m", 5100, "25 + 50 + 45 m + reserva"),
    ("Electricidad", "Cable Cu 4 × 2,5 mm² (Q24, Q27 y motores)", 260, "m", 3600, "58 m de circuitos + bajadas a motores"),
    ("Electricidad", "Cable Cu desnudo 50 mm² (anillo de puesta a tierra y bajadas)", 180, "m", 9300, "D16, plano 17"),
    ("Electricidad", "Jabalina Cu-Ac 5/8\" × 3 m con cámara de inspección", 10, "u", 62000, "PAT-1 a PAT-10"),
    ("Electricidad", "Bandeja perforada galvanizada 300 mm con accesorios", 80, "m", 28000, "recorridos de fuerza"),
    ("Electricidad", "Bandeja perforada galvanizada 150 mm (instrumentación)", 90, "m", 17000, "D15"),
    ("Electricidad", "Campana LED industrial 150 W (depósito)", 6, "u", 217000, "cálculo luminotécnico Q25"),
    ("Electricidad", "Farola LED 100 W con columna de 7 m", 5, "u", 713000, "Sector Este"),
    ("Electricidad", "Reflector LED 100 W / proyector Ex 60 W", 6, "u", 93000, "dársena y zona de biogás"),
    ("Electricidad", "Luz de emergencia autónoma 3 h con cartel SALIDA", 8, "u", 54000, "plano 15"),
    ("Electricidad", "Interruptores termomagnéticos 4P y diferenciales 30 mA (TG2 y seccionales)", 1, "gl", 2900000, "plano 23"),
    ("Electricidad", "Gabinetes IP65 para TS-LAV, TS-VEN, TL2 y TS-ENS", 4, "u", 420000, "plano 23"),
    ("Electricidad", "Caño corrugado/PVC Ø50 para tendidos enterrados", 220, "m", 3800, "Q22, Q23, Q25, TBI"),
]

# ------------------------------------------------------------------------------- 4. energía con LAR
TARIFA = {"cargo_fijo_mes": 85000.0,     # $/mes (estimado T3 BT)
          "potencia_kw_mes": 14500.0,    # $/kW·mes de potencia contratada (estimado T3 BT)
          "energia_kwh": 185.0,          # $/kWh (estimado T3 BT, sin subsidio)
          "inyeccion_kwh": 95.0}         # $/kWh reconocido por la energía inyectada (generación distribuida, estimado)


def energia():
    tg = R["tg2"]
    bio = R["biogas"]
    e_tgf = 54 * 8 * 250                                        # kWh/año del TGF (memoria Rev. C)
    e_tg2 = tg["demanda_tg2_kW"] * 8 * 250 + R["iluminacion"]["P_Q25_kW"] * 12 * 365
    e_total = e_tgf + e_tg2
    e_g1 = bio["E_el"] * 365                                    # kWh/año que genera G1
    autoconsumo = min(e_g1 * 0.55, e_total)                     # G1 coincide con el turno ≈ 55 % del tiempo
    inyectada = e_g1 - autoconsumo
    pot = tg["balance"]["adoptada_kW"]
    fijo = TARIFA["cargo_fijo_mes"] * 12 + TARIFA["potencia_kw_mes"] * pot * 12
    sin_g1 = fijo + TARIFA["energia_kwh"] * e_total
    con_g1 = fijo + TARIFA["energia_kwh"] * (e_total - autoconsumo) - TARIFA["inyeccion_kwh"] * inyectada
    return {"E_TGF_kWh": round(e_tgf), "E_TG2_kWh": round(e_tg2), "E_total_kWh": round(e_total),
            "E_G1_kWh": round(e_g1), "autoconsumo_kWh": round(autoconsumo), "inyectada_kWh": round(inyectada),
            "potencia_kW": pot, "tarifa": TARIFA, "costo_sin_G1_ARS": round(sin_g1), "costo_con_G1_ARS": round(con_g1),
            "costo_sin_G1_USD": round(USD(sin_g1)), "costo_con_G1_USD": round(USD(con_g1)),
            "ahorro_G1_USD": round(USD(sin_g1 - con_g1)), "precio_medio_ARS_kWh": round(sin_g1 / e_total, 1)}


# ------------------------------------------------------------------------------- 5. costos y evaluación
def evaluacion(inversion_usd, en, turnos=1, biogas=True):
    prod_t = 650.0 * turnos                                     # t/año de guano seco (memoria Rev. C)
    mix = {"bolsas 25 kg": (0.60, 250.0), "bolsas chicas 1-2-5 kg": (0.15, 600.0), "granel": (0.25, 130.0)}
    ventas = sum(prod_t * f * p for f, p in mix.values())
    digestato = 1.8 * 365 * 20.0 if biogas else 0.0             # t/año de fracción sólida × USD 20/t
    sulfato = 125 * 40.0 * turnos
    ahorro_gestion = (16000.0 + 2500.0) * turnos                # memoria Rev. C, tabla 21
    ingresos = ventas + digestato + sulfato + ahorro_gestion
    e_extra = en["costo_sin_G1_USD"] * 0.8 * (turnos - 1)       # el segundo turno duplica la energía variable
    costos = {
        "Cáscara de arroz (419 t/año por turno con el aire ajustado al 15 %, modelo térmico Rev. F; USD 25/t)": 419 * 25 * turnos,
        "Energía eléctrica con LAR": (en["costo_con_G1_USD"] if biogas else en["costo_sin_G1_USD"]) + e_extra,
        "Mano de obra (3 operarios por turno × USD 1.000 × 13 meses)": 3 * 1000 * 13 * turnos,
        "Bolsas, rótulos y pallets (envasado)": prod_t * 0.75 * 1000 / 25 * 0.45 + prod_t * 0.15 * 1000 / 2.2 * 0.08,
        "Mantenimiento y repuestos (3 % de equipos)": 0.03 * inversion_usd * 0.55 * (1 + 0.3 * (turnos - 1)),
        "Operación y mantenimiento del biogás (USD 0,03/kWh generado)": 0.03 * en["E_G1_kWh"] if biogas else 0.0,
        "Ácido, agua, combustible de la pala, monitoreos, H&S": 1500 + 3300 + 4000,
        "Seguros e impuestos (1 % de la inversión)": 0.01 * inversion_usd,
    }
    costo = sum(costos.values())
    neto = ingresos - costo
    tasa, n = 0.10, 15
    van = -inversion_usd + sum(neto / (1 + tasa) ** k for k in range(1, n + 1))
    # TIR por bisección
    lo, hi = -0.99, 1.0
    f = lambda r: -inversion_usd + sum(neto / (1 + r) ** k for k in range(1, n + 1))
    if f(lo) * f(hi) > 0:
        tir = float("nan")
    else:
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(lo) * f(mid) <= 0:
                hi = mid
            else:
                lo = mid
        tir = (lo + hi) / 2
    repago = inversion_usd / neto if neto > 0 else math.inf
    return {"ventas": round(ventas), "mix": mix, "digestato": round(digestato), "sulfato": round(sulfato),
            "ahorro_gestion": round(ahorro_gestion), "ingresos": round(ingresos),
            "costos": {k: round(v) for k, v in costos.items()}, "costo": round(costo), "neto": round(neto),
            "VAN": round(van), "TIR": round(tir * 100, 1) if tir == tir else None, "repago": round(repago, 1),
            "tasa": tasa, "anios": n}


def calcular():
    sec_filas = [(d, q, u, pu, round(q * pu), prov, fu) for d, q, u, pu, prov, fu in SECADOR]
    total_secador = sum(f[4] for f in sec_filas)
    inv_filas = []
    for cod, rub, desc, q, u, pu, prov, fu in INVERSION:
        if pu is None:
            pu = total_secador
        inv_filas.append((cod, rub, desc, q, u, pu, round(q * pu), prov, fu))
    sub_c = sum(f[6] for f in inv_filas if f[0].startswith("A"))
    sub_d = sum(f[6] for f in inv_filas if f[0].startswith("B"))
    sub_i = sum(f[6] for f in inv_filas if f[0].startswith("C"))
    imprevistos = 0.07 * (sub_c + sub_d + sub_i)
    total = sub_c + sub_d + sub_i + imprevistos
    lar = [(s, it, q, u, pu, round(q * pu), de) for s, it, q, u, pu, de in PEDIDO_LAR]
    total_lar = sum(f[5] for f in lar)
    en = energia()
    ev = evaluacion(total, en)
    # variante solo planta de secado (Rev. C + E1-E7, E10 y seguridad; sin biogás B7-B8 y su 7 % de ingeniería)
    sin_bio_inv = total - sum(f[6] for f in inv_filas if f[0] in ("B7", "B8")) * 1.07
    escenarios = []
    for nom, inv_e, turnos, bio in (("A – Planta completa, 1 turno (8 t/día)", total, 1, True),
                                    ("B – Sin biogás, 1 turno", sin_bio_inv, 1, False),
                                    ("C – Planta completa, 2 turnos (16 t/día)", total + 30000, 2, True),
                                    ("D – Sin biogás, 2 turnos", sin_bio_inv + 30000, 2, False)):
        e = evaluacion(inv_e, en, turnos, bio)
        escenarios.append({"nombre": nom, "inversion": round(inv_e), "neto": e["neto"], "VAN": e["VAN"],
                           "TIR": e["TIR"], "repago": e["repago"], "ingresos": e["ingresos"], "costo": e["costo"]})
    ev["escenarios"] = escenarios
    return {"dolar": DOLAR, "fecha": FECHA, "fuentes": FUENTES,
            "secador": {"filas": sec_filas, "total": round(total_secador)},
            "inversion": {"filas": inv_filas, "sub_revC": round(sub_c), "sub_revD": round(sub_d), "sub_ing": round(sub_i),
                          "imprevistos": round(imprevistos), "total": round(total), "total_ARS": round(ARS(total)),
                          "sin_biogas": round(sin_bio_inv)},
            "lar": {"filas": lar, "total_ARS": round(total_lar), "total_USD": round(USD(total_lar))},
            "energia": en, "evaluacion": ev}


def planilla(res, ruta):
    """Excel con las hojas Resumen, Inversión, Secador, Pedido LAR, Energía LAR y Evaluación."""
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    wb = Workbook()
    fino = Side(style="thin", color="888888")
    borde = Border(left=fino, right=fino, top=fino, bottom=fino)
    cab = PatternFill("solid", fgColor="DCE3EA")
    lar_fill = PatternFill("solid", fgColor="E2F0E4")

    def hoja(nombre, titulo, encabezado, filas, anchos, formatos=None, total=None):
        ws = wb.create_sheet(nombre)
        ws["A1"] = titulo
        ws["A1"].font = Font(bold=True, size=13)
        ws["A2"] = f"Secadora de guano 8 t/día · E.P.N.M. y S. N° 35 · precios al {FECHA} · dólar BNA $ {DOLAR:,.0f}".replace(",", ".")
        ws["A2"].font = Font(italic=True, size=9)
        for j, h in enumerate(encabezado, 1):
            c = ws.cell(row=4, column=j, value=h)
            c.font = Font(bold=True); c.fill = cab; c.border = borde
            c.alignment = Alignment(wrap_text=True, vertical="center")
        for i, fila in enumerate(filas, 5):
            for j, v in enumerate(fila, 1):
                c = ws.cell(row=i, column=j, value=v)
                c.border = borde
                c.alignment = Alignment(wrap_text=True, vertical="top")
                if formatos and formatos[j - 1]:
                    c.number_format = formatos[j - 1]
                if "LAR" in str(fila) and nombre != "Pedido LAR":
                    c.fill = lar_fill
        if total:
            r = len(filas) + 5
            for j, v in enumerate(total, 1):
                c = ws.cell(row=r, column=j, value=v)
                c.font = Font(bold=True); c.border = borde
                if formatos and formatos[j - 1]:
                    c.number_format = formatos[j - 1]
        for j, w in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = "A5"
        return ws

    inv = res["inversion"]
    ws = wb.active
    ws.title = "Resumen"
    ws["A1"] = "Presupuesto de la planta de secado de guano 8 t/día – Resumen"
    ws["A1"].font = Font(bold=True, size=14)
    filas = [("Planta de secado (Rev. C, con el secador por despiece)", inv["sub_revC"]),
             ("Ampliación Rev. D/E (limpieza, envasado, depósito, biogás, ventilación, seguridad, incendio, TG2)", inv["sub_revD"]),
             ("Ingeniería y habilitaciones", inv["sub_ing"]), ("Imprevistos (7 %)", inv["imprevistos"]),
             ("TOTAL INVERSIÓN (USD)", inv["total"]), ("TOTAL INVERSIÓN ($, dólar BNA)", inv["total_ARS"]),
             ("Variante sin biogás (USD)", inv["sin_biogas"]),
             ("Pedido de cotización a LAR (materiales, $)", res["lar"]["total_ARS"]),
             ("Energía con LAR, costo anual sin cogeneración (USD)", res["energia"]["costo_sin_G1_USD"]),
             ("Energía con LAR, costo anual con cogeneración (USD)", res["energia"]["costo_con_G1_USD"]),
             ("Beneficio neto anual (USD)", res["evaluacion"]["neto"]),
             ("VAN 15 años al 10 % (USD)", res["evaluacion"]["VAN"]), ("TIR (%)", res["evaluacion"]["TIR"]),
             ("Repago simple (años)", res["evaluacion"]["repago"])]

    for i, (a, b) in enumerate(filas, 3):
        ws.cell(row=i, column=1, value=a).border = borde
        c = ws.cell(row=i, column=2, value=b); c.border = borde; c.number_format = "#,##0.0" if isinstance(b, float) and b < 100 else "#,##0"
        if "TOTAL" in a:
            ws.cell(row=i, column=1).font = Font(bold=True); c.font = Font(bold=True)
    ws.column_dimensions["A"].width = 88
    ws.column_dimensions["B"].width = 20
    ws.cell(row=len(filas) + 4, column=1, value="Precisión de anteproyecto ± 25 %. Fuentes de precios en la hoja «Fuentes».").font = Font(italic=True)

    hoja("Inversión", "Presupuesto de inversión", ["Cód.", "Rubro", "Descripción", "Cant.", "Unid.", "USD unit.", "USD total", "Proveedor", "Fuente"],
         [list(f) for f in inv["filas"]], [6, 16, 70, 7, 6, 11, 12, 30, 8], [None, None, None, "#,##0", None, "#,##0", "#,##0", None, None],
         ["", "", "TOTAL (sin imprevistos)", "", "", "", inv["sub_revC"] + inv["sub_revD"] + inv["sub_ing"], "", ""])
    sec = res["secador"]
    hoja("Secador", "Despiece y costo del secador SC-4", ["Descripción", "Cant.", "Unid.", "USD unit.", "USD total", "Proveedor", "Fuente"],
         [list(f) for f in sec["filas"]], [70, 8, 6, 11, 12, 34, 8], [None, "#,##0", None, "#,##0.00", "#,##0", None, None],
         ["TOTAL SECADOR", "", "", "", sec["total"], "", ""])
    lar = res["lar"]
    hoja("Pedido LAR", "Pedido de cotización a la Cooperativa La Agrícola Regional (LAR) – Crespo",
         ["Sección LAR", "Ítem", "Cant.", "Unid.", "$ unit. referencia", "$ total referencia", "Cantidad sale de", "$ cotizado LAR", "Observaciones LAR"],
         [list(f) + ["", ""] for f in lar["filas"]], [18, 62, 9, 7, 16, 17, 36, 16, 24],
         [None, None, "#,##0", None, "#,##0", "#,##0", None, "#,##0", None],
         ["", "TOTAL DE REFERENCIA", "", "", "", lar["total_ARS"], "", "", ""])
    en = res["energia"]
    hoja("Energía LAR", "Costo anual de la energía eléctrica (LAR distribuidora, tarifa T3 grandes demandas BT)",
         ["Concepto", "Valor", "Unidad"],
         [["Energía del TGF (54 kW × 8 h × 250 d)", en["E_TGF_kWh"], "kWh/año"],
          ["Energía del TG2 (demanda + iluminación)", en["E_TG2_kWh"], "kWh/año"],
          ["Energía total", en["E_total_kWh"], "kWh/año"],
          ["Generación de G1 (biogás)", en["E_G1_kWh"], "kWh/año"],
          ["Autoconsumo de G1 / inyección a la red", f"{en['autoconsumo_kWh']} / {en['inyectada_kWh']}", "kWh/año"],
          ["Potencia contratada", en["potencia_kW"], "kW"],
          ["Cargo fijo (estimado)", en["tarifa"]["cargo_fijo_mes"], "$/mes"],
          ["Cargo por potencia (estimado)", en["tarifa"]["potencia_kw_mes"], "$/kW·mes"],
          ["Cargo por energía (estimado)", en["tarifa"]["energia_kwh"], "$/kWh"],
          ["Costo anual sin cogeneración", en["costo_sin_G1_ARS"], "$/año"],
          ["Costo anual con cogeneración", en["costo_con_G1_ARS"], "$/año"],
          ["Ahorro por la cogeneración", en["ahorro_G1_USD"], "USD/año"]],
         [52, 18, 12], [None, "#,##0", None])
    ev = res["evaluacion"]
    hoja("Evaluación", "Costos operativos, ingresos y evaluación (15 años, 10 %)", ["Concepto", "USD/año"],
         [["Ventas de guano seco (60 % bolsas 25 kg USD 250/t, 15 % bolsas chicas USD 600/t, 25 % granel USD 130/t)", ev["ventas"]],
          ["Fracción sólida del digestato (USD 20/t)", ev["digestato"]], ["Sulfato de amonio del lavador", ev["sulfato"]],
          ["Ahorros de gestión del guano y sanitarios", ev["ahorro_gestion"]], ["TOTAL INGRESOS", ev["ingresos"]]]
         + [[k, -v] for k, v in ev["costos"].items()] + [["TOTAL COSTOS", -ev["costo"]], ["BENEFICIO NETO", ev["neto"]],
                                                        ["VAN (USD)", ev["VAN"]], ["TIR (%)", ev["TIR"]], ["Repago (años)", ev["repago"]]],
         [92, 14], [None, "#,##0"])
    hoja("Fuentes", "Fuentes de los precios", ["Clave", "Fuente"], [[k, v] for k, v in res["fuentes"].items()], [10, 130])
    wb.save(ruta)


def main():
    res = calcular()
    with open(os.path.join(AQUI, "presupuesto.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    carpeta = os.path.join(RAIZ, "presupuesto")
    os.makedirs(carpeta, exist_ok=True)
    planilla(res, os.path.join(carpeta, "Presupuesto_Secadora_Guano.xlsx"))
    inv, ev, en = res["inversion"], res["evaluacion"], res["energia"]
    print(f"Secador SC-4: USD {res['secador']['total']:,}")
    print(f"Inversión: Rev C {inv['sub_revC']:,} + Rev D {inv['sub_revD']:,} + ing {inv['sub_ing']:,} + imprev {inv['imprevistos']:,} = USD {inv['total']:,} (${inv['total_ARS']:,}); sin biogás {inv['sin_biogas']:,}")
    print(f"Pedido LAR: ${res['lar']['total_ARS']:,} (USD {res['lar']['total_USD']:,})")
    print(f"Energía: {en['E_total_kWh']:,} kWh/año; sin G1 USD {en['costo_sin_G1_USD']:,}, con G1 USD {en['costo_con_G1_USD']:,}; precio medio ${en['precio_medio_ARS_kWh']}/kWh")
    for e in ev["escenarios"]:
        print("  ", e)
    print(f"Evaluación: ingresos {ev['ingresos']:,} costos {ev['costo']:,} neto {ev['neto']:,} VAN {ev['VAN']:,} TIR {ev['TIR']} repago {ev['repago']}")


if __name__ == "__main__":
    main()
