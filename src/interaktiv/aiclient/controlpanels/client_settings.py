from interaktiv.aiclient import _
from plone import schema
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.autoform import directives
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from zope.component import adapter
from zope.interface import Interface


class IAIClientSettings(Interface):
    openrouter_api_key = schema.Password(
        title=_("OpenRouter API Key"),
        description=_("API Key used to connect to OpenRouter"),
        required=False,
    )

    openrouter_model = schema.Choice(
        title=_("OpenRouter model"),
        description=_("Select the model you want to use for the AI Client."),
        required=True,
        vocabulary="interaktiv.aiclient.model_vocabulary",
    )

    openrouter_api_url = schema.TextLine(
        title=_("OpenRouter API URL"),
        description="",
        default="https://openrouter.ai/api/v1",
        required=True,
    )
    directives.omitted("openrouter_api_url")


class AIClientForm(RegistryEditForm):
    schema = IAIClientSettings
    schema_prefix = "interaktiv.aiclient"
    label = _("AI Client Settings")

    def updateWidgets(self, prefix=None):
        super().updateWidgets(prefix)

        widget = self.widgets.get("openrouter_model")
        vocab = widget.terms if widget else None

        if not vocab:
            widget.disabled = "disabled"

            self.formErrorsMessage = _(
                "Could not retrieve models from OpenRouter API. Please try again later."
            )
            self.status = self.formErrorsMessage

        if len(widget.value) and widget.value[0] not in vocab:
            self.status = _(
                "The selected model is no longer available. "
                "Please choose another one from the list."
            )

    def updateActions(self):
        super().updateActions()

        widget = self.widgets.get("openrouter_model")

        if widget.disabled == "disabled":
            del self.actions["save"]


@adapter(Interface, Interface)
class AIClientConfigletPanel(RegistryConfigletPanel):
    schema = IAIClientSettings
    schema_prefix = "interaktiv.aiclient"
    configlet_id = "aiclient-controlpanel"
    configlet_category_id = "Products"
    title = "AI Client"
    group = "Products"


AIClientView = layout.wrap_form(AIClientForm, ControlPanelFormWrapper)
