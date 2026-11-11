"""Pruebas de los cálculos (pytest): vuelven a calcular desde los programas y controlan relaciones físicas,
normativas y económicas que tienen que cumplirse siempre.

    python -m pytest tests -q
"""
import json
import math

import pytest

from conftest import CALC

import calculos_memoria as cm   # noqa: E402  (conftest agrega fuente/calculos al path)
import fatiga as fa             # noqa: E402
import presupuesto as pr        # noqa: E402


def _json(nombre):
    with open(CALC / nombre, encoding="utf-8") as f:
        return json.load(f)


def _normal(obj):
    """Igual que lo que queda en el JSON (tuplas -> listas)."""
    return json.loads(json.dumps(obj, ensure_ascii=False))


@pytest.fixture(scope="module")
def R():
    return _json("resultados.json")


@pytest.fixture(scope="module")
def P():
    return _json("presupuesto.json")


# ------------------------------------------------------------------ los JSON están al día
def test_resultados_json_al_dia(R):
    """resultados.json es exactamente lo que dan hoy los programas: nadie lo editó a mano."""
    ilum = cm.calc_iluminacion()
    nuevo = {"tg2": cm.calc_tg2(ilum), "iluminacion": ilum, "ventilacion": cm.calc_ventilacion(),
             "biogas": cm.calc_biogas(), "fuego": cm.calc_fuego(), "fatiga": fa.calc_fatiga()}
    assert _normal(nuevo) == R


def test_presupuesto_json_al_dia(P):
    assert _normal(pr.calcular()) == P


# ------------------------------------------------------------------ balance de masa del proceso
def test_balance_de_masa_del_secado():
    """8 t/día de guano al 72 % de humedad dan 2,6 t/día de abono al 15 % (materia seca constante)."""
    seco = 8.0 * (1 - 0.72) / (1 - 0.15)
    assert seco == pytest.approx(2.635, abs=0.001)
    assert round(seco, 1) == 2.6
    # el informe declara 329 kg/h de producto en un turno de 8 h
    assert seco * 1000 / 8 == pytest.approx(329, abs=1)


def test_consumo_de_cascara():
    """3.175 MJ/h con cáscara de PCI 13,5 MJ/kg y rendimiento 75 % -> 314 kg/h; 880 kW térmicos."""
    assert 3175 / (13.5 * 0.75) == pytest.approx(314, abs=0.5)
    assert 3175 / 3.6 == pytest.approx(880, abs=3)


# ------------------------------------------------------------------ tablero TG2 (AEA 90364-7-771)
def test_circuitos_tg2_verifican(R):
    for c in R["tg2"]["circuitos"]:
        assert c["Ib"] <= c["In"] <= c["Iz"], c["Q"]
        assert c["dU_total_pct"] <= c["lim_dU_pct"], c["Q"]
        assert c["verifica"], c["Q"]


def test_acometida_tg2(R):
    ac = R["tg2"]["acometida"]
    assert ac["S"] == 35 and ac["Iz"] == pytest.approx(98 * 0.95, abs=0.1)     # D1 enterrado a 25 °C
    assert R["tg2"]["I_demanda_A"] <= ac["Ir"] <= ac["Iz"]
    assert ac["I2_fusible"] <= ac["lim_I2"]                                     # I2 ≤ 1,45·Iz
    assert ac["verifica"]


def test_seccion_se_aumenta_si_no_verifica(monkeypatch):
    """Si un circuito no verifica In ≤ Iz, el programa sube la sección comercial y lo anota."""
    circuitos = [list(c) for c in cm.CIRCUITOS]
    q27 = next(c for c in circuitos if c[0] == "Q27")
    q27[3] = 1.5                                         # sección deliberadamente chica
    monkeypatch.setattr(cm, "CIRCUITOS", [tuple(c) for c in circuitos])
    c = next(c for c in cm.calc_tg2(cm.calc_iluminacion())["circuitos"] if c["Q"] == "Q27")
    assert c["S"] > 1.5 and c["verifica"]
    assert "sección aumentada de 1.5" in c["nota"]


def test_balance_de_potencia(R):
    b = R["tg2"]["balance"]
    tgf_max = float(b["TGF_kW"].split("-")[1])
    assert b["sin_G1_kW"] == pytest.approx(tgf_max + b["TG2_kW"] + b["incendio_kW"], abs=0.11)
    assert b["con_G1_kW"] == pytest.approx(b["sin_G1_kW"] + b["G1_kW"], abs=0.11)
    assert b["margen_sin_G1_pct"] == pytest.approx(100 * (b["adoptada_kW"] - b["sin_G1_kW"]) / b["adoptada_kW"], abs=0.1)
    assert b["adoptada_kW"] >= b["sin_G1_kW"]


def test_tablas_iz_iec_60364_5_52():
    """Valores de tabla (Cu/PVC, 3 conductores cargados) que usa el cálculo."""
    assert cm.IZ["E"][35] == 126 and cm.IZ["E"][4] == 34
    assert cm.IZ["D1"][35] == 98 and cm.IZ["D1"][16] == 64
    assert cm.K_PVC == 115


# ------------------------------------------------------------------ biogás
def test_biogas_coherente(R):
    b = R["biogas"]
    rinde = b["biogas"] / b["SV_kg"]
    assert 0.25 <= rinde <= 0.45, rinde                    # m³/kg SV: rango publicado para guano de gallina
    assert b["PCI"] == pytest.approx(0.58 * 35.8, abs=0.1)   # 58 % de metano, PCI del CH4 35,8 MJ/m³
    assert b["E_MJ"] == pytest.approx(b["biogas"] * b["PCI"], rel=0.01)
    assert b["horas"] == pytest.approx(b["E_el"] / 25, abs=0.1)   # motogenerador de 25 kWe


# ------------------------------------------------------------------ fatiga (Shigley-Budynas 8.ª ed.)
def test_factores_de_marin():
    assert fa.se_prima(570) == 285
    assert fa.ka(570, "maquinado") == pytest.approx(4.51 * 570 ** -0.265, rel=1e-9)
    assert fa.kb(50) == pytest.approx(1.24 * 50 ** -0.107, rel=1e-9)
    assert fa.kb(60) == pytest.approx(1.51 * 60 ** -0.157, rel=1e-9)
    assert fa.KE_CONF[99] == 0.814


def test_materiales_de_tabla_a20():
    m = fa.MATERIALES
    assert (m["SAE 1045 HR"]["Sut"], m["SAE 1045 HR"]["Sy"]) == (570, 310)
    assert (m["SAE 1020 HR"]["Sut"], m["SAE 1020 HR"]["Sy"]) == (380, 210)


def test_ejes_y_uniones_verifican(R):
    f = R["fatiga"]
    assert f["eje_motriz"]["verifica"] and f["eje_motriz"]["n_min"] >= f["n_adm"]
    assert min(c["n"] for c in f["eje_reenvio"]["casos"][1:]) >= f["n_adm"]     # ejecución propuesta Ø60/Ø50
    assert f["mensula"]["n"] >= f["n_adm"]
    assert f["chaveta"]["n_fatiga"] >= f["n_adm"]


def test_mensula_usa_kc_de_corte():
    """Cordón de soldadura a corte: Sse = 0,59·Se (Shigley ec. 6-26), no 0,67."""
    m = fa.mensula()
    se, _ = fa.marin(427.0, 12, "forjado", conf=fa.CONFIABILIDAD)
    assert m["Sse"] == pytest.approx(0.59 * se, abs=0.05)


def test_eje_de_1020_no_verifica():
    """La decisión del informe: con SAE 1020 el eje motriz no verifica; por eso se pide 1045 con certificado."""
    assert fa.eje_motriz("SAE 1020 HR")["n_min"] < fa.N_ADM


# ------------------------------------------------------------------ presupuesto y evaluación económica
def test_inversion_suma(P):
    inv = P["inversion"]
    assert inv["total"] == pytest.approx(inv["sub_revC"] + inv["sub_revD"] + inv["sub_ing"] + inv["imprevistos"], abs=2)
    assert inv["total_ARS"] == pytest.approx(inv["total"] * P["dolar"], rel=1e-4)
    assert P["dolar"] == 1550.0                               # BNA vendedor del 23/10/2026


@pytest.mark.parametrize("i", range(4))
def test_tir_y_repago_de_cada_escenario(P, i):
    e = P["evaluacion"]["escenarios"][i]
    n, tasa = P["evaluacion"]["anios"], P["evaluacion"]["tasa"]
    van = lambda r: -e["inversion"] + sum(e["neto"] / (1 + r) ** k for k in range(1, n + 1))   # noqa: E731
    assert abs(van(e["TIR"] / 100)) < 0.01 * e["inversion"]          # la TIR anula el VAN
    assert van(tasa) == pytest.approx(e["VAN"], abs=0.005 * e["inversion"])
    assert e["repago"] == pytest.approx(e["inversion"] / e["neto"], abs=0.06)


def test_escenarios_coherentes(P):
    a, b, c, d = P["evaluacion"]["escenarios"]
    assert c["inversion"] == a["inversion"] + 30000 and d["inversion"] == b["inversion"] + 30000
    assert b["inversion"] == P["inversion"]["sin_biogas"]
    assert c["TIR"] > a["TIR"] and d["TIR"] > b["TIR"]       # el segundo turno mejora el proyecto
    assert not math.isnan(a["TIR"])
