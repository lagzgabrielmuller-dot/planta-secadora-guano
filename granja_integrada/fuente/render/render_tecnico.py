"""Vistas técnicas ortográficas a escala (plantas, cortes, elevaciones y despieces) con Blender Workbench.

    /home/user/.venvs/blender/bin/python render_tecnico.py vistas.json

`vistas.json`: {"glb": "...", "salida": "carpeta", "px_por_m": 60, "vistas": [
   {"nombre": "...", "centro": [x, y, z], "mira": "abajo|norte|sur|este|oeste|[dx,dy,dz]",
    "ancho_m": 18, "alto_m": 12, "fondo_m": 200, "ocultar": [...], "solo": [...], "transparentes": [...],
    "color": "material|gris", "px_por_m": 60, "perspectiva": false}]}

Con "auto": true la cámara se encuadra sola sobre lo visible (centro, ancho_m y alto_m salen de la caja de los objetos
proyectada en los ejes de la imagen, con un margen "margen" de 4 %); "px_ancho" fija el ancho de la imagen en píxeles.

La cámara se pone en el plano de corte (centro) y mira hacia adentro: lo que queda detrás de la cámara no se ve, así
una planta "a +5,40 m" es la cámara a 5,40 m mirando hacia abajo y un corte es la cámara sobre el plano del corte.
Cada imagen sale con fondo transparente y un .json con la escala (m por píxel) y los ejes de la imagen, para ubicarla
a escala en la lámina y poner encima globos, cotas y niveles.
"""
from __future__ import annotations

import json
import math
import os
import sys

import bpy
from mathutils import Vector

DIRS = {"abajo": ((0, 0, -1), (0, 1, 0)), "norte": ((0, 1, 0), (0, 0, 1)), "sur": ((0, -1, 0), (0, 0, 1)),
        "este": ((1, 0, 0), (0, 0, 1)), "oeste": ((-1, 0, 0), (0, 0, 1))}


def preparar(glb):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=glb)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_object_outline = True
    sh.object_outline_color = (0.08, 0.08, 0.08)
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.cavity_ridge_factor = 1.0
    sh.cavity_valley_factor = 1.0
    sh.show_specular_highlight = False
    try:
        sh.show_shadows = False
    except AttributeError:
        pass
    sc.display.render_aa = "16"
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"


def raiz(ob):
    while ob.parent is not None:
        ob = ob.parent
    return ob.name.split(".")[0]


_GRIS = {}


def material_gris(alfa=1.0):
    if alfa not in _GRIS:
        m = bpy.data.materials.new(f"gris_{alfa}")
        m.diffuse_color = (0.86, 0.87, 0.88, alfa)
        _GRIS[alfa] = m
    return _GRIS[alfa]


def visibilidad(v):
    ocultar, solo, transp = set(v.get("ocultar", [])), set(v.get("solo", [])), set(v.get("transparentes", []))
    gris = v.get("color") == "gris"
    for ob in bpy.data.objects:
        if ob.type not in ("MESH", "EMPTY"):
            continue
        g = raiz(ob)
        ob.hide_render = bool(g in ocultar or (solo and g not in solo and g not in transp))
        if ob.type == "MESH":
            for slot in ob.material_slots:
                if g in transp:
                    slot.link = "OBJECT"
                    slot.material = material_gris(0.25)
                elif gris:
                    slot.link = "OBJECT"
                    slot.material = material_gris(1.0)
                else:
                    slot.link = "DATA"
    sh = bpy.context.scene.display.shading
    sh.color_type = "MATERIAL"
    try:
        sh.show_xray = bool(transp)
        sh.xray_alpha = 0.35
    except AttributeError:
        pass


def encuadre_auto(v, d, der, arr):
    """Caja de lo visible en los ejes de la cámara: devuelve (punto central adelante, ancho, alto, profundidad)."""
    pts = []
    for ob in bpy.data.objects:
        if ob.type != "MESH" or ob.hide_render:
            continue
        mw = ob.matrix_world
        pts += [mw @ Vector(c) for c in ob.bound_box]
    us, vs, ss = [p.dot(der) for p in pts], [p.dot(arr) for p in pts], [p.dot(d) for p in pts]
    m = float(v.get("margen", 0.04))
    w, h = max(us) - min(us), max(vs) - min(vs)
    c = der * ((max(us) + min(us)) / 2) + arr * ((max(vs) + min(vs)) / 2) + d * min(ss)
    return c, w * (1 + 2 * m), h * (1 + 2 * m), max(ss) - min(ss)


def camara(v):
    mira = v.get("mira", "abajo")
    if isinstance(mira, str):
        d, up = DIRS[mira]
    else:
        d, up = tuple(mira), tuple(v.get("arriba", (0, 0, 1)))
    d, up = Vector(d).normalized(), Vector(up).normalized()
    c = bpy.data.cameras.new(v["nombre"])
    if v.get("perspectiva"):
        c.type = "PERSP"
        c.lens = v.get("lente", 35)
    else:
        c.type = "ORTHO"
        c.ortho_scale = v.get("ancho_m", 1.0)
    c.sensor_fit = "HORIZONTAL"
    c.clip_start = v.get("clip_m", 0.001)
    c.clip_end = v.get("fondo_m", 500.0)
    ob = bpy.data.objects.new(v["nombre"], c)
    bpy.context.scene.collection.objects.link(ob)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.view_layer.update()
    m = ob.matrix_world
    derecha = (m.to_3x3() @ Vector((1, 0, 0))).normalized()
    arriba = (m.to_3x3() @ Vector((0, 1, 0))).normalized()
    if v.get("auto"):
        centro, ancho, alto, prof = encuadre_auto(v, d, derecha, arriba)
        v["centro"] = [round(x, 4) for x in centro]
        v["ancho_m"], v["alto_m"] = round(ancho, 4), round(alto, 4)
        v.setdefault("retiro_m", 20.0)
        c.ortho_scale = v["ancho_m"]
        c.clip_end = v["retiro_m"] + prof + 10.0
    ob.location = Vector(v["centro"]) - (d * v.get("retiro_m", 0.0))
    bpy.context.view_layer.update()
    bpy.context.scene.camera = ob
    return ob, derecha, arriba


def main():
    spec = json.load(open(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[1], encoding="utf-8"))
    preparar(spec["glb"])
    os.makedirs(spec["salida"], exist_ok=True)
    for v in spec["vistas"]:
        visibilidad(v)
        ob, der, arr = camara(v)
        ppm = (float(v["px_ancho"]) / v["ancho_m"]) if v.get("px_ancho") else float(v.get("px_por_m", spec.get("px_por_m", 60)))
        W = max(16, int(round(v["ancho_m"] * ppm)))
        H = max(16, int(round(v["alto_m"] * ppm)))
        sc = bpy.context.scene
        sc.render.resolution_x, sc.render.resolution_y = W, H
        sc.render.resolution_percentage = 100
        ruta = os.path.join(spec["salida"], v["nombre"] + ".png")
        sc.render.filepath = ruta
        bpy.ops.render.render(write_still=True)
        meta = {"ancho_m": v["ancho_m"], "alto_m": v["ancho_m"] * H / W, "px": [W, H], "centro": list(v["centro"]),
                "derecha": [round(x, 6) for x in der], "arriba": [round(x, 6) for x in arr]}
        json.dump(meta, open(os.path.join(spec["salida"], v["nombre"] + ".json"), "w"), indent=1)
        print(f"vista {v['nombre']}: {W} × {H} px", flush=True)


if __name__ == "__main__":
    main()
