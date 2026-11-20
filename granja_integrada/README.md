# Granja integrada · secado de guano y 4 galpones (Rev. A)

Rediseño de la planta de secado de guano de la Rev. F como **planta central de una granja de gallinas ponedoras**:
cuatro galpones automáticos de 36.000 gallinas en una fila Oeste-Este (G1, G2, planta, G3, G4), transporte
automático del guano por cintas hasta una tolva pulmón, secador SC-4 de la Rev. F sin cambios de forma, instalación
eléctrica, automatización, modelo 3D, renders, despieces y 20 láminas. El sistema de biogás de la Rev. D se elimina.

Todo lo de esta carpeta es nuevo. El proyecto anterior (la raíz del repositorio) **no se modificó**: de ahí solo se
leen funciones y datos (formato de las láminas y de la memoria, modelo del SC-4).

| Para ver | Dónde |
|---|---|
| Visor 3D (granja, planta, galpón tipo y secador) | [`index.html`](index.html) · en GitHub Pages: `/granja_integrada/` |
| Memoria técnica (37 páginas) | [`memoria/Memoria_tecnica_granja_integrada.pdf`](memoria/Memoria_tecnica_granja_integrada.pdf) y `.docx` |
| Láminas GI-01 a GI-20 (A3) | [`planos/Planos_GI.pdf`](planos/Planos_GI.pdf) · una por una en `planos/pdf/` y `planos/*.png` |
| Láminas en DXF | [`planos/dxf/Planos_DXF_GI.zip`](planos/dxf/Planos_DXF_GI.zip) (DXF con sus imágenes en `img/`) |
| Modelo STEP (SolidWorks, Fusion 360) | [`modelo_3d/Granja_integrada_STEP.zip`](modelo_3d/Granja_integrada_STEP.zip) |
| Listas de motores, instrumentos, alimentadores y E/S | [`documentacion/Listas_granja_integrada.xlsx`](documentacion/Listas_granja_integrada.xlsx) |
| Renders | [`renders/`](renders/) (R01 a R15) |
| Secador SC-4: planos de fabricación SC-01 a SC-06, manual de armado y visor | [`../secadora/`](../secadora/) (Rev. F, sin cambios) |

## Carpetas

| Carpeta | Contenido |
|---|---|
| `datos/` | `granja.json` (medidas y ubicaciones), `calculos.json` (balance, ventilación, cintas), `electrica.json` (balance de potencia, alimentadores, motores, instrumentos, E/S, automatización) y `piezas.json` (lista de piezas del 3D). Son la única fuente de números: 3D, planos, memoria y planilla leen de acá. |
| `fuente/` | Programas que generan todo (ver abajo). `fuente/modelo/` arma el 3D con CadQuery; `fuente/planos/` las láminas; `fuente/render/` los renders y las vistas técnicas, con sus especificaciones en `fuente/render/vistas/`. |
| `modelo_3d/` | GLB de la granja, la planta central, el galpón tipo y el secador; STEP en zip; despieces (`despieces/*.glb` y `*.json` con la lista numerada). |
| `planos/` | Láminas en PNG, PDF (una por una y juntas) y DXF; `img_tecnicas/` tiene las vistas ortográficas del modelo que usan las láminas. |
| `memoria/` | Memoria técnica en Word y PDF. |
| `documentacion/` | Planilla de listas (Excel, con fórmulas de totales y de verificación). |
| `renders/` | Renders en JPG (Blender Cycles). |
| `docs/` | Auditoría inicial del proyecto anterior y croquis de implantación. |

## Cómo se regenera

Con el Python que tiene CadQuery, trimesh, ezdxf, pymupdf, python-docx y openpyxl, y con Blender como módulo de
Python (`bpy`) para los renders. Los comandos se corren desde `granja_integrada/`:

```bash
python fuente/datos_granja.py              # datos/granja.json
python fuente/calculos_granja.py           # datos/calculos.json
python fuente/electrica_granja.py          # datos/electrica.json
python fuente/ensamblar.py                 # modelo_3d/*.glb, STEP y datos/piezas.json
python fuente/despieces.py                 # modelo_3d/despieces/
# vistas técnicas de las láminas (Blender Workbench) y renders (Blender Cycles)
python-blender fuente/render/render_tecnico.py fuente/render/vistas/tecnicas_granja.json
python-blender fuente/render/render_tecnico.py fuente/render/vistas/despiece_TP01.json      # y CPO, DVO, TSGU
python-blender fuente/render/render_blender.py fuente/render/vistas/renders_granja.json     # y planta, galpon, despiece
python fuente/render/a_jpg.py              # renders/_png/*.png -> renders/*.jpg
cd fuente/planos && python planos_gi.py && cd ../..   # 20 láminas, Planos_GI.pdf y zip de DXF
python fuente/memoria_gi.py                # memoria/*.docx y *.pdf (el PDF se imprime con node y Playwright)
python fuente/listas_gi.py                 # documentacion/Listas_granja_integrada.xlsx
```

`python-blender` es el intérprete donde está instalado `bpy`. Si cambia una medida, se cambia en
`fuente/datos_granja.py` y se corre todo en ese orden.

## Decisiones principales

- **Fila G1, G2, planta, G3, G4** con las cabeceras de guano al Sur y las de huevos al Norte; ventilación de túnel con
  paneles al Norte y ventiladores al Sur, del lado del guano.
- **Cintas en toda la línea** (transversal CT, inclinada CI con bordes de 120 mm y tacos de 110 mm a 46°, colectora CE,
  principal CP), sin palas ni transportadores desconectados. Se descartaron sinfín, cadena, cangilones y neumático para
  el guano húmedo.
- **Torres de transferencia TT-O y TT-E** con desviadora: posición A a la planta; posición B a un contenedor volquete
  de 20 m³, solo con el secador parado.
- **Tolva pulmón central TP-01** de 46 m³ (2,28 días de guano) con fondo vivo de 4 sinfines, pesaje y aspiración al
  biofiltro, en lugar de la playa de recepción y la tolva de 3,1 m³ de la Rev. F.
- **Secador SC-4 sin cambios**: régimen de 1.260 kg/h con aire a 121 °C en dos turnos (12,5 % de reserva). Aguas
  abajo se proponen (P) la tolva de retención F1 de 1,0 m³ y el enfriador de 1.200 m³/h.
- **Biogás eliminado**: el piloto del hogar pasa a GLP (tanque de 0,5 m³) y la salida Q23 del TG2 alimenta el tablero
  nuevo TS-GU.
- **Eléctrica**: ECT TT, transformador de 315 kVA al 64,2 % (P), alimentadores enterrados con dos caños por zanja
  separados 0,5 m (factor 0,95), caída máxima 3,06 % (M85). En los galpones rige además la sección 705 de la AEA 90364.
- **Automatización**: PLC-01 de seguridad con periferias ET 200SP por zona, PLC-02 del SC-4 como I-device, GRAFCET en
  tres gráficos (transporte, secado y seguridad con forzado); la planta no arranca con condiciones inseguras.

## Valores preliminares y pendientes

Los valores marcados **(P)** son propuestas de este rediseño y los **(H)** hipótesis; la memoria (sección 13) dice
cómo se confirma cada uno. Los principales: densidad del guano (950 kg/m³, a medir), potencias de las cintas
(fabricante), sinfines de la TP-01 (CEMA 350), carga de la CP-E y la BT-01 sobre las cerchas de la nave (cálculo
estructural), tolva F1 y enfriador (proveedor del secador), red de MT y transformador (distribuidora), cargas de los
galpones (integrador), distancias sanitarias (SENASA) y piloto a GLP (instalador matriculado).

## Verificación

- 20 láminas exportadas sin errores de DXF; revisión visual de todas.
- Cálculos con verificación automática (capacidad de cada cinta, Ib ≤ In ≤ Iz, I2 ≤ 1,45 · Iz, caída de tensión y
  protección con el cortocircuito mínimo); la planilla repite esas verificaciones con fórmulas.
- Control independiente de cálculos, planos y coherencia entre documentos, con sus correcciones aplicadas.
