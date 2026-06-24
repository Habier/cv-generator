#!/usr/bin/env python3
import argparse
import copy
import re
import unicodedata
from pathlib import Path
from typing import Any

MONTHS = {
    "es": ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    "en": ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
}


def localized(value: Any, lang: str) -> str:
    if isinstance(value, dict):
        return str(value.get(lang) or value.get("es") or value.get("en") or next((item for item in value.values() if item), ""))
    return str(value)


def format_date(value: Any, lang: str, labels: dict) -> str:
    if value in (None, "", "present"):
        return labels.get("present", "Present")
    value = str(value)
    if len(value) == 4:
        return value
    try:
        year, month = value.split("-")[:2]
        month_index = int(month)
    except ValueError:
        return value
    if lang not in MONTHS:
        return f"{year}-{month}"
    return f"{MONTHS[lang][month_index]} {year}"


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    return slug or "cv"


def template_choices(root: Path) -> list[str]:
    templates_root = root / "templates"
    return sorted([p.name for p in templates_root.iterdir() if p.is_dir() and (p / "cv.html.j2").exists()])


def add_localized_fallbacks(value: Any, lang: str, known_languages: list[str]) -> Any:
    if isinstance(value, list):
        return [add_localized_fallbacks(item, lang, known_languages) for item in value]
    if not isinstance(value, dict):
        return value

    updated = {key: add_localized_fallbacks(item, lang, known_languages) for key, item in value.items()}
    localized_keys = [key for key in (*known_languages, "es", "en") if key in updated]
    if lang not in updated and localized_keys:
        fallback_key = next((key for key in ("es", "en") if key in updated), None)
        fallback_key = fallback_key or localized_keys[0]
        if fallback_key is not None:
            updated[lang] = copy.deepcopy(updated[fallback_key])
    return updated


def languages_from_labels(data: dict[str, Any]) -> list[str]:
    labels = data.get("labels")
    if not isinstance(labels, dict) or not labels:
        raise SystemExit("cv.yml must define labels with at least one language key")
    return list(labels.keys())


def profiles_from_data(data: dict[str, Any]) -> list[str]:
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise SystemExit("cv.yml must define at least one profile under profiles")
    return list(profiles.keys())


def selected_template(root: Path, data: dict[str, Any], requested_template: str | None) -> str:
    choices = template_choices(root)
    template_name = requested_template or data.get("settings", {}).get("default_template", "default")
    if template_name not in choices:
        raise SystemExit(f"Invalid template: {template_name}. Available: {', '.join(choices)}")
    return template_name


def render_variant(
    root: Path,
    data: dict[str, Any],
    lang: str,
    profile: str,
    template_name: str,
    output_dir: Path,
    pdf_renderer: Any,
    write_html: bool,
) -> Path:
    known_languages = languages_from_labels(data)
    variant_data = add_localized_fallbacks(data, lang, known_languages)

    labels = variant_data["labels"][lang]
    profile_data = variant_data["profiles"][profile]
    title = localized(profile_data.get("title", ""), lang)

    experience = []
    for job in variant_data.get("experience", []):
        item = dict(job)
        item["company_name"] = localized(item["company"], lang)
        start = format_date(item.get("start"), lang, labels)
        end = format_date(item.get("end"), lang, labels)
        item["date_range"] = f"{start} – {end}"
        experience.append(item)

    projects = []
    for project in variant_data.get("projects", []):
        project_profiles = project.get("profiles")
        if project_profiles is not None and profile not in project_profiles:
            continue
        item = dict(project)
        projects.append(item)

    skills = variant_data.get("skills", {}).get(lang, {})

    from jinja2 import Environment, FileSystemLoader, select_autoescape

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
        template_name=template_name,
        personal=variant_data["personal"],
        labels=labels,
        title=title,
        summary=localized(profile_data.get("summary", ""), lang),
        experience=experience,
        projects=projects,
        education=variant_data.get("education", []),
        languages=variant_data.get("languages", []),
        skills=skills,
        certifications=variant_data.get("certifications", []),
    )

    base_name = f"cv-{slugify(variant_data['personal']['name'])}-{profile}-{lang}"

    if write_html:
        html_path = output_dir / f"{base_name}.html"
        html_path.write_text(html, encoding="utf-8")

    pdf_path = output_dir / f"{base_name}.pdf"

    try:
        pdf_renderer(string=html, base_url=str(template_dir)).write_pdf(str(pdf_path))
    except PermissionError as exc:
        raise SystemExit(
            f"Could not write PDF: {pdf_path}\n"
            "The file appears to be open in another program. Close the PDF and try again."
        ) from exc
    except OSError as exc:
        raise SystemExit(f"Could not write PDF: {pdf_path}\n{exc}") from exc
    return pdf_path


def iter_valid_variants(data: dict[str, Any]) -> list[tuple[str, str]]:
    languages = languages_from_labels(data)
    profiles = profiles_from_data(data)
    return [(lang, profile) for profile in profiles for lang in languages]


def resolve_cv_path(root: Path, requested_cv: str | None) -> Path:
    if requested_cv is None:
        data_path = root / "cv.yml"
    else:
        data_path = Path(requested_cv).expanduser()
        if not data_path.is_absolute():
            data_path = data_path.resolve()

    if not data_path.is_file():
        raise SystemExit(f"CV data file not found: {data_path}")
    return data_path


def build(args: argparse.Namespace) -> None:
    root = Path(__file__).resolve().parents[1]
    data_path = resolve_cv_path(root, args.cv)
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)

    import yaml

    data = yaml.safe_load(data_path.read_text(encoding="utf-8"))
    template_name = selected_template(root, data, args.template)
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise SystemExit("Could not import WeasyPrint. Install dependencies with: pip install -r requirements.txt") from exc
    generated = [
        render_variant(root, data, lang, profile, template_name, output_dir, HTML, args.html)
        for lang, profile in iter_valid_variants(data)
    ]

    for pdf_path in generated:
        print(f"Generated: {pdf_path}")
    print(f"Generated {len(generated)} PDF(s).")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    choices = template_choices(root)
    parser = argparse.ArgumentParser(description="Generate CV variants from a YAML data file")
    parser.add_argument("--cv", default=None, help="CV YAML file to read. Defaults to the repo root cv.yml")
    parser.add_argument("--template", choices=choices, default=None, help=f"Template to use. Available: {', '.join(choices)}")
    parser.add_argument("--html", action="store_true", help="Also write the rendered HTML files to output/")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
