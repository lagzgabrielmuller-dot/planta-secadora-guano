"""Arma la portada de la entrega (`index.html` en la raíz) desde la plantilla `portada.html`.

    python portal/portada.py            (desde fuente/)

- Los números marcados {{clave}} salen de calculos/resultados.json, presupuesto.json y del modelo del secador
  (piezas.json): si cambia un cálculo, la portada cambia sola.
- La lista de descargas se arma con el tamaño real de cada archivo (y las páginas de cada PDF).
- Arma las miniaturas de las 30 láminas (portal/img/planos/) y las fotos del secador (portal/img/sc_*.jpg) desde
  los PNG de los planos y los renders del visor del secador.
- Arma los ZIP de los DXF (P01-P24 y SC-01 a SC-06) con fecha fija, para que no cambien si no cambian los DXF.
- Controla que no quede ninguna clave sin reemplazar y que exista cada archivo enlazado.
- Escribe también `entrega.html`, que redirige a la portada (la dirección vieja sigue andando).
"""
import datetime
import json
import os
import re
import sys
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.dirname(AQUI)
RAIZ = os.path.dirname(FUENTE)
REPO_URL = "https://github.com/lagzgabrielmuller-dot/planta-secadora-guano"
SITIO_URL = "https://lagzgabrielmuller-dot.github.io/planta-secadora-guano/"


def leer_json(*partes):
    with open(os.path.join(*partes), encoding="utf-8") as f:
        return json.load(f)


def ar(x, dec=1):
    """Número con coma decimal y punto de miles."""
    return f"{x:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def mb(rel):
    return ar(os.path.getsize(os.path.join(RAIZ, rel)) / 1e6, 1) + " MB"


def paginas(rel):
    try:
        import pymupdf
    except ImportError:
        return None
    with pymupdf.open(os.path.join(RAIZ, rel)) as d:
        return d.page_count


def valores():
    r = leer_json(FUENTE, "calculos", "resultados.json")
    p = leer_json(FUENTE, "calculos", "presupuesto.json")
    piezas = leer_json(RAIZ, "secadora", "modelo_3d", "piezas.json")["piezas"]
    tg, b, v = r["tg2"], r["biogas"], r["ventilacion"]
    esc = {e["nombre"][0]: e for e in p["evaluacion"]["escenarios"]}
    return {
        "bio_m3": ar(b["biogas"], 0), "bio_kwh": ar(b["E_el"], 0), "bio_h": ar(b["horas"], 1),
        "bio_carga": ar(b["carga"], 2), "dig_cu": ar(b["V_dig_c_u"], 0),
        "tg2_kw": ar(tg["total_kW"], 2), "tg2_dem": ar(tg["demanda_tg2_kW"], 1), "tg2_idem": ar(tg["I_demanda_A"], 1),
        "ac_iz": ar(tg["acometida"]["Iz"], 1), "margen": ar(tg["balance"]["margen_sin_G1_pct"], 1),
        "lux": ar(r["iluminacion"]["E_real"], 0), "q_ex": ar(v["Q_real"], 0), "ren": ar(v["ren_real"], 1),
        "bf_area": ar(v["biofiltro"]["A"], 1), "bf_carga": ar(v["biofiltro"]["carga"], 0),
        "bf_t": ar(v["biofiltro"]["t_contacto"], 0),
        "masa_cad": ar(sum(x["masa_kg"] for x in piezas), 0), "n_piezas": str(len(piezas)),
        "uso_anclaje": ar(r["fatiga"]["anclajes"]["secador"]["uso_V_pct"], 1),
        "repago_C": ar(esc["C"]["repago"], 1), "tir_C": ar(esc["C"]["TIR"], 1),
        "repago_A": ar(esc["A"]["repago"], 1), "tir_A": ar(esc["A"]["TIR"], 1),
        "REPO_URL": REPO_URL, "SITIO_URL": SITIO_URL, "VERSION": datetime.date.today().strftime("%d/%m/%Y"),
    }


# ---- descargas: título, descripción y botones (texto, archivo, ¿se abre en otra pestaña?)
def filas():
    pag = {k: paginas(v) for k, v in (("informe", "informe/Informe_Final_Secadora_Guano.pdf"),
                                       ("memoria", "memoria/Memoria_de_calculo_RevD.pdf"),
                                       ("manual", "secadora/Manual_de_armado_SC4.pdf"))}
    n = lambda k, txt: f"{pag[k]} páginas, {txt}" if pag[k] else txt[0].upper() + txt[1:]   # noqa: E731
    return [
        ("Informe final", n("informe", "con los planos en anexo"),
         [("PDF", "informe/Informe_Final_Secadora_Guano.pdf", True), ("Word", "informe/Informe_Final_Secadora_Guano.docx", False)]),
        ("Memoria de cálculo", n("memoria", "tablero TG2, iluminación, ventilación, biogás y carga de fuego"),
         [("PDF", "memoria/Memoria_de_calculo_RevD.pdf", True), ("Word", "memoria/Memoria_de_calculo_RevD.docx", False)]),
        ("Manual de armado del secador", n("manual", "materiales, fijación al piso y montaje en 13 pasos"),
         [("PDF", "secadora/Manual_de_armado_SC4.pdf", True), ("Word", "secadora/Manual_de_armado_SC4.docx", False)]),
        ("Planos de la planta", "24 láminas A3 (IRAM): juego completo en PDF y cada lámina en DXF para AutoCAD",
         [("PDF", "planos/pdf/Planos_Secadora_RevD.pdf", True), ("DXF", "planos/dxf/Planos_DXF_P01-P24.zip", False)]),
        ("Planos del secador SC-4", "Láminas SC-01 a SC-06 con vistas, cortes, despiece y montaje",
         [("PDF", "secadora/planos/pdf/Planos_Secador_SC4.pdf", True), ("DXF", "secadora/planos/dxf/Planos_DXF_SC-01-SC-06.zip", False)]),
        ("Presupuesto", "Inversión, pedido a la Cooperativa LAR, energía y evaluación económica",
         [("Excel", "presupuesto/Presupuesto_Secadora_Guano.xlsx", False)]),
        ("Modelos 3D", "Secador SC-4 en STEP (SolidWorks, Fusion 360) y GLB (Blender); planta completa en STEP",
         [("STEP secador", "secadora/modelo_3d/Secador_SC4.step", False), ("GLB", "secadora/modelo_3d/Secador_SC4.glb", False),
          ("STEP planta", "modelo_3d/Secadora_guano_RevD_step.zip", False)]),
        ("Video de presentación", "3:51 en 1080p a 60 cuadros por segundo (versión sin música para la web)",
         [("MP4 1080p", "video/Secadora_guano_presentacion_1080p60.mp4", True), ("MP4 720p", "video/Secadora_guano_presentacion_720p.mp4", True)]),
    ]


ICONO_BAJAR = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" '
               'stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>')


def html_filas():
    out = ['<ul class="filas">']
    for titulo, desc, botones in filas():
        b = []
        for txt, rel, abrir in botones:
            nombre = os.path.basename(rel)
            if abrir:
                b.append(f'<a class="campo" href="{rel}" target="_blank" rel="noopener">{txt} <small>{mb(rel)}</small> ↗</a>'
                         f'<a class="campo campo-bajar" href="{rel}" download="{nombre}" data-descargar="{nombre}" '
                         f'aria-label="Descargar {txt} de {titulo.lower()}" title="Descargar">{ICONO_BAJAR}</a>')
            else:
                b.append(f'<a class="campo" href="{rel}" download="{nombre}" data-descargar="{nombre}" '
                         f'aria-label="Descargar {txt} de {titulo.lower()}">{txt} <small>{mb(rel)}</small> {ICONO_BAJAR}</a>')
        out.append(f'<li class="fila"><div><strong>{titulo}</strong><span>{desc}</span></div>'
                   f'<div class="fila-botones">{"".join(b)}</div></li>')
    out.append("</ul>")
    return "".join(out)


def zip_fijo(destino, archivos):
    """ZIP con fecha fija: mismo contenido, mismo archivo (no ensucia el repositorio)."""
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for ruta in archivos:
            info = zipfile.ZipInfo(os.path.basename(ruta), date_time=(2026, 10, 23, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(ruta, "rb") as f:
                z.writestr(info, f.read())


def zips_dxf():
    for carpeta, patron, nombre in (("planos/dxf", r"P\d\d\.dxf$", "Planos_DXF_P01-P24.zip"),
                                    ("secadora/planos/dxf", r"SC-\d\d\.dxf$", "Planos_DXF_SC-01-SC-06.zip")):
        d = os.path.join(RAIZ, carpeta)
        dxf = sorted(os.path.join(d, f) for f in os.listdir(d) if re.match(patron, f))
        zip_fijo(os.path.join(d, nombre), dxf)


def miniaturas():
    """JPG de 1800 px de ancho de cada lámina para la galería de planos de la portada."""
    from PIL import Image
    salida = os.path.join(RAIZ, "portal", "img", "planos")
    os.makedirs(salida, exist_ok=True)
    pares = [(os.path.join(RAIZ, "planos", f"P{i:02d}.png"), f"P{i:02d}.jpg") for i in range(1, 25)]
    pares += [(os.path.join(RAIZ, "secadora", "planos", f"SC-{i:02d}.png"), f"SC-{i:02d}.jpg") for i in range(1, 7)]
    for png, jpg in pares:
        im = Image.open(png).convert("RGB")
        im.thumbnail((1800, 1800), Image.LANCZOS)
        im.save(os.path.join(salida, jpg), "JPEG", quality=84, optimize=True, progressive=True)
    # fotos del secador SC-4 en la portada: salen de los renders del visor del secador (modelo CadQuery vigente)
    for nombre in ("general", "interior", "despiece", "accionamiento"):
        im = Image.open(os.path.join(RAIZ, "secadora", "renders", f"SC_{nombre}.png")).convert("RGB")
        im.thumbnail((1600, 1600), Image.LANCZOS)
        im.save(os.path.join(RAIZ, "portal", "img", f"sc_{nombre}.jpg"), "JPEG", quality=86, optimize=True, progressive=True)


REDIRECCION = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><title>Planta Secadora de Guano</title>
<meta http-equiv="refresh" content="0; url=index.html"><link rel="canonical" href="index.html"></head>
<body><p>La portada de la entrega ahora es <a href="index.html">index.html</a>.</p></body></html>
"""


def revisiones():
    """Letra de la revisión vigente de cada lámina, leída de su programa (la última fila de su tabla revs)."""
    letras = {}
    for i in range(1, 25):
        with open(os.path.join(FUENTE, "planos", f"P{i:02d}.py"), encoding="utf-8") as f:
            filas = re.findall(r'\("([A-Z])",\s*(?:FECHA|"[^"]*")\s*,\s*"', f.read())
        if filas:
            letras[f"P{i:02d}"] = filas[-1]
    with open(os.path.join(FUENTE, "secadora", "planos_sc.py"), encoding="utf-8") as f:
        sc = re.search(r"REVS = \[(.*?)\]\n", f.read(), re.S).group(1)
    letra_sc = re.findall(r'\("([A-Z])"', sc)[-1]
    letras.update({f"SC-{i:02d}": letra_sc for i in range(1, 7)})
    return letras


def con_revisiones(s):
    """Pone en los epígrafes de la galería de planos la revisión vigente de cada lámina."""
    letras = revisiones()
    m = re.search(r'(<script type="application/json" id="datos">)(.*?)(</script>)', s, re.S)
    datos = json.loads(m.group(2))
    for p in datos["planos"]:
        lam = p["cap"].split(" · ")[0]
        if lam in letras:
            p["cap"] = re.sub(r"Rev\. [A-Z]$", f"Rev. {letras[lam]}", p["cap"])
    return s[:m.start(2)] + json.dumps(datos, ensure_ascii=False) + s[m.end(2):]


def main():
    zips_dxf()
    miniaturas()
    with open(os.path.join(AQUI, "portada.html"), encoding="utf-8") as f:
        s = f.read()
    s = con_revisiones(s)
    v = valores()
    v["FILAS_DESCARGAS"] = html_filas()
    s = re.sub(r"\{\{(\w+)\}\}", lambda m: v[m.group(1)], s)
    sobran = re.findall(r"\{\{\w+\}\}", s)
    assert not sobran, f"claves sin reemplazar: {sobran}"
    # cada archivo enlazado tiene que existir
    refs = set(re.findall(r'(?:href|src|data-src|data-pdf)="([^"#]+)"', s))
    refs |= set(re.findall(r'"(?:src|pdf)": "([^"]+)"', s))
    faltan = sorted(r for r in refs if not re.match(r"(https?:|mailto:|data:)", r) and not os.path.exists(os.path.join(RAIZ, r)))
    if faltan:
        print("Faltan archivos enlazados desde la portada:", *faltan, sep="\n  ")
        return 1
    with open(os.path.join(RAIZ, "index.html"), "w", encoding="utf-8") as f:
        f.write(s)
    with open(os.path.join(RAIZ, "entrega.html"), "w", encoding="utf-8") as f:
        f.write(REDIRECCION)
    print(f"index.html listo ({len(s) / 1e3:.0f} kB, {len(refs)} enlaces controlados) y entrega.html (redirección)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
