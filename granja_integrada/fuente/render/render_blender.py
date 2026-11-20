"""Renders con Blender (Cycles, sin ventana) a partir del GLB del modelo.

    /home/user/.venvs/blender/bin/python render_blender.py vistas.json

`vistas.json`: {"glb": "...", "salida": "carpeta", "vistas": [{"nombre", "cam": [x,y,z], "mira": [x,y,z], "lente": 35,
"ancho": 1920, "alto": 1080, "muestras": 96, "ocultar": ["G:grupo", ...], "solo": [...], "sol": [azimut, altura],
"transparentes": [...], "alfa_transparentes": 0.1, "exposicion": 0.0}]}

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


def malla_alambre(nt, bsdf, tex, paso=0.025, alambre=0.12):
    """Alfa de malla electrosoldada: alambres cada `paso` m sobre los dos ejes del plano de cada cara."""
    sep = nodo(nt, "ShaderNodeSeparateXYZ", -700, -400)
    nt.links.new(tex.outputs["Object"], sep.inputs["Vector"])
    nsep = nodo(nt, "ShaderNodeSeparateXYZ", -700, -600)
    nt.links.new(tex.outputs["Normal"], nsep.inputs["Vector"])
    total = None
    for eje in ("X", "Y", "Z"):
        m = nodo(nt, "ShaderNodeMath", -560, -400)
        m.operation = "MULTIPLY"
        m.inputs[1].default_value = 1.0 / paso
        nt.links.new(sep.outputs[eje], m.inputs[0])
        f = nodo(nt, "ShaderNodeMath", -460, -400)
        f.operation = "FRACT"
        nt.links.new(m.outputs[0], f.inputs[0])
        lt = nodo(nt, "ShaderNodeMath", -360, -400)
        lt.operation = "LESS_THAN"
        lt.inputs[1].default_value = alambre
        nt.links.new(f.outputs[0], lt.inputs[0])
        # el eje solo cuenta si está en el plano de la cara (|n| chico en ese eje)
        an = nodo(nt, "ShaderNodeMath", -560, -600)
        an.operation = "ABSOLUTE"
        nt.links.new(nsep.outputs[eje], an.inputs[0])
        enp = nodo(nt, "ShaderNodeMath", -460, -600)
        enp.operation = "LESS_THAN"
        enp.inputs[1].default_value = 0.5
        nt.links.new(an.outputs[0], enp.inputs[0])
        mul = nodo(nt, "ShaderNodeMath", -260, -500)
        mul.operation = "MULTIPLY"
        nt.links.new(lt.outputs[0], mul.inputs[0])
        nt.links.new(enp.outputs[0], mul.inputs[1])
        if total is None:
            total = mul
        else:
            mx = nodo(nt, "ShaderNodeMath", -160, -500)
            mx.operation = "MAXIMUM"
            nt.links.new(total.outputs[0], mx.inputs[0])
            nt.links.new(mul.outputs[0], mx.inputs[1])
            total = mx
    nt.links.new(total.outputs[0], bsdf.inputs["Alpha"])


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
        ramp.color_ramp.elements[0].color = (0.045, 0.085, 0.020, 1)     # lineal: pasto de campo entrerriano
        ramp.color_ramp.elements[1].color = (0.110, 0.160, 0.045, 1)
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
    if nombre in ("malla",):
        malla_alambre(nt, bsdf, tex, paso=0.025, alambre=0.12)
    if nombre in ("luz",):
        bsdf.inputs["Emission Color"].default_value = (1.0, 0.97, 0.9, 1)
        bsdf.inputs["Emission Strength"].default_value = 40.0
    if nombre in ("gallina",):
        ruido(120.0, 8.0, 0.5, (0.8, 1.0))                  # plumaje


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


_FANTASMA = {}


def fantasma(rgb=(0.72, 0.78, 0.86), alfa=0.10):
    """Material semitransparente para mostrar un grupo como contexto (vistas técnicas y eléctricas)."""
    clave = (tuple(rgb), alfa)
    if clave not in _FANTASMA:
        m = bpy.data.materials.new(f"fantasma_{len(_FANTASMA)}")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*rgb, 1.0)
        b.inputs["Alpha"].default_value = alfa
        b.inputs["Roughness"].default_value = 0.6
        _FANTASMA[clave] = m
    return _FANTASMA[clave]


_RESALTE = {}


def resalte(rgb):
    """Material de color pleno con algo de emisión para destacar un sistema (eléctrica, recorrido del guano)."""
    clave = tuple(rgb)
    if clave not in _RESALTE:
        m = bpy.data.materials.new(f"resalte_{len(_RESALTE)}")
        m.use_nodes = True
        b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        b.inputs["Base Color"].default_value = (*rgb, 1.0)
        b.inputs["Emission Color"].default_value = (*rgb, 1.0)
        b.inputs["Emission Strength"].default_value = 0.6
        b.inputs["Roughness"].default_value = 0.5
        _RESALTE[clave] = m
    return _RESALTE[clave]


def visibilidad(v):
    """ocultar: grupos que no se ven; solo: únicos grupos que se ven; transparentes: grupos en fantasma (contexto);
    resaltar: {grupo: [r, g, b]} grupos en color pleno."""
    ocultar = set(v.get("ocultar", []))
    solo = set(v.get("solo", []))
    transp = set(v.get("transparentes", []))
    resaltar = v.get("resaltar", {})
    alfa = float(v.get("alfa_transparentes", 0.10))
    for ob in bpy.data.objects:
        if ob.type not in ("MESH", "EMPTY"):
            continue
        raiz = ob
        while raiz.parent is not None:
            raiz = raiz.parent
        grupo = raiz.name.split(".")[0]
        oculto = bool(grupo in ocultar or (solo and grupo not in solo and grupo not in transp))
        ob.hide_render = oculto
        if ob.type == "MESH":
            for slot in ob.material_slots:
                if grupo in resaltar:
                    slot.link = "OBJECT"
                    slot.material = resalte(resaltar[grupo])
                elif grupo in transp:
                    slot.link = "OBJECT"
                    slot.material = fantasma(alfa=alfa)
                else:
                    slot.link = "DATA"


def configurar_render(v):
    s = bpy.context.scene
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = int(v.get("muestras", 96))
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 6
    s.cycles.transparent_max_bounces = 48              # mallas de jaulas y guardas superpuestas
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
