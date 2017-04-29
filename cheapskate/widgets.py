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
    option_template_name = 'cc-bill-option.html'
