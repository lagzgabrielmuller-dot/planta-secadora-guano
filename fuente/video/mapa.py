"""Mapa del video: imágenes satelitales en cuatro niveles de detalle (región, Crespo, Parque Industrial y
lote) más los datos de OpenStreetMap para carteles, rutas y distancias.

    python mapa.py      # -> datos/mapa_L0..L3.jpg y datos/mapa.json

Imágenes: Esri World Imagery (fuentes: Esri, Maxar, Earthstar Geographics). Calles y lugares: © colaboradores
de OpenStreetMap (ODbL). Las teselas se guardan en _teselas/ para no volver a bajarlas.

Ubicación del lote: ORIENTATIVA (plano 14): campo al Noreste de la RN 12, frente al Parque Industrial de Crespo,
junto a la continuación de la calle Democracia. Se debe confirmar la parcela con la Municipalidad.
Ejes del video (los del visor): x al Este, y arriba, z al Sur, en metros; origen en el vértice SO de la nave.
"""
import json
import math
import os
import time
import urllib.request
import xml.etree.ElementTree as ET

from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
TESELAS = os.path.join(AQUI, "_teselas")
DATOS = os.path.join(AQUI, "datos")
UA = "SecadoraGuano-ProyectoEscolar/1.0 (EPNMyS 35 Crespo)"
URL = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

# centro del predio (120 × 76 m) y su posición en las coordenadas de la planta
LOTE = (-32.00543, -60.30751)
CENTRO_PREDIO_PLANTA = (38.0, 2.0)       # x Este, y Norte (m) desde el vértice SO de la nave
R_LAT = 110_900.0                         # m por grado de latitud a 32° S
R_LON = 111_320.0 * math.cos(math.radians(32.005))

ORIGEN = (LOTE[0] - CENTRO_PREDIO_PLANTA[1] / R_LAT, LOTE[1] - CENTRO_PREDIO_PLANTA[0] / R_LON)

# niveles: (nombre, lat sur, lon oeste, lat norte, lon este, zoom de las teselas, lado máximo de la textura)
NIVELES = [
    ("Lf", -32.75, -61.20, -31.30, -59.50, 11, 2560),     # fondo: centro de Entre Ríos (para las tomas más altas)
    ("L0", -32.21, -60.64, -31.68, -60.19, 12, 2048),    # región: Crespo, Paraná y la RN 12
    ("L1", -32.065, -60.365, -31.968, -60.245, 16, 3584), # Crespo
    ("L2", -32.024, -60.333, -31.990, -60.287, 17, 4096), # Parque Industrial
    ("L3", -32.0118, -60.3165, -31.9990, -60.2985, 18, 4096),  # lote
]

LUGARES = {   # lat, lon (OpenStreetMap / Nominatim)
    "Paraná": (-31.7319, -60.5238),
    "Crespo": (-32.0293, -60.3070),          # plaza central (centro de la planta urbana)
    "Parque Industrial Crespo": (-32.0050, -60.3150),
    "Nogoyá (por RN 12)": (-32.3930, -59.7880),
}


def a_mundo(lat, lon):
    """lat/lon -> (x Este, z Sur) en metros del video."""
    return ((lon - ORIGEN[1]) * R_LON, -(lat - ORIGEN[0]) * R_LAT)


def xy(lat, lon, z):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def tesela(z, x, y):
    ruta = os.path.join(TESELAS, f"{z}_{x}_{y}.jpg")
    if not os.path.exists(ruta):
        req = urllib.request.Request(URL.format(z=z, x=x, y=y), headers={"User-Agent": UA})
        for i in range(5):
            try:
                with urllib.request.urlopen(req, timeout=40) as r:
                    open(ruta, "wb").write(r.read())
                break
            except Exception:
                time.sleep(2 ** i)
    return Image.open(ruta).convert("RGB")


def nivel(nom, lat0, lon0, lat1, lon1, z, lado):
    x0, y0 = xy(lat1, lon0, z)
    x1, y1 = xy(lat0, lon1, z)
    tx0, ty0, tx1, ty1 = int(x0), int(y0), int(x1), int(y1)
    im = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    for tx in range(tx0, tx1 + 1):
        for ty in range(ty0, ty1 + 1):
            im.paste(tesela(z, tx, ty), ((tx - tx0) * 256, (ty - ty0) * 256))
    im = im.crop((round((x0 - tx0) * 256), round((y0 - ty0) * 256), round((x1 - tx0) * 256), round((y1 - ty0) * 256)))
    if max(im.size) > lado:
        k = lado / max(im.size)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
    im.save(os.path.join(DATOS, f"mapa_{nom}.jpg"), quality=88)
    xo, zs = a_mundo(lat0, lon0)            # esquina SO
    xe, zn = a_mundo(lat1, lon1)            # esquina NE
    print(f"{nom}: {im.size} px, {(xe - xo) / 1000:.1f} × {(zs - zn) / 1000:.1f} km")
    return {"nombre": nom, "x0": xo, "x1": xe, "zN": zn, "zS": zs, "px": im.size}


def osm(bbox, nombre):
    ruta = os.path.join(TESELAS, nombre)
    if not os.path.exists(ruta):
        url = "https://api.openstreetmap.org/api/0.6/map?bbox=" + ",".join(f"{v:.4f}" for v in bbox)
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        open(ruta, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    return ET.parse(ruta).getroot()


def vias(raiz, filtro):
    nodos = {n.get("id"): (float(n.get("lat")), float(n.get("lon"))) for n in raiz.iter("node")}
    res = []
    for w in raiz.iter("way"):
        tags = {t.get("k"): t.get("v") for t in w.findall("tag")}
        if filtro(tags):
            pts = [nodos[n.get("ref")] for n in w.findall("nd") if n.get("ref") in nodos]
            res.append({"tags": tags, "pts": [a_mundo(*p) for p in pts]})
    return res


def dist_km(a, b):
    return math.hypot((a[0] - b[0]) * R_LAT, (a[1] - b[1]) * R_LON) / 1000


def main():
    os.makedirs(TESELAS, exist_ok=True)
    os.makedirs(DATOS, exist_ok=True)
    niveles = [nivel(*n) for n in NIVELES]
    raiz = osm((-60.335, -32.025, -60.285, -31.990), "osm_pic.osm")
    rn12 = vias(raiz, lambda t: t.get("ref") == "RN12" or t.get("name") == "Ruta Nacional 12")
    pic = vias(raiz, lambda t: t.get("landuse") == "industrial")
    calles = vias(raiz, lambda t: t.get("name") in ("Democracia", "Brigadier General Juan Manuel de Rosas"))
    # distancia del lote a la RN 12 (al punto más cercano de la traza)
    lx, lz = a_mundo(*LOTE)
    d_rn = min(math.hypot(x - lx, z - lz) for v in rn12 for x, z in v["pts"])
    datos = {
        "origen": ORIGEN, "lote": LOTE, "lote_mundo": [lx, lz], "niveles": niveles,
        "lugares": {k: {"latlon": v, "xz": a_mundo(*v), "km": round(dist_km(LOTE, v), 1)} for k, v in LUGARES.items()},
        "rn12": [v["pts"] for v in rn12], "pic": [v["pts"] for v in pic], "calles": [v["pts"] for v in calles],
        "dist_rn12_m": round(d_rn), "creditos": "Imágenes: Esri, Maxar, Earthstar Geographics · Mapa: © colaboradores de OpenStreetMap",
    }
    json.dump(datos, open(os.path.join(DATOS, "mapa.json"), "w", encoding="utf-8"), ensure_ascii=False)
    print("origen", ORIGEN, "| RN 12 a", datos["dist_rn12_m"], "m |",
          {k: v["km"] for k, v in datos["lugares"].items()})


if __name__ == "__main__":
    main()
