# Instalación, uso local y pruebas

## Solo para ver la entrega

No hace falta instalar nada:

- **En internet:** abrí el sitio publicado (ver el README).
- **Sin internet:** descargá el repositorio (botón verde *Code → Download ZIP*), descomprimilo y abrí `index.html`
  con doble clic. Los visores 3D, el simulador y los PDF también andan desde la carpeta. Conviene Google Chrome o Edge.

## Para regenerar todo desde los programas

Requisitos:

| Herramienta | Versión probada | Para qué |
|---|---|---|
| Python | 3.12 (sirve 3.11) | cálculos, láminas, modelo CadQuery, Word, portada |
| Node.js | 22 | visores, capturas, impresión de PDF, video |
| Google Chrome o Chromium | cualquiera reciente | WebGL sin pantalla y PDF |
| Fuentes Arial o Liberation Sans | — | medidas de los textos de las láminas |

```bash
git clone https://github.com/lagzgabrielmuller-dot/planta-secadora-guano.git
cd planta-secadora-guano
python -m venv .venv
.venv/bin/pip install -r requirements.txt          # en Windows: .venv\Scripts\pip install -r requirements.txt
cd fuente && npm ci && cd ..
```

En Linux, ezdxf busca «Arial». Instalá `fonts-liberation` y corré una vez:

```bash
mkdir -p ~/.fonts && cp /usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf ~/.fonts/arial.ttf
cp /usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf ~/.fonts/arialbd.ttf
python -c "from ezdxf.fonts import fonts; fonts.build_system_font_cache()"
```

Si Chrome no está en el lugar de siempre, definí la variable `CHROME_PATH` con la ruta del ejecutable. Es la única
variable de entorno que usa el proyecto. **No hay claves ni credenciales.**

### Regenerar

```bash
cd fuente
python regenerar.py --lista          # muestra los 12 pasos
python regenerar.py                  # todo, en orden (unos 15 minutos sin placa de video)
python regenerar.py --desde planos   # desde un paso hasta el final
python regenerar.py calculos portal  # solo esos pasos
```

Orden: cálculos → presupuesto → secador (CadQuery) → visor del secador → renders del secador → visor de la planta →
renders → láminas → láminas SC → memoria → informe → portada. Si cambia un dato se corrige en el programa y se
regenera desde ese paso. Nunca se edita a mano un DXF, PDF, DOCX o HTML de salida.

El estudio térmico tiene su propio README (`simulacion_termica/README.md`): `pip install -r
simulacion_termica/requirements.txt` y `python simulacion_termica/correr_todo.py`.

## Pruebas

```bash
pip install -r tests/requirements.txt
python -m pytest tests -q            # cálculos, datos cruzados entre documentos, archivos, Rev. F
cd tests/e2e && npm install && npx playwright install chromium && cd ../..
node tests/e2e/probar_sitio.js       # sitio servido por HTTP: enlaces, video, galería, visores, celular
SITIO_URL=https://lagzgabrielmuller-dot.github.io/planta-secadora-guano/ node tests/e2e/probar_sitio.js   # el sitio publicado
```

Las mismas pruebas corren solas en GitHub Actions en cada cambio (`.github/workflows/pruebas.yml`).
