"""Arma el visor 3D de la planta (visor.html, en la raíz del repositorio) a partir de:
  base_revC.html   visor de la Rev. C tal como se entregó (three.js minificado, "Secadora de Guano 3D.zip")
  revD_modulo.js   módulo con todo lo agregado desde la Rev. D (piezas, capas, vistas, lista de partes,
                   motores detallados, entorno de Crespo). Se edita este archivo, nunca el visor.html.

    python build_visor.py           # -> ../../visor.html

El módulo se inyecta antes de la línea que conecta los botones del menú, y la escena lo llama con
__revDBuild(grupo, partes, datos) apenas el visor arma la planta. Además se cambian tres textos
del visor original (revisión de las láminas, subtítulo y cantidad de planos).
"""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.abspath(os.path.join(AQUI, "..", "..", "visor.html"))

REEMPLAZOS = [
    ("He=F1(Za,vs,{planta:ii,avisar:r=>yc(r)}),", "He=F1(Za,vs,{planta:ii,avisar:r=>yc(r)}),__revDBuild(Za,He,vs),"),
    ('Zt("#m3d").onclick=()=>Cc("3d");', None),            # acá va el módulo (ver abajo)
    ("A3 \\xB7 Rev. C \\xB7 l\\xE1mina", "A3 \\xB7 Rev. ${e.rev||\"C\"} \\xB7 l\\xE1mina"),
    ("8 t/día · Rev. C", "8 t/día · Rev. D"),
    # Rev. F (estudio térmico del secador): temperaturas de trabajo y guías de PTFE en los pisos 2 y 3
    ('["Aire de secado","135 \\xB0C \\u2192 65 \\xB0C","26.600 kg/h (31.000 m\\xB3/h)"],["Generador","882 kW","314 kg/h de c\\xE1scara de arroz"]',
     '["Aire de secado","\\u2248 100 \\xB0C \\u2192 33 \\xB0C","m\\xE1x. 135 \\xB0C \\xB7 26.600 kg/h \\xB7 escape casi saturado"],'
     '["Generador","882 kW (m\\xE1x.)","\\u2248 220 kg/h de c\\xE1scara en el punto de trabajo (314 a 135 \\xB0C)"]'),
    ("\\u2248 314 kg/h para 882 kW.", "\\u2248 314 kg/h para 882 kW a 135 \\xB0C (en el punto de trabajo, \\u2248 220 kg/h y 617 kW)."),
    ('<li><i style="background:var(--hot)"></i>Aire caliente (135 °C)</li>',
     '<li><i style="background:var(--hot)"></i>Aire caliente (≈ 100 °C, máx. 135)</li>'),
    ("Aire húmedo a tratar (65 °C)", "Aire húmedo a tratar (33-37 °C, casi saturado)"),
    ('{n:"4.7",nom:"Gu\\xEDas UHMW-PE 40 \\xD7 20",txt:"5 por banda sobre travesa\\xF1os L 50\\xD750\\xD75 c/1,0 m."}',
     '{n:"4.7",nom:"Gu\\xEDas PTFE / UHMW-PE 40 \\xD7 20",txt:"PTFE en los pisos 2 y 3 y UHMW-PE en el 1 (Rev. F); 5 por '
     'banda sobre travesa\\xF1os L 50\\xD750\\xD75 c/1,0 m; faldones de sellado en los bordes."}'),
    ('class="count">12<', 'class="count">24<'),
]


def armar():
    html = open(os.path.join(AQUI, "base_revC.html"), encoding="utf-8").read()
    modulo = open(os.path.join(AQUI, "revD_modulo.js"), encoding="utf-8").read()
    for viejo, nuevo in REEMPLAZOS:
        if html.count(viejo) != 1:
            raise ValueError(f"el visor base cambió: no encuentro una sola vez {viejo!r}")
        if nuevo is None:
            nuevo = "\n/* ==== REV. D ==== */\n" + modulo.rstrip("\n") + "\n\n__revDSetup();\n/* ==== FIN REV. D ==== */\n" + viejo
        html = html.replace(viejo, nuevo)
    with open(SALIDA, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print(f"{SALIDA}: {len(html.encode('utf-8')) / 1e6:.2f} MB")


if __name__ == "__main__":
    armar()
