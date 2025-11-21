from interaktiv.aiclient import _
from plone import schema
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.z3cform import layout
from zope.interface import Interface


class IAIClientSettings(Interface):
    openrouter_api_key = schema.Password(
        title=_("OpenRouter API Key"),
        description=_("API Key used to connect to OpenRouter"),
        required=True,
    )

    openrouter_model = schema.Choice(
        title=_("OpenRouter model"),
        description=_("Select the model you want to use for the AI Client."),
        required=True,
        vocabulary="interaktiv.aiclient.model_vocabulary",
    )

    openrouter_models_api_url = schema.TextLine(
        title=_("OpenRouter models API URL"),
        description="",
        default="https://openrouter.ai/api/v1/models",
        required=True,
    )
    directives.omitted("openrouter_models_api_url")


class AIClientForm(RegistryEditForm):
    schema = IAIClientSettings
    schema_prefix = "interaktiv.aiclient"
    label = _("AI Client Settings")


AIClientView = layout.wrap_form(AIClientForm, ControlPanelFormWrapper)
