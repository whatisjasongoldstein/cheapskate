PIPELINE_CSS = {
    'styles': {
        'source_filenames': (
            "css/normalize.css",
            "css/site.scss",
        ),
        'output_filename': 'css/app.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
}

PIPELINE_JS = {
    'scripts': {
        'source_filenames': (
            "js/underscore-min.js",
            "js/helpers.es6",
            "js/widgets.es6",
            "js/overview.es6",
            "js/credit-card-admin.es6",
        ),
        'output_filename': 'js/app.js',
        'extra_context': {
            'async': True,
        },
    }
}
