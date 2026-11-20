"""Memoria técnica de la granja integrada (Word + PDF), escrita desde los mismos datos que los planos y el 3D.

    python memoria_gi.py        # -> ../memoria/Memoria_tecnica_granja_integrada.docx y .pdf

Usa la clase Memoria del proyecto anterior (fuente/calculos/memoria_docx.py, solo lectura) para escribir a la vez el
Word y el HTML del PDF, con el mismo formato que la memoria de cálculo de la Rev. D. Los números salen de
datos/granja.json, datos/calculos.json, datos/electrica.json y datos/piezas.json; los valores preliminares se marcan
con (P) y las hipótesis con (H), como en el resto del proyecto.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent                                              # granja_integrada/
ANTERIOR = RAIZ.parent                                          # proyecto anterior (solo lectura)
sys.path.insert(0, str(ANTERIOR / "fuente" / "calculos"))
sys.path.insert(0, str(AQUI / "modelo"))

import memoria_docx as MD  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Pt, RGBColor  # noqa: E402

D = json.loads((RAIZ / "datos" / "granja.json").read_text(encoding="utf-8"))
K = json.loads((RAIZ / "datos" / "calculos.json").read_text(encoding="utf-8"))
E = json.loads((RAIZ / "datos" / "electrica.json").read_text(encoding="utf-8"))
PZ = json.loads((RAIZ / "datos" / "piezas.json").read_text(encoding="utf-8"))
SALIDA = RAIZ / "memoria" / "Memoria_tecnica_granja_integrada.docx"
PLANOS = RAIZ / "planos"
RENDERS = RAIZ / "renders"
ENCABEZADO = "Granja integrada · secado de guano y 4 galpones – Memoria técnica Rev. A"
c = MD.c
B = K["balance"]
V = K["ventilacion"]
ENT = K["entradas"]
T_ = {t["id"]: t for t in K["transportadores"]}
TR = {t["id"]: t for t in D["transporte"]}


def fmt(v, d=1):
    return c(v, d)


def ent(k, d=2):
    e = ENT[k]
    return f"{c(e['valor'], d)} ({e['tipo']})"


# ===================================================================================== portada e índice
def portada(m):
    for _ in range(2):
        m.p()
    m.p(MD.ESCUELA, negrita=True, centrado=True, tam=14)
    m.p(MD.LUGAR, centrado=True)
    m.p("Especialidad Electromecánica · 7.° año", centrado=True)
    m.p("Materia: (completar)", centrado=True, resaltar=True)
    m.p("Docente: (completar)", centrado=True, resaltar=True)
    for _ in range(3):
        m.p()
    m.p("PROYECTO FINAL", negrita=True, centrado=True, tam=13)
    m.p("Granja avícola integrada con planta central de secado de guano", negrita=True, centrado=True, tam=20)
    m.p("Memoria técnica – Revisión A", negrita=True, centrado=True, tam=16)
    m.p("4 galpones automáticos de 36.000 gallinas · transporte automático del guano · secador SC-4 (Rev. F) · "
        "instalación eléctrica · automatización · modelo 3D y planos GI-01 a GI-20", centrado=True, tam=11)
    for _ in range(4):
        m.p()
    m.p("Integrantes", negrita=True, centrado=True)
    for n in MD.INTEGRANTES:
        m.p(n, centrado=True)
    for _ in range(2):
        m.p()
    m.p(f"{MD.LUGAR} – noviembre de 2026", centrado=True)
    m.salto()
    m.h("Índice", 1, indice=False)
    MD.campo(m.d.add_paragraph(), 'TOC \\o "1-3" \\h \\z \\u')
    m.html.append('<div id="indice">__INDICE__</div>')
    m.salto()


def encabezado_pie(m):
    sec = m.d.sections[0]
    sec.different_first_page_header_footer = True
    hp = sec.header.paragraphs[0]
    hp.text = ENCABEZADO
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.runs[0].font.size = Pt(8.5)
    hp.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("Página ").font.size = Pt(9)
    MD.campo(fp, "PAGE")


def reducir(ruta, ancho_px=2000):
    """Copia liviana (JPG de 2.000 px de ancho) para el Word y el PDF; las láminas quedan en su resolución original."""
    from PIL import Image
    dst = SALIDA.parent / "_fig" / (ruta.stem + ".jpg")
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(ruta).convert("RGB")
    if im.width > ancho_px:
        im = im.resize((ancho_px, round(im.height * ancho_px / im.width)), Image.LANCZOS)
    im.save(dst, quality=86, optimize=True)
    return dst


def figura(m, ruta, epigrafe, ancho=16):
    ruta = Path(ruta)
    if ruta.exists():
        m.figura(str(reducir(ruta)), epigrafe, ancho)
    else:
        m.p(f"(Falta la figura {ruta.name}: se genera con fuente/render/.)", cursiva=True)


# ===================================================================================== 1. objeto
def objeto(m):
    m.h("1. Objeto, alcance y criterio")
    m.p("Esta memoria describe el rediseño de la planta de secado de guano de la Rev. F como planta central de una granja "
        "de gallinas ponedoras de cuatro galpones automáticos de 36.000 aves cada uno, con transporte automático del "
        "guano desde las cintas de las jaulas hasta la tolva pulmón de la planta, sin palas cargadoras ni camiones. "
        "El sistema de biogás de la Rev. D se elimina por completo. El secador SC-4, la nave de proceso y los equipos "
        "de la Rev. F se conservan como base; solo se agregan las interfaces necesarias y se proponen, marcadas como (P), "
        "las adecuaciones que el caudal nuevo exige aguas abajo del secador.")
    m.h("1.1 Alcance", 2)
    m.lista([
        "Implantación general con la fila Oeste-Este G1, G2, planta, G3, G4 y las zonas limpia y sucia (lámina GI-01).",
        "Galpones automáticos reutilizando el proyecto San Jorge: jaulas, cintas de guano, agua, alimento, huevos, "
        "ventilación de túnel y cabecera de guano (GI-02 y GI-03).",
        "Transporte automático del guano: cintas transversales, inclinadas, colectoras y principales, torres de "
        "transferencia con desviadora y contenedor de emergencia (GI-04 a GI-06).",
        "Recepción automática en la tolva pulmón TP-01 con fondo vivo de cuatro sinfines y pesaje (GI-07 y GI-18).",
        "Nave de proceso y secador SC-4 de la Rev. F con su integración (GI-08 a GI-10).",
        "Instalación eléctrica de la planta y del transporte, con las conexiones del guano en cada galpón (GI-12 a GI-14).",
        "Automatización: PLC, periferias, red, secuencia, enclavamientos, fallas, lazos e instrumentos (GI-11, GI-15 a GI-17).",
        "Modelo 3D completo (GLB y STEP), renders, despieces numerados (GI-18 a GI-20) y 20 láminas A3 en DXF y PDF.",
    ])
    m.h("1.2 Tipos de dato", 2)
    m.p("Cada valor lleva su origen, para separar lo calculado de lo propuesto y de lo que falta confirmar:")
    m.tabla("Tipos de dato usados en todo el proyecto", [
        ["Letra", "Significado"],
        ["R", "Del proyecto de la secadora (Rev. F, 11/11/2026): diseño calculado, no medido"],
        ["S", "Del proyecto San Jorge (relevado en el establecimiento o en la imagen satelital)"],
        ["V", "Verificado con una fuente externa citada"],
        ["P", "Preliminar: propuesta de este rediseño, con su criterio; a confirmar con el fabricante o en obra"],
        ["H", "Hipótesis: no hay dato publicado ni relevado; se indica cómo confirmarlo"],
    ], anchos=[2, 14], alin=["C", "L"])
    m.h("1.3 Normas y referencias", 2)
    m.lista([
        "AEA 90364-7-771 (instalaciones en inmuebles) y sección 705 (establecimientos agropecuarios) para los galpones; "
        "IEC 60364-5-52 para las corrientes admisibles y los factores de agrupamiento.",
        "AEA 95101 para las líneas subterráneas; IRAM 2178 para los cables de potencia; IRAM 2184 para la protección contra rayos.",
        "IEC 60909 para el cálculo de cortocircuito; IEC 61439 para los tableros; IEC 60034-30-1 para la eficiencia de los motores.",
        "DIN 22101 para las cintas transportadoras (método del coeficiente C) y CEMA 350 para los sinfines.",
        "IEC 60848 (GRAFCET) para la secuencia; IEC 62061 e ISO 13849-1 para las funciones de seguridad.",
        "Láminas en formato A3 según IRAM 4504, con el método de proyección ISO E de la IRAM 4501.",
        "Resolución SENASA 1699/2019 (bioseguridad de establecimientos avícolas comerciales): distancias y cercos a verificar.",
        "Reglamento (UE) 142/2011, anexo XI, tomado por la Rev. F para la higienización del producto (≥ 70 °C durante 60 min).",
    ])


# ===================================================================================== 2. biogás
def biogas(m):
    m.h("2. Eliminación del sistema de biogás")
    m.p("Antes de sacar cada elemento se revisó qué otros sistemas dependían de él. Ninguna función de la planta queda sin "
        "resolver: el guano que iba al biodigestor vuelve al secador, el encendido del hogar pasa a GLP y el circuito que "
        "alimentaba al tablero del biogás se reutiliza para el tablero nuevo del transporte.")
    quitados = [mo for mo in E["motores"] if mo["estado"].startswith("se quita")]
    glp = next(x for x in D["servicios"] if x["id"] == "GLP")
    v_glp = math.pi * (glp["D"] / 2) ** 2 * glp["L"] + 4 / 3 * math.pi * (glp["D"] / 2) ** 3
    m.tabla("Elementos del biogás y de la recepción por camión que se eliminan", [
        ["Elemento", "Acción", "Cómo se resuelve la dependencia"],
        ["Recepción, biodigestores BD-1 y BD-2, digestato, cogeneración y antorcha (E8.1 a E8.5)", "Se eliminan",
         "El guano vuelve al secador; la demanda eléctrica se cubre desde la red"],
        ["Línea de biogás al hogar y quemador piloto (E8.6)", "Se elimina",
         f"Piloto a GLP con tanque de {fmt(v_glp, 1)} m³ (Ø{fmt(glp['D'], 1)} × {fmt(glp['L'], 2)} m), regulador, "
         "2 electroválvulas y presostato (P)"],
        ["Tablero TS-BIO (salida Q23 del TG2)", "Se elimina", "El Q23 alimenta al TS-GU del transporte de guano"],
        ["Proyectores Ex de la zona de biogás (Q25)", "Se eliminan", "Desaparece la única zona clasificada de la planta"],
        ["Playa de recepción, tolva de 3,1 m³ y vibrador M15", "Se eliminan", "La recepción pasa a la tolva pulmón TP-01"],
        [f"Motores quitados ({len(quitados)})", "Se eliminan", ", ".join(mo["tag"] for mo in quitados)],
    ], anchos=[6, 2.4, 7.6], alin=["L", "C", "L"])


# ===================================================================================== 3. implantación
def implantacion(m):
    m.h("3. Implantación general")
    pr = D["predio"]
    g = D["galpon"]
    m.p(f"La granja se ordena en una fila de Oeste a Este: G1, G2, la planta de secado, G3 y G4. Las cabeceras de guano "
        f"de los galpones miran al Sur, hacia la línea de transporte, y las de huevos al Norte, hacia los depósitos DH-O y "
        f"DH-E. El predio dentro del cerco mide {fmt(pr['x1'] - pr['x0'], 0)} × {fmt(pr['y1'] - pr['y0'], 1)} m. La planta "
        "queda dentro de un cerco sanitario propio (zona sucia), con acceso de servicio separado de la zona limpia de "
        "galpones, huevos y alimento. La subestación y el estacionamiento quedan afuera del cerco, junto al ingreso único "
        "con vado y vestuarios de bioseguridad.")
    m.p(f"Los dos galpones de cada lado están a {fmt(g['eje_par'], 0)} m entre ejes, con el eje largo en dirección "
        "Norte-Sur. La ventilación de túnel toma aire por los paneles evaporativos del extremo Norte (lado limpio, de los "
        "huevos) y lo saca por los ventiladores del testero Sur: el aire usado, el polvo y el olor salen del lado del guano "
        "y de la línea de transporte, lejos de los depósitos de huevos. Desagüe pluvial (P): canaletas y bajadas en los "
        "techos y cunetas a los costados de los caminos internos hacia el bajo natural del predio, a definir con la "
        "planialtimetría; los paneles evaporativos tienen su canaleta colectora con retorno al tanque.")
    figura(m, PLANOS / "GI-01.png", "Implantación general de la granja (lámina GI-01)", 16)
    m.p("Coordenadas: en metros, con origen en el vértice Sudoeste de la nave de proceso (el mismo de la Rev. F), x hacia el "
        "Este e y hacia el Norte. Las cotas de nivel se miden desde el piso de la nave (±0,00).")


# ===================================================================================== 4. galpones
def galpones(m):
    g, j = D["galpon"], D["jaulas"]
    m.h("4. Galpones automáticos")
    m.p(f"Se reutiliza el galpón del proyecto San Jorge (S): nave de {fmt(g['L'], 0)} × {fmt(g['A'], 1)} m con alero a "
        f"+{fmt(g['h_alero'], 2)} m y techo a dos aguas de {fmt(g['pendiente_deg'], 0)}°, con {j['filas']} filas de jaulas de "
        f"{j['pisos']} pisos y {j['modulos_por_fila']} módulos de {fmt(j['modulo'], 2)} m por fila. Cada celda de "
        f"{fmt(j['celda_ancho'], 3)} × {fmt(j['celda_prof'], 3)} m aloja {j['aves_por_celda']} gallinas "
        f"({fmt(B['densidad_cm2_ave'], 0)} cm² por ave), lo que da {fmt(j['aves_por_galpon'], 0)} gallinas por galpón.")
    m.p(f"Debajo de cada piso corre una cinta de guano de polipropileno de {fmt(j['cinta_guano_ancho'], 2)} m a "
        f"{fmt(j['cinta_guano_v_m_min'], 0)} m/min. Las 20 cintas de cada galpón (4 filas × 5 pisos) descargan en la cabecera "
        "Sur sobre una cinta transversal CT en un canal de hormigón, que entrega a la cinta inclinada CI. El motorreductor de "
        "cada cinta de piso (1,1 kW, P) queda en la cabecera, con su botonera de fila y parada de emergencia.")
    m.h("4.1 Agua, alimento y huevos", 2)
    m.p("Los sistemas del galpón que no son el guano se toman del proyecto San Jorge (S) y los define el integrador del "
        "galpón; acá se dimensionan sus cargas y se ubican en el 3D:")
    m.lista([
        "Agua: líneas de bebederos de niple en cada piso, alimentadas por un colector de PEAD Ø32 con bajada a los "
        "reguladores de presión de cada fila. La sala de servicio del galpón tiene el tablero TS-G y el controlador ambiental.",
        f"Alimento: dos silos de 15 t por galpón (SA-Gx-1 y SA-Gx-2) sobre el lateral, cerca de la cabecera Norte, con sinfín "
        f"Ø90 a las tolvas de los carros de alimentación de cada fila; consumo de {fmt(B['alimento_t_dia_galpon'], 2)} t por "
        f"día y galpón (110 g por gallina), de modo que los dos silos cubren unos "
        f"{fmt(30 / B['alimento_t_dia_galpon'], 1)} días.",
        f"Huevos: cinta de huevos de {fmt(j['cinta_huevos_ancho'] * 1000, 0)} mm en cada piso, elevador de huevos en la "
        f"cabecera Norte de cada fila, cinta transversal de 300 mm y galería aérea cubierta hasta la estación de armado del "
        f"depósito DH-O o DH-E: {fmt(B['huevos_dia'], 0)} huevos por día con 90 % de postura (S), "
        f"{fmt(B['cajones_dia'], 0)} cajones de 360 huevos y {fmt(B['palets_dia'], 1)} palets de 25 cajones por día "
        f"({fmt(B['palets_dia_por_deposito'], 1)} por depósito), que se guardan con el transelevador del depósito.",
    ])
    m.tabla("Ventilación de túnel de cada galpón", [
        ["Concepto", "Valor", "Criterio"],
        ["Caudal de verano", f"{fmt(V['caudal_verano_m3h'], 0)} m³/h", f"{fmt(ENT['vent_m3h_ave']['valor'], 1)} m³/h por gallina (V)"],
        ["Ventiladores de 50\"", f"{V['ventiladores_50']} ({fmt(V['caudal_instalado_m3h'], 0)} m³/h)",
         f"{V['ventiladores_cabecera']} en el testero Sur y {V['ventiladores_laterales_por_lado']} por lateral; 36.000 m³/h c/u a 25 Pa (P)"],
        ["Sección y velocidad en el túnel", f"{fmt(V['seccion_m2'], 1)} m² · {fmt(V['velocidad_tunel_m_s'], 2)} m/s", "entre 1,0 y 2,5 m/s"],
        ["Ventilación mínima", f"{fmt(V['caudal_minimo_m3h'], 0)} m³/h con {V['ventiladores_36']} ventiladores de 36\"",
         "1 m³/h por gallina (V)"],
        ["Panel evaporativo (extremo Norte)", f"{fmt(V['panel_evaporativo_m2'], 1)} m² ({fmt(V['panel_por_lado_m'], 1)} m por lado × 1,8 m)",
         "1,8 m/s de velocidad frontal (P)"],
    ], anchos=[5, 6, 5], alin=["L", "L", "L"])
    figura(m, PLANOS / "GI-03.png", "Corte transversal del galpón tipo (lámina GI-03)", 16)


# ===================================================================================== 5. balance
def balance(m):
    m.h("5. Balance de guano y de producto")
    m.p("El guano fresco de cada galpón sale del dato de la secadora: 8 t/día para 60.000 aves (R).")
    m.ec("m = N · g", ["m: guano fresco (kg/día)", "N: gallinas", f"g = {fmt(ENT['guano_kg_ave_dia']['valor'], 3)} kg por gallina y día (R)"])
    m.calculo(f"m = {fmt(B['aves_por_galpon'], 0)} · {fmt(ENT['guano_kg_ave_dia']['valor'], 3)}",
              f"{fmt(B['guano_galpon_kg_dia'], 0)} kg/día por galpón; {fmt(B['guano_total_kg_dia'], 0)} kg/día los cuatro")
    m.ec("m_out = m_in · (1 − X_in) / (1 − X_out)", ["X_in = 0,72 (R)", "X_out = 0,15 (R): humedades del guano y del producto"])
    m.calculo(f"m_out = {fmt(B['guano_total_kg_dia'], 0)} · 0,28 / 0,85",
              f"{fmt(B['producto_seco_kg_dia'], 0)} kg/día de producto; agua evaporada {fmt(B['agua_evaporada_kg_dia'], 0)} kg/día")
    m.p(f"Con la alimentación de diseño del SC-4 (1.000 kg/h, R) harían falta {fmt(B['guano_total_kg_dia'] / 1000, 1)} h por "
        "día, más que los dos turnos. Se adopta un régimen que entra en 16 h con 95 % de disponibilidad (P) y se interpola la "
        "temperatura del aire entre los dos puntos de la Rev. F (1.000 kg/h a 100 °C y 1.440 kg/h a 135 °C):")
    m.ec("m_reg = m_día / (h · d)        T = 100 + (m_reg − 1.000) / 440 · 35",
         ["h = 16 h (P)", "d = 0,95 (P)"])
    m.calculo(f"m_reg = {fmt(B['guano_total_kg_dia'], 0)} / (16 · 0,95)",
              f"{fmt(B['secador_kg_h_regimen'], 0)} kg/h con aire a {fmt(B['T_aire_regimen_C'], 0)} °C; reserva "
              f"{fmt(B['reserva_secador_pct'], 1)} % hasta los 1.440 kg/h")
    prod_h = B["secador_kg_h_regimen"] * 0.28 / 0.85
    m.p(f"Al régimen adoptado salen {fmt(prod_h, 0)} kg/h de producto seco (329 kg/h en la Rev. F); la sección 8 verifica "
        "los equipos de la Rev. F que quedan aguas abajo con ese caudal.")
    m.p(f"Cada cinta de piso lleva {fmt(B['guano_por_cinta_kg'], 1)} kg ({fmt(B['guano_kg_por_m_de_cinta'], 2)} kg por metro). "
        f"Corriendo las 4 filas de un piso a la vez, el caudal es {fmt(B['flujo_por_piso_t_h'], 2)} t/h y un piso tarda "
        f"{fmt(B['tiempo_por_piso_min'], 1)} min; un galpón completo, unos {fmt(B['tiempo_por_galpon_min'], 0)} min. La secuencia "
        f"vacía un galpón por vez en cada lado; con los dos lados a la vez llegan a la TP-01 hasta "
        f"{fmt(B['flujo_lado_simultaneo_t_h'], 2)} t/h. Las colectoras y las principales se dimensionan para dos galpones por "
        f"lado, como reserva. La tolva pulmón de {fmt(B['tolva_pulmon_m3'], 0)} m³ guarda {fmt(B['tolva_pulmon_dias'], 2)} días "
        "de guano con densidad 950 kg/m³ (H, a medir).")
    m.tabla("Resumen del balance diario", [
        ["Concepto", "Valor"],
        ["Gallinas", fmt(B["aves_total"], 0)],
        ["Guano fresco (72 %)", f"{fmt(B['guano_total_kg_dia'], 0)} kg/día"],
        ["Producto seco (15 %)", f"{fmt(B['producto_seco_kg_dia'], 0)} kg/día ({fmt(prod_h, 0)} kg/h en régimen)"],
        ["Agua evaporada", f"{fmt(B['agua_evaporada_kg_dia'], 0)} kg/día"],
        ["Régimen del SC-4", f"{fmt(B['secador_kg_h_regimen'], 0)} kg/h · {fmt(B['T_aire_regimen_C'], 0)} °C · "
                             f"{B['secador_turnos']} turnos"],
        ["Huevos", f"{fmt(B['huevos_dia'], 0)} por día ({fmt(B['palets_dia'], 1)} palets)"],
    ], anchos=[8, 8], alin=["L", "R"])
    figura(m, PLANOS / "GI-11.png", "Diagrama de flujo del proceso y balance (lámina GI-11)", 16)


# ===================================================================================== 6. transporte
def transporte(m):
    m.h("6. Transporte automático del guano")
    m.p("Cada galpón entrega su guano por una cadena continua de cintas, sin transportadores desconectados: cinta transversal "
        "CT en el canal de la cabecera, cinta inclinada CI que sube a la galería, colectora CE del lado (Oeste u Este) que "
        "recibe los dos galpones, torre de transferencia TT con desviadora y cinta principal CP que entra a la nave hasta el "
        "pórtico de cabezales PC-01, sobre la tolva pulmón TP-01. Las galerías apoyan en caballetes cada 11 m como máximo, "
        "fuera de los caminos internos, y tienen pasarela, baranda y cable de parada en todo su largo. Cada cinta tiene tensor "
        "a tornillo en la cola, rascador primario y secundario en la cabeza y chute con puerta de inspección (GI-19).")
    m.h("6.1 Elección del sistema", 2)
    m.tabla("Sistemas de transporte evaluados para el guano fresco (72 % de humedad, pegajoso)", [
        ["Sistema", "A favor", "En contra para el guano fresco", "Decisión"],
        ["Cinta plana o en artesa; con bordes y tacos para subir", "Poco consumo y desgaste; acepta material pegajoso con "
         "rascadores; es el mismo sistema de las jaulas; sube a 45-60° con bordes y tacos", "Limpieza del retorno; galerías largas",
         "Adoptado"],
        ["Sinfín (tornillo)", "Cerrado y compacto", "Mucho consumo y desgaste en tramos largos; el guano húmedo se pega y "
         "forma tapones; malo en pendiente", "Solo como dosificador corto (fondo de la TP-01)"],
        ["Cadena de arrastre", "Cerrado; acepta pendiente", "Desgaste de cadena con material húmedo y abrasivo; ruido y "
         "mantenimiento", "Descartado"],
        ["Elevador de cangilones", "Vertical, poco espacio", "El material pegajoso no se descarga bien; necesita carga pareja",
         "Descartado (se usa para el producto seco, M11)"],
        ["Neumático", "Sin partes móviles en la línea", "No sirve para material húmedo y pegajoso; mucho consumo", "Descartado"],
    ], anchos=[3.4, 4.6, 5, 3], alin=["L", "L", "L", "L"])
    ci = TR["CI-1"]["trazado"]
    sube, horiz = ci[-1][2] - ci[-2][2], math.dist(ci[-2][:2], ci[-1][:2])
    m.p(f"La inclinada sube {fmt(sube, 2)} m en {fmt(horiz, 2)} m de horizontal ({fmt(math.degrees(math.atan2(sube, horiz)), 1)}°): "
        "entre el muro Sur del galpón y la colectora no hay más lugar, y una pendiente de 30° llevaría el pie de la cinta "
        "adentro del galpón o correría toda la línea de transporte hacia el Sur. Por eso se usa banda con bordes ondulados y "
        "tacos, que es la solución habitual entre 45° y 60°.")
    m.h("6.2 Método de cálculo", 2)
    m.p("La potencia se calculó con la DIN 22101 por el método del coeficiente C. Los resultados de potencia son "
        "preliminares (P): alcanzan para dimensionar la instalación y se confirman con el fabricante.")
    m.ec("A = b² · tg θ / 6        b = 0,9 · B − 0,05        Q = A · v · k · 3.600 · ρ",
         ["A: sección de la carga en cintas planas o en artesa (m²)", "B: ancho de banda (m)", "θ = 20°: ángulo de sobrecarga (P)",
          "v: velocidad (m/s)", "k: reducción por inclinación", "ρ = 950 kg/m³ (H)"])
    m.p("En las inclinadas el guano lo sostienen los tacos: se toma el volumen de cada bolsillo con la superficie libre "
        "horizontal, sin sobrecarga (del lado seguro), por el ancho útil entre bordes.")
    m.ec("A_t = h² / (2 · tg δ)        Q = A_t · w · (v / p) · 3.600 · ρ",
         ["h = 110 mm: altura de los tacos (P)", "p = 250 mm: paso de los tacos", "w = 0,39 m: ancho útil entre bordes de 120 mm",
          "δ: inclinación del tramo"])
    m.ec("F_H = C · f · L · g · [q_RO + q_RU + (2 · q_B + q_G) · cos δ]",
         ["C: coeficiente de resistencias secundarias (tabla de la DIN 22101)", "f = 0,025", "q_RO = 4,5 kg/m y q_RU = 1,1 kg/m: "
          "rodillos", "q_B: banda (P)", "q_G = Q / (3,6 · v): carga (kg/m)"])
    m.ec("P = (F_H + F_St + F_S) · v / η", ["F_St = q_G · H · g: fuerza para subir la carga", "F_S: rascadores y faldones (P)",
                                            "η = 0,85: rendimiento del motorreductor"])
    m.p("Caudales de diseño (P): en cada galpón corre un piso por vez con sus cuatro filas, con 25 % de margen; las "
        "colectoras y las principales se calculan para los dos galpones de su lado a la vez (reserva).")
    filas = [["Cinta", "Tipo", "L (m)", "B (mm)", "v (m/s)", "Q dis./cap. (t/h)", "P req. (kW)", "Motor (kW)", "Tambor"]]
    for t in K["transportadores"]:
        filas.append([t["id"], t["tipo"], fmt(t["L_m"], 1), f"{t['B_m'] * 1000:.0f}", fmt(t["v_m_s"], 2),
                      f"{fmt(t['Q_diseno_t_h'], 0)} / {fmt(t['Q_capacidad_t_h'], 1)}", fmt(t["P_requerida_kW"], 2),
                      fmt(t["motor_kW"], 2), f"Ø{t['tambor_D_m'] * 1000:.0f} · i ≈ {fmt(t['relacion_reductor'], 0)}"])
    m.tabla("Transportadores de guano (DIN 22101, potencias preliminares P)", filas,
            anchos=[1.4, 2.1, 1.3, 1.3, 1.3, 2.6, 1.7, 1.7, 2.6], alin=["C", "L", "R", "R", "R", "C", "R", "R", "C"])
    ok = all(t["verifica_capacidad"] for t in K["transportadores"])
    m.p(("Todas las cintas tienen capacidad mayor que el caudal de diseño, también las inclinadas con el método de los "
         "bolsillos. " if ok else "ATENCIÓN: hay cintas sin capacidad suficiente. ") +
        "Las colectoras y principales giran a 0,50 m/s con variador (arranque suave y velocidad ajustable); las "
        "transversales y las inclinadas, con arranque directo o variador según se indica en la lista de motores. El tambor "
        "motriz es de Ø400 mm en las bandas de 650 mm y de Ø320 mm en las de 500 mm, igual que en el modelo 3D.")
    tt = D["torres"][0]
    m.h("6.3 Torres de transferencia y desviadoras", 2)
    m.p(f"Cada torre (TT-O y TT-E) es una estructura de {fmt(tt['A'], 1)} × {fmt(tt['B'], 1)} m de columnas HEB 160 con "
        f"plataforma de rejilla a +{fmt(tt['z_plataforma'], 2)} m, techo a +8,20 m y escalera a 42°. Adentro, la colectora "
        f"descarga en la desviadora {tt['desviadora']}: en posición A el guano sigue a la cinta principal; en posición B cae "
        f"por un chute a {tt['chute_ang']}° hasta la boca de emergencia (+{fmt(tt['boca_emergencia_z'], 2)} m) y llena el "
        f"contenedor volquete {tt['contenedor']['id']} de {fmt(tt['contenedor']['cap_m3'], 0)} m³. La posición B solo se "
        "habilita con el secador parado y por orden del operador; los finales ZSA y ZSB confirman la posición y, sin "
        "confirmación, la colectora no arranca.")
    figura(m, PLANOS / "GI-04.png", "Planta general del transporte y detalles (lámina GI-04)", 16)
    figura(m, PLANOS / "GI-05.png", "Elevaciones de los dos lados y perfil de la cinta inclinada (lámina GI-05)", 16)
    figura(m, PLANOS / "GI-06.png", "Torre de transferencia TT-O: planta y cortes (lámina GI-06)", 16)


# ===================================================================================== 7. recepción
def recepcion(m):
    tp = D["tolva_pulmon"]
    sf = tp["sinfines"]
    m.h("7. Recepción automática: tolva pulmón TP-01")
    m.p("Se eligió una tolva central y no una por galpón. El secador necesita un caudal parejo durante 16 h y una tolva "
        "central lo da con un solo punto de dosificación y pesaje, una sola aspiración al biofiltro y una sola línea de "
        "alimentación (la M8 de la Rev. F). Con cuatro tolvas habría cuatro dosificadores y cuatro pesajes, el transporte "
        "debería andar las 16 h para alimentar al secador desde cada galpón (más desgaste y consumo) y habría olor en cuatro "
        "puntos. La tolva central, en cambio, deja que el transporte trabaje por tandas cortas y que los galpones vacíen "
        "cuando les conviene.")
    m.p(f"Reemplaza a la playa de recepción y a la tolva de 3,1 m³ de la Rev. F. Es una tolva de chapa F-24 de 8 mm con "
        f"rigidizadores UPN 100, de {fmt(tp['x1'] - tp['x0'], 2)} × {fmt(tp['y1'] - tp['y0'], 2)} m en planta y tapa "
        f"transitable a +{fmt(tp['z_tapa'], 2)} m, con {fmt(tp['volumen_util_m3'], 0)} m³ útiles "
        f"({fmt(B['tolva_pulmon_dias'], 2)} días de guano). El fondo vivo tiene {sf['n']} sinfines Ø400 de "
        f"{fmt(sf['largo'], 2)} m en artesas, con motorreductores M85 a M88 y variador, que descargan en la cinta "
        "de alimentación M8 del secador.")
    q_rev = math.pi / 4 * (0.400 ** 2 - 0.114 ** 2) * 0.320
    caudal_m3h = B["secador_kg_h_regimen"] / 950
    m.ec("V_v = π / 4 · (D² − d²) · s", ["D = 0,400 m", "d = 0,114 m (tubo)", "s = 0,320 m (paso)"])
    m.calculo(f"V_v = {fmt(q_rev * 1000, 1)} L por vuelta con el sinfín lleno",
              f"{fmt(caudal_m3h, 2)} m³/h al régimen → {fmt(caudal_m3h / (q_rev * 60), 2)} rpm con un sinfín o "
              f"{fmt(caudal_m3h / (q_rev * 60) / 4, 2)} rpm con los cuatro")
    m.p("Esas velocidades son muy bajas para un reductor común. Se propone (P) que los sinfines trabajen de a uno, alternados "
        "cada 15 min para que no se forme bóveda, entre 0,3 y 1,5 rpm con un reductor de varias etapas (i ≈ 900) y variador; los "
        "3 kW (P) se confirman con el método CEMA 350 para sinfines bajo tolva, que manda por el par de arranque con la "
        "tolva llena. Si el fabricante prefiere otra combinación (menor diámetro o paso variable en la zona de carga), el "
        "caudal se mantiene.")
    m.lista([
        "Pesaje: cuatro celdas de compresión WT-101 a WT-104 con SIWAREX WP231; el caudal al secador se controla por pérdida "
        "de peso (lazo FIC-101). Mientras entra guano de una principal, el lazo pasa a modo volumétrico (kg por vuelta de la "
        "última calibración) y vuelve al gravimétrico 2 min después de terminado el llenado.",
        "Nivel: radar LT-101 de 80 GHz en la tapa, horquillas LSHH-101 (alto-alto: corta las rutas) y LSL-101 (bajo).",
        "Seguridad: dos registros de 800 × 700 con interruptor ZS-REG por F-DI; estación de bloqueo y etiquetado con los "
        "seccionadores Q-M85 a Q-M88.",
        "Aspiración: boca Ø600 al extractor M23 de la Rev. F y al biofiltro, que mantiene la tolva en depresión.",
    ])
    figura(m, PLANOS / "GI-07.png", "Tolva pulmón TP-01: planta y cortes (lámina GI-07)", 16)


# ===================================================================================== 8. secador
def secador(m):
    s = D["planta"]["secador"]
    m.h("8. Nave de proceso y secador SC-4")
    m.p(f"La nave de 33 × 18 m y el secador SC-4 se conservan tal como quedaron en la Rev. F: secador de cinta de tres pisos "
        f"con bandas de malla AISI 304 de {fmt(s['banda_ancho'], 1)} m, cámara de {fmt(s['L'], 1)} × {fmt(s['A'], 1)} × "
        f"{fmt(s['H'], 1)} m de panel sándwich de 80 mm, hogar de cáscara de arroz, intercambiador humos-aire, ciclón, "
        "lavador de gases, tolva de retención y enfriador. El juego aparte SC-01 a SC-06, el manual de armado, el STEP y el "
        "visor del secador (carpeta secadora/ del proyecto) siguen siendo los documentos de fabricación.")
    m.tabla("Interfaces del SC-4 con la granja integrada", [
        ["Interfaz", "Rev. F (planta sola)", "Granja integrada"],
        ["Ingreso del guano", "camión, playa y pala a la tolva de 3,1 m³", "galpones → cintas → TP-01"],
        ["Alimentación", "cinta M8 desde la tolva de recepción", "cinta M8 desde los sinfines de la TP-01"],
        ["Caudal", "velocidad de la M8 (operador)", f"FIC-101 en el PLC-01: {fmt(B['secador_kg_h_regimen'], 0)} kg/h"],
        ["Control del secado", "PLC-02: TIC-01 y MIC-01", "sin cambios; MIC-01 corrige TIC-01 y FIC-101"],
        ["Comunicación", "PLC-02 solo", "PLC-02 como I-device del PLC-01"],
        ["Piloto del hogar", "biogás (E8.6)", "GLP con tanque de 0,5 m³"],
    ], anchos=[3.6, 5.6, 6.8], alin=["L", "L", "L"])
    m.h("8.1 Equipos de la Rev. F aguas abajo del secador, al caudal nuevo", 2)
    prod_h = B["secador_kg_h_regimen"] * 0.28 / 0.85
    v_ret = prod_h * 1.0 / 500
    pila = math.pi * 3 ** 2 * 2.3 / 3
    m.p(f"El secador sigue igual, pero el producto pasa de 329 a {fmt(prod_h, 0)} kg/h y de 2.635 a "
        f"{fmt(B['producto_seco_kg_dia'], 0)} kg/día. Se verificaron los equipos de la Rev. F que reciben ese caudal "
        "(densidad del producto 500 kg/m³, R):")
    m.tabla("Verificación aguas abajo y adecuaciones propuestas (P)", [
        ["Equipo (Rev. F)", "Capacidad", "Necesario al régimen", "Resultado y propuesta"],
        ["Sinfín de descarga M10", "1,16 m³/h", f"{fmt(prod_h / 500, 2)} m³/h", "Alcanza"],
        ["Elevador de cangilones M11", "≈ 1 m³/h", f"{fmt(prod_h / 500, 2)} m³/h", "Alcanza"],
        ["Tolva de retención F1 (≥ 70 °C durante 60 min)", "0,7 m³", f"{fmt(v_ret, 2)} m³ para 1 h",
         "No alcanza (51 min): se agranda a 1,0 m³ aislada, con el TT-05 (P)"],
        ["Enfriador con ventilador M40", "900 m³/h (R)", f"≈ {fmt(900 * prod_h / 329, 0)} m³/h",
         "Se lleva a 1.200 m³/h (P); el M40 se verifica con el proveedor (0,55 o 0,75 kW; el Q21 lo admite)"],
        ["Acopio en pila (Ø6 × 2,3 m)", f"{fmt(pila, 1)} m³ ≈ {fmt(pila * 0.5, 1)} t",
         f"{fmt(B['producto_seco_kg_dia'] / 1000, 1)} t/día", f"Cubre {fmt(pila * 0.5 / (B['producto_seco_kg_dia'] / 1000), 1)} "
         "días: despacho diario o segunda pila en la reserva 2.ª etapa (P)"],
        ["Ensacadora de 25 kg (E5)", "sin dato de catálogo (H)", f"{fmt(B['producto_seco_kg_dia'] / 25, 0)} bolsas/día si todo se ensaca",
         "≥ 35 bolsas/h en un turno de 8 h (P, a pedir al fabricante); el granel la descarga"],
    ], anchos=[4, 2.8, 3.2, 6], alin=["L", "C", "C", "L"])
    m.p("La forma y las medidas del secador no cambian. La tolva de retención y el enfriador agrandados son las únicas "
        "adecuaciones de la Rev. F; quedan marcadas como propuesta (P) para la ingeniería de detalle.")
    figura(m, PLANOS / "GI-10.png", "Secador SC-4 integrado a la granja (lámina GI-10)", 16)
    figura(m, PLANOS / "GI-08.png", "Planta de equipos de la nave (lámina GI-08)", 16)
    figura(m, PLANOS / "GI-09.png", "Cortes de la nave (lámina GI-09)", 16)


# ===================================================================================== 9. eléctrica
def electrica(m):
    bal = E["balance"]
    m.h("9. Instalación eléctrica")
    m.p("El alcance eléctrico es la planta de secado con sus equipos auxiliares y, en los galpones, las conexiones del "
        "transporte de guano (CCM de cada galpón). Lo del galpón que no es guano (ventilación, comederos, huevos, luz) lo "
        "define el integrador del galpón y acá entra solo como carga preliminar (P) para dimensionar el transformador y los "
        "alimentadores.")
    m.h("9.1 Criterio de cálculo", 2)
    m.lista([
        "Tensión 3 × 380/220 V, 50 Hz; esquema de conexión a tierra TT como en la Rev. F, con diferencial en todos los circuitos "
        "(tipo B de 300 mA en los variadores y tipo A de 30 mA en tomacorrientes y alumbrado).",
        "En los galpones rige además la sección 705 de la AEA 90364 (establecimientos agropecuarios): conexión equipotencial "
        "suplementaria de las partes metálicas al alcance de los animales y diferencial de 300 mA como protección contra "
        "incendio.",
        "Corriente admisible Iz de la IEC 60364-5-52 con factores de temperatura (bandeja a 40 °C: 0,87; enterrado a 25 °C: "
        "0,95) y de agrupamiento: 0,80 en bandeja y 0,95 en zanja, con dos caños por zanja separados 0,5 m (tabla B.52.19). "
        "Se verifica Ib ≤ In ≤ Iz e I2 ≤ 1,45 · Iz.",
        "Caída de tensión: del origen a cada motor ≤ 5 % (AEA 90364-7-771) y del TGBT a cada tablero seccional o CCM ≤ 3 %.",
        "Largos de cable medidos sobre las canalizaciones del modelo 3D (camino más corto por bandejas y caños), más 1 m por "
        "extremo y 5 % de reserva.",
        "Cortocircuito por el método de las impedancias (IEC 60909), con red de MT de 250 MVA y transformador de 315 kVA, "
        "ucc 4 % (P: confirmar con la distribuidora y el fabricante).",
    ])
    m.ec("I = P / (√3 · U · η · cos φ)        ΔU = √3 · I · L · (R · cos φ + X · sen φ)",
         ["R a 70 °C (ρ20 = 0,0172 Ω·mm²/m, α = 0,00393)", "X = 0,08 mΩ/m"])
    m.ec("Iz = I0 · kT · kG", ["I0: corriente admisible de tabla para el método de instalación (A)",
                               "kT: factor de temperatura", "kG: factor de agrupamiento"])
    m.ec("Icc = c · U0 / (√3 · Z)", ["c = 1,05 para el máximo y 0,95 para el mínimo",
                                      "Z: impedancia de la red, el transformador y los cables"])
    m.h("9.2 Balance de potencia y transformador", 2)
    filas = [["Carga", "Tipo", "kW inst.", "Factor", "kW dem."]]
    for f in bal["filas"]:
        filas.append([f["carga"], f["tipo"], fmt(f["kW_instalados"], 2), fmt(f["factor"], 2), fmt(f["kW_demanda"], 2)])
    filas.append(["Total", "", fmt(bal["kW_instalados"], 1), "", fmt(bal["kW_demanda"], 1)])
    m.tabla("Balance de potencia de la granja", filas, anchos=[9, 1.2, 2, 1.6, 2], alin=["L", "C", "R", "R", "R"], total=True)
    m.calculo(f"S = {fmt(bal['kW_demanda'], 1)} kW × {fmt(bal['simultaneidad_tableros'], 2)} / {fmt(bal['cos_phi_global'], 2)}",
              f"{fmt(bal['kVA_demanda'], 1)} kVA → transformador de {fmt(bal['transformador_kVA'], 0)} kVA al "
              f"{fmt(bal['carga_transformador_pct'], 1)} % (P)")
    m.p("El transformador de " + bal["nota"] + ".")
    m.h("9.3 Alimentadores", 2)
    filas = [["Circuito", "S (mm²)", "Mét.", "L (m)", "Ib (A)", "In (A)", "Iz (A)", "ΔU (%)", "ΔU tot. (%)"]]
    for a in E["alimentadores"]:
        filas.append([a["circuito"], fmt(a["S_mm2"], 0), a["metodo"], fmt(a["L_m"], 1), fmt(a["Ib_A"], 1),
                      fmt(a["In_A"], 0), fmt(a["Iz_A"], 1), fmt(a["dU_pct"], 2), fmt(a["dU_total_pct"], 2)])
    m.tabla("Alimentadores (Cu, IRAM 2178; los QF salen del TGBT)", filas,
            anchos=[5.4, 1.2, 0.9, 1.3, 1.3, 1.2, 1.3, 1.3, 1.5], alin=["L", "R", "C", "R", "R", "R", "R", "R", "R"])
    ok_al = all(a["verifica"] for a in E["alimentadores"])
    m.p(("Todos los alimentadores cumplen Ib ≤ In ≤ Iz, I2 ≤ 1,45 · Iz y la caída de tensión admitida. " if ok_al else
         "ATENCIÓN: hay alimentadores que no verifican; ver datos/electrica.json. ") +
        "Los alimentadores QF1 a QF6 van enterrados a −0,70 m en caños de PEAD con malla de advertencia (AEA 95101): Ø110 "
        "para 70 a 120 mm², Ø63 para 10 y 25 mm² y Ø40 para señales y fibra óptica (P). En cada zanja van dos caños "
        "separados 0,5 m (QF1 con QF2, QF3 con QF4 y QF5 con QF6), de ahí el factor 0,95; con los caños en contacto el "
        "factor sería 0,85 y el QF1 tendría que pasar a 95 mm². Hay cámaras de 40 × 40 cm en los cambios de dirección. El "
        "largo de cálculo de los alimentadores de los galpones es el recorrido ortogonal más 10 % (P) y se ajusta con la "
        "traza de obra.")
    m.h("9.4 Cortocircuito y poder de corte", 2)
    cc = E["cortocircuito"]
    m.p(f"Corriente de cortocircuito trifásica máxima: {fmt(cc['TGBT_kA'], 2)} kA en el TGBT, {fmt(cc['TGF_kA'], 2)} kA en el "
        f"TGF, {fmt(cc['TG2_kA'], 2)} kA en el TG2 y {fmt(cc['TS-GU_kA'], 2)} kA en el TS-GU. Poderes de corte adoptados:")
    m.lista(cc["poder_de_corte"])
    m.h("9.5 Tableros", 2)
    t = E["tableros"]["TS-GU"]
    m.p(f"TS-GU (nuevo): {t['ubicacion']}; alimentado desde {t['alimentado_desde']}. Contiene: " + "; ".join(t["contenido"]) + ".")
    ccm = E["tableros"]["CCM"][0]
    m.p(f"CCM de cada galpón (tipo CCM-G1): {ccm['ubicacion']}. Contiene: {ccm['contenido']}.")
    figura(m, PLANOS / "GI-12.png", "Esquema unifilar general (lámina GI-12)", 16)
    figura(m, PLANOS / "GI-13.png", "Unifilares del TS-GU y del CCM tipo (lámina GI-13)", 16)
    m.h("9.6 Motores nuevos", 2)
    m.p("Para cada motor se definió su función, ubicación, potencia, vínculo mecánico, alimentación, protección, mando y "
        "cable. Las potencias de las cintas de piso, transversales e inclinadas son preliminares (P, rango de los "
        "proveedores de jaulas); las de colectoras y principales salen del cálculo de la sección 6, y las de los sinfines "
        "M85 a M88 (3 kW) son preliminares hasta la verificación por CEMA 350 de la sección 7.")
    nuevos = [mo for mo in E["motores"] if mo["estado"] == "nuevo" and mo["tablero"] in ("TS-GU", "CCM-G1")]
    filas = [["Tag", "Equipo", "kW", "In (A)", "Arranque", "Cable", "L (m)", "ΔU tot. (%)"]]
    for mo in nuevos:
        arr = "VFD" if "variador" in mo["arranque"] else ("inversor" if "inversor" in mo["arranque"] else "directo")
        filas.append([mo["tag"], mo["nombre"][:44], fmt(mo["kW"], 2), fmt(mo["In_A"], 2), arr,
                      f"4G{fmt(mo['S_mm2'], 1)}", fmt(mo["L_m"], 1), fmt(mo["dU_total_pct"], 2)])
    m.tabla("Motores del TS-GU y del CCM-G1 (los CCM-G2 a G4 son iguales)", filas,
            anchos=[1.4, 6, 1.2, 1.4, 1.6, 1.6, 1.4, 1.6], alin=["C", "L", "R", "R", "C", "L", "R", "R"])
    r = E["resumen"]
    pc = r["peor_caida_total"]
    texto = (f"En total hay {r['motores_nuevos']} motores nuevos ({fmt(r['kW_nuevos'], 2)} kW). La mayor caída de tensión "
             f"desde el origen es la del {pc['tag']}: {fmt(pc['dU_total_pct'], 2)} % con {fmt(pc['L_m'], 1)} m de "
             f"{fmt(pc['S_mm2'], 1)} mm², por debajo del 5 % admitido. ")
    if not r["todos_verifican_dU"]:
        texto += "ATENCIÓN: hay motores con caída de tensión mayor que la admitida. "
    texto += ("Con el cortocircuito mínimo al final de cada línea actúan todas las protecciones."
              if r["todos_verifican_Icc_min"] else
              "ATENCIÓN: hay protecciones que no actúan con el cortocircuito mínimo.")
    m.p(texto + " La lista completa de motores e instrumentos, con su tablero, protección, cable y ubicación, está en la "
                "planilla documentacion/Listas_granja_integrada.xlsx.")
    m.h("9.7 Canalizaciones, puesta a tierra y pararrayos", 2)
    pat = E["puesta_a_tierra"]
    m.p(f"Esquema {pat['esquema']}. Objetivo: {pat['objetivo']}.")
    m.lista(pat["elementos"])
    m.p("Las bandejas son de tipo escalera de chapa galvanizada (300 mm la troncal BT-01 de la nave, 200 mm las demás y "
        "150 mm las de las cintas inclinadas), colgadas con varilla roscada M12 y perfil C cada 1,6 m o apoyadas en "
        "ménsulas. En las galerías van sobre la estructura de la cinta, del lado de la pasarela.")
    m.p("Dentro de la nave, la cinta principal CP-E cuelga de las cerchas del techo de la Rev. F y la bandeja troncal "
        "BT-01 de las correas, que descargan en las mismas cerchas. Se estiman unos 47 kg/m entre la cinta (estructura, "
        "banda, rodillos y guano) y la bandeja con sus cables, lo que da entre 2,5 y 3 kN por cercha (P). Esa carga no "
        "estaba en el cálculo de la estructura de la Rev. F: se verifica con el cálculo estructural de la nave antes del "
        "montaje (sección 13).")
    figura(m, PLANOS / "GI-14.png", "Canalizaciones y tendidos (lámina GI-14)", 16)


# ===================================================================================== 10. automatización
def automatizacion(m):
    A = E["automatizacion"]
    m.h("10. Automatización")
    m.h("10.1 Arquitectura", 2)
    m.lista(A["arquitectura"])
    figura(m, PLANOS / "GI-15.png", "Arquitectura de automatización y red (lámina GI-15)", 16)
    m.h("10.2 Secuencia de operación (GRAFCET)", 2)
    m.p("La secuencia sigue los 13 pasos de la consigna y se escribió en GRAFCET (IEC 60848) con tres gráficos que "
        "corren a la vez (lámina GI-16):")
    m.lista([
        "G1, transporte y recepción: desde el reposo, acepta el pedido de vaciado de un galpón si la TP-01 tiene lugar, "
        "verifica los permisivos, arranca la ruta de aguas abajo hacia aguas arriba, comprueba velocidad y desvío, vacía "
        "el galpón piso por piso y para la ruta de aguas arriba hacia aguas abajo. Hay un G1 por lado: los lados Oeste y "
        "Este pueden correr juntos, pero cada lado vacía un galpón por vez.",
        "G2, secado y producto: arranca el secador (paso 7), estabiliza la dosificación (paso 6) y abre en paralelo la "
        "regulación, el monitoreo, la descarga y el producto (pasos 8 a 11); con la orden de parada o la TP-01 baja hace "
        "la parada controlada del secado (12b).",
        "G3, seguridad: vigila las funciones de seguridad y, ante una falla de categoría 0, una parada de emergencia, un "
        "cable de parada o la pérdida de comunicación, fuerza G1 a su reposo y G2 a la parada controlada (paso 13). La "
        "planta no vuelve a arrancar hasta que la falla se elimina y el operador la reconoce.",
    ])
    m.p("Cada transición es una condición que el PLC puede comprobar; si alguna condición de seguridad no se cumple, la "
        "transición no se franquea y la planta no arranca.")
    filas = [["Paso", "Etapa", "Transición de salida", "Acciones"]]
    for s in A["secuencia"]:
        filas.append([str(s["n"]), s["etapa"], s["transicion"], "; ".join(s["acciones"])])
    m.tabla("Secuencia de los 13 pasos (GRAFCET de la lámina GI-16)", filas, anchos=[1.1, 3.2, 4.6, 7.1],
            alin=["C", "L", "L", "L"])
    m.h("10.3 Enclavamientos", 2)
    filas = [["Condición", "Efecto", "Señal"]] + [[r["condicion"], r["efecto"], r["senal"]] for r in A["enclavamientos"]]
    m.tabla("Matriz de enclavamientos", filas, anchos=[6.5, 6.5, 3], alin=["L", "L", "C"])
    m.h("10.4 Manejo de fallas", 2)
    filas = [["Falla", "Acción automática", "Acción del operador"]] + [
        [r["falla"], r["accion_automatica"], r["accion_del_operador"]] for r in A["fallas"]]
    m.tabla("Tabla de fallas", filas, anchos=[5, 5.5, 5.5], alin=["L", "L", "L"])
    m.h("10.5 Lazos de control", 2)
    filas = [["Lazo", "Variable", "Medición", "Actuador", "Consigna", "Controlador"]] + [
        [r["tag"], r["variable"], r["medicion"], r["actuador"], r["consigna"], r["controlador"]] for r in A["lazos"]]
    m.tabla("Lazos de control", filas, anchos=[1.8, 3, 3, 3.2, 2.8, 2.2], alin=["C", "L", "L", "L", "L", "L"])
    m.h("10.6 Instrumentación y entradas/salidas", 2)
    filas = [["Periferia", "DI", "F-DI", "DQ", "AI", "SIWAREX", "Variadores", "Módulos (con 20 % de reserva)"]]
    for rid, v in E["io"].items():
        s_ = v["señales"]
        filas.append([rid, s_.get("DI", 0), s_.get("F-DI", 0), s_.get("DQ", 0), s_.get("AI", 0), s_.get("SIWAREX", 0),
                      s_.get("PROFINET (variadores)", 0),
                      ", ".join(f"{k} {n}" for k, n in v["modulos_ET200SP_con_20pct_reserva"].items())])
    m.tabla("Entradas y salidas por periferia", filas, anchos=[2, 1.1, 1.1, 1.1, 1.1, 1.6, 1.8, 6.2],
            alin=["C", "R", "R", "R", "R", "R", "R", "L"])
    ins = [i for i in E["instrumentos"] if i["alcance"] == "planta / transporte"]
    m.p(f"El transporte y la recepción suman {sum(int(i['cantidad']) for i in ins)} instrumentos en {len(ins)} tags, "
        "ubicados en el modelo 3D en su posición real (lista agrupada en la lámina GI-17 y completa en la planilla "
        "documentacion/Listas_granja_integrada.xlsx).")


# ===================================================================================== 11. 3D, renders y despieces
def modelo_3d(m):
    m.h("11. Modelo 3D, renders y despieces")
    tot = PZ.get("instancias") or PZ.get("total_instancias")
    m.p("El modelo se arma con CadQuery (sólidos exactos) desde los mismos datos que los cálculos: la granja completa, la "
        "planta central, el galpón tipo y el secador se exportan en GLB (metros, para el visor y Blender) y en STEP (para "
        "SolidWorks o Fusion 360). La lista de piezas (datos/piezas.json) agrupa cada pieza por sistema, con su código, "
        "material y cantidad" + (f": {fmt(tot, 0)} instancias en total." if tot else "."))
    archivos = [["Archivo", "Contenido"],
                ["index.html", "visor 3D web: modelos, vistas guardadas, capas por sistema y selección de piezas"],
                ["modelo_3d/granja_integrada.glb", "granja completa: predio, galpones, depósitos, transporte, planta y eléctrica"],
                ["modelo_3d/planta_central.glb", "planta central con el transporte, las torres y la instalación eléctrica"],
                ["modelo_3d/galpon_tipo_G1.glb", "galpón tipo con jaulas, cintas, ventilación y cabecera de guano"],
                ["modelo_3d/secador_SC4.glb", "secador SC-4 de la Rev. F en su posición en la nave"],
                ["modelo_3d/Granja_integrada_STEP.zip", "STEP de la planta, del galpón tipo y del transporte"],
                ["modelo_3d/despieces/*.glb", "despieces de la TP-01, del cabezal CP-O, de la desviadora DV-O y del TS-GU"]]
    m.tabla("Archivos del modelo 3D", archivos, anchos=[6, 10], alin=["L", "L"])
    renders = [("R01_granja_general", "Vista general de la granja"), ("R02_planta_y_galpones", "Planta central entre los galpones"),
               ("R08_recorrido_del_guano", "Recorrido del guano desde el galpón G2"),
               ("R05_corte_tecnico_con_recorrido", "Corte técnico de la nave con transparencias"),
               ("R07_instalacion_electrica", "Instalación eléctrica resaltada sobre la planta en transparencia"),
               ("R11_torre_TT-O", "Torre de transferencia TT-O con su desviadora y contenedor"),
               ("R13_recepcion_TP-01", "Recepción: tolva pulmón TP-01 y pórtico de cabezales"),
               ("R10_galpon_cabecera_de_guano", "Cabecera de guano del galpón con el CCM y la cinta inclinada")]
    for n, txt in renders:
        figura(m, RENDERS / f"{n}.jpg", f"{txt} (render {n.split('_')[0]})", 15)
    m.p("Los despieces numerados (láminas GI-18 a GI-20) muestran la tolva pulmón, el cabezal de la cinta principal, la "
        "desviadora y el tablero TS-GU con su lista de piezas: número, descripción con medidas, cantidad y material. Cada "
        "globo apunta a la pieza en el modelo, porque sale de la misma posición 3D.")
    figura(m, PLANOS / "GI-18.png", "Despiece de la tolva pulmón TP-01 (lámina GI-18)", 16)
    figura(m, RENDERS / "R06_despiece_TP-01.jpg", "Despiece de la tolva pulmón TP-01: tapa con la aspiración, tolva, "
           "artesas, sinfines, motorreductores, estructura y escalera (render R06)", 15)


# ===================================================================================== 12. planos
TITULOS = {1: "Implantación general de la granja", 2: "Galpón tipo G1: planta y cabecera de guano",
           3: "Galpón tipo G1: corte transversal", 4: "Transporte de guano: planta general y detalles",
           5: "Transporte de guano: elevaciones y perfil de la CI", 6: "Torre de transferencia TT-O: planta y cortes",
           7: "Tolva pulmón TP-01: planta y cortes", 8: "Nave de proceso: planta de equipos", 9: "Nave de proceso: cortes",
           10: "Secador SC-4 (Rev. F): integración a la granja", 11: "Diagrama de flujo del proceso (PFD) y balance",
           12: "Esquema unifilar general: TGBT, TG2 y alimentadores", 13: "Esquemas unifilares: TS-GU y CCM-G1 (tipo)",
           14: "Instalación eléctrica: canalizaciones y tendidos", 15: "Arquitectura de automatización y red",
           16: "Secuencia (GRAFCET) y enclavamientos", 17: "Instrumentación: lista de E/S por periferia",
           18: "Tolva pulmón TP-01: despiece y lista de piezas", 19: "Cabezal CP-O y desviadora DV-O: despieces",
           20: "Tablero TS-GU: despiece y lista de equipos"}


def planos(m):
    m.h("12. Planos")
    m.p("Las 20 láminas A3 (formato IRAM 4504, método de proyección ISO E de la IRAM 4501) se generan con "
        "fuente/planos/planos_gi.py desde los datos y el modelo 3D: las plantas, cortes y elevaciones son vistas "
        "ortográficas del modelo con la cámara en el plano del corte, a escala exacta, con globos, niveles, cotas y tablas "
        "encima. Cada lámina sale en DXF (el archivo Planos_DXF_GI.zip trae las láminas con sus imágenes), en PNG y en PDF; "
        "el juego completo está en Planos_GI.pdf. En el PDF el rótulo, los textos, las cotas y las tablas son vectoriales, y "
        "las vistas del modelo van como imágenes de 180 a 400 ppp según la escala de cada vista.")
    filas = [["Lámina", "Título"]] + [[f"GI-{n:02d}", TITULOS[n]] for n in range(1, 21)]
    m.tabla("Juego de planos GI", filas, anchos=[2.2, 13.8], alin=["C", "L"])


# ===================================================================================== 13. preliminares y pendientes
def pendientes(m):
    m.h("13. Valores preliminares y pendientes")
    m.p("Lo que sigue no impide presentar el proyecto, pero hay que cerrarlo antes de la ingeniería de detalle y la compra:")
    m.tabla("Valores y verificaciones que se confirman antes de la ingeniería de detalle", [
        ["Valor o verificación", "Tipo", "Cómo se confirma"],
        ["Densidad aparente del guano fresco: 950 kg/m³", "H", "Medir en la granja (volumen y peso de una muestra); "
         "afecta la capacidad de las cintas y de la TP-01"],
        ["Potencias de las cintas de piso (1,1 kW), CT (0,55 kW) y CI (1,1 kW)", "P", "Hoja de datos del proveedor de jaulas y cintas"],
        ["Potencias de colectoras y principales (DIN 22101)", "P", "Cálculo del fabricante con su banda y sus rodillos"],
        ["Sinfines M85 a M88: 3 kW, 0,3 a 1,5 rpm, i ≈ 900", "P", "CEMA 350 para sinfines bajo tolva: par de arranque con la "
         "tolva llena; propuesta del fabricante"],
        ["Carga de la CP-E y de la BT-01 sobre las cerchas (2,5 a 3 kN por cercha)", "P", "Cálculo estructural de la nave "
         "de la Rev. F con la carga nueva, antes del montaje"],
        ["Tolva de retención F1 de 1,0 m³ y enfriador de 1.200 m³/h (M40 de 0,55 o 0,75 kW)", "P", "Proveedor del secador; "
         "actualizar los planos de fabricación de la Rev. F (juego SC-01 a SC-06 y planos de la nave) cuando se confirme"],
        ["Acopio del producto: 1,7 días en la pila de la Rev. F", "P", "Despacho diario o segunda pila en la zona de reserva "
         "de 2.ª etapa"],
        ["Ensacadora: ≥ 35 bolsas de 25 kg por hora", "H", "Catálogo del fabricante de la ensacadora E5"],
        ["Red de MT de 250 MVA y transformador de 315 kVA, ucc 4 %", "P", "Factibilidad de la distribuidora y placa del transformador"],
        ["Cargas de los galpones, depósitos y servicios", "P", "Proyecto del integrador del galpón (San Jorge)"],
        ["Ventiladores de 50\" (36.000 m³/h) y 36\" (17.000 m³/h)", "P", "Curva del fabricante a la presión de trabajo"],
        ["Distancias sanitarias y cerco a ≥ 50 m de los galpones", "P", "Res. SENASA 1699/2019 y habilitación provincial"],
        ["Desagüe pluvial del predio", "P", "Planialtimetría del terreno"],
        ["Medidas de los equipos del TS-GU", "P", "Proveedor del tablero (calentamiento según IEC 61439)"],
        ["Piloto a GLP del hogar", "P", "Proyecto de gas por instalador matriculado (ENARGAS)"],
    ], anchos=[6.6, 1.1, 8.3], alin=["L", "C", "L"])


# ===================================================================================== 14. cumplimiento
def cumplimiento(m):
    m.h("14. Verificación de las reglas de la consigna")
    m.tabla("Reglas de la consigna y cómo se cumplieron", [
        ["Regla", "Cómo se cumplió"],
        ["Conservar el diseño original de la secadora", "SC-4, nave y equipos de la Rev. F sin cambios de forma ni medidas; "
         "solo interfaces y, marcadas (P), la tolva F1 y el enfriador agrandados por el caudal nuevo"],
        ["Reutilizar el proyecto de galpones automáticos", "Galpón, jaulas, cintas, ventilación y depósitos del proyecto San Jorge"],
        ["Eliminar completamente el biogás", "Sección 2: biodigestores, cogeneración, antorcha, línea, TS-BIO y zona Ex"],
        ["No inventar componentes sin justificación", "Cada equipo nuevo tiene función, cálculo o criterio y tipo de dato"],
        ["No dejar transportadores desconectados", "Cadena CT → CI → CE → TT → CP → TP-01 continua en los dos lados"],
        ["No dejar equipos suspendidos o sin soporte", "Galerías en caballetes cada 11 m como máximo, bandejas colgadas con "
         "varilla y perfil, tableros en zócalo o muro; la carga de la CP-E y la BT-01 sobre las cerchas queda a verificar "
         "(sección 13)"],
        ["No generar geometrías incoherentes", "Planos y cortes sacados del modelo; revisión de interferencias y soportes"],
        ["No simplificar la secadora", "Se usa el modelo CadQuery detallado de la Rev. F"],
        ["Respaldos antes de cambios importantes", "Proyecto anterior intacto; todo lo nuevo en granja_integrada/ con control de versiones"],
        ["Comprobar el resultado", "Cálculos con verificación automática, revisión visual de las 20 láminas y control "
         "independiente de cálculos, planos y coherencia entre documentos, con sus correcciones aplicadas"],
    ], anchos=[6, 10], alin=["L", "L"])


def conclusiones(m):
    m.h("15. Conclusiones")
    prod_h = B["secador_kg_h_regimen"] * 0.28 / 0.85
    m.p(f"La planta de la Rev. F queda integrada a una granja de {fmt(B['aves_total'], 0)} gallinas sin cambiar el secador: "
        f"el guano de los cuatro galpones ({fmt(B['guano_total_kg_dia'] / 1000, 1)} t/día) llega solo, por cintas, a una tolva "
        f"pulmón con {fmt(B['tolva_pulmon_dias'], 1)} días de reserva, y el SC-4 lo seca en dos turnos a "
        f"{fmt(B['secador_kg_h_regimen'], 0)} kg/h con {fmt(B['reserva_secador_pct'], 1)} % de reserva de capacidad. Aguas "
        f"abajo, con {fmt(prod_h, 0)} kg/h de producto, la tolva de retención y el enfriador se agrandan (P) y el acopio "
        "pasa a despacho diario. La instalación eléctrica cumple la caída de tensión y el cortocircuito en todos los "
        f"circuitos, con el transformador al {fmt(E['balance']['carga_transformador_pct'], 0)} %. La automatización arranca "
        "la planta solo con todas las condiciones de seguridad cumplidas y lleva cada falla a un estado seguro. Los valores "
        "marcados (P) y (H) y las verificaciones de la sección 13 se cierran con los proveedores antes de la ingeniería de "
        "detalle.")


# ===================================================================================== PDF
def pdf_desde_html(m):
    """Igual que en la memoria de la Rev. D, pero con los temporales dentro de granja_integrada/memoria."""
    import pymupdf
    pdf = SALIDA.with_suffix(".pdf")
    tmp_html = SALIDA.parent / "_memoria.html"
    script = ANTERIOR / "fuente" / "imprimir_pdf.js"
    titulo = "Memoria técnica de la granja integrada"

    def imprimir(paginas):
        tmp_html.write_text(MD._html(m, paginas, titulo), encoding="utf-8")
        subprocess.run(["node", str(script), str(tmp_html), str(pdf)], check=True, cwd=str(ANTERIOR / "fuente"))

    imprimir(None)
    paginas = {}
    with pymupdf.open(pdf) as d:
        textos = [d[i].get_text() for i in range(d.page_count)]
    desde = 2
    for _nivel, hid, texto in m.indice:
        for i in range(desde, len(textos)):
            if texto in textos[i].replace("\n", " ") or texto in textos[i]:
                paginas[hid] = i + 1
                desde = i
                break
    imprimir(paginas)
    fuente = MD.fuente_arial()
    letra = {"fontname": "arial", "fontfile": fuente} if fuente else {"fontname": "helv"}
    with pymupdf.open(pdf) as d:
        for i in range(1, d.page_count):
            pg = d[i]
            w, h = pg.rect.width, pg.rect.height
            ancho = pymupdf.get_text_length(ENCABEZADO, fontsize=8.5, fontname="helv")
            pg.insert_text((w - 71 - ancho, 42), ENCABEZADO, fontsize=8.5, color=(0.4, 0.4, 0.4), **letra)
            pg.draw_line((71, 48), (w - 71, 48), color=(0.7, 0.7, 0.7), width=0.5)
            pg.insert_text((w / 2 - 30, h - 30), f"Página {i + 1} de {d.page_count}", fontsize=9, **letra)
        d.save(str(pdf) + ".tmp", garbage=3, deflate=True)
    os.replace(str(pdf) + ".tmp", pdf)
    tmp_html.unlink()
    import shutil
    shutil.rmtree(SALIDA.parent / "_fig", ignore_errors=True)
    print("PDF", pdf, "| páginas:", len(textos))


def main():
    m = MD.Memoria()
    portada(m)
    encabezado_pie(m)
    objeto(m)
    biogas(m)
    implantacion(m)
    galpones(m)
    balance(m)
    transporte(m)
    recepcion(m)
    secador(m)
    electrica(m)
    automatizacion(m)
    modelo_3d(m)
    planos(m)
    pendientes(m)
    cumplimiento(m)
    conclusiones(m)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    m.d.save(SALIDA)
    print("guardado", SALIDA, "| tablas", m.n_tabla, "| ecuaciones", m.n_ec, "| figuras", m.n_fig)
    pdf_desde_html(m)


if __name__ == "__main__":
    main()
