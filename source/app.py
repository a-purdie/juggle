from dash import Dash, _dash_renderer
from source.config import EXTERNAL_STYLESHEETS, APP_CONFIG, SECURITY_HEADERS, get_runtime_config
from source.layout import create_app_layout
from source import callbacks as cb

app = Dash(external_stylesheets=EXTERNAL_STYLESHEETS)

# Configure app settings
app.config.suppress_callback_exceptions = APP_CONFIG['suppress_callback_exceptions']
app.title = APP_CONFIG['title']
server = app.server
_dash_renderer._set_react_version(APP_CONFIG['react_version'])

# Set the application layout
app.layout = create_app_layout()

# Register callbacks
cb.register_callbacks(app)


def add_security_headers(response):
    """Add security headers to all responses."""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


@app.server.after_request
def apply_security_headers(response):
    """Apply security headers to all responses."""
    return add_security_headers(response)


if __name__ == '__main__':
    runtime_config = get_runtime_config()
    app.run(**runtime_config)