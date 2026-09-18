# -*- coding: utf-8 -*-
"""Pruebas del estado de sincronizacion con GitHub (core/storage.py):
detectado el caso real donde GITHUB_REPO en los Secrets apuntaba a un
repositorio que ya no existe (renombrado tras el rebrand), la app seguia
"funcionando" en apariencia pero perdia todos los datos en cada reinicio,
sin ningun aviso visible en la UI. get_sync_status()/_describe_github_error
son la base de ese aviso (ver core.ui.sync_status_banner)."""

from core.storage import _describe_github_error, _is_github_configured, get_sync_status


def test_not_configured_marks_status_accordingly():
    assert _is_github_configured() is False
    status = get_sync_status()
    assert status["configured"] is False
    assert "GITHUB_TOKEN" in status["message"] or "GITHUB_REPO" in status["message"]


def test_describe_github_error_404_mentions_repo_not_found():
    msg = _describe_github_error(404, "")
    assert "no existe" in msg.lower() or "no tiene acceso" in msg.lower()
    assert "GITHUB_REPO" in msg


def test_describe_github_error_401_and_403_mention_token():
    for code in (401, 403):
        msg = _describe_github_error(code, "")
        assert "token" in msg.lower()


def test_describe_github_error_generic_falls_back_to_http_status():
    msg = _describe_github_error(500, "boom")
    assert "500" in msg
    assert "boom" in msg
