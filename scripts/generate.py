#!/usr/bin/env python3
import argparse
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

MONTHS = {
    "es": ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    "en": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}


def localized(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        return value.get(lang) or value.get("es") or value.get("en") or ""
    return str(value)


def format_date(value: Any, lang: str, labels: dict) -> str:
    if value in (None, "", "present"):
        return labels["present"]
    value = str(value)
    if len(value) == 4:
        return value
    year, month = value.split("-")[:2]
    return f"{MONTHS[lang][int(month)]} {year}"


def sort_by_focus(technologies: list[str], boost: list[str]) -> list[str]:
    boost_set = {item.lower(): i for i, item in enumerate(boost)}
    return sorted(
        technologies,
        key=lambda t: (0, boost_set[t.lower()]) if t.lower() in boost_set else (1, technologies.index(t)),
    )


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return slug or "cv"


def template_choices(root: Path) -> list[str]:
    templates_root = root / "templates"
    return sorted([p.name for p in templates_root.iterdir() if p.is_dir() and (p / "cv.html.j2").exists()])


def build(args: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parents[1]
    data_path = root / "cv.yml"
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    lang = args.lang or data["settings"]["default_language"]
    profile = args.profile or data["settings"]["default_profile"]
    focus = args.focus or data["settings"]["default_focus"]
    template_name = args.template or data["settings"].get("default_template", "classic")

    if lang not in ("es", "en"):
        raise SystemExit("Invalid language. Use: es or en")
    if profile not in data["profiles"]:
        raise SystemExit(f"Invalid profile: {profile}")
    if focus not in data["focuses"]:
        raise SystemExit(f"Invalid focus: {focus}")

    choices = template_choices(root)
    if template_name not in choices:
        raise SystemExit(f"Invalid template: {template_name}. Available: {', '.join(choices)}")

    labels = data["labels"][lang]
    boost = data["focuses"][focus].get("boost_skills", [])
    title = data["profiles"][profile]["title"][lang] + data["focuses"][focus]["title_suffix"][lang]

    experience = []
    for job in data["experience"]:
        item = dict(job)
        item["company_name"] = localized(item["company"], lang)
        start = format_date(item.get("start"), lang, labels)
        end = format_date(item.get("end"), lang, labels)
        item["date_range"] = f"{start} – {end}"
        item["technologies"] = sort_by_focus(item.get("technologies", []), boost)
        experience.append(item)

    projects = []
    for project in data.get("projects", []):
        if profile not in project.get("profiles", []):
            continue
        item = dict(project)
        item["technologies"] = sort_by_focus(item.get("technologies", []), boost)
        projects.append(item)

    skills = data["skills"][profile][lang]

    template_dir = root / "templates" / template_name
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("cv.html.j2")
    html = template.render(
        lang=lang,
        profile=profile,
        focus=focus,
        template_name=template_name,
        personal=data["personal"],
        labels=labels,
        title=title,
        summary=data["profiles"][profile]["summary"][lang],
        experience=experience,
        projects=projects,
        education=data["education"],
        languages=data.get("languages", []),
        skills=skills,
        certifications=data.get("certifications", []),
    )

    base_name = f"cv-{slugify(data['personal']['name'])}-{profile}-{lang}"
    if focus != "default":
        base_name += f"-{focus}"
    if template_name != "classic":
        base_name += f"-{template_name}"

    html_path = output_dir / f"{base_name}.html"
    pdf_path = output_dir / f"{base_name}.pdf"
    css_name = f"style-{base_name}.css"
    css_output_path = output_dir / css_name

    html = html.replace('href="style.css"', f'href="{css_name}"')
    html_path.write_text(html, encoding="utf-8")
    shutil.copy(template_dir / "style.css", css_output_path)

    if args.pdf:
        try:
            from weasyprint import HTML
        except Exception as exc:
            raise SystemExit(
                "No se pudo importar WeasyPrint. Instala dependencias con: pip install -r requirements.txt"
            ) from exc
        HTML(filename=str(html_path)).write_pdf(str(pdf_path))
        print(f"Generated: {pdf_path}")
    else:
        print(f"Generated: {html_path}")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    choices = template_choices(root)
    parser = argparse.ArgumentParser(description="Generate CV variants from cv.yml")
    parser.add_argument("--lang", choices=["es", "en"], default=None)
    parser.add_argument("--profile", choices=["backend", "fullstack"], default=None)
    parser.add_argument("--focus", choices=["default", "laravel", "symfony"], default=None)
    parser.add_argument("--template", choices=choices, default=None, help=f"Template to use. Available: {', '.join(choices)}")
    parser.add_argument("--pdf", action="store_true", help="Generate PDF using WeasyPrint")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
