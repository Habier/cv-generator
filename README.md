# CV Generator

CV generator powered by a single local data file (`cv.yml`). It renders every valid CV variant for the selected visual template.

## What it includes

- One source of truth: `cv.yml`.
- Languages and profiles are inferred from the keys under `labels` and `profiles`.
- Generation renders every profile × every language.
- Templates are discovered dynamically from folders under `templates/` that contain `cv.html.j2`.
- You can create your own templates.

## Structure

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

## Installation

### Ubuntu / Debian

WeasyPrint needs system dependencies to generate PDFs:

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

## Local CV data and privacy

`cv.yml` is ignored by default, start from the safe public example, then edit the local copy:

```bash
cp cv.yml.example cv.yml
```

## Usage

Generate all valid PDF variants with the default template (`settings.default_template`, usually `default`):

```bash
python scripts/generate.py
```

Generate all valid PDF variants from a non-default CV data file:

```bash
python scripts/generate.py --cv path/to/cv.yml
```

Equivalent Make target:

```bash
make pdf TEMPLATE=default
```

Generated files are written to:

```text
output/
```

CLI options:

```text
--cv        CV YAML file to read. Defaults to the repo root cv.yml
--template  Template folder name discovered from templates/*/cv.html.j2
--html      Generate HTML files alongside PDFs
```

PDF generation is the default behavior.

## Configuration model

### Languages

Languages come from the keys under `labels`:

```yaml
labels:
  es:
    present: Actualidad
  en:
    present: Present
```

Any language key can be used. Localized content should use the same keys when possible.

If a localized field is missing a generated language, the generator falls back to another available value where possible.

### Profiles

Profiles come from the keys under `profiles`:

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

Each profile is generated once for each language key under `labels`. Output filenames follow `cv-{name}-{profile}-{language}.pdf`, with the template name appended for non-default templates.

### Skills

Skills are global per language, not per profile. Every generated profile for the same language uses the same `skills.<language>` groups:

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

### Projects

Projects may be shared by every profile or limited to specific profiles. Omit `profiles` when a project should appear in every generated profile:

```yaml
projects:
  - name: Shared Project
    description:
      es: Proyecto visible en todos los perfiles.
      en: Project visible in every profile.
```

Add `profiles` only when a project should be filtered to those profile keys:

```yaml
projects:
  - name: Fullstack Project
    profiles:
      - fullstack
    description:
      es: Proyecto visible solo en el perfil fullstack.
      en: Project visible only in the fullstack profile.
```

## Editing content

Editable content lives in `cv.yml`. If it does not exist yet, create it from the example:

```bash
cp cv.yml.example cv.yml
```

Common sections:

- `personal`
- `labels`
- `profiles`
- `experience`
- `projects`
- `education`
- `languages`
- `skills`
- `certifications`

## Editing design

Each template has its own CSS:

```text
templates/default/style.css
```

To create a new template:

1. Copy an existing template folder.
2. Edit `templates/my-template/style.css` and/or `templates/my-template/cv.html.j2`.
3. Generate all valid variants with the new template:

```bash
python scripts/generate.py --template my-template
```
