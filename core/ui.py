# -*- coding: utf-8 -*-
"""
core/ui.py - Componentes visuales compartidos para que TODA la app tenga el
mismo look centrado y organizado (logo, encabezados de pagina).
"""

import streamlit as st


def centered_logo(url: str, width: int = 110, caption: str = None) -> None:
    """Renderiza una imagen perfectamente centrada via HTML plano, sin
    depender de trucos de columnas (que no centran el contenido real)."""
    cap_html = f'<div style="color: var(--subtle-text-color); font-size: 0.8rem; margin-top: 4px;">{caption}</div>' if caption else ""
    st.markdown(
        f'<div style="text-align:center;">'
        f'<img src="{url}" width="{width}" style="display:inline-block;">'
        f"{cap_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = None, icon: str = None) -> None:
    """Encabezado de pagina centrado y consistente para todas las vistas."""
    heading = f"{icon} {title}" if icon else title
    st.markdown(f'<h1 class="main-header">{heading}</h1>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<p class="page-subtitle">{subtitle}</p>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def sync_status_banner(storage, user: dict) -> None:
    """Aviso visible (solo para profesor/maestro) cuando la sincronizacion
    con GitHub no esta configurada o el ultimo intento fallo: sin esto, los
    datos se guardan solo en el disco temporal de la app y se PIERDEN al
    reiniciarse, sin que nadie lo note (el error solo queda en los logs del
    servidor, no en la interfaz)."""
    if user.get("role") not in ("profesor", "maestro"):
        return

    status = storage.get_sync_status()

    if not status["configured"]:
        st.error(
            "🔴 **La sincronizacion con GitHub no esta configurada**: los datos se estan "
            "guardando solo en este contenedor y se **perderan** al reiniciarse la app. "
            "Agrega `GITHUB_TOKEN` y `GITHUB_REPO` en Settings → Secrets de Streamlit Cloud.",
            icon="🔴",
        )
        return

    if status["ok"] is False:
        st.error(
            f"🔴 **Fallo la sincronizacion con GitHub** ({status['repo'] or 'repo no configurado'} · "
            f"`{status['db_path']}`): {status['message']} Los cambios se estan guardando solo "
            "localmente y se perderan al reiniciarse la app.",
            icon="🔴",
        )
