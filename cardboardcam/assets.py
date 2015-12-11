from flask_assets import Bundle

common_css = Bundle(
    Bundle(
        'css/vendor/dropzone.css',
        'css/vendor/bootstrap.min.css',
        'css/vendor/helper.css',
        'css/main.css',
        filters='cssmin'),
    output='public/css/common.css'
)

common_js = Bundle(
    'js/vendor/jquery.min.js',
    'js/vendor/bootstrap.min.js',
    Bundle(
        'js/vendor/dropzone.js',
        'js/main.js',
        filters='jsmin'
    ),
    output='public/js/common.js'
)
