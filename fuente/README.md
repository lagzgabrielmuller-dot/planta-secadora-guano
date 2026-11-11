# Fuentes del proyecto (entrega final, Rev. F del 11/11/2026)

Todo lo que se entrega en este repositorio sale de estos programas. Si cambia un dato, se corrige acá y se
vuelve a generar; nunca se editan a mano los DXF, PDF, PNG o DOCX de salida.

## Requisitos

- Python 3.11 o 3.12: `pip install -r ../requirements.txt` (cadquery, ezdxf, pymupdf, python-docx, openpyxl, pillow,
  numpy, matplotlib, trimesh, imageio-ffmpeg). El estudio térmico usa además numba y scipy
  (`simulacion_termica/requirements.txt`).
- Node.js con `npm install` en esta carpeta (`puppeteer-core`; para el visor del secador, `three` y `esbuild`).
- Google Chrome (Windows) o Chromium (Linux). `navegador.js` lo busca solo; si está en otro lado,
  definir la variable `CHROME_PATH`.
- Linux: ezdxf necesita Arial. Instalar `fonts-liberation`, copiar Liberation Sans como `~/.fonts/arial.ttf` (y
  negrita/cursiva) y correr una vez `python -c "from ezdxf.fonts import fonts; fonts.build_system_font_cache()"`.
  Las láminas que miden textos con PIL usan Liberation Sans si no hay Arial (`lamina_secadora.fuente_pil`).

## Orden para regenerar todo

Lo más simple: `python regenerar.py` (todo), `python regenerar.py --lista` (pasos) o
`python regenerar.py --desde planos`. Es lo mismo que estos comandos, desde `fuente/`:

```
# 1. Cálculos (todos los números que comparten planos, memoria, informe y portal)
python calculos/calculos_memoria.py        # -> calculos/resultados.json (incluye fatiga.py)
python calculos/presupuesto.py             # -> calculos/presupuesto.json y presupuesto/*.xlsx

# 2. Secador SC-4 aparte (CadQuery)
python secadora/modelo_secador.py          # -> secadora/modelo_3d/ (STEP, GLB, piezas.json)
node secadora/visor/build.mjs              # -> secadora/Visor_Secador_SC4.html (un solo archivo, sin internet)
node secadora/visor/capturas.js            # -> secadora/renders/ (vistas, despiece y 13 pasos de montaje)

# 3. Visor de la planta completa
python visor/build_visor.py                # base_revC.html + revD_modulo.js -> ../visor.html
node renders_visor.js ../visor.html ../modelo_3d/renders     # renders del plano 10 y del informe
node extraer_layout.js ../visor.html datos/layout_planta.json   # solo si cambió la planta

# 4. Planos
cd planos && python juego.py && cd ..      # P01 a P24 + Planos_Secadora_RevD.pdf
cd secadora && python planos_sc.py && cd ..   # SC-01 a SC-06 + Planos_Secador_SC4.pdf

# 5. Documentos
python calculos/memoria_docx.py            # memoria/Memoria_de_calculo_RevD.docx y .pdf
python informe/informe_final.py            # informe/Informe_Final_*.docx/.pdf y secadora/Manual_de_armado_SC4.*
python portal/portada.py                   # ../index.html (portada) y ../entrega.html (redirección)
```

Se puede regenerar solo una parte: `python planos/juego.py 10 23`, `python secadora/planos_sc.py 2 4`,
`node secadora/visor/capturas.js paso 1 9`, etc.

## Qué hace cada carpeta

| Carpeta | Contenido |
|---|---|
| `calculos/` | `calculos_memoria.py` (TG2, iluminación, ventilación, biogás, carga de fuego), `fatiga.py` (ejes, chavetas, bulones, anclajes y rodamientos según Shigley-Budynas 8.ª ed.; ensayo de Wöhler del apunte INET), `presupuesto.py` (inversión, pedido a la Cooperativa La Agrícola Regional, energía con la LAR y evaluación económica), `memoria_docx.py` |
| `planos/` | Un script por lámina (P01 a P24), `juego.py` y `lamina_secadora.py` (hoja A3 IRAM, rótulo, capas, tablas, cotas, globos, compresión de imágenes del PDF) |
| `secadora/` | `modelo_secador.py` (modelo CadQuery con motores, reductores, cárteres, consolas y anclajes), `proyecciones.py` (vistas con líneas ocultas, con caché en `_cache/`), `planos_sc.py`, `pasos_montaje.json` (13 pasos) y `visor/` (app three.js, plantilla, empaquetado y capturas) |
| `visor/` | Visor de la planta: `base_revC.html` (visor de la Rev. C tal como se entregó), `revD_modulo.js` (todo lo agregado: partes D y E, motores detallados, tableros, entorno de Crespo, vistas guiadas) y `build_visor.py` |
| `informe/` | `informe_final.py` arma el Word definitivo y el manual; `texto_revC.md` es el texto del informe de la Rev. C ya corregido (fuente editable); `extraer_revC.py` se usó una sola vez para sacarlo del Word original |
| `portal/` | `portada.py` arma la portada `index.html` desde la plantilla `portada.html` con los números de los cálculos, los tamaños de los archivos, las miniaturas de las láminas y los ZIP de los DXF |
| `video/` | Video de presentación: mapa satelital, armado animado de la planta y del secador, recorrido y créditos (ver `video/README.md`) |
| `*.js` | Scripts Node con Chrome sin ventana: `navegador.js` (ruta de Chrome y opciones WebGL), `imprimir_pdf.js`, `renders_visor.js`, `capturar_geometria.js`, `extraer_layout.js` |

## Notas

- Los PDF de la memoria, el informe y el manual se imprimen con Chrome desde un HTML equivalente al
  Word, porque el Word de la compu no se deja automatizar. Al abrir un .docx, Word pide actualizar los
  campos: aceptar para que se arme el índice.
- En Linux, Chrome sin placa de video necesita `--use-angle=swiftshader --enable-unsafe-swiftshader`
  para WebGL (ya está en `navegador.js`). Las capturas del visor tardan varios minutos.
- `geo.json` (de `capturar_geometria.js`) y `secadora/_cache/` son temporales y no se guardan.
- STEP de la planta completa: `node capturar_geometria.js ../visor.html geo.json` y
  `python modelo_step.py geo.json ../modelo_3d/Secadora_guano_RevD`; después rehacer el .zip.
