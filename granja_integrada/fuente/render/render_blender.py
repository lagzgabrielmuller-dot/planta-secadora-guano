"""Renders con Blender (Cycles, sin ventana) a partir del GLB del modelo.

    /home/user/.venvs/blender/bin/python render_blender.py vistas.json

`vistas.json`: {"glb": "...", "salida": "carpeta", "vistas": [{"nombre", "cam": [x,y,z], "mira": [x,y,z], "lente": 35,
"ancho": 1920, "alto": 1080, "muestras": 96, "ocultar": ["G:grupo", ...], "solo": [...], "sol": [azimut, altura],
"corte": {"plano": "x"|"y"|"z", "valor": m, "lado": 1}}]}

Coordenadas de cámara en metros del proyecto (x Este, y Norte, z arriba). Los materiales del GLB se mejoran por nombre
(chapas, rejillas, hormigón, pasto, vidrio, mallas) con nodos procedurales.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time

import bpy
from mathutils import Vector


def limpiar():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def nodo(nt, tipo, x=0, y=0):
    n = nt.nodes.new(tipo)
    n.location = (x, y)
    return n


def mejorar_material(mat):
    """Agrega textura procedural según el nombre del material (los colores y la rugosidad vienen del GLB)."""
    nombre = mat.name.split(".")[0]
    if not mat.use_nodes:
        return
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    tex = nt.nodes.new("ShaderNodeTexCoord")
    tex.location = (-900, 0)

    def ruido(escala, detalle=6.0, fuerza=0.15, rug=None):
        n = nodo(nt, "ShaderNodeTexNoise", -600, 200)
        n.inputs["Scale"].default_value = escala
        n.inputs["Detail"].default_value = detalle
        nt.links.new(tex.outputs["Object"], n.inputs["Vector"])
        b = nodo(nt, "ShaderNodeBump", -300, -200)
        b.inputs["Strength"].default_value = fuerza
        nt.links.new(n.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
        if rug is not None:
            mr = nodo(nt, "ShaderNodeMapRange", -300, 100)
            mr.inputs["To Min"].default_value = rug[0]
            mr.inputs["To Max"].default_value = rug[1]
            nt.links.new(n.outputs["Fac"], mr.inputs["Value"])
            nt.links.new(mr.outputs["Result"], bsdf.inputs["Roughness"])

    def ondas(escala, eje="X", fuerza=0.35):
        w = nodo(nt, "ShaderNodeTexWave", -600, -100)
        w.inputs["Scale"].default_value = escala
        w.bands_direction = eje
        w.wave_profile = "SAW" if False else "SIN"
        nt.links.new(tex.outputs["Object"], w.inputs["Vector"])
        b = nodo(nt, "ShaderNodeBump", -300, -200)
        b.inputs["Strength"].default_value = fuerza
        nt.links.new(w.outputs["Fac"], b.inputs["Height"])
        nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])

    if nombre in ("hormigon", "hormigon_piso", "revoque"):
        ruido(18.0, 8.0, 0.25, (0.75, 0.95))
    elif nombre in ("pasto",):
        ruido(3.0, 10.0, 0.6, (0.8, 1.0))
        mix = nodo(nt, "ShaderNodeTexNoise", -600, 400)
        mix.inputs["Scale"].default_value = 0.08
        ramp = nodo(nt, "ShaderNodeValToRGB", -300, 400)
        ramp.color_ramp.elements[0].color = (0.20, 0.30, 0.10, 1)
        ramp.color_ramp.elements[1].color = (0.42, 0.50, 0.22, 1)
        nt.links.new(tex.outputs["Object"], mix.inputs["Vector"])
        nt.links.new(mix.outputs["Fac"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    elif nombre in ("asfalto", "ripio", "tierra"):
        ruido(40.0, 10.0, 0.4, (0.85, 1.0))
    elif nombre in ("chapa_trap", "chapa_techo", "panel", "panel_galpon"):
        ondas(1.6 if nombre.startswith("chapa") else 0.8, "X", 0.25)
    elif nombre in ("galv", "inox", "aluminio", "acero"):
        ruido(60.0, 4.0, 0.03, (0.25, 0.45) if nombre == "galv" else None)
    elif nombre in ("guano", "guano_seco", "cascara", "biofiltro", "celulosa"):
        ruido(25.0, 12.0, 0.8, (0.85, 1.0))
    elif nombre in ("vidrio", "policarbonato", "agua"):
        bsdf.inputs["Transmission Weight"].default_value = 0.9
        bsdf.inputs["Roughness"].default_value = 0.05
    if nombre in ("luz",):
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.97, 0.9, 1)
        bsdf.inputs["Emission Strength"].default_value = 6.0


def preparar_escena(glb, sol=(225.0, 38.0), cielo=0.30, sol_w=3.0):
    bpy.ops.import_scene.gltf(filepath=glb)
    for m in bpy.data.materials:
        try:
            mejorar_material(m)
        except Exception as ex:          # un material que no se pueda mejorar no frena el render
            print("material", m.name, ex)
    # mundo: cielo físico + sol
    w = bpy.data.worlds.new("cielo")
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes["Background"]
    sky = nt.nodes.new("ShaderNodeTexSky")
    for tipo in ("MULTIPLE_SCATTERING", "NISHITA", "HOSEK_WILKIE"):
        try:
            sky.sky_type = tipo
            break
        except TypeError:
            continue
    try:
        sky.sun_elevation = math.radians(sol[1])
        sky.sun_rotation = math.radians(sol[0])
        sky.sun_disc = False            # el disco solar lo pone la lámpara: con los dos la escena se quema
    except AttributeError:
        pass
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = cielo
    luz = bpy.data.lights.new("sol", "SUN")
    luz.energy = sol_w
    luz.angle = math.radians(1.2)
    ob = bpy.data.objects.new("sol", luz)
    bpy.context.scene.collection.objects.link(ob)
    az, el = math.radians(sol[0]), math.radians(sol[1])
    d = Vector((math.cos(el) * math.sin(az), math.cos(el) * math.cos(az), math.sin(el)))
    ob.rotation_euler = d.to_track_quat("Z", "Y").to_euler()


def camara(nombre, cam, mira, lente=35.0):
    c = bpy.data.cameras.new(nombre)
    c.lens = lente
    c.clip_start = 0.05
    c.clip_end = 3000
    ob = bpy.data.objects.new(nombre, c)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = Vector(cam)
    d = Vector(mira) - Vector(cam)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = ob
    return ob


def visibilidad(v):
    ocultar = set(v.get("ocultar", []))
    solo = set(v.get("solo", []))
    for ob in bpy.data.objects:
        if ob.type not in ("MESH", "EMPTY"):
            continue
        raiz = ob
        while raiz.parent is not None:
            raiz = raiz.parent
        grupo = raiz.name.split(".")[0]
        oculto = bool(grupo in ocultar or (solo and grupo not in solo))
        ob.hide_render = oculto


def configurar_render(v):
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = int(v.get("muestras", 96))
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 6
    s.render.resolution_x = int(v.get("ancho", 1920))
    s.render.resolution_y = int(v.get("alto", 1080))
    s.render.resolution_percentage = 100
    s.render.image_settings.file_format = "PNG"
    try:
        s.view_settings.view_transform = "AgX"
        s.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        s.view_settings.view_transform = "Filmic"
    s.view_settings.exposure = float(v.get("exposicion", 0.0))
    s.render.threads_mode = "AUTO"


def main():
    spec = json.load(open(sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[1], encoding="utf-8"))
    limpiar()
    preparar_escena(spec["glb"], tuple(spec.get("sol", (225.0, 38.0))), float(spec.get("cielo", 0.30)),
                    float(spec.get("sol_w", 3.0)))
    os.makedirs(spec["salida"], exist_ok=True)
    for v in spec["vistas"]:
        t0 = time.time()
        visibilidad(v)
        camara("cam_" + v["nombre"], v["cam"], v["mira"], v.get("lente", 35.0))
        configurar_render(v)
        bpy.context.scene.render.filepath = os.path.join(spec["salida"], v["nombre"] + ".png")
        bpy.ops.render.render(write_still=True)
        print(f"render {v['nombre']}: {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
