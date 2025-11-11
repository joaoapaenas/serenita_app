# app/navigation_service.py

import logging
from typing import Callable, Dict, Any

from PySide6.QtWidgets import QWidget

log = logging.getLogger(__name__)


class NavigationService:
    """
    A central registry for view providers.
    This service allows features to register themselves for navigation without
    a central factory knowing about all of them.
    """

    def __init__(self):
        self._providers: Dict[str, Callable[..., QWidget]] = {}
        log.debug("NavigationService initialized.")

    def register(self, view_name: str, provider_func: Callable[..., QWidget]):
        """
        Registers a provider function for a given view name.

        Args:
            view_name: The name/route to register (e.g., "configurations_landing").
            provider_func: A function (often a lambda) that creates and returns the view widget.
        """
        if view_name in self._providers:
            log.warning(f"View provider for '{view_name}' is being overwritten.")
        self._providers[view_name] = provider_func
        log.debug(f"Registered view provider for '{view_name}'.")

    def get_view(self, view_name: str, **kwargs: Any) -> QWidget | None:
        """
        Gets a view widget by calling its registered provider.

        Args:
            view_name: The name/route of the view to create.
            **kwargs: Arguments to pass to the provider function.

        Returns:
            The created QWidget, or None if no provider is registered.
        """
        provider = self._providers.get(view_name)
        if provider:
            log.info(f"Creating view for '{view_name}' using its provider.")
            try:
                return provider(**kwargs)
            except Exception:
                log.critical(f"Error creating view for '{view_name}'", exc_info=True)
                return None
        else:
            log.error(f"No view provider found for '{view_name}'.")
            return None
