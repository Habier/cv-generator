import argparse
import re
import sys
import types
from pathlib import Path

import pytest

from scripts import generate


def write_minimal_cv(path: Path) -> None:
    path.write_text(
        """
personal:
  name: Test User
settings:
  default_template: default
labels:
  en:
    present: Present
profiles:
  backend:
    title: Backend Developer
    summary: Summary
""".strip(),
        encoding="utf-8",
    )


def test_resolve_app_root_uses_source_root_when_not_frozen(monkeypatch):
    monkeypatch.delattr(sys, "frozen", raising=False)

    app_root = generate.resolve_app_root()

    assert (app_root / "scripts" / "generate.py").is_file()


def test_resolve_app_root_uses_executable_parent_when_frozen(tmp_path, monkeypatch):
    executable = tmp_path / "release" / "cv-generator.exe"
    executable.parent.mkdir()
    executable.write_text("", encoding="utf-8")
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(executable))

    assert generate.resolve_app_root() == executable.parent


def test_resolve_workspace_root_uses_current_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    assert generate.resolve_workspace_root() == tmp_path


def test_resolve_cv_path_fails_for_missing_default_cv(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        generate.resolve_cv_path(tmp_path, None)

    assert "CV data file not found" in str(exc_info.value)
    assert str(tmp_path / "cv.yml") in str(exc_info.value)


def test_resolve_cv_path_fails_for_nonexistent_requested_cv(tmp_path):
    with pytest.raises(SystemExit) as exc_info:
        generate.resolve_cv_path(tmp_path, "missing.yml")

    assert "CV data file not found" in str(exc_info.value)
    assert "missing.yml" in str(exc_info.value)


def test_resolve_output_dir_defaults_to_workspace_output(tmp_path):
    assert generate.resolve_output_dir(tmp_path, {}) == tmp_path / "output"
    assert generate.resolve_output_dir(tmp_path, {"settings": {}}) == tmp_path / "output"


def test_resolve_output_dir_uses_configured_relative_path(tmp_path):
    data = {"settings": {"output_dir": "build/cvs"}}

    assert generate.resolve_output_dir(tmp_path, data) == (tmp_path / "build/cvs").resolve()


def test_resolve_output_dir_uses_configured_absolute_path(tmp_path):
    custom = tmp_path / "custom"
    data = {"settings": {"output_dir": str(custom)}}

    assert generate.resolve_output_dir(tmp_path, data) == custom


def test_template_choices_accept_valid_and_ignore_invalid_template_dirs(tmp_path):
    templates_root = tmp_path / "templates"
    (templates_root / "default").mkdir(parents=True)
    (templates_root / "default" / "cv.html.j2").write_text("ok", encoding="utf-8")
    (templates_root / "missing-entrypoint").mkdir()
    (templates_root / "notes.txt").write_text("not a template", encoding="utf-8")

    assert generate.template_choices(tmp_path) == ["default"]


def test_template_choices_returns_empty_when_templates_root_is_missing(tmp_path):
    assert generate.template_choices(tmp_path) == []


def test_resolve_personal_links_selects_requested_language_and_preserves_other_fields():
    personal = {
        "linkedin": {
            "es": "https://linkedin.example/profile",
            "en": "https://linkedin.example/profile?locale=en-US",
        },
        "location": {"es": "Madrid, España", "en": "Madrid, Spain"},
    }

    resolved = generate.resolve_personal_links(personal, "en")

    assert resolved["linkedin"] == "https://linkedin.example/profile?locale=en-US"
    assert resolved["location"] == personal["location"]


def test_resolve_personal_links_preserves_scalar_urls_and_uses_localized_fallback_order():
    personal = {
        "github": "https://github.com/example",
        "portfolio": {
            "fr": "",
            "es": "https://example.com/es",
            "en": "https://example.com/en",
        },
    }

    resolved = generate.resolve_personal_links(personal, "fr")

    assert resolved["github"] == "https://github.com/example"
    assert resolved["portfolio"] == "https://example.com/es"


def test_display_url_strips_query_string():
    assert generate.display_url("https://www.linkedin.com/in/example/?locale=en-US") == "linkedin.com/in/example/"


def test_display_url_strips_https_and_http_schemes():
    assert generate.display_url("https://github.com/example") == "github.com/example"
    assert generate.display_url("http://example.com") == "example.com"


def test_display_url_strips_www_prefix():
    assert generate.display_url("https://www.example.com") == "example.com"
    assert generate.display_url("www.example.com") == "example.com"


def test_display_url_leaves_plain_urls_unchanged():
    assert generate.display_url("github.com/example") == "github.com/example"


def test_display_url_coerces_non_string_values():
    assert generate.display_url(123) == "123"
    assert generate.display_url(None) == "None"


@pytest.mark.parametrize("template_name", ["default", "default-icons"])
def test_render_variant_keeps_link_query_in_href_but_excludes_it_from_visible_text(tmp_path, template_name):
    app_root = Path(__file__).resolve().parents[1]
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    rendered_html = []

    class FakePdf:
        def write_pdf(self, path):
            Path(path).write_text("pdf", encoding="utf-8")

    def fake_pdf_renderer(*, string, base_url):
        rendered_html.append(string)
        return FakePdf()

    data = {
        "personal": {
            "name": "Test User",
            "location": {"es": "Madrid, España", "en": "Madrid, Spain"},
            "phone": "+34 600 000 000",
            "email": "test@example.com",
            "github": "https://github.com/example",
            "linkedin": {
                "es": "https://www.linkedin.com/in/javier-garcia-cabrera/",
                "en": "https://www.linkedin.com/in/javier-garcia-cabrera/?locale=en-US",
            },
        },
        "labels": {"es": {}, "en": {}},
        "profiles": {"backend": {"title": {"en": "Developer"}, "summary": {"en": "Summary"}}},
    }

    generate.render_variant(app_root, data, "en", "backend", template_name, output_dir, fake_pdf_renderer, False)

    linkedin_anchor = re.search(
        r'<a[^>]+href="https://www\.linkedin\.com/in/javier-garcia-cabrera/\?locale=en-US"[^>]*>(.*?)</a>',
        rendered_html[0],
        re.DOTALL,
    )

    assert linkedin_anchor is not None
    visible_text = re.sub(r"<[^>]+>", "", linkedin_anchor.group(1)).strip()
    assert visible_text == "linkedin.com/in/javier-garcia-cabrera/"
    assert "?locale=en-US" not in visible_text
    assert "{'es':" not in rendered_html[0]


@pytest.mark.parametrize("template_name", ["default", "default-icons"])
@pytest.mark.parametrize(
    ("certifications", "should_render"),
    [(None, False), ([], False), ([{"en": "Example Certification"}], True)],
)
def test_render_variant_only_shows_certifications_section_when_populated(
    tmp_path, template_name, certifications, should_render
):
    app_root = Path(__file__).resolve().parents[1]
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    rendered_html = []

    class FakePdf:
        def write_pdf(self, path):
            Path(path).write_text("pdf", encoding="utf-8")

    def fake_pdf_renderer(*, string, base_url):
        rendered_html.append(string)
        return FakePdf()

    data = {
        "personal": {
            "name": "Test User",
            "location": {"en": "Test City"},
            "phone": "+1 555 0100",
            "email": "test@example.com",
            "github": "https://github.com/example",
            "linkedin": "https://linkedin.com/in/example",
        },
        "labels": {"en": {"certifications": "Certifications"}},
        "profiles": {"backend": {"title": {"en": "Developer"}, "summary": {"en": "Summary"}}},
    }
    if certifications is not None:
        data["certifications"] = certifications

    generate.render_variant(app_root, data, "en", "backend", template_name, output_dir, fake_pdf_renderer, False)

    html = rendered_html[0]
    assert ('id="certifications-heading"' in html) is should_render
    assert ("Example Certification" in html) is should_render


@pytest.mark.parametrize("template_name", ["default", "default-icons"])
@pytest.mark.parametrize(
    ("description", "should_render"),
    [(None, False), ({"en": ""}, False), ({"en": "Job description"}, True)],
)
def test_render_variant_only_shows_job_description_when_populated(
    tmp_path, template_name, description, should_render
):
    app_root = Path(__file__).resolve().parents[1]
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    rendered_html = []

    class FakePdf:
        def write_pdf(self, path):
            Path(path).write_text("pdf", encoding="utf-8")

    def fake_pdf_renderer(*, string, base_url):
        rendered_html.append(string)
        return FakePdf()

    job = {
        "company": "Example Company",
        "role": {"en": "Developer"},
        "start": "2025-01",
        "end": "present",
        "bullets": [],
        "technologies": [],
    }
    if description is not None:
        job["description"] = description

    data = {
        "personal": {
            "name": "Test User",
            "location": {"en": "Test City"},
            "phone": "+1 555 0100",
            "email": "test@example.com",
            "github": "https://github.com/example",
            "linkedin": "https://linkedin.com/in/example",
        },
        "labels": {"en": {"present": "Present", "professional_experience": "Experience"}},
        "profiles": {"backend": {"title": {"en": "Developer"}, "summary": {"en": "Summary"}}},
        "experience": [job],
    }

    generate.render_variant(app_root, data, "en", "backend", template_name, output_dir, fake_pdf_renderer, False)

    job_article = re.search(r'<article class="item">(.*?)</article>', rendered_html[0], re.DOTALL)
    assert job_article is not None
    article_html = job_article.group(1)
    assert ("<p>Job description</p>" in article_html) is should_render
    assert article_html.count("<p") == (2 if should_render else 1)


def test_build_writes_output_under_workspace_root(tmp_path, monkeypatch):
    app_root = tmp_path / "app"
    workspace_root = tmp_path / "workspace"
    (app_root / "templates" / "default").mkdir(parents=True)
    (app_root / "templates" / "default" / "cv.html.j2").write_text("ok", encoding="utf-8")
    workspace_root.mkdir()
    write_minimal_cv(workspace_root / "cv.yml")

    output_dirs = []

    def fake_render_variant(app_root_arg, data, lang, profile, template_name, output_dir, pdf_renderer, write_html):
        output_dirs.append(output_dir)
        pdf_path = output_dir / "cv-test.pdf"
        pdf_path.write_text("pdf", encoding="utf-8")
        return pdf_path

    monkeypatch.setattr(generate, "resolve_app_root", lambda: app_root)
    monkeypatch.setattr(generate, "resolve_workspace_root", lambda: workspace_root)
    monkeypatch.setattr(generate, "render_variant", fake_render_variant)
    monkeypatch.setitem(sys.modules, "weasyprint", types.SimpleNamespace(HTML=object))

    generate.build(argparse.Namespace(cv=None, template=None, html=False))

    assert output_dirs == [workspace_root / "output"]
    assert (workspace_root / "output" / "cv-test.pdf").is_file()
    assert not (app_root / "output").exists()


def test_build_exits_before_render_when_default_cv_is_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exc_info:
        generate.build(argparse.Namespace(cv=None, template=None, html=False))

    assert "CV data file not found" in str(exc_info.value)
    assert str(tmp_path / "cv.yml") in str(exc_info.value)


def test_build_uses_configured_output_dir_from_cv_yml(tmp_path, monkeypatch):
    app_root = tmp_path / "app"
    workspace_root = tmp_path / "workspace"
    (app_root / "templates" / "default").mkdir(parents=True)
    (app_root / "templates" / "default" / "cv.html.j2").write_text("ok", encoding="utf-8")
    workspace_root.mkdir()
    (workspace_root / "cv.yml").write_text(
        """
personal:
  name: Test User
settings:
  default_template: default
  output_dir: build/cvs
labels:
  en:
    present: Present
profiles:
  backend:
    title: Backend Developer
    summary: Summary
""".strip(),
        encoding="utf-8",
    )

    output_dirs = []

    def fake_render_variant(app_root_arg, data, lang, profile, template_name, output_dir, pdf_renderer, write_html):
        output_dirs.append(output_dir)
        pdf_path = output_dir / "cv-test.pdf"
        pdf_path.write_text("pdf", encoding="utf-8")
        return pdf_path

    monkeypatch.setattr(generate, "resolve_app_root", lambda: app_root)
    monkeypatch.setattr(generate, "resolve_workspace_root", lambda: workspace_root)
    monkeypatch.setattr(generate, "render_variant", fake_render_variant)
    monkeypatch.setitem(sys.modules, "weasyprint", types.SimpleNamespace(HTML=object))

    generate.build(argparse.Namespace(cv=None, template=None, html=False))

    assert output_dirs == [(workspace_root / "build/cvs").resolve()]
    assert (workspace_root / "build/cvs" / "cv-test.pdf").is_file()
    assert not (workspace_root / "output").exists()


def test_main_exits_before_render_when_requested_cv_is_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["generate.py", "--cv", "missing.yml"])

    with pytest.raises(SystemExit) as exc_info:
        generate.main()

    assert "CV data file not found" in str(exc_info.value)
    assert "missing.yml" in str(exc_info.value)
