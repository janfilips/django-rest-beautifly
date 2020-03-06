from django.forms.utils import ErrorList
from django.utils.html import format_html_join


class BootstrapErrorList(ErrorList):
    def __str__(self):
        return self.as_alert()

    def as_alert(self):
        if self:
            return format_html_join(
                "",
                '<div class="alert alert-danger">{}</div>',
                ((str(e),) for e in self),
            )
        else:
            return ""
