# CV Generator

Language: [English](README.md) | [Español](README.es.md)

CV generator powered by a single local data file (`cv.yml`). It renders every valid CV variant for the selected visual template.

Example output: [`Example/example-cv.pdf`](Example/example-cv.pdf)

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

Portable executable releases use a similar visible layout:

```text
cv-generator/
├── cv-generator(.exe)
├── cv.yml.example
├── README.txt
├── templates/
└── _deps/
```

Release archives include `cv.yml.example` but do not include `cv.yml`; your private CV data stays outside the distributed app until you create it locally.
The `_deps/` folder contains bundled PyInstaller support files and must stay beside the executable.

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
make generate TEMPLATE=default
```

Run the test suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest tests/
```

Generated files are written to:

```text
output/
```

The output folder defaults to `output/` in the current working directory. Override it per CV by setting `settings.output_dir` in `cv.yml` (relative paths resolve against the working directory):

```yaml
settings:
  output_dir: build/cvs
```

CLI options:

```text
--cv        CV YAML file to read. Defaults to the current directory cv.yml
--template  Template folder name discovered from templates/*/cv.html.j2
--html      Generate HTML files alongside PDFs
```

PDF generation is the default behavior.

## Portable executable releases

Windows and Linux releases are built as PyInstaller `onedir` archives. After extracting a release, copy the example CV file into your working directory and edit it:

```bash
cp cv.yml.example cv.yml
```

Then run the executable from that working directory:

```bash
./cv-generator
```

On Windows, run:

```powershell
.\cv-generator.exe
```

You can also point at a specific CV file:

```bash
./cv-generator --cv path/to/cv.yml
```

Generated files are written to `output/` in the current working directory. Templates are loaded from the visible `templates/` folder beside the executable, while bundled support files stay in `_deps/`. You can inspect or copy a template folder and select it with `--template` when it contains `cv.html.j2`.

Windows release archives include the native libraries required by WeasyPrint, so end users do not need to install Python, MSYS2, Pango, or Cairo. Linux users may need the same Pango, Cairo, GDK-PixBuf, HarfBuzz, and libffi packages listed in the installation section for their distribution.

To build a Windows artifact locally, install Pango and GDK-PixBuf with MSYS2 and point `WEASYPRINT_DLL_DIRECTORIES` at its `mingw64/bin` directory before running PyInstaller:

```powershell
$env:WEASYPRINT_DLL_DIRECTORIES = "C:\msys64\mingw64\bin"
make build-executable
```

On Linux, build the local PyInstaller `onedir` artifact after installing the platform and development dependencies:

```bash
make build-executable
```

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

### Personal links

Personal links accept either a shared scalar URL or a language-specific mapping. Keep full `https://` URLs in both forms:

```yaml
personal:
  github: https://github.com/example
  linkedin:
    es: https://www.linkedin.com/in/example/
    en: https://www.linkedin.com/in/example/?locale=en-US
```

The mapping is optional: use a scalar when every CV language should use the same URL. This works for any link field under `personal`, not only `linkedin`. When the requested language is absent or empty, selection falls back to `es`, then `en`, then the first non-empty URL.

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
