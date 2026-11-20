"""Ensamblado final de la granja integrada: arma el modelo completo y exporta GLB, STEP y la lista de piezas.

    python ensamblar.py            # todo
    python ensamblar.py glb        # solo los GLB
    python ensamblar.py step       # solo los STEP

Salidas (carpeta modelo_3d/):
- granja_integrada.glb   la granja completa (visor y renders)
- planta_central.glb     nave, secador SC-4, equipos de la Rev. F, recepción, torres e instalación eléctrica de la planta
- galpon_tipo_G1.glb     galpón G1 con su cabecera de guano, cinta transversal, inclinada y CCM
- secador_SC4.glb        secador SC-4 solo
- Granja_integrada_STEP.zip con:
    Planta_central.step         nave, SC-4, equipos de la Rev. F (sólidos exactos o facetados), TP-01 y eléctrica
    Transporte_de_guano.step    cintas, galerías, torres, desviadoras, contenedores y obra civil
    Galpon_tipo_G1.step         galpón G1 con su transporte de guano
    Secador_SC4.step            secador SC-4 solo
    Instalacion_electrica.step  tableros, bandejas, caños, seccionadores y puesta a tierra de toda la granja
- datos/piezas.json      lista de piezas por grupo (cantidad, código, nombre y material)

Unidades del STEP: mm. Ejes: X al Este, Y al Norte, Z arriba; origen en el vértice Sudoeste de la nave (igual que los
planos y el proyecto anterior). Los GLB van en metros con Y arriba (glTF).
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI / "modelo"))
sys.path.insert(1, str(RAIZ.parent / "fuente"))          # proyecto anterior (solo lectura): modelo_step.forma_de

import cad            # noqa: E402
import electrica      # noqa: E402
import galpon         # noqa: E402
import planta         # noqa: E402
import sitio          # noqa: E402
import transporte     # noqa: E402

SALIDA = RAIZ / "modelo_3d"
TMP = SALIDA / "_step"

TRANSPORTE = {"Transporte de guano", "Transporte de guano - obra civil", "Torres de transferencia",
              "Contenedores de emergencia"}


def escena():
    e = cad.Escena("Granja integrada")
    sitio.construir(e)
    galpon.construir(e)
    informe = {}
    planta.construir(e, informe)
    transporte.construir(e)
    electrica.construir(e)
    return e, informe


def _pos(i):
    return i["M"][:3, 3] / 1000


def en_planta(i):
    """Zona de la planta central (nave, torres y sus galerías cortas)."""
    if "M" not in i or i["grupo"] == "Predio - terreno":
        return True
    x, y, _ = _pos(i)
    return -16 <= x <= 49 and -4 <= y <= 24


def en_galpon_g1(i):
    if "M" not in i:
        return False
    g = i["grupo"]
    if g.startswith(("Predio", "Torres", "Depósitos", "Planta", "Nave", "Galpones - cintas de huevos")) or "CE-" in (i["cod"] or ""):
        return False
    x, y, _ = _pos(i)
    return -76 <= x <= -54 and 13.0 <= y <= 132


# ===================================================================================== GLB
def exportar_glb(e):
    t = time.time()
    salidas = {}
    salidas["granja_integrada.glb"] = e.exportar_glb(SALIDA / "granja_integrada.glb")
    salidas["planta_central.glb"] = e.exportar_glb(SALIDA / "planta_central.glb", filtro=en_planta)
    todas = e.mallas
    e.mallas = []                                        # el galpón y el secador no llevan terreno ni equipos de la Rev. F
    salidas["galpon_tipo_G1.glb"] = e.exportar_glb(SALIDA / "galpon_tipo_G1.glb", filtro=en_galpon_g1)
    salidas["secador_SC4.glb"] = e.exportar_glb(SALIDA / "secador_SC4.glb", filtro=lambda i: i["grupo"] == "Secador SC-4")
    e.mallas = todas
    for n in salidas:
        print(f"  {n}: {os.path.getsize(SALIDA / n) / 1e6:.1f} MB")
    print(f"GLB en {time.time() - t:.0f} s")


# ===================================================================================== STEP
def piezas_revF():
    """Equipos de la Rev. F que siguen en la planta, como sólidos (exactos donde el visor tenía primitivas)."""
    import cadquery as cq
    import modelo_step as MS
    geo = json.loads(gzip.open(planta.GEO, "rt", encoding="utf-8").read())
    nombres = geo.get("nombres", {})
    cuenta = defaultdict(int)
    subs = {}
    for k in sorted(geo["partes"], key=MS.orden):
        if k in planta.EXCLUIR or k.startswith("4."):
            continue
        grupo = planta.GRUPO_DE.get(k, "Planta - otros equipos")
        por_color = defaultdict(list)
        for it in geo["partes"][k]:
            if not it.get("tri"):
                continue
            m = np.array(it["m"], float).reshape(4, 4).T
            v = np.array(it["tri"], float).reshape(-1, 3)
            w = (m @ np.c_[v, np.ones(len(v))].T).T[:, :3]
            p = np.c_[w[:, 0], -w[:, 2], w[:, 1]]
            ok, dxyz = planta._filtro_item(k, p.min(0), p.max(0))
            if not ok:
                continue
            f = MS.forma_de(it, cuenta)
            if f is None:
                continue
            if dxyz is not None:                              # equipos que se corrieron (circulador, luminaria, tanque)
                from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
                from OCP.gp import gp_Trsf, gp_Vec
                tr = gp_Trsf()
                tr.SetTranslation(gp_Vec(*(float(v) * 1000 for v in dxyz)))
                f = BRepBuilderAPI_Transform(f, tr, True).Shape()
            por_color[it.get("c", 0x999999)].append(f)
        if not por_color:
            continue
        etiqueta = f"{k} {nombres.get(k, '')}".strip().replace("/", "-")
        sub = cq.Assembly(name=etiqueta.replace(" ", "_"))
        for n, (c, formas) in enumerate(sorted(por_color.items())):
            sub.add(MS.compuesto(formas), name=f"{k}-{n + 1}", color=MS.color(int(c)))
        subs.setdefault(grupo, []).append(sub)
    print(f"  Rev. F: {cuenta['exactas']} sólidos exactos, {cuenta['facetadas']} facetados, {cuenta['descartadas']} descartados")
    return subs


def exportar_step(e):
    import cadquery as cq
    from OCP.Interface import Interface_Static
    Interface_Static.SetCVal_s("write.step.unit", "MM")
    t = time.time()
    TMP.mkdir(parents=True, exist_ok=True)
    archivos = []

    def guardar(nombre, filtro, extra=None):
        ruta = TMP / f"{nombre}.step"
        asm, n = _ensamble(e, filtro, f"Granja_integrada_{nombre}")
        for grupo, subs in (extra or {}).items():          # equipos de la Rev. F que siguen en la planta
            ga = cq.Assembly(name=grupo.replace(" ", "_") + "_RevF")
            for s_ in subs:
                ga.add(s_, name=s_.name)
            asm.add(ga, name=grupo.replace(" ", "_") + "_RevF")
            n += len(subs)
        asm.export(str(ruta), write_pcurves=False)
        archivos.append(ruta)
        print(f"  {ruta.name}: {n} piezas, {os.path.getsize(ruta) / 1e6:.1f} MB", flush=True)

    planta_grupos = lambda i: (i["grupo"].startswith(("Nave de proceso", "Secador SC-4", "Recepción", "Planta"))  # noqa: E731
                               or (i["grupo"].startswith("Instalación eléctrica") and en_planta(i)))
    guardar("Planta_central", planta_grupos, extra=piezas_revF())
    guardar("Transporte_de_guano", lambda i: i["grupo"] in TRANSPORTE)
    guardar("Galpon_tipo_G1", en_galpon_g1)
    guardar("Secador_SC4", lambda i: i["grupo"] == "Secador SC-4")
    guardar("Instalacion_electrica", lambda i: i["grupo"].startswith("Instalación eléctrica"))
    destino = SALIDA / "Granja_integrada_STEP.zip"
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for a in archivos:
            z.write(a, a.name)
        z.writestr("LEEME.txt", "Granja integrada - modelos STEP (AP214)\n"
                                "Unidades: mm. Ejes: X al Este, Y al Norte, Z arriba. Origen: vértice Sudoeste de la nave.\n"
                                "Cada archivo es un ensamble con un subensamble por sistema y una pieza por componente,\n"
                                "con su nombre y su color. Abre en SolidWorks, Fusion 360, FreeCAD y Onshape.\n"
                                "Los equipos de la Rev. F que siguen en la planta van en Planta_central.step como sólidos\n"
                                "exactos donde el modelo original tenía primitivas y como sólidos facetados en el resto.\n")
    print(f"STEP en {time.time() - t:.0f} s → {destino.name} ({os.path.getsize(destino) / 1e6:.1f} MB)")


def _ensamble(e, filtro, nombre):
    """Mismo ensamble que Escena.exportar_step, sin escribir el archivo."""
    import cadquery as cq
    raiz = cq.Assembly(name=nombre)
    subs = {}
    cont = defaultdict(int)
    for i in e.inst:
        if filtro and not filtro(i):
            continue
        g = i["grupo"]
        if g not in subs:
            subs[g] = cq.Assembly(name=g.replace(" ", "_"))
        r, g_, b, _m, _r2, a = cad.MAT[i["mat"]]
        base = (i["cod"] or i["nom"] or "pieza").replace(" ", "_").replace("/", "-")[:60]
        cont[(g, base)] += 1
        subs[g].add(cad.forma(i["key"]), name=f"{base}_{cont[(g, base)]}", loc=cq.Location(cad._trsf(i["M"])),
                    color=cq.Color(r, g_, b, a))
    for g, s in subs.items():
        raiz.add(s, name=g.replace(" ", "_"))
    return raiz, sum(cont.values())


# ===================================================================================== lista de piezas
def piezas(e, informe):
    lista = e.piezas()
    por_grupo = defaultdict(int)
    for p in lista:
        por_grupo[p["grupo"]] += p["cant"]
    out = {"total_instancias": len(e.inst), "grupos": dict(sorted(por_grupo.items())),
           "revF": {k: v for k, v in informe.items() if k != "excluidas"}, "piezas": lista}
    (RAIZ / "datos" / "piezas.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"piezas.json: {len(lista)} renglones, {len(e.inst)} instancias en {len(por_grupo)} grupos")


def main():
    que = sys.argv[1:] or ["glb", "step", "piezas"]
    SALIDA.mkdir(parents=True, exist_ok=True)
    t = time.time()
    e, informe = escena()
    print(f"escena: {len(e.inst)} instancias, {len(e.mallas)} mallas de la Rev. F, {time.time() - t:.0f} s")
    if "glb" in que:
        exportar_glb(e)
    if "step" in que:
        exportar_step(e)
    if "piezas" in que or "glb" in que:
        piezas(e, informe)


if __name__ == "__main__":
    main()
