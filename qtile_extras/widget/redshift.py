import subprocess

from libqtile.log_utils import logger
from libqtile.widget import base
from libqtile.widget.base import _TextBox

# TODO:
# * maybe a scroll that goes through:
# - gamma
# - brightness
# - temp?
# each with a slider like PulseVolume?
#
# * Fix text resizing when pressing button (imagine user uses different messages)
# * Fix parameters
# * Make icons larger
# * Add comments and docs


class RedshiftWidget(_TextBox, base.PaddingMixin):
    is_enabled = False

    orientations = base.ORIENTATION_HORIZONTAL

    defaults = [
        ("brightness", 1.0, "Redshift brightness"),
        ("disabled_txt", "", "Redshift disabled text"),
        ("enabled_txt", "", "Redshift enabled text"),
        ("gamma_red", 1.0, "Redshift gamma red"),
        ("gamma_blue", 1.0, "Redshift gamma blue"),
        ("gamma_green", 1.0, "Redshift gamma green"),
        ("font", "sans", "Default font"),
        ("fontsize", 50, "Font size"),
        ("foreground", "ffffff", "Font colour for information text"),
        ("temperature", 1700, "Redshift temperature to set when enabled"),
    ]

    _dependencies = ["redshift"]

    def __init__(self, **config):
        _TextBox.__init__(self, **config)
        self.add_defaults(RedshiftWidget.defaults)
        self.add_defaults(base.PaddingMixin.defaults)
        self.add_callbacks({"Button1": self._redshift_switch})

    def _configure(self, qtile, bar):
        _TextBox._configure(self, qtile, bar)
        # reset, so we know it is in some known in
        # initial state
        self._reset_redshift()
        self._set_text()

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        self._set_text()
        _TextBox.draw(self)

    # reset redshift
    def _reset_redshift(self):
        command_output = ""
        try:
            command_output = subprocess.run(
                ["redshift", "-x"], check=True, capture_output=True
            ).stdout
        except Exception:
            logger.exception(f"Exception trying to reset redshift: {command_output}")
            self._render_error_text()

    def _enable_redshift(self):
        command_output = ""
        gamma_val = (
            str(self.gamma_red)
            + ":"
            + str(self.gamma_green)
            + ":"
            + str(self.gamma_blue)
        )
        try:
            command = subprocess.run(
                [
                    "redshift",
                    "-P",
                    "-O",
                    str(self.temperature),
                    "-b",
                    str(self.brightness),
                    "-g",
                    gamma_val,
                ],
                check=True,
                capture_output=True,
            )
            command_output = command.stdout
            logger.info(command.args)
        except Exception:
            logger.exception(
                f"Exception trying to set redshift temperature: {command_output}"
            )
            self._render_error_text()

    # controls what happens when the widget is pressed
    def _redshift_switch(self):
        if self.is_enabled:
            self._reset_redshift()
        else:
            self._enable_redshift()
        self.is_enabled = not self.is_enabled
        self._set_text()
        self.bar.draw()

    def _render_error_text(self):
        self.text = "Redshift widget error"
        self.draw()

    def _set_text(self):
        if self.is_enabled:
            self.text = self.enabled_txt
        else:
            self.text = self.disabled_txt
