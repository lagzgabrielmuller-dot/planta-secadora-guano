"""Pruebas de la entrega (pytest): que estén todos los archivos, que se abran, que los integrantes estén bien
escritos y que los números de la memoria y del informe sean los de los cálculos.

    python -m pytest tests -q
"""
import json
import re
import zipfile

import pytest

from conftest import CALC, RAIZ

ezdxf = pytest.importorskip("ezdxf")
pymupdf = pytest.importorskip("pymupdf")

LAMINAS = [f"P{i:02d}" for i in range(1, 25)]
LAMINAS_SC = [f"SC-{i:02d}" for i in range(1, 7)]
INTEGRANTES = ["Müller", "Hofstetter", "Goette", "Stegmann", "Bernhardt", "Belluzzo"]
A3_PT = (420 / 25.4 * 72, 297 / 25.4 * 72)


def ar(x, dec=1):
    """Número con coma decimal y punto de miles (como en los documentos)."""
    s = f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def texto_pdf(rel):
    with pymupdf.open(RAIZ / rel) as d:
        return " ".join(" ".join(p.get_text().split()) for p in d)


@pytest.fixture(scope="module")
def R():
    with open(CALC / "resultados.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def P():
    with open(CALC / "presupuesto.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def informe():
    return texto_pdf("informe/Informe_Final_Secadora_Guano.pdf")


@pytest.fixture(scope="module")
def memoria():
    return texto_pdf("memoria/Memoria_de_calculo_RevD.pdf")


# ------------------------------------------------------------------ archivos
ARCHIVOS = [
    "index.html", "visor.html",
    "informe/Informe_Final_Secadora_Guano.docx", "informe/Informe_Final_Secadora_Guano.pdf",
    "memoria/Memoria_de_calculo_RevD.docx", "memoria/Memoria_de_calculo_RevD.pdf",
    "presupuesto/Presupuesto_Secadora_Guano.xlsx",
    "planos/pdf/Planos_Secadora_RevD.pdf",
    "modelo_3d/Secadora_guano_RevD_step.zip",
    "secadora/Visor_Secador_SC4.html", "secadora/Manual_de_armado_SC4.docx", "secadora/Manual_de_armado_SC4.pdf",
    "secadora/planos/pdf/Planos_Secador_SC4.pdf",
    "secadora/modelo_3d/Secador_SC4.step", "secadora/modelo_3d/Secador_SC4.glb", "secadora/modelo_3d/piezas.json",
] + [f"planos/{p}.png" for p in LAMINAS] + [f"planos/pdf/{p}.pdf" for p in LAMINAS] + \
    [f"planos/dxf/{p}.dxf" for p in LAMINAS] + [f"secadora/planos/{t}/{s}.{t}" for s in LAMINAS_SC for t in ("pdf", "dxf")]


@pytest.mark.parametrize("rel", ARCHIVOS)
def test_archivo_presente(rel):
    ruta = RAIZ / rel
    assert ruta.is_file() and ruta.stat().st_size > 1000, rel


@pytest.mark.parametrize("p", LAMINAS + LAMINAS_SC)
def test_lamina_dxf_valida_y_con_integrantes(p):
    ruta = RAIZ / ("planos/dxf" if p.startswith("P") else "secadora/planos/dxf") / f"{p}.dxf"
    doc = ezdxf.readfile(ruta)
    auditoria = doc.audit()
    assert not auditoria.has_errors, [str(e) for e in auditoria.errors][:3]
    textos = " ".join(e.dxf.text if e.dxftype() == "TEXT" else e.text for e in doc.modelspace().query("TEXT MTEXT"))
    for apellido in INTEGRANTES:
        assert apellido in textos, (p, apellido)
    assert not re.search(r"Hofstette(?!r)", textos)


@pytest.mark.parametrize("p", LAMINAS)
def test_lamina_pdf_a3(p):
    with pymupdf.open(RAIZ / "planos/pdf" / f"{p}.pdf") as d:
        assert d.page_count == 1
        w, h = d[0].rect.width, d[0].rect.height
        assert (w, h) == pytest.approx(A3_PT, abs=2), (w, h)


def test_juego_completo_tiene_24_laminas():
    with pymupdf.open(RAIZ / "planos/pdf/Planos_Secadora_RevD.pdf") as d:
        assert d.page_count == 24


def test_entrega_html_redirige_a_la_portada():
    t = (RAIZ / "entrega.html").read_text(encoding="utf-8")
    assert 'url=index.html' in t and 'href="index.html"' in t


def test_portada_sin_claves_y_con_numeros_de_los_calculos(R, P):
    t = (RAIZ / "index.html").read_text(encoding="utf-8")
    assert "{{" not in t and "drive.google" not in t and "Hofstetter" in t
    assert f"{ar(R['tg2']['total_kW'], 2)} kW" in t
    assert f"{ar(R['biogas']['biogas'], 0)} m³" in t
    c = next(e for e in P["evaluacion"]["escenarios"] if e["nombre"].startswith("C"))
    assert f"TIR del {ar(c['TIR'], 1)} %" in t


# ------------------------------------------------------------------ integrantes bien escritos en todo
@pytest.mark.parametrize("rel", ["informe/Informe_Final_Secadora_Guano.pdf", "memoria/Memoria_de_calculo_RevD.pdf",
                                 "secadora/Manual_de_armado_SC4.pdf"])
def test_integrantes_en_pdf(rel):
    t = texto_pdf(rel)
    assert "Hofstetter" in t and not re.search(r"Hofstette(?!r)", t)


@pytest.mark.parametrize("rel", ["informe/Informe_Final_Secadora_Guano.docx", "memoria/Memoria_de_calculo_RevD.docx",
                                 "secadora/Manual_de_armado_SC4.docx"])
def test_integrantes_en_word(rel):
    with zipfile.ZipFile(RAIZ / rel) as z:
        xml = " ".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n.endswith(".xml"))
    assert "Hofstetter" in xml and not re.search(r"Hofstette(?!r)", xml)


def test_ningun_archivo_de_texto_con_el_apellido_viejo():
    malos = []
    for ruta in RAIZ.rglob("*"):
        if ruta.suffix.lower() in (".html", ".md", ".py", ".js", ".mjs", ".json", ".txt") and "node_modules" not in ruta.parts \
                and ruta.name != "test_entrega.py":
            if re.search(r"Hofstette(?!r)", ruta.read_text(encoding="utf-8", errors="ignore")):
                malos.append(str(ruta.relative_to(RAIZ)))
    assert not malos, malos


# ------------------------------------------------------------------ números de los cálculos en los documentos
def test_numeros_del_tg2_en_memoria_e_informe(R, memoria, informe):
    tg = R["tg2"]
    for v, dec in ((tg["total_kW"], 2), (tg["demanda_tg2_kW"], 1), (tg["I_demanda_A"], 1),
                   (tg["acometida"]["Iz"], 1), (tg["balance"]["sin_G1_kW"], 1), (tg["balance"]["margen_sin_G1_pct"], 1)):
        assert ar(v, dec) in memoria, ("memoria", v)
        assert ar(v, dec) in informe, ("informe", v)


def test_numeros_de_biogas_en_memoria(R, memoria):
    b = R["biogas"]
    for v in (b["biogas"], b["E_el"]):
        assert ar(v, 0) in memoria, v
    assert ar(b["horas"], 1) in memoria


def test_fatiga_en_informe(R, informe):
    f = R["fatiga"]
    assert ar(f["eje_motriz"]["n_min"], 2) in informe
    assert ar(f["mensula"]["n"], 1) in informe
    assert ar(f["eje_reenvio"]["casos"][1]["n"], 2) in informe


def test_evaluacion_en_informe(P, informe):
    for e in P["evaluacion"]["escenarios"]:
        assert ar(e["TIR"], 1) in informe, e["nombre"]
        assert ar(e["repago"], 1) in informe, e["nombre"]
    assert ar(P["inversion"]["total"], 0) in informe


def test_piezas_del_secador(R):
    with open(RAIZ / "secadora/modelo_3d/piezas.json", encoding="utf-8") as f:
        piezas = json.load(f)
    lista = piezas["piezas"] if isinstance(piezas, dict) else piezas
    assert len(lista) == 68                               # 65 + faldones de sellado 4.21 de los 3 pisos (Rev. F)
    assert len({x['cod'] for x in lista}) == len(lista)   # sin códigos repetidos
    masa = R["fatiga"]["anclajes"]["masa"]
    assert masa["modelo_cad_kg"] == pytest.approx(sum(p.get("masa_kg", p.get("masa", 0)) for p in lista), rel=0.02)
