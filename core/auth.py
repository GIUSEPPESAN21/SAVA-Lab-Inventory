# -*- coding: utf-8 -*-
"""
core/auth.py - Registro, inicio de sesion y control de roles.

Regla de seguridad clave: el rol NUNCA se elige libremente en el registro.
- Toda cuenta nueva nace "estudiante".
- Nace "profesor" solo si su correo ya esta en la lista blanca (professors_whitelist),
  que unicamente un "maestro" puede editar.
- El rol "maestro" nunca se auto-asigna: la primera cuenta maestra se siembra desde
  st.secrets (MASTER_EMAIL / MASTER_INITIAL_PASSWORD) si todavia no existe ninguna.
"""

import logging

import bcrypt
import streamlit as st

logger = logging.getLogger(__name__)

DEFAULT_ALLOWED_DOMAINS = ["uniminuto.edu.co", "uniandes.edu.co"]


def get_allowed_domains() -> list:
    raw = st.secrets.get("ALLOWED_EMAIL_DOMAINS", "")
    if raw:
        return [d.strip().lower() for d in raw.split(",") if d.strip()]
    return DEFAULT_ALLOWED_DOMAINS


def is_institutional_email(email: str) -> bool:
    email = (email or "").strip().lower()
    if "@" not in email:
        return False
    domain = email.split("@")[-1]
    return any(domain == d or domain.endswith("." + d) for d in get_allowed_domains())


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def ensure_master_seed(storage) -> None:
    """Crea la primera cuenta maestra desde los Secrets si aun no existe ninguna."""
    try:
        if storage.count_masters() > 0:
            return
        master_email = st.secrets.get("MASTER_EMAIL", "")
        master_password = st.secrets.get("MASTER_INITIAL_PASSWORD", "")
        if not master_email or not master_password:
            return
        if storage.get_user_by_email(master_email):
            return
        storage.create_user(
            full_name="Administrador SAVA Lab",
            email=master_email,
            password_hash=hash_password(master_password),
            role="maestro",
            program="Direccion de Laboratorio",
            status="active",
        )
        logger.info("Cuenta maestra sembrada desde Secrets.")
    except Exception as e:
        logger.error(f"No se pudo sembrar la cuenta maestra: {e}")


def register_user(storage, full_name: str, email: str, password: str, program: str):
    email = (email or "").strip().lower()
    full_name = (full_name or "").strip()

    if not full_name:
        return None, "El nombre completo es obligatorio."
    if not is_institutional_email(email):
        domains = ", ".join(get_allowed_domains())
        return None, f"Debes registrarte con un correo institucional valido ({domains})."
    if not password or len(password) < 8:
        return None, "La contrasena debe tener al menos 8 caracteres."
    if storage.get_user_by_email(email):
        return None, "Ya existe una cuenta registrada con ese correo."

    role = "profesor" if storage.is_email_whitelisted_professor(email) else "estudiante"

    user = storage.create_user(
        full_name=full_name,
        email=email,
        password_hash=hash_password(password),
        role=role,
        program=program,
        status="active",
    )
    return user, None


def login_user(storage, email: str, password: str):
    email = (email or "").strip().lower()
    user = storage.get_user_by_email(email)
    if not user:
        return None, "No existe una cuenta con ese correo."
    if user.get("status") != "active":
        return None, "Tu cuenta esta deshabilitada. Contacta a un administrador."
    if not verify_password(password, user.get("password_hash", "")):
        return None, "Contrasena incorrecta."
    return user, None
