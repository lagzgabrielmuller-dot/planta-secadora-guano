"""Corre todos los escenarios, guarda los resultados y dibuja las figuras.

Uso:
    python correr_todo.py                 # calcula lo que falta y dibuja todo
    python correr_todo.py --rehacer       # recalcula todo (unos 25 min en una PC de 2 núcleos)
    python correr_todo.py --solo ventana clima
    python correr_todo.py --figuras       # solo redibuja a partir de resultados/*.json
"""
import argparse
import json
import os
import time

import escenarios as es

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "resultados")
os.makedirs(RES, exist_ok=True)

# Sintonía de los lazos de humedad. Ganancias en unidades de la variable manipulada por punto de
# humedad: (m/min)/% para las bandas y K/% para el aire. Las pruebas están en
# resultados/sintonia_pruebas.json. Para las bandas se deja la más suave probada: igual hace oscilar
# el producto entre 10 y 43 %, y con más ganancia entra en un ciclo entre 1 y 70 %.
SINTONIA = dict(
    vel=dict(Kc=0.003, Ti_min=120.0, Kff=0.0, rampa=0.05),
    T=dict(Kc=0.8, Ti_min=45.0, rampa=2.0),
    T_ff=dict(Kc=0.8, Ti_min=45.0, rampa=2.0, Kff=1.25, ff_retardo_s=40 * 60.0),
)


def ruta(nombre):
    return os.path.join(RES, f"{nombre}.json")


def guardar(nombre, d):
    with open(ruta(nombre), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, default=float)


def cargar(nombre):
    with open(ruta(nombre), encoding="utf-8") as f:
        return json.load(f)


def calcular(nombre, rehacer):
    if os.path.exists(ruta(nombre)) and not rehacer:
        return cargar(nombre)
    t0 = time.time()
    print(f"→ {nombre} ...", flush=True)
    if nombre == "perfiles":
        d = es.perfiles()
    elif nombre == "ventana":
        d = es.ventana()
    elif nombre == "temperatura":
        d = es.temperatura()
    elif nombre == "capacidad":
        d = es.capacidad()
    elif nombre == "recirculacion":
        d = es.recirculacion()
    elif nombre == "sensibilidad":
        d = es.sensibilidad()
    elif nombre == "clima":
        d = es.clima_anual()
    elif nombre == "variantes":
        d = es.variantes()
    elif nombre == "energia":
        d = es.energia(calcular("perfiles", False))
    elif nombre == "dinamica":
        T15 = calcular("perfiles", False)["T15"]
        d = es.dinamica_lazos(T15, SINTONIA)
    elif nombre == "sintonia_pruebas":
        d = es.sintonia(calcular("perfiles", False)["T15"])
    elif nombre == "bordes":
        d = es.bordes()
    elif nombre == "higiene":
        d = es.higiene_malla(calcular("perfiles", False)["T15"])
    else:
        raise KeyError(nombre)
    guardar(nombre, d)
    print(f"  {nombre}: {time.time() - t0:.0f} s", flush=True)
    return d


PASOS = ["perfiles", "ventana", "temperatura", "capacidad", "recirculacion", "sensibilidad", "clima",
         "variantes", "energia", "dinamica", "bordes", "higiene", "sintonia_pruebas"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehacer", action="store_true")
    ap.add_argument("--figuras", action="store_true")
    ap.add_argument("--solo", nargs="*")
    a = ap.parse_args()
    if not a.figuras:
        for p in (a.solo or PASOS):
            calcular(p, a.rehacer or bool(a.solo))
    import figuras
    figuras.todas()


if __name__ == "__main__":
    main()
