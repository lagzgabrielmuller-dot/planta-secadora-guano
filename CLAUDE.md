# Secadora de guano de gallina 8 t/día — entrega final

Estado del proyecto al 11/11/2026 (Rev. F). Leer esto antes de tocar nada. Repositorio oficial e independiente:
este reemplaza a la carpeta `revD_final/` del repositorio anterior `secadora` (que queda como antecedente).

## Qué es

Proyecto final de 7.° año, Especialidad Electromecánica, E.P.N.M. y S. N° 35 Técnica "Gral. Don José de
San Martín" (Crespo, Entre Ríos). Integrantes: Belluzzo B., Bernhardt M., Goette B., Hofstetter P., Müller G.,
Stegmann F. Materia y docente: **[COMPLETAR]** (resaltados en amarillo en la portada del informe y de la memoria).

Planta de secado de guano de gallina de 8 t/día (secador de cinta de 3 pisos SC-4, generador de aire
caliente a cáscara de arroz, ciclón, lavador de gases) en un predio de 120 × 76 m junto al Parque
Industrial de Crespo (RN 12 km 40,6), al lado de la planta de biogás «Ñande Zukunft I». La Rev. D agrega
los ítems de seguridad y mantenimiento D1–D24 y la ampliación E1–E10 (lavado de vehículos, ventilación de
la recepción con biofiltro, zaranda, ensacadora, envasadora, depósito de expedición, biogás con
cogeneración G1 25 kWe, Sector Este y ventilación general de la nave), todo con un tablero nuevo TG2.
La entrega final suma la verificación a fatiga, el secador SC-4 como entregable aparte, el presupuesto
con la Cooperativa La Agrícola Regional (LAR) y el informe definitivo en Word. La **Rev. F (11/11/2026)** incorpora el
estudio térmico del secador (`simulacion_termica/`): ver `docs/REV_F.md`.

Idioma de todo el proyecto: español técnico (Argentina), coma decimal y punto de miles, normas IRAM/AEA.

## Estructura de carpetas

```
index.html                  Portada pública de la entrega (la arma fuente/portal/portada.py; no editar a mano)
visor.html                  Visor 3D de la planta (three.js). Se ARMA con fuente/visor/build_visor.py: no editar a mano
entrega.html                Redirección a index.html (la dirección vieja sigue andando)
informe/                    Informe_Final_Secadora_Guano.docx/.pdf (Word definitivo, con la Rev. F)
memoria/                    Memoria_de_calculo_RevD.docx/.pdf (TG2, iluminación, ventilación, biogás, carga de fuego)
presupuesto/                Presupuesto_Secadora_Guano.xlsx (inversión, pedido a LAR, energía, evaluación)
planos/                     P01–P24: PNG (los usa el visor), pdf/ (A3 + juego completo), dxf/ (AutoCAD + ZIP)
modelo_3d/                  STEP de la planta (zip) y renders/
secadora/                   ENTREGABLE APARTE del secador SC-4 (visor, manual, STEP/GLB, láminas SC-01 a SC-06, renders)
simulacion_termica/         Modelo térmico del SC-4 (Python + numba), resultados, láminas y simulador.html
video/                      Video de presentación SIN la música (no es libre de derechos): 1080p60, 720p y web
portal/img/                 Imágenes de la portada (las miniaturas de las láminas las rehace portada.py)
docs/                       REV_F.md, ARQUITECTURA.md, INSTALACION.md, DESPLIEGUE.md, DATOS.md
tests/                      pytest (cálculos, datos, entrega, Rev. F) y e2e/ (sitio con Playwright)
fuente/                     Todos los programas (ver fuente/README.md); fuente/regenerar.py rehace todo en orden
AUDITORIA_FINAL.md          Auditoría integral del 11/11/2026 (problemas, correcciones, datos verificados, pruebas)
```

## Revisiones de las láminas

El conjunto se llama "Rev. D" (nombres de archivo, visor, memoria); cada lámina lleva su propia tabla `revs`:

- P01, P02, P04, P06–P13, P15, P16, P18, P19, P21: Rev. D.
- Rev. E: P03 (fatiga, reenvío Ø60/Ø50, límite de par del variador), P05 (LAR, T3 100 kW), P14 (superficie del
  PIC y retiros), P17 (D16 puesta a tierra), P20 (calor y digestato unificados), P22 (EX y VM).
- Rev. F: P23 (acometida 4 × 35 mm², Q25/Q26 con potencia), P24 (punto de funcionamiento de los AirTEC), P22
  (estudio térmico: guías PTFE, faldones, temperaturas de trabajo).
- Estudio térmico (11/2026): P02 y P06 y P18 pasan a Rev. E; P23 a Rev. G; SC-01 a SC-06 a Rev. B (ver docs/REV_F.md).
- Juego del secador SC-01 a SC-06: Rev. A (numeración propia "SC-xx", hoja x/06).

## Decisiones tomadas

1. **Acometida del TG2: 4 × 35 mm²** enterrada (Iz = 93,1 A), QG2 de 80 A regulado en Ir = 63 A por
   selectividad, fusibles NH00 80 A en el pilar: In ≤ Iz e I2 ≤ 1,45·Iz verifican (antes 4 × 25 mm² no verificaba).
2. **TG2:** potencia instalada 50,09 kW (con el ventilador M40 del enfriador, Rev. F), demanda 25,1 kW (44,8 A).
   Iluminación del Sector Este calculada (Q25 1,89 kW, Q26 0,15 kW). Balance sin G1 91,6 kW → **100 kW a contratar
   con la LAR, tarifa T3 BT** (margen 8,4 %). TGF: 66,9 kW instalados (plano 05).
3. **Fatiga (Shigley-Budynas 8.ª ed., `fuente/calculos/fatiga.py`):** eje motriz Ø60 con asiento rectificado,
   n = 1,59 (DE-Goodman); eje de reenvío pasa a Ø60/Ø50 (Rev. E), n = 1,95; el variador limita el par a 706 N·m;
   anclajes químicos M16 (10 placas, 40 anclajes) con uso 1,4 %. Plan de ensayo de Wöhler de 12 probetas (apunte INET
   y González Arias: no menos de 12). Material de los ejes (24/10, carpeta «Cosas para agregar»): Acindar lamina
   barra redonda de stock en SAE 1008–1020 y el 1045 solo a pedido; con SAE 1020 el eje motriz da n = 1,13 (no
   verifica), así que el 1045 se pide con certificado y se recibe por dureza Brinell HB 10/3000/15 ≥ 155 HB
   (impronta ≤ 4,81 mm). Informe, apartado 8.8.
4. **E10 (ventilación de la nave):** 2 extractores Campagnoni AirTEC 1215 con termostato y 2 ventiladores
   móviles 50" en tomas 2P+T; circuito Q27 → TS-VEN. Caudal verificado con el punto de funcionamiento.
5. **D16:** puesta a tierra, equipotencialidad y pararrayos en el plano 17.
6. **Secador SC-4:** columnas con placa base soldada en taller, vigas IPN 140 de 13 m en dos tramos
   (9,75 + 3,25 m) empalmados sobre la columna D, platea de 20 cm bajo el secador.
7. **Video de presentación** (`fuente/video/`, ver su README): escena three.js cuadro por cuadro con el mapa
   satelital (Esri + OpenStreetMap), la planta del visor por bloques y el secador CadQuery, al ritmo de la música
   que eligió el grupo (no libre de derechos: no se sube al repositorio). Ubicación del lote orientativa.
8. Planos, memoria, informe y portada comparten números a través de `fuente/calculos/resultados.json` y
   `presupuesto.json`: un valor se cambia en el programa de cálculo, nunca a mano en un plano o en el Word.
9. **Rev. F (estudio térmico, 11/11/2026):** humedad controlada con la temperatura del aire (MIC-01 en cascada sobre
   TIC-01, 90 a 150 °C; trabajo ≈ 100 °C, 135 °C es el máximo), guías PTFE en pisos 2 y 3, faldones de sellado 4.21,
   escape aislado con purga (sale casi saturado), CD-03 normalmente cerrada, tolva de retención 1 h + enfriador (M40),
   capacidad 1.440 kg/h a 135 °C. Alimentación: cinta con tacos M8 (plano 12), no sinfín. Ver docs/REV_F.md.

## Lo que queda para terceros (no se puede cerrar desde el proyecto)

- Materia y docente en las portadas: [COMPLETAR].
- LAR: potencia contratada, tarifa T3 vigente y conexión en paralelo de G1. Los precios del presupuesto son
  de referencia (± 25 %, dólar BNA $1.550 del 23/10/2026): reemplazar por la cotización formal de LAR.
- Retiros del lote con el reglamento del Parque Industrial y datos catastrales en la Municipalidad de Crespo.
- Fichas técnicas de los extractores AirTEC y de los VM (caudal, η, cos φ) y curva I²t de los interruptores.
- Ensayo de Wöhler del acero de los ejes (confirma el límite de fatiga adoptado).
- **Capítulo IX (fatiga) del libro de González Arias:** la carpeta «Cosas para agregar en la secadora de
  guano» está en Google Drive (subida el 24/10). El PDF del libro pesa 26,5 MB y Drive solo deja leer hasta
  la página ≈ 145; el capítulo IX (págs. 311 a 357) no se pudo leer. Si se sube aparte (menos de 10 MB),
  contrastar el diagrama de Smith y los factores de entalladura y corrosión con `fatiga.py`.

## Reglas para sesiones futuras

- El respaldo de la Rev. D original y el video con música quedan solo en el repositorio anterior `secadora`.
- Cambios de datos: en `fuente/` y regenerar; nunca editar a mano DXF/PDF/PNG/DOCX/HTML de salida.
- Al cambiar una lámina, agregar la fila en su tabla `revs` del script correspondiente.
- Antes de cerrar un cambio, regenerar en el orden de `fuente/README.md` lo que dependa de él (cálculos →
  planos → memoria → informe → portada) para que todo quede igual: `python fuente/regenerar.py --desde <paso>`.
- Antes de subir: `python -m pytest tests -q` y `node tests/e2e/probar_sitio.js` (ver docs/INSTALACION.md).
- La música del video no se sube nunca (no es libre de derechos).
