import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult


class AflasOptionsFlow(config_entries.OptionsFlow):
    """Handle Aflas.dk options flow."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = self._config_entry.options

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "update_interval",
                        default=options.get("update_interval", 60),
                    ): vol.In([5, 10, 30, 60, 120]),
                }
            ),
        )

