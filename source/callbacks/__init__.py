"""Callbacks module for the debt management application."""

from source.callbacks import form_callbacks
from source.callbacks import debt_callbacks
from source.callbacks import visualization_callbacks
from source.callbacks import ui_callbacks


def register_callbacks(app):
    """Register all application callbacks."""
    form_callbacks.register_callbacks(app)
    debt_callbacks.register_callbacks(app)
    visualization_callbacks.register_callbacks(app)
    ui_callbacks.register_callbacks(app)