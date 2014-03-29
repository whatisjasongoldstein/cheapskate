import json
from itertools import chain
from django.utils.safestring import mark_safe

from django.forms.widgets import SelectMultiple
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.html import conditional_escape, format_html, html_safe


class JSONSelectMultiple(SelectMultiple):
    """
    Multiple select widget that allows including json
    data inside the option elements.
    """

    def render_option(self, selected_choices, option_value, data):
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
        else:
            selected_html = ''
        return format_html('<option value="{}"{} data-json="{}">{}</option>',
                           option_value,
                           selected_html,
                           json.dumps(data),
                           force_text(data["title"]))

