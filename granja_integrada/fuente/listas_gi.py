"""Planilla de listas de la granja integrada: motores, instrumentos, alimentadores y entradas/salidas.

    python listas_gi.py        # -> ../documentacion/Listas_granja_integrada.xlsx

Sale de datos/electrica.json (el mismo archivo que usan la memoria, los planos y el 3D). Los totales y las
verificaciones de los alimentadores son fórmulas, para que la planilla se recalcule si se cambia un valor.
"""
from __future__ import annotations

import json
from pathlib import Path

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
E = json.loads((RAIZ / "datos" / "electrica.json").read_text(encoding="utf-8"))
SALIDA = RAIZ / "documentacion" / "Listas_granja_integrada.xlsx"

LETRA = "Arial"
F_TIT = Font(name=LETRA, size=13, bold=True)
F_CAB = Font(name=LETRA, size=10, bold=True, color="FFFFFF")
F_TXT = Font(name=LETRA, size=10)
F_TOT = Font(name=LETRA, size=10, bold=True)
F_NOTA = Font(name=LETRA, size=9, italic=True, color="555555")
RELLENO_CAB = PatternFill("solid", fgColor="2F4A5C")
RELLENO_TOT = PatternFill("solid", fgColor="E6ECF0")
FINO = Side(style="thin", color="B7C2CA")
BORDE = Border(left=FINO, right=FINO, top=FINO, bottom=FINO)


def hoja(wb, nombre, titulo, columnas, filas, formatos=None, nota=None):
    """Hoja con título en la fila 1, nota en la 2, encabezados en la 4 y datos desde la 5. Devuelve (ws, fila_final)."""
    ws = wb.create_sheet(nombre)
    ws["A1"] = titulo
    ws["A1"].font = F_TIT
    if nota:
        ws["A2"] = nota
        ws["A2"].font = F_NOTA
    for j, (cab, ancho) in enumerate(columnas, start=1):
        c = ws.cell(row=4, column=j, value=cab)
        c.font, c.fill, c.border = F_CAB, RELLENO_CAB, BORDE
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = ancho
    ws.row_dimensions[4].height = 30
    for i, fila in enumerate(filas, start=5):
        for j, v in enumerate(fila, start=1):
            c = ws.cell(row=i, column=j, value=v)
            c.font, c.border = F_TXT, BORDE
            c.alignment = Alignment(vertical="top", wrap_text=isinstance(v, str) and len(v) > 18)
            if formatos and formatos.get(j):
                c.number_format = formatos[j]
    fin = 4 + len(filas)
    ws.freeze_panes = "B5"
    ws.auto_filter.ref = f"A4:{get_column_letter(len(columnas))}{fin}"
    return ws, fin


def total(ws, fila, etiqueta, formulas, formatos=None):
    """Fila de totales: formulas = {columna: '=...'}."""
    c = ws.cell(row=fila, column=1, value=etiqueta)
    c.font, c.fill, c.border = F_TOT, RELLENO_TOT, BORDE
    for j, f in formulas.items():
        c = ws.cell(row=fila, column=j, value=f)
        c.font, c.fill, c.border = F_TOT, RELLENO_TOT, BORDE
        if formatos and formatos.get(j):
            c.number_format = formatos[j]


def leame(wb):
    ws = wb.active
    ws.title = "Léame"
    r = E["resumen"]
    lineas = [
        ("Granja integrada · secado de guano y 4 galpones", F_TIT),
        ("Listas de motores, instrumentos, alimentadores y entradas/salidas – Rev. A (noviembre de 2026)", F_TXT),
        ("", F_TXT),
        ("Origen: datos/electrica.json, el mismo archivo que usan la memoria técnica, las láminas GI-12 a GI-17 y el "
         "modelo 3D. Para cambiar un valor, cambiarlo en el cálculo (fuente/electrica_granja.py) y volver a generar "
         "esta planilla con fuente/listas_gi.py.", F_TXT),
        ("", F_TXT),
        ("Tipos de dato", F_TOT),
        ("R: del proyecto de la secadora (Rev. F)", F_TXT),
        ("S: del proyecto San Jorge", F_TXT),
        ("V: verificado con una fuente externa citada", F_TXT),
        ("P: preliminar, propuesta de este rediseño a confirmar con el fabricante o en obra", F_TXT),
        ("H: hipótesis sin dato publicado ni relevado", F_TXT),
        ("", F_TXT),
        ("Hojas", F_TOT),
        (f"Motores: los {len(E['motores'])} motores de la planta y del transporte ({r['motores_nuevos']} nuevos, los de la "
         "Rev. F que siguen y los que se quitan con el biogás).", F_TXT),
        (f"Instrumentos: {len(E['instrumentos'])} tags; las cantidades y los canales se suman con fórmulas.", F_TXT),
        ("Alimentadores: la verificación Ib ≤ In ≤ Iz, I2 ≤ 1,45 · Iz y la caída de tensión se recalcula con fórmulas.", F_TXT),
        ("E-S: señales por periferia y módulos ET 200SP con 20 % de reserva.", F_TXT),
    ]
    for i, (txt, f) in enumerate(lineas, start=1):
        c = ws.cell(row=i, column=1, value=txt)
        c.font = f
        c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions["A"].width = 110


def motores(wb):
    cols = [("Tag", 8), ("Equipo", 34), ("Función", 46), ("Ubicación", 30), ("Tablero", 10), ("kW", 7), ("Tipo kW", 7),
            ("In (A)", 8), ("Arranque", 18), ("Vínculo mecánico", 36), ("Protección", 32), ("Seccionador", 30),
            ("Mando", 28), ("Cable", 22), ("S (mm²)", 8), ("Iz (A)", 8), ("L (m)", 8), ("ΔU circuito (%)", 10),
            ("ΔU total (%)", 10), ("Estado", 30)]
    filas = []
    for m in E["motores"]:
        filas.append([m["tag"], m.get("nombre", ""), m["funcion"], m["ubicacion"], m["tablero"], m["kW"], m["origen_kW"],
                      m["In_A"], m["arranque"], m["vinculo"], m["proteccion"], m.get("seccionador", ""), m["mando"],
                      m.get("cable", ""), m["S_mm2"], m.get("Iz_A"), m["L_m"], m["dU_pct"], m.get("dU_total_pct"),
                      m["estado"]])
    fmt = {6: "0.00", 8: "0.00", 15: "0.0", 16: "0.0", 17: "0.0", 18: "0.00", 19: "0.00"}
    ws, fin = hoja(wb, "Motores", "Lista de motores", cols, filas, fmt,
                   "kW e In de la Rev. F (R) o preliminares (P); ΔU total = desde el origen de la instalación. "
                   "Las celdas vacías de los motores de la Rev. F no se recalcularon en este rediseño.")
    rango_e, rango_kw = f"$T$5:$T${fin}", f"$F$5:$F${fin}"
    total(ws, fin + 2, "kW nuevos", {6: f'=SUMIFS({rango_kw},{rango_e},"nuevo")'}, {6: "0.00"})
    total(ws, fin + 3, "Motores nuevos", {6: f'=COUNTIFS({rango_e},"nuevo")'}, {6: "0"})
    total(ws, fin + 4, "kW de la Rev. F que siguen", {6: f'=SUMIFS({rango_kw},{rango_e},"sin cambios*")'}, {6: "0.00"})
    total(ws, fin + 5, "kW que se quitan", {6: f'=SUMIFS({rango_kw},{rango_e},"se quita*")'}, {6: "0.00"})
    total(ws, fin + 6, "Mayor ΔU total (%)", {6: f"=MAX($S$5:$S${fin})"}, {6: "0.00"})
    ws.cell(row=fin + 6, column=7, value="límite 5 % (AEA 90364-7-771)").font = F_NOTA


def instrumentos(wb):
    cols = [("Tag", 12), ("Tipo", 40), ("Cantidad", 9), ("Señal", 10), ("Canales por unidad", 10), ("Canales", 9),
            ("Montaje", 50), ("Periferia", 11), ("Alcance", 30), ("Cable", 18), ("L total (m)", 10)]
    filas = []
    for k, i in enumerate(E["instrumentos"], start=5):
        filas.append([i["tag"], i["tipo"], int(i["cantidad"]), i["senal"], i.get("canales_por_unidad"),
                      f"=C{k}*E{k}" if i.get("canales_por_unidad") is not None else None,
                      i.get("montaje", "(controlador del galpón)"), i["periferia"], i["alcance"], i.get("cable", ""),
                      i.get("L_total_m")])
    ws, fin = hoja(wb, "Instrumentos", "Lista de instrumentos", cols, filas, {11: "0.0"},
                   "Ubicación de cada unidad en el modelo 3D: datos/electrica.json (campo «unidades»). "
                   "Los del galpón y el depósito son del controlador del galpón (fuera de alcance).")
    rango_a = f"$I$5:$I${fin}"
    total(ws, fin + 2, "Instrumentos del transporte", {3: f'=SUMIFS($C$5:$C${fin},{rango_a},"planta / transporte")'})
    total(ws, fin + 3, "Tags del transporte", {3: f'=COUNTIFS({rango_a},"planta / transporte")'})
    total(ws, fin + 4, "Instrumentos en total", {3: f"=SUM($C$5:$C${fin})"})
    total(ws, fin + 5, "Canales en total", {3: f"=SUM($F$5:$F${fin})"})
    total(ws, fin + 6, "Cable en total (m)", {3: f"=SUM($K$5:$K${fin})"}, {3: "0"})


def alimentadores(wb):
    cols = [("Circuito", 44), ("Desde", 8), ("Hasta", 9), ("Tipo de dato", 18), ("kW dem.", 8), ("Ib (A)", 8),
            ("In (A)", 8), ("S (mm²)", 8), ("Método", 8), ("Iz (A)", 8), ("L (m)", 8), ("ΔU (%)", 8),
            ("ΔU total (%)", 9), ("I2 (A)", 8), ("1,45 · Iz (A)", 9), ("Ib ≤ In ≤ Iz", 10), ("I2 ≤ 1,45 · Iz", 10),
            ("ΔU tot. ≤ 3 %", 10), ("Icc3 al final (kA)", 10)]
    filas = []
    for k, a in enumerate(E["alimentadores"], start=5):
        filas.append([a["circuito"], a["desde"], a["hasta"], a["tipo"], a["kW_demanda"], a["Ib_A"], a["In_A"],
                      a["S_mm2"], a["metodo"], a["Iz_A"], a["L_m"], a["dU_pct"], a["dU_total_pct"], a["I2_A"],
                      f"=1.45*J{k}", f'=IF(AND(F{k}<=G{k},G{k}<=J{k}),"sí","NO")', f'=IF(N{k}<=O{k},"sí","NO")',
                      f'=IF(M{k}<=3,"sí","NO")', a.get("Icc3_fin_kA")])
    ws, fin = hoja(wb, "Alimentadores", "Alimentadores (Cu, IRAM 2178)", cols, filas,
                   {5: "0.0", 6: "0.0", 10: "0.0", 11: "0.0", 12: "0.00", 13: "0.00", 14: "0.0", 15: "0.0", 19: "0.00"},
                   "Iz con factores de temperatura y agrupamiento (IEC 60364-5-52; en zanja, dos caños separados 0,5 m: "
                   "0,95). I2 = 1,45 · In para interruptores IEC 60898/60947-2.")
    ws.cell(row=4, column=15).comment = Comment("Límite de la condición de sobrecarga: I2 ≤ 1,45 · Iz.", "listas_gi")
    total(ws, fin + 2, "Alimentadores que verifican todo",
          {16: f'=COUNTIFS($P$5:$P${fin},"sí",$Q$5:$Q${fin},"sí",$R$5:$R${fin},"sí")'})
    ws.cell(row=fin + 2, column=17, value=f"de {len(filas)}").font = F_NOTA


def entradas_salidas(wb):
    cols = [("Periferia", 12), ("DI", 7), ("F-DI", 7), ("DQ", 7), ("AI", 7), ("SIWAREX", 9), ("Variadores PROFINET", 11),
            ("Total de señales", 10), ("Módulos ET 200SP (con 20 % de reserva)", 60)]
    filas = []
    for k, (rid, v) in enumerate(E["io"].items(), start=5):
        s = v["señales"]
        filas.append([rid, s.get("DI", 0), s.get("F-DI", 0), s.get("DQ", 0), s.get("AI", 0), s.get("SIWAREX", 0),
                      s.get("PROFINET (variadores)", 0), f"=SUM(B{k}:F{k})",
                      ", ".join(f"{m} {n}" for m, n in v["modulos_ET200SP_con_20pct_reserva"].items())])
    ws, fin = hoja(wb, "E-S", "Entradas y salidas por periferia", cols, filas, None,
                   "Total de señales = DI + F-DI + DQ + AI + SIWAREX (los variadores van por PROFINET).")
    total(ws, fin + 2, "Total", {j: f"=SUM({get_column_letter(j)}5:{get_column_letter(j)}{fin})" for j in range(2, 9)})


def main():
    wb = Workbook()
    leame(wb)
    motores(wb)
    instrumentos(wb)
    alimentadores(wb)
    entradas_salidas(wb)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    wb.save(SALIDA)
    print("guardado", SALIDA)


if __name__ == "__main__":
    main()
