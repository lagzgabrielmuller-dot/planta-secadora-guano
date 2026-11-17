"""Análisis de rentabilidad y recuperación de la inversión de la secadora de guano (Rev. F, noviembre de 2026).

Toma los datos del proyecto tal como están en los cálculos de la entrega (presupuesto.json, resultados.json y el
informe), les suma los precios de mercado relevados con fuente y fecha y las hipótesis que hacen falta donde no hay
dato, y calcula mes a mes el flujo de caja de cada escenario: producción, ventas, costos, amortizaciones, impuestos,
capital de trabajo, recuperación de la inversión, ROI, VAN, TIR y punto de equilibrio. También hace el análisis de
sensibilidad y el análisis inverso de capacidad (qué producción hace falta para recuperar la inversión en 2 a 5 años).

Moneda: pesos constantes de noviembre de 2026, sin IVA. Los montos en dólares del proyecto se pasan a pesos con el
dólar BNA vendedor del 16/11/2026 ($ 1.575/USD). Como todo está en moneda constante, la tasa de descuento es real y la
inflación general no cambia los resultados; lo que sí los cambia es que un costo suba más (o menos) que el precio de
venta, y eso se estudia en la sensibilidad (desfase de costos).

Tipo de cada dato (columna «tipo» de la tabla de supuestos):
  R  dato del proyecto (cálculos, planos o presupuesto de la entrega; son valores de diseño, no medidos)
  V  dato verificado de mercado o normativo, con fuente y fecha
  E  estimación propia hecha con datos R o V (se explica el cálculo)
  H  hipótesis de trabajo: no hay dato publicado; se adopta un valor razonable y se estudia su efecto

    python modelo_economico.py          # -> economia.json (lo leen la planilla, las figuras y el informe)
"""
from __future__ import annotations

import copy
import json
import math
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
CALC = os.path.join(AQUI, "..", "calculos")
PRES = json.load(open(os.path.join(CALC, "presupuesto.json"), encoding="utf-8"))
RES = json.load(open(os.path.join(CALC, "resultados.json"), encoding="utf-8"))

FECHA_REF = "noviembre de 2026"
DOLAR = 1575.0                 # V  $/USD, BNA vendedor 16/11/2026
MESES = 180                    # R  horizonte de 15 años (evaluación del proyecto)
TASA_REAL = 0.10               # R  tasa de descuento anual (evaluación del proyecto), real por ser moneda constante
DIAS_MES = 365 / 12

# =============================================================================== fuentes
FUENTES = {
    "PROY": "Proyecto, entrega Rev. F (11/11/2026): fuente/calculos/presupuesto.py y presupuesto.json, "
            "resultados.json, informe final (apartados 1, 6, 6.7, 15 y 26). Son valores de diseño, no medidos.",
    "BNA": "Dólar BNA vendedor $ 1.575 del 16/11/2026, sin cambios a la apertura del 17/11 (DolarHoy, Noticias "
           "Argentinas, sitio del BNA).",
    "IPC": "INDEC, IPC de octubre de 2026 (publicado el 12/11/2026): 2,2 % mensual, 33,1 % interanual; regulados "
           "2,9 % y «vivienda, agua, electricidad y gas» 4,2 % en el mes.",
    "GUANO_GRANEL": "La Nación (18/10/2024) y Bichos de Campo (22/10/2024): guano seco de 40 a 50 % de materia seca "
                    "a unos USD 30/t puesto en el campo de destino (granjas de Bahía Blanca); en Salta, USD 20/m³. "
                    "Antigüedad: 25 meses. No se encontró un precio de granel de 2026 para Entre Ríos.",
    "GUANO_BOLSA": "Mercado Libre / Caravanas, «Fertilizante guano gallinaza × 25 kg» (compost base guano de gallina, "
                   "polvo): $ 75.000 por bolsa al público, con IVA; «Fertilizante orgánico guano gallina × 1 kg»: "
                   "$ 18.500 (Caravanas, Mercado Libre). Relevado 11/2026, publicaciones sin fecha. Son precios "
                   "minoristas, no de planta.",
    "FERT": "Bichos de Campo, informe de fertilizantes del 7/11/2026: urea USD 595 a 605/t y MAP USD 965 a 995/t en el "
            "mercado mayorista argentino. Cloruro de potasio: USD 383/t, promedio mundial 2026 del Banco Mundial "
            "(que.es, 8/11/2026); no se encontró precio local.",
    "NPK": "Informe del proyecto, apartado 2: el guano tiene en base seca ≈ 3 % de N, 2,8 % de P₂O₅ y 2,2 % de K₂O.",
    "BOLSAS": "Mercado Libre, bolsas de rafia laminada 40 × 75 para 20-25 kg: pack de 100 a $ 74.289 (≈ $ 743 c/u), "
              "relevado 11/2026. El proyecto usa USD 0,45 por bolsa: coincide.",
    "UOM": "UOM rama 17, noviembre de 2026: operario calificado $ 5.054,03/h (iProfesional, El Cronista); mensual de "
           "referencia = 200 h (Mundo Gremial) = $ 1.010.806. Es el convenio de referencia; el que corresponda a la "
           "planta (químicos, rural u otro) se debe confirmar.",
    "FLETE": "Tarifas de referencia del transporte de granos: CATAC enero de 2026 ($ 8.453/t a 1 km, $ 16.119/t a "
             "51 km, $ 23.965/t a 101 km) y FETRA 13/11/2026 ($ 32.783/t a 100 km; $ 68.963/t a 300 km).",
    "GAN": "Impuesto a las ganancias de sociedades, escala del art. 73 (Ley 27.630) para ejercicios iniciados desde el "
           "1/1/2026, publicada por ARCA (Tributum, Contablix): 25 % hasta $ 133.514.185,74; 30 % hasta "
           "$ 1.335.141.857,38; 35 % por encima. Los tramos se actualizan por IPC.",
    "IIBB": "Ingresos brutos de Entre Ríos, industria: 1,25 % a 1,5 % según fuentes secundarias (Hacecuentas, "
            "Yo-Facturo, 11/2026). La alícuota del código de fabricación de abonos se debe confirmar con ATER.",
    "LEY25413": "Impuesto sobre los débitos y créditos bancarios, Ley 25.413: 0,6 % sobre los créditos y 0,6 % sobre "
                "los débitos.",
    "PALA": "Avisos de Agrofy y Mercado Libre (11/2026), cargadoras frontales usadas de ≈ 1 m³: Liugong 836 (2018) "
            "USD 32.000; SDLG L936 (2020) USD 37.400; Ctx926a USD 44.000.",
    "TIERRA": "Avisos de 11/2026: campo agrícola en Entre Ríos USD 6.700 a 6.900/ha (Gualeguaychú, La Paz); quinta de "
              "3 ha en Paraná USD 80.000 (≈ USD 2,7/m²); lotes urbanos en Crespo USD 73 a 124/m². No hay precio "
              "publicado de lotes del Parque Industrial de Crespo.",
    "GRANJAS": "Anuario Avícola 2025 (SAGyP, datos SIGSA-SENASA): 201 granjas de ponedoras en Entre Ríos, 22,2 % del "
               "país. No informa el número de aves por provincia.",
    "EPRE": "EPRE Entre Ríos, Res. 166/26 (6/10/2026) para los consumos de noviembre: el componente de distribución "
            "sube como mucho 2,8 %; los valores de la tarifa de grandes demandas no se publicaron en la prensa.",
}

# =============================================================================== 1. datos del proyecto (R)
INV = PRES["inversion"]
FILAS = {f[0]: f for f in INV["filas"]}                 # (cód, rubro, descripción, cant, unid, USD unit, USD total, ...)
SIN_BIOGAS = [c for c in FILAS if c not in ("B7", "B8")]
IMPREV = 0.07                                            # R  imprevistos del presupuesto
# clases para amortizar y para el mantenimiento (el vado B1 es mitad obra y mitad equipos)
OBRA = {"A9": 1.0, "B6": 1.0, "B9": 1.0, "B1": 0.5}
INTANGIBLE = {"C1": 1.0}

M_IN = 1000.0          # R  kg/h de guano húmedo (8 t en un turno de 8 h)
X_IN = 0.72            # R  humedad de entrada (base húmeda)
X_OUT = 0.15           # R  humedad del producto
H_TURNO = 8.0          # R  h de alimentación por turno
DIAS_ANIO = 250        # R  días de operación por año
M_IN_MAX = 1440.0      # R  capacidad del secador con aire a 135 °C (modelo térmico, apartado 6.7)
W_MAX = M_IN_MAX * (1 - (1 - X_IN) / (1 - X_OUT))        # kg/h de agua que puede evaporar (límite térmico)
CASCARA_ANIO = 419.0   # R  t/año por turno con el aire ajustado al 15 % (modelo térmico Rev. F)
Q_CASCARA = CASCARA_ANIO * 1000 / (H_TURNO * DIAS_ANIO) / (M_IN * (1 - (1 - X_IN) / (1 - X_OUT)))  # kg/kg de agua
RESIDENCIA_MIN = 97    # R  tiempo de residencia del guano en el secador (min)
H_SERVICIO = 9.0       # R  h/día de marcha por turno (estudio de fatiga: 8 h de carga + arranque y vaciado)
P_TGF = 54.0           # R  kW, demanda del TGF (66,9 kW instalados × 0,8)
_tg = RES["tg2"]
_fs = _tg["fs"]
P_TG2_BIO = 22.85      # R  kW del TS-BIO (circuito Q23), que no existe en la planta sin biogás
P_TG2 = _fs * (_tg["base_fs_kW"] - P_TG2_BIO)             # E  motores del TG2 sin el TS-BIO (la iluminación va aparte)
_P_BIO_ILUM = sum(c * w for nom, c, w in RES["iluminacion"]["cargas"] if "biogás" in nom) / 1000   # kW de la zona de biogás
KWH_ILUM = ((RES["iluminacion"]["P_Q25_kW"] - _P_BIO_ILUM) * 12 * 365     # E  iluminación exterior sin la zona de biogás
            + RES["iluminacion"]["P_Q26_kW"] * 24 * 365)                  #    y central de incendio todo el día
P_CONTRATADA = 85.0    # E  kW: balance del proyecto sin G1 (91,6 kW) menos las cargas del TS-BIO, redondeado
TARIFA = PRES["energia"]["tarifa"]                       # R  T3 estimada por el proyecto (10/2026), a confirmar
DISP_OBJETIVO = 0.92   # R  disponibilidad objetivo del plan de mantenimiento (informe, indicadores)
OPERARIOS_INFORME = 2  # R  informe: 2 operarios por turno
OPERARIOS_PRES = 3     # R  presupuesto: 3 operarios por turno
MIX_PROY = PRES["evaluacion"]["mix"]                     # R  canal: (fracción, USD/t)
PRECIO_PROY = sum(f * p for f, p in MIX_PROY.values())   # R  USD/t ponderado del proyecto
OTROS_USD = 1500 + 3300 + 4000                           # R  ácido, agua, gasoil de la pala, monitoreos, H&S
INV_2T_USD = 30000.0   # R  inversión adicional para el segundo turno (escenarios C y D del proyecto)
N_BASE, P2O5_BASE, K2O_BASE = 0.030, 0.028, 0.022        # R  nutrientes en base seca (informe, apartado 2)
LOTE_M2 = 120 * 76     # R  lote de 9.120 m² (apartado 16.3)

# =============================================================================== 2. mercado (V) y estimaciones (E)
UREA, MAP, KCL = 600.0, 980.0, 383.0                     # V  USD/t (urea y MAP mayoristas; KCl promedio mundial)
USD_KG_N = UREA / 1000 / 0.46
USD_KG_P2O5 = (MAP / 1000 - 0.11 * USD_KG_N) / 0.52
USD_KG_K2O = KCL / 1000 / 0.60
_ms = 1 - X_OUT
VALOR_NPK = 1000 * _ms * (N_BASE * USD_KG_N + P2O5_BASE * USD_KG_P2O5 + K2O_BASE * USD_KG_K2O)  # E  USD/t producto
BOLSA_25 = 74289 / 100                                   # V  $ por bolsa de rafia laminada 25 kg
BOLSA_CHICA_USD = 0.08                                   # R  USD por bolsa chica (proyecto)
SALARIO_REF = 5054.03 * 200                              # V  $/mes, operario calificado UOM rama 17
CARGAS = 0.30          # H  contribuciones patronales, ART y seguro de vida sobre el sueldo
COSTO_EMPLEADO = SALARIO_REF * 13 / 12 * (1 + CARGAS)    # E  $/mes por persona (13 sueldos con el aguinaldo)
HONORARIOS = 600000.0  # H  $/mes: estudio contable, asesoría legal y responsable técnico (SENASA, ambiente)
IIBB = 0.015           # V* ingresos brutos (industria, fuente secundaria: se toma el valor más alto del rango)
DEB_CRED = 0.006       # V  Ley 25.413 sobre cada crédito y cada débito
GAN_T1, GAN_T2 = 133514185.74, 1335141857.38             # V  tramos de la escala 2026 de sociedades
QUEBRANTO_ANIOS = 5    # V  años para compensar quebrantos (art. 25 LIG)
AMORT_ANIOS = {"obra": 50, "equipos": 10, "pala": 5, "intangible": 5}   # E  vidas útiles impositivas habituales
DIAS_COBRO, DIAS_STOCK, DIAS_PAGO = 45, 30, 30           # H  plazos del capital de trabajo
RAMPA = [(3, 0.5), (6, 0.8)]                             # H  puesta en marcha: meses 1-3 al 50 %, 4-6 al 80 %
H_ARRANQUE = H_SERVICIO - H_TURNO                        # R  1 h/día de ventiladores y bandas sin carga


def flete_granos(km):
    """$/t para granos: curva CATAC de enero de 2026 llevada al nivel de FETRA de noviembre de 2026 (E)."""
    puntos = [(1, 8453.24), (51, 16119.29), (101, 23965.15)]
    k = 32783.31 / 23965.15                               # actualización enero -> noviembre (100 km)
    if km <= 51:
        a, b = puntos[0], puntos[1]
    else:
        a, b = puntos[1], puntos[2]
    return k * (a[1] + (b[1] - a[1]) * (km - a[0]) / (b[0] - a[0]))


CAMION_GRANO, CAMION_CASCARA = 30.0, 10.0               # H  t por viaje (la cáscara, a 110 kg/m³, llena por volumen)
PRECIO_MOLINO = 5.0    # H  USD/t de cáscara en el molino (sin publicar; el proyecto da 20 a 30 USD/t sin aclarar el flete)
FLETE_CASCARA_50 = flete_granos(50) * CAMION_GRANO / CAMION_CASCARA / DOLAR     # E  USD/t de cáscara a 50 km
FLETE_CASCARA_100 = flete_granos(100) * CAMION_GRANO / CAMION_CASCARA / DOLAR   # E  USD/t a 100 km
GRANEL_MERCADO = 30.0 / 0.50 * _ms - flete_granos(40) / DOLAR   # E  USD/t ex planta: USD 30/t al 50 % de MS, puesto


# =============================================================================== 3. escenarios
def escenarios():
    """Parámetros de los tres escenarios. Cada línea: (clave, descripción, unidad, tipo, cons, real, opt)."""
    tabla = [
        ("m_in", "Alimentación de guano húmedo", "kg/h", "R", M_IN, M_IN, M_IN),
        ("X_in", "Humedad de entrada (base húmeda)", "%", "R/H", 0.75, X_IN, 0.70),
        ("X_out", "Humedad del producto", "%", "R", X_OUT, X_OUT, X_OUT),
        ("h_dia", "Horas de alimentación por día (1 turno)", "h", "R", H_TURNO, H_TURNO, H_TURNO),
        ("dias_anio", "Días de operación por año", "d", "R/H", 240, DIAS_ANIO, 264),
        ("disp", "Disponibilidad (horas de marcha / horas programadas)", "%", "R/H", 0.88, DISP_OBJETIVO, 0.95),
        ("merma", "Mermas (rechazo de zaranda, polvo, manipuleo)", "%", "H", 0.03, 0.02, 0.01),
        ("vendido", "Fracción de la producción que se vende", "%", "H", 0.80, 0.90, 0.95),
        ("mix", "Canales de venta (fracción; USD/t ex planta)", "—", "V/E/H",
         {"granel": (1.0, GRANEL_MERCADO)},
         {"granel": (0.60, VALOR_NPK), "bolsas 25 kg": (0.40, 200.0)},
         {k: tuple(v) for k, v in MIX_PROY.items()}),
        ("cascara", "Cáscara de arroz puesta en planta", "USD/t", "R/E/H", FLETE_CASCARA_100 + PRECIO_MOLINO,
         FLETE_CASCARA_50 + PRECIO_MOLINO, 25.0),
        ("flete_guano", "Flete del guano húmedo desde la granja", "USD/t", "E/H",
         flete_granos(40) / DOLAR, flete_granos(20) / DOLAR, 0.0),
        ("tarifa", "Tarifa eléctrica (factor sobre la T3 estimada del proyecto)", "—", "R/H", 1.20, 1.00, 1.00),
        ("op_turno", "Operarios por turno", "u", "R", OPERARIOS_PRES, OPERARIOS_PRES, OPERARIOS_INFORME),
        ("adm", "Personal de administración y ventas", "u", "H", 1, 1, 1),
        ("comerc", "Gastos de comercialización (sobre ventas)", "%", "H", 0.08, 0.05, 0.03),
        ("mant", "Mantenimiento y repuestos (sobre equipos, por año)", "%", "R/H", 0.04, 0.03, 0.025),
        ("f_inv", "Inversión del proyecto (factor por la precisión ± 25 %)", "—", "R/H", 1.15, 1.00, 0.95),
        ("tierra", "Terreno (lote de 9.120 m²)", "USD/m²", "H", 10.0, 5.0, 2.7),
        ("pala", "Pala cargadora usada de ≈ 1 m³", "USD", "V", 44000.0, 38000.0, 32000.0),
    ]
    esc = {}
    for i, nombre in enumerate(("conservador", "realista", "optimista")):
        p = {fila[0]: copy.deepcopy(fila[4 + i]) for fila in tabla}
        p.update(nombre=nombre, turnos=1, lineas=1, inv_extra_usd=0.0, p_extra_kw=0.0, ingresos_extra=0.0,
                 op_extra=0, f_tgf=1.0)
        esc[nombre] = p
    return tabla, esc


# =============================================================================== 4. inversión
def inversion(p):
    """Inversión inicial consolidada, en USD, por clase (para amortizar) y con los ítems no contemplados."""
    f = p["f_inv"]
    clases = {"obra": 0.0, "equipos": 0.0, "intangible": 0.0}
    filas = []
    for cod in SIN_BIOGAS:
        _c, rub, desc, q, u, pu, tot, *_ = FILAS[cod]
        tot = tot * f
        fo, fi = OBRA.get(cod, 0.0), INTANGIBLE.get(cod, 0.0)
        clases["obra"] += tot * fo
        clases["intangible"] += tot * fi
        clases["equipos"] += tot * (1 - fo - fi)
        filas.append((cod, rub, desc, q, u, pu * f, tot, "R"))
    sub = sum(clases.values())
    imprev = IMPREV * sub
    for k in clases:                                       # los imprevistos se reparten en proporción
        clases[k] *= 1 + IMPREV
    proyecto = sub + imprev
    extra = {
        "Terreno (lote de 9.120 m²)": (LOTE_M2 * p["tierra"], "terreno", "H"),
        "Pala cargadora frontal usada de ≈ 1 m³ (la usa el operario de campo y no figura en el presupuesto)":
            (p["pala"], "pala", "V"),
        "Puesta en marcha, ensayos con el módulo piloto (Rev. F) y capacitación (1 % del proyecto)":
            (0.01 * proyecto, "intangible", "H"),
        "Impuesto a los débitos bancarios sobre los pagos de la inversión (0,6 %)": (DEB_CRED * proyecto, "intangible", "V"),
    }
    if p.get("inv_extra_usd"):
        extra["Inversión adicional de la alternativa de ampliación: equipos"] = (p["inv_extra_usd"], "equipos", "R/E")
    if p.get("inv_extra_obra_usd"):
        extra["Inversión adicional de la alternativa de ampliación: obra civil"] = (p["inv_extra_obra_usd"], "obra", "E")
    clases["terreno"], clases["pala"] = 0.0, 0.0
    for _k, (v, cl, _t) in extra.items():
        clases[cl] += v
    total = proyecto + sum(v for v, _c, _t in extra.values())
    return {"filas": filas, "subtotal": sub, "imprevistos": imprev, "proyecto": proyecto, "extra": extra,
            "clases": clases, "total": total}


# =============================================================================== 5. producción y costos de un mes
def precio_medio(mix):
    return sum(f * pr for f, pr in mix.values())


def envase_por_t(mix):
    """$ por tonelada vendida: bolsa de 25 kg; las bolsas chicas van además en bolsas de 25 kg para el despacho."""
    c = 0.0
    for canal, (f, _pr) in mix.items():
        if "25" in canal:
            c += f * 40 * BOLSA_25
        elif "chica" in canal:
            c += f * (40 * BOLSA_25 + 1000 / 2.2 * BOLSA_CHICA_USD * DOLAR)
    return c


def mes(p, inv, f_rampa=1.0, k=1):
    """Producción, ventas y costos de un mes (en pesos). f_rampa reduce el caudal durante la puesta en marcha.
    p["deriva"] (opcional) = variación real anual de precios y costos respecto de la inflación general."""
    der = p.get("deriva") or {}
    g = lambda clave: (1 + der.get(clave, 0.0)) ** (min(k - 1, 60) / 12)   # noqa: E731  (el desfase dura 5 años)
    dias = p["dias_anio"] / 12
    h_carga = p["h_dia"] * dias * p["disp"]                 # h de alimentación efectivas en el mes
    m_in = p["m_in"] * p["lineas"]
    if p.get("tope_termico", True):                          # el secador no evapora más de W_MAX por línea
        f_w = 1 - (1 - p["X_in"]) / (1 - p["X_out"])
        m_in = min(m_in, W_MAX * p["lineas"] * p.get("f_cap", 1.0) / f_w)
    m_in *= f_rampa
    humedo = m_in * h_carga / 1000                          # t de guano húmedo procesado
    seco = humedo * (1 - p["X_in"]) / (1 - p["X_out"])      # t de producto al 15 % (sale del secador)
    agua = humedo - seco
    comerciable = seco * (1 - p["merma"])
    vendido = comerciable * p["vendido"]
    pm = precio_medio(p["mix"]) * DOLAR * g("precio")       # $/t
    ventas = vendido * pm + p.get("ingresos_extra", 0.0) * DOLAR / 12
    # energía: la planta marcha las horas de carga más 1 h por día de arranque y vaciado (estudio de fatiga); con
    # turnos seguidos el hogar no se apaga entre turnos, así que el arranque y el vaciado se hacen una sola vez
    h_marcha = (p["h_dia"] * p["disp"] + H_ARRANQUE) * dias
    kw = P_TGF * p["lineas"] * p["f_tgf"] + P_TG2
    kwh = kw * h_marcha + KWH_ILUM / 12
    t = TARIFA
    c_energia_var = kwh * t["energia_kwh"] * p["tarifa"] * g("energia")
    c_energia_fija = (t["cargo_fijo_mes"] + t["potencia_kw_mes"] * (P_CONTRATADA + p["p_extra_kw"])) * p["tarifa"] * g("energia")
    cascara = agua * Q_CASCARA                               # t de cáscara
    c_cascara = cascara * p["cascara"] * DOLAR
    c_flete = humedo * p["flete_guano"] * DOLAR
    c_envases = vendido * envase_por_t(p["mix"])
    horas_anio = p["h_dia"] * p["dias_anio"]
    c_otros = OTROS_USD * DOLAR / 12 * (0.4 + 0.6 * horas_anio / (H_TURNO * DIAS_ANIO))
    base_mant = inv["clases"]["equipos"] + inv["clases"]["pala"]
    c_mant = p["mant"] * base_mant * DOLAR / 12 * (0.7 + 0.3 * horas_anio / (H_TURNO * DIAS_ANIO))
    operarios = p["op_turno"] * p["turnos"] + p.get("op_extra", 0)
    c_mo = operarios * COSTO_EMPLEADO * g("salarios")
    c_adm = (p["adm"] * COSTO_EMPLEADO + HONORARIOS) * g("salarios")
    c_seguros = 0.01 * (inv["total"] - LOTE_M2 * p["tierra"]) * DOLAR / 12   # R  seguros, inmobiliario y tasas (1 %)
    c_comerc = p["comerc"] * ventas
    c_iibb = IIBB * ventas
    produccion = c_cascara + c_energia_var + c_energia_fija + c_flete + c_envases + c_otros + c_mant + c_mo
    estructura = c_adm + c_seguros
    pagos = produccion + estructura + c_comerc + c_iibb
    c_debcred = DEB_CRED * (ventas + pagos)
    comerciales = c_comerc + c_iibb + c_debcred
    return {
        "h_carga": h_carga, "h_marcha": h_marcha, "humedo_t": humedo, "seco_t": seco, "agua_t": agua,
        "comerciable_t": comerciable, "vendido_t": vendido, "precio_t": pm, "ventas": ventas, "kwh": kwh,
        "cascara_t": cascara, "operarios": operarios,
        "costos": {"cascara": c_cascara, "energia_var": c_energia_var, "energia_fija": c_energia_fija,
                   "flete_guano": c_flete, "envases": c_envases, "otros_insumos": c_otros,
                   "mantenimiento": c_mant, "mano_obra": c_mo, "administracion": c_adm, "seguros_tasas": c_seguros,
                   "comercializacion": c_comerc, "iibb": c_iibb, "deb_cred": c_debcred},
        "produccion": produccion, "estructura": estructura, "comerciales": comerciales,
        "total": produccion + estructura + comerciales,
        "compras": c_cascara + c_envases + c_energia_var + c_energia_fija + c_otros,
        "costo_var_produccion": c_cascara + c_energia_var + c_flete + c_envases,
    }


def precio_equilibrio(p, inv):
    """Precio medio ex planta ($/t) con el que el EBITDA de un mes de régimen es cero. No es igual al costo por kg,
    porque la comercialización, ingresos brutos y el impuesto a los débitos y créditos crecen con el precio."""
    def ebitda(f):
        q = dict(copy.deepcopy(p), mix={k: (fr, pr * f) for k, (fr, pr) in p["mix"].items()})
        m = mes(q, inv)
        return m["ventas"] - m["total"]
    lo, hi = 0.0, 50.0
    if ebitda(hi) < 0:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if ebitda(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return hi * precio_medio(p["mix"]) * DOLAR


def ganancias(base):
    """Impuesto a las ganancias de sociedades (escala 2026, en pesos constantes)."""
    if base <= 0:
        return 0.0
    if base <= GAN_T1:
        return 0.25 * base
    if base <= GAN_T2:
        return 0.25 * GAN_T1 + 0.30 * (base - GAN_T1)
    return 0.25 * GAN_T1 + 0.30 * (GAN_T2 - GAN_T1) + 0.35 * (base - GAN_T2)


def amortizacion_mensual(inv):
    cl = inv["clases"]
    return {k: cl[k] * DOLAR / AMORT_ANIOS[k] / 12 for k in AMORT_ANIOS}


def rampa(k):
    for hasta, f in RAMPA:
        if k <= hasta:
            return f
    return 1.0


# =============================================================================== 6. flujo de caja mensual
def flujo(p, meses=MESES):
    """Flujo de caja mensual en pesos constantes. Mes 0: inversión; meses 1..N: operación."""
    inv = inversion(p)
    am = amortizacion_mensual(inv)
    inv_ars = inv["total"] * DOLAR
    filas = []
    ct_ant = 0.0
    quebrantos = []                                        # [(año, monto)] pendientes de compensar
    impuesto_anual = {}
    acum = -inv_ars
    filas.append({"mes": 0, "inversion": -inv_ars, "flujo": -inv_ars, "flujo_operativo": -inv_ars, "acumulado": acum})
    base_anio, devengado = 0.0, {}
    for k in range(1, meses + 1):
        m = mes(p, inv, rampa(k), k)
        amort = sum(v for kk, v in am.items() if k <= AMORT_ANIOS[kk] * 12)
        ebitda = m["ventas"] - m["total"]
        ebit = ebitda - amort
        base_anio += ebit
        anio = (k - 1) // 12 + 1
        # capital de trabajo: cobrar + existencias - pagar
        ct = (m["ventas"] * DIAS_COBRO + m["costo_var_produccion"] * DIAS_STOCK - m["compras"] * DIAS_PAGO) / DIAS_MES
        dct = ct - ct_ant
        ct_ant = ct
        # ganancias: se liquida al cierre de cada año y se paga en 12 anticipos durante el año siguiente
        pago_gan = impuesto_anual.get(anio - 1, 0.0) / 12
        if k % 12 == 0:
            base = base_anio
            if base < 0:
                quebrantos.append([anio, -base])
                imp = 0.0
            else:
                for q in quebrantos:                        # compensa los quebrantos de los 5 años anteriores
                    if anio - q[0] <= QUEBRANTO_ANIOS and q[1] > 0 and base > 0:
                        usa = min(q[1], base)
                        q[1] -= usa
                        base -= usa
                imp = ganancias(base)
            impuesto_anual[anio] = imp
            devengado[anio] = imp
            base_anio = 0.0
        residual = 0.0
        if k == meses:                                     # valor residual y recupero del capital de trabajo
            cl = inv["clases"]
            residual = (LOTE_M2 * p["tierra"] + cl["obra"] * (1 - meses / 12 / AMORT_ANIOS["obra"])) * DOLAR + ct
            pago_gan += impuesto_anual.get(anio, 0.0)      # el impuesto del último año se cancela al final
        fc = ebitda - pago_gan - dct + residual
        acum += fc - residual
        filas.append({"mes": k, "anio": anio, "f_rampa": rampa(k), **{kk: m[kk] for kk in (
            "humedo_t", "seco_t", "comerciable_t", "vendido_t", "ventas", "kwh", "cascara_t", "h_carga")},
            "costos": m["costos"], "produccion": m["produccion"], "estructura": m["estructura"],
            "comerciales": m["comerciales"], "costo_total": m["total"], "ebitda": ebitda, "amortizacion": amort,
            "ebit": ebit, "ganancias_pagado": pago_gan, "capital_trabajo": ct, "d_ct": dct, "residual": residual,
            "flujo": fc, "flujo_operativo": fc - residual, "acumulado": acum})
    # el impuesto devengado se reparte por mes para el estado de resultados
    for f in filas[1:]:
        f["ganancias_devengado"] = devengado.get(f["anio"], 0.0) / 12
        f["beneficio_neto"] = f["ebit"] - f["ganancias_devengado"]
    return inv, filas


# =============================================================================== 7. indicadores
def payback(filas, tasa=None):
    """Mes en que el flujo acumulado (descontado si se da la tasa) se hace ≥ 0; interpola dentro del mes.
    No cuenta el valor residual ni el recupero del capital de trabajo del último mes: la inversión se tiene que
    recuperar con lo que genera la operación."""
    r = (1 + tasa) ** (1 / 12) - 1 if tasa else 0.0
    acum = 0.0
    for f in filas:
        v = f["flujo_operativo"] / (1 + r) ** f["mes"]
        if acum < 0 <= acum + v and f["mes"] > 0:
            return f["mes"] - 1 + (-acum / v)
        acum += v
    return None


def van(filas, tasa=TASA_REAL):
    r = (1 + tasa) ** (1 / 12) - 1
    return sum(f["flujo"] / (1 + r) ** f["mes"] for f in filas)


def tir(filas):
    """TIR anual equivalente de los flujos mensuales (bisección)."""
    def g(rm):
        return sum(f["flujo"] / (1 + rm) ** f["mes"] for f in filas)
    lo, hi = -0.05, 0.2
    if g(lo) * g(hi) > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        if g(lo) * g(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (1 + (lo + hi) / 2) ** 12 - 1


def anio(filas, n):
    """Suma de un año de operación (n = 1, 2, ...)."""
    sel = [f for f in filas[1:] if f["anio"] == n]
    claves = ("humedo_t", "seco_t", "comerciable_t", "vendido_t", "ventas", "kwh", "cascara_t", "h_carga",
              "produccion", "estructura", "comerciales", "costo_total", "ebitda", "amortizacion", "ebit",
              "ganancias_devengado", "ganancias_pagado", "beneficio_neto", "d_ct", "flujo")
    s = {k: sum(f[k] for f in sel) for k in claves}
    s["costos"] = {k: sum(f["costos"][k] for f in sel) for k in sel[0]["costos"]}
    return s


def indicadores(p, meses=MESES):
    inv, filas = flujo(p, meses)
    a2 = anio(filas, 2)                                    # año de régimen (sin puesta en marcha)
    a3 = anio(filas, 3)                                    # flujo de régimen: ya se paga el impuesto de un año entero
    inv_total = inv["total"] * DOLAR
    ct_regimen = filas[24]["capital_trabajo"]
    inv_con_ct = inv_total + max(ct_regimen, 0.0)
    m = mes(p, inv)                                        # mes tipo de régimen
    # punto de equilibrio con el mes de régimen: costos variables por t vendida y costos fijos de caja
    var = (m["costos"]["cascara"] + m["costos"]["energia_var"] + m["costos"]["flete_guano"] + m["costos"]["envases"]
           + 0.6 * m["costos"]["otros_insumos"])
    var_ventas = m["costos"]["comercializacion"] + m["costos"]["iibb"] + m["costos"]["deb_cred"]
    fijos = m["total"] - var - var_ventas
    t_v = m["vendido_t"]
    precio = m["ventas"] / t_v if t_v else 0.0
    cu = precio - (var + var_ventas) / t_v if t_v else 0.0  # contribución por t vendida
    am_mes = a2["amortizacion"] / 12
    pe_op = fijos * 12 / cu if cu > 0 else None              # t/año vendidas para cubrir los costos de caja
    pe_cont = (fijos + am_mes) * 12 / cu if cu > 0 else None
    pb = payback(filas)
    fc_reg = a3["flujo"] / 12
    return {
        "nombre": p["nombre"], "inversion": inv, "inv_total": inv_total, "ct_regimen": ct_regimen,
        "inv_con_ct": inv_con_ct, "anio1": anio(filas, 1), "anio2": a2, "anio3": a3,
        "precio_eq_t": precio_equilibrio(p, inv),
        "mes_regimen": m, "precio_t": m["precio_t"], "payback_meses": pb,
        "payback_descontado": payback(filas, TASA_REAL),
        "payback_formula": inv_total / fc_reg if fc_reg > 0 else None,
        "van": van(filas), "tir": tir(filas),
        "roi_anual": a2["beneficio_neto"] / inv_con_ct * 100,
        "roi_5": sum(f["beneficio_neto"] for f in filas[1:61]) / inv_con_ct * 100,
        "pe_operativo_t": pe_op, "pe_contable_t": pe_cont, "contribucion_t": cu, "fijos_mes": fijos,
        "pe_operativo_prod_t": pe_op / (p["vendido"] * (1 - p["merma"])) if pe_op else None,
        "costo_prod_kg": a2["produccion"] / (a2["seco_t"] * 1000),
        "costo_total_kg": a2["costo_total"] / (a2["vendido_t"] * 1000),
        "costo_total_kg_amort": (a2["costo_total"] + a2["amortizacion"]) / (a2["vendido_t"] * 1000),
        "neto_kg": a2["beneficio_neto"] / (a2["vendido_t"] * 1000),
        "flujo_regimen_mes": fc_reg, "filas": filas,
    }


# =============================================================================== 8. reconciliación con el proyecto
def puente():
    """Del beneficio neto del proyecto (variante sin biogás, un turno) al flujo del escenario realista, paso a paso.
    Cada paso cambia un supuesto; el efecto se mide con los valores de un año de régimen (USD/año)."""
    ev = PRES["evaluacion"]
    b = next(e for e in ev["escenarios"] if e["nombre"].startswith("B"))
    pasos = [("Proyecto: variante sin biogás, un turno (presupuesto.json)", b["neto"])]
    sin_bio = INV["sin_biogas"]
    prod = 650.0
    ventas = prod * PRECIO_PROY
    costos = PRES["evaluacion"]["costos"]
    # valores del proyecto para la variante sin biogás
    c_proy = {"cascara": costos[[k for k in costos if k.startswith("Cáscara")][0]],
              "energia": PRES["energia"]["costo_sin_G1_USD"], "mo": 39000.0,
              "envases": costos[[k for k in costos if k.startswith("Bolsas")][0]],
              "mant": 0.03 * sin_bio * 0.55, "otros": float(OTROS_USD), "seguros": 0.01 * sin_bio}
    neto_proy = ventas + 5000 + 18500 - sum(c_proy.values())
    assert abs(neto_proy - b["neto"]) < 2, (neto_proy, b["neto"])
    _t, esc = escenarios()
    r = esc["realista"]
    ind = indicadores(r)
    a2 = ind["anio3"]                                      # un año de régimen con el impuesto de un año entero
    usd = lambda x: x / DOLAR                                # noqa: E731
    ar = lambda x, d=1: f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")   # noqa: E731
    c = {k: usd(v) for k, v in a2["costos"].items()}
    v_real = usd(a2["ventas"])
    # pasos (en el orden en que se explican en el informe)
    prod_real_seco = a2["seco_t"]
    pasos.append(("Se quita el «ahorro en la gestión del guano» y el «ahorro sanitario»: son de la granja, no "
                  "ingresos de caja de la planta", -18500.0))
    pasos.append(("Se quita la venta del sulfato de amonio del lavador: no hay mercado ni registro verificados", -5000.0))
    pasos.append((f"Producción con disponibilidad del {r['disp'] * 100:.0f} %, mermas del {r['merma'] * 100:.0f} % y "
                  f"venta del {r['vendido'] * 100:.0f} % ({ar(a2['vendido_t'], 0)} t vendidas en lugar de 650 t)",
                  (a2["vendido_t"] - prod) * PRECIO_PROY))
    pasos.append((f"Precio medio realista (USD {ar(precio_medio(r['mix']))}/t en lugar de USD {ar(PRECIO_PROY)}/t)",
                  v_real - a2["vendido_t"] * PRECIO_PROY))
    pasos.append((f"Cáscara puesta en planta a USD {ar(r['cascara'], 0)}/t (flete por volumen) y consumo según la "
                  "producción real", -(c["cascara"] - c_proy["cascara"])))
    pasos.append((f"Flete del guano húmedo desde la granja (USD {ar(r['flete_guano'])}/t, 20 km)", -c["flete_guano"]))
    pasos.append(("Energía sin las cargas del biogás, iluminación contada una vez, 85 kW contratados y 1 h diaria de "
                  "arranque y vaciado",
                  -(c["energia_var"] + c["energia_fija"] - c_proy["energia"])))
    pasos.append(("Mano de obra con el sueldo UOM de noviembre de 2026 y cargas sociales del 30 %",
                  -(c["mano_obra"] - c_proy["mo"])))
    pasos.append(("Envases según el canal (40 % en bolsas de 25 kg)", -(c["envases"] - c_proy["envases"])))
    pasos.append(("Mantenimiento sobre el valor de los equipos (incluida la pala) y otros insumos según las horas",
                  -(c["mantenimiento"] + c["otros_insumos"] - c_proy["mant"] - c_proy["otros"])))
    pasos.append(("Seguros, inmobiliario y tasas (1 % de la inversión, como el proyecto)",
                  -(c["seguros_tasas"] - c_proy["seguros"])))
    pasos.append(("Administración, ventas y honorarios (no estaban en el proyecto)", -c["administracion"]))
    pasos.append(("Comercialización (5 %), ingresos brutos (1,5 %) e impuesto a los débitos y créditos",
                  -(c["comercializacion"] + c["iibb"] + c["deb_cred"])))
    ebitda = usd(a2["ebitda"])
    suma = sum(v for _t2, v in pasos)
    assert abs(suma - ebitda) < 5, (suma, ebitda)
    pasos.append(("Impuesto a las ganancias y variación del capital de trabajo (año de régimen)",
                  usd(a2["flujo"]) - ebitda))
    return {"pasos": pasos, "ebitda_realista_usd": ebitda, "flujo_realista_usd": usd(a2["flujo"]),
            "prod_real_seco": prod_real_seco}


# =============================================================================== 9. sensibilidad
_pct = lambda v: f"{v * 100:.0f} %".replace(".", ",")          # noqa: E731
_num = lambda v: f"{v:,.0f}".replace(",", ".")                   # noqa: E731
SENSIBLES = [
    # (clave, nombre, valor bajo, valor alto, cómo se aplica, formato del valor)
    ("precio", "Precio de venta", 0.70, 1.30, "factor", lambda v: f"{(v - 1) * 100:+.0f} %".replace("-", "−")),
    ("tarifa", "Costo de la energía eléctrica", 0.80, 1.30, "factor", lambda v: f"{(v - 1) * 100:+.0f} %".replace("-", "−")),
    ("h_dia", "Horas de funcionamiento por día", 6.0, 16.0, "valor", lambda v: f"{v:.0f} h"),
    ("m_in", "Producción por hora (guano húmedo)", 800.0, 1440.0, "valor", lambda v: f"{_num(v)} kg/h"),
    ("X_in", "Humedad inicial", 0.78, 0.65, "valor", _pct),
    ("X_out", "Humedad final", 0.12, 0.18, "valor", _pct),
    ("dias_anio", "Días de funcionamiento por mes", 216, 288, "valor", lambda v: f"{v / 12:.0f} d"),
    ("mant", "Mantenimiento (sobre equipos, por año)", 0.02, 0.05, "valor", _pct),
    ("cascara", "Cáscara puesta en planta", 25.0, 65.0, "valor", lambda v: f"USD {v:.0f}/t"),
    ("flete_guano", "Flete del guano húmedo", 0.0, flete_granos(40) / DOLAR, "valor",
     lambda v: "0 km" if v == 0 else "40 km"),
    ("vendido", "Fracción vendida", 0.70, 1.00, "valor", _pct),
]


def aplicar(p, clave, v, modo):
    q = copy.deepcopy(p)
    if clave == "precio":
        q["mix"] = {k: (f, pr * v) for k, (f, pr) in q["mix"].items()}
    elif modo == "factor":
        q[clave] = q[clave] * v
    else:
        q[clave] = v
    if clave == "h_dia":
        q["turnos"] = math.ceil(v / H_TURNO)
    return q


DERIVAS = [
    ("Energía +3 %/año y salarios +1 %/año por encima de la inflación (5 años)", {"energia": 0.03, "salarios": 0.01}),
    ("Precio del guano −2 %/año respecto de la inflación", {"precio": -0.02}),
]


def sensibilidad(p, rangos=None):
    """Cambia una variable por vez (valor bajo y alto) y mide el flujo anual de régimen, el payback y el VAN.
    rangos = {clave: (bajo, alto)} reemplaza los valores de SENSIBLES para otro caso base."""
    base = indicadores(p)
    out = []
    rangos = rangos or {}
    for clave, nombre, lo, hi, modo, fmt in SENSIBLES:
        if clave in rangos:
            lo, hi = rangos[clave]
        fila = {"clave": clave, "nombre": nombre, "desc": f"{nombre} ({fmt(lo)} / {fmt(hi)})",
                "txt_bajo": fmt(lo), "txt_alto": fmt(hi)}
        for nom, v in (("bajo", lo), ("alto", hi)):
            q = aplicar(p, clave, v, modo)
            if clave == "h_dia" and v > H_TURNO:
                q["inv_extra_usd"] = max(q.get("inv_extra_usd", 0.0), INV_2T_USD)
            ind = indicadores(q)
            fila[nom] = {"valor": v, "flujo_anual": ind["anio3"]["flujo"], "payback": ind["payback_meses"],
                         "van": ind["van"]}
        out.append(fila)
    der = []
    for desc, d in DERIVAS:
        ind = indicadores(dict(copy.deepcopy(p), deriva=d))
        der.append({"desc": desc, "flujo_anio5": anio(ind["filas"], 5)["flujo"], "payback": ind["payback_meses"],
                    "van": ind["van"]})
    return {"base": {"flujo_anual": base["anio3"]["flujo"], "payback": base["payback_meses"], "van": base["van"],
                     "flujo_anio5": anio(base["filas"], 5)["flujo"]}, "filas": out, "derivas": der}


# =============================================================================== 10. análisis inverso
def precio_necesario(p, meses_obj):
    """Factor sobre el precio medio que hace que el payback sea ≤ meses_obj (bisección)."""
    def ok(f):
        q = aplicar(p, "precio", f, "factor")
        pb = indicadores(q, meses=max(meses_obj + 12, 72))["payback_meses"]
        return pb is not None and pb <= meses_obj
    lo, hi = 0.0, 20.0
    if not ok(hi):
        return None
    for _ in range(40):
        mid = (lo + hi) / 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def capacidad_necesaria(p, meses_obj):
    """Caudal de guano húmedo (kg/h, mismas horas y estructura) que recupera la inversión en meses_obj.
    Es el mínimo teórico: supone que los costos fijos y la inversión no cambian (no mira el límite de la máquina)."""
    def ok(m_in):
        q = dict(copy.deepcopy(p), m_in=m_in, tope_termico=False)
        pb = indicadores(q, meses=max(meses_obj + 12, 72))["payback_meses"]
        return pb is not None and pb <= meses_obj
    lo, hi = 100.0, 60000.0
    if not ok(hi):
        return None
    for _ in range(40):
        mid = (lo + hi) / 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


CONFIGS = [  # (código, descripción, h/día, turnos, inversión adicional USD)
    ("1T", "1 turno (8 h/día)", 8.0, 1, 0.0),
    ("2T", "2 turnos (16 h/día)", 16.0, 2, INV_2T_USD),
    ("3T", "3 turnos (24 h/día)", 24.0, 3, INV_2T_USD),
]
INV_B = 2000.0         # E  tolva de retención de 1 m³ para 1.440 kg/h (ítem B17 escalado)


def capacidad_minima(p, cfg, meses_obj):
    """Caudal mínimo de guano húmedo (kg/h por línea) con esas horas que recupera la inversión en meses_obj.
    Si pasa de 1.000 kg/h se suma la tolva de retención mayor (alternativa B)."""
    _c, _d, h, turnos, inv_x = cfg

    def ok(m_in):
        q = dict(copy.deepcopy(p), m_in=m_in, h_dia=h, turnos=turnos, tope_termico=False,
                 inv_extra_usd=inv_x + (INV_B if m_in > M_IN else 0.0))
        pb = indicadores(q, meses=max(meses_obj + 12, 72))["payback_meses"]
        return pb is not None and pb <= meses_obj
    lo, hi = 50.0, 80000.0
    if not ok(hi):
        return None
    for _ in range(45):
        mid = (lo + hi) / 2
        if ok(mid):
            hi = mid
        else:
            lo = mid
    return hi


def detalle_capacidad(p, cfg, m_in):
    """Producción y resultados de una configuración con un caudal dado (para las tablas del punto 13)."""
    _c, _d, h, turnos, inv_x = cfg
    q = dict(copy.deepcopy(p), m_in=m_in, h_dia=h, turnos=turnos, tope_termico=False,
             inv_extra_usd=inv_x + (INV_B if m_in > M_IN else 0.0))
    ind = indicadores(q)
    a2, a3, m = ind["anio2"], ind["anio3"], ind["mes_regimen"]
    dias_mes = q["dias_anio"] / 12
    return {"m_in": m_in, "h_dia": h, "turnos": turnos, "dias_mes": dias_mes,
            "humedo_dia_kg": m["humedo_t"] / dias_mes * 1000, "humedo_mes_t": m["humedo_t"],
            "humedo_anio_t": a2["humedo_t"], "seco_anio_t": a2["seco_t"], "vendido_anio_t": a2["vendido_t"],
            "seco_mes_t": m["seco_t"], "vendido_mes_t": m["vendido_t"], "inv_total": ind["inv_total"],
            "flujo_anual": a3["flujo"], "payback": ind["payback_meses"], "van": ind["van"],
            "lineas_necesarias": math.ceil(m_in / M_IN_MAX - 1e-9)}


def alternativas(p):
    """Configuraciones de ampliación (punto 13.4). Cada una: cambios de parámetros, inversión extra y notas."""
    eq = {c: FILAS[c][6] for c in FILAS}
    proc = sum(eq[c] for c in ("A1", "A2", "A3", "A4", "A5", "A6", "A7"))
    inv_c = (proc * (2 ** 0.6 - 1) + 0.5 * eq["A8"] + 0.25 * eq["A9"] + 0.3 * eq["B14"]) * 1.10
    inv_d = (eq["A1"] + eq["A2"] + eq["A3"] + eq["A4"] + 0.5 * eq["A5"] + eq["A6"] + 0.5 * eq["A7"] + 0.5 * eq["A8"]
             + 0.5 * eq["A9"] + 0.5 * eq["B14"]) * (1 + IMPREV)
    inv_b = INV_B
    obra_c, obra_d = 0.25 * eq["A9"] * 1.10, 0.5 * eq["A9"] * (1 + IMPREV)
    inv_c -= obra_c
    inv_d -= obra_d
    alts = [
        ("Actual", "1 turno de 8 h, 1.000 kg/h, aire a ≈ 100 °C", {}),
        ("A1", "Más horas: 2 turnos (16 h/día)", {"h_dia": 16.0, "turnos": 2, "inv_extra_usd": INV_2T_USD}),
        ("A2", "Más horas: 3 turnos (24 h/día, 5 días por semana)", {"h_dia": 24.0, "turnos": 3,
                                                                    "inv_extra_usd": INV_2T_USD}),
        ("B", "Optimizar: aire a 135 °C, 1.440 kg/h en 1 turno (tolva de retención de 1 m³)",
         {"m_in": M_IN_MAX, "inv_extra_usd": inv_b}),
        ("A1+B", "2 turnos a 1.440 kg/h", {"m_in": M_IN_MAX, "h_dia": 16.0, "turnos": 2,
                                           "inv_extra_usd": INV_2T_USD + inv_b}),
        ("A2+B", "3 turnos a 1.440 kg/h", {"m_in": M_IN_MAX, "h_dia": 24.0, "turnos": 3,
                                           "inv_extra_usd": INV_2T_USD + inv_b}),
        ("C", "Máquina el doble de grande (2.000 kg/h a 100 °C), 1 turno",
         {"m_in": 2 * M_IN, "inv_extra_usd": inv_c, "inv_extra_obra_usd": obra_c, "op_extra": 1, "f_tgf": 1.8,
          "p_extra_kw": 45.0, "f_cap": 2.0}),
        ("D", "Segunda secadora SC-4 en paralelo (2 × 1.000 kg/h), 1 turno",
         {"lineas": 2, "inv_extra_usd": inv_d, "inv_extra_obra_usd": obra_d, "op_extra": 1, "p_extra_kw": 55.0}),
        ("D+A1", "Dos secadoras, 2 turnos", {"lineas": 2, "h_dia": 16.0, "turnos": 2, "op_extra": 2,
                                             "inv_extra_usd": inv_d + INV_2T_USD, "inv_extra_obra_usd": obra_d,
                                             "p_extra_kw": 55.0}),
    ]
    out = []
    for cod, desc, cambios in alts:
        q = dict(copy.deepcopy(p), **cambios)
        ind = indicadores(q)
        a2, a3 = ind["anio2"], ind["anio3"]
        w = q["m_in"] * q["lineas"] * (1 - (1 - q["X_in"]) / (1 - q["X_out"]))
        fp = precio_necesario(q, 60)
        out.append({"cod": cod, "desc": desc, "inv_extra_usd": q.get("inv_extra_usd", 0.0) + q.get("inv_extra_obra_usd", 0.0),
                    "precio_60": None if fp is None else fp * precio_medio(q["mix"]),
                    "costos_var": a2["costos"], "operarios": ind["mes_regimen"]["operarios"],
                    "inv_total": ind["inv_total"], "humedo_anio": a2["humedo_t"], "seco_anio": a2["seco_t"],
                    "vendido_anio": a2["vendido_t"], "ventas": a2["ventas"], "costos": a2["costo_total"],
                    "flujo_anual": a3["flujo"], "neto_anual": a2["beneficio_neto"], "payback": ind["payback_meses"],
                    "van": ind["van"],
                    "kg_h": q["m_in"] * q["lineas"], "h_dia": q["h_dia"],
                    "t_dia": q["m_in"] * q["lineas"] * q["h_dia"] * q["disp"] / 1000,   # por día de trabajo, con la disponibilidad
                    "agua_kg_h": w, "limite_termico": w <= W_MAX * q["lineas"] * (1.0 if cod != "C" else 2.0) + 1})
    return out


# =============================================================================== 11. programa principal
def resumen(ind):
    a2, m = ind["anio2"], ind["mes_regimen"]
    return {k: ind[k] for k in ("nombre", "inv_total", "ct_regimen", "inv_con_ct", "precio_t", "payback_meses",
                                "payback_descontado", "payback_formula", "van", "tir", "roi_anual", "roi_5",
                                "pe_operativo_t", "pe_contable_t", "pe_operativo_prod_t", "contribucion_t",
                                "fijos_mes", "costo_prod_kg", "costo_total_kg", "costo_total_kg_amort", "neto_kg",
                                "flujo_regimen_mes")} | {
        "anio2": {k: v for k, v in a2.items()}, "anio1": ind["anio1"], "anio3": ind["anio3"],
        "precio_eq_t": ind["precio_eq_t"],
        "mes": {k: m[k] for k in ("h_carga", "h_marcha", "humedo_t", "seco_t", "agua_t", "comerciable_t",
                                  "vendido_t", "ventas", "kwh", "cascara_t", "operarios", "produccion",
                                  "estructura", "comerciales", "total")} | {"costos": m["costos"]},
        "inversion": {"proyecto": ind["inversion"]["proyecto"], "total": ind["inversion"]["total"],
                      "clases": ind["inversion"]["clases"],
                      "extra": {k: v[0] for k, v in ind["inversion"]["extra"].items()}},
        "flujo_mensual": [{k: f.get(k) for k in ("mes", "ventas", "costo_total", "ebitda", "amortizacion",
                                                  "ganancias_pagado", "ganancias_devengado", "beneficio_neto",
                                                  "capital_trabajo", "d_ct", "residual", "flujo", "acumulado",
                                                  "seco_t", "humedo_t", "vendido_t")} for f in ind["filas"]],
    }


REFERENCIA = {"m_in": M_IN_MAX, "h_dia": 16.0, "turnos": 2, "inv_extra_usd": INV_2T_USD + 2000.0}
RANGOS_REF = {"h_dia": (12.0, 24.0), "m_in": (1000.0, 1440.0)}


def curva_precio(p, cambios, precios):
    """Payback (meses) en función del precio medio (USD/t) para una configuración."""
    out = []
    for pr in precios:
        q = dict(copy.deepcopy(p), **cambios)
        f = pr / precio_medio(q["mix"])
        q = aplicar(q, "precio", f, "factor")
        out.append(indicadores(q)["payback_meses"])
    return out


def _pb_van(p):
    ind = indicadores(p)
    return {"payback": ind["payback_meses"], "van": ind["van"], "flujo_anual": ind["anio3"]["flujo"]}


def calcular():
    tabla, esc = escenarios()
    inds = {n: indicadores(p) for n, p in esc.items()}
    sens = {n: sensibilidad(esc[n]) for n in ("realista", "optimista")}
    sens["referencia"] = sensibilidad(dict(copy.deepcopy(esc["optimista"]), **REFERENCIA), RANGOS_REF)
    precios = list(range(100, 801, 25))
    curvas = {cod: curva_precio(esc["realista"], cambios, precios) for cod, cambios in (
        ("Actual", {}), ("B", {"m_in": M_IN_MAX, "inv_extra_usd": INV_B}),
        ("A1+B", {"m_in": M_IN_MAX, "h_dia": 16.0, "turnos": 2, "inv_extra_usd": INV_2T_USD + INV_B}),
        ("A2+B", {"m_in": M_IN_MAX, "h_dia": 24.0, "turnos": 3, "inv_extra_usd": INV_2T_USD + INV_B}))}
    inverso = {}
    for n in ("conservador", "realista", "optimista"):
        p = esc[n]
        minimos = {}
        for cfg in CONFIGS:
            for N in (24, 36, 48, 60):
                m_in = capacidad_minima(p, cfg, N)
                minimos[f"{cfg[0]}_{N}"] = None if m_in is None else detalle_capacidad(p, cfg, m_in)
        inverso[n] = {"capacidad": {str(N): capacidad_necesaria(p, N) for N in (24, 36, 48, 60)},
                      "precio": {str(N): precio_necesario(p, N) for N in (24, 36, 48, 60)},
                      "minimos": minimos, "alternativas": alternativas(p)}
    return {
        "fecha": FECHA_REF, "dolar": DOLAR, "fuentes": FUENTES,
        "datos": {"M_IN": M_IN, "X_IN": X_IN, "X_OUT": X_OUT, "H_TURNO": H_TURNO, "DIAS_ANIO": DIAS_ANIO,
                  "M_IN_MAX": M_IN_MAX, "W_MAX": W_MAX, "Q_CASCARA": Q_CASCARA, "P_TGF": P_TGF, "P_TG2": P_TG2,
                  "KWH_ILUM": KWH_ILUM, "P_CONTRATADA": P_CONTRATADA, "PRECIO_PROY": PRECIO_PROY,
                  "VALOR_NPK": VALOR_NPK, "GRANEL_MERCADO": GRANEL_MERCADO, "COSTO_EMPLEADO": COSTO_EMPLEADO,
                  "FLETE_CASCARA_50": FLETE_CASCARA_50, "FLETE_CASCARA_100": FLETE_CASCARA_100,
                  "USD_KG_N": USD_KG_N, "USD_KG_P2O5": USD_KG_P2O5, "USD_KG_K2O": USD_KG_K2O,
                  "flete_20": flete_granos(20), "flete_40": flete_granos(40), "RESIDENCIA_MIN": RESIDENCIA_MIN},
        "supuestos": [list(f[:4]) + [f[4], f[5], f[6]] for f in tabla],
        "escenarios": {n: resumen(i) for n, i in inds.items()},
        "referencia": resumen(indicadores(dict(copy.deepcopy(esc["optimista"]), **REFERENCIA))),
        "variantes_referencia": {
            "tres_operarios": _pb_van(dict(copy.deepcopy(esc["optimista"]), **REFERENCIA, op_turno=3)),
            "supuestos_realistas_precio_proyecto": _pb_van(aplicar(dict(copy.deepcopy(esc["realista"]), **REFERENCIA),
                                                                   "precio", PRECIO_PROY / precio_medio(
                                                                       esc["realista"]["mix"]), "factor")),
        },
        "puente": puente(), "sensibilidad": sens, "inverso": inverso,
        "curva_precio": {"precios_usd_t": precios, "payback": curvas},
    }


def main():
    res = calcular()
    with open(os.path.join(AQUI, "economia.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    M = 1e6
    print(f"Referencia: {FECHA_REF}, dólar ${DOLAR:,.0f}")
    print(f"Precio NPK {VALOR_NPK:.1f} USD/t · granel de mercado {GRANEL_MERCADO:.1f} USD/t · proyecto {PRECIO_PROY:.1f}"
          f" · cáscara 50/100 km {FLETE_CASCARA_50:.1f}/{FLETE_CASCARA_100:.1f} USD/t · costo empleado "
          f"${COSTO_EMPLEADO:,.0f}/mes · Q cáscara {Q_CASCARA:.4f} kg/kg")
    for n, e in res["escenarios"].items():
        a2 = e["anio2"]
        pb = e["payback_meses"]
        print(f"\n== {n}: inversión ${e['inv_total'] / M:,.1f} M (USD {e['inv_total'] / DOLAR:,.0f}) + CT "
              f"${e['ct_regimen'] / M:,.1f} M; precio {e['precio_t'] / DOLAR:.1f} USD/t")
        print(f"   año 2: húmedo {a2['humedo_t']:,.0f} t, seco {a2['seco_t']:,.0f} t, vendido {a2['vendido_t']:,.0f} t;"
              f" ventas ${a2['ventas'] / M:,.1f} M, costos ${a2['costo_total'] / M:,.1f} M, EBITDA ${a2['ebitda'] / M:,.1f} M,"
              f" neto ${a2['beneficio_neto'] / M:,.1f} M, flujo ${a2['flujo'] / M:,.1f} M")
        print(f"   payback {'no recupera' if pb is None else f'{pb:.1f} meses'}; VAN ${e['van'] / M:,.1f} M; "
              f"TIR {e['tir']}; ROI anual {e['roi_anual']:.1f} %; costo prod {e['costo_prod_kg']:.0f} $/kg; "
              f"costo total {e['costo_total_kg']:.0f} $/kg; neto {e['neto_kg']:.0f} $/kg; PE op "
              f"{e['pe_operativo_t'] if e['pe_operativo_t'] is None else round(e['pe_operativo_t'])} t/año")
    print("\nPuente proyecto -> realista (USD/año):")
    for t, v in res["puente"]["pasos"]:
        print(f"  {v:>+12,.0f}  {t}")
    print(f"  = flujo realista año 2: {res['puente']['flujo_realista_usd']:,.0f} USD")
    for n, inv in res["inverso"].items():
        print(f"\nInverso {n}: capacidad kg/h {inv['capacidad']}; factor de precio {inv['precio']}")
        for k, d in inv["minimos"].items():
            if d:
                print(f"  mínimo {k}: {d['m_in']:,.0f} kg/h, {d['humedo_dia_kg']:,.0f} kg/día, {d['humedo_mes_t']:,.0f} t/mes húmedo,"
                      f" {d['vendido_anio_t']:,.0f} t/año vendidas, payback {d['payback']:.1f} m, líneas {d['lineas_necesarias']}")
            else:
                print(f"  mínimo {k}: no alcanzable")
        for a in inv["alternativas"]:
            pb = a["payback"]
            print(f"  {a['cod']:<6} +USD {a['inv_extra_usd']:>9,.0f}  {a['kg_h']:>5.0f} kg/h {a['h_dia']:>4.0f} h  "
                  f"vend {a['vendido_anio']:>6,.0f} t  flujo ${a['flujo_anual'] / M:>8,.1f} M/año  "
                  f"payback {'—' if pb is None else f'{pb:.0f} m'}  precio 60 m "
                  f"{'—' if a['precio_60'] is None else round(a['precio_60'])} USD/t")


if __name__ == "__main__":
    main()
