"""Informe «Análisis de rentabilidad económica y recuperación de la inversión» (Word, PDF y Markdown).

    python modelo_economico.py && python figuras_economia.py && python informe_economico.py

Todos los números salen de economia.json (el modelo) para que el informe, la planilla y los gráficos coincidan.
Usa la clase Memoria de calculos/memoria_docx.py (la misma del informe final): Word con python-docx y PDF desde el
HTML equivalente con Chrome. Además deja el texto en Markdown (analisis_economico/_informe.md) para el documento en
línea.
"""
from __future__ import annotations

import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "fuente", "calculos"))
sys.path.insert(0, AQUI)
import memoria_docx as MD  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.shared import Pt, RGBColor  # noqa: E402
from memoria_docx import ESCUELA, INTEGRANTES, Memoria, campo  # noqa: E402

import modelo_economico as ME  # noqa: E402

E = json.load(open(os.path.join(AQUI, "economia.json"), encoding="utf-8"))
SALIDA = os.path.join(RAIZ, "analisis_economico", "Analisis_economico_Secadora_Guano.docx")
FIG = os.path.join(RAIZ, "analisis_economico", "figuras")
D = E["dolar"]
ESCS = ("conservador", "realista", "optimista")
NOM = {"conservador": "Conservador", "realista": "Realista", "optimista": "Optimista"}


# =============================================================================== formato de números
def n(x, d=0):
    if x is None:
        return "—"
    t = f"{abs(x):,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return ("−" + t) if x < 0 and t.strip("0,") else t


def mill(x, d=1):
    return n(x / 1e6, d)


def pm(x, d=1):
    t = mill(abs(x), d)
    return ("−" if x < 0 and t.strip("0,") else "") + f"$ {t} millones"


def us(x):
    return f"USD {n(x)}"


def pc(x, d=1):
    return f"{n(x, d)} %"


def mes_txt(x, d=1):
    return "no recupera" if x is None else f"{n(x, d)} meses"


def anio_mes(x):
    """47,7 -> «mes 48 (año 4, mes 12)»."""
    if x is None:
        return "no recupera"
    k = int(x) + (1 if x % 1 > 1e-9 else 0)
    return f"mes {k} (año {(k - 1) // 12 + 1}, mes {(k - 1) % 12 + 1} de ese año)"


# =============================================================================== escritura doble: Word/PDF y Markdown
class Doc:
    def __init__(self):
        self.m = Memoria()
        self.md = []

    def h(self, t, nivel=1):
        self.m.h(t, nivel)
        self.md.append("#" * (nivel + 1) + " " + t)

    def p(self, t, **kw):
        self.m.p(t, **kw)
        self.md.append(f"**{t}**" if kw.get("negrita") else t)

    def lista(self, items):
        self.m.lista(items)
        self.md.append("\n".join(f"- {i}" for i in items))

    def tabla(self, titulo, filas, anchos=None, alin=None, total=False, resaltar=None):
        k = self.m.tabla(titulo, filas, anchos=anchos, alin=alin, total=total, resaltar=resaltar)
        cab = "| " + " | ".join(str(c) for c in filas[0]) + " |"
        sep = "|" + "|".join((" ---: " if (alin and alin[j] == "R") else " --- ") for j in range(len(filas[0]))) + "|"
        cuerpo = ["| " + " | ".join(str(c).replace("|", "/") for c in f) + " |" for f in filas[1:]]
        self.md.append(f"*Tabla {k} – {titulo}*\n\n" + "\n".join([cab, sep] + cuerpo))
        return k

    def figura(self, nombre, epigrafe, ancho=16):
        ruta = os.path.join(FIG, nombre)
        k = self.m.figura(ruta, epigrafe, ancho)
        self.md.append(f"[[figura:{nombre}|Figura {k} – {epigrafe}]]")
        return k

    def recuadro(self, titulo, texto):
        self.m.recuadro(titulo, texto)
        self.md.append(f"> **{titulo}.** {texto}")

    def ec(self, formula, simbolos=None):
        k = self.m.ec(formula, simbolos)
        self.md.append(f"`{formula}`   ({k})" + (f"\n\ndonde {'; '.join(simbolos)}." if simbolos else ""))
        return k

    def calculo(self, reemplazo, resultado):
        self.m.calculo(reemplazo, resultado)
        self.md.append(f"{reemplazo} → **{resultado}**")

    def salto(self):
        self.m.salto()


# =============================================================================== atajos de datos
ESC = E["escenarios"]
REF = E["referencia"]
DAT = E["datos"]
INV_ = E["inverso"]
R_ = ESC["realista"]
O_ = ESC["optimista"]
C_ = ESC["conservador"]
_tabla, PARAMS = ME.escenarios()


def a2(e, k):
    return e["anio2"][k]


def alt(nombre_esc, cod):
    return next(a for a in INV_[nombre_esc]["alternativas"] if a["cod"] == cod)


MIN60 = INV_["optimista"]["minimos"]["2T_60"]                     # capacidad mínima (precios del proyecto)
MIN60_3T = INV_["optimista"]["minimos"]["3T_60"]
A1B_R, A1B_O = alt("realista", "A1+B"), alt("optimista", "A1+B")
VAR = E["variantes_referencia"]


def a3(e, k):
    """Flujo de régimen: año 3, el primero en que se paga el impuesto de un año entero."""
    return e["anio3"][k]


def por_t_vendida_usd(e, *claves):
    """USD por tonelada vendida de un grupo de costos del mes de régimen."""
    return sum(e["mes"]["costos"][k] for k in claves) / e["mes"]["vendido_t"] / D


def parte(e, *claves):
    """Porcentaje del costo operativo total que representa un grupo de costos."""
    return sum(e["mes"]["costos"][k] for k in claves) / e["mes"]["total"] * 100


# =============================================================================== portada
def portada(d):
    m = d.m
    m.p()
    m.p(ESCUELA, negrita=True, centrado=True, tam=14)
    m.p("Crespo, Entre Ríos · Especialidad Electromecánica · 7.° año", centrado=True)
    m.p()
    m.p("PROYECTO FINAL · ANEXO ECONÓMICO", negrita=True, centrado=True, tam=13)
    m.p("Análisis de rentabilidad económica y recuperación de la inversión", negrita=True, centrado=True, tam=20)
    m.p("Secadora de guano de gallina 8 t/día (Rev. F)", negrita=True, centrado=True, tam=14)
    m.p("Inversión · Capacidad productiva · Costos · Ingresos · Payback · ROI · Punto de equilibrio · Escenarios · "
        "Sensibilidad · Análisis inverso de capacidad", centrado=True, tam=10.5)
    m.p(f"Precios en pesos constantes de {E['fecha']} (dólar BNA $ {n(D)}), sin IVA", centrado=True, tam=10.5)
    img = os.path.join(FIG, "f3_recuperacion_referencia.png")
    if os.path.exists(img):
        from docx.shared import Cm
        par = m.d.add_paragraph()
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.add_run().add_picture(img, width=Cm(13))
        import pathlib
        m.html.append(f'<p style="text-align:center"><img src="{pathlib.Path(img).resolve().as_uri()}" '
                      f'style="width:13cm"></p>')
    m.p("Integrantes", negrita=True, centrado=True)
    m.p(" · ".join(INTEGRANTES[:3]), centrado=True)
    m.p(" · ".join(INTEGRANTES[3:]), centrado=True)
    m.p("Crespo, Entre Ríos – noviembre de 2026", centrado=True)
    m.salto()
    m.h("Índice", 1, indice=False)
    campo(m.d.add_paragraph(), 'TOC \\o "1-2" \\h \\z \\u')
    m.html.append('<div id="indice">__INDICE__</div>')
    m.salto()
    d.md.append("# Análisis de rentabilidad económica y recuperación de la inversión\n\nSecadora de guano de gallina "
                f"8 t/día (Rev. F) · Anexo económico del proyecto final · precios en pesos de {E['fecha']}, sin IVA")


def encabezado_pie(m):
    sec = m.d.sections[0]
    sec.different_first_page_header_footer = True
    hp = sec.header.paragraphs[0]
    hp.text = "Secadora de guano 8 t/día – Análisis económico y recuperación de la inversión"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hp.runs[0].font.size = Pt(8.5)
    hp.runs[0].font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("Página ").font.size = Pt(9)
    campo(fp, "PAGE")


# =============================================================================== 1. resumen ejecutivo
def tabla_escenarios(d, titulo):
    filas = [["Concepto", "Conservador", "Realista", "Optimista"]]
    def fila(rot, f):
        filas.append([rot] + [f(ESC[e]) for e in ESCS])
    fila("Inversión inicial total ($ millones)", lambda e: mill(e["inv_total"]))
    fila("Inversión inicial total (USD)", lambda e: n(e["inv_total"] / D))
    fila("Guano húmedo procesado (t/año)", lambda e: n(a2(e, "humedo_t")))
    fila("Producto seco al 15 % obtenido (t/año)", lambda e: n(a2(e, "seco_t")))
    fila("Producto vendido (t/año)", lambda e: n(a2(e, "vendido_t")))
    fila("Producción mensual de producto seco (t/mes)", lambda e: n(a2(e, "seco_t") / 12, 1))
    fila("Precio medio ex planta (USD/t)", lambda e: n(e["precio_t"] / D, 1))
    fila("Ventas ($ millones por mes)", lambda e: mill(a2(e, "ventas") / 12, 2))
    fila("Costos operativos ($ millones por mes)", lambda e: mill(a2(e, "costo_total") / 12, 2))
    fila("Beneficio neto ($ millones por mes)", lambda e: mill(a2(e, "beneficio_neto") / 12, 2))
    fila("Beneficio neto ($ millones por año)", lambda e: mill(a2(e, "beneficio_neto"), 1))
    fila("Flujo de caja neto de régimen, año 3 ($ millones por año)", lambda e: mill(a3(e, "flujo"), 1))
    fila("Recuperación de la inversión", lambda e: mes_txt(e["payback_meses"]))
    fila("ROI anual (año 2)", lambda e: pc(e["roi_anual"]))
    fila("VAN a 15 años, 10 % real ($ millones)", lambda e: mill(e["van"], 0))
    return d.tabla(titulo, filas, anchos=[7.0, 3.0, 3.0, 3.0], alin=["L", "R", "R", "R"], resaltar=[13])


def resumen(d):
    d.h("1. Resumen ejecutivo", 1)
    d.p("Este anexo responde, con los datos del proyecto contrastados entre sí y con precios de mercado verificados, a "
        "la pregunta: si se invierte en construir la secadora de guano y se la pone a trabajar con una capacidad "
        "determinada, ¿cuánto dinero genera realmente y en cuánto tiempo se recupera la inversión? Se evalúa la planta "
        "de secado sin la planta de biogás, que es la primera etapa que recomienda el propio proyecto, operando un turno "
        "de 8 h como fue diseñada (1.000 kg/h de guano al 72 % de humedad). Todo está en pesos constantes de "
        f"{E['fecha']}, sin IVA, con el dólar BNA a $ {n(D)}.")
    tabla_escenarios(d, "Resultados de los tres escenarios con la secadora tal como fue diseñada (1 turno)")
    d.recuadro("Respuesta corta",
               f"La inversión total para poner la planta en marcha es de {pm(R_['inv_total'])} ({us(R_['inv_total'] / D)}) "
               f"en el escenario realista, más {pm(R_['ct_regimen'])} de capital de trabajo. Trabajando un turno, la "
               f"planta procesa {n(a2(R_, 'humedo_t'))} t/año de guano húmedo y vende {n(a2(R_, 'vendido_t'))} t de "
               f"producto seco; factura {pm(a2(R_, 'ventas') / 12, 1)} por mes pero gasta "
               f"{pm(a2(R_, 'costo_total') / 12, 1)}, de modo que no cubre sus costos y no recupera la inversión. "
               f"Ni siquiera con los precios que supuso el proyecto (USD {n(DAT['PRECIO_PROY'], 1)}/t, escenario "
               "optimista) recupera la inversión en 15 años con un turno. Para recuperarla en menos de 5 años hace falta "
               "trabajar más de un turno y que se den todos los supuestos del escenario optimista: precios del proyecto, "
               "guano al 70 %, sin flete del guano, 95 % de disponibilidad y 2 operarios por turno. Con dos turnos, el "
               f"caudal tiene que ser de {n(MIN60['m_in'])} kg/h o más ({n(MIN60['humedo_mes_t'])} t/mes de guano "
               f"húmedo); con tres turnos alcanza con {n(MIN60_3T['m_in'])} kg/h. Con dos turnos a 1.440 kg/h, la "
               f"capacidad máxima del secador, se recupera en el {anio_mes(A1B_O['payback'])}; con los precios del "
               f"proyecto pero los demás supuestos del escenario realista, la misma configuración tarda "
               f"{mes_txt(VAR['supuestos_realistas_precio_proyecto']['payback'], 0)}.")
    d.p("Las conclusiones principales son:", negrita=True)
    d.lista([
        f"El precio de venta es la variable que decide el proyecto. El único precio de granel encontrado es de USD 30/t "
        f"para guano semiseco (2024), que llevado a producto seco da unos USD {n(DAT['GRANEL_MERCADO'], 0)}/t ex planta; "
        f"el valor de sus nutrientes (N, P₂O₅ y K₂O) a precios de noviembre de 2026 es de USD {n(DAT['VALOR_NPK'], 1)}/t. "
        f"El proyecto supuso USD {n(DAT['PRECIO_PROY'], 1)}/t sin cotizaciones que lo respalden. Es el dato pendiente "
        "más importante.",
        f"El costo total de producir y vender un kilogramo es de $ {n(R_['costo_total_kg'], 0)} sin amortizaciones "
        f"(≈ USD {n(R_['costo_total_kg'] * 1000 / D, 0)}/t), más que el precio realista. Sólo el flete del guano "
        f"húmedo, la cáscara de arroz y la energía eléctrica suman USD "
        f"{n(por_t_vendida_usd(R_, 'flete_guano', 'cascara', 'energia_var', 'energia_fija'), 0)} por tonelada vendida, "
        f"más que el valor de los nutrientes del producto (USD {n(DAT['VALOR_NPK'], 1)}/t).",
        f"Con los precios y demás supuestos del escenario optimista, la capacidad mínima para recuperar la inversión "
        f"en 60 meses es de {n(MIN60['m_in'])} kg/h durante 16 h por día: {n(MIN60['humedo_dia_kg'] / 1000, 1)} t/día y "
        f"{n(MIN60['humedo_mes_t'])} t/mes de guano húmedo, y {n(MIN60['vendido_anio_t'])} t/año de producto vendido. "
        "Se logra con la misma máquina (a 135 °C seca hasta 1.440 kg/h), con un segundo turno y una tolva de retención "
        f"mayor: USD 32.000 de inversión adicional. Tres turnos también alcanzan ({n(MIN60_3T['m_in'])} kg/h), pero "
        "necesitan más guano por día.",
        f"Con el precio realista no hay ampliación razonable que recupere la inversión en 5 años: con dos turnos a "
        f"1.440 kg/h haría falta vender a unos USD {n(A1B_R['precio_60'], 0)}/t.",
        "El beneficio económico que sí es seguro es el ambiental y sanitario para las granjas (fin de los acopios, olores "
        "y moscas), que el proyecto contaba como «ahorro» pero que no es dinero que entra a la planta.",
    ])
    d.p("Antes de invertir hacen falta tres datos que hoy no existen: el precio mayorista firme y el volumen que compra "
        "el mercado (cartas de intención de compradores), la tarifa real de la Cooperativa La Agrícola Regional (LAR) y "
        "el precio de la cáscara puesta en planta. El apartado 3.3 lista todos los datos pendientes.")


# =============================================================================== 2. método
def metodo(d):
    d.h("2. Alcance, criterios y método", 1)
    d.h("2.1. Qué se evalúa", 2)
    d.p("Se evalúa la planta de secado de la Rev. F sin la planta de biogás (ítems B7 y B8 del presupuesto), con todo lo "
        "demás que el proyecto necesita para funcionar y habilitarse: secador SC-4, generador a cáscara, ventilación, "
        "tratamiento de gases, transporte, control, instalación eléctrica, nave, recepción, zaranda, ensacado, depósito, "
        "lavado de vehículos, seguridad e incendio. Es la variante «B – Sin biogás, 1 turno» del presupuesto y la primera "
        "etapa que recomienda el informe (apartado 26). El biogás es un negocio distinto y, según la propia evaluación "
        "del proyecto, empeora los indicadores.")
    d.p("El horizonte es de 15 años (180 meses) y la tasa de descuento, del 10 % anual, como en la evaluación del "
        "proyecto. Como todo está en moneda constante, esa tasa es real (sin inflación).")
    d.h("2.2. Moneda, fecha de referencia e inflación", 2)
    d.p(f"Todos los importes están en pesos constantes de {E['fecha']}, sin IVA. Los montos que el proyecto tiene en "
        f"dólares (presupuesto al 23/10/2026, $ 1.550/USD) se pasan a pesos con el dólar BNA vendedor del 16/11/2026, "
        f"$ {n(D)}/USD. Con inflación de 2,2 % mensual y 33,1 % interanual (INDEC, octubre de 2026), una proyección en "
        "pesos corrientes obligaría a suponer la inflación y el dólar de los próximos 15 años; en moneda constante esos "
        "supuestos no hacen falta, porque precios y costos se mantienen en su valor real. Lo que sí cambia el resultado "
        "es que un costo suba más que el precio de venta (por ejemplo, las tarifas eléctricas, que en octubre subieron "
        "4,2 % contra 2,2 % del índice general). Ese desfase se estudia en la sensibilidad (apartado 11.3). Las escalas "
        "del impuesto a las ganancias se actualizan por IPC, así que en moneda constante sus tramos también son fijos.")
    d.p("Los precios que no son de noviembre de 2026 se indican con su fecha y antigüedad (por ejemplo, el precio del "
        "guano a granel es de octubre de 2024: 25 meses).")
    d.h("2.3. Tipos de datos", 2)
    d.p("Cada dato del modelo lleva una letra que dice de dónde sale. La lista completa, con los valores de cada "
        "escenario, está en el anexo A y en la hoja «Supuestos» de la planilla.")
    d.tabla("Tipos de datos", [
        ["Tipo", "Significado", "Ejemplos"],
        ["R", "Dato del proyecto (cálculos, planos, presupuesto). Son valores de diseño: nada fue medido todavía",
         "1.000 kg/h, 72 % → 15 %, 54 kW del TGF, presupuesto de USD 767.651"],
        ["V", "Dato verificado de mercado o normativo, con fuente y fecha", "Dólar $ 1.575, sueldo UOM, urea USD 600/t, "
         "escala de ganancias 2026"],
        ["E", "Estimación propia hecha con datos R o V; se explica el cálculo", "Valor agronómico NPK, flete de cáscara, "
         "potencia sin biogás"],
        ["H", "Hipótesis: no hay dato publicado; se adopta un valor razonable y se estudia su efecto",
         "Precio de la bolsa de 25 kg, fracción vendida, terreno, honorarios"],
    ], anchos=[1.2, 8.3, 6.5], alin=["C", "L", "L"])
    d.h("2.4. Fórmulas utilizadas", 2)
    d.p("Producción (balance de masa). El sólido seco no se evapora, así que se conserva entre la entrada y la salida "
        "del secador; el agua que se va es la diferencia de masas:")
    d.ec("m_s = m_in · (1 − X_in)        m_out = m_s / (1 − X_out)        W = m_in − m_out",
         ["m_in = guano húmedo (kg/h)", "X_in, X_out = humedad de entrada y salida en base húmeda",
          "m_s = sólido seco (kg/h)", "m_out = producto al 15 % (kg/h)", "W = agua evaporada (kg/h)"])
    d.p("Ventas y resultados. Se separan con cuidado la facturación, los costos y la ganancia:")
    d.ec("Ventas = producto vendido × precio medio ex planta",
         ["producto vendido = producto seco × (1 − mermas) × fracción vendida"])
    d.ec("Beneficio bruto = Ventas − Costo de producción",
         ["costo de producción = cáscara + energía + flete del guano + envases + insumos + mantenimiento + mano de obra"])
    d.ec("Beneficio operativo (EBITDA) = Ventas − todos los costos operativos",
         ["se suman la administración, los seguros y tasas, la comercialización, ingresos brutos y el impuesto a los "
          "débitos y créditos; EBIT = EBITDA − amortizaciones"])
    d.ec("Beneficio neto = EBIT − Impuesto a las ganancias")
    d.ec("Flujo de caja neto = EBITDA − Ganancias pagado − Δ Capital de trabajo − Inversiones",
         ["es el dinero que realmente entra o sale cada mes; las amortizaciones no son un pago y sólo bajan el impuesto"])
    d.p("Recuperación de la inversión (payback). Con flujos constantes vale Payback = Inversión / Flujo de caja periódico. "
        "Como en los primeros meses hay puesta en marcha, capital de trabajo e impuestos que se pagan con un año de "
        "atraso, se busca el mes exacto en que el flujo acumulado deja de ser negativo, interpolando dentro del mes:")
    d.ec("Payback = (k − 1) + |FA(k−1)| / FC(k)",
         ["k = primer mes con flujo acumulado FA ≥ 0", "FC(k) = flujo de caja del mes k",
          "no se cuenta el valor residual del final: la inversión se tiene que recuperar con lo que genera la operación"])
    d.ec("ROI = Beneficio neto / Inversión inicial × 100",
         ["se informa por año (año 2, el primero completo sin puesta en marcha) y acumulado a 5 años; la inversión "
          "incluye el capital de trabajo"])
    d.ec("Q_eq = Costos fijos / (Precio − Costo variable unitario)",
         ["punto de equilibrio en toneladas de producto vendido por año; los costos variables son los que bajan si se "
          "trabaja menos (cáscara, flete, envases, energía, parte de los insumos, comercialización e impuestos sobre las "
          "ventas)"])
    d.ec("VAN = Σ FC(k) / (1 + 0,10)^(k/12)        TIR: tasa que hace VAN = 0",
         ["k = mes, de 0 a 180; el VAN sí incluye el valor residual del terreno, de la obra civil y del capital de trabajo"])
    d.p("Capital de trabajo: dinero inmovilizado en ventas a cobrar (45 días), existencias (30 días de costos variables "
        "de producción) menos lo que se debe a proveedores (30 días de compras). Impuesto a las ganancias: escala de "
        "sociedades 2026 (25 %, 30 % y 35 %), con quebrantos que se compensan durante 5 años, liquidado al cierre de cada "
        "año y pagado en 12 anticipos durante el año siguiente. Amortizaciones impositivas: obra civil 50 años, equipos "
        "10 años, pala 5 años, ingeniería y puesta en marcha 5 años.")
    d.h("2.5. Herramientas y control", 2)
    d.p("El cálculo se hizo con un modelo en Python (fuente/economia/modelo_economico.py) y se repitió, fórmula por "
        "fórmula, en una planilla de Excel que recalcula sola (analisis_economico/Modelo_economico_Secadora_Guano.xlsx). "
        "La hoja «Indicadores» compara los 22 resultados de las dos implementaciones en los tres escenarios: la "
        "diferencia es cero. Las búsquedas por bisección del análisis inverso y la sensibilidad se hicieron sólo en "
        "Python.")


# =============================================================================== 3. revisión del proyecto
INCONSISTENCIAS = [
    ("Operarios por turno", "Informe (13.1): 2 por turno. Presupuesto: 3 por turno × USD 1.000 × 13 meses.",
     "± USD 13.000 por año y turno", "Realista y conservador: 3 (el tercero envasa). Optimista: 2."),
    ("«Ahorro en la gestión del guano» y «ahorro sanitario» como ingresos (USD 18.500/año)",
     "Evaluación del proyecto (tabla 21 de la Rev. C). La planta está junto al Parque Industrial y recibe guano de "
     "granjas por camión.", "Es un beneficio de la granja, no dinero que entra a la planta",
     "Se excluye del flujo de caja; se menciona como beneficio para las granjas."),
    ("Flete del guano húmedo", "Informe 16.3: «los camiones de guano llegan desde las granjas». El presupuesto no "
     "tiene ese costo.", "≈ USD 18.000/año a 20 km", "Se agrega (20 km realista, 40 km conservador); en el optimista "
     "lo pagan las granjas."),
    ("Pala cargadora", "Informe 13.1: el operario de campo alimenta la tolva con la pala; el presupuesto incluye su "
     "combustible pero no la máquina.", "USD 32.000 a 44.000 de inversión", "Se agrega una pala usada de ≈ 1 m³."),
    ("Terreno", "El lote de 9.120 m² no figura en la inversión.", "USD 25.000 a 91.000", "Se agrega como hipótesis "
     "(no hay precio publicado)."),
    ("Capital de trabajo", "No se considera.", "$ 3 a 33 millones según el escenario", "Se calcula mes a mes."),
    ("Precio de venta", f"Proyecto: USD {n(DAT['PRECIO_PROY'], 1)}/t ponderado, sin fuente de mercado. Mercado a granel: "
     "USD 30/t (semiseco, 10/2024). Minorista: $ 75.000 por bolsa de 25 kg.", "Es la variable de mayor efecto",
     "Tres hipótesis de precio (escenarios) y precio de equilibrio."),
    ("Sulfato de amonio del lavador (USD 5.000/año)", "Sin comprador ni registro como fertilizante.", "USD 5.000/año",
     "No se cuenta como ingreso."),
    ("Energía de la variante sin biogás", "presupuesto.py usa las cargas del TS-BIO (22,85 kW) y 100 kW contratados "
     "también para la variante sin biogás, y cuenta la iluminación dos veces (dentro de la demanda del TG2 y aparte).",
     "≈ USD 4.900/año", "Motores del TG2 sin TS-BIO (10,4 kW), iluminación una sola vez y 85 kW contratados."),
    ("Horas de marcha", "Balance y energía con 8 h/día; el estudio de fatiga usa 9 h/día de servicio (arranque y "
     "vaciado).", "+12 % de energía", "Energía con 1 h diaria de arranque y vaciado por turno."),
    ("Consumo eléctrico específico", "Indicador del plan de mantenimiento: menos de 170 kWh/t de producto. El "
     f"presupuesto del proyecto equivale a ≈ {n(ME.PRES['energia']['E_total_kWh'] / (ME.M_IN * (1 - ME.X_IN) / (1 - ME.X_OUT) * ME.H_TURNO * ME.DIAS_ANIO / 1000), 0)} kWh/t "
     f"y la estimación de este análisis, con los mismos datos, ≈ {n(R_['mes']['kwh'] / R_['mes']['seco_t'], 0)} kWh/t.",
     "El costo de energía podría ser menor", "Se mantiene la estimación del proyecto (lado seguro) y se estudia ±."),
    ("Consumo específico de cáscara", "Indicador del plan: 470 kg por t de agua evaporada (método de diseño, 314 kg/h). "
     f"Modelo térmico Rev. F: {n(DAT['Q_CASCARA'] * 1000, 0)} kg/t (419 t/año).", "−33 % de cáscara",
     "Se usa el modelo térmico (Rev. F). El indicador del plan quedó con el valor viejo."),
    ("Producción anual", "650 t/año (memoria Rev. C) contra 659 t/año del balance a 8 h × 250 días con 100 % de "
     "disponibilidad; el plan de mantenimiento fija una disponibilidad objetivo del 92 %.", "−8 % de producción",
     f"Realista: 92 % de disponibilidad: {n(a2(R_, 'seco_t'))} t/año de producto seco y "
     f"{n(a2(R_, 'comerciable_t'))} t comerciables (2 % de mermas)."),
    ("Precio de la cáscara", "Informe: 20 a 30 USD/t «a menos de 100 km», sin aclarar el flete. A 110 kg/m³ un camión "
     "lleva ≈ 10 t, un tercio que con granos.", "USD 25 → 47/t", "Flete estimado por volumen a 50 km (realista) y "
     "100 km (conservador)."),
    ("Segundo turno", "Proyecto: +USD 30.000 sin detalle; los «otros» costos (ácido, gasoil de la pala) no cambian "
     "con dos turnos.", "Subestima los costos de 2 turnos", "Se mantiene la inversión y los insumos se escalan con las "
     "horas."),
    ("Imprevistos", "7 % en un presupuesto de anteproyecto con precisión de ± 25 %.", "Inversión subestimada",
     "Conservador: inversión del proyecto +15 %; optimista −5 %."),
    ("IVA en los precios del presupuesto", "Algunos precios son «+ IVA» (matafuegos) y otros son de venta al público "
     "con IVA (Mercado Libre).", "Mezcla de bases", "Se toma el presupuesto como sin IVA; el IVA se trata aparte "
     "(apartado 5.3)."),
]

def pendientes():
    """Datos faltantes, con el peso de cada uno calculado con el escenario realista."""
    e = R_
    inv = e["inversion"]
    eq = sum(ME.FILAS[c][6] for c in ("A2", "A3", "A4", "A5", "A6", "A7")) * (1 + ME.IMPREV)
    return [
        ("Precio mayorista y volumen que compra el mercado (granel, big bag y bolsa de 25 kg)",
         "Decide si el proyecto es rentable", "Cartas de intención o cotizaciones de 3 a 5 compradores (horticultores, "
         "viveros, cooperativas, distribuidores)", "Hipótesis por escenario"),
        ("Tarifa T3 real de la LAR (cargo fijo, potencia y energía)",
         f"≈ {n(parte(e, 'energia_var', 'energia_fija'), 0)} % de los costos",
         "Pedido de factibilidad y cuadro tarifario a la LAR", "Estimación del proyecto (10/2026)"),
        ("Cáscara de arroz puesta en planta", f"≈ {n(parte(e, 'cascara'), 0)} % de los costos",
         "Cotización de molinos y de un fletero", "Flete estimado por volumen y USD 5/t en el molino (hipótesis)"),
        ("Quién paga el flete del guano y a qué distancia están las granjas",
         f"≈ {n(parte(e, 'flete_guano'), 0)} % de los costos", "Acuerdo con las granjas proveedoras",
         "20 km pagado por la planta (realista)"),
        ("Precio del terreno", f"≈ {n(inv['extra']['Terreno (lote de 9.120 m²)'] / inv['total'] * 100, 0)} % de la "
         "inversión", "Municipalidad de Crespo / dirección del Parque Industrial", "USD 5/m² (hipótesis)"),
        ("Convenio colectivo aplicable y cargas sociales", f"≈ {n(parte(e, 'mano_obra', 'administracion'), 0)} % de "
         "los costos", "Contador / sindicato", "UOM rama 17 y 30 % de cargas"),
        ("Alícuota de ingresos brutos, tasas municipales y beneficios del Parque Industrial",
         f"≈ {n(parte(e, 'iibb', 'seguros_tasas'), 0)} % de los costos", "ATER, Municipalidad",
         "1,5 % y 1 % de la inversión (proyecto)"),
        ("Cotización de los equipos A2 a A7 (consultas de la Rev. C, ± 25 %)",
         f"≈ {n(eq / inv['total'] * 100, 0)} % de la inversión", "Pedido de cotización a fabricantes",
         "Valores del proyecto"),
        ("Capacidad real medida", "No hay ningún equipo construido: todo es de diseño",
         "Módulo piloto previsto en la Rev. F", "Capacidad de diseño y del modelo térmico"),
        ("Análisis químico del producto (N, P₂O₅, K₂O, humedad, patógenos)", "Define el valor agronómico y el registro",
         "Laboratorio, con muestras del módulo piloto", "3 % / 2,8 % / 2,2 % en base seca (bibliografía)"),
        ("Registro del producto en SENASA (costo y plazo)", "Condición para vender", "Consulta al SENASA",
         "Incluido en ingeniería y habilitaciones (C1)"),
        ("Régimen de IVA y recupero del crédito fiscal de la inversión", "Costo financiero",
         "Contador", "Se supone recuperado (sin costo)"),
    ]


def revision(d):
    d.h("3. Revisión del proyecto: datos, inconsistencias y faltantes", 1)
    d.h("3.1. Documentos revisados", 2)
    d.p("Se leyó el repositorio completo de la entrega Rev. F: el informe final (balance de masa y energía, modelo "
        "térmico 6.7, operación, mantenimiento, ubicación y evaluación económica), la memoria de cálculo (TG2, "
        "iluminación, ventilación, biogás, carga de fuego y fatiga), el presupuesto con su planilla (inversión, despiece "
        "del secador, pedido a la LAR, energía y evaluación) y los resultados del estudio térmico. No hay ninguna "
        "inversión efectivamente realizada ni mediciones: el proyecto es un anteproyecto y todos sus números son de "
        "diseño.")
    d.h("3.2. Inconsistencias encontradas", 2)
    d.p("No se tomó ningún dato como correcto sólo por figurar en un documento. Estas son las diferencias entre archivos "
        "o con la realidad que cambian el resultado económico, y el criterio adoptado:")
    filas = [["#", "Dato", "Qué dice cada fuente", "Efecto", "Criterio adoptado"]]
    for i, (dato, fuentes, efecto, criterio) in enumerate(INCONSISTENCIAS, 1):
        filas.append([str(i), dato, fuentes, efecto, criterio])
    d.tabla("Inconsistencias y criterio adoptado", filas, anchos=[0.7, 3.2, 5.6, 2.6, 4.0], alin=["C", "L", "L", "L", "L"])
    d.h("3.3. Datos faltantes", 2)
    d.p("Los datos que siguen no están disponibles. No se ocultan: el análisis usa una hipótesis para cada uno y la "
        "sensibilidad muestra cuánto pesa. Antes de invertir hay que conseguirlos en este orden:")
    filas = [["Dato pendiente", "Por qué importa", "Cómo conseguirlo", "Qué se usó"]]
    filas += [list(p) for p in pendientes()]
    d.tabla("Datos pendientes", filas, anchos=[5.0, 3.4, 4.4, 3.4], alin=["L", "L", "L", "L"])


# =============================================================================== 4. descripción técnica
def tecnica(d):
    d.h("4. Descripción técnica de la secadora", 1)
    d.p("La planta seca el guano fresco de gallinas ponedoras en un secador continuo de cinta de malla inoxidable de "
        "tres pisos (SC-4, 2 m de ancho, 13 m de largo, 72 m² de superficie de secado), con aire caliente que produce un "
        "generador a cáscara de arroz de 880 kW con intercambiador humos-aire. El guano entra al 72 % de humedad por "
        "una cinta con tacos desde la tolva de recepción, recorre los tres pisos en unos 97 minutos y sale al 15 % "
        "por el sinfín de descarga; pasa una hora en una tolva de retención a 70 °C o más (higienización), se enfría, "
        "se zarandea y se despacha a granel o en bolsas. El aire de escape se trata en un ciclón y un lavador de gases "
        "con ácido. La humedad del producto se controla con la temperatura del aire (lazo en cascada, Rev. F).")
    m_ = R_["mes"]
    filas = [["Dato", "Valor", "Tipo"],
             ["Alimentación de diseño", "1.000 kg/h de guano húmedo (8 t en un turno de 8 h)", "R"],
             ["Humedad de entrada / de salida", "72 % / 15 % (base húmeda)", "R"],
             ["Producto seco / agua evaporada", "329,4 kg/h / 670,6 kg/h", "R"],
             ["Capacidad máxima con aire a 135 °C", f"1.440 kg/h al 72 % (evapora {n(DAT['W_MAX'], 0)} kg/h de agua)", "R"],
             ["Tiempo de residencia (un «ciclo» de una partícula)", "97 min", "R"],
             ["Combustible", f"cáscara de arroz, {n(DAT['Q_CASCARA'] * 1000, 0)} kg por t de agua evaporada (≈ 210 kg/h)", "R"],
             ["Potencia eléctrica instalada", "66,9 kW en el TGF + 27,2 kW en el TG2 sin biogás", "R/E"],
             ["Demanda eléctrica en marcha", f"{n(DAT['P_TGF'], 1)} kW (TGF) + {n(DAT['P_TG2'], 1)} kW (motores del "
              f"TG2) = {n(DAT['P_TGF'] + DAT['P_TG2'], 1)} kW, más la iluminación exterior", "R/E"],
             ["Operación", "1 turno de 8 h de carga + 1 h de arranque y vaciado; 250 días por año", "R"],
             ["Personal", "2 operarios por turno según el informe, 3 según el presupuesto", "R"],
             ["Mantenimiento", "preventivo programado (tabla 18 del informe); disponibilidad objetivo > 92 %", "R"],
             ["Energía por tonelada de producto", f"{n(m_['kwh'] / m_['seco_t'], 0)} kWh/t (estimación de este "
              "análisis con los datos del proyecto; el plan pide menos de 170)", "E"]]
    d.tabla("Datos técnicos que usa el análisis económico", filas, anchos=[5.6, 9.2, 1.2], alin=["L", "L", "C"])


# =============================================================================== 5. inversión
def inversion(d):
    d.h("5. Inversión inicial", 1)
    d.h("5.1. Inversión efectivamente realizada", 2)
    d.p("No hay inversión realizada: la secadora no se construyó, ni siquiera el módulo piloto que propone la Rev. F. "
        "Los montos que siguen son estimaciones de presupuesto con la precisión que declara el proyecto (± 25 %).")
    d.h("5.2. Inversión estimada por el proyecto (sin biogás)", 2)
    d.p("La tabla reproduce los ítems del presupuesto del proyecto sin la planta de biogás, con su cantidad, costo "
        "unitario y total. Los precios son del 23/10/2026; se informan en dólares y en pesos de noviembre.")
    filas = [["Cód.", "Concepto", "Cant.", "Unid.", "USD unit.", "USD total", "$ millones"]]
    for cod in ME.SIN_BIOGAS:
        _c, rub, desc, q, u, pu, tot, *_ = ME.FILAS[cod]
        txt = desc if len(desc) < 95 else desc[:92] + "…"
        filas.append([cod, f"{rub}: {txt}", n(q), u, n(pu), n(tot), mill(tot * D, 1)])
    sub = sum(ME.FILAS[c][6] for c in ME.SIN_BIOGAS)
    filas.append(["", "Subtotal", "", "", "", n(sub), mill(sub * D, 1)])
    filas.append(["", "Imprevistos (7 %)", "", "", "", n(sub * ME.IMPREV), mill(sub * ME.IMPREV * D, 1)])
    filas.append(["", "Inversión del proyecto sin biogás", "", "", "", n(sub * (1 + ME.IMPREV)),
                  mill(sub * (1 + ME.IMPREV) * D, 1)])
    d.tabla("Inversión estimada por el proyecto (presupuesto.json, sin los ítems B7 y B8)", filas,
            anchos=[1.0, 8.2, 1.1, 1.0, 1.6, 1.7, 1.6], alin=["C", "L", "R", "C", "R", "R", "R"], total=True)
    # agrupado por concepto pedido
    E_SEC = ME.PRES["secador"]["filas"]
    def secador(*claves):
        return sum(f[4] for f in E_SEC if any(k in f[0] for k in claves))
    estructura = secador("Perfiles", "Paneles", "Malla", "Guías", "Faldones", "Plenum", "Pasarela", "Bulonería",
                         "Pintura", "PTFE")
    transmision = secador("Tambor", "Rodamientos", "tensoras", "Motorreductor", "Cadena", "Rodillos")
    mo_sec = secador("Mano de obra", "Montaje")
    g = {c: ME.FILAS[c][6] for c in ME.SIN_BIOGAS}
    conceptos = [
        ("Estructura y materiales del secador (perfiles, paneles, malla inoxidable, guías, faldones, pasarela, "
         "bulonería, pintura)", estructura),
        ("Motores, reductores y transmisiones del secador (motorreductores, cadenas, tambores, rodamientos)", transmision),
        ("Mano de obra de fabricación y montaje del secador (1.900 h de taller + 240 h de montaje)", mo_sec),
        ("Generación de calor: generador a cáscara de 880 kW (A2) y silo de cáscara (A5)", g["A2"] + g["A5"]),
        ("Ventilación y aire (A3) y ventilación de la nave (B10, B11)", g["A3"] + g["B10"] + g["B11"]),
        ("Tratamiento de gases (A4) y aislación del escape (B18)", g["A4"] + g["B18"]),
        ("Transporte del material (A6) y descarga con tolva de retención (B17)", g["A6"] + g["B17"]),
        ("Control, automatización y sensores (A7: tablero, variadores, PLC, HMI, instrumentos)", g["A7"]),
        ("Instalaciones eléctricas y puesta a tierra (A8, B14, B15)", g["A8"] + g["B14"] + g["B15"]),
        ("Obra civil: nave, depósito, predio y vado (A9, B6, B9, B1)", g["A9"] + g["B6"] + g["B9"] + g["B1"]),
        ("Equipos auxiliares: recepción, zaranda, ensacadora y envasadora (B2 a B5)",
         g["B2"] + g["B3"] + g["B4"] + g["B5"]),
        ("Seguridad, incendio y mejoras por fatiga (B12, B13, B16)", g["B12"] + g["B13"] + g["B16"]),
        ("Ingeniería y habilitaciones (C1)", g["C1"]),
        ("Imprevistos (7 %)", sub * ME.IMPREV),
    ]
    filas = [["Concepto", "USD", "$ millones", "%"]]
    tot = sum(v for _c, v in conceptos)
    for c, v in conceptos:
        filas.append([c, n(v), mill(v * D, 1), pc(v / tot * 100)])
    filas.append(["Total del proyecto sin biogás", n(tot), mill(tot * D, 1), "100 %"])
    d.tabla("La misma inversión agrupada por concepto", filas, anchos=[10.5, 2.0, 2.0, 1.4], alin=["L", "R", "R", "R"],
            total=True)
    d.p("Herramientas y trabajos externos: las herramientas son del taller que fabrica (no se compran); los trabajos "
        "externos (rectificado, ensayos, termografía) están dentro de los ítems. Transporte e instalación: el montaje del "
        "secador está en el despiece (240 h); el flete de los equipos de fabricantes nacionales se supone incluido en "
        "sus precios o en los imprevistos, porque el proyecto no lo detalla.")
    d.h("5.3. Costos no contemplados por el proyecto", 2)
    filas = [["Concepto", "Tipo", "Conservador", "Realista", "Optimista"]]
    claves = list(R_["inversion"]["extra"].keys())
    for k in claves:
        tipo = "H" if ("Terreno" in k or "Puesta" in k) else "V"
        filas.append([k, tipo] + [n(ESC[e]["inversion"]["extra"][k]) for e in ESCS])
    filas.append(["Capital de trabajo de régimen ($ convertidos a USD)", "E"] +
                 [n(ESC[e]["ct_regimen"] / D) for e in ESCS])
    d.tabla("Costos no contemplados en el presupuesto del proyecto (USD)", filas, anchos=[8.8, 1.0, 2.1, 2.1, 2.1],
            alin=["L", "C", "R", "R", "R"])
    d.p("Quedan fuera del flujo de caja, con su efecto estimado: (a) el IVA de la inversión, que se paga al comprar y "
        "se recupera recién con el IVA de las ventas; con ventas de unos $ 110 millones por año, recuperar un crédito "
        "fiscal del orden de $ 200 millones llevaría muchos años, así que conviene estudiar con un contador el régimen "
        "de devolución anticipada para bienes de capital; (b) el financiamiento: todo se supone con capital propio; "
        "(c) un vehículo de reparto, porque las ventas se suponen ex planta; (d) la reposición de la pala o de "
        "equipos dentro de los 15 años: se supone que el mantenimiento los conserva. Esto no cambia el payback de la "
        "referencia (llega antes del año 5), pero hace optimista su VAN.")
    d.h("5.4. Inversión inicial consolidada", 2)
    filas = [["Concepto", "Conservador", "Realista", "Optimista"]]
    filas.append(["Factor sobre el presupuesto del proyecto (± 25 %)"] + [n(PARAMS[e]["f_inv"], 2) for e in ESCS])
    filas.append(["Inversión del proyecto sin biogás (USD)"] + [n(ESC[e]["inversion"]["proyecto"]) for e in ESCS])
    filas.append(["Costos no contemplados (USD)"] + [n(ESC[e]["inversion"]["total"] - ESC[e]["inversion"]["proyecto"])
                                                     for e in ESCS])
    filas.append(["Inversión inicial total (USD)"] + [n(ESC[e]["inv_total"] / D) for e in ESCS])
    filas.append(["Inversión inicial total ($ millones)"] + [mill(ESC[e]["inv_total"]) for e in ESCS])
    filas.append(["Capital de trabajo de régimen ($ millones)"] + [mill(ESC[e]["ct_regimen"]) for e in ESCS])
    filas.append(["Inversión total con capital de trabajo ($ millones)"] + [mill(ESC[e]["inv_con_ct"]) for e in ESCS])
    d.tabla("Inversión inicial consolidada", filas, anchos=[8.0, 2.7, 2.7, 2.7], alin=["L", "R", "R", "R"], total=True)
    d.recuadro("Cifra consolidada", f"La inversión inicial necesaria en el escenario realista es de "
               f"{pm(R_['inv_total'])} ({us(R_['inv_total'] / D)}), más {pm(R_['ct_regimen'])} de capital de trabajo: "
               f"{pm(R_['inv_con_ct'])} en total. El rango entre escenarios va de {pm(O_['inv_total'], 0)} a "
               f"{pm(C_['inv_total'], 0)}.")


# =============================================================================== 6. capacidad
def capacidad(d):
    d.h("6. Capacidad productiva", 1)
    d.h("6.1. Balance de masa", 2)
    d.p("Con la fórmula (1) y los datos de diseño (1.000 kg/h al 72 %, producto al 15 %):")
    d.calculo("m_s = 1.000 · (1 − 0,72)", "280,0 kg/h de sólido seco")
    d.calculo("m_out = 280 / (1 − 0,15)", "329,4 kg/h de producto seco")
    d.calculo("W = 1.000 − 329,4", "670,6 kg/h de agua evaporada")
    d.p("Por cada tonelada de guano húmedo salen 329 kg de producto seco al 15 % (323 kg comerciables, descontado un "
        "2 % de mermas): casi dos tercios de la masa son agua que se evapora. Por eso el guano húmedo procesado y el "
        "producto seco se informan siempre por separado.")
    d.h("6.2. Ciclo de trabajo", 2)
    d.p("La secadora es continua: no trabaja por tandas. Cada partícula tarda unos 97 minutos en recorrer los tres pisos; "
        "ese es el «tiempo por ciclo» del material. Para la operación se toma como ciclo un turno: arranque del hogar y "
        "precalentamiento, 8 h de alimentación y vaciado del secador (≈ 1 h en total sin carga). Con un turno por día hay "
        "un ciclo diario; con dos o tres turnos seguidos, el arranque y el vaciado se hacen una sola vez.")
    d.h("6.3. Producción del escenario realista", 2)
    m_ = R_["mes"]
    dias = PARAMS["realista"]["dias_anio"] / 12
    disp = PARAMS["realista"]["disp"]
    filas = [["Período", "Guano húmedo (t)", "Producto seco (t)", "Comerciable (t)", "Vendido (t)"]]
    hora = m_["humedo_t"] / m_["h_carga"]
    escalas = [("Por hora de carga (alimentación)", 1 / m_["h_carga"]), ("Por ciclo (1 turno, con 92 % de disponibilidad)",
                                                          1 / dias),
               ("Por día", 1 / dias), ("Por semana (5 días)", 5 / dias), ("Por mes", 1.0), ("Por año", 12.0)]
    for rot, f in escalas:
        filas.append([rot] + [n(m_[k] * f, 2 if f < 0.1 else 1) for k in ("humedo_t", "seco_t", "comerciable_t",
                                                                           "vendido_t")])
    d.tabla(f"Producción del escenario realista (1 turno, {n(dias, 1)} días por mes, disponibilidad del "
            f"{n(disp * 100)} %)", filas, anchos=[6.0, 2.6, 2.6, 2.6, 2.4], alin=["L", "R", "R", "R", "R"])
    d.p(f"Por hora de carga entra {n(hora, 2)} t de guano húmedo (el caudal de diseño) y sale "
        f"{n(m_['seco_t'] / m_['h_carga'] * 1000, 1)} kg de producto. En un año se procesan "
        f"{n(m_['humedo_t'] * 12)} t de guano húmedo, de las que quedan {n(m_['seco_t'] * 12)} t de producto seco; "
        f"descontadas las mermas ({n(PARAMS['realista']['merma'] * 100)} %) y suponiendo que se vende el "
        f"{n(PARAMS['realista']['vendido'] * 100)} %, se venden {n(m_['vendido_t'] * 12)} t.")
    d.h("6.4. Escenarios de producción", 2)
    filas = [["Dato", "Conservador", "Realista", "Optimista"]]
    for rot, k, f in (("Humedad del guano de entrada", "X_in", lambda v: pc(v * 100, 0)),
                      ("Días de operación por año", "dias_anio", lambda v: n(v)),
                      ("Disponibilidad", "disp", lambda v: pc(v * 100, 0)),
                      ("Mermas", "merma", lambda v: pc(v * 100, 0)),
                      ("Fracción vendida", "vendido", lambda v: pc(v * 100, 0))):
        filas.append([rot] + [f(PARAMS[e][k]) for e in ESCS])
    for rot, k, dd in (("Guano húmedo procesado (t/mes)", "humedo_t", 1), ("Producto seco (t/mes)", "seco_t", 1),
                       ("Producto vendido (t/mes)", "vendido_t", 1)):
        filas.append([rot] + [n(ESC[e]["mes"][k], dd) for e in ESCS])
    for rot, k in (("Guano húmedo procesado (t/año)", "humedo_t"), ("Producto seco (t/año)", "seco_t"),
                   ("Producto vendido (t/año)", "vendido_t")):
        filas.append([rot] + [n(a2(ESC[e], k)) for e in ESCS])
    d.tabla("Producción de los tres escenarios (1 turno de 8 h, 1.000 kg/h)", filas, anchos=[7.0, 3.0, 3.0, 3.0],
            alin=["L", "R", "R", "R"])
    d.figura("f1_produccion.png", "Guano húmedo procesado, producto seco obtenido y producto vendido por año")
    d.h("6.5. Capacidad máxima de la máquina", 2)
    d.p(f"El modelo térmico de la Rev. F muestra que, con aire a 135 °C, el secador evapora {n(DAT['W_MAX'], 0)} kg/h de "
        "agua: 1.440 kg/h de guano al 72 %. Esa es la capacidad máxima de una línea con el generador de 880 kW, que a "
        "ese caudal trabaja prácticamente a pleno (885 kW). Si el guano viene más húmedo, el límite baja (al 78 %, "
        "1.303 kg/h). El análisis inverso (apartado 12) usa este límite. No hay capacidad real medida: hasta que se "
        "pruebe el módulo piloto, todas las capacidades son de diseño.")


# =============================================================================== 7. costos
def costos(d):
    d.h("7. Costos operativos", 1)
    m_ = R_["mes"]
    c = m_["costos"]
    dias = PARAMS["realista"]["dias_anio"] / 12
    d.h("7.1. Energía eléctrica", 2)
    kwh_h = DAT["P_TGF"] + DAT["P_TG2"]
    d.p(f"Potencia instalada: 66,9 kW en el tablero general de fuerza (TGF) y 27,2 kW en el TG2 sin las cargas del "
        f"biogás. La demanda en marcha es de {n(DAT['P_TGF'], 1)} kW del TGF (66,9 kW × 0,8) más "
        f"{n(DAT['P_TG2'], 1)} kW de los motores del TG2: {n(kwh_h, 1)} kWh por hora de marcha; la iluminación "
        f"exterior y la central de incendio suman {n(DAT['KWH_ILUM'], 0)} kWh por año aparte. La planta marcha 9 h por "
        f"día con un turno (8 h de carga y 1 h de arranque y vaciado; con turnos seguidos, el arranque y el vaciado se "
        f"hacen una sola vez). Se contratan {n(DAT['P_CONTRATADA'])} kW a la LAR con la tarifa T3 "
        "de grandes demandas en baja tensión estimada por el proyecto (cargo fijo $ 85.000/mes, potencia "
        "$ 14.500/kW·mes y energía $ 185/kWh; valores de octubre de 2026 a confirmar con la LAR).")
    filas = [["Concepto", "Valor"],
             ["Consumo por hora de marcha", f"{n(kwh_h, 1)} kWh"],
             ["Consumo por ciclo (1 turno)", f"{n(m_['kwh'] / dias, 0)} kWh"],
             ["Consumo diario / mensual", f"{n(m_['kwh'] / dias, 0)} kWh / {n(m_['kwh'], 0)} kWh"],
             ["Costo de la energía consumida", f"$ {n(c['energia_var'], 0)} por mes"],
             ["Cargo fijo y potencia contratada", f"$ {n(c['energia_fija'], 0)} por mes"],
             ["Costo total de la electricidad", f"$ {n(c['energia_var'] + c['energia_fija'], 0)} por mes"],
             ["Precio medio resultante", f"$ {n((c['energia_var'] + c['energia_fija']) / m_['kwh'], 1)}/kWh"],
             ["Energía por tonelada de producto", f"{n(m_['kwh'] / m_['seco_t'], 0)} kWh/t"]]
    d.tabla("Energía eléctrica del escenario realista", filas, anchos=[8.0, 7.0], alin=["L", "R"])
    d.h("7.2. Combustible: cáscara de arroz", 2)
    hora = m_["cascara_t"] / m_["h_carga"] * 1000
    d.p(f"El consumo sale del modelo térmico de la Rev. F: 419 t por año para un turno, es decir "
        f"{n(DAT['Q_CASCARA'] * 1000, 0)} kg de cáscara por tonelada de agua evaporada (incluye las estaciones del año). "
        f"En el escenario realista se queman {n(hora, 0)} kg/h. El precio puesto en planta (USD "
        f"{n(PARAMS['realista']['cascara'], 1)}/t) suma una hipótesis de USD 5/t en el molino (no hay precio publicado) "
        f"y el flete: la cáscara pesa 110 kg/m³ y un "
        f"camión lleva unas 10 t, un tercio que con granos, así que el flete por tonelada es el triple que la tarifa de "
        f"referencia de granos (≈ USD {n(DAT['FLETE_CASCARA_50'], 1)}/t a 50 km).")
    filas = [["Concepto", "Valor"],
             ["Consumo por hora de carga", f"{n(hora, 0)} kg/h"],
             ["Costo por hora", f"$ {n(c['cascara'] / m_['h_carga'], 0)}"],
             ["Costo por ciclo (1 turno)", f"$ {n(c['cascara'] / dias, 0)}"],
             ["Consumo y costo mensual", f"{n(m_['cascara_t'], 1)} t – $ {n(c['cascara'], 0)}"]]
    d.tabla("Cáscara de arroz del escenario realista", filas, anchos=[8.0, 7.0], alin=["L", "R"])
    d.h("7.3. Mano de obra", 2)
    d.p(f"Personal: 3 operarios por turno (operador de proceso, operario de campo con la pala y operario de envasado, "
        f"como el presupuesto) y 1 persona de administración y ventas. Cada uno trabaja el turno de 8 h más el "
        f"arranque y el vaciado. El costo laboral se toma del sueldo de un operario calificado de la UOM rama 17 de "
        f"noviembre de 2026 ($ 5.054/h × 200 h = $ {n(ME.SALARIO_REF, 0)} por mes), con 13 sueldos por año (aguinaldo) "
        f"y 30 % de contribuciones patronales, ART y seguro de vida: $ {n(ME.COSTO_EMPLEADO, 0)} por persona y por mes. "
        f"Se suman $ {n(ME.HONORARIOS, 0)} por mes de honorarios contables, legales y del responsable técnico.")
    filas = [["Concepto", "Personas", "$ por mes"],
             ["Operarios (1 turno)", "3", n(c["mano_obra"], 0)],
             ["Administración y ventas", "1", n(ME.COSTO_EMPLEADO, 0)],
             ["Honorarios profesionales", "—", n(ME.HONORARIOS, 0)],
             ["Total", "4", n(c["mano_obra"] + c["administracion"], 0)]]
    d.tabla("Mano de obra y administración del escenario realista", filas, anchos=[8.0, 2.5, 4.5],
            alin=["L", "C", "R"], total=True)
    d.h("7.4. Mantenimiento", 2)
    d.p(f"Se presupuesta el {n(PARAMS['realista']['mant'] * 100)} % por año del valor de los equipos y de la pala "
        f"(criterio del proyecto), un 70 % fijo y un 30 % que crece con las horas de marcha: $ {n(c['mantenimiento'], 0)} "
        "por mes. Cubre lubricantes (aceite sintético de los motorreductores, grasa de alta temperatura, aceite de "
        "cadenas), repuestos y componentes de desgaste (malla, guías de PTFE y UHMW-PE, labios de los faldones, paletas "
        "del esparcidor, hélices de sinfines, refractario, relleno del lavador), el mantenimiento preventivo de la tabla "
        "18 del informe y las reparaciones. La vida útil de los componentes principales es la que surge de la memoria de "
        "cálculo:")
    filas = [["Componente", "Vida útil o reposición", "Fuente"],
             ["Ejes de los tambores", "Vida infinita a fatiga (n = 1,59 Goodman, asientos rectificados)", "Memoria, fatiga"],
             ["Rodamientos UCF 212 / UCT 210", "L10 mayor a 6,8 × 10⁷ h (0,4 rpm): manda la carga estática (s0 ≥ 8)",
              "Memoria, fatiga"],
             ["Cadena ASA 60", "n = 3,27 a fatiga; se lubrica semanalmente", "Memoria, fatiga"],
             ["Aceite de los motorreductores", "Anual o 5.000 h", "Plan de mantenimiento"],
             ["Malla, guías y faldones", "Se mide el desgaste cada 6 meses y se reemplazan tramos; vida a definir con el "
              "fabricante", "Plan (sin dato de vida)"],
             ["Refractario del hogar", "Inspección semestral y reparación de grietas", "Plan (sin dato de vida)"],
             ["Rodamientos de ventiladores", "Cambio anual con el balanceo", "Plan de mantenimiento"]]
    d.tabla("Vida útil y reposición de los componentes principales", filas, anchos=[4.2, 8.4, 3.4], alin=["L", "L", "L"])
    d.h("7.5. Otros costos", 2)
    d.lista([
        f"Embalaje: bolsa de rafia laminada de 25 kg a $ {n(ME.BOLSA_25, 0)} (Mercado Libre, noviembre de 2026; el "
        f"proyecto usa USD 0,45, igual). En el escenario realista va en bolsas el 40 % de lo vendido: "
        f"$ {n(c['envases'], 0)} por mes.",
        f"Transporte: flete del guano húmedo desde las granjas (20 km, ≈ USD {n(PARAMS['realista']['flete_guano'], 1)}/t "
        f"con la tarifa de referencia de granos): $ {n(c['flete_guano'], 0)} por mes. El producto se vende ex planta; la "
        "entrega, si se bonifica, está en la comercialización.",
        "Almacenamiento: depósito propio de 240 m² (inversión B6); su costo está en el seguro, las tasas y el capital de "
        "trabajo inmovilizado en existencias.",
        f"Limpieza, agua, ácido del lavador, gasoil de la pala, monitoreos ambientales e higiene y seguridad: los "
        f"USD 8.800 por año del proyecto, 40 % fijo y 60 % según las horas: $ {n(c['otros_insumos'], 0)} por mes.",
        f"Administración: $ {n(c['administracion'], 0)} por mes (apartado 7.3).",
        f"Seguros, impuesto inmobiliario y tasas fijas: 1 % de la inversión por año (proyecto): "
        f"$ {n(c['seguros_tasas'], 0)} por mes.",
        f"Comercialización (comisiones, publicidad, muestras, entregas bonificadas): "
        f"{n(PARAMS['realista']['comerc'] * 100)} % de las ventas.",
        "Impuestos sobre la actividad: ingresos brutos 1,5 % de las ventas; impuesto a los débitos y créditos bancarios "
        "0,6 % de cada cobro y de cada pago; impuesto a las ganancias según la escala de sociedades 2026 (apartado 9).",
    ])
    d.p("Para no contar dos veces un mismo gasto: el combustible de la pala está sólo en «otros insumos»; el "
        "mantenimiento de la pala, en el mantenimiento; el seguro del 1 % del proyecto no incluye ingresos brutos ni "
        "ganancias, que se calculan aparte; y la amortización no se suma al flujo de caja (sólo reduce el impuesto).")
    d.h("7.6. Resumen de costos y costo por kilogramo", 2)
    filas = [["Rubro ($ por mes)", "Conservador", "Realista", "Optimista"]]
    rubros = [("Cáscara de arroz", ("cascara",)), ("Energía eléctrica", ("energia_var", "energia_fija")),
              ("Flete del guano húmedo", ("flete_guano",)), ("Envases", ("envases",)),
              ("Otros insumos (ácido, agua, gasoil, monitoreos)", ("otros_insumos",)),
              ("Mantenimiento y repuestos", ("mantenimiento",)), ("Mano de obra operativa", ("mano_obra",)),
              ("Administración, ventas y honorarios", ("administracion",)), ("Seguros, inmobiliario y tasas",
                                                                            ("seguros_tasas",)),
              ("Comercialización", ("comercializacion",)), ("Ingresos brutos", ("iibb",)),
              ("Impuesto a los débitos y créditos", ("deb_cred",))]
    for rot, ks in rubros:
        filas.append([rot] + [n(sum(ESC[e]["mes"]["costos"][k] for k in ks), 0) for e in ESCS])
    filas.append(["Costo operativo total"] + [n(ESC[e]["mes"]["total"], 0) for e in ESCS])
    d.tabla("Costos operativos de un mes de régimen", filas, anchos=[7.6, 2.8, 2.8, 2.8], alin=["L", "R", "R", "R"],
            total=True)
    filas = [["Costo por kilogramo", "Conservador", "Realista", "Optimista"],
             ["Costo de producción por kg de producto seco obtenido"] + [f"$ {n(ESC[e]['costo_prod_kg'], 0)}"
                                                                          for e in ESCS],
             ["Costo operativo total por kg vendido"] + [f"$ {n(ESC[e]['costo_total_kg'], 0)}" for e in ESCS],
             ["Costo total con amortizaciones por kg vendido"] + [f"$ {n(ESC[e]['costo_total_kg_amort'], 0)}"
                                                                  for e in ESCS],
             ["Precio medio de venta por kg"] + [f"$ {n(ESC[e]['precio_t'] / 1000, 0)}" for e in ESCS]]
    d.tabla("Costo por kilogramo de producto seco", filas, anchos=[7.6, 2.8, 2.8, 2.8], alin=["L", "R", "R", "R"],
            resaltar=[2])
    d.figura("f2_ingresos_costos.png", "Ventas y costos de un mes de régimen, con los costos apilados por rubro")
    d.p("El costo fijo pesa mucho porque la planta es grande para lo que produce en un turno: mano de obra, "
        "administración, mantenimiento, seguros y la parte fija de la energía son más de la mitad del costo total. Por "
        "eso el costo por kilogramo baja mucho al trabajar más horas o a mayor caudal (apartado 12).")


# =============================================================================== 8. ingresos
def ingresos(d):
    d.h("8. Ingresos", 1)
    d.h("8.1. Producción obtenida y producción comercializada", 2)
    d.p("Del producto seco que sale del secador se descuentan las mermas (rechazo de la zaranda, polvo no recuperado, "
        "manipuleo) y sólo una parte se vende: no hay contratos ni un estudio de mercado que respalde vender todo, y la "
        "demanda de abonos es estacional. Se supone que se vende el 80 % (conservador), el 90 % (realista) o el 95 % "
        "(optimista) del producto comerciable; el resto se entrega sin cargo o se aplica en campos cercanos.")
    d.h("8.2. Precios de referencia relevados", 2)
    filas = [["Referencia", "Valor", "Fecha / antigüedad", "Qué representa"],
             ["Guano seco a granel (Bahía Blanca), 40-50 % de materia seca", "USD 30/t puesto en destino",
              "10/2024 (25 meses)", "Precio de mercado de granel; producto semiseco, no higienizado"],
             ["Guano en Salta", "USD 20/m³", "10/2024 (25 meses)", "Granel"],
             ["Fertilizante guano gallinaza, bolsa de 25 kg (al público, con IVA)", "$ 75.000 la bolsa",
              "relevado 11/2026", "Precio minorista: no es precio de planta"],
             ["Guano de gallina, 1 kg (al público; Caravanas, Mercado Libre)", "$ 18.500", "relevado 11/2026",
              "Minorista, envase chico"],
             ["Urea (mayorista)", "USD 595 a 605/t", "7/11/2026", "Base del valor del nitrógeno"],
             ["Fosfato monoamónico MAP (mayorista)", "USD 965 a 995/t", "7/11/2026", "Base del valor del fósforo"],
             ["Cloruro de potasio (promedio mundial)", "USD 383/t", "2026 (Banco Mundial)", "Base del valor del potasio"],
             ["Precio supuesto por el proyecto", f"USD {n(DAT['PRECIO_PROY'], 1)}/t ponderado", "10/2026",
              "60 % bolsa 25 kg a USD 250, 15 % bolsas chicas a USD 600, 25 % granel a USD 130; sin fuente"]]
    d.tabla("Precios de referencia del producto", filas, anchos=[5.4, 3.2, 2.8, 4.6], alin=["L", "R", "L", "L"])
    d.h("8.3. Valor agronómico del producto", 2)
    d.p("Un comprador agrícola compara el guano con los fertilizantes que reemplaza. Con los nutrientes del informe "
        "(3 % de N, 2,8 % de P₂O₅ y 2,2 % de K₂O en base seca), el producto al 15 % de humedad tiene por tonelada "
        "25,5 kg de N, 23,8 kg de P₂O₅ y 18,7 kg de K₂O. El kilogramo de N se valúa con la urea (46 % de N), el de P₂O₅ "
        "con el MAP (11-52-0, descontado su nitrógeno) y el de K₂O con el cloruro de potasio (60 %):")
    d.calculo(f"N: 600 / 460 = USD {n(DAT['USD_KG_N'], 3)}/kg;  P₂O₅: (0,980 − 0,11 × {n(DAT['USD_KG_N'], 3)}) / 0,52 = "
              f"USD {n(DAT['USD_KG_P2O5'], 3)}/kg;  K₂O: 0,383 / 0,60 = USD {n(DAT['USD_KG_K2O'], 3)}/kg",
              "precios por kg de nutriente")
    d.calculo(f"25,5 × {n(DAT['USD_KG_N'], 3)} + 23,8 × {n(DAT['USD_KG_P2O5'], 3)} + 18,7 × {n(DAT['USD_KG_K2O'], 3)}",
              f"USD {n(DAT['VALOR_NPK'], 1)} por tonelada de producto")
    d.p("Es un techo para la venta a granel a productores extensivos: el nitrógeno orgánico no está todo disponible el "
        "primer año, aunque la materia orgánica suma valor en horticultura. El precio de granel de 2024 (USD 30/t con "
        "50 % de materia seca, es decir USD 60 por tonelada de materia seca) llevado a un producto con 85 % de materia "
        f"seca y descontado el flete hasta el comprador da USD {n(DAT['GRANEL_MERCADO'], 1)}/t ex planta.")
    d.h("8.4. Hipótesis de precio de cada escenario", 2)
    d.p("No hay un precio de venta mayorista verificado: es un dato pendiente. Por eso cada escenario usa una hipótesis "
        "distinta, y la sensibilidad y el análisis inverso buscan el precio necesario.")
    filas = [["Escenario", "Canales de venta", "Precio medio ex planta", "Base"]]
    for e in ESCS:
        mix = PARAMS[e]["mix"]
        txt = "; ".join(f"{k} {n(f * 100)} % a USD {n(pr, 1)}/t" for k, (f, pr) in mix.items())
        base = {"conservador": "Mercado de granel 2024 llevado a producto seco",
                "realista": "Granel al valor agronómico; bolsa de 25 kg a USD 200/t (hipótesis: 80 % del proyecto)",
                "optimista": "Precios del proyecto (sin cotizaciones)"}[e]
        filas.append([NOM[e], txt, f"USD {n(ESC[e]['precio_t'] / D, 1)}/t ($ {n(ESC[e]['precio_t'] / 1000, 0)}/kg)", base])
    d.tabla("Hipótesis de precio por escenario (sin IVA)", filas, anchos=[2.4, 6.0, 3.2, 4.4], alin=["L", "L", "R", "L"])
    d.h("8.5. Ingresos", 2)
    filas = [["Ingreso", "Conservador", "Realista", "Optimista"]]
    for rot, f in (("Por kg vendido ($)", lambda e: n(e["precio_t"] / 1000, 0)),
                   ("Por ciclo de 1 turno ($)", lambda e: n(e["mes"]["ventas"] / (PARAMS[e["nombre"]]["dias_anio"] / 12), 0)),
                   ("Por día ($)", lambda e: n(e["mes"]["ventas"] / (PARAMS[e["nombre"]]["dias_anio"] / 12), 0)),
                   ("Por mes ($ millones)", lambda e: mill(e["mes"]["ventas"], 2)),
                   ("Por año ($ millones)", lambda e: mill(a2(e, "ventas"), 1))):
        filas.append([rot] + [f(ESC[e]) for e in ESCS])
    d.tabla("Ingresos por ventas (régimen)", filas, anchos=[6.4, 3.2, 3.2, 3.2], alin=["L", "R", "R", "R"])
    d.p("Facturar no es ganar: de cada peso que entra hay que pagar los costos del apartado 7 antes de que quede algún "
        "beneficio. El apartado siguiente hace esa cuenta.")


# =============================================================================== 9. rentabilidad
def rentabilidad(d):
    d.h("9. Rentabilidad y recuperación de la inversión", 1)
    d.h("9.1. Beneficio bruto, beneficio operativo y flujo de caja", 2)
    filas = [["$ millones por año (año de régimen)", "Conservador", "Realista", "Optimista"]]
    def f(e, k):
        return mill(a2(ESC[e], k), 1)
    filas.append(["Ventas"] + [f(e, "ventas") for e in ESCS])
    filas.append(["Costo de producción"] + [mill(ESC[e]["anio2"]["produccion"], 1) for e in ESCS])
    filas.append(["Beneficio bruto"] + [mill(ESC[e]["anio2"]["ventas"] - ESC[e]["anio2"]["produccion"], 1) for e in ESCS])
    filas.append(["Gastos de estructura y comerciales"] + [mill(ESC[e]["anio2"]["estructura"] + ESC[e]["anio2"]["comerciales"], 1)
                                                         for e in ESCS])
    filas.append(["Beneficio operativo antes de amortizaciones (EBITDA)"] + [f(e, "ebitda") for e in ESCS])
    filas.append(["Amortizaciones"] + [f(e, "amortizacion") for e in ESCS])
    filas.append(["Beneficio operativo (EBIT)"] + [f(e, "ebit") for e in ESCS])
    filas.append(["Impuesto a las ganancias devengado"] + [f(e, "ganancias_devengado") for e in ESCS])
    filas.append(["Beneficio neto"] + [f(e, "beneficio_neto") for e in ESCS])
    filas.append(["Flujo de caja neto (EBITDA − ganancias pagado − Δ capital de trabajo; año 3)"] +
                 [mill(a3(ESC[e], "flujo"), 1) for e in ESCS])
    d.tabla("Estado de resultados y flujo de caja de un año de régimen", filas, anchos=[8.2, 2.6, 2.6, 2.6],
            alin=["L", "R", "R", "R"], resaltar=[9, 10])
    d.p(f"En el escenario realista las ventas ({pm(a2(R_, 'ventas'), 1)} por año) no alcanzan a pagar ni el costo de "
        f"producción ({pm(R_['anio2']['produccion'], 1)}): el beneficio bruto ya es negativo. En el optimista el "
        f"EBITDA es positivo ({pm(a2(O_, 'ebitda'), 1)} por año), pero las amortizaciones lo absorben y el beneficio neto "
        "queda cerca de cero. No se paga impuesto a las ganancias porque no hay ganancia imponible.")
    d.h("9.2. Período de recuperación de la inversión", 2)
    d.p("Con la fórmula de flujo constante, Payback = Inversión / Flujo de caja mensual, el escenario realista no tiene "
        "payback porque su flujo es negativo. En el optimista, con un flujo de "
        f"{pm(a3(O_, 'flujo') / 12, 2)} por mes, daría {n(O_['payback_formula'], 0)} meses; pero el cálculo mes a mes, que "
        "cuenta la puesta en marcha, el capital de trabajo y el impuesto a las ganancias que aparece cuando terminan "
        "las amortizaciones de la pala y de los equipos, muestra que en 180 meses el flujo acumulado no llega a cero: "
        "con un turno la inversión no se recupera en la vida del proyecto en ningún escenario.")
    d.figura("f4_recuperacion_escenarios.png", "Flujo de caja acumulado de los tres escenarios y de la configuración de "
             "referencia (sin valor residual)")
    rp = REF["payback_meses"]
    d.p(f"Para mostrar la curva de recuperación con el mes exacto se usa la configuración de referencia: la misma planta "
        f"trabajando 2 turnos a 1.440 kg/h (aire a 135 °C), con los precios y demás supuestos del escenario optimista y "
        f"USD 32.000 de inversión adicional (segundo turno y tolva de retención mayor). Su inversión es de "
        f"{pm(REF['inv_total'])}; el flujo acumulado arranca en −{mill(REF['inv_total'], 1)} millones, baja un poco "
        f"durante la puesta en marcha (capital de trabajo) y se hace cero en el {anio_mes(rp)}: {mes_txt(rp)} exactos. "
        f"Descontado al 10 % real, la recuperación llega en {mes_txt(REF['payback_descontado'])}.")
    d.figura("f3_recuperacion_referencia.png", "Curva de recuperación mes a mes de la referencia (2 turnos a 1.440 kg/h, "
             "precios del proyecto): inversión acumulada, flujo mensual, flujo acumulado y mes de recuperación")
    filas = [["Mes", "Flujo del mes ($ M)", "Acumulado ($ M)"]]
    fm = REF["flujo_mensual"]
    for k in (0, 1, 3, 6, 12, 24, 36, 47, 48, 60):
        filas.append([str(k), mill(fm[k]["flujo"], 1), mill(fm[k]["acumulado"], 1)])
    d.tabla("Flujo mensual y acumulado de la referencia en meses seleccionados", filas, anchos=[2.0, 4.0, 4.0],
            alin=["C", "R", "R"], resaltar=[8, 9])
    d.h("9.3. Retorno sobre la inversión (ROI)", 2)
    filas = [["ROI", "Conservador", "Realista", "Optimista", "Referencia"]]
    filas.append(["Anual, año 2: beneficio neto / (inversión + capital de trabajo)"] +
                 [pc(ESC[e]["roi_anual"]) for e in ESCS] + [pc(REF["roi_anual"])])
    filas.append(["Acumulado a 5 años: Σ beneficio neto de los años 1 a 5 / (inversión + capital de trabajo)"] +
                 [pc(ESC[e]["roi_5"]) for e in ESCS] + [pc(REF["roi_5"])])
    d.tabla("Retorno sobre la inversión", filas, anchos=[6.4, 2.4, 2.4, 2.4, 2.4], alin=["L", "R", "R", "R", "R"])
    d.p(f"El ROI se calcula con el beneficio neto contable (después de amortizaciones e impuestos). La referencia rinde "
        f"un {pc(REF['roi_anual'])} anual: en 5 años devuelve el {pc(REF['roi_5'], 0)} de lo invertido como beneficio "
        "neto, y el resto de la recuperación de caja viene de las amortizaciones, que son dinero que queda en la empresa.")
    d.h("9.4. Punto de equilibrio", 2)
    filas = [["Concepto", "Conservador", "Realista", "Optimista"]]
    filas.append(["Precio por t vendida ($)"] + [n(ESC[e]["precio_t"], 0) for e in ESCS])
    filas.append(["Contribución por t vendida ($)"] + [n(ESC[e]["contribucion_t"], 0) for e in ESCS])
    filas.append(["Costos fijos de caja ($ por año)"] + [mill(ESC[e]["fijos_mes"] * 12, 1) + " M" for e in ESCS])
    filas.append(["Equilibrio operativo: producto vendido (t/año)"] +
                 [("no existe" if ESC[e]["pe_operativo_t"] is None else n(ESC[e]["pe_operativo_t"], 0)) for e in ESCS])
    filas.append(["Equilibrio contable, con amortizaciones (t/año)"] +
                 [("no existe" if ESC[e]["pe_contable_t"] is None else n(ESC[e]["pe_contable_t"], 0)) for e in ESCS])
    filas.append(["Producto vendido en el escenario (t/año)"] + [n(a2(ESC[e], "vendido_t"), 0) for e in ESCS])
    filas.append(["Precio de equilibrio operativo, EBITDA = 0 (USD/t)"] +
                 [("no existe" if ESC[e]["precio_eq_t"] is None else n(ESC[e]["precio_eq_t"] / D, 0)) for e in ESCS])
    d.tabla("Punto de equilibrio en toneladas de producto seco vendido por año", filas, anchos=[7.0, 3.0, 3.0, 3.0],
            alin=["L", "R", "R", "R"])
    d.p(f"En el escenario conservador cada tonelada vendida pierde plata aun antes de los costos fijos (contribución "
        f"negativa): no existe punto de equilibrio. En el realista la contribución es casi nula "
        f"($ {n(R_['contribucion_t'], 0)} por tonelada), de modo que haría falta vender "
        f"{n(R_['pe_operativo_t'], 0)} t/año: unas {n(R_['pe_operativo_t'] / a2(R_, 'vendido_t'), 0)} veces lo que vende "
        f"con un turno. En el optimista alcanza con vender "
        f"{n(O_['pe_operativo_t'], 0)} t/año para cubrir los costos de caja, pero para cubrir también las amortizaciones "
        f"hacen falta {n(O_['pe_contable_t'], 0)} t/año, más de lo que se vende con un turno "
        f"({n(a2(O_, 'vendido_t'), 0)} t).")
    d.p(f"Visto por el precio, el EBITDA del escenario realista se anula con un precio medio de "
        f"$ {n(R_['precio_eq_t'] / 1000, 0)}/kg (USD {n(R_['precio_eq_t'] / D, 0)}/t): algo más que el costo operativo "
        f"por kilogramo vendido ($ {n(R_['costo_total_kg'], 0)}), porque la comercialización, ingresos brutos y el "
        "impuesto a los débitos y créditos crecen con el precio.")
    d.h("9.5. Rentabilidad por kilogramo", 2)
    filas = [["$ por kg vendido", "Conservador", "Realista", "Optimista", "Referencia"]]
    filas.append(["Precio de venta"] + [n(ESC[e]["precio_t"] / 1000, 0) for e in ESCS] + [n(REF["precio_t"] / 1000, 0)])
    filas.append(["Costo operativo"] + [n(ESC[e]["costo_total_kg"], 0) for e in ESCS] + [n(REF["costo_total_kg"], 0)])
    filas.append(["Beneficio neto (después de amortizaciones e impuestos)"] + [n(ESC[e]["neto_kg"], 0) for e in ESCS] +
                 [n(REF["neto_kg"], 0)])
    d.tabla("Rentabilidad por kilogramo comercializado", filas, anchos=[6.6, 2.3, 2.3, 2.3, 2.5],
            alin=["L", "R", "R", "R", "R"])
    d.h("9.6. VAN y TIR", 2)
    filas = [["Indicador (15 años, 10 % real)", "Conservador", "Realista", "Optimista", "Referencia"]]
    filas.append(["VAN ($ millones)"] + [mill(ESC[e]["van"], 0) for e in ESCS] + [mill(REF["van"], 0)])
    filas.append(["TIR (anual, real)"] + [("—" if ESC[e]["tir"] is None else pc(ESC[e]["tir"] * 100)) for e in ESCS] +
                 [pc(REF["tir"] * 100)])
    d.tabla("Valor actual neto y tasa interna de retorno", filas, anchos=[6.6, 2.3, 2.3, 2.3, 2.5],
            alin=["L", "R", "R", "R", "R"])
    d.p("El VAN incluye el valor residual del terreno, de la obra civil y del capital de trabajo al cabo de 15 años. "
        "Una TIR menor que el 10 % real significa que el dinero rinde menos que la tasa exigida; las TIR negativas del "
        "conservador y del realista existen sólo por ese valor residual del final.")


# =============================================================================== 10. escenarios
def escenarios_cap(d):
    d.h("10. Escenarios: comparación y variables de mayor impacto", 1)
    d.p("Cada escenario cambia a la vez varios supuestos, en el sentido que corresponde a su nombre:")
    filas = [["Supuesto", "Conservador", "Realista", "Optimista"]]
    for rot, k, f in (("Humedad del guano", "X_in", lambda v: pc(v * 100, 0)),
                      ("Días por año", "dias_anio", lambda v: n(v)),
                      ("Disponibilidad", "disp", lambda v: pc(v * 100, 0)),
                      ("Fracción vendida", "vendido", lambda v: pc(v * 100, 0)),
                      ("Cáscara puesta en planta (USD/t)", "cascara", lambda v: n(v, 1)),
                      ("Flete del guano (USD/t)", "flete_guano", lambda v: n(v, 1)),
                      ("Tarifa eléctrica (factor)", "tarifa", lambda v: n(v, 2)),
                      ("Operarios por turno", "op_turno", lambda v: n(v)),
                      ("Comercialización (% de ventas)", "comerc", lambda v: pc(v * 100, 0)),
                      ("Mantenimiento (% de equipos)", "mant", lambda v: pc(v * 100, 1)),
                      ("Inversión (factor sobre el proyecto)", "f_inv", lambda v: n(v, 2)),
                      ("Terreno (USD/m²)", "tierra", lambda v: n(v, 1)),
                      ("Pala usada (USD)", "pala", lambda v: n(v))):
        filas.append([rot] + [f(PARAMS[e][k]) for e in ESCS])
    filas.append(["Precio medio (USD/t)"] + [n(ESC[e]["precio_t"] / D, 1) for e in ESCS])
    d.tabla("Supuestos que cambian entre escenarios", filas, anchos=[7.0, 3.0, 3.0, 3.0], alin=["L", "R", "R", "R"])
    tabla_escenarios(d, "Comparación de resultados de los escenarios")
    d.h("10.1. Del resultado del proyecto al escenario realista", 2)
    d.p("La evaluación del proyecto (variante sin biogás, un turno) daba un beneficio de USD 77.933 por año y un repago "
        "de 9,9 años. El puente siguiente muestra, paso a paso, por qué el escenario realista da otro número. Cada paso "
        "cambia un solo supuesto y se mide con un año de régimen:")
    filas = [["Paso", "USD por año"]]
    for t, v in E["puente"]["pasos"]:
        filas.append([t, ("+" if v > 0 else "") + n(v, 0)])
    filas.append(["Flujo de caja del escenario realista (año 2)", n(E["puente"]["flujo_realista_usd"], 0)])
    d.tabla("Puente entre la evaluación del proyecto y el escenario realista", filas, anchos=[12.6, 3.0],
            alin=["L", "R"], total=True)
    d.figura("f8_puente.png", "Del beneficio anual del proyecto al flujo de caja del escenario realista (USD por año)")
    pz = {t.split(" ")[0] + t.split(" ")[1]: v for t, v in E["puente"]["pasos"]}
    pasos = E["puente"]["pasos"]
    def paso(prefijo):
        return next(v for t, v in pasos if t.startswith(prefijo))
    d.p(f"Las variables con más impacto son, en este orden: el precio medio ({n(paso('Precio medio'), 0)} USD por año al "
        f"pasar del precio del proyecto al realista), los volúmenes realmente vendidos (disponibilidad, mermas y venta "
        f"parcial: {n(paso('Producción con'), 0)} USD), los «ahorros» que no son de la planta ({n(paso('Se quita el «ahorro'), 0)}"
        f" USD), el flete del guano ({n(paso('Flete del guano'), 0)} USD) y los gastos de administración que el proyecto no "
        f"tenía ({n(paso('Administración'), 0)} USD). La sensibilidad del apartado 11 lo confirma variable por variable.")
    del pz


# =============================================================================== 11. sensibilidad
def sensibilidad(d):
    d.h("11. Análisis de sensibilidad", 1)
    d.p("Se cambia una variable por vez, con las demás en su valor base, y se mide el efecto sobre el flujo de caja anual "
        "de régimen y sobre el mes de recuperación de la inversión.")
    d.h("11.1. Escenario realista", 2)
    s = E["sensibilidad"]["realista"]
    filas = [["Variable", "Valor", "Flujo anual ($ M)", "Δ ($ M)", "Payback"]]
    base = s["base"]["flujo_anual"]
    filas.append(["Base (escenario realista)", "—", mill(base, 1), "—", mes_txt(s["base"]["payback"])])
    for f in s["filas"]:
        for lado in ("bajo", "alto"):
            v = f[lado]
            filas.append([f["nombre"], f[f"txt_{lado}"], mill(v["flujo_anual"], 1), mill(v["flujo_anual"] - base, 1),
                          mes_txt(v["payback"], 0)])
    d.tabla("Sensibilidad del escenario realista (una variable por vez)", filas, anchos=[6.2, 2.4, 2.6, 2.2, 2.6],
            alin=["L", "R", "R", "R", "R"])
    d.p("Ningún cambio individual vuelve positivo el flujo del escenario realista: la planta pierde dinero en todas las "
        "variantes. Las que más lo mueven son el precio, la humedad del guano, el flete del guano, la fracción vendida y "
        "la cáscara. Trabajar más horas o más días casi no cambia el resultado (incluso lo empeora con un segundo turno), "
        "porque con el precio realista cada tonelada adicional apenas paga sus costos variables.")
    d.h("11.2. Configuración de referencia (2 turnos a 1.440 kg/h, precios del proyecto)", 2)
    d.p(f"Para medir cuánto mueve cada variable el período de recuperación hace falta un caso que recupere la inversión. "
        f"Se usa la configuración de referencia, que recupera en {mes_txt(REF['payback_meses'])}:")
    s = E["sensibilidad"]["referencia"]
    filas = [["Variable", "Valor", "Payback", "Flujo anual ($ M)"]]
    for f in s["filas"]:
        for lado in ("bajo", "alto"):
            v = f[lado]
            filas.append([f["nombre"], f[f"txt_{lado}"], mes_txt(v["payback"]), mill(v["flujo_anual"], 1)])
    d.tabla("Sensibilidad del payback de la referencia", filas, anchos=[6.6, 2.6, 3.0, 3.0], alin=["L", "R", "R", "R"])
    d.figura("f5_tornado.png", "Diagrama de tornado: meses de recuperación al cambiar cada variable (referencia)")
    sr = {f["clave"]: f for f in E["sensibilidad"]["referencia"]["filas"]}
    pb0 = E["sensibilidad"]["referencia"]["base"]["payback"]
    menores = [sr[k] for k in ("tarifa", "mant", "X_out")]
    dmax = max(max(abs(f["bajo"]["payback"] - pb0), abs(f["alto"]["payback"] - pb0)) for f in menores)
    d.p(f"Las variables críticas son la humedad del guano que entra (con 78 % la recuperación pasa de {n(pb0, 0)} a "
        f"{n(sr['X_in']['bajo']['payback'], 0)} meses, porque se obtiene menos producto por tonelada y además baja el "
        f"caudal máximo), el precio de venta (±30 % lleva el payback de {n(sr['precio']['alto']['payback'], 0)} a "
        f"{n(sr['precio']['bajo']['payback'], 0)} meses), el caudal por hora, la fracción vendida y las horas de trabajo. "
        f"El costo de la energía, el mantenimiento y la humedad final mueven el payback en menos de {n(dmax + 0.5, 0)} "
        "meses.")
    d.figura("f6_precio_payback.png", "Meses de recuperación en función del precio medio de venta para cuatro "
             "configuraciones (demás supuestos del escenario realista)")
    d.p(f"La figura anterior responde «¿a qué precio se recupera la inversión?»: con el resto de los supuestos del "
        f"escenario realista, para recuperar en 60 meses hace falta vender a unos USD "
        f"{n(alt('realista', 'Actual')['precio_60'], 0)}/t con un turno a 1.000 kg/h, USD "
        f"{n(alt('realista', 'B')['precio_60'], 0)}/t con un turno a 1.440 kg/h, USD {n(A1B_R['precio_60'], 0)}/t con dos "
        f"turnos y USD {n(alt('realista', 'A2+B')['precio_60'], 0)}/t con tres. El precio realista (USD "
        f"{n(R_['precio_t'] / D, 1)}/t) queda muy lejos de todos.")
    d.h("11.3. Inflación y variación de costos", 2)
    filas = [["Caso", "Escenario", "Flujo del año 5 ($ M)", "Payback", "VAN ($ M)"]]
    for caso, rot in (("realista", "Realista"), ("referencia", "Referencia")):
        s = E["sensibilidad"][caso]
        filas.append(["Base (sin desfase)", rot, mill(s["base"]["flujo_anio5"], 1), mes_txt(s["base"]["payback"]),
                      mill(s["base"]["van"], 0)])
        for dd in s["derivas"]:
            filas.append([dd["desc"], rot, mill(dd["flujo_anio5"], 1), mes_txt(dd["payback"]), mill(dd["van"], 0)])
    d.tabla("Efecto de que costos y precios no acompañen a la inflación", filas, anchos=[6.6, 2.2, 2.4, 2.4, 2.4],
            alin=["L", "L", "R", "R", "R"])
    sref = E["sensibilidad"]["referencia"]
    da = sref["derivas"][0]["payback"] - sref["base"]["payback"]
    db = sref["derivas"][1]["payback"] - sref["base"]["payback"]
    d.p(f"En moneda constante la inflación general no cambia los resultados. Si durante 5 años la energía sube 3 % por "
        f"año y los sueldos 1 % por año por encima de la inflación, la recuperación de la referencia se atrasa "
        f"{n(da, 1)} meses; si el precio del guano pierde 2 % por año contra la inflación (por ejemplo, porque sigue al "
        f"dólar y el tipo de cambio real baja), se atrasa {n(db, 1)} meses.")


# =============================================================================== 12. análisis inverso
def inverso(d):
    d.h("12. Análisis inverso de capacidad: recuperar la inversión en menos de 5 años", 1)
    d.h("12.1. Objetivo económico", 2)
    d.p("Se busca la capacidad mínima con la que la planta recupera el 100 % de la inversión inicial en 60 meses o menos, "
        "con flujos de caja positivos en régimen y considerando todos los costos operativos, energéticos, laborales, de "
        "mantenimiento, comercialización e impuestos, la puesta en marcha y el capital de trabajo. Para cada "
        "configuración de horas (1, 2 o 3 turnos) se busca, por bisección, el caudal de guano húmedo (kg/h) que hace que "
        "el flujo acumulado llegue a cero en el mes 60. Se hace con los precios realistas y con los del proyecto.")
    d.h("12.2. Producción necesaria", 2)
    d.p("Con el precio realista no existe una producción alcanzable que cumpla la condición: el caudal necesario sería "
        f"de {n(INV_['realista']['minimos']['2T_60']['m_in'], 0)} kg/h con dos turnos "
        f"({n(INV_['realista']['minimos']['2T_60']['lineas_necesarias'])} secadoras SC-4) o de "
        f"{n(INV_['realista']['minimos']['1T_60']['m_in'], 0)} kg/h con un turno, porque cada tonelada adicional casi no "
        "deja margen; y eso suponiendo, a favor del proyecto, que esas máquinas no costaran nada más. Con los precios del "
        "proyecto, en cambio, sí hay una solución con la máquina actual:")
    filas = [["Dato", "1 turno", "2 turnos", "3 turnos"]]
    mins = INV_["optimista"]["minimos"]
    cfgs = ("1T_60", "2T_60", "3T_60")
    filas.append(["Caudal de guano húmedo (kg/h)"] + [n(mins[c]["m_in"], 0) for c in cfgs])
    filas.append(["Horas de funcionamiento por día"] + [n(mins[c]["h_dia"], 0) for c in cfgs])
    filas.append(["Días de trabajo por mes"] + [n(mins[c]["dias_mes"], 0) for c in cfgs])
    filas.append(["Guano húmedo procesado por día (kg)"] + [n(mins[c]["humedo_dia_kg"], 0) for c in cfgs])
    filas.append(["Guano húmedo procesado por mes (t)"] + [n(mins[c]["humedo_mes_t"], 0) for c in cfgs])
    filas.append(["Guano húmedo procesado por año (t)"] + [n(mins[c]["humedo_anio_t"], 0) for c in cfgs])
    filas.append(["Producto seco obtenido por año (t)"] + [n(mins[c]["seco_anio_t"], 0) for c in cfgs])
    filas.append(["Producto seco vendido por año (t)"] + [n(mins[c]["vendido_anio_t"], 0) for c in cfgs])
    filas.append(["Producto seco vendido por mes (t)"] + [n(mins[c]["vendido_mes_t"], 1) for c in cfgs])
    filas.append(["Secadoras SC-4 necesarias (máx. 1.440 kg/h c/u)"] + [n(mins[c]["lineas_necesarias"]) for c in cfgs])
    d.tabla("Producción mínima para recuperar la inversión en 60 meses (precios del proyecto, demás supuestos del "
            "escenario optimista)", filas, anchos=[7.0, 3.0, 3.0, 3.0], alin=["L", "R", "R", "R"], resaltar=[1, 8])
    d.p(f"Con un turno harían falta {n(mins['1T_60']['m_in'], 0)} kg/h, más que la capacidad máxima de una secadora: no es "
        f"posible sin una segunda máquina. Con dos turnos alcanza con {n(mins['2T_60']['m_in'], 0)} kg/h y con tres, "
        f"{n(mins['3T_60']['m_in'], 0)} kg/h; las dos están dentro de lo que la máquina puede hacer. La de dos turnos "
        f"necesita menos guano por día ({n(mins['2T_60']['humedo_dia_kg'] / 1000, 1)} t contra "
        f"{n(mins['3T_60']['humedo_dia_kg'] / 1000, 1)} t) porque el tercer turno agrega más costo de personal que "
        "margen: es la capacidad mínima económicamente necesaria.")
    d.h("12.3. Aumento necesario de capacidad", 2)
    cap_act, cap_obj = 1000.0, mins["2T_60"]["m_in"]
    dia_act, dia_obj = 8.0, cap_obj * 16 / 1000
    d.ec("Aumento (%) = (C_obj − C_act) / C_act × 100",
         ["C_obj = capacidad objetivo", "C_act = capacidad actual (por hora o por día)"])
    d.calculo(f"Por hora: ({n(cap_obj, 0)} − 1.000) / 1.000 × 100", f"{n((cap_obj - cap_act) / cap_act * 100, 1)} %")
    d.calculo(f"Por día: ({n(dia_obj, 1)} t − 8 t) / 8 t × 100", f"{n((dia_obj - dia_act) / dia_act * 100, 0)} %")
    filas = [["Capacidad", "Actual (diseño)", "Objetivo", "Diferencia", "Aumento"],
             ["Caudal de guano húmedo (kg/h)", "1.000", n(cap_obj, 0), n(cap_obj - cap_act, 0),
              pc((cap_obj - cap_act) / cap_act * 100)],
             ["Horas por día", "8", "16", "8", "100 %"],
             ["Guano húmedo por día programado (t)", "8,0", n(dia_obj, 1), n(dia_obj - dia_act, 1),
              pc((dia_obj - dia_act) / dia_act * 100, 0)],
             ["Guano húmedo por mes (t, con disponibilidad)", n(O_["mes"]["humedo_t"], 0), n(mins["2T_60"]["humedo_mes_t"], 0),
              n(mins["2T_60"]["humedo_mes_t"] - O_["mes"]["humedo_t"], 0),
              pc((mins["2T_60"]["humedo_mes_t"] / O_["mes"]["humedo_t"] - 1) * 100, 0)],
             ["Producto vendido por año (t)", n(a2(O_, "vendido_t"), 0), n(mins["2T_60"]["vendido_anio_t"], 0),
              n(mins["2T_60"]["vendido_anio_t"] - a2(O_, "vendido_t"), 0),
              pc((mins["2T_60"]["vendido_anio_t"] / a2(O_, "vendido_t") - 1) * 100, 0)]]
    d.tabla("Capacidad actual y capacidad objetivo (precios del proyecto)", filas, anchos=[5.6, 2.6, 2.4, 2.4, 2.4],
            alin=["L", "R", "R", "R", "R"])
    d.p(f"Con dos turnos, más horas solas no alcanzan: a 1.000 kg/h se recupera la inversión en "
        f"{mes_txt(alt('optimista', 'A1')['payback'], 0)}. Hace falta, además, subir el caudal por encima de los "
        f"1.000 kg/h de diseño, cosa que la máquina permite sin modificarla: con el aire hasta 135 °C seca 1.440 kg/h "
        "(apartado 6.5). Lo único que hay que agrandar es la tolva de retención (de 0,7 a ≈ 1 m³, para mantener la "
        "hora a 70 °C con más producto) y verificar el enfriador. Con tres turnos, en cambio, alcanza con más horas: "
        f"a 1.000 kg/h recupera en {mes_txt(alt('optimista', 'A2')['payback'], 0)}, pero necesita "
        f"{n(alt('optimista', 'A2')['t_dia'], 0)} t/día de guano y vender {n(alt('optimista', 'A2')['vendido_anio'], 0)} "
        "t/año, más que la configuración de dos turnos.")
    d.figura("f7_capacidad_necesaria.png", "Caudal de guano húmedo necesario para recuperar la inversión en 2 a 5 años "
             "según las horas de trabajo (precios del proyecto)")
    d.h("12.4. Alternativas de ampliación", 2)
    notas = {
        "Actual": "Diseño del proyecto.",
        "A1": "Viable: ejes a vida infinita y rodamientos con L10 de millones de horas; se duplica el desgaste de malla, "
              "guías y refractario (mantenimiento).",
        "A2": "Viable: la marcha continua evita arranques; el mantenimiento queda para los fines de semana.",
        "B": "Viable según el modelo térmico: generador a pleno (885 kW); tolva de retención de 1 m³; sin margen si el "
             "guano viene más húmedo; validar con el módulo piloto.",
        "A1+B": "Viable con las condiciones de A1 y B.",
        "A2+B": "Viable con las condiciones de A2 y B; necesita 35 t/día de guano.",
        "C": "Es una planta nueva: secador, generador, ventiladores y lavador el doble de grandes; estimación ± 40 %.",
        "D": "Viable: segunda línea igual; ampliar la nave, la acometida (+55 kW) y el personal.",
        "D+A1": "Viable con las condiciones de A1 y D; necesita 32 t/día de guano.",
    }
    for nombre_esc, rot in (("optimista", "precios del proyecto"), ("realista", "precio realista")):
        alts = INV_[nombre_esc]["alternativas"]
        base = alts[0]
        filas = [["Alt.", "Descripción", "Inversión adicional (USD)", "Guano húmedo (t/año)", "Vendido (t/año)",
                  "Costos adicionales ($ M/año)", "Flujo adicional, año 3 ($ M/año)", "Payback", "Precio para 60 meses"]]
        for a in alts:
            filas.append([a["cod"], a["desc"], n(a["inv_extra_usd"], 0), n(a["humedo_anio"], 0), n(a["vendido_anio"], 0),
                          mill(a["costos"] - base["costos"], 1), mill(a["flujo_anual"] - base["flujo_anual"], 1),
                          mes_txt(a["payback"], 0), "—" if a["precio_60"] is None else f"USD {n(a['precio_60'], 0)}/t"])
        d.tabla(f"Alternativas de ampliación con {rot}", filas,
                anchos=[1.1, 4.4, 1.9, 1.7, 1.6, 1.7, 1.7, 1.7, 1.8], alin=["C", "L", "R", "R", "R", "R", "R", "R", "R"],
                resaltar=[5])
    filas = [["Alt.", "Viabilidad técnica"]] + [[k, v] for k, v in notas.items()]
    d.tabla("Viabilidad técnica de cada alternativa", filas, anchos=[1.4, 14.6], alin=["C", "L"])
    d.p("Alternativa A (más horas): la máquina puede trabajar 16 o 24 h por día sin comprometer su vida útil, porque los "
        "ejes se verificaron a vida infinita y los rodamientos giran tan despacio que su vida es prácticamente "
        "ilimitada; lo que se gasta más rápido son la malla, las guías, los faldones y el refractario, y eso está en el "
        "costo de mantenimiento, que crece con las horas. Alternativa B (optimizar el proceso): subir la temperatura del "
        "aire hasta 135 °C aprovecha el intercambiador y los ventiladores que ya existen; no hace falta cambiar la "
        "circulación de aire ni la alimentación (la cinta llega con el variador al 56 %), sólo la tolva de retención. "
        "Alternativa C (máquina más grande): exige rediseñar el secador, el generador, los ventiladores y el lavador; "
        f"cuesta unos USD 200.000 (regla de los seis décimos) y, con un turno, recupera algo antes que la B "
        f"({mes_txt(alt('optimista', 'C')['payback'], 0)} contra {mes_txt(alt('optimista', 'B')['payback'], 0)}), "
        "pero cuesta cien veces más; con dos turnos la B ya cumple el objetivo sin rediseñar. Alternativa D (segunda "
        "secadora): "
        "duplica la producción con USD 353.000 más; con un turno recupera peor que la B, y con dos turnos recupera en "
        f"{mes_txt(alt('optimista', 'D+A1')['payback'], 0)}, pero necesita el doble de guano y de mercado.")
    d.h("12.5. Objetivos de recuperación de 2 a 5 años", 2)
    filas = [["Objetivo", "Plazo", "Configuración mínima", "Caudal (kg/h)", "Guano húmedo (t/año)",
              "Producto seco obtenido (t/año)", "Producto vendido (t/año)"]]
    objetivos = (("Recuperación rápida", 24), ("Recuperación intermedia", 36), ("Recuperación conservadora", 48),
                 ("Recuperación límite", 60))
    no_alcanza = []
    for rot, N in objetivos:
        mejor = None
        for cfg in ("1T", "2T", "3T"):
            dd = mins.get(f"{cfg}_{N}")
            if dd and dd["lineas_necesarias"] == 1 and (mejor is None or dd["humedo_anio_t"] < mejor[1]["humedo_anio_t"]):
                mejor = (cfg, dd)
        if mejor is None:
            no_alcanza.append(N)
            filas.append([rot, f"{N // 12} años", "no alcanzable con una secadora", "—", "—", "—", "—"])
            continue
        cfg, dd = mejor
        txt = {"1T": "1 turno", "2T": "2 turnos", "3T": "3 turnos"}[cfg] + ", 1 secadora"
        filas.append([rot, f"{N // 12} años", txt, n(dd["m_in"], 0), n(dd["humedo_anio_t"], 0), n(dd["seco_anio_t"], 0),
                      n(dd["vendido_anio_t"], 0)])
    d.tabla("Producción necesaria para cada objetivo de recuperación (precios del proyecto)", filas,
            anchos=[3.2, 1.4, 3.0, 1.8, 2.2, 2.3, 2.1], alin=["L", "C", "L", "R", "R", "R", "R"], resaltar=[4])
    d.p(f"Para recuperar en 2 años, aun con tres turnos, haría falta {n(mins['3T_24']['m_in'], 0)} kg/h, por encima del "
        f"máximo de 1.440 kg/h de una secadora; con dos secadoras en dos turnos (alternativa D+A1) la recuperación es de "
        f"{mes_txt(alt('optimista', 'D+A1')['payback'], 0)}, así que el objetivo de 2 años no se alcanza con ninguna de las "
        f"alternativas estudiadas. En 3 años alcanza con tres turnos a {n(mins['3T_36']['m_in'], 0)} kg/h y en 4 años con "
        f"dos turnos a {n(mins['2T_48']['m_in'], 0)} kg/h, casi al máximo. Con el precio realista ninguno de los cuatro "
        "objetivos es alcanzable.")
    d.h("12.6. Restricciones de producción y comercialización", 2)
    hen = 8000 / 60000                                          # kg de guano por gallina y día (informe)
    m2 = mins["2T_60"]
    gall_dia = m2["humedo_dia_kg"] / hen
    gall_anio = m2["humedo_anio_t"] * 1000 / (hen * 365)
    d.lista([
        f"Materia prima: {n(m2['humedo_dia_kg'] / 1000, 1)} t/día de guano en los días de trabajo equivalen a "
        f"{n(gall_dia / 1000, 0)} mil gallinas; si el guano de los fines de semana se acopia y se procesa en la semana, "
        f"alcanza con {n(gall_anio / 1000, 0)} mil (a 133 g por gallina y día, el dato del proyecto: 8 t/día para 60.000 "
        "aves). Son dos granjas como la del proyecto. En Entre Ríos hay 201 granjas de ponedoras (22 % del país, Anuario "
        "Avícola 2025); la materia prima existe, pero hay que asegurarla con contratos.",
        "Humedad y variabilidad: con guano al 78 % el caudal máximo baja a 1.303 kg/h y la recuperación de la referencia "
        "se atrasa a 96 meses (apartado 11.2). Hay que pedir a las granjas guano de cinta de secado, más seco.",
        "Almacenamiento: el acopio de producto a granel del proyecto es de unos 22 m³ (≈ 11 t, un día y medio de "
        "producción a dos turnos) y el depósito de 240 m² guarda del orden de 200 t embolsadas (estimación: 1 t por "
        "pallet en dos alturas sobre la mitad de la superficie), algo más de un mes de ventas. Como la demanda de "
        "abonos es estacional, hará falta vender a granel en temporada o ampliar el depósito.",
        f"Personal: con los supuestos del escenario optimista, 4 operarios (2 por turno, como dice el informe) más "
        f"administración. Con 3 por turno, como el presupuesto, la recuperación de la referencia pasa de "
        f"{mes_txt(REF['payback_meses'])} a {mes_txt(VAR['tres_operarios']['payback'])}. Hay personal disponible en "
        "Crespo.",
        "Energía eléctrica: con una sola línea la demanda no cambia al agregar turnos (85 kW contratados alcanzan); sí "
        "aumenta la energía consumida. La alternativa D necesita unos 55 kW más y revisar la acometida.",
        "Capacidad térmica: a 1.440 kg/h el generador de 880 kW trabaja a pleno (885 kW): no queda margen; por eso el "
        "objetivo mínimo (1.224 kg/h) es mejor que operar siempre en el máximo.",
        f"Mercado: {n(m2['vendido_anio_t'], 0)} t/año de producto equivalen, a la dosis de 3 t/ha que usan los "
        f"horticultores (La Nación, 2024), a unas {n(m2['vendido_anio_t'] / 3, 0)} ha por año. No se encontró un estudio "
        "de la demanda regional: no se puede dar por viable la ampliación hasta tener compradores para ese volumen.",
        "Paradas por mantenimiento: con dos turnos el mantenimiento preventivo se hace en el tercer turno y los fines de "
        "semana; la disponibilidad del 95 % del escenario optimista es exigente y debe medirse en el módulo piloto.",
    ])
    d.h("12.7. Resultado final", 2)
    filas = [["Concepto", "Capacidad actual", "Capacidad objetivo", "Incremento", "Recuperación"],
             ["Precios y demás supuestos del escenario optimista (USD 272,5/t)", "1.000 kg/h × 8 h = 8 t/día",
              f"{n(m2['m_in'], 0)} kg/h × 16 h = {n(m2['m_in'] * 16 / 1000, 1)} t/día",
              f"+{n((m2['m_in'] / 1000 - 1) * 100, 1)} % por hora; +{n((m2['m_in'] * 16 / 8000 - 1) * 100, 0)} % por día",
              f"60 meses (actual: {mes_txt(O_['payback_meses'], 0)})"],
             ["Precios del proyecto, a capacidad máxima", "1.000 kg/h × 8 h", "1.440 kg/h × 16 h = 23 t/día",
              "+44 % por hora; +188 % por día", mes_txt(A1B_O["payback"], 1)],
             [f"Precio realista (USD {n(R_['precio_t'] / D, 1)}/t)", "1.000 kg/h × 8 h",
              f"no alcanzable ({n(INV_['realista']['minimos']['2T_60']['m_in'], 0)} kg/h con 2 turnos)",
              "—", f"necesita USD {n(A1B_R['precio_60'], 0)}/t con 2 turnos a 1.440 kg/h"]]
    d.tabla("Resultado del análisis inverso", filas, anchos=[3.6, 2.8, 3.6, 3.4, 3.0], alin=["L", "L", "L", "L", "L"],
            resaltar=[1])
    inv_amp = 32000.0
    d.lista([
        f"1. Guano húmedo por mes: {n(m2['humedo_mes_t'], 0)} t (con los precios del proyecto, en 2 turnos y "
        f"{n(m2['dias_mes'], 0)} días por mes). Con el precio realista no hay cantidad que alcance.",
        f"2. Producto seco: producir {n(m2['seco_anio_t'], 0)} t/año ({n(m2['seco_mes_t'], 0)} t/mes) y vender "
        f"{n(m2['vendido_anio_t'], 0)} t/año ({n(m2['vendido_mes_t'], 0)} t/mes).",
        f"3. Caudal: {n(m2['m_in'], 0)} kg/h de guano húmedo durante 16 h por día.",
        f"4. Aumento: {n(m2['m_in'] - 1000, 0)} kg/h más por hora y 8 h más por día: de 8 t a "
        f"{n(m2['m_in'] * 16 / 1000, 1)} t de guano por día.",
        f"5. Porcentaje: +{n((m2['m_in'] / 1000 - 1) * 100, 1)} % de caudal y +{n((m2['m_in'] * 16 / 8000 - 1) * 100, 0)} % "
        "de producción diaria.",
        "6. Con dos turnos no alcanza sólo con más horas: hay que subir además el caudal con el aire hasta 135 °C, que "
        f"la máquina actual permite. Con tres turnos alcanza con más horas solas "
        f"({mes_txt(alt('optimista', 'A2')['payback'], 0)} a 1.000 kg/h), a costa de más guano y más mercado. En ningún "
        "caso hace falta una máquina más grande.",
        f"7. Costo de la ampliación: USD {n(inv_amp, 0)} ($ {mill(inv_amp * D, 1)} millones): USD 30.000 del segundo turno "
        "(estimación del proyecto) y USD 2.000 de la tolva de retención mayor, más el capital de trabajo adicional.",
        f"8. Para el objetivo de 60 meses, la alternativa más conveniente es la A1+B (dos turnos con el aire hasta "
        f"135 °C): es la que menos guano y menos mercado necesita ({n(MIN60['humedo_dia_kg'] / 1000, 1)} t/día a "
        f"{n(MIN60['m_in'], 0)} kg/h), cuesta USD 32.000 y a 1.440 kg/h recupera en {mes_txt(A1B_O['payback'], 0)}. La "
        f"que recupera más rápido es la A2+B (tres turnos a 1.440 kg/h: {mes_txt(alt('optimista', 'A2+B')['payback'], 0)}), "
        f"pero necesita {n(alt('optimista', 'A2+B')['t_dia'], 1)} t/día de guano y vender "
        f"{n(alt('optimista', 'A2+B')['vendido_anio'], 0)} t/año. La A1+B recupera en 5 años con un precio medio desde "
        f"unos USD {n(A1B_O['precio_60'], 0)}/t con los costos del escenario optimista, o USD {n(A1B_R['precio_60'], 0)}/t "
        "con los del realista; con precios algo menores su VAN sigue siendo positivo, pero tarda más de 5 años.",
    ])


# =============================================================================== 13. viabilidad
def viabilidad(d):
    d.h("13. Evaluación de viabilidad", 1)
    rp = REF["payback_meses"]
    resp = [
        ("¿Es rentable construir y operar esta secadora?",
         f"Con la información que se puede verificar hoy, no. Con un turno no recupera la inversión en 15 años en ningún "
         f"escenario (VAN entre {pm(O_['van'], 0)} y {pm(C_['van'], 0)}). Recupera la inversión en 5 años sólo "
         "trabajando más de un turno (dos turnos con el caudal subido, o tres turnos), con todos los supuestos del "
         f"escenario optimista y precios del orden de los del proyecto (al menos USD {n(A1B_O['precio_60'], 0)}/t con dos "
         "turnos a 1.440 kg/h), que todavía no están respaldados por compradores."),
        ("¿Cuánto dinero se necesita invertir en total?",
         f"{pm(R_['inv_con_ct'])} en el escenario realista ({us(R_['inv_total'] / D)} de inversión fija más el capital "
         f"de trabajo); entre {pm(O_['inv_total'], 0)} y {pm(C_['inv_total'], 0)} según el escenario."),
        ("¿Cuánto dinero genera mensualmente?",
         f"Factura {pm(a2(R_, 'ventas') / 12, 1)} por mes en el escenario realista y {pm(a2(O_, 'ventas') / 12, 1)} en el "
         f"optimista. El flujo de caja es de {pm(a2(R_, 'flujo') / 12, 1)} por mes (realista) y "
         f"{pm(a3(O_, 'flujo') / 12, 1)} (optimista); con dos turnos a 1.440 kg/h y precios del proyecto, "
         f"{pm(REF['anio3']['flujo'] / 12, 1)} por mes de régimen."),
        ("¿Cuánto cuesta producir un kilogramo de guano seco?",
         f"$ {n(R_['costo_prod_kg'], 0)} de costo de producción por kg obtenido y $ {n(R_['costo_total_kg'], 0)} de costo "
         f"operativo total por kg vendido (≈ USD {n(R_['costo_total_kg'] * 1000 / D, 0)}/t); $ "
         f"{n(R_['costo_total_kg_amort'], 0)} con amortizaciones (escenario realista). Con dos turnos a 1.440 kg/h el "
         f"costo operativo baja a $ {n(REF['costo_total_kg'], 0)} por kg."),
        ("¿Cuál es el beneficio económico mensual?",
         f"Negativo con un turno: {pm(a2(R_, 'beneficio_neto') / 12, 1)} por mes en el realista y "
         f"{pm(a2(O_, 'beneficio_neto') / 12, 2)} en el optimista. Con la referencia de dos turnos, "
         f"{pm(REF['anio2']['beneficio_neto'] / 12, 1)} por mes después de impuestos."),
        ("¿En cuánto tiempo se recupera la inversión?",
         f"Con un turno, nunca dentro de los 15 años. Con dos turnos a 1.440 kg/h y precios del proyecto, en el "
         f"{anio_mes(rp)} ({mes_txt(rp)}); con dos turnos a {n(MIN60['m_in'], 0)} kg/h, en 60 meses. Las dos cifras "
         "suponen todos los supuestos del escenario optimista."),
        ("¿Qué producción mínima necesitamos para que el proyecto sea rentable?",
         f"Para cubrir los costos de caja con los precios del proyecto, {n(O_['pe_operativo_t'], 0)} t/año vendidas; para "
         f"recuperar la inversión en 5 años, {n(MIN60['vendido_anio_t'], 0)} t/año vendidas, procesando "
         f"{n(MIN60['humedo_mes_t'], 0)} t/mes de guano húmedo. Con el precio realista no hay producción alcanzable que "
         "la haga rentable."),
        ("¿Qué factores pueden hacer que el proyecto deje de ser rentable?",
         "Un precio de venta menor que el supuesto, vender menos de lo producido, guano más húmedo (78 %), menos horas o "
         "días de trabajo, tener que pagar el flete del guano y una cáscara más cara. La energía y el mantenimiento "
         "pesan mucho menos."),
        ("¿Qué modificaciones técnicas permitirían mejorar su rentabilidad?",
         "Operar con el aire hasta 135 °C para llegar a 1.440 kg/h (tolva de retención de 1 m³); trabajar en dos turnos; "
         "recibir guano más seco (cintas de secado en los galpones), que da más producto por tonelada y menos cáscara; "
         "instalar la planta en la granja o cerca, para no pagar flete de guano; reducir el consumo eléctrico de los "
         f"ventiladores (el plan pide menos de 170 kWh/t y la estimación da {n(R_['mes']['kwh'] / R_['mes']['seco_t'], 0)}); "
         "y producir un producto de mayor "
         "valor (peletizado o envasado) si hay mercado."),
        ("¿Qué tan conveniente sería ampliar la capacidad productiva?",
         "Conviene ampliar las horas y el caudal de la máquina existente (alternativa A1+B): cuesta USD 32.000 y es la "
         "forma de recuperar en menos de 5 años con menos guano y menos mercado (tres turnos también recuperan, con más "
         "guano). No conviene una máquina más grande ni una segunda secadora "
         "mientras no haya materia prima (≈ 100.000 a 140.000 gallinas) y compradores para 1.600 t/año o más."),
    ]
    for i, (q, a) in enumerate(resp, 1):
        d.p(f"{i}. {q}", negrita=True)
        d.p(a)
    d.recuadro("Conclusión", "La secadora es técnicamente sólida y le resuelve a las granjas un problema ambiental real, "
               "pero como negocio independiente, con un turno, no se paga. Es viable sólo si se dan juntas tres "
               f"condiciones: trabajar más de un turno con el caudal subido (dos turnos a {n(MIN60['m_in'], 0)} kg/h o "
               f"más, unas {n(MIN60['humedo_dia_kg'] / 1000, 0)} t/día de guano), conseguir ese guano sin pagar su flete y "
               f"vender a precios como los del proyecto (USD {n(DAT['PRECIO_PROY'], 1)}/t; a la capacidad máxima de "
               f"1.440 kg/h alcanza con unos USD {n(A1B_O['precio_60'], 0)}/t). La primera depende del proyecto; las "
               "otras dos hay que demostrarlas con contratos antes de invertir.")


# =============================================================================== 14. recomendaciones
def recomendaciones(d):
    d.h("14. Recomendaciones para mejorar la rentabilidad", 1)
    d.lista([
        "1. Conseguir antes de invertir los tres datos críticos: cotizaciones o cartas de intención de compradores con "
        "precio y volumen, la tarifa real de la LAR y la cáscara puesta en planta.",
        "2. Construir y probar el módulo piloto de la Rev. F: medir la capacidad real, el consumo de cáscara y de "
        "electricidad, la higienización y el análisis químico del producto, y usar sus muestras para abrir el mercado.",
        "3. Diseñar la operación para dos turnos desde el inicio y trabajar con el aire hasta 135 °C (1.224 a 1.440 kg/h), "
        "con la tolva de retención de 1 m³.",
        "4. Asociarse con las granjas: que entreguen el guano en la planta (se ahorran su gestión) o instalar la planta en "
        "la granja más grande; pedir guano de cinta de secado, con menos humedad.",
        "5. Invertir por etapas: sin biogás; si el canal principal resulta ser el granel, postergar la ensacadora, la "
        "envasadora de bolsas chicas y el depósito (≈ USD 113.000 con imprevistos).",
        "6. Buscar un canal de mayor valor para una parte de la producción (horticultura, viveros, bolsas) con registro en "
        "el SENASA y marca propia, sin suponer que se vende todo.",
        "7. Revisar con un contador el IVA de la inversión (devolución anticipada), los beneficios del Parque Industrial y "
        "las líneas de crédito para pymes, que pueden mejorar el flujo de los primeros años.",
        "8. Medir desde el arranque los indicadores del plan (disponibilidad, kg de cáscara por t de agua y kWh por t) y "
        "corregir el indicador de cáscara del plan (470 kg/t es el valor del método de diseño; el modelo térmico da "
        f"{n(DAT['Q_CASCARA'] * 1000, 0)} kg/t).",
    ])


# =============================================================================== fuentes y anexos
def fuentes(d):
    d.h("15. Fuentes", 1)
    d.lista([f"[{k}] {v}" for k, v in E["fuentes"].items()])


def anexos(d):
    d.h("Anexo A. Supuestos del modelo", 1)
    filas = [["Supuesto", "Unidad", "Tipo", "Conservador", "Realista", "Optimista"]]
    for clave, desc, unidad, tipo, c, r, o in _tabla:
        if clave == "mix":
            filas.append([desc, "—", tipo] + ["; ".join(f"{k} {n(f * 100)} % a {n(p, 1)}" for k, (f, p) in v.items())
                                              for v in (c, r, o)])
            continue
        fmt = (lambda v: pc(v * 100, 1)) if unidad == "%" else (lambda v: n(v, 2) if isinstance(v, float) and v < 100
                                                                 else n(v, 0))
        filas.append([desc, unidad, tipo] + [fmt(v) for v in (c, r, o)])
    d.tabla("Supuestos de los tres escenarios (la planilla los lista con su fuente)", filas,
            anchos=[5.6, 1.4, 1.2, 2.6, 2.6, 2.6], alin=["L", "C", "C", "R", "R", "R"])
    d.h("Anexo B. Flujo de caja anual", 1)
    for _nombre, e, rot in (("realista", R_, "escenario realista"), ("referencia", REF,
                                                                      "referencia: 2 turnos a 1.440 kg/h, precios del proyecto")):
        filas = [["Año", "Ventas", "Costos", "EBITDA", "Amortiz.", "Ganancias pagado", "Δ capital de trabajo",
                  "Flujo de caja", "Acumulado"]]
        fm = e["flujo_mensual"]
        acum = fm[0]["flujo"]
        filas.append(["0", "", "", "", "", "", "", mill(fm[0]["flujo"], 1), mill(acum, 1)])
        for y in range(1, 16):
            sel = fm[1 + 12 * (y - 1): 1 + 12 * y]

            def sm(k, sel=sel):
                return sum((f.get(k) or 0.0) for f in sel)
            flujo_op = sm("flujo") - sm("residual")
            acum += flujo_op
            filas.append([str(y), mill(sm("ventas"), 1), mill(sm("costo_total"), 1), mill(sm("ebitda"), 1),
                          mill(sm("amortizacion"), 1), mill(sm("ganancias_pagado"), 1), mill(sm("d_ct"), 1),
                          mill(flujo_op, 1), mill(acum, 1)])
        d.tabla(f"Flujo de caja anual, {rot} ($ millones; sin el valor residual del mes 180)", filas,
                anchos=[1.0, 1.9, 1.9, 1.9, 1.7, 1.9, 1.9, 1.9, 1.9], alin=["C"] + ["R"] * 8)
    d.h("Anexo C. Archivos y cómo regenerarlos", 1)
    d.lista([
        "analisis_economico/Analisis_economico_Secadora_Guano.docx y .pdf: este informe.",
        "analisis_economico/Modelo_economico_Secadora_Guano.xlsx: planilla con fórmulas (supuestos, inversión, mes tipo, "
        "flujo mensual de 180 meses, impuestos, flujo anual, indicadores con control contra Python, escenarios, "
        "sensibilidad e inverso).",
        "analisis_economico/figuras/: los ocho gráficos.",
        "fuente/economia/modelo_economico.py (modelo), figuras_economia.py, planilla_economica.py e informe_economico.py. "
        "Se regeneran con «python regenerar.py economia» desde fuente/.",
    ])


# =============================================================================== README de la sección (GitHub)
def readme():
    """analisis_economico/README.md: la portada de la sección en GitHub, con los números del modelo."""
    m2 = MIN60
    filas = ["| | Conservador | Realista | Optimista |", "|---|---:|---:|---:|"]
    def fila(rot, f):
        filas.append(f"| {rot} | " + " | ".join(f(ESC[e]) for e in ESCS) + " |")
    fila("Inversión inicial total", lambda e: f"$ {mill(e['inv_total'], 0)} M (USD {n(e['inv_total'] / D)})")
    fila("Guano húmedo procesado", lambda e: f"{n(a2(e, 'humedo_t'))} t/año")
    fila("Producto seco vendido", lambda e: f"{n(a2(e, 'vendido_t'))} t/año")
    fila("Precio medio ex planta", lambda e: f"USD {n(e['precio_t'] / D, 1)}/t")
    fila("Ventas", lambda e: f"$ {mill(a2(e, 'ventas') / 12, 1)} M/mes")
    fila("Costos operativos", lambda e: f"$ {mill(a2(e, 'costo_total') / 12, 1)} M/mes")
    fila("Flujo de caja neto de régimen", lambda e: f"$ {mill(a3(e, 'flujo'), 0)} M/año")
    fila("Recuperación de la inversión", lambda e: mes_txt(e["payback_meses"]))
    fila("ROI anual (año 2)", lambda e: pc(e["roi_anual"]))
    texto = f"""# Análisis de rentabilidad y recuperación de la inversión

Anexo económico del proyecto final: **¿cuánto dinero genera realmente la secadora de guano y en cuánto tiempo se
recupera la inversión?** Pesos constantes de {E['fecha']}, sin IVA, dólar BNA $ {n(D)}. Planta de secado sin biogás,
la primera etapa que recomienda el proyecto.

| Archivo | Contenido |
|---|---|
| [Analisis_economico_Secadora_Guano.pdf](Analisis_economico_Secadora_Guano.pdf) | Informe completo: inversión, capacidad, costos, ingresos, payback, ROI, punto de equilibrio, escenarios, sensibilidad, análisis inverso de capacidad y conclusión |
| [Analisis_economico_Secadora_Guano.docx](Analisis_economico_Secadora_Guano.docx) | El mismo informe en Word |
| [Modelo_economico_Secadora_Guano.xlsx](Modelo_economico_Secadora_Guano.xlsx) | Planilla con fórmulas: se elige el escenario y se cambian los datos en azul; recalcula el flujo de 180 meses, los impuestos y los indicadores |
| [figuras/](figuras/) | Los ocho gráficos del informe |

## Resultados con la secadora tal como fue diseñada (1 turno, 1.000 kg/h)

{chr(10).join(filas)}

**Con un turno la planta no recupera la inversión en ningún escenario.** El costo operativo de un kilogramo vendido es
de $ {n(R_['costo_total_kg'], 0)} (realista), más que el precio que se puede respaldar hoy: el único precio de granel
encontrado es de USD 30/t para guano semiseco (2024) y el valor de los nutrientes del producto es de
USD {n(DAT['VALOR_NPK'], 1)}/t; el proyecto supuso USD {n(DAT['PRECIO_PROY'], 1)}/t sin cotizaciones.

## Capacidad mínima para recuperar la inversión en 5 años

Con los precios y demás supuestos del escenario optimista alcanza con **2 turnos a {n(m2['m_in'], 0)} kg/h**
({n(m2['humedo_mes_t'], 0)} t/mes de guano húmedo y {n(m2['vendido_anio_t'], 0)} t/año de producto vendido), con la misma
máquina: con el aire hasta 135 °C seca hasta 1.440 kg/h. Cuesta USD 32.000 (segundo turno y tolva de retención mayor). A
1.440 kg/h recupera en {mes_txt(A1B_O['payback'])}. Tres turnos también alcanzan ({n(MIN60_3T['m_in'], 0)} kg/h), con más
guano por día. Con los precios del proyecto pero los demás supuestos del escenario realista, dos turnos a 1.440 kg/h tardan
{mes_txt(VAR['supuestos_realistas_precio_proyecto']['payback'], 0)}; con el precio realista haría falta vender a unos
USD {n(A1B_R['precio_60'], 0)}/t.

![Curva de recuperación de la inversión](figuras/f3_recuperacion_referencia.png)

![Payback según el precio de venta](figuras/f6_precio_payback.png)

## Datos pendientes antes de invertir

1. Precio mayorista y volumen que compra el mercado (cartas de intención de compradores).
2. Tarifa real de la Cooperativa La Agrícola Regional.
3. Cáscara de arroz puesta en planta y quién paga el flete del guano.

## Cómo se regenera

`python fuente/regenerar.py economia` rehace el modelo (`fuente/economia/modelo_economico.py`), los gráficos, la planilla
y el informe. La planilla repite el modelo con fórmulas de Excel; su hoja «Indicadores» compara los resultados con los
de Python (diferencia cero en los tres escenarios).
"""
    with open(os.path.join(os.path.dirname(SALIDA), "README.md"), "w", encoding="utf-8") as f:
        f.write(texto)


# =============================================================================== principal
def main():
    d = Doc()
    portada(d)
    encabezado_pie(d.m)
    resumen(d)
    metodo(d)
    revision(d)
    tecnica(d)
    inversion(d)
    capacidad(d)
    costos(d)
    ingresos(d)
    rentabilidad(d)
    escenarios_cap(d)
    sensibilidad(d)
    inverso(d)
    viabilidad(d)
    recomendaciones(d)
    fuentes(d)
    anexos(d)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    d.m.d.save(SALIDA)
    with open(os.path.join(os.path.dirname(SALIDA), "_informe.md"), "w", encoding="utf-8") as f:
        f.write("\n\n".join(d.md) + "\n")
    readme()
    print("guardado", SALIDA, "| tablas", d.m.n_tabla, "| ecuaciones", d.m.n_ec, "| figuras", d.m.n_fig)
    MD.pdf_desde_html(d.m, SALIDA, "Secadora de guano 8 t/día – Análisis económico y recuperación de la inversión",
                      "Análisis económico – Secadora de guano")


if __name__ == "__main__":
    main()
