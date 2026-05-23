from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .api import AflasAPI
from .const import DOMAIN
from .options_flow import AflasOptionsFlow

_LOGGER = logging.getLogger(__name__)


class AflasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the initial configuration flow for Aflas.dk."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user input for initial setup."""
        errors = {}

        if user_input is not None:
            username = user_input["username"]
            password = user_input["password"]
            vaerknummer = user_input["vaerknummer"]

            api = AflasAPI(username, password, vaerknummer)

            result = await self.hass.async_add_executor_job(api.validate_login)

            if result is True:
                return self.async_create_entry(
                    title=f"Aflas.dk ({vaerknummer})",
                    data=user_input,
                    options={"update_interval": 60},  # default 60 minutes
                )

            if result == "invalid_auth":
                errors["base"] = "invalid_auth"
            else:
                errors["base"] = "cannot_connect"

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("vaerknummer"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return AflasOptionsFlow(config_entry)

