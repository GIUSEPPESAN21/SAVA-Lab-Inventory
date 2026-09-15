# -*- coding: utf-8 -*-
"""
core/reports.py - Analitica de uso del laboratorio y exportacion de la base de datos.
"""

import io
from datetime import datetime, timezone

import pandas as pd


def most_borrowed_items(loans: list, top_n: int = 10) -> pd.DataFrame:
    if not loans:
        return pd.DataFrame(columns=["Item", "Veces Prestado", "Unidades Totales"])
    df = pd.DataFrame(loans)
    summary = df.groupby("item_name").agg(
        **{"Veces Prestado": ("id", "count"), "Unidades Totales": ("quantity", "sum")}
    ).reset_index().rename(columns={"item_name": "Item"})
    return summary.sort_values("Veces Prestado", ascending=False).head(top_n)


def average_loan_duration_hours(loans: list) -> float:
    returned = [l for l in loans if l.get("status") == "returned" and l.get("checkout_at") and l.get("return_at")]
    if not returned:
        return 0.0
    durations = [(l["return_at"] - l["checkout_at"]).total_seconds() / 3600 for l in returned]
    return sum(durations) / len(durations)


def top_users_by_loans(loans: list, top_n: int = 10) -> pd.DataFrame:
    if not loans:
        return pd.DataFrame(columns=["Usuario", "Rol", "Prestamos"])
    df = pd.DataFrame(loans)
    summary = df.groupby(["user_name", "user_role"]).size().reset_index(name="Prestamos")
    summary = summary.rename(columns={"user_name": "Usuario", "user_role": "Rol"})
    return summary.sort_values("Prestamos", ascending=False).head(top_n)


def export_full_database(items: list, users: list, loans: list) -> io.BytesIO:
    df_items = pd.DataFrame(items)
    df_users = pd.DataFrame(users)
    if not df_users.empty and "password_hash" in df_users.columns:
        df_users = df_users.drop(columns=["password_hash"])
    df_loans = pd.DataFrame(loans)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if not df_items.empty:
            df_items.to_excel(writer, sheet_name="items", index=False)
        if not df_users.empty:
            df_users.to_excel(writer, sheet_name="users", index=False)
        if not df_loans.empty:
            df_loans.to_excel(writer, sheet_name="loans", index=False)
    output.seek(0)
    return output
