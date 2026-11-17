"""Pruebas del análisis económico (pytest): el modelo reproduce la evaluación del proyecto y el balance de masa, el
JSON está al día, y el informe, la planilla y el README tienen los mismos números.

    python -m pytest tests/test_economia.py -q
"""
import json
import re
import shutil
import subprocess
import sys

import pytest

from conftest import CALC, RAIZ

ECO = RAIZ / "fuente" / "economia"
sys.path.insert(0, str(ECO))
import modelo_economico as me  # noqa: E402

pymupdf = pytest.importorskip("pymupdf")
openpyxl = pytest.importorskip("openpyxl")

CARPETA = RAIZ / "analisis_economico"
PDF = CARPETA / "Analisis_economico_Secadora_Guano.pdf"
XLSX = CARPETA / "Modelo_economico_Secadora_Guano.xlsx"


def ar(x, d=1):
    """Número con coma decimal y punto de miles (como en los documentos)."""
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


@pytest.fixture(scope="module")
def E():
    with open(ECO / "economia.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def texto():
    with pymupdf.open(PDF) as d:
        return " ".join(" ".join(p.get_text().split()) for p in d)


# ------------------------------------------------------------------ archivos
@pytest.mark.parametrize("rel", ["Analisis_economico_Secadora_Guano.pdf", "Analisis_economico_Secadora_Guano.docx",
                                 "Modelo_economico_Secadora_Guano.xlsx", "README.md"] +
                         [f"figuras/{f}" for f in ("f1_produccion.png", "f2_ingresos_costos.png",
                                                   "f3_recuperacion_referencia.png", "f4_recuperacion_escenarios.png",
                                                   "f5_tornado.png", "f6_precio_payback.png",
                                                   "f7_capacidad_necesaria.png", "f8_puente.png")])
def test_archivo_presente(rel):
    ruta = CARPETA / rel
    assert ruta.is_file() and ruta.stat().st_size > 1000, rel


# ------------------------------------------------------------------ modelo
def test_balance_de_masa(E):
    a = E["escenarios"]["realista"]["anio2"]
    assert a["seco_t"] / a["humedo_t"] == pytest.approx(0.28 / 0.85, rel=1e-9)
    assert me.W_MAX == pytest.approx(1440 * (1 - 0.28 / 0.85))
    assert a["vendido_t"] == pytest.approx(a["seco_t"] * 0.98 * 0.90, rel=1e-9)


def test_puente_parte_del_proyecto_y_cierra(E):
    with open(CALC / "presupuesto.json", encoding="utf-8") as f:
        P = json.load(f)
    b = next(e for e in P["evaluacion"]["escenarios"] if e["nombre"].startswith("B"))
    pasos = E["puente"]["pasos"]
    assert pasos[0][1] == b["neto"]
    assert sum(v for _t, v in pasos) == pytest.approx(E["puente"]["flujo_realista_usd"], abs=5)


@pytest.mark.parametrize("nombre", ["conservador", "realista", "optimista"])
def test_json_al_dia(E, nombre):
    """economia.json coincide con lo que calcula hoy el modelo (si cambia un dato del proyecto, hay que regenerar)."""
    _t, esc = me.escenarios()
    ind = me.indicadores(esc[nombre])
    e = E["escenarios"][nombre]
    assert ind["inv_total"] == pytest.approx(e["inv_total"], rel=1e-9)
    assert ind["anio2"]["flujo"] == pytest.approx(e["anio2"]["flujo"], rel=1e-9)
    assert ind["van"] == pytest.approx(e["van"], rel=1e-9)
    assert (ind["payback_meses"] is None) == (e["payback_meses"] is None)


def test_inversion_del_proyecto_sin_biogas(E):
    with open(CALC / "presupuesto.json", encoding="utf-8") as f:
        P = json.load(f)
    assert E["escenarios"]["realista"]["inversion"]["proyecto"] == pytest.approx(P["inversion"]["sin_biogas"], abs=1)


@pytest.mark.parametrize("caso", ["referencia", "conservador", "realista", "optimista"])
def test_payback_es_el_cruce_del_flujo_acumulado(E, caso):
    """El payback es el primer mes en que el flujo acumulado sin valor residual llega a cero (interpolado)."""
    e = E[caso] if caso == "referencia" else E["escenarios"][caso]
    acum, pb = 0.0, None
    for f in e["flujo_mensual"]:
        v = f["flujo"] - (f.get("residual") or 0.0)
        if f["mes"] > 0 and acum < 0 <= acum + v:
            pb = f["mes"] - 1 - acum / v
            break
        acum += v
    if e["payback_meses"] is None:
        assert pb is None
    else:
        assert pb == pytest.approx(e["payback_meses"], abs=1e-6)


def test_la_referencia_recupera_y_los_escenarios_de_un_turno_no(E):
    assert E["referencia"]["payback_meses"] < 60
    for n in ("conservador", "realista", "optimista"):
        assert E["escenarios"][n]["payback_meses"] is None


def test_capacidad_minima_dentro_del_limite_de_la_maquina(E):
    m = E["inverso"]["optimista"]["minimos"]["2T_60"]
    assert m["payback"] == pytest.approx(60, abs=0.05)
    assert 1000 < m["m_in"] <= me.M_IN_MAX and m["lineas_necesarias"] == 1


# ------------------------------------------------------------------ informe y README
def test_informe_con_los_numeros_del_modelo(E, texto):
    r, ref = E["escenarios"]["realista"], E["referencia"]
    for v in (ar(r["inv_total"] / 1e6, 1), ar(r["inv_total"] / E["dolar"], 0), ar(ref["payback_meses"], 1),
              ar(E["inverso"]["optimista"]["minimos"]["2T_60"]["m_in"], 0), ar(E["datos"]["VALOR_NPK"], 1),
              ar(r["costo_total_kg"], 0)):
        assert v in texto, v
    assert "no recupera" in texto


def test_informe_sin_marcadores_ni_apellido_viejo(texto):
    assert "[COMPLETAR]" not in texto and "A completar" not in texto
    for malo in ("TODO", "XXX", "nan", "None", "inf"):
        assert not re.search(rf"\b{malo}\b", texto), malo
    assert not re.search("Hofstet" + "te(?!r)", texto)      # partido para no marcarse a sí mismo (test_entrega)


def test_readme_de_la_seccion(E):
    t = (CARPETA / "README.md").read_text(encoding="utf-8")
    assert ar(E["inverso"]["optimista"]["minimos"]["2T_60"]["m_in"], 0) in t
    for rel in re.findall(r"\]\(([^)#]+)\)", t):
        assert (CARPETA / rel).exists(), rel


# ------------------------------------------------------------------ planilla
def test_planilla_con_formulas_y_nombres():
    wb = openpyxl.load_workbook(XLSX)
    for hoja in ("Supuestos", "Inversión", "Mes tipo", "Flujo mensual", "Impuestos", "Flujo anual", "Indicadores"):
        assert hoja in wb.sheetnames, hoja
    for n in ("ESC", "INV_ARS", "FM_FLUJO", "CTRL_DIF", "p_pr_b25"):
        assert n in wb.defined_names, n
    formulas = sum(1 for ws in wb.worksheets for fila in ws.iter_rows() for c in fila
                   if isinstance(c.value, str) and c.value.startswith("="))
    assert formulas > 5000


SOFFICE = shutil.which("soffice") or shutil.which("libreoffice")


@pytest.mark.skipif(not SOFFICE, reason="hace falta LibreOffice para recalcular la planilla")
@pytest.mark.parametrize("escenario", [1, 2, 3])
def test_planilla_recalculada_igual_que_python(tmp_path, escenario):
    """Con LibreOffice, la hoja Indicadores no tiene diferencias contra el modelo en Python."""
    wb = openpyxl.load_workbook(XLSX)
    wb["Supuestos"]["C4"].value = escenario
    copia = tmp_path / f"esc{escenario}.xlsx"
    wb.save(copia)
    subprocess.run([SOFFICE, "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(tmp_path / "out"),
                    str(copia)], check=True, capture_output=True, timeout=180)
    ws = openpyxl.load_workbook(tmp_path / "out" / copia.name, data_only=True)["Indicadores"]
    filas = {ws.cell(row=r, column=1).value: ws.cell(row=r, column=2).value for r in range(5, 40)}
    control = next(v for k, v in filas.items() if k and k.startswith("Control"))
    assert control == 0
