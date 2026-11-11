"""Regenera toda la entrega en el orden correcto (Windows, Linux o macOS).

    python regenerar.py                    # todo
    python regenerar.py calculos planos    # solo esos pasos, en el orden de abajo
    python regenerar.py --desde planos     # desde ese paso hasta el final
    python regenerar.py --lista            # muestra los pasos

Se corre desde `fuente/` con el entorno de Python activado (`pip install -r ../requirements.txt`) y después
de `npm ci`. Cada paso es el mismo comando que figura en `fuente/README.md`; si uno falla, se detiene.
"""
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

PASOS = [
    ("calculos", "Cálculos: resultados.json (TG2, iluminación, ventilación, biogás, fuego, fatiga)",
     [[PY, "calculos/calculos_memoria.py"]]),
    ("presupuesto", "Presupuesto: presupuesto.json y planilla Excel",
     [[PY, "calculos/presupuesto.py"]]),
    ("secador", "Secador SC-4 en CadQuery: STEP, GLB y piezas.json",
     [[PY, "secadora/modelo_secador.py"]]),
    ("visor_secador", "Visor del secador (un solo HTML, sin internet)",
     [["node", "secadora/visor/build.mjs"]]),
    ("capturas_secador", "Renders del secador: vistas, despiece y 13 pasos de montaje",
     [["node", "secadora/visor/capturas.js"]]),
    ("visor", "Visor 3D de la planta (visor.html)",
     [[PY, "visor/build_visor.py"]]),
    ("renders_visor", "Renders del visor de la planta (plano 10 e informe)",
     [["node", "renders_visor.js", "../visor.html", "../modelo_3d/renders"]]),
    ("planos", "Láminas P01 a P24 y juego completo en PDF",
     [[PY, "juego.py"]], "planos"),
    ("planos_sc", "Láminas del secador SC-01 a SC-06",
     [[PY, "planos_sc.py"]], "secadora"),
    ("memoria", "Memoria de cálculo (Word y PDF)",
     [[PY, "calculos/memoria_docx.py"]]),
    ("informe", "Informe final y manual de armado (Word y PDF)",
     [[PY, "informe/informe_final.py"]]),
    ("portal", "Página principal (index.html) con los números de los cálculos",
     [[PY, "portal/portada.py"]]),
]


def main(args):
    nombres = [p[0] for p in PASOS]
    if "--lista" in args:
        for p in PASOS:
            print(f"{p[0]:<18} {p[1]}")
        return 0
    if "--desde" in args:
        i = args.index("--desde")
        elegidos = nombres[nombres.index(args[i + 1]):]
    elif args:
        malos = [a for a in args if a not in nombres]
        if malos:
            print("Pasos desconocidos:", ", ".join(malos), "· usar --lista")
            return 2
        elegidos = [n for n in nombres if n in args]
    else:
        elegidos = nombres
    t_total = time.time()
    for paso in PASOS:
        nombre, desc, comandos = paso[:3]
        if nombre not in elegidos:
            continue
        carpeta = os.path.join(AQUI, paso[3]) if len(paso) > 3 else AQUI
        print(f"\n=== {nombre}: {desc}", flush=True)
        t0 = time.time()
        for cmd in comandos:
            r = subprocess.run(cmd, cwd=carpeta)
            if r.returncode != 0:
                print(f"*** Falló «{' '.join(cmd)}» (código {r.returncode})")
                return r.returncode
        print(f"--- {nombre} listo en {time.time() - t0:.0f} s", flush=True)
    print(f"\nTodo regenerado en {(time.time() - t_total) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
