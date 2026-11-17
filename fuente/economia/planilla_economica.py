"""Planilla Excel del análisis económico, con fórmulas que recalculan (misma lógica que modelo_economico.py).

    python planilla_economica.py      # -> analisis_economico/Modelo_economico_Secadora_Guano.xlsx

Hojas: Léame · Supuestos (selector de escenario y todos los datos, con su tipo y fuente) · Inversión · Mes tipo
(régimen) · Flujo mensual (meses 0 a 180) · Impuestos (ganancias con quebrantos de 5 años) · Flujo anual ·
Indicadores (con el control contra el modelo en Python) · Escenarios, Sensibilidad e Inverso (valores del modelo).
Colores: azul = dato que se puede cambiar; negro = fórmula; verde = vínculo a otra hoja; fondo amarillo = supuesto
clave. Después de generarla se recalcula con LibreOffice para guardar los valores (ver tests/test_economia.py).
"""
from __future__ import annotations

import json
import os
import sys

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import modelo_economico as M  # noqa: E402

RAIZ = M.RAIZ
SALIDA = os.path.join(RAIZ, "analisis_economico", "Modelo_economico_Secadora_Guano.xlsx")
E = json.load(open(os.path.join(AQUI, "economia.json"), encoding="utf-8"))

AZUL, NEGRO, VERDE = Font(name="Arial", size=10, color="0000FF"), Font(name="Arial", size=10), \
    Font(name="Arial", size=10, color="008000")
NEGRITA = Font(name="Arial", size=10, bold=True)
TITULO = Font(name="Arial", size=13, bold=True)
CHICA = Font(name="Arial", size=9, italic=True, color="555555")
AMARILLO = PatternFill("solid", fgColor="FFFF00")
CAB = PatternFill("solid", fgColor="DCE3EA")
fino = Side(style="thin", color="999999")
BORDE = Border(left=fino, right=fino, top=fino, bottom=fino)
F_ARS = '"$" #,##0;[Red]-"$" #,##0;"-"'
F_USD = '"USD" #,##0;[Red]-"USD" #,##0;"-"'
F_NUM = '#,##0;[Red]-#,##0;"-"'
F_DEC = '#,##0.00;[Red]-#,##0.00;"-"'
F_PCT = '0.0%;[Red]-0.0%;"-"'
F_MES = '0.0'

wb = Workbook()


def nombre(n, hoja, celda):
    ref = f"'{hoja}'!${celda[0] if celda[1].isdigit() else celda[:2]}${celda[1:] if celda[1].isdigit() else celda[2:]}"
    wb.defined_names[n] = DefinedName(n, attr_text=ref)


def abs_ref(col, fila):
    return f"${col}${fila}"


def put(ws, celda, valor, fuente=NEGRO, fmt=None, fill=None, borde=True, wrap=False):
    c = ws[celda]
    c.value = valor
    c.font = fuente
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if borde:
        c.border = BORDE
    c.alignment = Alignment(vertical="top", wrap_text=wrap)
    return c


def encabezado(ws, fila, textos, anchos=None):
    for j, t in enumerate(textos, 1):
        c = ws.cell(row=fila, column=j, value=t)
        c.font = NEGRITA
        c.fill = CAB
        c.border = BORDE
        c.alignment = Alignment(wrap_text=True, vertical="center")
    if anchos:
        for j, w in enumerate(anchos, 1):
            ws.column_dimensions[get_column_letter(j)].width = w


# =============================================================================== Léame
ws = wb.active
ws.title = "Léame"
ws["A1"] = "Modelo económico – Secadora de guano de gallina 8 t/día (Rev. F)"
ws["A1"].font = TITULO
lineas = [
    f"Pesos constantes de {M.FECHA_REF}, sin IVA. Dólar BNA vendedor ${M.DOLAR:,.0f} (16/11/2026).".replace(",", "."),
    "Cómo se usa: en la hoja «Supuestos» se elige el escenario (celda C4: 1 conservador, 2 realista, 3 optimista) y "
    "se pueden cambiar los datos en azul. Todo lo demás se recalcula: inversión, mes tipo, flujo mensual, impuestos, "
    "flujo anual e indicadores.",
    "Colores: azul = dato que se puede cambiar · negro = fórmula · verde = vínculo a otra hoja · fondo amarillo = "
    "supuesto clave (precio, fracción vendida, flete, cáscara).",
    "Tipo de dato: R = del proyecto (diseño, no medido) · V = verificado con fuente y fecha · E = estimación propia "
    "con datos R o V · H = hipótesis (no hay dato publicado).",
    "Para ver la referencia que recupera la inversión en 48 meses (2 turnos a 1.440 kg/h con los precios del proyecto): "
    "elegir el escenario 3 y, en la columna Optimista, poner alimentación 1.440 kg/h, 16 h/día, 2 turnos e inversión "
    "adicional USD 32.000.",
    "La hoja «Indicadores» compara cada resultado con el del modelo en Python (fuente/economia/modelo_economico.py); "
    "con los datos sin tocar, la diferencia es cero. «Escenarios», «Sensibilidad» e «Inverso» son valores del modelo "
    "en Python (las búsquedas por bisección no se hacen con fórmulas).",
    "No incluye: IVA (se supone recuperado), financiamiento (todo con capital propio), inflación diferencial (se "
    "estudia en el informe, sensibilidad), ni el valor residual de los equipos.",
]
for i, t in enumerate(lineas, 3):
    c = ws.cell(row=i, column=1, value=t)
    c.font = NEGRO
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[i].height = 42
ws.column_dimensions["A"].width = 120
ws.cell(row=len(lineas) + 4, column=1, value="Fuentes").font = NEGRITA
for i, (k, v) in enumerate(M.FUENTES.items(), len(lineas) + 5):
    c = ws.cell(row=i, column=1, value=f"[{k}] {v}")
    c.font = Font(name="Arial", size=9)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[i].height = 38

# =============================================================================== Supuestos
ws = wb.create_sheet("Supuestos")
S = "Supuestos"
ws["A1"] = "Supuestos del modelo"
ws["A1"].font = TITULO
ws["A2"] = f"Valores a {M.FECHA_REF}. La columna «Activo» toma el escenario elegido en C4."
ws["A2"].font = CHICA
put(ws, "A4", "Escenario activo (1 = conservador, 2 = realista, 3 = optimista)", NEGRITA)
put(ws, "C4", 2, AZUL, fill=AMARILLO)
nombre("ESC", S, "C4")
encabezado(ws, 6, ["Parámetro", "Unidad", "Tipo", "Conservador", "Realista", "Optimista", "Activo", "Clave",
                   "Nota / fuente"], [52, 9, 7, 13, 13, 13, 13, 14, 70])
tabla, esc = M.escenarios()
notas = {
    "m_in": "Diseño: 1.000 kg/h (8 t en 8 h). El secador llega a 1.440 kg/h con aire a 135 °C (modelo térmico).",
    "X_in": "Proyecto: 72 % (INTA, 70 a 75 %); el lazo de humedad admite 65 a 78 %.",
    "X_out": "Especificación del producto (15 %).",
    "h_dia": "Un turno de 8 h de alimentación (más 1 h de arranque y vaciado para la energía).",
    "dias_anio": "Proyecto: 250 días/año. Conservador 240 (20/mes), optimista 264 (22/mes).",
    "disp": "Proyecto: objetivo de disponibilidad > 92 % (plan de mantenimiento).",
    "merma": "Hipótesis: rechazo de zaranda (plumas, cáscara de huevo), polvo no recuperado, manipuleo.",
    "vendido": "Hipótesis: no hay contratos ni estudio de mercado; no se supone que se vende todo.",
    "cascara": "Proyecto: USD 25/t. Estimado: flete de cáscara por volumen (10 t por viaje) a 50 y 100 km + USD 5/t en molino.",
    "flete_guano": "Estimado con tarifa de referencia de granos (CATAC 01/2026 llevada a FETRA 11/2026): 20 km ≈ USD 9,9/t, 40 km ≈ USD 12,5/t. Optimista: lo pagan las granjas.",
    "tarifa": "Factor sobre la T3 BT estimada por el proyecto (10/2026, a confirmar con la LAR).",
    "op_turno": "Presupuesto: 3 por turno. Informe: 2 por turno (inconsistencia del proyecto).",
    "adm": "Hipótesis: 1 persona de administración y ventas (no estaba en el proyecto).",
    "comerc": "Hipótesis: comisiones, distribución bonificada, publicidad y muestras.",
    "mant": "Proyecto: 3 % sobre equipos. Se aplica sobre equipos + pala; 70 % fijo y 30 % según horas.",
    "f_inv": "Precisión del presupuesto ± 25 %: conservador +15 %, optimista −5 %.",
    "tierra": "Hipótesis: no hay precio publicado del Parque Industrial (quinta en Paraná ≈ USD 2,7/m²).",
    "pala": "Avisos 11/2026 de cargadoras usadas de ≈ 1 m³ (USD 32.000 a 44.000).",
}
filas_param = []
for clave, desc, unidad, tipo, c, r, o in tabla:
    if clave == "mix":
        canales = [("granel", "f_gr", "pr_gr", "granel"), ("bolsas 25 kg", "f_b25", "pr_b25", "bolsa de 25 kg"),
                   ("bolsas chicas 1-2-5 kg", "f_bch", "pr_bch", "bolsas chicas de 1, 2 y 5 kg")]
        for canal, kf, kp, rot in canales:
            vals_f = [d.get(canal, (0, 0))[0] for d in (c, r, o)]
            vals_p = [d.get(canal, (0, 0))[1] for d in (c, r, o)]
            filas_param.append((kf, f"Fracción de la venta en {rot}", "%", "H", *vals_f,
                                "Mezcla de canales del escenario (la del optimista es la del proyecto)."))
            filas_param.append((kp, f"Precio ex planta, {rot}", "USD/t", "V/E/H", *vals_p,
                                {"granel": "Conservador: USD 30/t al 50 % de MS (2024) llevado a 85 % de MS, menos flete. "
                                           "Realista: valor de los nutrientes N-P-K a precios de urea, MAP y KCl (11/2026).",
                                 "bolsas 25 kg": "Hipótesis: no se encontró precio mayorista; minorista $ 75.000 la bolsa "
                                                 "con IVA. Proyecto: USD 250/t.",
                                 "bolsas chicas 1-2-5 kg": "Proyecto: USD 600/t."}[canal]))
        continue
    filas_param.append((clave, desc, unidad, tipo, c, r, o, notas.get(clave, "")))
config = [
    ("turnos", "Turnos por día", "u", "R", 1, 1, 1, "Configuración: 2 o 3 turnos para estudiar ampliaciones."),
    ("lineas", "Secadoras en paralelo", "u", "R", 1, 1, 1, "Alternativa D: 2."),
    ("inv_extra", "Inversión adicional en equipos (ampliación)", "USD", "R/E", 0, 0, 0,
     "Proyecto: USD 30.000 para el 2.° turno; tolva de retención mayor para 1.440 kg/h: USD 2.000 (E)."),
    ("inv_extra_obra", "Inversión adicional en obra civil (ampliación)", "USD", "E", 0, 0, 0, ""),
    ("op_extra", "Operarios adicionales (fuera de los turnos)", "u", "H", 0, 0, 0, ""),
    ("f_tgf", "Factor de potencia del TGF (máquina más grande)", "—", "E", 1, 1, 1, "Alternativa C: 1,8."),
    ("p_extra", "Potencia contratada adicional", "kW", "E", 0, 0, 0, ""),
    ("f_cap", "Factor de capacidad térmica (máquina más grande)", "—", "E", 1, 1, 1, "Alternativa C: 2."),
    ("tope", "Limitar el caudal a la capacidad térmica (1 = sí)", "—", "R", 1, 1, 1,
     "El secador no evapora más de 966 kg/h de agua por línea (1.440 kg/h al 72 %)."),
]
PCT = {"X_in", "X_out", "disp", "merma", "vendido", "comerc", "mant", "f_gr", "f_b25", "f_bch"}
CLAVE_FILA = {}
fila = 7
for clave, desc, unidad, tipo, c, r, o, nota in filas_param + config:
    fmt = F_PCT if clave in PCT else (F_DEC if clave in ("cascara", "flete_guano", "tarifa", "f_inv", "tierra",
                                                          "pr_gr", "pr_b25", "pr_bch", "f_tgf", "f_cap") else F_NUM)
    put(ws, f"A{fila}", desc)
    put(ws, f"B{fila}", unidad)
    put(ws, f"C{fila}", tipo)
    clave_fill = AMARILLO if clave in ("pr_gr", "pr_b25", "pr_bch", "vendido", "flete_guano", "cascara") else None
    for col, v in zip("DEF", (c, r, o)):
        put(ws, f"{col}{fila}", v, AZUL, fmt, clave_fill)
    put(ws, f"G{fila}", f"=CHOOSE(ESC,D{fila},E{fila},F{fila})", NEGRO, fmt)
    put(ws, f"H{fila}", f"p_{clave}", CHICA)
    put(ws, f"I{fila}", nota, Font(name="Arial", size=9), wrap=True)
    nombre(f"p_{clave}", S, f"G{fila}")
    CLAVE_FILA[clave] = fila
    fila += 1

fila += 1
put(ws, f"A{fila}", "Constantes, datos del proyecto y precios de referencia", NEGRITA, borde=False)
fila += 1
encabezado(ws, fila, ["Dato", "Unidad", "Tipo", "Valor", "", "", "", "Nombre", "Fuente / cálculo"])
fila += 1
d = E["datos"]
constantes = [
    ("DOLAR", "Dólar BNA vendedor (16/11/2026)", "$/USD", "V", M.DOLAR, F_DEC, "BNA"),
    ("W_MAX", "Agua que evapora el secador como máximo (1.440 kg/h de 72 % a 15 %)", "kg/h", "R", M.W_MAX, F_DEC,
     "Modelo térmico, apartado 6.7"),
    ("Q_CASC", "Cáscara por kg de agua evaporada (419 t/año para 1.341 t de agua)", "kg/kg", "R", M.Q_CASCARA,
     '0.0000', "Modelo térmico Rev. F, aire ajustado al 15 %"),
    ("H_ARR", "Horas de arranque y vaciado por turno (ventiladores y bandas sin carga)", "h", "R", M.H_ARRANQUE,
     F_DEC, "Estudio de fatiga: 9 h de servicio por día"),
    ("P_TGF", "Demanda del TGF (66,9 kW instalados × 0,8)", "kW", "R", M.P_TGF, F_DEC, "Informe, apartado 11"),
    ("P_TG2", "Demanda del TG2 sin las cargas del biogás", "kW", "E", M.P_TG2, F_DEC,
     "resultados.json: 25,1 kW − 0,55 × 22,85 kW del TS-BIO"),
    ("KWH_ILUM", "Iluminación exterior (12 h/día, 365 días)", "kWh/año", "R", M.KWH_ILUM, F_NUM, "resultados.json"),
    ("P_CONTR", "Potencia contratada (sin biogás)", "kW", "E", M.P_CONTRATADA, F_NUM,
     "Balance del proyecto sin G1 (91,6 kW) menos el TS-BIO"),
    ("T_FIJO", "Cargo fijo T3 BT", "$/mes", "R", M.TARIFA["cargo_fijo_mes"], F_ARS, "Proyecto (estimado, a confirmar)"),
    ("T_POT", "Cargo por potencia contratada", "$/kW·mes", "R", M.TARIFA["potencia_kw_mes"], F_ARS, "Proyecto"),
    ("T_ENER", "Cargo por energía", "$/kWh", "R", M.TARIFA["energia_kwh"], F_DEC, "Proyecto"),
    ("BOLSA_25", "Bolsa de rafia laminada de 25 kg", "$/u", "V", M.BOLSA_25, F_DEC, "Mercado Libre 11/2026"),
    ("BOLSA_CH", "Bolsa chica (1, 2 o 5 kg)", "USD/u", "R", M.BOLSA_CHICA_USD, F_DEC, "Proyecto"),
    ("SALARIO", "Sueldo de referencia: operario calificado UOM rama 17 (200 h)", "$/mes", "V", M.SALARIO_REF, F_ARS,
     "iProfesional, El Cronista (11/2026)"),
    ("CARGAS", "Contribuciones patronales, ART y seguro de vida", "%", "H", M.CARGAS, F_PCT, "Hipótesis"),
    ("HONOR", "Honorarios contables, legales y técnicos", "$/mes", "H", M.HONORARIOS, F_ARS, "Hipótesis"),
    ("IIBB", "Ingresos brutos (industria, Entre Ríos)", "%", "V", M.IIBB, F_PCT, "Fuentes secundarias, a confirmar"),
    ("DEBCRED", "Impuesto a los débitos y créditos (cada movimiento)", "%", "V", M.DEB_CRED, '0.00%', "Ley 25.413"),
    ("GAN_T1", "Ganancias sociedades: fin del tramo del 25 %", "$", "V", M.GAN_T1, F_ARS, "ARCA, escala 2026"),
    ("GAN_T2", "Ganancias sociedades: fin del tramo del 30 %", "$", "V", M.GAN_T2, F_ARS, "ARCA, escala 2026"),
    ("OTROS_USD", "Ácido, agua, gasoil de la pala, monitoreos, H&S (1 turno)", "USD/año", "R", float(M.OTROS_USD),
     F_NUM, "Proyecto"),
    ("SEG_PCT", "Seguros, inmobiliario y tasas (sobre la inversión sin terreno)", "%/año", "R", 0.01, F_PCT, "Proyecto"),
    ("D_COBRO", "Plazo de cobro", "días", "H", M.DIAS_COBRO, F_NUM, "Hipótesis"),
    ("D_STOCK", "Existencias (sobre los costos variables de producción)", "días", "H", M.DIAS_STOCK, F_NUM, "Hipótesis"),
    ("D_PAGO", "Plazo de pago a proveedores", "días", "H", M.DIAS_PAGO, F_NUM, "Hipótesis"),
    ("R1_HASTA", "Puesta en marcha: último mes al 50 %", "mes", "H", M.RAMPA[0][0], F_NUM, "Hipótesis"),
    ("R1_F", "Puesta en marcha: caudal de los meses 1 a 3", "%", "H", M.RAMPA[0][1], F_PCT, "Hipótesis"),
    ("R2_HASTA", "Puesta en marcha: último mes al 80 %", "mes", "H", M.RAMPA[1][0], F_NUM, "Hipótesis"),
    ("R2_F", "Puesta en marcha: caudal de los meses 4 a 6", "%", "H", M.RAMPA[1][1], F_PCT, "Hipótesis"),
    ("VIDA_OBRA", "Vida útil impositiva: obra civil", "años", "E", M.AMORT_ANIOS["obra"], F_NUM, "Práctica habitual (2 %/año)"),
    ("VIDA_EQ", "Vida útil impositiva: equipos", "años", "E", M.AMORT_ANIOS["equipos"], F_NUM, "Práctica habitual"),
    ("VIDA_PALA", "Vida útil impositiva: pala cargadora", "años", "E", M.AMORT_ANIOS["pala"], F_NUM, "Práctica habitual"),
    ("VIDA_INT", "Amortización de ingeniería, habilitaciones y puesta en marcha", "años", "E",
     M.AMORT_ANIOS["intangible"], F_NUM, "Práctica habitual"),
    ("TASA_REAL", "Tasa de descuento real anual", "%", "R", M.TASA_REAL, F_PCT, "Evaluación del proyecto (10 %)"),
    ("LOTE", "Superficie del lote", "m²", "R", float(M.LOTE_M2), F_NUM, "Informe, apartado 16.3"),
    ("IMPREV", "Imprevistos del presupuesto", "%", "R", M.IMPREV, F_PCT, "presupuesto.py"),
    ("PUESTA", "Puesta en marcha, módulo piloto y capacitación (sobre el proyecto)", "%", "H", 0.01, F_PCT, "Hipótesis"),
    ("H_REF", "Horas de referencia por año (1 turno: 8 h × 250 d)", "h/año", "R", M.H_TURNO * M.DIAS_ANIO, F_NUM,
     "Para escalar mantenimiento y otros insumos con las horas"),
]
for n, desc, unidad, tipo, v, fmt, fuente in constantes:
    put(ws, f"A{fila}", desc)
    put(ws, f"B{fila}", unidad)
    put(ws, f"C{fila}", tipo)
    put(ws, f"D{fila}", v, AZUL, fmt)
    put(ws, f"H{fila}", n, CHICA)
    put(ws, f"I{fila}", fuente, Font(name="Arial", size=9), wrap=True)
    nombre(n, S, f"D{fila}")
    fila += 1
put(ws, f"A{fila}", "Costo laboral por persona (13 sueldos con aguinaldo y cargas)")
put(ws, f"B{fila}", "$/mes")
put(ws, f"C{fila}", "E")
put(ws, f"D{fila}", "=SALARIO*13/12*(1+CARGAS)", NEGRO, F_ARS)
put(ws, f"H{fila}", "COSTO_EMP", CHICA)
nombre("COSTO_EMP", S, f"D{fila}")
fila += 1
put(ws, f"A{fila}", "Precio medio ponderado del escenario activo")
put(ws, f"B{fila}", "USD/t")
put(ws, f"C{fila}", "E")
put(ws, f"D{fila}", "=p_f_gr*p_pr_gr+p_f_b25*p_pr_b25+p_f_bch*p_pr_bch", NEGRO, F_DEC)
put(ws, f"H{fila}", "PRECIO_USD", CHICA)
nombre("PRECIO_USD", S, f"D{fila}")
fila += 1
put(ws, f"A{fila}", "Envases por tonelada vendida (bolsas de 25 kg; las chicas van además en bolsas de 25 kg)")
put(ws, f"B{fila}", "$/t")
put(ws, f"C{fila}", "E")
put(ws, f"D{fila}", "=p_f_b25*40*BOLSA_25+p_f_bch*(40*BOLSA_25+1000/2.2*BOLSA_CH*DOLAR)", NEGRO, F_ARS)
put(ws, f"H{fila}", "ENVASE_T", CHICA)
nombre("ENVASE_T", S, f"D{fila}")
ws.freeze_panes = "A7"

# =============================================================================== Inversión
ws = wb.create_sheet("Inversión")
I = "Inversión"
ws["A1"] = "Inversión inicial (planta sin biogás) – USD y pesos"
ws["A1"].font = TITULO
ws["A2"] = ("Ítems del presupuesto del proyecto (presupuesto.json, precios al 23/10/2026) multiplicados por el factor "
            "del escenario; los no contemplados se suman abajo. Fracciones de obra civil e intangible para amortizar.")
ws["A2"].font = CHICA
encabezado(ws, 4, ["Cód.", "Rubro", "Descripción", "Cant.", "Unid.", "USD unit. (proyecto)", "USD total (proyecto)",
                   "Fracción obra civil", "Fracción intangible", "USD del escenario", "Tipo"],
           [6, 16, 70, 8, 6, 13, 14, 10, 10, 15, 6])
f0 = 5
for i, cod in enumerate(M.SIN_BIOGAS):
    r = f0 + i
    _c, rub, desc, q, u, pu, _tot, *_ = M.FILAS[cod]
    put(ws, f"A{r}", cod)
    put(ws, f"B{r}", rub)
    put(ws, f"C{r}", desc, wrap=False)
    put(ws, f"D{r}", q, AZUL, F_NUM)
    put(ws, f"E{r}", u)
    put(ws, f"F{r}", pu, AZUL, F_NUM)
    put(ws, f"G{r}", f"=D{r}*F{r}", NEGRO, F_NUM)
    put(ws, f"H{r}", M.OBRA.get(cod, 0.0), AZUL, F_PCT)
    put(ws, f"I{r}", M.INTANGIBLE.get(cod, 0.0), AZUL, F_PCT)
    put(ws, f"J{r}", f"=G{r}*p_f_inv", NEGRO, F_NUM)
    put(ws, f"K{r}", "R")
f1 = f0 + len(M.SIN_BIOGAS) - 1
r = f1 + 1
filas_inv = [
    ("Subtotal del proyecto (sin biogás)", f"=SUM(J{f0}:J{f1})", "SUB_INV"),
    ("Imprevistos (7 %)", f"=IMPREV*J{r}", None),
    ("Inversión del proyecto (sin biogás)", f"=J{r}+J{r + 1}", "INV_PROY"),
]
for k, (rot, fml, n) in enumerate(filas_inv):
    put(ws, f"C{r + k}", rot, NEGRITA)
    put(ws, f"J{r + k}", fml, NEGRITA, F_NUM)
    if n:
        nombre(n, I, f"J{r + k}")
r += len(filas_inv) + 1
put(ws, f"C{r}", "Costos no contemplados en el presupuesto del proyecto", NEGRITA, borde=False)
r += 1
extras = [
    ("Terreno: lote de 9.120 m² (hipótesis de precio por m²)", "=LOTE*p_tierra", "TERRENO_USD", "H"),
    ("Pala cargadora frontal usada de ≈ 1 m³ (la usa el operario de campo; no figura en el presupuesto)", "=p_pala",
     "PALA_USD", "V"),
    ("Puesta en marcha, ensayos con el módulo piloto (Rev. F) y capacitación (1 % del proyecto)", "=PUESTA*INV_PROY",
     "PUESTA_USD", "H"),
    ("Impuesto a los débitos bancarios sobre los pagos de la inversión (0,6 %)", "=DEBCRED*INV_PROY", "DEB_INV_USD", "V"),
    ("Inversión adicional de la ampliación: equipos", "=p_inv_extra", "EXTRA_EQ_USD", "R/E"),
    ("Inversión adicional de la ampliación: obra civil", "=p_inv_extra_obra", "EXTRA_OBRA_USD", "E"),
]
r_ext0 = r
for rot, fml, n, tipo in extras:
    put(ws, f"C{r}", rot)
    put(ws, f"J{r}", fml, VERDE, F_NUM)
    put(ws, f"K{r}", tipo)
    nombre(n, I, f"J{r}")
    r += 1
put(ws, f"C{r}", "INVERSIÓN INICIAL TOTAL (USD)", NEGRITA)
put(ws, f"J{r}", f"=INV_PROY+SUM(J{r_ext0}:J{r - 1})", NEGRITA, F_NUM, AMARILLO)
nombre("INV_USD", I, f"J{r}")
r += 1
put(ws, f"C{r}", "INVERSIÓN INICIAL TOTAL ($ de noviembre de 2026)", NEGRITA)
put(ws, f"J{r}", "=INV_USD*DOLAR", NEGRITA, F_ARS, AMARILLO)
nombre("INV_ARS", I, f"J{r}")
r += 2
put(ws, f"C{r}", "Clases para amortizar y para el mantenimiento (USD, con los imprevistos repartidos)", NEGRITA,
    borde=False)
r += 1
clases = [
    ("Obra civil (50 años)", f"=SUMPRODUCT(J{f0}:J{f1},H{f0}:H{f1})*(1+IMPREV)+EXTRA_OBRA_USD", "CL_OBRA"),
    ("Equipos (10 años)", f"=SUMPRODUCT(J{f0}:J{f1},1-H{f0}:H{f1}-I{f0}:I{f1})*(1+IMPREV)+EXTRA_EQ_USD", "CL_EQ"),
    ("Pala cargadora (5 años)", "=PALA_USD", "CL_PALA"),
    ("Ingeniería, habilitaciones, puesta en marcha e impuesto (5 años)",
     f"=SUMPRODUCT(J{f0}:J{f1},I{f0}:I{f1})*(1+IMPREV)+PUESTA_USD+DEB_INV_USD", "CL_INT"),
    ("Terreno (no se amortiza)", "=TERRENO_USD", "CL_TERRENO"),
]
r_cl0 = r
for rot, fml, n in clases:
    put(ws, f"C{r}", rot)
    put(ws, f"J{r}", fml, NEGRO, F_NUM)
    nombre(n, I, f"J{r}")
    r += 1
put(ws, f"C{r}", "Control: suma de clases − inversión total (debe dar 0)")
put(ws, f"J{r}", f"=SUM(J{r_cl0}:J{r - 1})-INV_USD", NEGRO, F_DEC)
nombre("CTRL_CLASES", I, f"J{r}")
ws.freeze_panes = "A5"

# =============================================================================== Mes tipo
ws = wb.create_sheet("Mes tipo")
T = "Mes tipo"
ws["A1"] = "Mes tipo de régimen (caudal pleno) – producción, ventas y costos"
ws["A1"].font = TITULO
ws["A2"] = "Fórmulas del balance de masa y de los costos; el flujo mensual escala lo que depende del caudal durante la puesta en marcha."
ws["A2"].font = CHICA
encabezado(ws, 4, ["Concepto", "Valor", "Unidad", "Fórmula / criterio"], [58, 18, 10, 80])
mt = [
    # (nombre, rótulo, fórmula, unidad, formato, criterio)
    ("MT_DIAS", "Días de operación por mes", "=p_dias_anio/12", "d", F_DEC, "días por año / 12"),
    ("MT_HCARGA", "Horas de alimentación efectivas", "=p_h_dia*MT_DIAS*p_disp", "h/mes", F_DEC,
     "horas por día × días × disponibilidad"),
    ("MT_FW", "Fracción de agua evaporada por kg de guano", "=1-(1-p_X_in)/(1-p_X_out)", "kg/kg", "0.0000",
     "1 − (1 − X_in) / (1 − X_out)"),
    ("MT_MIN", "Caudal de guano húmedo (todas las líneas)",
     "=IF(p_tope=1,MIN(p_m_in*p_lineas,W_MAX*p_lineas*p_f_cap/MT_FW),p_m_in*p_lineas)", "kg/h", F_DEC,
     "limitado por la evaporación máxima del secador"),
    ("MT_HUM", "Guano húmedo procesado", "=MT_MIN*MT_HCARGA/1000", "t/mes", F_DEC, "m_in × h / 1000"),
    ("MT_SECO", "Producto seco al 15 % obtenido", "=MT_HUM*(1-p_X_in)/(1-p_X_out)", "t/mes", F_DEC,
     "m_out = m_in (1 − X_in) / (1 − X_out): el sólido seco se conserva"),
    ("MT_AGUA", "Agua evaporada", "=MT_HUM-MT_SECO", "t/mes", F_DEC, "W = m_in − m_out"),
    ("MT_COMERC", "Producto comerciable (descontadas las mermas)", "=MT_SECO*(1-p_merma)", "t/mes", F_DEC, ""),
    ("MT_VEND", "Producto vendido", "=MT_COMERC*p_vendido", "t/mes", F_DEC, "comerciable × fracción vendida"),
    ("MT_VENTAS", "Ventas", "=MT_VEND*PRECIO_USD*DOLAR", "$/mes", F_ARS, "vendido × precio medio × dólar"),
    ("MT_HMARCHA", "Horas de marcha (carga + arranque y vaciado)", "=(p_h_dia*p_disp+H_ARR*p_turnos)*MT_DIAS", "h/mes",
     F_DEC, ""),
    ("MT_KW", "Potencia media demandada", "=P_TGF*p_lineas*p_f_tgf+P_TG2", "kW", F_DEC, "TGF + TG2 (sin biogás)"),
    ("MT_KWH", "Energía eléctrica", "=MT_KW*MT_HMARCHA+KWH_ILUM/12", "kWh/mes", F_NUM, "kW × h + iluminación"),
    ("MT_CASC_T", "Cáscara de arroz", "=MT_AGUA*Q_CASC", "t/mes", F_DEC, "agua evaporada × consumo específico"),
    ("C_CASC", "Costo de la cáscara", "=MT_CASC_T*p_cascara*DOLAR", "$/mes", F_ARS, ""),
    ("C_EVAR", "Energía: cargo variable", "=MT_KWH*T_ENER*p_tarifa", "$/mes", F_ARS, ""),
    ("C_EFIJ", "Energía: cargo fijo y potencia contratada", "=(T_FIJO+T_POT*(P_CONTR+p_p_extra))*p_tarifa", "$/mes",
     F_ARS, ""),
    ("C_FLETE", "Flete del guano húmedo", "=MT_HUM*p_flete_guano*DOLAR", "$/mes", F_ARS, ""),
    ("C_ENV", "Envases", "=MT_VEND*ENVASE_T", "$/mes", F_ARS, ""),
    ("C_OTROS", "Otros insumos (ácido, agua, gasoil de la pala, monitoreos, H&S)",
     "=OTROS_USD*DOLAR/12*(0.4+0.6*p_h_dia*p_dias_anio/H_REF)", "$/mes", F_ARS, "40 % fijo, 60 % según horas"),
    ("C_MANT", "Mantenimiento y repuestos", "=p_mant*(CL_EQ+CL_PALA)*DOLAR/12*(0.7+0.3*p_h_dia*p_dias_anio/H_REF)",
     "$/mes", F_ARS, "sobre equipos + pala; 70 % fijo, 30 % según horas"),
    ("MT_OPER", "Operarios", "=p_op_turno*p_turnos+p_op_extra", "u", F_NUM, ""),
    ("C_MO", "Mano de obra operativa", "=MT_OPER*COSTO_EMP", "$/mes", F_ARS, ""),
    ("C_ADM", "Administración, ventas y honorarios", "=p_adm*COSTO_EMP+HONOR", "$/mes", F_ARS, ""),
    ("C_SEG", "Seguros, inmobiliario y tasas", "=SEG_PCT*(INV_USD-TERRENO_USD)*DOLAR/12", "$/mes", F_ARS, ""),
    ("C_COMERC", "Comercialización", "=p_comerc*MT_VENTAS", "$/mes", F_ARS, ""),
    ("C_IIBB", "Ingresos brutos", "=IIBB*MT_VENTAS", "$/mes", F_ARS, ""),
    ("MT_PROD", "Costo de producción", "=C_CASC+C_EVAR+C_EFIJ+C_FLETE+C_ENV+C_OTROS+C_MANT+C_MO", "$/mes", F_ARS, ""),
    ("MT_ESTR", "Gastos de estructura", "=C_ADM+C_SEG", "$/mes", F_ARS, ""),
    ("C_DEB", "Impuesto a los débitos y créditos", "=DEBCRED*(MT_VENTAS+MT_PROD+MT_ESTR+C_COMERC+C_IIBB)", "$/mes", F_ARS,
     "0,6 % de los cobros y de los pagos"),
    ("MT_TOTAL", "Costo total (sin amortizaciones)", "=MT_PROD+MT_ESTR+C_COMERC+C_IIBB+C_DEB", "$/mes", F_ARS, ""),
    ("MT_EBITDA", "Resultado operativo antes de amortizaciones (EBITDA)", "=MT_VENTAS-MT_TOTAL", "$/mes", F_ARS, ""),
    # partes para escalar con la puesta en marcha
    ("MT_CVAR", "Costos que siguen al caudal (cáscara, flete, envases)", "=C_CASC+C_FLETE+C_ENV", "$/mes", F_ARS, ""),
    ("MT_COMV", "Costos que siguen a las ventas (comercialización e IIBB)", "=C_COMERC+C_IIBB", "$/mes", F_ARS, ""),
    ("MT_FIJOS", "Costos que no dependen del caudal", "=C_EVAR+C_EFIJ+C_OTROS+C_MANT+C_MO+C_ADM+C_SEG", "$/mes",
     F_ARS, ""),
    ("AM_OBRA", "Amortización mensual: obra civil", "=CL_OBRA*DOLAR/VIDA_OBRA/12", "$/mes", F_ARS, ""),
    ("AM_EQ", "Amortización mensual: equipos", "=CL_EQ*DOLAR/VIDA_EQ/12", "$/mes", F_ARS, ""),
    ("AM_PALA", "Amortización mensual: pala", "=CL_PALA*DOLAR/VIDA_PALA/12", "$/mes", F_ARS, ""),
    ("AM_INT", "Amortización mensual: intangibles", "=CL_INT*DOLAR/VIDA_INT/12", "$/mes", F_ARS, ""),
]
for i, (n, rot, fml, unidad, fmt, crit) in enumerate(mt, 5):
    put(ws, f"A{i}", rot)
    put(ws, f"B{i}", fml, NEGRO, fmt)
    put(ws, f"C{i}", unidad)
    put(ws, f"D{i}", crit, Font(name="Arial", size=9))
    nombre(n, T, f"B{i}")
ws.freeze_panes = "A5"

# =============================================================================== Impuestos (antes del flujo: el flujo lo usa)
wsI = wb.create_sheet("Impuestos")
# =============================================================================== Flujo mensual
ws = wb.create_sheet("Flujo mensual")
FM = "Flujo mensual"
ws["A1"] = "Flujo de caja mensual ($ de noviembre de 2026). Mes 0: inversión; meses 1 a 180: operación."
ws["A1"].font = TITULO
cols = ["Mes", "Año", "Caudal (fracción)", "Guano húmedo (t)", "Producto seco (t)", "Vendido (t)", "Ventas ($)",
        "Costos que siguen al caudal ($)", "Comercialización e IIBB ($)", "Costos fijos ($)", "Débitos y créditos ($)",
        "Costo total ($)", "EBITDA ($)", "Amortización ($)", "EBIT ($)", "Compras ($)", "Capital de trabajo ($)",
        "Variación del capital de trabajo ($)", "Ganancias pagado ($)", "Valor residual ($)", "Flujo de caja ($)",
        "Flujo operativo, sin residual ($)", "Acumulado operativo ($)", "Factor de descuento",
        "Acumulado descontado ($)", "Payback (mes)", "Payback descontado (mes)"]
encabezado(ws, 3, cols, [6, 6, 9, 11, 11, 10, 15, 15, 14, 15, 13, 15, 15, 14, 15, 14, 15, 15, 14, 15, 15, 15, 16, 10,
                         16, 10, 10])
R0 = 4                                   # fila del mes 0
N = M.MESES
for k in range(0, N + 1):
    r = R0 + k
    put(ws, f"A{r}", k, NEGRO, F_NUM)
    if k == 0:
        put(ws, f"U{r}", "=-INV_ARS", VERDE, F_ARS)
        put(ws, f"V{r}", f"=U{r}", NEGRO, F_ARS)
        put(ws, f"W{r}", f"=V{r}", NEGRO, F_ARS)
        put(ws, f"X{r}", 1, NEGRO, '0.0000')
        put(ws, f"Y{r}", f"=V{r}*X{r}", NEGRO, F_ARS)
        put(ws, f"Q{r}", 0, NEGRO, F_ARS)
        continue
    p = r - 1
    put(ws, f"B{r}", f"=INT((A{r}-1)/12)+1", NEGRO, F_NUM)
    put(ws, f"C{r}", f"=IF(A{r}<=R1_HASTA,R1_F,IF(A{r}<=R2_HASTA,R2_F,1))", NEGRO, F_PCT)
    put(ws, f"D{r}", f"=MT_HUM*C{r}", VERDE, F_DEC)
    put(ws, f"E{r}", f"=MT_SECO*C{r}", VERDE, F_DEC)
    put(ws, f"F{r}", f"=MT_VEND*C{r}", VERDE, F_DEC)
    put(ws, f"G{r}", f"=MT_VENTAS*C{r}", VERDE, F_ARS)
    put(ws, f"H{r}", f"=MT_CVAR*C{r}", VERDE, F_ARS)
    put(ws, f"I{r}", f"=MT_COMV*C{r}", VERDE, F_ARS)
    put(ws, f"J{r}", "=MT_FIJOS", VERDE, F_ARS)
    put(ws, f"K{r}", f"=DEBCRED*(G{r}+H{r}+I{r}+J{r})", NEGRO, F_ARS)
    put(ws, f"L{r}", f"=H{r}+I{r}+J{r}+K{r}", NEGRO, F_ARS)
    put(ws, f"M{r}", f"=G{r}-L{r}", NEGRO, F_ARS)
    put(ws, f"N{r}", f"=AM_OBRA*(A{r}<=VIDA_OBRA*12)+AM_EQ*(A{r}<=VIDA_EQ*12)+AM_PALA*(A{r}<=VIDA_PALA*12)"
                     f"+AM_INT*(A{r}<=VIDA_INT*12)", VERDE, F_ARS)
    put(ws, f"O{r}", f"=M{r}-N{r}", NEGRO, F_ARS)
    put(ws, f"P{r}", f"=(C_CASC+C_ENV)*C{r}+C_EVAR+C_EFIJ+C_OTROS", VERDE, F_ARS)
    put(ws, f"Q{r}", f"=(G{r}*D_COBRO+((C_CASC+C_FLETE+C_ENV)*C{r}+C_EVAR)*D_STOCK-P{r}*D_PAGO)/(365/12)", NEGRO, F_ARS)
    put(ws, f"R{r}", f"=Q{r}-Q{p}", NEGRO, F_ARS)
    put(ws, f"S{r}", f"=IF(B{r}>=2,INDEX(Impuestos!$G$4:$G$18,B{r}-1)/12,0)+IF(A{r}={N},Impuestos!$G$18,0)", VERDE,
        F_ARS)
    put(ws, f"T{r}", f"=IF(A{r}={N},(CL_TERRENO+CL_OBRA*(1-{N}/12/VIDA_OBRA))*DOLAR+Q{r},0)", NEGRO, F_ARS)
    put(ws, f"U{r}", f"=M{r}-S{r}-R{r}+T{r}", NEGRO, F_ARS)
    put(ws, f"V{r}", f"=U{r}-T{r}", NEGRO, F_ARS)
    put(ws, f"W{r}", f"=W{p}+V{r}", NEGRO, F_ARS)
    put(ws, f"X{r}", f"=(1+TASA_REAL)^(-A{r}/12)", NEGRO, '0.0000')
    put(ws, f"Y{r}", f"=Y{p}+V{r}*X{r}", NEGRO, F_ARS)
    put(ws, f"Z{r}", f'=IF(AND(W{p}<0,W{r}>=0),A{r}-1-W{p}/V{r},"")', NEGRO, F_MES)
    put(ws, f"AA{r}", f'=IF(AND(Y{p}<0,Y{r}>=0),A{r}-1-Y{p}/(V{r}*X{r}),"")', NEGRO, F_MES)
RF = R0 + N
ws.freeze_panes = "B4"
for n, col in (("FM_MES", "A"), ("FM_ANIO", "B"), ("FM_VENTAS", "G"), ("FM_COSTO", "L"), ("FM_EBITDA", "M"),
               ("FM_AMORT", "N"), ("FM_EBIT", "O"), ("FM_GAN", "S"), ("FM_DCT", "R"), ("FM_FLUJO", "U"),
               ("FM_FOP", "V"), ("FM_SECO", "E"), ("FM_VEND", "F"), ("FM_HUM", "D"), ("FM_CT", "Q")):
    wb.defined_names[n] = DefinedName(n, attr_text=f"'{FM}'!${col}${R0}:${col}${RF}")

# =============================================================================== Impuestos
ws = wsI
ws["A1"] = "Impuesto a las ganancias: base anual, quebrantos (5 años, los más viejos primero) y escala 2026"
ws["A1"].font = TITULO
encabezado(ws, 3, ["Año", "EBIT anual ($)", "Ganancia ($)", "Quebranto ($)", "Quebranto compensado ($)",
                   "Base imponible ($)", "Impuesto devengado ($)", "Beneficio neto ($)"],
           [6, 17, 16, 16, 18, 17, 17, 17])
for y in range(1, 16):
    r = 3 + y
    put(ws, f"A{r}", y, NEGRO, F_NUM)
    put(ws, f"B{r}", f"=SUMIF(FM_ANIO,A{r},FM_EBIT)", VERDE, F_ARS)
    put(ws, f"C{r}", f"=MAX(0,B{r})", NEGRO, F_ARS)
    put(ws, f"D{r}", f"=MAX(0,-B{r})", NEGRO, F_ARS)
    put(ws, f"E{r}", f"=SUMPRODUCT(($D$21:$R$21=A{r})*$D$23:$R$37)", NEGRO, F_ARS)
    put(ws, f"F{r}", f"=C{r}-E{r}", NEGRO, F_ARS)
    put(ws, f"G{r}", f"=IF(F{r}<=0,0,IF(F{r}<=GAN_T1,0.25*F{r},IF(F{r}<=GAN_T2,0.25*GAN_T1+0.3*(F{r}-GAN_T1),"
                     f"0.25*GAN_T1+0.3*(GAN_T2-GAN_T1)+0.35*(F{r}-GAN_T2))))", NEGRO, F_ARS)
    put(ws, f"H{r}", f"=B{r}-G{r}", NEGRO, F_ARS)
put(ws, "A20", "Uso de quebrantos: fila = año en que se generó; columna = año en que se compensa (hasta 5 años después)",
    NEGRITA, borde=False)
put(ws, "B21", "j \\ año", NEGRITA)
put(ws, "C22", 0, NEGRO, F_NUM)
for y in range(1, 16):
    col = get_column_letter(3 + y)
    put(ws, f"{col}21", y, NEGRITA, F_NUM)
    put(ws, f"{col}22", 0, NEGRO, F_NUM)
for j in range(1, 16):
    r = 22 + j
    put(ws, f"B{r}", j, NEGRITA, F_NUM)
    put(ws, f"C{r}", 0, NEGRO, F_NUM)
    for y in range(1, 16):
        col = get_column_letter(3 + y)
        prev_col = get_column_letter(2 + y)
        put(ws, f"{col}{r}", f"=IF(AND({col}$21-$B{r}>=1,{col}$21-$B{r}<=5),MAX(0,MIN(INDEX($D$4:$D$18,$B{r})"
                             f"-SUM($C{r}:{prev_col}{r}),INDEX($C$4:$C$18,{col}$21)-SUM({col}$22:{col}{r - 1}))),0)",
            NEGRO, F_NUM)
        ws.column_dimensions[col].width = max(ws.column_dimensions[col].width or 0, 12)

# =============================================================================== Flujo anual
ws = wb.create_sheet("Flujo anual")
ws["A1"] = "Flujo de caja anual ($ de noviembre de 2026)"
ws["A1"].font = TITULO
encabezado(ws, 3, ["Año", "Guano húmedo (t)", "Producto seco (t)", "Vendido (t)", "Ventas ($)", "Costo total ($)",
                   "EBITDA ($)", "Amortización ($)", "EBIT ($)", "Ganancias devengado ($)", "Beneficio neto ($)",
                   "Ganancias pagado ($)", "Variación del capital de trabajo ($)", "Flujo de caja ($)",
                   "Acumulado operativo ($)"], [6, 13, 13, 12, 16, 16, 16, 15, 16, 16, 16, 16, 16, 16, 17])
put(ws, "A4", 0, NEGRO, F_NUM)
put(ws, "N4", "=-INV_ARS", VERDE, F_ARS)
put(ws, "O4", "=N4", NEGRO, F_ARS)
for y in range(1, 16):
    r = 4 + y
    put(ws, f"A{r}", y, NEGRO, F_NUM)
    for col, n in zip("BCDEFGHI", ("FM_HUM", "FM_SECO", "FM_VEND", "FM_VENTAS", "FM_COSTO", "FM_EBITDA", "FM_AMORT",
                                   "FM_EBIT")):
        put(ws, f"{col}{r}", f"=SUMIF(FM_ANIO,$A{r},{n})", VERDE, F_DEC if col in "BCD" else F_ARS)
    put(ws, f"J{r}", f"=Impuestos!G{3 + y}", VERDE, F_ARS)
    put(ws, f"K{r}", f"=I{r}-J{r}", NEGRO, F_ARS)
    put(ws, f"L{r}", f"=SUMIF(FM_ANIO,$A{r},FM_GAN)", VERDE, F_ARS)
    put(ws, f"M{r}", f"=SUMIF(FM_ANIO,$A{r},FM_DCT)", VERDE, F_ARS)
    put(ws, f"N{r}", f"=SUMIF(FM_ANIO,$A{r},FM_FOP)", VERDE, F_ARS)
    put(ws, f"O{r}", f"=O{r - 1}+N{r}", NEGRO, F_ARS)
ws["A21"] = ("El flujo anual no incluye el valor residual del mes 180 (terreno, obra civil y capital de trabajo), que "
             "sí entra en el VAN.")
ws["A21"].font = CHICA
ws.freeze_panes = "B4"

# =============================================================================== Indicadores
ws = wb.create_sheet("Indicadores")
ws["A1"] = "Indicadores del escenario activo y control contra el modelo en Python"
ws["A1"].font = TITULO
ws["A2"] = '=CHOOSE(ESC,"Escenario conservador","Escenario realista","Escenario optimista")'
ws["A2"].font = NEGRITA
encabezado(ws, 4, ["Indicador", "Excel (fórmulas)", "Unidad", "Python (modelo)", "Diferencia", "Fórmula"],
           [52, 18, 10, 18, 14, 70])
ind = [
    ("Inversión inicial total", "=INV_ARS", "$", "inv_total", F_ARS, "suma de la hoja Inversión × dólar"),
    ("Capital de trabajo de régimen (mes 24)", "=INDEX(FM_CT,25)", "$", "ct_regimen", F_ARS,
     "cobrar 45 d + existencias 30 d − pagar 30 d"),
    ("Producción de producto seco (año 2)", "=MT_SECO*12", "t/año", ("anio2", "seco_t"), F_DEC, ""),
    ("Producto vendido (año 2)", "=MT_VEND*12", "t/año", ("anio2", "vendido_t"), F_DEC, ""),
    ("Ventas (año 2)", "='Flujo anual'!E6", "$/año", ("anio2", "ventas"), F_ARS, ""),
    ("Costo total sin amortizaciones (año 2)", "='Flujo anual'!F6", "$/año", ("anio2", "costo_total"), F_ARS, ""),
    ("Beneficio operativo antes de amortizaciones, EBITDA (año 2)", "='Flujo anual'!G6", "$/año", ("anio2", "ebitda"),
     F_ARS, "ventas − costos operativos"),
    ("Beneficio neto (año 2)", "='Flujo anual'!K6", "$/año", ("anio2", "beneficio_neto"), F_ARS,
     "EBITDA − amortizaciones − ganancias"),
    ("Flujo de caja neto (año 2)", "='Flujo anual'!N6", "$/año", ("anio2", "flujo"), F_ARS,
     "EBITDA − ganancias pagado − Δ capital de trabajo"),
    ("Payback: mes en que el acumulado llega a cero",
     f"=IF(COUNT('{FM}'!Z{R0 + 1}:Z{RF})=0,\"no recupera\",MIN('{FM}'!Z{R0 + 1}:Z{RF}))", "mes", "payback_meses",
     F_MES, "primer mes con acumulado ≥ 0, interpolado (sin valor residual)"),
    ("Payback descontado (10 % real)",
     f"=IF(COUNT('{FM}'!AA{R0 + 1}:AA{RF})=0,\"no recupera\",MIN('{FM}'!AA{R0 + 1}:AA{RF}))", "mes",
     "payback_descontado", F_MES, ""),
    ("Payback con la fórmula Inversión / flujo mensual de régimen",
     "=IF('Flujo anual'!N6>0,INV_ARS/('Flujo anual'!N6/12),\"flujo ≤ 0\")", "mes", "payback_formula", F_MES,
     "sólo orientativo: no cuenta la puesta en marcha"),
    ("VAN a 15 años (10 % real)", "=SUMPRODUCT(FM_FLUJO,(1+TASA_REAL)^(-FM_MES/12))", "$", "van", F_ARS,
     "Σ flujo / (1 + 0,10)^(mes/12), con valor residual"),
    ("TIR (anual equivalente)", "=IFERROR((1+IRR(FM_FLUJO,0.005))^12-1,IFERROR((1+IRR(FM_FLUJO,-0.03))^12-1,"
     "IFERROR((1+IRR(FM_FLUJO,-0.04))^12-1,IFERROR((1+IRR(FM_FLUJO,-0.06))^12-1,\"no existe\"))))", "%/año", "tir", F_PCT, "TIR mensual de los 181 flujos, llevada a anual: (1 + TIR)^12 − 1"),
    ("ROI anual (año 2)", "='Flujo anual'!K6/(INV_ARS+MAX(INDEX(FM_CT,25),0))", "%/año", "roi_anual", F_PCT,
     "beneficio neto del año 2 / (inversión + capital de trabajo)"),
    ("ROI acumulado a 5 años", "=SUM('Flujo anual'!K5:K9)/(INV_ARS+MAX(INDEX(FM_CT,25),0))", "%", "roi_5", F_PCT,
     "Σ beneficio neto años 1 a 5 / (inversión + capital de trabajo)"),
    ("Costo de producción por kg de producto seco", "=MT_PROD/(MT_SECO*1000)", "$/kg", "costo_prod_kg", F_DEC, ""),
    ("Costo total por kg vendido (sin amortizaciones)", "=MT_TOTAL/(MT_VEND*1000)", "$/kg", "costo_total_kg", F_DEC, ""),
    ("Costo total por kg vendido (con amortizaciones)", "=(MT_TOTAL+(AM_OBRA+AM_EQ+AM_PALA+AM_INT))/(MT_VEND*1000)",
     "$/kg", "costo_total_kg_amort", F_DEC, ""),
    ("Beneficio neto por kg vendido (año 2)", "='Flujo anual'!K6/('Flujo anual'!D6*1000)", "$/kg", "neto_kg", F_DEC, ""),
    ("Contribución por tonelada vendida", "=MT_VENTAS/MT_VEND-(C_CASC+C_EVAR+C_FLETE+C_ENV+0.6*C_OTROS+C_COMERC+C_IIBB+C_DEB)/MT_VEND",
     "$/t", "contribucion_t", F_ARS, "precio − costos variables por t"),
    ("Punto de equilibrio operativo (producto vendido)",
     "=IF(B{fila_cu}>0,(MT_TOTAL-(C_CASC+C_EVAR+C_FLETE+C_ENV+0.6*C_OTROS+C_COMERC+C_IIBB+C_DEB))*12/B{fila_cu},\"no existe\")",
     "t/año", "pe_operativo_t", F_DEC, "costos fijos de caja / contribución por t"),
]
fila_cu = 5 + [x[3] for x in ind].index("contribucion_t")
for i, (rot, fml, unidad, clave, fmt, crit) in enumerate(ind, 5):
    put(ws, f"A{i}", rot)
    put(ws, f"B{i}", fml.replace("{fila_cu}", str(fila_cu)), NEGRO, fmt)
    put(ws, f"C{i}", unidad)
    vals = []
    for n in ("conservador", "realista", "optimista"):
        e = E["escenarios"][n]
        v = e[clave[0]][clave[1]] if isinstance(clave, tuple) else e[clave]
        if clave in ("roi_anual", "roi_5") and v is not None:
            v = v / 100                                     # el modelo guarda el ROI en %; la planilla, en fracción
        if v is None:
            v = {"payback_formula": "flujo ≤ 0"}.get(clave, "no recupera" if "payback" in str(clave) else "no existe")
        vals.append(v)
    put(ws, f"D{i}", f'=CHOOSE(ESC,{",".join(json.dumps(v, ensure_ascii=False) if isinstance(v, str) else repr(v) for v in vals)})',
        AZUL, fmt)
    put(ws, f"E{i}", f'=IF(ISNUMBER(B{i}),IF(ISNUMBER(D{i}),B{i}-D{i},"distinto"),IF(B{i}=D{i},0,"distinto"))',
        NEGRO, F_DEC)
    put(ws, f"F{i}", crit, Font(name="Arial", size=9))
    put(ws, f"G{i}", f'=IF(ISNUMBER(E{i}),IF(ABS(E{i})>0.00001*IF(ISNUMBER(D{i}),ABS(D{i}),0)+0.01,1,0),'
                     f'IF(E{i}="distinto",1,0))', NEGRO, F_NUM)
ws.cell(row=4, column=7, value="¿Difiere?").font = NEGRITA
fila_ctrl = 5 + len(ind) + 1
put(ws, f"A{fila_ctrl}", "Control: indicadores en los que Excel y Python difieren (debe dar 0)", NEGRITA)
put(ws, f"B{fila_ctrl}", f"=SUM(G5:G{fila_ctrl - 2})", NEGRITA, F_NUM, AMARILLO)
nombre("CTRL_DIF", "Indicadores", f"B{fila_ctrl}")
ws.freeze_panes = "A5"

# =============================================================================== hojas de valores del modelo en Python
def hoja_valores(nombre_hoja, titulo, cab, filas, anchos, fmts):
    ws = wb.create_sheet(nombre_hoja)
    ws["A1"] = titulo
    ws["A1"].font = TITULO
    ws["A2"] = "Valores calculados con fuente/economia/modelo_economico.py (no son fórmulas)."
    ws["A2"].font = CHICA
    encabezado(ws, 4, cab, anchos)
    for i, f in enumerate(filas, 5):
        for j, v in enumerate(f, 1):
            c = ws.cell(row=i, column=j, value=v)
            c.font = NEGRO
            c.border = BORDE
            if fmts[j - 1] and isinstance(v, (int, float)):
                c.number_format = fmts[j - 1]
    ws.freeze_panes = "A5"
    return ws


Mi = 1e6
filas = []
for n in ("conservador", "realista", "optimista"):
    e = E["escenarios"][n]
    a = e["anio2"]
    pb = e["payback_meses"]
    filas.append([n.capitalize(), e["inv_total"] / M.DOLAR, e["inv_total"] / Mi, a["humedo_t"], a["seco_t"],
                  a["vendido_t"], e["precio_t"] / M.DOLAR, a["ventas"] / 12 / Mi, a["costo_total"] / 12 / Mi,
                  a["beneficio_neto"] / 12 / Mi, a["beneficio_neto"] / Mi, a["flujo"] / Mi,
                  "no recupera" if pb is None else pb, e["roi_anual"] / 100, e["van"] / Mi])
r = E["referencia"]
a = r["anio2"]
filas.append(["Referencia: optimista con 2 turnos a 1.440 kg/h", r["inv_total"] / M.DOLAR, r["inv_total"] / Mi,
              a["humedo_t"], a["seco_t"], a["vendido_t"], r["precio_t"] / M.DOLAR, a["ventas"] / 12 / Mi,
              a["costo_total"] / 12 / Mi, a["beneficio_neto"] / 12 / Mi, a["beneficio_neto"] / Mi, a["flujo"] / Mi,
              r["payback_meses"], r["roi_anual"] / 100, r["van"] / Mi])
hoja_valores("Escenarios", "Comparación de escenarios (año 2, de régimen)",
             ["Escenario", "Inversión (USD)", "Inversión ($ M)", "Guano húmedo (t/año)", "Producto seco (t/año)",
              "Vendido (t/año)", "Precio medio (USD/t)", "Ventas ($ M/mes)", "Costos ($ M/mes)",
              "Beneficio neto ($ M/mes)", "Beneficio neto ($ M/año)", "Flujo de caja ($ M/año)", "Payback (meses)",
              "ROI anual", "VAN ($ M)"],
             filas, [40, 13, 12, 12, 12, 11, 11, 11, 11, 12, 12, 12, 11, 9, 11],
             [None, F_NUM, F_DEC, F_NUM, F_NUM, F_NUM, F_DEC, F_DEC, F_DEC, F_DEC, F_DEC, F_DEC, F_MES, F_PCT, F_DEC])

filas = []
for caso, rot in (("realista", "Realista"), ("optimista", "Optimista"), ("referencia", "Referencia 2 turnos 1.440 kg/h")):
    s = E["sensibilidad"][caso]
    for f in s["filas"]:
        for lado in ("bajo", "alto"):
            v = f[lado]
            filas.append([rot, f["nombre"], f[f"txt_{lado}"], v["flujo_anual"] / Mi,
                          "no recupera" if v["payback"] is None else v["payback"], v["van"] / Mi])
    for d in s["derivas"]:
        filas.append([rot, d["desc"], "5 años", d["flujo_anio5"] / Mi,
                      "no recupera" if d["payback"] is None else d["payback"], d["van"] / Mi])
hoja_valores("Sensibilidad", "Sensibilidad: una variable por vez",
             ["Caso base", "Variable", "Valor", "Flujo de caja anual ($ M)", "Payback (meses)", "VAN ($ M)"],
             filas, [30, 60, 12, 16, 14, 12], [None, None, None, F_DEC, F_MES, F_DEC])

filas = []
for n in ("realista", "optimista"):
    inv = E["inverso"][n]
    for k, dd in inv["minimos"].items():
        cfg, N_ = k.split("_")
        if dd:
            filas.append([n, cfg, int(N_), dd["m_in"], dd["humedo_dia_kg"], dd["humedo_mes_t"], dd["humedo_anio_t"],
                          dd["seco_anio_t"], dd["vendido_anio_t"], dd["lineas_necesarias"]])
        else:
            filas.append([n, cfg, int(N_), "no alcanzable", None, None, None, None, None, None])
hoja_valores("Inverso", "Análisis inverso: caudal mínimo por configuración para recuperar en 24 a 60 meses",
             ["Escenario de precios", "Configuración", "Plazo (meses)", "Caudal (kg/h por secadora)",
              "Guano húmedo (kg/día)", "Guano húmedo (t/mes)", "Guano húmedo (t/año)", "Producto seco (t/año)",
              "Vendido (t/año)", "Secadoras SC-4 necesarias"],
             filas, [16, 12, 10, 14, 14, 14, 14, 14, 12, 12],
             [None, None, F_NUM, F_NUM, F_NUM, F_NUM, F_NUM, F_NUM, F_NUM, F_NUM])


def main():
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    for hoja in wb.worksheets:
        for fila_ in hoja.iter_rows():
            for c in fila_:
                if c.value is not None and c.font and c.font.name != "Arial":
                    c.font = Font(name="Arial", size=c.font.size or 10, bold=c.font.bold, italic=c.font.italic,
                                  color=c.font.color)
    wb["Supuestos"]["C4"].comment = Comment("1 = conservador, 2 = realista, 3 = optimista", "modelo")
    wb.calculation.fullCalcOnLoad = True                   # Excel y LibreOffice recalculan al abrir
    wb.save(SALIDA)
    print("guardado", SALIDA)


if __name__ == "__main__":
    main()
