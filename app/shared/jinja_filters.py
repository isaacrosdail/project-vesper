from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

from datetime import datetime


def prettyiso(value: str) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)


def register_filters(app: Flask) -> None:
    app.jinja_env.filters["prettyiso"] = prettyiso
