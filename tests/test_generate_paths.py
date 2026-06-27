import argparse
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


def test_template_choices_accept_valid_and_ignore_invalid_template_dirs(tmp_path):
    templates_root = tmp_path / "templates"
    (templates_root / "default").mkdir(parents=True)
    (templates_root / "default" / "cv.html.j2").write_text("ok", encoding="utf-8")
    (templates_root / "missing-entrypoint").mkdir()
    (templates_root / "notes.txt").write_text("not a template", encoding="utf-8")

    assert generate.template_choices(tmp_path) == ["default"]


def test_template_choices_returns_empty_when_templates_root_is_missing(tmp_path):
    assert generate.template_choices(tmp_path) == []


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


def test_main_exits_before_render_when_requested_cv_is_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["generate.py", "--cv", "missing.yml"])

    with pytest.raises(SystemExit) as exc_info:
        generate.main()

    assert "CV data file not found" in str(exc_info.value)
    assert "missing.yml" in str(exc_info.value)
