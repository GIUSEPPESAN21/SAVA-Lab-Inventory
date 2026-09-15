# -*- coding: utf-8 -*-
"""
core/notifications.py - Alertas por WhatsApp (Twilio), 100% opcional.

A diferencia de la app original, un fallo o ausencia de la libreria/credenciales
de Twilio NUNCA debe tumbar la aplicacion: todo el modulo se degrada en
silencio (con log de advertencia) si no esta disponible o configurado.
"""

import logging

import streamlit as st

logger = logging.getLogger(__name__)

REQUIRED_SECRETS = [
    "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_FROM_NUMBER", "DESTINATION_WHATSAPP_NUMBER",
]


def _get_client():
    if not all(k in st.secrets for k in REQUIRED_SECRETS):
        return None
    try:
        from twilio.rest import Client
        return Client(st.secrets["TWILIO_ACCOUNT_SID"], st.secrets["TWILIO_AUTH_TOKEN"])
    except Exception as e:
        logger.warning(f"Twilio no disponible: {e}")
        return None


def send_whatsapp_alert(message: str) -> bool:
    client = _get_client()
    if not client:
        return False
    try:
        from_number = st.secrets["TWILIO_WHATSAPP_FROM_NUMBER"]
        to_number = st.secrets["DESTINATION_WHATSAPP_NUMBER"]
        client.messages.create(from_=f"whatsapp:{from_number}", body=message, to=f"whatsapp:{to_number}")
        return True
    except Exception as e:
        logger.error(f"Error al enviar alerta de WhatsApp: {e}")
        return False
