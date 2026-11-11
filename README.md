# Planta secadora de guano de gallina · 8 t/día

[![Pruebas](https://github.com/lagzgabrielmuller-dot/planta-secadora-guano/actions/workflows/pruebas.yml/badge.svg)](https://github.com/lagzgabrielmuller-dot/planta-secadora-guano/actions/workflows/pruebas.yml)

Proyecto final 2026 de 7.° año de la Especialidad Electromecánica de la E.P.N.M. y S. N.° 35 Técnica
«Gral. Don José de San Martín» (Crespo, Entre Ríos). Es una planta que convierte 8 t/día de guano fresco de
gallina (72 % de humedad) en 2,6 t/día de abono seco (15 %). Usa un secador de cinta de tres pisos (SC-4), un
generador de aire caliente a cáscara de arroz, tratamiento de gases, biogás con cogeneración y una ampliación de
seguridad, envasado y expedición.

**Sitio público:** https://lagzgabrielmuller-dot.github.io/planta-secadora-guano/: portada, visores 3D, planos,
informe, memoria, presupuesto, simulador y video.

## Qué hay en la entrega

| Entregable | Archivo |
|---|---|
| Portada de la entrega (abre todo) | [`index.html`](index.html) |
| Informe final (Word y PDF) | [`informe/`](informe/) |
| Memoria de cálculo: TG2, iluminación, ventilación, biogás y carga de fuego | [`memoria/`](memoria/) |
| Presupuesto: inversión, pedido a la Cooperativa LAR, energía y evaluación económica | [`presupuesto/`](presupuesto/) |
| 24 láminas A3 IRAM: PDF, DXF para AutoCAD y PNG | [`planos/`](planos/) |
| Visor 3D de la planta completa, sin internet | [`visor.html`](visor.html) |
| Secador SC-4 aparte: visor con despiece, corte y montaje en 13 pasos; manual de armado; STEP y GLB; láminas SC-01 a SC-06 | [`secadora/`](secadora/) |
| Modelo STEP de la planta y renders | [`modelo_3d/`](modelo_3d/) |
| Estudio térmico del secador: modelo físico, láminas y simulador interactivo | [`simulacion_termica/`](simulacion_termica/) |
| Video de presentación de 3:51 (1080p a 60 cuadros por segundo, sin música) | [`video/`](video/) |
| Programas que generan todo lo anterior | [`fuente/`](fuente/) |

## Revisión vigente: Rev. F (11/11/2026)

La Rev. F incorpora los cambios del estudio térmico del secador:

- la humedad se controla con la temperatura del aire, que ronda los 100 °C (135 °C es el máximo);
- guías de PTFE;
- sello de los bordes de las bandas;
- escape aislado con purga de condensado;
- recirculación por humedad relativa;
- tolva de retención de 1 h más enfriador para higienizar;
- capacidad de 1.440 kg/h.

También corrige incoherencias que venían de revisiones anteriores. El detalle, con cada número y su fuente, está en
[`docs/REV_F.md`](docs/REV_F.md). Los números principales:

| | |
|---|---|
| Producción | 1.000 kg/h de guano al 72 % → 329 kg/h de abono al 15 % (un turno de 8 h) |
| Secador SC-4 | 3 pisos de 2,0 × 12 m (72 m²), 13,0 × 2,6 × 3,4 m, 68 piezas, 9.538 kg |
| Generador | 880 kW a cáscara de arroz (máximo); en el punto de trabajo, 617 kW y 219 kg/h |
| Electricidad | TGF 66,9 kW + TG2 50,09 kW; 100 kW a contratar con la LAR (tarifa T3 BT) |
| Biogás | 184 m³/día, 318 kWh/día de electricidad (motogenerador de 25 kWe) |
| Inversión | USD 999.841 (planta completa); dos turnos: TIR 17,7 %, repago 5,2 años |

## Cómo verla

- **En internet:** el sitio público (arriba). Anda en computadora y en celular.
- **Sin internet:** *Code → Download ZIP*, descomprimir y abrir `index.html`. Conviene Google Chrome o Edge.

## Cómo regenerarla y probarla

```bash
pip install -r requirements.txt && (cd fuente && npm ci)
python fuente/regenerar.py              # rehace planos, modelo 3D, Word, PDF, visores y portada
pip install -r tests/requirements.txt
python -m pytest tests -q               # cálculos, datos cruzados entre documentos, archivos, Rev. F
node tests/e2e/probar_sitio.js          # el sitio, como lo sirve GitHub Pages, en computadora y celular
```

Paso a paso, requisitos y la única variable de entorno (`CHROME_PATH`, opcional): [`docs/INSTALACION.md`](docs/INSTALACION.md).
Cómo está armado: [`docs/ARQUITECTURA.md`](docs/ARQUITECTURA.md). Publicación y actualización:
[`docs/DESPLIEGUE.md`](docs/DESPLIEGUE.md).

**Regla del proyecto:** un dato se corrige en el programa de cálculo y se regenera. Nunca se edita a mano un PDF,
DXF, Word o HTML de salida. Las pruebas fallan si un documento quedó con un número viejo.

## Calidad y auditoría

La auditoría del 11/11/2026 está en [`AUDITORIA_FINAL.md`](AUDITORIA_FINAL.md): problemas encontrados y
corregidos, datos verificados contra fuentes externas, lo que no se pudo verificar, pruebas ejecutadas y pendientes.
Los cambios por versión están en [`CHANGELOG.md`](CHANGELOG.md).

## Estructura

```
index.html  visor.html  entrega.html     portada, visor 3D de la planta, redirección
informe/  memoria/  presupuesto/          documentos
planos/  modelo_3d/  secadora/            planos, modelos 3D y el secador SC-4
simulacion_termica/  video/               estudio térmico y video (sin música)
portal/img/                               imágenes de la portada
docs/  tests/  .github/workflows/         documentación, pruebas y CI
fuente/                                   programas (Python y Node.js) y datos
```

## Integrantes

Bautista Belluzzo · Martín Bernhardt · Baltazar Goette · Pablo Hofstetter · Gabriel Müller · Facundo Stegmann

## Límites y pendientes

- Los precios son de referencia (± 25 %, dólar BNA $ 1.550 del 23/10/2026). Faltan las cotizaciones formales: LAR,
  PTFE, perfil de silicona y ventilador del enfriador.
- La ubicación del lote es orientativa: hay que confirmarla con la Municipalidad de Crespo.
- La materia y el docente siguen como `[COMPLETAR]` en las portadas del informe y de la memoria.
- La ingeniería de detalle de la Rev. F queda pendiente: redibujo de los planos 08 y 19 con la tolva de retención,
  el enfriador y la prolongación del elevador.
- El video público va sin la música que eligió el grupo, porque no es libre de derechos.

## Uso y créditos

Proyecto escolar. Los textos, planos y modelos son de sus autores; para reutilizarlos, pedir permiso al grupo.
three.js (licencia MIT) se usa en los visores y en el simulador. Las imágenes satelitales del video son de Esri,
Maxar y Earthstar Geographics; el mapa, de los colaboradores de OpenStreetMap (ODbL).
