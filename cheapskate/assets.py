from django_assets import Bundle, register
from webassets_libsass import LibSass

from webassets.filter import register_filter
from webassets_babel import BabelFilter

register_filter(BabelFilter)

styles = Bundle(
    "css/normalize.css", 
    "css/site.scss",
    filters="libsass",
    output="css/app.css")

register("app_styles", styles)


scripts = Bundle(
    "js/underscore.js",
    "js/helpers.es6",
    "js/widgets.es6",
    "js/credit-card-admin.es6",
    filters=["babel"],
    output="js/app.js")

register("app_scripts", scripts)
