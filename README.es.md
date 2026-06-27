# Generador de CV

Idioma: [English](README.md) | [Español](README.es.md)

Generador de CV basado en un único archivo de datos local (`cv.yml`). Renderiza todas las variantes válidas del CV para la plantilla visual seleccionada.

Ejemplo de salida: [`Example/example-cv.pdf`](Example/example-cv.pdf)

## Qué incluye

- Una única fuente de verdad: `cv.yml`.
- Los idiomas y perfiles se infieren desde las claves de `labels` y `profiles`.
- La generación renderiza cada combinación de perfil × idioma.
- Las plantillas se descubren dinámicamente desde las carpetas bajo `templates/` que contienen `cv.html.j2`.
- Puedes crear tus propias plantillas.

## Estructura

```text
cv-generator/
├── cv.yml
├── cv.yml.example
├── Makefile
├── requirements.txt
├── README.md
├── scripts/
│   └── generate.py
└── templates/
```

Las distribuciones portables del ejecutable usan una estructura visible similar:

```text
cv-generator/
├── cv-generator(.exe)
├── cv.yml.example
├── templates/
└── _deps/
```

Los archivos de release incluyen `cv.yml.example`, pero no incluyen `cv.yml`; tus datos privados del CV permanecen fuera de la aplicación distribuida hasta que los crees localmente.
La carpeta `_deps/` contiene los archivos de soporte empaquetados por PyInstaller y debe permanecer junto al ejecutable.

## Instalación

### Ubuntu / Debian

WeasyPrint necesita dependencias del sistema para generar PDFs:

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip make \
  libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev \
  libcairo2 libgdk-pixbuf-2.0-0
make install
cp cv.yml.example cv.yml
source .venv/bin/activate
```

### macOS

```bash
brew install python make pango cairo gdk-pixbuf libffi
make install
cp cv.yml.example cv.yml
source .venv/bin/activate
```

## Datos locales del CV y privacidad

`cv.yml` se ignora por defecto. Empieza desde el ejemplo público seguro y luego edita la copia local:

```bash
cp cv.yml.example cv.yml
```

## Uso

Genera todas las variantes PDF válidas con la plantilla por defecto (`settings.default_template`, normalmente `default`):

```bash
python scripts/generate.py
```

Genera todas las variantes PDF válidas desde un archivo de datos de CV que no sea el predeterminado:

```bash
python scripts/generate.py --cv path/to/cv.yml
```

Target equivalente de Make:

```bash
make generate TEMPLATE=default
```

Ejecuta la batería de tests:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/
```

Los archivos generados se escriben en:

```text
output/
```

Opciones de la CLI:

```text
--cv        Archivo YAML del CV que se debe leer. Por defecto usa cv.yml en el directorio actual
--template  Nombre de la carpeta de plantilla descubierta desde templates/*/cv.html.j2
--html      Genera archivos HTML junto a los PDFs
```

La generación de PDF es el comportamiento predeterminado.

## Releases portables del ejecutable

Las releases para Windows y Linux se construyen como archivos PyInstaller `onedir`. Después de extraer una release, copia el archivo de ejemplo del CV en tu directorio de trabajo y edítalo:

```bash
cp cv.yml.example cv.yml
```

Después ejecuta el binario desde ese directorio de trabajo:

```bash
./cv-generator
```

En Windows, ejecuta:

```powershell
.\cv-generator.exe
```

También puedes apuntar a un archivo CV específico:

```bash
./cv-generator --cv path/to/cv.yml
```

Los archivos generados se escriben en `output/` dentro del directorio de trabajo actual. Las plantillas se cargan desde la carpeta visible `templates/` junto al ejecutable, mientras los archivos de soporte empaquetados permanecen en `_deps/`. Puedes inspeccionar o copiar una carpeta de plantilla y seleccionarla con `--template` cuando contenga `cv.html.j2`.

El ejecutable sigue dependiendo de las librerías de plataforma que WeasyPrint necesita. En Linux puede que necesites los mismos paquetes de Pango, Cairo, GDK-PixBuf, HarfBuzz y libffi indicados en la sección de instalación para tu distribución.

Construye localmente un artefacto PyInstaller `onedir` cuando tengas instaladas las dependencias de desarrollo:

```bash
make build-executable
```

## Modelo de configuración

### Idiomas

Los idiomas vienen de las claves bajo `labels`:

```yaml
labels:
  es:
    present: Actualidad
  en:
    present: Present
```

Puede usarse cualquier clave de idioma. El contenido localizado debería usar las mismas claves siempre que sea posible.

Si falta un campo localizado para un idioma generado, el generador usa otro valor disponible cuando puede hacerlo.

### Perfiles

Los perfiles vienen de las claves bajo `profiles`:

```yaml
profiles:
  backend:
    title:
      es: Desarrollador backend
      en: Backend Developer
    summary:
      es: Desarrollador backend con 6 años de experiencia...
      en: Backend developer with 6 years of experience...
```

Cada perfil se genera una vez por cada clave de idioma bajo `labels`. Los nombres de salida siguen el formato `cv-{name}-{profile}-{language}.pdf`; para plantillas que no sean la predeterminada, se añade el nombre de la plantilla.

### Habilidades

Las habilidades son globales por idioma, no por perfil. Cada perfil generado para el mismo idioma usa los mismos grupos de `skills.<language>`:

```yaml
skills:
  es:
    Backend:
      - PHP
      - Laravel
  en:
    Backend:
      - PHP
      - Laravel
```

### Proyectos

Los proyectos pueden compartirse entre todos los perfiles o limitarse a perfiles específicos. Omite `profiles` cuando un proyecto deba aparecer en cada perfil generado:

```yaml
projects:
  - name: Shared Project
    description:
      es: Proyecto visible en todos los perfiles.
      en: Project visible in every profile.
```

Añade `profiles` solo cuando un proyecto deba filtrarse a esas claves de perfil:

```yaml
projects:
  - name: Fullstack Project
    profiles:
      - fullstack
    description:
      es: Proyecto visible solo en el perfil fullstack.
      en: Project visible only in the fullstack profile.
```

## Editar contenido

El contenido editable vive en `cv.yml`. Si todavía no existe, créalo desde el ejemplo:

```bash
cp cv.yml.example cv.yml
```

Secciones comunes:

- `personal`
- `labels`
- `profiles`
- `experience`
- `projects`
- `education`
- `languages`
- `skills`
- `certifications`

## Editar diseño

Cada plantilla tiene su propio CSS:

```text
templates/default/style.css
```

Para crear una plantilla nueva:

1. Copia una carpeta de plantilla existente.
2. Edita `templates/my-template/style.css` y/o `templates/my-template/cv.html.j2`.
3. Genera todas las variantes válidas con la nueva plantilla:

```bash
python scripts/generate.py --template my-template
```
