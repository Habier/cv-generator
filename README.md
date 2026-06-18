# Generador de CV

Generador de CV basado en una única fuente de datos (`cv.yml`) para producir variantes por idioma, perfil, foco tecnológico y plantilla visual.

## Qué incluye

- Una única fuente de verdad: `cv.yml`.
- Un ejemplo público seguro: `cv.yml.example`; copia este fichero a `cv.yml` para trabajar con tus datos locales.
- Idiomas: `es`, `en`.
- Perfiles: `backend`, `fullstack`.
- Focos: `default`, `laravel`, `symfony`.
- Plantillas:
  - `classic`: plantilla sobria inicial.
  - `pdf-like`: la más parecida a tu CV actual en PDF; una columna, cabecera centrada, secciones simples.
  - `compact`: más densa, pensada para encajar mejor en 1-2 páginas.
  - `sidebar`: versión con columna lateral para contacto y skills.
  - `ats-clean`: ATS-conscious one-column template with subtle color accents and clear semantic sections.

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
    ├── classic/
    │   ├── cv.html.j2
    │   └── style.css
    ├── pdf-like/
    │   ├── cv.html.j2
    │   └── style.css
    ├── compact/
    │   ├── cv.html.j2
    │   └── style.css
    ├── sidebar/
    │   ├── cv.html.j2
    │   └── style.css
    └── ats-clean/
        ├── cv.html.j2
        └── style.css
```

## Instalación

### Ubuntu / Debian

WeasyPrint necesita algunas dependencias del sistema para generar PDF:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip make \
  libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libffi-dev \
  libcairo2 libgdk-pixbuf-2.0-0
```

Después:

```bash
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

## Local CV data and privacy

`cv.yml` contains private CV data and is intentionally ignored by Git. Start from the safe public example, then edit the local copy:

```bash
cp cv.yml.example cv.yml
```

Do not commit your personal `cv.yml`. If it was already tracked in a repository, remove it from the index with `git rm --cached cv.yml` while keeping the local file.

## Uso rápido

Generar las cuatro versiones principales en PDF usando la plantilla por defecto (`classic`):

```bash
make pdf
```

Generar las cuatro versiones usando la plantilla más parecida a tu PDF actual:

```bash
make pdf TEMPLATE=pdf-like
```

Generar todas las versiones principales con todas las plantillas:

```bash
make all-templates
```

Generate the ATS-conscious one-column template with subtle color accents:

```bash
make pdf TEMPLATE=ats-clean
```

Los ficheros se crean en:

```text
output/
```

## Comandos concretos

Backend español:

```bash
make backend-es TEMPLATE=pdf-like
```

Backend inglés:

```bash
make backend-en TEMPLATE=pdf-like
```

Fullstack español:

```bash
make fullstack-es TEMPLATE=pdf-like
```

Fullstack inglés:

```bash
make fullstack-en TEMPLATE=pdf-like
```

Versión Laravel:

```bash
make backend-es-laravel TEMPLATE=pdf-like
```

## Generar HTML en vez de PDF

Útil para revisar rápido en navegador:

```bash
make html TEMPLATE=pdf-like
```

O previsualizar un CV backend español con todas las plantillas:

```bash
make preview-templates
```

## Uso directo del script

```bash
python scripts/generate.py --profile backend --lang es --template pdf-like --pdf
python scripts/generate.py --profile fullstack --lang en --template compact --focus laravel --pdf
python scripts/generate.py --profile backend --lang es --template ats-clean --pdf
```

Opciones:

```text
--profile   backend | fullstack
--lang      es | en
--focus     default | laravel | symfony
--template  ats-clean | classic | compact | pdf-like | sidebar
--pdf       genera PDF; sin esta opción genera HTML
```

## Editar contenido

Todo el contenido editable está en `cv.yml`. Si todavía no existe, créalo desde `cv.yml.example` y luego edita la copia local:

```bash
cp cv.yml.example cv.yml
```

- Datos personales: `personal`
- Títulos y resúmenes: `profiles`
- Experiencia: `experience`
- Proyectos: `projects`
- Formación: `education`
- Skills: `skills`
- Certificaciones: `certifications`

Por ejemplo, para cambiar una fecha o una tecnología, edítala una sola vez en `cv.yml` y vuelve a ejecutar `make pdf`.

## Editar diseño

Cada plantilla tiene su propio CSS:

```text
templates/pdf-like/style.css
templates/compact/style.css
templates/sidebar/style.css
templates/ats-clean/style.css
```

Para crear una nueva plantilla:

1. Copia una carpeta existente, por ejemplo:

```bash
cp -r templates/pdf-like templates/my-template
```

2. Edita `templates/my-template/style.css` y/o `templates/my-template/cv.html.j2`.
3. Genera el CV:

```bash
python scripts/generate.py --profile backend --lang es --template my-template --pdf
```

El script detecta automáticamente las carpetas dentro de `templates/` que tengan un `cv.html.j2`.

## Recomendación

Para tu caso, empezaría usando:

```bash
make pdf TEMPLATE=pdf-like
```

Es la plantilla más cercana a los PDFs que ya estabas usando, pero generada automáticamente desde `cv.yml`.
