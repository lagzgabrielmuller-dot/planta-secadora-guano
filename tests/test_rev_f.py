"""Pruebas de la Rev. F (estudio térmico del secador SC-4): que cada cambio propuesto esté en los cálculos, los
planos, el modelo 3D, el presupuesto y el informe. Ver docs/REV_F.md."""
import json
import re

import pytest

from conftest import CALC, RAIZ

ezdxf = pytest.importorskip("ezdxf")
pymupdf = pytest.importorskip("pymupdf")


def textos_dxf(rel):
    doc = ezdxf.readfile(RAIZ / rel)
    return " ".join(e.dxf.text if e.dxftype() == "TEXT" else e.plain_text() for e in doc.modelspace().query("TEXT MTEXT"))


@pytest.fixture(scope="module")
def informe():
    with pymupdf.open(RAIZ / "informe/Informe_Final_Secadora_Guano.pdf") as d:
        return " ".join(" ".join(p.get_text().split()) for p in d)


@pytest.fixture(scope="module")
def R():
    return json.loads((CALC / "resultados.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def P():
    return json.loads((CALC / "presupuesto.json").read_text(encoding="utf-8"))


def test_ventilador_del_enfriador_en_el_tg2(R):
    assert any(m["tag"] == "M40" and m["kW"] == 0.55 for m in R["tg2"]["motores"])
    q21 = next(c for c in R["tg2"]["circuitos"] if c["Q"] == "Q21")
    assert "M40" in q21["cargas"] and q21["verifica"]


def test_guias_ptfe_y_faldones_en_el_modelo():
    piezas = json.loads((RAIZ / "secadora/modelo_3d/piezas.json").read_text(encoding="utf-8"))["piezas"]
    mat = {p["cod"]: p["material"] for p in piezas}
    assert mat["4.7-1"] == "UHMW-PE" and mat["4.7-2"] == "PTFE" and mat["4.7-3"] == "PTFE"
    assert all(f"4.21-{n}" in mat for n in (1, 2, 3))


def test_presupuesto_con_items_rev_f(P):
    codigos = {f[0] for f in P["inversion"]["filas"]}
    assert {"B17", "B18"} <= codigos
    costos = P["evaluacion"]["costos"]
    assert any("419 t/año" in k for k in costos)
    assert any("PTFE" in f[0] for f in P["secador"]["filas"])


@pytest.mark.parametrize("lamina, letra", [("P02", "E"), ("P06", "E"), ("P18", "E"), ("P22", "F"), ("P23", "G")])
def test_laminas_revisadas(lamina, letra):
    t = textos_dxf(f"planos/dxf/{lamina}.dxf")
    assert "11/2026" in t, lamina
    assert re.search(rf"\b{letra}\b", t)


def test_plano_18_cd03_por_humedad_relativa():
    t = textos_dxf("planos/dxf/P18.dxf")
    assert "HR < 90 %" in t and "45 g/kg" not in t


def test_plano_06_lazo_en_cascada():
    t = textos_dxf("planos/dxf/P06.dxf")
    assert "consigna de TIC-01" in t and "FY-01" in t


def test_informe_con_la_rev_f(informe):
    for frase in ("Verificación con el modelo térmico", "PTFE", "faldón", "tolva de retención", "1.440 kg/h",
                  "5,6 cm/s", "Cinta de alimentación", "casi saturado"):
        assert frase in informe, frase
    for vieja in ("sinfín dosificador", "Sinfín dosificador", "planta de biogás existente", "67,7 kW"):
        assert vieja not in informe, vieja


def test_simulador_marca_los_cambios_como_incorporados():
    html = (RAIZ / "simulacion_termica/simulador.html").read_text(encoding="utf-8")
    assert "Cambios incorporados al proyecto en la Rev. F" in html and "sinfín dosificador" not in html
