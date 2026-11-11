# Video de presentación de la secadora de guano

Video de 3:51 sincronizado con la música: vuelo sobre el mapa satelital desde Paraná hasta el lote en Crespo,
la planta que se arma sola (piso, estructura, el secador que se arma en el aire y baja a su lugar, equipos,
paredes, techo, ampliaciones y vehículos), despiece del secador SC-4, recorrido del proceso en 8 pasos,
seguridad, ampliación del Sector Este, cifras de ingeniería, atardecer, noche y créditos.

Todo se genera con estos programas; la escena es una página three.js que se dibuja cuadro por cuadro en
Chrome sin ventana (el tiempo no corre solo: cada cuadro llama a `window.__cuadro(t)`).

## Pasos (desde `revD_final/fuente/`)

```
# 1. Datos (una vez; se guardan en video/datos/, que no se sube al repositorio)
node capturar_geometria.js ../visor.html video/_tmp/geo.json      # piezas del visor con sus colores
python video/preparar_planta.py video/_tmp/geo.json               # -> datos/planta.bin, planta_col.bin, planta.json
python video/mapa.py                                              # imágenes satelitales en 5 niveles + OpenStreetMap
python video/ritmo.py video/_musica.mp3                           # pulsos y compases -> datos/ritmo.json
node video/trafico.js                                             # recorridos de camiones y pala del visor -> datos/trafico.json

# 2. Escena
node video/escena/build.mjs                                       # -> video/escena.html (copia también el GLB del secador)
node video/muestras.js /tmp/muestras 30 60 100 150                # capturas sueltas para revisar encuadres

# 3. Cuadros y video
node video/capturar.js ../video/_cuadros/previa 0 "" 10 960 540 82        # vista previa (≈ 20 min)
python video/montar.py ../video/_cuadros/previa 10 ../video/previa.mp4 --crf 26
# final 1080p60: dos procesos intercalados (cuadros k, k+4, k+8...), primero los pares y después los impares
node video/capturar.js ../video/_cuadros/final 0 "" 60 1920 1080 92 4 & node video/capturar.js ../video/_cuadros/final 0.033 "" 60 1920 1080 92 4
node video/capturar.js ../video/_cuadros/final 0.016 "" 60 1920 1080 92 4 & node video/capturar.js ../video/_cuadros/final 0.0499 "" 60 1920 1080 92 4
# GitHub acepta archivos de hasta 100 MB: 1080p60 a 3000 kbit/s en dos pasadas (≈ 93 MB)
python video/montar.py ../video/_cuadros/final 60 ../video/Secadora_guano_presentacion_1080p60.mp4 --kbps 3000 --pasadas 2
python video/montar.py ../video/_cuadros/final 60 ../video/Secadora_guano_presentacion_720p.mp4 --cada 2 --ancho 1280 --kbps 1600
# versión liviana para la página de entrega publicada (archivos de hasta 15 MB)
python video/montar.py ../video/_cuadros/final 60 ../video/_cuadros/Secadora_guano_web.mp4 --cada 2 --ancho 960 --kbps 380 --audio 96 --pasadas 2
```

`capturar.js` numera los cuadros por su tiempo y saltea los que ya existen: se puede cortar y retomar, o
correr varias tandas en paralelo con distintos tramos (`desde` y `hasta` en segundos) o intercaladas con `cada_n`.
Sin placa de video (SwiftShader, 4 núcleos) el 1080p60 lleva unas 5 a 6 horas: la parte del mapa sale a ≈ 0,5 s por
cuadro y la planta a ≈ 2,5 s. `montar.py --cada 2` arma una versión a 30 fps con los mismos cuadros.

**Con la placa de video de la PC** (RTX): `set VIDEO_GPU=1` antes de `node capturar.js` usa ANGLE con Direct3D
en lugar de SwiftShader (dibujo por procesador) y el render final baja de horas a minutos.

## Archivos

| Archivo | Qué hace |
|---|---|
| `escena/motor.js` | Renderizador, cielo y luces (día, atardecer, noche), mapa en niveles, planta por bloques, secador detallado, carteles con línea guía (sin superponerse), trazos del mapa, cámara por claves |
| `escena/guion.js` | El guion: tiempos por compás `B(n, pulso)`, cámara, armado de la obra, armado y despiece del secador, vehículos, textos y cifras |
| `trafico.js` | Graba del visor los recorridos de los camiones y la pala (posición y giro cada 0,1 s): el video los reproduce tal cual, así el camión entra de culata por el portón P1 y la pala va de la pila a la tolva sin atravesar equipos |
| `escena/plantilla.html` | Capa de textos (títulos, placas, carteles, cifras, créditos) en 1920 × 1080 |
| `mapa.py` | Teselas de Esri World Imagery y datos de OpenStreetMap (RN 12, Parque Industrial, calles) |
| `preparar_planta.py` | Divide la planta en bloques por pieza y color (y la nave en piso, estructura, paredes y techo) |
| `ritmo.py` | Pulsos (87,4 por minuto), compases y energía por compás de la música |

## Datos y cuidados

- **Ubicación del lote: orientativa** (plano 14): campo al Noreste de la RN 12, frente al Parque Industrial,
  junto a la continuación de la calle Democracia. La planta de biogás vecina está proyectada y su lugar no está
  definido. El video lo aclara en pantalla.
- Distancias calculadas desde el centro del lote: 204 m a la RN 12, 2,6 km al centro de Crespo y 36,6 km en línea
  recta a Paraná.
- Cifras en pantalla tomadas de los cálculos (`calculos/resultados.json`) y del portal: 8 t/día al 72 % → 2,6 t/día
  al 15 %, generador de 880 kW (314 kg/h de cáscara), potencia instalada 66,9 + 50,1 kW, eje motriz n = 1,59,
  40 anclajes M16. No se muestran datos pendientes de confirmar (inversión, potencia a contratar).
- Créditos de imágenes en pantalla: Esri, Maxar, Earthstar Geographics y colaboradores de OpenStreetMap.
- **Música:** «Addiction» (LONOWN y Asenssia, versión slowed), la eligió el grupo. No es libre de derechos: sirve
  para proyectarlo en la escuela; si se sube a YouTube u otra red puede quedar silenciado o reclamado. No se guarda
  en el repositorio.
