# Publicación (GitHub Pages)

El sitio es estático: GitHub Pages sirve por HTTPS los mismos archivos del repositorio, sin compilar nada.

| Dato | Valor |
|---|---|
| Plataforma | GitHub Pages, publicación desde la rama `main`, carpeta raíz `/` |
| Dirección pública | https://lagzgabrielmuller-dot.github.io/planta-secadora-guano/ |
| HTTPS | Lo da GitHub automáticamente (*Enforce HTTPS* activado) |
| Rutas | `index.html` (portada), `visor.html`, `secadora/Visor_Secador_SC4.html`, `simulacion_termica/simulador.html`, `entrega.html` (redirige a la portada) |
| Variables de entorno | Ninguna: el sitio no usa claves, servicios externos ni base de datos |
| `.nojekyll` | Presente: GitHub no procesa el sitio con Jekyll y sirve todos los archivos tal cual |
| Límites de GitHub Pages | Sitio menor a 1 GB, archivos menores a 100 MB. El más grande es el video 1080p60 sin música, de 87 MB |

## Activación (una sola vez)

1. En GitHub, en el repositorio: **Settings → Pages**.
2. En *Build and deployment*, en *Source*, elegir **Deploy from a branch**, rama **`main`** y carpeta **`/ (root)`**.
   Después, **Save**.
3. Esperar uno o dos minutos. La dirección aparece arriba, en la misma página. Activar **Enforce HTTPS** si no lo
   está.

## Actualización automática

Cada `git push` a `main` vuelve a publicar el sitio solo: GitHub corre el flujo *pages build and deployment*. En
paralelo, el flujo **Pruebas** (`.github/workflows/pruebas.yml`) corre los cálculos, los controles de datos y la
prueba del sitio. Si una prueba falla, el sitio igual se publica, pero el aviso queda en la pestaña *Actions*.

Para cambiar algo:

```bash
# 1. corregir el dato en fuente/ (nunca a mano en un PDF, DXF o Word)
python fuente/regenerar.py --desde <paso>
python -m pytest tests -q && node tests/e2e/probar_sitio.js
git add -A && git commit -m "Descripción del cambio" && git push
```

## Verificación después de publicar

```bash
SITIO_URL=https://lagzgabrielmuller-dot.github.io/planta-secadora-guano/ node tests/e2e/probar_sitio.js
```

La prueba abre la portada en computadora y en celular (iPhone 13). Controla que respondan los enlaces internos, que
el video cargue, que ande la galería de planos, que se abran las páginas de equipos, que redirija `entrega.html` y
que los dos visores 3D y el simulador dibujen sin errores.
